# WondrLink Chat — Project Report

## 1. Executive Summary

WondrLink Chat is a web-based tool designed to help colon cancer patients and their caregivers better understand their diagnosis, treatment options, and care journey. It acts as a personal health education companion — answering questions in plain language, tailored to each patient's unique medical profile.

The app pulls from trusted medical guidelines (NCCN, ACS, NCI), searches for relevant clinical trials on ClinicalTrials.gov, and presents information in a warm, supportive tone. It is not a replacement for medical advice, but a bridge that helps patients feel more informed and prepared for conversations with their oncology team.

**Key highlights:**
- Personalized responses based on the patient's cancer stage, biomarkers, and treatment history
- Real-time clinical trial matching with relevance scoring and geographic proximity
- Built-in safety features including emergency symptom detection and medical disclaimers
- Accessible design with voice input, mobile support, and screen reader compatibility

---

## 2. Who It's For

**Primary users:** Patients diagnosed with colon or colorectal cancer at any stage (I–IV), and their caregivers or family members.

**What they need:** Clear, trustworthy answers to questions like:
- "What does my stage mean?"
- "What are my treatment options?"
- "Are there clinical trials near me?"
- "What side effects should I watch for?"
- "How do I prepare for my next appointment?"

---

## 3. How It Works (High Level)

1. **Sign up & build a profile** — The patient creates an account and fills in a guided 6-step profile covering their diagnosis, stage, biomarkers, treatments, and symptoms.
2. **Ask questions** — The patient types (or speaks) a question in the chat window.
3. **Get a personalized answer** — The system looks up relevant medical guidelines, considers the patient's profile, and generates an answer tailored to their situation.
4. **Find clinical trials** — When relevant, the app automatically searches ClinicalTrials.gov and shows matching trials with distance, eligibility info, and match strength.
5. **Save and export** — Patients can bookmark trials, export chat history, and provide feedback on responses.

---

## 4. Features

### 4.1 Patient Profile Wizard

A guided 6-step setup that captures the patient's complete picture:

| Step | What's Collected |
|------|-----------------|
| 1. Patient Info | Name, age, zip code, sex, activity level, allergies, other health conditions |
| 2. Diagnosis | Cancer type (e.g., adenocarcinoma), stage (I–IV) |
| 3. Test Results | Biomarkers — MSI status, KRAS, NRAS, BRAF, HER2, and more |
| 4. Treatment | Current and past treatments, regimen names, treatment line, side effects |
| 5. Symptoms | Current symptoms the patient is experiencing |
| 6. Review | Summary of everything entered, with the ability to go back and edit |

The profile is used to personalize every response the patient receives.

### 4.2 Conversational Chat

- **Plain language answers** — Medical concepts explained without jargon
- **Voice input** — Patients can speak their question instead of typing
- **Conversation memory** — The app remembers what was discussed earlier in the session
- **Response length control** — Users can choose brief, normal, or detailed answers
- **Suggested questions** — Clickable starter questions to help patients get going
- **Feedback buttons** — Thumbs up/down on each response to help improve the system
- **Chat export** — Download the full conversation as a text file

### 4.3 Medical Knowledge Base

The app is powered by **11 medical documents** (guidelines, research papers, and patient education materials) covering:

- NCCN Patient Guidelines for Colon Cancer
- American Society of Colon and Rectal Surgeons (ASCRS) guidelines
- Comprehensive colon cancer care guides
- Screening and prevention protocols
- Survivorship and follow-up care
- Emergency symptom references

When a patient asks a question, the system searches through these documents to find the most relevant information and uses it to form its answer. This ensures responses are grounded in evidence-based medical literature, not general knowledge.

### 4.4 Clinical Trials

One of the app's most powerful features. When a patient asks about clinical trials (or the system detects it's relevant):

- **Real-time search** — Queries ClinicalTrials.gov for currently recruiting trials
- **Personalized matching** — Filters by the patient's cancer type, stage, biomarkers, treatment history, age, and sex
- **Relevance scoring** — Each trial is scored 0–100 and labeled as Strong, Moderate, or General match
- **Distance calculation** — Shows how far each trial site is from the patient's zip code
- **Eligibility warnings** — Flags potential issues (e.g., "minimum age is 65, patient is 58")
- **Safety disclaimers** — Amber warning banner reminding patients to verify info with their oncologist
- **External resources** — Links to ClinicalTrials.gov, CCA Trial Finder, and NCI Trial Search
- **Bookmark/watchlist** — Patients can save trials they're interested in and view them in a sidebar panel anytime
- **Doctor questions** — Each trial discussion includes suggested questions to bring to the oncologist
- **Cost guidance** — Information about how clinical trial costs typically work (experimental treatment often covered, routine care billed to insurance)

### 4.5 Safety Features

- **Emergency symptom detection** — If a patient describes symptoms like high fever during chemo, severe bleeding, breathing difficulty, or chest pain, the app immediately displays a red emergency banner with guidance to call 911 or go to the ER
- **Urgent symptom detection** — For less critical but important symptoms (worsening pain, inability to eat/drink), an orange urgent banner advises contacting the oncology team the same day
- **Medical disclaimers** — Every response is framed as educational, not medical advice
- **First-time acknowledgement** — New users must read and accept a disclaimer before accessing the app
- **PII protection** — The system automatically detects and removes personal information (Social Security numbers, phone numbers, etc.) from messages before they are processed
- **Anti-hallucination guardrails** — The AI is instructed to never fabricate trial names, drug names, or statistics. If unsure, it says so

### 4.6 Accessibility & Design

- **Mobile-friendly** — Responsive design that works on phones, tablets, and desktops
- **Voice input** — For patients who have difficulty typing
- **Screen reader support** — ARIA labels, live regions, and keyboard navigation throughout
- **High contrast** — Clear, readable text and color-coded elements
- **Skip navigation** — Keyboard shortcut to jump directly to the chat area
- **Privacy & Terms modals** — Accessible policy documents available from the footer

---

## 5. Technology Overview

| Component | What It Does |
|-----------|-------------|
| **Frontend** | A single web page (HTML, CSS, JavaScript) that runs in the browser — no app download needed |
| **Backend** | A Python server that handles all the logic — processing questions, searching documents, calling the AI |
| **Database** | Supabase (cloud-hosted PostgreSQL) stores patient profiles, chat history, and document content |
| **AI Models** | Two AI language models work together — a primary model (Llama 3.3 70B via Together AI) for complex questions, and a backup model (Llama 3.1 8B via Groq) for reliability |
| **Medical Documents** | 11 PDF guideline documents processed and indexed for search |
| **Clinical Trials API** | ClinicalTrials.gov (US government database) queried in real-time |
| **Hosting** | Vercel serverless platform — scales automatically, no server maintenance needed |
| **Authentication** | Secure email/password login with JWT tokens |

---

## 6. How Responses Are Generated

When a patient asks a question, the system goes through several steps:

1. **Safety check** — Remove any personal information from the message
2. **Classify the question** — Is this about treatment, side effects, clinical trials, prognosis, or general information?
3. **Search the knowledge base** — Find the most relevant sections from the 11 medical documents
4. **Build context** — Combine the patient's profile, relevant guidelines, and conversation history
5. **Generate answer** — Send everything to the AI model, which produces a personalized response
6. **Validate** — Check the response for medical safety (e.g., flag if it contains emergency symptoms)
7. **Add resources** — Attach relevant links to trusted organizations (NCI, ACS, NCCN, etc.)
8. **Search trials** — If the question is about clinical trials, also query ClinicalTrials.gov
9. **Return to patient** — Display the answer with any trial cards, urgency banners, or resource links

---

## 7. Recent Improvements

### Clinical Trials Enhancements
- Added safety disclaimers and a visible warning banner above trial results
- Trials now scored and filtered based on patient biomarkers, age, and treatment history
- Added links to CCA Trial Finder and NCI Trial Search alongside ClinicalTrials.gov
- Users can now bookmark trials they're interested in and view them in a sidebar watchlist
- AI responses now include suggested questions for the oncologist and cost/insurance guidance
- Improved distinction between colon and rectal cancer trials

### General App Improvements
- Added emergency and urgent symptom detection with colored alert banners
- Added privacy policy and terms of use modals
- Input validation and PII sanitization on all user messages
- Chat export to downloadable text file
- Thumbs up/down feedback on every AI response
- Dynamic suggested questions that adapt to the patient's profile
- Multiple accessibility improvements (ARIA labels, keyboard navigation, screen reader support)

---

## 8. What's Next

Potential future enhancements:
- **Response caching** for faster, more consistent answers to common questions
- **Multi-language support** for non-English-speaking patients
- **Integration with electronic health records** for automatic profile population
- **Caregiver accounts** with shared access to patient profiles
- **Push notifications** for trial status changes on bookmarked trials

---

## 9. Summary

WondrLink Chat is a patient-centered tool that combines trusted medical knowledge, personalized AI responses, and real-time clinical trial matching to help colon cancer patients navigate their care journey with confidence. Every feature is designed with the patient's wellbeing in mind — from the warm conversational tone to the emergency symptom detection to the trial bookmark feature.

The app is live, functional, and actively being improved based on user needs and quality assurance feedback.

---

*Report prepared by Siva Pichappan — February 2026*
