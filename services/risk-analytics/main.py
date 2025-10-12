"""
Risk analytics service main application.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import sys
import os
import requests

# Setup path for shared schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import AnalyticsRecord, DetectionRequest, DetectionResult, ContentEvent
from sqlite_store import SQLiteAnalyticsStore

app = FastAPI(title="ASTRA Risk Analytics Service", version="0.1.0")

# Global store instance (SQLite for persistent storage)
analytics_store = SQLiteAnalyticsStore()

# Templates for simple HTML dashboard
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Configuration for service endpoints
DETECTION_SERVICE_URL = os.getenv("DETECTION_SERVICE_URL", "http://localhost:8002")
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "risk-analytics",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render analytics dashboard."""
    stats = await analytics_store.get_stats()
    recent_records = await analytics_store.get_recent(limit=50)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "records": recent_records
    })


@app.post("/analyze", response_model=dict)
async def analyze_content(request: DetectionRequest):
    """
    Submit content for detection and store result.
    
    Args:
        request: DetectionRequest with text to analyze
    
    Returns:
        Detection result and storage confirmation
    """
    try:
        # Call detection service
        response = requests.post(
            f"{DETECTION_SERVICE_URL}/detect",
            json=request.dict(),
            timeout=30
        )
        response.raise_for_status()
        result = DetectionResult(**response.json())
        
        # Store in analytics
        analytics_record = AnalyticsRecord(
            event_id=result.event_id or "manual",
            source="api",
            text_preview=request.text[:200],
            detection_label=result.label,
            confidence=result.confidence,
            timestamp=result.timestamp
        )
        await analytics_store.add_record(analytics_record)
        
        return {
            "status": "success",
            "detection": result.dict(),
            "stored": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/records", response_model=List[AnalyticsRecord])
async def get_records(limit: int = 100):
    """Get recent analytics records."""
    return await analytics_store.get_recent(limit=limit)


@app.get("/stats")
async def get_stats():
    """Get aggregate statistics."""
    return await analytics_store.get_stats()


@app.post("/sync-from-ingestion")
async def sync_from_ingestion():
    """
    Pull events from ingestion service and run them through detection.
    
    Returns:
        Summary of sync operation
    """
    try:
        # Fetch events from ingestion
        response = requests.get(f"{INGESTION_SERVICE_URL}/events", timeout=10)
        response.raise_for_status()
        events = [ContentEvent(**e) for e in response.json()]
        
        processed = 0
        for event in events:
            # Send to detection
            det_response = requests.post(
                f"{DETECTION_SERVICE_URL}/detect",
                json={"text": event.text},
                timeout=30
            )
            if det_response.status_code == 200:
                result = DetectionResult(**det_response.json())
                
                # Store analytics record
                analytics_record = AnalyticsRecord(
                    event_id=event.id,
                    source=event.source,
                    text_preview=event.text[:200],
                    detection_label=result.label,
                    confidence=result.confidence,
                    timestamp=result.timestamp
                )
                await analytics_store.add_record(analytics_record)
                processed += 1
        
        return {
            "status": "success",
            "events_fetched": len(events),
            "events_processed": processed
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
