# ASTRA - Restart All Services with SQLite
# Stops existing services, re-initializes DB if missing, and starts all services.

$ErrorActionPreference = 'Stop'

Write-Host "==> Restarting ASTRA services..." -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
Set-Location $repoRoot

# 1) Stop all
& "$PSScriptRoot\stop-all.ps1"

# 2) Ensure database exists
$dbPath = Join-Path $repoRoot "data\astra.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "[INIT] Database not found. Initializing..." -ForegroundColor Yellow
    python "tools\scripts\init_db.py"
}

# 3) Start all
& "$PSScriptRoot\start-with-sqlite.ps1"
