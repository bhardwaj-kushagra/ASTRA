<#
 ASTRA - Start All Services with SQLite
 Launches all three services in separate windows without embedding quoted paths.
 This avoids PowerShell ParserError caused by apostrophes in directory names.
#>

Write-Host "==> Starting ASTRA services with SQLite persistence..." -ForegroundColor Cyan
Write-Host ""

# Resolve repo root (two directories above this script)
$repoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
Set-Location $repoRoot

# Paths
$pythonExe = "C:\python 3.11\python.exe"
$dbPath = Join-Path $repoRoot "data\astra.db"
$ingestionDir = Join-Path $repoRoot "services\ingestion"
$detectionDir = Join-Path $repoRoot "services\detection"
$analyticsDir = Join-Path $repoRoot "services\risk-analytics"

# Ensure database exists
if (-not (Test-Path $dbPath)) {
    Write-Host "WARNING: Database not found!" -ForegroundColor Yellow
    Write-Host "         Initializing database..." -ForegroundColor Yellow
    & $pythonExe (Join-Path $repoRoot "tools\scripts\init_db.py")
    Write-Host ""
}

function Start-ServiceProc {
    param(
        [string]$WorkDir,
        [string[]]$ArgList
    )
    if (-not $ArgList -or $ArgList.Count -eq 0) {
        throw "Argument list cannot be empty."
    }
    Start-Process -FilePath $pythonExe -WorkingDirectory $WorkDir -ArgumentList $ArgList | Out-Null
}

# Start Ingestion Service
Write-Host "[OK] Starting Ingestion Service (port 8001) with SQLite..." -ForegroundColor Yellow
Start-ServiceProc -WorkDir $ingestionDir -ArgList @("main.py")
Start-Sleep -Seconds 1

# Start Detection Service
Write-Host "[OK] Starting Detection Service (port 8002)..." -ForegroundColor Yellow
Start-ServiceProc -WorkDir $detectionDir -ArgList @("main.py")
Start-Sleep -Seconds 1

# Start Risk Analytics Service
Write-Host "[OK] Starting Risk Analytics Service (port 8003) with SQLite..." -ForegroundColor Yellow
Start-ServiceProc -WorkDir $analyticsDir -ArgList @("main.py")

Write-Host ""
Write-Host "==> All services started with persistent SQLite storage!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Ingestion:  http://127.0.0.1:8001"
Write-Host "  Detection:  http://127.0.0.1:8002"
Write-Host "  Analytics:  http://127.0.0.1:8003"
Write-Host ""
Write-Host "Database:    data\astra.db" -ForegroundColor Cyan
Write-Host "Dashboard:   http://127.0.0.1:8003/dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "INFO: Data now persists across restarts!" -ForegroundColor Cyan
Write-Host "      Use tools\scripts\stop-all.ps1 to stop all services."
