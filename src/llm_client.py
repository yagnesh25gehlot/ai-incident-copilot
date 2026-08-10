import json
import httpx

from typing import Literal
from pydantic import BaseModel, Field
import time

BASE_URL = "http://127.0.0.1:8080"
MODEL = "local-qwen"


def clean_json_response(raw_response: str) -> str:
    cleaned = raw_response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):]

    if cleaned.startswith("```"):
        cleaned = cleaned[len("```"):]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


class IncidentAnalysis(BaseModel):
    root_cause: str
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0, le=1)


def ask_llm(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a concise production incident assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 128,
    }

    start = time.perf_counter()

    with httpx.Client(trust_env=False, timeout=60.0) as client:
        response = client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
        )

    elapsed = time.perf_counter() - start

    response.raise_for_status()
    data = response.json()

    print("\n--- LLM metrics ---")
    print("Latency:", round(elapsed, 2), "seconds")
    print("Prompt tokens:", data["usage"]["prompt_tokens"])
    print("Completion tokens:", data["usage"]["completion_tokens"])
    print("Total tokens:", data["usage"]["total_tokens"])

    return data["choices"][0]["message"]["content"]


def analyze_incident(incident: str) -> IncidentAnalysis:
    prompt = f"""
Analyze this incident:

{incident}

Return ONLY valid JSON in exactly this format:

{{
  "root_cause": "short explanation",
  "severity": "low | medium | high | critical",
  "confidence": 0.0
}}

confidence must be a number between 0 and 1.
Do not include markdown or explanation outside the JSON.
"""

    raw_response = ask_llm(prompt)

    print("Raw LLM response:")
    print(raw_response)

    cleaned_response = clean_json_response(raw_response)
    parsed_json = json.loads(cleaned_response)

    return IncidentAnalysis.model_validate(parsed_json)


if __name__ == "__main__":
    result = analyze_incident(
        "The payment API is returning database connection timeout errors "
        "for most requests and users cannot complete checkout."
    )

    print("\nValidated Pydantic object:")
    print(result)

    print("\nSeverity:", result.severity)
    print("Confidence:", result.confidence)




