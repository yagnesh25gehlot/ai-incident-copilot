from sentence_transformers import SentenceTransformer

from bm25_retriever import BM25Retriever
from ingestion import ingest_directory
from vector_store import PgVectorStore


def main():
    chunks = ingest_directory("data/knowledge")

    bm25 = BM25Retriever(chunks)

    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = PgVectorStore()

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

        print("\nBM25 RESULTS")

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

        print("\nDENSE RESULTS")

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
            print(rank, result)

        print()


if __name__ == "__main__":
    main()