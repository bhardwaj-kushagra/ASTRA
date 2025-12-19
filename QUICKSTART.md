# ASTRA Prototype - Quick Start Guide

## Overview
This is a minimal viable prototype of ASTRA demonstrating the core detection pipeline:
- **Ingestion Service** (port 8001): Collects content from files and HTTP sources
- **Detection Service** (port 8002): Classifies text using transformer models
- **Risk Analytics** (port 8003): Dashboard and aggregation layer

## Architecture
```
┌─────────────────┐
│   Ingestion     │  File/HTTP connectors → Content events
│   Service       │
│   (port 8001)   │
└────────┬────────┘
         │
         │ REST API calls
         ▼
┌─────────────────┐
│   Detection     │  Zero-shot classifier → AI/Human/Suspicious
│   Service       │
│   (port 8002)   │
└────────┬────────┘
         │
         │ Results aggregation
         ▼
┌─────────────────┐
│ Risk Analytics  │  Dashboard + Statistics
│   Service       │
│   (port 8003)   │
└─────────────────┘
```

## Prerequisites
- Python 3.10 or higher
- 8GB+ RAM (for transformer models)
- Internet connection (first run downloads models)

## Installation

### Quick Setup (Recommended)

**Step 1: Install Dependencies**

From the ASTRA root directory, run the automated setup script:

```powershell
.\setup.ps1
```

This will:
- Install required Python packages (fastapi, transformers, sqlalchemy, etc.)
- Download AI models on first run

**Step 2: Initialize Database**

Initialize the SQLite database for persistent storage:

```powershell
python tools\scripts\init_db.py
```

This creates `data\astra.db` with all necessary tables.

### Manual Setup
- Install all dependencies for all services
- Activate the environment

### Manual Setup (Alternative)

If you prefer to install manually:

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install each service's dependencies
cd services\ingestion
pip install -r requirements.txt
cd ..\..

cd services\detection
pip install -r requirements.txt
cd ..\..

cd services\risk-analytics
pip install -r requirements.txt
cd ..\..
```

## Running the Prototype

### Quick Start (Recommended)

**From the ASTRA root directory**, run the startup script:

```powershell
.\tools\scripts\start-all-services.ps1
```

This will launch all three services in separate PowerShell windows automatically.

### Manual Start (3 separate terminals)

**Important:** Always run from the ASTRA root directory, then `cd` into each service folder.

**Terminal 1 - Ingestion Service:**
```powershell
# From ASTRA root:
cd services\ingestion
python main.py
```

**Terminal 2 - Detection Service:**
```powershell
# From ASTRA root:
cd services\detection
python main.py
```

**Terminal 3 - Analytics Service:**
```powershell
# From ASTRA root:
cd services\risk-analytics
python main.py
```

## Testing the System

### 1. Check service health
```powershell
# Ingestion
curl http://localhost:8001

# Detection
curl http://localhost:8002

# Analytics
curl http://localhost:8003
```

### 2. Test file ingestion
```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8001/ingest" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "connector_type": "file",
    "config": {
      "path": "..\\..\\data\\samples",
      "pattern": "*.txt"
    }
  }'

```

### 3. Test detection directly
```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8002/detect" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "text": "I finally finished that book you lent me, and honestly, Im still staring at the wall trying to process that ending. We definitely need to grab coffee this weekend because I have so many thoughts.."
  }'
```

### 4. Sync events to analytics
```powershell
curl -X POST http://localhost:8003/sync-from-ingestion
```

### 5. View dashboard
Open browser to: **http://localhost:8003/dashboard**

### 6. Run integration tests
```powershell
python tools\scripts\test_integration.py
```

## API Endpoints

### Ingestion Service (8001)
- `GET /` - Health check
- `POST /ingest` - Trigger ingestion with connector config
- `GET /events` - List ingested events

### Detection Service (8002)
- `GET /` - Health check
- `POST /detect` - Analyze text content
- `GET /models` - List available detectors

### Analytics Service (8003)
- `GET /` - Health check
- `GET /dashboard` - Web dashboard (HTML)
- `POST /analyze` - Submit content for detection + storage
- `GET /records` - Retrieve detection records
- `GET /stats` - Aggregate statistics
- `POST /sync-from-ingestion` - Pull and analyze ingestion events

## Extending the Prototype

### Adding a new connector
1. Create `services/ingestion/connectors/my_connector.py`
2. Extend `Connector` base class
3. Register with `ConnectorRegistry.register("my-connector", MyConnector)`

### Adding a new detector
1. Create `services/detection/detectors/my_detector.py`
2. Extend `Detector` base class
3. Register with `DetectorRegistry.register("my-detector", MyDetector)`

### Integrating new services
- Future modules (graph intelligence, attribution, federation) follow the same pattern
- Services communicate via REST APIs (can be replaced with message queues)
- Shared schemas in `data/schemas/models.py`

## Troubleshooting

**Model download fails:**
- Check internet connection
- Increase timeout in detector initialization

**Import errors:**
- Ensure `data/schemas/models.py` is accessible
- Check `sys.path` modifications in service files

**Port conflicts:**
- Change ports in `main.py` files or set environment variables

**Out of memory:**
- Use smaller models (e.g., `distilbert-base-uncased`)
- Reduce batch sizes
- Run services on separate machines

## Next Steps
- Add message queue (Redis Streams, Kafka) for asynchronous processing
- Implement graph intelligence service for propagation analysis
- Build attribution service with watermarking integration
- Deploy using Docker and Kubernetes
- Add CI/CD pipelines and monitoring

See `docs/roadmap.md` for full development plan.
