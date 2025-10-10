# Ingestion Service

Handles multi-source content acquisition, normalization, and enrichment for ASTRA.

## Responsibilities
- Connectors for social platforms, messaging apps, dark web, and partner feeds.
- Schema validation and enrichment (language detection, metadata extraction).
- Streaming into the event backbone (e.g., Kafka topics) and data lake staging.

## Next Steps
1. Define source onboarding checklist and data contracts.
2. Prototype connector SDK with rate limiting and retry policies.
3. Instrument metrics for volume, latency, and data quality.
