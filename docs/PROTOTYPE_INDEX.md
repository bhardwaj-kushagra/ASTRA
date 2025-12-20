# ASTRA Prototype Index

This page is the “source of truth” entrypoint for the current working prototype.

## What’s implemented

- **Phase 1 (Core pipeline)**: Ingestion → Detection → Risk Analytics dashboard (shared SQLite).
- **Phase 2 (Attribution + graph)**: `actor_id`, `source_hash`, and the co-occurrence graph view.
- **Phase 3 (Threat exchange)**: Versioned JSON export/import between two instances.
- **Phase 4 (Manual adversarial eval)**: Handcrafted samples + simple vs zero-shot comparison script.

## Key docs

- Quick start: `QUICKSTART.md`
- Demo flow: `DEMO_GUIDE.md`
- Deep-dive: `docs/DEVELOPER_GUIDE.md`
- MVP reference: `docs/MVP_REFERENCE.md`
- SQLite notes: `docs/SQLITE_MIGRATION.md`
- Threat exchange: `docs/THREAT_EXCHANGE.md`
- Adversarial samples: `data/samples/adversarial/README.md`

## Key endpoints

- Ingestion:
  - `POST /ingest`
  - `GET /events`
- Detection:
  - `POST /detect`
  - `GET /detector`
  - `POST /detector/{name}`
- Risk Analytics:
  - `GET /dashboard`
  - `POST /sync-from-ingestion`
  - `GET /graph/cooccurrence?max_edges=...&max_nodes=...`
  - `GET /threat-exchange/export`
  - `POST /threat-exchange/import`
  - `GET /threat-exchange/indicators`

## Key scripts

- Start single stack: `tools/scripts/start-all-services.ps1` or `tools/scripts/start-all-uvicorn.ps1`
- Start multiple stacks: `tools/scripts/start-astra-stack-uvicorn.ps1`
- Threat exchange demo: `tools/scripts/threat-exchange-demo.ps1`
- Adversarial comparison: `tools/scripts/evaluate_adversarial_detectors.py`
