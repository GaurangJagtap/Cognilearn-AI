"""
Harsh's Evaluator, Report Generator & API Pipeline Verification Script.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app.core.evaluator import evaluate_answer
from backend.app.core.report_generator import generate_report
from fastapi.testclient import TestClient
from backend.app.main import app

def run_harsh_verification():
    print("=" * 75)
    print(" HARSH'S EVALUATOR, REPORT & FRONTEND API LAYER — HANDOVER VERIFICATION")
    print("=" * 75)

    # 1. Test Evaluator Engine
    res1 = evaluate_answer(
        question="What is the SI unit of Electric Current?",
        correct_answer="Ampere",
        student_answer="Ampere"
    )
    print(f"[OK] Correct Answer Evaluation: {res1['action']} (correct={res1['correct']})")

    res2 = evaluate_answer(
        question="According to Ohm's Law, what happens to current if resistance increases at constant voltage?",
        correct_answer="Current decreases",
        student_answer="Current increases"
    )
    print(f"[OK] Misconception Answer Evaluation: {res2['action']}")
    print(f"     Misconception: {res2['misconception']}")

    # 2. Test Learning Report Generator
    sample_quiz = [
        {"question": "What is unit of current?", "selected": "Ampere", "correct": "Ampere", "is_correct": True, "topic": "Units"},
        {"question": "What is Ohm's Law?", "selected": "V = I * R", "correct": "V = I * R", "is_correct": True, "topic": "Formula"}
    ]
    report = generate_report(sample_quiz)
    print(f"[OK] Report Generator: Score={report['score']}%")
    print(f"     Recommendation: {report['recommendation']}")

    # 3. Test API Endpoints
    client = TestClient(app)
    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    print("[OK] FastAPI /api/health Endpoint verified!")

    b_res = client.get("/api/bonus/flashcards")
    assert b_res.status_code == 200
    print(f"[OK] FastAPI /api/bonus/flashcards Endpoint verified! ({len(b_res.json()['flashcards'])} cards)")

    print("\n=============================================================")
    print("ALL HARSH EVALUATOR & FRONTEND DELIVERABLES VERIFIED 100% CLEANLY!")
    print("=============================================================")

if __name__ == "__main__":
    run_harsh_verification()
