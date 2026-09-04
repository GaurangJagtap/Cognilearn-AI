from backend.app.core.evaluator import evaluate_answer
from backend.app.core.report_generator import generate_report
from backend.app.db.database import get_learner_profile, save_learner_profile
from backend.app.db.models import LearnerProfile

def test_steps_6_and_7():
    print("=== Testing Step 6: Adaptive Evaluator & Step 7: Assessment & DB Persistence ===")
    
    # 1. Test Step 6 - Adaptive Answer Evaluation (Correct answer)
    res_correct = evaluate_answer(
        question="What is the unit of electric current?",
        correct_answer="Ampere",
        student_answer="Ampere"
    )
    print(f"[OK] Correct answer evaluation verified (Action: '{res_correct['action']}')")
    assert res_correct["correct"] is True
    
    # 2. Test Step 6 - Adaptive Answer Evaluation (Incorrect answer -> Misconception + Re-explanation)
    res_wrong = evaluate_answer(
        question="What happens to current if resistance increases at constant voltage?",
        correct_answer="Current decreases",
        student_answer="Current increases"
    )
    print(f"[OK] Incorrect answer evaluation verified:")
    print(f"     Misconception: {res_wrong['misconception']}")
    print(f"     Action: {res_wrong['action']}")
    print(f"     Adaptive Explanation: {res_wrong['new_explanation']}")
    assert res_wrong["correct"] is False
    assert res_wrong["action"] == "re_explain"
    
    # 3. Test Step 7 - Assessment Report & SQLite DB Persistence
    quiz_results = [
        {"concept": "Voltage", "is_correct": True},
        {"concept": "Ohm's Law", "is_correct": False}
    ]
    report = generate_report(quiz_results, student_id="gaurang_step7_test")
    print(f"[OK] Assessment report generated (Score: {report['score']}%)")
    print(f"     Weak areas: {report['weak_areas']}")
    
    # 4. Verify SQLite LearnerProfile Persistence
    profile = get_learner_profile("gaurang_step7_test")
    print(f"[OK] SQLite DB persistence verified for student '{profile.student_id}'")
    print(f"     Persisted Weak Concepts: {profile.weak_concepts}")
    assert "Ohm's Law" in profile.weak_concepts, "DB persistence missed weak concept"
    
    print("\n=============================================================")
    print("[SUCCESS] STEPS 6 & 7 VERIFICATION PASSED 100% CLEANLY!")
    print("=============================================================")

if __name__ == "__main__":
    test_steps_6_and_7()
