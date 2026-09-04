"""
Time-Based Lesson Rules Engine (Gaurang's Technical Responsibility)
Encodes explicit structural constraints based on time_minutes (Section 2.5 of Architecture document).
"""

from typing import Dict, Any

TIME_RULES_MAP = {
    5: {
        "max_sections": 1,
        "min_sections": 1,
        "description": "5-Minute Quick Briefing",
        "structure_rule": "1 section max. Only the single most important core concept. No side examples. 1 quick checkpoint question.",
        "quiz_count": 1
    },
    20: {
        "max_sections": 4,
        "min_sections": 3,
        "description": "20-Minute Standard Lesson",
        "structure_rule": "3-4 sections. Core concepts + one relatable real-world example per section. One checkpoint question every 1-2 sections.",
        "quiz_count": 2
    },
    60: {
        "max_sections": 8,
        "min_sections": 6,
        "description": "60-Minute Comprehensive Masterclass",
        "structure_rule": "6-8 sections. Full detailed explanations, multiple examples, 1 checkpoint question per section, ends with a 4-question final quiz.",
        "quiz_count": 4
    },
    10080: { # 7 days in minutes
        "max_sections": 7,
        "min_sections": 7,
        "description": "7-Day Revision & Mastery Plan",
        "structure_rule": "Output a day-by-day revision plan (Day 1 to Day 7) with daily sub-topics, self-check tasks, and text/audio summary briefs.",
        "quiz_count": 7
    }
}

def get_time_rules(time_minutes: int) -> Dict[str, Any]:
    """
    Finds the closest matching structural rule set for a given duration in minutes.
    """
    if time_minutes <= 10:
        return TIME_RULES_MAP[5]
    elif time_minutes <= 35:
        return TIME_RULES_MAP[20]
    elif time_minutes <= 180:
        return TIME_RULES_MAP[60]
    else:
        return TIME_RULES_MAP[10080]
