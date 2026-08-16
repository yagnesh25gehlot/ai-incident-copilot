import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from ingestion import ingest_directory
from reranker import CrossEncoderReranker
from vector_store import PgVectorStore
from retrieval_metrics import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"
EVAL_FILE = PROJECT_ROOT / "data" / "eval" / "retrieval_eval.json"


def load_eval_dataset():
    with open(EVAL_FILE, "r") as f:
        return json.load(f)


def evaluate_results(
    retrieved: list[tuple[str, int]],
    relevant: set[tuple[str, int]],
    k: int,
):
    return {
        "precision": precision_at_k(
            retrieved,
            relevant,
            k,
        ),
        "recall": recall_at_k(
            retrieved,
            relevant,
            k,
        ),
        "rr": reciprocal_rank(
            retrieved,
            relevant,
        ),
        "ndcg": ndcg_at_k(
            retrieved,
            relevant,
            k,
        ),
    }


def main():
    chunks = ingest_directory(KNOWLEDGE_DIR)

    if not chunks:
        raise RuntimeError(
            f"No knowledge chunks found in {KNOWLEDGE_DIR}"
        )

    eval_dataset = load_eval_dataset()

    # ---------------------------
    # Build retrieval components
    # ---------------------------

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

    methods = [
        "bm25",
        "dense",
        "hybrid",
        "hybrid_reranker",
    ]

    totals = {
        method: {
            "precision": 0.0,
            "recall": 0.0,
            "rr": 0.0,
            "ndcg": 0.0,
        }
        for method in methods
    }

    k = 3

    # ---------------------------
    # Evaluate every query
    # ---------------------------

    for item in eval_dataset:
        query = item["query"]

        relevant = {
            (source, chunk_id)
            for source, chunk_id in item["relevant"]
        }

        print("=" * 100)
        print(f"QUERY: {query}")
        print(f"RELEVANT: {relevant}")
        print("=" * 100)

        # ==================================================
        # BM25
        # ==================================================

        bm25_results = bm25.search(
            query,
            top_k=k,
        )

        bm25_keys = [
            (chunk.source, chunk.chunk_id)
            for chunk, score in bm25_results
        ]

        bm25_metrics = evaluate_results(
            bm25_keys,
            relevant,
            k,
        )

        # ==================================================
        # Dense
        # ==================================================

        query_embedding = embedding_model.encode(
            query,
            normalize_embeddings=True,
        )

        dense_results = vector_store.search(
            query_embedding,
            top_k=k,
        )

        dense_keys = [
            (source, chunk_id)
            for source, chunk_id, text, score
            in dense_results
        ]

        dense_metrics = evaluate_results(
            dense_keys,
            relevant,
            k,
        )

        # ==================================================
        # Hybrid RRF
        # ==================================================

        hybrid_results = hybrid.search(
            query,
            top_k=k,
            candidate_k=5,
        )

        hybrid_keys = [
            (source, chunk_id)
            for source, chunk_id, text, score
            in hybrid_results
        ]

        hybrid_metrics = evaluate_results(
            hybrid_keys,
            relevant,
            k,
        )

        # ==================================================
        # Hybrid + reranker
        # ==================================================

        candidates = hybrid.search(
            query,
            top_k=5,
            candidate_k=5,
        )

        reranked_results = reranker.rerank(
            query,
            candidates,
            top_k=k,
        )

        reranker_keys = [
            (source, chunk_id)
            for source, chunk_id, text, rrf_score, rerank_score
            in reranked_results
        ]

        reranker_metrics = evaluate_results(
            reranker_keys,
            relevant,
            k,
        )

        query_results = {
            "bm25": bm25_metrics,
            "dense": dense_metrics,
            "hybrid": hybrid_metrics,
            "hybrid_reranker": reranker_metrics,
        }

        # ---------------------------
        # Print per-query results
        # ---------------------------

        for method, metrics in query_results.items():
            print(
                f"{method:18} "
                f"P@{k}={metrics['precision']:.3f} | "
                f"R@{k}={metrics['recall']:.3f} | "
                f"RR={metrics['rr']:.3f} | "
                f"NDCG@{k}={metrics['ndcg']:.3f}"
            )

            totals[method]["precision"] += metrics["precision"]
            totals[method]["recall"] += metrics["recall"]
            totals[method]["rr"] += metrics["rr"]
            totals[method]["ndcg"] += metrics["ndcg"]

        print()

    # ======================================================
    # Aggregate results
    # ======================================================

    num_queries = len(eval_dataset)

    print()
    print("=" * 100)
    print("FINAL AVERAGE RESULTS")
    print("=" * 100)

    final_results = {}

    for method in methods:
        avg_precision = (
                totals[method]["precision"]
                / num_queries
        )

        avg_recall = (
                totals[method]["recall"]
                / num_queries
        )

        mrr = (
                totals[method]["rr"]
                / num_queries
        )

        avg_ndcg = (
                totals[method]["ndcg"]
                / num_queries
        )

        final_results[method] = {
            "precision_at_3": avg_precision,
            "recall_at_3": avg_recall,
            "mrr": mrr,
            "ndcg_at_3": avg_ndcg,
        }

        print(
            f"{method:18} "
            f"P@{k}={avg_precision:.3f} | "
            f"R@{k}={avg_recall:.3f} | "
            f"MRR={mrr:.3f} | "
            f"NDCG@{k}={avg_ndcg:.3f}"
        )

    return final_results









if __name__ == "__main__":
    main()