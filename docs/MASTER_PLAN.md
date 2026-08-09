# MASTER PLAN — 14-Day AI Engineer Capstone

## Project

**Production AI Incident & Knowledge Copilot**

## Schedule

Planned learning sprint: **August 11–24, 2026**.

Weekdays target: ~1–2 hours.  
Weekend target: ~3–4 hours.

The MVP should be functionally complete by roughly Day 10. Days 11–14 make it production-style and interview-defensible.

---

# Non-negotiable learning philosophy

For important concepts:

**understand -> implement -> run -> break -> measure -> trade off -> explain**

Do not optimize for maximum code volume. Optimize for maximum interview-defensible understanding.

Boilerplate may be provided directly. Conceptual code should be written or completed by the learner when reasonable.

---

# Day 0 — Environment and project control plane

**Date:** Aug 10  
**Goal:** Make future sessions reproducible and impossible to lose.

Checklist:

- [x] Local repository created
- [x] Git initialized
- [~] GitHub remote created; first push pending
- [x] IDE opens repository (PyCharm)
- [x] Python interpreter configured in PyCharm
- [x] `uv` installed
- [x] Python 3.12 available through `uv`
- [x] virtual environment created
- [x] baseline `pytest` runs
- [x] Docker Desktop + Compose verified with hello-world container
- [x] Ollama skipped due macOS 12.6; llama.cpp local inference verified via Docker
- [x] `START_HERE.md` read
- [ ] `PROJECT_STATE.md` updated
- [ ] Day 0 commit pushed

No AI concepts count as learned on Day 0.

---

# Day 1 — LLM fundamentals + first local model

**Date:** Aug 11  
**Target:** 1.5–2 h

Learn:
- inference vs training
- tokens and tokenization
- context window
- temperature / sampling intuition
- system vs user instructions
- structured output
- local vs hosted inference
- latency/cost/privacy tradeoff

Implement:
- first local model invocation
- small Python LLM client abstraction
- plain-text response
- structured Pydantic response
- simple timing/token experiment

Failure experiment:
- malformed/unstructured answer
- observe validation failure

Interview exit criteria:
- explain why local model is useful here
- explain temperature
- explain structured output vs free text

---

# Day 2 — Embeddings + similarity search from first principles

**Date:** Aug 12  
**Target:** 1.5–2 h

Learn:
- what embeddings represent
- vector dimensions
- cosine similarity
- dot product
- normalization
- semantic vs lexical matching

Implement:
- generate embeddings locally
- cosine similarity by hand
- naive in-memory top-k vector search
- tiny incident corpus

Experiment:
- semantic paraphrase
- exact identifier/error-code query
- observe at least one weakness of dense retrieval

Interview exit criteria:
- cosine vs dot product
- why embeddings are not exact keyword search
- what changes when embedding model changes

---

# Day 3 — Document ingestion + basic RAG

**Date:** Aug 13  
**Target:** 1.5–2 h

Learn:
- ingestion pipeline
- parsing/cleaning
- chunks
- overlap
- metadata
- retrieval-augmented generation
- grounding and citations

Implement:
- ingest local incident/runbook documents
- fixed/recursive chunking
- retrieve top-k
- construct context
- answer with citations

Failure experiment:
- bad chunk size or missing context
- ask question not supported by corpus

Interview exit criteria:
- RAG vs sending entire document
- chunk-size tradeoffs
- RAG vs model knowledge

---

# Day 4 — PostgreSQL + pgvector + vector indexing

**Date:** Aug 14  
**Target:** 1.5–2 h

Learn:
- relational data vs vector data
- exact nearest neighbor vs ANN
- HNSW intuition
- recall vs latency
- metadata filtering

Implement:
- PostgreSQL in Docker
- pgvector extension
- document/chunk schema
- vector insertion and retrieval
- metadata filter

Experiment:
- compare naive in-memory search with DB-backed retrieval
- inspect query/index behavior at small scale

Interview exit criteria:
- why pgvector
- HNSW intuition
- when dedicated vector DB may be preferable

---

# Day 5 — Production RAG: BM25 + hybrid search + reranking

**Date:** Aug 15  
**Target:** 3–4 h

Learn:
- lexical retrieval
- TF-IDF intuition
- BM25 intuition
- dense vs sparse retrieval
- hybrid search
- rank fusion
- rerankers / cross-encoders
- recall vs precision

Implement:
- BM25 retrieval
- dense retrieval
- hybrid fusion
- reranker
- citations and context builder

Experiment:
- exact error codes / product names
- semantic paraphrases
- compare dense-only, sparse-only, hybrid, hybrid+rerank

Record:
- retrieval quality numbers in `EXPERIMENTS.md`

Interview exit criteria:
- explain the failure that justified hybrid search
- explain reranking cost/quality tradeoff
- explain why not rerank entire corpus

---

# Day 6 — RAG evaluation + prompt evaluation

**Date:** Aug 16  
**Target:** 3–4 h

Learn:
- offline evaluation
- golden datasets
- precision@k / recall@k
- MRR / NDCG intuition
- answer correctness
- faithfulness / groundedness
- LLM-as-judge limitations
- regression testing for AI

Implement:
- small evaluation dataset
- retrieval evaluator
- answer evaluator
- basic experiment runner
- MLflow/local tracking if practical

Experiment:
- compare at least two retrieval configurations
- produce a small baseline table

Interview exit criteria:
- how to know RAG improved
- why “looks good to me” is insufficient
- when human eval is necessary

---

# Day 7 — Tool calling + agent loop

**Date:** Aug 17  
**Target:** 1.5–2 h

Learn:
- tool/function calling
- agent loop
- deterministic workflow vs agent
- tool schema
- retries/timeouts
- termination

Implement:
- at least 3 safe tools:
  - search knowledge
  - search synthetic logs/incidents
  - retrieve deployment/service information
- first manual/simple agent loop

Failure experiment:
- tool error/timeout
- invalid arguments

Interview exit criteria:
- agent vs workflow
- when not to use an agent
- tool safety boundaries

---

# Day 8 — LangGraph + state + memory + guardrails + HITL

**Date:** Aug 18  
**Target:** 1.5–2 h

Learn:
- graph/state-machine thinking
- state
- checkpoint/persistence intuition
- short-term conversation state vs long-term memory vs RAG
- prompt injection
- tool authorization
- human-in-the-loop

Implement:
- LangGraph workflow
- routing node
- retrieval/tool node
- response node
- basic guardrail
- dangerous-action approval gate

Failure experiment:
- prompt injection attempt
- request unauthorized/high-risk tool action

Interview exit criteria:
- why LangGraph instead of plain loop
- memory vs RAG
- where HITL belongs

---

# Day 9 — Classical ML classifier

**Date:** Aug 19  
**Target:** 1.5–2 h

Learn:
- supervised learning
- features/labels
- train/validation/test
- TF-IDF
- logistic regression
- class imbalance
- precision/recall/F1
- confusion matrix
- overfitting

Implement:
- synthetic/labeled incident dataset
- TF-IDF + Logistic Regression incident classifier
- evaluation metrics
- model save/load
- compare with an LLM classifier on a tiny sample

Interview exit criteria:
- why small ML model instead of LLM
- precision vs recall
- data leakage / overfitting

---

# Day 10 — Fine-tuning: SFT + LoRA/QLoRA

**Date:** Aug 20  
**Target:** 1.5–2 h

Learn:
- pretraining vs fine-tuning
- supervised fine-tuning
- LoRA intuition
- QLoRA intuition
- adapters
- dataset formatting
- learning rate/epoch/batch-size intuition
- RAG vs fine-tuning vs prompting

Implement:
- prepare a tiny instruction dataset
- run one small LoRA/QLoRA experiment locally or on a free notebook environment if available
- compare baseline vs tuned output

Important:
- one learning experiment is enough
- do not spend hours optimizing training

Interview exit criteria:
- when to fine-tune
- LoRA benefits/tradeoffs
- why fine-tuning does not replace fresh knowledge retrieval

---

# Day 11 — FastAPI + persistence + Redis

**Date:** Aug 21  
**Target:** 1.5–2 h

Learn:
- API boundary
- Pydantic contracts
- async intuition
- relational persistence
- cache-aside
- TTL
- cache invalidation
- rate limiting intuition

Implement:
- FastAPI endpoints
- conversations/incidents/feedback persistence
- Redis cache
- latency before/after cache
- safe fallback when Redis is unavailable

Interview exit criteria:
- what belongs in Postgres vs Redis
- async vs sync
- cache failure behavior

---

# Day 12 — Kafka + async/event-driven reliability

**Date:** Aug 22  
**Target:** 3–4 h

Learn:
- producer
- topic
- partition
- consumer
- consumer group
- ordering
- retries
- dead-letter queue
- at-least-once delivery
- idempotency
- backpressure intuition

Implement:
- incident-created event
- investigation consumer
- simulate failure
- retry
- DLQ
- idempotent processing

Experiment:
- duplicate event
- consumer crash/failure

Interview exit criteria:
- Kafka vs synchronous API
- Kafka vs task queue
- duplicate-processing handling
- ordering tradeoffs

---

# Day 13 — Docker Compose + observability + reliability

**Date:** Aug 23  
**Target:** 3–4 h

Learn:
- service boundaries
- health/readiness
- logs/metrics/traces
- correlation IDs
- token/latency/cost tracking
- failure isolation

Implement:
- Docker Compose local stack
- API + Postgres/pgvector + Redis + Kafka + supporting services
- tracing/metrics at a learning-appropriate depth
- failure drills

Failure drills:
- kill Redis
- stop DB
- fail a tool/model call
- observe/report behavior

Interview exit criteria:
- p95/p99
- tracing an agent request
- graceful degradation

---

# Day 14 — Kubernetes + CI/CD + load test + system design + mock interview

**Date:** Aug 24  
**Target:** ~2 h minimum; extend if useful

Learn/practice:
- Deployment / Service
- replicas
- liveness/readiness
- horizontal scaling intuition
- CI/CD gates
- AI eval regression gate
- basic load testing
- end-to-end system design
- cost/latency/quality/scaling tradeoffs

Implement only a thin slice:
- local Kubernetes or equivalent learning deployment if machine supports it
- scale replicas
- kill a pod and observe recovery
- simple CI pipeline
- simple load test

Mock interview:
- architecture walkthrough
- RAG deep dive
- agents/workflow
- evals
- fine-tuning
- reliability
- scaling
- security/guardrails
- cost optimization

---

# Master Coverage Matrix

Legend:
- `[ ]` not started
- `[~]` partial
- `[x]` completed and Definition of Done met
- `[-]` intentionally skipped with reason recorded

| Topic | Theory | Implemented | Tested/Measured | Tradeoff | Interview |
|---|---|---|---|---|---|
| LLM fundamentals | [ ] | [ ] | [ ] | [ ] | [ ] |
| Prompting / structured output | [ ] | [ ] | [ ] | [ ] | [ ] |
| Embeddings | [ ] | [ ] | [ ] | [ ] | [ ] |
| Similarity search | [ ] | [ ] | [ ] | [ ] | [ ] |
| RAG | [ ] | [ ] | [ ] | [ ] | [ ] |
| Chunking / metadata | [ ] | [ ] | [ ] | [ ] | [ ] |
| PostgreSQL | [ ] | [ ] | [ ] | [ ] | [ ] |
| pgvector / ANN / HNSW | [ ] | [ ] | [ ] | [ ] | [ ] |
| BM25 / sparse retrieval | [ ] | [ ] | [ ] | [ ] | [ ] |
| Hybrid retrieval | [ ] | [ ] | [ ] | [ ] | [ ] |
| Reranking | [ ] | [ ] | [ ] | [ ] | [ ] |
| RAG evals | [ ] | [ ] | [ ] | [ ] | [ ] |
| LLM-as-judge | [ ] | [ ] | [ ] | [ ] | [ ] |
| Tool calling | [ ] | [ ] | [ ] | [ ] | [ ] |
| Agents | [ ] | [ ] | [ ] | [ ] | [ ] |
| LangGraph/workflows | [ ] | [ ] | [ ] | [ ] | [ ] |
| State / memory | [ ] | [ ] | [ ] | [ ] | [ ] |
| Guardrails / prompt injection | [ ] | [ ] | [ ] | [ ] | [ ] |
| Human-in-the-loop | [ ] | [ ] | [ ] | [ ] | [ ] |
| Classical ML | [ ] | [ ] | [ ] | [ ] | [ ] |
| ML evaluation | [ ] | [ ] | [ ] | [ ] | [ ] |
| Fine-tuning / SFT | [ ] | [ ] | [ ] | [ ] | [ ] |
| LoRA / QLoRA | [ ] | [ ] | [ ] | [ ] | [ ] |
| FastAPI | [ ] | [ ] | [ ] | [ ] | [ ] |
| Async Python | [ ] | [ ] | [ ] | [ ] | [ ] |
| Redis | [ ] | [ ] | [ ] | [ ] | [ ] |
| Kafka | [ ] | [ ] | [ ] | [ ] | [ ] |
| Idempotency / retries / DLQ | [ ] | [ ] | [ ] | [ ] | [ ] |
| Docker / Compose | [ ] | [ ] | [ ] | [ ] | [ ] |
| Observability | [ ] | [ ] | [ ] | [ ] | [ ] |
| MLflow / experiment tracking | [ ] | [ ] | [ ] | [ ] | [ ] |
| Kubernetes basics | [ ] | [ ] | [ ] | [ ] | [ ] |
| CI/CD | [ ] | [ ] | [ ] | [ ] | [ ] |
| Load testing | [ ] | [ ] | [ ] | [ ] | [ ] |
| AI system design | [ ] | [ ] | [ ] | [ ] | [ ] |

---

# Explicitly deferred topics

These are not allowed to derail the 14-day sprint unless needed by an interview:

- training a foundation model from scratch
- deep CUDA/Triton kernels
- distributed multi-GPU training internals
- deep computer-vision model training
- deep speech model training
- advanced RLHF/RL research
- polished frontend
- production cloud deployment costs
- enterprise-grade Kubernetes administration
- GraphRAG / multimodal / MCP / multi-agent extensions before core plan is complete

They may be added after Day 14.
