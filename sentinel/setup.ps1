#Requires -Version 5.1
<#
.SYNOPSIS
    Setup script for Phase 2.1 Foundation
.DESCRIPTION
    Automates the setup process: checks prerequisites, creates venv, installs dependencies
.NOTES
    Run this script from the phase2.1-foundation directory
#>

$ErrorActionPreference = 'Stop'

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║         Phase 2.1 Foundation - Setup Script                    ║
║         System Statistics Project                              ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check Python version
Write-Host "`n[1/6] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
            Write-Host "  ✗ Python 3.12+ required, found $major.$minor" -ForegroundColor Red
            Write-Host "  Install Python 3.12+ from https://www.python.org/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    Write-Host "  Install Python 3.12+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check for uv
Write-Host "`n[2/6] Checking for uv package manager..." -ForegroundColor Yellow
$uvInstalled = $false
try {
    $uvVersion = uv --version 2>&1
    Write-Host "  ✓ Found: $uvVersion" -ForegroundColor Green
    $uvInstalled = $true
} catch {
    Write-Host "  ⚠ uv not found (optional but recommended)" -ForegroundColor Yellow
    Write-Host "  Install with: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Gray
}

# Create virtual environment
Write-Host "`n[3/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  ⚠ Virtual environment already exists" -ForegroundColor Yellow
    $response = Read-Host "  Recreate? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item -Recurse -Force .venv
        Write-Host "  Removed existing .venv" -ForegroundColor Gray
    } else {
        Write-Host "  Using existing .venv" -ForegroundColor Green
        $skipVenv = $true
    }
}

if (-not $skipVenv) {
    if ($uvInstalled) {
        uv venv --python 3.12
    } else {
        python -m venv .venv
    }
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[4/6] Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ✗ Activation script not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n[5/6] Installing dependencies..." -ForegroundColor Yellow
if ($uvInstalled) {
    uv pip install -r requirements.txt
} else {
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

# Create .env file
Write-Host "`n[6/6] Setting up configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env from template" -ForegroundColor Green
    Write-Host "  Edit .env to customize settings" -ForegroundColor Gray
} else {
    Write-Host "  ⚠ .env already exists, skipping" -ForegroundColor Yellow
}

# Create data directory
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "  ✓ Created data directory" -ForegroundColor Green
}

# Summary
Write-Host "`n" -NoNewline
Write-Host ("═" * 64) -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host ("═" * 64) -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review and edit .env if needed" -ForegroundColor White
Write-Host "  2. Run test: python -c `"from collectors import CPUCollector; import asyncio; asyncio.run(CPUCollector().collect())`"" -ForegroundColor White
Write-Host "  3. Start development!" -ForegroundColor White

Write-Host "`nTo activate the environment in future sessions:" -ForegroundColor Yellow
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor Gray

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
