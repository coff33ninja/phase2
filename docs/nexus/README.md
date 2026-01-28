# Nexus - Web Dashboard & API Gateway

**Version:** 0.1.0  
**Status:** ✅ Operational  
**Port:** 8001

## Overview

Nexus is the central web interface for Phase 2, providing:
- Real-time system monitoring dashboard
- Chat interface with Sage AI
- REST API for all components
- Training status visibility
- Component health monitoring

## Quick Start

```powershell
# Start Nexus
cd nexus
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --ws none

# Or use the start script
.\start-all.ps1 -Nexus

# Access dashboard
start http://localhost:8001
```

## Features

### 1. Web Dashboard
- **Real-time Metrics:** Live CPU, RAM, GPU usage
- **Training Status:** Progress bars and data collection info
- **Component Status:** Health indicators for all services
- **Chat Interface:** Talk to Sage AI directly from browser

### 2. REST API
- **Metrics API:** Current and historical system data
- **Patterns API:** Learned patterns from Oracle
- **Chat API:** Interact with Sage
- **Control API:** Manage Guardian profiles
- **Status API:** System and training status

### 3. Training Visibility
- Progress bar showing training readiness
- Data collection metrics (hours and samples)
- Next steps and recommendations
- Auto-updates every 10 seconds

## Architecture

```
Browser → Nexus (Port 8001) → FastAPI
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Sentinel    Oracle       Sage
  (DB)       (DB)       (CLI)
```

## API Endpoints

### Metrics
- `GET /api/metrics/current` - Current system metrics
- `GET /api/metrics/history` - Historical data

### Status
- `GET /api/status/system` - Complete system status
- `GET /api/status/training` - Training readiness details

### Chat
- `POST /api/chat/message` - Send message to Sage
- `GET /api/chat/history` - Conversation history

### Patterns
- `GET /api/patterns/learned` - Learned patterns from Oracle

### Control
- `GET /api/control/profiles` - Guardian profiles

### Health
- `GET /health` - Service health check
- `GET /docs` - API documentation (Swagger)

## Configuration

Edit `nexus/.env`:

```env
# Server
HOST=0.0.0.0
PORT=8001
RELOAD=false
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

# Database paths
SENTINEL_DB_PATH=../sentinel/data/system_stats.db
ORACLE_DB_PATH=../oracle/data/patterns.db
SAGE_DB_PATH=../sage/data/conversations.db
GUARDIAN_DB_PATH=../guardian/data/actions.db
```

## Dashboard Features

### Training Status Section
Shows real-time training progress:
- **Progress Bar:** Visual indicator (0-100%)
- **Data Collection:** Hours and samples collected
- **Requirements:** Minimum vs current values
- **Status Messages:** Dynamic based on progress
- **Auto-Updates:** Refreshes every 10 seconds

### Component Status
Real-time health indicators:
- 🟢 **Sentinel:** Collecting data
- 🔴 **Oracle:** Not trained / 🟢 Trained
- 🟢 **Sage:** AI ready
- 🟢 **Guardian:** On-demand
- 🟢 **Nexus:** Active

### Live Metrics
- CPU usage percentage
- RAM usage percentage
- GPU usage percentage
- Updates every 5 seconds

### Chat Interface
- Send messages to Sage
- View conversation history
- Get AI insights
- Real-time responses

## Usage Examples

### Check System Status
```powershell
# Via API
curl http://localhost:8001/api/status/system | ConvertFrom-Json

# Via browser
start http://localhost:8001
```

### Get Training Status
```powershell
curl http://localhost:8001/api/status/training | ConvertFrom-Json
```

### Chat with Sage
```powershell
$body = @{
    message = "What is my current CPU usage?"
    context = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/chat/message" -Method POST -Body $body -ContentType "application/json"
```

## Troubleshooting

### Port Already in Use
```powershell
# Check what's using port 8001
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <process_id> /F

# Or use a different port
cd nexus
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8002
```

### WebSocket Errors
Nexus runs with `--ws none` flag to disable WebSockets. If you see WebSocket errors:
```powershell
# Ensure websockets package is correct version
cd nexus
uv pip install "websockets==11.0.3"
```

### Dashboard Not Loading
```powershell
# Check if Nexus is running
curl http://localhost:8001/health

# Check logs
Get-Content nexus\logs\nexus.log -Tail 50

# Restart Nexus
.\stop-all.ps1
.\start-all.ps1 -Nexus
```

### API Returns 404
```powershell
# Verify endpoint exists
curl http://localhost:8001/docs

# Check if router is included in main.py
```

## Performance

- **Response Time:** <100ms for API calls
- **Dashboard Load:** <2 seconds
- **Memory Usage:** ~200MB
- **CPU Usage:** <1% idle, <5% under load

## Security

- **CORS:** Restricted to localhost by default
- **No Authentication:** Local-only deployment
- **Input Validation:** All endpoints validate input
- **Rate Limiting:** Gemini API calls rate-limited

## Development

### Running in Development Mode
```powershell
cd nexus
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

### Adding New Endpoints
1. Create new file in `nexus/api/`
2. Define router with `APIRouter()`
3. Add endpoints with decorators
4. Include router in `main.py`

### Testing
```powershell
cd nexus
pytest tests/ -v
```

## Related Documentation

- [API Reference](API.md) - Complete API documentation
- [Configuration](CONFIGURATION.md) - Detailed configuration options
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Development](DEVELOPMENT.md) - Development guidelines

---

**Last Updated:** January 28, 2026  
**Component:** Nexus  
**Status:** Operational
