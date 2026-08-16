def citation_precision(
    cited_sources: list[str],
    retrieved_sources: set[str],
) -> float:
    if not cited_sources:
        return 0.0

    valid = sum(
        1
        for source in cited_sources
        if source in retrieved_sources
    )

    return valid / len(cited_sources)


def expected_source_recall(
    cited_sources: list[str],
    expected_sources: set[str],
) -> float:
    if not expected_sources:
        return 1.0

    cited = set(cited_sources)

    found = sum(
        1
        for source in expected_sources
        if source in cited
    )

    return found / len(expected_sources)


if __name__ == "__main__":
    retrieved_sources = {
        "postgres_runbook.md",
        "tls_runbook.md",
    }

    cited_sources = [
        "postgres_runbook.md",
        "redis_incident.md",
    ]

    expected_sources = {
        "postgres_runbook.md",
    }

    print(
        "Citation precision:",
        citation_precision(
            cited_sources,
            retrieved_sources,
        ),
    )

    print(
        "Expected source recall:",
        expected_source_recall(
            cited_sources,
            expected_sources,
        ),
    )