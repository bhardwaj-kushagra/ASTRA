# ASTRA - Start All Services (uvicorn, explicit IPv4)
# Runs uvicorn for each service on 127.0.0.1 to avoid IPv6/localhost issues.
# Uses Start-Process with WorkingDirectory to avoid quoting problems in paths with apostrophes.

$ErrorActionPreference = 'Stop'

Write-Host "==> Starting ASTRA services (uvicorn, IPv4)" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$pythonExe = "C:\python 3.11\python.exe"

$services = @(
    @{ name = 'Ingestion';    dir = Join-Path $repoRoot 'services\ingestion';     port = 8001 },
    @{ name = 'Detection';    dir = Join-Path $repoRoot 'services\detection';     port = 8002 },
    @{ name = 'RiskAnalytics';dir = Join-Path $repoRoot 'services\risk-analytics'; port = 8003 }
)

function Start-Uvicorn {
    param(
        [string]$WorkDir,
        [int]$Port
    )
    $args = @('-m','uvicorn','main:app','--host','127.0.0.1','--port',"$Port")
    Start-Process -FilePath $pythonExe -WorkingDirectory $WorkDir -ArgumentList $args | Out-Null
}

foreach ($svc in $services) {
    Write-Host ("[OK] Starting {0} (port {1})..." -f $svc.name, $svc.port) -ForegroundColor Yellow
    Start-Uvicorn -WorkDir $svc.dir -Port $svc.port
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Ingestion:  http://127.0.0.1:8001"
Write-Host "  Detection:  http://127.0.0.1:8002"
Write-Host "  Analytics:  http://127.0.0.1:8003"
Write-Host ""
Write-Host "TIP: Use tools\scripts\stop-all.ps1 to stop all services." -ForegroundColor Green
