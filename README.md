# Cognilearn AI — Intelligent Adaptive Education Platform

> An AI-powered adaptive learning system that transforms textbook documents, syllabus notes, and raw text into interactive lessons with automated speech narration, dynamic concept graphics, difficulty-level quizzes, live performance analytics, learner profile tracking, and active-recall flashcards.

---

## 🌟 Key Features

- 📄 **Document Ingestion & Parsing**: Extract curriculum context automatically from PDF, DOCX, PPTX, and TXT files.
- 🎓 **Adaptive Lesson Studio**: Generates 4 distinct subtopic modules tailored by learner proficiency (Beginner, Intermediate, Advanced) and language (English, Hindi, Hinglish).
- 🎙️ **Audio Narration Player**: Built-in speech synthesis with speed control (`1.0x`–`2.0x`), progress scrubber, and seek controls.
- 📊 **Dynamic Concept Visualizer**: Interactive canvas graphs and formula visualizers that adapt dynamically to any subject (Calculus, Electricity, AI, Chemistry, etc.).
- 📝 **Difficulty-Filtered Quiz Engine**: Contextual MCQs categorized into Easy, Medium, and Hard tiers evaluated against ground-truth answers.
- 📈 **Performance Analytics**: Diagnostic scoring, strengths & gap identification, and personalized pedagogical recommendations.
- 👤 **Learner Profile Ledger**: Live tracking of study streaks, completed modules, and concept mastery ledgers for authenticated and guest users.
- 🃏 **Interactive Study Tools**: Active recall flashcards deck with 3D flip effects, concept taxonomy maps, and exportable study notes.
- 🎨 **Modern Light Blue UI**: Styled with ambient sky-blue mesh gradients, glassmorphism card elevation, and responsive micro-interactions.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.12, Pydantic, Uvicorn, SQLite
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (CDN), Lucide Icons, Chart.js
- **Audio & Media**: Speech Synthesis Engine, Canvas API
- **Testing**: Pytest & Integration Test Suite

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed on system

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/GaurangJagtap/Cognilearn-AI.git
cd Cognilearn-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt  # Or pip install fastapi uvicorn sqlite3
```

### 3. Running the Application
```bash
# Launch FastAPI Backend Server
python -m backend.app.main
```
Open your browser and navigate to **`http://localhost:8000`**.

---

## 📄 License
Distributed under the MIT License.
