# Phase 2 - AI-Powered System Intelligence

A hybrid AI system combining local ML (TensorFlow) with cloud AI (Google Gemini 2.5 Flash) for intelligent system monitoring, pattern learning, and proactive optimization.

## � Features

- **Sentinel** - Real-time system metrics collection (CPU, RAM, GPU, Disk, Network)
- **Oracle** - Local ML pattern learning with TensorFlow (LSTM, Anomaly Detection, Clustering)
- **Sage** - AI assistant powered by Gemini 2.5 Flash for natural language insights
- **Guardian** - Auto-tuning and system optimization profiles
- **Nexus** - Web dashboard with chat interface for system interaction

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key

### Installation

1. Clone the repository:
```powershell
git clone https://github.com/coff33ninja/phase2.git
cd phase2
```

2. Run the setup script:
```powershell
.\setup-all.ps1 -QuickSetup
```

3. Configure your Gemini API key:
```powershell
# Edit sage/.env and add your API key
GEMINI_API_KEY=your_api_key_here
```

4. Start all components:
```powershell
.\start-all.ps1 -All
```

5. Access the dashboard:
```
http://localhost:8001
```

## 📊 Components

### Sentinel - Data Collection
**Purpose:** Real-time system monitoring and data storage

**What It Does:**
- Collects metrics every 30 seconds from 11 specialized collectors
- Stores data in SQLite time-series database
- Detects patterns, spikes, and anomalies
- Provides CLI for data access and export

**Collectors:**
- **CPU:** Usage, frequency, per-core metrics, temperature (needs AIDA64)
- **RAM:** Total, used, available, cached memory
- **GPU:** Usage, VRAM, temperature ✅, fan speed, power draw
- **Disk:** Read/write speeds, queue length, per-disk usage
- **Network:** Download/upload speeds, active connections
- **Process:** Top processes by CPU/RAM, thread counts
- **Context:** User activity, time of day, detected actions (gaming/coding/browsing)
- **Temperature:** System sensors (needs AIDA64/HWiNFO64 - see TEMPERATURE_SETUP.md)
- **PowerShell:** Custom script integration (optional)
- **WMI:** Windows Management Instrumentation (optional)
- **AIDA64:** Comprehensive hardware sensors (implemented, not integrated)

**Database Schema:**
- `system_snapshots` - Main table with timestamps
- `cpu_metrics`, `ram_metrics`, `gpu_metrics`, etc. - Separate metric tables
- Foreign key relationships for efficient queries

**See:** `COLLECTOR_REFERENCE.md` for detailed collector documentation

---

### Oracle - ML Pattern Learning
**Purpose:** Local machine learning for predictions and anomaly detection

**What It Does:**
- Learns patterns from Sentinel's collected data
- Predicts future resource usage (5, 15, 30, 60 minutes ahead)
- Detects anomalies and unusual behavior
- Clusters usage patterns (gaming, work, idle, etc.)
- Trains models automatically every 24 hours

**ML Models:**
- **LSTM Forecaster:** Time-series prediction for CPU, RAM, GPU
- **Isolation Forest:** Anomaly detection (unusual system behavior)
- **K-Means Clustering:** Groups similar usage patterns
- **Classifier:** Identifies activity types

**Requirements:**
- Minimum 1000 samples (~12 hours of Sentinel data)
- TensorFlow 2.20.0
- Currently has ~23 samples (needs 977 more)

**Modules:**
- `models/` - ML model implementations
- `training/` - Data loading and feature engineering
- `inference/` - Predictions and pattern matching
- `patterns/` - Pattern storage and behavior profiles

**See:** `oracle/README.md` for detailed ML documentation

---

### Sage - AI Assistant
**Purpose:** Natural language interface powered by Google Gemini 2.5 Flash

**What It Does:**
- Answers questions about your system in natural language
- Provides insights and recommendations
- Tracks conversation history
- Aggregates context from Sentinel and Oracle
- Generates proactive insights

**Features:**
- **Context-Aware:** Sees current metrics, learned patterns, and history
- **Conversational:** Maintains session context across messages
- **Proactive:** Monitors for issues and suggests optimizations
- **Learning:** Collects feedback to improve responses

**Modules:**
- `gemini_client/` - Gemini API integration with rate limiting
- `conversation/` - Session management and intent classification
- `prompts/` - System prompts and dynamic prompt building
- `context/` - Context aggregation from all sources
- `insights/` - Proactive monitoring and insight generation
- `feedback/` - User feedback collection and preference learning

**Example Questions:**
- "What's my current CPU usage?"
- "Show me RAM trends over the last hour"
- "Are there any anomalies?"
- "What patterns have you learned?"
- "Optimize my system for gaming"

**See:** `sage/README.md` for detailed AI documentation

---

### Guardian - Auto-Tuning
**Purpose:** Automated system optimization with safety mechanisms

**What It Does:**
- Applies optimization profiles (Gaming, Work, Power Saver)
- Manages processes and resource allocation
- Tunes CPU, GPU, and RAM settings
- Creates snapshots before changes
- Automatic rollback on failure

**Profiles:**
- **Gaming:** Max performance, close background apps, prioritize game
- **Work:** Balanced mode, keep productivity apps
- **Power Saver:** Minimize power consumption, reduce performance

**Actions:**
- **Process:** Kill, set priority, set CPU affinity, limit memory
- **Resource:** Clear cache, defragment memory, adjust page file
- **System:** Set power plan, adjust frequencies, configure QoS

**Safety:**
- **Snapshots:** Capture system state before changes
- **Validation:** Check if actions are safe
- **Rollback:** Restore previous state on failure

**Modules:**
- `profiles/` - Profile definitions and management
- `actions/` - System action implementations
- `execution/` - Safe action execution with logging
- `safety/` - Snapshots, rollback, validation
- `integration/` - Connect to Sentinel, Oracle, Sage

**See:** `guardian/README.md` for detailed optimization documentation

---

### Nexus - Dashboard
**Purpose:** Web interface and API gateway

**What It Does:**
- Provides web dashboard on http://localhost:8001
- Exposes REST API for all components
- Real-time chat interface with Sage
- Displays live system metrics
- Shows learned patterns and predictions

**Features:**
- **Dashboard:** Beautiful HTML interface with real-time updates
- **Chat:** Talk to Sage AI directly from browser
- **Metrics:** Live CPU, RAM, GPU, Disk, Network graphs
- **Patterns:** View learned patterns and anomalies
- **Control:** Apply Guardian profiles from UI
- **API Docs:** Swagger documentation at /docs

**API Endpoints:**
- `/api/chat/*` - Chat with Sage
- `/api/metrics/*` - System metrics (current, history, processes, summary)
- `/api/patterns/*` - Learned patterns, anomalies, predictions
- `/api/control/*` - Guardian profile management
- `/health` - Service health check

**Modules:**
- `api/` - FastAPI endpoint implementations
- `templates/` - HTML dashboard
- `static/` - CSS, JavaScript, images
- `websockets/` - Real-time streaming (currently disabled)

**See:** `nexus/README.md` for detailed API documentation

## 🛠️ Management Commands

```powershell
# Setup (first time)
.\setup-all.ps1 -QuickSetup

# Start all components
.\start-all.ps1 -All

# Stop all components
.\stop-all.ps1

# Check status
.\status-all.ps1

# Uninstall (removes venvs, data, logs, config)
.\uninstall-all.ps1

# Uninstall but keep data
.\uninstall-all.ps1 -KeepData

# Uninstall but keep virtual environments
.\uninstall-all.ps1 -KeepVenvs

# View running jobs
Get-Job

# View component output
Receive-Job -Id <job_id> -Keep
```

## 📁 Project Structure

```
phase2/
├── sentinel/          # Data collection (11 collectors, SQLite storage)
│   ├── collectors/    # CPU, RAM, GPU, Disk, Network, Process, etc.
│   ├── aggregator/    # Data pipeline and normalization
│   ├── storage/       # Database layer and query builder
│   ├── patterns/      # Pattern detection (baseline, spikes, thresholds)
│   └── cli/           # Command-line interface
│
├── oracle/            # ML pattern learning (TensorFlow)
│   ├── models/        # LSTM, Isolation Forest, K-Means, Classifier
│   ├── training/      # Data loading and feature engineering
│   ├── inference/     # Predictions and pattern matching
│   ├── patterns/      # Pattern storage and behavior profiles
│   └── integration/   # Sentinel connector and scheduler
│
├── sage/              # Gemini AI integration
│   ├── gemini_client/ # Gemini 2.5 Flash API client
│   ├── conversation/  # Session management and intent classification
│   ├── prompts/       # System prompts and prompt building
│   ├── context/       # Context aggregation from all sources
│   ├── insights/      # Proactive monitoring
│   └── feedback/      # User feedback and preference learning
│
├── guardian/          # Auto-tuning and optimization
│   ├── profiles/      # Gaming, Work, Power Saver profiles
│   ├── actions/       # Process, Resource, System actions
│   ├── execution/     # Safe action execution
│   ├── safety/        # Snapshots, rollback, validation
│   └── integration/   # Connect to other components
│
├── nexus/             # Web dashboard and API gateway
│   ├── api/           # REST API endpoints (chat, metrics, patterns, control)
│   ├── templates/     # HTML dashboard
│   ├── static/        # CSS, JavaScript
│   └── websockets/    # Real-time streaming (disabled)
│
├── setup-all.ps1      # Installation script (Python 3.12 + uv)
├── start-all.ps1      # Start all components in background
├── stop-all.ps1       # Stop all components
├── status-all.ps1     # Check component status
│
└── Documentation/
    ├── README.md                  # This file
    ├── SETUP.md                   # Setup instructions
    ├── USAGE.md                   # Usage guide
    ├── SCRIPTS.md                 # Script reference
    ├── QUICKSTART.md              # Quick start guide
    ├── WHAT_IT_LEARNS.md          # Privacy and data collection
    ├── IMPROVEMENTS_NEEDED.md     # Known issues and improvements
    ├── TEMPERATURE_SETUP.md       # Temperature monitoring setup
    ├── COLLECTOR_REFERENCE.md     # Detailed collector docs
    ├── MODULE_ARCHITECTURE.md     # System architecture
    ├── architecture.md            # Technical architecture
    └── data-sources.md            # Data source documentation
```

**See `MODULE_ARCHITECTURE.md` for detailed component architecture and data flow.**

## 🔧 Configuration

Each component has its own `.env` file for configuration:

- `sentinel/.env` - Collection intervals, database paths
- `oracle/.env` - Training parameters, model settings
- `sage/.env` - Gemini API key, model selection
- `guardian/.env` - Profile settings, thresholds
- `nexus/.env` - Server port, CORS settings

## 📈 Data Flow

```
Sentinel → Collects Metrics → SQLite Database
    ↓
Oracle → Reads Data → Trains ML Models → Learns Patterns
    ↓
Sage → Queries Patterns → Generates Insights → Gemini 2.5 Flash
    ↓
Nexus → Displays Data → Chat Interface → User
```

## 🤖 Chat with Sage

Ask Sage questions like:
- "What's my current system status?"
- "Show me CPU usage trends"
- "Are there any anomalies?"
- "What patterns have you learned?"
- "Optimize my system for gaming"

## 📊 API Endpoints

- `GET /api/metrics/current` - Current system metrics
- `GET /api/metrics/history` - Historical data
- `GET /api/patterns/learned` - ML patterns
- `POST /api/chat/message` - Chat with Sage
- `GET /api/control/profiles` - Guardian profiles
- `GET /docs` - Full API documentation

## 🔒 Security

- API keys stored in `.env` files (not committed)
- CORS configured for localhost only
- No external data transmission except Gemini API
- Local ML models for privacy

## � Troubleshooting

### Sentinel not collecting data
```powershell
cd sentinel
.\.venv\Scripts\python.exe main.py status
```

### Oracle needs more data
Oracle requires 1000+ samples (several hours of collection) before training models.

### Sage not responding
Check your Gemini API key in `sage/.env`

### Port conflicts
Nexus uses port 8001. Change in `nexus/.env` if needed.

## � License

MIT License - See LICENSE file for details

## 👤 Author

**coff33ninja**
- GitHub: [@coff33ninja](https://github.com/coff33ninja)
- Email: coff33ninja69@gmail.com

## 🙏 Acknowledgments

- Google Gemini 2.5 Flash for AI capabilities
- TensorFlow for local ML
- FastAPI for web framework
- psutil for system metrics

## 📚 Documentation

### Getting Started
- [Quick Start Guide](QUICKSTART.md) - Get up and running in 5 minutes
- [Setup Guide](SETUP.md) - Detailed installation instructions
- [Usage Guide](USAGE.md) - How to use each component

### Architecture & Design
- [Module Architecture](MODULE_ARCHITECTURE.md) - Complete system architecture
- [Technical Architecture](architecture.md) - Technical design details
- [Data Sources](data-sources.md) - Data collection sources

### Component Documentation
- [Collector Reference](COLLECTOR_REFERENCE.md) - All 11 collectors explained
- [Temperature Setup](TEMPERATURE_SETUP.md) - Enable temperature monitoring
- [Sentinel README](sentinel/README.md) - Data collection details
- [Oracle README](oracle/README.md) - ML model details
- [Sage README](sage/README.md) - AI assistant details
- [Guardian README](guardian/README.md) - Auto-tuning details
- [Nexus README](nexus/README.md) - Dashboard and API details

### Reference
- [Scripts Reference](SCRIPTS.md) - PowerShell script documentation
- [What It Learns](WHAT_IT_LEARNS.md) - Privacy and data collection
- [Improvements Needed](IMPROVEMENTS_NEEDED.md) - Known issues and roadmap

---

**Status**: Active Development
**Version**: 0.1.0
**Python**: 3.12+
**Platform**: Windows 10/11
