# Sentinel Quick Start

## Installation

```powershell
cd sentinel
.\setup.ps1
```

## Running Sentinel

### Recommended: Service Mode (Background with Auto-Restart)

```powershell
# Start
.\start-service.ps1

# Stop
.\stop-service.ps1

# Check status
Get-Content sentinel.pid
Get-Process -Id (Get-Content sentinel.pid)
```

### Alternative: Interactive Mode (Visible Window)

```powershell
.\.venv\Scripts\python.exe main.py monitor --interval 5
```

## Checking Logs

```powershell
# View recent activity
Get-Content logs\sentinel.log -Tail 50

# Monitor in real-time
Get-Content logs\sentinel.log -Wait -Tail 20

# Check for errors
Get-Content logs\sentinel.log | Select-String "ERROR"

# View service restarts
Get-Content logs\service.log
```

## Database Status

```powershell
.\.venv\Scripts\python.exe main.py status
```

## Troubleshooting

If Sentinel stops collecting data:

1. **Check logs:**
   ```powershell
   Get-Content logs\sentinel.log -Tail 100
   ```

2. **Restart service:**
   ```powershell
   .\stop-service.ps1
   .\start-service.ps1
   ```

3. **See full guide:**
   - `docs/sentinel/TROUBLESHOOTING.md`
   - `docs/sentinel/USAGE.md`

## Key Features

✅ **Auto-restart** - Automatically recovers from crashes
✅ **File logging** - All activity logged to `logs/sentinel.log`
✅ **Error recovery** - Continues collecting despite individual failures
✅ **Background mode** - Runs hidden, survives window closure
✅ **Easy management** - Simple start/stop scripts

## Configuration

Edit `.env` file:

```bash
# Collection interval (seconds)
COLLECTION_INTERVAL_HIGH=5

# Log level
LOG_LEVEL=INFO

# Database path
DATABASE_PATH=./data/system_stats.db
```

## Next Steps

- View collected data: `.\.venv\Scripts\python.exe main.py history --metric cpu`
- Export data: `.\.venv\Scripts\python.exe main.py export --format json --output data.json`
- See full documentation: `docs/sentinel/USAGE.md`
