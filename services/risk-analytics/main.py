"""Risk analytics service main application."""
from fastapi import FastAPI, Request, Response, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import uuid
from pathlib import Path
import sys
import os
import requests

# Setup path for shared schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import AnalyticsRecord, DetectionRequest, DetectionResult, ContentEvent
from sqlite_store import SQLiteAnalyticsStore

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ASTRA Risk Analytics Service", version="0.1.0")

# Static files and templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Global store instance (SQLite for persistent storage)
analytics_store = SQLiteAnalyticsStore()

# Configuration for service endpoints
DETECTION_SERVICE_URL = os.getenv("DETECTION_SERVICE_URL", "http://localhost:8002")
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")


def _fetch_detector_info() -> tuple[Optional[str], list[str]]:
    """Fetch active detector and available options from detection service."""
    try:
        resp = requests.get(f"{DETECTION_SERVICE_URL}/detector", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        active = data.get("active_detector") or data.get("default")
        available = data.get("available_detectors") or data.get("detectors") or []
        return active, list(available)
    except Exception:
        return None, []


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "risk-analytics",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/favicon.ico")
async def favicon() -> Response:
    """Return an empty favicon to avoid 404 noise in logs."""
    return Response(status_code=204)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render analytics dashboard."""
    stats = await analytics_store.get_stats()
    recent_records = await analytics_store.get_recent(limit=50)
    active_detector, available_detectors = _fetch_detector_info()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "records": recent_records,
        "active_detector": active_detector,
        "available_detectors": available_detectors,
        "error": None,
    })


@app.post("/dashboard/analyze-text", response_class=HTMLResponse)
async def dashboard_analyze_text(request: Request, text: str = Form(...)):
    """Analyze ad-hoc text from the dashboard and store result."""
    try:
        response = requests.post(
            f"{DETECTION_SERVICE_URL}/detect",
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        result = DetectionResult(**response.json())

        analytics_record = AnalyticsRecord(
            event_id=result.event_id or f"dash-{uuid.uuid4().hex[:8]}",
            source="dashboard-text",
            text_preview=text[:200],
            detection_label=result.label,
            confidence=result.confidence,
            timestamp=result.timestamp,
        )
        await analytics_store.add_record(analytics_record)

        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as exc:  # pragma: no cover - UI path
        stats = await analytics_store.get_stats()
        recent_records = await analytics_store.get_recent(limit=50)
        active_detector, available_detectors = _fetch_detector_info()
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "stats": stats,
                "records": recent_records,
                "active_detector": active_detector,
                "available_detectors": available_detectors,
                "error": str(exc),
            },
            status_code=500,
        )


@app.post("/dashboard/upload-file", response_class=HTMLResponse)
async def dashboard_upload_file(request: Request, file: UploadFile = File(...)):
    """Analyze an uploaded text file via the dashboard and store result."""
    try:
        content_bytes = await file.read()
        text = content_bytes.decode("utf-8", errors="ignore")
        if not text.strip():
            raise ValueError("Uploaded file is empty or not valid text.")

        response = requests.post(
            f"{DETECTION_SERVICE_URL}/detect",
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        result = DetectionResult(**response.json())

        analytics_record = AnalyticsRecord(
            event_id=result.event_id or f"file-{uuid.uuid4().hex[:8]}",
            source=f"upload:{file.filename}",
            text_preview=text[:200],
            detection_label=result.label,
            confidence=result.confidence,
            timestamp=result.timestamp,
        )
        await analytics_store.add_record(analytics_record)

        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as exc:  # pragma: no cover - UI path
        stats = await analytics_store.get_stats()
        recent_records = await analytics_store.get_recent(limit=50)
        active_detector, available_detectors = _fetch_detector_info()
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "stats": stats,
                "records": recent_records,
                "active_detector": active_detector,
                "available_detectors": available_detectors,
                "error": str(exc),
            },
            status_code=500,
        )


@app.post("/dashboard/set-detector", response_class=HTMLResponse)
async def dashboard_set_detector(request: Request, detector_name: str = Form(...)):
    """Switch the active detector via the dashboard selector."""
    try:
        resp = requests.post(
            f"{DETECTION_SERVICE_URL}/detector/{detector_name}",
            timeout=10,
        )
        resp.raise_for_status()
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as exc:  # pragma: no cover - UI path
        stats = await analytics_store.get_stats()
        recent_records = await analytics_store.get_recent(limit=50)
        active_detector, available_detectors = _fetch_detector_info()
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "stats": stats,
                "records": recent_records,
                "active_detector": active_detector,
                "available_detectors": available_detectors,
                "error": f"Failed to switch detector: {exc}",
            },
            status_code=500,
        )


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
