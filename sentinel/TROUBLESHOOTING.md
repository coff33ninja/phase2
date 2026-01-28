# Troubleshooting Guide

## Installation Issues

### Problem: `uv` command not found

**Symptoms:**
```
'uv' is not recognized as an internal or external command
```

**Solution:**
1. Install uv from https://docs.astral.sh/uv/
2. For Windows with Python installed:
   ```powershell
   pip install uv
   ```
3. Or use the standalone installer from the uv website

### Problem: Python 3.12 not found

**Symptoms:**
```
Python 3.12 not found
```

**Solution:**
```powershell
# Install Python 3.12 using uv
uv python install 3.12

# Or download from python.org
```

### Problem: Virtual environment activation fails

**Symptoms:**
```
Execution of scripts is disabled on this system
```

**Solution (Windows PowerShell):**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.venv\Scripts\Activate.ps1
```

## Runtime Issues

### Problem: Import errors after installation

**Symptoms:**
```python
ModuleNotFoundError: No module named 'psutil'
```

**Solution:**
```powershell
# Ensure venv is activated
.venv\Scripts\Activate.ps1

# Reinstall dependencies
uv pip install -r requirements.txt
```

### Problem: GPU metrics not available

**Symptoms:**
```
No GPU detected or GPU tools not available
```

**Solutions:**

**For NVIDIA GPUs:**
1. Install NVIDIA drivers
2. Verify nvidia-smi works:
   ```powershell
   nvidia-smi
   ```

**For AMD GPUs:**
1. Install ROCm
2. Verify rocm-smi works

**Fallback:**
```powershell
# Install GPUtil as fallback
uv pip install GPUtil
```

### Problem: Permission denied for network connections

**Symptoms:**
```
PermissionError: [WinError 5] Access is denied
```

**Solution:**
Run PowerShell as Administrator, or modify `network_collector.py` to skip connection counting:

```python
def _count_connections(self) -> int:
    try:
        # ... existing code ...
    except (psutil.AccessDenied, Exception):
        return 0  # Return 0 instead of raising
```

### Problem: Database locked error

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
1. Ensure only one instance is running
2. Close any database browsers
3. Delete the database file and restart:
   ```powershell
   Remove-Item data\system_stats.db
   python main.py collect
   ```

### Problem: High CPU usage

**Symptoms:**
- System becomes slow
- CPU usage > 5%

**Solutions:**
1. Increase collection interval:
   ```python
   # In .env
   COLLECTION_INTERVAL_HIGH=5  # Instead of 1
   ```

2. Disable unused collectors:
   ```python
   # In aggregator/pipeline.py
   # Comment out collectors you don't need
   # self.gpu_collector = GPUCollector()
   ```

3. Reduce process collector count:
   ```python
   self.process_collector = ProcessCollector(top_n=5)  # Instead of 10
   ```

## Data Issues

### Problem: No data in database

**Symptoms:**
```
Total snapshots: 0
```

**Solution:**
1. Check if collection is running:
   ```powershell
   python main.py status
   ```

2. Try manual collection:
   ```powershell
   python main.py collect
   ```

3. Check logs for errors:
   ```powershell
   # Enable debug logging
   python main.py --log-level DEBUG collect
   ```

### Problem: Incorrect metric values

**Symptoms:**
- CPU always 0%
- RAM values don't make sense

**Solution:**
1. Run test script:
   ```powershell
   python test_basic.py
   ```

2. Check psutil installation:
   ```powershell
   python -c "import psutil; print(psutil.cpu_percent())"
   ```

3. Reinstall psutil:
   ```powershell
   uv pip uninstall psutil
   uv pip install psutil
   ```

## CLI Issues

### Problem: CLI commands not working

**Symptoms:**
```
Error: No such command 'monitor'
```

**Solution:**
1. Ensure you're in the correct directory:
   ```powershell
   cd phases\phase2\phase2.1-foundation
   ```

2. Run with python explicitly:
   ```powershell
   python main.py monitor
   ```

3. Check click installation:
   ```powershell
   uv pip install click rich
   ```

### Problem: Display issues in terminal

**Symptoms:**
- Garbled output
- Colors not showing

**Solution:**
1. Use Windows Terminal instead of CMD
2. Or disable colors:
   ```python
   # In cli/main.py
   console = Console(force_terminal=False)
   ```

## Performance Issues

### Problem: Slow data collection

**Symptoms:**
- Collection takes > 1 second
- System feels sluggish

**Solutions:**
1. Profile the collectors:
   ```python
   import time
   start = time.time()
   await collector.collect()
   print(f"Time: {time.time() - start}")
   ```

2. Disable slow collectors temporarily

3. Check disk I/O:
   - Move database to SSD
   - Reduce write frequency

### Problem: Database growing too large

**Symptoms:**
- Database > 1GB
- Queries slow

**Solutions:**
1. Run cleanup:
   ```python
   from storage import Database
   from config import Config
   
   config = Config.load()
   db = Database(config.storage.database_path)
   await db.connect()
   await db.cleanup_old_data(30)  # Keep only 30 days
   await db.vacuum()
   ```

2. Adjust retention in `.env`:
   ```
   DATA_RETENTION_DAYS=30
   ```

## Testing Issues

### Problem: Tests failing

**Symptoms:**
```
FAILED tests/test_collectors.py::test_cpu_collector
```

**Solution:**
1. Install test dependencies:
   ```powershell
   uv pip install pytest pytest-asyncio
   ```

2. Run tests with verbose output:
   ```powershell
   pytest -v
   ```

3. Run specific test:
   ```powershell
   pytest tests/test_collectors.py::test_cpu_collector -v
   ```

## Common Error Messages

### `AttributeError: module 'psutil' has no attribute 'sensors_temperatures'`

**Cause:** Windows doesn't support temperature sensors through psutil

**Solution:** This is expected on Windows. Temperature will be None.

### `ImportError: cannot import name 'BaseCollector'`

**Cause:** Python path issue

**Solution:**
```powershell
# Run from project root
cd phases\phase2\phase2.1-foundation
python main.py collect
```

### `pydantic.ValidationError`

**Cause:** Invalid data in models

**Solution:** Check the error message for which field is invalid and fix the data source.

## Getting Help

If you're still stuck:

1. Check the logs:
   ```powershell
   # Look in logs/ directory if logging to file
   # Or run with debug level
   python main.py --log-level DEBUG collect
   ```

2. Run the basic test:
   ```powershell
   python test_basic.py
   ```

3. Check system requirements:
   - Python 3.12+
   - Windows 10/11
   - 500MB free RAM
   - 1GB free disk space

4. Review the implementation checklist:
   - See IMPLEMENTATION_CHECKLIST.md for known limitations

## Known Limitations

1. **Temperature sensors:** Not available on all systems
2. **GPU metrics:** Requires vendor-specific tools
3. **Network connections:** May require admin privileges
4. **Process details:** Some processes may be inaccessible
5. **AMD GPU support:** Limited compared to NVIDIA

## Tips for Smooth Operation

1. **Start simple:** Begin with `collect` command before `monitor`
2. **Check status regularly:** Use `status` command to verify operation
3. **Monitor resources:** Keep an eye on CPU/RAM usage
4. **Regular cleanup:** Run cleanup monthly
5. **Backup data:** Export important data regularly
