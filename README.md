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
- Google Gemini API key (for Sage)

### Installation

#### Option 1: Install All Components (Recommended)
```powershell
# Clone the repository
git clone https://github.com/coff33ninja/phase2.git
cd phase2

# Run automated setup for all components
.\setup-all.ps1 -QuickSetup
```

#### Option 2: Install Individual Components
Each component has its own `setup.ps1` script:
```powershell
# Install Sentinel only
cd sentinel
.\setup.ps1

# Install Oracle only
cd oracle
.\setup.ps1

# Install Sage only
cd sage
.\setup.ps1

# Install Guardian only
cd guardian
.\setup.ps1

# Install Nexus only
cd nexus
.\setup.ps1
```

### Configuration

Configure your Gemini API key:
```powershell
# Edit sage/.env and sentinel/.env
GEMINI_API_KEY=your_api_key_here
```

### Starting Components

```powershell
# Start Sentinel (data collection)
cd sentinel
.\.venv\Scripts\python.exe main.py monitor

# Start Nexus (dashboard) - in new terminal
cd nexus
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws none

# Access the dashboard
start http://localhost:8001

# Check system status
.\status.ps1
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
- Shows training status and progress

**Features:**
- **Dashboard:** Real-time HTML interface with auto-updates
- **Chat:** Talk to Sage AI directly from browser
- **Metrics:** Live CPU, RAM, GPU usage displays
- **Training Status:** Progress bars showing data collection and readiness
- **Component Health:** Real-time status indicators for all services
- **API Docs:** Swagger documentation at /docs

**API Endpoints:**
- `/api/chat/*` - Chat with Sage
- `/api/metrics/*` - System metrics (current, history)
- `/api/patterns/*` - Learned patterns from Oracle
- `/api/status/*` - System and training status
- `/api/control/*` - Guardian profile management
- `/health` - Service health check

**Current Status:**
- ✅ Dashboard operational
- ✅ Training status visibility
- ✅ Real-time metrics display
- ✅ Chat interface with Sage
- ✅ Component health monitoring

**See:** [docs/nexus/](docs/nexus/) for detailed documentation

## 🛠️ Management Commands

### Global Commands (All Components)

```powershell
# Setup all components
.\setup-all.ps1 -QuickSetup

# Check system status
.\status.ps1

# Stop all components
.\stop-all.ps1

# Uninstall all (removes venvs, data, logs, config)
.\uninstall-all.ps1

# Uninstall but keep data
.\uninstall-all.ps1 -KeepData
```

### Component-Specific Commands

Each component has its own setup, uninstall, and management scripts:

```powershell
# Sentinel
cd sentinel
.\setup.ps1                                    # Install
.\uninstall.ps1                                # Uninstall
.\uninstall.ps1 -KeepData                      # Uninstall but keep database
.\.venv\Scripts\python.exe main.py status      # Check status
.\.venv\Scripts\python.exe main.py monitor     # Start monitoring

# Oracle
cd oracle
.\setup.ps1                                    # Install
.\uninstall.ps1                                # Uninstall
.\.venv\Scripts\python.exe main.py train       # Train models

# Sage
cd sage
.\setup.ps1                                    # Install
.\uninstall.ps1                                # Uninstall
.\uninstall.ps1 -KeepConfig                    # Keep API key
.\.venv\Scripts\python.exe main.py status      # Check status
.\.venv\Scripts\python.exe main.py query "..."  # Ask question

# Guardian
cd guardian
.\setup.ps1                                    # Install
.\uninstall.ps1                                # Uninstall
.\.venv\Scripts\python.exe main.py status      # Check status

# Nexus
cd nexus
.\setup.ps1                                    # Install
.\uninstall.ps1                                # Uninstall
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws none
```

### Uninstall Options

All uninstall scripts support these flags:
- `-KeepData` - Preserve database files
- `-KeepVenv` - Preserve virtual environment
- `-KeepConfig` - Preserve .env configuration

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
Sentinel → Collects Metrics → SQLite Database (every 5 seconds)
    ↓
Oracle → Reads Data → Trains ML Models → Learns Patterns (needs 1h + 100 samples)
    ↓
Sage → Queries Data → Generates Insights → Gemini 2.5 Flash
    ↓
Nexus → Displays Data → Chat Interface → Training Status → User
```

### Current System State

**Operational:**
- ✅ Sentinel: Collecting data every 5 seconds
- ✅ Nexus: Dashboard running on port 8001
- ✅ Sage: AI assistant ready (with API key)
- ✅ Training Status: Visible in dashboard and CLI

**In Progress:**
- ⏳ Oracle: Collecting training data (needs 0.5h + 95 samples more)
- ⏳ Guardian: Ready for use (on-demand)

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
- [Module Architecture](MODULE_ARCHITECTURE.md) - Complete system architecture

### Component Documentation
- [Sentinel](docs/sentinel/) - Data collection and monitoring
- [Oracle](docs/oracle/) - Machine learning and pattern recognition
- [Sage](docs/sage/) - AI assistant powered by Gemini 2.5 Flash
- [Guardian](docs/guardian/) - Auto-tuning and optimization
- [Nexus](docs/nexus/) - Web dashboard and API gateway

### Reference Documentation
- [Collector Reference](docs/COLLECTOR_REFERENCE.md) - All 11 collectors explained
- [Temperature Setup](docs/TEMPERATURE_SETUP.md) - Enable temperature monitoring
- [Scripts Reference](docs/SCRIPTS.md) - PowerShell script documentation
- [Training Readiness](docs/TRAINING_READINESS.md) - ML training requirements
- [What It Learns](docs/WHAT_IT_LEARNS.md) - Privacy and data collection

### Complete Documentation
See [docs/](docs/) for the complete documentation index.

---

**Status**: Active Development  
**Version**: 0.1.0  
**Python**: 3.12+  
**Platform**: Windows 10/11  
**Last Updated**: January 28, 2026
