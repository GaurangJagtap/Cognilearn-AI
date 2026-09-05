"""
AI Learning Platform Main Entrypoint & Master Orchestrator
"""

import sys
import os

# Ensure the project root directory is always on sys.path for cloud hosts like Render
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

# Core Modules
from backend.app.core.lesson_planner import generate_lesson_plan
from backend.app.core.retriever import ingest_document, retrieve_relevant_chunks
from backend.app.core.learning_path_generator import generate_learning_path
from backend.app.db.models import LessonPlan, LearnerProfile

# Subsystem Imports
from backend.app.core.ingestion import extract_text
from backend.app.core.language_manager import detect_language, switch_language, prepare
from backend.app.core.visual_classifier import classify_visual
from backend.app.media.tts import generate_audio
from backend.app.media.avatar import generate_avatar_video
from backend.app.media.visuals import render_visual
from backend.app.media.video_assembler import stitch_video
from backend.app.core.evaluator import evaluate_answer
from backend.app.core.report_generator import generate_report

# API Router
from backend.app.api.routes import router as api_router

app = FastAPI(
    title="AI Learning Platform",
    description="Adaptive Learning Backend API and Master Orchestrator",
    version="1.0.0"
)

# Include API Router
app.include_router(api_router)

# Mount static web app and storage assets
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
EXTRACTED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "extracted_images")
GENERATED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "generated_visuals")

os.makedirs(EXTRACTED_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

app.mount("/extracted_images", StaticFiles(directory=EXTRACTED_DIR), name="extracted_images")
app.mount("/generated_visuals", StaticFiles(directory=GENERATED_DIR), name="generated_visuals")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    @app.get("/")
    def serve_frontend():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

def orchestrate_full_lesson_pipeline(
    topic: str,
    file_path: Optional[str] = None,
    time_minutes: int = 20,
    language: str = "en"
) -> Dict[str, Any]:
    print(f"\n[ORCHESTRATOR] Starting pipeline for topic: '{topic}' ({time_minutes} min, lang='{language}')")
    
    retrieved_context = ""
    if file_path:
        text = extract_text(file_path)
        ingest_document(text)
        retrieved_context = retrieve_relevant_chunks(topic)
        
    profile = {"preferred_level": "beginner"}
    plan = generate_lesson_plan(
        topic=topic,
        profile=profile,
        time_minutes=time_minutes,
        language=language,
        retrieved_context=retrieved_context
    )
    
    plan_dict = plan.model_dump()
    
    generated_clips = []
    for section in plan_dict.get("sections", []):
        concept = section["concept"]
        visual_type = classify_visual(concept)
        section["visual_type"] = visual_type
        script, _ = prepare(section, language)
        
        asset_path = render_visual(concept, visual_type)
        audio_path = generate_audio(script, language)
        clip_path = generate_avatar_video(audio_path, script=script)
        generated_clips.append(clip_path)
        
    final_video = stitch_video(generated_clips)
    
    print(f"[ORCHESTRATOR] Assembly complete! Final lesson video stored at: '{final_video}'")
    return {
        "lesson_plan": plan_dict,
        "final_video_path": final_video,
        "section_clips": generated_clips
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    is_prod = os.environ.get("RENDER") is not None or os.environ.get("ENVIRONMENT") == "production"
    print("\n=============================================================")
    print(f" AI Learning Platform Application Server (Port {port})")
    print(f" Open in Browser: http://localhost:{port}  OR  http://127.0.0.1:{port}")
    print("=============================================================\n")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=not is_prod)

