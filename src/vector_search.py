import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class VectorSearch:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.documents: list[str] = []
        self.embeddings = None

    def index(self, documents: list[str]) -> None:
        self.documents = documents

        self.embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

    def search(self, query: str, top_k: int = 3):
        if self.embeddings is None:
            raise ValueError("No documents indexed")

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        scores = np.dot(
            self.embeddings,
            query_embedding,
        )

        ranked_indices = np.argsort(scores)[::-1]

        results = []

        for index in ranked_indices[:top_k]:
            results.append(
                {
                    "text": self.documents[index],
                    "score": float(scores[index]),
                }
            )

        return results


if __name__ == "__main__":
    documents = [
        "PostgreSQL connection pool exhausted and requests are timing out.",
        "TLS certificate expired and clients cannot establish secure connections.",
        "Redis memory usage reached the limit and cache writes are failing.",
        "Authentication service rejects users because the identity provider is unavailable.",
        "Disk usage is at 100 percent and the application cannot write log files.",
    ]

    search_engine = VectorSearch()
    search_engine.index(documents)

    results = search_engine.search(
        "Database connections are unavailable and requests keep timing out",
        top_k=3,
    )

    for result in results:
        print(
            f"{result['score']:.4f} -> {result['text']}"
        )