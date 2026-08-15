from pathlib import Path

from sentence_transformers import SentenceTransformer

from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from ingestion import ingest_directory
from reranker import CrossEncoderReranker
from vector_store import PgVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def print_header(title: str):
    print()
    print(title)
    print("-" * len(title))


def main():
    chunks = ingest_directory(KNOWLEDGE_DIR)

    if not chunks:
        raise RuntimeError(
            f"No knowledge chunks found in {KNOWLEDGE_DIR}"
        )

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

    queries = [
        "PostgreSQL connection pool exhausted",
        "Why are payment API requests timing out because the database has no free connections?",
        "INC-REDIS-7421",
        "Why can't the service acquire a DB slot?",
    ]

    for query in queries:
        print()
        print("=" * 100)
        print(f"QUERY: {query}")
        print("=" * 100)

        # --------------------------------------------------
        # 1. BM25
        # --------------------------------------------------

        print_header("BM25")

        bm25_results = bm25.search(
            query,
            top_k=3,
        )

        for rank, (chunk, score) in enumerate(
            bm25_results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{score:.4f} | "
                f"{chunk.source} | "
                f"chunk={chunk.chunk_id}"
            )

        # --------------------------------------------------
        # 2. Dense
        # --------------------------------------------------

        print_header("DENSE")

        query_embedding = embedding_model.encode(
            query,
            normalize_embeddings=True,
        )

        dense_results = vector_store.search(
            query_embedding,
            top_k=3,
        )

        for rank, result in enumerate(
            dense_results,
            start=1,
        ):
            source, chunk_id, text, score = result

            print(
                f"{rank}. "
                f"{score:.4f} | "
                f"{source} | "
                f"chunk={chunk_id}"
            )

        # --------------------------------------------------
        # 3. Hybrid RRF
        # --------------------------------------------------

        print_header("HYBRID RRF")

        hybrid_results = hybrid.search(
            query,
            top_k=3,
            candidate_k=5,
        )

        for rank, result in enumerate(
            hybrid_results,
            start=1,
        ):
            source, chunk_id, text, score = result

            print(
                f"{rank}. "
                f"{score:.6f} | "
                f"{source} | "
                f"chunk={chunk_id}"
            )

        # --------------------------------------------------
        # 4. Hybrid + Cross-Encoder
        # --------------------------------------------------

        print_header("HYBRID + RERANKER")

        # Give the reranker more candidates than final top-k.
        rerank_candidates = hybrid.search(
            query,
            top_k=5,
            candidate_k=5,
        )

        reranked_results = reranker.rerank(
            query,
            rerank_candidates,
            top_k=3,
        )

        for rank, result in enumerate(
            reranked_results,
            start=1,
        ):
            (
                source,
                chunk_id,
                text,
                rrf_score,
                reranker_score,
            ) = result

            print(
                f"{rank}. "
                f"rerank={reranker_score:.4f} | "
                f"RRF={rrf_score:.6f} | "
                f"{source} | "
                f"chunk={chunk_id}"
            )


if __name__ == "__main__":
    main()