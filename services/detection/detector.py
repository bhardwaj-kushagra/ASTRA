"""
Abstract detector interface and detector registry.
"""
from abc import ABC, abstractmethod
from typing import Dict, Type
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import DetectionRequest, DetectionResult


class Detector(ABC):
    """Base class for all detection models."""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    async def detect(self, request: DetectionRequest) -> DetectionResult:
        """
        Analyze content and return detection result.
        
        Args:
            request: Detection request with text and metadata
        
        Returns:
            DetectionResult with label, confidence, and metadata
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Unique identifier for this detector."""
        pass


class DetectorRegistry:
    """Registry for managing available detectors."""
    
    _detectors: Dict[str, Type[Detector]] = {}
    
    @classmethod
    def register(cls, name: str, detector_class: Type[Detector]):
        """Register a new detector type."""
        cls._detectors[name] = detector_class
    
    @classmethod
    def get_detector(cls, name: str, config: dict) -> Detector:
        """Instantiate a detector by name."""
        if name not in cls._detectors:
            raise ValueError(f"Unknown detector: {name}")
        return cls._detectors[name](config)
    
    @classmethod
    def list_detectors(cls) -> list:
        """List all registered detector names."""
        return list(cls._detectors.keys())
