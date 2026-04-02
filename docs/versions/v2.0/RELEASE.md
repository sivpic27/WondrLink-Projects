# WondrChat 2.0

**Release Date:** March 2026
**Status:** Production (https://wondrchat.vercel.app)

---

## Overview

WondrChat 2.0 is a comprehensive healthcare AI chatbot built specifically for colon cancer patients, caregivers, and family members. It provides personalized, evidence-based answers grounded in medical guidelines and powered by a dual-LLM architecture with a 20-document RAG knowledge base.

---

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Single-page HTML/CSS/JS (public/index.html) |
| Backend | Flask (Python 3.9) on Vercel serverless |
| Database | Supabase (PostgreSQL) with Row Level Security |
| Primary LLM | Together AI (Llama 3.3 70B) |
| Fallback LLM | Groq (Llama 3.1 8B) |
| RAG | TF-based keyword search with medical term boosting |
| Clinical Trials | ClinicalTrials.gov API v2 |
| Auth | Supabase Auth (JWT Bearer tokens) |

---

## Features

### Core Chat System
- 21 API endpoints (auth, chat, profile, screening, trials, feedback)
- 9-category query classification: clinical_trial, treatment, side_effect, prognosis, diagnosis, caregiver, screening_ambassador, emotional, general
- Dual-LLM fallback (Together AI primary, Groq secondary)
- PII detection and sanitization on user input
- Medical response validation and safety checks
- Token budgeting and response length control (normal/brief/detailed)

### Patient Profile System
- JSON-based patient profile upload or 6-step form wizard
- Extracts: demographics, diagnosis, stage, biomarkers, treatments, comorbidities, symptoms
- Profile-driven response personalization
- Cancer type mismatch detection
- Profile update extraction from chat messages

### RAG Knowledge Base
- 20 medical documents indexed into 1,737 chunks
- TF-based keyword search with medical term boosting
- Cosine similarity with phrase bonus detection
- Dynamic threshold filtering (2-5 chunks per query)
- Documents include: NCCN guidelines, ASCRS guidelines, clinical reviews, survivorship guides, stress/sleep research, caregiver resources, screening barriers

### Clinical Trials Integration
- ClinicalTrials.gov API v2 search
- Geolocation-based trial matching (zip code to distance)
- Trial relevance scoring (0-100) based on biomarkers, cancer type, treatment history
- Patient profile cross-checking (age, sex, biomarkers, treatment line, distance)
- Search readiness validation (requires zip code and stage)
- Frontend relevance badges (Strong/Moderate/General match)

### 13 Clinical Feedback Items

**Personalization (Phase 1):**
1. Comorbidity-aware responses — drug-disease interaction warnings for diabetes, hypertension, heart/kidney disease, obesity, neuropathy, liver disease, COPD
2. Treatment line auto-detection — infers 1L/2L/3L+ from medication names (FOLFOX, Regorafenib, Pembrolizumab, etc.) with confidence levels
3. ANP tone framework — Acknowledge, Normalize, Partner. Three sensitivity levels (HIGH/MEDIUM/LOW). Toxic positivity filter blocks phrases like "stay positive", "you'll be fine"
4. Stage IV personalization — palliative care context, SPIKES protocol, honest but empowering responses for advanced-stage patients

**Mental Health Screening (Phase 2):**
5. PHQ-9 (depression) — 9-item validated instrument with severity scoring and crisis protocol (Q9 suicidal ideation triggers 988 Lifeline)
6. GAD-7 (anxiety) — 7-item validated instrument with severity scoring
7. PSS-10 (perceived stress) — 10-item instrument with reverse scoring
8. ISI (insomnia severity) — 7-item sleep screening

**Content Enrichment (Phase 3):**
9. Clinical trial jargon help — plain-language definitions for Phase I/II/III, randomized, placebo, double-blind, eligibility
10. Stress-immune education — based on D'Andre 2024 analytical review; careful framing with no causal claims
11. Caregiver support — dedicated query type, ACS and NCI caregiver resources
12. Compassionate use guidance — FDA expanded access, Right to Try Act, Project Facilitate

**Engagement (Phase 4):**
13. Screening ambassador — family screening advocacy, barriers education, home test options (FIT, Cologuard)
14. Holistic wellness — evidence-based exercise, yoga, mindfulness recommendations

### Authentication and Safety
- Supabase Auth with JWT Bearer tokens
- Medical disclaimer acknowledgement flow
- PII detection and sanitization (SSN, DOB, phone, email, address, credit card)
- Response validation with medical safety checks
- Emergency/urgency detection with immediate care guidance
- Crisis resources for suicidal ideation (988 Lifeline, Crisis Text Line, 911)

### Database Schema
- patient_profiles — patient medical data
- pdf_chunks / pdf_documents — indexed knowledge base
- chat_messages — conversation history with metadata
- screening_scores — PHQ-9, GAD-7, PSS-10, ISI results
- user_acknowledgements — disclaimer acceptance
- chat_feedback — thumbs up/down on responses

### Testing
- 60-test comprehensive suite (scripts/test_all_features.py)
- Two test profiles: Stage IIIB and Stage IV
- 23 unit tests + 37 LLM integration tests
- Covers all 13 clinical feedback items + KB expansion + regression

---

## Knowledge Base Documents (20)

| Document | Chunks | Topic |
|----------|--------|-------|
| colon.pdf | 809 | Comprehensive colon cancer reference |
| the_american_society_of_colon_and_rectal_surgeons.7.pdf | 143 | ASCRS guidelines |
| colon cancer survivorship.pdf | 125 | Survivorship care |
| colon cancer review 1-3.pdf | 240 | Clinical reviews (3 docs) |
| Cancer_Stress_DAndre_2024.pdf | 81 | Stress-immune pathways |
| Comprehensive_Colon_Cancer_Guide_441_QA.pdf | 82 | 441 Q&A pairs |
| colon-patient.pdf | 66 | Patient education |
| Cancer_Sleep_Disorders.pdf | 63 | Sleep and cancer |
| colon cancer screening.pdf | 50 | Screening guidelines |
| Prevention and Screening Strategies.pdf | 34 | Prevention strategies |
| NCI_Caring_for_Caregiver_2024.pdf | 17 | Caregiver guidance |
| Colon Cancer_Emergency_Urgent_Symptoms.pdf | 16 | Emergency symptoms |
| Perceived_Stress_Scale_Reference.pdf | 3 | PSS validation |
| NCI_Stress_Cancer_Fact_Sheet.pdf | 2 | Stress education |
| CRC_Screening_Barriers.pdf | 2 | Screening barriers |
| PSS10_Clinical_Reference.pdf | 2 | PSS-10 scoring |
| CRC_Treatment_Line_Reference.pdf | 1 | Treatment lines |
| ACS_Caregiver_Support.pdf | 1 | ACS caregiver resources |

---

## Deployment
- Vercel serverless (Python runtime)
- Static frontend from /public/
- Lambda size limit: 50MB
- Team: wondr-chat
- Live URL: https://wondrchat.vercel.app
