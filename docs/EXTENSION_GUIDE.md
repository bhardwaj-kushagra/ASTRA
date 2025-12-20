# ASTRA Prototype Extension Guide

This document explains how to extend the ASTRA prototype with new capabilities while maintaining modularity and scalability.

## Architecture Patterns

### 1. Plugin Architecture

All services use a **registry pattern** for extensibility:

- **Ingestion**: `ConnectorRegistry` for new data sources
- **Detection**: `DetectorRegistry` for new models
- **Analytics**: Future `VisualizationRegistry` for dashboard widgets

### 2. Service Communication

Current prototype uses **REST APIs** for synchronous communication:

```text
Ingestion (writes SQLite) → Analytics (pulls) → Detection (pull model)
```

For production scale, you can migrate to an **event-driven architecture** (future work; not implemented in this prototype):

```text
Ingestion → Message Queue → Detection → Analytics
          ↓
      Graph Intelligence
      Attribution
      Federation
```

### 3. Shared Schemas

All data models live in `data/schemas/models.py` using **Pydantic**:

- `ContentEvent` - normalized ingestion output
- `DetectionRequest` / `DetectionResult` - detection I/O
- `AnalyticsRecord` - aggregated results

Extend schemas carefully to maintain backward compatibility.

---

## Adding a New Connector

### Step 1: Create connector class

File: `services/ingestion/connectors/twitter_connector.py`

```python
from connector import Connector, ConnectorRegistry
from models import ContentEvent
import uuid

class TwitterConnector(Connector):
    @property
    def source_name(self) -> str:
        return "twitter"
    
    def fetch(self) -> Iterator[ContentEvent]:
        # Your implementation: API calls, rate limiting, etc.
        api_key = self.config.get("api_key")
        query = self.config.get("query")
        
        # Fetch tweets...
        for tweet in fetch_tweets(api_key, query):
            yield ContentEvent(
                id=str(uuid.uuid4()),
                source=self.source_name,
                content_type="text",
                text=tweet["text"],
                metadata={
                    "tweet_id": tweet["id"],
                    "author": tweet["author"],
                    "timestamp": tweet["created_at"]
                }
            )

# Register
ConnectorRegistry.register("twitter", TwitterConnector)
```

### Step 2: Import in main.py

```python
# services/ingestion/main.py
from connectors import file_connector, http_connector, twitter_connector
```

### Step 3: Use it

```bash
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"connector_type":"twitter","config":{"api_key":"XXX","query":"#AI"}}'
```

---

## Adding a New Detector

### Step 1: Create detector class

File: `services/detection/detectors/roberta_detector.py`

```python
from detector import Detector, DetectorRegistry
from models import DetectionRequest, DetectionResult
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class RoBERTaDetector(Detector):
    def __init__(self, config: dict):
        super().__init__(config)
        model_id = config.get("model_id", "roberta-base-openai-detector")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
    
    @property
    def model_name(self) -> str:
        return "roberta-detector"
    
    async def detect(self, request: DetectionRequest) -> DetectionResult:
        inputs = self.tokenizer(request.text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
        
        # Assuming binary: [human, AI-generated]
        ai_prob = probs[0][1].item()
        label = "AI-generated" if ai_prob > 0.5 else "human-written"
        
        return DetectionResult(
            label=label,
            confidence=max(ai_prob, 1 - ai_prob),
            detector_model=self.model_name
        )

DetectorRegistry.register("roberta", RoBERTaDetector)
```

### Notes: Local / Offline Models

Built-in detectors support local model folders for offline deployments:

- **Zero-shot** uses `ZERO_SHOT_MODEL_PATH` (or `config["model_path"]`) to load a Hugging Face model from disk.
- **RAG (embedding)** uses `RAG_MODEL_PATH` (or `config["model_path"]`) to load a Sentence Transformer model from disk.

You can follow the same pattern in custom detectors:

- Prefer `config.get("model_path") or os.getenv("YOUR_MODEL_PATH")`
- Use local-only loading flags where available (e.g., `local_files_only=True` for Hugging Face)

### Step 2: Import and configure

```python
# services/detection/main.py
from detectors import zero_shot_detector, roberta_detector

# Update get_detector() to use new model
default_detector = DetectorRegistry.get_detector("roberta", {
    "model_id": "roberta-base-openai-detector"
})
```

---

## Adding a New Service Module

Example: **Graph Intelligence Service**

### Step 1: Create service directory

```text
services/graph-intelligence/
├── main.py
├── requirements.txt
├── graph_builder.py
├── gnn_model.py
└── README.md
```

### Step 2: Define interface contracts

```python
# graph_builder.py
from models import ContentEvent, DetectionResult

class GraphBuilder:
    def add_content_node(self, event: ContentEvent):
        """Add content node to graph."""
        pass
    
    def add_detection_edge(self, event_id: str, result: DetectionResult):
        """Link detection result to content."""
        pass
    
    def detect_clusters(self) -> List[Cluster]:
        """Run GNN to find coordinated clusters."""
        pass
```

### Step 3: Expose REST API

```python
# main.py
from fastapi import FastAPI
app = FastAPI(title="ASTRA Graph Intelligence", version="0.1.0")

@app.post("/analyze-propagation")
async def analyze_propagation(events: List[ContentEvent]):
    # Build graph, run GNN, return insights
    pass
```

### Step 4: Wire into analytics

```python
# services/risk-analytics/main.py
GRAPH_SERVICE_URL = "http://localhost:8004"

@app.get("/graph-insights")
async def get_graph_insights():
    response = requests.get(f"{GRAPH_SERVICE_URL}/clusters")
    return response.json()
```

---

## Future: Migration to Message Queue (Not Implemented)

### Current (REST-based)

```text
Analytics calls Detection → Detection returns result
```

### Future (Event-driven)

```text
Ingestion → Kafka topic "content-events"
          ↓
      Detection subscribes
          ↓
      Publishes to "detection-results"
          ↓
      Analytics subscribes
```

### Implementation sketch

This section is a forward-looking sketch only. The current prototype uses shared SQLite + REST and does not include Kafka/Redis publishers or consumers.

High-level steps:

1. Add a publisher implementation (e.g., Kafka/Redis Streams) alongside `SQLitePublisher`.
2. Add consumers to Detection/Analytics to replace the current REST pull flow.
3. Preserve existing external APIs where possible (so the system can run in either mode).

Example pseudocode (not part of this repo today):

```python
class KafkaPublisher(EventPublisher):
    def __init__(self, topic: str):
        self.producer = KafkaProducer(...)
        self.topic = topic
    
    async def publish(self, event: ContentEvent):
        self.producer.send(self.topic, value=event.json())
```

Add consumers in each service (pseudocode):

```python
consumer = KafkaConsumer("content-events")
for message in consumer:
    event = ContentEvent(**json.loads(message.value))
    # Process event...
```

---

## Data Schema Evolution

### Adding a new field

```python
# data/schemas/models.py
class ContentEvent(BaseModel):
    id: str
    source: str
    text: str
    metadata: Dict[str, Any]
    timestamp: datetime
    language: Optional[str] = None  # NEW FIELD (optional for backward compat)
```

### Versioning schemas

For breaking changes, create versioned models:

```python
class ContentEventV2(BaseModel):
    # New schema
    pass

# Support both in APIs
@app.post("/ingest")
async def ingest(event: Union[ContentEvent, ContentEventV2]):
    # Handle both versions
    pass
```

---

## Deployment Patterns

### Containerization

```dockerfile
# services/detection/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Docker Compose (local dev)

```yaml
version: '3.8'
services:
  ingestion:
    build: ./services/ingestion
    ports: ["8001:8001"]
  
  detection:
    build: ./services/detection
    ports: ["8002:8002"]
  
  analytics:
    build: ./services/risk-analytics
    ports: ["8003:8003"]
    depends_on: [ingestion, detection]
```

### Kubernetes (production)

- Deploy each service as a `Deployment`
- Expose via `Service` objects
- Use `ConfigMap` for configuration
- Store secrets in `Secret` objects
- Add HPA (Horizontal Pod Autoscaler) for scaling

---

## Testing Strategy

### Unit Tests

```python
# services/detection/test_detector.py
import pytest
from detectors.zero_shot_detector import ZeroShotDetector

@pytest.mark.asyncio
async def test_zero_shot_detector():
    detector = ZeroShotDetector({"labels": ["AI", "human"]})
    result = await detector.detect(DetectionRequest(text="Test"))
    assert result.confidence > 0.0
```

### Integration Tests

See `tools/scripts/test_integration.py` for end-to-end examples.

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8002/detect
```

---

## Monitoring & Observability

### Add metrics

```python
from prometheus_client import Counter, Histogram

detection_requests = Counter('detection_requests_total', 'Total detections')
detection_latency = Histogram('detection_latency_seconds', 'Detection latency')

@app.post("/detect")
async def detect(request: DetectionRequest):
    detection_requests.inc()
    with detection_latency.time():
        return await detector.detect(request)
```

### Centralized logging

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
logger = logging.getLogger("detection-service")
logger.info(f"Processed event {event.id}")
```

---

## Security Hardening

1. **API Authentication**: Add JWT or API key middleware
2. **Rate Limiting**: Use `slowapi` or nginx rate limits
3. **Input Validation**: Pydantic already validates; add size limits
4. **Secrets Management**: Use environment variables + Vault
5. **Network Policies**: Restrict service-to-service communication in K8s

---

## Next Module Recommendations

1. **Attribution Service** (Phase 2)
   - Watermark verification API integration
   - Stylometric fingerprinting
   - Evidence chain storage

2. **Graph Intelligence** (Phase 2)
   - NetworkX or DGL for graph construction
   - GNN models (GraphSAGE, GAT) for cluster detection
   - SIEM integration for alerting

3. **Federation Gateway** (Phase 3)
   - STIX/TAXII endpoints
   - Differential privacy filters
   - Blockchain audit log

4. **Red-Team Harness** (Phase 4)
   - TextAttack integration
   - Adversarial sample generation
   - Continuous regression testing

Each module follows the same pattern: registry-based extensibility, shared schemas, REST or event-based communication.
