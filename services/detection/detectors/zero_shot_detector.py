"""
Zero-shot text classifier using Hugging Face transformers.
"""
import sys
import os
from transformers import pipeline

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
        model_id = config.get("model_id", "facebook/bart-large-mnli")
        self.classifier = pipeline("zero-shot-classification", model=model_id)
        self.labels = config.get("labels", ["AI-generated", "human-written", "suspicious"])
    
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
        result = self.classifier(request.text, candidate_labels=self.labels)
        
        # Extract top prediction
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        return DetectionResult(
            label=top_label,
            confidence=float(top_score),
            model_name=self.model_name,
            metadata={
                "all_labels": result["labels"],
                "all_scores": [float(s) for s in result["scores"]]
            }
        )


# Register this detector
DetectorRegistry.register("zero-shot", ZeroShotDetector)
