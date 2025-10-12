# ASTRA - Start All Services with SQLite
# Launches all three services in separate PowerShell windows

Write-Host "🚀 Starting ASTRA services with SQLite persistence..." -ForegroundColor Cyan
Write-Host ""

# Check if database exists
$dbPath = "data\astra.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "⚠️  Database not found!" -ForegroundColor Yellow
    Write-Host "   Initializing database..." -ForegroundColor Yellow
    python tools\scripts\init_db.py
    Write-Host ""
}

$rootDir = Get-Location
$pythonExe = "C:\python 3.11\python.exe"

# Start Ingestion Service
Write-Host "✓ Starting Ingestion Service (port 8001) with SQLite..." -ForegroundColor Yellow
$ingestionDir = Join-Path $rootDir "services\ingestion"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$ingestionDir'; & '$pythonExe' main.py"

Start-Sleep -Seconds 2

# Start Detection Service  
Write-Host "✓ Starting Detection Service (port 8002)..." -ForegroundColor Yellow
$detectionDir = Join-Path $rootDir "services\detection"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$detectionDir'; & '$pythonExe' main.py"

Start-Sleep -Seconds 2

# Start Risk Analytics Service
Write-Host "✓ Starting Risk Analytics Service (port 8003) with SQLite..." -ForegroundColor Yellow
$analyticsDir = Join-Path $rootDir "services\risk-analytics"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$analyticsDir'; & '$pythonExe' main.py"

Write-Host ""
Write-Host "🎉 All services started with persistent SQLite storage!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Ingestion:  http://localhost:8001"
Write-Host "  Detection:  http://localhost:8002"
Write-Host "  Analytics:  http://localhost:8003"
Write-Host ""
Write-Host "💾 Database:    data\astra.db" -ForegroundColor Cyan
Write-Host "📊 Dashboard:   http://localhost:8003/dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "ℹ️  Data now persists across restarts!" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C in each service window to stop them."
