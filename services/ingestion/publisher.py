"""
Event publisher interface for sending ContentEvents downstream.
"""
from abc import ABC, abstractmethod
from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import ContentEvent


class EventPublisher(ABC):
    """Abstract publisher for content events."""
    
    @abstractmethod
    async def publish(self, event: ContentEvent):
        """Publish a single event."""
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[ContentEvent]):
        """Publish a batch of events."""
        pass


class InMemoryPublisher(EventPublisher):
    """Simple in-memory publisher for MVP (stores events in a list)."""
    
    def __init__(self):
        self.events: List[ContentEvent] = []
    
    async def publish(self, event: ContentEvent):
        """Add event to in-memory list."""
        self.events.append(event)
        print(f"[InMemoryPublisher] Published event {event.id} from {event.source}")
    
    async def publish_batch(self, events: List[ContentEvent]):
        """Add batch of events to in-memory list."""
        for event in events:
            await self.publish(event)
    
    def get_all_events(self) -> List[ContentEvent]:
        """Retrieve all published events (for testing/demo)."""
        return self.events
    
    def clear(self):
        """Clear all events."""
        self.events.clear()
