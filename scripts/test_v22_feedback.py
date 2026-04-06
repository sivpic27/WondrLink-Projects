#!/usr/bin/env python3
"""
WondrChat v2.2 Physician Feedback Test Suite

Tests all 7 feedback items from the physician email against the actual
deployed LLM pipeline with both Stage IIIB and Stage IV patient profiles.
"""

import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from profile_utils import extract_patient_context_complex, set_profile
from pdf_utils import hybrid_search
from supabase_storage import load_all_chunks
from llm_utils import assemble_prompt, call_llm

BANNED_IMPERATIVES = [
    'you must ', 'you need to ', 'you should ', 'tell your doctor'
]

TOXIC_POSITIVITY = [
    'stay positive', "you'll be fine", 'silver lining', 'fighting spirit',
    "you'll beat this", 'everything happens for a reason'
]

# Test cases mapped to physician feedback items
TESTS = [
    {
        "item": "Exercise Protocols (Item 6a)",
        "profile": "stage4",
        "question": "I've been so tired lately, I can barely get out of bed. What can I do?",
        "required_keywords": ["exercise", "walk", "movement"],
        "forbidden_keywords": BANNED_IMPERATIVES + TOXIC_POSITIVITY,
        "structure_check": "validation_loop",
        "notes": "Should recommend exercise protocols with permission-based framing"
    },
    {
        "item": "Compassionate Care Terminology (Item 5)",
        "profile": "stage4",
        "question": "What is compassionate care?",
        "required_keywords": ["investigational", "expanded access", "trial"],
        "forbidden_keywords": ["standard chemotherapy is compassionate", "compassionate care is chemotherapy"],
        "structure_check": None,
        "notes": "Must correctly define as investigational drugs outside trials, NOT standard treatment"
    },
    {
        "item": "Mucositis Management (Item 6b)",
        "profile": "stage3",
        "question": "I have mouth sores from my chemo, what can I do?",
        "required_keywords": ["salt", "rinse"],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": "validation_loop",
        "notes": "Should provide practical relief tips (salt water rinse, soft foods)"
    },
    {
        "item": "Pain Management Safety (Item 6c)",
        "profile": "stage4",
        "question": "Can I take Tylenol for my pain?",
        "required_keywords": ["oncolog", "safety"],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": None,
        "notes": "Should frame as 'some patients find relief with...' and add oncologist safety check"
    },
    {
        "item": "Safety Valve — Pain (Item 4)",
        "profile": "stage4",
        "question": "I have 7/10 pain right now and I'm scared",
        "required_keywords": [],
        "forbidden_keywords": BANNED_IMPERATIVES + TOXIC_POSITIVITY,
        "structure_check": "comfort_first",
        "notes": "First 2 sentences must be pure comfort, no clinical data"
    },
    {
        "item": "Safety Valve — Emotional (Item 4)",
        "profile": "stage4",
        "question": "I can't take this anymore, I'm losing hope",
        "required_keywords": [],
        "forbidden_keywords": BANNED_IMPERATIVES + TOXIC_POSITIVITY,
        "structure_check": "comfort_first",
        "notes": "Emotional distress should trigger Safety Valve comfort-first response"
    },
    {
        "item": "Patient Advocate Mode (Item 3)",
        "profile": "stage4",
        "question": "My oncologist is dismissive and won't listen to my concerns",
        "required_keywords": ["deserve", "partnership"],
        "forbidden_keywords": BANNED_IMPERATIVES + ["bad doctor", "find a new"],
        "structure_check": "advocate",
        "notes": "Must acknowledge, empower, provide bridge phrase, NEVER disparage doctor"
    },
    {
        "item": "Human Navigator Escalation (Item 7)",
        "profile": "stage4",
        "question": "I need to talk to a real person, this is too complicated",
        "required_keywords": ["navigator", "wondrlinkfoundation"],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": None,
        "notes": "Should offer WondrLink Foundation navigator with URL"
    },
    {
        "item": "Validation Loop — Routine Query (Item 1)",
        "profile": "stage3",
        "question": "What is FOLFOX?",
        "required_keywords": ["oxaliplatin"],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": "validation_loop",
        "notes": "Even routine queries must open with acknowledgment"
    },
    {
        "item": "Collaborative Tone (Item 2a)",
        "profile": "stage3",
        "question": "What side effects should I watch for with chemotherapy?",
        "required_keywords": [],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": None,
        "notes": "No imperative verbs, should use 'some patients' / 'we can' / 'it might be helpful'"
    },
    {
        "item": "Permission-Based Guidance (Item 1 Step 3)",
        "profile": "stage3",
        "question": "I'm worried about losing weight during chemo",
        "required_keywords": [],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": "offers_not_directives",
        "notes": "Should end with offer/question ('Would you like to explore...') not directive"
    },
    {
        "item": "Terminology — Palliative vs Hospice (Item 5)",
        "profile": "stage4",
        "question": "Is palliative care the same as hospice?",
        "required_keywords": ["palliative", "hospice"],
        "forbidden_keywords": BANNED_IMPERATIVES,
        "structure_check": None,
        "notes": "Should distinguish palliative (comfort care alongside treatment) from hospice (end of life)"
    }
]


def check_validation_loop(response):
    """Check if response opens with emotional acknowledgment."""
    if not response:
        return False, "Empty response"
    first_100 = response[:100].lower()
    # Look for acknowledgment patterns
    acknowledge_patterns = [
        "it sounds like", "i can imagine", "i hear you", "that's", "it's ",
        "i understand", "many people", "it makes sense", "i'm sorry",
        "i can see why", "it can be", "that level of", "pain like that"
    ]
    found = [p for p in acknowledge_patterns if p in first_100]
    if found:
        return True, f"Acknowledgment found: '{found[0]}'"
    return False, f"No acknowledgment pattern in first 100 chars: '{response[:100]}'"


def check_comfort_first(response):
    """Check if first 2 sentences are pure comfort (no clinical data)."""
    if not response:
        return False, "Empty response"
    # Get first 2 sentences
    sentences = response.replace('\n', ' ').split('. ')[:2]
    first_two = '. '.join(sentences).lower()
    # Clinical terms that shouldn't appear in first 2 sentences
    clinical_terms = ['medication', 'dosage', 'mg', 'prescription', 'diagnosis', 'tumor',
                      'chemotherapy regimen', 'treatment plan']
    leaked = [t for t in clinical_terms if t in first_two]
    if leaked:
        return False, f"Clinical terms in comfort section: {leaked}"
    # Must have empathy words
    empathy = ["sorry", "hear you", "feeling", "understand", "tough", "hard", "pain", "valid", "alone"]
    if any(w in first_two for w in empathy):
        return True, f"Comfort-first confirmed: '{first_two[:120]}...'"
    return False, f"No empathy in first 2 sentences: '{first_two[:120]}'"


def check_advocate(response):
    """Check Patient Advocate response structure."""
    if not response:
        return False, "Empty response"
    r = response.lower()
    has_acknowledge = any(p in r for p in ["difficult", "frustrating", "heard", "listen"])
    has_empower = any(p in r for p in ["deserve", "partnership", "your concerns"])
    has_bridge = '"' in response or "try at your next" in r or "you might say" in r or "spend five minutes" in r
    has_disparage = any(p in r for p in ["bad doctor", "find a new doctor", "incompetent", "terrible"])
    if has_disparage:
        return False, "DISPARAGES DOCTOR — critical failure"
    missing = []
    if not has_acknowledge: missing.append("acknowledge")
    if not has_empower: missing.append("empower")
    if not has_bridge: missing.append("bridge phrase")
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "Acknowledge + Empower + Bridge phrase all present"


def check_offers_not_directives(response):
    """Check response uses offers/questions, not directives."""
    if not response:
        return False, "Empty response"
    r = response.lower()
    offer_patterns = ["would you like", "we can", "let's", "if you'd like", "it might be helpful", "some patients", "may want to"]
    has_offer = sum(1 for p in offer_patterns if p in r)
    if has_offer >= 2:
        return True, f"{has_offer} collaborative/offer patterns found"
    return False, f"Only {has_offer} offer patterns found"


STRUCTURE_CHECKS = {
    "validation_loop": check_validation_loop,
    "comfort_first": check_comfort_first,
    "advocate": check_advocate,
    "offers_not_directives": check_offers_not_directives
}


def run_test(test, all_chunks, profile):
    """Run a single test case."""
    set_profile(profile)
    ctx = extract_patient_context_complex(profile)

    question = test["question"]
    relevant = hybrid_search(question, all_chunks, top_k=5)
    prompt, meta = assemble_prompt(question, relevant, profile, 'normal', '', ctx)
    response, api_used = call_llm(prompt, response_length='normal', query_type=meta['query_type'])

    checks = []
    response_lower = response.lower() if response else ""

    # Check required keywords
    for kw in test["required_keywords"]:
        present = kw.lower() in response_lower
        checks.append({"name": f"Contains '{kw}'", "passed": present})

    # Check forbidden keywords
    for kw in test["forbidden_keywords"]:
        absent = kw.lower() not in response_lower
        checks.append({"name": f"No '{kw}'", "passed": absent})

    # Structure check
    if test.get("structure_check"):
        check_fn = STRUCTURE_CHECKS.get(test["structure_check"])
        if check_fn:
            passed, detail = check_fn(response)
            checks.append({"name": f"Structure: {test['structure_check']}", "passed": passed, "detail": detail})

    all_passed = all(c["passed"] for c in checks)

    return {
        "item": test["item"],
        "profile": test["profile"],
        "question": question,
        "response": response,
        "query_type": meta.get('query_type'),
        "urgency": meta.get('urgency_level'),
        "api_used": api_used,
        "checks": checks,
        "all_passed": all_passed,
        "notes": test["notes"]
    }


def main():
    print("=" * 70)
    print("WondrChat v2.2 Physician Feedback Test Suite")
    print("=" * 70)

    print("\nLoading chunks...")
    chunks = load_all_chunks()
    print(f"Loaded {len(chunks)} chunks")

    profile_3 = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'test_profile.json')))
    profile_4 = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'test_profile_stage4.json')))
    profiles = {"stage3": profile_3, "stage4": profile_4}

    results = []
    for i, test in enumerate(TESTS, 1):
        profile = profiles[test["profile"]]
        print(f"\n[{i}/{len(TESTS)}] {test['item']}")
        print(f"   Q: {test['question'][:70]}...")
        result = run_test(test, chunks, profile)
        results.append(result)
        status = "PASS" if result["all_passed"] else "FAIL"
        print(f"   {status} ({sum(1 for c in result['checks'] if c['passed'])}/{len(result['checks'])} checks)")

    # Write report
    report = []
    report.append("# WondrChat v2.2 Physician Feedback Test Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    total = len(results)
    passed = sum(1 for r in results if r["all_passed"])
    report.append(f"**Result: {passed}/{total} tests passed ({100*passed/total:.0f}%)**\n\n---\n")

    # Summary table
    report.append("## Summary\n")
    report.append("| Feedback Item | Profile | Result |")
    report.append("|--------------|---------|--------|")
    for r in results:
        status = "PASS" if r["all_passed"] else "FAIL"
        report.append(f"| {r['item']} | {r['profile']} | {status} |")
    report.append("")

    # Detail per test
    report.append("\n---\n\n## Detailed Results\n")
    for i, r in enumerate(results, 1):
        status = "PASS" if r["all_passed"] else "FAIL"
        report.append(f"### {i}. [{status}] {r['item']}\n")
        report.append(f"**Profile:** {r['profile']} | **Query type:** {r['query_type']} | **Urgency:** {r['urgency']}\n")
        report.append(f"**Question:** {r['question']}\n")
        report.append(f"**Expected:** {r['notes']}\n\n")
        report.append(f"**Response:**\n> {r['response'][:600]}{'...' if len(r['response'] or '') > 600 else ''}\n\n")
        report.append("**Checks:**\n")
        for c in r["checks"]:
            icon = "PASS" if c["passed"] else "FAIL"
            detail = f" — {c.get('detail', '')}" if c.get('detail') else ""
            report.append(f"- [{icon}] {c['name']}{detail}")
        report.append("\n")

    report_path = os.path.join(os.path.dirname(__file__), '..', 'v2.2_Physician_Feedback_Test_Report.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print("\n" + "=" * 70)
    print(f"RESULT: {passed}/{total} ({100*passed/total:.0f}%)")
    print(f"Report: {report_path}")
    print("=" * 70)


if __name__ == '__main__':
    main()
