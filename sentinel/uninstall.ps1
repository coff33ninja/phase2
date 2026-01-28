#Requires -Version 5.1
<#
.SYNOPSIS
    Uninstall script for Sentinel
.DESCRIPTION
    Removes virtual environment, data, logs, and configuration
.PARAMETER KeepData
    Keep data directory (database files)
.PARAMETER KeepVenv
    Keep virtual environment
.PARAMETER KeepConfig
    Keep .env configuration file
#>

param(
    [switch]$KeepData,
    [switch]$KeepVenv,
    [switch]$KeepConfig
)

$ErrorActionPreference = 'Stop'

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║         Sentinel - Uninstall Script                            ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "`nThis will remove:" -ForegroundColor Yellow
if (-not $KeepVenv) { Write-Host "  • Virtual environment (.venv/)" -ForegroundColor White }
if (-not $KeepData) { Write-Host "  • Data directory (data/)" -ForegroundColor White }
Write-Host "  • Log files (logs/)" -ForegroundColor White
if (-not $KeepConfig) { Write-Host "  • Configuration (.env)" -ForegroundColor White }

$response = Read-Host "`nContinue? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Uninstall cancelled" -ForegroundColor Yellow
    exit 0
}

# Remove virtual environment
if (-not $KeepVenv) {
    Write-Host "`n[1/4] Removing virtual environment..." -ForegroundColor Yellow
    if (Test-Path ".venv") {
        Remove-Item -Recurse -Force .venv
        Write-Host "  ✓ Removed .venv/" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ .venv/ not found" -ForegroundColor Gray
    }
} else {
    Write-Host "`n[1/4] Keeping virtual environment..." -ForegroundColor Yellow
}

# Remove data directory
if (-not $KeepData) {
    Write-Host "`n[2/4] Removing data directory..." -ForegroundColor Yellow
    if (Test-Path "data") {
        Remove-Item -Recurse -Force data
        Write-Host "  ✓ Removed data/" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ data/ not found" -ForegroundColor Gray
    }
} else {
    Write-Host "`n[2/4] Keeping data directory..." -ForegroundColor Yellow
}

# Remove logs directory
Write-Host "`n[3/4] Removing logs..." -ForegroundColor Yellow
if (Test-Path "logs") {
    Remove-Item -Recurse -Force logs
    Write-Host "  ✓ Removed logs/" -ForegroundColor Green
} else {
    Write-Host "  ⚠ logs/ not found" -ForegroundColor Gray
}

# Remove .env file
if (-not $KeepConfig) {
    Write-Host "`n[4/4] Removing configuration..." -ForegroundColor Yellow
    if (Test-Path ".env") {
        Remove-Item -Force .env
        Write-Host "  ✓ Removed .env" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ .env not found" -ForegroundColor Gray
    }
} else {
    Write-Host "`n[4/4] Keeping configuration..." -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -NoNewline
Write-Host ("═" * 64) -ForegroundColor Cyan
Write-Host " Uninstall Complete!" -ForegroundColor Green
Write-Host ("═" * 64) -ForegroundColor Cyan

if ($KeepData) {
    Write-Host "`nData preserved in data/" -ForegroundColor Yellow
}
if ($KeepVenv) {
    Write-Host "Virtual environment preserved in .venv/" -ForegroundColor Yellow
}
if ($KeepConfig) {
    Write-Host "Configuration preserved in .env" -ForegroundColor Yellow
}

Write-Host "`nTo reinstall, run: .\setup.ps1" -ForegroundColor Gray
