# ASTRA – Adaptive Surveillance Tracking and Recognition Architecture

**Status: ✅ PROTOTYPE OPERATIONAL** | [Quick Start](QUICKSTART.md) | [Demo Guide](DEMO_GUIDE.md) | [Developer Guide](docs/DEVELOPER_GUIDE.md)

ASTRA is a multi-layered defense platform that detects, attributes, and mitigates hostile information operations powered by large language models (LLMs). The system combines AI-driven analytics, graph intelligence, forensic tooling, and policy enforcement to protect national security partners from malicious narrative campaigns.

## Vision

- Deliver **high-precision AI-generated content detection** with sub-second response times.
- Provide **forensic attribution** and cross-border intelligence sharing without compromising privacy.
- Empower analysts with **real-time risk scoring, dashboards, and simulation tooling** for proactive defense.
- Institutionalize **Responsible AI and governance** guardrails through automation, transparency, and red-teaming.

## Core Capability Pillars

1. **Real-Time Detection** – Transformer ensembles, stylometry, and entropy-based detectors for text and multimedia.
2. **Attribution & Forensics** – Watermark verification, fingerprinting, evidence chain management.
3. **Graph Intelligence** – GNN-powered propagation analysis, coordination detection, and influence mapping.
4. **Federated Intelligence Exchange** – Secure, policy-aware data sharing across allied networks.
5. **Risk Analytics & Visualization** – Dashboards, trend analytics, predictive modeling, and reporting.
6. **Vendor Collaboration & Red-Teaming** – Continuous adversarial testing, guardrail validation, and disclosure workflows.
7. **Privacy & Compliance** – Differential privacy, federated learning, explainability, and transparency reporting.

## Prototype (What Exists Today)

This repo currently implements a working, local prototype (Windows-first) using shared SQLite + REST orchestration:

- Ingestion persists `content_events` with `actor_id`, `source_hash`, and `processing_status`.
- Risk Analytics pulls only `NEW` events via `POST /sync-from-ingestion`, runs detection concurrently, and updates `processing_status` to `DETECTED`/`FAILED`.
- A lightweight co-occurrence graph is available at `GET /graph/cooccurrence` and is embedded in the dashboard.
- Phase 3 threat exchange is implemented as REST-based JSON import/export.
- Phase 4 evaluation is implemented via a manual adversarial sample set plus a comparison script.

Key docs:

- `docs/MVP_REFERENCE.md`
- `docs/THREAT_EXCHANGE.md`
- `data/samples/adversarial/README.md`

## Repository Structure

```text
docs/                     Project knowledge base (architecture, governance, operations, roadmap)
services/                 Domain services (ingestion, detection, attribution, graph, federation, analytics, red-team)
platform/                 Infrastructure-as-code and MLOps platform assets
data/                     Schemas, synthetic datasets, and data documentation
tools/                    Shared tooling, automation scripts, and developer utilities
```

See `docs/README.md` and the service-specific READMEs for deeper detail.

## Architecture at a Glance

- **Data Foundation**: Streaming ingestion → feature store → curated lakehouse.
- **Analytic Engines**: Detection ensembles, graph neural networks, attribution pipelines.
- **Exchange Fabric**: Federated gateway enforcing privacy, policy, and audit trails.
- **Analyst Experience**: Risk dashboards, alert triage, scenario simulation.
- **Governance Overlay**: Responsible AI, compliance automation, and red-team feedback loops.

Diagrams and contract details live in `docs/architecture/`.

## Delivery Roadmap

High-level milestones are tracked in `docs/roadmap.md`. Each phase concludes with:

- Demo and stakeholder review
- Security & privacy assessment
- Updated documentation and runbooks

## Getting Started (WIP)

### Quick Setup

1. **Prerequisites**: Python 3.10+, 8GB+ RAM
2. **Automated setup** (from ASTRA root):

   ```powershell
   .\setup.ps1
   ```

3. **Start all services** (choose one):

   ```powershell
   .\tools\scripts\start-all-uvicorn.ps1   # separate windows with logs (IPv4)
   # or
   .\tools\scripts\start-with-sqlite.ps1   # python main.py per service
   ```

4. **Test the system**:

   - Ingestion: `http://127.0.0.1:8001`
   - Detection: `http://127.0.0.1:8002`
   - Dashboard: `http://127.0.0.1:8003/dashboard`

### Phase 3 / Phase 4 scripts

- Threat exchange demo (two instances): `tools/scripts/threat-exchange-demo.ps1`
- Start an additional stack on different ports + DB: `tools/scripts/start-astra-stack-uvicorn.ps1`
- Adversarial comparison (simple vs zero-shot): `tools/scripts/evaluate_adversarial_detectors.py`

### Detection Models (Prototype)

The Detection service exposes three built-in detector modes (selectable at runtime):

- **simple**: lightweight heuristic baseline (no model downloads)
- **rag**: retrieval-style detector using local sentence-transformer embeddings + kNN over a small labeled knowledge base
- **zero-shot**: Hugging Face Transformers zero-shot classifier (default model id: `facebook/bart-large-mnli`)

Switch detectors in either of these ways:

- **From the dashboard**: use the detector dropdown at `http://127.0.0.1:8003/dashboard`
- **Via API**: `POST http://127.0.0.1:8002/detector/{name}` where `{name}` is `simple`, `rag`, or `zero-shot`
- **Via env var**: set `DETECTOR_NAME` before starting the detection service

### Offline / Local Model Setup

For air-gapped or offline runs, you can pre-download models into `astra-models/` (ignored by git) and point the services at the local folders:

- Zero-shot: run `python tools/scripts/download_zero_shot_model.py` and set `ZERO_SHOT_MODEL_PATH`
- RAG: run `python tools/scripts/download_rag_model.py` and set `RAG_MODEL_PATH`

See `QUICKSTART.md` for the exact PowerShell commands.

See `QUICKSTART.md` for detailed setup, testing, and troubleshooting instructions.

## Collaboration & Governance

- Track work via issues with labels per module (`ingestion`, `detection`, etc.).
- Propose significant changes through Architecture Decision Records (ADRs) in `docs/architecture/adr/`.
- Maintain Responsible AI, privacy, and federation policies within `docs/governance/`.
- Document operational runbooks and incident response updates in `docs/operations/`.

## Contributing

1. Fork or branch from `main` using trunk-based development conventions.
2. Ensure lint, tests, and security scans pass before opening a pull request.
3. Request reviews from the relevant module lead and governance rep.
4. Capture learnings in ADRs, runbooks, or roadmap updates as appropriate.

## License

TBD – select a license once partner requirements are finalized.
