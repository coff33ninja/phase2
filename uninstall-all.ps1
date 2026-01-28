# Phase 2 - Complete Uninstall Script
# Removes all components, data, and virtual environments

param(
    [switch]$KeepData,
    [switch]$KeepVenvs,
    [switch]$Force
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "Phase 2 - Complete Uninstall" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

if (-not $Force) {
    Write-Host "WARNING: This will remove:" -ForegroundColor Yellow
    Write-Host "  - All virtual environments (.venv folders)" -ForegroundColor Yellow
    Write-Host "  - All collected data (databases)" -ForegroundColor Yellow
    Write-Host "  - All logs" -ForegroundColor Yellow
    Write-Host "  - All configuration files (.env)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Flags:" -ForegroundColor Cyan
    Write-Host "  -KeepData   : Keep databases and collected data" -ForegroundColor Cyan
    Write-Host "  -KeepVenvs  : Keep virtual environments" -ForegroundColor Cyan
    Write-Host "  -Force      : Skip confirmation prompt" -ForegroundColor Cyan
    Write-Host ""
    
    $confirmation = Read-Host "Are you sure you want to uninstall? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-Host "Uninstall cancelled." -ForegroundColor Green
        exit 0
    }
}

Write-Host ""
Write-Host "→ Stopping all running components..." -ForegroundColor Cyan

# Stop all background jobs
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue

# Stop Python processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "  Stopping Python processes..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Stop Uvicorn processes
$uvicornProcesses = Get-Process -Name "*uvicorn*" -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    Write-Host "  Stopping Uvicorn processes..." -ForegroundColor Yellow
    $uvicornProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host "✓ All processes stopped" -ForegroundColor Green
Write-Host ""

# Components to uninstall
$components = @("sentinel", "oracle", "sage", "guardian", "nexus")

foreach ($component in $components) {
    Write-Host "→ Uninstalling $component..." -ForegroundColor Cyan
    
    $componentPath = Join-Path $PSScriptRoot $component
    
    if (Test-Path $componentPath) {
        # Remove virtual environment
        if (-not $KeepVenvs) {
            $venvPath = Join-Path $componentPath ".venv"
            if (Test-Path $venvPath) {
                Write-Host "  Removing virtual environment..." -ForegroundColor Yellow
                Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  ✓ Virtual environment removed" -ForegroundColor Green
            }
        } else {
            Write-Host "  ⊙ Keeping virtual environment" -ForegroundColor Cyan
        }
        
        # Remove data
        if (-not $KeepData) {
            $dataPath = Join-Path $componentPath "data"
            if (Test-Path $dataPath) {
                Write-Host "  Removing data..." -ForegroundColor Yellow
                Remove-Item -Path $dataPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  ✓ Data removed" -ForegroundColor Green
            }
        } else {
            Write-Host "  ⊙ Keeping data" -ForegroundColor Cyan
        }
        
        # Remove logs
        $logsPath = Join-Path $componentPath "logs"
        if (Test-Path $logsPath) {
            Write-Host "  Removing logs..." -ForegroundColor Yellow
            Remove-Item -Path $logsPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Logs removed" -ForegroundColor Green
        }
        
        # Remove .env file
        $envPath = Join-Path $componentPath ".env"
        if (Test-Path $envPath) {
            Write-Host "  Removing .env file..." -ForegroundColor Yellow
            Remove-Item -Path $envPath -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ .env file removed" -ForegroundColor Green
        }
        
        # Remove __pycache__ directories
        $pycacheDirs = Get-ChildItem -Path $componentPath -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
        if ($pycacheDirs) {
            Write-Host "  Removing Python cache..." -ForegroundColor Yellow
            $pycacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Python cache removed" -ForegroundColor Green
        }
        
        # Remove .pytest_cache directories
        $pytestCacheDirs = Get-ChildItem -Path $componentPath -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue
        if ($pytestCacheDirs) {
            Write-Host "  Removing pytest cache..." -ForegroundColor Yellow
            $pytestCacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Pytest cache removed" -ForegroundColor Green
        }
        
        # Remove .egg-info directories
        $eggInfoDirs = Get-ChildItem -Path $componentPath -Recurse -Directory -Filter "*.egg-info" -ErrorAction SilentlyContinue
        if ($eggInfoDirs) {
            Write-Host "  Removing egg-info..." -ForegroundColor Yellow
            $eggInfoDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Egg-info removed" -ForegroundColor Green
        }
        
        Write-Host "✓ $component uninstalled" -ForegroundColor Green
    } else {
        Write-Host "⊙ $component not found" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Remove root-level cache and temp files
Write-Host "→ Cleaning root directory..." -ForegroundColor Cyan

# Remove .pytest_cache
if (Test-Path ".pytest_cache") {
    Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Removed .pytest_cache" -ForegroundColor Green
}

# Remove backup files
$backupFiles = Get-ChildItem -Path $PSScriptRoot -Filter "*_backup_*.zip" -ErrorAction SilentlyContinue
if ($backupFiles) {
    Write-Host "  Found $($backupFiles.Count) backup file(s)" -ForegroundColor Yellow
    if (-not $KeepData) {
        $backupFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Removed backup files" -ForegroundColor Green
    } else {
        Write-Host "  ⊙ Keeping backup files" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Uninstall Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Components uninstalled: $($components.Count)" -ForegroundColor White

if (-not $KeepVenvs) {
    Write-Host "  Virtual environments: Removed" -ForegroundColor White
} else {
    Write-Host "  Virtual environments: Kept" -ForegroundColor White
}

if (-not $KeepData) {
    Write-Host "  Data and databases: Removed" -ForegroundColor White
} else {
    Write-Host "  Data and databases: Kept" -ForegroundColor White
}

Write-Host "  Logs: Removed" -ForegroundColor White
Write-Host "  Configuration files: Removed" -ForegroundColor White
Write-Host "  Cache files: Removed" -ForegroundColor White
Write-Host ""

Write-Host "What remains:" -ForegroundColor Cyan
Write-Host "  - Source code (Python files)" -ForegroundColor White
Write-Host "  - Documentation (*.md files)" -ForegroundColor White
Write-Host "  - Scripts (*.ps1 files)" -ForegroundColor White
Write-Host "  - Requirements files (requirements.txt)" -ForegroundColor White
if ($KeepData) {
    Write-Host "  - Data directories (databases)" -ForegroundColor White
}
if ($KeepVenvs) {
    Write-Host "  - Virtual environments (.venv)" -ForegroundColor White
}
Write-Host ""

Write-Host "To reinstall:" -ForegroundColor Cyan
Write-Host "  .\setup-all.ps1 -QuickSetup" -ForegroundColor White
Write-Host ""
