"""
Evaluator Core Engine (Step 6 - Adaptive Teaching & Misconception Analysis)
Evaluates checkpoint questions, identifies student misconceptions, and generates adaptive re-explanations.
"""

import json
import os
from typing import Dict, Any
from backend.app.db.models import EvaluationResult
from backend.app.prompts.evaluator_prompt import EVALUATOR_SYSTEM_PROMPT, build_evaluator_user_prompt
from backend.app.config import settings

def generate_mock_evaluation(question: str, correct_answer: str, student_answer: str) -> EvaluationResult:
    """Fallback evaluator for offline testing."""
    is_correct = (student_answer.strip().lower() == correct_answer.strip().lower())
    
    if is_correct:
        return EvaluationResult(
            correct=True,
            misconception="",
            action="advance",
            new_explanation="Excellent! You've mastered this checkpoint concept.",
            new_analogy="Think of this like passing a checkpoint in a race with full momentum."
        )
    else:
        return EvaluationResult(
            correct=False,
            misconception=f"Confused '{student_answer}' with correct answer '{correct_answer}'.",
            action="re_explain",
            new_explanation=f"Let's look at this from another angle. '{correct_answer}' is correct because of the direct relationship between variables.",
            new_analogy="Imagine adjusting the pressure valve on a water pipe — increasing pressure pushes more water through faster."
        )

def evaluate_answer(question: str, correct_answer: str, student_answer: str) -> Dict[str, Any]:
    """
    Evaluates student answer with LLM / fallback engine.
    """
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            user_prompt = build_evaluator_user_prompt(question, correct_answer, student_answer)
            response = client.chat.completions.create(
                model=settings.DEFAULT_LLM_MODEL,
                messages=[
                    {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            eval_dict = json.loads(content)
            return EvaluationResult(**eval_dict).model_dump()
            
        except Exception as e:
            print(f"[WARNING] Evaluator LLM call failed ({e}). Using mock evaluation engine.")
            return generate_mock_evaluation(question, correct_answer, student_answer).model_dump()
    else:
        return generate_mock_evaluation(question, correct_answer, student_answer).model_dump()
