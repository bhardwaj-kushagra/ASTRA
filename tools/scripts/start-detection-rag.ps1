param(
    [string]$PythonExe = "python"
)

Write-Host "==> Starting Detection Service with RAG detector" -ForegroundColor Cyan
$detDir = Join-Path (Resolve-Path .).Path "services\detection"
$env:DETECTOR_NAME = "rag"
Start-Process -FilePath $PythonExe -ArgumentList 'main.py' -WorkingDirectory $detDir | Out-Null
Write-Host "[OK] Detection on http://127.0.0.1:8002 (RAG)" -ForegroundColor Green