param(
    [string]$From = "http://127.0.0.1:8003",
    [string]$To = "http://127.0.0.1:8103",
    [int]$Limit = 200
)

$ErrorActionPreference = 'Stop'

Write-Host "==> Exporting threat exchange from $From" -ForegroundColor Cyan
$export = Invoke-RestMethod -Method Get -Uri ("$From/threat-exchange/export?limit=$Limit")

Write-Host "==> Importing into $To" -ForegroundColor Cyan
$body = $export | ConvertTo-Json -Depth 10
$importResp = Invoke-RestMethod -Method Post -Uri "$To/threat-exchange/import" -ContentType 'application/json' -Body $body

Write-Host "[OK] Imported" $importResp.inserted "indicators from" $importResp.producer_instance_id -ForegroundColor Green

Write-Host "==> Checking recent imported indicators on $To" -ForegroundColor Cyan
$recent = Invoke-RestMethod -Method Get -Uri "$To/threat-exchange/indicators?limit=10"
$recent | Select-Object -First 10 | Format-Table -AutoSize
