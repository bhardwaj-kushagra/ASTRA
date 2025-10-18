# ASTRA - Smoke Test (End-to-End)
# Verifies that services are reachable and the basic flow works.

$ErrorActionPreference = 'Stop'

function Test-Url200 {
    param([string]$Url,[int]$Timeout=5)
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $Timeout -ErrorAction Stop
        return $resp.StatusCode -eq 200
    } catch { return $false }
}

Write-Host "==> Running ASTRA smoke test..." -ForegroundColor Cyan

# Base URL for local services (use IPv4 to avoid localhost/IPv6 issues)
$baseUrl = 'http://127.0.0.1'
$ing = $baseUrl + ':8001'
$det = $baseUrl + ':8002'
$ana = $baseUrl + ':8003'

Write-Host "DEBUG: constructed URLs -> ing='$ing' det='$det' ana='$ana'" -ForegroundColor Cyan

# Health checks
$ok_ing = Test-Url200 "$ing/"
$ok_det = Test-Url200 "$det/"
$ok_ana = Test-Url200 "$ana/"

Write-Host "[Health] Ingestion:  $($ok_ing) @ $ing/"
Write-Host "[Health] Detection:  $($ok_det) @ $det/"
Write-Host "[Health] Analytics:  $($ok_ana) @ $ana/"

if (-not ($ok_ing -and $ok_det -and $ok_ana)) {
    Write-Host "[WARN] One or more services are not healthy. Proceeding with best-effort checks." -ForegroundColor Yellow
}

# Sample detection
$sampleText = "This is a short sample text for detection."
$dreq = @{ text = $sampleText } | ConvertTo-Json
$dok = $false
try {
    $dresp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$det/detect" -Body $dreq -ContentType 'application/json' -TimeoutSec 20
    $djson = $dresp.Content | ConvertFrom-Json
    Write-Host "[Detect] label=$($djson.label) conf=$([math]::Round([double]$djson.confidence,3))" -ForegroundColor Green
    $dok = $true
} catch {
    Write-Host "[Detect] FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Analytics analyze
$aok = $false
try {
    $areq = @{ text = $sampleText } | ConvertTo-Json
    $aresp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$ana/analyze" -Body $areq -ContentType 'application/json' -TimeoutSec 20
    $ajson = $aresp.Content | ConvertFrom-Json
    Write-Host "[Analyze] status=$($ajson.status) stored=$($ajson.stored)" -ForegroundColor Green
    $aok = $true
} catch {
    Write-Host "[Analyze] FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Records and stats
try {
    $r = Invoke-WebRequest -UseBasicParsing -Uri "$ana/records?limit=5" -TimeoutSec 10
    $s = Invoke-WebRequest -UseBasicParsing -Uri "$ana/stats" -TimeoutSec 10
    $rc = ($r.Content | ConvertFrom-Json).Count
    $sj = $s.Content | ConvertFrom-Json
    # Use the full cmdlet name instead of the Select alias to satisfy script analyzers
    $statKeys = ($sj | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) -join ','
    Write-Host "[Records] last=$rc; [Stats] keys=$statKeys" -ForegroundColor Green
} catch {
    Write-Host "[Records/Stats] FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
}

if ($ok_ing -and $ok_det -and $ok_ana -and $dok -and $aok) {
    Write-Host "==> SMOKE TEST: PASS" -ForegroundColor Green
    exit 0
} else {
    Write-Host "==> SMOKE TEST: PARTIAL/FAIL (see messages above)" -ForegroundColor Yellow
    exit 1
}
