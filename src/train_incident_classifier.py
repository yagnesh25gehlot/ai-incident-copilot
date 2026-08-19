from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DATA_PATH = Path("data/ml/incidents.csv")
MODEL_PATH = Path("models/incident_classifier.joblib")

RANDOM_STATE = 42


def load_data() -> tuple[pd.Series, pd.Series]:
    df = pd.read_csv(DATA_PATH)

    print(f"Total examples: {len(df)}")
    print("\nClass distribution:")
    print(df["label"].value_counts())

    return df["text"], df["label"]


def split_data(X, y):
    # 60% train, 40% temporary
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.40,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Temporary 40% becomes:
    # 20% validation
    # 20% test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    print("\nDataset split:")
    print(f"Train:      {len(X_train)}")
    print(f"Validation: {len(X_val)}")
    print(f"Test:       {len(X_test)}")

    return X_train, X_val, X_test, y_train, y_val, y_test


def build_model(c_value: float) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 1),
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=c_value,
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def choose_best_c(X_train, y_train, X_val, y_val) -> float:
    candidate_c_values = [0.1, 1.0, 10.0]

    best_c = None
    best_f1 = -1.0

    print("\nValidation experiments:")

    for c_value in candidate_c_values:
        model = build_model(c_value)

        model.fit(X_train, y_train)

        predictions = model.predict(X_val)

        macro_f1 = f1_score(
            y_val,
            predictions,
            average="macro",
            zero_division=0,
        )

        print(f"C={c_value:<4} validation macro-F1={macro_f1:.4f}")

        if macro_f1 > best_f1:
            best_f1 = macro_f1
            best_c = c_value

    print(f"\nSelected C = {best_c}")
    print(f"Best validation macro-F1 = {best_f1:.4f}")

    return best_c


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    print("\nFINAL TEST RESULTS")
    print("=" * 60)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    labels = sorted(y_test.unique())

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    print("Confusion matrix labels:")
    print(labels)

    print("\nConfusion matrix:")
    print(matrix)


def main():
    X, y = load_data()

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_data(X, y)

    best_c = choose_best_c(
        X_train,
        y_train,
        X_val,
        y_val,
    )

    # Hyperparameter selection is finished.
    # We can now use both train + validation data
    # to train the final model.
    X_final_train = pd.concat([X_train, X_val])
    y_final_train = pd.concat([y_train, y_val])

    final_model = build_model(best_c)
    final_model.fit(X_final_train, y_final_train)

    evaluate_model(
        final_model,
        X_test,
        y_test,
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        final_model,
        MODEL_PATH,
    )

    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()