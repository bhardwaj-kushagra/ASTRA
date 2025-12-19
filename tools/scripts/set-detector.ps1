param(
    [ValidateSet("simple", "rag", "zero-shot")]
    [string]$Name = "simple",

    [string]$BaseUrl = "http://localhost:8002"
)

Write-Host "Switching detector to '$Name' at $BaseUrl" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/detector/$Name" -Method Post -TimeoutSec 30
    Write-Host "Active detector:" $response.active_detector -ForegroundColor Green
    if ($response.available_detectors) {
        Write-Host "Available detectors:" ($response.available_detectors -join ", ")
    }
}
catch {
    Write-Host "Failed to switch detector:" $_ -ForegroundColor Red
    exit 1
}
