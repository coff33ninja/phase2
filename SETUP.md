# Phase 2 Complete Setup Guide

Complete guide to setting up all Phase 2 components.

---

## Quick Start

### Automated Setup (Recommended)

```powershell
# Navigate to Phase 2 directory
cd phases/phase2

# Run complete setup
.\setup-all.ps1

# Quick setup (skip tests and confirmations)
.\setup-all.ps1 -QuickSetup

# Setup specific component only
.\setup-all.ps1 -Component Sentinel
```

### Manual Setup

If you prefer to set up components individually:

```powershell
# 1. Sentinel
cd sentinel
.\setup.ps1

# 2. Oracle
cd ../oracle
.\setup.ps1

# 3. Sage
cd ../sage
.\setup.ps1

# 4. Guardian
cd ../guardian
.\setup.ps1

# 5. Nexus
cd ../nexus
.\setup.ps1
```

---

## Prerequisites

### Required Software

1. **Python 3.12**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **uv Package Manager**
   - Install: `pip install uv`
   - Or visit: https://docs.astral.sh/uv/
   - Verify: `uv --version`

3. **Windows 10/11**
   - PowerShell 5.1 or higher
   - Administrator privileges (for some actions)

### Optional Software

1. **AIDA64** (for enhanced hardware monitoring)
   - Download: https://www.aida64.com/

2. **HWiNFO** (alternative hardware monitoring)
   - Download: https://www.hwinfo.com/

3. **Git** (for version control)
   - Download: https://git-scm.com/

---

## Setup Process

### Step 1: Prerequisites Check

The setup script automatically checks:
- ✓ Python 3.12 installation
- ✓ uv package manager
- ✓ Correct directory location

### Step 2: Component Installation

For each component, the script:
1. Installs Python dependencies via uv
2. Installs component in editable mode
3. Creates necessary directories (data, logs)
4. Copies .env.example to .env
5. Runs tests (optional)

### Step 3: Configuration

After installation, configure each component:

#### Sentinel Configuration
```env
# sentinel/.env
LOG_LEVEL=INFO
COLLECTION_INTERVAL=5
ENABLE_GPU_MONITORING=true
ENABLE_TEMPERATURE_MONITORING=true
```

#### Oracle Configuration
```env
# oracle/.env
LOG_LEVEL=INFO
MODEL_UPDATE_INTERVAL=3600
ENABLE_AUTO_TRAINING=true
```

#### Sage Configuration
```env
# sage/.env
GEMINI_API_KEY=your-api-key-here
LOG_LEVEL=INFO
ENABLE_PROACTIVE_INSIGHTS=true
```

#### Guardian Configuration
```env
# guardian/.env
AUTOMATION_LEVEL=semi_auto
ENABLE_ROLLBACK=true
PROTECTED_PROCESSES=explorer.exe,System,Registry,csrss.exe
```

#### Nexus Configuration
```env
# nexus/.env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Verification

### Test Each Component

```powershell
# Sentinel
cd sentinel
python main.py status

# Oracle
cd ../oracle
python main.py status

# Sage
cd ../sage
python main.py status

# Guardian
cd ../guardian
python main.py status

# Nexus
cd ../nexus
python -m cli.main status
```

### Run Tests

```powershell
# Run all tests
cd phases/phase2
pytest sentinel/tests/ -v
pytest oracle/tests/ -v
pytest sage/tests/ -v
pytest guardian/tests/ -v
```

---

## Starting Components

### Recommended Startup Order

1. **Start Sentinel** (Data Collection)
   ```powershell
   cd sentinel
   python main.py collect
   ```

2. **Start Oracle** (Optional - for ML predictions)
   ```powershell
   cd oracle
   python main.py train
   ```

3. **Start Sage** (Optional - for AI chat)
   ```powershell
   cd sage
   python main.py
   ```

4. **Start Nexus** (Dashboard)
   ```powershell
   cd nexus
   python main.py
   ```

5. **Use Guardian** (As needed)
   ```powershell
   cd guardian
   python main.py activate gaming
   ```

### Access Points

- **Nexus Dashboard:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **WebSocket Stream:** ws://localhost:8000/ws/metrics

---

## Troubleshooting

### Common Issues

#### 1. Python Version Mismatch

**Problem:** Python 3.12 not found

**Solution:**
```powershell
# Install Python 3.12 via uv
uv python install 3.12

# Or download from python.org
```

#### 2. uv Not Found

**Problem:** uv command not recognized

**Solution:**
```powershell
# Install uv
pip install uv

# Or use pipx
pipx install uv
```

#### 3. Permission Denied

**Problem:** Cannot create directories or files

**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → Run as Administrator
```

#### 4. Port Already in Use

**Problem:** Nexus port 8000 already in use

**Solution:**
```powershell
# Use different port
cd nexus
python main.py --port 8080
```

#### 5. Database Not Found

**Problem:** Component cannot find database

**Solution:**
```powershell
# Check .env file paths
# Ensure Sentinel is running first
cd sentinel
python main.py collect
```

#### 6. Import Errors

**Problem:** Module not found errors

**Solution:**
```powershell
# Reinstall component
cd <component>
uv pip install -e .
```

#### 7. Tests Failing

**Problem:** Tests fail during setup

**Solution:**
```powershell
# Skip tests during setup
.\setup-all.ps1 -SkipTests

# Or run tests manually later
cd <component>
pytest tests/ -v
```

---

## Advanced Setup

### Custom Installation Paths

Edit `.env` files to customize paths:

```env
# Custom database locations
SENTINEL_DB_PATH=E:/Data/sentinel.db
ORACLE_DB_PATH=E:/Data/oracle.db
SAGE_DB_PATH=E:/Data/sage.db
GUARDIAN_DB_PATH=E:/Data/guardian.db
```

### Development Setup

For development with auto-reload:

```powershell
# Install dev dependencies
uv pip install -r requirements.txt
uv pip install pytest pytest-cov ruff

# Run with auto-reload
cd nexus
python main.py --reload
```

### Production Setup

For production deployment:

1. **Disable Debug Mode**
   ```env
   LOG_LEVEL=WARNING
   RELOAD=false
   ```

2. **Use Reverse Proxy**
   ```nginx
   # Nginx configuration
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /ws/ {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

3. **Enable HTTPS**
   ```powershell
   # Use Let's Encrypt or similar
   certbot --nginx -d your-domain.com
   ```

4. **Run as Service**
   ```powershell
   # Use NSSM or Windows Task Scheduler
   nssm install Nexus "python" "E:\path\to\nexus\main.py"
   ```

---

## Uninstallation

### Remove All Components

```powershell
# Navigate to Phase 2 directory
cd phases/phase2

# Uninstall each component
uv pip uninstall sentinel oracle sage guardian nexus

# Remove virtual environment
Remove-Item -Recurse -Force .venv

# Remove data and logs (optional)
Remove-Item -Recurse -Force */data
Remove-Item -Recurse -Force */logs
```

### Remove Specific Component

```powershell
# Uninstall component
uv pip uninstall <component-name>

# Remove data
cd <component>
Remove-Item -Recurse -Force data logs
```

---

## Maintenance

### Update Components

```powershell
# Update dependencies
cd <component>
uv pip install --upgrade -r requirements.txt

# Reinstall component
uv pip install -e .
```

### Backup Data

```powershell
# Backup all databases
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path */data/*.db -DestinationPath "backup_$date.zip"
```

### Clean Logs

```powershell
# Remove old logs (older than 30 days)
Get-ChildItem -Path */logs/*.log -Recurse | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item
```

---

## Support

### Getting Help

1. **Check Logs**
   ```powershell
   # View component logs
   Get-Content <component>/logs/*.log -Tail 50
   ```

2. **Check Status**
   ```powershell
   # Component status
   cd <component>
   python main.py status
   ```

3. **Run Diagnostics**
   ```powershell
   # Nexus health check
   curl http://localhost:8000/health
   ```

4. **Documentation**
   - Component README: `<component>/README.md`
   - Usage Guide: `<component>/USAGE.md`
   - API Docs: http://localhost:8000/docs

---

## Best Practices

1. **Start with Sentinel** - Always start Sentinel first as other components depend on its data

2. **Configure Before Running** - Edit .env files before starting components

3. **Monitor Logs** - Check logs regularly for errors or warnings

4. **Backup Regularly** - Backup databases and configurations

5. **Update Dependencies** - Keep dependencies up to date

6. **Use Virtual Environment** - Always use the .venv for isolation

7. **Test After Updates** - Run tests after updating components

8. **Secure API Keys** - Never commit .env files with API keys

---

## Quick Reference

### Setup Commands

```powershell
# Complete setup
.\setup-all.ps1

# Quick setup (no prompts)
.\setup-all.ps1 -QuickSetup

# Skip tests
.\setup-all.ps1 -SkipTests

# Setup one component
.\setup-all.ps1 -Component Sentinel
```

### Start Commands

```powershell
# Sentinel
cd sentinel && python main.py collect

# Oracle
cd oracle && python main.py train

# Sage
cd sage && python main.py

# Guardian
cd guardian && python main.py status

# Nexus
cd nexus && python main.py
```

### Test Commands

```powershell
# Run all tests
pytest <component>/tests/ -v

# Run with coverage
pytest <component>/tests/ --cov=<component>

# Run specific test
pytest <component>/tests/test_file.py::test_function
```

---

**Last Updated:** January 28, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
