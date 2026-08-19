from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class InvestigationState(TypedDict):
    question: str
    service: str
    status: str


def identify_service(state: InvestigationState):
    print("\nIDENTIFY SERVICE NODE")
    print("State received:", state)

    question = state["question"].lower()

    if "payment-api" in question:
        service = "payment-api"
    else:
        service = "unknown"

    return {
        "service": service,
    }


def route_service(
    state: InvestigationState,
) -> Literal["investigate", "reject"]:

    print("\nROUTING")
    print("Service:", state["service"])

    if state["service"] == "unknown":
        return "reject"

    return "investigate"


def investigate(state: InvestigationState):
    print("\nINVESTIGATE NODE")
    print("State received:", state)

    return {
        "status": "ready-for-investigation",
    }


def reject(state: InvestigationState):
    print("\nREJECT NODE")
    print("State received:", state)

    return {
        "status": "unsupported-service",
    }


builder = StateGraph(InvestigationState)

builder.add_node("identify_service", identify_service)
builder.add_node("investigate", investigate)
builder.add_node("reject", reject)


builder.add_edge(
    START,
    "identify_service",
)


builder.add_conditional_edges(
    "identify_service",
    route_service,
    {
        "investigate": "investigate",
        "reject": "reject",
    },
)


builder.add_edge(
    "investigate",
    END,
)

builder.add_edge(
    "reject",
    END,
)


graph = builder.compile()


initial_state = {
    "question": "Why is payment-apk timing out?",
    "service": "",
    "status": "",
}


final_state = graph.invoke(initial_state)

print("\nFINAL STATE:")
print(final_state)