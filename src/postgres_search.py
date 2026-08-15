from sentence_transformers import SentenceTransformer

from vector_store import PgVectorStore


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    model = SentenceTransformer(EMBEDDING_MODEL)

    question = "Why are payment API requests timing out?"

    query_embedding = model.encode(
        question,
        normalize_embeddings=True,
    )

    store = PgVectorStore()

    results = store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    for source, chunk_id, content, similarity in results:
        print(
            f"{similarity:.4f} | "
            f"{source} | "
            f"chunk={chunk_id}"
        )

        print(content)
        print("-" * 80)

        filtered_results = store.search_by_source(
            query_embedding=query_embedding,
            source="postgres_runbook.md",
            top_k=3,
        )

        print("\nFILTERED RESULTS\n")

        for source, chunk_id, content, similarity in filtered_results:
            print(
                f"{similarity:.4f} | "
                f"{source} | "
                f"chunk={chunk_id}"
            )


if __name__ == "__main__":
    main()