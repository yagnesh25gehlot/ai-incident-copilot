# PROJECT STATE

> This is the exact operational state of the course. Update at the end of every session.

## Identity

Project: **Production AI Incident & Knowledge Copilot**
Sprint: **14-day AI Engineer capstone**
Current day: Day 7 — Tool Calling + Agent Loop
Current phase: Day 7 checkpoint
Overall status: DAY 7 COMPLETE — final Git checkpoint pending

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

# Day 3 — Document Ingestion + Basic RAG

Status: **COMPLETE**

## Theory completed

- [x] Understood document ingestion pipeline
- [x] Understood loading vs chunking
- [x] Understood ingestion vs indexing vs retrieval vs generation
- [x] Understood chunk-size tradeoffs
- [x] Understood chunk overlap
- [x] Understood metadata
- [x] Understood RAG grounding
- [x] Understood top-k behavior
- [x] Understood that top-ranked does not necessarily mean relevant
- [x] Understood similarity-threshold tradeoffs
- [x] Understood unsupported-query behavior
- [x] Understood retrieved source vs supporting source
- [x] Understood that RAG does not eliminate hallucination

## Implementation completed

- [x] Created local Markdown knowledge corpus
- [x] Added PostgreSQL runbook
- [x] Added Redis incident
- [x] Added TLS runbook
- [x] Implemented `Chunk` dataclass
- [x] Implemented Markdown document loading
- [x] Implemented fixed-size word chunking
- [x] Implemented chunk overlap
- [x] Added source and chunk ID metadata
- [x] Implemented `ChunkRetriever`
- [x] Generated normalized embeddings for chunks
- [x] Implemented dense top-k retrieval
- [x] Added minimum similarity filtering
- [x] Built retrieved context for the LLM
- [x] Connected retrieval to local Qwen
- [x] Generated first grounded RAG answer
- [x] Added structured RAG response with Pydantic
- [x] Added citation validation against retrieved sources
- [x] Added deterministic fallback when no relevant chunks are found

## Experiments

### Supported question

Question:

`Why are payment API requests timing out?`

Observed:

- PostgreSQL runbook ranked first.
- Qwen generated the correct explanation that the PostgreSQL connection pool was exhausted.
- Dense retrieval also returned irrelevant TLS chunks.

### Unsupported question

Question:

`Why is the Kafka consumer lag increasing in the order service?`

Without threshold:

- PostgreSQL chunks were still returned because top-k always returns the best available matches.
- Qwen incorrectly attributed Kafka lag to PostgreSQL-related causes.

Classification:

**retrieval failure followed by generation hallucination**

Added temporary:

`min_score = 0.3`

This prevented low-scoring unsupported retrieval and used a deterministic fallback instead.

Important:

`0.3` is experimental and has not been calibrated through evaluation.

### Chunk-size experiment

Baseline:

- `chunk_size = 80 words`
- `overlap = 20 words`
- 7 chunks
- best retrieval score approximately `0.50`
- good final answer

Experiment:

- `chunk_size = 20 words`
- `overlap = 0`
- 18 chunks
- best retrieval score approximately `0.72`
- final answer quality became worse because context was fragmented

Key lesson:

**Higher retrieval similarity does not necessarily mean better end-to-end RAG answer quality.**

## Current baseline

- Chunk size: `80 words`
- Overlap: `20 words`
- `top_k = 3`
- `min_score = 0.3` — experimental only
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding dimension: `384`
- Generator: `Qwen2.5-0.5B-Instruct Q4_K_M`
- Vector search: exact brute-force in-memory search

## Git checkpoint

Day 3 commit:

`cc16666 — Complete Day 3 document ingestion and basic RAG`

Pushed successfully to `origin/main`.

## Current blockers

None.

## Next learning session

**Day 4 — PostgreSQL + pgvector + vector indexing**

Next exact action:

Start PostgreSQL + pgvector in Docker and move persisted chunks/embeddings from Python memory into PostgreSQL.


# Day 4 — PostgreSQL + pgvector + Vector Indexing

Status: **COMPLETE**

## Theory completed

- [x] Understood relational data vs vector data
- [x] Understood why pgvector is useful
- [x] Understood pgvector as a PostgreSQL extension rather than a separate database
- [x] Understood exact nearest-neighbor search vs approximate nearest-neighbor search
- [x] Understood HNSW intuition
- [x] Understood recall vs latency tradeoff
- [x] Understood metadata filtering
- [x] Understood metadata-filter precision/recall tradeoff
- [x] Understood HNSW `m`
- [x] Understood HNSW `ef_construction`
- [x] Understood HNSW `ef_search`
- [x] Understood that creating an index does not guarantee PostgreSQL will use it
- [x] Understood why sequential scan can be preferable for very small tables
- [x] Understood index storage/write-cost tradeoffs

## PostgreSQL / pgvector setup

Docker container:

`incident-copilot-postgres`

Image:

`pgvector/pgvector:pg17`

Host/container port mapping:

`5433 -> 5432`

Database:

`incident_copilot`

User:

`copilot`

pgvector extension version:

`0.8.6`

Verified with:

`SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';`

## Database schema

Created table:

`chunks`

Fields:

- `id BIGSERIAL PRIMARY KEY`
- `source TEXT NOT NULL`
- `chunk_id INTEGER NOT NULL`
- `content TEXT NOT NULL`
- `embedding VECTOR(384) NOT NULL`

Embedding dimension remains `384` because the current embedding model is:

`sentence-transformers/all-MiniLM-L6-v2`

## Python dependencies added

- `psycopg[binary]`
- `pgvector`

## Implementation completed

Implemented:

`src/vector_store.py`

Capabilities:

- [x] PostgreSQL connection through psycopg
- [x] pgvector Python type registration
- [x] Clear stored chunks
- [x] Insert one vector-backed chunk
- [x] Batch insert chunks
- [x] PostgreSQL cosine-distance retrieval
- [x] Conversion of cosine distance back to similarity
- [x] Metadata filtering by source

Implemented:

`src/index_to_postgres.py`

Capabilities:

- [x] Reused Day 3 ingestion pipeline
- [x] Loaded Markdown knowledge documents
- [x] Generated normalized MiniLM embeddings
- [x] Combined each Chunk with its matching embedding using `zip`
- [x] Persisted chunk metadata, text, and embeddings into PostgreSQL

Implemented:

`src/postgres_search.py`

Capabilities:

- [x] Generated query embedding
- [x] Sent query vector to PostgreSQL
- [x] Retrieved top-k chunks using pgvector cosine distance
- [x] Printed similarity scores and source metadata
- [x] Tested metadata-filtered retrieval

Implemented:

`src/compare_retrievers.py`

Capabilities:

- [x] Compared Day 3 NumPy retrieval with PostgreSQL retrieval
- [x] Verified matching ranking behavior
- [x] Verified matching similarity scores

## Day 4 ingestion result

Observed:

- Loaded chunks: `7`
- Embedding shape: `(7, 384)`
- Inserted PostgreSQL chunks: `7`

## PostgreSQL retrieval experiment

Question:

`Why are payment API requests timing out?`

Observed PostgreSQL results:

1. `0.4999` → `postgres_runbook.md`, chunk `0`
2. `0.3492` → `tls_runbook.md`, chunk `0`

This reproduced the Day 3 dense-retrieval behavior.

Key lesson:

The migration from in-memory NumPy retrieval to PostgreSQL/pgvector preserved retrieval behavior while adding persistence and database-native search.

## NumPy vs pgvector comparison

Day 3 NumPy retrieval:

`normalized document embeddings @ normalized query embedding`

PostgreSQL retrieval:

`1 - (embedding <=> query_embedding)`

Because both query and document vectors are normalized:

`dot product ≈ cosine similarity`

The top-k ranking and similarity scores matched closely between both implementations.

This validated correctness of the PostgreSQL migration.

## Metadata filtering experiment

Added source filtering:

`WHERE source = %s`

Key lesson:

Correct metadata filters can:

- improve precision
- reduce irrelevant candidates
- reduce search work

Incorrect or overly strict metadata filters can:

- exclude correct evidence
- lower retrieval recall

## HNSW index

Created:

`chunks_embedding_hnsw_idx`

Using:

`hnsw (embedding vector_cosine_ops)`

Reason for `vector_cosine_ops`:

The current retrieval metric is cosine distance through pgvector's `<=>` operator.

## HNSW mental model

HNSW performs approximate nearest-neighbor search using a navigable hierarchical graph.

Instead of comparing the query vector against every stored vector, it explores promising graph neighborhoods.

Tradeoff:

- exact search → maximum recall, more work at scale
- HNSW / ANN → lower search cost and latency, potentially slightly lower recall

## HNSW tuning concepts

`m`

Controls graph connectivity.

Higher values can improve recall but increase index size and construction/search cost.

`ef_construction`

Controls how thoroughly the graph is searched while building the index.

Higher values can create a better-quality graph but make index construction slower.

`ef_search`

Controls how broadly HNSW explores candidates at query time.

Higher values:

- improve recall
- increase query latency/work

Lower values:

- reduce latency
- may reduce recall

## Query-plan experiment

Used:

`EXPLAIN ANALYZE`

Important lesson:

Creating an HNSW index does not force PostgreSQL to use it.

With the current corpus of only 7 rows, PostgreSQL may prefer a sequential scan because scanning the whole table can be cheaper than index traversal.

Therefore the current corpus is useful for understanding HNSW mechanics but not for meaningful ANN performance benchmarking.

## Current retrieval architecture

Ingestion:

`Markdown -> Chunk -> MiniLM embedding -> PostgreSQL chunks table`

Retrieval:

`question -> MiniLM query embedding -> pgvector search -> top-k chunks`

Current vector metric:

`cosine distance`

Current ANN index:

`HNSW`

Current metadata filter experiment:

`source`

## Day 4 key production lesson

Moving vectors into PostgreSQL separates ingestion from retrieval.

Previously:

`application startup -> ingest -> embed -> keep vectors in RAM`

Now:

`offline/indexing step -> persist chunks and vectors in PostgreSQL`

Then retrieval can happen independently:

`query -> query embedding -> PostgreSQL vector search`

This architecture is closer to a production RAG system.

## Current blockers

None.

## Git checkpoint

Pending.

Expected Day 4 Git changes:

- `src/vector_store.py`
- `src/index_to_postgres.py`
- `src/postgres_search.py`
- `src/compare_retrievers.py`
- `pyproject.toml`
- `uv.lock`
- `PROJECT_STATE.md`

# Day 5 — Production RAG: BM25 + Hybrid Search + Reranking

Status: **COMPLETE**

## Theory completed

- [x] Understood lexical retrieval
- [x] Understood term frequency intuition
- [x] Understood document frequency
- [x] Understood inverse document frequency
- [x] Understood TF-IDF intuition
- [x] Understood BM25 intuition
- [x] Understood BM25 term-frequency saturation
- [x] Understood BM25 document-length normalization
- [x] Understood dense vs sparse retrieval
- [x] Understood lexical retrieval strengths for exact identifiers/error codes
- [x] Understood semantic retrieval strengths for paraphrases
- [x] Understood hybrid retrieval
- [x] Understood why raw BM25 and cosine scores should not be naively added
- [x] Understood Reciprocal Rank Fusion
- [x] Understood candidate generation vs final ranking
- [x] Understood retrieval recall vs reranking precision
- [x] Understood bi-encoder vs cross-encoder architecture
- [x] Understood cross-encoder quality/latency tradeoff
- [x] Understood why reranking the entire corpus is expensive

## Dependencies

Added:

- `rank-bm25`

Existing `sentence-transformers` dependency reused for:

- `CrossEncoder`
- dense embedding model

## Implementation completed

Implemented:

`src/bm25_retriever.py`

Capabilities:

- [x] BM25 index over ingested chunks
- [x] Basic lowercase whitespace tokenization
- [x] BM25 query scoring
- [x] top-k lexical ranking
- [x] source/chunk metadata preserved

Implemented:

`src/compare_bm25_dense.py`

Capabilities:

- [x] Same-query comparison between BM25 and pgvector dense retrieval
- [x] lexical query experiment
- [x] semantic paraphrase experiment
- [x] exact identifier experiment

Implemented:

`src/hybrid_retriever.py`

Capabilities:

- [x] BM25 candidate retrieval
- [x] dense candidate retrieval
- [x] chunk identity using source + chunk_id
- [x] Reciprocal Rank Fusion
- [x] configurable candidate_k
- [x] configurable final top_k

Implemented:

`src/reranker.py`

Capabilities:

- [x] cross-encoder candidate reranking
- [x] query-document pair construction
- [x] final top-k ranking
- [x] preserved RRF score and reranker score for inspection

Implemented:

`src/compare_retrieval_methods.py`

Capabilities:

- [x] BM25 comparison
- [x] dense comparison
- [x] hybrid RRF comparison
- [x] hybrid + reranker comparison

Created:

`EXPERIMENTS.md`

with Day 5 retrieval observations.

## Key experiments

### Exact identifier

Query:

`INC-REDIS-7421`

BM25 correctly produced a strong Redis lexical match.

Key lesson:

Exact identifiers and similar tokens are strong lexical-retrieval use cases.

### Semantic query with weak lexical overlap

Query:

`Why can't the service acquire a DB slot?`

BM25 incorrectly favored TLS/Redis chunks.

Dense retrieval correctly ranked PostgreSQL chunks.

Key lesson:

Dense retrieval can recover semantic similarity when query and source terminology differ.

### Hybrid RRF

RRF combined BM25 and dense rankings without combining incompatible raw scores.

However, for the DB-slot query, RRF did not produce the best final ranking.

Key lesson:

Hybrid retrieval can improve candidate recall but does not guarantee final precision.

### Cross-encoder reranking

For the DB-slot query, reranking promoted a PostgreSQL chunk to rank 1.

Observed top reranker scores:

- PostgreSQL chunk 1: `-10.5761`
- Redis chunk 0: `-10.6054`
- PostgreSQL chunk 0: `-10.6302`

The ranking improved, but the score margin was small.

Therefore no strong claim about reranker superiority is made yet.

Quantitative evaluation is deferred to Day 6.

## Current production-style retrieval architecture

`query`

→ BM25 lexical retrieval

+

→ MiniLM query embedding → PostgreSQL/pgvector dense retrieval

→ Reciprocal Rank Fusion

→ candidate set

→ cross-encoder reranker

→ final top-k chunks

→ RAG context

→ LLM

## Current limitations

- corpus contains only a few knowledge documents
- BM25 tokenizer is intentionally basic
- no systematic labeled retrieval dataset yet
- candidate_k and top_k are not calibrated
- RRF k=60 is currently a default, not experimentally tuned
- reranker quality has only been inspected on a few manual queries
- retrieval latency has not yet been benchmarked systematically

## Current blockers

None.

## Next learning session

# Day 6 — RAG Evaluation + Prompt Evaluation

Status: **COMPLETE**

## Theory completed

- [x] Understood offline evaluation
- [x] Understood golden datasets
- [x] Understood Precision@K
- [x] Understood Recall@K
- [x] Understood Reciprocal Rank
- [x] Understood Mean Reciprocal Rank
- [x] Understood DCG / NDCG intuition
- [x] Understood retrieval vs generation evaluation
- [x] Understood correctness vs faithfulness
- [x] Understood citation validity vs citation relevance
- [x] Understood LLM-as-judge limitations
- [x] Understood human-evaluation necessity
- [x] Understood AI regression testing
- [x] Understood deterministic abstention

## Implementation completed

- [x] Created retrieval golden dataset
- [x] Created answer golden dataset
- [x] Implemented Precision@K
- [x] Implemented Recall@K
- [x] Implemented MRR
- [x] Implemented NDCG
- [x] Implemented four-way retrieval evaluator
- [x] Implemented deterministic citation/source checks
- [x] Implemented experimental LLM judge
- [x] Tested correct/hallucinated/partial answers
- [x] Rejected local judge as primary semantic evaluator
- [x] Added reranker relevance threshold
- [x] Added deterministic unsupported-query abstention
- [x] Implemented AI regression gate
- [x] Verified regression gate exit code 0

## Current retrieval baseline

Hybrid + reranker:

- P@3: `0.583`
- R@3: `1.000`
- MRR: `1.000`
- NDCG@3: `0.990`

## Current deterministic RAG baseline

- citation validity: `1.000`
- expected-source recall: `1.000`
- abstention accuracy: `1.000`
- supported-query answer rate: `1.000`
- unsupported-query abstention rate: `1.000`

## Experimental relevance threshold

`MIN_RERANK_SCORE = -2.0`

Not yet calibrated on a sufficiently large dataset.

## Important limitation

The regression gate does not currently guarantee semantic answer correctness or full claim-level faithfulness.

Human evaluation is still required for these dimensions.

## Current blockers

None.

## Next learning session

# Day 7 — Tool Calling + Agent Loop

Status: **COMPLETE**

## Theory completed

- [x] Understood tool/function calling
- [x] Understood that tools are ordinary application functions exposed to an LLM
- [x] Understood tool name + description + argument schema
- [x] Understood tool calling vs agent loop
- [x] Understood deterministic workflow vs agent
- [x] Understood when not to use an agent
- [x] Understood application-owned tool execution
- [x] Understood tool allowlisting
- [x] Understood least-privilege tool design
- [x] Understood argument validation
- [x] Understood agent termination rules
- [x] Understood no-progress / repeated-tool-call detection
- [x] Understood tool execution errors
- [x] Understood timeout/retry concepts
- [x] Understood why retries should depend on failure type
- [x] Understood idempotency risk for retrying side-effecting tools
- [x] Understood hybrid agent + deterministic workflow design

## Implementation completed

Implemented:

`src/agent_tools.py`

Capabilities:

- [x] `SearchKnowledgeArgs`
- [x] `SearchIncidentsArgs`
- [x] `GetServiceInfoArgs`
- [x] Pydantic validation for tool arguments
- [x] `get_service_info`
- [x] `search_incidents`
- [x] `search_knowledge`
- [x] Reused Day 5 hybrid BM25 + dense retrieval
- [x] Reused cross-encoder reranking
- [x] Applied reranker relevance threshold
- [x] Lazy initialization of embedding/reranker models
- [x] Tool registry
- [x] Safe tool dispatcher
- [x] Unknown-tool rejection
- [x] Invalid-argument rejection
- [x] Tool-execution error handling
- [x] Timeout/retry experiment

Implemented:

`src/agent_loop.py`

Capabilities:

- [x] Structured `AgentDecision`
- [x] Manual JSON tool-calling protocol
- [x] Local Qwen agent routing
- [x] JSON cleanup/parsing
- [x] Narrow deterministic protocol normalization
- [x] Tool execution feedback to model
- [x] Evidence collection
- [x] Maximum-step termination
- [x] Duplicate-tool-call detection
- [x] No-progress protection
- [x] Deterministic fallback for weak-model routing
- [x] Separate grounded final-answer generation

## Tool set

Production learning tools:

1. `get_service_info`
   - service version
   - environment
   - health/status
   - backing database

2. `search_incidents`
   - synthetic incident lookup
   - service/severity filtering

3. `search_knowledge`
   - BM25
   - pgvector dense retrieval
   - Reciprocal Rank Fusion
   - cross-encoder reranking
   - relevance filtering

## Agent experiments

### Invalid protocol

The local Qwen initially returned:

`action="search_incidents"`

instead of:

`action="tool"`

Pydantic rejected the invalid decision.

A narrow deterministic normalization layer was added for this unambiguous protocol error.

### Ungrounded final-answer attempt

Before using a tool, the model attempted to invent causes such as:

- high traffic
- network issues
- server overload

The application rejected ungrounded final answers.

### Repeated tool-call loop

The model repeatedly called the same tool with identical arguments.

Added:

- executed-call history
- duplicate detection
- no-progress termination
- deterministic fallback

### Successful agent run

Question:

`Why is payment-api timing out?`

Observed path:

`user -> search_incidents -> tool evidence -> final`

Tool evidence identified:

`PostgreSQL connection pool exhaustion`

Final grounded answer:

`Payment API requests timing out due to PostgreSQL connection pool exhaustion.`

### Knowledge-tool experiment

Query:

`Why are payment API requests timing out?`

Before threshold:

- PostgreSQL chunk 0: rerank approximately `3.9629`
- PostgreSQL chunk 1: approximately `-9.7003`
- TLS chunk 0: approximately `-9.8970`

Using:

`MIN_RERANK_SCORE = -2.0`

only PostgreSQL chunk 0 was returned.

Key lesson:

`top_k=3` means at most three useful results, not exactly three regardless of relevance.

## Reliability experiments

Tested:

- invalid arguments
- unknown tool
- synthetic tool exception
- timeout behavior
- retry policy
- maximum-step termination
- repeated identical tool calls

Important retry lesson:

Permanent errors such as invalid arguments or unknown tools should not be retried.

Transient failures such as network timeouts may be retried when the operation is safe.

Side-effecting operations require idempotency/deduplication before blind retrying.

## Key production lesson

LLM agents should not own application authority.

The LLM may propose the next action, but application code owns:

- allowed tools
- argument validation
- authorization
- execution
- retries
- timeouts
- termination
- no-progress detection
- deterministic fallbacks

More agent autonomy is not automatically better.

For predictable execution paths, deterministic workflows are usually safer, cheaper, faster, and easier to test.

## Current blockers

None.

## Next learning session

**Day 8 — LangGraph + State + Memory + Guardrails + Human-in-the-Loop**

Next exact action:

Replace the manual agent-loop orchestration with an explicit LangGraph state graph while preserving the Day 7 tool safety boundaries.lement safe tool schemas for knowledge search, synthetic log/incident lookup, and service/deployment information, then build a simple deterministic agent/tool loop with argument validation, error handling, and termination rules.