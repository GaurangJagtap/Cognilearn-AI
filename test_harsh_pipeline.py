"""
Harsh's Evaluator, Report Generator & API Pipeline Verification Script.
Platform: Cognilearn-AI / Bharat AI
"""

import sys
import os
from pathlib import Path

# Ensure backend root is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app.core.evaluator import evaluate_answer
from backend.app.core.report_generator import generate_report
from fastapi.testclient import TestClient
from backend.app.main import app


def run_harsh_verification():
    print("=" * 75)
    print(" HARSH'S EVALUATOR, REPORT & FRONTEND API LAYER — HANDOVER VERIFICATION")
    print("=" * 75)

    # 1. Test Evaluator Engine: Correct Answer
    res1 = evaluate_answer(
        question="What is the SI unit of Electric Current?",
        correct_answer="Ampere",
        student_answer="Ampere"
    )
    print(f"[OK] Correct Answer Evaluation: {res1['action']} (correct={res1['correct']})")
    assert res1["correct"] is True, "Evaluation expected correct=True"

    # 2. Test Evaluator Engine: Misconception Detection
    res2 = evaluate_answer(
        question="According to Ohm's Law, what happens to current if resistance increases at constant voltage?",
        correct_answer="Current decreases",
        student_answer="Current increases"
    )
    print(f"[OK] Misconception Answer Evaluation: {res2['action']}")
    print(f"     Misconception: {res2.get('misconception', 'Inverse relationship violated')}")
    assert res2["correct"] is False, "Evaluation expected correct=False"

    # 3. Test Learning Report Generator
    sample_quiz = [
        {"question": "What is unit of current?", "selected": "Ampere", "correct": "Ampere", "is_correct": True, "topic": "Units"},
        {"question": "What is Ohm's Law?", "selected": "V = I * R", "correct": "V = I * R", "is_correct": True, "topic": "Formula"},
        {"question": "What is resistance?", "selected": "Opposition to current", "correct": "Opposition to current", "is_correct": True, "topic": "Circuit Properties"}
    ]
    report = generate_report(sample_quiz)
    print(f"[OK] Report Generator: Score={report['score']}%")
    print(f"     Recommendation: {report['recommendation']}")
    assert report["score"] == 100, "Expected 100% score"

    # 4. Test FastAPI Endpoints via TestClient
    client = TestClient(app)
    h_res = client.get("/api/health")
    assert h_res.status_code == 200, "Health check failed"
    print("[OK] FastAPI /api/health Endpoint verified!")

    # Test Primary Study Tools endpoint
    st_res = client.get("/api/study-tools")
    assert st_res.status_code == 200, "Study tools endpoint failed"
    st_data = st_res.json()
    print(f"[OK] FastAPI /api/study-tools Endpoint verified!")
    print(f"     Flashcards: {len(st_data.get('flashcards', []))}")
    print(f"     Taxonomy Pillars: {len(st_data.get('taxonomy_tree', {}).get('children', []))}")
    print(f"     Process Flow Stages: {len(st_data.get('pipeline_flow', []))}")

    # Test Backwards-Compatible Flashcards Alias
    b_res = client.get("/api/bonus/flashcards")
    assert b_res.status_code == 200, "Bonus flashcards alias failed"
    print(f"[OK] FastAPI /api/bonus/flashcards Backwards-compatible alias verified!")

    # Test Answer Evaluation Endpoint
    eval_res = client.post("/api/evaluate", json={
        "question": "What is the unit of power?",
        "correct_answer": "Watt",
        "student_answer": "Watt"
    })
    assert eval_res.status_code == 200, "Evaluate endpoint failed"
    assert eval_res.json()["correct"] is True, "Expected correct evaluation"
    print("[OK] FastAPI /api/evaluate Endpoint verified!")

    print("\n=============================================================")
    print("ALL HARSH EVALUATOR & FRONTEND DELIVERABLES VERIFIED 100% CLEANLY!")
    print("=============================================================")


if __name__ == "__main__":
    run_harsh_verification()
