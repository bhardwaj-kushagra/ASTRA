# ASTRA - Start All Services
# Launches all three services in separate PowerShell windows

Write-Host "Starting ASTRA services..." -ForegroundColor Cyan

$rootDir = Get-Location
$venvActivate = Join-Path $rootDir "venv\Scripts\Activate.ps1"

# Start Ingestion Service
Write-Host "Starting Ingestion Service (port 8001)..." -ForegroundColor Yellow
$ingestionDir = Join-Path $rootDir "services\ingestion"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$ingestionDir'; & '$venvActivate'; python main.py"

Start-Sleep -Seconds 2

# Start Detection Service
Write-Host "Starting Detection Service (port 8002)..." -ForegroundColor Yellow
$detectionDir = Join-Path $rootDir "services\detection"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$detectionDir'; & '$venvActivate'; python main.py"

Start-Sleep -Seconds 2

# Start Risk Analytics Service
Write-Host "Starting Risk Analytics Service (port 8003)..." -ForegroundColor Yellow
$analyticsDir = Join-Path $rootDir "services\risk-analytics"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$analyticsDir'; & '$venvActivate'; python main.py"

Write-Host ""
Write-Host "All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Ingestion:  http://localhost:8001"
Write-Host "  Detection:  http://localhost:8002"
Write-Host "  Analytics:  http://localhost:8003"
Write-Host ""
Write-Host "Dashboard:  http://localhost:8003/dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C in each service window to stop them."
