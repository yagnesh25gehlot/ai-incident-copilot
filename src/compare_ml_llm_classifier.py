import json
import time
from pathlib import Path

import httpx
import joblib


MODEL_PATH = Path("models/incident_classifier.joblib")

LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"
LLM_MODEL = "local-qwen"

ALLOWED_LABELS = [
    "database",
    "cache",
    "tls",
    "authentication",
    "network",
    "deployment",
    "unknown",
]


EXAMPLES = [
    (
        "The application has run out of DB slots",
        "database",
    ),
    (
        "Secure communication fails during certificate negotiation",
        "tls",
    ),
    (
        "Previously stored values cannot be retrieved quickly",
        "cache",
    ),
    (
        "The identity system refuses to establish a user session",
        "authentication",
    ),
    (
        "The backend cannot communicate with the remote machine",
        "network",
    ),
    (
        "Everything worked until the latest software change was rolled out",
        "deployment",
    ),
    (
        "Kafka consumer lag is continuously increasing",
        "unknown",
    ),
    (
        "Requests are timing out",
        "unknown",
    ),
]


def classify_with_ml(model, text: str):
    start = time.perf_counter()

    probabilities = model.predict_proba([text])[0]
    classes = model.classes_

    best_index = probabilities.argmax()

    prediction = classes[best_index]
    score = float(probabilities[best_index])

    latency = time.perf_counter() - start

    return {
        "prediction": prediction,
        "score": score,
        "latency": latency,
    }


def classify_with_llm(text: str):
    prompt = f"""
Classify the following incident into exactly one category.

Allowed categories:
- database
- cache
- tls
- authentication
- network
- deployment
- unknown

Use "unknown" if:
- there is not enough information,
- the incident does not belong to one of the known categories,
- or the category cannot be determined reliably.

Incident:
{text}

Return only valid JSON in this format:

{{
  "label": "database"
}}
""".strip()

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an incident classifier. "
                    "Return only the requested JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.0,
        "max_tokens": 40,
    }

    start = time.perf_counter()

    with httpx.Client(
        timeout=30.0,
        trust_env=False,
    ) as client:
        response = client.post(
            LLM_URL,
            json=payload,
        )

        response.raise_for_status()

    latency = time.perf_counter() - start

    content = response.json()["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        parsed = json.loads(content)
        prediction = parsed.get("label", "unknown")
    except json.JSONDecodeError:
        prediction = "unknown"

    if prediction not in ALLOWED_LABELS:
        prediction = "unknown"

    return {
        "prediction": prediction,
        "latency": latency,
        "raw": content,
    }


def main():
    ml_model = joblib.load(MODEL_PATH)

    ml_correct = 0
    llm_correct = 0

    total_ml_latency = 0.0
    total_llm_latency = 0.0

    for text, expected in EXAMPLES:
        ml_result = classify_with_ml(
            ml_model,
            text,
        )

        llm_result = classify_with_llm(
            text,
        )

        if ml_result["prediction"] == expected:
            ml_correct += 1

        if llm_result["prediction"] == expected:
            llm_correct += 1

        total_ml_latency += ml_result["latency"]
        total_llm_latency += llm_result["latency"]

        print("\n" + "=" * 90)
        print(f"Incident : {text}")
        print(f"Expected : {expected}")

        print(
            f"ML       : {ml_result['prediction']}"
            f" | score={ml_result['score']:.4f}"
            f" | latency={ml_result['latency'] * 1000:.3f} ms"
        )

        print(
            f"LLM      : {llm_result['prediction']}"
            f" | latency={llm_result['latency']:.3f} s"
        )

    total = len(EXAMPLES)

    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)

    print(
        f"ML accuracy:  "
        f"{ml_correct}/{total} = {ml_correct / total:.3f}"
    )

    print(
        f"LLM accuracy: "
        f"{llm_correct}/{total} = {llm_correct / total:.3f}"
    )

    print(
        f"\nAverage ML latency:  "
        f"{(total_ml_latency / total) * 1000:.3f} ms"
    )

    print(
        f"Average LLM latency: "
        f"{total_llm_latency / total:.3f} s"
    )


if __name__ == "__main__":
    main()