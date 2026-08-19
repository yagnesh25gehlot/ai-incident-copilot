from typing import Literal

from pydantic import BaseModel, Field

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

class SlowToolArgs(BaseModel):
    sleep_seconds: float = Field(ge=0, le=10)




class RestartServiceArgs(BaseModel):
    service: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z0-9._-]+$",
    )


def restart_service(args: RestartServiceArgs) -> dict:
    """
    Learning-only synthetic high-risk tool.

    IMPORTANT:
    This does NOT restart any real service.
    """

    return {
        "service": args.service,
        "status": "restart-simulated",
        "message": (
            "Learning simulation only. "
            "No real service was restarted."
        ),
    }


def slow_tool(args: SlowToolArgs) -> dict:
    time.sleep(args.sleep_seconds)

    return {
        "message": "Slow tool completed",
        "slept_for": args.sleep_seconds,
    }


MIN_RERANK_SCORE = -2.0
SERVICES = {
    "payment-api": {
        "service": "payment-api",
        "version": "2.4.1",
        "environment": "production",
        "status": "degraded",
        "database": "postgres",
    },
    "order-service": {
        "service": "order-service",
        "version": "1.8.3",
        "environment": "production",
        "status": "healthy",
        "database": "postgres",
    },
    "auth-service": {
        "service": "auth-service",
        "version": "3.1.0",
        "environment": "production",
        "status": "healthy",
        "database": "redis",
    },
}


class SearchKnowledgeArgs(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=5)


class SearchIncidentsArgs(BaseModel):
    service: str = Field(min_length=1)
    severity: Literal["low", "medium", "high", "critical"] | None = None
    limit: int = Field(default=5, ge=1, le=10)


class GetServiceInfoArgs(BaseModel):
    service: str = Field(min_length=1)


class FailureTestArgs(BaseModel):
    message: str = "test"


def failure_test(args: FailureTestArgs) -> dict:
    raise RuntimeError("Synthetic tool failure")

def get_service_info(args: GetServiceInfoArgs) -> dict:
    service = SERVICES.get(args.service)

    if service is None:
        return {
            "found": False,
            "error": f"Unknown service: {args.service}",
        }

    return {
        "found": True,
        "service": service,
    }

INCIDENTS = [
    {
        "incident_id": "INC-1001",
        "service": "payment-api",
        "severity": "high",
        "message": "Payment API requests timing out due to PostgreSQL connection pool exhaustion.",
    },
    {
        "incident_id": "INC-1002",
        "service": "payment-api",
        "severity": "medium",
        "message": "Payment API latency increased after deployment version 2.4.1.",
    },
    {
        "incident_id": "INC-1003",
        "service": "order-service",
        "severity": "critical",
        "message": "Order processing stopped because Kafka consumer lag exceeded threshold.",
    },
    {
        "incident_id": "INC-1004",
        "service": "auth-service",
        "severity": "medium",
        "message": "Authentication latency increased because Redis response time increased.",
    },
]


def search_incidents(args: SearchIncidentsArgs) -> dict:
    matches = []

    for incident in INCIDENTS:
        if incident["service"] != args.service:
            continue

        if args.severity is not None:
            if incident["severity"] != args.severity:
                continue

        matches.append(incident)

        if len(matches) >= args.limit:
            break

    return {
        "count": len(matches),
        "incidents": matches,
    }


def search_knowledge(args: SearchKnowledgeArgs) -> dict:
    hybrid, reranker = get_knowledge_retrieval_stack()

    retrieval_k = max(args.top_k, 5)

    candidates = hybrid.search(
        args.query,
        top_k=retrieval_k,
        candidate_k=5,
    )

    reranked_results = reranker.rerank(
        args.query,
        candidates,
        top_k=retrieval_k,
    )

    filtered_results = [
        result
        for result in reranked_results
        if result[4] >= MIN_RERANK_SCORE
    ]

    filtered_results = filtered_results[:args.top_k]

    results = []

    for (
        source,
        chunk_id,
        text,
        rrf_score,
        reranker_score,
    ) in filtered_results:
        results.append(
            {
                "source": source,
                "chunk_id": chunk_id,
                "text": text,
                "rrf_score": rrf_score,
                "reranker_score": reranker_score,
            }
        )

    return {
        "query": args.query,
        "count": len(results),
        "results": results,
    }


TOOL_REGISTRY = {
    "search_knowledge": {
        "args_model": SearchKnowledgeArgs,
        "function": search_knowledge,
    },
    "search_incidents": {
        "args_model": SearchIncidentsArgs,
        "function": search_incidents,
    },
    "get_service_info": {
        "args_model": GetServiceInfoArgs,
        "function": get_service_info,
    },
    "restart_service": {
        "args_model": RestartServiceArgs,
        "function": restart_service,
    },
}





def execute_tool(tool_name: str, raw_arguments: dict) -> dict:
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        return {
            "ok": False,
            "error": f"Unknown tool: {tool_name}",
        }

    args_model = tool["args_model"]
    function = tool["function"]

    try:
        validated_args = args_model.model_validate(raw_arguments)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Invalid tool arguments: {exc}",
        }

    try:
        result = function(validated_args)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Tool execution failed: {exc}",
        }

    return {
        "ok": True,
        "result": result,
    }




def execute_tool_with_timeout(
    tool_name: str,
    raw_arguments: dict,
    timeout_seconds: float = 2.0,
) -> dict:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            execute_tool,
            tool_name,
            raw_arguments,
        )

        try:
            return future.result(
                timeout=timeout_seconds
            )

        except FutureTimeoutError:
            return {
                "ok": False,
                "error": (
                    f"Tool timed out after "
                    f"{timeout_seconds} seconds"
                ),
            }

def execute_tool_with_retry(
    tool_name: str,
    raw_arguments: dict,
    timeout_seconds: float = 2.0,
    max_attempts: int = 2,
) -> dict:

    last_result = None

    for attempt in range(1, max_attempts + 1):

        print(
            f"Tool attempt {attempt}/{max_attempts}"
        )

        result = execute_tool_with_timeout(
            tool_name,
            raw_arguments,
            timeout_seconds=timeout_seconds,
        )

        if result["ok"]:
            return result

        last_result = result

        error = result.get("error", "")

        # Retry only timeout failures.
        if "timed out" not in error.lower():
            return result

    return last_result


from pathlib import Path

from sentence_transformers import SentenceTransformer

from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from ingestion import ingest_directory
from reranker import CrossEncoderReranker
from vector_store import PgVectorStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

_knowledge_hybrid = None
_knowledge_reranker = None


def get_knowledge_retrieval_stack():
    global _knowledge_hybrid
    global _knowledge_reranker

    if (
        _knowledge_hybrid is not None
        and _knowledge_reranker is not None
    ):
        return _knowledge_hybrid, _knowledge_reranker

    chunks = ingest_directory(KNOWLEDGE_DIR)

    if not chunks:
        raise RuntimeError(
            f"No knowledge chunks found in {KNOWLEDGE_DIR}"
        )

    bm25 = BM25Retriever(chunks)

    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = PgVectorStore()

    _knowledge_hybrid = HybridRetriever(
        bm25_retriever=bm25,
        vector_store=vector_store,
        embedding_model=embedding_model,
    )

    _knowledge_reranker = CrossEncoderReranker()

    return _knowledge_hybrid, _knowledge_reranker

# if __name__ == "__main__":
#     print("VALID TOOL CALL")
#
#     result = execute_tool(
#         "search_incidents",
#         {
#             "service": "payment-api",
#             "limit": 5,
#         },
#     )
#
#     print(result)
#
#     print()
#     print("INVALID ARGUMENTS")
#
#     result = execute_tool(
#         "search_incidents",
#         {
#             "service": "payment-api",
#             "limit": 100,
#         },
#     )
#
#     print(result)
#
#     print()
#     print("UNKNOWN TOOL")
#
#     result = execute_tool(
#         "delete_database",
#         {},
#     )
#
#     print(result)


if __name__ == "__main__":
    print("TIMEOUT + RETRY TEST")

    result = execute_tool_with_retry(
        "slow_tool",
        {
            "sleep_seconds": 0.5,
        },
        timeout_seconds=1,
        max_attempts=2,
    )

    print(result)