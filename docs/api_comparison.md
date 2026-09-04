# API & Third-Party Service Evaluation (Yukta's Research Deliverable)

**Author:** Yukta (Research Lead & Technical Support)  
**Target Document:** Submission Documentation - "APIs and Third-Party Services" Section  

---

## 1. LLM Provider Benchmark & Selection

| Provider | Model | Latency (p95) | Cost ($ / 1M tokens) | Language Coverage | Decision & Rationale |
|---|---|---|---|---|---|
| **OpenAI** | `gpt-4o` | ~1.2s | $2.50 / $10.00 | Excellent (Multilingual + Hinglish) | **PRIMARY CHOICE** - Strongest JSON adherence & code-switching capability for Hinglish narration scripts. |
| **Google** | `gemini-1.5-pro` | ~1.5s | $1.25 / $5.00 | Strong Indian Languages | **ALTERNATIVE** - Selected as secondary fallback due to cost efficiency and large context window. |
| **Anthropic** | `claude-3-5-sonnet` | ~1.8s | $3.00 / $15.00 | High Quality | Considered for prompt tuning evaluations. |

---

## 2. Text-To-Speech (TTS) Provider Evaluation

| Provider | Voice Naturalness | Indian Language Coverage | Latency | Pricing | Selection |
|---|---|---|---|---|---|
| **ElevenLabs** | 9.8 / 10 | Multilingual (v2 Turbo model) | ~800ms | $0.18 / 1k chars | **PRIMARY (Best Quality)** - Outstanding conversational voice quality for avatar video sync. |
| **Azure Speech** | 8.9 / 10 | 12+ Indian Languages (Hindi, Marathi, Tamil, etc.) | ~300ms | $0.016 / 1k chars | **SECONDARY (Best Language Coverage)** - Excellent Indian regional accent models. |

---

## 3. Talking Avatar Video Generation API Evaluation

| Provider | Lip-Sync Accuracy | API Rendering Speed | Cost Per Video Minute | Selection |
|---|---|---|---|---|
| **D-ID API** | High (HD Talking Head) | ~15-20s rendering | ~$0.10 / clip | **PRIMARY CHOICE** - Fast REST API integration for per-section avatar video generation. |
| **HeyGen API** | Very High | ~25-35s rendering | ~$0.25 / clip | Secondary alternative for high-fidelity avatar rendering. |
