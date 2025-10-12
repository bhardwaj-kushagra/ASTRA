"""
Ingestion service main application.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Setup path for shared schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))

from models import ContentEvent
from connector import ConnectorRegistry
from sqlite_publisher import SQLitePublisher

# Import connectors to register them
from connectors import file_connector, http_connector

app = FastAPI(title="ASTRA Ingestion Service", version="0.1.0")

# Global publisher instance (SQLite for persistent storage)
publisher = SQLitePublisher()


class ConnectorConfig(BaseModel):
    """Configuration for running a connector."""
    connector_type: str
    config: dict


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "ingestion",
        "version": "0.1.0",
        "status": "running",
        "connectors": ConnectorRegistry.list_connectors()
    }


@app.post("/ingest", response_model=dict)
async def ingest_content(connector_config: ConnectorConfig):
    """
    Trigger content ingestion using specified connector.
    
    Args:
        connector_config: Connector type and configuration
    
    Returns:
        Summary of ingestion results
    """
    try:
        connector = ConnectorRegistry.get_connector(
            connector_config.connector_type,
            connector_config.config
        )
        
        events = list(connector.fetch())
        await publisher.publish_batch(events)
        
        return {
            "status": "success",
            "connector": connector_config.connector_type,
            "events_ingested": len(events),
            "event_ids": [e.id for e in events]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/events", response_model=List[ContentEvent])
async def get_events(limit: Optional[int] = 100):
    """
    Retrieve ingested events (for debugging/testing).
    
    Args:
        limit: Maximum number of events to return
    """
    all_events = await publisher.get_all_events()
    return all_events[-limit:] if limit else all_events


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
