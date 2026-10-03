# Project 02: AI Research Assistant (Production Two-Tier RAG)

A production-grade Academic & Technical Research Assistant featuring a Two-Tier Model Routing Architecture, Multi-Query Recall Expansion, Contextual Compression, SQLite Persistent Session Memory, and Strict Pydantic Verification Contracts with Anti-Hallucination Guardrails.

---

## 1. System Architecture

`	ext
[ User Research Query ]
          |
          v
[ Tier 1: Multi-Query Retriever (gpt-5.4-mini) ] ---> Expands into 3 academic query variations (High Recall)
          |
          v
[ Chroma Vector Store ] ---------------------------> Retrieves top-k candidate chunks (1000 chars, 200 overlap)
          |
          v
[ Tier 1: Contextual Compressor (gpt-5.4-mini) ] ---> Strips 80% fluff/noise, preserves pure formulas/facts (High Precision)
          |
          v
[ SQLite Persistent Memory (research_vault.db) ] ---> Reads/Writes multi-turn session history via SQLChatMessageHistory
          |
          v
[ Tier 2: Frontier Thinker (gpt-6-astra) ] --------> Synthesizes answer under anti-hallucination guardrails
          |
          v
[ Structured Output: ResearchResponse ] -----------> Strict JSON contract:
                                                      * answer: str
                                                      * sources: List[str]
                                                      * confidence: float (0.0 to 1.0)
                                                      * suggestions: List[str]
`

---

## 2. Key Engineering Highlights

1. **Two-Tier Model Routing (Cost & Precision Optimization)**:
   - **Cleaner / Extractor Tier (gpt-5.4-mini-2026-03-17)**: High throughput, zero latency, free tier eligible. Eliminates token waste before feeding into the frontier model.
   - **Frontier Thinker Tier (gpt-6-astra)**: State-of-the-art reasoning for complex mathematical proofs, deep synthesis, and verified structured outputs.
2. **Academic Chunking Strategy**:
   - chunk_size=1000 with chunk_overlap=200 to preserve mathematical proofs and equations without boundary truncation.
3. **Anti-Hallucination Guardrail Contract**:
   - Explicit prompt constraint forcing confidence=0.0 and empty sources=[] when facts are not grounded in source context.
4. **Persistent Session Memory**:
   - Backed by SQLite (SQLChatMessageHistory), isolating user sessions and surviving process restarts and server outages.

---

## 3. Setup & Execution

1. Configure your .env file in the root directory:
   `ash
   OPENAI_API_KEY=your_openai_api_key_here
   `

2. Run the research assistant:
   `ash
   python app.py
   `
