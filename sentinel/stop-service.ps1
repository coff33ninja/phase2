#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Stop Sentinel background service
.DESCRIPTION
    Stops the Sentinel monitor process running in the background
.EXAMPLE
    .\stop-service.ps1
#>

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$PidFile = Join-Path $ScriptDir "sentinel.pid"

Write-Host "Stopping Sentinel Service..." -ForegroundColor Cyan

# Check if PID file exists
if (-not (Test-Path $PidFile)) {
    Write-Host "Sentinel is not running (no PID file found)" -ForegroundColor Yellow
    exit 0
}

# Read PID
$ProcessId = Get-Content $PidFile

# Check if process exists
$Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue

if (-not $Process) {
    Write-Host "Sentinel process not found (PID: $ProcessId)" -ForegroundColor Yellow
    Remove-Item -Path $PidFile
    exit 0
}

# Stop process
try {
    Stop-Process -Id $ProcessId -Force
    Write-Host "Sentinel stopped (PID: $ProcessId)" -ForegroundColor Green
}
catch {
    Write-Host "Error stopping process: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Clean up PID file
    Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
}
