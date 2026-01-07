#!/usr/bin/env python3
"""
WondrLink Chatbot Test Script

This script tests the chatbot with a dummy patient profile and 20 questions,
then generates a PDF report with the results.
"""

import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from profile_utils import extract_patient_context_complex, format_patient_summary_complex, set_profile
from pdf_utils import search_chunks
from supabase_storage import load_all_chunks
from llm_utils import (
    get_response_settings, call_llm, classify_query_type,
    assemble_prompt, get_relevant_resources, detect_symptom_urgency
)

# 20 Test Questions organized by category
TEST_QUESTIONS = [
    # Screening (2)
    {"category": "Screening", "question": "What age should I start colon cancer screening?"},
    {"category": "Screening", "question": "What's the difference between a colonoscopy and a FIT test?"},

    # Treatment (4)
    {"category": "Treatment", "question": "What is FOLFOX and how does it work?"},
    {"category": "Treatment", "question": "Why was bevacizumab added to my treatment?"},
    {"category": "Treatment", "question": "How many cycles of chemotherapy will I need?"},
    {"category": "Treatment", "question": "What does it mean that my tumor is KRAS mutated?"},

    # Side Effects (4)
    {"category": "Side Effects", "question": "The tingling in my fingers is getting worse. Is this normal?"},
    {"category": "Side Effects", "question": "How can I manage the fatigue from chemotherapy?"},
    {"category": "Side Effects", "question": "What foods should I eat to help with nausea?"},
    {"category": "Side Effects", "question": "Will the neuropathy go away after treatment ends?"},

    # Survivorship (3)
    {"category": "Survivorship", "question": "What follow-up tests will I need after finishing treatment?"},
    {"category": "Survivorship", "question": "How often should I get a colonoscopy after colon cancer?"},
    {"category": "Survivorship", "question": "What lifestyle changes can help prevent recurrence?"},

    # Emergency/Urgent (3)
    {"category": "Emergency", "question": "I have a fever of 101F and chills. What should I do?"},
    {"category": "Emergency", "question": "I'm having severe abdominal pain. Is this an emergency?"},
    {"category": "Emergency", "question": "When should I go to the ER during chemotherapy?"},

    # General Information (2)
    {"category": "General", "question": "What is stage IIIB colon cancer?"},
    {"category": "General", "question": "What does R0 resection mean from my surgery?"},

    # Emotional Support (2)
    {"category": "Emotional", "question": "I'm feeling anxious about my diagnosis. Is this normal?"},
    {"category": "Emotional", "question": "How do I talk to my family about my cancer?"},
]


def load_test_profile():
    """Load the dummy patient profile."""
    profile_path = os.path.join(os.path.dirname(__file__), '..', 'test_profile.json')
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    set_profile(profile)
    return profile


def build_prompt_legacy(question: str, patient_context: dict, relevant_chunks: list, history: list = None) -> str:
    """Legacy prompt builder - kept for reference."""
    prompt_parts = []

    if patient_context:
        patient_summary = format_patient_summary_complex(patient_context)
        prompt_parts.append(f"PATIENT CONTEXT:\n{patient_summary}")

    if relevant_chunks:
        guidelines = "\n\n".join(relevant_chunks[:5])
        prompt_parts.append(f"RELEVANT GUIDELINES:\n{guidelines}")

    prompt_parts.append(f"PATIENT QUESTION:\n{question}")
    prompt_parts.append("""
INSTRUCTIONS:
- Provide a helpful, empathetic response based on the patient's specific situation
- Use simple, everyday language
- If this relates to their current treatment, reference their specific regimen
- Include appropriate safety disclaimers when discussing treatments
- For emergency symptoms, advise seeking immediate care
""")

    return "\n\n".join(prompt_parts)


def run_single_test(question_data: dict, patient_context: dict, all_chunks: list, profile: dict) -> dict:
    """Run a single test question and return the result using enhanced prompt assembly."""
    question = question_data["question"]
    category = question_data["category"]

    print(f"  Testing: {question[:50]}...")

    try:
        # Search for relevant chunks
        relevant_chunks = search_chunks(question, all_chunks, top_k=5)

        # Use enhanced assemble_prompt (returns tuple: prompt, metadata)
        prompt, metadata = assemble_prompt(
            message=question,
            retrieved=relevant_chunks,
            patient=profile,
            response_length="normal",
            conversation_context="",
            patient_context=patient_context
        )

        # Detect query type for resources
        query_type = metadata.get('query_type', 'general')
        urgency_detected = metadata.get('urgency_detected', False)
        urgency_level = metadata.get('urgency_level')

        # Call LLM
        response, api_used = call_llm(prompt, response_length="normal", query_type=query_type)

        # Append resources based on query type (skip for emergency responses)
        if not urgency_detected or urgency_level != 'emergency':
            resources = get_relevant_resources(query_type, include_resources=True, query=question)
            if resources:
                response += resources

        return {
            "category": category,
            "question": question,
            "answer": response,
            "api_used": api_used,
            "chunks_retrieved": len(relevant_chunks),
            "query_type": query_type,
            "urgency_detected": urgency_detected,
            "urgency_level": urgency_level,
            "success": True,
            "error": None
        }

    except Exception as e:
        return {
            "category": category,
            "question": question,
            "answer": None,
            "api_used": None,
            "chunks_retrieved": 0,
            "query_type": None,
            "urgency_detected": False,
            "urgency_level": None,
            "success": False,
            "error": str(e)
        }


def generate_markdown_report(profile: dict, results: list) -> str:
    """Generate a markdown report from test results."""
    patient_context = extract_patient_context_complex(profile)

    report = []
    report.append("# WondrLink Chatbot Test Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Questions:** {len(results)}")
    successful = sum(1 for r in results if r['success'])
    report.append(f"\n**Successful Responses:** {successful}/{len(results)}")

    # Procedure Section
    report.append("\n\n---\n")
    report.append("## 1. Test Procedure")
    report.append("""
This test evaluates the WondrLink chatbot's ability to provide accurate,
personalized, and empathetic responses to colon cancer patient questions.

**Methodology:**
1. Created a realistic dummy patient profile (Stage IIIB colon cancer patient)
2. Loaded the profile into the system
3. Asked 20 questions across 7 categories:
   - Screening (2 questions)
   - Treatment (4 questions)
   - Side Effects (4 questions)
   - Survivorship (3 questions)
   - Emergency/Urgent (3 questions)
   - General Information (2 questions)
   - Emotional Support (2 questions)
4. Captured and evaluated responses for accuracy and appropriateness
""")

    # Patient Profile Section
    report.append("\n\n---\n")
    report.append("## 2. Dummy Patient Profile")
    report.append("\n### Patient Demographics")
    patient = profile.get('patient', {})
    report.append(f"- **Name:** {patient.get('name', 'N/A')}")
    report.append(f"- **Date of Birth:** {patient.get('dob', 'N/A')}")
    report.append(f"- **Sex:** {patient.get('sex', 'N/A')}")
    report.append(f"- **ECOG Status:** {patient.get('ecog', 'N/A')}")
    report.append(f"- **Allergies:** {patient.get('allergies', 'None')}")
    comorbidities = patient.get('comorbidities', [])
    report.append(f"- **Comorbidities:** {', '.join(comorbidities) if comorbidities else 'None'}")

    report.append("\n### Diagnosis")
    diagnosis = profile.get('primaryDiagnosis', {})
    report.append(f"- **Site:** {diagnosis.get('site', 'N/A')}")
    report.append(f"- **Histology:** {diagnosis.get('histology', 'N/A')}")
    report.append(f"- **Stage:** {diagnosis.get('stage', 'N/A')}")
    report.append(f"- **Date of Diagnosis:** {diagnosis.get('dateOfDiagnosis', 'N/A')}")

    report.append("\n### Biomarkers")
    biomarkers = diagnosis.get('biomarkers', {})
    for marker, value in biomarkers.items():
        report.append(f"- **{marker}:** {value}")

    report.append("\n### Current Treatment")
    treatments = profile.get('treatments', [])
    for tx in treatments:
        report.append(f"- **Regimen:** {tx.get('regimen', 'N/A')}")
        report.append(f"- **Line:** {tx.get('line', 'N/A')}")
        report.append(f"- **Status:** {tx.get('status', 'N/A')}")
        report.append(f"- **Cycle:** {tx.get('cycleNumber', 'N/A')}")
        toxicities = tx.get('toxicities', [])
        if toxicities:
            report.append("- **Current Toxicities:**")
            for tox in toxicities:
                report.append(f"  - Grade {tox.get('grade')} {tox.get('event')}")

    report.append("\n### Surgical History")
    surgeries = profile.get('surgicalHistory', [])
    for surgery in surgeries:
        report.append(f"- **Procedure:** {surgery.get('procedure', 'N/A')}")
        report.append(f"- **Date:** {surgery.get('date', 'N/A')}")
        report.append(f"- **Outcome:** {surgery.get('outcome', 'N/A')}")

    # Questions and Answers Section
    report.append("\n\n---\n")
    report.append("## 3. Questions and Answers")

    current_category = None
    q_num = 1

    for result in results:
        if result['category'] != current_category:
            current_category = result['category']
            report.append(f"\n### {current_category} Questions\n")

        report.append(f"#### Q{q_num}: {result['question']}")

        if result['success']:
            report.append(f"\n**Answer:**\n{result['answer']}")
            report.append(f"\n*API: {result['api_used']} | Chunks retrieved: {result['chunks_retrieved']}*")
        else:
            report.append(f"\n**Error:** {result['error']}")

        report.append("\n")
        q_num += 1

    # Summary Section
    report.append("\n---\n")
    report.append("## 4. Test Summary")

    # Stats by category
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0}
        categories[cat]['total'] += 1
        if r['success']:
            categories[cat]['success'] += 1

    report.append("\n### Results by Category\n")
    report.append("| Category | Questions | Successful |")
    report.append("|----------|-----------|------------|")
    for cat, stats in categories.items():
        report.append(f"| {cat} | {stats['total']} | {stats['success']} |")

    report.append(f"\n**Overall Success Rate:** {successful}/{len(results)} ({100*successful/len(results):.1f}%)")

    return "\n".join(report)


def main():
    print("=" * 60)
    print("WondrLink Chatbot Test")
    print("=" * 60)

    # Load profile
    print("\n1. Loading patient profile...")
    profile = load_test_profile()
    patient_context = extract_patient_context_complex(profile)
    print(f"   Profile loaded: {profile['patient']['name']}")
    print(f"   Diagnosis: {profile['primaryDiagnosis']['site']} {profile['primaryDiagnosis']['histology']}, Stage {profile['primaryDiagnosis']['stage']}")

    # Load chunks
    print("\n2. Loading document chunks...")
    all_chunks = load_all_chunks()
    print(f"   Loaded {len(all_chunks)} chunks")

    # Run tests
    print(f"\n3. Running {len(TEST_QUESTIONS)} test questions...")
    results = []

    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"   [{i}/{len(TEST_QUESTIONS)}] {q['category']}: ", end="")
        result = run_single_test(q, patient_context, all_chunks, profile)
        results.append(result)
        status = "OK" if result['success'] else "FAIL"
        print(status)

    # Generate report
    print("\n4. Generating report...")
    markdown_report = generate_markdown_report(profile, results)

    # Save markdown
    report_dir = os.path.join(os.path.dirname(__file__), '..')
    md_path = os.path.join(report_dir, 'WondrLink_Test_Report.md')
    with open(md_path, 'w') as f:
        f.write(markdown_report)
    print(f"   Saved: {md_path}")

    # Try to generate PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        pdf_path = os.path.join(report_dir, 'WondrLink_Test_Report.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Question', fontSize=11, spaceAfter=6, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Answer', fontSize=10, spaceAfter=12, leftIndent=20))
        styles.add(ParagraphStyle(name='Category', fontSize=14, spaceAfter=10, fontName='Helvetica-Bold', textColor=colors.darkblue))

        story = []

        # Title
        story.append(Paragraph("WondrLink Chatbot Test Report", styles['Title']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))

        # Procedure
        story.append(Paragraph("1. Test Procedure", styles['Heading1']))
        story.append(Paragraph("This test evaluates the WondrLink chatbot with a dummy patient profile and 20 questions across 7 categories.", styles['Normal']))
        story.append(Spacer(1, 15))

        # Profile Summary
        story.append(Paragraph("2. Patient Profile", styles['Heading1']))
        profile_text = f"""
        <b>Name:</b> {profile['patient']['name']}<br/>
        <b>DOB:</b> {profile['patient']['dob']}<br/>
        <b>Diagnosis:</b> {profile['primaryDiagnosis']['site']} {profile['primaryDiagnosis']['histology']}, Stage {profile['primaryDiagnosis']['stage']}<br/>
        <b>Treatment:</b> {profile['treatments'][0]['regimen']} (Cycle {profile['treatments'][0]['cycleNumber']})<br/>
        <b>Key Biomarkers:</b> KRAS {profile['primaryDiagnosis']['biomarkers']['KRAS']}, MSI: {profile['primaryDiagnosis']['biomarkers']['MSI']}
        """
        story.append(Paragraph(profile_text, styles['Normal']))
        story.append(Spacer(1, 15))

        # Questions and Answers
        story.append(Paragraph("3. Questions and Answers", styles['Heading1']))

        current_cat = None
        for i, r in enumerate(results, 1):
            if r['category'] != current_cat:
                current_cat = r['category']
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"{current_cat} Questions", styles['Category']))

            q_text = f"Q{i}: {r['question']}"
            story.append(Paragraph(q_text, styles['Question']))

            if r['success'] and r['answer']:
                # Clean answer for PDF
                answer = r['answer'].replace('\n', '<br/>').replace('&', '&amp;')
                story.append(Paragraph(f"<i>{answer}</i>", styles['Answer']))
            else:
                story.append(Paragraph(f"<i>Error: {r.get('error', 'Unknown')}</i>", styles['Answer']))

        # Build PDF
        doc.build(story)
        print(f"   Saved: {pdf_path}")

    except ImportError:
        print("   Note: reportlab not installed. PDF not generated.")
        print("   Install with: pip install reportlab")
    except Exception as e:
        print(f"   PDF generation failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    print(f"Total Questions: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print("\nDone!")


if __name__ == '__main__':
    main()
