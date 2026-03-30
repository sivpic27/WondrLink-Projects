"""
HIPAA De-identification Module for WondrLink

Strips Protected Health Information (PHI) from patient context before
sending to external LLM APIs (Together AI, Groq) that lack BAA coverage.

Preserves all clinically relevant data:
- Cancer type, stage, histology
- Biomarkers (KRAS, MSI, BRAF, etc.)
- Treatment regimen, line, cycle number, toxicities
- Comorbidities and symptoms
- Performance status (ECOG)
- Age (but not DOB)
- Sex/gender (clinically relevant)

Strips HIPAA identifiers:
- Names, DOB, addresses, zip codes, phone, email, SSN
- Medical record numbers, account numbers
- Any other direct identifiers
"""

import re
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def deidentify_patient_context(patient_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove PHI from patient_context dict before it enters prompt assembly.

    This is called AFTER extract_patient_context_complex() but BEFORE
    filter_relevant_context() and assemble_prompt().

    Args:
        patient_context: The extracted patient context dict

    Returns:
        A new dict with PHI stripped, clinical data preserved
    """
    if not patient_context:
        return patient_context

    # Create a copy to avoid mutating the original
    safe = dict(patient_context)

    # Strip direct identifiers
    safe.pop('patient_name', None)
    safe.pop('zip_code', None)

    # Keep age (derived from DOB, not identifying alone) but remove raw DOB if present
    safe.pop('dob', None)
    safe.pop('date_of_birth', None)

    # Keep race_ethnicity — clinically relevant for treatment response differences
    # (e.g., UGT1A1 polymorphisms more common in certain populations)
    # But strip if combined with other identifiers could be re-identifying
    # For now, keep it — it's a Safe Harbor "permitted" field when other identifiers removed

    return safe


def deidentify_raw_profile(patient: dict) -> dict:
    """
    Remove PHI from the raw patient profile dict before it enters prompt assembly.

    The raw profile is used in assemble_prompt() to access biomarkers and
    treatment data. This strips identifying fields while preserving clinical data.

    Args:
        patient: The raw patient profile JSON

    Returns:
        A new dict with PHI stripped
    """
    if not patient:
        return patient

    import copy
    safe = copy.deepcopy(patient)

    # Strip patient-level identifiers
    patient_info = safe.get('patient', {})
    if isinstance(patient_info, dict):
        patient_info.pop('name', None)
        patient_info.pop('firstName', None)
        patient_info.pop('lastName', None)
        patient_info.pop('dob', None)
        patient_info.pop('dateOfBirth', None)
        patient_info.pop('zipCode', None)
        patient_info.pop('zip_code', None)
        patient_info.pop('address', None)
        patient_info.pop('phone', None)
        patient_info.pop('email', None)
        patient_info.pop('ssn', None)
        patient_info.pop('mrn', None)
        patient_info.pop('medicalRecordNumber', None)
        patient_info.pop('insuranceId', None)
        patient_info.pop('accountNumber', None)

    # Strip dates from surgical history (convert to relative timeframes)
    surgeries = safe.get('surgicalHistory', [])
    if isinstance(surgeries, list):
        for surgery in surgeries:
            if isinstance(surgery, dict) and 'date' in surgery:
                surgery['date'] = _relativize_date(surgery['date'])

    # Strip treatment start dates (convert to relative)
    treatments = safe.get('treatments', [])
    if isinstance(treatments, list):
        for tx in treatments:
            if isinstance(tx, dict) and 'startDate' in tx:
                tx['startDate'] = _relativize_date(tx['startDate'])

    # Strip diagnosis date (convert to relative)
    dx = safe.get('primaryDiagnosis', {})
    if isinstance(dx, dict) and 'dateOfDiagnosis' in dx:
        dx['dateOfDiagnosis'] = _relativize_date(dx['dateOfDiagnosis'])

    return safe


def deidentify_conversation_context(conversation: str) -> str:
    """
    Scrub any PII that may have leaked into conversation history.

    Args:
        conversation: Formatted conversation context string

    Returns:
        Conversation with PII patterns replaced
    """
    if not conversation:
        return conversation

    sanitized = conversation

    # SSN patterns
    sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[ID REMOVED]', sanitized)

    # Phone patterns
    sanitized = re.sub(r'\b(?:\+1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', sanitized)

    # Email patterns
    sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', sanitized)

    # Street address patterns (number + street name)
    sanitized = re.sub(r'\b\d{1,5}\s+(?:[A-Z][a-z]+\s+){1,3}(?:St|Ave|Blvd|Dr|Rd|Ln|Ct|Way|Pl)\b\.?',
                       '[ADDRESS]', sanitized, flags=re.IGNORECASE)

    return sanitized


def _relativize_date(date_str: str) -> str:
    """
    Convert an absolute date to a relative timeframe.

    '2024-07-10' → 'approximately 20 months ago'
    """
    if not date_str or date_str in ('unspecified', 'None', ''):
        return date_str

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        now = datetime.now()
        delta = now - date
        months = delta.days // 30

        if months < 1:
            return 'within the last month'
        elif months == 1:
            return 'approximately 1 month ago'
        elif months < 12:
            return f'approximately {months} months ago'
        else:
            years = months // 12
            remaining_months = months % 12
            if remaining_months == 0:
                return f'approximately {years} year{"s" if years > 1 else ""} ago'
            return f'approximately {years} year{"s" if years > 1 else ""} and {remaining_months} month{"s" if remaining_months > 1 else ""} ago'
    except (ValueError, TypeError):
        # If date parsing fails, remove it entirely
        return 'date not specified'
