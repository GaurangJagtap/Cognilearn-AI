"""
Assessment Report Generator (Step 7 - Quiz Assessment & Persistence)
Converts final quiz logs into comprehensive student performance reports and updates Learner Profile memory.
"""

import json
import os
from typing import Dict, Any, List
from backend.app.prompts.report_prompt import REPORT_SYSTEM_PROMPT, build_report_user_prompt
from backend.app.db.database import update_student_concepts, get_learner_profile
from backend.app.config import settings

def check_is_correct(selected: str, correct: str) -> bool:
    s = selected.strip().lower()
    c = correct.strip().lower()
    if not s or not c:
        return False
    if s == c:
        return True
    if len(s) == 1 and c.startswith(s):
        return True
    if len(c) == 1 and s.startswith(c):
        return True
    if len(s) > 3 and len(c) > 3 and (s in c or c in s):
        return True
    return False

def generate_report(quiz_results: List[Dict[str, Any]], student_id: str = "u123") -> Dict[str, Any]:
    """
    Generates assessment report with deterministic grading accuracy and persists performance metrics.
    """
    if not quiz_results:
        return {
            "score": 0,
            "strong_areas": [],
            "weak_areas": [],
            "recommendation": "No quiz results submitted."
        }
        
    evaluated_results = []
    for item in quiz_results:
        sel = str(item.get("selected", ""))
        corr = str(item.get("correct", ""))
        is_corr = check_is_correct(sel, corr)

        topic = item.get("topic") or item.get("concept_category") or item.get("concept") or "General Concept"
        evaluated_results.append({
            "question": item.get("question", ""),
            "selected": sel,
            "correct": corr,
            "is_correct": is_corr,
            "topic": topic
        })

    total = len(evaluated_results)
    correct_count = sum(1 for q in evaluated_results if q["is_correct"])
    score_pct = int((correct_count / total) * 100) if total > 0 else 0

    strong = [q["topic"] for q in evaluated_results if q["is_correct"]]
    weak = [q["topic"] for q in evaluated_results if not q["is_correct"]]

    strong_unique = list(dict.fromkeys(strong))
    weak_unique = list(dict.fromkeys(weak))

    # Persist progress to database
    update_student_concepts(student_id=student_id, new_strong=strong_unique, new_weak=weak_unique)

    recommendation = f"Score: {score_pct}%. Keep practicing weak areas: {', '.join(weak_unique) if weak_unique else 'None'}."

    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            user_prompt = build_report_user_prompt(evaluated_results)
            response = client.chat.completions.create(
                model=settings.DEFAULT_LLM_MODEL,
                messages=[
                    {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            report_llm = json.loads(content)
            if report_llm.get("recommendation"):
                recommendation = report_llm.get("recommendation")
        except Exception as e:
            print(f"[WARNING] Report Generator LLM call failed ({e}). Using fallback recommendation.")

    # ALWAYS return deterministic math score & topics to prevent LLM hallucinations
    return {
        "score": score_pct,
        "strong_areas": strong_unique,
        "weak_areas": weak_unique,
        "recommendation": recommendation
    }
