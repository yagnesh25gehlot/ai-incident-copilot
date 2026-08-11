# PROJECT STATE

> This is the exact operational state of the course. Update at the end of every session.

## Identity

Project: **Production AI Incident & Knowledge Copilot**
Sprint: **14-day AI Engineer capstone**
Current day: **Day 2 — Embeddings + Similarity Search**
Current phase: **Day 2 checkpoint**
Overall status: **DAY 2 COMPLETE — final Git checkpoint pending**

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

---

# Day 0 — Setup

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

---

# Local inference setup

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

---

# Day 1 — LLM Fundamentals + First Python LLM Client

Status: **COMPLETE**

## Theory completed

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

## Python implementation completed

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

## Current structured schema

`IncidentAnalysis`

Fields:

* `root_cause: str`
* `severity: Literal["low", "medium", "high", "critical"]`
* `confidence: float` constrained to `[0, 1]`

## Important Day 1 observations

### 1. LLM output is probabilistic

The same incident produced different severity classifications across executions even with a low temperature.

Low temperature reduces randomness; it does not guarantee identical or correct answers.

### 2. Prompt instructions are not guarantees

The model was explicitly instructed to return only JSON without Markdown, but it returned Markdown-fenced JSON.

This caused `json.loads()` to fail before Pydantic validation.

A cleanup step was added before JSON parsing.

### 3. JSON parsing and schema validation are separate

Pipeline:

`LLM text → cleanup → json.loads() → Pydantic validation → typed application object`

`json.loads()` validates JSON syntax.

Pydantic validates the application's expected schema, types, enums, and constraints.

### 4. Validation failure was deliberately tested

Invalid data such as:

* unsupported severity value
* confidence greater than `1`

was passed to `IncidentAnalysis`.

Pydantic rejected the invalid application data as expected.

### 5. Root-cause quality is not yet the goal

The current small model sometimes restates the incident symptom instead of discovering a meaningful root cause.

This is acceptable at this stage because Day 1 validates the LLM/application plumbing.

Retrieval, grounding, evaluation, and answer-quality improvements come later in the syllabus.

## Day 1 measured inference sample

One measured structured-analysis request:

* Latency: ~0.86 seconds
* Prompt tokens: 109
* Completion tokens: 48
* Total tokens: 157

These numbers are a learning measurement, not a formal benchmark.

## Networking/debugging lesson

Initial Python requests using the original client failed with:

`httpx.ConnectError: [Errno 8] nodename nor servname provided, or not known`

Debugging established:

* llama.cpp server was healthy
* Docker port mapping was healthy
* `curl` could reach the server
* Python and `httpx` could reach `127.0.0.1:8080`
* local inference itself was healthy

Current client uses:

`http://127.0.0.1:8080`

and:

`httpx.Client(trust_env=False, ...)`

Python-driven local Qwen inference is verified successfully.

---

# Day 2 — Embeddings + Similarity Search

Status: **COMPLETE**

## Theory completed

* [x] Understood what text embeddings represent
* [x] Understood embeddings as fixed-length numerical vectors
* [x] Understood that semantic meaning is distributed across vector dimensions
* [x] Understood embedding dimensionality
* [x] Understood why vectors from different embedding models should not be directly compared
* [x] Understood why changing embedding models usually requires re-embedding stored documents
* [x] Understood dot product
* [x] Understood vector magnitude / norm
* [x] Understood cosine similarity from first principles
* [x] Understood cosine similarity as normalized dot product
* [x] Understood that cosine similarity compares vector direction rather than raw magnitude
* [x] Understood vector normalization
* [x] Understood that `normalize_embeddings=True` produces unit-length vectors
* [x] Understood why cosine similarity equals dot product for unit-normalized vectors
* [x] Understood semantic retrieval vs lexical/exact matching
* [x] Understood why exact identifiers, error codes, hostnames, and versions can favor lexical retrieval
* [x] Understood basic dense-retrieval failure modes
* [x] Understood `top_k` and the recall/context tradeoff
* [x] Understood brute-force exact vector search
* [x] Understood ANN at a conceptual level
* [x] Understood brute-force vs ANN recall/latency tradeoff

## Dependencies added

* `sentence-transformers`
* transitive dependencies including:

  * NumPy
  * PyTorch
  * Transformers
  * scikit-learn
  * SciPy

## Embedding model

Current local embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

Primary purpose:

`text → embedding vector`

This model is used for retrieval representations and is separate from the generative Qwen model used for answer generation.

## Implementation completed

Implemented:

`src/embedding_demo.py`

Capabilities:

* [x] Generated embeddings locally using SentenceTransformers
* [x] Inspected embedding shape/dimensionality
* [x] Implemented cosine similarity manually using NumPy
* [x] Compared semantically similar vs unrelated sentences
* [x] Generated normalized embeddings
* [x] Verified normalized vector magnitudes are approximately `1`
* [x] Verified cosine similarity approximately equals dot product for normalized embeddings

Implemented:

`src/vector_search.py`

Capabilities:

* [x] Created reusable `VectorSearch` class
* [x] Indexed a list of incident documents
* [x] Generated normalized document embeddings
* [x] Generated query embedding
* [x] Computed query-document similarity using dot product
* [x] Ranked documents by similarity score
* [x] Returned configurable top-k results
* [x] Added protection against searching before indexing
* [x] Built first naive in-memory dense retriever

## Day 2 semantic-similarity experiment

Example texts:

A:

`PostgreSQL connection pool exhausted`

B:

`Database has no free connections remaining`

C:

`How do I reset my employee password?`

Observed similarity:

* A vs B: `0.5324976`
* A vs C: `0.063713655`

Interpretation:

The embedding model placed the semantically similar database statements much closer together than the unrelated password question.

Important:

Cosine similarity values are not probabilities.

For example, `0.53` does not mean the model is “53% confident.”

Useful score thresholds must be determined experimentally for the specific retrieval task and corpus.

## Day 2 first vector-retrieval experiment

Query:

`Database connections are unavailable and requests keep timing out`

Top results:

1. `0.6417` → PostgreSQL connection pool exhausted and requests are timing out.
2. `0.3416` → TLS certificate expired and clients cannot establish secure connections.
3. `0.2754` → Authentication service rejects users because the identity provider is unavailable.

Observation:

The correct PostgreSQL incident ranked first.

The TLS result still received some similarity because connection-establishment failures are semantically related to connection problems.

This illustrates that dense retrieval captures semantic relationships but is not perfectly precise.

## Exact-identifier experiment

Query:

`INC-REDIS-7421`

Observed result:

* `0.4814` → exact-ID Redis document
* `0.3864` → semantically related Redis document
* `0.1378` → PostgreSQL document

The exact-ID document ranked first in this small experiment.

However, this does not prove dense retrieval is the best mechanism for identifiers.

Exact identifiers, error codes, ticket IDs, hostnames, and version strings are still strong use cases for lexical/exact retrieval.

Hybrid retrieval will later combine both approaches.

## Current retrieval architecture

Current brute-force dense retrieval:

`documents → embedding model → normalized document vectors`

Then:

`query → query embedding → dot product with every document vector → sort descending → top-k`

Because document/query vectors are normalized:

`dot product ≈ cosine similarity`

## Brute-force vs ANN mental model

Current implementation:

**Exact / brute-force nearest-neighbor search**

For every query:

`query vector → compare against every stored document vector`

Advantages:

* exact ranking over the stored corpus
* high recall
* simple and easy to understand

Disadvantages:

* work grows with corpus size
* becomes expensive for very large corpora

ANN:

* searches only a strategically selected portion of the vector index
* reduces latency significantly at scale
* can sacrifice some recall

ANN/HNSW implementation is intentionally deferred to Day 4.

## `top_k` lesson

`top_k` controls how many highest-scoring retrieved documents/chunks are returned.

Too small:

* may miss required evidence
* lowers retrieval recall

Too large:

* adds irrelevant context
* consumes additional tokens
* increases latency/cost
* can distract the generative model

Example:

If the correct chunk ranks fourth but `top_k=3`, the required evidence never reaches the LLM.

That is primarily a **retrieval failure**, not necessarily a generation failure.

## RAG debugging mental model

For a wrong answer:

`Was the correct evidence retrieved?`

If **no**:

→ investigate retrieval.

If **yes**:

→ investigate prompt construction / generation / model reasoning.

This distinction will be important during RAG evaluation.

---

# Current mental models

## LLM generation

`context → transformer → logits → temperature scaling → softmax → probability distribution → decoding/sampling → next token → repeat`

## Structured generation path

`Python application → HTTP/JSON → llama.cpp → Qwen inference → response text → cleanup → JSON parsing → Pydantic validation → typed object`

## Dense retrieval

`text → embedding model → vector`

Then:

`query vector + document vectors → similarity scoring → ranking → top-k`

## Future RAG path

`question/incident → retrieve relevant chunks → build grounded context → LLM inference → answer`

RAG changes the **context**.

Fine-tuning changes the **weights**.

Inference uses the model without changing its weights.

---

# Current blockers

None.

---

# Remaining Day 2 checkpoint work

* [ ] Review final Git contents
* [ ] Stage latest Day 2 file versions
* [ ] Commit Day 2 checkpoint
* [ ] Push `main` to GitHub
* [ ] Verify clean working tree

## Expected Day 2 Git changes

* `src/embedding_demo.py`
* `src/vector_search.py`
* `pyproject.toml`
* `uv.lock`
* `PROJECT_STATE.md`

---

# GitHub remote

`https://github.com/yagnesh25gehlot/ai-incident-copilot.git`

---

# Next exact action

Stage the final Day 2 changes, create the Day 2 Git checkpoint, push `main`, and verify a clean working tree.

---

# Next learning session

**Day 3 — Document Ingestion + Basic RAG**

Planned learning:

1. Understand the document-ingestion pipeline.
2. Understand parsing and cleaning.
3. Understand chunking.
4. Understand chunk size and overlap.
5. Understand document/chunk metadata.
6. Create a small local incident/runbook corpus.
7. Chunk and embed the corpus.
8. Retrieve relevant chunks using the Day 2 vector-search foundation.
9. Build an LLM context from retrieved chunks.
10. Generate the first grounded RAG answer.
11. Add simple source/citation information.
12. Test an unsupported question and observe RAG failure behavior.

Do not start Day 3 implementation until the Day 2 Git checkpoint is complete.
