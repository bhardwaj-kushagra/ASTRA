"""
Zero-shot text classifier using Hugging Face transformers.
"""
import sys
import os
from typing import Optional, Any, Callable, Union, Dict

try:
    from transformers import pipeline  # heavy dependency
except Exception as import_err:  # noqa: BLE001
    pipeline = None  # Will handle gracefully in detector
    _transformers_import_error = import_err

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import DetectionRequest, DetectionResult
from detector import Detector, DetectorRegistry


class ZeroShotDetector(Detector):
    """
    Zero-shot classifier for detecting AI-generated content.
    Uses facebook/bart-large-mnli by default.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.labels = config.get("labels", ["AI-generated", "human-written", "suspicious"])
        self.model_id = config.get("model_id", "facebook/bart-large-mnli")
        # classifier is Union[callable pipeline, Exception sentinel, None]
        self.classifier = None  # type: ignore[assignment]
        if pipeline is not None:
            try:
                self.classifier = pipeline("zero-shot-classification", model=self.model_id)
            except Exception as e:  # noqa: BLE001
                # Defer raising until detect is called; allows service to start
                self.classifier = e  # store exception sentinel
    
    @property
    def model_name(self) -> str:
        return "zero-shot-classifier"
    
    async def detect(self, request: DetectionRequest) -> DetectionResult:
        """
        Classify text using zero-shot classification.
        
        Args:
            request: DetectionRequest with text to analyze
        
        Returns:
            DetectionResult with predicted label and confidence
        """
        if pipeline is None:
            raise RuntimeError(f"transformers import failed: {_transformers_import_error}")
        if isinstance(self.classifier, Exception):
            raise RuntimeError(f"transformers pipeline init failed: {self.classifier}")
        classifier = self.classifier  # type: ignore[assignment]
        if classifier is None:
            raise RuntimeError("transformers pipeline not initialized")
        # Call the pipeline (dict with 'labels' and 'scores')
        result: Dict[str, Any] = classifier(request.text, candidate_labels=self.labels)  # type: ignore[call-arg]
        
        # Extract top prediction
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        return DetectionResult(
            label=top_label,
            confidence=float(top_score),
            detector_model=self.model_name,
            metadata={
                "all_labels": result["labels"],
                "all_scores": [float(s) for s in result["scores"]]
            }
        )


# Register this detector
try:
    DetectorRegistry.register("zero-shot", ZeroShotDetector)
except Exception:  # noqa: BLE001
    pass
