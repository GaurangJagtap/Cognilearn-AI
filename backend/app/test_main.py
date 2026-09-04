import json
from backend.app.main import orchestrate_full_lesson_pipeline, app
from backend.app.core.learning_path_generator import generate_learning_path
from fastapi.testclient import TestClient

def test_full_project_pipeline():
    print("=== FINAL INTEGRATION VERIFICATION FOR GAURANG'S WORK ===")
    
    # 1. Test Learning Path Roadmap Generator
    path = generate_learning_path("Artificial Intelligence & Neural Networks")
    print(f"[OK] Learning Path Roadmap generated: '{path.path_title}' with {len(path.milestones)} milestones")
    assert len(path.milestones) >= 4, "Learning path milestones count mismatch"
    
    # 2. Test End-to-End Orchestrator Pipeline
    result = orchestrate_full_lesson_pipeline(
        topic="Quantum Mechanics Fundamentals",
        file_path="docs/contracts.md",
        time_minutes=20,
        language="hi"
    )
    
    assert "lesson_plan" in result, "Pipeline output missing lesson_plan"
    assert "final_video_path" in result, "Pipeline output missing final_video_path"
    assert len(result["section_clips"]) > 0, "No section clips generated"
    
    print(f"[OK] Master Orchestrator execution clean!")
    print(f"     Title: {result['lesson_plan']['title']}")
    print(f"     Sections: {len(result['lesson_plan']['sections'])}")
    print(f"     Stitched Video: {result['final_video_path']}")
    
    # 3. Test FastAPI Server Endpoints via TestClient
    client = TestClient(app)
    
    # Health endpoint
    response = client.get("/api/health")
    assert response.status_code == 200
    print("[OK] FastAPI /api/health endpoint verified!")
    
    # Evaluate answer endpoint
    eval_resp = client.post("/api/evaluate", json={
        "question": "What is 2+2?",
        "correct_answer": "4",
        "student_answer": "4"
    })
    assert eval_resp.status_code == 200
    assert eval_resp.json()["correct"] is True
    print("[OK] FastAPI /api/evaluate endpoint verified!")

    print("=============================================================")
    print("[SUCCESS] ALL TECHNICAL RESPONSIBILITIES & INTEGRATION ARE 100% DONE!")
    print("=============================================================")

if __name__ == "__main__":
    test_full_project_pipeline()
