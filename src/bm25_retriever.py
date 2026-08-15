from rank_bm25 import BM25Okapi

from ingestion import Chunk, ingest_directory


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("BM25Retriever requires at least one chunk")

        self.chunks = chunks

        self.tokenized_corpus = [
            self._tokenize(chunk.text)
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[Chunk, float]]:

        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        return [
            (self.chunks[i], float(scores[i]))
            for i in ranked_indices[:top_k]
        ]


if __name__ == "__main__":
    chunks = ingest_directory("data/knowledge")

    retriever = BM25Retriever(chunks)

    queries = [
        "PostgreSQL connection pool exhausted",
        "Why are payment API requests timing out because the database has no free connections?",
        "INC-REDIS-7421",
    ]

    for query in queries:
        print("=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = retriever.search(query, top_k=3)

        for rank, (chunk, score) in enumerate(results, start=1):
            print(
                f"Rank {rank} | "
                f"score={score:.4f} | "
                f"source={chunk.source} | "
                f"chunk={chunk.chunk_id}"
            )

            print(chunk.text)
            print()