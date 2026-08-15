from pathlib import Path

from ingestion import ingest_directory
from rag import ChunkRetriever
from vector_store import PgVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def main() -> None:
    question = "Why are payment API requests timing out?"

    chunks = ingest_directory(str(KNOWLEDGE_DIR))

    # -------------------------
    # NumPy / in-memory search
    # -------------------------

    memory_retriever = ChunkRetriever()
    memory_retriever.index(chunks)

    memory_results = memory_retriever.search(
        question,
        top_k=3,
        min_score=0.0,
    )

    print("\nIN-MEMORY RESULTS\n")

    for chunk, score in memory_results:
        print(
            f"{score:.4f} | "
            f"{chunk.source} | "
            f"chunk={chunk.chunk_id}"
        )

    # -------------------------
    # PostgreSQL search
    # -------------------------

    query_embedding = memory_retriever.model.encode(
        question,
        normalize_embeddings=True,
    )

    store = PgVectorStore()

    postgres_results = store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    print("\nPOSTGRES RESULTS\n")

    for source, chunk_id, _content, similarity in postgres_results:
        print(
            f"{similarity:.4f} | "
            f"{source} | "
            f"chunk={chunk_id}"
        )


if __name__ == "__main__":
    main()