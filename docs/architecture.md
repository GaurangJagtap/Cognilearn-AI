# AI Teacher - Complete System Architecture

**Author & Technical Lead:** Gaurang  
**Team Members:** Gaurang, Yukta, Siddhant, Harsh  

---

## 1. Executive Summary & Problem Statement

Standard AI education tools often output overwhelming walls of text or static videos. The **AI Teacher** platform bridges human-like personalized instruction and dynamic media generation by building a structured, time-constrained lesson planner backed by RAG knowledge grounding, text-to-speech, talking avatar generation, interactive checkpoint questions, and long-term learner profile memory.

---

## 2. High-Level System Flow

```
[User Input: Topic / Document Upload]
                |
                v
        +---------------+
        | Ingestion     |  Extracts raw text from PDF/DOCX/PPTX
        +-------+-------+
                |
                v
        +---------------+
        | RAG Engine    |  Chunk (~500 tokens), embed, store in Vector DB, retrieve top-k chunks
        +-------+-------+
                |
                v
        +---------------+
        | Time Rules    |  Enforces 5-min (1 section), 20-min (3-4 sections), 60-min (6-8 sections)
        +-------+-------+
                |
                v
        +---------------+
        | Lesson        |  Generates strict JSON Lesson Plan obeying level, language & memory
        | Planner       |  
        +-------+-------+
                |
                v
        +---------------+
        | Media         |  Visual Classifier -> TTS -> Avatar -> Video Assembler (Stitched MP4)
        | Pipeline      |
        +-------+-------+
                |
                v
        +---------------+
        | Interaction   |  Checkpoint questions -> Evaluator (Misconception Detection & Re-explanation)
        | & Assessment  |  Final Quiz -> Performance Report -> SQLite LearnerProfile Persistence
        +---------------+
```

---

## 3. Core Component Breakdown & Ownership

| Component | Responsible Teammate | Key Files | Description |
|---|---|---|---|
| **Lesson Planner & Brain** | Gaurang | `core/lesson_planner.py`, `prompts/lesson_plan_prompt.py` | LLM call generating structured lesson JSON (20% score weight). |
| **RAG Knowledge Pipeline** | Gaurang | `core/retriever.py`, `embeddings.py`, `chunking.py` | Grounding explanations in uploaded document chunks (15% score weight). |
| **Time-Based Lesson Rules** | Gaurang | `core/time_rules.py` | Deterministic structural rules per lesson duration. |
| **Learning Path Generator** | Gaurang | `core/learning_path_generator.py` | Roadmap generator for broad subjects. |
| **Master Orchestrator** | Gaurang | `main.py` | Assembly line connecting all team modules. |
| **Language Manager & Visuals Classifier** | Yukta | `core/language_manager.py`, `visual_classifier.py` | Language detection/switching & visual representation type classification. |
| **Media & Video Pipeline** | Siddhant | `media/tts.py`, `avatar.py`, `visuals.py`, `video_assembler.py` | TTS narration, talking avatar rendering, slide asset generation, MP4 stitching. |
| **Evaluator & Frontend App** | Harsh | `core/evaluator.py`, `report_generator.py`, `frontend/` | Misconception detection, quiz report generator, FastAPI endpoints & React UI. |
