param(
    [int]$BasePort = 8000,
    [string]$DbPath = "",
    [string]$InstanceId = "",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent

$ingestionDir  = Join-Path $repoRoot 'services\ingestion'
$detectionDir  = Join-Path $repoRoot 'services\detection'
$analyticsDir  = Join-Path $repoRoot 'services\risk-analytics'

$ingestionPort = $BasePort + 1
$detectionPort = $BasePort + 2
$analyticsPort = $BasePort + 3

if ([string]::IsNullOrWhiteSpace($DbPath)) {
    $DbPath = Join-Path $repoRoot ("data\astra-{0}.db" -f $analyticsPort)
}
if ([string]::IsNullOrWhiteSpace($InstanceId)) {
    $InstanceId = "astra-{0}" -f $analyticsPort
}

Write-Host "==> Starting ASTRA stack" -ForegroundColor Cyan
Write-Host "    InstanceId: $InstanceId" -ForegroundColor Cyan
Write-Host "    DB Path:    $DbPath" -ForegroundColor Cyan
Write-Host "    Ports:      ingestion=$ingestionPort detection=$detectionPort analytics=$analyticsPort" -ForegroundColor Cyan

$env:ASTRA_DB_PATH = $DbPath
$env:ASTRA_INSTANCE_ID = $InstanceId
$env:DETECTION_SERVICE_URL = "http://127.0.0.1:$detectionPort"
$env:INGESTION_SERVICE_URL = "http://127.0.0.1:$ingestionPort"

function Start-Uvicorn {
    param(
        [string]$WorkDir,
        [int]$Port
    )
    $uvArgs = @('-m','uvicorn','main:app','--host','127.0.0.1','--port',"$Port")
    Start-Process -FilePath $PythonExe -WorkingDirectory $WorkDir -ArgumentList $uvArgs | Out-Null
}

Start-Uvicorn -WorkDir $ingestionDir -Port $ingestionPort
Start-Sleep -Milliseconds 400
Start-Uvicorn -WorkDir $detectionDir -Port $detectionPort
Start-Sleep -Milliseconds 400
Start-Uvicorn -WorkDir $analyticsDir -Port $analyticsPort

Write-Host "[OK] Stack started" -ForegroundColor Green
Write-Host "  Ingestion:  http://127.0.0.1:$ingestionPort" -ForegroundColor Yellow
Write-Host "  Detection:  http://127.0.0.1:$detectionPort" -ForegroundColor Yellow
Write-Host "  Analytics:  http://127.0.0.1:$analyticsPort/dashboard" -ForegroundColor Yellow
