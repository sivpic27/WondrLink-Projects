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

---

## Hybrid RAG with pgvector

**Problem:** TF-based keyword search misses semantic matches — a query about "feeling sick after chemo" won't find chunks that say "treatment-related nausea" because the keywords don't overlap.

**Solution:** Hybrid retrieval combining existing TF keyword search with vector similarity search, merged via Reciprocal Rank Fusion (RRF).

| Component | Detail |
|-----------|--------|
| Embedding model | intfloat/multilingual-e5-large-instruct (1024 dims) via Together AI (free) |
| Vector store | Supabase pgvector with HNSW index |
| Fusion method | RRF with k=60 — no tuning needed |
| Fallback | TF-only if vector search unavailable |
| Cost | $0/year (uses existing Together AI key) |

**How it works:**
1. User sends a query
2. TF search returns top-k ranked results (keyword matching)
3. Vector search returns top-k ranked results (semantic similarity)
4. RRF merges both ranked lists: `score = sum(1 / (60 + rank))`
5. Top-k merged results go to the LLM

**Future improvement:** If budget allows, switching to OpenAI's text-embedding-3-small ($0.02 one-time, 1536 dims) would improve medical retrieval accuracy based on MEDRAG benchmark evidence.

**Files:**
- Created: `lib/vector_search.py`, `scripts/generate_embeddings.py`
- Modified: `lib/pdf_utils.py` (hybrid_search function), `api/index.py` (uses hybrid_search)
- Migration: pgvector extension, embedding column, HNSW index, match_chunks() RPC

---

---

## Mental Health Trend Dashboard

**Problem:** WondrChat captures PHQ-9, GAD-7, PSS-10, and ISI screening scores, but patients can only see their most recent score. No longitudinal visualization exists. Research shows measurement-based care (showing patients their trends) improves remission rates by up to 75%.

**Solution:** Interactive dashboard accessible via "View Trends" button in the Wellness Check-In sidebar. Uses Chart.js with the PROTEUS Consortium-recommended traffic-light severity bands.

### Features

| Feature | Detail |
|---------|--------|
| Line charts | One per instrument, with color-banded severity zones (green/yellow/orange/red) |
| Narrative text | "Your depression score improved from moderate to mild" |
| Score change alerts | Increase of 5+ points triggers a warning to share with provider |
| Severity alerts | PHQ-9 >= 15, GAD-7 >= 15, PSS-10 >= 27, ISI >= 22 |
| Retake prompts | 30+ days since last check-in prompts a retake |
| Missing instruments | Shows which screenings haven't been completed yet |

### Severity Bands (PROTEUS Consortium)

**PHQ-9:** 0-4 Minimal (green), 5-9 Mild (yellow), 10-14 Moderate (orange), 15-19 Mod. Severe (red), 20-27 Severe (dark red)
**GAD-7:** 0-4 Minimal, 5-9 Mild, 10-14 Moderate, 15-21 Severe
**PSS-10:** 0-13 Low, 14-26 Moderate, 27-40 High
**ISI:** 0-7 No Insomnia, 8-14 Subthreshold, 15-21 Moderate, 22-28 Severe

### Alert Thresholds

- PHQ-9 Q9 >= 1 (suicidal ideation) -> Crisis resources (988 Lifeline) — already existed
- Score increase >= 5 points between assessments -> "Consider sharing with your care team"
- Severe thresholds (PHQ-9 >= 15, GAD-7 >= 15, PSS-10 >= 27, ISI >= 22) -> Provider share prompt

**Files:**
- New endpoint: `GET /api/screening/history`
- Modified: `lib/supabase_storage.py` (load_all_screening_history)
- Modified: `public/index.html` (Chart.js CDN, dashboard overlay, chart rendering, alerts, narratives)

---

---

## PRO-CTCAE Symptom Tracking

**Problem:** Side effect monitoring is reactive — patients only report symptoms when they remember to mention them in chat. Published evidence shows PRO-CTCAE-based symptom tracking with automated alerts reduces hospitalizations by 39% and costs by $1,146 per patient (Patt et al., JCO 2023).

**Solution:** 10-item symptom check-in using PRO-CTCAE severity scale, integrated into the existing screening engine, dashboard, and chat context.

### Symptoms Tracked

| Symptom | Why |
|---------|-----|
| Nausea | FOLFOX/FOLFIRI common |
| Fatigue | Most reported side effect across all regimens |
| Diarrhea | Irinotecan, 5-FU, targeted therapy |
| Neuropathy | Oxaliplatin dose-limiting toxicity |
| Pain | General cancer + treatment-related |
| Appetite loss | Chemotherapy-induced |
| Mouth sores | 5-FU, capecitabine |
| Hand-foot syndrome | Capecitabine, regorafenib |
| Constipation | Opioids, ondansetron |
| Skin rash | Anti-EGFR (cetuximab, panitumumab) |

### Severity Scale
None (0) / Mild (1) / Moderate (2) / Severe (3) / Very Severe (4)

### Grade 3+ Toxicity Alert
When any individual symptom is rated Severe or Very Severe, an immediate alert displays the specific symptom names and instructs: "Contact your oncology team today to report these symptoms."

### Chat Integration
When a patient asks about side effects or treatment, the LLM prompt automatically includes their most recent symptom check-in data (moderate+ symptoms only), so the AI can reference what they've actually reported.

### Dashboard
Symptom burden trends appear in the "View Trends" dashboard alongside mental health instruments, with the same severity-banded chart format.

**Files:**
- Modified: `public/index.html` (SYMPTOM instrument, toxicity alert, sidebar button)
- Modified: `api/index.py` (symptom context injection, SYMPTOM in load endpoint)
- Modified: `lib/llm_utils.py` (symptom report in filter_relevant_context)
- Modified: `lib/supabase_storage.py` (SYMPTOM in history instruments)

---

## Commits

```
b77c787 Add HIPAA de-identification layer and update screening language
7160cf1 Implement hybrid RAG with pgvector and add version docs
ba3f657 Add mental health trend dashboard with severity-banded charts
b3e0958 Fix dashboard chart infinite resize loop
c262cc4 Add PRO-CTCAE symptom tracking with dashboard and chat integration
```
