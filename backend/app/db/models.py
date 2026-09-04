from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CheckpointQuestion(BaseModel):
    type: str = Field(default="mcq", description="Question type, e.g. mcq, short_answer")
    question: str
    options: List[str] = Field(default_factory=list)
    correct: str

class Section(BaseModel):
    id: str
    concept: str
    explanation: str
    concise_explanation: Optional[str] = Field(default=None, description="Concise bulleted summary")
    detailed_explanation: Optional[str] = Field(default=None, description="In-depth detailed explanation")
    example: str
    visual_type: str = Field(default="diagram", description="visual representation: diagram | graph | code | timeline | equation")
    narration_script: str
    checkpoint_question: Optional[CheckpointQuestion] = None
    image_url: Optional[str] = Field(default=None, description="Extracted document image URL if available")
    visual_details: Optional[Dict[str, Any]] = Field(default=None, description="LLM-generated visual details like nodes, edges, labels, formulas")

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str] = Field(default_factory=list)
    correct: str
    difficulty: str = Field(default="medium", description="Question difficulty: easy | medium | hard")
    concept_category: Optional[str] = Field(default=None, description="Target concept category")

class LessonPlan(BaseModel):
    title: str
    level: str = "beginner"
    time_minutes: int = 20
    language: str = "en"
    topic_or_chapter: str
    sections: List[Section] = Field(default_factory=list)
    final_quiz: List[QuizQuestion] = Field(default_factory=list)

class AssessmentRecord(BaseModel):
    topic: str
    score: int
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    strong_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)

class LearnerProfile(BaseModel):
    student_id: str = "u123"
    name: str = "Student"
    email: str = "student@aiplatform.org"
    username: str = "student_user"
    registered_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    topics_studied: List[str] = Field(default_factory=list)
    current_learning_path: Optional[str] = None
    milestone_progress: Dict[str, str] = Field(default_factory=dict)
    strong_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    assessment_history: List[Dict[str, Any]] = Field(default_factory=list)
    checkpoint_history: List[Dict[str, Any]] = Field(default_factory=list)
    preferred_language: str = "en"
    preferred_level: str = "beginner"

    def add_topic_studied(self, topic: str) -> None:
        if topic and topic not in self.topics_studied:
            self.topics_studied.append(topic)

    def record_assessment(
        self,
        topic: str,
        score: int,
        date_str: Optional[str] = None,
        strong_areas: Optional[List[str]] = None,
        weak_areas: Optional[List[str]] = None,
    ):
        record = {
            "topic": topic,
            "score": score,
            "date": date_str or datetime.now().strftime("%Y-%m-%d"),
            "strong_areas": strong_areas or [],
            "weak_areas": weak_areas or []
        }
        self.assessment_history.append(record)
        self.add_topic_studied(topic)

        if strong_areas:
            for c in strong_areas:
                if c not in self.strong_concepts:
                    self.strong_concepts.append(c)
                if c in self.weak_concepts:
                    self.weak_concepts.remove(c)

        if weak_areas:
            for c in weak_areas:
                if c not in self.weak_concepts and c not in self.strong_concepts:
                    self.weak_concepts.append(c)

        return record

    def set_learning_path(self, path_title: str, milestones: Optional[Dict[str, str]] = None) -> None:
        self.current_learning_path = path_title
        if milestones:
            self.milestone_progress = milestones

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

class EvaluationResult(BaseModel):
    correct: bool
    misconception: str
    action: str = Field(default="advance", description="'re_explain' or 'advance'")
    new_explanation: str
    new_analogy: Optional[str] = None

class Milestone(BaseModel):
    id: str
    topic: str
    status: str = "not_started"

class LearningPath(BaseModel):
    path_title: str
    milestones: List[Milestone] = Field(default_factory=list)
