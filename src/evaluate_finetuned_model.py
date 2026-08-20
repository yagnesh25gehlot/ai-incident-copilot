import json
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

ADAPTER_DIR = Path("models/incident_lora")
EVAL_FILE = Path("data/finetuning/incidents_eval.jsonl")


def load_eval_examples():
    examples = []

    with EVAL_FILE.open() as f:
        for line in f:
            examples.append(json.loads(line))

    return examples


def generate_response(model, tokenizer, device, incident):
    prompt = f"Incident: {incident}\nResponse:\n"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=40,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return response.strip()


def extract_category(response):
    for line in response.splitlines():
        if line.startswith("CATEGORY:"):
            return line.split(":", 1)[1].strip().lower()

    return None


def has_correct_format(response):
    lines = response.splitlines()

    has_category = any(
        line.startswith("CATEGORY:")
        for line in lines
    )

    has_summary = any(
        line.startswith("SUMMARY:")
        for line in lines
    )

    return has_category and has_summary


def evaluate(model, tokenizer, device, examples, name):
    print("\n" + "=" * 100)
    print(name)
    print("=" * 100)

    correct_categories = 0
    correct_formats = 0

    for index, example in enumerate(examples, start=1):
        incident = example["incident"]
        expected = example["expected_category"]

        response = generate_response(
            model,
            tokenizer,
            device,
            incident,
        )

        predicted = extract_category(response)
        format_ok = has_correct_format(response)

        if predicted == expected:
            correct_categories += 1

        if format_ok:
            correct_formats += 1

        print(f"\nExample {index}")
        print(f"Incident: {incident}")
        print(f"Expected category: {expected}")
        print(f"Predicted category: {predicted}")
        print(f"Format correct: {format_ok}")
        print("Response:")
        print(response)

    total = len(examples)

    category_accuracy = correct_categories / total
    format_accuracy = correct_formats / total

    print("\n" + "-" * 100)
    print(f"{name} RESULTS")
    print("-" * 100)

    print(
        f"Category accuracy: "
        f"{correct_categories}/{total} "
        f"= {category_accuracy:.3f}"
    )

    print(
        f"Format accuracy: "
        f"{correct_formats}/{total} "
        f"= {format_accuracy:.3f}"
    )

    return {
        "category_accuracy": category_accuracy,
        "format_accuracy": format_accuracy,
    }


def main():
    device = torch.device(
        "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    print(f"Device: {device}")

    examples = load_eval_examples()

    print(f"Evaluation examples: {len(examples)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # --------------------------------------------------------------
    # BASE MODEL
    # --------------------------------------------------------------

    print("\nLoading base model...")

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float32,
    )

    base_model = base_model.to(device)
    base_model.eval()

    base_results = evaluate(
        base_model,
        tokenizer,
        device,
        examples,
        "BASE MODEL",
    )

    # --------------------------------------------------------------
    # ATTACH TRAINED LoRA ADAPTER
    # --------------------------------------------------------------

    print("\nLoading LoRA adapter...")

    tuned_model = PeftModel.from_pretrained(
        base_model,
        ADAPTER_DIR,
    )

    tuned_model = tuned_model.to(device)
    tuned_model.eval()

    tuned_results = evaluate(
        tuned_model,
        tokenizer,
        device,
        examples,
        "LoRA-TUNED MODEL",
    )

    # --------------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------------

    print("\n" + "=" * 100)
    print("BASE VS LoRA")
    print("=" * 100)

    print(
        f"Category accuracy: "
        f"{base_results['category_accuracy']:.3f}"
        f" -> "
        f"{tuned_results['category_accuracy']:.3f}"
    )

    print(
        f"Format accuracy: "
        f"{base_results['format_accuracy']:.3f}"
        f" -> "
        f"{tuned_results['format_accuracy']:.3f}"
    )


if __name__ == "__main__":
    main()