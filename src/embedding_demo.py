import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_NAME)

    texts = [
        "PostgreSQL connection pool exhausted and requests are timing out.",
        "Database has no free connections remaining.",
        "How do I reset my employee password?",
    ]

    embeddings = model.encode(texts)

    print("Embedding shape:", embeddings.shape)
    print("Embedding dimension:", len(embeddings[0]))

    similarity_ab = cosine_similarity(
        embeddings[0],
        embeddings[1],
    )

    similarity_ac = cosine_similarity(
        embeddings[0],
        embeddings[2],
    )

    print("\n--- Semantic similarity ---")
    print("Database incident vs paraphrase:", similarity_ab)
    print("Database incident vs password query:", similarity_ac)

    normalized_embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    cosine_score = cosine_similarity(
        normalized_embeddings[0],
        normalized_embeddings[1],
    )

    dot_score = np.dot(
        normalized_embeddings[0],
        normalized_embeddings[1],
    )

    print("\n--- Normalization check ---")
    print("Vector A norm:", np.linalg.norm(normalized_embeddings[0]))
    print("Vector B norm:", np.linalg.norm(normalized_embeddings[1]))
    print("Cosine similarity:", cosine_score)
    print("Dot product:", dot_score)