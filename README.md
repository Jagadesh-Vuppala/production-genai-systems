# Production GenAI Systems: Architecture & Implementation Suite

An enterprise-grade repository showcasing robust, production-tested Generative AI architectures, multi-provider resiliency patterns, two-tier advanced RAG systems, and autonomous multi-agent stateful graph workflows.

Developed and maintained by **[Jagadesh Vuppala](https://github.com/Jagadesh-Vuppala)**.

---

## ??? Systems Portfolio Overview

| System | Architecture Pattern | Key Tech Stack | Production Highlights |
| :--- | :--- | :--- | :--- |
| **[01-Smart-QA-Bot](./01-smart-qa-bot)** | Multi-Provider Resilient Q&A Engine | LangChain, LangSmith, Pydantic v2, GPT-4o-mini, Claude-3-Haiku | Zero-downtime cross-cloud failover, typed structured contracts, full latency & token telemetry |
| **[02-AI-Research-Assistant](./02-ai-research-assistant)** | Two-Tier Advanced RAG with Compression | LangChain, ChromaDB, SQLite, Pydantic v2, GPT-6-Astra, GPT-5.4-mini | High-recall Multi-Query, noise-filtering contextual compression, anti-hallucination contract, persistent SQLite session memory |
| **[03-Autonomous-Financial-Advisor](./03-autonomous-financial-advisor)** | Autonomous Multi-Agent CFP Wealth System | LangGraph, Pydantic v2, DuckDuckGo Live Search, GPT-6-Astra, GPT-5.4-mini | Symmetric 1-hop fan-out/fan-in, self-healing dynamic guardrails, deterministic cashflow balancing, closed-loop QC audit loop |

---

## ?? Architectural Deep-Dives

### System 01: Smart Q&A Bot (Resilient Multi-Provider Engine)
A mission-critical question-answering service engineered to prevent common LLM production failures (provider downtime, unparseable responses, untracked costs).

`	ext
[ User Input ] --? [ ChatPromptTemplate ] --? [ Resilient Model Engine ]
                                                +-- Primary  : OpenAI (gpt-4o-mini)
                                                +-- Fallback : Anthropic (claude-3-haiku)
                                                           ¦
                                                           ?
                                              [ Pydantic v2 Typed Contract ]
                                              (Strict validation, graceful shields, LangSmith tracing)
`
- **Cross-Cloud Zero Downtime**: Automated failover from OpenAI to Anthropic during HTTP 429 rate-limits or 5xx outages via .with_fallbacks().
- **Strict Typed Validation**: Guarantees typed Pydantic v2 output objects with validation constraints (ge=0.0, le=1.0).
- **Telemetry & Traceability**: Full LangSmith observability tracking latency trees, token consumption, and cost telemetry.

---

### System 02: AI Research Assistant (Two-Tier Production RAG)
An academic & technical research engine solving semantic search limitations through intelligent query expansion, token noise filtering, and persistent state.

`	ext
[ Research Query ] --? [ Tier 1: Multi-Query Expander ] --? [ Chroma Vector Store ]
                                                                      ¦
                                                                      ?
[ Tier 2: Frontier Thinker ] ?-- [ SQLite Memory Vault ] ?-- [ Tier 1: Contextual Compressor ]
  (gpt-6-astra synthesis)         (Persistent sessions)          (Strips 80% fluff/noise)
`
- **High-Recall Multi-Query Expansion**: Generates 3 academic query reformulations to bridge lexical vocabulary gaps.
- **Contextual Token Compression**: Uses high-speed Tier 1 LLM to strip 80% irrelevant fluff, feeding only pure formulas and verified facts to the synthesis model.
- **Persistent SQLite Vault**: Multi-turn conversation retention across restarts via SQLChatMessageHistory.

---

### System 03: Autonomous Financial Advisor (CFP Multi-Agent System)
A Certified Financial Planner (CFP) grade autonomous committee orchestrating live web research, deterministic cashflow math, and self-correcting compliance auditing.

`	ext
[ START ] --? [ Supervisor Node ] --? [ Insurance Specialist ]
                                                ¦
                       +-------------------------------------------------+
                       ? (Symmetric Fan-Out)                             ? (Symmetric Fan-Out)
             [ Investment Specialist ]                         [ Tax Specialist ]
             (Multi-Asset Allocation)                          (2026 Slab & 87A Optimization)
                       ¦                                                 ¦
                       +-------------------------------------------------+
                                                ? (Symmetric Fan-In)
                                       [ Synthesizer Node ]
                                                ¦
                                                ?
                                       [ QC Auditor Node ] --? (Score >= 7) --? [ Approved Blueprint ]
                                                ¦
                                                +--? (Score < 7) --? Rejection Loop back to Supervisor
`
- **Symmetric 1-Hop Fan-Out / Fan-In**: Eliminates asynchronous superstep race conditions (InvalidUpdateError) by enforcing uniform hop distances between concurrent specialists.
- **Autonomous Cover Sizing & Live Pricing**: Derives term and health coverage dynamically from salary (10x–15x rule) and budget constraints via live web search.
- **Self-Healing Guardrails**: Code-level self-healing ensures non-zero premiums and deterministic accounting: Needs + Wants + Debt + Insurance + Investments == Total Salary.
- **Closed-Loop Audit Gate**: Evaluates plan compliance and enforces iterative refinement if mathematical balance or policy clarity fails.

---

## ??? Repository Navigation & Quickstart

Each system is completely self-contained with dedicated code, dependencies, and documentation:

`ash
# System 01: Smart Q&A Bot
cd 01-smart-qa-bot && pip install -r requirements.txt && python smart_bot_section_1.py

# System 02: AI Research Assistant
cd 02-ai-research-assistant && pip install -r requirements.txt && python app.py

# System 03: Autonomous Financial Advisor
cd 03-autonomous-financial-advisor && pip install -r requirements.txt && python main.py
`

---

## ????? Author & Maintainer
**Jagadesh Vuppala**  
*Senior Generative AI & LLM Systems Engineer*  
*GitHub:* [@Jagadesh-Vuppala](https://github.com/Jagadesh-Vuppala)
