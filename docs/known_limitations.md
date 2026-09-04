# AI Teacher - Known Limitations & Transparency Document

**Author:** Gaurang (Main Planner & Technical Lead)  

In accordance with hackathon submission guidelines, the following known limitations and architectural trade-offs are documented for full transparency:

1. **Adaptive Re-Explanation Latency Trade-Off**:
   - During the interactive checkpoint loop, when a student answers incorrectly, adaptive re-explanations generate fast text and TTS audio rather than re-rendering the full talking-head avatar video in real-time. This minimizes student wait time from 30+ seconds to under 2 seconds.
2. **Local Vector Database Scale**:
   - The RAG pipeline uses an in-memory/SQLite vector store optimized for quick hackathon deployment on individual textbook chapters (~50-100 pages). For enterprise multi-gigabyte document libraries, a remote vector cluster (e.g. Pinecone/Weaviate) can be plugged in seamlessly.
3. **Avatar Processing API Rate Limits**:
   - In offline development mode, the orchestrator uses deterministic video stubs to allow offline integration testing without incurring API latency or rate limits.
