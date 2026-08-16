from evaluate_rag_answers import main as evaluate_rag_answers
from evaluate_retrieval import main as evaluate_retrieval


# ============================================================
# Regression thresholds
# ============================================================

# These are learning-project thresholds based on the current
# evaluation baseline. They are NOT universal production values.

RETRIEVAL_THRESHOLDS = {
    "precision_at_3": 0.55,
    "recall_at_3": 0.95,
    "mrr": 0.95,
    "ndcg_at_3": 0.90,
}


ANSWER_THRESHOLDS = {
    "citation_validity": 1.0,
    "expected_source_recall": 1.0,
    "abstention_accuracy": 1.0,
    "supported_answer_rate": 1.0,
    "unsupported_abstention_rate": 1.0,
}


def check_thresholds(
    category: str,
    actual: dict[str, float],
    thresholds: dict[str, float],
) -> list[str]:

    failures = []

    print()
    print("=" * 100)
    print(f"{category} REGRESSION CHECK")
    print("=" * 100)

    for metric, minimum in thresholds.items():

        value = actual[metric]

        passed = value >= minimum

        status = "PASS" if passed else "FAIL"

        print(
            f"{metric:35} "
            f"actual={value:.3f} | "
            f"minimum={minimum:.3f} | "
            f"{status}"
        )

        if not passed:
            failures.append(
                f"{category}: "
                f"{metric}={value:.3f} "
                f"< required {minimum:.3f}"
            )

    return failures


def main():

    print()
    print("#" * 100)
    print("RUNNING AI REGRESSION EVALUATION")
    print("#" * 100)

    # ========================================================
    # Retrieval evaluation
    # ========================================================

    retrieval_results = evaluate_retrieval()

    production_retrieval = (
        retrieval_results["hybrid_reranker"]
    )

    # ========================================================
    # RAG answer evaluation
    # ========================================================

    answer_results = evaluate_rag_answers()

    # ========================================================
    # Apply regression thresholds
    # ========================================================

    failures = []

    failures.extend(
        check_thresholds(
            category="RETRIEVAL",
            actual=production_retrieval,
            thresholds=RETRIEVAL_THRESHOLDS,
        )
    )

    failures.extend(
        check_thresholds(
            category="ANSWER",
            actual=answer_results,
            thresholds=ANSWER_THRESHOLDS,
        )
    )

    # ========================================================
    # Final gate result
    # ========================================================

    print()
    print("=" * 100)
    print("AI REGRESSION GATE RESULT")
    print("=" * 100)

    if failures:

        print("FAILED")
        print()

        for failure in failures:
            print(f"- {failure}")

        raise SystemExit(1)

    print("PASSED")

    raise SystemExit(0)


if __name__ == "__main__":
    main()