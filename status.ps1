# Phase 2 System Status Script
# Shows comprehensive status of all components and training readiness
# Author: coff33ninja
# Date: January 28, 2026

param(
    [switch]$Detailed
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                    Phase 2 System Status                    " -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if Sage is available
if (Test-Path "sage\.venv\Scripts\python.exe") {
    Write-Host "Running comprehensive status check..." -ForegroundColor Yellow
    Write-Host ""
    
    # Run Sage's status command
    Push-Location sage
    & .\.venv\Scripts\python.exe main.py status
    Pop-Location
} else {
    Write-Host "Error: Sage not installed" -ForegroundColor Red
    Write-Host "Run: .\setup-all.ps1 -QuickSetup" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Show running jobs if detailed
if ($Detailed) {
    Write-Host ""
    Write-Host "Running Background Jobs:" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Cyan
    
    $jobs = Get-Job
    if ($jobs) {
        $jobs | Format-Table -AutoSize
        
        Write-Host ""
        Write-Host "Job Management:" -ForegroundColor Yellow
        Write-Host "  View output: Receive-Job -Id <id>" -ForegroundColor White
        Write-Host "  Stop all:    Get-Job | Stop-Job" -ForegroundColor White
        Write-Host "  Remove all:  Get-Job | Remove-Job" -ForegroundColor White
    } else {
        Write-Host "  No background jobs running" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Start components: .\start-all.ps1 -All" -ForegroundColor White
    }
    Write-Host ""
}

# Quick actions
Write-Host "Quick Actions:" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Start all:     .\start-all.ps1 -All" -ForegroundColor White
Write-Host "  Stop all:      .\stop-all.ps1" -ForegroundColor White
Write-Host "  Ask Sage:      cd sage && .\.venv\Scripts\python.exe main.py query" -ForegroundColor White
Write-Host "  Train Oracle:  cd oracle && .\.venv\Scripts\python.exe main.py train" -ForegroundColor White
Write-Host "  Dashboard:     http://localhost:8001" -ForegroundColor White
Write-Host ""

