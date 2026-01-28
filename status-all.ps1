# Phase 2 Status Check Script
# Checks status of all Phase 2 components
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

function Test-ComponentStatus {
    param(
        [string]$Name,
        [string]$Path
    )
    
    Write-Host "$Name" -ForegroundColor Yellow -NoNewline
    Write-Host " ($Path)" -ForegroundColor DarkGray
    
    # Check if directory exists
    if (-not (Test-Path $Path)) {
        Write-Host "  ✗ Directory not found" -ForegroundColor Red
        return
    }
    
    # Check if installed (check for venv)
    Push-Location $Path
    $venvExists = Test-Path ".venv"
    $installed = $venvExists -and (Test-Path ".venv\Scripts\python.exe")
    Pop-Location
    
    if ($installed) {
        Write-Host "  ✓ Installed (venv ready)" -ForegroundColor Green
    } elseif ($venvExists) {
        Write-Host "  ⚠ Venv exists but incomplete" -ForegroundColor Yellow
    } else {
        Write-Host "  ✗ Not installed" -ForegroundColor Red
    }
    
    # Check database
    $dbPath = Join-Path $Path "data"
    if (Test-Path $dbPath) {
        $dbFiles = Get-ChildItem -Path $dbPath -Filter "*.db" -ErrorAction SilentlyContinue
        if ($dbFiles) {
            Write-Host "  ✓ Database: $($dbFiles.Count) file(s)" -ForegroundColor Green
        } else {
            Write-Host "  ○ Database: No data yet" -ForegroundColor Gray
        }
    }
    
    # Check logs
    $logPath = Join-Path $Path "logs"
    if (Test-Path $logPath) {
        $logFiles = Get-ChildItem -Path $logPath -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            Write-Host "  ✓ Logs: $($logFiles.Count) file(s)" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

Write-Header "Phase 2 Component Status"

# Check components
Test-ComponentStatus -Name "Sentinel" -Path "sentinel"
Test-ComponentStatus -Name "Oracle" -Path "oracle"
Test-ComponentStatus -Name "Sage" -Path "sage"
Test-ComponentStatus -Name "Guardian" -Path "guardian"
Test-ComponentStatus -Name "Nexus" -Path "nexus"

# Check running processes
Write-Host "Running Processes:" -ForegroundColor Cyan
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  Python: $($pythonProcs.Count) process(es)" -ForegroundColor Green
} else {
    Write-Host "  Python: None running" -ForegroundColor Gray
}

# Check background jobs
$jobs = Get-Job -ErrorAction SilentlyContinue
if ($jobs) {
    Write-Host "  Background Jobs: $($jobs.Count)" -ForegroundColor Green
    $jobs | Format-Table -AutoSize
} else {
    Write-Host "  Background Jobs: None" -ForegroundColor Gray
}

Write-Host ""
