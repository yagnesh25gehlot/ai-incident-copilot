from pathlib import Path

from sentence_transformers import SentenceTransformer

from ingestion import ingest_directory
from vector_store import PgVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    chunks = ingest_directory(str(KNOWLEDGE_DIR))

    print(f"Loaded chunks: {len(chunks)}")

    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [chunk.text for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    print(f"Embedding shape: {embeddings.shape}")

    rows = []

    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            (
                chunk.source,
                chunk.chunk_id,
                chunk.text,
                embedding,
            )
        )

    store = PgVectorStore()

    store.clear()
    store.insert_many(rows)

    print(f"Inserted chunks into PostgreSQL: {len(rows)}")


if __name__ == "__main__":
    main()