from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


def load_documents(directory: str) -> list[tuple[str, str]]:
    documents = []

    for path in Path(directory).glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append((path.name, text))

    return documents


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 80,
    overlap: int = 20,
) -> list[Chunk]:

    words = text.split()

    chunks = []

    start = 0
    chunk_id = 0

    while start < len(words):
        end = start + chunk_size

        chunk_words = words[start:end]

        chunk = Chunk(
            text=" ".join(chunk_words),
            source=source,
            chunk_id=chunk_id,
        )

        chunks.append(chunk)

        start += chunk_size - overlap
        chunk_id += 1

    return chunks





def ingest_directory(directory: str) -> list[Chunk]:
    documents = load_documents(directory)

    all_chunks = []

    for source, text in documents:
        chunks = chunk_text(
            text=text,
            source=source,
        )

        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    chunks = ingest_directory("data/knowledge")

    for chunk in chunks:
        print("=" * 80)
        print(f"Source: {chunk.source}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(chunk.text)