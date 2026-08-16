# EXPERIMENT LOG

Do not invent numbers. Record only experiments actually executed.

Use this template.

---

## EXP-XXX — <title>

**Date:**  
**Question:**  
**Hypothesis:**  

### Setup

- dataset:
- model:
- retrieval configuration:
- relevant parameters:

### Result

| Variant | Metric | Result |
|---|---|---|
| | | |

### What failed / surprised us

-

### Decision

-

### Interview story

> Problem -> experiment -> evidence -> decision -> tradeoff
> 
> 
> 


# Day 6 — RAG Evaluation and AI Regression Testing

## Goal

Move from subjective inspection of RAG quality to measurable offline evaluation.

Evaluation was split into:

1. retrieval evaluation
2. deterministic answer-behavior evaluation
3. experimental semantic answer evaluation

---

## Golden retrieval dataset

Created:

`data/eval/retrieval_eval.json`

The dataset contains manually labeled queries and relevant chunk IDs.

Golden labels are independent of retriever output.

This avoids circular evaluation where a retriever's own prediction becomes its expected answer.

---

## Retrieval metrics implemented

Implemented manually:

- Precision@K
- Recall@K
- Reciprocal Rank
- Mean Reciprocal Rank
- DCG
- NDCG@K

Implemented in:

`src/retrieval_metrics.py`

### Metric interpretation

Precision@K:

How much of the retrieved top-k is relevant?

Recall@K:

How much of all known relevant evidence was retrieved?

MRR:

How early does the first relevant result appear?

NDCG:

How good is the ordering of relevant results throughout the ranked list?

---

## Retrieval benchmark

Compared:

- BM25
- dense retrieval
- hybrid RRF
- hybrid + cross-encoder reranker

Final average results:

| Method | P@3 | R@3 | MRR | NDCG@3 |
|---|---:|---:|---:|---:|
| BM25 | 0.500 | 0.875 | 0.875 | 0.875 |
| Dense | 0.542 | 0.938 | 1.000 | 0.942 |
| Hybrid RRF | 0.542 | 0.938 | 0.938 | 0.913 |
| Hybrid + reranker | 0.583 | 1.000 | 1.000 | 0.990 |

Observation:

Hybrid retrieval alone was not automatically better than dense retrieval.

For the semantic query:

`Why can't the service acquire a DB slot?`

BM25 failed completely.

Dense retrieval correctly retrieved PostgreSQL chunks.

Plain RRF allowed poor lexical rankings to hurt the final ordering.

The cross-encoder reranker recovered the correct ranking.

Key lesson:

Adding more retrieval components does not guarantee better quality. Each configuration must be evaluated.

---

## Answer evaluation

Created:

`data/eval/answer_eval.json`

Evaluated:

- retrieved-source citation validity
- expected-source recall
- supported-query answer behavior
- unsupported-query abstention behavior

Unsupported example:

`Why is Kafka consumer lag increasing in the order service?`

The corpus has no supporting evidence for this question.

---

## LLM-as-judge experiment

Implemented:

`src/llm_judge.py`

Judge model:

`Qwen2.5-0.5B-Instruct`

The judge was tested with:

1. correct answer
2. hallucinated answer
3. partially hallucinated answer

The judge failed to reliably identify unsupported claims.

It incorrectly marked hallucinated answers as correct and faithful.

Conclusion:

The local 0.5B model is not reliable enough to act as the primary semantic answer evaluator.

LLM-as-judge is therefore retained as an experimental component only.

Semantic correctness currently requires human review or a stronger calibrated evaluator.

---

## Reranker relevance-threshold experiment

Problem:

Even when the correct chunk ranked first, irrelevant low-ranked chunks were included in the LLM context and sometimes distracted the small generator.

Observed reranker scores included:

Relevant examples:

- PostgreSQL: `3.9629`
- PostgreSQL: `8.3648`
- Redis: `5.5895`
- TLS: `0.8254`
- TLS continuation: `-1.0091`

Unsupported Kafka candidates:

- `-10.6208`
- `-11.2761`
- `-11.4514`

Added experimental threshold:

`MIN_RERANK_SCORE = -2.0`

Candidates below the threshold are excluded from generation context.

Important:

`-2.0` is not a universal cross-encoder threshold.

It is only a learning baseline derived from the current small evaluation dataset.

---

## Deterministic abstention

If no reranked candidate passes the relevance threshold:

`filtered_candidates == []`

the application does not call the LLM.

It deterministically returns:

`Insufficient evidence in knowledge base.`

This fixed the unsupported Kafka hallucination.

Architecture:

`query`

→ hybrid retrieval

→ cross-encoder reranking

→ relevance threshold

→ relevant candidates?

- yes → LLM generation
- no → deterministic abstention

---

## Final deterministic answer metrics

Observed:

- retrieved-source citation validity: `1.000`
- expected-source recall: `1.000`
- abstention accuracy: `1.000`
- supported-query answer rate: `1.000`
- unsupported-query abstention rate: `1.000`

Important limitation:

These values do not imply semantic answer correctness is 100%.

A generated answer can cite a valid source while still misunderstanding or incompletely answering the question.

---

## AI regression gate

Implemented:

`src/regression_gate.py`

Current retrieval thresholds:

- Precision@3 >= `0.55`
- Recall@3 >= `0.95`
- MRR >= `0.95`
- NDCG@3 >= `0.90`

Current answer-behavior thresholds:

- citation validity >= `1.0`
- expected-source recall >= `1.0`
- abstention accuracy >= `1.0`
- supported-answer rate >= `1.0`
- unsupported-abstention rate >= `1.0`

The gate runs both evaluators and exits:

- `0` when metrics pass
- `1` when a regression occurs

Latest execution:

`AI REGRESSION GATE RESULT: PASSED`

Process exit code:

`0`

---

## Key Day 6 lessons

1. Retrieval quality must be measured rather than judged by a few examples.
2. Recall and MRR measure different behavior.
3. NDCG distinguishes rankings that have identical recall and MRR.
4. Hybrid retrieval is not automatically superior.
5. Good retrieval does not guarantee good generation.
6. Valid citations do not guarantee factual correctness.
7. Structured output can be schema-valid but semantically inconsistent.
8. LLM-as-judge is itself an AI system with failure modes.
9. Deterministic checks should be preferred where possible.
10. Unsupported questions need explicit evaluation.
11. Retrieval thresholds can provide deterministic abstention.
12. AI metrics can become CI quality gates through process exit codes.

---

## Remaining limitations

- evaluation datasets are very small
- labels are manually created
- threshold calibration is weak
- semantic answer correctness is not automatically gated
- local judge is too weak for reliable faithfulness evaluation
- no statistical confidence analysis yet
- no experiment tracking system such as MLflow yet
- no latency/cost benchmark in the regression gate yet

These are accepted learning-project limitations.
