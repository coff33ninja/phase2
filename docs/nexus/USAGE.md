# Nexus Usage Guide

Complete guide to using Nexus dashboard for system monitoring and control.

---

## Table of Contents

1. [Installation](#installation)
2. [Starting the Server](#starting-the-server)
3. [API Endpoints](#api-endpoints)
4. [WebSocket Streaming](#websocket-streaming)
5. [Integration](#integration)
6. [Examples](#examples)

---

## Installation

### Prerequisites

- Python 3.12
- uv package manager
- Windows 10/11
- Sentinel, Oracle, Sage, Guardian (Phase 2.1-2.4) installed

### Setup

```powershell
# Navigate to Nexus directory
cd phases/phase2/nexus

# Run setup script
.\setup.ps1

# Verify installation
python main.py --help
```

---

## Starting the Server

### Basic Start

```powershell
# Start with default settings (localhost:8000)
python main.py

# Or use CLI command
nexus serve
```

### Custom Configuration

```powershell
# Custom host and port
python main.py --host 0.0.0.0 --port 8080

# Disable auto-reload
python main.py --no-reload
```

### Access Points

- **Dashboard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **WebSocket:** ws://localhost:8000/ws/metrics

---

## API Endpoints

### Metrics API

#### Get Current Metrics

```http
GET /api/metrics/current
```

Returns current system metrics from Sentinel.

**Response:**
```json
{
  "timestamp": "2026-01-28T12:00:00",
  "cpu_usage": 45.2,
  "ram_usage": 60.5,
  "gpu_usage": 12.0,
  "disk_usage": 75.0,
  "network_usage": 10.5
}
```

#### Get Metrics History

```http
GET /api/metrics/history?hours=1&metric=cpu_usage
```

**Parameters:**
- `hours` (optional): Hours to look back (1-168, default: 1)
- `metric` (optional): Specific metric to retrieve

**Response:**
```json
[
  {
    "timestamp": "2026-01-28T12:00:00",
    "value": 45.2
  },
  ...
]
```

#### Get Process List

```http
GET /api/metrics/processes?limit=20
```

**Parameters:**
- `limit` (optional): Max processes to return (1-100, default: 20)

**Response:**
```json
[
  {
    "pid": 1234,
    "name": "chrome.exe",
    "cpu_percent": 15.2,
    "memory_mb": 500
  },
  ...
]
```

#### Get Metrics Summary

```http
GET /api/metrics/summary
```

Returns average and peak values for the last hour.

### Patterns API

#### Get Learned Patterns

```http
GET /api/patterns/learned?limit=10
```

Returns behavior patterns learned by Oracle.

#### Get Predictions

```http
GET /api/patterns/predictions?metric=cpu_usage&horizon=30
```

**Parameters:**
- `metric`: Metric to predict (default: cpu_usage)
- `horizon`: Minutes ahead (5-120, default: 30)

#### Get Anomalies

```http
GET /api/patterns/anomalies?hours=24
```

Returns detected anomalies from Oracle.

#### Get Behavior Profile

```http
GET /api/patterns/behavior?profile_type=current
```

Returns behavior profile for specified type.

### Chat API

#### Send Message to Sage

```http
POST /api/chat/message
Content-Type: application/json

{
  "message": "Why is my system slow?",
  "context": {}
}
```

#### Get Chat History

```http
GET /api/chat/history?limit=20
```

#### Get Insights

```http
GET /api/chat/insights?hours=24
```

Returns proactive insights from Sage.

### Control API

#### List Guardian Profiles

```http
GET /api/control/profiles
```

**Response:**
```json
[
  {
    "name": "gaming",
    "description": "Optimize system for gaming performance",
    "enabled": true,
    "actions": 5
  },
  ...
]
```

#### Activate Profile

```http
POST /api/control/profiles/activate
Content-Type: application/json

{
  "profile_name": "gaming"
}
```

#### Execute Action

```http
POST /api/control/actions/execute
Content-Type: application/json

{
  "action_type": "close_process",
  "target": "chrome.exe",
  "parameters": {}
}
```

#### Get Action History

```http
GET /api/control/actions/history?limit=20
```

#### Rollback Action

```http
POST /api/control/actions/rollback?action_id=abc123
```

#### Get Guardian Status

```http
GET /api/control/status
```

---

## WebSocket Streaming

### Connect to Metrics Stream

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics');

ws.onopen = () => {
    console.log('Connected to metrics stream');
};

ws.onmessage = (event) => {
    const metrics = JSON.parse(event.data);
    console.log('Metrics:', metrics);
    // Update your UI with real-time data
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from metrics stream');
};
```

### Python Client Example

```python
import asyncio
import websockets
import json

async def stream_metrics():
    uri = "ws://localhost:8000/ws/metrics"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            metrics = json.loads(message)
            print(f"CPU: {metrics.get('cpu_usage')}%")
            print(f"RAM: {metrics.get('ram_usage')}%")
            print("---")

asyncio.run(stream_metrics())
```

---

## Integration

### Sentinel Integration

Nexus reads metrics directly from Sentinel's database:

```python
# Automatic integration via config
SENTINEL_DB_PATH=../sentinel/data/system_stats.db
```

### Oracle Integration

Access patterns and predictions from Oracle:

```python
# Automatic integration via config
ORACLE_DB_PATH=../oracle/data/patterns.db
```

### Sage Integration

Chat interface connects to Sage:

```python
# Automatic integration via config
SAGE_DB_PATH=../sage/data/conversations.db
```

### Guardian Integration

Control Guardian profiles and actions:

```python
# Automatic integration via config
GUARDIAN_DB_PATH=../guardian/data/actions.db
```

---

## Examples

### Example 1: Monitor System in Real-Time

```powershell
# Start Nexus
python main.py

# Open browser
start http://localhost:8000

# View real-time metrics via WebSocket
# Connect to ws://localhost:8000/ws/metrics
```

### Example 2: Get Current System Status

```powershell
# Using curl
curl http://localhost:8000/api/metrics/current

# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/metrics/current"
```

### Example 3: Activate Gaming Profile

```powershell
# Using curl
curl -X POST http://localhost:8000/api/control/profiles/activate `
  -H "Content-Type: application/json" `
  -d '{"profile_name":"gaming"}'

# Using PowerShell
$body = @{profile_name="gaming"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/control/profiles/activate" `
  -Method Post -Body $body -ContentType "application/json"
```

### Example 4: View API Documentation

```powershell
# Start server
python main.py

# Open API docs
start http://localhost:8000/docs

# Interactive API testing available at /docs
```

### Example 5: Check Component Status

```powershell
# Check Nexus status
python main.py status

# Check health endpoint
curl http://localhost:8000/health
```

---

## CLI Commands

### Serve

Start the Nexus server:

```powershell
nexus serve
nexus serve --host 0.0.0.0 --port 8080
nexus serve --no-reload
```

### Status

Check Nexus and component status:

```powershell
nexus status
```

### Config

Show Nexus configuration:

```powershell
nexus config
```

---

## Configuration

### Environment Variables

Edit `.env` file:

```env
# Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Integration Paths
SENTINEL_DB_PATH=../sentinel/data/system_stats.db
ORACLE_DB_PATH=../oracle/data/patterns.db
SAGE_DB_PATH=../sage/data/conversations.db
GUARDIAN_DB_PATH=../guardian/data/actions.db

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100
```

---

## Troubleshooting

### Server Won't Start

Check if port is already in use:

```powershell
netstat -ano | findstr :8000
```

Use a different port:

```powershell
python main.py --port 8080
```

### Component Not Found

Check component status:

```powershell
nexus status
```

Verify database paths in `.env` file.

### WebSocket Connection Failed

Ensure server is running and accessible:

```powershell
curl http://localhost:8000/health
```

Check firewall settings if accessing remotely.

---

## Best Practices

1. **Start Sentinel first** - Nexus needs Sentinel data
2. **Use HTTPS in production** - Configure reverse proxy (Nginx)
3. **Monitor logs** - Check `logs/nexus.log` for issues
4. **Rate limit API** - Implement rate limiting for production
5. **Secure WebSocket** - Use WSS (secure WebSocket) in production

---

## Support

For issues or questions:

1. Check logs: `logs/nexus.log`
2. Verify component status: `nexus status`
3. Check API health: http://localhost:8000/health
4. View API docs: http://localhost:8000/docs

---

**Last Updated:** January 28, 2026  
**Version:** 0.1.0  
**Status:** Production Ready
