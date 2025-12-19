"""Detection service main application."""
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
try:
    # Register zero-shot if dependencies are installed; fail gracefully otherwise
    from detectors import zero_shot_detector  # noqa: F401
except Exception:  # noqa: BLE001
    zero_shot_detector = None  # type: ignore[assignment]

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
    available = DetectorRegistry.list_detectors()
    return {
        "service": "detection",
        "version": "0.1.0",
        "status": "running",
        "available_detectors": available,
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
    available = DetectorRegistry.list_detectors()
    return {
        "detectors": available,
        "active_detector": DETECTOR_NAME,
        "default": DETECTOR_NAME
    }


@app.get("/detector")
async def get_active_detector():
    """Return the active detector and available options."""
    available = DetectorRegistry.list_detectors()
    return {
        "active_detector": DETECTOR_NAME,
        "available_detectors": available,
    }


@app.post("/detector/{name}")
async def set_active_detector(name: str):
    """Switch the active detector at runtime.

    Supported names: simple, rag, zero-shot (if dependencies installed).
    """
    global DETECTOR_NAME, default_detector

    if name == "zero-shot":
        # Try to register zero-shot detector lazily; handle missing deps.
        try:
            from detectors import zero_shot_detector  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=f"Zero-shot detector unavailable: {exc}")
    elif name not in DetectorRegistry.list_detectors():
        raise HTTPException(status_code=400, detail=f"Unknown detector: {name}")

    DETECTOR_NAME = name
    default_detector = None  # reset so get_detector() reinitializes with new type

    # Optionally warm up the detector so the first request isn't surprised.
    try:
        _ = get_detector()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to initialize detector '{name}': {exc}")

    return {
        "status": "success",
        "active_detector": DETECTOR_NAME,
        "available_detectors": DetectorRegistry.list_detectors(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
