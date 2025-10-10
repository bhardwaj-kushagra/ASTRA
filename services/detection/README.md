# Detection Service

Provides real-time classification and scoring of suspected AI-generated or malicious narratives.

## Responsibilities
- Host fine-tuned transformer models and ensemble orchestrations.
- Expose REST/gRPC endpoints with latency SLAs for SOC integrations.
- Track evaluation metrics (precision, recall, ROC) and drift signals.

## Next Steps
1. Select baseline model architectures and datasets for training.
2. Establish MLOps pipeline for continuous training and benchmarking.
3. Implement explainability hooks (SHAP/LIME) for analyst review.
