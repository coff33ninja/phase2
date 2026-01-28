# Phase 2 Management Scripts

Complete guide to Phase 2 management scripts for easy setup, start, stop, and status checking.

---

## Available Scripts

### 1. setup-all.ps1
**Purpose:** Install and configure all Phase 2 components

**Usage:**
```powershell
# Complete setup (with prompts)
.\setup-all.ps1

# Quick setup (no prompts, skip tests)
.\setup-all.ps1 -QuickSetup

# Skip tests
.\setup-all.ps1 -SkipTests

# Setup specific component only
.\setup-all.ps1 -Component Sentinel
.\setup-all.ps1 -Component Oracle
.\setup-all.ps1 -Component Sage
.\setup-all.ps1 -Component Guardian
.\setup-all.ps1 -Component Nexus
```

**What it does:**
- ✓ Checks prerequisites (Python 3.12, uv)
- ✓ Installs dependencies for each component
- ✓ Installs components in editable mode
- ✓ Creates necessary directories (data, logs)
- ✓ Copies .env.example to .env
- ✓ Runs tests (optional)
- ✓ Provides next steps

---

### 2. start-all.ps1
**Purpose:** Start all Phase 2 components

**Usage:**
```powershell
# Manual start (shows instructions)
.\start-all.ps1

# Background start (runs as jobs)
.\start-all.ps1 -Background

# Start Sentinel only
.\start-all.ps1 -SentinelOnly

# Start Nexus only
.\start-all.ps1 -NexusOnly
```

**What it does:**
- ✓ Starts Sentinel (data collection)
- ✓ Starts Nexus (dashboard)
- ✓ Provides access URLs
- ✓ Shows management commands

**Access Points:**
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### 3. stop-all.ps1
**Purpose:** Stop all running Phase 2 components

**Usage:**
```powershell
# Stop all components
.\stop-all.ps1
```

**What it does:**
- ✓ Stops all background jobs
- ✓ Stops Python processes
- ✓ Stops Uvicorn (Nexus) processes
- ✓ Confirms shutdown

---

### 4. status-all.ps1
**Purpose:** Check status of all Phase 2 components

**Usage:**
```powershell
# Check status
.\status-all.ps1
```

**What it shows:**
- ✓ Installation status
- ✓ Database status
- ✓ Log files
- ✓ Running processes
- ✓ Background jobs

---

## Quick Start Workflow

### First Time Setup

```powershell
# 1. Navigate to Phase 2 directory
cd phases/phase2

# 2. Run complete setup
.\setup-all.ps1

# 3. Configure components (edit .env files)
# Edit sentinel/.env, oracle/.env, sage/.env, guardian/.env, nexus/.env

# 4. Start components
.\start-all.ps1 -Background

# 5. Check status
.\status-all.ps1

# 6. Access dashboard
start http://localhost:8000
```

### Daily Usage

```powershell
# Start components
.\start-all.ps1 -Background

# Check status
.\status-all.ps1

# Stop components
.\stop-all.ps1
```

---

## Script Details

### setup-all.ps1 Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-SkipTests` | Switch | Skip running tests during setup |
| `-QuickSetup` | Switch | Skip prompts and tests |
| `-Component` | String | Setup specific component only |

**Examples:**
```powershell
# Interactive setup with tests
.\setup-all.ps1

# Fast setup without prompts
.\setup-all.ps1 -QuickSetup

# Setup without tests
.\setup-all.ps1 -SkipTests

# Setup Sentinel only
.\setup-all.ps1 -Component Sentinel
```

### start-all.ps1 Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-Background` | Switch | Run components as background jobs |
| `-SentinelOnly` | Switch | Start Sentinel only |
| `-NexusOnly` | Switch | Start Nexus only |

**Examples:**
```powershell
# Manual start (shows instructions)
.\start-all.ps1

# Background start
.\start-all.ps1 -Background

# Sentinel only
.\start-all.ps1 -SentinelOnly -Background
```

---

## Background Job Management

When using `-Background` flag, components run as PowerShell jobs.

### View Jobs
```powershell
# List all jobs
Get-Job

# View job output
Receive-Job -Id <job-id>

# View latest output
Receive-Job -Id <job-id> -Keep
```

### Stop Jobs
```powershell
# Stop specific job
Stop-Job -Id <job-id>

# Stop all jobs
Get-Job | Stop-Job

# Remove stopped jobs
Get-Job | Remove-Job
```

### Monitor Jobs
```powershell
# Watch job status
while ($true) {
    Clear-Host
    Get-Job | Format-Table -AutoSize
    Start-Sleep -Seconds 2
}
```

---

## Troubleshooting

### Script Won't Run

**Problem:** Execution policy prevents script

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\setup-all.ps1
```

### Setup Fails

**Problem:** Component installation fails

**Solution:**
```powershell
# Check prerequisites
python --version  # Should be 3.12.x
uv --version      # Should be installed

# Try manual setup
cd <component>
.\setup.ps1
```

### Components Won't Start

**Problem:** Start script fails

**Solution:**
```powershell
# Check if already running
.\status-all.ps1

# Stop existing processes
.\stop-all.ps1

# Try manual start
cd sentinel
python main.py collect
```

### Port Already in Use

**Problem:** Nexus port 8000 in use

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <pid> /F

# Or use different port
cd nexus
python main.py --port 8080
```

---

## Advanced Usage

### Custom Setup

```powershell
# Setup with custom options
.\setup-all.ps1 -SkipTests -Component Sentinel

# Then manually configure
cd sentinel
notepad .env

# Test manually
pytest tests/ -v
```

### Selective Start

```powershell
# Start only what you need
.\start-all.ps1 -SentinelOnly -Background

# Later, start Nexus
cd nexus
python main.py
```

### Development Mode

```powershell
# Setup for development
.\setup-all.ps1 -SkipTests

# Start with auto-reload
cd nexus
python main.py --reload
```

### Production Mode

```powershell
# Setup for production
.\setup-all.ps1 -QuickSetup

# Configure for production
# Edit .env files:
# - Set LOG_LEVEL=WARNING
# - Set RELOAD=false
# - Configure proper paths

# Start in background
.\start-all.ps1 -Background
```

---

## Maintenance Scripts

### Backup Data

```powershell
# Create backup
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path */data/*.db -DestinationPath "backup_$date.zip"
```

### Clean Logs

```powershell
# Remove old logs (30+ days)
Get-ChildItem -Path */logs/*.log -Recurse | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item
```

### Update Components

```powershell
# Update all components
foreach ($comp in @("sentinel", "oracle", "sage", "guardian", "nexus")) {
    cd $comp
    uv pip install --upgrade -r requirements.txt
    uv pip install -e .
    cd ..
}
```

### Reset Component

```powershell
# Reset specific component
$comp = "sentinel"
cd $comp
Remove-Item -Recurse -Force data, logs
uv pip uninstall $comp
uv pip install -e .
cd ..
```

---

## Script Customization

### Modify Setup Script

Edit `setup-all.ps1` to customize:
- Component order
- Default parameters
- Additional checks
- Post-install actions

### Modify Start Script

Edit `start-all.ps1` to customize:
- Startup order
- Default parameters
- Additional components
- Startup delays

### Create Custom Script

```powershell
# Example: Start with custom config
param([string]$Profile = "default")

Write-Host "Starting with profile: $Profile"

# Load profile-specific settings
$config = Get-Content "profiles/$Profile.json" | ConvertFrom-Json

# Start components with custom settings
cd sentinel
python main.py collect --interval $config.sentinel.interval

cd ../nexus
python main.py --port $config.nexus.port
```

---

## Best Practices

1. **Always run setup-all.ps1 first** - Ensures all components are properly installed

2. **Use -Background for production** - Keeps components running in background

3. **Check status regularly** - Use status-all.ps1 to monitor health

4. **Stop cleanly** - Always use stop-all.ps1 before shutdown

5. **Backup before updates** - Backup data before running updates

6. **Test after setup** - Run tests to verify installation

7. **Monitor logs** - Check logs for errors and warnings

8. **Use version control** - Keep scripts in git for tracking changes

---

## Quick Reference

```powershell
# Setup
.\setup-all.ps1                    # Full setup
.\setup-all.ps1 -QuickSetup        # Fast setup
.\setup-all.ps1 -Component Nexus   # One component

# Start
.\start-all.ps1                    # Manual start
.\start-all.ps1 -Background        # Background start
.\start-all.ps1 -SentinelOnly      # Sentinel only

# Stop
.\stop-all.ps1                     # Stop all

# Status
.\status-all.ps1                   # Check status

# Jobs
Get-Job                            # List jobs
Receive-Job -Id 1                  # View output
Stop-Job -Id 1                     # Stop job
Get-Job | Remove-Job               # Clean up
```

---

**Last Updated:** January 28, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
