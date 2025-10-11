"""
In-memory data store for analytics service.
"""
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import AnalyticsRecord


class AnalyticsStore:
    """Simple in-memory storage for detection results."""
    
    def __init__(self):
        self.records: List[AnalyticsRecord] = []
    
    async def add_record(self, record: AnalyticsRecord):
        """Add a new analytics record."""
        self.records.append(record)
    
    async def get_recent(self, limit: int = 100) -> List[AnalyticsRecord]:
        """Get most recent records."""
        return self.records[-limit:]
    
    async def get_all(self) -> List[AnalyticsRecord]:
        """Get all records."""
        return self.records
    
    async def get_by_label(self, label: str) -> List[AnalyticsRecord]:
        """Filter records by detection label."""
        return [r for r in self.records if r.detection_label == label]
    
    async def clear(self):
        """Clear all records."""
        self.records.clear()
    
    async def get_stats(self) -> dict:
        """Calculate aggregate statistics."""
        if not self.records:
            return {
                "total_events": 0,
                "by_label": {},
                "avg_confidence": 0.0
            }
        
        label_counts = {}
        total_confidence = 0.0
        
        for record in self.records:
            label_counts[record.detection_label] = label_counts.get(record.detection_label, 0) + 1
            total_confidence += record.confidence
        
        return {
            "total_events": len(self.records),
            "by_label": label_counts,
            "avg_confidence": total_confidence / len(self.records)
        }
