# WondrChat 2.1

**Release Date:** April 2026
**Status:** Production (https://wondrchat.vercel.app)
**Previous Version:** [v2.0](../v2.0/RELEASE.md)

---

## Summary

WondrChat 2.1 adds a HIPAA de-identification layer that strips all Protected Health Information from patient data before it reaches external LLM APIs. It also repositions screening instruments to present raw scores without clinical interpretation, reducing regulatory risk under FDA SaMD guidelines.

---

## Changes

### HIPAA De-identification Layer

**Problem:** WondrChat sends patient profiles (name, DOB, zip code, diagnosis dates) to Together AI and Groq for LLM inference. Neither provider offers a Business Associate Agreement (BAA), making this a HIPAA compliance gap.

**Solution:** New module `lib/deidentify.py` with three functions that run automatically inside `assemble_prompt()` before any patient data enters the prompt string.

| Function | What It Strips | What It Preserves |
|----------|---------------|-------------------|
| `deidentify_patient_context()` | Patient name, zip code, DOB | Age, sex, cancer type, stage, biomarkers, comorbidities, treatments, symptoms, ECOG |
| `deidentify_raw_profile()` | Name, DOB, address, phone, email, SSN, MRN, insurance ID, account number. Converts absolute dates to relative timeframes ("approximately 20 months ago") | All clinical fields: diagnosis, biomarkers, treatments, toxicities, surgical outcomes |
| `deidentify_conversation_context()` | SSN, phone, email, address patterns in chat history | All conversation content |

**Integration point:** Step 0 in `assemble_prompt()`, before any context assembly. Every LLM call goes through de-identification automatically.

**Files:**
- Created: `lib/deidentify.py`
- Modified: `lib/llm_utils.py` (assemble_prompt Step 0, removed name/zip from filter_relevant_context)

---

### Screening Instrument Language Update

**Problem:** Screening messages like "We recommend discussing this with your oncologist" constitute clinical interpretation, which risks FDA classification as Software as a Medical Device (SaMD). Per the 21st Century Cures Act Section 3060, clinical decision support directed at patients (not healthcare professionals) cannot rely on the CDS exclusion.

**Solution:** All four screening instruments now present raw scores with standard severity labels and a consistent "Share this result with your healthcare provider" message. No clinical interpretation or treatment recommendations.

**Before:**
> "Your score suggests moderate depression symptoms. We recommend discussing this with your oncologist or a counselor."

**After:**
> "Your PHQ-9 score falls in the moderate range. Share this result with your healthcare provider."

**Instruments updated:** PHQ-9, GAD-7, PSS-10, ISI

**File:** `public/index.html`

---

### Disclaimer Update

**Problem:** Previous disclaimer positioned WondrChat as an "educational support tool." Stronger language needed to maintain health education positioning and avoid SaMD classification.

**Changes:**
- "educational support tool" changed to "health education tool"
- Added: "not a substitute for professional medical advice, diagnosis, or treatment"
- Added: "If you use our screening tools (PHQ-9, GAD-7, PSS-10, ISI), please share your results with your healthcare provider"

**File:** `public/index.html` (acknowledgement modal)

---

## Test Results

**58/60 (96.7%)** — no regressions from v2.0

- Unit tests: 23/23
- LLM integration tests: 35/37
- 2 failures are LLM wording variability, not code defects

---

## Commit

```
b77c787 Add HIPAA de-identification layer and update screening language
```
