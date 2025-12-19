# ASTRA - MVP Reference Documentation

**Date:** December 20, 2025  
**Status:** Phase 1 (Prototype / MVP)

## 1. Project Overview
**ASTRA** is a modular, microservice-based system designed to detect, analyze, and manage risks associated with AI-generated content. It serves as a platform for ingesting content from various sources, running it through pluggable detection models (to identify if text is human or AI-written), and visualizing the results in a risk analytics dashboard.

The project is currently in the **Prototype / MVP Phase**, focusing on the core pipeline of ingestion, detection, and basic reporting.

---

## 2. System Architecture (Current Implementation)
The system is built using **Python** and **FastAPI**, organized into three distinct microservices that communicate via HTTP. Data persistence is handled by **SQLite** using **SQLAlchemy**.

### A. Shared Core (`data/`)
*   **Purpose:** Defines the common language and storage for all services.
*   **Key Files:**
    *   `data/schemas/models.py`: Contains Pydantic models shared across services.
        *   `ContentEvent`: Represents raw ingested data.
        *   `DetectionResult`: Represents the output of an AI detector (label, confidence).
    *   `data/schemas/database.py`: Defines the SQLAlchemy ORM models (`ContentEventDB`, `DetectionResultDB`) and the `DatabaseManager` for SQLite connections.

### B. Ingestion Service (`services/ingestion/`)
*   **Purpose:** Fetches content from external sources and normalizes it.
*   **Key Components:**
    *   **Connectors**: Uses a `ConnectorRegistry` to manage plugins.
        *   `FileConnector`: Reads local files.
        *   `HttpConnector`: Fetches content from URLs.
    *   **Publisher**: `SQLitePublisher` persists raw events to the shared SQLite database.
*   **Entry Point**: `services/ingestion/main.py` exposes endpoints like `/ingest` to trigger data collection.

### C. Detection Service (`services/detection/`)
*   **Purpose:** The "Brain" of the system. Analyzes text to determine its origin.
*   **Key Components:**
    *   **Detectors**: Uses a `DetectorRegistry` to switch between models.
        *   **Simple**: A heuristic detector (likely based on text length/patterns).
        *   **RAG**: Retrieval-Augmented Generation detector (minimal implementation).
        *   **Zero-Shot**: Uses a Hugging Face model (`facebook/bart-large-mnli`) to classify text as "AI-generated", "human-written", or "suspicious".
*   **Configuration**: The active detector is controlled via the `DETECTOR_NAME` environment variable or runtime API calls.
*   **Entry Point**: `services/detection/main.py` exposes `/detect`.

### D. Risk Analytics Service (`services/risk-analytics/`)
*   **Purpose:** The user interface and orchestration layer.
*   **Key Components:**
    *   **Dashboard**: A server-side rendered UI (Jinja2 templates) at `/dashboard`.
    *   **Sync Logic**: The `/sync-from-ingestion` endpoint pulls data from the Ingestion service and sends it to the Detection service, effectively bridging the two.
    *   **Store**: `SQLiteAnalyticsStore` saves the final analysis results.
*   **Entry Point**: `services/risk-analytics/main.py`.

---

## 3. Workflow & Data Flow
1.  **Ingest**: A user triggers ingestion (e.g., via API). The **Ingestion Service** fetches data and saves it as `ContentEvent` records in SQLite.
2.  **Sync**: The **Risk Analytics Service** requests events from Ingestion (`GET /events`).
3.  **Detect**: For each event, Risk Analytics sends the text to the **Detection Service** (`POST /detect`).
4.  **Analyze**: The Detection Service runs the active model (e.g., Zero-Shot) and returns a `DetectionResult`.
5.  **Store & View**: Risk Analytics saves the result as an `AnalyticsRecord` and displays it on the dashboard.

---

## 4. Future Plans & Roadmap
The project is structured for expansion. While the "Detection Core" is working, several major components are planned but currently exist only as placeholders.

### Immediate Next Steps (Codebase Improvements)
1.  **Asynchronous Processing**: Currently, the `sync-from-ingestion` process performs synchronous HTTP calls in a loop. This should be moved to a background task queue (e.g., Celery or just `asyncio.gather`) to improve performance.
2.  **Database Migration**: The system uses a single SQLite file. Moving to PostgreSQL would be necessary for concurrency and scale.
3.  **Automated Sync**: Instead of manual `/sync-from-ingestion` calls, implement an event bus (Kafka/RabbitMQ) so ingestion automatically triggers detection.

### Roadmap (Based on `docs/` and Placeholders)
*   **Phase 2: Attribution & Graph Intelligence**
    *   *Goal*: Identify *who* or *what specific model* generated the content.
    *   *Status*: Folders `services/attribution` and `services/graph-intelligence` exist but contain only READMEs.
    *   *Plan*: Implement watermarking verification and stylometric forensics.

*   **Phase 3: Federation**
    *   *Goal*: Allow different ASTRA instances to share threat intelligence securely.
    *   *Status*: Folder `services/federation` is empty.
    *   *Plan*: Build a secure exchange gateway.

*   **Phase 4: Red Teaming**
    *   *Goal*: Adversarial testing of the detectors.
    *   *Status*: Folder `services/red-team` is empty.
    *   *Plan*: Create automated attacks to test detector robustness.

---

## 5. Summary of Findings
*   **Code Quality**: The code is clean, modular, and uses modern Python features (Type hinting, Pydantic).
*   **Extensibility**: The Registry pattern used in Ingestion and Detection makes it very easy to add new data sources or AI models without rewriting core logic.
*   **Current State**: It is a functional prototype capable of end-to-end demonstration but requires architectural hardening (DB, Queues) for production use.
