import json
from typing import Literal

import httpx
from pydantic import BaseModel, Field, model_validator

from agent_tools import execute_tool


# ============================================================
# Configuration
# ============================================================

BASE_URL = "http://127.0.0.1:8080"
MODEL = "local-qwen"

MAX_STEPS = 5
MAX_REPEATED_CALLS = 2


# ============================================================
# Agent prompt
# ============================================================

SYSTEM_PROMPT = """
You are an incident investigation agent.

Your job is to investigate incidents using the available tools before
providing a final answer.

Available tools:

1. search_incidents

Description:
Search operational incidents for a service.

Arguments:
{
  "service": "string",
  "severity": "low | medium | high | critical | optional",
  "limit": "integer from 1 to 10"
}


2. get_service_info

Description:
Retrieve deployment and runtime information about a service.

Arguments:
{
  "service": "string"
}


3. search_knowledge

Description:
Search incident runbooks and operational knowledge using
hybrid BM25 + dense retrieval followed by cross-encoder reranking.

Arguments:
{
  "query": "string",
  "top_k": "integer from 1 to 5"
}


Tool selection guidance:

- Use get_service_info for deployment, version, environment,
  database, or current service status.

- Use search_incidents for known/recent incident records
  associated with a service.

- Use search_knowledge for diagnostic procedures, known failure
  modes, runbooks, root-cause explanations, and resolutions.


IMPORTANT:

The "action" field has exactly two valid values:

"tool"
"final"

Never put a tool name inside the "action" field.

Correct tool call:

{
  "action": "tool",
  "tool": "search_incidents",
  "arguments": {
    "service": "payment-api",
    "limit": 5
  }
}

Incorrect:

{
  "action": "search_incidents"
}


For a final answer:

{
  "action": "final",
  "answer": "your answer"
}


Rules:

- Use tools when information is needed to investigate an incident.
- Use at least one tool before providing the final incident answer.
- Never invent tool results.
- Do not repeat the same tool call after it has already succeeded.
- If existing tool evidence answers the question, return action="final".
- Only request another tool if additional information is genuinely needed.
- Return exactly one valid JSON object.
- Do not include Markdown fences.
- Do not include explanations outside the JSON.
"""


# ============================================================
# Agent decision schema
# ============================================================

class AgentDecision(BaseModel):
    action: Literal["tool", "final"]

    tool: Literal[
              "search_knowledge",
              "search_incidents",
              "get_service_info",
          ] | None = None

    arguments: dict = Field(default_factory=dict)

    answer: str | None = None

    @model_validator(mode="after")
    def validate_decision(self):
        if self.action == "tool" and self.tool is None:
            raise ValueError(
                "tool must be provided when action='tool'"
            )

        if self.action == "final" and not self.answer:
            raise ValueError(
                "answer must be provided when action='final'"
            )

        return self


# ============================================================
# LLM client
# ============================================================

def call_llm(messages: list[dict]) -> str:
    with httpx.Client(
        trust_env=False,
        timeout=60.0,
    ) as client:

        response = client.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 256,
            },
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]


# ============================================================
# JSON parsing
# ============================================================

def parse_json_response(text: str) -> dict:
    """
    Clean common model-formatting mistakes and extract
    one JSON object.
    """

    text = text.strip()

    # Handle accidental Markdown fences.
    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Extract the JSON object if surrounding text exists.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "No JSON object found in model response"
        )

    json_text = text[start:end + 1]

    return json.loads(json_text)


# ============================================================
# Narrow deterministic repair
# ============================================================

def normalize_agent_decision(data: dict) -> dict:
    """
    Repair one narrow protocol error made by the small model.

    Example:

    {
        "action": "search_incidents",
        "tool": "search_incidents"
    }

    becomes:

    {
        "action": "tool",
        "tool": "search_incidents"
    }

    We only repair known and unambiguous tool names.
    """

    known_tools = {
        "search_knowledge",
        "search_incidents",
        "get_service_info",
    }

    action = data.get("action")

    if action in known_tools:
        data = data.copy()

        if data.get("tool") is None:
            data["tool"] = action

        data["action"] = "tool"

    return data


# ============================================================
# Final grounded answer generation
# ============================================================

def generate_final_answer(
    user_query: str,
    evidence: list[dict],
) -> str:
    """
    Generate the user-facing answer separately from
    agent routing.

    The model is explicitly restricted to collected
    tool evidence.
    """

    prompt = f"""
User question:

{user_query}


Collected tool evidence:

{json.dumps(evidence, indent=2)}


Answer the user's question using ONLY the collected tool evidence.

Do not invent causes or facts that are not present in the evidence.

If the evidence is insufficient to determine the root cause, say:

Insufficient evidence to determine the root cause.

Return only the answer text.
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You produce grounded incident investigation answers "
                "using only supplied tool evidence. "
                "Never invent information."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    try:
        return call_llm(messages).strip()

    except Exception as exc:
        return (
            "Unable to generate the final incident answer because "
            f"the LLM call failed: {exc}"
        )


# ============================================================
# Agent loop
# ============================================================

def run_agent(user_query: str) -> str:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    tool_calls_made = 0

    # Tracks:
    #
    # (tool name, normalized JSON arguments)
    #
    # Example:
    #
    # (
    #     "get_service_info",
    #     '{"service": "payment-api"}'
    # )
    #
    executed_calls = set()

    repeated_call_count = 0

    collected_evidence: list[dict] = []

    # ========================================================
    # Main agent loop
    # ========================================================

    for step in range(1, MAX_STEPS + 1):

        print()
        print("=" * 80)
        print(f"AGENT STEP {step}")
        print("=" * 80)

        # ----------------------------------------------------
        # Ask model for next decision
        # ----------------------------------------------------

        try:
            raw_response = call_llm(messages)

        except Exception as exc:
            print()
            print("LLM CALL FAILED:")
            print(exc)

            return (
                "Agent failed because the LLM call failed: "
                f"{exc}"
            )

        print("MODEL OUTPUT:")
        print(raw_response)

        # ----------------------------------------------------
        # Parse + normalize + validate model decision
        # ----------------------------------------------------

        try:
            parsed = parse_json_response(raw_response)

            parsed = normalize_agent_decision(parsed)

            decision = AgentDecision.model_validate(parsed)

        except Exception as exc:
            print()
            print("INVALID AGENT RESPONSE:")
            print(exc)

            # Save the bad assistant response so the model
            # can see what it previously produced.
            messages.append(
                {
                    "role": "assistant",
                    "content": raw_response,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous response was invalid.\n\n"
                        "The field 'action' must be exactly either "
                        "'tool' or 'final'.\n\n"
                        "Example valid tool call:\n"
                        '{"action":"tool",'
                        '"tool":"search_incidents",'
                        '"arguments":{'
                        '"service":"payment-api",'
                        '"limit":5'
                        "}}\n\n"
                        "Return exactly one valid JSON object."
                    ),
                }
            )

            continue

        # ====================================================
        # FINAL ANSWER DECISION
        # ====================================================

        if decision.action == "final":

            # Do not allow an ungrounded answer for this
            # investigation workflow.
            if tool_calls_made == 0:
                print()
                print("UNGROUNDED FINAL ANSWER REJECTED")

                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            decision.model_dump()
                        ),
                    }
                )

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "You have not used an investigation tool yet. "
                            "Do not guess the root cause. "
                            "Use at least one available tool first."
                        ),
                    }
                )

                continue

            # We deliberately generate the final answer in a
            # separate grounded-generation step rather than
            # blindly trusting the routing model's answer.
            return generate_final_answer(
                user_query=user_query,
                evidence=collected_evidence,
            )

        # ====================================================
        # TOOL DECISION
        # ====================================================

        print()
        print(f"REQUESTED TOOL: {decision.tool}")
        print(f"ARGUMENTS: {decision.arguments}")

        # Normalize argument ordering so:
        #
        # {"service": "x", "limit": 5}
        #
        # and:
        #
        # {"limit": 5, "service": "x"}
        #
        # are recognized as the same call.
        call_key = (
            decision.tool,
            json.dumps(
                decision.arguments,
                sort_keys=True,
            ),
        )

        # ====================================================
        # DUPLICATE / NO-PROGRESS DETECTION
        # ====================================================

        if call_key in executed_calls:

            repeated_call_count += 1

            print()
            print("REPEATED TOOL CALL DETECTED")

            # ------------------------------------------------
            # Deterministic fallback
            # ------------------------------------------------
            #
            # If the model repeatedly asks for service info,
            # querying incidents is a predictable next
            # investigation step.
            #
            # This demonstrates a hybrid:
            #
            # agent + deterministic workflow
            #
            if decision.tool == "get_service_info":

                service = decision.arguments.get("service")

                fallback_arguments = {
                    "service": service,
                    "limit": 5,
                }

                fallback_key = (
                    "search_incidents",
                    json.dumps(
                        fallback_arguments,
                        sort_keys=True,
                    ),
                )

                if (
                    service
                    and fallback_key not in executed_calls
                ):
                    print()
                    print(
                        "USING DETERMINISTIC FALLBACK: "
                        "search_incidents"
                    )

                    fallback_result = execute_tool(
                        "search_incidents",
                        fallback_arguments,
                    )

                    executed_calls.add(fallback_key)

                    tool_calls_made += 1

                    collected_evidence.append(
                        {
                            "tool": "search_incidents",
                            "arguments": fallback_arguments,
                            "result": fallback_result,
                        }
                    )

                    print()
                    print("FALLBACK TOOL RESULT:")
                    print(fallback_result)

                    # At this point we already have:
                    #
                    # service info
                    # +
                    # incidents
                    #
                    # so avoid another unreliable routing
                    # iteration and produce a grounded answer.
                    return generate_final_answer(
                        user_query=user_query,
                        evidence=collected_evidence,
                    )

            # ------------------------------------------------
            # If evidence already exists, avoid wasting more
            # model calls repeating the same request.
            # ------------------------------------------------

            if collected_evidence:
                print()
                print(
                    "NO PROGRESS — GENERATING ANSWER FROM "
                    "COLLECTED EVIDENCE"
                )

                return generate_final_answer(
                    user_query=user_query,
                    evidence=collected_evidence,
                )

            # ------------------------------------------------
            # General repeated-call guard
            # ------------------------------------------------

            if repeated_call_count >= MAX_REPEATED_CALLS:
                return (
                    "Agent stopped because it repeatedly "
                    "requested the same tool call without "
                    "making progress."
                )

            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        decision.model_dump()
                    ),
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "You already executed this exact tool call "
                        "and received its result. "
                        "Do not repeat it. "
                        "Use existing evidence and return "
                        "action='final', or select a different tool "
                        "only if additional evidence is necessary."
                    ),
                }
            )

            continue

        # ====================================================
        # SAFE TOOL EXECUTION
        # ====================================================

        # Record this call so it cannot be repeatedly executed.
        executed_calls.add(call_key)

        tool_result = execute_tool(
            decision.tool,
            decision.arguments,
        )

        tool_calls_made += 1

        print()
        print("TOOL RESULT:")
        print(tool_result)

        # Store tool result as investigation evidence.
        collected_evidence.append(
            {
                "tool": decision.tool,
                "arguments": decision.arguments,
                "result": tool_result,
            }
        )

        # ----------------------------------------------------
        # Store model decision in conversation history
        # ----------------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    decision.model_dump()
                ),
            }
        )

        # ----------------------------------------------------
        # Give tool result back to model
        # ----------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": (
                    f"TOOL RESULT for {decision.tool}:\n"
                    f"{json.dumps(tool_result)}\n\n"
                    "This tool call has already completed. "
                    "Do NOT repeat the same tool with the same "
                    "arguments. "
                    "If this evidence answers the user's question, "
                    "return action='final'. "
                    "Otherwise choose a different tool only if "
                    "additional information is genuinely required. "
                    "Never invent information."
                ),
            }
        )

    # ========================================================
    # Global max-step termination
    # ========================================================

    if collected_evidence:
        print()
        print("MAX STEPS REACHED")

        print(
            "GENERATING FINAL ANSWER FROM COLLECTED EVIDENCE"
        )

        return generate_final_answer(
            user_query=user_query,
            evidence=collected_evidence,
        )

    return (
        "Unable to complete the investigation within "
        f"{MAX_STEPS} agent steps."
    )


# ============================================================
# Manual test
# ============================================================

if __name__ == "__main__":

    answer = run_agent(
        "Why is payment-api timing out?"
    )

    print()
    print("=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)
    print(answer)