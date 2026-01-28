# Phase 2.1 Foundation - Usage Guide

## Quick Start

### 1. Setup Environment

```powershell
# Navigate to project directory
cd phases/phase2/phase2.1-foundation

# Run setup script (creates venv and installs dependencies)
.\setup.ps1
```

### 2. Activate Virtual Environment

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

### 3. Configure (Optional)

Copy `.env.example` to `.env` and customize:

```powershell
copy .env.example .env
notepad .env
```

## CLI Commands

### Collect Data Once

Collect system metrics once and display:

```powershell
python main.py collect
```

### Continuous Monitoring

Monitor system metrics in real-time:

```powershell
# Monitor with default 1-second interval
python main.py monitor

# Monitor with custom interval
python main.py monitor --interval 5

# Monitor for specific duration (60 seconds)
python main.py monitor --duration 60
```

### View Status

Show database statistics:

```powershell
python main.py status
```

### View History

View historical data for specific metrics:

```powershell
# View CPU history (last 24 hours)
python main.py history --metric cpu

# View RAM history (last 12 hours)
python main.py history --metric ram --hours 12

# Available metrics:
# - cpu
# - ram
# - disk_read
# - network_download
```

### Export Data

Export collected data to file:

```powershell
# Export to JSON
python main.py export --format json --output data.json

# Export to CSV
python main.py export --format csv --output data.csv

# Export specific time range
python main.py export --format json --output data.json --hours 48
```

## Python API Usage

### Basic Collection

```python
import asyncio
from config import Config
from aggregator import Pipeline

async def main():
    # Load configuration
    config = Config.load()
    
    # Create pipeline
    pipeline = Pipeline(config)
    
    # Initialize
    await pipeline.initialize()
    
    try:
        # Collect once
        snapshot = await pipeline.collect_once()
        print(f"CPU: {snapshot.cpu.usage_percent}%")
        print(f"RAM: {snapshot.ram.usage_percent}%")
        
        # Store in database
        snapshot_id = await pipeline.collect_and_store()
        print(f"Saved with ID: {snapshot_id}")
    
    finally:
        await pipeline.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
```

### Continuous Collection

```python
import asyncio
from config import Config
from aggregator import Pipeline

async def main():
    config = Config.load()
    pipeline = Pipeline(config)
    
    await pipeline.initialize()
    
    try:
        # Start continuous collection (runs in background)
        await pipeline.start()
        
        # Keep running
        while True:
            await asyncio.sleep(10)
            stats = await pipeline.get_statistics()
            print(f"Total snapshots: {stats['total_snapshots']}")
    
    except KeyboardInterrupt:
        print("Stopping...")
    
    finally:
        await pipeline.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
```

### Using Individual Collectors

```python
import asyncio
from collectors import CPUCollector, RAMCollector

async def main():
    cpu = CPUCollector()
    ram = RAMCollector()
    
    # Collect CPU metrics
    cpu_metrics = await cpu.collect()
    print(f"CPU Usage: {cpu_metrics.usage_percent}%")
    print(f"CPU Frequency: {cpu_metrics.frequency_mhz} MHz")
    
    # Collect RAM metrics
    ram_metrics = await ram.collect()
    print(f"RAM Usage: {ram_metrics.usage_percent}%")
    print(f"RAM Available: {ram_metrics.available_gb} GB")

if __name__ == '__main__':
    asyncio.run(main())
```

### Database Queries

```python
import asyncio
from config import Config
from storage import Database, Repository

async def main():
    config = Config.load()
    db = Database(config.storage.database_path)
    repo = Repository(db)
    
    await db.connect()
    
    try:
        # Get recent snapshots
        snapshots = await repo.get_recent_snapshots(limit=10)
        for snap in snapshots:
            print(f"{snap['timestamp']}: CPU={snap['cpu_usage']}%")
        
        # Get metric history
        history = await repo.get_metric_history('cpu', hours=24)
        print(f"Got {len(history)} data points")
        
        # Get statistics
        stats = await repo.get_statistics()
        print(f"Database size: {stats['database_size_mb']} MB")
    
    finally:
        await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

## Configuration Options

### Environment Variables

Edit `.env` file:

```bash
# Collection Intervals (seconds)
COLLECTION_INTERVAL_HIGH=1
COLLECTION_INTERVAL_MEDIUM=5
COLLECTION_INTERVAL_LOW=30
COLLECTION_INTERVAL_VERY_LOW=300

# Storage
DATABASE_PATH=./data/system_stats.db
DATA_RETENTION_DAYS=90

# Privacy
SEND_TO_GEMINI=false
ANONYMIZE_DATA=true

# System
LOG_LEVEL=INFO
MAX_CPU_OVERHEAD=2.0
MAX_RAM_MB=500

# Gemini (for Phase 2.3)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Programmatic Configuration

```python
from config import Config, CollectionIntervals, StorageConfig

# Create custom configuration
config = Config(
    intervals=CollectionIntervals(
        high_frequency=2,  # 2 seconds
        medium_frequency=10
    ),
    storage=StorageConfig(
        database_path=Path("./custom_data/metrics.db"),
        data_retention_days=30
    )
)

# Initialize
config.initialize()
```

## Common Use Cases

### 1. Performance Monitoring

Monitor system performance during application testing:

```powershell
# Start monitoring
python main.py monitor --interval 1 --duration 300

# In another terminal, run your application
# ...

# After 5 minutes, view the data
python main.py history --metric cpu --hours 1
```

### 2. Resource Usage Analysis

Analyze resource usage patterns:

```python
import asyncio
from config import Config
from storage import Database, Repository

async def analyze():
    config = Config.load()
    db = Database(config.storage.database_path)
    repo = Repository(db)
    
    await db.connect()
    
    # Get CPU history
    cpu_data = await repo.get_metric_history('cpu', hours=24)
    
    # Calculate statistics
    values = [d['value'] for d in cpu_data]
    avg_cpu = sum(values) / len(values)
    max_cpu = max(values)
    
    print(f"Average CPU: {avg_cpu:.1f}%")
    print(f"Peak CPU: {max_cpu:.1f}%")
    
    await db.disconnect()

asyncio.run(analyze())
```

### 3. Automated Data Collection

Run as a background service:

```python
# service.py
import asyncio
from config import Config
from aggregator import Pipeline
from utils.logger import setup_logger

async def main():
    # Setup logging
    setup_logger(log_level="INFO", log_file=Path("./logs/collector.log"))
    
    config = Config.load()
    pipeline = Pipeline(config)
    
    await pipeline.start()
    
    # Run forever
    try:
        while True:
            await asyncio.sleep(3600)  # Check every hour
            
            # Cleanup old data
            await pipeline.database.cleanup_old_data(
                config.storage.data_retention_days
            )
    
    except KeyboardInterrupt:
        pass
    
    finally:
        await pipeline.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
```

## Troubleshooting

### Issue: Import Errors

**Solution**: Ensure virtual environment is activated and dependencies are installed:

```powershell
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### Issue: GPU Metrics Not Available

**Solution**: Install GPU tools:
- NVIDIA: Install NVIDIA drivers and nvidia-smi
- AMD: Install ROCm and rocm-smi
- Or install GPUtil: `uv pip install GPUtil`

### Issue: Permission Denied for Network Connections

**Solution**: Run with administrator privileges or disable network connection counting in code.

### Issue: Database Locked

**Solution**: Ensure only one instance is writing to the database at a time.

## Performance Tips

1. **Adjust Collection Interval**: Higher intervals = lower overhead
2. **Disable Unused Collectors**: Modify pipeline.py to skip collectors you don't need
3. **Regular Cleanup**: Run cleanup_old_data() periodically
4. **Vacuum Database**: Run `database.vacuum()` monthly to optimize storage

## Next Steps

- Phase 2.2: Add local ML model for pattern detection
- Phase 2.3: Integrate Gemini 2.5 Flash for AI insights
- Phase 2.4: Build real-time dashboard
- Phase 2.5: Add auto-tuning capabilities

## Support

For issues or questions:
1. Check TROUBLESHOOTING.md
2. Review IMPLEMENTATION_CHECKLIST.md for known limitations
3. Check logs in `./logs/` directory
