"""
Lesson Planner Prompt Engineering (Gaurang's Technical Responsibility)
Builds strict system & user prompts for generating structured Lesson Plan JSON.
"""

LESSON_PLANNER_SYSTEM_PROMPT = """You are an expert AI Master Teacher. 
Your goal is to take educational content or topics and transform them into a highly engaging, structured, and pedagogical lesson plan in JSON format.

CRITICAL INSTRUCTIONS:
1. OUTPUT ONLY VALID JSON. Do not include markdown code block ticks ```json or any introductory text.
2. Follow the requested JSON schema strictly.
3. Apply the human-like teaching principles:
   - Use clear, conversational language in the narration script.
   - Match the target language requested (e.g. 'hi' for Hindi, 'hinglish' for Hinglish, 'en' for English).
   - Tailor explanations to the student's level (e.g., beginner, intermediate, advanced).
   - Emphasize weak concepts from the student's history if provided.
4. Adhere strictly to the requested time-based section constraints.

JSON SCHEMA REQUIREMENT:
{
  "title": "<string>",
  "level": "<string>",
  "time_minutes": <int>,
  "language": "<string>",
  "topic_or_chapter": "<string>",
  "sections": [
    {
      "id": "s1",
      "concept": "<concept title>",
      "explanation": "<clear explanation>",
      "example": "<relatable real-world example>",
      "visual_type": "<diagram | graph | code | timeline | equation>",
      "visual_details": {
        "diagram_type": "<flowchart | concept_map | process | graph | equation>",
        "title": "<diagram header>",
        "nodes": [
          {"id": "n1", "label": "<component or step name>", "category": "<input | process | output | key>", "description": "<short description>"}
        ],
        "edges": [
          {"from": "n1", "to": "n2", "label": "<relationship or flow label>"}
        ],
        "key_formula": "<formula or key takeaway if applicable>"
      },
      "narration_script": "<engaging, conversational spoken narration script>",
      "checkpoint_question": {
        "type": "mcq",
        "question": "<question string>",
        "options": ["<option1>", "<option2>", "<option3>", "<option4>"],
        "correct": "<exact correct option text>"
      }
    }
  ],
  "final_quiz": [
    {
      "id": "q1",
      "question": "<quiz question>",
      "options": ["<opt1>", "<opt2>", "<opt3>", "<opt4>"],
      "correct": "<correct opt>"
    }
  ]
}
"""

def build_user_prompt(
    topic: str,
    level: str,
    time_minutes: int,
    language: str,
    retrieved_context: str = "",
    weak_concepts: list = None,
    strong_concepts: list = None,
    structure_rule: str = ""
) -> str:
    weak_concepts = weak_concepts or []
    strong_concepts = strong_concepts or []
    
    prompt = f"""Generate a structured Lesson Plan for the following topic:

TOPIC/CHAPTER: {topic}
TARGET LEARNER LEVEL: {level}
DURATION: {time_minutes} minutes
TARGET TEACHING LANGUAGE: {language}

STRUCTURAL CONSTRAINT RULE:
{structure_rule}

STUDENT PROFILE CONTEXT:
- Weak concepts to give extra attention/analogies: {', '.join(weak_concepts) if weak_concepts else 'None'}
- Strong concepts already mastered: {', '.join(strong_concepts) if strong_concepts else 'None'}
"""

    if retrieved_context.strip():
        prompt += f"\nGROUNDING KNOWLEDGE CONTEXT (RAG Material):\n{retrieved_context}\n"
    else:
        prompt += "\nUse your general domain knowledge to construct a comprehensive lesson.\n"

    prompt += "\nOutput the complete valid JSON payload now:"
    return prompt
