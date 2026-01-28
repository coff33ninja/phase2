# Sage Setup Script
Write-Host "Setting up Sage (Phase 2.3)..." -ForegroundColor Cyan

# Check if uv is installed
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Error: uv is not installed" -ForegroundColor Red
    Write-Host "Install from: https://docs.astral.sh/uv/" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.12") {
    Write-Host "Python 3.12 detected: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Warning: Python 3.12 recommended, found: $pythonVersion" -ForegroundColor Yellow
}

# Create virtual environment if not exists
if (!(Test-Path ".venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Cyan
    uv venv --python 3.12
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
uv pip install --python .venv\Scripts\python.exe -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "`nCreating .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file - Please add your GEMINI_API_KEY" -ForegroundColor Yellow
}

# Create data directories
Write-Host "`nCreating data directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Install package in editable mode
Write-Host "`nInstalling Sage package..." -ForegroundColor Cyan
uv pip install --python .venv\Scripts\python.exe -e .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSetup complete!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Add your GEMINI_API_KEY to .env file"
    Write-Host "2. Run: python main.py status"
    Write-Host "3. Run: python main.py query 'How is my system performing?'"
} else {
    Write-Host "Error installing package" -ForegroundColor Red
    exit 1
}
