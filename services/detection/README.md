# Detection Service

Real-time classification and scoring of suspected AI-generated or malicious narratives using transformer-based models.

## Responsibilities (MVP)
- Host pre-trained or fine-tuned transformer model (RoBERTa, DistilBERT, or zero-shot classifier).
- Expose REST API for text classification with confidence scores.
- Extensible detector registry for plugging in additional models.

## Tech Stack
- Python 3.10+, FastAPI
- Hugging Face Transformers
- Pydantic for request/response validation
- Optional: ONNX runtime for inference optimization

## Future Enhancements
- Ensemble orchestration combining multiple detectors.
- Stylometric and entropy-based feature extraction.
- Explainability hooks (SHAP/LIME) for analyst review.
- Model drift detection and continuous retraining pipelines.

## Next Steps
1. Select baseline model and evaluation dataset.
2. Implement REST endpoint with health check and inference routes.
3. Add logging and metrics instrumentation.
