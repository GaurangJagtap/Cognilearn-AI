"""
Learning Path Generator Module (Gaurang's Technical Responsibility)
Generates structured learning roadmaps for broad subjects.
"""

import json
import os
from typing import Dict, Any
from backend.app.db.models import LearningPath, Milestone
from backend.app.prompts.learning_path_prompt import LEARNING_PATH_SYSTEM_PROMPT, build_learning_path_user_prompt
from backend.app.config import settings

def generate_mock_learning_path(topic: str) -> LearningPath:
    """Deterministic fallback learning path generator for offline testing."""
    return LearningPath(
        path_title=f"Learning Path: {topic}",
        milestones=[
            Milestone(id="m1", topic=f"{topic} Fundamentals", status="not_started"),
            Milestone(id="m2", topic=f"{topic} Core Principles", status="not_started"),
            Milestone(id="m3", topic=f"Intermediate {topic}", status="not_started"),
            Milestone(id="m4", topic=f"Advanced Applications of {topic}", status="not_started")
        ]
    )

def generate_learning_path(topic: str) -> LearningPath:
    """
    Primary Learning Path Generator function.
    Calls OpenAI / Gemini LLM if API key is present; falls back to mock generator otherwise.
    """
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            user_prompt = build_learning_path_user_prompt(topic)
            response = client.chat.completions.create(
                model=settings.DEFAULT_LLM_MODEL,
                messages=[
                    {"role": "system", "content": LEARNING_PATH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            path_dict = json.loads(content)
            return LearningPath(**path_dict)
            
        except Exception as e:
            print(f"[WARNING] Learning path LLM call failed ({e}). Using mock generator.")
            return generate_mock_learning_path(topic)
    else:
        return generate_mock_learning_path(topic)
