"""
FastAPI Routes for AI Teacher
Glue layer connecting:
  - Ingestion / File upload
  - Lesson Planner
  - Answer Evaluator
  - Report Generator
  - Learner Profile & History
  - Bonus interactive features (Flashcards, Concept Map, Notes)
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from pydantic import BaseModel, Field

from backend.app.core.ingestion import extract_text, extract_images_from_doc
from backend.app.core.evaluator import evaluate_answer
from backend.app.core.report_generator import generate_report
from backend.app.core.lesson_planner import generate_lesson_plan
from backend.app.core.retriever import ingest_document, retrieve_relevant_chunks

router = APIRouter(prefix="/api", tags=["AI Learning Platform API"])

STORAGE_UPLOADS_DIR = Path("storage/uploads")
STORAGE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SESSION_STATE = {
    "current_lesson_plan": None,
    "extracted_images": [],
    "learner_profile": {
        "user_id": "student_001",
        "name": "Student",
        "level": "beginner",
        "language": "en",
        "learning_streak_days": 1,
        "completed_lessons": 0,
        "mastered_concepts": [],
        "needs_review_concepts": []
    },
    "quiz_history": []
}

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    level: Optional[str] = "beginner"
    language: Optional[str] = "en"

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str

class EvaluationRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: str

class EvaluationResponse(BaseModel):
    correct: bool
    misconception: str
    action: str
    new_explanation: str

class QuizResultItem(BaseModel):
    question: str
    selected: str
    correct: str
    is_correct: Optional[bool] = None
    topic: Optional[str] = None

class AssessmentRequest(BaseModel):
    quiz_results: List[QuizResultItem]

class AssessmentResponse(BaseModel):
    score: int
    strong_areas: List[str]
    weak_areas: List[str]
    recommendation: str

class GenerateLessonRequest(BaseModel):
    text: Optional[str] = ""
    topic: Optional[str] = "Electricity & Magnetism"
    level: Optional[str] = "beginner"
    time_minutes: Optional[int] = 20
    language: Optional[str] = "en"

class LearnerProfileModel(BaseModel):
    user_id: str = "student_001"
    name: str = "Student"
    email: str = "student@aiplatform.org"
    username: str = "student_user"
    level: str = "beginner"
    language: str = "en"
    learning_streak_days: int = 4
    completed_lessons: int = 3
    mastered_concepts: List[str] = []
    needs_review_concepts: List[str] = []

# --- AUTHENTICATION ROUTES ---
@router.post("/auth/register")
def register_user(payload: UserRegisterRequest):
    profile = {
        "user_id": f"usr_{hash(payload.username) & 0xfffffff}",
        "name": payload.name,
        "email": payload.email,
        "username": payload.username,
        "level": payload.level or "beginner",
        "language": payload.language or "en",
        "registered_at": datetime.now().strftime("%Y-%m-%d"),
        "learning_streak_days": 1,
        "completed_lessons": 0,
        "mastered_concepts": [],
        "needs_review_concepts": [],
        "topics_studied": [],
        "assessment_history": []
    }
    SESSION_STATE["learner_profile"] = profile
    return {"status": "success", "message": "User registered successfully", "profile": profile}

@router.post("/auth/login")
def login_user(payload: UserLoginRequest):
    if not payload.username_or_email:
        raise HTTPException(status_code=400, detail="Username or email required")
    profile = SESSION_STATE.get("learner_profile") or {
        "user_id": "student_001",
        "name": payload.username_or_email.split("@")[0].title(),
        "email": payload.username_or_email,
        "username": payload.username_or_email,
        "level": "beginner",
        "language": "en",
        "learning_streak_days": 1,
        "completed_lessons": 0,
        "mastered_concepts": [],
        "needs_review_concepts": []
    }
    SESSION_STATE["learner_profile"] = profile
    return {"status": "success", "message": "Login successful", "profile": profile}

@router.get("/auth/me")
def get_current_user():
    return SESSION_STATE.get("learner_profile") or {}

# --- DYNAMIC STUDY TOOLS ROUTE ---
@router.get("/study-tools")
def get_study_tools():
    lesson = SESSION_STATE.get("current_lesson_plan") or {}
    topic = lesson.get("topic_or_chapter") or lesson.get("title") or "Study Module"
    sections = lesson.get("sections") or []

    # Dynamic Flashcards generated from sections
    flashcards = []
    for idx, sec in enumerate(sections, 1):
        concept = sec.get("concept") or f"Concept {idx}"
        explanation = sec.get("explanation") or sec.get("detailed_explanation") or "Key concept principle"
        example = sec.get("example") or "Practical real-world application"
        flashcards.append({
            "id": f"fc_{idx}",
            "front": f"What is {concept}?",
            "back": explanation,
            "example": example
        })

    if not flashcards:
        flashcards = [
            {
                "id": "fc_1",
                "front": f"What is the core principle of {topic}?",
                "back": f"The primary operational framework and policy scope governing {topic}.",
                "example": f"Real-world application of {topic} in modern workflows."
            }
        ]

    # Dynamic Concept Taxonomy Map Tree
    taxonomy_tree = {
        "name": topic,
        "children": [
            {
                "name": sec.get("concept", f"Pillar {idx}"),
                "children": [
                    {"name": "Foundational Guidelines"},
                    {"name": "Operational Execution"},
                    {"name": "Target Impact & Outcomes"}
                ]
            } for idx, sec in enumerate(sections, 1)
        ] if sections else [
            {
                "name": f"{topic} Core Strategy",
                "children": [{"name": "Policy & Scope"}, {"name": "Implementation"}, {"name": "Evaluation Metrics"}]
            }
        ]
    }

    # Dynamic Study Notes Summary
    notes_lines = [
        f"# Master Study Notes: {topic.upper()}",
        f"**Date:** {datetime.now().strftime('%B %d, %Y')} | **Target Level:** {lesson.get('level', 'Beginner').title()}",
        "---",
        "## 📌 Key Module Pillars & Concepts\n"
    ]
    for idx, sec in enumerate(sections, 1):
        notes_lines.append(f"### {idx}. {sec.get('concept', 'Pillar ' + str(idx))}")
        notes_lines.append(f"{sec.get('explanation', '')}\n")
        notes_lines.append(f"* **Practical Example:** {sec.get('example', '')}\n")

    return {
        "topic": topic,
        "flashcards": flashcards,
        "taxonomy_tree": taxonomy_tree,
        "study_notes": "\n".join(notes_lines)
    }

def get_default_sample_lesson() -> dict:
    sample_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "docs", "sample_lesson_plan.json")
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "title": "Chapter 4: Electricity & Magnetism",
        "level": "beginner",
        "time_minutes": 20,
        "language": "en",
        "topic_or_chapter": "Electric Current and Ohm's Law",
        "sections": [
            {
                "id": "s1",
                "concept": "Electric Current and Voltage",
                "explanation": "Electric current is the rate of flow of electric charge in a circuit. Voltage is the electrical pressure that drives current.",
                "example": "Think of voltage as water pressure in a tank, and current as the flow of water through the hose.",
                "visual_type": "diagram",
                "narration_script": "Welcome! Today we will explore electric current and voltage. Current is the rate of flow of charge, and voltage is the electrical pressure driving the flow.",
                "checkpoint_question": {
                    "type": "mcq",
                    "question": "What is the SI unit of Electric Current?",
                    "options": ["Volt", "Ampere", "Ohm", "Watt"],
                    "correct": "Ampere"
                }
            }
        ],
        "final_quiz": [
            {
                "id": "q1",
                "question": "Which formula correctly represents Ohm's Law?",
                "options": ["V = I * R", "V = I / R", "R = V * I", "I = V * R"],
                "correct": "V = I * R"
            }
        ]
    }

def _infer_suggested_topic(filename: str, text: str) -> str:
    name_without_ext = Path(filename).stem
    clean_name = re.sub(r'[\-_]', ' ', name_without_ext)
    clean_name = re.sub(r'\b(ppt|pptx|pdf|docx|notes|chapter|doc|draft|v\d+)\b', '', clean_name, flags=re.IGNORECASE).strip()
    
    if clean_name and len(clean_name) >= 3:
        return clean_name.title()
        
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("---")]
    if lines:
        first_line = lines[0]
        first_line = re.sub(r'^[#*\-•\s]+', '', first_line).strip()
        if 3 <= len(first_line) <= 60:
            return first_line.title()
            
    return "Uploaded Study Guide"

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Learning Platform API"}

@router.post("/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    extracted_text = ""
    filename = "uploaded_notes.txt"
    extracted_images = []

    if file:
        filename = file.filename
        saved_file_path = STORAGE_UPLOADS_DIR / filename
        content_bytes = await file.read()
        
        with open(saved_file_path, "wb") as f:
            f.write(content_bytes)

        try:
            extracted_text = extract_text(str(saved_file_path))
            extracted_images = extract_images_from_doc(str(saved_file_path))
            SESSION_STATE["extracted_images"] = extracted_images
        except Exception as e:
            print(f"[Upload Error] Extraction failed for {filename}: {e}")
            extracted_text = f"File uploaded: {filename}. Content ready for lesson planning."
    elif raw_text:
        extracted_text = raw_text.strip()
        SESSION_STATE["extracted_images"] = []
    else:
        extracted_text = "Electricity and Magnetism Fundamentals: Electric current is the rate at which charge flows."
        SESSION_STATE["extracted_images"] = []

    if len(extracted_text) > 50000:
        extracted_text = extracted_text[:50000] + "\n... [Content truncated for display length]"

    suggested_topic = _infer_suggested_topic(filename, extracted_text)

    return {
        "status": "success",
        "filename": filename,
        "text": extracted_text,
        "suggested_topic": suggested_topic,
        "char_count": len(extracted_text),
        "extracted_images": extracted_images,
        "preview": extracted_text[:200] + ("..." if len(extracted_text) > 200 else "")
    }

@router.post("/generate-lesson-plan")
def generate_lesson_plan_endpoint(payload: GenerateLessonRequest):
    retrieved_context = ""
    if payload.text:
        ingest_document(payload.text)
        retrieved_context = retrieve_relevant_chunks(payload.topic or "Electricity")

    profile = {
        "preferred_level": payload.level or "beginner",
        "weak_concepts": SESSION_STATE["learner_profile"].get("needs_review_concepts", [])
    }

    plan_model = generate_lesson_plan(
        topic=payload.topic or "Electricity & Magnetism",
        profile=profile,
        time_minutes=payload.time_minutes or 20,
        language=payload.language or "en",
        retrieved_context=retrieved_context
    )

    lesson_plan = plan_model.model_dump()

    # Enrich sections with extracted document images or dynamic visual details
    extracted_imgs = SESSION_STATE.get("extracted_images", [])
    for idx, sec in enumerate(lesson_plan.get("sections", [])):
        concept = sec.get("concept", "Core Concept")
        visual_type = sec.get("visual_type", "diagram")

        # Assign extracted document image if available
        if extracted_imgs:
            img_obj = extracted_imgs[idx % len(extracted_imgs)]
            sec["image_url"] = img_obj["url"]

        # Ensure visual_details exists
        if not sec.get("visual_details"):
            sec["visual_details"] = {
                "diagram_type": visual_type,
                "title": concept,
                "nodes": [
                    {"id": "n1", "label": f"{concept} Input", "category": "input", "description": f"Initial state or input of {concept}"},
                    {"id": "n2", "label": f"Core Process", "category": "process", "description": f"Main mechanism of {concept}"},
                    {"id": "n3", "label": f"Output / Result", "category": "output", "description": f"Key outcome of {concept}"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "leads to"},
                    {"from": "n2", "to": "n3", "label": "results in"}
                ],
                "key_formula": f"{concept} Principle"
            }

    SESSION_STATE["current_lesson_plan"] = lesson_plan
    return lesson_plan

@router.get("/current-lesson")
def get_current_lesson():
    if SESSION_STATE["current_lesson_plan"] is None:
        SESSION_STATE["current_lesson_plan"] = get_default_sample_lesson()
    return SESSION_STATE["current_lesson_plan"]

@router.post("/interact", response_model=EvaluationResponse)
@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_student_interaction(payload: EvaluationRequest):
    result = evaluate_answer(
        question=payload.question,
        correct_answer=payload.correct_answer,
        student_answer=payload.student_answer
    )
    return result

@router.post("/assessment", response_model=AssessmentResponse)
@router.post("/report", response_model=AssessmentResponse)
def generate_assessment_report(payload: AssessmentRequest):
    quiz_results_dicts = [item.model_dump() for item in payload.quiz_results]
    report = generate_report(quiz_results_dicts)

    SESSION_STATE["quiz_history"].append(report)
    profile = SESSION_STATE["learner_profile"]
    if report["strong_areas"]:
        for area in report["strong_areas"]:
            if area not in profile["mastered_concepts"]:
                profile["mastered_concepts"].append(area)
    if report["weak_areas"]:
        profile["needs_review_concepts"] = report["weak_areas"]

    return report

@router.get("/profile")
def get_learner_profile():
    return SESSION_STATE["learner_profile"]

@router.post("/profile")
def update_learner_profile(profile_update: LearnerProfileModel):
    SESSION_STATE["learner_profile"] = profile_update.model_dump()
    return {"status": "success", "profile": SESSION_STATE["learner_profile"]}

@router.get("/bonus/flashcards")
def get_flashcards():
    lesson = SESSION_STATE["current_lesson_plan"] or get_default_sample_lesson()
    cards = []
    for s in lesson.get("sections", []):
        cards.append({
            "id": f"fc_{s['id']}",
            "concept": s["concept"],
            "front": f"What is {s['concept']}?",
            "back": s["explanation"],
            "example": s.get("example", "")
        })
    return {"flashcards": cards}

@router.get("/bonus/concept-map")
def get_concept_map():
    return {
        "root": "Electricity & Circuits",
        "nodes": [
            {"id": "n1", "label": "Electric Charge (Q)", "type": "fundamental"},
            {"id": "n2", "label": "Current I (Amps)", "type": "flow"},
            {"id": "n3", "label": "Voltage V (Volts)", "type": "pressure"},
            {"id": "n4", "label": "Resistance R (Ohms)", "type": "opposition"},
            {"id": "n5", "label": "Ohm's Law (V = I*R)", "type": "law"}
        ],
        "links": [
            {"source": "n1", "target": "n2"},
            {"source": "n3", "target": "n2"},
            {"source": "n4", "target": "n2"}
        ]
    }

@router.get("/bonus/notes")
def get_study_notes():
    lesson = SESSION_STATE["current_lesson_plan"] or get_default_sample_lesson()
    md_content = f"# Study Notes: {lesson.get('title', 'Electricity & Magnetism')}\n\n"
    md_content += f"**Level:** {lesson.get('level', 'Beginner').capitalize()} | **Language:** {lesson.get('language', 'en').upper()}\n\n"
    md_content += "## Key Concepts Summary\n\n"
    for sec in lesson.get("sections", []):
        md_content += f"### {sec['concept']}\n"
        md_content += f"- **Explanation:** {sec['explanation']}\n"
        md_content += f"- **Key Analogy:** *{sec['example']}*\n\n"
    return {"notes_markdown": md_content}
