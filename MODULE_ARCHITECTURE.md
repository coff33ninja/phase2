# Module Architecture Documentation

Complete architectural overview of the Phase 2 hybrid AI system.

---

## System Overview

Phase 2 is a **hybrid AI system** combining:
- **Local ML** (TensorFlow/Oracle) for pattern learning and predictions
- **Cloud AI** (Google Gemini 2.5 Flash/Sage) for natural language insights
- **Real-time monitoring** (Sentinel) for data collection
- **Auto-tuning** (Guardian) for system optimization
- **Web interface** (Nexus) for user interaction

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │   Terminal   │  │   Scripts    │          │
│  │ (Dashboard)  │  │    (CLI)     │  │ (Automation) │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NEXUS (Port 8001)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Server                         │  │
│  │  • Web Dashboard (HTML/CSS/JS)                           │  │
│  │  • REST API Endpoints                                    │  │
│  │  • WebSocket Streaming (disabled)                        │  │
│  │  • CORS Configuration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Chat API    │  │ Metrics API  │  │ Control API  │         │
│  │ /api/chat/*  │  │/api/metrics/*│  │/api/control/*│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     Sage     │  │   Sentinel   │  │   Guardian   │         │
│  │  Connector   │  │  Connector   │  │  Connector   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE SERVICES                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    SENTINEL                             │    │
│  │  Data Collection & Storage                             │    │
│  │  • 11 Collectors (CPU, RAM, GPU, etc.)                │    │
│  │  • SQLite Time-Series Database                        │    │
│  │  • Aggregation Pipeline                               │    │
│  │  • Pattern Detection                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                     ORACLE                              │    │
│  │  Local ML & Pattern Learning                           │    │
│  │  • TensorFlow 2.20.0                                  │    │
│  │  • LSTM Forecasting                                   │    │
│  │  • Anomaly Detection (Isolation Forest)              │    │
│  │  • Clustering (K-Means)                               │    │
│  │  • Automatic Training (every 24h)                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                      SAGE                               │    │
│  │  AI Assistant (Gemini 2.5 Flash)                      │    │
│  │  • Natural Language Processing                        │    │
│  │  • Context Aggregation                                │    │
│  │  • Conversation Management                            │    │
│  │  • Proactive Insights                                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    GUARDIAN                             │    │
│  │  Auto-Tuning & Optimization                            │    │
│  │  • Profile Management (Gaming, Work, Power Saver)     │    │
│  │  • System Actions (CPU, RAM, GPU tuning)             │    │
│  │  • Safety (Snapshots, Rollback, Validation)          │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Sentinel   │  │    Oracle    │  │     Sage     │         │
│  │  system_     │  │  patterns.db │  │conversations │         │
│  │  stats.db    │  │              │  │  .db         │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sentinel Architecture

### Purpose
Real-time system monitoring and data collection

### Module Structure

```
sentinel/
├── collectors/          # Data collection modules
│   ├── base.py         # Base collector class
│   ├── cpu_collector.py
│   ├── ram_collector.py
│   ├── gpu_collector.py
│   ├── disk_collector.py
│   ├── network_collector.py
│   ├── process_collector.py
│   ├── context_collector.py
│   ├── temperature_collector.py  # ⚠️ Not working
│   ├── powershell_collector.py   # Optional
│   ├── wmi_collector.py          # Optional
│   └── aida64_collector.py       # ✅ Implemented, not integrated
│
├── aggregator/         # Data processing pipeline
│   ├── pipeline.py     # Main orchestration
│   ├── normalizer.py   # Data format standardization
│   ├── validator.py    # Data quality checks
│   ├── ring_buffer.py  # Circular buffer for streaming
│   └── queue_manager.py # Async collection management
│
├── storage/            # Database layer
│   ├── database.py     # SQLite connection management
│   ├── repository.py   # Data access layer (CRUD)
│   ├── query_builder.py # Flexible query construction
│   ├── schema.sql      # Database schema
│   └── migrations.py   # Schema versioning
│
├── patterns/           # Pattern detection
│   ├── baseline.py     # Normal operating range
│   ├── threshold.py    # Simple threshold alerts
│   └── spike_detector.py # Sudden change detection
│
├── cli/                # Command-line interface
│   └── main.py         # CLI commands (collect, monitor, status)
│
├── utils/              # Utilities
│   ├── logger.py       # Logging configuration
│   ├── formatters.py   # Data formatting
│   ├── system_utils.py # System helpers
│   └── time_utils.py   # Time utilities
│
├── config.py           # Configuration management
├── models.py           # Data models (Pydantic)
└── main.py             # Entry point
```

### Data Flow

1. **Collection Phase**
   - Each collector runs asynchronously every 30 seconds
   - Collectors return `Dict[str, Any]` or `None` on failure
   - Failed collectors don't crash the pipeline

2. **Aggregation Phase**
   - Pipeline collects data from all enabled collectors
   - Normalizer standardizes data formats
   - Validator checks data quality and ranges
   - Ring buffer stores recent data for streaming

3. **Storage Phase**
   - Repository saves data to SQLite database
   - Separate tables for each metric type
   - Foreign key relationships via `snapshot_id`
   - Indexes on timestamp for fast queries

4. **Pattern Detection Phase**
   - Baseline calculator determines normal ranges
   - Threshold detector identifies out-of-range values
   - Spike detector finds sudden changes
   - Results stored for Oracle to learn from

### Database Schema

```sql
-- Main snapshot table
CREATE TABLE system_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    context_data TEXT  -- JSON
);

-- Metric tables (linked via snapshot_id)
CREATE TABLE cpu_metrics (
    id INTEGER PRIMARY KEY,
    snapshot_id INTEGER NOT NULL,
    usage_percent REAL,
    frequency_mhz REAL,
    temperature_celsius REAL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id)
);

CREATE TABLE ram_metrics (...);
CREATE TABLE gpu_metrics (...);
CREATE TABLE disk_metrics (...);
CREATE TABLE network_metrics (...);
CREATE TABLE process_info (...);
```

---

## Oracle Architecture

### Purpose
Local machine learning for pattern recognition and prediction

### Module Structure

```
oracle/
├── models/             # ML model implementations
│   ├── base_model.py   # Base model class
│   ├── lstm_forecaster.py  # Time-series prediction
│   ├── anomaly_detector.py # Isolation Forest
│   ├── clustering.py   # K-Means clustering
│   └── classifier.py   # Pattern classification
│
├── training/           # Model training
│   ├── trainer.py      # Training orchestration
│   ├── data_loader.py  # Load data from Sentinel
│   └── feature_engineering.py # Feature extraction
│
├── inference/          # Prediction & analysis
│   ├── predictor.py    # Make predictions
│   ├── pattern_matcher.py # Match patterns
│   ├── confidence_calculator.py # Confidence scores
│   └── explainer.py    # Explain predictions
│
├── patterns/           # Pattern storage
│   ├── usage_patterns.py # Usage pattern storage
│   ├── behavior_profiles.py # User behavior profiles
│   ├── baseline_manager.py # Baseline management
│   └── correlation_matrix.py # Metric correlations
│
├── integration/        # External integrations
│   ├── sentinel_connector.py # Connect to Sentinel DB
│   └── model_scheduler.py # Schedule training runs
│
├── cli/                # Command-line interface
│   └── main.py         # CLI commands (train, predict, status)
│
├── config.py           # Configuration
└── main.py             # Entry point
```

### ML Pipeline

1. **Data Loading**
   - Connects to Sentinel's SQLite database
   - Loads last N snapshots (configurable)
   - Requires minimum 1000 samples for training
   - Currently has ~23 samples (needs 977 more)

2. **Feature Engineering**
   - Extracts features from raw metrics
   - Creates time-based features (hour, day, week)
   - Calculates rolling averages and trends
   - Normalizes values for ML models

3. **Model Training**
   - LSTM: Predicts future resource usage
   - Isolation Forest: Detects anomalies
   - K-Means: Clusters usage patterns
   - Trains every 24 hours automatically

4. **Inference**
   - Makes predictions for next 5, 15, 30, 60 minutes
   - Calculates confidence scores
   - Identifies anomalies in real-time
   - Stores results in patterns.db

5. **Pattern Storage**
   - Learned patterns stored in SQLite
   - Behavior profiles (gaming, work, idle)
   - Baseline metrics for comparison
   - Correlation matrices between metrics

### Models

**LSTM Forecaster:**
- Predicts CPU, RAM, GPU usage
- Horizons: 5, 15, 30, 60 minutes
- Architecture: 2 LSTM layers + Dense output
- Loss: Mean Squared Error

**Anomaly Detector:**
- Isolation Forest algorithm
- Detects unusual system behavior
- Contamination: 0.1 (10% anomalies expected)
- Features: All metrics + time features

**Clustering:**
- K-Means with 5 clusters
- Groups similar usage patterns
- Identifies: Gaming, Work, Idle, Streaming, Heavy Load
- Updates clusters weekly

---

## Sage Architecture

### Purpose
AI assistant for natural language system insights

### Module Structure

```
sage/
├── gemini_client/      # Gemini API integration
│   ├── client.py       # API client (google-genai)
│   ├── rate_limiter.py # Rate limiting
│   ├── token_counter.py # Token usage tracking
│   └── error_handler.py # Error handling & retries
│
├── conversation/       # Conversation management
│   ├── session_manager.py # Session tracking
│   └── intent_classifier.py # Intent detection
│
├── prompts/            # Prompt engineering
│   ├── system_prompt.py # System instructions
│   └── prompt_builder.py # Dynamic prompt construction
│
├── context/            # Context aggregation
│   └── context_aggregator.py # Gather system context
│
├── insights/           # Proactive insights
│   └── proactive_monitor.py # Generate insights
│
├── feedback/           # Learning from feedback
│   ├── feedback_collector.py # Collect user feedback
│   ├── preference_learner.py # Learn preferences
│   └── model_updater.py # Update prompts
│
├── cli/                # Command-line interface
│   └── main.py         # CLI commands (query, chat)
│
├── config.py           # Configuration
└── main.py             # Entry point
```

### Conversation Flow

1. **User Input**
   - User asks question via Nexus chat or CLI
   - Question sent to Sage

2. **Context Gathering**
   - Fetches current system metrics from Sentinel
   - Retrieves learned patterns from Oracle
   - Loads conversation history
   - Aggregates into context string

3. **Prompt Construction**
   - System prompt defines Sage's role
   - Context added (current metrics, patterns)
   - User question appended
   - Sent to Gemini 2.5 Flash

4. **Gemini Processing**
   - Gemini analyzes question + context
   - Generates natural language response
   - Returns insights and recommendations

5. **Response Delivery**
   - Response sent back to user
   - Conversation saved to database
   - Feedback collected (optional)

### Gemini Integration

**Model:** gemini-2.5-flash  
**Context Window:** 1 million tokens  
**Temperature:** 0.7 (balanced creativity)  
**Max Output:** 2048 tokens

**System Prompt:**
```
You are Sage, an AI assistant for system monitoring.
You have access to real-time system metrics and learned patterns.
Provide helpful, concise insights about system performance.
Be proactive in identifying issues and suggesting optimizations.
```

**Example Context:**
```
Current System State:
- CPU: 34.8% @ 3700 MHz
- RAM: 60.9% (19.5 GB / 32 GB)
- GPU: 12% @ 36°C
- Top Process: chrome.exe (15.2% CPU, 2.5 GB RAM)

Learned Patterns:
- Gaming sessions typically start at 7 PM
- CPU usage spikes during video encoding
- RAM usage increases gradually during work hours
```

---

## Guardian Architecture

### Purpose
Automated system optimization and tuning

### Module Structure

```
guardian/
├── profiles/           # Optimization profiles
│   ├── profile_manager.py # Profile management
│   ├── gaming_profile.py  # Gaming optimizations
│   ├── work_profile.py    # Work optimizations
│   ├── power_saver_profile.py # Power saving
│   ├── gaming.yaml        # Gaming config
│   ├── work.yaml          # Work config
│   └── power_saver.yaml   # Power saver config
│
├── actions/            # System actions
│   ├── base_action.py  # Base action class
│   ├── process_actions.py # Process management
│   ├── resource_actions.py # Resource tuning
│   └── system_actions.py # System settings
│
├── execution/          # Action execution
│   ├── executor.py     # Execute actions safely
│   └── logger.py       # Action logging
│
├── safety/             # Safety mechanisms
│   ├── snapshot.py     # System snapshots
│   ├── rollback.py     # Rollback changes
│   └── validator.py    # Validate actions
│
├── integration/        # External integrations
│   ├── sentinel_connector.py # Monitor metrics
│   ├── oracle_connector.py # Get predictions
│   └── sage_connector.py # Get recommendations
│
├── cli/                # Command-line interface
│   └── main.py         # CLI commands (apply, rollback)
│
├── config.py           # Configuration
└── main.py             # Entry point
```

### Optimization Profiles

**Gaming Profile:**
- CPU: High performance mode
- GPU: Maximum performance
- RAM: Clear cache, prioritize game
- Processes: Close background apps
- Network: Prioritize gaming traffic

**Work Profile:**
- CPU: Balanced mode
- RAM: Moderate cache
- Processes: Keep productivity apps
- Network: Normal priority

**Power Saver Profile:**
- CPU: Power saving mode
- GPU: Minimum performance
- Display: Reduce brightness
- Processes: Close unnecessary apps

### Action Types

**Process Actions:**
- Kill process by name/PID
- Set process priority
- Set CPU affinity
- Limit process memory

**Resource Actions:**
- Clear RAM cache
- Defragment memory
- Adjust page file
- Clear temp files

**System Actions:**
- Set power plan
- Adjust CPU frequency
- Set GPU performance mode
- Configure network QoS

### Safety Mechanisms

**Snapshots:**
- Capture system state before changes
- Store: Process list, settings, configurations
- Automatic snapshot before profile application

**Rollback:**
- Restore previous system state
- Undo all changes made by profile
- Automatic rollback on failure

**Validation:**
- Check if action is safe
- Verify system stability after changes
- Prevent dangerous operations

---

## Nexus Architecture

### Purpose
Web dashboard and API gateway

### Module Structure

```
nexus/
├── api/                # API endpoints
│   ├── chat.py         # Chat with Sage
│   ├── metrics.py      # System metrics
│   ├── patterns.py     # Learned patterns
│   └── control.py      # Guardian control
│
├── websockets/         # WebSocket streaming
│   └── metrics_stream.py # Real-time metrics (disabled)
│
├── templates/          # HTML templates
│   └── index.html      # Dashboard UI
│
├── static/             # Static files (CSS, JS)
│
├── config.py           # Configuration
└── main.py             # FastAPI application
```

### API Endpoints

**Chat API:**
- `POST /api/chat/message` - Send message to Sage
- `GET /api/chat/history` - Get conversation history

**Metrics API:**
- `GET /api/metrics/current` - Current system metrics
- `GET /api/metrics/history` - Historical data
- `GET /api/metrics/processes` - Process information
- `GET /api/metrics/summary` - Summary statistics

**Patterns API:**
- `GET /api/patterns/learned` - Learned patterns from Oracle
- `GET /api/patterns/anomalies` - Detected anomalies
- `GET /api/patterns/predictions` - Future predictions

**Control API:**
- `GET /api/control/profiles` - Available profiles
- `POST /api/control/apply` - Apply profile
- `POST /api/control/rollback` - Rollback changes

**Health API:**
- `GET /health` - Service health check
- `GET /docs` - API documentation (Swagger)

### Dashboard Features

**Real-time Metrics:**
- CPU usage gauge
- RAM usage bar
- GPU temperature
- Network traffic graph

**Chat Interface:**
- Send messages to Sage
- View conversation history
- Get AI insights

**System Status:**
- Component health indicators
- Active profile display
- Recent anomalies

**Quick Actions:**
- Apply optimization profile
- View detailed metrics
- Export data

---

## Data Flow Example

### User asks: "What's my CPU usage?"

1. **User → Nexus**
   - User types in chat: "What's my CPU usage?"
   - Nexus receives POST to `/api/chat/message`

2. **Nexus → Sentinel**
   - Nexus queries Sentinel database
   - Gets current CPU metrics: 34.8% @ 3700 MHz

3. **Nexus → Sage**
   - Nexus calls Sage CLI with context
   - Context includes: CPU 34.8%, recent trends
   - Sage receives: "Current System: CPU 34.8%... User asks: What's my CPU usage?"

4. **Sage → Gemini**
   - Sage sends prompt to Gemini 2.5 Flash
   - Gemini processes with 1M token context
   - Gemini generates response

5. **Gemini → Sage → Nexus → User**
   - Gemini: "Your CPU is at 34.8% utilization, running at 3.7 GHz. This is normal for light usage."
   - Sage saves conversation to database
   - Nexus returns response to user
   - User sees response in chat

**Total Time:** ~2-3 seconds

---

## Inter-Component Communication

### Sentinel → Oracle
- **Method:** Direct SQLite database access
- **Frequency:** Oracle reads every 24 hours for training
- **Data:** Last 1000+ snapshots

### Sentinel → Nexus
- **Method:** Direct SQLite database access
- **Frequency:** Real-time (every API request)
- **Data:** Current metrics, historical data

### Oracle → Nexus
- **Method:** Direct SQLite database access
- **Frequency:** On-demand (when patterns requested)
- **Data:** Learned patterns, predictions, anomalies

### Sage → Sentinel
- **Method:** Via Nexus (subprocess call)
- **Frequency:** Per chat message
- **Data:** Current metrics as context

### Guardian → Sentinel
- **Method:** Direct SQLite database access
- **Frequency:** Continuous monitoring
- **Data:** Current metrics for profile decisions

### Guardian → Oracle
- **Method:** Direct SQLite database access
- **Frequency:** Before profile application
- **Data:** Predictions for optimization decisions

---

## Technology Stack

### Languages
- **Python 3.12** - All components
- **SQL** - Database queries
- **JavaScript** - Dashboard frontend
- **HTML/CSS** - Dashboard UI
- **PowerShell** - Setup and management scripts

### Frameworks
- **FastAPI** - Nexus web server
- **Click** - CLI interfaces
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM (optional)

### Libraries
- **TensorFlow 2.20.0** - Oracle ML models
- **google-genai** - Sage Gemini integration
- **psutil** - System metrics collection
- **pynvml** - NVIDIA GPU metrics
- **uvicorn** - ASGI server for Nexus

### Databases
- **SQLite** - All data storage
  - `sentinel/data/system_stats.db` - Metrics
  - `oracle/data/patterns.db` - ML patterns
  - `sage/data/conversations.db` - Chat history
  - `sage/data/feedback.db` - User feedback

### Tools
- **uv** - Python package manager
- **pytest** - Testing framework
- **ruff** - Code linting and formatting

---

## Deployment Architecture

### Development (Current)
- All components run locally
- PowerShell scripts for management
- Background jobs for services
- SQLite for data storage

### Production (Future)
- Docker containers for each component
- Docker Compose for orchestration
- Shared volumes for databases
- Nginx reverse proxy
- Systemd services (Linux) or Windows Services

---

## Performance Characteristics

### Sentinel
- **CPU:** <2% average
- **RAM:** <500MB
- **Disk:** ~10MB/day (compressed)
- **Collection:** 30 seconds interval

### Oracle
- **CPU:** <5% during training, <1% idle
- **RAM:** ~1GB during training, ~200MB idle
- **Disk:** ~50MB for models
- **Training:** Every 24 hours (10-30 minutes)

### Sage
- **CPU:** <1% idle, spikes during chat
- **RAM:** ~100MB
- **Network:** ~1KB per message to Gemini
- **Response Time:** 2-3 seconds

### Guardian
- **CPU:** <1% monitoring, spikes during profile application
- **RAM:** ~100MB
- **Disk:** Minimal
- **Profile Application:** 5-10 seconds

### Nexus
- **CPU:** <1% idle, <5% under load
- **RAM:** ~200MB
- **Network:** Minimal (local only)
- **Response Time:** <100ms for API calls

**Total System Overhead:** <10% CPU, <2GB RAM

---

## Security Considerations

### Data Privacy
- All data stored locally (except Gemini API calls)
- No telemetry or external reporting
- Process names collected, but not file paths or arguments
- No window titles or clipboard data

### API Security
- CORS restricted to localhost
- No authentication (local only)
- Rate limiting on Gemini API
- Input validation on all endpoints

### System Safety
- Guardian snapshots before changes
- Automatic rollback on failure
- Validation of all system actions
- No destructive operations without confirmation

---

## Scalability

### Current Limits
- **Sentinel:** 1 snapshot/30 seconds = 2,880/day
- **Oracle:** Requires 1000+ samples (12 hours of data)
- **Sage:** Gemini API rate limits apply
- **Database:** SQLite handles millions of rows

### Future Scaling
- Multiple machines (distributed Sentinel)
- PostgreSQL for larger datasets
- Redis for caching
- Load balancing for Nexus

---

## Monitoring & Observability

### Logs
- Each component logs to `logs/` directory
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log rotation (daily, keep 30 days)

### Metrics
- Sentinel tracks its own overhead
- Oracle logs training metrics
- Sage logs API usage and costs
- Guardian logs all actions taken

### Health Checks
- `/health` endpoint in Nexus
- Component status in dashboard
- Automatic restart on failure (via PowerShell jobs)

---

## Development Workflow

### Adding a New Feature

1. **Design**
   - Document in architecture.md
   - Create module structure
   - Define data models

2. **Implementation**
   - Write code in appropriate module
   - Follow existing patterns
   - Add type hints and docstrings

3. **Testing**
   - Write unit tests
   - Write integration tests
   - Test manually

4. **Integration**
   - Update CLI if needed
   - Update API if needed
   - Update dashboard if needed

5. **Documentation**
   - Update README
   - Update module docs
   - Add usage examples

---

**Last Updated:** January 28, 2026  
**Version:** 0.1.0  
**Status:** Active Development
