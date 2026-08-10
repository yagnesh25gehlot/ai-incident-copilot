# PROJECT STATE

> This is the exact operational state of the course. Update at the end of every session.

## Identity

Project: **Production AI Incident & Knowledge Copilot**
Sprint: **14-day AI Engineer capstone**
Current day: **Day 1 — LLM Fundamentals + First Python LLM Client**
Current phase: **Day 1 checkpoint**
Overall status: **DAY 1 COMPLETE — final Git checkpoint pending**

## Permanent local project root

`/Users/yagnesh/Desktop/projects/ai-incident-copilot`

## Machine / environment

* macOS 12.6 Monterey
* Apple Silicon `arm64`
* 8 GB RAM
* PyCharm
* Git 2.33.0
* `uv` 0.12.3
* Python 3.12.13
* Docker Desktop 4.37.2
* Docker Engine 27.4.0
* Docker Compose 2.31.0

## Day 0 — Setup

Status: **COMPLETE**

Completed:

* [x] Project concept selected
* [x] 14-day learning strategy agreed
* [x] Durable source-of-truth approach agreed
* [x] Starter repository created
* [x] Permanent local project root selected
* [x] Git repository initialized on `main`
* [x] Git identity configured
* [x] GitHub HTTPS remote configured
* [x] PyCharm opened and project interpreter configured
* [x] `uv` installed
* [x] Python 3.12.13 installed through `uv`
* [x] `.venv` created
* [x] Baseline pytest passed
* [x] Docker daemon verified
* [x] Docker `hello-world` container executed successfully
* [x] Local Qwen2.5-0.5B-Instruct Q4_K_M GGUF downloaded
* [x] `llama.cpp` server executed through Docker
* [x] Local OpenAI-compatible `/v1/chat/completions` request succeeded
* [x] Generated first local LLM response
* [x] `docs/START_HERE.md` read
* [x] Initial repository pushed to GitHub

## Local inference setup

Current local model:

`Qwen2.5-0.5B-Instruct Q4_K_M`

Model location:

`models/qwen2.5-0.5b-instruct-q4_k_m.gguf`

Runtime:

`llama.cpp` server inside Docker

Model alias:

`local-qwen`

Local API:

`http://127.0.0.1:8080`

Current runtime context window:

`2048 tokens`

Reason Ollama was not used:

Current Ollama releases do not support this machine's macOS 12.6 environment.

Day 0 environment-validation inference sample:

* Prompt tokens: 39
* Completion tokens: 38
* Total tokens: 77
* Generation speed: ~31.45 tokens/sec

These are environment-validation numbers only, not a formal benchmark.

## Day 1 — LLM Fundamentals + First Python LLM Client

Status: **COMPLETE**

### Theory completed

* [x] Understood training vs inference
* [x] Understood RAG vs fine-tuning vs inference
* [x] Understood tokens and tokenization
* [x] Understood context-window budgeting
* [x] Understood next-token generation
* [x] Understood logits
* [x] Understood softmax and conversion of logits into probabilities
* [x] Understood probabilistic token sampling
* [x] Understood greedy decoding at a conceptual level
* [x] Understood temperature and its effect on the probability distribution
* [x] Understood that low temperature does not guarantee factual correctness
* [x] Understood system vs user instruction priority
* [x] Introduced prompt-injection / instruction-override risk
* [x] Understood why retrieved RAG content must be treated as data rather than trusted instructions
* [x] Compared local-model vs hosted-model tradeoffs
* [x] Understood why hosted models do not inherently have Internet access
* [x] Understood prompt/input tokens vs completion/output tokens
* [x] Understood basic LLM latency components: prefill, decoding, and network/queue overhead
* [x] Understood why structured output is useful for application integration
* [x] Understood why LLM output should be treated as untrusted application input
* [x] Understood JSON parsing vs schema validation

### Python implementation completed

Dependencies added:

* `httpx`
* `pydantic`

Implemented:

`src/llm_client.py`

Capabilities implemented:

* [x] Python → llama.cpp HTTP communication using `httpx`
* [x] OpenAI-compatible `/v1/chat/completions` invocation
* [x] System and user messages
* [x] Temperature configuration
* [x] Maximum output-token configuration
* [x] Plain-text local LLM invocation
* [x] Structured incident-analysis prompt
* [x] JSON response parsing
* [x] Cleanup of Markdown-fenced JSON returned by the model
* [x] Pydantic `IncidentAnalysis` schema
* [x] Constrained severity values
* [x] Confidence constraint between `0` and `1`
* [x] Conversion of LLM JSON into a typed Pydantic object
* [x] Intentional Pydantic validation-failure experiment
* [x] Latency measurement using `time.perf_counter()`
* [x] Prompt-token measurement
* [x] Completion-token measurement
* [x] Total-token measurement

### Current structured schema

`IncidentAnalysis`

Fields:

* `root_cause: str`
* `severity: Literal["low", "medium", "high", "critical"]`
* `confidence: float` constrained to `[0, 1]`

### Important Day 1 observations

#### 1. LLM output is probabilistic

The same incident produced different severity classifications across executions even with a low temperature.

Low temperature reduces randomness; it does not guarantee identical or correct answers.

#### 2. Prompt instructions are not guarantees

The model was explicitly instructed to return only JSON without Markdown, but it returned:

````text
```json
{ ... }
````

```

This caused `json.loads()` to fail before Pydantic validation.

A cleanup step was added before JSON parsing.

#### 3. JSON parsing and schema validation are separate

Pipeline:

`LLM text → cleanup → json.loads() → Pydantic validation → typed application object`

`json.loads()` validates JSON syntax.

Pydantic validates the application's expected schema, types, enums, and constraints.

#### 4. Validation failure was deliberately tested

Invalid data such as:

- unsupported severity value
- confidence greater than `1`

was passed to `IncidentAnalysis`.

Pydantic rejected the invalid application data as expected.

#### 5. Root-cause quality is not yet the goal

The current small model sometimes restates the incident symptom instead of discovering a meaningful root cause.

This is acceptable at this stage because Day 1 validates the LLM/application plumbing.

Retrieval, grounding, evaluation, and answer-quality improvements come later in the syllabus.

### Day 1 measured inference sample

One measured structured-analysis request:

- Latency: ~0.86 seconds
- Prompt tokens: 109
- Completion tokens: 48
- Total tokens: 157

These numbers are a learning measurement, not a formal benchmark.

### Networking/debugging lesson

Initial Python requests using the original client failed with:

`httpx.ConnectError: [Errno 8] nodename nor servname provided, or not known`

Debugging established:

- llama.cpp server was healthy
- Docker port mapping was healthy
- `curl` could reach the server
- Python and `httpx` could reach `127.0.0.1:8080`
- local inference itself was healthy

Current client uses:

`http://127.0.0.1:8080`

and:

`httpx.Client(trust_env=False, ...)`

Python-driven local Qwen inference is now verified successfully.

## Current mental model

LLM generation:

`context → transformer → logits → temperature scaling → softmax → probability distribution → decoding/sampling → next token → repeat`

Current application path:

`Python application → HTTP/JSON → llama.cpp server → Qwen inference → JSON HTTP response → response cleanup → JSON parsing → Pydantic validation → typed IncidentAnalysis`

Future RAG path:

`incident/question → retrieval → relevant document chunks → prompt/context → LLM inference → grounded answer`

RAG changes the **context**, not the model weights.

Fine-tuning changes the **model weights**.

Inference uses the trained model to generate output.

## Current blockers

None.

## Remaining Day 1 checkpoint work

- [ ] Review final Git contents
- [ ] Stage final Day 1 files
- [ ] Commit Day 1 checkpoint
- [ ] Push `main` to GitHub
- [ ] Verify clean working tree

## Expected Day 1 Git changes

- `src/llm_client.py`
- `pyproject.toml`
- `uv.lock`
- `PROJECT_STATE.md`

## GitHub remote

`https://github.com/yagnesh25gehlot/ai-incident-copilot.git`

## Next exact action

Review and stage the final Day 1 changes, create the Day 1 Git checkpoint, push `main`, and verify a clean working tree.

## Next learning session

**Day 2 — Embeddings + Vector Search**

Planned direction:

1. Understand what embeddings represent.
2. Understand semantic similarity.
3. Understand cosine similarity.
4. Generate embeddings for sample incident/runbook text.
5. Compare semantically similar and dissimilar text.
6. Implement the first vector-search experiment.
7. Connect embedding concepts back to the future RAG pipeline.

Do not start Day 2 implementation until the Day 1 Git checkpoint is complete.
```
