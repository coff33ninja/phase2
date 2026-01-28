# Phase 2 Start All Components Script
# Starts all Phase 2 components in the correct order
# Author: coff33ninja
# Date: January 28, 2026

param(
    [switch]$Background,
    [switch]$SentinelOnly,
    [switch]$NexusOnly,
    [switch]$All
)

$ErrorActionPreference = "Stop"

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

function Start-ComponentBackground {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Command
    )
    
    Write-Info "Starting $Name in background..."
    
    $job = Start-Job -ScriptBlock {
        param($p, $c)
        Set-Location $p
        
        # Activate venv and run command
        if (Test-Path ".venv\Scripts\python.exe") {
            # Execute the full command directly
            Invoke-Expression "& .\.venv\Scripts\$c"
        } else {
            Write-Error "Virtual environment not found in $p"
        }
    } -ArgumentList $Path, $Command
    
    Write-Success "$Name started (Job ID: $($job.Id))"
    return $job
}

Write-Header "Phase 2 Component Launcher"

# Check if in correct directory
if (-not (Test-Path "sentinel")) {
    Write-Host "✗ Please run this script from the root directory with component folders" -ForegroundColor Red
    exit 1
}

# If -All flag is used, set -Background automatically
if ($All) {
    $Background = $true
    Write-Info "Starting all components in background mode..."
}

# If no flags provided, show usage
if (-not $Background -and -not $SentinelOnly -and -not $NexusOnly) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start-all.ps1 -Background      # Start all in background" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -All             # Same as -Background" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -SentinelOnly    # Start only Sentinel" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -NexusOnly       # Start only Nexus" -ForegroundColor White
    Write-Host ""
    Write-Host "Without flags, showing manual start instructions..." -ForegroundColor Cyan
    Write-Host ""
}

$jobs = @()

# Start Sentinel
if (-not $NexusOnly) {
    Write-Info "Starting Sentinel (Data Collection)..."
    
    if ($Background) {
        $jobs += Start-ComponentBackground -Name "Sentinel" -Path "sentinel" -Command "python main.py collect"
    } else {
        Write-Host "  Run in separate terminal: cd sentinel && python main.py collect" -ForegroundColor White
    }
    
    if ($SentinelOnly) {
        Write-Success "Sentinel started!"
        Write-Host ""
        Write-Host "To stop: Get-Job | Stop-Job" -ForegroundColor Cyan
        exit 0
    }
    
    # Wait for Sentinel to initialize
    Start-Sleep -Seconds 3
}

# Start Sage (AI Assistant)
if (-not $SentinelOnly -and -not $NexusOnly) {
    Write-Info "Starting Sage (AI Assistant)..."
    Write-Host "  Note: Sage runs interactively. Use 'cd sage && .\.venv\Scripts\python.exe main.py query' to chat" -ForegroundColor Gray
    
    # Sage is interactive, so we'll skip it in background mode
    # Users should run it manually when they want to chat
    
    # Wait a moment
    Start-Sleep -Seconds 1
}

# Start Oracle (Local ML)
if (-not $SentinelOnly -and -not $NexusOnly) {
    Write-Info "Starting Oracle (Local ML - Pattern Learning)..."
    
    if ($Background) {
        # Oracle runs scheduler for continuous learning
        # Set TensorFlow environment variables to suppress warnings
        $jobs += Start-Job -ScriptBlock {
            param($p)
            Set-Location $p
            
            # Set TensorFlow environment variables
            $env:TF_ENABLE_ONEDNN_OPTS = "0"
            $env:TF_CPP_MIN_LOG_LEVEL = "2"
            
            # Activate venv and run command
            if (Test-Path ".venv\Scripts\python.exe") {
                & .\.venv\Scripts\python.exe main.py scheduler
            } else {
                Write-Error "Virtual environment not found in $p"
            }
        } -ArgumentList "oracle"
        
        Write-Success "Oracle started (Job ID: $($jobs[-1].Id))"
    } else {
        Write-Host "  Run in separate terminal: cd oracle && .\.venv\Scripts\python.exe main.py scheduler" -ForegroundColor White
    }
    
    # Wait for Oracle to initialize
    Start-Sleep -Seconds 2
}

# Start Nexus
if (-not $SentinelOnly) {
    Write-Info "Starting Nexus (Dashboard)..."
    
    if ($Background) {
        $jobs += Start-ComponentBackground -Name "Nexus" -Path "nexus" -Command "python -m uvicorn main:app --host 0.0.0.0 --port 8001 --no-access-log --ws none"
    } else {
        Write-Host "  Run in separate terminal: cd nexus && .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws none" -ForegroundColor White
    }
    
    # Wait for Nexus to start
    Start-Sleep -Seconds 2
}

Write-Header "Components Started!"

if ($Background) {
    Write-Host "Running Jobs:" -ForegroundColor Cyan
    Get-Job | Format-Table -AutoSize
    
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Yellow
    Write-Host "  Dashboard: http://localhost:8001" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8001/docs" -ForegroundColor White
    Write-Host "  Health:    http://localhost:8001/health" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Management Commands:" -ForegroundColor Yellow
    Write-Host "  View jobs:   Get-Job" -ForegroundColor White
    Write-Host "  View output: Receive-Job -Id <id>" -ForegroundColor White
    Write-Host "  Stop all:    Get-Job | Stop-Job" -ForegroundColor White
    Write-Host "  Remove all:  Get-Job | Remove-Job" -ForegroundColor White
} else {
    Write-Host "Manual Start Instructions:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Terminal 1 - Sentinel:" -ForegroundColor Yellow
    Write-Host "  cd sentinel" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe main.py collect" -ForegroundColor White
    Write-Host ""
    Write-Host "Terminal 2 - Nexus:" -ForegroundColor Yellow
    Write-Host "  cd nexus" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --ws none" -ForegroundColor White
    Write-Host ""
    Write-Host "Optional - Oracle (Terminal 3):" -ForegroundColor Yellow
    Write-Host "  cd oracle" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe main.py train" -ForegroundColor White
    Write-Host ""
    Write-Host "Optional - Sage (Terminal 4):" -ForegroundColor Yellow
    Write-Host "  cd sage" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Optional - Guardian (As needed):" -ForegroundColor Yellow
    Write-Host "  cd guardian" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe main.py activate gaming" -ForegroundColor White
    Write-Host ""
    Write-Host "TIP: Use '.\start-all.ps1 -Background' to start automatically!" -ForegroundColor Green
}

Write-Host ""
