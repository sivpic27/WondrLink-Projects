# llm_utils.py
import os
import re
import logging
import json
from typing import List, Dict, Any, Tuple, Optional, Union

logger = logging.getLogger("llm_utils")

# =============================================================================
# PII DETECTION AND FILTERING (Compliance Feature)
# =============================================================================

# PII patterns to detect and filter from user queries
PII_PATTERNS = {
    'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # Social Security Number
    'dob': r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})\b',  # Date patterns
    'phone': r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone numbers
    'email': r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
    'address': r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b',  # Street addresses
    'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',  # Credit card numbers
}

# PII instruction to add to system prompt
PII_INSTRUCTION = """
PII HANDLING (CRITICAL):
- Do NOT acknowledge, repeat, or store any personally identifiable information such as:
  * Full names (last names, family names)
  * Dates of birth or specific birth dates
  * Social Security numbers
  * Phone numbers
  * Email addresses
  * Street addresses
  * Credit card numbers
- If the user provides such information, do NOT include it in your response
- Only use the patient's first name if provided in their profile
- Focus on the medical content of the question, ignoring any PII
"""


def detect_pii(text: str) -> Dict[str, List[str]]:
    """
    Detect PII in user input.

    Args:
        text: The text to scan for PII

    Returns:
        Dict of detected PII types and their matched values
    """
    detected = {}

    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected[pii_type] = matches

    return detected


def sanitize_query(query: str) -> Tuple[str, List[str]]:
    """
    Remove PII from user query before sending to LLM.

    Args:
        query: The user's query text

    Returns:
        Tuple of (sanitized_query, list_of_warnings)
    """
    sanitized = query
    warnings = []

    # Remove SSN
    if re.search(PII_PATTERNS['ssn'], query):
        sanitized = re.sub(PII_PATTERNS['ssn'], '[REMOVED]', sanitized)
        warnings.append("SSN detected and removed")

    # Remove DOB patterns (but be careful not to remove treatment cycle dates)
    # Only remove if it looks like a birthdate context
    dob_context = re.search(r'\b(?:born|birthday|dob|date of birth)\s*(?:is|:)?\s*' + PII_PATTERNS['dob'], query, re.IGNORECASE)
    if dob_context:
        sanitized = re.sub(r'\b(?:born|birthday|dob|date of birth)\s*(?:is|:)?\s*' + PII_PATTERNS['dob'], '[DOB REMOVED]', sanitized, flags=re.IGNORECASE)
        warnings.append("Date of birth detected and removed")

    # Remove phone numbers
    if re.search(PII_PATTERNS['phone'], query):
        sanitized = re.sub(PII_PATTERNS['phone'], '[PHONE REMOVED]', sanitized)
        warnings.append("Phone number detected and removed")

    # Remove emails
    if re.search(PII_PATTERNS['email'], query):
        sanitized = re.sub(PII_PATTERNS['email'], '[EMAIL REMOVED]', sanitized)
        warnings.append("Email detected and removed")

    # Remove street addresses
    if re.search(PII_PATTERNS['address'], query, re.IGNORECASE):
        sanitized = re.sub(PII_PATTERNS['address'], '[ADDRESS REMOVED]', sanitized, flags=re.IGNORECASE)
        warnings.append("Address detected and removed")

    # Remove credit card numbers
    if re.search(PII_PATTERNS['credit_card'], query):
        sanitized = re.sub(PII_PATTERNS['credit_card'], '[CARD REMOVED]', sanitized)
        warnings.append("Credit card number detected and removed")

    return sanitized, warnings

# Token counting with tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    # Use cl100k_base encoding (same as GPT-4, works well for Llama models)
    TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")
    logger.info("tiktoken initialized successfully")
except ImportError:
    TIKTOKEN_AVAILABLE = False
    TOKEN_ENCODING = None
    logger.warning("tiktoken not available, using approximate token counting")

# LLM clients - lazy initialization to ensure env vars are loaded first
_groq_client = None
_together_client = None
_groq_initialized = False
_together_initialized = False


def _init_groq():
    """Lazily initialize Groq client on first use."""
    global _groq_client, _groq_initialized
    if _groq_initialized:
        return _groq_client
    _groq_initialized = True
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            _groq_client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully")
        else:
            logger.warning("GROQ_API_KEY not set in environment")
    except ImportError:
        logger.warning("groq package not installed")
    except Exception as e:
        logger.warning(f"Groq initialization failed: {e}")
    return _groq_client


def _init_together():
    """Lazily initialize Together client on first use."""
    global _together_client, _together_initialized
    if _together_initialized:
        return _together_client
    _together_initialized = True
    try:
        from together import Together
        api_key = os.environ.get("TOGETHER_API_KEY")
        if api_key:
            _together_client = Together(api_key=api_key)
            logger.info("Together client initialized successfully")
        else:
            logger.warning("TOGETHER_API_KEY not set in environment")
    except ImportError:
        logger.warning("together package not installed")
    except Exception as e:
        logger.warning(f"Together initialization failed: {e}")
    return _together_client


def get_groq_client():
    """Get Groq client, initializing if needed."""
    return _init_groq()


def get_together_client():
    """Get Together client, initializing if needed."""
    return _init_together()


def is_groq_available():
    """Check if Groq is available."""
    return get_groq_client() is not None


def is_together_available():
    """Check if Together is available."""
    return get_together_client() is not None


def get_llm_status() -> Dict[str, Any]:
    """Get the status of LLM providers."""
    together_avail = is_together_available()
    groq_avail = is_groq_available()
    return {
        "together_available": together_avail,
        "groq_available": groq_avail,
        "primary_api": "together" if together_avail else "groq" if groq_avail else None
    }


# Token budget constants
TOKEN_BUDGET = {
    'system': 400,      # System message (increased for enhanced prompts)
    'patient': 400,     # Patient context
    'chunks': 1500,     # Retrieved guideline chunks
    'history': 400,     # Conversation history
    'question': 100,    # User question
    'instructions': 200,# Response instructions
    'response': 1200    # Buffer for response
}


# =============================================================================
# ENHANCED SYSTEM PROMPT - Comprehensive behavioral guidelines
# =============================================================================

ENHANCED_SYSTEM_PROMPT = """ROLE: You are WondrLink, a Colon Cancer AI Concierge - a patient education assistant specializing in colon cancer. You provide evidence-based information in plain language to help patients and caregivers understand their diagnosis and treatment.

PATIENT PROFILE USAGE:
- You have access to the patient's full medical profile. Always use this information to personalize your answers.
- If the user asks about their profile, who they are, or what you know about them, provide a warm summary of the information you have on file.
- Proactively incorporate biomarker implications when relevant:
  * KRAS/NRAS mutations → EGFR inhibitors (cetuximab, panitumumab) are ineffective
  * MSS (Microsatellite Stable) → Checkpoint inhibitors (immunotherapy) unlikely to help
  * MSI-H (High) → May benefit from immunotherapy
  * BRAF V600E → May respond to targeted therapy combinations

URGENCY CALIBRATION:
- EMERGENCY (call 911/go to ER immediately): fever >100.4°F during chemo, severe bleeding, difficulty breathing, chest pain, severe abdominal pain, signs of bowel obstruction, confusion, seizure
- URGENT (contact oncologist same day): worsening neuropathy, new or worsening symptoms, uncontrolled nausea/vomiting, inability to eat/drink for 24+ hours, new pain
- ROUTINE: general questions, lifestyle advice, emotional support, informational queries

RESPONSE GUIDELINES:
1. Lead with actionable information, not disclaimers
2. Use "discuss with your medical team" as a secondary point, not the primary answer
3. For WORSENING symptoms:
   - Flag as requiring PROMPT attention (not just "talk to your doctor soon")
   - Provide interim management tips while awaiting medical consultation
   - Mention that dose modifications are COMMON and EXPECTED - patients shouldn't fear reporting symptoms
4. Be honest about prognosis:
   - Oxaliplatin neuropathy: Acute (cold-triggered) usually resolves; chronic can be permanent in ~10-15%
   - Don't hedge excessively - patients deserve clear, evidence-based expectations
5. For emotional questions: Validate feelings, mention oncology social workers and support groups

SAFETY RULES:
1. Never diagnose or recommend specific treatments - only discuss possible options
2. For emergency symptoms: Immediately advise calling 911 or going to ER
3. For urgent symptoms: Advise contacting oncologist the same day
4. Always include "discuss with your medical team" for treatment decisions - but as supporting context, not the main answer

TONE: Warm, empathetic, and empowering. Acknowledge emotional difficulty when appropriate. Use "you" and "your" to personalize. Avoid medical jargon unless explaining it."""


# =============================================================================
# FOLLOW-UP QUESTION DIVERSITY
# =============================================================================

FOLLOW_UP_INSTRUCTION = """
FOLLOW-UP SUGGESTIONS:
At the end of your response, suggest 2-3 related questions the patient might want to ask next.
These should cover DIFFERENT aspects of their care (not all about the same drug/treatment):
- A question about a different treatment option or drug
- A question about side effect management or quality of life
- A question about practical concerns or emotional support

Format as: "You might also want to ask about: • [Question 1] • [Question 2] • [Question 3]"
"""


# =============================================================================
# SYMPTOM URGENCY DETECTION
# =============================================================================

CONCERNING_SYMPTOM_PATTERNS = {
    'emergency_fever': {
        'keywords': ['fever', '100.4', '101', '102', '103', 'temperature', 'chills'],
        'requires_chemo_context': True,
        'urgency': 'emergency',
        'guidance': '🚨 EMERGENCY: Fever during chemotherapy is a medical emergency due to risk of neutropenic sepsis. Contact your oncologist immediately or go to the ER. Do not wait.'
    },
    'emergency_breathing': {
        'keywords': ['can\'t breathe', 'difficulty breathing', 'short of breath', 'chest pain', 'chest tightness'],
        'requires_chemo_context': False,
        'urgency': 'emergency',
        'guidance': '🚨 EMERGENCY: These symptoms require immediate medical attention. Call 911 or go to the nearest emergency room immediately.'
    },
    'emergency_bleeding': {
        'keywords': ['severe bleeding', 'blood in stool', 'vomiting blood', 'heavy bleeding'],
        'requires_chemo_context': False,
        'urgency': 'emergency',
        'guidance': '🚨 EMERGENCY: Significant bleeding requires immediate medical evaluation. Go to the ER or call 911.'
    },
    'urgent_worsening': {
        'keywords': ['worse', 'worsening', 'getting worse', 'increased', 'more severe', 'progressing'],
        'requires_chemo_context': False,
        'urgency': 'urgent',
        'guidance': '⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don\'t hesitate to report changes.'
    },
    'urgent_neuropathy': {
        'keywords': ['tingling worse', 'numbness worse', 'neuropathy worse', 'fingers worse', 'toes worse', 'can\'t feel', 'dropping things'],
        'requires_chemo_context': False,
        'urgency': 'urgent',
        'guidance': '⚠️ URGENT: Worsening neuropathy during oxaliplatin-based therapy requires prompt evaluation. Contact your oncology team within 24-48 hours. Dose modifications are COMMON and can help prevent permanent nerve damage. Call the main clinic line during business hours or the after-hours line if evening/weekend. If you don\'t hear back within a few hours, call again. In the meantime: avoid cold exposure, use warm (not cold) beverages, and wear gloves when handling frozen items.'
    },
    'urgent_dehydration': {
        'keywords': ['can\'t eat', 'can\'t drink', 'not eating', 'not drinking', 'severe nausea', 'severe vomiting', 'can\'t keep anything down'],
        'requires_chemo_context': False,
        'urgency': 'urgent',
        'guidance': '⚠️ URGENT: Inability to eat or drink for more than 24 hours can lead to dehydration and requires medical attention. Contact your oncology team today.'
    }
}


def detect_symptom_urgency(message: str, patient_context: dict = None) -> dict:
    """
    Detect if user message describes concerning symptoms requiring escalation.

    Returns dict with:
    - detected: bool
    - urgency: 'emergency' | 'urgent' | None
    - pattern: str (which pattern matched)
    - guidance: str (specific guidance to prepend to response)
    """
    if patient_context is None:
        patient_context = {}

    message_lower = message.lower()
    on_chemo = bool(patient_context.get('current_treatments'))

    # Check patterns in priority order (emergencies first)
    for pattern_name, pattern in CONCERNING_SYMPTOM_PATTERNS.items():
        # Check if any keywords match
        if any(kw in message_lower for kw in pattern['keywords']):
            # Some patterns only apply during chemo
            if pattern.get('requires_chemo_context') and not on_chemo:
                continue

            return {
                'detected': True,
                'pattern': pattern_name,
                'urgency': pattern['urgency'],
                'guidance': pattern['guidance']
            }

    return {'detected': False, 'urgency': None, 'pattern': None, 'guidance': None}


# =============================================================================
# PATIENT RESOURCES
# =============================================================================

# =============================================================================
# CURATED PATIENT RESOURCES - Contextually referenced based on query type
# =============================================================================
PATIENT_RESOURCES = {
    # General Information - staging, treatment overviews, guidelines
    'general': [
        {'name': 'National Cancer Institute', 'url': 'https://www.cancer.gov/types/colorectal', 'desc': 'Comprehensive cancer info'},
        {'name': 'American Cancer Society', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer.html', 'desc': 'Patient-friendly overviews'},
        {'name': 'NCCN Patient Guidelines', 'url': 'https://www.nccn.org/patients/guidelines/content/PDF/colon-patient.pdf', 'desc': 'Evidence-based treatment guidelines'},
    ],

    # Advocacy Organizations - patient advocacy, resources
    'advocacy': [
        {'name': 'Colorectal Cancer Alliance', 'url': 'https://colorectalcancer.org', 'desc': 'Patient support and resources'},
        {'name': 'Fight Colorectal Cancer', 'url': 'https://fightcolorectalcancer.org', 'desc': 'Advocacy and patient resources'},
        {'name': 'Colon Cancer Coalition', 'url': 'https://coloncancercoalition.org', 'desc': 'Awareness and screening'},
    ],

    # Support Communities - peer support, online communities
    'support': [
        {'name': 'Colontown', 'url': 'https://colontown.org', 'desc': 'Active peer support community (11,000+ members)'},
        {'name': 'Colontown University', 'url': 'https://learn.colontown.org', 'desc': 'Free patient education courses'},
        {'name': 'Blue Hope Nation (CCA)', 'url': 'https://colorectalcancer.org/bluehq', 'desc': 'Online support hub'},
        {'name': 'Smart Patients CRC', 'url': 'https://www.smartpatients.com/communities/colorectal-cancer', 'desc': 'Patient discussion community'},
    ],

    # Clinical Trials - trial search, trial finder
    'clinical_trials': [
        {'name': 'ClinicalTrials.gov', 'url': 'https://clinicaltrials.gov', 'desc': 'NIH database of all trials'},
        {'name': 'NCI Trial Search', 'url': 'https://www.cancer.gov/research/participate/clinical-trials-search', 'desc': 'National Cancer Institute trials'},
        {'name': 'CCA Trial Finder', 'url': 'https://colorectalcancer.org/treatment/types-treatment/clinical-trials/clinical-trial-finder', 'desc': 'Simplified trial search'},
    ],

    # Treatment Information - surgery, chemo, targeted therapy, immunotherapy
    'treatment': [
        {'name': 'ACS Colon Treatment', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/treating.html', 'desc': 'Treatment overview'},
        {'name': 'NCI Treatment (PDQ)', 'url': 'https://www.cancer.gov/types/colorectal/patient/colon-treatment-pdq', 'desc': 'Detailed treatment info'},
        {'name': 'Chemocare Drug Info', 'url': 'https://chemocare.com/chemotherapy/drug-info/default.aspx', 'desc': 'Chemotherapy drug details'},
    ],

    # Side Effects (General) - chemo side effects, symptom management
    'side_effects_chemo': [
        {'name': 'Chemocare Side Effects', 'url': 'https://chemocare.com/chemotherapy/side-effects/default.aspx', 'desc': 'Drug-specific side effects'},
        {'name': 'NCI Side Effects', 'url': 'https://www.cancer.gov/about-cancer/treatment/side-effects', 'desc': 'Managing treatment effects'},
        {'name': 'ACS Side Effects', 'url': 'https://www.cancer.org/cancer/managing-cancer/side-effects.html', 'desc': 'Side effect management'},
    ],

    # Neuropathy - tingling, numbness, nerve damage
    'neuropathy': [
        {'name': 'Foundation for PN', 'url': 'https://www.foundationforpn.org', 'desc': 'Neuropathy-specific support'},
        {'name': 'Chemocare Neuropathy', 'url': 'https://chemocare.com/chemotherapy/side-effects/peripheral-neuropathy.aspx', 'desc': 'Management tips'},
    ],

    # Fatigue - tiredness, energy, exhaustion
    'fatigue': [
        {'name': 'Cancer.org Fatigue', 'url': 'https://www.cancer.org/treatment/treatments-and-side-effects/physical-side-effects/fatigue.html', 'desc': 'Fatigue management'},
        {'name': 'NCI Late Effects', 'url': 'https://www.cancer.gov/about-cancer/coping/survivorship/late-effects', 'desc': 'Long-term effects'},
    ],

    # Nausea - vomiting, appetite, anti-nausea
    'nausea': [
        {'name': 'Chemocare Nausea', 'url': 'https://chemocare.com/chemotherapy/side-effects/nausea-and-vomiting.aspx', 'desc': 'Nausea management'},
    ],

    # Emotional & Mental Health - anxiety, depression, coping, family
    'emotional': [
        {'name': 'Cancer Support Community', 'url': 'https://www.cancersupportcommunity.org', 'desc': 'Free support groups'},
        {'name': 'CancerCare Counseling', 'url': 'https://www.cancercare.org', 'desc': 'Free counseling services'},
        {'name': 'Imerman Angels', 'url': 'https://imermanangels.org', 'desc': 'Free 1-on-1 cancer support'},
        {'name': 'Cancer Hope Network', 'url': 'https://www.cancerhopenetwork.org', 'desc': 'Peer support matching'},
    ],

    # Financial Assistance - costs, copays, insurance
    'financial': [
        {'name': 'Patient Advocate Foundation', 'url': 'https://www.patientadvocate.org', 'desc': 'Insurance and financial help'},
        {'name': 'CancerCare Financial', 'url': 'https://www.cancercare.org/financial', 'desc': 'Financial assistance programs'},
        {'name': 'CCA Financial Resources', 'url': 'https://colorectalcancer.org/resources-support/resources/financial-assistance', 'desc': 'CRC-specific financial help'},
        {'name': 'NeedyMeds', 'url': 'https://www.needymeds.org', 'desc': 'Medication assistance finder'},
        {'name': 'PAN Foundation', 'url': 'https://www.panfoundation.org', 'desc': 'Co-pay assistance'},
    ],

    # Survivorship - after treatment, long-term, follow-up
    'survivorship': [
        {'name': 'ACS Survivorship', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/after-treatment/follow-up.html', 'desc': 'Follow-up care guide'},
        {'name': 'Cancer Survivors Network', 'url': 'https://csn.cancer.org', 'desc': 'ACS peer support'},
        {'name': 'NCI Follow-Up Care', 'url': 'https://www.cancer.gov/about-cancer/coping/survivorship/follow-up-care', 'desc': 'Survivorship care planning'},
    ],

    # Screening - colonoscopy, FIT test, prevention, early detection
    'screening': [
        {'name': 'ACS Screening Guidelines', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/detection-diagnosis-staging/acs-recommendations.html', 'desc': 'Screening recommendations'},
        {'name': 'USPSTF Guidelines', 'url': 'https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/colorectal-cancer-screening', 'desc': 'Federal screening guidelines'},
        {'name': 'CDC Screen for Life', 'url': 'https://www.cdc.gov/colorectal-cancer/screening/index.html', 'desc': 'CDC screening resources'},
    ],

    # Diagnosis - symptoms, staging, biomarker testing
    'diagnosis': [
        {'name': 'ACS Diagnosis', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/detection-diagnosis-staging/how-diagnosed.html', 'desc': 'How CRC is diagnosed'},
        {'name': 'ACS Staging', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/detection-diagnosis-staging/staged.html', 'desc': 'Cancer staging explained'},
        {'name': 'Biomarker Testing (CCA)', 'url': 'https://colorectalcancer.org/treatment/biomarker-testing', 'desc': 'Biomarker testing guide'},
        {'name': 'NCI Biomarkers', 'url': 'https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment', 'desc': 'Testing for treatment'},
    ],

    # Nutrition - diet, eating, weight, dietitian
    'nutrition': [
        {'name': 'Oncology Nutrition (AND)', 'url': 'https://www.oncologynutrition.org', 'desc': 'Dietitian resources'},
        {'name': 'Cancer.org Nutrition', 'url': 'https://www.cancer.org/treatment/survivorship-during-and-after-treatment/staying-active/nutrition.html', 'desc': 'Nutrition during treatment'},
    ],

    # Ostomy - colostomy, ileostomy, stoma care
    'ostomy': [
        {'name': 'UOAA', 'url': 'https://www.ostomy.org', 'desc': 'Ostomy education and support'},
        {'name': 'UOAA Support Groups', 'url': 'https://www.ostomy.org/support-group-finder/', 'desc': 'Find local support'},
        {'name': 'ACS Colostomy Guide', 'url': 'https://www.cancer.org/cancer/managing-cancer/treatment-types/surgery/ostomies/colostomy.html', 'desc': 'Living with colostomy'},
        {'name': 'MSK Ostomy Care', 'url': 'https://www.mskcc.org/cancer-care/patient-education/caring-for-your-ileostomy-colostomy', 'desc': 'Practical ostomy care'},
    ],

    # Hereditary & Genetic - Lynch syndrome, genetic testing, family history
    'hereditary': [
        {'name': 'NCI Genetics (PDQ)', 'url': 'https://www.cancer.gov/types/colorectal/patient/colorectal-genetics-pdq', 'desc': 'Genetics of CRC'},
        {'name': 'Find Genetic Counselor', 'url': 'https://www.findageneticcounselor.com', 'desc': 'NSGC counselor finder'},
        {'name': 'Lynch Syndrome Info', 'url': 'https://www.cancer.net/cancer-types/lynch-syndrome', 'desc': 'Lynch syndrome guide'},
        {'name': 'FORCE', 'url': 'https://www.facingourrisk.org', 'desc': 'Hereditary cancer support'},
    ],

    # Helplines - phone support, crisis lines
    'helplines': [
        {'name': 'American Cancer Society', 'url': 'tel:1-800-227-2345', 'desc': '1-800-227-2345 (24/7)'},
        {'name': 'CCA Helpline', 'url': 'tel:1-877-422-2030', 'desc': '1-877-422-2030 (M-F 9am-9pm ET)'},
        {'name': 'NCI Cancer Info', 'url': 'tel:1-800-422-6237', 'desc': '1-800-422-6237 (M-F 9am-9pm ET)'},
        {'name': 'Cancer Support Helpline', 'url': 'tel:1-888-793-9355', 'desc': '1-888-793-9355 (free, confidential)'},
    ],

    # Caregiver resources
    'caregiver': [
        {'name': 'ACS Caregiver Guide', 'url': 'https://www.cancer.org/cancer/caregivers.html', 'desc': 'Caregiver resource guide'},
        {'name': 'NCI Caregiver Support', 'url': 'https://www.cancer.gov/about-cancer/coping/caregiver-support', 'desc': 'Support for caregivers'},
        {'name': 'Caregiver Action Network', 'url': 'https://www.caregiveraction.org', 'desc': 'Caregiver advocacy'},
    ],

    # Surgery specific
    'surgery': [
        {'name': 'ACS Colon Surgery', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/treating/surgery.html', 'desc': 'Surgery for colon cancer'},
        {'name': 'ASCRS Patient Info', 'url': 'https://www.fascrs.org/patients', 'desc': 'Colorectal surgery info'},
    ],

    # Prevention - risk reduction, lifestyle
    'prevention': [
        {'name': 'ACS Prevention', 'url': 'https://www.cancer.org/cancer/colon-rectal-cancer/causes-risks-prevention/prevention.html', 'desc': 'CRC prevention'},
        {'name': 'NCI Prevention (PDQ)', 'url': 'https://www.cancer.gov/types/colorectal/patient/colorectal-prevention-pdq', 'desc': 'Prevention strategies'},
        {'name': 'CCA Risk Factors', 'url': 'https://colorectalcancer.org/prevention-screening/risk-factors', 'desc': 'Risk factor info'},
    ],
}


def get_relevant_resources(query_type: str, include_resources: bool = True, query: str = "") -> str:
    """
    Return formatted resource links based on query type and specific symptoms.

    Args:
        query_type: One of 'treatment', 'side_effect', 'emotional', 'general', 'survivorship', etc.
        include_resources: Whether to include resources (can be disabled for brief responses)
        query: The original user query for symptom-specific resource matching

    Returns:
        Formatted string with relevant resource links, or empty string
    """
    if not include_resources:
        return ""

    query_lower = query.lower() if query else ""

    # Keyword-specific resource selection (prioritized matching)
    if 'neuropathy' in query_lower or 'tingling' in query_lower or 'numbness' in query_lower:
        categories = ['neuropathy', 'side_effects_chemo']
    elif 'nausea' in query_lower or 'vomit' in query_lower:
        categories = ['nausea', 'side_effects_chemo']
    elif 'fatigue' in query_lower or 'tired' in query_lower or 'exhausted' in query_lower:
        categories = ['fatigue', 'side_effects_chemo']
    elif 'ostomy' in query_lower or 'colostomy' in query_lower or 'ileostomy' in query_lower or 'stoma' in query_lower:
        categories = ['ostomy', 'support']
    elif 'screening' in query_lower or 'colonoscopy' in query_lower or 'fit test' in query_lower:
        categories = ['screening', 'general']
    elif 'prevention' in query_lower or 'prevent' in query_lower or 'risk factor' in query_lower:
        categories = ['prevention', 'screening']
    elif 'diet' in query_lower or 'nutrition' in query_lower or 'eating' in query_lower or 'food' in query_lower or 'weight' in query_lower:
        categories = ['nutrition', 'support']
    elif 'trial' in query_lower or 'clinical' in query_lower or 'study' in query_lower:
        categories = ['clinical_trials', 'support']
    elif 'financial' in query_lower or 'cost' in query_lower or 'insurance' in query_lower or 'afford' in query_lower or 'pay' in query_lower:
        categories = ['financial', 'support']
    elif 'genetic' in query_lower or 'hereditary' in query_lower or 'lynch' in query_lower or 'family history' in query_lower:
        categories = ['hereditary', 'general']
    elif 'surgery' in query_lower or 'resection' in query_lower or 'operation' in query_lower:
        categories = ['surgery', 'treatment']
    elif 'caregiver' in query_lower or 'family member' in query_lower or 'spouse' in query_lower or 'loved one' in query_lower:
        categories = ['caregiver', 'emotional']
    elif 'helpline' in query_lower or 'call' in query_lower or 'phone' in query_lower or 'talk to someone' in query_lower:
        categories = ['helplines', 'emotional']
    elif 'support group' in query_lower or 'community' in query_lower or 'others' in query_lower or 'connect' in query_lower:
        categories = ['support', 'emotional']
    elif 'biomarker' in query_lower or 'kras' in query_lower or 'msi' in query_lower or 'braf' in query_lower or 'testing' in query_lower:
        categories = ['diagnosis', 'treatment']
    elif 'stage' in query_lower or 'staging' in query_lower or 'diagnosis' in query_lower or 'diagnosed' in query_lower:
        categories = ['diagnosis', 'general']
    elif any(word in query_lower for word in ['anxious', 'anxiety', 'scared', 'fear', 'worried', 'depressed', 'depression', 'cope', 'coping', 'mental']):
        categories = ['emotional', 'helplines']
    else:
        # Fall back to query type mapping
        type_mapping = {
            'emotional': ['emotional', 'helplines'],
            'treatment': ['treatment', 'clinical_trials'],
            'side_effect': ['side_effects_chemo', 'support'],
            'prognosis': ['support', 'general'],
            'diagnosis': ['diagnosis', 'general'],
            'general': ['general', 'advocacy'],
            'survivorship': ['survivorship', 'support'],
            'screening': ['screening', 'prevention']
        }
        categories = type_mapping.get(query_type, ['general'])

    resources = []

    for cat in categories:
        if cat in PATIENT_RESOURCES:
            resources.extend(PATIENT_RESOURCES[cat][:2])  # Max 2 per category

    if not resources:
        return ""

    # Limit to 5 resources max to provide more helpful links
    resources = resources[:5]

    # Format as pipe-separated for compact display
    links = [f'<a href="{r["url"]}" target="_blank" rel="noopener noreferrer">{r["name"]}</a>' for r in resources]
    formatted = "\n\n📚 " + " | ".join(links)

    return formatted


# =============================================================================
# OXALIPLATIN NEUROPATHY GUIDANCE
# =============================================================================

OXALIPLATIN_NEUROPATHY_GUIDANCE = """
IMPORTANT - For oxaliplatin-related neuropathy:
- ACUTE (cold-triggered): Usually resolves between cycles. Immediate tips: Avoid cold drinks/foods, wear gloves for frozen items, use room-temperature or warm beverages.
- CHRONIC (cumulative tingling/numbness): Dose modifications are COMMON and EXPECTED. Report worsening promptly - this helps prevent permanent damage.
- PROGNOSIS: Acute symptoms typically resolve fully. Chronic sensory neuropathy improves in most patients after stopping oxaliplatin, but can be PERMANENT in approximately 10-15% of patients.
- INTERIM MANAGEMENT: Avoid extreme cold, consider warm compresses for hands/feet, report if symptoms interfere with daily activities (buttoning shirts, writing, walking).
"""


# =============================================================================
# STANDARD CHEMOTHERAPY CYCLE GUIDANCE (Step 2)
# =============================================================================

STANDARD_CYCLE_GUIDANCE = {
    'FOLFOX': {
        'Adjuvant': {
            'expected_cycles': 12,
            'duration': '6 months',
            'note': 'Standard adjuvant FOLFOX is 12 cycles over 6 months. Some centers use 6 cycles of a modified schedule.'
        },
        'Metastatic': {
            'expected_cycles': None,
            'duration': 'ongoing',
            'note': 'Treatment continues until disease progression or intolerance.'
        }
    },
    'FOLFIRI': {
        'Adjuvant': {
            'expected_cycles': 12,
            'duration': '6 months',
            'note': 'Standard adjuvant FOLFIRI is 12 cycles over 6 months.'
        },
        'Metastatic': {
            'expected_cycles': None,
            'duration': 'ongoing',
            'note': 'Treatment continues until disease progression or intolerance.'
        }
    },
    'CAPOX': {
        'Adjuvant': {
            'expected_cycles': 8,
            'duration': '6 months',
            'note': 'Standard adjuvant CAPOX (XELOX) is 8 cycles over 6 months.'
        }
    }
}


# =============================================================================
# TREATMENT RESPONSE STRUCTURE
# =============================================================================

TREATMENT_RESPONSE_STRUCTURE = """
TREATMENT DISCUSSION FORMAT:
When discussing treatment options for this patient, structure your response as follows:

1. PRIMARY OPTION: Identify the most commonly used/first-line treatment for their specific situation (considering cancer type, stage, and biomarkers). Explain briefly why it's typically preferred.

2. ALTERNATIVES (2-3): List backup treatments that may be considered if:
   - The primary option isn't well tolerated
   - The patient doesn't respond to primary treatment
   - There are specific contraindications based on their profile

For EACH option mentioned, briefly note:
- How it works (in simple terms)
- Key side effects to expect
- Why it might or might not be suitable for THIS patient based on their biomarkers

Remind the patient that treatment selection involves many factors and should be discussed with their oncologist.
"""


def get_cycle_context(regimen: str, line: str, current_cycle: int) -> str:
    """Generate treatment progress context for prompts."""
    if not regimen or not current_cycle:
        return ""

    # Normalize regimen name (handle "FOLFOX + Bevacizumab")
    base_regimen = regimen.split('+')[0].strip().upper()

    guidance = STANDARD_CYCLE_GUIDANCE.get(base_regimen, {}).get(line)
    if not guidance:
        return f"Currently on cycle {current_cycle}"

    expected = guidance.get('expected_cycles')
    if expected and current_cycle:
        remaining = max(0, expected - current_cycle)
        return f"Cycle {current_cycle} of {expected} ({guidance['duration']}). {remaining} cycles remaining. {guidance.get('note', '')}"
    elif current_cycle:
        return f"Cycle {current_cycle}. {guidance.get('note', '')}"
    return ""


# =============================================================================
# COLONOSCOPY SURVEILLANCE GUIDELINES (Step 4)
# =============================================================================

COLONOSCOPY_SURVEILLANCE_GUIDELINES = """
POST-COLON CANCER COLONOSCOPY SCHEDULE (NCCN/ACS Guidelines):
- First colonoscopy: 1 year after surgery
- If normal at 1 year: Repeat at 3 years
- If normal at 3 years: Every 5 years thereafter
- If polyps found: May need more frequent surveillance (every 1-3 years depending on findings)
- Always discuss your specific schedule with your oncologist based on your individual situation.
"""


# =============================================================================
# FIT TEST GUIDANCE (V4 Step 3)
# =============================================================================

FIT_TEST_GUIDANCE = """
ABOUT FIT (FECAL IMMUNOCHEMICAL TEST):
- FIT detects hidden blood in stool, which can indicate:
  * Cancer
  * Advanced adenomas (precancerous polyps)
  * Other GI bleeding sources
- A positive FIT test requires follow-up colonoscopy to determine the cause
- FIT is an effective screening tool when colonoscopy isn't feasible
- FIT should be done annually for average-risk screening
- FIT is NOT a replacement for colonoscopy after a cancer diagnosis
"""


# =============================================================================
# STAGE PROGNOSIS CONTEXT (V4 Step 7)
# =============================================================================

STAGE_PROGNOSIS_CONTEXT = {
    'IIIA': "Stage IIIA colon cancer generally has favorable outcomes with appropriate treatment. Your care team can provide more specific prognosis information.",
    'IIIB': "Stage IIIB colon cancer has meaningful cure rates with surgery and adjuvant chemotherapy. Five-year survival rates vary based on individual factors. Your care team can discuss your specific prognosis based on your pathology, biomarkers, and response to treatment.",
    'IIIC': "Stage IIIC represents more advanced local disease but is still potentially curable. Discuss your specific outlook with your oncology team.",
}


# =============================================================================
# ER PREPARATION TIPS (V4 Step 4)
# =============================================================================

ER_PREPARATION_TIPS = """
If going to the ER:
• Tell triage immediately that you're on chemotherapy - this often expedites evaluation
• Bring your medication list or take a photo of your pill bottles
• Have your oncologist's after-hours number saved in your phone
• Bring your insurance card and ID
• If possible, have someone accompany you
"""


# =============================================================================
# EMOTIONAL SUPPORT GUIDANCE (V4 Step 2 - Fixed genetic counselor role)
# =============================================================================

EMOTIONAL_SUPPORT_GUIDANCE = """
For emotional support:
- Normalize the emotion: Anxiety, fear, and sadness are completely normal reactions to a cancer diagnosis
- Mention specific resources:
  * Oncology social workers are available at most cancer centers - ask your care team
  * Cancer Support Helpline: 1-888-793-9355 (free, confidential)
  * Calm and Headspace apps have free cancer-specific meditation programs
- For "scanxiety": Anxiety often peaks around scan times - this is very common
- For family communication: Oncology social workers and CancerCare counselors can help with family discussions
- NOTE: Genetic counselors are for hereditary risk discussions (e.g., "Should my children get tested?"), NOT general family communication
"""


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken or approximate fallback."""
    if not text:
        return 0

    if TIKTOKEN_AVAILABLE and TOKEN_ENCODING:
        return len(TOKEN_ENCODING.encode(text))

    # Fallback: approximate 4 chars per token (conservative estimate)
    return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int, preserve_end: bool = False) -> str:
    """
    Truncate text to fit within token budget.

    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        preserve_end: If True, keep end of text (for conversation history)
    """
    if not text:
        return text

    current_tokens = count_tokens(text)
    if current_tokens <= max_tokens:
        return text

    if TIKTOKEN_AVAILABLE and TOKEN_ENCODING:
        tokens = TOKEN_ENCODING.encode(text)
        if preserve_end:
            truncated_tokens = tokens[-max_tokens:]
        else:
            truncated_tokens = tokens[:max_tokens]
        return TOKEN_ENCODING.decode(truncated_tokens)

    # Fallback: approximate by character ratio
    char_limit = max_tokens * 4
    if preserve_end:
        return "..." + text[-char_limit:]
    return text[:char_limit] + "..."


def select_chunks_within_budget(chunks: list, max_tokens: int) -> str:
    """Select and format chunks that fit within token budget.
       Accepts List[str] or List[Dict] (with 'content' key).
    """
    if not chunks:
        return "No specific guideline excerpts found for this query."

    selected = []
    current_tokens = 0

    for i, chunk in enumerate(chunks):
        # Handle dict vs str
        if isinstance(chunk, dict):
            text = chunk.get('content', '') or chunk.get('chunk_text', '') or ""
        else:
            text = str(chunk)

        if not text:
            continue

        chunk_tokens = count_tokens(text)
        # Account for separator tokens
        separator_tokens = 15 if i > 0 else 0

        if current_tokens + chunk_tokens + separator_tokens > max_tokens:
            # Try to fit a truncated version if we have no chunks yet
            if not selected:
                truncated = truncate_to_tokens(text, max_tokens - 50)
                selected.append(truncated)
            break

        selected.append(text)
        current_tokens += chunk_tokens + separator_tokens

    if selected:
        return "\n---GUIDELINE EXCERPT---\n".join(selected)
    return "No specific guideline excerpts found for this query."


def classify_query_type(message: str) -> str:
    """
    Classify the query into categories to determine what context is relevant.
    Returns: treatment | side_effect | prognosis | diagnosis | general
    """
    message_lower = message.lower()

    treatment_keywords = [
        'treatment', 'therapy', 'chemotherapy', 'chemo', 'radiation', 'surgery',
        'medication', 'drug', 'regimen', 'folfox', 'folfiri', 'immunotherapy',
        'targeted therapy', 'clinical trial', 'option', 'next step'
    ]

    side_effect_keywords = [
        'side effect', 'symptom', 'pain', 'nausea', 'fatigue', 'tired',
        'neuropathy', 'diarrhea', 'constipation', 'vomit', 'fever', 'rash',
        'toxicity', 'adverse', 'reaction', 'feeling', 'hurt', 'ache'
    ]

    prognosis_keywords = [
        'prognosis', 'survival', 'outcome', 'life expectancy', 'cure',
        'remission', 'progression', 'spread', 'metastasis', 'stage',
        'how long', 'will i', 'chance', 'likely'
    ]

    diagnosis_keywords = [
        'diagnosis', 'test', 'scan', 'biopsy', 'ct', 'mri', 'pet',
        'blood work', 'lab', 'marker', 'cea', 'biomarker', 'genetic'
    ]

    profile_keywords = [
        'profile', 'my info', 'about me', 'my data', 'my record',
        'who am i', 'what do you know', 'patient info'
    ]

    scores = {
        'treatment': sum(1 for kw in treatment_keywords if kw in message_lower),
        'side_effect': sum(1 for kw in side_effect_keywords if kw in message_lower),
        'prognosis': sum(1 for kw in prognosis_keywords if kw in message_lower),
        'diagnosis': sum(1 for kw in diagnosis_keywords if kw in message_lower),
        'profile': sum(1 for kw in profile_keywords if kw in message_lower)
    }

    max_score = max(scores.values())
    if max_score == 0:
        return 'general'

    for category, score in scores.items():
        if score == max_score:
            return category

    return 'general'


def should_suggest_clinical_trials(query_type: str, patient_context: Dict[str, Any], message: str) -> bool:
    """
    Determine if we should proactively mention clinical trials availability.

    Triggers when:
    - Query is about treatment AND patient is metastatic (Stage IV)
    - Query suggests treatment resistance or progression
    - Patient is asking about next options or alternatives

    Args:
        query_type: The classified query type ('treatment', 'side_effect', etc.)
        patient_context: Patient profile data
        message: The user's question

    Returns:
        True if clinical trials should be proactively suggested
    """
    if query_type != 'treatment':
        return False

    if not patient_context:
        return False

    message_lower = message.lower()

    # Check for metastatic/Stage IV disease
    stage = str(patient_context.get('stage', '')).upper()
    is_metastatic = 'IV' in stage or '4' in stage or 'METASTATIC' in stage.upper()

    # Check for treatment resistance/progression language
    resistance_indicators = [
        'not working', 'stopped working', 'progressed', 'spread',
        'failed', 'resistant', 'progression', 'growing', 'worse'
    ]
    has_resistance_context = any(ind in message_lower for ind in resistance_indicators)

    # Check for "next options" language
    next_options_indicators = [
        'next step', 'other option', 'alternative', 'what else',
        'if this fails', 'after this', 'what\'s next', 'backup',
        'second line', 'third line', 'more options'
    ]
    asking_about_options = any(ind in message_lower for ind in next_options_indicators)

    return is_metastatic or has_resistance_context or asking_about_options


def filter_relevant_context(patient_context: Dict[str, Any], query_type: str, message: str) -> str:
    """Provides full patient context without selective filtering for richer AI understanding."""
    if not patient_context:
        return "No patient profile available."

    full_context = []

    # Demographics
    name = patient_context.get('patient_name')
    age = patient_context.get('age')
    if name and age:
        full_context.append(f"Patient: {name}, {age} years old")
    elif name:
        full_context.append(f"Patient: {name}")

    zip_code = patient_context.get('zip_code', 'unspecified')
    if zip_code != 'unspecified':
        full_context.append(f"Location: {zip_code}")
        
    race = patient_context.get('race_ethnicity', 'unspecified')
    if race != 'unspecified':
        full_context.append(f"Race/Ethnicity: {race}")

    # Diagnosis & Stage
    cancer_type = patient_context.get('cancer_type', 'unspecified cancer')
    stage = patient_context.get('stage', 'unspecified')
    if stage != 'unspecified':
        full_context.append(f"Diagnosis: {cancer_type}, stage {stage}")
    else:
        full_context.append(f"Diagnosis: {cancer_type}")

    # Treatment Info
    treatments = patient_context.get('current_treatments', [])
    if treatments:
        full_context.append(f"Treatments: {', '.join(treatments)}")

    current_cycle = patient_context.get('current_cycle_number')
    treatment_line = patient_context.get('treatment_line')
    current_regimen = patient_context.get('current_regimen')
    if current_cycle and current_regimen:
        from lib.llm_utils import get_cycle_context
        cycle_info = get_cycle_context(current_regimen, treatment_line, current_cycle)
        if cycle_info:
            full_context.append(f"Treatment status: {cycle_info}")

    # Biomarkers
    biomarkers = patient_context.get('biomarkers', 'unspecified')
    if biomarkers != 'unspecified' and biomarkers:
        full_context.append(f"Biomarkers: {biomarkers}")
        # Explicit warnings for AI
        if 'MSS' in biomarkers or 'Microsatellite Stable' in biomarkers:
            full_context.append("⚠️ MSI Status: MSS - immunotherapy/checkpoint inhibitors likely ineffective")
        elif 'MSI-H' in biomarkers or 'MSI-High' in biomarkers or 'Unstable' in biomarkers:
            full_context.append("✓ MSI Status: MSI-H - may respond to immunotherapy")

    # Medications & History
    meds = patient_context.get('medications', [])
    if meds:
        full_context.append(f"Medications: {', '.join(meds)}")

    history = patient_context.get('medical_history', [])
    if history:
        full_context.append(f"History: {', '.join(history)}")

    allergies = patient_context.get('allergies', 'none reported')
    if allergies != 'none reported':
        full_context.append(f"Allergies: {allergies}")

    # Status & Sites
    status = patient_context.get('performance_status', 'unspecified')
    if status != 'unspecified':
        full_context.append(f"Performance: {status}")

    sites = patient_context.get('disease_sites', [])
    if sites:
        full_context.append(f"Disease sites: {', '.join(sites)}")

    # Symptoms
    symptoms = patient_context.get('symptoms', [])
    if symptoms:
        full_context.append(f"Recent symptoms: {', '.join(symptoms)}")

    return " | ".join(full_context)


def get_response_settings(response_length: str) -> Dict[str, Any]:
    """Get max_tokens, temperature, and system message based on response length setting."""
    # Use the enhanced system prompt for all response lengths
    base_system = ENHANCED_SYSTEM_PROMPT

    if response_length == "brief":
        return {
            "max_tokens": 150,
            "temperature": 0.3,
            "system_message": base_system + "\n\nRESPONSE LENGTH: Brief (1-2 sentences). Be concise but still warm and helpful.",
            "prompt_instruction": "Answer in 1-2 sentences using simple words. Be concise but complete.",
            "include_resources": False  # Don't add resources for brief responses
        }
    elif response_length == "detailed":
        return {
            "max_tokens": 400,
            "temperature": 0.4,
            "system_message": base_system + "\n\nRESPONSE LENGTH: Detailed (4-6 sentences). Be thorough. Explain medical terms. Include relevant context.",
            "prompt_instruction": "Answer in 4-6 sentences. Explain any medical terms in plain language. Be thorough.",
            "include_resources": True
        }
    else:  # normal (default)
        return {
            "max_tokens": 250,
            "temperature": 0.35,
            "system_message": base_system + "\n\nRESPONSE LENGTH: Normal (2-4 sentences). Balance conciseness with helpfulness.",
            "prompt_instruction": "Answer in 2-4 sentences using simple words. Be clear and helpful.",
            "include_resources": True
        }


def format_conversation_context(history: List[Dict[str, str]], max_tokens: int = None) -> str:
    """
    Format conversation history for inclusion in prompt with token budgeting.

    Uses sliding window to include most recent messages within token budget.
    """
    if not history:
        return ""

    if max_tokens is None:
        max_tokens = TOKEN_BUDGET['history']

    # Start from most recent and work backwards
    formatted_parts = []
    current_tokens = 20  # Reserve for header

    for entry in reversed(history):
        question = entry.get('question', '')
        answer = entry.get('answer', '')

        # Truncate long answers
        if count_tokens(answer) > 100:
            answer = truncate_to_tokens(answer, 100)

        entry_text = f"Q: {question}\nA: {answer}"
        entry_tokens = count_tokens(entry_text)

        if current_tokens + entry_tokens > max_tokens:
            break

        formatted_parts.insert(0, entry_text)
        current_tokens += entry_tokens

    if not formatted_parts:
        return ""

    return "PREVIOUS CONVERSATION:\n" + "\n\n".join(formatted_parts)


def assemble_prompt(message: str, retrieved: list, patient: dict,
                    response_length: str = "normal", conversation_context: str = "",
                    patient_context: Dict[str, Any] = None) -> Tuple[str, dict]:
    """
    Enhanced prompt assembly with:
    - Query-relevant context filtering
    - Symptom urgency detection
    - Biomarker implications
    - Neuropathy-specific guidance
    - Token budgeting

    Returns:
        Tuple of (prompt_string, metadata_dict)
        metadata_dict includes urgency info, query_type, etc.
    """
    settings = get_response_settings(response_length)
    query_type = classify_query_type(message)

    if patient_context is None:
        patient_context = {}

    # ==========================================================================
    # STEP 1: Detect symptom urgency FIRST
    # ==========================================================================
    urgency_info = detect_symptom_urgency(message, patient_context)

    # ==========================================================================
    # STEP 2: Get filtered patient context (concise, query-relevant)
    # ==========================================================================
    filtered_context = filter_relevant_context(patient_context, query_type, message)
    filtered_context = truncate_to_tokens(filtered_context, TOKEN_BUDGET['patient'])

    # ==========================================================================
    # STEP 3: Add biomarker implications for treatment/prognosis queries
    # ==========================================================================
    biomarker_context = ""
    if query_type in ['treatment', 'prognosis', 'diagnosis']:
        # Get raw biomarkers from patient profile
        raw_biomarkers = patient.get('primaryDiagnosis', {}).get('biomarkers', {}) if patient else {}
        if raw_biomarkers:
            try:
                from profile_utils import get_biomarker_implications, extract_biomarkers_summary
                implications = get_biomarker_implications(raw_biomarkers)
                if implications:
                    biomarker_context = "\n\nBIOMARKER IMPLICATIONS (use these to inform your answer):\n"
                    for impl in implications[:2]:  # Max 2 implications
                        biomarker_context += f"• {impl}\n"
            except ImportError:
                pass  # profile_utils not available

    # ==========================================================================
    # STEP 4: Add neuropathy guidance if relevant
    # ==========================================================================
    neuropathy_context = ""
    message_lower = message.lower()
    neuropathy_keywords = ['neuropathy', 'tingling', 'numbness', 'fingers', 'toes', 'nerve', 'peripheral']
    is_neuropathy_question = any(kw in message_lower for kw in neuropathy_keywords)

    # Check if patient is on oxaliplatin-based regimen
    current_treatments = patient_context.get('current_treatments', [])
    on_oxaliplatin = any('folfox' in str(tx).lower() or 'oxaliplatin' in str(tx).lower()
                         for tx in current_treatments)

    if is_neuropathy_question and on_oxaliplatin:
        neuropathy_context = "\n\n" + OXALIPLATIN_NEUROPATHY_GUIDANCE

    # ==========================================================================
    # STEP 4b: Add colonoscopy surveillance guidelines if relevant (V3 Step 4)
    # ==========================================================================
    colonoscopy_context = ""
    colonoscopy_keywords = ['colonoscopy', 'surveillance', 'follow-up', 'follow up', 'after treatment']
    is_colonoscopy_question = any(kw in message_lower for kw in colonoscopy_keywords)

    if is_colonoscopy_question or query_type == 'survivorship':
        colonoscopy_context = "\n\n" + COLONOSCOPY_SURVEILLANCE_GUIDELINES

    # ==========================================================================
    # STEP 4c: Add emotional support guidance if relevant (V3 Step 6)
    # ==========================================================================
    emotional_context = ""
    emotional_keywords = ['anxious', 'anxiety', 'scared', 'fear', 'worried', 'depressed', 'sad', 'emotional', 'cope', 'coping', 'family', 'tell']
    is_emotional_question = any(kw in message_lower for kw in emotional_keywords)

    if is_emotional_question or query_type == 'emotional':
        emotional_context = "\n\n" + EMOTIONAL_SUPPORT_GUIDANCE

    # ==========================================================================
    # STEP 4d: Detect bevacizumab in adjuvant setting (V3 Step 7)
    # ==========================================================================
    treatment_warning = ""
    treatment_line = patient_context.get('treatment_line', '')
    current_regimen = patient_context.get('current_regimen', '')

    if treatment_line == 'Adjuvant' and current_regimen and 'bevacizumab' in current_regimen.lower():
        treatment_warning = """
NOTE: Patient is receiving bevacizumab in the adjuvant setting. Bevacizumab is NOT typically recommended for standard adjuvant treatment in stage II/III colon cancer (per NCCN guidelines). This may indicate:
- Enrollment in a clinical trial
- Physician decision based on specific patient factors
This is a reasonable question to bring to their next appointment. It doesn't mean anything is wrong—treatment plans are sometimes individualized based on factors not captured in general guidelines."""

    # ==========================================================================
    # STEP 4e: Detect immunotherapy questions and add MSI context (V4 Step 1)
    # ==========================================================================
    msi_context = ""
    immunotherapy_keywords = ['immunotherapy', 'checkpoint', 'pembrolizumab', 'keytruda', 'nivolumab', 'opdivo']
    is_immunotherapy_question = any(kw in message_lower for kw in immunotherapy_keywords)

    if is_immunotherapy_question:
        biomarkers = patient_context.get('biomarkers', '')
        if 'MSS' in biomarkers or 'Microsatellite Stable' in biomarkers:
            msi_context = "\n\n⚠️ IMPORTANT MSI STATUS: Patient is MSS (Microsatellite Stable). Checkpoint inhibitors/immunotherapy are unlikely to be effective as standalone treatment for MSS colorectal cancer. Other treatment options remain available."
        elif 'MSI-H' in biomarkers or 'MSI-High' in biomarkers:
            msi_context = "\n\n✓ MSI STATUS: Patient is MSI-H (Microsatellite Instability-High). May respond well to immunotherapy/checkpoint inhibitors."

    # ==========================================================================
    # STEP 4f: Add FIT test guidance if relevant (V4 Step 3)
    # ==========================================================================
    fit_test_context = ""
    fit_keywords = ['fit test', 'fecal', 'stool test', 'fit vs', 'colonoscopy vs']
    is_fit_question = any(kw in message_lower for kw in fit_keywords)

    if is_fit_question:
        fit_test_context = "\n\n" + FIT_TEST_GUIDANCE

    # ==========================================================================
    # STEP 4g: Add prognosis context for stage questions (V4 Step 7)
    # ==========================================================================
    prognosis_context = ""
    stage_keywords = ['stage iii', 'stage 3', 'what stage', 'my stage', 'stage iiib', 'stage 3b']
    is_stage_question = any(kw in message_lower for kw in stage_keywords)
    stage = patient_context.get('stage', '')

    if is_stage_question and stage:
        stage_upper = stage.upper()
        if stage_upper in STAGE_PROGNOSIS_CONTEXT:
            prognosis_context = f"\n\nPROGNOSIS CONTEXT:\n{STAGE_PROGNOSIS_CONTEXT[stage_upper]}"

    # ==========================================================================
    # STEP 5: Format retrieved guidelines with token budget
    # ==========================================================================
    if retrieved:
        guideline_context = select_chunks_within_budget(retrieved, TOKEN_BUDGET['chunks'])
        chunks_used = guideline_context.count('---GUIDELINE EXCERPT---') + 1 if guideline_context else 0
        guideline_note = f"Based on {chunks_used} relevant guideline section(s):"
        logger.info(f"Prompt using {chunks_used} chunks, {count_tokens(guideline_context)} tokens for guidelines")
    else:
        guideline_context = "No specific guideline excerpts found for this query."
        guideline_note = "Based on general cancer care knowledge:"

    # ==========================================================================
    # STEP 6: Build urgency-aware instructions
    # ==========================================================================
    urgency_instruction = ""
    if urgency_info['detected']:
        if urgency_info['urgency'] == 'emergency':
            urgency_instruction = f"""
CRITICAL - EMERGENCY DETECTED: Start your response with this exact guidance:
"{urgency_info['guidance']}"
Then include these ER preparation tips:
{ER_PREPARATION_TIPS}
Then provide additional context."""
        elif urgency_info['urgency'] == 'urgent':
            urgency_instruction = f"""
IMPORTANT - URGENT SYMPTOM DETECTED: Include this guidance prominently in your response:
"{urgency_info['guidance']}"
Provide interim management tips while they await medical consultation."""

    # ==========================================================================
    # STEP 7: Build the prompt
    # ==========================================================================
    prompt_parts = []

    if conversation_context:
        prompt_parts.append(conversation_context)
        prompt_parts.append("")

    # Patient context (concise - don't repeat unnecessarily)
    prompt_parts.extend([
        f"PATIENT CONTEXT (Query Type: {query_type}):",
        filtered_context
    ])

    # Add biomarker implications if relevant
    if biomarker_context:
        prompt_parts.append(biomarker_context)

    # Add neuropathy guidance if relevant
    if neuropathy_context:
        prompt_parts.append(neuropathy_context)

    # Add colonoscopy surveillance guidelines if relevant (V3 Step 4)
    if colonoscopy_context:
        prompt_parts.append(colonoscopy_context)

    # Add emotional support guidance if relevant (V3 Step 6)
    if emotional_context:
        prompt_parts.append(emotional_context)

    # Add treatment warning if relevant (V3 Step 7)
    if treatment_warning:
        prompt_parts.append(treatment_warning)

    # Add MSI context if relevant (V4 Step 1)
    if msi_context:
        prompt_parts.append(msi_context)

    # Add FIT test guidance if relevant (V4 Step 3)
    if fit_test_context:
        prompt_parts.append(fit_test_context)

    # Add prognosis context if relevant (V4 Step 7)
    if prognosis_context:
        prompt_parts.append(prognosis_context)

    prompt_parts.extend([
        "",
        "MEDICAL GUIDELINES:",
        guideline_note,
        guideline_context,
        "",
        f"USER'S QUESTION: {message}",
        ""
    ])

    # Instructions section
    prompt_parts.append("INSTRUCTIONS:")
    prompt_parts.append(f"• {settings['prompt_instruction']}")
    prompt_parts.append("• Use simple, everyday language - explain medical terms if you must use them")
    prompt_parts.append("• Lead with actionable information, not disclaimers")
    prompt_parts.append("• Be specific and practical")

    if urgency_instruction:
        prompt_parts.append(urgency_instruction)

    # Query-specific instructions
    if query_type == 'side_effect':
        prompt_parts.append("• For side effects: provide interim management tips, mention when to contact the care team")
    elif query_type == 'emotional':
        prompt_parts.append("• For emotional concerns: validate feelings, mention oncology social workers and support groups")
    elif query_type == 'treatment':
        prompt_parts.append(TREATMENT_RESPONSE_STRUCTURE)
        prompt_parts.append("• Reference the patient's specific biomarkers when discussing treatment eligibility")

    # Add follow-up question suggestions for non-brief responses
    if response_length != "brief":
        prompt_parts.append(FOLLOW_UP_INSTRUCTION)

    # Check if clinical trials should be proactively suggested
    if should_suggest_clinical_trials(query_type, patient_context, message):
        prompt_parts.append("• Given the patient's situation, include a brief mention that clinical trials may be worth exploring. Phrase naturally: 'There may also be clinical trials available for your situation - just ask if you'd like me to search for trials near you.'")

    prompt_parts.extend([
        "",
        "RESPONSE:"
    ])

    # Prepare metadata for post-processing
    metadata = {
        'query_type': query_type,
        'urgency_detected': urgency_info['detected'],
        'urgency_level': urgency_info.get('urgency'),
        'urgency_pattern': urgency_info.get('pattern'),
        'is_neuropathy_question': is_neuropathy_question,
        'on_oxaliplatin': on_oxaliplatin,
        'include_resources': settings.get('include_resources', True)
    }

    return "\n".join(prompt_parts), metadata


def trim_incomplete_sentence(response: str) -> str:
    """Trim any incomplete sentence at the end of a response."""
    if not response:
        return response
    response = response.strip()
    if response and response[-1] in '.!?"':
        return response
    last_period = response.rfind('.')
    last_exclaim = response.rfind('!')
    last_question = response.rfind('?')
    last_punct = max(last_period, last_exclaim, last_question)
    if last_punct > 0:
        return response[:last_punct + 1]
    return response


# Disclaimer templates - context-aware
DISCLAIMERS = {
    "action": "\n\n⚠️ Before making any changes to your treatment, please consult your healthcare team.",
    "general": "\n\n💡 This is general information. Your doctor can provide personalized guidance.",
    "emergency": "\n\n🚨 If you're experiencing these symptoms, please contact your healthcare provider or emergency services immediately.",
    "dosage": "\n\nNote: Dosages should be confirmed with your prescribing physician."
}


def should_add_disclaimer(query: str, response: str) -> Tuple[bool, Optional[str]]:
    """
    Determine if a disclaimer is needed and which type.

    Returns (needs_disclaimer, disclaimer_type) where disclaimer_type is one of:
    - "action": Response gives actionable medical advice
    - "general": General treatment discussion
    - "emergency": Emergency symptoms detected
    - "dosage": Specific dosage mentioned
    - None: No disclaimer needed
    """
    query_lower = query.lower()
    response_lower = response.lower()

    # Skip disclaimer for purely informational queries
    info_only_patterns = [
        r"what (is|are|does)",
        r"explain",
        r"tell me about",
        r"how does .* work",
        r"what happens",
        r"why (is|does|do)"
    ]
    is_info_query = any(re.search(p, query_lower) for p in info_only_patterns)

    # Check if response gives actionable advice
    action_patterns = [
        r"you should",
        r"you need to",
        r"take \d+",
        r"stop taking",
        r"start taking",
        r"recommended dose",
        r"increase your",
        r"decrease your"
    ]
    gives_action = any(re.search(p, response_lower) for p in action_patterns)

    # Check for dosage mentions
    dosage_pattern = r'\b(\d+\s*(mg|ml|mcg|units?|tablets?|pills?|capsules?))\b'
    has_dosage = bool(re.search(dosage_pattern, response, re.IGNORECASE))
    defers_to_doctor = any(phrase in response_lower for phrase in ['doctor', 'physician', 'prescrib', 'healthcare'])

    if has_dosage and not defers_to_doctor:
        return True, "dosage"

    if gives_action:
        return True, "action"

    # Don't add disclaimer for pure informational responses
    if is_info_query:
        return False, None

    # Add general disclaimer only if discussing treatments without being purely informational
    treatment_words = ['treatment', 'therapy', 'medication', 'drug', 'chemo']
    if any(word in response_lower for word in treatment_words):
        return True, "general"

    return False, None


def enhanced_medical_validation(response: str, query: str) -> dict:
    """Comprehensive medical-specific validation for safety concerns."""
    safety_flags = []
    modified_response = response

    response_lower = response.lower()
    query_lower = query.lower()

    # 1. Check for dangerous absolute claims (expanded list)
    absolute_patterns = [
        (r'\b(will cure|will definitely|100%|guaranteed to)\b', "absolute_claim"),
        (r'\b(never causes?|always works?|completely safe)\b', "absolute_claim"),
        (r'\b(no side effects?|risk-free|cannot fail)\b', "absolute_claim"),
    ]

    for pattern, flag_type in absolute_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            safety_flags.append(f"Contains {flag_type}: pattern '{pattern}'")

    # 2. Check for emergency symptoms not addressed
    emergency_symptoms = [
        'chest pain', 'difficulty breathing', 'severe bleeding',
        'high fever', 'severe headache', 'confusion', 'seizure',
        'can\'t breathe', 'unconscious', 'stroke symptoms'
    ]
    query_has_emergency = any(s in query_lower for s in emergency_symptoms)
    response_addresses_emergency = any(
        phrase in response_lower
        for phrase in ['seek medical', 'call 911', 'emergency', 'immediately', 'urgent', 'hospital']
    )

    if query_has_emergency and not response_addresses_emergency:
        modified_response = DISCLAIMERS['emergency'] + "\n\n" + modified_response
        safety_flags.append("Added emergency warning")

    # 3. Check response completeness - trim incomplete sentences
    if response and not response.rstrip().endswith(('.', '!', '?', '"', ')')):
        last_period = response.rfind('.')
        if last_period > len(response) * 0.5:  # Keep if >50% of response
            modified_response = response[:last_period + 1]
            safety_flags.append("Trimmed incomplete sentence")

    return {
        "safe": len([f for f in safety_flags if 'absolute_claim' in f]) == 0,
        "flags": safety_flags,
        "severity": "high" if query_has_emergency else "low",
        "modified_response": modified_response
    }


def validate_response(response: str, user_question: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate AI response for safety, relevance, and quality.

    Uses context-aware disclaimer logic to avoid over-disclaiming on informational queries.
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'enhanced_response': response,
        'needs_disclaimer': False,
        'disclaimer_type': None
    }

    if not response or len(response.strip()) < 10:
        validation_result['is_valid'] = False
        validation_result['warnings'].append("Response too short or empty")
        return validation_result

    # Run enhanced medical validation first
    medical_validation = enhanced_medical_validation(response, user_question)

    # Use the potentially modified response (e.g., with emergency warning or trimmed)
    current_response = medical_validation.get('modified_response', response)
    validation_result['warnings'].extend(medical_validation.get('flags', []))

    # Check if this is a high-severity situation
    if medical_validation.get('severity') == 'high':
        validation_result['enhanced_response'] = current_response
        # Emergency disclaimer already added by enhanced_medical_validation
        return validation_result

    # Use smart disclaimer logic
    needs_disclaimer, disclaimer_type = should_add_disclaimer(user_question, current_response)

    if needs_disclaimer and disclaimer_type:
        validation_result['needs_disclaimer'] = True
        validation_result['disclaimer_type'] = disclaimer_type
        current_response += DISCLAIMERS.get(disclaimer_type, DISCLAIMERS['general'])
        logger.info(f"Added {disclaimer_type} disclaimer")

    validation_result['enhanced_response'] = current_response

    return validation_result


def select_model_for_query(query: str, query_type: str, response_length: str) -> str:
    """
    Select the appropriate model based on query complexity.

    Returns: "together" for complex queries (70B model), "groq" for simple queries (8B model)
    """
    query_lower = query.lower()
    word_count = len(query.split())

    # Simple query indicators -> use faster Groq model
    simple_indicators = [
        word_count < 8,                          # Very short questions
        query_type == 'general',                 # General questions
        '?' not in query,                        # Statements, not questions
        response_length == 'brief',              # Brief responses requested
    ]

    # Complex query indicators -> use larger Together model
    complex_indicators = [
        query_type in ['treatment', 'prognosis'],  # Medical decision topics
        'why' in query_lower,                      # Explanatory questions
        'should i' in query_lower,                 # Decision-making questions
        'compare' in query_lower,                  # Comparative analysis
        response_length == 'detailed',             # Detailed responses requested
        word_count > 20,                           # Long complex questions
    ]

    # Count indicators
    simple_count = sum(1 for x in simple_indicators if x)
    complex_count = sum(1 for x in complex_indicators if x)

    # Default to Together for medical safety, but use Groq for clearly simple queries
    if simple_count >= 3 and complex_count == 0:
        return "groq"

    return "together"


def call_llm(prompt: str, response_length: str = "normal", temperature: float = None,
             query: str = None, query_type: str = None) -> Tuple[str, str]:
    """
    Call LLM API with smart model routing.

    Uses Together AI (70B) for complex queries and Groq (8B) for simple queries.
    Falls back between providers if one fails.

    Args:
        prompt: The prompt to send to the LLM
        response_length: "brief", "normal", or "detailed" - controls token limits and temperature
        temperature: Optional override for temperature (uses settings default if None)
        query: Original user query (for smart routing)
        query_type: Classified query type (for smart routing)

    Returns: (response_text, api_used)
    """
    settings = get_response_settings(response_length)

    # Use settings temperature unless explicitly overridden
    effective_temperature = temperature if temperature is not None else settings["temperature"]

    # Always use Together AI (70B) as primary for consistent quality
    preferred_model = "together"
    logger.info(f"Using Together AI (70B) for query type: {query_type or 'unknown'}")

    together_error = None
    groq_error = None

    def try_together():
        """Try Together AI (70B model)."""
        nonlocal together_error
        client = get_together_client()
        if not client:
            together_error = "Together client not available (API key may be invalid)"
            logger.warning(together_error)
            return None
        try:
            logger.info(f"Calling Together AI (70B), response_length: {response_length}, temp: {effective_temperature}")
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": settings["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings["max_tokens"],
                temperature=effective_temperature,
                top_p=0.9,
            )
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.info(f"Together AI response success - length: {len(content)}")
                    return content.strip(), "together"
            together_error = "Together AI returned empty response"
            logger.warning(together_error)
        except Exception as e:
            together_error = f"Together AI API error: {str(e)}"
            logger.warning(together_error)
        return None

    def try_groq():
        """Try Groq (8B model - faster)."""
        nonlocal groq_error
        client = get_groq_client()
        if not client:
            groq_error = "Groq client not available (API key may be invalid)"
            logger.warning(groq_error)
            return None
        try:
            logger.info(f"Calling Groq (8B), response_length: {response_length}, temp: {effective_temperature}")
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": settings["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings["max_tokens"],
                temperature=effective_temperature,
                top_p=0.9,
            )
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.info(f"Groq response success - length: {len(content)}")
                    return content.strip(), "groq"
            groq_error = "Groq returned empty response"
            logger.warning(groq_error)
        except Exception as e:
            groq_error = f"Groq API error: {str(e)}"
            logger.warning(groq_error)
        return None

    # Try preferred model first, then fallback
    if preferred_model == "groq":
        result = try_groq()
        if result:
            return result
        # Fallback to Together
        result = try_together()
        if result:
            return result
    else:
        result = try_together()
        if result:
            return result
        # Fallback to Groq
        result = try_groq()
        if result:
            return result

    # Both failed - include detailed error messages
    error_details = []
    if together_error:
        error_details.append(f"Together: {together_error}")
    if groq_error:
        error_details.append(f"Groq: {groq_error}")
    
    error_msg = "No LLM API available or both failed"
    if error_details:
        error_msg += f" - Details: {'; '.join(error_details)}"
    
    raise RuntimeError(error_msg)


def _quick_extract_profile_updates(message: str) -> dict:
    """
    Quick regex-based extraction for common profile field updates.
    This runs before the LLM call for faster response on simple updates.
    """
    import re
    updates = {}
    msg_lower = message.lower()

    # Zip code patterns
    zip_patterns = [
        r"(?:my\s+)?(?:new\s+)?zip\s*(?:code)?\s*(?:is|:)?\s*(\d{5}(?:-\d{4})?)",
        r"(?:i\s+)?(?:live|moved)\s+(?:in|to)\s+(?:zip\s*(?:code)?\s*)?(\d{5}(?:-\d{4})?)",
        r"zip\s*(?:code)?[:\s]+(\d{5}(?:-\d{4})?)",
    ]
    for pattern in zip_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            if "patient" not in updates:
                updates["patient"] = {}
            updates["patient"]["zipCode"] = match.group(1)
            break

    # Age patterns
    age_patterns = [
        r"(?:i\s+am|i'm|my\s+age\s+is)\s+(\d{1,3})\s*(?:years?\s*old)?",
        r"(?:my\s+)?age[:\s]+(\d{1,3})",
        r"(\d{1,3})\s*(?:years?\s*old|yo|y\.?o\.?)",
    ]
    for pattern in age_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            age = int(match.group(1))
            if 1 <= age <= 120:  # Reasonable age range
                if "patient" not in updates:
                    updates["patient"] = {}
                updates["patient"]["age"] = str(age)
                break

    # Weight patterns (lbs)
    weight_patterns = [
        r"(?:i\s+)?weigh\s+(\d{2,3})\s*(?:lbs?|pounds?)?",
        r"(?:my\s+)?weight\s*(?:is|:)?\s*(\d{2,3})\s*(?:lbs?|pounds?)?",
        r"(\d{2,3})\s*(?:lbs?|pounds?)",
    ]
    for pattern in weight_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            weight = int(match.group(1))
            if 50 <= weight <= 500:  # Reasonable weight range
                if "patient" not in updates:
                    updates["patient"] = {}
                updates["patient"]["weight"] = str(weight)
                break

    # Stage patterns
    stage_patterns = [
        r"(?:i\s+am|i'm|i\s+have|diagnosed\s+with)\s+stage\s+(i{1,3}v?|[1-4])",
        r"(?:my\s+)?(?:cancer\s+)?stage\s*(?:is|:)?\s*(i{1,3}v?|[1-4])",
    ]
    for pattern in stage_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            stage_raw = match.group(1).upper()
            stage_map = {"1": "Stage I", "2": "Stage II", "3": "Stage III", "4": "Stage IV",
                         "I": "Stage I", "II": "Stage II", "III": "Stage III", "IV": "Stage IV"}
            if stage_raw in stage_map:
                if "primaryDiagnosis" not in updates:
                    updates["primaryDiagnosis"] = {}
                updates["primaryDiagnosis"]["stage"] = stage_map[stage_raw]
                break

    # Name patterns
    name_patterns = [
        r"(?:my\s+name\s+is|i'm|call\s+me)\s+([A-Z][a-z]+)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, message)  # Case-sensitive for names
        if match:
            if "patient" not in updates:
                updates["patient"] = {}
            updates["patient"]["firstName"] = match.group(1)
            break

    return updates


def extract_profile_updates_from_query(message: str, current_profile: dict) -> dict:
    """
    Scan user query for profile-relevant updates using LLM.

    Returns: Dict of updates found.
    """
    # First, try quick regex-based extraction for common simple updates
    quick_updates = _quick_extract_profile_updates(message)
    if quick_updates:
        logger.info(f"Quick extraction found updates: {quick_updates}")
        return quick_updates

    client = get_together_client() or get_groq_client()
    if not client:
        logger.warning("No LLM client available for profile extraction")
        return {}

    system_prompt = """
    You are a medical data extraction assistant. Analyze the user's message and identify any NEW or UPDATED information
    relevant to their patient profile. Use the CURRENT profile as context to only extract CHANGED or NEW information.

    IMPORTANT: Look for ANY mention of personal or medical information updates, including:
    - "my zip code is...", "I live in...", "my new address..."
    - "I am X years old", "my age is...", "I'm..."
    - "my name is...", "call me..."
    - "I weigh...", "my weight is..."
    - "I'm X feet X inches", "my height is..."
    - "I started...", "I'm now on...", "my new treatment is..."
    - "I have...", "I was diagnosed with..."
    - "my biomarker is...", "my KRAS is...", "I'm MSI-high"
    - "I'm experiencing...", "I have side effects like..."

    Extract fields like:
    - Age (or date of birth)
    - Symptoms (toxicities)
    - Treatments (regimens, cycle numbers, status)
    - Biomarkers (KRAS, NRAS, BRAF, MSI, MMR, HER2, etc.)
    - Comorbidities
    - Basic info (name, zip code, race/ethnicity, height, weight)

    CURRENT PROFILE:
    {current_profile_json}

    Return ONLY a JSON object with the updates. If no updates are found, return {{}}.
    The JSON structure should follow the patient profile format:
    {{
      "patient": {{ "age": ..., "firstName": ..., "zipCode": ..., "weight": ..., "heightFt": ..., "heightIn": ... }},
      "primaryDiagnosis": {{ "biomarkers": {{ ... }}, "stage": ..., "histology": ... }},
      "treatments": [ {{ "category": ..., "regimen": ..., "status": ... }} ],
      "symptoms": [ ... ]
    }}
    Include ONLY the fields that have changed.
    """
    
    current_profile_json = json.dumps(current_profile, indent=2)
    
    try:
        model = "meta-llama/Llama-3.3-70B-Instruct-Turbo" if get_together_client() else "llama-3.1-8b-instant"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.format(current_profile_json=current_profile_json)},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            return json.loads(content)
    except Exception as e:
        logger.error(f"Profile extraction failed: {e}")
    
    return {}

