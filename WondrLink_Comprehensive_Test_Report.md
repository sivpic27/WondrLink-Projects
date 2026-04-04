# WondrLink Comprehensive Test Report

**Generated:** 2026-04-03 21:45:06

**Total Tests:** 60
**Passed:** 56/60 (93.3%)


---
## 1. Unit Tests

**Passed:** 23/23


### Item 2: Treatment Line

- **[PASS]** `auto_detect_treatment_line('FOLFOX + Bevacizumab', None)`
  - Expected: line=1L_or_adj, confidence=medium
  - Actual: detected=True, line=1L_or_adj, confidence=medium
- **[PASS]** `auto_detect_treatment_line('CAPOX', None)`
  - Expected: line=1L_or_adj, confidence=medium
  - Actual: detected=True, line=1L_or_adj, confidence=medium
- **[PASS]** `auto_detect_treatment_line('Regorafenib', None)`
  - Expected: line=3L+, confidence=high
  - Actual: detected=True, line=3L+, confidence=high
- **[PASS]** `auto_detect_treatment_line('TAS-102', None)`
  - Expected: line=3L+, confidence=high
  - Actual: detected=True, line=3L+, confidence=high
- **[PASS]** `auto_detect_treatment_line('Pembrolizumab', {'MSI': 'MSS'})`
  - Expected: line=1L_msi_h, confidence=low
  - Actual: detected=True, line=1L_msi_h, confidence=low
- **[PASS]** `auto_detect_treatment_line('Pembrolizumab', {'MSI': 'MSI-H'})`
  - Expected: line=1L_msi_h, confidence=high
  - Actual: detected=True, line=1L_msi_h, confidence=high
- **[PASS]** `auto_detect_treatment_line('FOLFIRI', None)`
  - Expected: line=1L_or_2L, confidence=medium
  - Actual: detected=True, line=1L_or_2L, confidence=medium
- **[PASS]** `auto_detect_treatment_line('Some random drug', None)`
  - Expected: line=None, confidence=None
  - Actual: detected=False, line=None, confidence=None

### Item 1: Comorbidity Unit

- **[PASS]** `get_comorbidity_interactions(['Type 2 Diabetes', 'Hypertension'], 'treatment')`
  - Expected: Non-empty list with diabetes and hypertension notes
  - Actual: 3 interactions returned
- **[PASS]** `get_comorbidity_interactions(['Type 2 Diabetes'], 'general')`
  - Expected: Empty list (general queries don't get comorbidity context)
  - Actual: 0 interactions returned

### Item 6: Tone Sensitivity

- **[PASS]** `Tone sensitivity for: 'Am I going to die?'`
  - Expected: high
  - Actual: high
- **[PASS]** `Tone sensitivity for: 'I'm so scared and anxious'`
  - Expected: medium
  - Actual: medium
- **[PASS]** `Tone sensitivity for: 'What diet should I follow?'`
  - Expected: low
  - Actual: low
- **[PASS]** `Tone sensitivity for: 'Will I survive this?'`
  - Expected: high
  - Actual: high
- **[PASS]** `Tone sensitivity for: 'What is my life expectancy?'`
  - Expected: high
  - Actual: high
- **[PASS]** `Tone sensitivity for: 'I feel hopeless'`
  - Expected: medium
  - Actual: medium
- **[PASS]** `Tone sensitivity for: 'What is FOLFOX?'`
  - Expected: low
  - Actual: low

### Query Classification

- **[PASS]** `classify_query_type('I'm caring for my husband who has colon cancer...')`
  - Expected: caregiver
  - Actual: caregiver
- **[PASS]** `classify_query_type('Should my children get screened for colon cancer?...')`
  - Expected: screening_ambassador
  - Actual: screening_ambassador
- **[PASS]** `classify_query_type('The tingling in my fingers is getting worse from F...')`
  - Expected: side_effect
  - Actual: side_effect
- **[PASS]** `classify_query_type('What is FOLFOX and how does it work?...')`
  - Expected: treatment
  - Actual: treatment
- **[PASS]** `classify_query_type('I'm feeling anxious and scared...')`
  - Expected: emotional
  - Actual: emotional
- **[PASS]** `classify_query_type('What does Phase III mean in a clinical trial?...')`
  - Expected: clinical_trial
  - Actual: clinical_trial


---
## 2. Profile A Tests (Stage IIIB)

**Patient:** John Martinez — Stage IIIB, FOLFOX + Bevacizumab
**Comorbidities:** Type 2 Diabetes, Hypertension, Mild Peripheral Neuropathy
**Passed:** 28/31


### Item 6: Empathy Tone

#### [PASS] Q: Am I going to die?
*HIGH sensitivity — full ANP framework expected*


**Answer:** It's completely understandable that you're worried about your prognosis, and it's natural to have fears about the future. Your feelings make sense, and many people in your situation wonder about this. Given your stage IIIB sigmoid colon adenocarcinoma and current treatment with FOLFOX + Bevacizumab, your care team can help you understand the potential outcomes and what to expect, taking into account your KRAS mutation and MSS status, which may impact the effectiveness of certain treatments.

You...

*API: together | Query type: prognosis | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = prognosis
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0

#### [PASS] Q: I'm so scared about my diagnosis. I can't stop crying.
*MEDIUM sensitivity — normalization expected*


**Answer:** It sounds like you're feeling overwhelmed and scared about your diagnosis, and that's completely understandable - it's normal to feel that way when faced with a serious health issue. Many people in your situation experience anxiety, fear, and sadness, and it's okay to acknowledge and express these emotions. You might find it helpful to talk to an oncology social worker or call the Cancer Support Helpline at 1-888-793-9355 for emotional support and guidance.

You might also want to ask about: 
• ...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = emotional
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0

#### [PASS] Q: What diet should I follow during chemo?
*LOW sensitivity — must NOT trigger high tone from 'die' in 'diet'*


**Answer:** It sounds like you're looking for ways to manage your diet during chemotherapy, and I can imagine how overwhelming that must feel. Many people facing cancer treatment feel this way, and it's great that you're taking proactive steps to understand your options. During chemotherapy, it's often helpful to eat small, frequent meals to manage nausea, and cold or room-temperature foods can be easier to tolerate. You might consider trying bland, starchy foods like crackers, toast, or rice, and drinking ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Chunks > 0

#### [PASS] Q: I feel like giving up. Nothing is working.
*HIGH sensitivity — acknowledge + normalize expected*


**Answer:** It sounds like you're feeling really overwhelmed and hopeless right now, and that's completely understandable given what you're going through. Many people with cancer feel this way at some point, and it's okay to acknowledge those feelings. You might find it helpful to talk to an oncology social worker or join a support group, where you can share your feelings and connect with others who are going through similar experiences - you can reach out to the Cancer Support Helpline at 1-888-793-9355 fo...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = emotional
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0


### Item 1: Comorbidity

#### [FAIL] Q: What side effects should I watch for with my FOLFOX treatment?
*Should mention diabetes-chemo interaction (dexamethasone)*


**Answer:** It sounds like you're concerned about the side effects of your FOLFOX treatment, and that's completely understandable. With FOLFOX, you should watch for side effects like fatigue, nausea, diarrhea, and peripheral neuropathy, which can cause numbness or tingling in your hands and feet. If you experience any of these side effects, you can try managing them by eating small, frequent meals, staying hydrated, and avoiding cold foods and drinks, especially during and after oxaliplatin infusions - and ...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [FAIL] Contains 'diabet'
- [PASS] Chunks > 0

#### [PASS] Q: Can my diabetes affect how I tolerate chemotherapy?
*Should mention steroid-glucose interaction*


**Answer:** It sounds like you're concerned about how your diabetes might affect your chemotherapy experience, and that's a very valid concern. Your diabetes can impact how you tolerate chemotherapy, as some chemotherapy drugs may affect your blood sugar levels or interact with your diabetes medications. For example, steroids like dexamethasone, which are sometimes used with chemotherapy, can raise blood sugar levels. You might also want to ask about: 
• How to manage your blood sugar levels during chemothe...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'diabetes'
- [PASS] Chunks > 0

#### [PASS] Q: I have hypertension. Is bevacizumab safe for me?
*Should mention bevacizumab-hypertension interaction*


**Answer:** It sounds like you're concerned about how bevacizumab might affect your hypertension, and that's a really valid concern. Bevacizumab can indeed increase blood pressure, so it's essential to monitor your blood pressure regularly while on this treatment. You might want to discuss with your oncologist how to manage your hypertension while on bevacizumab, as they can help you weigh the benefits and risks. 

Given your KRAS mutation and MSS status, bevacizumab is being used in combination with FOLFOX...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'blood pressure'
- [PASS] Contains 'hypertension'
- [PASS] Chunks > 0


### Item 8: Stress-Immune

#### [PASS] Q: Can stress make my cancer worse?
*Must NOT make causal claims about stress and cancer*


**Answer:** It sounds like you're feeling anxious about how stress might affect your cancer, and that's completely understandable. Managing stress is important for your overall wellbeing and quality of life during treatment, as it can help with sleep, energy, and mood. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours; in the meantime, try relaxation techniques like deep breathing, meditation, or short walks to help manage stress. 

You might also...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = emotional
- [PASS] Contains 'wellbeing'
- [PASS] Contains 'quality of life'
- [PASS] No 'stress causes cancer'
- [PASS] No 'stress makes cancer worse'
- [PASS] No 'stress will make your cancer worse'
- [PASS] Chunks > 0

#### [PASS] Q: Tell me about mindfulness for cancer patients
*Should mention MBSR or mindfulness-based programs*


**Answer:** Mindfulness can be a powerful tool for cancer patients, helping to reduce stress and anxiety, improve mood, and even manage symptoms like fatigue and nausea. You can try mindfulness practices like meditation, deep breathing, or yoga to help you feel more calm and centered during treatment. The Society for Integrative Oncology and CancerCare offer resources and guidance on mindfulness-based stress reduction, which has been specifically studied in cancer populations. 

You might also want to ask a...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'MBSR'
- [PASS] Contains 'mindfulness'
- [PASS] Chunks > 0


### Item 10: Caregiver

#### [FAIL] Q: I'm caring for my husband who has colon cancer. How can I help him?
*Should classify as caregiver and provide caregiver-specific guidance*


**Answer:** It sounds like you're taking on a big role in supporting your husband through his colon cancer journey, and that's truly admirable. To help him, you can start by tracking his treatment schedule and side effects, and encouraging him to stay hydrated and eat small, frequent meals to manage nausea and fatigue. You can also offer emotional support by listening to his concerns and feelings, and reminding him that it's okay to take breaks and rest when needed. 

You might also want to ask about: 
• Ho...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = caregiver
- [FAIL] Contains 'caregiver'
- [PASS] Chunks > 0

#### [PASS] Q: How do I help my wife manage her chemo side effects at home?
*Should classify as caregiver*


**Answer:** It sounds like you're looking for ways to support your wife during this challenging time, and that's truly admirable. To help manage her chemo side effects at home, you can start by keeping a symptom journal to track when side effects occur and how severe they are, which can be helpful to share with her medical team. You can also encourage her to stay hydrated, eat small frequent meals, and take breaks to rest when needed. Additionally, helping her with household chores and errands can reduce he...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = caregiver
- [PASS] Chunks > 0


### Item 9: Ambassador

#### [PASS] Q: Should my children get screened for colon cancer since I have it?
*Should recommend family screening, mention age 40 or 10 years before*


**Answer:** Since you have colon cancer, it's a good idea for your children to talk to their doctor about their risk and when to start screening. Generally, people with a first-degree relative (like a parent) with colon cancer should start screening at age 40, or 10 years before the relative's diagnosis, whichever is earlier. They can discuss options like a colonoscopy, FIT test, Cologuard, or CT Colonography with their doctor. 

You might also want to ask about: 
• How your family's medical history might a...

*API: together | Query type: screening_ambassador | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = screening_ambassador
- [PASS] Contains 'screen'
- [PASS] Contains 'colonoscop'
- [PASS] Chunks > 0

#### [PASS] Q: Is colon cancer hereditary? Should my family get tested?
*Should detect as screening_ambassador*


**Answer:** It sounds like you're worried about your family's risk of colon cancer, and that's completely understandable. Many people in your situation wonder about this, and it's great that you're thinking about their health. Colon cancer can be hereditary, and if you have a first-degree relative with the disease, they should start screening at age 40 or 10 years before your diagnosis, whichever is earlier - options include colonoscopy, FIT test, Cologuard, or CT Colonography. 

You might also want to ask ...

*API: together | Query type: screening_ambassador | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = screening_ambassador
- [PASS] Contains 'screen'
- [PASS] Contains 'family'
- [PASS] Chunks > 0


### Item 12: Compassionate Use

#### [PASS] Q: I've exhausted all my treatment options. What else can I try?
*Should mention expanded access, compassionate use, or clinical trials*


**Answer:** It sounds like you're feeling concerned about your treatment options, and I can imagine how overwhelming that must feel. Given your KRAS mutation and MSS status, some treatments like EGFR-targeted therapies won't be effective for you. However, there are other options to consider, such as switching to an alternative chemotherapy backbone or adding new targeted agents. You might be eligible for regimens like FOLFIRI or irinotecan-based treatments, which work by targeting different pathways in your...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'trial'
- [PASS] Chunks > 0

#### [PASS] Q: What is compassionate use and how do I access it?
*Should explain FDA expanded access pathways*


**Answer:** Compassionate use, also known as expanded access, is a way for patients with serious or life-threatening conditions to access investigational drugs that are not yet approved by the FDA, but may help them. To access it, your oncologist would need to identify a drug that might help you, the manufacturer must agree to provide it, and the FDA would review and typically decide within days. You can also reach out to the FDA's Project Facilitate at 1-855-543-3784 or the Reagan-Udall Foundation's Expand...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'FDA'
- [PASS] Contains 'expanded access'
- [PASS] Contains 'investigational'
- [PASS] Chunks > 0


### Item 11: Wellness

#### [PASS] Q: What exercises are safe during chemotherapy?
*Should recommend evidence-based exercise*


**Answer:** It sounds like you're looking for ways to stay active during chemotherapy, and that's a great idea. Gentle exercises like walking, yoga, and swimming are usually safe and can help reduce fatigue and improve overall well-being. You might want to avoid high-impact activities that could put too much strain on your body, especially since you're experiencing some neuropathy. 

You might also want to ask about: 
• How to manage neuropathy symptoms during exercise
• What dietary changes can help with n...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'exercise'
- [PASS] Chunks > 0

#### [PASS] Q: Tell me about yoga for cancer patients
*Should discuss yoga with safety notes*


**Answer:** Yoga can be a great way to manage stress and improve your overall well-being while going through cancer treatment. Gentle, modified yoga programs, such as "Yoga for Cancer," are specifically designed for cancer patients and can help with fatigue, anxiety, and procedure anxiety. You can ask your oncologist about local yoga programs or online resources that cater to cancer patients, and many hospitals and cancer centers also offer yoga classes as part of their supportive care services. 

You might...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'yoga'
- [PASS] Chunks > 0


### Item 7: Trial Jargon

#### [PASS] Q: What does Phase III mean in a clinical trial?
*Should explain Phase III in plain language*


**Answer:** It sounds like you're interested in learning more about clinical trials, specifically what Phase III means. Phase III (a type of clinical trial that compares a new treatment to the current standard treatment) is a stage of research where a new treatment is compared to the standard treatment to see if it's more effective and safe. Clinical trial availability changes frequently, so always verify trial status at ClinicalTrials.gov or with your oncology team before making decisions. 

As someone wit...

*API: together | Query type: clinical_trial | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = clinical_trial
- [PASS] Contains 'Phase III'
- [PASS] Contains 'compar'
- [PASS] Contains 'standard'
- [PASS] Chunks > 0

#### [PASS] Q: I found a randomized trial. Should I be worried about getting a placebo?
*Should explain cancer trials rarely use pure placebo*


**Answer:** It sounds like you're considering a clinical trial and are worried about receiving a placebo - that's a completely understandable concern. In a randomized trial, participants are assigned to different groups, and some might receive a placebo, which is an inactive treatment. However, many clinical trials are designed to compare a new treatment to the current standard of care, not a placebo. Clinical trial availability changes frequently, so always verify trial status at ClinicalTrials.gov or with...

*API: together | Query type: clinical_trial | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = clinical_trial
- [PASS] Contains 'placebo'
- [PASS] Chunks > 0


### KB: Stress

#### [PASS] Q: How does stress affect the immune system in cancer patients?
*Should retrieve chunks from Cancer_Stress_DAndre_2024.pdf*


**Answer:** It sounds like you're feeling overwhelmed and wondering how stress affects your immune system during cancer treatment. Managing stress is important for your overall wellbeing and quality of life, and it can help you feel better, sleep better, and have more energy. When you're stressed, your body releases hormones like cortisol and adrenaline, which can affect your immune function over time. 

You might also want to ask about: 
• How can I manage my fatigue and nausea during chemotherapy to impro...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'stress'
- [PASS] No 'stress causes cancer'
- [PASS] Chunks > 0


### KB: Caregiver

#### [PASS] Q: What resources are available for cancer caregivers?
*Should retrieve from NCI/ACS caregiver docs*


**Answer:** As a caregiver, it's great that you're looking for resources to support yourself and your loved one. There are many organizations that offer help, such as CancerCare, which has a caregiver support group and hotline (800-813-4673), and the Caregiver Action Network, which provides guidance and resources. You can also find online support groups and communities, like COLONTOWN, where you can connect with others who are going through similar experiences.

You might also want to ask about: 
• How to m...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0


### KB: Screening Barriers

#### [PASS] Q: Why don't people get screened for colon cancer?
*Should retrieve from CRC_Screening_Barriers.pdf*


**Answer:** It sounds like you're interested in understanding why people might not get screened for colon cancer, and I can imagine how concerning that must be for you. Many people don't get screened because they're afraid of the procedure, don't know about all the screening options, or worry about the cost. Additionally, some people might think they don't need to get screened if they're not showing symptoms, or they might believe that colon cancer only affects older adults. 

You might also want to ask abo...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### KB: Sleep

#### [PASS] Q: How does cancer treatment affect sleep?
*Should retrieve from Cancer_Sleep_Disorders.pdf*


**Answer:** It sounds like you're concerned about how cancer treatment is affecting your sleep, and I can imagine how frustrating that must be for you. Many people with cancer experience sleep problems due to anxiety, pain, medications, and treatment schedules. To improve your sleep, you can try practicing good sleep hygiene, such as maintaining a consistent sleep schedule, creating a relaxing bedtime routine, and avoiding caffeine and electronics before bedtime. Sometimes, medications or cognitive behavior...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'sleep'
- [PASS] Chunks > 0


### Regression: Screening

#### [PASS] Q: What age should I start colon cancer screening?

**Answer:** It sounds like you're thinking about colon cancer screening, and I can understand why that's on your mind given your current diagnosis and treatment. For people with an average risk of colon cancer, screening usually starts at age 45, but since you've already been diagnosed with colon cancer, your doctor will likely recommend a different schedule for follow-up screenings. You might want to discuss with your medical team how your current treatment and diagnosis will affect your future screening s...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains '45'
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### Regression: Treatment

#### [PASS] Q: What is FOLFOX and how does it work?

**Answer:** FOLFOX is a type of chemotherapy that combines three drugs: 5-FU, Leucovorin, and Oxaliplatin. It works by targeting and killing cancer cells, and is often used to treat colon cancer. In your case, FOLFOX is being used in combination with Bevacizumab, which is a targeted therapy that helps stop the growth of new blood vessels that feed the cancer. 

You might also want to ask about: 
• How Bevacizumab interacts with your hypertension and what precautions you should take
• What strategies can hel...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'oxaliplatin'
- [PASS] Chunks > 0

#### [PASS] Q: Why was bevacizumab added to my treatment?

**Answer:** It sounds like you're wondering why bevacizumab was added to your treatment plan, and I can imagine how important it is to understand your care. Bevacizumab is not typically recommended for standard adjuvant treatment in stage II/III colon cancer, but it may have been added to your treatment due to specific factors in your case, such as your KRAS mutation or other individual considerations. You might want to discuss this with your oncologist to understand their reasoning. 

You might also want t...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'bevacizumab'
- [PASS] Chunks > 0


### Regression: Side Effects

#### [PASS] Q: The tingling in my fingers is getting worse. Is this normal?

**Answer:** The worsening tingling in your fingers can be a sign of oxaliplatin-related neuropathy, which is a common side effect of your treatment. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don't hesitate to report changes. In the meantime, you can try to manage your symptoms by avoiding extreme cold, wearing gloves when handling cold items, and using warm compresses on your hands. 

You might ...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [PASS] Contains 'neuropathy'
- [PASS] Chunks > 0

#### [PASS] Q: How can I manage the fatigue from chemotherapy?

**Answer:** It sounds like the fatigue from chemotherapy has been really draining for you, and I can imagine how frustrating that feels. Many people facing cancer treatment feel this way, and it's completely normal. To manage your fatigue, you can try getting plenty of rest, eating small, frequent meals, and staying hydrated - it might also be helpful to talk to your care team about adjusting your treatment schedule or exploring medications that can help with fatigue. 

You might also want to ask about: 
• ...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [PASS] Contains 'fatigue'
- [PASS] Chunks > 0


### Regression: Emergency

#### [FAIL] Q: I have a fever of 101F and chills. What should I do?

**Answer:** 🚨 EMERGENCY: Fever during chemotherapy is a medical emergency due to risk of neutropenic sepsis. Contact your oncologist immediately or go to the ER. Do not wait. If going to the ER, tell triage immediately that you're on chemotherapy, bring your medication list or a photo of your pill bottles, have your oncologist's after-hours number saved, and bring your insurance card and ID. In the meantime, try to stay hydrated by drinking plenty of fluids, and avoid taking any medications that may mask yo...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [FAIL] Contains 'call'
- [PASS] Contains 'immediately'
- [PASS] Chunks > 0


### Regression: Emotional

#### [PASS] Q: I'm feeling anxious about my diagnosis. Is this normal?

**Answer:** It sounds like the anxiety you're feeling about your diagnosis is really weighing on you, and I can imagine how overwhelming that must feel. Anxiety, fear, and sadness are completely normal reactions to a cancer diagnosis, and many people in your situation wonder about this. You might find it helpful to talk to an oncology social worker, who can provide emotional support and connect you with resources like the Cancer Support Helpline or meditation programs through apps like Calm and Headspace.

...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0


### Regression: General

#### [PASS] Q: What is stage IIIB colon cancer?

**Answer:** It sounds like you're looking for a clear understanding of your stage IIIB colon cancer diagnosis, and I'm here to help you with that. Stage IIIB means that the cancer has grown through the wall of your colon and has spread to nearby lymph nodes, but not to distant parts of your body. This stage has a range of possible outcomes, with five-year survival rates generally falling between 50-70%, depending on factors like the tumor's grade, your overall health, and how well you respond to treatment.
...

*API: together | Query type: prognosis | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'stage'
- [PASS] Contains 'lymph'
- [PASS] Chunks > 0



---
## 3. Profile B Tests (Stage IV)

**Patient:** Maria Santos — Stage IV, Regorafenib
**Comorbidities:** Heart disease, Kidney disease
**Passed:** 5/6


### Item 13: Stage IV

#### [PASS] Q: What is my prognosis with stage IV colon cancer?
*Should trigger STAGE_IV_PALLIATIVE_CONTEXT*


**Answer:** It sounds like you're facing a really tough situation with your stage IV colon cancer diagnosis, and I can imagine how overwhelming it must feel to think about your prognosis. Many people in your situation wonder about this, and it's completely understandable to have questions about what the future might hold. Your care team can help you understand the different scenarios, including the best-case, expected, and if-disease-progresses outcomes, which depend on various factors such as your tumor's ...

*API: together | Query type: prognosis | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = prognosis
- [PASS] Contains 'treatment'
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0

#### [FAIL] Q: Should I consider hospice?
*Should distinguish palliative from hospice*


**Answer:** It sounds like you're thinking about what's next and wanting to make sure you have all the support you need. Hospice is not about giving up hope, but rather about changing what you hope for - focusing on comfort, quality of life, and being with loved ones when treatment is no longer curative. Your care team can help you with this, and it's completely okay to ask about it. 

You might also want to ask about: 
• What are some other treatment options I could consider if my current treatment stops w...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'palliative'
- [PASS] Contains 'hospice'
- [FAIL] No 'giving up'
- [PASS] Chunks > 0

#### [PASS] Q: Is there any hope for stage 4 colon cancer?
*Balanced, honest, empowering — not toxic positivity*


**Answer:** It's completely understandable to feel concerned about your stage 4 colon cancer diagnosis, and it's great that you're looking for information and hope. While stage 4 colon cancer is serious, many people live well for years with this diagnosis, and treatment options continue to expand. Your oncologist can discuss different scenarios with you, including the best-case, expected, and if-disease-progresses outcomes, and also explore options like immunotherapy, which may be effective given your MSI-H...

*API: together | Query type: prognosis | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = prognosis
- [PASS] Contains 'treatment'
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0

#### [PASS] Q: How do I talk to my family about my prognosis?
*Emotional + Stage IV context*


**Answer:** It sounds like discussing your prognosis with your family is weighing heavily on your mind, and I can imagine how difficult this conversation must be for you. Talking to your family about your prognosis can be a challenging but important conversation to have, and it's great that you're thinking about how to approach it. You might consider speaking with a genetic counselor or an oncology social worker who can help you develop a plan for discussing your prognosis with your loved ones. They can als...

*API: together | Query type: screening_ambassador | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] No 'everything happens for a reason'
- [PASS] No 'stay positive'
- [PASS] No 'you'll be fine'
- [PASS] No 'just think positive'
- [PASS] No 'other people have it worse'
- [PASS] No 'silver lining'
- [PASS] No 'fighting spirit'
- [PASS] No 'battle this'
- [PASS] No 'you'll beat this'
- [PASS] Chunks > 0


### Item 1: Comorbidity B

#### [PASS] Q: What should I watch for with regorafenib and my heart condition?
*Should mention heart disease interactions*


**Answer:** It sounds like you're concerned about how your heart condition might be affected by regorafenib, and that's a very valid concern. With your heart disease, it's essential to monitor your cardiac health closely while on regorafenib, as some chemotherapy drugs can increase the risk of cardiotoxicity. You should report any symptoms like chest pain, palpitations, or shortness of breath to your oncologist immediately. Given your BRAF V600E mutation and MSI-H status, you may also want to discuss with y...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'heart'
- [PASS] Chunks > 0

#### [PASS] Q: How does kidney disease affect my cancer treatment?
*Should mention renal dose adjustments*


**Answer:** It sounds like you're concerned about how your kidney disease might impact your cancer treatment, and that's a very valid concern. Your kidney disease can affect the dosing of certain chemotherapy drugs, such as oxaliplatin, which may need to be adjusted to prevent further kidney damage. Additionally, your oncologist will closely monitor your kidney function through regular lab tests to ensure that any potential kidney problems are caught early. 

You might also want to ask about: 
• How your cu...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'kidney'
- [PASS] Chunks > 0



---
## 4. Summary by Category

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Item 2: Treatment Line | 8 | 8 | 0 |
| Item 1: Comorbidity Unit | 2 | 2 | 0 |
| Item 6: Tone Sensitivity | 7 | 7 | 0 |
| Query Classification | 6 | 6 | 0 |
| Item 6: Empathy Tone | 4 | 4 | 0 |
| Item 1: Comorbidity | 3 | 2 | 1 |
| Item 8: Stress-Immune | 2 | 2 | 0 |
| Item 10: Caregiver | 2 | 1 | 1 |
| Item 9: Ambassador | 2 | 2 | 0 |
| Item 12: Compassionate Use | 2 | 2 | 0 |
| Item 11: Wellness | 2 | 2 | 0 |
| Item 7: Trial Jargon | 2 | 2 | 0 |
| KB: Stress | 1 | 1 | 0 |
| KB: Caregiver | 1 | 1 | 0 |
| KB: Screening Barriers | 1 | 1 | 0 |
| KB: Sleep | 1 | 1 | 0 |
| Regression: Screening | 1 | 1 | 0 |
| Regression: Treatment | 2 | 2 | 0 |
| Regression: Side Effects | 2 | 2 | 0 |
| Regression: Emergency | 1 | 0 | 1 |
| Regression: Emotional | 1 | 1 | 0 |
| Regression: General | 1 | 1 | 0 |
| Item 13: Stage IV | 4 | 3 | 1 |
| Item 1: Comorbidity B | 2 | 2 | 0 |


---
## 5. Failures Detail

- **[LLM]** Item 1: Comorbidity: "What side effects should I watch for with my FOLFOX treatmen..." — Contains 'diabet'
- **[LLM]** Item 10: Caregiver: "I'm caring for my husband who has colon cancer. How can I he..." — Contains 'caregiver'
- **[LLM]** Regression: Emergency: "I have a fever of 101F and chills. What should I do?..." — Contains 'call'
- **[LLM]** Item 13: Stage IV: "Should I consider hospice?..." — No 'giving up'