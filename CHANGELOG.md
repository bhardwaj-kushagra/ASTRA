# Changelog

All notable changes to ASTRA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial ASTRA prototype with three core microservices
- Ingestion service with file and HTTP connectors
- Detection service with pluggable detectors: `simple`, `rag`, `zero-shot`
- Risk analytics service with web dashboard
- Dashboard direct analysis inputs: typed text + file upload
- Dashboard detector selector (switches detection service between `simple`, `rag`, `zero-shot`)
- Detection runtime detector switching endpoints: `GET /detector`, `POST /detector/{name}`
- Offline/local model support via env vars: `ZERO_SHOT_MODEL_PATH`, `RAG_MODEL_PATH`
- Model download helpers: `tools/scripts/download_zero_shot_model.py`, `tools/scripts/download_rag_model.py`
- Registry-based plugin architecture for extensibility
- Comprehensive documentation suite
- Setup automation scripts for Windows PowerShell
- Integration test framework
- Sample data for testing

### Changed

- RAG detector implementation: now uses Sentence Transformers embeddings + kNN retrieval over a small labeled knowledge base
- Docs updated to reflect detector switching, offline model paths, and dashboard inputs

### Architecture

- Microservices pattern with REST APIs
- Shared Pydantic schemas for service contracts
- SQLite persistence (data/astra.db) for ingestion + analytics + detection results
- FastAPI framework for all services
- Jinja2 templates for dashboard UI

### Documentation

- `README.md` - Project overview and introduction
- `QUICKSTART.md` - Installation and usage guide
- `STATUS.md` - System status and health check guide
- `CONTRIBUTING.md` - Contribution guidelines
- `docs/EXTENSION_GUIDE.md` - Developer extension patterns
- `docs/architecture/` - Architecture documentation
- `docs/governance/` - Policies and compliance docs
- `.env.example` - Environment configuration template

### Services

#### Ingestion Service (v0.1.0)

- File system connector for local file ingestion
- HTTP connector for API-based content streams
- Event publishing to SQLite (persistent storage)
- RESTful API endpoints

#### Detection Service (v0.1.0)

- Detectors: `simple`, `rag`, `zero-shot`
- Runtime switching: `GET /detector`, `POST /detector/{name}`
- Optional offline/local models via `ZERO_SHOT_MODEL_PATH` and `RAG_MODEL_PATH`

#### Risk Analytics Service (v0.1.0)

- Web dashboard with real-time statistics
- Event aggregation and storage
- Detection breakdown visualization
- Recent events table with confidence scores
- Sync endpoint for batch processing from ingestion
- Direct analysis: typed text + file upload
- Detector selector to switch models from the UI

### Known Limitations

- No authentication/authorization
- Single-node deployment only
- Limited to text content analysis

## [0.1.0] - 2025-10-12

### Initial Release

- Basic prototype with core functionality
- Three operational microservices
- Plugin-based architecture foundation
- Documentation and setup automation

---

## Versioning Notes

**Version Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to APIs or architecture
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes and minor improvements

**Upcoming Milestones**:

- v0.2.0: Operational hardening (better error handling, config, docs)
- v0.3.0: Advanced detection models
- v0.4.0: Graph intelligence service
- v0.5.0: Attribution service
- v1.0.0: Production-ready release
