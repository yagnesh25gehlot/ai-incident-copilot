from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    question: str
    step_count: int
    tool_result: str
    final_answer: str


def router_node(state: AgentState):
    print("\nROUTER NODE")
    print("State:", state)

    return {
        "step_count": state["step_count"] + 1,
    }


def route_action(
    state: AgentState,
) -> Literal["tool", "final"]:

    print("\nROUTE ACTION")
    print("Step count:", state["step_count"])

    if not state["tool_result"]:
        return "tool"

    return "final"


def tool_node(state: AgentState):
    print("\nTOOL NODE")
    print("Executing synthetic incident search...")

    return {
        "tool_result": (
            "Payment API requests are timing out because "
            "the PostgreSQL connection pool is exhausted."
        )
    }


def final_node(state: AgentState):
    print("\nFINAL NODE")

    answer = f"Based on tool evidence: {state['tool_result']}"

    return {
        "final_answer": answer,
    }


builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("tool", tool_node)
builder.add_node("final", final_node)


builder.add_edge(
    START,
    "router",
)


builder.add_conditional_edges(
    "router",
    route_action,
    {
        "tool": "tool",
        "final": "final",
    },
)


builder.add_edge(
    "tool",
    "router",
)


builder.add_edge(
    "final",
    END,
)


graph = builder.compile()


initial_state = {
    "question": "Why is payment-api timing out?",
    "step_count": 0,
    "tool_result": "",
    "final_answer": "",
}


final_state = graph.invoke(initial_state)

print("\nFINAL GRAPH STATE:")
print(final_state)