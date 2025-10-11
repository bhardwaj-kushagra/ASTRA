"""
Abstract base connector and connector registry for pluggable ingestion sources.
"""
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Type
import sys
import os

# Add parent directories to path for shared schema imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import ContentEvent


class Connector(ABC):
    """Base class for all content connectors."""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def fetch(self) -> Iterator[ContentEvent]:
        """
        Fetch content from the source and yield normalized ContentEvent objects.
        
        Yields:
            ContentEvent: Normalized content events.
        """
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this connector source."""
        pass


class ConnectorRegistry:
    """Registry for managing available connectors."""
    
    _connectors: Dict[str, Type[Connector]] = {}
    
    @classmethod
    def register(cls, name: str, connector_class: Type[Connector]):
        """Register a new connector type."""
        cls._connectors[name] = connector_class
    
    @classmethod
    def get_connector(cls, name: str, config: dict) -> Connector:
        """Instantiate a connector by name."""
        if name not in cls._connectors:
            raise ValueError(f"Unknown connector: {name}")
        return cls._connectors[name](config)
    
    @classmethod
    def list_connectors(cls) -> list:
        """List all registered connector names."""
        return list(cls._connectors.keys())
