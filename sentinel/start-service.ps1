#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start Sentinel as a background service with auto-restart
.DESCRIPTION
    Runs Sentinel monitor command in the background with automatic restart on failure.
    Logs are written to sentinel/logs/sentinel.log
.PARAMETER Interval
    Collection interval in seconds (default: 5)
.PARAMETER NoRestart
    Disable auto-restart on failure
.EXAMPLE
    .\start-service.ps1
    .\start-service.ps1 -Interval 1
    .\start-service.ps1 -NoRestart
#>

param(
    [int]$Interval = 5,
    [switch]$NoRestart
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Starting Sentinel Service..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Create logs directory
$LogsDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

$LogFile = Join-Path $LogsDir "service.log"
$PidFile = Join-Path $ScriptDir "sentinel.pid"

# Check if already running
if (Test-Path $PidFile) {
    $OldPid = Get-Content $PidFile
    $Process = Get-Process -Id $OldPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Sentinel is already running (PID: $OldPid)" -ForegroundColor Yellow
        Write-Host "Stop it first with: .\stop-service.ps1" -ForegroundColor Yellow
        exit 1
    }
}

# Function to start Sentinel
function Start-Sentinel {
    $StartTime = Get-Date
    Write-Host "[$($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))] Starting Sentinel monitor (interval: ${Interval}s)..." -ForegroundColor Green
    
    # Start process in background
    $Process = Start-Process -FilePath ".venv\Scripts\python.exe" `
        -ArgumentList "main.py", "monitor", "--interval", $Interval `
        -WorkingDirectory $ScriptDir `
        -WindowStyle Hidden `
        -PassThru
    
    # Save PID
    $Process.Id | Out-File -FilePath $PidFile -Encoding ASCII
    
    Write-Host "Sentinel started (PID: $($Process.Id))" -ForegroundColor Green
    Write-Host "Logs: sentinel/logs/sentinel.log" -ForegroundColor Cyan
    Write-Host "Service log: $LogFile" -ForegroundColor Cyan
    
    return $Process
}

# Start Sentinel
$Process = Start-Sentinel

if ($NoRestart) {
    Write-Host "Auto-restart disabled. Sentinel will not restart on failure." -ForegroundColor Yellow
    exit 0
}

# Monitor and auto-restart
Write-Host "`nMonitoring Sentinel process (Ctrl+C to stop)..." -ForegroundColor Cyan
Write-Host "To stop: .\stop-service.ps1" -ForegroundColor Yellow

$RestartCount = 0
$MaxRestarts = 10
$RestartDelay = 5

try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check if process is still running
        $Process = Get-Process -Id $Process.Id -ErrorAction SilentlyContinue
        
        if (-not $Process) {
            $RestartCount++
            $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            
            Write-Host "[$Timestamp] Sentinel stopped unexpectedly (restart $RestartCount/$MaxRestarts)" -ForegroundColor Red
            Add-Content -Path $LogFile -Value "[$Timestamp] Sentinel stopped unexpectedly (restart $RestartCount/$MaxRestarts)"
            
            if ($RestartCount -ge $MaxRestarts) {
                Write-Host "[$Timestamp] Maximum restart attempts reached. Stopping service." -ForegroundColor Red
                Add-Content -Path $LogFile -Value "[$Timestamp] Maximum restart attempts reached. Stopping service."
                Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
                exit 1
            }
            
            Write-Host "Waiting ${RestartDelay}s before restart..." -ForegroundColor Yellow
            Start-Sleep -Seconds $RestartDelay
            
            # Restart
            $Process = Start-Sentinel
            Add-Content -Path $LogFile -Value "[$Timestamp] Sentinel restarted (PID: $($Process.Id))"
        }
    }
}
catch {
    Write-Host "`nStopping service..." -ForegroundColor Yellow
    
    # Stop process
    if ($Process) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
    
    # Clean up PID file
    Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
    
    Write-Host "Service stopped" -ForegroundColor Green
}
