from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query: str,
        candidates: list[tuple],
        top_k: int = 3,
    ):
        if not candidates:
            return []

        pairs = [
            (query, candidate[2])
            for candidate in candidates
        ]

        scores = self.model.predict(pairs)

        scored_candidates = []

        for candidate, score in zip(candidates, scores):
            source, chunk_id, text, rrf_score = candidate

            scored_candidates.append(
                (
                    source,
                    chunk_id,
                    text,
                    rrf_score,
                    float(score),
                )
            )

        scored_candidates.sort(
            key=lambda item: item[4],
            reverse=True,
        )

        return scored_candidates[:top_k]




if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer

    from bm25_retriever import BM25Retriever
    from hybrid_retriever import HybridRetriever
    from ingestion import ingest_directory
    from vector_store import PgVectorStore

    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

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
        print("=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        # Important:
        # Retrieve MORE candidates than the final number we need.
        hybrid_candidates = hybrid.search(
            query,
            top_k=5,
            candidate_k=5,
        )

        results = reranker.rerank(
            query,
            hybrid_candidates,
            top_k=3,
        )

        for rank, result in enumerate(results, start=1):
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

        print()