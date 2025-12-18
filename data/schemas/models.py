"""
Shared data models for ASTRA services.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ContentEvent(BaseModel):
    """Normalized content event emitted by ingestion service."""
    id: str = Field(..., description="Unique event identifier")
    source: str = Field(..., description="Origin connector (file, http, api)")
    content_type: str = Field(default="text", description="text, image, video, etc.")
    text: str = Field(..., description="Raw text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Connector-specific metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DetectionRequest(BaseModel):
    """Request payload for detection service."""
    text: str = Field(..., description="Text content to analyze")
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class DetectionResult(BaseModel):
    """Detection response with classification and confidence.

    The original field `model_name` triggered a Pydantic protected namespace warning
    (conflict with `model_`). We keep external compatibility by exposing
    `detector_model` as the canonical field while aliasing `model_name`.
    """
    event_id: Optional[str] = None
    label: str = Field(..., description="AI-generated, human, suspicious, etc.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    detector_model: str = Field(..., alias="model_name", description="Detector model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        # Allow alias population; disable protected namespace restriction for this model
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class AnalyticsRecord(BaseModel):
    """Aggregated detection record for analytics dashboard."""
    event_id: str
    source: str
    text_preview: str = Field(..., max_length=200)
    detection_label: str
    confidence: float
    timestamp: datetime
    model_config = {"protected_namespaces": ()}
