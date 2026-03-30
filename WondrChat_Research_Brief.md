# WondrChat — Project Research Brief

> This document is a complete snapshot of the WondrChat project for research purposes. Use it to understand the full system before recommending improvements.

---

## What WondrChat Is

A healthcare AI chatbot for **colon cancer patients**. Patients upload their medical profile (diagnosis, biomarkers, treatments, comorbidities) and get personalized, evidence-based answers from an LLM grounded in medical guidelines.

**Live at:** https://wondrchat.vercel.app

**Target users:** Colon cancer patients, their caregivers, and family members who may need screening.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Single-page HTML/CSS/JS (7,445 lines in one file) |
| Backend | Flask (Python 3.9) on Vercel serverless |
| Database | Supabase (PostgreSQL) — auth, profiles, chat, documents, screening scores |
| LLM | Together AI (Llama 3.3 70B primary) + Groq (Llama 3.1 8B fallback) |
| RAG | TF-based keyword search over 1,737 PDF chunks from 20 medical documents |
| Clinical Trials | ClinicalTrials.gov API v2 with relevance scoring |
| Auth | Supabase Auth (JWT Bearer tokens) |

---

## Project Structure

```
api/index.py          — 883 lines, 21 API endpoints (Flask)
lib/llm_utils.py      — 2,420 lines, prompt assembly, query classification, LLM calls
lib/clinical_trials.py — 1,224 lines, trial search, relevance scoring, validation
lib/profile_utils.py  — 701 lines, patient context, biomarkers, comorbidities
lib/pdf_utils.py      — 344 lines, PDF extraction, chunking, TF search
lib/supabase_storage.py — 752 lines, all database operations
public/index.html     — 7,445 lines, entire frontend (CSS + HTML + JS embedded)
data/                 — 20 PDF medical guideline documents
scripts/              — Seeding and test scripts
```

---

## API Endpoints (21 total)

**Auth:** POST register, login, logout | GET me
**Profile:** POST upload_profile, clear_profile | GET get_patient
**Chat:** POST chat, save_message | GET chat_history | DELETE clear_chat
**Screening:** POST screening/save | GET screening/load
**Trials:** GET clinical_trials
**Other:** POST feedback | GET data_sources, health, debug | POST/GET acknowledgement

---

## What the Chat Endpoint Does (POST /api/chat)

1. Authenticate user (JWT)
2. Sanitize PII from message
3. Classify query into one of 9 types
4. Load relevant PDF chunks via TF-based search (top_k=5, or 8 for treatment/trial queries)
5. Load patient profile and extract context (biomarkers, comorbidities, treatment line)
6. Load conversation history
7. Assemble prompt with: system prompt + patient context + guidelines + history + query
8. Call LLM (Together AI → Groq fallback)
9. Validate response (medical safety, tone, completeness)
10. Append relevant resources (unless emergency)
11. If clinical trial query: search ClinicalTrials.gov and attach results
12. Save to chat history
13. Return response with metadata

---

## Query Classification System (9 Categories)

| Category | Triggers On | What Happens |
|----------|------------|--------------|
| clinical_trial | "clinical trial", "phase III", "recruiting" | Searches ClinicalTrials.gov |
| treatment | "chemotherapy", "FOLFOX", "immunotherapy" | Expanded chunk retrieval (top_k=8) |
| side_effect | "nausea", "neuropathy", "side effect" + symptom boost | Comorbidity warnings surfaced |
| prognosis | "survival", "will I die", "any hope" | HIGH tone sensitivity, ANP framework |
| diagnosis | "biopsy", "scan", "biomarker" | Standard retrieval |
| caregiver | "caring for", "my husband", "help my wife" | Caregiver-specific guidance |
| screening_ambassador | "my family", "should they get screened" | Family screening education |
| emotional | "stressed", "anxious", "yoga", "giving up" | Warm tone, wellness resources |
| general | (no keywords match) | Default behavior |

---

## Patient Profile Structure

```json
{
  "patient": {
    "name": "...", "dob": "...", "sex": "...", "ecog": 1,
    "allergies": "...",
    "comorbidities": ["Type 2 Diabetes", "Hypertension"]
  },
  "primaryDiagnosis": {
    "site": "Sigmoid Colon",
    "histology": "Adenocarcinoma",
    "stage": "IIIB",
    "biomarkers": {
      "KRAS": "G12D mutation", "NRAS": "Wild-type",
      "BRAF": "Wild-type", "MSI": "MSS", "HER2": "Negative"
    }
  },
  "treatments": [{
    "line": "Adjuvant",
    "regimen": "FOLFOX + Bevacizumab",
    "cycleNumber": 8,
    "toxicities": [{"event": "Peripheral Neuropathy", "grade": 2}]
  }],
  "surgicalHistory": [{
    "procedure": "Laparoscopic Sigmoid Colectomy",
    "outcome": "R0 resection, 18 lymph nodes examined, 3 positive"
  }],
  "symptoms": ["Mild tingling in fingers", "Fatigue"]
}
```

---

## 13 Clinical Feedback Items (All Implemented)

These were requested by the clinical advisor and are all live:

1. **Comorbidity-aware responses** — Diabetes, hypertension, heart/kidney disease interactions surfaced in treatment/side_effect queries
2. **Treatment line auto-detection** — FOLFOX → 1L/adjuvant, Regorafenib → 3L+, Pembrolizumab → 1L MSI-H (with confidence levels)
3. **PHQ-9 & GAD-7 screening** — Full validated instruments with severity scoring and crisis protocol (Q9 suicidal ideation → 988 Lifeline)
4. **PSS-10 (Perceived Stress Scale)** — 10-item instrument with reverse scoring
5. **ISI (Insomnia Severity Index)** — 7-item sleep screening
6. **ANP tone framework** — Acknowledge → Normalize → Partner; 3 sensitivity levels; toxic positivity filter
7. **Clinical trial jargon help** — Plain-language definitions for Phase I/II/III, randomized, placebo, etc.
8. **Stress-immune education** — Based on D'Andre 2024; careful framing (no causal claims)
9. **Screening ambassador** — Family screening advocacy, barriers education, home test options
10. **Caregiver support** — Dedicated query type, ACS/NCI resources
11. **Holistic wellness** — Exercise, yoga, mindfulness recommendations
12. **Compassionate use guidance** — FDA expanded access, Right to Try, Project Facilitate
13. **Stage IV personalization** — Palliative context, SPIKES protocol, honest but empowering responses

---

## Knowledge Base (20 Documents, 1,737 Chunks)

| Document | Chunks | Topic |
|----------|--------|-------|
| colon.pdf | 809 | Comprehensive colon cancer reference |
| the_american_society_of_colon_and_rectal_surgeons.7.pdf | 143 | ASCRS guidelines |
| colon cancer survivorship.pdf | 125 | Survivorship care |
| colon cancer review 1-3.pdf | 240 | Clinical reviews |
| Cancer_Stress_DAndre_2024.pdf | 81 | Stress-immune pathways |
| Comprehensive_Colon_Cancer_Guide_441_QA.pdf | 82 | 441 Q&A pairs |
| colon-patient.pdf | 66 | Patient education |
| Cancer_Sleep_Disorders.pdf | 63 | Sleep and cancer |
| colon cancer screening.pdf | 50 | Screening guidelines |
| Prevention and Screening Strategies.pdf | 34 | Prevention strategies |
| NCI_Caring_for_Caregiver_2024.pdf | 17 | Caregiver guidance |
| Colon Cancer_Emergency_Urgent_Symptoms.pdf | 16 | Emergency symptoms |
| Other reference docs | 11 | PSS-10, screening barriers, ACS caregiver, NCI stress, treatment lines |

**RAG approach:** TF-based keyword search with medical term boosting (not vector embeddings). Cosine similarity with phrase bonuses. Dynamic threshold filtering ensures 2-5 chunks returned per query.

---

## Database Tables (Supabase)

| Table | Purpose |
|-------|---------|
| patient_profiles | Patient medical data (raw_profile JSON) |
| pdf_chunks | Indexed document chunks (document_id, content, chunk_index) |
| pdf_documents | Document metadata (filename, chunk_count, status) |
| chat_messages | Chat history (user_id, role, content, metadata JSONB) |
| conversations | Chat sessions |
| messages | Individual messages within conversations |
| user_acknowledgements | Disclaimer acceptance |
| screening_scores | PHQ-9, GAD-7, PSS-10, ISI scores (instrument, scores, total_score, severity_label) |
| chat_feedback | Thumbs up/down on responses |

---

## Test Results (Latest: March 2026)

**60 tests total — 57 passed (95%)**

- Unit tests: 23/23 (treatment line detection, comorbidity interactions, tone sensitivity, query classification)
- LLM integration tests: 34/37 (all 13 clinical items tested across 2 patient profiles)
- 3 failures are LLM wording variability, not code bugs

---

## Current Strengths

1. **Profile-driven personalization** — Every response considers the patient's specific biomarkers, stage, comorbidities, and treatment
2. **9-category query routing** — Right context for right question
3. **Tone sensitivity** — Handles "Am I going to die?" differently than "What is FOLFOX?"
4. **Clinical trials integration** — Auto-searches ClinicalTrials.gov with relevance scoring (0-100)
5. **Mental health screening** — 4 validated instruments with crisis detection
6. **Dual-LLM fallback** — Together AI (70B) primary, Groq (8B) fallback
7. **Safety guardrails** — PII sanitization, medical validation, toxic positivity filter, emergency detection

---

## Known Gaps & Limitations

### Feature Gaps
- No symptom tracking dashboard or longitudinal trends
- No nutrition/dietary interactive tools (only referral links)
- No treatment timeline visualization
- No drug-drug interaction checking (only comorbidity-drug interactions)
- No survivorship surveillance schedule or follow-up reminders
- No hereditary cancer risk calculator (Lynch syndrome, FAP)
- No caregiver-specific profile or mode
- Screening scores are saved but not visualized over time

### Technical Gaps
- Frontend is a single 7,445-line HTML file (no component framework)
- TF-based search (no vector embeddings) — keyword-dependent, may miss semantic matches
- No outcome tracking or feedback loop to improve recommendations
- No formal test framework (pytest) — ad-hoc test scripts only
- No CI/CD pipeline (manual Vercel deploys)
- English-only (no i18n)
- Web-only (no native mobile app, no offline support)
- No telehealth or EHR integration

### Compliance Gaps
- No FDA 21 CFR Part 11 documentation
- No WCAG 2.1 AA accessibility audit
- No explainability audit trail (which chunks influenced which response)
- Limited adverse event reporting (only PHQ-9 Q9 crisis detection)

---

## Environment Variables Required

```
GROQ_API_KEY          — Groq LLM API
TOGETHER_API_KEY      — Together.ai LLM API
SUPABASE_URL          — Supabase project URL
SUPABASE_KEY          — Supabase public key
SUPABASE_SERVICE_ROLE_KEY — Supabase admin key
```

---

## Dependencies

```
flask==2.3.3
supabase>=2.0.0
python-dotenv==1.0.0
groq>=0.8.0
together>=1.0.0
pdfplumber==0.7.6
PyPDF2==3.0.1
tiktoken>=0.5.0
```

---

## Deployment

- Vercel serverless (Python runtime)
- Static frontend served from /public/
- Lambda size limit: 50MB
- Team: wondr-chat on Vercel
- Repo: github.com/sivpic27/WondrLink-Projects
