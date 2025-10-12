<#
    Check ASTRA Services Status (hardened)
    - Prefer IPv4 (127.0.0.1) to avoid IPv6/localhost quirks
    - Add small retry with backoff
    - Clearer output
#>

Write-Host "Checking ASTRA service status..." -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Ingestion"; Urls=@("http://127.0.0.1:8001/", "http://localhost:8001/")},
    @{Name="Detection"; Urls=@("http://127.0.0.1:8002/", "http://localhost:8002/")},
    @{Name="Analytics"; Urls=@("http://127.0.0.1:8003/", "http://localhost:8003/")}
)

function Test-ServiceHealthy {
    param(
        [string[]]$Urls,
        [int]$Retries = 2,
        [int]$TimeoutSec = 3
    )

    foreach ($url in $Urls) {
        for ($i = 0; $i -le $Retries; $i++) {
            try {
                $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec $TimeoutSec -ErrorAction Stop
                if ($resp.StatusCode -eq 200) { return @{ healthy = $true; url = $url } }
            } catch {
                Start-Sleep -Milliseconds (300 * ($i + 1))
            }
        }
    }
    return @{ healthy = $false; url = $Urls[0] }
}

foreach ($svc in $services) {
    $result = Test-ServiceHealthy -Urls $svc.Urls -Retries 2 -TimeoutSec 4
    if ($result.healthy) {
        Write-Host ("[OK] {0} Service: RUNNING" -f $svc.Name) -ForegroundColor Green
        Write-Host ("     URL: {0}" -f $result.url)
    } else {
        Write-Host ("[WAIT] {0} Service: NOT READY" -f $svc.Name) -ForegroundColor Yellow
        Write-Host ("       Tried: {0}" -f ($svc.Urls -join ", "))
    }
    Write-Host ""
}

Write-Host "Note: Detection service may take 1-2 minutes on first run to download models." -ForegroundColor Yellow
Write-Host "Dashboard: http://127.0.0.1:8003/dashboard" -ForegroundColor Cyan
