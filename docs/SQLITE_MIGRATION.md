# SQLite Migration Guide

## What Changed

ASTRA has been migrated from in-memory storage to persistent SQLite database storage.

### Before (In-Memory)

- Data lost on service restart
- `InMemoryPublisher` in ingestion service
- `AnalyticsStore` in analytics service
- No data persistence

### After (SQLite)

- **Persistent storage** - data survives restarts
- `SQLitePublisher` in ingestion service
- `SQLiteAnalyticsStore` in analytics service
- Single `astra.db` file in `data/` directory

---

## Database Schema

### Tables

#### `content_events`

Stores ingested content from all sources.

| Column | Type | Description |
| --- | --- | --- |
| id | String(36) | Primary key (UUID) |
| source | String(100) | Source identifier (e.g., "file", "twitter") |
| actor_id | String(100) | Convention-based actor identifier (not normalized) |
| source_hash | String(128) | Stable hash of source+content for grouping/dedup |
| text | Text | Full content text |
| metadata_json | Text | JSON metadata (flexible schema) |
| processing_status | String(20) | Workflow status: NEW → DETECTED or FAILED |
| timestamp | DateTime | When content was ingested |

**Indexes:** source, actor_id, source_hash, processing_status, timestamp

**Notes:**

- `processing_status` enables robust async processing: Risk Analytics processes only `NEW` events, then updates status to `DETECTED` or `FAILED`.
- For the prototype, services share a single SQLite file and Risk Analytics updates `processing_status` via direct DB writes.

---

#### `detection_results`

Stores AI detection results (currently unused, reserved for future).

| Column | Type | Description |
| --- | --- | --- |
| id | Integer | Auto-increment primary key |
| event_id | String(36) | Reference to content_events.id |
| label | String(50) | Detection label ("AI-generated", "human-written") |
| confidence | Float | Confidence score (0.0-1.0) |
| detector_type | String(50) | Detector used ("zero-shot", etc.) |
| timestamp | DateTime | When detection occurred |

**Indexes:** event_id, label, timestamp

---

#### `analytics_records`

Stores analytics data for dashboard visualization.

| Column | Type | Description |
| --- | --- | --- |
| id | Integer | Auto-increment primary key |
| event_id | String(36) | Reference to content_events.id |
| source | String(100) | Content source |
| text_preview | String(500) | First 500 chars of text |
| detection_label | String(50) | AI detection result |
| confidence | Float | Detection confidence |
| timestamp | DateTime | Record creation time |

**Indexes:** event_id, source, detection_label, timestamp

---

## Usage

### Initialize Database

```powershell
# First time setup
python tools/scripts/init_db.py

# Reset database (WARNING: deletes all data)
python tools/scripts/init_db.py --reset

# Custom database location
python tools/scripts/init_db.py --db-path /path/to/custom.db
```

### Start Services

```powershell
# Services now use SQLite automatically
.\tools\scripts\start-all-services.ps1
```

### Database Location

Default: `C:\A Developer's Stuff\ASTRA\data\astra.db`

---

## Code Changes

### Ingestion Service

**Before:**

```python
from publisher import InMemoryPublisher
publisher = InMemoryPublisher()
```

**After:**

```python
from sqlite_publisher import SQLitePublisher
publisher = SQLitePublisher()
```

**New Methods:**

- `publish_batch(events)` - Batch insert for efficiency
- `get_event_by_id(event_id)` - Retrieve specific event
- `count_events()` - Get total event count

---

### Analytics Service

**Before:**

```python
from store import AnalyticsStore
analytics_store = AnalyticsStore()
```

**After:**

```python
from sqlite_store import SQLiteAnalyticsStore
analytics_store = SQLiteAnalyticsStore()
```

**Same API:**

- `add_record(record)` - Store analytics record
- `get_recent(limit)` - Get recent records
- `get_stats()` - Get aggregate statistics
- `clear_all()` - Clear all records (testing)

---

## Benefits

### ✅ Persistence

- Data survives service restarts
- No data loss
- Historical data available

### ✅ Performance

- Indexed queries for fast retrieval
- Efficient batch inserts
- Scales to millions of records

### ✅ Reliability

- ACID transactions
- Concurrent access support
- SQLite's proven stability

### ✅ Flexibility

- Easy to migrate to PostgreSQL later
- Same SQLAlchemy ORM models work
- Can add columns without breaking existing code

---

## Migration Path

### From Development (In-Memory)

No migration needed - database starts empty.

### To Production (PostgreSQL)

Simple change in `database.py`:

```python
# Change from
engine = create_engine('sqlite:///data/astra.db')

# To
engine = create_engine('postgresql://user:pass@host/astra')
```

All SQLAlchemy models remain the same!

---

## Troubleshooting

### Database locked error

**Cause:** Multiple processes accessing SQLite simultaneously.

**Solution:** SQLite is configured with `check_same_thread=False` for FastAPI. If issues persist, migrate to PostgreSQL for production.

### Missing tables error

**Cause:** Database not initialized.

**Solution:**

```powershell
python tools/scripts/init_db.py
```

### Old in-memory data

**Cause:** Services restarted with SQLite, old data was in memory.

**Solution:** Re-ingest content to populate database.

---

## Database Management

### View Database

Use any SQLite browser:

- [DB Browser for SQLite](https://sqlitebrowser.org/)
- VS Code extension: "SQLite"
- Command line: `sqlite3 data/astra.db`

### Query Examples

```sql
-- Count events by source
SELECT source, COUNT(*) FROM content_events GROUP BY source;

-- Recent detections
SELECT * FROM analytics_records ORDER BY timestamp DESC LIMIT 10;

-- Average confidence by label
SELECT detection_label, AVG(confidence) 
FROM analytics_records 
GROUP BY detection_label;
```

### Backup

```powershell
# Simple file copy
Copy-Item data\astra.db data\astra_backup.db

# Or use SQLite backup command
sqlite3 data\astra.db ".backup data\astra_backup.db"
```

---

## Performance Tips

- **Indexes are already optimized** for common queries.
- **Use batch operations** when inserting multiple records.
- **Close sessions** properly (handled automatically).
- **VACUUM periodically** to reclaim space:

```powershell
sqlite3 data\astra.db "VACUUM;"
```

---

## Next Steps

- [x] SQLite persistence implemented
- [ ] Add database connection pooling
- [ ] Implement data retention policies
- [ ] Add database backup automation
- [ ] Create data export/import tools
- [ ] Migrate to PostgreSQL for production scale
