"""
SQLite-based analytics store for persistent data storage.
"""
from typing import List, Dict
import sys
import os
from datetime import datetime
from sqlalchemy import func

# Setup path for database models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import AnalyticsRecord
from database import DatabaseManager, AnalyticsRecordDB


class SQLiteAnalyticsStore:
    """
    SQLite-based analytics store for persistent record storage.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def add_record(self, record: AnalyticsRecord):
        """
        Store an analytics record in the database.
        
        Args:
            record: AnalyticsRecord to store
        """
        session = self.db_manager.get_session()
        try:
            db_record = AnalyticsRecordDB(
                event_id=record.event_id,
                source=record.source,
                text_preview=record.text_preview,
                detection_label=record.detection_label,
                confidence=record.confidence,
                timestamp=record.timestamp
            )
            
            session.add(db_record)
            session.commit()
        finally:
            session.close()
    
    async def get_recent(self, limit: int = 100) -> List[AnalyticsRecord]:
        """
        Get recent analytics records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of AnalyticsRecord objects, newest first
        """
        session = self.db_manager.get_session()
        try:
            db_records = (session.query(AnalyticsRecordDB)
                         .order_by(AnalyticsRecordDB.timestamp.desc())
                         .limit(limit)
                         .all())
            
            records = []
            for db_record in db_records:
                records.append(AnalyticsRecord(
                    event_id=db_record.event_id,
                    source=db_record.source,
                    text_preview=db_record.text_preview,
                    detection_label=db_record.detection_label,
                    confidence=db_record.confidence,
                    timestamp=db_record.timestamp
                ))
            
            return records
        finally:
            session.close()
    
    async def get_stats(self) -> Dict:
        """
        Get aggregate statistics from stored records.
        
        Returns:
            Dictionary with statistics
        """
        session = self.db_manager.get_session()
        try:
            total_events = session.query(AnalyticsRecordDB).count()
            
            if total_events == 0:
                return {
                    "total_events": 0,
                    "avg_confidence": 0.0,
                    "by_label": {},
                    "by_source": {}
                }
            
            # Average confidence
            avg_confidence = session.query(func.avg(AnalyticsRecordDB.confidence)).scalar() or 0.0
            
            # Count by label
            label_counts = (session.query(
                AnalyticsRecordDB.detection_label,
                func.count(AnalyticsRecordDB.id)
            )
            .group_by(AnalyticsRecordDB.detection_label)
            .all())
            
            by_label = {label: count for label, count in label_counts}
            
            # Count by source
            source_counts = (session.query(
                AnalyticsRecordDB.source,
                func.count(AnalyticsRecordDB.id)
            )
            .group_by(AnalyticsRecordDB.source)
            .all())
            
            by_source = {source: count for source, count in source_counts}
            
            return {
                "total_events": total_events,
                "avg_confidence": float(avg_confidence),
                "by_label": by_label,
                "by_source": by_source
            }
        finally:
            session.close()
    
    async def clear_all(self):
        """Clear all analytics records (for testing)."""
        session = self.db_manager.get_session()
        try:
            session.query(AnalyticsRecordDB).delete()
            session.commit()
        finally:
            session.close()
