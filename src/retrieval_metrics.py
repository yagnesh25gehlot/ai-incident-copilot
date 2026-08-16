from typing import Sequence


ChunkKey = tuple[str, int]


def precision_at_k(
    retrieved: Sequence[ChunkKey],
    relevant: set[ChunkKey],
    k: int,
) -> float:
    top_k = retrieved[:k]

    if not top_k:
        return 0.0

    relevant_retrieved = sum(
        1
        for item in top_k
        if item in relevant
    )

    return relevant_retrieved / len(top_k)


def recall_at_k(
    retrieved: Sequence[ChunkKey],
    relevant: set[ChunkKey],
    k: int,
) -> float:
    if not relevant:
        return 0.0

    top_k = retrieved[:k]

    relevant_retrieved = sum(
        1
        for item in top_k
        if item in relevant
    )

    return relevant_retrieved / len(relevant)


def reciprocal_rank(
    retrieved: Sequence[ChunkKey],
    relevant: set[ChunkKey],
) -> float:
    for rank, item in enumerate(
        retrieved,
        start=1,
    ):
        if item in relevant:
            return 1.0 / rank

    return 0.0



import math

def dcg_at_k(
    retrieved: Sequence[ChunkKey],
    relevant: set[ChunkKey],
    k: int,
) -> float:
    score = 0.0

    for rank, item in enumerate(
        retrieved[:k],
        start=1,
    ):
        relevance = 1.0 if item in relevant else 0.0

        score += relevance / math.log2(rank + 1)

    return score

def ndcg_at_k(
    retrieved: Sequence[ChunkKey],
    relevant: set[ChunkKey],
    k: int,
) -> float:
    if not relevant:
        return 0.0

    actual_dcg = dcg_at_k(
        retrieved,
        relevant,
        k,
    )

    ideal_relevant_count = min(
        len(relevant),
        k,
    )

    ideal_dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(
            1,
            ideal_relevant_count + 1,
        )
    )

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg



if __name__ == "__main__":
    retrieved = [
        ("tls_runbook.md", 0),
        ("postgres_runbook.md", 1),
        ("redis_incident.md", 0),
    ]

    relevant = {
        ("postgres_runbook.md", 0),
        ("postgres_runbook.md", 1),
    }

    print(
        "Precision@3:",
        precision_at_k(
            retrieved,
            relevant,
            k=3,
        ),
    )

    print(
        "Recall@3:",
        recall_at_k(
            retrieved,
            relevant,
            k=3,
        ),
    )

    print(
        "Reciprocal Rank:",
        reciprocal_rank(
            retrieved,
            relevant,
        ),
    )

    print(
        "NDCG@3:",
        ndcg_at_k(
            retrieved,
            relevant,
            k=3,
        ),
    )








