# Changelog

All notable changes to ASTRA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial ASTRA prototype with three core microservices
- Ingestion service with file and HTTP connectors
- Detection service with zero-shot transformer classifier (BART-based)
- Risk analytics service with web dashboard
- Registry-based plugin architecture for extensibility
- Comprehensive documentation suite
- Setup automation scripts for Windows PowerShell
- Integration test framework
- Sample data for testing

### Architecture
- Microservices pattern with REST APIs
- Shared Pydantic schemas for service contracts
- In-memory data storage (temporary, for prototype)
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
- Event publishing to in-memory store
- RESTful API endpoints

#### Detection Service (v0.1.0)
- Zero-shot classification using BART-large-MNLI
- Binary classification: AI-generated vs human-written
- Confidence scoring
- Lazy model loading for performance

#### Risk Analytics Service (v0.1.0)
- Web dashboard with real-time statistics
- Event aggregation and storage
- Detection breakdown visualization
- Recent events table with confidence scores
- Sync endpoint for batch processing from ingestion

### Known Limitations
- In-memory storage only (data lost on restart)
- No authentication/authorization
- No persistence layer
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
- v0.2.0: Database persistence layer
- v0.3.0: Advanced detection models
- v0.4.0: Graph intelligence service
- v0.5.0: Attribution service
- v1.0.0: Production-ready release
