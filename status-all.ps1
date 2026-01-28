# Phase 2 Comprehensive Status Check Script
# Shows status of all Phase 2 components via Sentinel's comprehensive status
# Author: coff33ninja
# Date: January 28, 2026

$ErrorActionPreference = "Stop"

# Check if Sentinel is installed
if (-not (Test-Path "sentinel\.venv\Scripts\python.exe")) {
    Write-Host ""
    Write-Host "❌ Sentinel not installed" -ForegroundColor Red
    Write-Host "   Sentinel is required for system status checks" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Run: .\setup-all.ps1 -QuickSetup" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Run Sentinel's comprehensive status (includes all components)
Push-Location sentinel
try {
    & ".\.venv\Scripts\python.exe" -m cli.main status --full
    
    # Quick Actions Footer
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Quick Actions" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Start all:     " -NoNewline -ForegroundColor White
    Write-Host ".\start-all.ps1 -All" -ForegroundColor Green
    Write-Host "  Stop all:      " -NoNewline -ForegroundColor White
    Write-Host ".\stop-all.ps1" -ForegroundColor Green
    Write-Host "  Dashboard:     " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:8001" -ForegroundColor Green
    Write-Host "  Ask Sage:      " -NoNewline -ForegroundColor White
    Write-Host "cd sage && .\.venv\Scripts\python.exe -m cli.main query" -ForegroundColor Green
    Write-Host "  Train Oracle:  " -NoNewline -ForegroundColor White
    Write-Host "cd oracle && .\.venv\Scripts\python.exe -m cli.main train" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Component-specific status:" -ForegroundColor DarkGray
    Write-Host "    Sentinel:  cd sentinel && .\.venv\Scripts\python.exe -m cli.main status" -ForegroundColor DarkGray
    Write-Host "    Oracle:    cd oracle && .\.venv\Scripts\python.exe -m cli.main status" -ForegroundColor DarkGray
    Write-Host "    Sage:      cd sage && .\.venv\Scripts\python.exe -m cli.main status" -ForegroundColor DarkGray
    Write-Host "    Guardian:  cd guardian && .\.venv\Scripts\python.exe -m cli.main status" -ForegroundColor DarkGray
    Write-Host "    Nexus:     cd nexus && .\.venv\Scripts\python.exe -m cli.main status" -ForegroundColor DarkGray
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "❌ Error running status check: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
finally {
    Pop-Location
}
