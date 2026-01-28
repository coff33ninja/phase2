# Guardian Setup Script
# Sets up the Guardian environment with uv package manager

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Guardian Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
Write-Host "Checking for uv..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "Error: uv is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install uv first:" -ForegroundColor Yellow
    Write-Host "  pip install uv" -ForegroundColor White
    Write-Host "  or visit: https://docs.astral.sh/uv/" -ForegroundColor White
    exit 1
}

Write-Host "✓ uv found" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor White

if ($pythonVersion -notmatch "3\.12") {
    Write-Host "Warning: Python 3.12 recommended" -ForegroundColor Yellow
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor White
} else {
    uv venv --python 3.12
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
uv pip install --python .venv\Scripts\python.exe -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Install in editable mode
Write-Host "Installing Guardian in editable mode..." -ForegroundColor Yellow
uv pip install --python .venv\Scripts\python.exe -e .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Guardian installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Guardian" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
$directories = @("data", "logs", "profiles")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  Created $dir/" -ForegroundColor White
    }
}
Write-Host "✓ Directories ready" -ForegroundColor Green
Write-Host ""

# Copy .env.example to .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created (please configure)" -ForegroundColor Green
    Write-Host ""
}

# Create default profiles
Write-Host "Creating default profiles..." -ForegroundColor Yellow
python -c "from profiles import ProfileManager; ProfileManager().create_default_profiles()"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Default profiles created" -ForegroundColor Green
} else {
    Write-Host "! Could not create default profiles (will be created on first run)" -ForegroundColor Yellow
}
Write-Host ""

# Setup complete
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure .env file with your settings" -ForegroundColor White
Write-Host "  2. Run: python main.py status" -ForegroundColor White
Write-Host "  3. Run: python main.py profiles" -ForegroundColor White
Write-Host "  4. Run: python main.py activate gaming" -ForegroundColor White
Write-Host ""
Write-Host "For help: python main.py --help" -ForegroundColor Cyan
Write-Host ""
