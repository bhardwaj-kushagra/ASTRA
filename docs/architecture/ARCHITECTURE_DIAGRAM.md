# ASTRA Prototype Architecture Diagram

## High-Level System View

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ASTRA Platform                                │
│        Adaptive Surveillance Tracking & Recognition Architecture     │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  ANALYST EXPERIENCE LAYER                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Risk Analytics Dashboard (port 8003)                           │   │
│  │  - Real-time detection feed                                     │   │
│  │  - Statistical aggregations                                     │   │
│  │  - Confidence scoring visualizations                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ REST API
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  DETECTION & ANALYSIS LAYER                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Detection Service (port 8002)                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Detector Registry (Extensible)                           │  │   │
│  │  │  - Zero-Shot Classifier (MVP)                            │  │   │
│  │  │  - [Future: RoBERTa fine-tuned]                          │  │   │
│  │  │  - [Future: Stylometric analyzer]                        │  │   │
│  │  │  - [Future: Ensemble orchestrator]                       │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ REST API
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA INGESTION LAYER                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Ingestion Service (port 8001)                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Connector Registry (Extensible)                          │  │   │
│  │  │  - File Connector (MVP)                                  │  │   │
│  │  │  - HTTP Connector (MVP)                                  │  │   │
│  │  │  - [Future: Social media APIs]                           │  │   │
│  │  │  - [Future: Dark web scrapers]                           │  │   │
│  │  │  - [Future: Partner threat feeds]                        │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Event Publisher                                          │  │   │
│  │  │  - InMemoryPublisher (MVP)                               │  │   │
│  │  │  - [Future: Kafka/Redis Streams]                         │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                   ┌────┴─────┐          ┌─────┴──────┐
                   │  Files   │          │  HTTP URLs │
                   │  (*.txt) │          │  (APIs)    │
                   └──────────┘          └────────────┘


═══════════════════════════════════════════════════════════════════════════
                    FUTURE EXPANSION MODULES (Phase 2+)
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│  GRAPH INTELLIGENCE SERVICE (port 8004)                                 │
│  - Propagation analysis using GNNs                                      │
│  - Coordination cluster detection                                       │
│  - Influence mapping                                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  ATTRIBUTION & FORENSICS SERVICE (port 8005)                            │
│  - Watermark verification                                               │
│  - Stylometric fingerprinting                                           │
│  - Evidence chain management                                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FEDERATION GATEWAY (port 8006)                                         │
│  - Secure cross-border intelligence exchange                            │
│  - STIX/TAXII protocols                                                 │
│  - Differential privacy enforcement                                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  RED-TEAM & ADVERSARIAL SERVICE (port 8007)                             │
│  - Continuous adversarial testing                                       │
│  - Vulnerability disclosure workflows                                   │
│  - Guardrail validation                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow - MVP Prototype

```
1. Content Ingestion
   ┌─────────┐
   │ Sample  │
   │ Files   │
   └────┬────┘
        │
        ▼
   POST /ingest
        │
        ▼
   ┌──────────────────┐
   │ File Connector   │ ──→ ContentEvent(id, source, text, metadata)
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │ InMemoryPublisher│ ──→ Store events in memory
   └──────────────────┘


2. Detection Analysis
   ┌──────────────────┐
   │ Analytics Service│
   └────────┬─────────┘
            │
            │ GET /events (fetch from ingestion)
            ▼
   ┌──────────────────┐
   │ Ingestion Service│ ──→ Returns List[ContentEvent]
   └──────────────────┘
            │
            │ For each event
            ▼
   POST /detect {text: "..."}
            │
            ▼
   ┌──────────────────────┐
   │ Detection Service    │
   │ - Zero-shot model    │ ──→ DetectionResult(label, confidence)
   └──────────────────────┘
            │
            ▼
   ┌──────────────────────┐
   │ Analytics Store      │ ──→ Save AnalyticsRecord
   └──────────────────────┘


3. Visualization
   Browser ──→ GET /dashboard ──→ Analytics Service
                                        │
                                        ▼
                                   Render HTML with:
                                   - Total events
                                   - Detection breakdown
                                   - Recent records table
                                   - Confidence scores
```

## Extension Points

### Adding New Connectors
```python
# services/ingestion/connectors/my_connector.py
class MyConnector(Connector):
    def fetch(self) -> Iterator[ContentEvent]:
        # Your logic here
        pass

ConnectorRegistry.register("my-connector", MyConnector)
```

### Adding New Detectors
```python
# services/detection/detectors/my_detector.py
class MyDetector(Detector):
    async def detect(self, request) -> DetectionResult:
        # Your logic here
        pass

DetectorRegistry.register("my-detector", MyDetector)
```

### Future Event-Driven Architecture
```
Ingestion ──→ Kafka Topic "content-events"
                    │
                    ├──→ Detection Service (subscriber)
                    │         │
                    │         ▼
                    │    Kafka Topic "detection-results"
                    │         │
                    │         ├──→ Analytics (subscriber)
                    │         │
                    ├──→ Graph Intelligence (subscriber)
                    │
                    └──→ Attribution (subscriber)
```

## Technology Stack

**Current (MVP):**
- Python 3.10+
- FastAPI (REST APIs)
- Pydantic (data validation)
- Hugging Face Transformers (models)
- Jinja2 (templates)
- In-memory storage

**Future (Production):**
- Kafka/Redis Streams (messaging)
- PostgreSQL (persistence)
- NetworkX/DGL (graph analytics)
- PyTorch Geometric (GNNs)
- Prometheus/Grafana (monitoring)
- Kubernetes (orchestration)
- Terraform (IaC)

## Security Considerations

**Implemented:**
- Input validation via Pydantic
- Type safety
- Error handling

**Future:**
- API authentication (JWT)
- Rate limiting
- Secrets management (Vault)
- Network policies
- Audit logging
- End-to-end encryption
