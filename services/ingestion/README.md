# Ingestion Service

Lightweight connector framework to ingest content from files, APIs, or streaming sources and publish normalized events.

## Responsibilities (MVP)
- Pluggable connectors (file, HTTP, social API stubs).
- Schema validation and metadata enrichment.
- Event publishing to shared message queue or direct REST calls.

## Tech Stack
- Python 3.10+
- Pydantic for schema validation
- Redis Streams or in-memory queue for event bus
- Extensible connector interface

## Future Enhancements
- Rate limiting, retry policies, and backpressure management.
- Language detection, metadata extraction, and enrichment pipelines.
- Kafka/Kinesis integration for production-scale streaming.

## Next Steps
1. Implement base `Connector` abstract class.
2. Add file and HTTP connector implementations.
3. Wire event publisher to queue backend.
