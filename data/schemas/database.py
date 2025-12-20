"""
SQLAlchemy database models for ASTRA persistent storage.

This module defines the database schema using SQLAlchemy ORM.
All services use these models for persistent data storage.
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, Generator
import os

Base = declarative_base()


class ContentEventDB(Base):
    """Database model for ingested content events."""
    
    __tablename__ = 'content_events'
    
    id = Column(String(36), primary_key=True)
    source = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(100), nullable=True, index=True)
    source_hash = Column(String(128), nullable=True, index=True)
    text = Column(Text, nullable=False)
    metadata_json = Column(Text)  # JSON string for flexible metadata
    processing_status = Column(String(20), nullable=False, default="NEW", index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ContentEvent(id={self.id}, source={self.source})>"


class DetectionResultDB(Base):
    """Database model for detection results."""
    
    __tablename__ = 'detection_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), index=True)
    label = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    detector_type = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<DetectionResult(event_id={self.event_id}, label={self.label}, confidence={self.confidence})>"


class AnalyticsRecordDB(Base):
    """Database model for analytics records."""
    
    __tablename__ = 'analytics_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), index=True)
    source = Column(String(100), index=True)
    text_preview = Column(String(500))
    detection_label = Column(String(50), index=True)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AnalyticsRecord(event_id={self.event_id}, label={self.detection_label})>"


class ThreatIndicatorDB(Base):
    """Database model for imported/exchanged threat indicators (Phase 3)."""

    __tablename__ = 'threat_indicators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    producer_instance_id = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(100), nullable=True, index=True)
    source_hash = Column(String(128), nullable=True, index=True)
    detection_label = Column(String(50), nullable=False, index=True)
    max_confidence = Column(Float, nullable=False)
    event_count = Column(Integer, nullable=False)
    first_seen = Column(DateTime, nullable=False, index=True)
    last_seen = Column(DateTime, nullable=False, index=True)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return (
            f"<ThreatIndicator(producer={self.producer_instance_id}, label={self.detection_label}, "
            f"count={self.event_count})>"
        )


class DatabaseManager:
    """
    Singleton database manager for ASTRA.
    
    Provides centralized database connection and session management.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._engine is None:
            if db_path is None:
                # Allow per-instance DB overrides for local multi-instance demos.
                # If unset, falls back to the workspace data/astra.db.
                db_path = os.getenv("ASTRA_DB_PATH")

            if db_path is None:
                # Default to workspace data directory
                workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(workspace_root, 'data', 'astra.db')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Create engine
            self._engine = create_engine(
                f'sqlite:///{db_path}',
                echo=False,  # Set to True for SQL debugging
                connect_args={'check_same_thread': False}  # Allow multi-threading
            )
            
            # Create session factory
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            
            # Create tables
            Base.metadata.create_all(bind=self._engine)
    
    @property
    def engine(self):
        return self._engine
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if self._SessionLocal is None:
            raise RuntimeError("DatabaseManager not initialized")
        return self._SessionLocal()
    
    def close_session(self, session: Session):
        """Close a database session."""
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db_session)):
            items = db.query(ContentEventDB).all()
            return items
    """
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
