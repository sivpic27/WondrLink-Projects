# profile_utils.py
import os
import json
import logging
from typing import Dict, Any, List, Union
from datetime import datetime, date

logger = logging.getLogger("profile_utils")

# In-memory profile cache (for serverless, this resets between invocations)
PATIENT_PROFILE = {}


def calculate_age(dob_str: str) -> int:
    """Calculate age from date of birth string (YYYY-MM-DD format)"""
    try:
        if not dob_str or dob_str == 'unspecified':
            return None
        birth = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except (ValueError, TypeError):
        return None


def save_and_load_profile(file_storage, upload_folder: str) -> dict:
    """
    Save uploaded JSON profile to disk and load it into memory.
    Returns parsed dict if valid, else raises Exception.
    """
    if not file_storage:
        raise ValueError("No file provided")

    filename = file_storage.filename
    if not filename.lower().endswith(".json"):
        raise ValueError("File must be a JSON")

    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    file_storage.save(save_path)

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        global PATIENT_PROFILE
        PATIENT_PROFILE = data
        logger.info("Loaded patient profile: %s", filename)
        return data
    except Exception as e:
        logger.exception("Failed to load patient profile")
        raise ValueError(f"Invalid JSON: {e}")


def parse_profile_json(json_content: bytes) -> dict:
    """Parse profile from JSON bytes (for serverless without file system)."""
    try:
        data = json.loads(json_content.decode('utf-8'))
        global PATIENT_PROFILE
        PATIENT_PROFILE = data
        logger.info("Loaded patient profile from JSON content")
        return data
    except Exception as e:
        logger.exception("Failed to parse profile JSON")
        raise ValueError(f"Invalid JSON: {e}")


def get_profile() -> dict:
    """Return current patient profile (dict)."""
    return PATIENT_PROFILE


def set_profile(profile: dict):
    """Set the current patient profile (dict)."""
    global PATIENT_PROFILE
    PATIENT_PROFILE = profile
    logger.info("Patient profile set in memory")


def safe_extract_value(data: Any, path: str, default: str = "unspecified") -> str:
    """Safely extract a value from nested dictionary using dot notation."""
    if not data:
        return default

    try:
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        if isinstance(current, (str, int, float)):
            return str(current)
        elif isinstance(current, bool):
            return "yes" if current else "no"
        elif isinstance(current, list):
            if current:
                return ', '.join(str(item) for item in current[:3]) + ('...' if len(current) > 3 else '')
            else:
                return default
        elif isinstance(current, dict):
            if 'status' in current:
                return str(current['status'])
            elif 'value' in current:
                return str(current['value'])
            else:
                return str(current)
        else:
            return str(current) if current is not None else default

    except Exception:
        return default


def extract_treatments_summary(treatments: List[Dict]) -> List[str]:
    """Extract a summary of treatments from complex treatment data"""
    if not treatments or not isinstance(treatments, list):
        return []

    summaries = []
    for treatment in treatments:
        if not isinstance(treatment, dict):
            continue

        line = treatment.get('line', 'unknown line')
        regimen = treatment.get('regimen', 'unknown regimen')
        status = treatment.get('status', 'completed')

        if status == 'active':
            summary = f"Currently on {regimen} ({line})"
        else:
            summary = f"{regimen} ({line})"

        summaries.append(summary)

    return summaries


def extract_biomarkers_summary(biomarkers: Dict) -> str:
    """Extract key biomarkers into readable format"""
    if not biomarkers or not isinstance(biomarkers, dict):
        return "unspecified"

    key_markers = []

    important_markers = ['KRAS', 'NRAS', 'BRAF', 'HER2', 'MSI', 'MMR', 'NTRK', 'PIK3CA']

    for marker in important_markers:
        if marker in biomarkers:
            value = biomarkers[marker]
            if value and str(value).strip():
                key_markers.append(f"{marker}: {value}")

    return ', '.join(key_markers) if key_markers else "pending/unspecified"


def extract_current_symptoms(profile: Dict) -> List[str]:
    """Extract current symptoms/toxicities from treatment data"""
    symptoms = []

    treatments = profile.get('treatments', [])
    if isinstance(treatments, list):
        for treatment in treatments:
            if isinstance(treatment, dict) and treatment.get('status') == 'active':
                toxicities = treatment.get('toxicities', [])
                if isinstance(toxicities, list):
                    for tox in toxicities:
                        if isinstance(tox, dict):
                            event = tox.get('event', '')
                            grade = tox.get('grade', '')
                            if event:
                                symptom = f"Grade {grade} {event}" if grade else event
                                symptoms.append(symptom)

    direct_symptoms = profile.get('symptoms', [])
    if isinstance(direct_symptoms, list):
        symptoms.extend([str(s) for s in direct_symptoms])

    return symptoms


def extract_current_medications(profile: Dict) -> List[str]:
    """Extract current medications from treatment regimens"""
    medications = []

    treatments = profile.get('treatments', [])
    if isinstance(treatments, list):
        for treatment in treatments:
            if isinstance(treatment, dict) and treatment.get('status') == 'active':
                regimen = treatment.get('regimen', '')
                if regimen:
                    meds = []
                    if 'FOLFOX' in regimen:
                        meds.extend(['5-FU', 'Leucovorin', 'Oxaliplatin'])
                    if 'FOLFIRI' in regimen:
                        meds.extend(['5-FU', 'Leucovorin', 'Irinotecan'])
                    if 'bevacizumab' in regimen:
                        meds.append('Bevacizumab')
                    if 'panitumumab' in regimen:
                        meds.append('Panitumumab')
                    if 'TAS-102' in regimen:
                        meds.append('Trifluridine/Tipiracil')

                    medications.extend(meds)

    seen = set()
    unique_meds = []
    for med in medications:
        if med not in seen:
            seen.add(med)
            unique_meds.append(med)

    return unique_meds


def extract_patient_context_complex(profile: dict) -> Dict[str, Any]:
    """Enhanced patient context extraction that handles complex nested JSON structures."""
    if not profile:
        return {}

    context = {}

    patient_info = profile.get('patient', {})
    if isinstance(patient_info, dict):
        dob = safe_extract_value(patient_info, 'dob', 'unspecified')
        age = calculate_age(dob)
        if age is not None:
            context['age'] = age
        else:
            context['age'] = None

        name = safe_extract_value(patient_info, 'name', None)
        if name and name != 'unspecified':
            context['patient_name'] = name

        context['gender'] = safe_extract_value(patient_info, 'sex', 'unspecified')
        context['performance_status'] = f"ECOG {safe_extract_value(patient_info, 'ecog', 'unspecified')}"
        context['allergies'] = safe_extract_value(patient_info, 'allergies', 'none reported')

        comorbidities = patient_info.get('comorbidities', [])
        if isinstance(comorbidities, list) and comorbidities:
            context['medical_history'] = comorbidities
        else:
            context['medical_history'] = []

    primary_dx = profile.get('primaryDiagnosis', {})
    if isinstance(primary_dx, dict):
        site = safe_extract_value(primary_dx, 'site', '')
        histology = safe_extract_value(primary_dx, 'histology', '')
        stage = safe_extract_value(primary_dx, 'stage', 'unspecified')

        if site and histology:
            context['cancer_type'] = f"{site} {histology}"
        elif site:
            context['cancer_type'] = f"{site} cancer"
        elif histology:
            context['cancer_type'] = histology
        else:
            context['cancer_type'] = 'unspecified'

        context['stage'] = stage

        biomarkers = primary_dx.get('biomarkers', {})
        if isinstance(biomarkers, dict):
            context['biomarkers'] = extract_biomarkers_summary(biomarkers)
        else:
            context['biomarkers'] = 'unspecified'

    treatments = profile.get('treatments', [])
    if isinstance(treatments, list):
        context['current_treatments'] = extract_treatments_summary(treatments)
        context['medications'] = extract_current_medications(profile)
    else:
        context['current_treatments'] = []
        context['medications'] = []

    context['symptoms'] = extract_current_symptoms(profile)

    resistance = profile.get('resistance', [])
    if isinstance(resistance, list) and resistance:
        latest_resistance = resistance[-1] if resistance else {}
        if isinstance(latest_resistance, dict):
            mechanism = safe_extract_value(latest_resistance, 'mechanism', '')
            if mechanism:
                context['resistance_mechanism'] = mechanism

    current_options = profile.get('currentOptions', [])
    if isinstance(current_options, list) and current_options:
        context['treatment_options'] = current_options[:3]

    recurrences = profile.get('recurrences', [])
    if isinstance(recurrences, list) and recurrences:
        latest_recurrence = recurrences[-1] if recurrences else {}
        if isinstance(latest_recurrence, dict):
            sites = latest_recurrence.get('sites', [])
            if isinstance(sites, list) and sites:
                context['disease_sites'] = sites

    return context


def format_patient_summary_complex(context: Dict[str, Any]) -> str:
    """Format complex patient context into a readable summary for AI and UI display."""
    if not context:
        return "No patient profile available."

    summary_parts = []

    cancer_type = context.get('cancer_type', 'unspecified cancer')
    stage = context.get('stage', 'unspecified')
    if stage != 'unspecified':
        summary_parts.append(f"Diagnosis: {cancer_type}, stage {stage}")
    else:
        summary_parts.append(f"Diagnosis: {cancer_type}")

    demo_parts = []
    gender = context.get('gender', 'unspecified')
    if gender != 'unspecified':
        demo_parts.append(gender)

    performance_status = context.get('performance_status', 'unspecified')
    if performance_status != 'unspecified':
        demo_parts.append(performance_status)

    if demo_parts:
        summary_parts.append(f"Patient: {', '.join(demo_parts)}")

    treatments = context.get('current_treatments', [])
    if treatments:
        current_tx = [tx for tx in treatments if 'Currently on' in tx]
        if current_tx:
            summary_parts.append(current_tx[0])

    biomarkers = context.get('biomarkers', 'unspecified')
    if biomarkers != 'unspecified' and biomarkers:
        summary_parts.append(f"Key biomarkers: {biomarkers}")

    symptoms = context.get('symptoms', [])
    if symptoms:
        summary_parts.append(f"Current issues: {', '.join(symptoms[:2])}{'...' if len(symptoms) > 2 else ''}")

    resistance = context.get('resistance_mechanism', '')
    if resistance:
        summary_parts.append(f"Resistance: {resistance}")

    return " | ".join(summary_parts)
