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

function Test-ComponentSetup {
    param([string]$ComponentPath)
    
    $venvPath = Join-Path $ComponentPath ".venv\Scripts\python.exe"
    
    if (-not (Test-Path $venvPath)) {
        return $false
    }
    
    # Quick check if dependencies are installed by checking for click
    Push-Location $ComponentPath
    try {
        $null = uv pip show click 2>&1
        Pop-Location
        return $LASTEXITCODE -eq 0
    }
    catch {
        Pop-Location
        return $false
    }
}

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

# Validate component setup
Write-Info "Validating component setup..."
$componentsToCheck = @("sentinel", "nexus")
if (-not $SentinelOnly -and -not $NexusOnly) {
    $componentsToCheck += @("oracle", "sage", "guardian")
}

$setupIssues = @()
foreach ($comp in $componentsToCheck) {
    if (-not (Test-ComponentSetup -ComponentPath $comp)) {
        $setupIssues += $comp
    }
}

if ($setupIssues.Count -gt 0) {
    Write-Host ""
    Write-Host "✗ Setup incomplete for: $($setupIssues -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run setup first:" -ForegroundColor Yellow
    Write-Host "  .\setup-all.ps1 -QuickSetup" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Success "All components validated"

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



# Start Sentinel
if (-not $NexusOnly) {
    Write-Info "Starting Sentinel (Data Collection)..."
    
    if ($Background) {
        # Start Sentinel service in background using Start-Process
        Push-Location sentinel
        try {
            $null = Start-Process -FilePath "powershell.exe" `
                -ArgumentList "-File", "start-service.ps1", "-Interval", "5" `
                -WindowStyle Hidden `
                -PassThru
            
            # Wait a moment for PID file to be created
            Start-Sleep -Seconds 2
            
            if (Test-Path "sentinel.pid") {
                $sentinelPid = Get-Content "sentinel.pid"
                Write-Success "Sentinel service started (PID: $sentinelPid)"
            } else {
                Write-Success "Sentinel service starting..."
            }
        }
        catch {
            Write-Host "  Error starting Sentinel: $_" -ForegroundColor Red
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Host "  Run in separate terminal: cd sentinel && .\start-service.ps1" -ForegroundColor White
    }
    
    if ($SentinelOnly) {
        Write-Success "Sentinel started!"
        Write-Host ""
        Write-Host "To stop: cd sentinel && .\stop-service.ps1" -ForegroundColor Cyan
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
        Push-Location oracle
        try {
            $oracleProcess = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
                -ArgumentList "main.py", "scheduler" `
                -WindowStyle Hidden `
                -PassThru `
                -RedirectStandardError "logs\oracle_error.log" `
                -RedirectStandardOutput "logs\oracle_output.log"
            
            Write-Success "Oracle started (PID: $($oracleProcess.Id))"
        }
        catch {
            Write-Host "  Error starting Oracle: $_" -ForegroundColor Red
        }
        finally {
            Pop-Location
        }
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
        # Start Nexus using Start-Process with hidden window
        Push-Location nexus
        try {
            $nexusProcess = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
                -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--ws", "wsproto", "--log-level", "info" `
                -WindowStyle Hidden `
                -PassThru
            
            Write-Success "Nexus started (PID: $($nexusProcess.Id))"
        }
        catch {
            Write-Host "  Error starting Nexus: $_" -ForegroundColor Red
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Host "  Run in separate terminal: cd nexus && .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws wsproto" -ForegroundColor White
    }
    
    # Wait for Nexus to start
    Start-Sleep -Seconds 2
}

Write-Header "Components Started!"

if ($Background) {
    Write-Host "Running Processes:" -ForegroundColor Cyan
    
    # Show Sentinel
    if (Test-Path "sentinel\sentinel.pid") {
        $sentinelPid = Get-Content "sentinel\sentinel.pid"
        Write-Host "  Sentinel (PID: $sentinelPid)" -ForegroundColor Green
    }
    
    # Show Python processes
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcs) {
        Write-Host "  Python processes: $($pythonProcs.Count)" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Yellow
    Write-Host "  Dashboard: http://localhost:8001" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8001/docs" -ForegroundColor White
    Write-Host "  Health:    http://localhost:8001/health" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Management Commands:" -ForegroundColor Yellow
    Write-Host "  Status:      .\status-all.ps1" -ForegroundColor White
    Write-Host "  Stop all:    .\stop-all.ps1" -ForegroundColor White
    Write-Host "  View logs:   Get-Content <component>\logs\*.log -Tail 50 -Wait" -ForegroundColor White
} else {
    Write-Host "Manual Start Instructions:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Terminal 1 - Sentinel:" -ForegroundColor Yellow
    Write-Host "  cd sentinel" -ForegroundColor White
    Write-Host "  .\start-service.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Terminal 2 - Nexus:" -ForegroundColor Yellow
    Write-Host "  cd nexus" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws none" -ForegroundColor White
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
