# Phase 2 Complete Setup Script
# Installs and configures all Phase 2 components
# Author: coff33ninja
# Date: January 28, 2026

param(
    [switch]$SkipTests,
    [switch]$QuickSetup,
    [string]$Component = "all"
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "→ $Text" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host "[$Text]" -ForegroundColor Cyan
}

# Check prerequisites
function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    # Check uv
    Write-Info "Checking uv package manager..."
    try {
        $uvVersion = uv --version 2>&1
        Write-Success "uv found: $uvVersion"
    } catch {
        Write-Error-Custom "uv not found! Please install uv first:"
        Write-Host "  pip install uv" -ForegroundColor White
        Write-Host "  or visit: https://docs.astral.sh/uv/" -ForegroundColor White
        exit 1
    }
    
    # Install Python 3.12 via uv if needed
    Write-Info "Ensuring Python 3.12 is available..."
    try {
        uv python install 3.12 2>&1 | Out-Null
        Write-Success "Python 3.12 ready"
    } catch {
        Write-Host "  Note: Python 3.12 may already be installed" -ForegroundColor Yellow
    }
    
    # Check if in correct directory
    if (-not (Test-Path "sentinel")) {
        Write-Error-Custom "Please run this script from the root directory with component folders"
        exit 1
    }
    
    Write-Success "All prerequisites met!"
}

# Setup individual component
function Install-Component {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Description
    )
    
    Write-Step "Setting up $Name"
    Write-Info $Description
    
    Push-Location $Path
    
    try {
        # Create venv with Python 3.12 if not exists
        if (-not (Test-Path ".venv")) {
            Write-Info "Creating virtual environment with Python 3.12..."
            uv venv --python 3.12
            
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create virtual environment"
            }
        }
        
        # Install dependencies using the venv's Python
        Write-Info "Installing dependencies..."
        uv pip install --python .venv\Scripts\python.exe -r requirements.txt
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        
        # Install in editable mode
        Write-Info "Installing $Name in editable mode..."
        uv pip install --python .venv\Scripts\python.exe -e .
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install $Name"
        }
        
        # Create necessary directories
        $dirs = @("data", "logs")
        foreach ($dir in $dirs) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
        
        # Copy .env.example to .env if not exists
        if ((Test-Path ".env.example") -and -not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
            Write-Info "Created .env file (please configure)"
        }
        
        Write-Success "$Name installed successfully!"
        
    } catch {
        Write-Error-Custom "Failed to install ${Name}: $_"
        Pop-Location
        return $false
    }
    
    Pop-Location
    return $true
}

# Run tests for component
function Test-Component {
    param(
        [string]$Name,
        [string]$Path
    )
    
    if ($SkipTests) {
        Write-Info "Skipping tests for $Name"
        return $true
    }
    
    Write-Info "Running tests for $Name..."
    
    Push-Location $Path
    
    try {
        if (Test-Path "tests") {
            pytest tests/ -v
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$Name tests passed!"
            } else {
                Write-Host "  Warning: Some tests failed for $Name" -ForegroundColor Yellow
            }
        } else {
            Write-Info "No tests found for $Name"
        }
    } catch {
        Write-Host "  Warning: Could not run tests for $Name" -ForegroundColor Yellow
    }
    
    Pop-Location
    return $true
}

# Main setup process
function Start-Setup {
    Write-Header "Phase 2 Complete Setup"
    Write-Host "This script will install all Phase 2 components:" -ForegroundColor White
    Write-Host "  1. Sentinel  - Data Collection & Storage" -ForegroundColor White
    Write-Host "  2. Oracle    - Local ML & Pattern Learning" -ForegroundColor White
    Write-Host "  3. Sage      - Gemini Integration" -ForegroundColor White
    Write-Host "  4. Guardian  - Auto-Tuning & Optimization" -ForegroundColor White
    Write-Host "  5. Nexus     - Dashboard & Interface" -ForegroundColor White
    Write-Host ""
    
    if (-not $QuickSetup) {
        $confirm = Read-Host "Continue? (Y/N)"
        if ($confirm -ne "Y" -and $confirm -ne "y") {
            Write-Host "Setup cancelled." -ForegroundColor Yellow
            exit 0
        }
    }
    
    # Test prerequisites
    Test-Prerequisites
    
    # Component definitions
    $components = @(
        @{
            Name = "Sentinel"
            Path = "sentinel"
            Description = "Data Collection & Storage - Watches and records everything"
            Order = 1
        },
        @{
            Name = "Oracle"
            Path = "oracle"
            Description = "Local ML & Pattern Learning - Predicts and learns patterns"
            Order = 2
        },
        @{
            Name = "Sage"
            Path = "sage"
            Description = "Gemini Integration - Provides wisdom and guidance"
            Order = 3
        },
        @{
            Name = "Guardian"
            Path = "guardian"
            Description = "Auto-Tuning & Optimization - Protects and optimizes"
            Order = 4
        },
        @{
            Name = "Nexus"
            Path = "nexus"
            Description = "Dashboard & Interface - Connects everything together"
            Order = 5
        }
    )
    
    # Filter components if specific one requested
    if ($Component -ne "all") {
        $components = $components | Where-Object { $_.Name -eq $Component }
        if ($components.Count -eq 0) {
            Write-Error-Custom "Component '$Component' not found!"
            Write-Host "Available components: Sentinel, Oracle, Sage, Guardian, Nexus" -ForegroundColor Yellow
            exit 1
        }
    }
    
    # Install components
    $successCount = 0
    $failCount = 0
    
    foreach ($comp in $components) {
        if (Install-Component -Name $comp.Name -Path $comp.Path -Description $comp.Description) {
            $successCount++
            
            # Run tests
            if (-not $QuickSetup) {
                Test-Component -Name $comp.Name -Path $comp.Path
            }
        } else {
            $failCount++
        }
    }
    
    # Summary
    Write-Header "Setup Complete!"
    
    Write-Host "Results:" -ForegroundColor Cyan
    Write-Host "  ✓ Successfully installed: $successCount component(s)" -ForegroundColor Green
    if ($failCount -gt 0) {
        Write-Host "  ✗ Failed to install: $failCount component(s)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Configure .env files in each component directory" -ForegroundColor White
    Write-Host "  2. Start Sentinel: cd sentinel && python main.py collect" -ForegroundColor White
    Write-Host "  3. Start Nexus: cd nexus && python main.py" -ForegroundColor White
    Write-Host "  4. Access dashboard: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "For detailed usage, see USAGE.md in each component directory" -ForegroundColor Cyan
    Write-Host ""
}

# Run setup
try {
    Start-Setup
} catch {
    Write-Error-Custom "Setup failed: $_"
    exit 1
}
