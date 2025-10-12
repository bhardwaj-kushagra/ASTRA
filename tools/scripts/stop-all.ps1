# ASTRA - Stop All Services
# Stops ingestion (8001), detection (8002), and analytics (8003) services.
# Kills process trees and waits until ports are freed. Safe for repeated invocations.

Write-Host "==> Stopping ASTRA services..." -ForegroundColor Cyan

$ports = @(8001, 8002, 8003)
$svcDirsRegex = 'services\\(ingestion|detection|risk-analytics)'
$stopped = New-Object System.Collections.Generic.HashSet[int]

function Stop-ProcessTreeSafely {
    param([int]$ProcessId)
    try {
        if (-not $stopped.Contains($ProcessId)) {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
            [void]$stopped.Add($ProcessId)
        }
    } catch {}
}

# 1) Stop processes listening on the well-known service ports
foreach ($p in $ports) {
    try {
        $conns = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            if ($c.OwningProcess) {
                Write-Host ("[KILL] Port {0} -> PID {1} (tree)" -f $p, $c.OwningProcess) -ForegroundColor Yellow
                # Kill entire process tree to catch uvicorn worker/child processes
                Start-Process -FilePath taskkill.exe -ArgumentList "/PID $($c.OwningProcess) /F /T" -NoNewWindow -Wait
                Stop-ProcessTreeSafely -ProcessId $c.OwningProcess
            }
        }
    } catch {}
}

# 2) Stop python processes started from service folders (uvicorn/main.py)
try {
    $py = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^python(\.exe)?$' -and $_.CommandLine -match $svcDirsRegex
    }
    foreach ($proc in $py) {
        Write-Host ("[KILL] Python PID {0}" -f $proc.ProcessId) -ForegroundColor Yellow
    Stop-ProcessTreeSafely -ProcessId [int]$proc.ProcessId
    }
} catch {}

# 3) Close stray PowerShell windows from service start (NoExit)
try {
    $ps = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^powershell(\.exe)?$' -and $_.CommandLine -match $svcDirsRegex
    }
    foreach ($proc in $ps) {
        Write-Host ("[KILL] PowerShell PID {0}" -f $proc.ProcessId) -ForegroundColor Yellow
    Stop-ProcessTreeSafely -ProcessId [int]$proc.ProcessId
    }
} catch {}

Start-Sleep -Milliseconds 300

# 4) Wait until ports are freed (up to ~3 seconds)
for ($i = 0; $i -lt 10; $i++) {
    $remaining = @()
    foreach ($p in $ports) {
        try {
            $conns = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
            if ($conns) { $remaining += $p }
        } catch {}
    }
    if ($remaining.Count -eq 0) { break }
    Start-Sleep -Milliseconds 300
}

# Summary
$remaining = @()
foreach ($p in $ports) {
    try {
        $conns = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
        if ($conns) { $remaining += $p }
    } catch {}
}

if ($remaining.Count -eq 0) {
    Write-Host "[OK] All service ports are free (8001, 8002, 8003)." -ForegroundColor Green
} else {
    Write-Host ("[WARN] Still listening on ports: {0}" -f ($remaining -join ", ")) -ForegroundColor Yellow
}
