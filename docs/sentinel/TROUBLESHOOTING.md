# Sentinel Troubleshooting Guide

## Common Issues

### Sentinel Stops Collecting Data

**Symptoms:**
- Database stops updating
- No new snapshots in `sentinel/data/system_stats.db`
- Process not visible in Task Manager

**Root Causes:**
1. Process crashed due to unhandled exception
2. User closed the console window
3. System resource constraints
4. Database corruption

**Solutions:**

1. **Check the logs:**
   ```powershell
   # View recent logs
   Get-Content sentinel\logs\sentinel.log -Tail 50
   ```

2. **Use the service mode with auto-restart:**
   ```powershell
   cd sentinel
   .\start-service.ps1
   ```
   This will automatically restart Sentinel if it crashes.

3. **Check database status:**
   ```powershell
   cd sentinel
   .\.venv\Scripts\python.exe main.py status
   ```

4. **Verify process is running:**
   ```powershell
   # Check if sentinel.pid exists
   Get-Content sentinel\sentinel.pid
   
   # Check if process is running
   Get-Process -Id (Get-Content sentinel\sentinel.pid)
   ```

### No Log Files Created

**Symptoms:**
- `sentinel/logs/` directory is empty
- Can't diagnose crashes

**Solution:**
The latest version now creates log files automatically. If you're running an older version:

1. Stop Sentinel
2. Pull latest changes
3. Restart Sentinel - logs will now be created at `sentinel/logs/sentinel.log`

### High CPU Usage

**Symptoms:**
- Sentinel uses more than 2% CPU consistently
- System feels sluggish

**Solutions:**

1. **Increase collection interval:**
   Edit `sentinel/.env`:
   ```
   COLLECTION_INTERVAL_HIGH=5  # Change from 1 to 5 seconds
   ```

2. **Check for collector issues:**
   ```powershell
   # View logs for errors
   Get-Content sentinel\logs\sentinel.log | Select-String "ERROR"
   ```

3. **Disable optional collectors:**
   Edit `sentinel/.env`:
   ```
   ENABLE_AIDA64=false
   ENABLE_HWINFO=false
   ```

### Database Locked Errors

**Symptoms:**
- "Database is locked" errors in logs
- Failed to save snapshots

**Solutions:**

1. **Check for multiple Sentinel instances:**
   ```powershell
   Get-Process python | Where-Object {$_.CommandLine -like "*sentinel*"}
   ```

2. **Stop all instances and restart:**
   ```powershell
   cd sentinel
   .\stop-service.ps1
   Start-Sleep -Seconds 2
   .\start-service.ps1
   ```

3. **If database is corrupted, backup and recreate:**
   ```powershell
   cd sentinel\data
   Copy-Item system_stats.db system_stats.db.backup
   Remove-Item system_stats.db
   # Restart Sentinel - it will create a new database
   ```

### Memory Leaks

**Symptoms:**
- Sentinel memory usage grows over time
- Eventually crashes or slows down

**Solutions:**

1. **Check current memory usage:**
   ```powershell
   Get-Process python | Where-Object {$_.CommandLine -like "*sentinel*"} | Select-Object WorkingSet64
   ```

2. **Restart Sentinel daily:**
   Use Windows Task Scheduler to restart Sentinel once per day:
   ```powershell
   # Stop
   cd sentinel
   .\stop-service.ps1
   
   # Wait
   Start-Sleep -Seconds 5
   
   # Start
   .\start-service.ps1
   ```

3. **Report the issue:**
   Include logs and memory usage patterns in your bug report.

## Service Management

### Starting Sentinel as a Service

**Recommended method** (with auto-restart):
```powershell
cd sentinel
.\start-service.ps1
```

**Options:**
```powershell
# Custom interval
.\start-service.ps1 -Interval 1

# Disable auto-restart
.\start-service.ps1 -NoRestart
```

### Stopping the Service

```powershell
cd sentinel
.\stop-service.ps1
```

### Checking Service Status

```powershell
# Check if running
Get-Content sentinel\sentinel.pid
Get-Process -Id (Get-Content sentinel\sentinel.pid)

# View recent activity
Get-Content sentinel\logs\sentinel.log -Tail 20

# Database statistics
cd sentinel
.\.venv\Scripts\python.exe main.py status
```

## Log Analysis

### View Recent Errors

```powershell
Get-Content sentinel\logs\sentinel.log | Select-String "ERROR" -Context 2
```

### View Critical Issues

```powershell
Get-Content sentinel\logs\sentinel.log | Select-String "CRITICAL" -Context 5
```

### Monitor Logs in Real-Time

```powershell
Get-Content sentinel\logs\sentinel.log -Wait -Tail 20
```

### Check for Crashes

```powershell
Get-Content sentinel\logs\service.log
```

## Performance Tuning

### Reduce Resource Usage

1. **Increase collection interval:**
   ```
   COLLECTION_INTERVAL_HIGH=5  # Default: 1
   ```

2. **Reduce process monitoring:**
   Edit `sentinel/collectors/process_collector.py` to reduce `top_n` parameter

3. **Disable GPU monitoring if not needed:**
   Comment out GPU collector in `sentinel/aggregator/pipeline.py`

### Optimize Database

```powershell
cd sentinel
.\.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('data/system_stats.db'); conn.execute('VACUUM'); conn.close()"
```

## Getting Help

If you're still experiencing issues:

1. **Collect diagnostic information:**
   ```powershell
   # System info
   systeminfo
   
   # Python version
   cd sentinel
   .\.venv\Scripts\python.exe --version
   
   # Package versions
   .\.venv\Scripts\pip.exe list
   
   # Recent logs
   Get-Content logs\sentinel.log -Tail 100
   ```

2. **Check documentation:**
   - `docs/sentinel/README.md` - Overview
   - `docs/sentinel/USAGE.md` - Usage guide
   - `docs/README.md` - General documentation

3. **Report the issue:**
   Include all diagnostic information and steps to reproduce.
