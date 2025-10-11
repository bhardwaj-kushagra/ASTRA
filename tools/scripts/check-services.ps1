# Check ASTRA Services Status
Write-Host "Checking ASTRA service status..." -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Ingestion"; URL="http://localhost:8001"},
    @{Name="Detection"; URL="http://localhost:8002"},
    @{Name="Analytics"; URL="http://localhost:8003"}
)

foreach ($service in $services) {
    try {
        $null = Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✓ $($service.Name) Service: RUNNING" -ForegroundColor Green
        Write-Host "  URL: $($service.URL)"
    }
    catch {
        Write-Host "⏳ $($service.Name) Service: NOT READY" -ForegroundColor Yellow
        Write-Host "  URL: $($service.URL)"
    }
    Write-Host ""
}

Write-Host "Note: Detection service may take 1-2 minutes on first run to download models." -ForegroundColor Yellow
Write-Host "Dashboard: http://localhost:8003/dashboard" -ForegroundColor Cyan
