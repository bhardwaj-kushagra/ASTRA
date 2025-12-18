"""
Detection service main application.
"""
from fastapi import FastAPI, HTTPException
from typing import Optional
import sys
import os

# Setup path for shared schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import DetectionRequest, DetectionResult
from detector import DetectorRegistry

# Import detectors to register them
from detectors import simple_detector      # registers lightweight simple detector
from detectors import rag_detector         # registers minimal RAG detector

app = FastAPI(title="ASTRA Detection Service", version="0.1.0")

# Initialize default detector (lazy loading for production)
default_detector = None
DETECTOR_NAME = os.getenv("DETECTOR_NAME", "simple")


def get_detector():
    """Lazy initialization of detector."""
    global default_detector
    if default_detector is None:
        if DETECTOR_NAME == "zero-shot":
            # Lazy import to avoid heavy dependency cost unless requested
            from detectors import zero_shot_detector  # noqa: F401
            default_detector = DetectorRegistry.get_detector("zero-shot", {
                "model_id": "facebook/bart-large-mnli",
                "labels": ["AI-generated", "human-written", "suspicious"]
            })
        elif DETECTOR_NAME == "rag":
            default_detector = DetectorRegistry.get_detector("rag", {
                "top_k": 2
            })
        else:
            default_detector = DetectorRegistry.get_detector("simple", {
                "threshold_len": 600
            })
    return default_detector


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "detection",
        "version": "0.1.0",
        "status": "running",
        "available_detectors": DetectorRegistry.list_detectors(),
        "active_detector": DETECTOR_NAME
    }


@app.post("/detect", response_model=DetectionResult)
async def detect_content(request: DetectionRequest):
    """
    Analyze text content for AI-generated signals.
    
    Args:
        request: DetectionRequest with text to analyze
    
    Returns:
        DetectionResult with classification and confidence
    """
    try:
        detector = get_detector()
        result = await detector.detect(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/models")
async def list_models():
    """List available detector models."""
    return {
        "detectors": DetectorRegistry.list_detectors(),
        "default": "zero-shot"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
