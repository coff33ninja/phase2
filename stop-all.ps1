# Phase 2 Stop All Components Script
# Stops all running Phase 2 components
# Author: coff33ninja
# Date: January 28, 2026

$ErrorActionPreference = "Continue"

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

Write-Header "Stopping Phase 2 Components"

# Stop Sentinel service first (uses PID file)
Write-Info "Stopping Sentinel service..."
Push-Location sentinel
try {
    if (Test-Path "sentinel.pid") {
        & .\stop-service.ps1 | Out-Null
        Write-Success "Sentinel service stopped"
    } else {
        Write-Info "Sentinel service not running (no PID file)"
    }
}
catch {
    Write-Info "Error stopping Sentinel service: $_"
}
finally {
    Pop-Location
}

# Stop background jobs
Write-Info "Stopping background jobs..."
$jobs = Get-Job
if ($jobs) {
    $jobs | Stop-Job
    $jobs | Remove-Job
    Write-Success "Stopped $($jobs.Count) background job(s)"
} else {
    Write-Info "No background jobs found"
}

# Stop Python processes
Write-Info "Stopping Python processes..."
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | 
    Where-Object { $_.Path -like "*phase2*" }

if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Success "Stopped $($pythonProcesses.Count) Python process(es)"
} else {
    Write-Info "No Python processes found"
}

# Stop Uvicorn (Nexus)
Write-Info "Stopping Uvicorn processes..."
$uvicornProcesses = Get-Process uvicorn -ErrorAction SilentlyContinue

if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Success "Stopped $($uvicornProcesses.Count) Uvicorn process(es)"
} else {
    Write-Info "No Uvicorn processes found"
}

Write-Header "All Components Stopped"
Write-Host "All Phase 2 components have been stopped." -ForegroundColor Green
Write-Host ""
