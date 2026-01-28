# Oracle Setup Script
# Automated setup for Oracle ML engine

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Oracle Setup - Phase 2.2" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from Oracle directory
if (!(Test-Path "pyproject.toml")) {
    Write-Host "Error: Must run from Oracle directory" -ForegroundColor Red
    exit 1
}

# Check for Python
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check for uv
Write-Host "[2/6] Checking uv package manager..." -ForegroundColor Yellow
$uvVersion = uv --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: uv not found, using pip" -ForegroundColor Yellow
    $useUv = $false
} else {
    Write-Host "Found: $uvVersion" -ForegroundColor Green
    $useUv = $true
}

# Create directories
Write-Host "[3/6] Creating directories..." -ForegroundColor Yellow
$dirs = @("data", "saved_models", "logs")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    }
}

# Copy .env.example to .env if not exists
Write-Host "[4/6] Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file" -ForegroundColor Green
} else {
    Write-Host ".env already exists" -ForegroundColor Yellow
}

# Create virtual environment if not exists
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    if ($useUv) {
        uv venv --python 3.12
    } else {
        python -m venv .venv
    }
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Install dependencies
Write-Host "[5/6] Installing dependencies..." -ForegroundColor Yellow
if ($useUv) {
    uv pip install --python .venv\Scripts\python.exe -r requirements.txt
} else {
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install package in editable mode
Write-Host "[6/6] Installing Oracle package..." -ForegroundColor Yellow
if ($useUv) {
    uv pip install --python .venv\Scripts\python.exe -e .
} else {
    .\.venv\Scripts\python.exe -m pip install -e .
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "  Setup Complete!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Ensure Sentinel is running and has collected data"
    Write-Host "2. Run: python main.py status"
    Write-Host "3. Run: python main.py train --days 30"
    Write-Host ""
} else {
    Write-Host "Error: Package installation failed" -ForegroundColor Red
    exit 1
}
