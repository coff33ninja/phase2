# Phase 2 Quick Start Guide

Get up and running with Phase 2 in 5 minutes!

---

## Prerequisites

1. **Python 3.12** - [Download](https://www.python.org/downloads/)
2. **uv package manager** - Install: `pip install uv`
3. **Windows 10/11** with PowerShell

---

## Installation (2 minutes)

```powershell
# 1. Navigate to Phase 2
cd phases/phase2

# 2. Run automated setup
.\setup-all.ps1 -QuickSetup

# Done! All components installed.
```

---

## Configuration (1 minute)

### Required: Sage API Key

```powershell
# Edit Sage configuration
notepad sage\.env

# Add your Gemini API key:
GEMINI_API_KEY=your-api-key-here
```

Get API key: https://makersuite.google.com/app/apikey

### Optional: Adjust Settings

Other components work with default settings, but you can customize:
- `sentinel/.env` - Data collection settings
- `oracle/.env` - ML model settings
- `guardian/.env` - Automation settings
- `nexus/.env` - Dashboard settings

---

## Start Components (1 minute)

```powershell
# Start everything in background
.\start-all.ps1 -Background

# Or start manually in separate terminals:
# Terminal 1: cd sentinel && python main.py collect
# Terminal 2: cd nexus && python main.py
```

---

## Access Dashboard (30 seconds)

```powershell
# Open dashboard
start http://localhost:8000

# Or manually:
# Dashboard: http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Health:    http://localhost:8000/health
```

---

## Verify Installation (30 seconds)

```powershell
# Check component status
.\status-all.ps1

# Should show:
# ✓ Sentinel - Installed
# ✓ Oracle - Installed
# ✓ Sage - Installed
# ✓ Guardian - Installed
# ✓ Nexus - Installed
```

---

## First Steps

### 1. View Real-Time Metrics

Open http://localhost:8000 and see:
- Live CPU, RAM, GPU usage
- Process list
- System status

### 2. Try the API

```powershell
# Get current metrics
curl http://localhost:8000/api/metrics/current

# Get process list
curl http://localhost:8000/api/metrics/processes

# View API documentation
start http://localhost:8000/docs
```

### 3. Use Guardian

```powershell
# Navigate to Guardian
cd guardian

# View available profiles
python main.py profiles

# Activate gaming profile
python main.py activate gaming

# Check status
python main.py status
```

### 4. Chat with Sage (if API key configured)

```powershell
# Navigate to Sage
cd sage

# Start Sage
python main.py

# Ask questions about your system
```

---

## Common Commands

```powershell
# Start components
.\start-all.ps1 -Background

# Stop components
.\stop-all.ps1

# Check status
.\status-all.ps1

# View logs
Get-Content sentinel\logs\*.log -Tail 20
Get-Content nexus\logs\*.log -Tail 20
```

---

## Troubleshooting

### Setup Failed

```powershell
# Check prerequisites
python --version  # Should be 3.12.x
uv --version      # Should show version

# Try manual setup
cd sentinel
.\setup.ps1
```

### Components Won't Start

```powershell
# Stop existing processes
.\stop-all.ps1

# Check status
.\status-all.ps1

# Try manual start
cd sentinel
python main.py collect
```

### Port 8000 In Use

```powershell
# Use different port
cd nexus
python main.py --port 8080
```

### No Data in Dashboard

```powershell
# Ensure Sentinel is running
cd sentinel
python main.py collect

# Wait 30 seconds for data collection
# Refresh dashboard
```

---

## Next Steps

### Learn More

- **Full Setup Guide:** [SETUP.md](SETUP.md)
- **Script Documentation:** [SCRIPTS.md](SCRIPTS.md)
- **Component READMEs:** See each component's README.md
- **Usage Guides:** See each component's USAGE.md

### Explore Features

1. **Real-Time Monitoring**
   - View live metrics in Nexus dashboard
   - Connect to WebSocket: `ws://localhost:8000/ws/metrics`

2. **Pattern Learning**
   - Oracle learns your usage patterns
   - View predictions: http://localhost:8000/api/patterns/predictions

3. **AI Assistance**
   - Chat with Sage about your system
   - Get proactive insights

4. **Automation**
   - Create custom Guardian profiles
   - Automate system optimizations

5. **API Integration**
   - Use REST API for custom integrations
   - Build your own dashboards

### Customize

1. **Create Custom Profiles**
   ```powershell
   cd guardian/profiles
   copy gaming.yaml custom.yaml
   notepad custom.yaml
   ```

2. **Adjust Collection Interval**
   ```powershell
   # Edit sentinel/.env
   COLLECTION_INTERVAL=10  # seconds
   ```

3. **Enable Auto-Training**
   ```powershell
   # Edit oracle/.env
   ENABLE_AUTO_TRAINING=true
   ```

---

## Support

### Get Help

1. **Check Logs**
   ```powershell
   Get-Content <component>\logs\*.log -Tail 50
   ```

2. **Check Status**
   ```powershell
   .\status-all.ps1
   ```

3. **Health Check**
   ```powershell
   curl http://localhost:8000/health
   ```

4. **Documentation**
   - Component README: `<component>/README.md`
   - Usage Guide: `<component>/USAGE.md`
   - API Docs: http://localhost:8000/docs

---

## Summary

You now have:
- ✅ All 5 Phase 2 components installed
- ✅ Real-time system monitoring
- ✅ ML-powered pattern learning
- ✅ AI-powered insights (with API key)
- ✅ Automated optimizations
- ✅ Web dashboard and API

**Total Setup Time:** ~5 minutes  
**Components:** 5/5 installed  
**Status:** Production Ready ✅

---

**Enjoy your hybrid AI system!** 🎉

For detailed documentation, see:
- [SETUP.md](SETUP.md) - Complete setup guide
- [SCRIPTS.md](SCRIPTS.md) - Script documentation
- [README.md](README.md) - Phase 2 overview

---

**Last Updated:** January 28, 2026  
**Version:** 1.0.0
