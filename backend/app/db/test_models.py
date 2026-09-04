import json
from backend.app.db.models import LessonPlan, LearnerProfile

def verify_contracts():
    # Load sample lesson plan
    with open("docs/sample_lesson_plan.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Parse into Pydantic model
    plan = LessonPlan(**data)
    print("[OK] LessonPlan parsed successfully!")
    print(f"   Title: {plan.title}")
    print(f"   Sections count: {len(plan.sections)}")
    print(f"   Final quiz questions: {len(plan.final_quiz)}")
    
    # Sample Learner Profile test
    profile_data = {
        "student_id": "gaurang_test",
        "topics_studied": ["Electricity Basics"],
        "strong_concepts": ["Voltage"],
        "weak_concepts": ["Ohm's Law"],
        "preferred_language": "hi",
        "preferred_level": "beginner"
    }
    profile = LearnerProfile(**profile_data)
    print("[OK] LearnerProfile parsed successfully!")
    print(f"   Student ID: {profile.student_id}")

if __name__ == "__main__":
    verify_contracts()
