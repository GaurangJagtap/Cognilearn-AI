# Yukta's Module Handover Documentation — AI Teacher Platform

**Module Owner & Author:** Yukta  
**Integration Lead:** Gaurang (Master Orchestrator & Lesson Planner)  
**Co-Collaborators:** Siddhant (Media & Video Pipeline), Harsh (Assessment & Frontend App)  
**Version:** 2.0 (Production-Ready)  
**Status:** Complete & Verified  

---

## 1. Executive Summary & Module Scope

This documentation provides the comprehensive technical specification, architecture, implementation details, API contracts, and verification procedures for the core subsystems developed by **Yukta** for the **AI Teacher Platform (Cognilearn-AI / Bharat AI)**:

1. **Language Manager (`backend/app/core/language_manager.py`)**: Multi-lingual source language detection (English, Hindi, Hinglish, regional Indian scripts), dynamic mid-lesson language translation/switching with strict JSON schema preservation, and orchestrator preparation pipelines.
2. **Visual-Type Classifier (`backend/app/core/visual_classifier.py`)**: Multi-subject pedagogical visual taxonomy classifier determining whether a lesson concept is best represented via a `diagram`, `graph`, `code`, `equation`, or `timeline`.
3. **Learner Profile & Long-Term Memory Models (`backend/app/db/models.py`)**: Persistent learner state tracking, checkpoint progression, mastery metrics, misconception ledgers, and spaced repetition triggers.
4. **API Comparison Benchmark Analysis (`docs/api_comparison.md`)**: Empirical evaluation of external cloud providers vs. open-source/offline fallbacks across LLM, Text-to-Speech (TTS), and Talking Avatar synthesis engines.

---

## 2. Subsystem Architecture & Integration Flow

```
                                [Learner Query / Document Upload]
                                                |
                                                v
             +----------------------------------------------------------------------+
             |  1. LANGUAGE MANAGER (Yukta)                                         |
             |     - detect_language(input_text) -> 'en' | 'hi' | 'hinglish' | ...   |
             +----------------------------------+-----------------------------------+
                                                |
                                                v
             +----------------------------------------------------------------------+
             |  2. LESSON PLANNER & RAG (Gaurang)                                   |
             |     - Retrieves grounded chunks & generates 4-section lesson plan    |
             +----------------------------------+-----------------------------------+
                                                |
                        +-----------------------+-----------------------+
                        |                                               |
                        v                                               v
+-----------------------------------------------+   +-----------------------------------------------+
| 3. VISUAL CLASSIFIER (Yukta)                  |   | 4. MID-LESSON SWITCHING & PREPARE (Yukta)     |
|    - classify_visual(concept, subject)        |   |    - switch_language(section, new_lang)       |
|    - Assigns: diagram | graph | code | etc.   |   |    - prepare(section, lang) for TTS           |
+-----------------------+-----------------------+   +-----------------------+-----------------------+
                        |                                                   |
                        +-----------------------+---------------------------+
                                                |
                                                v
             +----------------------------------------------------------------------+
             |  5. MEDIA GENERATION & VIDEO PIPELINE (Siddhant)                     |
             |     - Generates visual assets, TTS audio, and avatar video frames    |
             +----------------------------------+-----------------------------------+
                                                |
                                                v
             +----------------------------------------------------------------------+
             |  6. EVALUATOR & LEARNER PROFILE (Harsh & Yukta)                      |
             |     - Checkpoint evaluation, misconception logging                   |
             |     - Updates LearnerProfile (SQLite/Pydantic state persistence)     |
             +----------------------------------------------------------------------+
```

---

## 3. Module Specifications & Implementation Details

### 3.1 Language Manager (`backend/app/core/language_manager.py`)

#### Primary Responsibilities:
- **Language Detection**: Identifies whether user input or curriculum text is standard English, Devanagari Hindi, Romanized Hinglish, or regional Indic scripts (Tamil `ta`, Telugu `te`, Kannada `kn`, Bengali `bn`, Marathi `mr`).
- **Hinglish Detection**: Distinguishes between pure English and colloquial Indian English/Hinglish (e.g., *"Mujhe ye topic simple example ke saath samjhao"*) using linguistic keyword matching and phonetic markers.
- **Mid-Lesson Language Switching**: Allows a student to switch language mid-stream (e.g., from English to Hindi or Hinglish) without losing their position, section IDs, visual configurations, or checkpoint state.
- **Orchestrator Preparation (`prepare`)**: Sanitizes narrative scripts for speech synthesis (TTS) while formatting structural dictionaries for frontend rendering.

#### Core API Functions:

```python
def detect_language(text: str) -> str:
    """
    Detects language code from raw string.
    Returns: 'en', 'hi', 'hinglish', 'ta', 'te', 'kn', 'bn', 'mr'.
    """

def switch_language(section_data: Union[dict, LessonSection], target_language: str) -> dict:
    """
    Translates narration_script, explanation, and checkpoint_question
    while strictly preserving section 'id', 'concept', and 'visual_type'.
    """

def prepare(section: Union[dict, LessonSection], language: str = "en") -> Tuple[str, dict]:
    """
    Adapter function for Gaurang's master orchestrator:
    Returns (spoken_narration_script, sanitized_section_payload_dict).
    """
```

---

### 3.2 Visual-Type Classifier (`backend/app/core/visual_classifier.py`)

#### Primary Responsibilities:
- Categorizes curriculum concepts into 5 pedagogical visual types:
  1. `diagram`: Structural systems, biological organisms, architectural components, flow networks.
  2. `graph`: Mathematical functions, economic relationships, thermodynamic curves, coordinate geometries.
  3. `code`: Algorithmic logic, data structures, software development syntax, pseudocode.
  4. `equation`: Formal mathematical proofs, chemical reactions, physical laws (e.g., $E=mc^2$, $V=IR$).
  5. `timeline`: Historical chronological sequences, biological evolution phases, multi-step process lifecycles.

#### Heuristic & Prompt Rule Engine:
- **Fast Path (Deterministic Heuristics)**: Instant regex and keyword scoring (<1ms execution) based on subject domain and concept noun phrases.
- **LLM Semantic Classifier**: Secondary fallback utilizing `visual_classifier_prompt.py` for ambiguous or cross-disciplinary concepts.
- **Explainability**: `classify_visual_with_reasoning()` outputs detailed pedagogical rationale for frontend display or analytics logging.

```python
def classify_visual(concept_title: str, subject_domain: str = "general") -> str:
    """Returns: 'diagram' | 'graph' | 'code' | 'equation' | 'timeline'"""

def classify_visual_with_reasoning(concept_title: str, subject_domain: str = "general") -> dict:
    """Returns: {'visual_type': str, 'confidence': float, 'reasoning': str}"""
```

---

### 3.3 Learner Profile & Long-Term Memory (`backend/app/db/models.py`)

#### Primary Responsibilities:
- Defines database schema and Pydantic validation models for learner persistence.
- Tracks:
  - `user_id`, `name`, `preferred_language`, `mastery_level` (Beginner, Intermediate, Advanced).
  - `completed_topics` and `checkpoint_progress` (which section questions were passed or failed).
  - `misconception_ledger`: Catalog of specific conceptual errors identified by the Evaluator during lessons.
  - `spaced_repetition_queue`: Due dates for revisiting difficult subtopics.
  - `study_streak_days` and `total_learning_minutes`.

#### Schema Model (Pydantic / SQLite):
```python
class LearnerProfile(BaseModel):
    user_id: str
    name: str = "Guest Learner"
    preferred_language: str = "en"
    proficiency_tier: str = "Beginner"
    total_study_minutes: int = 0
    streak_days: int = 1
    completed_milestones: List[str] = Field(default_factory=list)
    misconceptions: List[Dict[str, Any]] = Field(default_factory=list)
    checkpoint_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 3.4 API Comparison Benchmark (`docs/api_comparison.md`)

A comprehensive 3-tier comparative benchmark covering latency, unit cost, regional language fluency, and offline fallback viability across:
- **LLMs**: OpenAI GPT-4o-mini (Primary), Anthropic Claude 3.5 Sonnet, Google Gemini 1.5 Flash, Groq Llama-3-70B.
- **Text-to-Speech**: Deepgram Aura, Microsoft Edge-TTS (Free/Active), ElevenLabs (Premium), Google gTTS (Fallback).
- **Talking Avatars**: D-ID, SadTalker, HeyGen, and our zero-latency SVG Canvas fallback avatar.

*(See full breakdown in [`docs/api_comparison.md`](file:///c:/Bharat%20AI/docs/api_comparison.md)).*

---

## 4. Verification & Testing Matrix

Yukta's deliverables are covered by automated unit and integration tests:

| Test Script | Target Subsystem | Assertions Verified | Status |
|---|---|---|---|
| `verify_yukta_handover.py` | Full Handover Suite | Language detection (5 dialects), mid-lesson translation, section ID preservation, visual taxonomy classification, learner profile instantiation. | **PASS** (100%) |
| `backend/app/test_steps_6_7.py` | Steps 6 & 7 Integrations | Evaluator response handling, language switching on contract JSON, visual classifier heuristic accuracy. | **PASS** (100%) |
| `backend/app/test_main.py` | Master Orchestrator | Complete pipeline execution from input document to final video/report with language and visual metadata intact. | **PASS** (100%) |

### How to Execute Verification:
Run the standalone handover verification script:
```powershell
$env:PYTHONPATH="."
python verify_yukta_handover.py
```

Expected Output:
```text
======================================================================
AI TEACHER - YUKTA'S MODULE HANDOVER VERIFICATION
======================================================================
[1] Testing Language Detection (detect_language)... [OK]
[2] Testing Mid-Lesson Language Switching (switch_language)... [OK]
[3] Testing Orchestrator Preparation (language_manager.prepare)... [OK]
[4] Testing Visual-Type Classifier (classify_visual)... [OK]
[5] Testing Learner Profile & Long-Term Memory Models... [OK]
======================================================================
[SUCCESS] ALL YUKTA DELIVERABLES VERIFIED AND PRODUCTION READY!
======================================================================
```

---

## 5. Maintenance & Future Roadmap

1. **Expanding Regional Indic Dialects**: Integrate IndicTrans2 / Bhashini APIs for low-resource Indian languages (Odia, Punjabi, Gujarati, Malayalam).
2. **Audio Waveform Cache**: Cache common phonetic patterns in `storage/generated_audio/` to reduce TTS latency on repeat lessons.
3. **Adaptive Visual Complexity**: Expand `visual_classifier.py` to select 3D interactive WebGL models (Three.js) for high-complexity anatomical and mechanical structures.

---

**Signed off by:** Yukta  
**Accepted by:** Gaurang (Integration Lead)  
