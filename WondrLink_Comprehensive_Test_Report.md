# WondrLink Comprehensive Test Report

**Generated:** 2026-04-02 16:13:45

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


**Answer:** It's completely understandable that you're worried about your prognosis, and it's natural to have concerns about the future. As a stage IIIB colon cancer patient, your treatment plan, including FOLFOX and Bevacizumab, is aimed at reducing the risk of cancer recurrence. Many people with stage III colon cancer are able to live for several years after treatment, and some may even be cured, but it's essential to discuss your individual prognosis and any concerns with your care team.

You might also ...

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


**Answer:** It's completely understandable that you're feeling scared and overwhelmed by your diagnosis - it's a lot to take in. Many people in your situation feel the same way, and it's okay to feel sad and cry. You don't have to go through this alone; oncology social workers and support groups can offer you emotional support and guidance, and you can also call the Cancer Support Helpline at 1-888-793-9355 for free and confidential help.

You might also want to ask about: 
• How can I manage my peripheral ...

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


**Answer:** To manage your diet during chemotherapy, it's recommended to eat small, frequent meals to help with nausea and appetite. You should also focus on getting enough protein and calories, and consider high-calorie foods if you're losing weight. Additionally, opting for bland foods when feeling nauseous and soft foods if you have mouth sores can be helpful. 

You might also want to ask about: 
• How to manage diarrhea or constipation that may occur during treatment
• What exercises or activities can h...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Chunks > 0

#### [PASS] Q: I feel like giving up. Nothing is working.
*HIGH sensitivity — acknowledge + normalize expected*


**Answer:** It's completely understandable to feel like giving up when dealing with a challenging situation like cancer treatment. Your feelings are valid, and many people in your situation have felt the same way. You don't have to go through this alone - oncology social workers and support groups can offer emotional support and help you cope with your feelings. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy and other side effects to improve my quality of life?
• What are m...

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


**Answer:** With FOLFOX treatment, you should watch for side effects like fatigue, nausea, diarrhea, and peripheral neuropathy, which can cause numbness or tingling in your fingers and toes. To manage these side effects, make sure to stay hydrated, eat small meals, and take your medications as prescribed. If you experience severe or worsening symptoms, such as difficulty breathing, chest pain, or severe abdominal pain, contact your care team immediately. For less severe symptoms, like mild nausea or fatigue...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [FAIL] Contains 'diabet'
- [PASS] Chunks > 0

#### [PASS] Q: Can my diabetes affect how I tolerate chemotherapy?
*Should mention steroid-glucose interaction*


**Answer:** Your diabetes can affect how you tolerate chemotherapy, as some chemotherapy drugs can raise blood sugar levels. It's essential to monitor your blood sugar levels closely and adjust your diabetes management plan as needed. Your oncologist and diabetes care team should work together to ensure your diabetes is well-managed during chemotherapy. 

You might also want to ask about: 
• How to manage potential interactions between your diabetes medications and chemotherapy
• What steps you can take to ...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'diabetes'
- [PASS] Chunks > 0

#### [PASS] Q: I have hypertension. Is bevacizumab safe for me?
*Should mention bevacizumab-hypertension interaction*


**Answer:** Bevacizumab can be used with caution in patients with hypertension, but it's essential to monitor your blood pressure regularly. You should report any readings above your established threshold to your oncology team, as bevacizumab can worsen high blood pressure. Given your KRAS mutation and MSS status, bevacizumab is being used in combination with FOLFOX, which is not the standard adjuvant treatment for stage II/III colon cancer, so it's crucial to discuss this with your oncologist.

You might a...

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


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. It's understandable to worry about how stress might affect your cancer, but research shows that the relationship between stress and cancer progression is complex and not fully understood. ⚠️ URGENT: Worsening symptoms should be reported to your oncology team promptly - typically within 24-48 hours. Dose modifications are common and expected; don't hesitate to report changes. In the meantime, consider pr...

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


**Answer:** Mindfulness can be a powerful tool for cancer patients, helping to reduce stress and anxiety, improve sleep, and increase energy levels. Mindfulness-Based Stress Reduction (MBSR) is a specific program that has been studied and shown to be beneficial for people with cancer, and it can be found in many cancer centers or online. You can also try using apps like Calm or Headspace, which offer free cancer-specific meditation programs. 

You might also want to ask about: 
• How can I manage my fatigue...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'MBSR'
- [PASS] Contains 'mindfulness'
- [PASS] Chunks > 0


### Item 10: Caregiver

#### [PASS] Q: I'm caring for my husband who has colon cancer. How can I help him?
*Should classify as caregiver and provide caregiver-specific guidance*


**Answer:** As a caregiver, you play a vital role in supporting your husband's journey with colon cancer. You can help him by tracking his chemotherapy cycles, managing side effects at home, and encouraging him to stay hydrated and eat nutritious food. It's also essential to take care of yourself, as caregiving can be emotionally and physically demanding - consider reaching out to respite care resources or peer caregiver support groups for help. 

You might also want to ask about: 
• How to manage his perip...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = caregiver
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0

#### [PASS] Q: How do I help my wife manage her chemo side effects at home?
*Should classify as caregiver*


**Answer:** To help your wife manage her chemo side effects at home, make sure she stays hydrated by drinking plenty of water, and encourage her to rest when she feels tired. You can also help her keep track of her medications and appointments using a planner or a reminder app. Additionally, consider reaching out to a dietitian for guidance on managing her decreased appetite and nausea.

You might also want to ask about: 
• How to manage her peripheral neuropathy symptoms, such as tingling in her fingers, t...

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


**Answer:** Colon cancer can be hereditary, meaning it can run in families, but this is not always the case. If you have a first-degree relative (like a parent, sibling, or child) with colon cancer, it's a good idea for them to start screening earlier, usually at age 40 or 10 years before the relative's diagnosis. You can encourage your family members to talk to their doctor about their risk and screening options, such as a colonoscopy, FIT test, or Cologuard. 

You might also want to ask about: 
• How can ...

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


**Answer:** Given your stage IIIB sigmoid colon adenocarcinoma and current treatment with FOLFOX + Bevacizumab, if your cancer were to progress, your options might include switching to a different chemotherapy backbone, adding new targeted agents, or considering clinical trials. For example, if you had a KRAS mutation like you do, EGFR-targeted therapies wouldn't be effective, but other treatments could be. You might be eligible for treatments like irinotecan-based regimens or other targeted therapies, depe...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'trial'
- [PASS] Chunks > 0

#### [PASS] Q: What is compassionate use and how do I access it?
*Should explain FDA expanded access pathways*


**Answer:** Compassionate use, also known as expanded access, allows patients with serious conditions to access investigational drugs outside of clinical trials when no other options are available. To access it, your oncologist must identify a potentially helpful drug, the manufacturer must agree to provide it, and the FDA must review and approve the request. You can start by discussing this option with your oncologist and exploring resources like the FDA's Project Facilitate or the Reagan-Udall Foundation'...

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


**Answer:** During chemotherapy, it's generally safe to do light to moderate exercises, such as walking, yoga, or swimming, as long as you're feeling up to it. These exercises can help reduce cancer-related fatigue and improve your overall well-being. However, it's essential to avoid high-impact activities that may put too much strain on your body, especially if you're experiencing side effects like neuropathy or fatigue. 

You might also want to ask about: 
• How to manage neuropathy symptoms, such as ting...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'exercise'
- [PASS] Chunks > 0

#### [PASS] Q: Tell me about yoga for cancer patients
*Should discuss yoga with safety notes*


**Answer:** Yoga can be a great way to manage stress and improve your overall well-being during cancer treatment. Gentle, modified yoga programs, such as "Yoga for Cancer," are specifically designed for cancer patients and can help with fatigue, anxiety, and procedure anxiety. You can ask your oncologist about local yoga programs or online resources that cater to cancer patients, and many communities offer free or low-cost classes. 

You might also want to ask about: 
• How to manage peripheral neuropathy s...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'yoga'
- [PASS] Chunks > 0


### Item 7: Trial Jargon

#### [PASS] Q: What does Phase III mean in a clinical trial?
*Should explain Phase III in plain language*


**Answer:** In a clinical trial, "Phase III" refers to a stage where a new treatment is compared to the current standard treatment to see if it's more effective and safe (this phase means the treatment has already shown promise in earlier phases and is now being tested on a larger group of people). Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials.gov or with your oncology team before making decisions. As someone with colon cancer and a KRAS mutation, you might be ...

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


**Answer:** When considering a clinical trial, it's natural to worry about receiving a placebo. In a randomized trial, participants are assigned to either the experimental treatment group or the control group, which may receive a placebo or the standard treatment. However, clinical trials are designed to compare the safety and effectiveness of new treatments, and placebos are used to ensure the results are accurate. Clinical trial availability changes frequently. Always verify trial status at ClinicalTrials...

*API: together | Query type: clinical_trial | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = clinical_trial
- [PASS] Contains 'placebo'
- [PASS] Chunks > 0


### KB: Stress

#### [PASS] Q: How does stress affect the immune system in cancer patients?
*Should retrieve chunks from Cancer_Stress_DAndre_2024.pdf*


**Answer:** Managing stress is important for your overall wellbeing and quality of life during treatment. When you're stressed, your body releases hormones like cortisol and adrenaline, which can affect your immune function, sleep, and ability to recover from treatment over time. This doesn't mean stress affects your cancer directly, but rather it can make it harder for your body to feel its best while you're going through treatment. You can manage stress through techniques like mindfulness, exercise, and s...

*API: together | Query type: emotional | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'stress'
- [PASS] No 'stress causes cancer'
- [PASS] Chunks > 0


### KB: Caregiver

#### [PASS] Q: What resources are available for cancer caregivers?
*Should retrieve from NCI/ACS caregiver docs*


**Answer:** As a caregiver, it's great that you're looking for resources to support yourself and your loved one. There are many organizations that offer help, such as CancerCare, which has a caregiver support group and hotline (800-813-4673), and the Caregiver Action Network, which provides online resources and community support. You can also reach out to oncology social workers, who can offer emotional support and connect you with local resources.

You might also want to ask about: 
• How to manage your lo...

*API: together | Query type: caregiver | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'caregiver'
- [PASS] Chunks > 0


### KB: Screening Barriers

#### [PASS] Q: Why don't people get screened for colon cancer?
*Should retrieve from CRC_Screening_Barriers.pdf*


**Answer:** Many people don't get screened for colon cancer because they're afraid of the procedure, don't know about all the screening options, or worry about the cost. Some people also think they only need to get screened if they have symptoms, but the truth is that colon cancer often doesn't cause symptoms in its early stages. Regular screening can help detect cancer before symptoms develop, and there are several options available, including colonoscopy, FIT tests, and Cologuard. 

You might also want to...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### KB: Sleep

#### [PASS] Q: How does cancer treatment affect sleep?
*Should retrieve from Cancer_Sleep_Disorders.pdf*


**Answer:** Cancer treatment can affect sleep in several ways, including anxiety, pain, medications, and treatment schedules. To manage sleep problems, good sleep hygiene practices, such as maintaining a consistent sleep schedule and creating a relaxing bedtime routine, can be helpful. Sometimes, medications or cognitive behavioral therapy for insomnia (CBT-I) may also be recommended to address underlying causes like pain or anxiety.

You might also want to ask about: 
• How can I manage my fatigue and decr...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'sleep'
- [PASS] Chunks > 0


### Regression: Screening

#### [PASS] Q: What age should I start colon cancer screening?

**Answer:** For average-risk individuals, colon cancer screening should start at age 45. However, since you have a history of colon cancer, your doctor may recommend a different screening schedule. It's essential to discuss your individual screening plan with your medical team, considering your diagnosis and treatment history. 

You might also want to ask about: 
• How can I manage my peripheral neuropathy symptoms to improve my quality of life?
• What are the possible side effects of bevacizumab, and how c...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains '45'
- [PASS] Contains 'screen'
- [PASS] Chunks > 0


### Regression: Treatment

#### [PASS] Q: What is FOLFOX and how does it work?

**Answer:** FOLFOX is a type of chemotherapy that combines three drugs: 5-FU, Leucovorin, and Oxaliplatin. It works by targeting and killing cancer cells, and is commonly used to treat colon cancer. As you're currently on FOLFOX + Bevacizumab, it's essential to note that the Oxaliplatin in FOLFOX can cause peripheral neuropathy, a side effect you're already experiencing. Given your KRAS mutation, EGFR-targeted therapies like cetuximab and panitumumab are not effective for your cancer.

You might also want t...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = treatment
- [PASS] Contains 'oxaliplatin'
- [PASS] Chunks > 0

#### [PASS] Q: Why was bevacizumab added to my treatment?

**Answer:** Bevacizumab was added to your treatment, which is not typically recommended for standard adjuvant treatment in stage II/III colon cancer. This might be because you're part of a clinical trial or your doctor decided it was best for your specific situation. As someone with a KRAS mutation and MSS (Microsatellite Stable) status, you might not benefit from certain targeted therapies like EGFR inhibitors, but other treatments could be effective. 

You might also want to ask about: 
• How will my bloo...

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

**Answer:** To manage fatigue from chemotherapy, you can try treating the underlying causes, such as anemia, poor nutrition, or sleep problems. This might involve taking iron supplements, eating small frequent meals, or practicing relaxation techniques like deep breathing or meditation to improve sleep. You can also discuss with your medical team about adjusting your treatment schedule or dose to help alleviate fatigue. If your fatigue worsens or you experience difficulty breathing, chest pain, or severe ab...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Query type = side_effect
- [PASS] Contains 'fatigue'
- [PASS] Chunks > 0


### Regression: Emergency

#### [FAIL] Q: I have a fever of 101F and chills. What should I do?

**Answer:** 🚨 EMERGENCY: Fever during chemotherapy is a medical emergency due to risk of neutropenic sepsis. Contact your oncologist immediately or go to the ER. Do not wait. If going to the ER, tell triage immediately that you're on chemotherapy, bring your medication list or a photo of your pill bottles, have your oncologist's after-hours number saved, and bring your insurance card and ID. While waiting for medical attention, try to stay hydrated by drinking plenty of fluids, but avoid taking any medicati...

*API: together | Query type: side_effect | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [FAIL] Contains 'call'
- [PASS] Contains 'immediately'
- [PASS] Chunks > 0


### Regression: Emotional

#### [PASS] Q: I'm feeling anxious about my diagnosis. Is this normal?

**Answer:** It's completely normal to feel anxious about your diagnosis, and many people in your situation experience similar emotions. Anxiety, fear, and sadness are common reactions to a cancer diagnosis, and it's essential to acknowledge these feelings. You can talk to an oncology social worker or call the Cancer Support Helpline at 1-888-793-9355 for emotional support, and you can also try using apps like Calm and Headspace that offer free cancer-specific meditation programs.

You might also want to ask...

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

**Answer:** Stage IIIB colon cancer means that the cancer has grown through the wall of your colon and has spread to nearby lymph nodes, but not to distant parts of your body. This stage has a relatively good prognosis, with a 5-year survival rate ranging from 50-70%, depending on various factors such as the tumor's grade, location, and your overall health. Your treatment with FOLFOX and Bevacizumab is aimed at reducing the risk of the cancer coming back. 

You might also want to ask about: 
• How will my K...

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


**Answer:** Your prognosis with stage IV colon cancer is complex, and it's understandable to have questions about what to expect. Generally, the 5-year survival rate for stage IV colon cancer is around 10-15%, but this can vary depending on several factors, including your tumor's genetic markers, such as your MSI-H status, which may respond well to immunotherapy, and your overall health, including your heart and kidney disease. It's also important to consider that treatment options continue to expand, and m...

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


**Answer:** It's completely understandable that you're thinking about hospice, given your stage IV colon cancer diagnosis. However, hospice is not just about giving up hope, but about changing what you hope for - focusing on comfort, quality of life, and support when treatment is no longer effective. Your care team can help you determine if hospice is the right choice for you, and it's essential to discuss your goals, values, and priorities with them. 

You might also want to ask about: 
• How can I manage ...

*API: together | Query type: general | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'palliative'
- [PASS] Contains 'hospice'
- [FAIL] No 'giving up'
- [PASS] Chunks > 0

#### [PASS] Q: Is there any hope for stage 4 colon cancer?
*Balanced, honest, empowering — not toxic positivity*


**Answer:** It's completely understandable to wonder about hope with a stage 4 colon cancer diagnosis. While stage 4 cancer is serious, many people live well for years with this diagnosis, and treatment options continue to expand. Your oncologist can discuss different scenarios with you, including the best-case, expected, and if-disease-progresses outcomes, and how your specific situation, including your MSI-H status and BRAF V600E mutation, might impact your prognosis.

You might also want to ask about: 
•...

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


**Answer:** Talking to your family about your prognosis can be really tough, and it's completely normal to feel anxious or unsure about how to start the conversation. Many people in your situation find it helpful to have a family meeting, where everyone can come together and discuss what's going on - oncology social workers can even help facilitate these conversations. You might want to ask your care team about getting support from a social worker or counselor to help with this conversation. 

You might als...

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


**Answer:** Given your heart condition, it's essential to monitor your cardiac health while on regorafenib. You should watch for symptoms like chest pain, shortness of breath, or palpitations, and report them to your oncologist immediately. Your doctor will also regularly check your heart function, possibly with an echocardiogram, to ensure regorafenib isn't affecting your heart. 

You might also want to ask about: 
• How to manage your current side effects, such as hand-foot syndrome and fatigue, to improv...

*API: together | Query type: treatment | Chunks: 5*

**Checks:**
- [PASS] Response exists
- [PASS] Contains 'heart'
- [PASS] Chunks > 0

#### [PASS] Q: How does kidney disease affect my cancer treatment?
*Should mention renal dose adjustments*


**Answer:** Having kidney disease means that your oncologist needs to carefully choose and adjust your cancer treatments to avoid hurting your kidneys. Some chemotherapy drugs, like oxaliplatin, can be harmful to kidneys, so your doctor may need to modify the dose or choose a different treatment. Your kidney function will be regularly checked before each treatment cycle to ensure it's safe to proceed. 

You might also want to ask about: 
• How your current treatment, Regorafenib, might be affecting your kid...

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