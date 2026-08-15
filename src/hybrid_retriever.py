from collections import defaultdict

from sentence_transformers import SentenceTransformer

from bm25_retriever import BM25Retriever
from ingestion import ingest_directory
from vector_store import PgVectorStore


class HybridRetriever:
    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_store: PgVectorStore,
        embedding_model: SentenceTransformer,
        rrf_k: int = 60,
    ):
        self.bm25_retriever = bm25_retriever
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 5,
    ):
        bm25_results = self.bm25_retriever.search(
            query,
            top_k=candidate_k,
        )

        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
        )

        dense_results = self.vector_store.search(
            query_embedding,
            top_k=candidate_k,
        )

        rrf_scores = defaultdict(float)
        documents = {}

        # BM25 results
        for rank, (chunk, score) in enumerate(
            bm25_results,
            start=1,
        ):
            key = (chunk.source, chunk.chunk_id)

            documents[key] = {
                "source": chunk.source,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
            }

            rrf_scores[key] += 1 / (self.rrf_k + rank)

        # Dense results
        for rank, result in enumerate(
            dense_results,
            start=1,
        ):
            source, chunk_id, text, score = result

            key = (source, chunk_id)

            documents[key] = {
                "source": source,
                "chunk_id": chunk_id,
                "text": text,
            }

            rrf_scores[key] += 1 / (self.rrf_k + rank)

        ranked_keys = sorted(
            rrf_scores,
            key=lambda key: rrf_scores[key],
            reverse=True,
        )

        results = []

        for key in ranked_keys[:top_k]:
            document = documents[key]

            results.append(
                (
                    document["source"],
                    document["chunk_id"],
                    document["text"],
                    rrf_scores[key],
                )
            )

        return results


if __name__ == "__main__":
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

    chunks = ingest_directory(KNOWLEDGE_DIR)

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

        results = hybrid.search(
            query,
            top_k=3,
            candidate_k=5,
        )

        for rank, result in enumerate(results, start=1):
            source, chunk_id, text, score = result

            print(
                f"{rank}. "
                f"RRF={score:.6f} | "
                f"{source} | "
                f"chunk={chunk_id}"
            )

        print()