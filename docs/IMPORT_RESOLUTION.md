# Import Resolution Guide

## Problem
VS Code Pylance was showing "Import could not be resolved" warnings for the `models` module.

## Root Cause
The services use runtime `sys.path` manipulation to import from `data/schemas/models.py`, but Pylance performs static analysis before runtime and doesn't see these imports.

## Solution

### 1. Package Structure
Added `__init__.py` files to make proper Python packages:
- `data/__init__.py`
- `data/schemas/__init__.py`

### 2. VS Code Configuration
Created `.vscode/settings.json`:
```json
{
    "python.analysis.extraPaths": ["${workspaceFolder}"],
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "none"
    }
}
```

### 3. Pyright Configuration
Created `pyrightconfig.json`:
```json
{
    "extraPaths": ["."],
    "reportMissingImports": "none"
}
```

## How It Works

### Runtime (Services Running)
Services use this pattern:
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import ContentEvent
```

This works perfectly when services run.

### Static Analysis (VS Code/Pylance)
Pylance now knows to:
1. Look in workspace root for imports
2. Suppress missing import warnings since they're resolved at runtime

## Verification

Test imports work:
```powershell
python -c "import sys; sys.path.insert(0, 'C:\A Developer''s Stuff\ASTRA'); from data.schemas import models; print('OK')"
```

Or test a service directly:
```powershell
cd services\ingestion
python main.py
```

## Notes
- The `.vscode/` directory is git-ignored for developer preferences
- Services work without VS Code - the sys.path manipulation is portable
- This pattern allows services to be standalone while sharing schemas
