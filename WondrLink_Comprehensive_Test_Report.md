# WondrLink Comprehensive Test Report

**Generated:** 2026-04-03 10:38:20

**Total Tests:** 60
**Passed:** 57/60 (95.0%)


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


**Answer:** It's completely understandable that you're worried about your prognosis, and it's natural to have concerns about the future. Many people in your situation wonder about this, and it's okay to feel scared or unsure. Your care team can help you understand your individual prognosis and what to expect, and they'll be able to discuss the specifics of your treatment and how it's progressing.

You might also want to ask about: 
• How will we monitor for potential recurrence of my cancer after I finish t...

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


**Answer:** It's completely understandable that you're feeling scared and overwhelmed by your diagnosis - it's a lot to take in. Many people in your situation feel the same way, and it's okay to acknowledge those feelings. You can reach out to an oncology social worker at your cancer center for emotional support, or call the Cancer Support Helpline at 1-888-793-9355 for confidential guidance. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy symptoms to improve my daily life?
...

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


**Answer:** To manage your diet during chemotherapy, it's recommended to eat small, frequent meals to help with nausea and appetite. You should also focus on getting enough protein and calories, and consider high-calorie foods if you're losing weight. Additionally, choosing bland foods when you're feeling nauseous and soft foods if you have mouth sores can be helpful. 

You might also want to ask about: 
• How to manage diarrhea and constipation during treatment
• What exercises are safe and recommended to ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Chunks > 0

#### [PASS] Q: I feel like giving up. Nothing is working.
*HIGH sensitivity — acknowledge + normalize expected*


**Answer:** It's completely understandable that you're feeling like giving up - cancer treatment can be really tough, both physically and emotionally. Many people in your situation feel overwhelmed and sad, and it's okay to acknowledge those feelings. You don't have to go through this alone; consider talking to an oncology social worker or joining a support group to connect with others who understand what you're going through.

You might also want to ask about: 
• How can I manage my fatigue and nausea to i...

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


**Answer:** With FOLFOX treatment, you should watch for side effects like fatigue, nausea, diarrhea, and peripheral neuropathy, which can cause numbness or tingling in your hands and feet. To manage these side effects, make sure to stay hydrated, eat small meals, and rest when you need to - and don't hesitate to contact your care team if they worsen or become severe. If you experience severe symptoms like chest pain, difficulty breathing, or severe abdominal pain, seek immediate medical attention. 

You mig...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [FAIL] Contains 'diabet'
- [PASS] Chunks > 0

#### [PASS] Q: Can my diabetes affect how I tolerate chemotherapy?
*Should mention steroid-glucose interaction*


**Answer:** Your diabetes can affect how you tolerate chemotherapy, as some chemotherapy drugs can raise or lower your blood sugar levels. It's essential to monitor your blood sugar levels closely and adjust your diabetes management plan as needed while undergoing chemotherapy. You should discuss your diabetes management with your oncologist and healthcare team to ensure your treatment plan is tailored to your needs. 

You might also want to ask about: 
• How to manage potential interactions between your di...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'diabetes'
- [PASS] Chunks > 0

#### [PASS] Q: I have hypertension. Is bevacizumab safe for me?
*Should mention bevacizumab-hypertension interaction*


**Answer:** Bevacizumab can be used with caution in patients with hypertension, like you, but it's essential to monitor your blood pressure regularly. Your oncologist will closely watch your blood pressure and may adjust your treatment or add medications to control it if needed. Since you have a KRAS mutation and are MSS, bevacizumab is still a viable option for you, but it's crucial to discuss the potential benefits and risks with your medical team.

You might also want to ask about: 
• How to manage your ...

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


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. Stress doesn't directly make cancer worse, but it can affect your immune system, sleep, and energy levels. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don't hesitate to report changes. In the meantime, try relaxation techniques like deep breathing, meditation, or short walks to help manage str...

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


**Answer:** Mindfulness can be a powerful tool for cancer patients, helping to reduce stress and anxiety, improve mood, and even manage symptoms like fatigue and nausea. You can try mindfulness practices like meditation, deep breathing, or yoga, which can be adapted to your needs and abilities. The Society for Integrative Oncology and CancerCare offer resources and guidance on mindfulness-based stress reduction, which has been specifically studied and shown to be beneficial for cancer patients. 

You might ...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'MBSR'
- [PASS] Contains 'mindfulness'
- [PASS] Chunks > 0


### Item 10: Caregiver

#### [PASS] Q: I'm caring for my husband who has colon cancer. How can I help him?
*Should classify as caregiver and provide caregiver-specific guidance*


**Answer:** As a caregiver, you play a vital role in supporting your husband through his colon cancer journey. You can help him by tracking his chemotherapy cycles, managing side effects at home, and encouraging him to stay hydrated and eat nutritious food. It's also essential to take care of yourself, as caregiving can be emotionally and physically demanding - consider reaching out to respite care resources or peer caregiver support groups for help. 

You might also want to ask about: 
• How to manage his ...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = caregiver
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0

#### [PASS] Q: How do I help my wife manage her chemo side effects at home?
*Should classify as caregiver*


**Answer:** To help your wife manage her chemo side effects at home, you can start by keeping a symptom journal to track when side effects occur and how severe they are, which can be helpful to share with her medical team. You can also help her stay hydrated by encouraging her to drink plenty of water, and manage her diet by preparing small, frequent meals that are easy to digest. Additionally, encouraging her to take short walks and engage in gentle exercises can help reduce fatigue.

You might also want t...

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
• How to manage your current fatigue and na...

*API: together | Query type: screening_ambassador | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = screening_ambassador
- [PASS] Contains 'screen'
- [PASS] Contains 'colonoscop'
- [PASS] Chunks > 0

#### [PASS] Q: Is colon cancer hereditary? Should my family get tested?
*Should detect as screening_ambassador*


**Answer:** Having a family history of colon cancer can increase the risk for your loved ones. If you have a first-degree relative (like a parent, sibling, or child) with colon cancer, they should start screening at age 40 or 10 years before the relative's diagnosis, whichever is earlier. Screening options include colonoscopy, FIT test, Cologuard, or CT Colonography, and it's essential to discuss these with your care team to determine the best approach for your family. 

You might also want to ask about: 
•...

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


**Answer:** Given your stage IIIB sigmoid colon adenocarcinoma and current treatment with FOLFOX + Bevacizumab, if your cancer were to progress, your next steps could include switching to a different chemotherapy backbone or adding new targeted agents. For example, you might consider regimens like FOLFIRI (which includes irinotecan) or CAPEOX (which includes capecitabine and oxaliplatin), but since you have a KRAS mutation, EGFR-targeted therapies wouldn't be effective for you. Additionally, given your MSS ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'trial'
- [PASS] Chunks > 0

#### [FAIL] Q: What is compassionate use and how do I access it?
*Should explain FDA expanded access pathways*


**Answer:** Compassionate use, also known as expanded access, allows patients with serious conditions to access experimental drugs outside of clinical trials when no other options are available. To access it, your oncologist must identify a potentially helpful drug, the manufacturer must agree to provide it, and the FDA must review and approve the request. You can also reach out to resources like the FDA's Project Facilitate or the Reagan-Udall Foundation's ExpandedAccessNavigator.org for guidance. 

You mi...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'FDA'
- [PASS] Contains 'expanded access'
- [FAIL] Contains 'investigational'
- [PASS] Chunks > 0


### Item 11: Wellness

#### [PASS] Q: What exercises are safe during chemotherapy?
*Should recommend evidence-based exercise*


**Answer:** During chemotherapy, it's generally safe to do light to moderate exercises, such as walking, yoga, or swimming, as long as you're feeling up to it. These activities can help reduce fatigue and improve overall well-being. However, it's essential to avoid high-intensity exercises or those that may put too much strain on your body, especially if you're experiencing side effects like neuropathy or fatigue. 

You might also want to ask about: 
• How to manage neuropathy symptoms, such as tingling or ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'exercise'
- [PASS] Chunks > 0

#### [PASS] Q: Tell me about yoga for cancer patients
*Should discuss yoga with safety notes*


**Answer:** Yoga can be a great way to manage stress and improve your overall well-being while going through cancer treatment. Gentle, modified yoga programs, such as "Yoga for Cancer," are specifically designed for cancer patients and can help with fatigue, anxiety, and procedure anxiety. You can ask your oncologist about local yoga programs or online resources that cater to cancer patients, and many cancer centers also offer yoga classes as part of their supportive care services. 

You might also want to ...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'yoga'
- [PASS] Chunks > 0


### Item 7: Trial Jargon

#### [PASS] Q: What does Phase III mean in a clinical trial?
*Should explain Phase III in plain language*


**Answer:** In a clinical trial, Phase III (what we're discussing here is a Phase III trial, which means the treatment is being tested in a large group of patients to see how well it works and how safe it is) refers to a stage of research where a new treatment is compared to the current standard treatment to see if it's more effective or has fewer side effects. Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials.gov or with your oncology team before making decisions....

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


**Answer:** When considering a clinical trial, it's natural to worry about receiving a placebo, but many trials are designed to compare a new treatment to the current standard of care, not a placebo. In the context of your sigmoid colon adenocarcinoma and MSS (Microsatellite Stable) status, some clinical trials might focus on combination therapies that could be beneficial. Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials.gov or with your oncology team before makin...

*API: together | Query type: clinical_trial | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = clinical_trial
- [PASS] Contains 'placebo'
- [PASS] Chunks > 0


### KB: Stress

#### [PASS] Q: How does stress affect the immune system in cancer patients?
*Should retrieve chunks from Cancer_Stress_DAndre_2024.pdf*


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. When you're stressed, your body releases hormones like cortisol and adrenaline, which can affect your immune function, sleep, and ability to recover from treatment over time. This doesn't mean stress affects your cancer directly, but rather it can impact how you feel and your energy levels. You can manage stress through techniques like mindfulness, exercise, and social support - resources like the Socie...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'stress'
- [PASS] No 'stress causes cancer'
- [PASS] Chunks > 0


### KB: Caregiver

#### [PASS] Q: What resources are available for cancer caregivers?
*Should retrieve from NCI/ACS caregiver docs*


**Answer:** As a caregiver, it's great that you're looking for resources to support yourself and your loved one. There are many organizations that offer help, such as CancerCare, which has a caregiver support group and hotline (800-813-4673), and the Caregiver Action Network, which provides online resources and community support. You can also reach out to oncology social workers, who can provide emotional support and connect you with local resources.

You might also want to ask about: 
• How to manage your ...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0


### KB: Screening Barriers

#### [PASS] Q: Why don't people get screened for colon cancer?
*Should retrieve from CRC_Screening_Barriers.pdf*


**Answer:** Many people don't get screened for colon cancer because they're afraid of the procedure, don't know about non-invasive options, or think it's only necessary if they have symptoms. Additionally, cost concerns, inconvenience, and misconceptions about risk can also be barriers to screening. It's essential to talk to your doctor about screening options, such as colonoscopy, FIT test, or Cologuard, to find one that works for you. 

You might also want to ask about: 
• How can I manage my peripheral n...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### KB: Sleep

#### [PASS] Q: How does cancer treatment affect sleep?
*Should retrieve from Cancer_Sleep_Disorders.pdf*


**Answer:** Cancer treatment can affect sleep in several ways, including through medications, stress, and changes in your daily routine. To manage sleep problems, you can try practicing good sleep hygiene, such as keeping a consistent sleep schedule, avoiding caffeine and electronics before bedtime, and creating a relaxing bedtime routine. Additionally, cognitive behavioral therapy for insomnia (CBT-I) and sometimes medications can help.

You might also want to ask about: 
• How can I manage my fatigue and ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'sleep'
- [PASS] Chunks > 0


### Regression: Screening

#### [PASS] Q: What age should I start colon cancer screening?

**Answer:** For average-risk individuals, colon cancer screening should start at age 45. However, since you have a history of colon cancer, your doctor may recommend a different screening schedule. It's essential to discuss your specific situation with your medical team to determine the best approach for you. 

You might also want to ask about: 
• How will my treatment plan change after I complete the 12 cycles of FOLFOX + Bevacizumab?
• What can I do to manage my grade 2 peripheral neuropathy and prevent i...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains '45'
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### Regression: Treatment

#### [PASS] Q: What is FOLFOX and how does it work?

**Answer:** FOLFOX is a type of chemotherapy that combines three drugs: 5-FU, Leucovorin, and Oxaliplatin. It works by stopping cancer cells from growing and dividing, which helps to slow down the spread of the cancer. As someone with a KRAS mutation and MSS (Microsatellite Stable) status, you're currently receiving FOLFOX with Bevacizumab, which is a targeted therapy that helps stop the growth of new blood vessels that feed the cancer. 

You might also want to ask about: 
• How to manage the side effects o...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'oxaliplatin'
- [PASS] Chunks > 0

#### [PASS] Q: Why was bevacizumab added to my treatment?

**Answer:** Bevacizumab was added to your treatment, which is not a standard approach for stage II/III colon cancer, suggesting that your doctor may have considered specific factors in your case or that you might be part of a clinical trial. Your treatment includes FOLFOX (a combination of 5-FU, Leucovorin, and Oxaliplatin) plus Bevacizumab, which works by stopping tumors from developing their own blood supply. Given your KRAS mutation and MSS status, certain treatments like EGFR-targeted therapies and immu...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'bevacizumab'
- [PASS] Chunks > 0


### Regression: Side Effects

#### [PASS] Q: The tingling in my fingers is getting worse. Is this normal?

**Answer:** The tingling in your fingers is a common side effect of oxaliplatin, a medication you're taking as part of your FOLFOX treatment. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don't hesitate to report changes. In the meantime, you can try to manage your symptoms by avoiding extreme cold, wearing gloves when handling cold items, and using warm compresses on your hands. 

You might also wa...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [PASS] Contains 'neuropathy'
- [PASS] Chunks > 0

#### [PASS] Q: How can I manage the fatigue from chemotherapy?

**Answer:** To manage fatigue from chemotherapy, you can try treating underlying causes such as anemia, poor nutrition, and sleep problems. This can involve eating a healthy diet, staying hydrated, and getting regular exercise, like short walks, to help improve your energy levels. You can also discuss with your medical team about adjusting your treatment or adding medications to help with fatigue, and don't hesitate to reach out to them if your fatigue worsens or you experience difficulty breathing, chest p...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [PASS] Contains 'fatigue'
- [PASS] Chunks > 0


### Regression: Emergency

#### [FAIL] Q: I have a fever of 101F and chills. What should I do?

**Answer:** 🚨 EMERGENCY: Fever during chemotherapy is a medical emergency due to risk of neutropenic sepsis. Contact your oncologist immediately or go to the ER. Do not wait. If going to the ER, tell triage immediately that you're on chemotherapy, bring your medication list or a photo of your pill bottles, have your oncologist's after-hours number saved, and bring your insurance card and ID. While waiting for medical attention, try to stay hydrated by drinking plenty of fluids and rest as much as possible.
...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [FAIL] Contains 'call'
- [PASS] Contains 'immediately'
- [PASS] Chunks > 0


### Regression: Emotional

#### [PASS] Q: I'm feeling anxious about my diagnosis. Is this normal?

**Answer:** It's completely normal to feel anxious about your diagnosis, and many people in your situation experience similar emotions. Anxiety, fear, and sadness are common reactions to a cancer diagnosis, and it's essential to acknowledge and address these feelings. You can reach out to an oncology social worker for support, or call the Cancer Support Helpline at 1-888-793-9355 for free and confidential guidance.

You might also want to ask about: 
• How can I manage my fatigue and nausea during treatment...

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

**Answer:** Stage IIIB colon cancer means that the cancer has grown through the wall of your colon and has spread to nearby lymph nodes, but not to distant parts of your body. This stage has a meaningful cure rate with surgery and adjuvant chemotherapy, like the FOLFOX and Bevacizumab treatment you're currently receiving. Your overall prognosis depends on several factors, including the stage of your cancer, tumor grade, location, and your overall health, with five-year survival rates for stage III colon can...

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
**Passed:** 6/6


### Item 13: Stage IV

#### [PASS] Q: What is my prognosis with stage IV colon cancer?
*Should trigger STAGE_IV_PALLIATIVE_CONTEXT*


**Answer:** Your prognosis with stage IV colon cancer is complex, and it's understandable to have questions about what to expect. Generally, the 5-year survival rate for stage IV colon cancer is around 10-15%, but this can vary depending on several factors, including your tumor's genetic markers, such as your MSI-H status, which may respond well to immunotherapy, and your overall health. It's also important to consider that treatment options continue to expand, and many people live well for years with stage...

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

#### [PASS] Q: Should I consider hospice?
*Should distinguish palliative from hospice*


**Answer:** It's completely understandable that you're thinking about hospice, given your stage IV colon cancer diagnosis. However, hospice is not just about end-of-life care, but also about changing what you hope for - focusing on comfort, quality of life, and support when treatment is no longer effective. Your care team can help you determine if hospice is the right choice for you, and it's essential to discuss your goals, values, and priorities with them. 

You might also want to ask about: 
• What are m...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'palliative'
- [PASS] Contains 'hospice'
- [PASS] No 'giving up'
- [PASS] Chunks > 0

#### [PASS] Q: Is there any hope for stage 4 colon cancer?
*Balanced, honest, empowering — not toxic positivity*


**Answer:** This is genuinely hard to hear, and it's completely understandable that you're wondering about hope for stage 4 colon cancer. Many people in your situation feel the same way, and it's a sign of strength, not giving up, that you're asking about this. Your oncologist can discuss different scenarios with you, including best-case, expected, and if-disease-progresses outcomes, and it's also important to consider palliative care, which focuses on living as well as possible, not giving up on treatment....

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


**Answer:** Talking to your family about your prognosis can be really tough, but it's a great way to make sure everyone is on the same page and that you're all supported. Many people in your situation find it helpful to have a family meeting, where you can all discuss what's going on and how you're feeling. You might consider asking a social worker or counselor to help facilitate this conversation, as they can provide guidance and support. Your care team can also help you with this, so don't hesitate to rea...

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


**Answer:** Given your heart condition and current treatment with regorafenib, it's essential to monitor your heart health closely. You should watch for symptoms like chest pain, shortness of breath, or palpitations, and report them to your oncologist immediately. Your heart condition may also affect the choice of future treatments, such as avoiding certain drugs like bevacizumab that can increase the risk of bleeding or worsening heart disease. 

You might also want to ask about: 
• How to manage your curr...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'heart'
- [PASS] Chunks > 0

#### [PASS] Q: How does kidney disease affect my cancer treatment?
*Should mention renal dose adjustments*


**Answer:** Having kidney disease means that your oncologist needs to carefully choose and dose your cancer treatments to avoid hurting your kidneys. Some chemotherapy drugs, like oxaliplatin, can be harmful to kidneys, so your doctor may need to adjust the dose or choose a different treatment. For example, your current treatment, Regorafenib, may need to be monitored closely due to its potential effects on kidney function. Given your BRAF V600E mutation and MSI-H status, you may be eligible for targeted th...

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
| Item 10: Caregiver | 2 | 2 | 0 |
| Item 9: Ambassador | 2 | 2 | 0 |
| Item 12: Compassionate Use | 2 | 1 | 1 |
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
| Item 13: Stage IV | 4 | 4 | 0 |
| Item 1: Comorbidity B | 2 | 2 | 0 |


---
## 5. Failures Detail

- **[LLM]** Item 1: Comorbidity: "What side effects should I watch for with my FOLFOX treatmen..." — Contains 'diabet'
- **[LLM]** Item 12: Compassionate Use: "What is compassionate use and how do I access it?..." — Contains 'investigational'
- **[LLM]** Regression: Emergency: "I have a fever of 101F and chills. What should I do?..." — Contains 'call'