# EXPERIMENTS

# Day 5 — BM25, Hybrid Retrieval, and Reranking

## Goal

Compare four retrieval strategies:

1. BM25 lexical retrieval
2. Dense semantic retrieval using MiniLM + pgvector
3. Hybrid retrieval using Reciprocal Rank Fusion (RRF)
4. Hybrid retrieval followed by a cross-encoder reranker

The purpose was to understand retrieval failure modes rather than assume one retrieval strategy is universally best.

---

## Retrieval configuration

### BM25

Library:

`rank-bm25`

Retriever:

`BM25Okapi`

Current tokenization:

`text.lower().split()`

This tokenizer is intentionally simple and may treat punctuation as part of tokens.

---

### Dense retrieval

Embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

Embedding dimension:

`384`

Embeddings:

normalized

Storage/search:

PostgreSQL + pgvector

Similarity:

cosine similarity

ANN index:

HNSW

---

### Hybrid retrieval

Fusion method:

Reciprocal Rank Fusion (RRF)

Current RRF constant:

`k = 60`

Candidate retrieval:

- BM25 top candidates
- dense top candidates

RRF combines rank positions rather than directly adding BM25 and cosine scores.

Formula:

`RRF(d) = Σ 1 / (k + rank(d))`

---

### Reranker

Model:

`cross-encoder/ms-marco-MiniLM-L-6-v2`

Architecture:

Cross-encoder

The query and candidate chunk are processed together to produce a relevance score.

The cross-encoder is only applied to retrieved candidates rather than the entire corpus.

---

# Experiment 1 — Lexical PostgreSQL query

Query:

`PostgreSQL connection pool exhausted`

BM25 correctly ranked PostgreSQL chunks at the top.

Observed BM25 top scores:

- PostgreSQL chunk 0: `3.0877`
- PostgreSQL chunk 1: `2.1187`
- PostgreSQL chunk 2: `0.3814`

Dense retrieval also correctly retrieved PostgreSQL chunks.

Observation:

Both lexical and dense retrieval work well when the query has strong lexical overlap and clear semantic similarity with the source material.

---

# Experiment 2 — Natural-language PostgreSQL query

Query:

`Why are payment API requests timing out because the database has no free connections?`

BM25 still performed strongly.

Observed BM25:

- PostgreSQL chunk 0: `6.3445`
- PostgreSQL chunk 1: `3.5701`
- TLS chunk 0: `1.1536`

Dense retrieval:

- PostgreSQL chunk 0: `0.5517`
- PostgreSQL chunk 1: `0.3824`
- TLS chunk 0: `0.2906`

Observation:

This query initially appeared to be a semantic-paraphrase test, but it still contained significant lexical overlap such as:

- payment
- API
- requests
- database
- connections
- timeout

Therefore BM25 also performed well.

Key lesson:

BM25 does not automatically fail on natural-language questions. It becomes weaker when relevant documents use different vocabulary from the query.

---

# Experiment 3 — Exact identifier

Query:

`INC-REDIS-7421`

BM25:

- Redis chunk 1: `0.9869`
- Redis chunk 0: `0.6726`
- PostgreSQL chunk 0: `0.0000`

Dense retrieval:

- Redis chunk 0: `0.5082`
- Redis chunk 1: `0.4060`
- PostgreSQL chunk 2: `0.1433`

Observation:

Both methods found Redis, but BM25 produced a strong lexical signal for the exact incident identifier.

The shorter Redis chunk received a higher BM25 score despite both chunks containing the identifier.

This demonstrated BM25 document-length normalization.

Key lesson:

Exact identifiers, error codes, hostnames, product names, and similar tokens are strong use cases for lexical retrieval.

---

# Experiment 4 — Semantic paraphrase with weak lexical overlap

Query:

`Why can't the service acquire a DB slot?`

BM25 results:

1. TLS
2. TLS
3. Redis

Dense results:

1. PostgreSQL chunk 0: `0.3080`
2. PostgreSQL chunk 2: `0.2945`
3. PostgreSQL chunk 1: `0.2588`

Observation:

BM25 failed because the query phrase:

`acquire a DB slot`

has little lexical overlap with terms such as:

`PostgreSQL connection pool exhausted`

Dense retrieval correctly associated the semantic concepts.

This provided the concrete failure case that justified hybrid retrieval.

---

# Experiment 5 — Reciprocal Rank Fusion

BM25 and dense scores were not directly combined because they have incompatible score scales.

Example:

BM25 scores may be:

`6.3445`

while cosine similarity may be:

`0.5517`

Directly adding them would allow the BM25 numerical scale to dominate.

RRF therefore combines rank positions instead.

For the semantic DB-slot query, hybrid RRF returned approximately:

1. Redis
2. PostgreSQL
3. Redis

Observation:

RRF preserved candidates from both lexical and dense retrieval, but fusion did not automatically produce the best final ranking.

Key lesson:

Hybrid retrieval can improve candidate recall without guaranteeing optimal precision.

---

# Experiment 6 — Cross-encoder reranking

Query:

`Why can't the service acquire a DB slot?`

After reranking:

1. PostgreSQL chunk 1 — reranker score `-10.5761`
2. Redis chunk 0 — reranker score `-10.6054`
3. PostgreSQL chunk 0 — reranker score `-10.6302`

The reranker promoted PostgreSQL to rank 1.

However, the score difference between the top PostgreSQL and Redis candidates was small.

Difference:

approximately `0.0293`

Observation:

The reranker corrected the top-ranked source in this example, but the margin was weak.

Therefore this experiment alone is not sufficient evidence that the reranker consistently improves retrieval.

Day 6 evaluation will measure retrieval quality across multiple labeled queries.

---

# Key lessons

## Dense vs lexical

BM25 is strong when query/document terms overlap strongly, especially for:

- identifiers
- error codes
- hostnames
- product names
- exact phrases

Dense retrieval is strong when query and document express similar meaning with different vocabulary.

---

## Hybrid search

Hybrid search attempts to benefit from both lexical and semantic retrieval.

It primarily improves candidate coverage/recall.

It does not guarantee that the final ranking is optimal.

---

## Why RRF

BM25 scores and cosine similarity scores are not directly comparable.

RRF uses ranks rather than raw scores, avoiding naive score-scale problems.

---

## Retrieval vs reranking

Candidate retrieval should emphasize recall:

`large corpus -> BM25/dense -> candidate set`

Reranking should emphasize precision:

`candidate set -> cross-encoder -> final top-k`

---

## Why not cross-encode the full corpus

A dense retriever can precompute document embeddings and efficiently search them.

A cross-encoder must jointly process:

`query + document`

for every candidate.

Therefore cross-encoding the entire corpus would be much more expensive.

Production pattern:

`large corpus -> cheap retrieval -> small candidate set -> expensive reranking`

---

# Current conclusion

No retrieval method was universally best.

Observed behavior:

- BM25 performed strongly on exact lexical queries.
- Dense retrieval handled weak lexical-overlap semantic queries better.
- RRF combined signals and improved candidate coverage.
- RRF could still rank irrelevant candidates too highly.
- Cross-encoder reranking improved the top result in the semantic DB-slot experiment.
- A larger labeled evaluation set is required before claiming that one configuration is superior.

This motivates Day 6 retrieval evaluation.