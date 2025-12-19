"""Utility script to download the zero-shot model locally.

This script downloads a Hugging Face sequence classification model
(e.g., facebook/bart-large-mnli) and saves it into a local directory
inside the repo (default: astra-models/facebook-bart-large-mnli).

The resulting directory can then be referenced via the ZERO_SHOT_MODEL_PATH
environment variable so the detection service runs fully offline.
"""
from __future__ import annotations

import os
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForSequenceClassification


def get_repo_root() -> Path:
    # tools/scripts/download_zero_shot_model.py -> tools -> repo root
    return Path(__file__).resolve().parent.parent.parent


def main() -> None:
    model_id = os.getenv("ZERO_SHOT_MODEL_ID", "facebook/bart-large-mnli")

    # Default path: <repo_root>/astra-models/<model_id-sanitized>
    repo_root = get_repo_root()
    folder_name = model_id.replace("/", "-")
    default_dir = repo_root / "astra-models" / folder_name

    target_dir_str = os.getenv("ZERO_SHOT_MODEL_PATH", str(default_dir))
    target_dir = Path(target_dir_str)
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading model '{model_id}' to '{target_dir}'...")

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)

    tokenizer.save_pretrained(target_dir)
    model.save_pretrained(target_dir)

    print("Download complete. Set ZERO_SHOT_MODEL_PATH to this directory for offline use.")


if __name__ == "__main__":
    main()
