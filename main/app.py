import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, session

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Local utils
from pdf_utils import process_pdf, search_chunks
from profile_utils import save_and_load_profile, get_profile, extract_patient_context_complex, format_patient_summary_complex, set_profile
from storage_utils import PersistentStorage
from auth_utils import create_user, authenticate_user, get_user, get_user_directory

# -------------------------
# Config & Globals
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Groq integration only
try:
    from groq import Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    print(f"GROQ_API_KEY loaded: {'Yes' if GROQ_API_KEY else 'No'}")
    if GROQ_API_KEY:
        print(f"GROQ_API_KEY starts with: {GROQ_API_KEY[:10]}...")
    
    # Simple Groq client initialization
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    GROQ_AVAILABLE = groq_client is not None
    print(f"Groq client available: {GROQ_AVAILABLE}")
except Exception as e:
    print(f"Groq initialization failed: {e}")
    groq_client = None
    GROQ_AVAILABLE = False

# Together AI integration (primary)
try:
    from together import Together
    TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
    print(f"TOGETHER_API_KEY loaded: {'Yes' if TOGETHER_API_KEY else 'No'}")
    if TOGETHER_API_KEY:
        print(f"TOGETHER_API_KEY starts with: {TOGETHER_API_KEY[:10]}...")

    together_client = Together(api_key=TOGETHER_API_KEY) if TOGETHER_API_KEY else None
    TOGETHER_AVAILABLE = together_client is not None
    print(f"Together client available: {TOGETHER_AVAILABLE}")
except Exception as e:
    print(f"Together initialization failed: {e}")
    together_client = None
    TOGETHER_AVAILABLE = False

# Runtime dirs
PDF_UPLOAD_DIR = os.path.join("/tmp", "wondr_uploads")
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

# Data folder for pre-loaded PDFs (backend-managed)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Tracking file for chunked PDFs
CHUNK_TRACKER_FILE = os.path.join("/tmp", "wondr_storage", "chunk_tracker.json")

# Initialize persistent storage
storage = PersistentStorage()

# Allowed origins for CORS
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

def _origin_allowed(origin: str) -> bool:
    if not origin:
        return False
    origin = origin.strip().lower()
    allowed = [o.strip().lower() for o in ALLOWED_ORIGINS if o]
    if "*" in allowed:
        return True
    return origin in allowed

# App init
APP_HOST = "0.0.0.0"
APP_PORT = int(os.environ.get("PORT", 5000))
DEBUG = bool(os.environ.get("DEBUG", "True") == "True")

app = Flask(__name__, static_folder=".")
app.secret_key = os.environ.get("SECRET_KEY", "wondrlink-dev-secret-key-change-in-production")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wondr-app")

# In-memory state
indexed_chunks: List[str] = []

# Conversation history storage (session_id -> list of Q&A pairs)
conversation_history: Dict[str, List[Dict[str, str]]] = {}
MAX_HISTORY_LENGTH = 5  # Keep last 5 Q&A pairs

# Chunk tracker functions
def load_chunk_tracker() -> Dict[str, Any]:
    """Load the chunk tracker file that tracks which PDFs have been processed"""
    try:
        if os.path.exists(CHUNK_TRACKER_FILE):
            with open(CHUNK_TRACKER_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load chunk tracker: {e}")
    return {"files": {}}

def save_chunk_tracker(tracker: Dict[str, Any]):
    """Save the chunk tracker file"""
    try:
        os.makedirs(os.path.dirname(CHUNK_TRACKER_FILE), exist_ok=True)
        with open(CHUNK_TRACKER_FILE, 'w') as f:
            json.dump(tracker, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save chunk tracker: {e}")

def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get file modification time and size for tracking"""
    stat = os.stat(filepath)
    return {
        "mtime": stat.st_mtime,
        "size": stat.st_size
    }

def scan_and_chunk_data_folder():
    """
    Scan the data folder for PDFs and chunk any new or modified files.
    Skip files that have already been chunked and haven't changed.
    """
    global indexed_chunks

    logger.info(f"Scanning data folder: {DATA_DIR}")

    # Load existing tracker
    tracker = load_chunk_tracker()
    tracked_files = tracker.get("files", {})

    # Find all PDFs in data folder
    pdf_files = []
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(filename)

    logger.info(f"Found {len(pdf_files)} PDF files in data folder")

    # Track which files need processing
    files_to_process = []
    files_unchanged = []

    for filename in pdf_files:
        filepath = os.path.join(DATA_DIR, filename)
        file_info = get_file_info(filepath)

        # Check if file is already tracked and unchanged
        if filename in tracked_files:
            tracked_info = tracked_files[filename]
            # Also re-process if chunk_count is 0 (failed extraction)
            if (tracked_info.get("mtime") == file_info["mtime"] and
                tracked_info.get("size") == file_info["size"] and
                tracked_info.get("chunk_count", 0) > 0):
                files_unchanged.append(filename)
                continue

        files_to_process.append((filename, filepath, file_info))

    logger.info(f"Files unchanged (skipping): {len(files_unchanged)}")
    logger.info(f"Files to process: {len(files_to_process)}")

    # Process new/modified files
    for filename, filepath, file_info in files_to_process:
        try:
            logger.info(f"Processing PDF: {filename}")
            chunks = process_pdf(filepath)

            # Save chunks to storage
            storage.save_document_chunks(filename, chunks)

            # Update tracker
            tracked_files[filename] = {
                "mtime": file_info["mtime"],
                "size": file_info["size"],
                "chunk_count": len(chunks),
                "processed_at": datetime.now().isoformat()
            }

            logger.info(f"Processed {filename}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")

    # Remove tracked files that no longer exist in data folder
    for tracked_filename in list(tracked_files.keys()):
        if tracked_filename not in pdf_files:
            logger.info(f"Removing tracked file no longer in data folder: {tracked_filename}")
            storage.remove_document(tracked_filename)
            del tracked_files[tracked_filename]

    # Save updated tracker
    tracker["files"] = tracked_files
    tracker["last_scan"] = datetime.now().isoformat()
    save_chunk_tracker(tracker)

    # Load all chunks into memory
    indexed_chunks = storage.load_all_chunks()
    logger.info(f"Total chunks loaded: {len(indexed_chunks)}")

    return {
        "processed": len(files_to_process),
        "unchanged": len(files_unchanged),
        "total_chunks": len(indexed_chunks)
    }

# Load persisted data on startup
def load_persisted_data():
    """Load chunks and profile from disk on application startup"""
    global indexed_chunks

    # Scan data folder and process any new PDFs
    logger.info("Scanning data folder for PDFs...")
    scan_result = scan_and_chunk_data_folder()
    logger.info(f"Data folder scan complete: {scan_result}")

    # Note: Patient profiles are now loaded per-user when they authenticate
    logger.info("Profile loading deferred to user authentication")

# Load data on startup
load_persisted_data()

# -------------------------
# Enhanced Patient Context Helpers
# -------------------------
def extract_patient_context(profile: dict) -> Dict[str, Any]:
    """Extract and structure key patient information for better AI context"""
    return extract_patient_context_complex(profile)

def format_patient_summary(context: Dict[str, Any]) -> str:
    """Format patient context into a readable summary for AI"""
    return format_patient_summary_complex(context)

def classify_query_type(message: str) -> str:
    """
    Classify the query into categories to determine what context is relevant.

    Returns: treatment | side_effect | prognosis | diagnosis | general
    """
    message_lower = message.lower()

    # Treatment-related queries
    treatment_keywords = [
        'treatment', 'therapy', 'chemotherapy', 'chemo', 'radiation', 'surgery',
        'medication', 'drug', 'regimen', 'folfox', 'folfiri', 'immunotherapy',
        'targeted therapy', 'clinical trial', 'option', 'next step'
    ]

    # Side effect/symptom queries
    side_effect_keywords = [
        'side effect', 'symptom', 'pain', 'nausea', 'fatigue', 'tired',
        'neuropathy', 'diarrhea', 'constipation', 'vomit', 'fever', 'rash',
        'toxicity', 'adverse', 'reaction', 'feeling', 'hurt', 'ache'
    ]

    # Prognosis/outcome queries
    prognosis_keywords = [
        'prognosis', 'survival', 'outcome', 'life expectancy', 'cure',
        'remission', 'progression', 'spread', 'metastasis', 'stage',
        'how long', 'will i', 'chance', 'likely'
    ]

    # Diagnosis/testing queries
    diagnosis_keywords = [
        'diagnosis', 'test', 'scan', 'biopsy', 'ct', 'mri', 'pet',
        'blood work', 'lab', 'marker', 'cea', 'biomarker', 'genetic'
    ]

    # Count keyword matches for each category
    treatment_score = sum(1 for kw in treatment_keywords if kw in message_lower)
    side_effect_score = sum(1 for kw in side_effect_keywords if kw in message_lower)
    prognosis_score = sum(1 for kw in prognosis_keywords if kw in message_lower)
    diagnosis_score = sum(1 for kw in diagnosis_keywords if kw in message_lower)

    # Determine category with highest score
    scores = {
        'treatment': treatment_score,
        'side_effect': side_effect_score,
        'prognosis': prognosis_score,
        'diagnosis': diagnosis_score
    }

    max_score = max(scores.values())
    if max_score == 0:
        return 'general'

    # Return category with highest score
    for category, score in scores.items():
        if score == max_score:
            return category

    return 'general'

def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
    """Get conversation history for a session"""
    return conversation_history.get(session_id, [])

def add_to_conversation_history(session_id: str, question: str, answer: str):
    """Add a Q&A pair to conversation history"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only last N entries
    if len(conversation_history[session_id]) > MAX_HISTORY_LENGTH:
        conversation_history[session_id] = conversation_history[session_id][-MAX_HISTORY_LENGTH:]

def format_conversation_context(history: List[Dict[str, str]]) -> str:
    """Format conversation history for inclusion in prompt"""
    if not history:
        return ""

    formatted = "PREVIOUS CONVERSATION:\n"
    for i, entry in enumerate(history, 1):
        formatted += f"\nQ{i}: {entry['question']}\nA{i}: {entry['answer'][:200]}...\n"  # Truncate long answers

    return formatted

def filter_relevant_context(patient_context: Dict[str, Any], query_type: str, message: str) -> str:
    """
    Filter patient context to include only information relevant to the query type.
    This reduces prompt bloat and improves response focus.
    """
    if not patient_context:
        return "No patient profile available."

    # Always include basic info
    filtered_parts = []

    # Cancer type and stage (always relevant)
    cancer_type = patient_context.get('cancer_type', 'unspecified cancer')
    stage = patient_context.get('stage', 'unspecified')
    if stage != 'unspecified':
        filtered_parts.append(f"Diagnosis: {cancer_type}, stage {stage}")
    else:
        filtered_parts.append(f"Diagnosis: {cancer_type}")

    # Include context based on query type
    if query_type == 'treatment':
        # For treatment queries: current treatments, biomarkers, treatment options
        treatments = patient_context.get('current_treatments', [])
        if treatments:
            current_tx = [tx for tx in treatments if 'Currently on' in tx]
            if current_tx:
                filtered_parts.append(f"Current treatment: {current_tx[0]}")

        biomarkers = patient_context.get('biomarkers', 'unspecified')
        if biomarkers != 'unspecified' and biomarkers:
            filtered_parts.append(f"Biomarkers: {biomarkers}")

        treatment_options = patient_context.get('treatment_options', [])
        if treatment_options:
            filtered_parts.append(f"Options being considered: {', '.join(treatment_options[:3])}")

    elif query_type == 'side_effect':
        # For side effect queries: current medications, existing symptoms
        medications = patient_context.get('medications', [])
        if medications:
            filtered_parts.append(f"Current medications: {', '.join(medications[:5])}")

        symptoms = patient_context.get('symptoms', [])
        if symptoms:
            filtered_parts.append(f"Known symptoms: {', '.join(symptoms[:3])}")

        # Include current treatment for context
        treatments = patient_context.get('current_treatments', [])
        if treatments:
            current_tx = [tx for tx in treatments if 'Currently on' in tx]
            if current_tx:
                filtered_parts.append(f"Treatment: {current_tx[0]}")

    elif query_type == 'prognosis':
        # For prognosis queries: stage, biomarkers, disease sites
        disease_sites = patient_context.get('disease_sites', [])
        if disease_sites:
            filtered_parts.append(f"Disease sites: {', '.join(disease_sites[:3])}")

        biomarkers = patient_context.get('biomarkers', 'unspecified')
        if biomarkers != 'unspecified' and biomarkers:
            filtered_parts.append(f"Biomarkers: {biomarkers}")

        resistance = patient_context.get('resistance_mechanism', '')
        if resistance:
            filtered_parts.append(f"Resistance: {resistance}")

    elif query_type == 'diagnosis':
        # For diagnosis queries: biomarkers, any test results
        biomarkers = patient_context.get('biomarkers', 'unspecified')
        if biomarkers != 'unspecified' and biomarkers:
            filtered_parts.append(f"Biomarkers: {biomarkers}")

    else:  # general
        # For general queries: provide summary
        performance_status = patient_context.get('performance_status', 'unspecified')
        if performance_status != 'unspecified':
            filtered_parts.append(f"Performance status: {performance_status}")

        treatments = patient_context.get('current_treatments', [])
        if treatments:
            current_tx = [tx for tx in treatments if 'Currently on' in tx]
            if current_tx:
                filtered_parts.append(f"Current treatment: {current_tx[0]}")

    # Add medical history if mentioned in query
    if any(word in message.lower() for word in ['history', 'previous', 'past', 'before', 'allergy', 'allergic']):
        medical_history = patient_context.get('medical_history', [])
        if medical_history:
            filtered_parts.append(f"Medical history: {', '.join(medical_history[:3])}")

        allergies = patient_context.get('allergies', 'none reported')
        if allergies != 'none reported':
            filtered_parts.append(f"Allergies: {allergies}")

    return " | ".join(filtered_parts)

# -------------------------
# Enhanced Response Settings
# -------------------------
def get_response_settings(response_length: str):
    """Get max_tokens and system message based on response length setting"""
    if response_length == "brief":
        return {
            "max_tokens": 100,
            "system_message": """You are WondrLink, a caring cancer guide. Use simple everyday words. Be warm and supportive. CRITICAL: Answer in exactly 1-2 sentences only. Stop after your second sentence.

MEDICAL INSTRUCTIONS:
- Base responses on established medical guidelines
- Prioritize patient safety
- Consider the patient's specific cancer type and stage""",
            "prompt_instruction": "Answer in EXACTLY 1-2 sentences using simple words. Stop after your second sentence. No introductions or filler."
        }
    elif response_length == "detailed":
        return {
            "max_tokens": 250,
            "system_message": """You are WondrLink, a knowledgeable cancer guide. Use simple everyday language. Be thorough but concise. CRITICAL: Answer in 4-5 sentences maximum. Stop after your fifth sentence.

MEDICAL INSTRUCTIONS:
- Base responses on established medical guidelines
- Prioritize patient safety
- Consider the patient's specific cancer type and stage""",
            "prompt_instruction": "Answer in 4-5 sentences maximum using simple words. Explain medical terms briefly. Stop after your fifth sentence."
        }
    else:  # normal (default)
        return {
            "max_tokens": 150,
            "system_message": """You are WondrLink, a helpful cancer guide. Use simple everyday language. Be clear and helpful. CRITICAL: Answer in exactly 2-3 sentences. Stop after your third sentence.

MEDICAL INSTRUCTIONS:
- Base responses on established medical guidelines
- Prioritize patient safety
- Consider the patient's specific cancer type and stage""",
            "prompt_instruction": "Answer in EXACTLY 2-3 sentences using simple words. Stop after your third sentence. No introductions or filler."
        }

def assemble_prompt(message: str, retrieved: List[str], patient: dict, response_length: str = "normal",
                    conversation_context: str = "") -> str:
    """Enhanced prompt assembly with query-relevant context filtering and conversation history"""

    # Get response settings
    settings = get_response_settings(response_length)

    # Classify query type to determine relevant context
    query_type = classify_query_type(message)

    # Extract patient context
    patient_context = extract_patient_context(patient)

    # Filter context to only what's relevant for this query type
    filtered_context = filter_relevant_context(patient_context, query_type, message)

    # Format retrieved guidelines
    if retrieved:
        guideline_context = "\n---GUIDELINE EXCERPT---\n".join(retrieved)
        guideline_note = f"Based on {len(retrieved)} relevant guideline sections:"
    else:
        guideline_context = "No specific guideline excerpts found for this query."
        guideline_note = "Based on general cancer care knowledge:"

    # Determine urgency context
    urgency_keywords = ['pain', 'fever', 'bleeding', 'severe', 'emergency', 'urgent', 'can\'t', 'unable', 'worsening', 'side effect', 'toxicity']
    is_potentially_urgent = any(keyword in message.lower() for keyword in urgency_keywords)

    urgency_instruction = ""
    if is_potentially_urgent:
        urgency_instruction = "\nIMPORTANT: This question may be about a serious side effect or urgent situation. If you think they need to see a doctor right away, say so clearly."

    # Build the prompt with optional conversation history
    prompt_parts = [
        "You are WondrLink, a caring cancer guide who explains things in simple, everyday language.",
        ""
    ]

    # Add conversation history if available
    if conversation_context:
        prompt_parts.append(conversation_context)
        prompt_parts.append("")

    # Add chain-of-thought for complex queries (treatment, prognosis, side effects)
    complex_query_types = ['treatment', 'prognosis', 'side_effect']
    chain_of_thought = ""

    if query_type in complex_query_types and response_length != "brief":
        chain_of_thought = """
BEFORE ANSWERING, THINK STEP-BY-STEP:
1. What specific aspect of cancer care does this question address?
2. What is most relevant from the patient's situation?
3. What evidence-based guidance applies here?
4. What simple language can I use to explain this?

"""

    prompt_parts.extend([
        f"PATIENT INFORMATION (Query Type: {query_type}):",
        filtered_context,
        "",
        "MEDICAL GUIDELINES AVAILABLE:",
        guideline_note,
        guideline_context,
        "",
        f"USER'S QUESTION: {message}",
        "",
        chain_of_thought,
        "INSTRUCTIONS FOR YOUR RESPONSE:",
        f"- {settings['prompt_instruction']}",
        "- Use simple words that anyone can understand - NO medical jargon",
        "- When you must use a medical term, immediately explain it in plain English",
        "- Be specific about what this person should expect or do next",
        f"- Focus on their exact type of cancer ({patient_context.get('cancer_type', 'cancer')}) and current situation",
        "- Give practical, helpful advice they can actually use",
        "- Be warm and encouraging while being honest"
    ])

    if conversation_context:
        prompt_parts.append("- Consider the previous conversation for context, but focus on answering the current question")

    prompt_parts.append(f"- If they ask about something that doesn't match their diagnosis, gently point out the difference{urgency_instruction}")
    prompt_parts.extend([
        "",
        "Remember: Explain everything like you're talking to a friend who isn't a doctor.",
        "",
        "RESPONSE:"
    ])

    return "\n".join(prompt_parts)

def trim_incomplete_sentence(response: str) -> str:
    """Trim any incomplete sentence at the end of a response."""
    if not response:
        return response
    response = response.strip()
    # If ends with proper punctuation, return as-is
    if response and response[-1] in '.!?"':
        return response
    # Find last sentence-ending punctuation
    last_period = response.rfind('.')
    last_exclaim = response.rfind('!')
    last_question = response.rfind('?')
    last_punct = max(last_period, last_exclaim, last_question)
    if last_punct > 0:
        return response[:last_punct + 1]
    return response  # Return original if no sentence found

def enhanced_medical_validation(response: str, query: str) -> dict:
    """
    Additional medical-specific validation beyond standard validation.
    Checks for medical safety concerns and absolute claims.
    """
    safety_flags = []

    response_lower = response.lower()
    query_lower = query.lower()

    # Check for absolute medical claims (should be avoided)
    absolute_words = ['always', 'never', 'guaranteed', 'cure', 'definitely', 'impossible', 'certainly will']
    for word in absolute_words:
        if word in response_lower:
            safety_flags.append(f"Contains absolute medical claim: '{word}'")

    # Check for emergency situations that need immediate care
    emergency_terms = ['emergency', '911', 'call doctor', 'immediately', 'urgent care', 'hospital']
    has_emergency_in_query = any(term in query_lower for term in ['severe pain', 'can\'t breathe', 'bleeding heavily', 'chest pain', 'stroke'])
    mentions_emergency_action = any(term in response_lower for term in emergency_terms)

    if has_emergency_in_query and not mentions_emergency_action:
        safety_flags.append("Emergency query detected but response doesn't recommend immediate medical attention")

    # Check for medication dosage information (should defer to doctor)
    dosage_terms = ['take', 'mg', 'dose', 'pill', 'tablet', 'milligram']
    if any(term in response_lower for term in dosage_terms) and 'doctor' not in response_lower:
        safety_flags.append("Mentions medication without deferring to healthcare provider")

    # Check response completeness (not cut off)
    if response and not response.rstrip().endswith(('.', '!', '?', '"')):
        safety_flags.append("Response may be incomplete (doesn't end with punctuation)")

    return {
        "safe": len(safety_flags) == 0,
        "flags": safety_flags,
        "severity": "high" if any("emergency" in flag.lower() for flag in safety_flags) else "low"
    }

def validate_response(response: str, user_question: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate AI response for safety, relevance, and quality.
    Returns dict with: is_valid, warnings, enhanced_response
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'enhanced_response': response,
        'needs_disclaimer': False
    }

    if not response or len(response.strip()) < 10:
        validation_result['is_valid'] = False
        validation_result['warnings'].append("Response too short or empty")
        return validation_result

    response_lower = response.lower()
    question_lower = user_question.lower()

    # Check for emergency symptoms - require immediate medical attention
    emergency_keywords = [
        'chest pain', 'difficulty breathing', 'severe bleeding', 'unconscious',
        'stroke', 'heart attack', 'severe allergic reaction', 'anaphylaxis',
        'high fever', 'severe headache', 'confusion', 'can\'t breathe'
    ]

    has_emergency = any(keyword in question_lower for keyword in emergency_keywords)
    mentions_doctor = any(word in response_lower for word in ['doctor', 'physician', 'medical', 'emergency', 'hospital', '911'])

    # If emergency symptoms but no mention of seeking medical care, flag it
    if has_emergency and not mentions_doctor:
        validation_result['warnings'].append("Emergency symptom detected but response doesn't recommend medical attention")
        validation_result['enhanced_response'] += "\n\n⚠️ IMPORTANT: If you're experiencing severe or worsening symptoms, contact your doctor immediately or seek emergency care."

    # Check for medication/treatment advice - needs disclaimer
    treatment_keywords = ['take', 'medication', 'drug', 'dose', 'prescription', 'treatment']
    if any(keyword in response_lower for keyword in treatment_keywords):
        validation_result['needs_disclaimer'] = True

    # Check response addresses the question (basic relevance check)
    # Extract key nouns from question
    question_words = set(question_lower.split())
    response_words = set(response_lower.split())
    common_words = question_words & response_words

    # If very few words in common, might be off-topic
    if len(common_words) < max(2, len(question_words) * 0.1):
        validation_result['warnings'].append("Response may not directly address the question")

    # Check for contradictions with patient profile
    if patient_context:
        cancer_type = patient_context.get('cancer_type', '').lower()

        # If patient has specific cancer type, check response doesn't discuss wrong type
        other_cancer_types = ['breast', 'lung', 'colon', 'prostate', 'pancreatic', 'ovarian']
        if cancer_type:
            for other_type in other_cancer_types:
                if other_type in cancer_type:
                    continue  # This is their cancer type
                # Check if response discusses a different cancer type prominently
                if response_lower.count(other_type + ' cancer') > 2:
                    validation_result['warnings'].append(f"Response discusses {other_type} cancer but patient has {cancer_type}")

    # Add standard medical disclaimer if needed
    if validation_result['needs_disclaimer']:
        disclaimer = "\n\n💡 Medical Disclaimer: This information is for educational purposes. Always consult your healthcare team before making any changes to your treatment or medication."
        validation_result['enhanced_response'] += disclaimer

    return validation_result

def call_llm(prompt: str,
             response_length: str = "normal",
             temperature: float = 0.2) -> tuple:
    """
    Call LLM API with Together AI as primary, Groq as fallback.

    Returns: (response_text, api_used)
        - response_text: The generated response
        - api_used: "together" or "groq"
    """
    settings = get_response_settings(response_length)

    # Try Together AI first (primary)
    if TOGETHER_AVAILABLE and together_client:
        try:
            logger.info(f"Calling Together AI with model: meta-llama/Llama-3.3-70B-Instruct-Turbo, response_length: {response_length}, max_tokens: {settings['max_tokens']}")
            response = together_client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": settings["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings["max_tokens"],
                temperature=temperature,
                top_p=0.9,
            )

            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.info(f"Together AI response success - length: {len(content)}")
                    return content.strip(), "together"

            logger.warning("Together AI returned empty response, falling back to Groq")
        except Exception as e:
            logger.warning(f"Together AI failed: {e}, falling back to Groq")

    # Fallback to Groq
    if GROQ_AVAILABLE and groq_client:
        try:
            logger.info(f"Calling Groq (fallback) with model: llama-3.1-8b-instant, response_length: {response_length}, max_tokens: {settings['max_tokens']}")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": settings["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings["max_tokens"],
                temperature=temperature,
                top_p=0.9,
            )

            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.info(f"Groq response success - length: {len(content)}")
                    return content.strip(), "groq"
        except Exception as e:
            logger.exception(f"Groq API also failed: {e}")
            raise RuntimeError(f"Both Together AI and Groq failed") from e

    # If we get here, no API is available
    raise RuntimeError("No LLM API available (both Together and Groq unavailable or failed)")

# -------------------------
# Authentication
# -------------------------
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    """Get the current logged-in user's ID from session"""
    return session.get('user_id')

@app.route("/auth/register", methods=["POST"])
def register():
    """Register a new user account"""
    try:
        data = request.get_json(force=True)
        username = data.get("username", "").strip()
        password = data.get("password", "")

        user_id, error = create_user(username, password)

        if error:
            return jsonify({"error": error}), 400

        # Auto-login after registration
        session['user_id'] = user_id
        session['username'] = username

        logger.info(f"New user registered and logged in: {username}")
        return jsonify({
            "status": "ok",
            "message": "Account created successfully",
            "user": {"user_id": user_id, "username": username}
        })
    except Exception as e:
        logger.exception("Registration error")
        return jsonify({"error": str(e)}), 500

@app.route("/auth/login", methods=["POST"])
def login():
    """Authenticate and log in a user"""
    try:
        data = request.get_json(force=True)
        username = data.get("username", "").strip()
        password = data.get("password", "")

        user_id, user_name = authenticate_user(username, password)

        if not user_id:
            return jsonify({"error": "Invalid username or password"}), 401

        session['user_id'] = user_id
        session['username'] = user_name

        logger.info(f"User logged in: {user_name}")
        return jsonify({
            "status": "ok",
            "message": "Logged in successfully",
            "user": {"user_id": user_id, "username": user_name}
        })
    except Exception as e:
        logger.exception("Login error")
        return jsonify({"error": str(e)}), 500

@app.route("/auth/logout", methods=["POST"])
def logout():
    """Log out the current user"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return jsonify({"status": "ok", "message": "Logged out successfully"})

@app.route("/auth/me", methods=["GET"])
def get_current_user():
    """Get current logged-in user info"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"authenticated": False}), 200

    user = get_user(user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False}), 200

    return jsonify({
        "authenticated": True,
        "user": user
    })

# -------------------------
# Routes
# -------------------------
@app.route("/upload_profile", methods=["POST"])
@login_required
def upload_profile():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400
        profile = save_and_load_profile(file, PDF_UPLOAD_DIR)

        # Persist profile to storage
        user_id = session.get('user_id')
        storage.save_profile(profile, user_id)
        logger.info(f"Persisted patient profile to storage for user {user_id}")

        # Extract and return structured context for frontend display
        patient_context = extract_patient_context(profile)
        patient_summary = format_patient_summary(patient_context)

        logger.info(f"Loaded patient profile: {profile}")
        return jsonify({
            "status": "ok",
            "profile": profile,
            "patient_summary": patient_summary,
            "context": patient_context
        })
    except Exception as e:
        logger.exception("upload_profile error")
        return jsonify({"error": str(e)}), 400

@app.route("/get_patient", methods=["GET"])
@login_required
def get_patient_route():
    # Try to load profile from storage for this user
    user_id = session.get('user_id')
    profile = storage.load_profile(user_id)
    if profile:
        set_profile(profile)  # Set in memory for chat
    else:
        profile = get_profile()  # Fallback to memory
    if profile:
        patient_context = extract_patient_context(profile)
        patient_summary = format_patient_summary(patient_context)
        return jsonify({
            "profile": profile,
            "patient_summary": patient_summary,
            "context": patient_context
        })
    else:
        return jsonify({})

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    global indexed_chunks
    try:
        data = request.get_json(force=True)
        message = data.get("message")
        response_length = data.get("response_length", "normal")
        session_id = data.get("session_id", "default")  # Get or create session ID

        if not message:
            return jsonify({"error": "No message provided"}), 400

        logger.info(f"Chat request (session: {session_id}): {message}, response_length: {response_length}")

        # Get conversation history for this session
        history = get_conversation_history(session_id)
        conversation_context = format_conversation_context(history)

        # Get patient profile first to check for mismatched queries
        patient_profile = get_profile()
        patient_context = extract_patient_context(patient_profile) if patient_profile else {}
        
        # Check if user is asking about wrong cancer type
        mismatch_detected = False
        if patient_context.get('cancer_type'):
            user_cancer_mentions = []
            cancer_keywords = ['breast cancer', 'lung cancer', 'prostate cancer', 'colon cancer', 'colorectal', 'pancreatic', 'ovarian', 'melanoma']
            user_message_lower = message.lower()
            
            for cancer_type in cancer_keywords:
                if cancer_type in user_message_lower:
                    user_cancer_mentions.append(cancer_type)
            
            # If user mentions a different cancer type than their profile
            patient_cancer = patient_context.get('cancer_type', '').lower()
            if user_cancer_mentions:
                for mentioned_cancer in user_cancer_mentions:
                    if mentioned_cancer not in patient_cancer and patient_cancer not in mentioned_cancer:
                        mismatch_detected = True
                        break

        # 1) Retrieve guideline chunks with enhanced search
        retrieved = []
        try:
            retrieved = search_chunks(message, indexed_chunks, top_k=5)
            logger.info("search_chunks returned %d chunks", len(retrieved))
        except Exception:
            logger.exception("search_chunks failed; using empty list")
            retrieved = []

        logger.info(f"Patient profile for chat: {bool(patient_profile)}")

        # 3) Assemble enhanced prompt with mismatch detection and conversation history
        if mismatch_detected:
            # Add a note to the prompt about the mismatch
            message_with_note = f"{message}\n\n[SYSTEM NOTE: User asked about different cancer type than their profile - please address this gently]"
            prompt = assemble_prompt(message_with_note, retrieved, patient_profile, response_length, conversation_context)
        else:
            prompt = assemble_prompt(message, retrieved, patient_profile, response_length, conversation_context)

        logger.info("Assembled prompt length: %d (with %d conversation history items)", len(prompt), len(history))

        # 4) Check if any LLM API is available
        if not (TOGETHER_AVAILABLE or GROQ_AVAILABLE):
            error_msg = "No LLM API available. Please check TOGETHER_API_KEY or GROQ_API_KEY."
            logger.error(error_msg)
            return jsonify({
                "error": error_msg,
                "debug_info": {
                    "together_available": TOGETHER_AVAILABLE,
                    "groq_available": GROQ_AVAILABLE,
                    "has_together_key": bool(TOGETHER_API_KEY),
                    "has_groq_key": bool(GROQ_API_KEY),
                    "retrieved_count": len(retrieved),
                    "has_patient_profile": bool(patient_profile)
                }
            }), 500

        # 5) Call LLM API with enhanced context
        try:
            logger.info("Attempting LLM call...")
            answer, api_used = call_llm(prompt, response_length)
            if not answer:
                raise RuntimeError("LLM returned empty response")

            # Trim any incomplete sentence at the end
            answer = trim_incomplete_sentence(answer)

            logger.info(f"{api_used.upper()} response success - length: %d", len(answer))

            # 6) Validate response for safety and quality
            validation = validate_response(answer, message, patient_context)

            # Enhanced medical validation
            medical_validation = enhanced_medical_validation(answer, message)

            # Log any warnings
            all_warnings = validation['warnings'] + medical_validation['flags']
            if all_warnings:
                logger.warning(f"Response validation warnings: {all_warnings}")

            # Flag high-severity medical issues
            if medical_validation['severity'] == 'high':
                logger.error(f"HIGH SEVERITY medical validation issue: {medical_validation['flags']}")

            # Use enhanced response (with disclaimers if needed)
            final_answer = validation['enhanced_response']

            # 7) Add to conversation history for future context
            add_to_conversation_history(session_id, message, answer)  # Store original answer, not enhanced
            logger.info(f"Added to conversation history for session {session_id}")

            return jsonify({
                "answer": final_answer,
                "api_used": api_used,  # NEW: "together" or "groq"
                "used_groq": api_used == "groq",  # KEEP for backward compatibility
                "retrieved_count": len(retrieved),
                "response_length": response_length,
                "patient_context_used": bool(patient_context),
                "mismatch_detected": mismatch_detected,
                "validation_warnings": all_warnings,  # Include all warnings for debugging
                "medical_safety_check": medical_validation['safe'],  # NEW
                "conversation_length": len(history) + 1,  # New conversation length
                "debug_info": {
                    "api_used": api_used,  # NEW
                    "together_available": TOGETHER_AVAILABLE,  # NEW
                    "groq_available": GROQ_AVAILABLE,  # NEW
                    "retrieved_count": len(retrieved),
                    "has_patient_profile": bool(patient_profile),
                    "prompt_length": len(prompt),
                    "response_length_setting": response_length,
                    "patient_cancer_type": patient_context.get('cancer_type', 'none'),
                    "patient_stage": patient_context.get('stage', 'none'),
                    "mismatch_detected": mismatch_detected,
                    "query_type": classify_query_type(message),
                    "validation_passed": validation['is_valid'],
                    "medical_validation_passed": medical_validation['safe'],  # NEW
                    "medical_validation_severity": medical_validation['severity'],  # NEW
                    "session_id": session_id
                }
            })
        except Exception as e:
            logger.exception(f"LLM API generation failed: {e}")
            return jsonify({
                "error": f"LLM API failed: {str(e)}",
                "debug_info": {
                    "together_available": TOGETHER_AVAILABLE,
                    "groq_available": GROQ_AVAILABLE,
                    "has_together_key": bool(TOGETHER_API_KEY),
                    "has_groq_key": bool(GROQ_API_KEY),
                    "retrieved_count": len(retrieved),
                    "has_patient_profile": bool(patient_profile),
                    "error_details": str(e)
                }
            }), 500

    except Exception as e:
        logger.exception("Unexpected /chat error: %s", e)
        return jsonify({"error": str(e)}), 500

# -------------------------
# Data Sources Endpoint (read-only)
# -------------------------
@app.route("/data_sources", methods=["GET"])
def get_data_sources():
    """Get list of PDF data sources from the data folder with last-updated dates"""
    try:
        tracker = load_chunk_tracker()
        tracked_files = tracker.get("files", {})

        data_sources = []
        for filename in os.listdir(DATA_DIR):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(DATA_DIR, filename)
                file_stat = os.stat(filepath)

                # Get chunk count from tracker if available
                tracked_info = tracked_files.get(filename, {})
                chunk_count = tracked_info.get("chunk_count", 0)
                processed_at = tracked_info.get("processed_at")

                data_sources.append({
                    "filename": filename,
                    "chunk_count": chunk_count,
                    "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "processed_at": processed_at,
                    "size_bytes": file_stat.st_size
                })

        # Sort by filename
        data_sources.sort(key=lambda x: x["filename"].lower())

        return jsonify({
            "status": "ok",
            "data_sources": data_sources,
            "total_count": len(data_sources),
            "total_chunks": len(indexed_chunks),
            "last_scan": tracker.get("last_scan")
        })
    except Exception as e:
        logger.exception("get_data_sources error")
        return jsonify({"error": str(e)}), 500


@app.route("/clear_profile", methods=["POST"])
@login_required
def clear_profile():
    """Clear stored patient profile"""
    try:
        user_id = session.get('user_id')
        storage.clear_profile(user_id)
        set_profile({})
        logger.info(f"Cleared patient profile from memory and storage for user {user_id}")
        return jsonify({"status": "ok", "message": "Profile cleared"})
    except Exception as e:
        logger.exception("clear_profile error")
        return jsonify({"error": str(e)}), 500

@app.route("/debug", methods=["GET"])
def debug_status():
    profile = get_profile()
    patient_context = extract_patient_context(profile) if profile else {}

    return jsonify({
        "together_available": TOGETHER_AVAILABLE,  # NEW
        "together_has_key": bool(TOGETHER_API_KEY),  # NEW
        "groq_available": GROQ_AVAILABLE,
        "groq_has_key": bool(GROQ_API_KEY),
        "primary_api": "together" if TOGETHER_AVAILABLE else "groq",  # NEW
        "indexed_chunks": len(indexed_chunks),
        "patient_profile": bool(profile),
        "patient_context": patient_context,
        "environment_vars": {
            "TOGETHER_API_KEY": "SET" if os.environ.get("TOGETHER_API_KEY") else "NOT_SET",
            "GROQ_API_KEY": "SET" if os.environ.get("GROQ_API_KEY") else "NOT_SET"
        }
    })

# -------------------------
# CORS
# -------------------------
@app.route("/", defaults={"path": ""}, methods=["OPTIONS"])
@app.route("/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    return ("", 200)

@app.after_request
def apply_cors(response):
    origin = request.headers.get("Origin")
    if _origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    logger.info("Starting Wondr Link app on %s:%s", APP_HOST, APP_PORT)
    logger.info(f"Debug info - Groq: {GROQ_AVAILABLE}")
    app.run(host=APP_HOST, port=5030, debug=DEBUG)