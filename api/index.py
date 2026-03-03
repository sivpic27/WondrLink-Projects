# api/index.py - WondrLink Flask API for Vercel Serverless
import os
import sys
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify

# Add lib to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from dotenv import load_dotenv
load_dotenv()

# Import lib modules
from supabase_client import get_supabase_client, verify_token
from auth_helpers import register_user, login_user, logout_user, get_current_user
from supabase_storage import (
    save_profile, load_profile, clear_profile,
    load_all_chunks, get_conversation_history, add_conversation,
    get_document_metadata, update_profile_with_sources,
    check_acknowledgement, save_acknowledgement,
    save_chat_message, load_chat_history, clear_chat_history
)
from profile_utils import (
    extract_patient_context_complex, format_patient_summary_complex,
    set_profile, get_profile, parse_profile_json
)
from pdf_utils import search_chunks
from llm_utils import (
    assemble_prompt, call_llm, classify_query_type,
    trim_incomplete_sentence, validate_response, enhanced_medical_validation,
    format_conversation_context, get_llm_status, sanitize_query,
    extract_profile_updates_from_query, get_relevant_resources
)
from clinical_trials import (
    search_trials_for_patient, format_trials_for_chat, is_clinical_trial_query,
    validate_trial_search_readiness
)

# -------------------------
# Config & Globals
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wondr-api")

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")

def _origin_allowed(origin: str) -> bool:
    if not origin:
        return False
    origin = origin.strip().lower()
    allowed = [o.strip().lower() for o in ALLOWED_ORIGINS if o]
    if "*" in allowed:
        return True
    return origin in allowed

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "wondrlink-dev-secret-key")

# -------------------------
# Auth Decorator
# -------------------------
def require_auth(f):
    """Decorator to require JWT authentication via Authorization header."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required", "code": "AUTH_REQUIRED"}), 401

        token = auth_header.split(' ')[1]
        user = verify_token(token)

        if not user:
            return jsonify({"error": "Invalid or expired token", "code": "INVALID_TOKEN"}), 401

        # Attach user to request context
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# Auth Routes
# -------------------------
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    """Register a new user with Supabase Auth."""
    try:
        # Try to get JSON data from request body
        data = {}
        try:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
            elif request.is_json:
                data = request.get_json(silent=True) or {}
        except Exception:
            data = {}

        email = data.get("email", "").strip()
        password = data.get("password", "")

        user_data, error = register_user(email, password)

        if error:
            return jsonify({"error": error}), 400

        logger.info(f"New user registered: {email}")
        return jsonify({
            "status": "ok",
            "message": "Account created successfully",
            "user": {
                "user_id": user_data["user_id"],
                "email": user_data["email"]
            },
            "access_token": user_data.get("access_token"),
            "refresh_token": user_data.get("refresh_token")
        })
    except Exception as e:
        logger.exception("Registration error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    """Authenticate and log in a user."""
    try:
        # Try to get JSON data from request body
        data = {}
        try:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
            elif request.is_json:
                data = request.get_json(silent=True) or {}
        except Exception:
            data = {}

        email = data.get("email", "").strip()
        password = data.get("password", "")

        user_data, error = login_user(email, password)

        if error:
            return jsonify({"error": error}), 401

        logger.info(f"User logged in: {email}")
        return jsonify({
            "status": "ok",
            "message": "Logged in successfully",
            "user": {
                "user_id": user_data["user_id"],
                "email": user_data["email"]
            },
            "access_token": user_data["access_token"],
            "refresh_token": user_data["refresh_token"]
        })
    except Exception as e:
        logger.exception("Login error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """Log out the current user."""
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1] if auth_header and auth_header.startswith('Bearer ') else None

    if token:
        logout_user(token)

    logger.info("User logged out")
    return jsonify({"status": "ok", "message": "Logged out successfully"})


@app.route("/api/auth/me", methods=["GET"])
def api_get_current_user():
    """Get current logged-in user info."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"authenticated": False}), 200

    token = auth_header.split(' ')[1]
    user = get_current_user(token)

    if not user:
        return jsonify({"authenticated": False}), 200

    return jsonify({
        "authenticated": True,
        "user": user
    })

# -------------------------
# Profile Routes
# -------------------------
@app.route("/api/upload_profile", methods=["POST"])
@require_auth
def api_upload_profile():
    """Upload a patient profile JSON."""
    try:
        user_id = request.user["user_id"]

        # Handle JSON body
        if request.is_json:
            profile = request.get_json(silent=True)
            if not profile:
                return jsonify({"error": "Invalid JSON body"}), 400
        else:
            # Handle file upload
            file = request.files.get("file")
            if not file:
                return jsonify({"error": "No file or JSON provided"}), 400

            content = file.read()
            profile = json.loads(content.decode('utf-8'))

        # Save to Supabase
        if not save_profile(user_id, profile):
            logger.error(f"Failed to save profile to database for user {user_id}")
            return jsonify({"error": "Failed to save profile to database. Please check server logs."}), 500

        # Set in memory for this request
        set_profile(profile)

        # Extract context
        patient_context = extract_patient_context_complex(profile)
        patient_summary = format_patient_summary_complex(patient_context)

        logger.info(f"Loaded patient profile for user {user_id}")
        return jsonify({
            "status": "ok",
            "profile": profile,
            "patient_summary": patient_summary,
            "context": patient_context
        })
    except Exception as e:
        logger.exception("upload_profile error")
        return jsonify({"error": str(e)}), 400


@app.route("/api/get_patient", methods=["GET"])
@require_auth
def api_get_patient():
    """Get the current patient profile."""
    try:
        user_id = request.user["user_id"]

        # Load from Supabase
        profile = load_profile(user_id)

        if profile:
            set_profile(profile)
            patient_context = extract_patient_context_complex(profile)
            patient_summary = format_patient_summary_complex(patient_context)
            return jsonify({
                "profile": profile,
                "patient_summary": patient_summary,
                "context": patient_context
            })
        else:
            return jsonify({})
    except Exception as e:
        logger.exception("get_patient error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear_profile", methods=["POST"])
@require_auth
def api_clear_profile():
    """Clear the stored patient profile."""
    try:
        user_id = request.user["user_id"]
        clear_profile(user_id)
        set_profile({})
        logger.info(f"Cleared patient profile for user {user_id}")
        return jsonify({"status": "ok", "message": "Profile cleared"})
    except Exception as e:
        logger.exception("clear_profile error")
        return jsonify({"error": str(e)}), 500

# -------------------------
# Acknowledgement Routes
# -------------------------
@app.route("/api/check_acknowledgement", methods=["GET"])
@require_auth
def api_check_acknowledgement():
    """Check if user has acknowledged the disclaimer."""
    try:
        user_id = request.user["user_id"]
        acknowledged = check_acknowledgement(user_id)
        return jsonify({"acknowledged": acknowledged})
    except Exception as e:
        logger.exception("check_acknowledgement error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/save_acknowledgement", methods=["POST"])
@require_auth
def api_save_acknowledgement():
    """Save user acknowledgement of the disclaimer."""
    try:
        user_id = request.user["user_id"]
        success = save_acknowledgement(user_id)
        if success:
            return jsonify({"status": "ok", "message": "Acknowledgement saved"})
        else:
            return jsonify({"error": "Failed to save acknowledgement"}), 500
    except Exception as e:
        logger.exception("save_acknowledgement error")
        return jsonify({"error": str(e)}), 500


# -------------------------
# Chat History Routes
# -------------------------
@app.route("/api/chat_history", methods=["GET"])
@require_auth
def api_get_chat_history():
    """Load chat history for the authenticated user."""
    try:
        user_id = request.user["user_id"]
        limit = request.args.get("limit", 50, type=int)
        messages = load_chat_history(user_id, limit)
        return jsonify({"messages": messages})
    except Exception as e:
        logger.exception("get_chat_history error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/save_message", methods=["POST"])
@require_auth
def api_save_message():
    """Save a chat message for the authenticated user."""
    try:
        user_id = request.user["user_id"]
        data = request.get_json() or {}
        role = data.get("role")
        content = data.get("content")
        metadata = data.get("metadata")  # Optional metadata (e.g., clinical_trials)

        if not role or not content:
            return jsonify({"error": "role and content are required"}), 400

        if role not in ["user", "assistant"]:
            return jsonify({"error": "role must be 'user' or 'assistant'"}), 400

        success = save_chat_message(user_id, role, content, metadata)
        if success:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"error": "Failed to save message"}), 500
    except Exception as e:
        logger.exception("save_message error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear_chat", methods=["DELETE"])
@require_auth
def api_clear_chat():
    """Clear all chat history for the authenticated user."""
    try:
        user_id = request.user["user_id"]
        success = clear_chat_history(user_id)
        if success:
            return jsonify({"status": "ok", "message": "Chat history cleared"})
        else:
            return jsonify({"error": "Failed to clear chat history"}), 500
    except Exception as e:
        logger.exception("clear_chat error")
        return jsonify({"error": str(e)}), 500


# -------------------------
# Chat Route
# -------------------------
@app.route("/api/chat", methods=["POST"])
@require_auth
def api_chat():
    """Main chat endpoint."""
    try:
        user_id = request.user["user_id"]
        # Try to get JSON data from request body
        data = {}
        try:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
            elif request.is_json:
                data = request.get_json(silent=True) or {}
        except Exception:
            data = {}

        message = data.get("message")
        response_length = data.get("response_length", "normal")
        session_id = data.get("session_id", "default")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Enforce max message length (safety net for frontend maxlength)
        if len(message) > 2000:
            message = message[:2000]

        # Sanitize PII from user message (compliance)
        original_message = message
        message, pii_warnings = sanitize_query(message)
        if pii_warnings:
            # Log PII types detected but NOT the actual values (for privacy)
            pii_types = [w.split(':')[0].strip() if ':' in w else w for w in pii_warnings]
            logger.warning(f"PII detected and sanitized: {len(pii_warnings)} item(s) - types: {pii_types}")

        logger.info(f"Chat request (session: {session_id}): {message[:50]}...")

        # Load chunks from Supabase
        indexed_chunks = load_all_chunks()

        # Get conversation history from Supabase
        history = get_conversation_history(session_id)
        conversation_context = format_conversation_context(history)

        # Load patient profile from Supabase
        patient_profile = load_profile(user_id)
        # load_profile returns {} if not found, which is falsy in Python. 
        # We want to ensure extract_patient_context_complex is called even if profile is mostly empty.
        patient_context = extract_patient_context_complex(patient_profile) if (patient_profile is not None and len(patient_profile) > 0) else {}

        # Check for cancer type mismatch
        mismatch_detected = False
        if patient_context.get('cancer_type'):
            cancer_keywords = ['breast cancer', 'lung cancer', 'prostate cancer', 'colon cancer',
                             'colorectal', 'pancreatic', 'ovarian', 'melanoma']
            user_message_lower = message.lower()
            patient_cancer = patient_context.get('cancer_type', '').lower()

            for cancer_type in cancer_keywords:
                if cancer_type in user_message_lower:
                    if cancer_type not in patient_cancer and patient_cancer not in cancer_type:
                        mismatch_detected = True
                        break

        # Classify query type early so we can adjust chunk retrieval
        query_type = classify_query_type(message)
        effective_top_k = 8 if query_type in ('treatment', 'clinical_trial') else 5

        # Search relevant chunks
        retrieved = []
        try:
            retrieved = search_chunks(message, indexed_chunks, top_k=effective_top_k)
            logger.info(f"search_chunks returned {len(retrieved)} chunks (top_k={effective_top_k}, query_type={query_type})")
        except Exception:
            logger.exception("search_chunks failed")

        # Assemble prompt
        if mismatch_detected:
            message_with_note = f"{message}\n\n[SYSTEM NOTE: User asked about different cancer type than their profile]"
            prompt, prompt_metadata = assemble_prompt(message_with_note, retrieved, patient_profile, response_length,
                                    conversation_context, patient_context)
        else:
            prompt, prompt_metadata = assemble_prompt(message, retrieved, patient_profile, response_length,
                                    conversation_context, patient_context)

        # Check LLM availability
        llm_status = get_llm_status()
        if not llm_status["primary_api"]:
            return jsonify({
                "error": "No LLM API available. Please check TOGETHER_API_KEY or GROQ_API_KEY.",
                "debug_info": llm_status
            }), 500

        # Call LLM with smart routing (query_type already classified above)
        try:
            answer, api_used = call_llm(prompt, response_length, query=message, query_type=query_type)
            if not answer:
                raise RuntimeError("LLM returned empty response")

            answer = trim_incomplete_sentence(answer)
            logger.info(f"{api_used.upper()} response success - length: {len(answer)}")

            # Validate response
            validation = validate_response(answer, message, patient_context)
            medical_validation = enhanced_medical_validation(answer, message)

            all_warnings = validation['warnings'] + medical_validation['flags']
            if all_warnings:
                logger.warning(f"Response validation warnings: {all_warnings}")

            final_answer = validation['enhanced_response']

            # Add relevant patient resources (unless brief response)
            if response_length != "brief":
                resources_text = get_relevant_resources(query_type, include_resources=True, query=message)
                if resources_text:
                    final_answer = final_answer + resources_text

            # --- Feature: Clinical Trials Search ---
            # Return trials data separately for frontend rendering (not as markdown in answer)
            clinical_trials_data = None
            if is_clinical_trial_query(message) and patient_context:
                try:
                    logger.info(f"Clinical trial query detected for user {user_id}")

                    # Pre-search validation: check if profile has enough data
                    readiness = validate_trial_search_readiness(patient_context)
                    if not readiness["ready"]:
                        clinical_trials_data = {
                            "error": "incomplete_profile",
                            "message": readiness["prompt_message"],
                            "missing_critical": readiness["missing_critical"],
                            "missing_helpful": readiness["missing_helpful"]
                        }
                    else:
                        trials_result = search_trials_for_patient(patient_context, max_results=5)
                        if not trials_result.get("error"):
                            # Return full trials data for frontend rendering
                            clinical_trials_data = {
                                "found": len(trials_result.get("trials", [])),
                                "total": trials_result.get("total_found", 0),
                                "trials": trials_result.get("trials", []),
                                "search_criteria": trials_result.get("search_criteria", {})
                            }
                            # Include profile completeness tip if helpful fields are missing
                            if readiness.get("prompt_message"):
                                clinical_trials_data["profile_completeness"] = readiness["prompt_message"]
                            logger.info(f"Found {clinical_trials_data['found']} clinical trials for user")
                        elif trials_result.get("error") == "no_zip_code":
                            clinical_trials_data = {
                                "error": "no_zip_code",
                                "message": "To search for clinical trials near you, please add your zip code to your profile."
                            }
                except Exception as e:
                    logger.error(f"Error searching clinical trials: {e}", exc_info=True)

            # Store conversation in Supabase (store original answer without resources for cleaner history)
            add_conversation(session_id, user_id, message, answer)

            # --- Feature 1: Scan for profile updates ---
            profile_updates = {}
            update_success = False
            try:
                profile_updates = extract_profile_updates_from_query(original_message, patient_profile or {})
                if profile_updates:
                    logger.info(f"Detected profile updates for user {user_id}: {profile_updates}")
                    source_info = {
                        "source_type": "chat",
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    update_success = update_profile_with_sources(user_id, profile_updates, source_info)
                    if update_success:
                        logger.info(f"Successfully updated profile for user {user_id}")
                    else:
                        logger.error(f"Failed to save profile updates for user {user_id}")
            except Exception as e:
                logger.error(f"Error in profile update scanning: {e}", exc_info=True)

            # Extract sources for the frontend button
            sources_metadata = []
            guidelines_used = []
            guideline_keywords = ['NCCN', 'guideline', 'ACS', 'ASCO', 'CDC', 'NCI', 'recommendation']
            try:
                seen_sources = set()
                for chunk in retrieved:
                    if isinstance(chunk, dict) and chunk.get('filename'):
                        fname = chunk['filename']
                        # Clean filename for display (remove id prefix if present, usually not needed if simple)
                        # Deduplicate
                        if fname not in seen_sources:
                            sources_metadata.append({
                                "title": fname,
                                "type": "document"
                            })
                            seen_sources.add(fname)

                            # Check if this is a medical guideline source
                            fname_lower = fname.lower()
                            if any(kw.lower() in fname_lower for kw in guideline_keywords):
                                guidelines_used.append(fname)

                # Prioritize the specific guide user mentioned
                for s in sources_metadata:
                    if "Comprehensive_Colon_Cancer_Guide" in s["title"]:
                        s["is_featured"] = True
            except Exception as e:
                logger.error(f"Error extracting source metadata: {e}", exc_info=True)

            # Build response
            response_data = {
                "answer": final_answer,
                "api_used": api_used,
                "retrieved_count": len(retrieved),
                "response_length": response_length,
                "patient_context_used": bool(patient_context),
                "mismatch_detected": mismatch_detected,
                "pii_filtered": len(pii_warnings) > 0,
                "validation_warnings": all_warnings,
                "medical_safety_check": medical_validation['safe'],
                "conversation_length": len(history) + 1,
                "has_profile_updates": bool(profile_updates),
                "profile_updates_saved": update_success if profile_updates else None,
                "sources": sources_metadata,
                "guidelines_used": guidelines_used,
                "has_guidelines": len(guidelines_used) > 0,
                "clinical_trials": clinical_trials_data,
                "urgency": {
                    "detected": prompt_metadata.get('urgency_detected', False),
                    "level": prompt_metadata.get('urgency_level'),
                    "guidance": prompt_metadata.get('urgency_guidance', '')
                } if prompt_metadata.get('urgency_detected') else None,
                "debug_info": {
                    "api_used": api_used,
                    "retrieved_count": len(retrieved),
                    "has_patient_profile": bool(patient_profile),
                    "query_type": query_type,
                    "session_id": session_id,
                }
            }

            # If profile was updated successfully, include the updated context
            if profile_updates and update_success:
                # Reload the updated profile to get fresh context
                updated_profile = load_profile(user_id)
                if updated_profile:
                    updated_context = extract_patient_context_complex(updated_profile)
                    response_data["updated_profile_context"] = updated_context
                    response_data["profile_update_fields"] = list(profile_updates.keys())

            return jsonify(response_data)

        except Exception as e:
            logger.exception(f"LLM API generation failed: {e}")
            return jsonify({
                "error": f"LLM API failed: {str(e)}",
                "debug_info": llm_status
            }), 500

    except Exception as e:
        logger.exception("Unexpected /chat error")
        return jsonify({"error": str(e)}), 500

# -------------------------
# Feedback Route
# -------------------------
@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """Save user feedback on bot responses."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        rating = data.get("rating")  # "up" or "down"
        message_preview = data.get("message_preview", "")[:200]

        if rating not in ("up", "down"):
            return jsonify({"error": "Invalid rating"}), 400

        # Store in Supabase chat_feedback table (create if needed)
        try:
            client = get_supabase_client()
            client.table("chat_feedback").insert({
                "user_id": user_id,
                "rating": rating,
                "message_preview": message_preview
            }).execute()
        except Exception as e:
            # Table may not exist yet — log but don't fail
            logger.warning(f"Could not save feedback (table may not exist): {e}")

        return jsonify({"status": "ok"})
    except Exception as e:
        logger.exception("Feedback error")
        return jsonify({"error": str(e)}), 500

# -------------------------
# Data Sources Route
# -------------------------
@app.route("/api/data_sources", methods=["GET"])
def api_data_sources():
    """Get list of PDF data sources."""
    try:
        metadata = get_document_metadata()

        return jsonify({
            "status": "ok",
            "data_sources": metadata,
            "total_count": len(metadata),
            "total_chunks": sum(doc.get('chunk_count', 0) for doc in metadata)
        })
    except Exception as e:
        logger.exception("get_data_sources error")
        return jsonify({"error": str(e)}), 500


# -------------------------
# Screening Endpoints (Items 3, 4, 5 - PHQ-9/GAD-7/PSS-10/ISI)
# -------------------------
@app.route("/api/screening/save", methods=["POST"])
@require_auth
def api_save_screening():
    """Save a completed screening instrument score."""
    try:
        user_id = request.user["user_id"]
        data = request.get_json(silent=True) or {}

        instrument = data.get('instrument')  # PHQ9, GAD7, PSS10, ISI
        scores = data.get('scores', {})
        total_score = data.get('total_score')
        severity_label = data.get('severity_label', '')

        if not instrument or total_score is None:
            return jsonify({"error": "instrument and total_score required"}), 400

        valid_instruments = ['PHQ9', 'GAD7', 'PSS10', 'ISI']
        if instrument not in valid_instruments:
            return jsonify({"error": f"instrument must be one of {valid_instruments}"}), 400

        # Crisis check: PHQ-9 Q9 (suicidal ideation)
        is_crisis = False
        crisis_resources = None
        if instrument == 'PHQ9':
            q9_score = scores.get('q9', 0)
            if isinstance(q9_score, (int, float)) and q9_score >= 1:
                is_crisis = True
                crisis_resources = {
                    "message": "You indicated thoughts of self-harm. Please reach out for support immediately.",
                    "resources": [
                        {"name": "988 Suicide & Crisis Lifeline", "contact": "Call or text 988"},
                        {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                        {"name": "Emergency Services", "contact": "Call 911"}
                    ]
                }

        from supabase_storage import save_screening_score
        success = save_screening_score(user_id, instrument, scores, total_score, severity_label)

        return jsonify({
            "status": "ok" if success else "error",
            "is_crisis": is_crisis,
            "crisis_resources": crisis_resources,
            "total_score": total_score,
            "severity_label": severity_label
        })
    except Exception as e:
        logger.exception("Screening save error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/screening/load", methods=["GET"])
@require_auth
def api_load_screening():
    """Load most recent screening scores for all instruments."""
    try:
        user_id = request.user["user_id"]
        from supabase_storage import load_latest_screening_score

        result = {}
        for instrument in ['PHQ9', 'GAD7', 'PSS10', 'ISI']:
            score_data = load_latest_screening_score(user_id, instrument)
            if score_data:
                result[instrument] = score_data

        return jsonify({"status": "ok", "scores": result})
    except Exception as e:
        logger.exception("Screening load error")
        return jsonify({"error": str(e)}), 500


# -------------------------
# Clinical Trials Route
# -------------------------
@app.route("/api/clinical_trials", methods=["GET"])
@require_auth
def api_clinical_trials():
    """Search ClinicalTrials.gov for trials matching patient profile."""
    try:
        user_id = request.user["user_id"]
        max_results = request.args.get("limit", 5, type=int)

        # Load patient profile from Supabase
        profile = load_profile(user_id)
        if not profile:
            return jsonify({
                "error": "No patient profile found. Please build your profile first.",
                "trials": []
            }), 400

        # Extract patient context
        patient_context = extract_patient_context_complex(profile)

        # Validate profile readiness for trial search
        readiness = validate_trial_search_readiness(patient_context)
        if not readiness["ready"]:
            return jsonify({
                "error": readiness["prompt_message"],
                "missing_critical": readiness["missing_critical"],
                "missing_helpful": readiness["missing_helpful"],
                "trials": []
            }), 400

        # Search for clinical trials
        results = search_trials_for_patient(patient_context, max_results=max_results)

        if results.get("error"):
            return jsonify({
                "status": "error",
                "error": results.get("error_message", "Error searching for trials"),
                "trials": []
            }), 200  # Still 200 since it's a valid response

        return jsonify({
            "status": "ok",
            "trials": results["trials"],
            "total_found": results["total_found"],
            "search_criteria": {
                "condition": results["search_criteria"].get("query.cond"),
                "location": patient_context.get("zip_code"),
                "biomarkers": patient_context.get("biomarkers"),
                "intervention": results["search_criteria"].get("query.intr")
            }
        })

    except Exception as e:
        logger.exception("clinical_trials error")
        return jsonify({"error": str(e), "trials": []}), 500


# -------------------------
# Debug Route
# -------------------------
@app.route("/api/debug", methods=["GET"])
def api_debug():
    """Debug information about system status."""
    llm_status = get_llm_status()

    return jsonify({
        "together_available": llm_status["together_available"],
        "groq_available": llm_status["groq_available"],
        "primary_api": llm_status["primary_api"],
        "supabase_configured": bool(os.environ.get("SUPABASE_URL")),
        "environment": {
            "SUPABASE_URL": "SET" if os.environ.get("SUPABASE_URL") else "NOT_SET",
            "SUPABASE_KEY": "SET" if os.environ.get("SUPABASE_KEY") else "NOT_SET",
            "TOGETHER_API_KEY": "SET" if os.environ.get("TOGETHER_API_KEY") else "NOT_SET",
            "GROQ_API_KEY": "SET" if os.environ.get("GROQ_API_KEY") else "NOT_SET"
        }
    })

# -------------------------
# Health Check
# -------------------------
@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "wondrlink-api"})

# -------------------------
# CORS
# -------------------------
@app.route("/api/<path:path>", methods=["OPTIONS"])
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

# -------------------------
# For local development
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
