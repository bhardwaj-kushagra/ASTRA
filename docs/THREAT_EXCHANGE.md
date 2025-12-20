# Threat Exchange (Phase 3)

ASTRA Phase 3 adds a lightweight, REST-based JSON format for exchanging threat summaries between two running instances.

This is intentionally minimal:

- No Kafka / message queues
- No signatures / PKI (future work)
- SQLite-friendly export queries

## Endpoints (Risk Analytics)

- `GET /threat-exchange/export?limit=200`
  - Returns a JSON envelope containing summarized indicators derived from local analytics records.
- `POST /threat-exchange/import`
  - Accepts an exported envelope and stores the indicators into the shared SQLite table `threat_indicators`.
- `GET /threat-exchange/indicators?limit=200&producer_instance_id=...`
  - Lists imported indicators.

## JSON format

The envelope is versioned via `schema_version`.

```json
{
  "schema_version": "astra-threat-exchange-1.0",
  "producer": {
    "instance_id": "astra-instance-a",
    "service": "risk-analytics",
    "generated_at": "2025-12-21T12:00:00Z",
    "base_url": "http://127.0.0.1:8003"
  },
  "indicators": [
    {
      "actor_id": "file-system",
      "source_hash": "<sha256>",
      "detection_label": "suspicious",
      "max_confidence": 0.81,
      "event_count": 3,
      "first_seen": "2025-12-21T11:00:00Z",
      "last_seen": "2025-12-21T11:10:00Z"
    }
  ],
  "summary": {
    "indicator_count": 1,
    "events_by_label": {
      "suspicious": 3
    }
  }
}
```

## Demo (two instances)

Start two stacks on different ports, each using its own SQLite file (via `ASTRA_DB_PATH`). For example:

- Instance A: export from `http://127.0.0.1:8003`
- Instance B: import into `http://127.0.0.1:8103`

Then run:

```powershell
.\tools\scripts\threat-exchange-demo.ps1 -From http://127.0.0.1:8003 -To http://127.0.0.1:8103
```
