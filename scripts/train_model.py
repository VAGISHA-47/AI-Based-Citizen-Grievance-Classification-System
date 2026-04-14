import argparse
from pathlib import Path

from datasets import load_dataset
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    Trainer,
    TrainingArguments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT for grievance classification")
    parser.add_argument("--train-file", default="data/train.csv", help="CSV with columns: text,label")
    parser.add_argument("--validation-file", default="data/val.csv", help="CSV with columns: text,label")
    parser.add_argument("--output-dir", default="models/distilbert-grievance", help="Model output directory")
    parser.add_argument("--num-labels", type=int, required=True, help="Number of category labels")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    train_path = Path(args.train_file)
    val_path = Path(args.validation_file)
    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError("Training and validation CSV files must exist before training.")

    dataset = load_dataset(
        "csv",
        data_files={"train": str(train_path), "validation": str(val_path)},
    )

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)

    tokenized = dataset.map(tokenize, batched=True)
    tokenized = tokenized.rename_column("label", "labels")
    tokenized.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=args.num_labels,
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        learning_rate=2e-5,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
