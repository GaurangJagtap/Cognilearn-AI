import json
from backend.app.core.time_rules import get_time_rules
from backend.app.core.lesson_planner import generate_lesson_plan

def run_step_2_tests():
    print("=== Testing Step 2: Time-Based Rules & Lesson Planner Engine ===")
    
    # Test 1: Time Rules Map
    rule_5 = get_time_rules(5)
    rule_20 = get_time_rules(20)
    rule_60 = get_time_rules(60)
    
    assert rule_5["max_sections"] == 1, "5 min rule failed"
    assert rule_20["max_sections"] == 4, "20 min rule failed"
    assert rule_60["max_sections"] == 8, "60 min rule failed"
    print("[OK] Time-based rules logic verified!")
    
    # Test 2: Generate 5-Minute Lesson Plan
    plan_5 = generate_lesson_plan(
        topic="Newton's Laws of Motion",
        profile={"preferred_level": "beginner"},
        time_minutes=5,
        language="en"
    )
    print(f"[OK] 5-Min Lesson Plan generated: '{plan_5.title}' ({len(plan_5.sections)} section)")
    assert len(plan_5.sections) == 1, "5-min plan section count mismatch"
    
    # Test 3: Generate 20-Minute Lesson Plan
    plan_20 = generate_lesson_plan(
        topic="Photosynthesis & Cell Respiration",
        profile={"preferred_level": "intermediate", "weak_concepts": ["Calvin Cycle"]},
        time_minutes=20,
        language="hi"
    )
    print(f"[OK] 20-Min Lesson Plan generated: '{plan_20.title}' ({len(plan_20.sections)} sections)")
    assert len(plan_20.sections) >= 3, "20-min plan section count mismatch"
    
    # Test 4: Validate output serialization to dict/json
    plan_json = plan_20.model_dump_json(indent=2)
    parsed_json = json.loads(plan_json)
    assert "sections" in parsed_json, "JSON serialization failed"
    print("[OK] Lesson Plan JSON serialization verified successfully!")
    print("\n=== STEP 2 VERIFICATION PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_step_2_tests()
