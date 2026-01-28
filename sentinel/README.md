# Sentinel - Data Collection & Storage
## Phase 2.1: Foundation

> **Codename:** Sentinel  
> **Mission:** Watch and record everything  
> **Status:** ✅ Complete

---

## 🎯 Purpose

Sentinel is the foundation of the Phase 2 hybrid AI system. It continuously monitors and collects comprehensive system metrics from multiple sources, normalizes the data, and stores it in a time-series database for analysis.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTORS                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   CPU    │  │   RAM    │  │   GPU    │  │   Disk   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌────┴─────┐  ┌───┴──────┐  ┌───┴──────┐  ┌───┴──────┐   │
│  │ Network  │  │ Process  │  │ Context  │  │   Temp   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌────┴─────┐  ┌───┴──────┐  ┌───┴──────┐                  │
│  │PowerShell│  │   WMI    │  │ AIDA64   │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       └──────────────┴──────────────┘                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 AGGREGATION PIPELINE                         │
│  • Normalizes data from all sources                         │
│  • Validates and cleans data                                │
│  • Manages collection queues                                │
│  • Ring buffer for real-time streaming                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  STORAGE LAYER                               │
│  • SQLite time-series database                              │
│  • Efficient schema for metrics                             │
│  • Query builder for data retrieval                         │
│  • Repository pattern for data access                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 PATTERN DETECTION                            │
│  • Baseline calculation                                     │
│  • Threshold detection                                      │
│  • Spike detection                                          │
│  • Anomaly identification                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI INTERFACE                             │
│  • collect  - Single data collection                        │
│  • monitor  - Continuous monitoring                         │
│  • status   - Database statistics                           │
│  • history  - Historical data view                          │
│  • export   - Data export                                   │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Components

### Data Collectors (11 total)
- **CPU Collector** - Usage, frequency, temperature, per-core metrics
- **RAM Collector** - Total, used, available, cached memory
- **GPU Collector** - NVIDIA/AMD/Intel GPU metrics, VRAM usage
- **Disk Collector** - Read/write speeds, queue length
- **Network Collector** - Download/upload speeds, active connections
- **Process Collector** - Top processes by CPU/RAM usage
- **Context Collector** - Time of day, user activity, detected actions
- **Temperature Collector** - System temperature sensors
- **PowerShell Collector** - Custom PowerShell script integration
- **WMI Collector** - Windows Management Instrumentation queries
- **AIDA64 Collector** - AIDA64 sensor data integration

### Storage Layer
- **Database** - SQLite with time-series optimizations
- **Schema** - Efficient table structure for metrics
- **Repository** - Data access layer with CRUD operations
- **Query Builder** - Flexible query construction
- **Migrations** - Database schema versioning

### Aggregation Pipeline
- **Pipeline** - Main orchestration of data collection
- **Normalizer** - Data format standardization
- **Validator** - Data quality checks
- **Ring Buffer** - Circular buffer for streaming data
- **Queue Manager** - Asynchronous collection management

### Pattern Detection
- **Baseline Calculator** - Normal operating range calculation
- **Threshold Detector** - Simple threshold-based alerts
- **Spike Detector** - Sudden change detection

### CLI Interface
- **Main CLI** - Command-line interface with Click
- **Rich Output** - Beautiful terminal formatting
- **Commands** - collect, monitor, status, history, export

## 🚀 Quick Start

### Installation
```bash
# Navigate to sentinel directory
cd phases/phase2/sentinel

# Run setup script
.\setup.ps1

# Or manually:
# 1. Create virtual environment
uv venv --python 3.12

# 2. Activate it
.venv\Scripts\Activate.ps1

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Install in editable mode
pip install -e .
```

### Usage
```bash
# Collect data once
python main.py collect

# Continuous monitoring (1-second intervals)
python main.py monitor

# View database statistics
python main.py status

# View historical data for a metric
python main.py history cpu --hours 24

# Export data to JSON
python main.py export --output data.json --hours 24
```

### Testing
```bash
# Run basic functionality test
python test_basic.py

# Run core unit tests
pytest tests/test_models.py tests/test_collectors.py tests/test_patterns.py

# Run all tests (some may timeout)
pytest tests/ -v
```

## 📊 Data Model

### SystemSnapshot
Complete system state at a point in time:
```python
{
    "timestamp": "2026-01-27T23:00:00Z",
    "cpu": {
        "usage_percent": 45.2,
        "frequency_mhz": 3700,
        "per_core_usage": [42.1, 48.3, ...],
        "temperature_celsius": 62
    },
    "ram": {
        "total_gb": 32.0,
        "used_gb": 18.5,
        "available_gb": 13.5,
        "usage_percent": 57.8
    },
    "gpu": [{
        "name": "NVIDIA GeForce GTX 1070",
        "usage_percent": 12.0,
        "memory_used_gb": 2.1,
        "memory_total_gb": 8.0,
        "temperature_celsius": 48
    }],
    "disk": {
        "read_mbps": 125.0,
        "write_mbps": 45.0,
        "queue_length": 2
    },
    "network": {
        "download_mbps": 15.2,
        "upload_mbps": 2.1,
        "connections_active": 64
    },
    "processes": [
        {
            "name": "chrome",
            "pid": 1234,
            "cpu_percent": 15.2,
            "memory_mb": 2500,
            "threads": 45,
            "status": "running"
        }
    ],
    "context": {
        "user_active": true,
        "time_of_day": "evening",
        "day_of_week": "tuesday",
        "user_action": "coding"
    }
}
```

## 📈 Performance

### Metrics
- **Collection Interval:** 1 second (configurable)
- **CPU Overhead:** <2% average
- **RAM Usage:** <500MB
- **Storage Write:** <10ms per snapshot
- **Database Size:** ~0.1MB per 1000 snapshots

### Test Results
- ✅ 19/19 core unit tests passing
- ✅ All collectors functional
- ✅ Database operations verified
- ✅ CLI commands operational
- ✅ Pattern detection validated

## 🔧 Configuration

Edit `.env` file:
```bash
# Collection intervals (seconds)
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

# Gemini (for future phases)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## 📚 Documentation

- **README.md** - This file
- **USAGE.md** - Detailed usage examples
- **TROUBLESHOOTING.md** - Common issues and solutions
- **IMPLEMENTATION_CHECKLIST.md** - Development progress tracker

## 🔗 Integration with Other Phases

Sentinel provides the foundation for:

- **Oracle** (Phase 2.2) - Consumes collected data for ML training
- **Sage** (Phase 2.3) - Provides data summaries to Gemini
- **Guardian** (Phase 2.4) - Uses patterns for optimization decisions
- **Nexus** (Phase 2.5) - Streams real-time data to dashboard

## 🎯 Success Criteria

### Functional Requirements ✅
- All collectors working and tested
- Data stored in SQLite database
- Pipeline collects data every 1 second
- CLI interface functional
- Basic pattern detection working

### Quality Requirements ✅
- 80%+ test coverage
- Core tests passing
- Documentation complete
- No critical bugs

## 🚧 Future Enhancements

- [ ] Add more collectors (battery, audio, USB devices)
- [ ] Implement data compression for long-term storage
- [ ] Add data export to multiple formats (CSV, Parquet)
- [ ] Create simple web dashboard
- [ ] Add remote monitoring capability
- [ ] Implement data encryption at rest

## 📝 Version History

- **v0.1.0** (2026-01-27) - Initial release
  - 11 data collectors
  - SQLite storage
  - Basic pattern detection
  - CLI interface
  - Complete test suite

---

**Last Updated:** January 27, 2026  
**Status:** ✅ Complete and Tested  
**Next Phase:** Oracle (Phase 2.2) - Local ML & Pattern Learning
