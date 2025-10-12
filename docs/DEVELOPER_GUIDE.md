# ASTRA Developer Guide (Deep-Dive)

This guide is a comprehensive onboarding document for new contributors. It explains what ASTRA is, what each part of the repository does, how the services work together, how to run/debug locally, and where to go next. It is intentionally detailed and operationally focused.

Contents
- 1. Project Overview
- 2. Architecture and Data Flow
- 3. Folder Structure and Key Files (map)
- 4. Data Contract and Persistence (ORM + schema)
- 5. Service-by-Service Deep Dive (APIs, internals)
- 6. Local Setup, Running, and Scripts
- 7. Developer Tasks and Workflows
- 8. Theory and Design Rationale
- 9. Troubleshooting and Diagnostics
- 10. Roadmap and Next Steps
- 11. Contribution Guide
- 12. Appendix: Quick Commands and References

## 1. Project Overview

ASTRA is a lightweight microservice system for near–real-time risk analytics. It ingests content events, performs detection/classification, and aggregates analytics for dashboards. The current implementation prioritizes simplicity and durability using SQLite + SQLAlchemy.

- Language: Python 3.11
- Services: Ingestion (8001), Detection (8002), Risk Analytics (8003)
- Persistence: SQLite (data/astra.db) with SQLAlchemy ORM
- Orchestration: PowerShell scripts (Windows-first), uvicorn

High-level flow
1) Ingestion receives content events (text + metadata), serializes metadata to JSON, and persists rows.  
2) Detection processes text and returns label + confidence (stateless except for writes).  
3) Risk analytics aggregates and stores records for dashboard/queries.

## 2. Architecture and Data Flow

Core building blocks:
- FastAPI apps per service, run using uvicorn.
- Shared Pydantic models for requests/responses.
- Shared SQLAlchemy models for persistence.
- Persistence adapters isolate data access (Publisher/Store pattern).

Data flow (local, single-node):
source → ingestion (/ingest) → SQLite:content_events → detection (/detect) → SQLite:detection_results → analytics (/analyze or /sync-from-ingestion) → SQLite:analytics_records → dashboard (/dashboard)

Concurrency model:
- SQLite handles transactional writes; suitable for low/medium local workloads.  
- Services are stateless and can be restarted independently.

Evolvability:
- Database engine can be swapped by adjusting the SQLAlchemy engine URL and introducing migrations.
- Connectors and detectors are pluggable via registries.

## 3. Folder Structure and Key Files (map)

- services/
  - ingestion/
    - main.py: FastAPI app; health `/`, ingest `/ingest`, list `/events`.
    - sqlite_publisher.py: Writes to content_events; batch insert; list/count methods.
    - connectors/
      - file_connector.py: Reads files from a directory, yields events.
      - http_connector.py: Fetches content via HTTP, yields events.
    - connector.py: ConnectorRegistry for discovery/instantiation.
  - detection/
    - main.py: FastAPI app; health `/`, detect `/detect`, list models `/models`.
    - detector.py: DetectorRegistry and base interfaces.
    - detectors/
      - zero_shot_detector.py: Example detector; integrates a zero-shot classification approach (configurable labels).
  - risk-analytics/
    - main.py: FastAPI app; health `/`, dashboard `/dashboard`, records `/records`, stats `/stats`, sync `/sync-from-ingestion`.
    - sqlite_store.py: CRUD for analytics_records; query aggregates.
    - templates/
      - dashboard.html: HTML + Jinja2 template for recent records + stats.

- data/schemas/
  - models.py: Pydantic models (ContentEvent, DetectionRequest/Result, AnalyticsRecord).
  - database.py: SQLAlchemy ORM models (ContentEventDB, DetectionResultDB, AnalyticsRecordDB) and DatabaseManager.

- tools/scripts/
  - init_db.py: Initializes (creates) schema if missing.
  - start-with-sqlite.ps1: Start services using python main.py with safe WorkingDirectory.
  - start-all-uvicorn.ps1: Start uvicorn for each service (127.0.0.1) with separate windows.
  - check-services.ps1: Robust health probe using IPv4 first with retries/backoff.
  - stop-all.ps1: Kills service process trees, waits until ports are free.
  - restart-all.ps1: Stop + ensure DB + start sequence.

- docs/
  - ASTRA_Proposed_Solution.md: IEEE-style article of the completed stage.
  - DEVELOPER_GUIDE.md: This guide.

- .vscode/
  - settings.json: Editor settings and Python interpreter path.

- requirements.txt: Python dependencies.
- .gitignore: Ignore venvs and SQLite artifacts.

## 4. Data Contract and Persistence (ORM + schema)

Pydantic (API) models (data/schemas/models.py):
- ContentEvent: id, source, text, metadata (dict), timestamp
- DetectionRequest: text
- DetectionResult: label, confidence, detector_type?, event_id?, timestamp
- AnalyticsRecord: event_id, source, text_preview, detection_label, confidence, timestamp

SQLAlchemy (DB) models (data/schemas/database.py):
- content_events
  - id (Integer, PK)
  - source (String)
  - text (Text)
  - metadata_json (Text)
  - timestamp (DateTime)
- detection_results
  - id (Integer, PK)
  - event_id (Integer, FK → content_events.id)
  - label (String)
  - confidence (Float)
  - detector_type (String)
  - timestamp (DateTime)
- analytics_records
  - id (Integer, PK)
  - event_id (Integer, FK → content_events.id)
  - source (String)
  - text_preview (Text)
  - detection_label (String)
  - confidence (Float)
  - timestamp (DateTime)

Indexes: Add as needed per read/write patterns (future step with Alembic).

## 5. Service-by-Service Deep Dive

Ingestion Service (8001)
- Endpoints:
  - GET / → health, connectors list
  - POST /ingest {connector_type, config} → runs connector.fetch(), persists via SQLitePublisher
  - GET /events?limit=N → recent events for debugging
- Internals:
  - ConnectorRegistry instantiates the requested connector with config
  - SQLitePublisher.publish_batch() writes many rows in a transaction
  - JSON metadata serialized to metadata_json

Detection Service (8002)
- Endpoints:
  - GET / → health, available_detectors
  - POST /detect {text} → returns DetectionResult
  - GET /models → list detectors
- Internals:
  - DetectorRegistry returns the configured/default detector (e.g., zero-shot)
  - get_detector() lazily initializes to reduce cold-start latency elsewhere
  - Detector.detect() returns label + confidence + timestamp

Risk Analytics Service (8003)
- Endpoints:
  - GET / → health
  - GET /dashboard → HTML view using Jinja2 templates
  - GET /records?limit=N → recent analytics records
  - GET /stats → aggregate statistics (counts per label, avg confidence, etc.)
  - POST /sync-from-ingestion → pulls events from ingestion, detects, stores records
- Internals:
  - SQLiteAnalyticsStore.get_recent() returns latest AnalyticsRecord rows
  - SQLiteAnalyticsStore.get_stats() computes aggregates via SQLAlchemy
  - Simple orchestration to call detection and store results

## 6. Local Setup, Running, and Scripts

Prereqs
- Python 3.11 (scripts use C:\python 3.11\python.exe by default)
- Windows PowerShell 5.1+

Install dependencies
```powershell
pip install -r requirements.txt
```

Initialize database
```powershell
python tools\scripts\init_db.py
```

Start services
- Uvicorn (separate windows, logs visible):
```powershell
.\tools\scripts\start-all-uvicorn.ps1
```
- Standard start (python main.py):
```powershell
.\tools\scripts\start-with-sqlite.ps1
```

Check health
```powershell
.\tools\scripts\check-services.ps1
```

Stop/Restart
```powershell
.\tools\scripts\stop-all.ps1
.\tools\scripts\restart-all.ps1
```

Notes
- Scripts avoid inline -Command quoting to prevent parser errors in paths with apostrophes.
- Health check prefers 127.0.0.1 (avoids IPv6 localhost quirks) and retries.

## 7. Developer Tasks and Workflows

Add a new connector (ingestion)
- Create services/ingestion/connectors/<your_connector>.py
- Register in connectors/__init__.py or via ConnectorRegistry
- Implement a fetch() generator that yields ContentEvent

Add a new detector (detection)
- Create services/detection/detectors/<your_detector>.py
- Register in detectors/__init__.py or via DetectorRegistry
- Implement detect(request: DetectionRequest) → DetectionResult

Extend analytics
- Add query/aggregation in services/risk-analytics/sqlite_store.py
- Expose via services/risk-analytics/main.py (e.g., /stats, /records)
- Update dashboard template as needed

Schema changes
- Edit data/schemas/database.py
- Re-run tools/scripts/init_db.py for additive changes; for destructive updates, add Alembic migrations (future work)

## 8. Theory and Design Rationale

- Durability and auditability: Event and detection tables include timestamps and are append-only (immutable history).
- Simplicity-first for local: SQLite requires no external services and is sufficient for early prototyping or single-node deployments.
- Separation of concerns: Each service has a single responsibility; publishers/stores encapsulate persistence, minimizing coupling.
- Evolution path: Swap to PostgreSQL with minimal code churn; add migrations and structured logging/metrics when needed.

## 9. Troubleshooting and Diagnostics

Ports stuck in LISTEN after restart
- Run stop-all.ps1; it kills process trees and loops until ports are free.

Health shows NOT READY
- Use http://127.0.0.1:PORT instead of localhost.
- Give detection an extra minute on first run if it downloads models.

PowerShell parser error (terminator missing)
- Scripts use Start-Process with -WorkingDirectory to avoid quoting issues. If still seen, reload VS Code and retry.

Database missing or locked
- Re-run init_db.py to create tables.
- Ensure you don’t have the DB file open in another tool while writing.

Logging
- For uvicorn runs, use start-all-uvicorn.ps1 to keep a window per service. For headless logs, we can add file redirection on request.

## 10. Roadmap and Next Steps

Short-term
- Observability: structured logging, metrics, standard /health and /ready.
- Migrations: integrate Alembic.
- Packaging: Dockerfiles and compose for cross-platform reproducibility.
- Tests: expand unit and integration tests across service seams.

Mid-term
- Database evolution: PostgreSQL support.
- Search/indexing: consider adding FTS for text queries.
- Role-based access and auth for APIs and dashboard.

## 11. Contribution Guide

Coding standards
- Python: black/flake8 or ruff; type hints where feasible.
- PowerShell: PSScriptAnalyzer; prefer explicit variables over automatic ones.

Branching and commits
- Create feature branches; use conventional commit messages (feat:, fix:, docs:, chore:).

PRs and reviews
- Include reproduction steps; keep diffs focused; add tests when changing behavior.

## 12. Appendix: Quick Commands and References

Health checks
```powershell
.\tools\scripts\check-services.ps1
```

Manual service runs (debug)
```powershell
cd services\ingestion;  python -m uvicorn main:app --host 127.0.0.1 --port 8001
cd services\detection;  python -m uvicorn main:app --host 127.0.0.1 --port 8002
cd services\risk-analytics;  python -m uvicorn main:app --host 127.0.0.1 --port 8003
```

References
- SQLite: https://www.sqlite.org/docs.html
- SQLAlchemy: https://docs.sqlalchemy.org
- FastAPI: https://fastapi.tiangolo.com
- Uvicorn: https://www.uvicorn.org

---

If anything is unclear, open an issue or start a discussion. Contributions are welcome!
