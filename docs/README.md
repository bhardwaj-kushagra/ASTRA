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

See `QUICKSTART.md` for run commands and demo steps.

Use this directory to coordinate cross-functional collaboration between AI engineering, cyber intelligence, operations, and policy teams.
