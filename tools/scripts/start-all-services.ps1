# ASTRA - Start All Services
# Launches all three services in separate PowerShell windows

Write-Host "Starting ASTRA services (safe quoting)..." -ForegroundColor Cyan

$rootDir = (Resolve-Path .).Path
$pythonExe = "python"  # assumes on PATH; adjust if needed

function Start-AstraService {
	param(
		[string]$Name,
		[int]$Port,
		[string]$ServiceDir
	)
	Write-Host "[OK] Starting $Name Service (port $Port)..." -ForegroundColor Yellow
	# Use -WorkingDirectory to avoid quoting issues with apostrophes in path
	Start-Process -FilePath $pythonExe -ArgumentList 'main.py' -WorkingDirectory $ServiceDir -WindowStyle Normal
	Start-Sleep -Milliseconds 800
}

$ingestionDir  = Join-Path $rootDir "services" | Join-Path -ChildPath "ingestion"
$detectionDir  = Join-Path $rootDir "services" | Join-Path -ChildPath "detection"
$analyticsDir  = Join-Path $rootDir "services" | Join-Path -ChildPath "risk-analytics"

Start-AstraService -Name Ingestion -Port 8001 -ServiceDir $ingestionDir
Start-AstraService -Name Detection -Port 8002 -ServiceDir $detectionDir
Start-AstraService -Name RiskAnalytics -Port 8003 -ServiceDir $analyticsDir

Write-Host ""; Write-Host "All services started!" -ForegroundColor Green; Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Ingestion:  http://127.0.0.1:8001"
Write-Host "  Detection:  http://127.0.0.1:8002"
Write-Host "  Analytics:  http://127.0.0.1:8003"
Write-Host ""; Write-Host "Dashboard:  http://127.0.0.1:8003/dashboard" -ForegroundColor Green
Write-Host ""; Write-Host "Use tools/scripts/stop-all.ps1 to stop all services." -ForegroundColor Cyan
