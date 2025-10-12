"""
SQLite-based publisher for persistent content event storage.
"""
from typing import List
import sys
import os
import json

# Setup path for database models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import ContentEvent
from database import DatabaseManager, ContentEventDB


class SQLitePublisher:
    """
    SQLite-based publisher that persists content events to database.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def publish(self, event: ContentEvent):
        """
        Publish (store) a content event to SQLite database.
        
        Args:
            event: ContentEvent to store
        """
        session = self.db_manager.get_session()
        try:
            # Convert Pydantic model to SQLAlchemy model
            db_event = ContentEventDB(
                id=event.id,
                source=event.source,
                text=event.text,
                metadata_json=json.dumps(event.metadata) if event.metadata else None,
                timestamp=event.timestamp
            )
            
            session.add(db_event)
            session.commit()
        finally:
            session.close()
    
    async def publish_batch(self, events: List[ContentEvent]):
        """
        Publish multiple events in a batch.
        
        Args:
            events: List of ContentEvent objects to store
        """
        session = self.db_manager.get_session()
        try:
            for event in events:
                db_event = ContentEventDB(
                    id=event.id,
                    source=event.source,
                    text=event.text,
                    metadata_json=json.dumps(event.metadata) if event.metadata else None,
                    timestamp=event.timestamp
                )
                session.add(db_event)
            
            session.commit()
        finally:
            session.close()
    
    async def get_all_events(self) -> List[ContentEvent]:
        """
        Retrieve all stored content events from database.
        
        Returns:
            List of ContentEvent objects
        """
        session = self.db_manager.get_session()
        try:
            db_events = session.query(ContentEventDB).order_by(ContentEventDB.timestamp.desc()).all()
            
            # Convert SQLAlchemy models to Pydantic models
            events = []
            for db_event in db_events:
                events.append(ContentEvent(
                    id=db_event.id,
                    source=db_event.source,
                    text=db_event.text,
                    metadata=json.loads(db_event.metadata_json) if db_event.metadata_json else {},
                    timestamp=db_event.timestamp
                ))
            
            return events
        finally:
            session.close()
    
    async def get_event_by_id(self, event_id: str) -> ContentEvent:
        """
        Retrieve a specific event by ID.
        
        Args:
            event_id: Event ID to retrieve
            
        Returns:
            ContentEvent or None if not found
        """
        session = self.db_manager.get_session()
        try:
            db_event = session.query(ContentEventDB).filter(ContentEventDB.id == event_id).first()
            
            if db_event:
                return ContentEvent(
                    id=db_event.id,
                    source=db_event.source,
                    text=db_event.text,
                    metadata=json.loads(db_event.metadata_json) if db_event.metadata_json else {},
                    timestamp=db_event.timestamp
                )
            return None
        finally:
            session.close()
    
    async def count_events(self) -> int:
        """Get total count of stored events."""
        session = self.db_manager.get_session()
        try:
            return session.query(ContentEventDB).count()
        finally:
            session.close()
