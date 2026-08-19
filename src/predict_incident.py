from pathlib import Path

import joblib


MODEL_PATH = Path("models/incident_classifier.joblib")


def main():
    model = joblib.load(MODEL_PATH)

    examples = [
        # Semantic paraphrase with little training vocabulary overlap
        "The application has run out of DB slots",

        # Indirect TLS wording
        "Secure communication fails during certificate negotiation",

        # Cache idea without the word Redis/cache
        "Previously stored values cannot be retrieved quickly",

        # Authentication paraphrase
        "The identity system refuses to establish a user session",

        # Network paraphrase
        "The backend cannot communicate with the remote machine",

        # Deployment paraphrase
        "Everything worked until the latest software change was rolled out",

        # Completely unsupported class
        "Kafka consumer lag is continuously increasing",

        # Ambiguous incident
        "Requests are timing out",
    ]

    predictions = model.predict(examples)
    probabilities = model.predict_proba(examples)

    classes = model.classes_

    for text, prediction, probs in zip(
        examples,
        predictions,
        probabilities,
    ):
        print("\n" + "=" * 80)
        print(f"Incident:  {text}")
        print(f"Prediction: {prediction}")

        ranked = sorted(
            zip(classes, probs),
            key=lambda item: item[1],
            reverse=True,
        )

        print("Class scores:")

        for label, probability in ranked:
            print(f"  {label:<15} {probability:.4f}")


if __name__ == "__main__":
    main()