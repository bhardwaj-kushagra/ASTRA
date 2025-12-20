# Tooling & Automation Scripts

Place helper scripts, CLI utilities, and automation tooling used across ASTRA services.

## Suggestions

- Common data loaders and validation tools.
- Deployment aides (blue/green switchers, canary orchestrators).
- Developer productivity scripts (lint wrappers, local stack bootstrapping).

Document prerequisites and usage instructions within each script directory.

## Phase 3

- `start-astra-stack-uvicorn.ps1`: Start a full stack on a configurable port range and SQLite file (via `ASTRA_DB_PATH`).
- `threat-exchange-demo.ps1`: Export indicators from one Risk Analytics instance and import them into another.

## Phase 4

- `evaluate_adversarial_detectors.py`: Run the manual adversarial samples against `simple` and `zero-shot` detectors and write a JSON report.
