# ASTRA Documentation Portal

Welcome to the knowledge base for ASTRA (Adaptive Surveillance Tracking and Recognition Architecture).

## Sections

- **Architecture** – system design artifacts, ADRs, and component diagrams.
- **Operations** – SOC runbooks, incident response, red-team exercises.
- **Governance** – privacy, compliance, responsible AI, and federation agreements.
- **Roadmap** – release planning, milestones, and delivery cadences.

## Prototype Notes (Current Behavior)

- Detection service supports three detectors (`simple`, `rag`, `zero-shot`) and can be switched at runtime.
- Offline/air-gapped runs are supported by pre-downloading models and setting `ZERO_SHOT_MODEL_PATH` / `RAG_MODEL_PATH`.
- The analytics dashboard supports direct text analysis, file upload analysis, and detector selection.

## Most Used Docs

- `docs/MVP_REFERENCE.md` — what the prototype implements today
- `docs/SQLITE_MIGRATION.md` — SQLite schema and persistence notes
- `docs/THREAT_EXCHANGE.md` — Phase 3 JSON format + two-instance demo
- `data/samples/adversarial/README.md` — Phase 4 manual sample set + evaluation entrypoint

## Most Used Scripts

- `tools/scripts/start-all-services.ps1` / `tools/scripts/start-all-uvicorn.ps1`
- `tools/scripts/start-astra-stack-uvicorn.ps1` (multi-instance)
- `tools/scripts/threat-exchange-demo.ps1`
- `tools/scripts/evaluate_adversarial_detectors.py`

See `QUICKSTART.md` for run commands and demo steps.

Use this directory to coordinate cross-functional collaboration between AI engineering, cyber intelligence, operations, and policy teams.
