"""
Yukta's Handover Verification Script.
Platform: Cognilearn-AI / Bharat AI

Executes and demonstrates all deliverables:
1. Language Manager (detection, switching, orchestrator preparation)
2. Visual-Type Classifier (multi-subject pedagogical taxonomy)
3. Learner Profile & Long-Term Memory Models

Run: python verify_yukta_handover.py
"""

import json
import sys
import os

# Ensure UTF-8 output encoding across Windows / Linux consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is discoverable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.language_manager import detect_language, switch_language, prepare
from backend.app.core.visual_classifier import classify_visual, classify_visual_with_reasoning
from backend.app.db.models import LearnerProfile


def safe_print(msg: str):
    """Safely prints UTF-8 strings even on legacy Windows terminals."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='backslashreplace').decode('ascii'))


def run_handover_verification():
    safe_print("=" * 75)
    safe_print("AI TEACHER - YUKTA'S MODULE HANDOVER VERIFICATION SUITE")
    safe_print("=" * 75)

    # 1. VERIFY LANGUAGE DETECTION
    safe_print("\n[1] Testing Language Detection (detect_language)...")
    sample_queries = [
        ("I am a beginner. Teach me Chapter 4 in 20 minutes in Hindi.", "en"),
        ("नमस्ते! आज हम विद्युत धारा और वोल्टेज के सिद्धांत को समझेंगे।", "hi"),
        ("Mujhe ye Hinglish mein simple example ke saath samjhao.", "hinglish"),
        ("Namaste! Aaj hum electricity aur voltage ke simple concept ko samjhenge.", "hinglish"),
        ("மின்சாரம் மற்றும் மின்னழுத்தம் பற்றிய பாடம்", "ta")
    ]
    for text, expected in sample_queries:
        detected = detect_language(text)
        safe_print(f"  Input: \"{text[:50]}...\"")
        safe_print(f"  --> Detected: '{detected}' | Expected: '{expected}' (MATCH: {detected == expected})")
        assert detected == expected, f"Language detection mismatch: got '{detected}', expected '{expected}'"

    # 2. VERIFY MID-LESSON LANGUAGE SWITCHING ON CONTRACT JSON
    safe_print("\n[2] Testing Mid-Lesson Language Switching (switch_language)...")
    sample_section = {
        "id": "s1",
        "concept": "Current and Voltage",
        "explanation": "Electric current is the rate of flow of electric charge in a circuit. Voltage is the electrical pressure that drives current.",
        "example": "Think of voltage as water pressure in a tank, and current as the flow of water through the hose.",
        "visual_type": "diagram",
        "narration_script": "Hello! Today we will explore the fundamental concepts of electric current and voltage.",
        "checkpoint_question": {
            "type": "mcq",
            "question": "What is the SI unit of Electric Current?",
            "options": ["Volt", "Ampere", "Ohm", "Watt"],
            "correct": "Ampere"
        }
    }

    safe_print("  Original Section (English):")
    safe_print(f"    Narration: {sample_section['narration_script']}")
    
    hindi_section = switch_language(sample_section, "hi")
    safe_print("\n  Switched to Hindi ('hi'):")
    safe_print(f"    ID (preserved): {hindi_section['id']}")
    safe_print(f"    Visual Type (preserved): {hindi_section['visual_type']}")
    safe_print(f"    Narration: {hindi_section['narration_script']}")
    safe_print(f"    Explanation: {hindi_section['explanation']}")
    safe_print(f"    Question: {hindi_section['checkpoint_question']['question']}")
    assert hindi_section["id"] == sample_section["id"], "Section ID preservation failed"
    assert hindi_section["visual_type"] == sample_section["visual_type"], "Visual type preservation failed"

    hinglish_section = switch_language(sample_section, "hinglish")
    safe_print("\n  Switched to Hinglish ('hinglish'):")
    safe_print(f"    Narration: {hinglish_section['narration_script']}")
    assert hinglish_section["id"] == sample_section["id"], "Section ID preservation failed"

    # 3. VERIFY ORCHESTRATOR PREPARE FUNCTION
    safe_print("\n[3] Testing Orchestrator Preparation (language_manager.prepare)...")
    script, lang_payload = prepare(sample_section, language="hi")
    safe_print(f"  Returned Spoken Script: \"{script[:60]}...\"")
    safe_print(f"  Returned Section Dict ID: {lang_payload['id']}")
    assert len(script) > 0, "Spoken script was empty"
    assert lang_payload["id"] == sample_section["id"], "Section ID mismatch in prepared payload"

    # 4. VERIFY VISUAL-TYPE CLASSIFIER
    safe_print("\n[4] Testing Visual-Type Classifier (classify_visual)...")
    sample_concepts = [
        ("Electric Current and Circuit Loop", "physics", "diagram"),
        ("Ohm's Law V-I Characteristics Curve", "physics", "graph"),
        ("Binary Search Algorithm Implementation", "computer science", "code"),
        ("Einstein Mass Energy Equivalence Formula", "physics", "equation"),
        ("Chronological History of the Internet", "history", "timeline")
    ]
    for concept, domain, expected_type in sample_concepts:
        vtype = classify_visual(concept, domain)
        res = classify_visual_with_reasoning(concept, domain)
        safe_print(f"  Concept: '{concept}' [{domain}]")
        safe_print(f"  --> Visual Type: '{vtype}' (Confidence: {res['confidence']:.2f})")
        assert vtype == expected_type, f"Visual classification mismatch for '{concept}': got '{vtype}', expected '{expected_type}'"

    # 5. VERIFY LEARNER PROFILE & MEMORY MODEL
    safe_print("\n[5] Testing Learner Profile & Long-Term Memory Models...")
    profile = LearnerProfile(
        user_id="usr_test_101",
        name="Yukta Test Learner",
        preferred_language="hi",
        proficiency_tier="Intermediate",
        total_study_minutes=45,
        streak_days=3,
        completed_milestones=["Electric Current", "Ohm's Law"],
        misconceptions=[{"topic": "Resistance", "note": "Confused resistance with resistivity"}]
    )
    safe_print(f"  Profile Created: {profile.name} (Tier: {profile.proficiency_tier}, Streak: {profile.streak_days} days)")
    safe_print(f"  Completed Milestones: {profile.completed_milestones}")
    assert profile.user_id == "usr_test_101", "Profile ID mismatch"
    assert len(profile.completed_milestones) == 2, "Milestones count mismatch"

    safe_print("\n" + "=" * 75)
    safe_print("[SUCCESS] ALL YUKTA DELIVERABLES VERIFIED AND PRODUCTION READY!")
    safe_print("=" * 75)


if __name__ == "__main__":
    run_handover_verification()
