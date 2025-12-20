"""Risk analytics service main application."""
from fastapi import FastAPI, Request, Response, Form, UploadFile, File, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import uuid
from pathlib import Path
import sys
import os
import asyncio
import requests
import httpx
from sqlalchemy import func

# Setup path for shared schemas and database models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import AnalyticsRecord, DetectionRequest, DetectionResult, ContentEvent
from database import DatabaseManager, ContentEventDB, AnalyticsRecordDB, ThreatIndicatorDB
from sqlite_store import SQLiteAnalyticsStore
from cooccurrence_graph import build_actor_sourcehash_graph
from threat_exchange import ThreatExchangeEnvelope, ThreatExchangeProducer, ThreatIndicator, build_summary

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ASTRA Risk Analytics Service", version="0.1.0")

# Static files and templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Global store instance (SQLite for persistent storage)
analytics_store = SQLiteAnalyticsStore()

# Shared database manager for direct status updates
db_manager = DatabaseManager()

# Configuration for service endpoints
DETECTION_SERVICE_URL = os.getenv("DETECTION_SERVICE_URL", "http://localhost:8002")
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")


def _instance_id() -> str:
    return os.getenv("ASTRA_INSTANCE_ID") or os.getenv("COMPUTERNAME") or "astra-instance"


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


@app.get("/graph/cooccurrence")
async def get_cooccurrence_graph(
    max_edges: int = Query(300, ge=1, le=5000, description="Maximum number of edges to return"),
    max_nodes: int = Query(250, ge=2, le=5000, description="Maximum number of nodes to return"),
):
    """Return a co-occurrence graph over actor_id and source_hash.

    This uses direct DB reads from the shared SQLite database.
    """
    session = db_manager.get_session()
    try:
        return build_actor_sourcehash_graph(
            session=session,
            ContentEventDB=ContentEventDB,
            max_edges=max_edges,
            max_nodes=max_nodes,
        )
    finally:
        session.close()


@app.get("/threat-exchange/export")
async def export_threat_exchange(
    limit: int = Query(200, ge=1, le=5000, description="Maximum number of indicators to export"),
    base_url: Optional[str] = Query(None, description="Optional base URL to include in producer metadata"),
):
    """Export threat indicators as a versioned JSON envelope.

    Indicators are derived from local analytics records joined to content_events.
    """
    session = db_manager.get_session()
    try:
        rows = (
            session.query(
                ContentEventDB.actor_id,
                ContentEventDB.source_hash,
                AnalyticsRecordDB.detection_label,
                func.max(AnalyticsRecordDB.confidence),
                func.count(AnalyticsRecordDB.id),
                func.min(AnalyticsRecordDB.timestamp),
                func.max(AnalyticsRecordDB.timestamp),
            )
            .join(AnalyticsRecordDB, AnalyticsRecordDB.event_id == ContentEventDB.id)
            .filter(ContentEventDB.actor_id.isnot(None))
            .filter(ContentEventDB.source_hash.isnot(None))
            .group_by(ContentEventDB.actor_id, ContentEventDB.source_hash, AnalyticsRecordDB.detection_label)
            .order_by(func.count(AnalyticsRecordDB.id).desc())
            .limit(limit)
            .all()
        )

        indicators: List[ThreatIndicator] = []
        for actor_id, source_hash, label, max_conf, count, first_seen, last_seen in rows:
            indicators.append(
                ThreatIndicator(
                    actor_id=actor_id,
                    source_hash=source_hash,
                    detection_label=label,
                    max_confidence=float(max_conf or 0.0),
                    event_count=int(count or 0),
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
            )

        producer = ThreatExchangeProducer(instance_id=_instance_id(), base_url=base_url)
        envelope = ThreatExchangeEnvelope(
            producer=producer,
            indicators=indicators,
            summary=build_summary(indicators=indicators),
        )
        return envelope.model_dump()
    finally:
        session.close()


@app.post("/threat-exchange/import")
async def import_threat_exchange(envelope: ThreatExchangeEnvelope):
    """Import a threat exchange envelope and persist indicators.

    This is intentionally additive: it does not modify local content_events or analytics_records.
    """
    if not envelope.schema_version.startswith("astra-threat-exchange-"):
        raise HTTPException(status_code=400, detail=f"Unsupported schema_version: {envelope.schema_version}")

    session = db_manager.get_session()
    try:
        inserted = 0
        for ind in envelope.indicators:
            if ind.event_count < 1:
                continue
            db_row = ThreatIndicatorDB(
                producer_instance_id=envelope.producer.instance_id,
                actor_id=ind.actor_id,
                source_hash=ind.source_hash,
                detection_label=ind.detection_label,
                max_confidence=float(ind.max_confidence),
                event_count=int(ind.event_count),
                first_seen=ind.first_seen,
                last_seen=ind.last_seen,
            )
            session.add(db_row)
            inserted += 1

        session.commit()
        return {
            "status": "success",
            "producer_instance_id": envelope.producer.instance_id,
            "inserted": inserted,
        }
    finally:
        session.close()


@app.get("/threat-exchange/indicators")
async def list_imported_indicators(
    limit: int = Query(200, ge=1, le=5000),
    producer_instance_id: Optional[str] = Query(None, description="Filter by producer instance"),
):
    """List imported threat indicators."""
    session = db_manager.get_session()
    try:
        q = session.query(ThreatIndicatorDB).order_by(ThreatIndicatorDB.received_at.desc())
        if producer_instance_id:
            q = q.filter(ThreatIndicatorDB.producer_instance_id == producer_instance_id)
        rows = q.limit(limit).all()
        return [
            {
                "id": r.id,
                "producer_instance_id": r.producer_instance_id,
                "actor_id": r.actor_id,
                "source_hash": r.source_hash,
                "detection_label": r.detection_label,
                "max_confidence": r.max_confidence,
                "event_count": r.event_count,
                "first_seen": r.first_seen,
                "last_seen": r.last_seen,
                "received_at": r.received_at,
            }
            for r in rows
        ]
    finally:
        session.close()


@app.post("/sync-from-ingestion")
async def sync_from_ingestion():
    """
    Pull NEW events from ingestion and run them through detection asynchronously.
    Updates processing_status in the shared DB directly (DETECTED/FAILED).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{INGESTION_SERVICE_URL}/events")
            response.raise_for_status()
            raw_events = response.json()

        all_events = [ContentEvent(**e) for e in raw_events]

        # Only process events that are still marked as NEW
        new_events: List[ContentEvent] = [
            e for e in all_events
            if (e.processing_status or "NEW").upper() == "NEW"
        ]

        if not new_events:
            return {
                "status": "success",
                "events_fetched": len(all_events),
                "events_processed": 0,
                "message": "No NEW events to process."
            }

        async def process_event(event: ContentEvent) -> bool:
            """Run detection for a single event and update status/analytics."""
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    det_response = await client.post(
                        f"{DETECTION_SERVICE_URL}/detect",
                        json={"text": event.text},
                    )
                    det_response.raise_for_status()

                result = DetectionResult(**det_response.json())

                analytics_record = AnalyticsRecord(
                    event_id=event.id,
                    source=event.source,
                    text_preview=event.text[:200],
                    detection_label=result.label,
                    confidence=result.confidence,
                    timestamp=result.timestamp,
                )
                await analytics_store.add_record(analytics_record)

                _set_event_processing_status(event.id, "DETECTED")
                return True
            except Exception:
                _set_event_processing_status(event.id, "FAILED")
                return False

        # Run detection concurrently for all NEW events
        tasks = [process_event(event) for event in new_events]
        results = await asyncio.gather(*tasks)
        processed = sum(1 for r in results if r)

        return {
            "status": "success",
            "events_fetched": len(all_events),
            "events_processed": processed,
            "events_failed": len(new_events) - processed,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def _set_event_processing_status(event_id: str, status: str) -> None:
    """Update processing_status for a content event in the shared DB."""
    session = db_manager.get_session()
    try:
        event = session.query(ContentEventDB).filter(ContentEventDB.id == event_id).first()
        if event is not None:
            event.processing_status = status
            session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
