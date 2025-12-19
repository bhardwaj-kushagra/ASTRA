# ASTRA API Demonstration Guide

This guide helps you demonstrate the ASTRA FastAPI endpoints to your mentor or any stakeholder.

## Prerequisites

Before starting the demo, ensure:

1. All services are running (Ingestion on 8001, Detection on 8002, Risk Analytics on 8003)
2. Database is initialized (`python tools\scripts\init_db.py`)
3. You have a tool to send HTTP requests (Postman, curl, or Python script)

## Starting the Services

### Option 1: Automated Start (Recommended)

```powershell
.\tools\scripts\start-all-services.ps1
```

### Option 2: Manual Start (3 terminals)

```powershell
# Terminal 1 - Ingestion
cd services\ingestion
python main.py

# Terminal 2 - Detection
cd services\detection
python main.py

# Terminal 3 - Risk Analytics
cd services\risk-analytics
python main.py
```

---

## Demonstration Flow

### Step 1: Health Checks - Verify All Services Are Running

**Show that all services are operational:**

```powershell
# Check Ingestion Service
curl http://localhost:8001

# Check Detection Service
curl http://localhost:8002

# Check Analytics Service
curl http://localhost:8003
```

**Expected Response (Ingestion):**

```json
{
  "service": "ingestion",
  "version": "0.1.0",
  "status": "running",
  "connectors": ["file", "http"]
}
```

**Expected Response (Detection):**

```json
{
  "service": "detection",
  "version": "0.1.0",
  "status": "running",
  "available_detectors": ["simple", "rag", "zero-shot"],
  "active_detector": "simple"
}
```

---

### Step 2: Demonstrate Content Ingestion

**Endpoint:** `POST http://localhost:8001/ingest`

#### Test 1: Ingest from Files

```powershell
curl -X POST http://localhost:8001/ingest `
  -H "Content-Type: application/json" `
  -d '{\"connector_type\":\"file\",\"config\":{\"path\":\"..\\..\\data\\samples\",\"pattern\":\"*.txt\"}}'
```

**What this does:**

- Reads all `.txt` files from `data/samples` directory
- Creates ContentEvent objects for each file
- Stores them in SQLite database
- Returns summary with event IDs

**Expected Response:**

```json
{
  "status": "success",
  "connector": "file",
  "events_ingested": 3,
  "event_ids": ["evt_123", "evt_456", "evt_789"]
}
```

#### Test 2: Ingest from HTTP Source

```powershell
curl -X POST http://localhost:8001/ingest `
  -H "Content-Type: application/json" `
  -d '{\"connector_type\":\"http\",\"config\":{\"urls\":[\"https://example.com/article1\"]}}'
```

**What this does:**

- Fetches content from specified URLs
- Creates ContentEvent for each response
- Stores in database

---

### Step 3: View Ingested Events

**Endpoint:** `GET http://localhost:8001/events`

```powershell
# Get all events (up to 100)
curl http://localhost:8001/events

# Get specific number of events
curl "http://localhost:8001/events?limit=5"
```

**Expected Response:**

```json
[
  {
    "id": "evt_123",
    "content": "Sample text content...",
    "source": "file://data/samples/test.txt",
    "timestamp": "2024-01-15T10:30:00Z",
    "metadata": {
      "connector": "file",
      "filename": "test.txt"
    }
  }
]
```

---

### Step 4: Demonstrate AI Detection

**Endpoint:** `POST http://localhost:8002/detect`

#### Test 1: Detect Human-Written Text

```powershell
curl -X POST http://localhost:8002/detect `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"Hey! How are you doing today? I just went to the park and saw some cute dogs playing. Weather is nice!\"}'
```

**Expected Response:**

```json
{
  "label": "human-written",
  "confidence": 0.85,
  "metadata": {
    "detector": "simple",
    "signals": {
      "text_length": 95,
      "avg_word_length": 4.2,
      "repetition_score": 0.1
    }
  }
}
```

#### Test 2: Detect AI-Generated Text

```powershell
curl -X POST http://localhost:8002/detect `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"The implementation of strategic frameworks necessitates comprehensive analysis. Furthermore, it is imperative to consider multifaceted dimensions. Consequently, stakeholders must collaborate synergistically.\"}'
```

**Expected Response:**

```json
{
  "label": "AI-generated",
  "confidence": 0.92,
  "metadata": {
    "detector": "simple",
    "signals": {
      "text_length": 185,
      "avg_word_length": 8.5,
      "repetition_score": 0.4
    }
  }
}
```

#### Test 3: List Available Detectors

```powershell
curl http://localhost:8002/models
```

**Expected Response:**

```json
{
  "detectors": ["simple", "rag", "zero-shot"],
  "active_detector": "simple",
  "default": "simple"
}
```

#### Test 4: Switch the Active Detector (Runtime)

You can switch detectors without restarting the service:

```powershell
# Switch to zero-shot
curl -X POST http://localhost:8002/detector/zero-shot

# Switch to RAG
curl -X POST http://localhost:8002/detector/rag

# Switch back to simple
curl -X POST http://localhost:8002/detector/simple
```

You can also query the current detector:

```powershell
curl http://localhost:8002/detector
```

---

### Step 5: End-to-End Analytics Workflow

**Endpoint:** `POST http://localhost:8003/analyze`

This endpoint combines ingestion + detection + storage in one call.

```powershell
curl -X POST http://localhost:8003/analyze `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"Artificial intelligence continues to revolutionize various industries through innovative applications and transformative solutions.\",\"source\":\"demo-input\",\"metadata\":{\"demo\":true}}'
```

**Expected Response:**

```json
{
  "record_id": "rec_001",
  "detection_result": {
    "label": "AI-generated",
    "confidence": 0.88
  },
  "content_preview": "Artificial intelligence continues...",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

---

### Step 5A (UI): Demonstrate Dashboard Direct Inputs

Open the dashboard:

- <http://localhost:8003/dashboard>

From the dashboard you can demonstrate:

- **Analyze Typed Text** (posts to `/dashboard/analyze-text`)
- **Analyze Uploaded File** (posts to `/dashboard/upload-file`)
- **Detector selector** (posts to `/dashboard/set-detector`, switching the detection service between `simple`, `rag`, `zero-shot`)

This is useful for demos because it requires no curl/Postman setup beyond starting the services.

### Step 6: Sync Events from Ingestion to Analytics

**Endpoint:** `POST http://localhost:8003/sync-from-ingestion`

```powershell
curl -X POST http://localhost:8003/sync-from-ingestion
```

**What this does:**

1. Fetches all events from Ingestion service (port 8001)
2. Sends each to Detection service (port 8002)
3. Stores results in Analytics database
4. Returns summary

**Expected Response:**

```json
{
  "status": "success",
  "events_fetched": 5,
  "events_processed": 5,
  "detection_summary": {
    "AI-generated": 2,
    "human-written": 2,
    "suspicious": 1
  }
}
```

---

### Step 7: View Detection Records

**Endpoint:** `GET http://localhost:8003/records`

```powershell
# Get all records
curl http://localhost:8003/records

# Get with filter
curl "http://localhost:8003/records?limit=10"
```

**Expected Response:**

```json
{
  "total": 15,
  "records": [
    {
      "id": "rec_001",
      "content_preview": "Artificial intelligence...",
      "detection_label": "AI-generated",
      "confidence": 0.88,
      "source": "demo-input",
      "timestamp": "2024-01-15T10:35:00Z"
    }
  ]
}
```

---

### Step 8: View Statistics Dashboard

**Endpoint:** `GET http://localhost:8003/stats`

```powershell
curl http://localhost:8003/stats
```

**Expected Response:**

```json
{
  "total_records": 15,
  "detection_distribution": {
    "AI-generated": 6,
    "human-written": 7,
    "suspicious": 2
  },
  "avg_confidence": 0.82,
  "high_confidence_detections": 12,
  "recent_activity": {
    "last_hour": 5,
    "last_24h": 15
  }
}
```

---

### Step 9: View Web Dashboard

**Endpoint:** `GET http://localhost:8003/dashboard`

**Open in browser:**

```text
http://localhost:8003/dashboard
```

This provides a visual HTML interface showing:

- Real-time statistics
- Detection history
- Confidence distribution charts
- Recent detections table

---

## Advanced Demo Scenarios

### Scenario 1: Batch Processing Pipeline

**Step-by-step workflow:**

```powershell
# 1. Ingest multiple files
curl -X POST http://localhost:8001/ingest `
  -H "Content-Type: application/json" `
  -d '{\"connector_type\":\"file\",\"config\":{\"path\":\"..\\..\\data\\samples\",\"pattern\":\"*.txt\"}}'

# 2. Sync to analytics (processes through detection)
curl -X POST http://localhost:8003/sync-from-ingestion

# 3. View results
curl http://localhost:8003/stats

# 4. View in dashboard
# Open browser: http://localhost:8003/dashboard
```

---

### Scenario 2: Real-Time Detection Demo

**Create a live demonstration script:**

```powershell
# Save as demo_realtime.ps1
$texts = @(
    "Hello! This is a casual message from a human.",
    "The optimization of synergistic paradigms necessitates holistic integration.",
    "I love pizza and ice cream!",
    "Implementing best practices requires comprehensive strategic frameworks."
)

foreach ($text in $texts) {
    Write-Host "`nAnalyzing: $text"
    curl -X POST http://localhost:8002/detect `
        -H "Content-Type: application/json" `
        -d "{`"text`":`"$text`"}"
    Start-Sleep -Seconds 2
}
```

---

## Alternative Tools for Testing

### Option 1: Using PowerShell (Built-in)

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8001" -Method Get

# POST request
$body = @{
    text = "Sample text to analyze"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/detect" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

---

### Option 2: Using Python Script

```python
# demo_api.py
import requests
import json

BASE_URLS = {
    "ingestion": "http://localhost:8001",
    "detection": "http://localhost:8002",
    "analytics": "http://localhost:8003"
}

# Test detection
def test_detection(text):
    response = requests.post(
        f"{BASE_URLS['detection']}/detect",
        json={"text": text}
    )
    return response.json()

# Test ingestion
def test_ingestion():
    response = requests.post(
        f"{BASE_URLS['ingestion']}/ingest",
        json={
            "connector_type": "file",
            "config": {
                "path": "../../data/samples",
                "pattern": "*.txt"
            }
        }
    )
    return response.json()

# Run demo
if __name__ == "__main__":
    print("Testing Detection Service:")
    result = test_detection("This is a test message.")
    print(json.dumps(result, indent=2))
    
    print("\nTesting Ingestion Service:")
    result = test_ingestion()
    print(json.dumps(result, indent=2))
```

**Run it:**

```powershell
python demo_api.py
```

---

### Option 3: Using Postman

1. **Import endpoints:**
   - Create new collection: "ASTRA API"
   - Add requests for each endpoint

2. **Example Detection Request:**
   - Method: POST
   - URL: `http://localhost:8002/detect`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):

     ```json
     {
       "text": "Sample text to analyze"
     }
     ```

3. **Save as collection** for easy replay

---

### Option 4: Interactive Swagger UI

FastAPI automatically generates interactive documentation:

```text
http://localhost:8001/docs  # Ingestion API docs
http://localhost:8002/docs  # Detection API docs
http://localhost:8003/docs  # Analytics API docs
```

**Features:**

- See all endpoints with descriptions
- Try endpoints directly in browser
- View request/response schemas
- No additional setup needed

---

## Demonstration Script for Mentor

### Quick 5-Minute Demo

```powershell
# 1. Show services are running
Write-Host "Step 1: Checking service health..."
curl http://localhost:8001
curl http://localhost:8002
curl http://localhost:8003

# 2. Demonstrate detection
Write-Host "`nStep 2: Detecting AI-generated content..."
curl -X POST http://localhost:8002/detect `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"The implementation of strategic frameworks necessitates comprehensive analysis.\"}'

# 3. Show ingestion
Write-Host "`nStep 3: Ingesting sample files..."
curl -X POST http://localhost:8001/ingest `
  -H "Content-Type: application/json" `
  -d '{\"connector_type\":\"file\",\"config\":{\"path\":\"..\\..\\data\\samples\",\"pattern\":\"*.txt\"}}'

# 4. Sync and analyze
Write-Host "`nStep 4: Processing through pipeline..."
curl -X POST http://localhost:8003/sync-from-ingestion

# 5. Show results
Write-Host "`nStep 5: Viewing statistics..."
curl http://localhost:8003/stats

Write-Host "`nStep 6: Open dashboard at http://localhost:8003/dashboard"
```

---

## Troubleshooting During Demo

### Issue: Service not responding

```powershell
# Check if service is running
netstat -ano | findstr "8001"
netstat -ano | findstr "8002"
netstat -ano | findstr "8003"
```

### Issue: Database not initialized

```powershell
python tools\scripts\init_db.py
```

### Issue: Import errors

```powershell
# Ensure you're in the right directory
cd "c:\A Developer's Stuff\ASTRA"

# Check virtual environment is activated
.\venv\Scripts\Activate.ps1
```

---

## Summary

This guide covered:

1. ✅ Starting all services
2. ✅ Health checks for verification
3. ✅ Content ingestion (file & HTTP)
4. ✅ AI detection with multiple test cases
5. ✅ End-to-end analytics workflow
6. ✅ Viewing results and statistics
7. ✅ Web dashboard demonstration
8. ✅ Multiple testing tools (curl, PowerShell, Python, Postman, Swagger)
9. ✅ Demo scripts for mentor presentation

**For your mentor verification, recommend using:**

- Swagger UI (`/docs` endpoints) for interactive testing
- PowerShell demo script for automated walkthrough
- Web dashboard for visual demonstration

Good luck with your demo! 🚀
