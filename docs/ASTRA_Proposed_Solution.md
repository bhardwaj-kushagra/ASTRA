# ASTRA: A Lightweight Microservice Architecture for Real‑Time Risk Analytics with SQLite Persistence

## Abstract

Organizations increasingly need near–real-time analytics pipelines that are easy to deploy, maintain, and extend—especially in constrained or heterogeneous environments. This article presents the first completed stage of ASTRA, a lightweight, Python-based microservice architecture for risk analytics. The current stage implements an end-to-end pipeline—event ingestion, detection, and analytics aggregation—backed by persistent storage using SQLite and SQLAlchemy. The design prioritizes portability (single-file database, zero external dependencies), reliability (transactional writes, explicit schemas), and developer ergonomics (clear contracts and simple operational scripts). We describe the system model, storage schema, service responsibilities, and operational considerations, then discuss security, limitations, and practical next steps. While the pipeline is built for local or single-node use, the abstractions are designed to enable later evolution to clustered databases or more advanced analytics without reworking the core interfaces. This proposed solution serves as a deployable foundation for applied research and rapid prototyping in risk analytics.

## Index Terms

Microservices; Event Ingestion; Real‑Time Analytics; SQLite; SQLAlchemy; Python; Persistent Storage; System Architecture; Operational Automation.

## 1. Introduction

Real-time or near–real-time risk analytics commonly begins with an event stream (content, telemetry, or logs), a detection step that assigns labels or scores, and an analytics step that aggregates insights for human or automated consumers. Many prototypes start with in-memory data structures, which are fast to develop but lose state across restarts and complicate cross-service coordination. ASTRA addresses this gap by grounding the pipeline in a persistent, transactional store from the outset—without introducing operational overhead.

This article details the first completed part of ASTRA: a minimal, production-lean pipeline composed of three Python HTTP microservices—Ingestion, Detection, and Risk Analytics—using SQLite (via SQLAlchemy) for durable storage. The goals are:

- Simplicity: zero external database servers, easy local setup.
- Reliability: ACID-compliant writes and explicit schemas.
- Evolvability: clear interfaces that support future scaling.

We focus on the implemented components and leave federated or distributed extensions for later work.

## 2. System Overview

ASTRA comprises three cooperating services and a shared persistence layer:

- Ingestion Service (port 8001): Receives content events (source, text, metadata), validates them, and persists to the database.
- Detection Service (port 8002): Processes ingested events to assign labels and confidence scores; persists detection results.
- Risk Analytics Service (port 8003): Builds aggregates and summaries for dashboards and reports.

The persistence layer is a single SQLite database file (data/astra.db) accessed via SQLAlchemy ORM. A small management utility initializes or resets the schema. Operational PowerShell scripts start and check the services to streamline local development on Windows.

## 3. Data Model and Contracts

ASTRA uses explicit, normalized tables with concise schemas that map to SQLAlchemy models:

- content_events
  - id (PK, String(36) UUID)
  - source (text)
  - actor_id (text; convention-based, not normalized)
  - source_hash (text; stable hash of source+content)
  - text (text)
  - metadata_json (text; JSON-serialized)
  - processing_status (text; NEW → DETECTED/FAILED)
  - timestamp (datetime)

- detection_results
  - id (PK, integer)
  - event_id (FK → content_events.id)
  - label (text)
  - confidence (real)
  - detector_type (text)
  - timestamp (datetime)

- analytics_records
  - id (PK, integer)
  - event_id (FK → content_events.id)
  - source (text)
  - text_preview (text)
  - detection_label (text)
  - confidence (real)
  - timestamp (datetime)

These tables encode the core contract between services:

1) Ingestion persists each event (with optional metadata).  
2) Detection persists a result for an event (label + confidence).  
3) Analytics derives and stores records suitable for dashboards.

Using JSON for metadata_json keeps the base schema stable while allowing rich, source-specific attributes.

## 4. Persistence Layer and Implementation

The persistence layer centers on a DatabaseManager that creates a SQLAlchemy engine and session factory, enabling safe session-scoped operations per request. SQLite is configured for local use with check_same_thread disabled (to accommodate service threading models) and uses file-backed storage at data/astra.db. Key components include:

- SQLAlchemy ORM models for each table, co-located in a single module for clarity.
- Database initialization utility that creates all tables (idempotent if already present).
- Publisher (Ingestion) and Store (Analytics) adapters that encapsulate data access patterns and shield services from ORM details.

Rationale for SQLite at this stage:

- Zero external dependencies; excellent for Windows and developer laptops.
- ACID transactions ensure durability and consistency.
- Simple operational footprint with predictable performance for single-node workloads.

## 5. Service Responsibilities

- Ingestion Service: Validates input payloads, serializes metadata to JSON, and writes ContentEventDB rows. Exposes read endpoints for recent events and counts to aid observability.
- Detection Service: Attaches labels and confidence scores to existing events, recording Detector type. Implemented to be stateless aside from writes to detection_results.
- Risk Analytics Service: Builds aggregated views (e.g., counts per label, average confidence) and returns recent analytics records for UI consumption.

By constraining each service to a single responsibility and routing all durable state changes through the persistence adapters, ASTRA preserves separation of concerns and facilitates testability.

## 6. Operations and Tooling

To keep operations straightforward on Windows, ASTRA provides:

- Database initialization: tools/scripts/init_db.py
- Service orchestration: tools/scripts/start-with-sqlite.ps1
- Health checks: tools/scripts/check-services.ps1

Scripts are ASCII-encoded to avoid Unicode parsing issues in Windows PowerShell 5.1. Paths are relative to the repository root, and the services use a single Python installation for consistency.

## 7. Security, Privacy, and Ethics

- Data locality: SQLite keeps data on the host, minimizing external exposure.  
- Least privilege: Services only access what they write; no cross-service direct coupling beyond shared storage.  
- PII handling: If content may contain personal data, apply minimization, redaction, and access controls.  
- Auditability: Explicit schemas with timestamps provide an immutable trail of key events.  

Practitioners should align deployment with organizational policies, including disk encryption and secure backups.

## 8. Limitations

- Concurrency: SQLite serializes writes; adequate for single-node or modest write rates, but not high-volume OLTP.  
- Scaling: No built-in replication or clustering; future transitions to PostgreSQL/MySQL may be warranted.  
- Observability: Lightweight by design; add structured logging and metrics exporters as workloads grow.  
- Migrations: Schema is stable but lacks versioned migrations; Alembic can be introduced later.

## 9. Future Work (Near Term)

- Storage evolution: Swap the SQLAlchemy engine to PostgreSQL when multi-writer throughput or remote access is required.  
- Schema migrations: Add Alembic for versioned, reversible changes.  
- Health and readiness: Standardize /health and /ready endpoints plus service-level metrics.  
- Robust testing: Expand unit and integration tests across service boundaries.  
- Packaging: Containerize services and scripts for reproducible deployment.  

Note: Federated and distributed designs are intentionally out of scope for this stage and will be addressed separately.

## 10. Reproducibility and Availability

- Source: [https://github.com/bhardwaj-kushagra/ASTRA](https://github.com/bhardwaj-kushagra/ASTRA)  
- Environment: Python 3.11, SQLite 3, SQLAlchemy 2.x  
- Essential artifacts: data/astra.db, data/schemas/database.py, services/*/ (microservices), tools/scripts/* (operations)  
- Typical flow: initialize database → start services → ingest content → run detection → query analytics.  

The repository includes simple scripts for initialization and service orchestration; they are suitable for local verification and demonstrations.

## 11. Conclusion

This first stage of ASTRA demonstrates that a practical, durable analytics pipeline can be realized with a small set of principled choices: explicit schemas, transactional persistence, and microservices with single responsibilities. SQLite provides enough reliability and performance for local and single-node scenarios while keeping operational complexity low. The abstractions—especially the publisher/store adapters and ORM models—position the system to scale up later without revisiting foundational contracts. As a proposed solution for applied research and early deployments, ASTRA balances rigor with approachability.

## References

1) SQLite Documentation, [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)  
2) SQLAlchemy 2.0 Documentation, [https://docs.sqlalchemy.org](https://docs.sqlalchemy.org)  
3) Newman, S., Building Microservices, O’Reilly Media, 2021.  
