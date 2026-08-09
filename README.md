# Production AI Incident & Knowledge Copilot

A 14-day, local-first AI engineering capstone designed to build real implementation knowledge for AI Engineer interviews.

## Core goal

Build a production-style AI copilot that can investigate technical incidents using internal documents, logs, structured data and tools, then return grounded answers with citations and safe action recommendations.

The project deliberately grows from a tiny local LLM call into:

- LLM prompting and structured output
- embeddings and semantic retrieval
- RAG
- PostgreSQL + pgvector
- BM25 + hybrid retrieval + reranking
- evaluation
- tool calling and agents
- LangGraph workflows
- state, memory, guardrails and human approval
- a small classical ML classifier
- LoRA/QLoRA fine-tuning
- FastAPI
- Redis
- Kafka
- Docker Compose
- observability
- basic Kubernetes
- CI/CD and load testing
- production system-design tradeoffs

## Source of truth

Never rely on chat history alone.

1. `docs/MASTER_PLAN.md` — complete syllabus and definition of done.
2. `docs/PROJECT_STATE.md` — exact current progress and next step.
3. `docs/DECISIONS.md` — architecture decisions and tradeoffs.
4. Git history — actual code state.

## Start here

Before every learning session, read:

1. `docs/START_HERE.md`
2. `docs/PROJECT_STATE.md`

Then follow the exact session protocol.
