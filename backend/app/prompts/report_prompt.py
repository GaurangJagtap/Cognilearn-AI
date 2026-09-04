"""
Report Generator Prompt Engineering (Step 7 - Quiz Assessment & Learning Report)
Builds prompt for converting final quiz results into comprehensive learning reports.
"""

REPORT_SYSTEM_PROMPT = """You are an educational assessment AI.
Analyse the student's final quiz performance and generate a structured performance report in JSON format.

CRITICAL INSTRUCTIONS:
1. OUTPUT ONLY VALID JSON. Do not include markdown code block ticks.

JSON SCHEMA:
{
  "score": <int percentage 0-100>,
  "strong_areas": ["<topic1>", "<topic2>"],
  "weak_areas": ["<topic1>", "<topic2>"],
  "recommendation": "<detailed actionable study recommendation>"
}
"""

def build_report_user_prompt(quiz_results: list) -> str:
    return f"""QUIZ RESULTS LOG:
{quiz_results}

Analyze this performance log and output the valid JSON report now:"""
