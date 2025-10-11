# ASTRA Setup Script
# Run this from the root ASTRA directory

Write-Host "=== ASTRA Prototype Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host ""
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies for each service
Write-Host ""
Write-Host "Installing Ingestion Service dependencies..." -ForegroundColor Yellow
Set-Location "services\ingestion"
pip install -r requirements.txt --quiet
Set-Location "..\..\"

Write-Host ""
Write-Host "Installing Detection Service dependencies..." -ForegroundColor Yellow
Set-Location "services\detection"
pip install -r requirements.txt --quiet
Set-Location "..\..\"

Write-Host ""
Write-Host "Installing Risk Analytics Service dependencies..." -ForegroundColor Yellow
Set-Location "services\risk-analytics"
pip install -r requirements.txt --quiet
Set-Location "..\..\"

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start services in 3 separate terminals:"
Write-Host "   Terminal 1: cd services\ingestion; python main.py"
Write-Host "   Terminal 2: cd services\detection; python main.py"
Write-Host "   Terminal 3: cd services\risk-analytics; python main.py"
Write-Host ""
Write-Host "2. Or use the start script:"
Write-Host "   .\tools\scripts\start-all-services.ps1"
Write-Host ""
