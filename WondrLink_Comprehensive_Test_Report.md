# WondrLink Comprehensive Test Report

**Generated:** 2026-03-03 11:08:53

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
**Passed:** 29/31


### Item 6: Empathy Tone

#### [PASS] Q: Am I going to die?
*HIGH sensitivity — full ANP framework expected*


**Answer:** It's completely understandable that you're worried about your prognosis, and it's natural to have concerns about the future. Your stage IIIB colon cancer diagnosis and current treatment with FOLFOX and Bevacizumab are important factors in determining your outlook, and it's great that you're thinking about what's ahead. Many people in your situation have gone on to live for many years after treatment, and your care team can help you understand the specifics of your case and what to expect.

You m...

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


**Answer:** It's completely understandable that you're feeling scared and overwhelmed by your diagnosis - it's a lot to take in. Many people in your situation feel the same way, and it's okay to feel sad and cry. You don't have to go through this alone; oncology social workers and support groups can offer you emotional support and help you cope with your feelings. 

You might also want to ask about: 
• How can I manage my fatigue and nausea to improve my quality of life during treatment?
• What are some hea...

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


**Answer:** To manage your diet during chemotherapy, it's recommended that you eat small, frequent meals to help with nausea and appetite. You should also focus on getting enough protein and calories, and consider high-calorie foods if you're losing weight. Additionally, drinking 8-10 glasses of fluid daily and including electrolytes can help prevent dehydration. 

You might also want to ask about: 
• How to manage diarrhea or constipation that may occur during treatment
• What exercises or activities can h...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Chunks > 0

#### [PASS] Q: I feel like giving up. Nothing is working.
*HIGH sensitivity — acknowledge + normalize expected*


**Answer:** It's completely understandable to feel like giving up when dealing with a challenging situation like cancer treatment. Your feelings are valid, and many people in your situation feel overwhelmed and frustrated. You don't have to face this alone - oncology social workers and support groups can offer emotional support and help you cope with these feelings. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy symptoms to improve my quality of life?
• What are my options ...

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


**Answer:** With FOLFOX treatment, you should watch for side effects like fatigue, nausea, diarrhea, and peripheral neuropathy, which can cause numbness or tingling in your hands and feet. To manage these side effects, make sure to stay hydrated, eat small meals, and take your medications as prescribed. If you experience severe or worsening symptoms, such as difficulty breathing, chest pain, or severe abdominal pain, contact your care team immediately. For less severe symptoms, like mild nausea or fatigue, ...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [FAIL] Contains 'diabet'
- [PASS] Chunks > 0

#### [PASS] Q: Can my diabetes affect how I tolerate chemotherapy?
*Should mention steroid-glucose interaction*


**Answer:** Your diabetes can affect how you tolerate chemotherapy, as some chemotherapy drugs can raise or lower your blood sugar levels. It's essential to monitor your blood sugar levels closely and adjust your diabetes management plan as needed while undergoing chemotherapy. You should discuss your diabetes management with your oncologist and healthcare team to ensure your safety and the best possible outcomes. 

You might also want to ask about: 
• How to manage potential interactions between your diabe...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'diabetes'
- [PASS] Chunks > 0

#### [PASS] Q: I have hypertension. Is bevacizumab safe for me?
*Should mention bevacizumab-hypertension interaction*


**Answer:** Bevacizumab can be used with caution in patients with hypertension, like you, but it's essential to monitor your blood pressure regularly. Your oncologist will closely watch your blood pressure and may adjust your treatment or add medications to control it. Since you have hypertension, it's crucial to report any changes in your blood pressure to your oncology team. 

You might also want to ask about: 
• How to manage potential interactions between your hypertension medications and cancer treatme...

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


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. While stress itself doesn't directly make cancer worse, it can affect your immune function, sleep, and ability to recover from treatment. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don't hesitate to report changes. In the meantime, you can try relaxation techniques like deep breathing, medita...

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


**Answer:** Mindfulness can be a powerful tool for cancer patients like you, John, to manage stress and improve overall wellbeing. Practicing mindfulness through techniques like meditation and deep breathing can help reduce anxiety and fatigue, and even improve sleep quality. You can explore mindfulness programs specifically designed for cancer patients, such as Mindfulness-Based Stress Reduction (MBSR), or use apps like Calm and Headspace that offer free cancer-specific meditation programs. 

You might als...

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


**Answer:** To help your wife manage her chemo side effects at home, make sure she stays hydrated by drinking plenty of water, and encourage her to rest when she feels tired. You can also help her keep track of her medications and appointments using a planner or a reminder app. Additionally, preparing small, frequent meals can help with nausea and decreased appetite, which are common side effects of chemotherapy.

You might also want to ask about: 
• How to manage her peripheral neuropathy, which is a commo...

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
• How your KRAS mutation and current treatm...

*API: together | Query type: screening_ambassador | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = screening_ambassador
- [PASS] Contains 'screen'
- [PASS] Contains 'colonoscop'
- [PASS] Chunks > 0

#### [PASS] Q: Is colon cancer hereditary? Should my family get tested?
*Should detect as screening_ambassador*


**Answer:** Colon cancer can be hereditary, and having a family history of the disease increases your risk. If you have a first-degree relative (like a parent, sibling, or child) with colon cancer, they should start screening at age 40 or 10 years before the relative's diagnosis, whichever is earlier. They can discuss screening options like colonoscopy, FIT test, Cologuard, or CT Colonography with their doctor. 

You might also want to ask about: 
• How can I manage my fatigue and nausea during treatment to...

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


**Answer:** Given your stage IIIB sigmoid colon adenocarcinoma and current treatment with FOLFOX + Bevacizumab, if your cancer were to progress, your next steps could involve switching to alternative chemotherapy backbones or adding new targeted agents. For instance, since you have a KRAS mutation, EGFR-targeted therapies like cetuximab or panitumumab would not be effective for you. However, other options might include irinotecan-based regimens or considering clinical trials, especially given your MSS statu...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'trial'
- [PASS] Chunks > 0

#### [PASS] Q: What is compassionate use and how do I access it?
*Should explain FDA expanded access pathways*


**Answer:** Compassionate use, also known as expanded access, is a way for patients with serious or life-threatening conditions to access investigational drugs outside of a clinical trial when no comparable alternative exists. To access it, your oncologist must identify a drug that might help you and the manufacturer must agree to provide it, then the FDA will review and typically decide within days. You can also reach out to resources like FDA Project Facilitate or the Reagan-Udall Foundation's ExpandedAcc...

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


**Answer:** During chemotherapy, it's generally safe to do light to moderate exercises, such as walking, yoga, or swimming, as long as you're feeling up to it. These activities can help reduce fatigue and improve overall well-being. However, it's essential to avoid heavy lifting, high-impact exercises, or activities that may cause injury, especially if you have low blood cell counts or are experiencing neuropathy. 

You might also want to ask about: 
• How to manage fatigue and neuropathy symptoms during ex...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'exercise'
- [PASS] Chunks > 0

#### [PASS] Q: Tell me about yoga for cancer patients
*Should discuss yoga with safety notes*


**Answer:** Yoga can be a great way to manage stress and improve your overall well-being while going through cancer treatment. Gentle, modified yoga programs, such as "Yoga for Cancer," are specifically designed for cancer patients and can help with fatigue, anxiety, and procedure anxiety. You can ask your oncologist about local yoga programs or online resources that cater to cancer patients, and many communities offer free or low-cost classes. 

You might also want to ask about: 
• How can I manage my peri...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'yoga'
- [PASS] Chunks > 0


### Item 7: Trial Jargon

#### [PASS] Q: What does Phase III mean in a clinical trial?
*Should explain Phase III in plain language*


**Answer:** In a clinical trial, Phase III (what we're discussing here refers to a specific stage in the research process) means that the treatment is being tested in a large group of patients to see how well it works and how safe it is compared to standard treatments. This phase helps researchers understand the treatment's effectiveness and potential side effects. Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials.gov or with your oncology team before making decisi...

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


**Answer:** When considering a clinical trial, it's natural to worry about receiving a placebo, which is an inactive treatment used for comparison. However, many clinical trials are designed to compare a new treatment to the current standard of care, rather than a placebo. Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials.gov or with your oncology team before making decisions. You might want to discuss with your oncologist whether you're a good candidate for a clin...

*API: together | Query type: clinical_trial | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = clinical_trial
- [PASS] Contains 'placebo'
- [PASS] Chunks > 0


### KB: Stress

#### [PASS] Q: How does stress affect the immune system in cancer patients?
*Should retrieve chunks from Cancer_Stress_DAndre_2024.pdf*


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. When you're stressed, your body releases hormones like cortisol and adrenaline, which can affect your immune function, sleep, and ability to recover from treatment over time. This doesn't mean stress affects your cancer directly, but rather it can impact how you feel and your energy levels. You can manage stress through techniques like mindfulness, exercise, and social support, and resources like the So...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'stress'
- [PASS] No 'stress causes cancer'
- [PASS] Chunks > 0


### KB: Caregiver

#### [PASS] Q: What resources are available for cancer caregivers?
*Should retrieve from NCI/ACS caregiver docs*


**Answer:** As a caregiver, it's great that you're looking for resources to support yourself and your loved one, John. There are many organizations that offer help, such as CancerCare, which has a caregiver support group that you can reach at 800-813-4673, and the Caregiver Action Network, which provides guidance and resources for caregivers. You can also find online communities, like COLONTOWN, where you can connect with others who are going through similar experiences.

You might also want to ask about: 
...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0


### KB: Screening Barriers

#### [PASS] Q: Why don't people get screened for colon cancer?
*Should retrieve from CRC_Screening_Barriers.pdf*


**Answer:** Many people don't get screened for colon cancer because they're afraid of the procedure, don't know about all the screening options, or think it's only for older adults. Some also worry about the cost or are embarrassed about the preparation and procedure. Additionally, lack of awareness, cultural and language barriers, and not having a doctor recommend it can also prevent people from getting screened. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy symptoms to i...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### KB: Sleep

#### [PASS] Q: How does cancer treatment affect sleep?
*Should retrieve from Cancer_Sleep_Disorders.pdf*


**Answer:** Cancer treatment can affect sleep due to anxiety, pain, medications, and treatment schedules. To manage sleep problems, you can try good sleep hygiene practices, such as maintaining a consistent sleep schedule, creating a relaxing bedtime routine, and avoiding caffeine and electronics before bedtime. Additionally, cognitive behavioral therapy for insomnia (CBT-I) and sometimes medications can help. 

You might also want to ask about: 
• How can I manage my fatigue and decreased appetite during t...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'sleep'
- [PASS] Chunks > 0


### Regression: Screening

#### [PASS] Q: What age should I start colon cancer screening?

**Answer:** For average-risk individuals, colon cancer screening should start at age 45. However, since you have a history of colon cancer, your doctor may recommend a different screening schedule. It's essential to follow your doctor's advice on screening and surveillance to ensure any potential issues are caught early. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy symptoms to improve my quality of life?
• What are the potential benefits and risks of continuing bevacizuma...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains '45'
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### Regression: Treatment

#### [PASS] Q: What is FOLFOX and how does it work?

**Answer:** FOLFOX is a type of chemotherapy that combines three drugs: 5-FU, Leucovorin, and Oxaliplatin. It works by interfering with the growth and spread of cancer cells, helping to slow or stop their growth. As you're currently on FOLFOX + Bevacizumab, it's essential to discuss any concerns or side effects with your medical team, considering your KRAS mutation and MSS status, which may impact the effectiveness of certain treatments.

You might also want to ask about: 
• How Bevacizumab interacts with y...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'oxaliplatin'
- [PASS] Chunks > 0

#### [PASS] Q: Why was bevacizumab added to my treatment?

**Answer:** Bevacizumab was added to your treatment, which is not typically recommended for standard adjuvant treatment in stage II/III colon cancer, so it's likely your doctor chose this based on specific factors about your case. Your treatment includes FOLFOX (a combination of 5-FU, Leucovorin, and Oxaliplatin) plus Bevacizumab, which works by stopping tumors from forming new blood vessels. Since you have a KRAS mutation and are MSS (Microsatellite Stable), some treatments like EGFR-targeted therapies and...

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

**Answer:** To manage fatigue from chemotherapy, you can try treating underlying causes such as anemia, poor nutrition, and sleep problems. This can involve eating smaller, more frequent meals, staying hydrated, and getting regular exercise, like short walks. You should also discuss your fatigue with your care team, as they may be able to adjust your treatment or recommend medications to help. If your fatigue worsens or you're unable to eat or drink for 24 hours, contact your oncologist the same day.

You m...

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

**Answer:** It's completely normal to feel anxious about your diagnosis, and many people in your situation experience similar emotions. Anxiety, fear, and sadness are common reactions to a cancer diagnosis, and it's essential to acknowledge and address these feelings. You can reach out to an oncology social worker at your cancer center or call the Cancer Support Helpline at 1-888-793-9355 for emotional support and guidance.

You might also want to ask about: 
• How can I manage my anxiety and stress during ...

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
**Passed:** 5/6


### Item 13: Stage IV

#### [PASS] Q: What is my prognosis with stage IV colon cancer?
*Should trigger STAGE_IV_PALLIATIVE_CONTEXT*


**Answer:** Your prognosis with stage IV colon cancer is serious, but it's great that you're asking about it - that takes a lot of courage. Many people in your situation wonder about this, and it's completely understandable to have questions. With stage IV colon cancer, the five-year survival rate is around 10-15%, but this can vary depending on factors like your tumor's genetic markers, overall health, and how well you respond to treatment - for example, your MSI-H status may make you a good candidate for ...

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


**Answer:** Hospice care is not just for people who are giving up hope, but rather for those who need extra support with symptom management and quality of life. Since you're currently on Regorafenib and experiencing some side effects, it's essential to discuss your goals and priorities with your oncologist before considering hospice. They can help you understand if hospice care is right for you and ensure that your wishes are respected. 

You might also want to ask about: 
• How can I manage my persistent f...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'palliative'
- [PASS] Contains 'hospice'
- [FAIL] No 'giving up'
- [PASS] Chunks > 0

#### [PASS] Q: Is there any hope for stage 4 colon cancer?
*Balanced, honest, empowering — not toxic positivity*


**Answer:** It's completely understandable to have questions about the prognosis for stage 4 colon cancer, and I want to acknowledge that this is a difficult and emotional topic. Many people in your situation wonder about their chances of a good outcome, and it's a sign of strength, not giving up, to ask about prognosis. Your oncologist can discuss different scenarios with you, including the best-case, expected, and if-disease-progresses outcomes, and it's also important to consider palliative care, which f...

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


**Answer:** Talking to your family about your prognosis can be really tough, but it's a great way to make sure everyone is on the same page and that you're all supported. Many people in your situation find it helpful to have a family meeting, where you can all discuss what's going on and how you're feeling - oncology social workers can even help facilitate these conversations. Your care team can also provide guidance on how to have these conversations, and resources like CancerCare counselors can offer addi...

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


**Answer:** With regorafenib and your heart condition, it's essential to watch for signs of cardiotoxicity, such as chest pain, palpitations, or shortness of breath, and report them to your oncologist immediately. Your heart disease history also means that certain chemotherapy drugs like 5-fluorouracil (5-FU) and capecitabine may need to be used cautiously or avoided. Given your BRAF V600E mutation and MSI-H status, you may be eligible for targeted therapy combinations like encorafenib + cetuximab or immuno...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'heart'
- [PASS] Chunks > 0

#### [PASS] Q: How does kidney disease affect my cancer treatment?
*Should mention renal dose adjustments*


**Answer:** Having kidney disease means that your body has trouble filtering waste and excess fluids, which can affect how your body processes certain cancer treatments. Your oncologist will closely monitor your kidney function and adjust the doses of your medications, such as Regorafenib, to ensure they don't harm your kidneys. It's also important to note that some chemotherapy drugs, like oxaliplatin, can be harmful to the kidneys, so your doctor may choose alternative treatments or adjust the doses accor...

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
- **[LLM]** Regression: Emergency: "I have a fever of 101F and chills. What should I do?..." — Contains 'call'
- **[LLM]** Item 13: Stage IV: "Should I consider hospice?..." — No 'giving up'