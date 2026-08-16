import json
from pathlib import Path

import httpx
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from answer_metrics import (
    citation_precision,
    expected_source_recall,
)
from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from ingestion import ingest_directory
from reranker import CrossEncoderReranker
from vector_store import PgVectorStore


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"
EVAL_FILE = PROJECT_ROOT / "data" / "eval" / "answer_eval.json"

BASE_URL = "http://127.0.0.1:8080"
MODEL = "local-qwen"

ABSTENTION_TEXT = "Insufficient evidence in knowledge base."

# Experimental threshold based on the current tiny evaluation set.
# This is NOT a universal cross-encoder threshold.
MIN_RERANK_SCORE = -2.0


# ============================================================
# Structured RAG response
# ============================================================

class RAGAnswer(BaseModel):
    answer: str
    citations: list[str]
    abstained: bool


# ============================================================
# Load evaluation dataset
# ============================================================

def load_eval_dataset():
    with open(EVAL_FILE, "r") as f:
        return json.load(f)


# ============================================================
# Clean JSON returned by LLM
# ============================================================

def clean_json_response(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):]

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


# ============================================================
# Normalize semantically inconsistent LLM output
# ============================================================

def normalize_answer(answer: RAGAnswer) -> RAGAnswer:
    """
    Fix cases such as:

    {
        "answer": "Insufficient evidence in knowledge base.",
        "citations": [],
        "abstained": false
    }

    This is schema-valid but semantically inconsistent.
    """

    text_abstained = (
        answer.answer.strip().lower()
        == ABSTENTION_TEXT.lower()
    )

    if text_abstained or answer.abstained:
        answer.answer = ABSTENTION_TEXT
        answer.citations = []
        answer.abstained = True

    return answer


# ============================================================
# Generate answer using local Qwen
# ============================================================

def generate_answer(
    question: str,
    context: str,
    allowed_sources: set[str],
) -> RAGAnswer:

    system_prompt = """
You answer questions using only the supplied context.

IMPORTANT:

If the supplied context directly contains information that answers the
question, you MUST answer the question.

Only abstain when the supplied context does not contain enough relevant
information to answer the question.

Do not require extra information beyond what the question asks.

SUPPORTED EXAMPLE:

Question:
Why are API requests timing out?

Context:
SOURCE: postgres_runbook.md
The PostgreSQL connection pool is exhausted.
Requests wait for available database connections and eventually time out.

Correct output:
{
  "answer": "The API requests are timing out because the PostgreSQL connection pool is exhausted, so requests wait for available database connections.",
  "citations": ["postgres_runbook.md"],
  "abstained": false
}

UNSUPPORTED EXAMPLE:

Question:
Why is Kafka consumer lag increasing?

Context:
SOURCE: postgres_runbook.md
A PostgreSQL connection pool was exhausted.

Correct output:
{
  "answer": "Insufficient evidence in knowledge base.",
  "citations": [],
  "abstained": true
}

RULES:

- Use only the supplied context.
- Do not use outside knowledge.
- Do not invent facts.
- If the context answers the question, do NOT abstain.
- Cite only filenames shown in SOURCE fields.
- Cite only sources that support the answer.
- If you abstain, citations must be [].
- Return ONLY valid JSON.

Return exactly this structure:

{
  "answer": "answer text",
  "citations": ["source.md"],
  "abstained": false
}
"""

    user_prompt = f"""
QUESTION:
{question}

CONTEXT:
{context}

Answer the QUESTION using only the CONTEXT above.
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": 0.0,
        "max_tokens": 250,
    }

    with httpx.Client(
        trust_env=False,
        timeout=60.0,
    ) as client:

        response = client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
        )

        response.raise_for_status()

    raw_text = (
        response.json()["choices"][0]["message"]["content"]
    )

    parsed = json.loads(
        clean_json_response(raw_text)
    )

    answer = RAGAnswer.model_validate(parsed)

    # --------------------------------------------------------
    # Deterministic citation protection
    # --------------------------------------------------------

    answer.citations = [
        source
        for source in answer.citations
        if source in allowed_sources
    ]

    # --------------------------------------------------------
    # Enforce abstention consistency
    # --------------------------------------------------------

    answer = normalize_answer(answer)

    return answer


# ============================================================
# Main evaluation
# ============================================================

def main():

    # --------------------------------------------------------
    # Load evaluation data
    # --------------------------------------------------------

    eval_dataset = load_eval_dataset()

    chunks = ingest_directory(KNOWLEDGE_DIR)

    if not chunks:
        raise RuntimeError(
            f"No knowledge chunks found in {KNOWLEDGE_DIR}"
        )

    # --------------------------------------------------------
    # Build retrieval pipeline
    # --------------------------------------------------------

    bm25 = BM25Retriever(chunks)

    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = PgVectorStore()

    hybrid = HybridRetriever(
        bm25_retriever=bm25,
        vector_store=vector_store,
        embedding_model=embedding_model,
    )

    reranker = CrossEncoderReranker()

    # --------------------------------------------------------
    # Metric accumulators
    # --------------------------------------------------------

    total_citation_precision = 0.0
    total_expected_source_recall = 0.0

    answered_count = 0

    correct_abstentions = 0

    supported_queries = 0
    supported_queries_answered = 0

    unsupported_queries = 0
    unsupported_queries_abstained = 0

    # ========================================================
    # Evaluate each question
    # ========================================================

    for item in eval_dataset:

        question = item["question"]

        reference_answer = item["reference_answer"]

        expected_sources = set(
            item["expected_sources"]
        )

        should_answer = item["should_answer"]

        if should_answer:
            supported_queries += 1
        else:
            unsupported_queries += 1

        # ====================================================
        # Step 1: Hybrid candidate generation
        # ====================================================

        hybrid_candidates = hybrid.search(
            question,
            top_k=5,
            candidate_k=5,
        )

        # ====================================================
        # Step 2: Cross-encoder reranking
        # ====================================================

        reranked = reranker.rerank(
            question,
            hybrid_candidates,
            top_k=3,
        )

        # ====================================================
        # Step 3: Relevance threshold
        # ====================================================

        filtered_candidates = [
            result
            for result in reranked
            if result[4] >= MIN_RERANK_SCORE
        ]

        # ====================================================
        # Print retrieval debugging information
        # ====================================================

        print()
        print("=" * 100)
        print(f"QUESTION: {question}")
        print("=" * 100)

        print()
        print("RERANKED CHUNKS:")

        for (
            source,
            chunk_id,
            text,
            rrf_score,
            rerank_score,
        ) in reranked:

            print(
                f"{source} | "
                f"chunk={chunk_id} | "
                f"rerank={rerank_score:.4f} | "
                f"RRF={rrf_score:.6f}"
            )

        print()
        print(
            f"FILTERED CONTEXT "
            f"(rerank >= {MIN_RERANK_SCORE}):"
        )

        if not filtered_candidates:
            print(
                "No candidate passed the relevance threshold."
            )

        else:
            for (
                source,
                chunk_id,
                text,
                rrf_score,
                rerank_score,
            ) in filtered_candidates:

                print(
                    f"{source} | "
                    f"chunk={chunk_id} | "
                    f"rerank={rerank_score:.4f}"
                )

        # ====================================================
        # Step 4: Deterministic abstention or LLM generation
        # ====================================================

        if not filtered_candidates:

            retrieved_sources = set()

            answer = RAGAnswer(
                answer=ABSTENTION_TEXT,
                citations=[],
                abstained=True,
            )

        else:

            retrieved_sources = {
                source
                for (
                    source,
                    chunk_id,
                    text,
                    rrf_score,
                    rerank_score,
                )
                in filtered_candidates
            }

            context_parts = []

            for (
                source,
                chunk_id,
                text,
                rrf_score,
                rerank_score,
            ) in filtered_candidates:

                context_parts.append(
                    f"""
SOURCE: {source}
CHUNK: {chunk_id}

{text}
"""
                )

            context = "\n\n".join(context_parts)

            answer = generate_answer(
                question=question,
                context=context,
                allowed_sources=retrieved_sources,
            )

        # ====================================================
        # Step 5: Deterministic evaluation
        # ====================================================

        citation_p = citation_precision(
            answer.citations,
            retrieved_sources,
        )

        expected_recall = expected_source_recall(
            answer.citations,
            expected_sources,
        )

        expected_abstention = not should_answer

        abstention_correct = (
            answer.abstained
            == expected_abstention
        )

        if abstention_correct:
            correct_abstentions += 1

        # ----------------------------------------------------
        # Citation metrics are meaningful only for answers
        # ----------------------------------------------------

        if not answer.abstained:

            total_citation_precision += citation_p

            total_expected_source_recall += (
                expected_recall
            )

            answered_count += 1

        # ----------------------------------------------------
        # Supported query behavior
        # ----------------------------------------------------

        if should_answer and not answer.abstained:
            supported_queries_answered += 1

        # ----------------------------------------------------
        # Unsupported query behavior
        # ----------------------------------------------------

        if (
            not should_answer
            and answer.abstained
        ):
            unsupported_queries_abstained += 1

        # ====================================================
        # Human-review output
        # ====================================================

        print()
        print(f"REFERENCE: {reference_answer}")

        print()
        print(f"GENERATED: {answer.answer}")

        print()
        print(f"CITATIONS: {answer.citations}")

        print(
            f"Retrieved-source citation validity: "
            f"{citation_p:.3f}"
        )

        print(
            f"Expected source recall: "
            f"{expected_recall:.3f}"
        )

        print(
            f"Abstention expected: "
            f"{expected_abstention}"
        )

        print(
            f"Abstained: "
            f"{answer.abstained}"
        )

        print(
            f"Abstention correct: "
            f"{abstention_correct}"
        )

    # ========================================================
    # Final aggregate results
    # ========================================================

    n = len(eval_dataset)

    print()
    print("=" * 100)
    print("FINAL DETERMINISTIC ANSWER RESULTS")
    print("=" * 100)

    # --------------------------------------------------------
    # Citation metrics
    # --------------------------------------------------------

    if answered_count > 0:

        avg_citation_precision = (
            total_citation_precision
            / answered_count
        )

        avg_expected_source_recall = (
            total_expected_source_recall
            / answered_count
        )

    else:

        avg_citation_precision = 0.0
        avg_expected_source_recall = 0.0

    print(
        "Average retrieved-source citation validity "
        "on answered queries:",
        round(
            avg_citation_precision,
            3,
        ),
    )

    print(
        "Average expected-source recall "
        "on answered queries:",
        round(
            avg_expected_source_recall,
            3,
        ),
    )

    # --------------------------------------------------------
    # Overall abstention accuracy
    # --------------------------------------------------------

    abstention_accuracy = (
        correct_abstentions / n
        if n
        else 0.0
    )

    print(
        "Abstention accuracy:",
        round(
            abstention_accuracy,
            3,
        ),
    )

    # --------------------------------------------------------
    # Supported query answer rate
    # --------------------------------------------------------

    supported_answer_rate = (
        supported_queries_answered
        / supported_queries
        if supported_queries
        else 0.0
    )

    print(
        "Supported-query answer rate:",
        round(
            supported_answer_rate,
            3,
        ),
    )

    # --------------------------------------------------------
    # Unsupported query abstention rate
    # --------------------------------------------------------

    unsupported_abstention_rate = (
        unsupported_queries_abstained
        / unsupported_queries
        if unsupported_queries
        else 0.0
    )

    print(
        "Unsupported-query abstention rate:",
        round(
            unsupported_abstention_rate,
            3,
        ),
    )


    final_results = {
        "citation_validity": avg_citation_precision,
        "expected_source_recall": avg_expected_source_recall,
        "abstention_accuracy": abstention_accuracy,
        "supported_answer_rate": supported_answer_rate,
        "unsupported_abstention_rate": unsupported_abstention_rate,
    }

    return final_results


if __name__ == "__main__":
    main()