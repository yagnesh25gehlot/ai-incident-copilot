# ARCHITECTURE DECISION RECORDS

These decisions prevent random technology drift. Changes are allowed only when an experiment or new constraint justifies them.

---

## ADR-001 — Local-first learning architecture

**Status:** Accepted

**Decision:** Run as much infrastructure locally as practical.

**Why:**
- near-zero cost
- ability to inspect and break components
- easier experimentation
- teaches infrastructure instead of only managed-service SDK calls

**Tradeoff:**
- local machine has limited RAM/CPU/GPU
- not representative of true production scale
- some cloud-specific operational knowledge will remain conceptual

**Revisit when:** a learning objective genuinely requires a managed/cloud service.

---

## ADR-002 — Python 3.12 for the capstone

**Status:** Accepted

**Decision:** Use Python 3.12 as the project runtime.

**Why:**
- modern Python
- broad AI/ML ecosystem compatibility
- avoids using the newest runtime merely for novelty during a compressed sprint

**Tradeoff:** we intentionally do not optimize for testing the newest Python language release.

---

## ADR-003 — uv for Python environment/dependency management

**Status:** Accepted

**Decision:** Use `uv` rather than mixing global Python, pip installs and ad-hoc virtualenv commands.

**Why:**
- reproducible environment
- Python version management
- dependency locking
- fast setup
- one consistent workflow

**Tradeoff:** interviews may mention pip/venv/Poetry; we will still understand the underlying concepts.

---

## ADR-004 — IntelliJ IDEA is acceptable as the IDE

**Status:** Accepted

**Decision:** No IDE migration is required if IntelliJ IDEA with Python support is already comfortable.

**Why:** IDE choice should not consume the 14-day learning budget.

**Tradeoff:** a Python-focused IDE may provide a slightly more natural default experience.

---

## ADR-005 — llama.cpp local inference first, hosted model optional

**Status:** Accepted

**Decision:** Use `llama.cpp` through Docker as the initial local inference runtime.

Initial model:

`Qwen2.5-0.5B-Instruct Q4_K_M`

**Why:**
- current machine runs macOS 12.6, so current Ollama releases are not suitable
- Docker is already working reliably
- `llama.cpp` supports GGUF quantized models
- zero per-call inference cost
- exposes the model-serving layer instead of hiding it behind a hosted API
- provides an OpenAI-compatible HTTP endpoint that our application can call

**Tradeoff:**
- the initial 0.5B model is intentionally small and significantly weaker than frontier hosted models
- Docker on macOS does not expose Apple Metal acceleration in the same way as a native llama.cpp build
- inference quality and performance are therefore not representative of a production model
- this is a learning runtime, not our final model-quality benchmark

**Observed environment validation:**
- local API request succeeded
- approximately 31.45 generated tokens/sec on the first tiny test

**Revisit when:**
- we benchmark model quality,
- need a stronger model,
- compare local vs hosted inference,
- or upgrade the local operating system/runtime.

---

## ADR-006 — PostgreSQL + pgvector as primary vector persistence

**Status:** Planned

**Decision:** Use PostgreSQL + pgvector before introducing a dedicated vector DB.

**Why:**
- one DB for relational + vector learning
- local and free
- metadata filtering
- production-relevant tradeoff discussion

**Tradeoff:** specialized vector services may offer easier managed scaling/features.

---

## ADR-007 — Production polish is intentionally secondary

**Status:** Accepted

**Decision:** Optimize the first 14 days for knowledge and interview defensibility, not UI polish or large-scale deployment.

**Consequences:**
- minimal/no polished frontend
- small datasets
- thin Kubernetes exercise
- one fine-tuning experiment
- local infrastructure
