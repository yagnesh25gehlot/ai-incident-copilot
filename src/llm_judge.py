import json

import httpx
from pydantic import BaseModel, Field


BASE_URL = "http://127.0.0.1:8080"
MODEL = "local-qwen"


from typing import Literal

from pydantic import BaseModel


class AnswerEvaluation(BaseModel):
    correctness: Literal["pass", "partial", "fail"]
    faithfulness: Literal["pass", "partial", "fail"]
    has_unsupported_claims: bool
    reason: str


class LLMJudge:
    def __init__(
        self,
        base_url: str = BASE_URL,
        model: str = MODEL,
    ):
        self.base_url = base_url
        self.model = model

    def evaluate(
        self,
        question: str,
        reference_answer: str,
        context: str,
        generated_answer: str,
    ) -> AnswerEvaluation:

        system_prompt = """
        You are evaluating a RAG answer.

        You MUST evaluate the generated answer only for the QUESTION that was asked.

        Do NOT require the answer to explain anything deeper than the question requires.

        For example:

        Question:
        Why are API requests timing out?

        Reference:
        The database connection pool is exhausted, so requests wait for connections.

        Generated:
        Requests are timing out because the database connection pool is exhausted.

        This is CORRECT.
        Do NOT require an explanation for why the connection pool itself became exhausted,
        because that was not the question.

        Evaluate two properties separately.

        CORRECTNESS:
        Compare the generated answer with the REFERENCE ANSWER.

        pass:
        The main answer matches the reference.

        partial:
        The main answer is partly correct but important information is missing or incorrect.

        fail:
        The main answer contradicts or does not match the reference.

        FAITHFULNESS:
        Check every factual claim in the generated answer against the RETRIEVED CONTEXT.

        pass:
        All factual claims are supported by the context.

        partial:
        The main answer is supported, but there is at least one additional unsupported claim.

        fail:
        The main claim is unsupported or contradicts the context.

        UNSUPPORTED CLAIMS:
        Set has_unsupported_claims=true if the generated answer contains ANY factual claim
        that is not supported by the retrieved context.

        Important:
        - Do not use outside knowledge.
        - Do not invent requirements.
        - Do not judge writing style.
        - Do not require more detail than the question asks for.
        - Treat the reference answer as the expected answer for correctness.
        - Treat the retrieved context as the only evidence for faithfulness.

        Return ONLY JSON exactly in this structure:

        {
          "correctness": "pass",
          "faithfulness": "pass",
          "has_unsupported_claims": false,
          "reason": "short explanation"
        }
        """

        user_prompt = f"""
QUESTION:
{question}

REFERENCE ANSWER:
{reference_answer}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{generated_answer}
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.0,
            "max_tokens": 200,
        }

        with httpx.Client(
            trust_env=False,
            timeout=60.0,
        ) as client:
            response = client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
            )

            response.raise_for_status()

        raw_text = (
            response.json()["choices"][0]["message"]["content"]
        )

        cleaned = raw_text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):]

        elif cleaned.startswith("```"):
            cleaned = cleaned[len("```"):]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)

        return AnswerEvaluation.model_validate(parsed)


if __name__ == "__main__":
    judge = LLMJudge()

    question = "Why are payment API requests timing out?"

    reference_answer = (
        "The PostgreSQL connection pool is exhausted. "
        "Requests wait for available database connections "
        "and eventually time out."
    )

    context = """
When the PostgreSQL connection pool becomes exhausted,
payment API requests begin waiting for available database
connections. Requests eventually time out and users may
receive HTTP 500 errors.

Connection pool exhaustion can occur because of a traffic
spike, slow database queries, or leaked application connections.
"""

    good_answer = (
        "Payment API requests are timing out because the "
        "PostgreSQL connection pool is exhausted, causing "
        "requests to wait for free database connections."
    )

    hallucinated_answer = (
        "Payment API requests are timing out because the "
        "PostgreSQL server CPU reached 100%, which caused "
        "the database to reject all incoming traffic."
    )

    partially_correct_answer = (
        "The PostgreSQL connection pool is exhausted, "
        "causing requests to wait for free connections. "
        "The exhaustion happened because CPU usage reached 100%."
    )

    print("=" * 80)
    print("GOOD ANSWER")
    print("=" * 80)

    good_result = judge.evaluate(
        question=question,
        reference_answer=reference_answer,
        context=context,
        generated_answer=good_answer,
    )

    print(good_result.model_dump_json(indent=2))

    print()

    print("=" * 80)
    print("HALLUCINATED ANSWER")
    print("=" * 80)

    bad_result = judge.evaluate(
        question=question,
        reference_answer=reference_answer,
        context=context,
        generated_answer=hallucinated_answer,
    )

    print(bad_result.model_dump_json(indent=2))

    print()

    print("=" * 80)
    print("PARTIALLY CORRECT ANSWER")
    print("=" * 80)

    partial_result = judge.evaluate(
        question=question,
        reference_answer=reference_answer,
        context=context,
        generated_answer=partially_correct_answer,
    )

    print(partial_result.model_dump_json(indent=2))