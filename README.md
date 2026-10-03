# Production GenAI Systems: Architecture & Implementation Suite

An enterprise-grade repository showcasing robust, production-tested Generative AI architectures, multi-provider resiliency patterns, structured data extraction, and deep observability.

Developed and maintained by **[Jagadesh Vuppala](https://github.com/Jagadesh-Vuppala)**.

---

## 🏛️ Systems Portfolio Overview

| System | Architecture Pattern | Key Tech Stack | Production Highlights |
| :--- | :--- | :--- | :--- |
| **[01-Smart-QA-Bot](./01-smart-qa-bot)** | Multi-Provider Resilient Q&A Engine | LangChain, LangSmith, Pydantic v2, GPT-4o-mini, Claude-3-Haiku | Zero-downtime failover, typed structured contracts, full telemetry |
| **[02-AI-Research-Assistant](./02-ai-research-assistant)** | Two-Tier Advanced RAG with Multi-Query & Compression | LangChain, ChromaDB, SQLite, Pydantic v2, GPT-6-Astra, GPT-5.4-mini | High-recall Multi-Query, noise-filtering contextual compression, anti-hallucination contract, persistent SQLite session memory |
| **03-Multi-Agent-Workflows** *(Upcoming)* | Hierarchical Agent Teams with Supervision | LangGraph, Tool Calling, State Checkpointing | Human-in-the-loop, cyclical graph loops |

---

## 🚀 Deep-Dive: System 01 - Smart Q&A Bot

A mission-critical question-answering service engineered to prevent common LLM production failures (provider downtime, unparseable responses, untracked costs).

### 🔍 Architecture Flow

```
[ User Input / CLI / API ]
            │
            ▼
[ ChatPromptTemplate ] ──► System Instructions + Dynamic MessagesPlaceholder (Chat History)
            │ (LCEL `|` Pipe)
            ▼
[ Resilient Model Engine ]
   ├── Primary  : OpenAI (gpt-4o-mini)
   └── Fallback : Anthropic (claude-3-haiku) via .with_fallbacks()
            │
            ▼
[ Pydantic v2 Schema Contract ] ──► QAResponse(answer, confidence, reasoning, follow_up_questions, sources_needed)
            │
            ├──► [ Graceful Safety Shield ]: Catches exceptions without crashing, returns typed degraded state
            └──► [ LangSmith Telemetry ]: Traces latency (ms), token consumption, and root-cause analysis
```

### ⚡ Key Architectural Patterns Implemented

1. **Multi-Provider Failover:**
   Configured cross-cloud redundancy (`OpenAI` ➔ `Anthropic`). If OpenAI experiences rate-limits (HTTP 429) or service outages (HTTP 500/503), the engine automatically reroutes the request to Claude without dropping the request.

2. **Strict Typed Contracts (Pydantic v2):**
   Eliminates unstructured text parsing issues by guaranteeing typed objects with strict validation constraints (`ge=0.0, le=1.0`).

3. **Enterprise Observability (LangSmith):**
   Integrated telemetry via `@traceable` decorators and runtime hooks to record latency trees, token usage (input vs. output breakdown), and pricing telemetry.

4. **Conversational State Retention:**
   Employs `MessagesPlaceholder` for clean multi-turn state injection while keeping core templates immutable.

---

## 🛠️ Quickstart & Local Setup

Ensure you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# Clone the repository
git clone https://github.com/Jagadesh-Vuppala/production-genai-systems.git
cd production-genai-systems/01-smart-qa-bot

# Configure environment variables
cp .env.example .env
# Add your OPENAI_API_KEY, ANTHROPIC_API_KEY, and LANGCHAIN_API_KEY to .env

# Install dependencies and sync virtualenv
uv sync

# Run the interactive CLI bot
uv run python smart_bot_section_1.py
```

---

## 👤 Author
**Jagadesh Vuppala**  
*Senior Generative AI & LLM Systems Engineer*  
*GitHub:* [@Jagadesh-Vuppala](https://github.com/Jagadesh-Vuppala)
