# Detection Service

Real-time classification and scoring of suspected AI-generated or malicious narratives.

This service exposes a stable `/detect` contract while allowing the active detector implementation to be switched at runtime.

## Built-in Detectors

ASTRA ships with three detector modes:

- `simple` — lightweight heuristic baseline (no ML dependencies; always offline)
- `rag` — embedding retrieval + kNN over a small labeled knowledge base (Sentence Transformers)
- `zero-shot` — Hugging Face Transformers zero-shot classifier (default model id: `facebook/bart-large-mnli`)

## API

- `GET /` — health + `available_detectors`
- `POST /detect` — analyze `{ "text": "..." }` and return `DetectionResult`
- `GET /models` — list registered detectors
- `GET /detector` — show current active detector + available detectors
- `POST /detector/{name}` — switch active detector (`simple`, `rag`, `zero-shot`)

## Configuration

Environment variables:

- `DETECTOR_NAME` — start-up detector selection (`simple` | `rag` | `zero-shot`)
- `ZERO_SHOT_MODEL_PATH` — optional local folder for the zero-shot model (fully offline)
- `RAG_MODEL_PATH` — optional local folder for the Sentence Transformer embedding model (fully offline)

Offline model download helpers:

- `python tools/scripts/download_zero_shot_model.py`
- `python tools/scripts/download_rag_model.py`

## Tech Stack

- Python + FastAPI
- Detector registry pattern (`DetectorRegistry`) for extensibility
- Optional ML deps:
  - `transformers` + `torch` for `zero-shot`
  - `sentence-transformers` for `rag`
