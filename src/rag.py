from pathlib import Path

import httpx
import numpy as np
from sentence_transformers import SentenceTransformer

from ingestion import Chunk, ingest_directory

import json

from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

BASE_URL = "http://127.0.0.1:8080"
MODEL = "local-qwen"


class RAGAnswer(BaseModel):
    answer: str
    citations: list[str]






class ChunkRetriever:
    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.chunks: list[Chunk] = []
        self.embeddings = None

    def index(self, chunks: list[Chunk]) -> None:
        if not chunks:
            raise ValueError("Cannot index an empty chunk list.")

        self.chunks = chunks

        texts = [chunk.text for chunk in chunks]

        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        print(f"Indexed chunks: {len(self.chunks)}")
        print(f"Embedding shape: {self.embeddings.shape}")

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.3,
    ) -> list[tuple[Chunk, float]]:

        if self.embeddings is None:
            raise RuntimeError("Index documents before searching.")

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        scores = self.embeddings @ query_embedding

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            score = float(scores[index])

            if score >= min_score:
                results.append(
                    (
                        self.chunks[index],
                        score,
                    )
                )

        return results


def build_context(
    results: list[tuple[Chunk, float]],
) -> str:

    context_parts = []

    for chunk, _score in results:
        context_parts.append(
            f"[Source: {chunk.source}, Chunk: {chunk.chunk_id}]\n"
            f"{chunk.text}"
        )

    return "\n\n".join(context_parts)


def build_sources(
    results: list[tuple[Chunk, float]],
) -> list[str]:

    sources = []

    for chunk, _score in results:
        if chunk.source not in sources:
            sources.append(chunk.source)

    return sources


def generate_answer(
    question: str,
    context: str,
) -> RAGAnswer:

    system_prompt = """
You are an incident knowledge assistant.

Answer the user's question using only the provided context.

If the context does not contain enough information to answer,
say that the available knowledge does not contain enough information.

Do not invent facts.

Return ONLY valid JSON in this format:

{
  "answer": "your answer",
  "citations": ["source_filename.md"]
}

Only include source filenames that directly support the answer.
"""

    user_prompt = f"""
CONTEXT:

{context}

QUESTION:

{question}
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
        "temperature": 0.1,
        "max_tokens": 200,
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

        data = response.json()

    raw_answer = data["choices"][0]["message"]["content"].strip()

    # Small local models may still wrap JSON in Markdown fences.
    if raw_answer.startswith("```"):
        raw_answer = raw_answer.strip("`")

        if raw_answer.startswith("json"):
            raw_answer = raw_answer[4:]

        raw_answer = raw_answer.strip()

    parsed = json.loads(raw_answer)

    return RAGAnswer.model_validate(parsed)



def validate_citations(
    citations: list[str],
    results: list[tuple[Chunk, float]],
) -> list[str]:

    allowed_sources = {
        chunk.source
        for chunk, _score in results
    }

    return [
        citation
        for citation in citations
        if citation in allowed_sources
    ]

if __name__ == "__main__":

    print(f"Knowledge directory: {KNOWLEDGE_DIR}")

    chunks = ingest_directory(str(KNOWLEDGE_DIR))

    print(f"Loaded chunks: {len(chunks)}")

    retriever = ChunkRetriever()
    retriever.index(chunks)

    question = "Why are payment API requests timing out?"

    results = retriever.search(
        question,
        top_k=3,
        min_score=0.3,
    )

    print("\nRETRIEVED CHUNKS\n")

    for chunk, score in results:
        print(
            f"{score:.4f} | "
            f"{chunk.source} | "
            f"chunk={chunk.chunk_id}"
        )

    if not results:
        print("\nANSWER\n")
        print(
            "The available knowledge does not contain enough "
            "information to answer this question."
        )

    else:
        context = build_context(results)

        rag_answer = generate_answer(
            question=question,
            context=context,
        )

        citations = validate_citations(
            rag_answer.citations,
            results,
        )

        print("\nANSWER\n")
        print(rag_answer.answer)

        print("\nCITATIONS\n")

        for citation in citations:
            print(f"- {citation}")


