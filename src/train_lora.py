from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

TRAIN_FILE = Path("data/finetuning/incidents_sft.jsonl")
OUTPUT_DIR = Path("models/incident_lora")


def main():
    print("=" * 80)
    print("DAY 10 — LoRA SFT")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Load our tiny supervised fine-tuning dataset
    # ------------------------------------------------------------------

    dataset = load_dataset(
        "json",
        data_files=str(TRAIN_FILE),
        split="train",
    )

    def add_prompt_separator(example):
        prompt = example["prompt"]

        if not prompt.endswith("\n"):
            prompt += "\n"

        return {
            "prompt": prompt,
            "completion": example["completion"],
        }

    dataset = dataset.map(add_prompt_separator)

    print(f"Training examples: {len(dataset)}")
    print(f"Columns: {dataset.column_names}")
    print(f"Example: {dataset[0]}")

    # ------------------------------------------------------------------
    # 2. Load tokenizer
    # ------------------------------------------------------------------

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ------------------------------------------------------------------
    # 3. Load pretrained Qwen
    # ------------------------------------------------------------------

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float32,
    )

    # ------------------------------------------------------------------
    # 4. Define LoRA configuration
    # ------------------------------------------------------------------

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
        ],
        bias="none",
    )

    # ------------------------------------------------------------------
    # 5. Define SFT training configuration
    # ------------------------------------------------------------------

    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),

        num_train_epochs=15,

        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,

        learning_rate=1e-4,

        logging_steps=1,

        max_length=128,

        completion_only_loss=True,

        fp16=False,
        bf16=False,
        dataloader_pin_memory=False,

        packing=False,

        save_strategy="no",

        report_to="none",

        seed=42,

        torch_empty_cache_steps=1,
    )

    # ------------------------------------------------------------------
    # 6. Build trainer
    # ------------------------------------------------------------------

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=lora_config,
    )

    # ------------------------------------------------------------------
    # 7. IMPORTANT: inspect LoRA parameter count
    # ------------------------------------------------------------------

    trainer.model.print_trainable_parameters()

    # ------------------------------------------------------------------
    # 8. Train
    # ------------------------------------------------------------------

    print("\nStarting training...\n")

    train_result = trainer.train()

    print("\nTraining complete.")

    print(f"Final training loss: {train_result.training_loss:.4f}")

    # ------------------------------------------------------------------
    # 9. Save ONLY the LoRA adapter + tokenizer
    # ------------------------------------------------------------------

    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\nLoRA adapter saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()