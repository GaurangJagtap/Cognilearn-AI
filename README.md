# Cognilearn AI (Bharat AI) — Intelligent Adaptive Education Platform

> An AI-powered adaptive learning system that transforms textbook documents, syllabus notes, and raw text into interactive lessons with automated speech narration, dynamic concept graphics, document-adaptive flowcharts, difficulty-tiered quizzes, live performance analytics, learner profile tracking, and active-recall flashcards.

---

## 🌟 Key Features

- 📄 **Document Ingestion & RAG Grounding**: Extract curriculum context automatically from PDF, DOCX, PPTX, and TXT files with chunking (~500 tokens), isolated vector embeddings, and automatic cache reset between uploads.
- 🎓 **Adaptive Lesson Studio**: Generates 4 distinct subtopic modules tailored by learner proficiency (Beginner, Intermediate, Advanced) and language (English, Hindi, Hinglish, regional Indic languages).
- 🌳 **Dynamic Document-Adaptive Flowcharts**:
  - **Concept Taxonomy Map**: Hierarchical taxonomy tree displaying unique concept pillars and extracted technical subnodes tailored to the uploaded material.
  - **Process Pipeline Flowchart**: Multi-phase sequential flow showing operational workflows and technical phases.
  - **Canvas Text-Wrapping**: Crisp, responsive rendering on HTML5 Canvas without text truncation.
- 🎙️ **Audio Narration Player**: Built-in speech synthesis with speed control (`1.0x`–`2.0x`), progress scrubber, and seek controls.
- 📊 **Dynamic Concept Visualizer**: Interactive canvas graphs, equations, circuit loops, and system architectures that adapt dynamically to any subject (Calculus, Electricity, AI, Chemistry, etc.).
- 📝 **Difficulty-Filtered Quiz Engine**: Contextual MCQs categorized into Easy, Medium, and Hard tiers evaluated against ground-truth answers with misconception detection and re-explanations.
- 📈 **Performance Analytics**: Diagnostic scoring, strengths & gap identification, and personalized pedagogical recommendations.
- 👤 **Learner Profile Ledger**: Live tracking of study streaks, completed modules, checkpoint assessments, and concept mastery ledgers in SQLite/Pydantic.
- 🃏 **Interactive Study Tools**: Active recall flashcards deck with 3D flip effects, concept taxonomy maps, and exportable study notes.
- 🎨 **Modern Sky-Blue UI**: Styled with ambient sky-blue mesh gradients, glassmorphism card elevation, and responsive micro-interactions.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.10+, Pydantic, Uvicorn, SQLite
- **AI & RAG Engine**: OpenAI GPT-4o-mini, TF-IDF / Vector Embeddings, Ingestion Parser
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 Design System, Lucide Icons, Canvas API
- **Audio & Media**: Speech Synthesis Engine (Edge-TTS / gTTS / Web Speech API)
- **Testing & Verification**: Pytest, TestClient, Integration Verification Suites

---

## 📂 Project Structure

```text
Bharat AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py                 # FastAPI endpoints (lessons, quizzes, study-tools, etc.)
│   │   ├── core/
│   │   │   ├── chunking.py               # Text chunking and sentence boundary splitter
│   │   │   ├── embeddings.py             # Vector store with clear() reset support
│   │   │   ├── evaluator.py              # Misconception detection & re-explanation engine
│   │   │   ├── ingestion.py              # PDF / DOCX / PPTX / TXT document parsing
│   │   │   ├── language_manager.py       # Indic language detection & mid-lesson translation
│   │   │   ├── learning_path_generator.py # Milestone roadmap builder
│   │   │   ├── lesson_planner.py         # Dynamic 4-pillar lesson & concept generator
│   │   │   ├── report_generator.py       # Performance & gap diagnostic reports
│   │   │   ├── retriever.py              # RAG context retriever with reset support
│   │   │   ├── time_rules.py             # Section duration constraints
│   │   │   └── visual_classifier.py      # Diagram/graph/code/equation/timeline classifier
│   │   ├── db/
│   │   │   └── models.py                 # SQLite/Pydantic models (LearnerProfile, Lessons)
│   │   ├── media/
│   │   │   ├── avatar.py                 # Talking avatar frame renderer
│   │   │   ├── tts.py                    # Multi-provider Text-to-Speech synthesis
│   │   │   ├── video_assembler.py        # Video stitching engine
│   │   │   └── visuals.py                # Concept visual asset generator
│   │   ├── prompts/                      # Specialized LLM system prompts
│   │   ├── config.py                     # Environment variables & system configuration
│   │   ├── main.py                       # FastAPI application & orchestrator pipeline
│   │   ├── test_main.py                  # End-to-end integration test suite
│   │   └── test_steps_6_7.py             # Steps 6 & 7 test suite
│   └── requirements.txt                  # Python dependencies
├── docs/
│   ├── api_comparison.md                 # Evaluation of LLM, TTS & Avatar cloud providers
│   ├── architecture.md                   # Complete system architecture & team ownership
│   ├── contracts.md                      # Inter-module JSON schema contracts
│   ├── demo_script.md                    # Step-by-step hackathon demo walkthrough
│   ├── known_limitations.md              # System boundaries and edge-case handling
│   ├── sample_lesson_plan.json           # Canonical sample lesson plan JSON
│   └── yukta_handover_documentation.md   # Comprehensive handover & technical specification
├── static/
│   ├── index.html                        # Main frontend application markup
│   ├── styles.css                        # Modern CSS styling & glassmorphism theme
│   └── app.js                            # Frontend controller, canvas visualizer & mind-map
├── verify_yukta_handover.py              # Handover verification test runner
├── README.md                             # Project documentation & quick start guide
└── .gitignore                            # Ignored cache, storage & environment files
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed on your system
- Git

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/GaurangJagtap/Cognilearn-AI.git
cd Cognilearn-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Running the Server

#### On Windows (PowerShell):
```powershell
$env:PYTHONPATH="."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### On Linux / macOS:
```bash
export PYTHONPATH="."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started, open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health check and uptime status |
| `POST` | `/api/upload-document` | Upload and parse PDF, DOCX, PPTX, or TXT file |
| `POST` | `/api/generate-lesson-plan` | Generate a 4-section structured curriculum from topic/document |
| `GET` | `/api/current-lesson` | Fetch the currently loaded active lesson plan |
| `POST` | `/api/switch-language` | Switch lesson language mid-session while preserving state |
| `POST` | `/api/evaluate` | Evaluate student answer, diagnose misconceptions, and re-explain |
| `GET` | `/api/study-tools` | Retrieve active-recall flashcards, concept tree, and process flowchart |
| `GET` | `/api/learning-path` | Generate milestone roadmap for subject exploration |
| `GET` | `/api/learner-profile` | Fetch learner streak, mastery score, and checkpoint history |

---

## 🧪 Testing & Verification

Run the comprehensive test suites to verify all technical responsibilities and integration points:

```powershell
# Run Master Orchestrator & End-to-End Pipeline Verification
$env:PYTHONPATH="."
python backend/app/test_main.py

# Run Evaluator & Language/Visual Steps Verification
python backend/app/test_steps_6_7.py

# Run Yukta Handover Verification
python verify_yukta_handover.py
```

---

## 📚 Documentation Links

- [System Architecture Specification](docs/architecture.md)
- [Yukta's Handover & Technical Specification](docs/yukta_handover_documentation.md)
- [Inter-Module JSON Schema Contracts](docs/contracts.md)
- [API Provider Comparison Benchmark](docs/api_comparison.md)
- [Demo Presentation Script](docs/demo_script.md)
- [Known Limitations & Roadmap](docs/known_limitations.md)

---

## 📄 License

Distributed under the MIT License.
