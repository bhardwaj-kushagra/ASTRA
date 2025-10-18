# Warm up detection service by triggering the first model call
param(
    [string]$Url = 'http://127.0.0.1:8002/detect',
    [int]$TimeoutSec = 600
)

$ErrorActionPreference = 'Stop'

Write-Host "==> Warming up detection service at $Url (timeout ${TimeoutSec}s)..." -ForegroundColor Cyan

$body = @{ text = 'Warm up text to trigger model download' } | ConvertTo-Json
$sw = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri $Url -Body $body -ContentType 'application/json' -TimeoutSec $TimeoutSec
    $sw.Stop()
    Write-Host ("[Warmup] Status={0}, Elapsed={1:n1}s" -f $resp.StatusCode, ($sw.Elapsed.TotalSeconds)) -ForegroundColor Green
} catch {
    $sw.Stop()
    Write-Host ("[Warmup] FAILED after {0:n1}s: {1}" -f $sw.Elapsed.TotalSeconds, $_.Exception.Message) -ForegroundColor Yellow
    exit 1
}
