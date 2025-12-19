# ASTRA Glossary and Key Concepts

This glossary collects precise, practitioner‑oriented definitions for terms and technologies referenced in ASTRA. Each entry includes: what it is, why it matters, operational notes, and common pitfalls.

## Microservice

- What: An independently deployable service focused on a small, well‑defined capability, communicating over lightweight interfaces (HTTP/gRPC).
- Why: Decouples concerns (ingestion, detection, analytics), enabling independent development, scaling, and fault isolation.
- Ops notes: Define clear contracts (schemas, status codes), health endpoints, idempotent operations, and observability (logs/metrics).
- Pitfalls: Chatty network calls, cascading failures, inconsistent schemas, version drift.

## FastAPI

- What: A modern Python web framework for building high‑performance HTTP APIs using type hints and Pydantic models.
- Why: Simple to build typed endpoints (request/response), automatic OpenAPI docs, async support.
- Ops notes: Use uvicorn/gunicorn for production; prefer explicit timeouts and validation.
- Pitfalls: Blocking I/O inside async handlers; mismatched Pydantic versions.

## Uvicorn

- What: An ASGI server used to run FastAPI apps.
- Why: Lightweight and fast; supports async concurrency.
- Ops notes: Bind to explicit IPv4 (`127.0.0.1`) to avoid localhost/IPv6 resolution issues; set graceful timeouts.
- Pitfalls: Running CPU‑heavy work on event loop; missing reload flags in dev.

## SQLite

- What: Embedded, file‑based relational database providing ACID transactions without a server.
- Why: Zero external dependencies; ideal for local/single‑node prototypes requiring durability.
- Ops notes: Prefer WAL mode for read concurrency: `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`. Keep one writer; many readers are fine.
- Pitfalls: Write contention under high concurrency; large transactions blocking readers; file locking across network filesystems.

## SQLAlchemy (ORM)

- What: Python ORM/SQL toolkit mapping Python classes → SQL tables with session‑managed transactions.
- Why: Clean schema definitions and transactional operations; portable across DB engines.
- Ops notes: Use scoped sessions per request; explicit commits; avoid long‑lived sessions.
- Pitfalls: Lazy loading causing N+1 queries; incorrect session scoping across threads.

## Pydantic

- What: Data validation/serialization library using Python type hints.
- Why: Guarantees API contracts (types, ranges), auto‑docs integration.
- Ops notes: Pydantic v2 uses `BaseModel.model_config`; avoid names colliding with protected namespaces (e.g., `model_name` vs `model_…`).
- Pitfalls: Mixing v1/v2 APIs; alias handling and `protected_namespaces` warnings.

## Health Endpoint

- What: An HTTP endpoint (e.g., `/`) reporting service status/version.
- Why: Enables health checks, readiness/liveness probes, simple debugging.
- Ops notes: Keep fast, side‑effect free; include version and key configuration flags.

## Ingestion Service

- What: Receives raw events (text, metadata), validates, and persists to storage (`content_events`).
- Why: Normalizes input and provides durable entry to the pipeline.
- Ops notes: Enforce idempotency (dedupe by event id), validate schemas, return 201/200 with IDs.

## Detection Service

- What: Classifies content (e.g., AI‑generated vs human) and returns label + confidence.
- Why: Core analytic decision component; can host multiple detectors behind a registry.
- Ops notes: Use lazy initialization; guard heavy model imports; timeouts for external calls.

## Analytics Service

- What: Aggregates detections into dashboards, statistics, and records.
- Why: Presents insights and enables human‑in-the-loop review.
- Ops notes: Keep read paths fast; paginate; compute aggregates lazily or cached.

## Detector Registry

- What: A factory/registry mapping detector names to classes and configurations.
- Why: Hot‑swap different detectors (heuristic, zero‑shot, RAG) without changing endpoint contracts.
- Ops notes: Validate names; return friendly errors for unknown detectors.

## Heuristic (Simple) Detector

- What: Lightweight rule‑based classifier using string features (length, keywords).
- Why: Fast, dependency‑free for demos; stable latency.
- Ops notes: Document rules and confidence mapping; use as baseline.
- Pitfalls: Lower accuracy; domain drift.

## Zero‑Shot Detector

- What: A classifier (e.g., `facebook/bart-large-mnli`) that assigns labels without task‑specific training by mapping labels to natural language hypotheses.
- Why: Flexible; decent accuracy across domains using transformers.
- Ops notes: Heavy dependencies (`transformers`, `torch`). Models download on first run unless you pre-download and point the service at a local folder (e.g., `ZERO_SHOT_MODEL_PATH`) for fully offline inference.
- Pitfalls: Cold‑start latency, NumPy/torch wheel mismatches, large memory footprint.

## RAG (Retrieval‑Augmented Generation)

- What: Pipeline that retrieves relevant documents and augments generation/classification using the retrieved context.
- Why: Improves grounding and explainability; supports evidence‑based decisions.
- Prototype note: In this repo, the "RAG" detector is implemented as embedding retrieval using Sentence Transformers + kNN over a small labeled knowledge base (no LLM generation step).
- Ops notes: Needs retriever (BM25/FAISS/vector DB), chunking, prompt/design; measure retrieval quality (precision/recall) and answer faithfulness. For offline runs, pre-download the embedding model and set `RAG_MODEL_PATH`.
- Pitfalls: Poor chunking/retrieval harms final answers; evaluation must separate retrieval vs generation errors.

## RAGAS (RAG Assessment)

- What: An evaluation framework for RAG systems providing metrics like faithfulness, answer relevancy, context precision/recall.
- Why: Standardizes evaluation beyond simple accuracy.
- Ops notes: Requires ground truth questions, answers, and contexts; integrate tracing of retrieved docs.
- Pitfalls: Misaligned ground truth; mixing retrieval vs generation errors in reporting.

## WAL (Write‑Ahead Logging)

- What: SQLite journal mode allowing concurrent readers with a single writer by appending changes to a log.
- Why: Improves read concurrency and tail latency for read‑heavy workloads.
- Ops notes: `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;` and periodic checkpoints.
- Pitfalls: Very large WAL files if checkpoints disabled; network filesystems.

## ACID

- What: Atomicity, Consistency, Isolation, Durability — database guarantees for transactions.
- Why: Ensures reliable state even under crashes; critical for pipelines needing persistence.
- Ops notes: Keep transactions small; handle errors; verify integrity after failures.

## Idempotency

- What: Operation yielding the same result when retried (e.g., inserting with the same event id doesn’t duplicate).
- Why: Required when retries happen (network hiccups, restarts).
- Ops notes: Use unique keys, upserts, or conditional writes.

## Latency p50/p95/p99

- What: Percentile latency (median, tail) across requests.
- Why: Tail latency drives user experience and stability; report p95/p99 alongside averages.
- Ops notes: Measure per stage (ingest, detect, end‑to‑end); include cold vs warm starts.

## Cold Start

- What: First request that initializes heavy resources (e.g., model load).
- Why: Impacts real‑time systems; must be measured separately.
- Ops notes: Warm‑up calls; model caching; background initialization.

## Dashboard (Jinja2)

- What: Server‑rendered HTML using Jinja2 templates for ASTRA’s analytics UI.
- Why: Minimal footprint; easy to extend; no frontend build step.
- Ops notes: Move inline CSS to static files; attach JS carefully (non‑blocking).

## IPv4 vs localhost

- What: `localhost` can resolve to IPv6 on some systems; using `127.0.0.1` avoids connection issues for tools that don’t support IPv6.
- Ops notes: Prefer explicit IPv4 for local testing and health scripts.

## PowerShell Quoting (Apostrophes)

- What: Single quotes terminate at an apostrophe in the path (e.g., `Developer's`).
- Why: Causes parser errors in commands like `Set-Location`.
- Ops notes: Use `-WorkingDirectory` or double quotes, or escape the apostrophe by doubling it.

## Smoke Test

- What: A quick end‑to‑end script validating basic health and key endpoints.
- Why: Confirms services are reachable and that minimal workflows succeed.
- Ops notes: Prefer IPv4, explicit timeouts, clear PASS/FAIL output.

## Protected Namespace (Pydantic)

- What: Pydantic reserves `model_` namespace; fields like `model_name` may warn.
- Fix: Use `model_config = {"protected_namespaces": ()}` or alias to a different field name.

## Optional Heavy Stack

- What: `transformers`, `torch`, `sentencepiece` used by zero‑shot detector.
- Ops notes: Pin compatible versions; consider `numpy<2` to avoid compiled extension mismatches; cache models.

## Evaluation (Benchmarks)

- What: Repeatable measurements for throughput, p50/p95 latencies, and durability.
- Ops notes: Report conditions (CPU/RAM/OS, batch sizes, warm vs cold), seeds/dataset versions, and PRAGMAs.

---

If you want this glossary extended with your team’s internal terms or abbreviations, share the list and I’ll append canonical definitions here.
