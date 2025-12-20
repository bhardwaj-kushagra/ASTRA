# Ingestion Service

Lightweight connector framework to ingest content from files, APIs, or streaming sources and publish normalized events.

## Responsibilities (MVP)

- Pluggable connectors (file, HTTP, social API stubs).
- Schema validation and metadata enrichment.
- Persist normalized events to the shared SQLite database (via `SQLitePublisher`).
- Expose REST endpoints to trigger ingestion and list events.

## Tech Stack

- Python 3.10+
- Pydantic for schema validation
- SQLite (shared `data/astra.db`) via SQLAlchemy
- Extensible connector interface

## Future Enhancements

- Rate limiting, retry policies, and backpressure management.
- Language detection, metadata extraction, and enrichment pipelines.
- Message bus integration (Kafka/Redis Streams/Kinesis) for production-scale streaming (future work).

## Next Steps

1. Implement base `Connector` abstract class.
2. Add file and HTTP connector implementations.
3. (Future) Add a message-bus publisher backend.
