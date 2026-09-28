# Project 01: Smart Q&A Bot (Production-Grade)

A production-ready question-answering system built with LangChain (LCEL), Pydantic structured output, graceful error degradation, and LangSmith observability.

## 🎯 Architecture
```
[User Question]
       │
       ▼
[ChatPromptTemplate] (System guidelines + Human question)
       │ (LCEL `|` Pipe)
       ▼
[ChatOpenAI (gpt-4o-mini)]
       │ (with_structured_output)
       ▼
[QAResponse Schema] ──► { answer, confidence, reasoning, follow_up_questions, sources_needed }
       │
       ├──► [Graceful Shield]: Try/Except fallback (returns degraded response on failure)
       └──► [LangSmith Tracing]: Intercepts metrics (latency, token costs, runs)
```

## 📦 Setup & Execution
1. Ensure `.env` contains your `OPENAI_API_KEY` and optionally `LANGCHAIN_API_KEY`.
2. Run with dedicated project environment:
   ```bash
   uv run python main.py
   ```
