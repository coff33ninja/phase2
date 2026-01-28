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
Collects system metrics every 30 seconds:
- CPU usage and temperature
- RAM usage and caching
- GPU usage and memory
- Disk I/O and queue length
- Network traffic and connections
- Process information

### Oracle - ML Pattern Learning
Local machine learning with TensorFlow:
- LSTM forecasting for resource prediction
- Isolation Forest for anomaly detection
- K-Means clustering for usage patterns
- Automatic model training every 24 hours
- Requires 1000+ samples for initial training

### Sage - AI Assistant
Gemini 2.5 Flash integration:
- Natural language system queries
- Proactive insights and recommendations
- Conversation history tracking
- Context-aware responses

### Guardian - Auto-Tuning
System optimization profiles:
- Gaming profile (max performance)
- Work profile (balanced)
- Power saver profile (efficiency)
- Automatic profile switching

### Nexus - Dashboard
Web interface on port 8001:
- Real-time metrics display
- Chat with Sage AI
- System status monitoring
- API documentation

## 🛠️ Management Commands

```powershell
# Start all components
.\start-all.ps1 -All

# Stop all components
.\stop-all.ps1

# Check status
.\status-all.ps1

# View running jobs
Get-Job

# View component output
Receive-Job -Id <job_id> -Keep
```

## 📁 Project Structure

```
phase2/
├── sentinel/          # Data collection
├── oracle/            # ML pattern learning
├── sage/              # Gemini AI integration
├── guardian/          # Auto-tuning
├── nexus/             # Web dashboard
├── setup-all.ps1      # Installation script
├── start-all.ps1      # Start script
├── stop-all.ps1       # Stop script
└── status-all.ps1     # Status check
```

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

- [Setup Guide](SETUP.md)
- [Usage Guide](USAGE.md)
- [Architecture](architecture.md)
- [Data Sources](data-sources.md)
- [Scripts Reference](SCRIPTS.md)

---

**Status**: Active Development
**Version**: 0.1.0
**Python**: 3.12+
**Platform**: Windows 10/11
