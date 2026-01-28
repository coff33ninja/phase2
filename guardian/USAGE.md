# Guardian Usage Guide

Complete guide to using Guardian for system optimization and automation.

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [CLI Commands](#cli-commands)
4. [Profiles](#profiles)
5. [Actions](#actions)
6. [Safety Features](#safety-features)
7. [Integration](#integration)
8. [Examples](#examples)

---

## Installation

### Prerequisites

- Python 3.12
- uv package manager
- Windows 10/11
- Sentinel, Oracle, and Sage (Phase 2.1-2.3) installed

### Setup

```powershell
# Navigate to Guardian directory
cd phases/phase2/guardian

# Run setup script
.\setup.ps1

# Verify installation
python main.py --help
```

---

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Automation Settings
AUTOMATION_LEVEL=semi_auto  # manual, semi_auto, fully_auto

# Safety Settings
ENABLE_ROLLBACK=true
SNAPSHOT_BEFORE_ACTION=true
MAX_ROLLBACK_HISTORY=10

# Risk Thresholds
APPROVAL_RISK_THRESHOLD=medium  # low, medium, high

# Protected Processes (comma-separated)
PROTECTED_PROCESSES=explorer.exe,System,Registry,csrss.exe

# Integration Paths
SENTINEL_DB_PATH=../sentinel/data/system_stats.db
ORACLE_DB_PATH=../oracle/data/patterns.db
SAGE_DB_PATH=../sage/data/conversations.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/guardian.log
ACTION_LOG_DB=./data/actions.db

# Profiles
DEFAULT_PROFILE=balanced
ENABLE_AUTO_PROFILE_SWITCHING=true

# Performance
MAX_CONCURRENT_ACTIONS=3
ACTION_TIMEOUT_SECONDS=30
```

### Automation Levels

- **manual**: Ask before every action
- **semi_auto**: Ask only for high-risk actions
- **fully_auto**: Execute all validated actions automatically

---

## CLI Commands

### Status

Show Guardian status and configuration:

```powershell
python main.py status
```

### Execute Action

Execute a single action:

```powershell
# Close a process
python main.py execute close_process chrome.exe

# Set process priority
python main.py execute set_priority game.exe -p priority=high

# Switch power plan
python main.py execute power_plan performance

# Clear RAM
python main.py execute clear_ram system

# Set display brightness
python main.py execute display_brightness display -p level=50
```

### Activate Profile

Activate an automation profile:

```powershell
# Activate gaming profile
python main.py activate gaming

# Activate work profile
python main.py activate work

# Activate power saver profile
python main.py activate power_saver
```

### List Profiles

Show all available profiles:

```powershell
python main.py profiles
```

### Action History

View recent action history:

```powershell
# Show last 10 actions
python main.py history

# Show last 20 actions
python main.py history -n 20
```

### Rollback

Rollback the last action:

```powershell
python main.py rollback
```

### Configuration

View or modify configuration:

```powershell
# Show all configuration
python main.py config

# Show specific key
python main.py config -k automation_level

# Set value (requires restart)
python main.py config -k automation_level -v fully_auto
```

---

## Profiles

### Built-in Profiles

#### Gaming Profile

Optimizes system for gaming performance:

- Closes Discord, Spotify, Chrome
- Sets game to high priority
- Switches to performance power plan
- Maximizes GPU performance
- Rolls back on exit

```powershell
python main.py activate gaming
```

#### Work Profile

Optimizes for productivity:

- Starts Teams, Outlook
- Closes Steam, gaming apps
- Switches to balanced power plan
- Enables focus mode notifications

```powershell
python main.py activate work
```

#### Power Saver Profile

Maximizes battery life:

- Switches to power saver plan
- Reduces display brightness
- Closes resource-heavy apps
- Suspends background apps
- Reduces GPU power

```powershell
python main.py activate power_saver
```

### Custom Profiles

Create custom profiles in `profiles/` directory:

```yaml
# profiles/custom.yaml
name: custom
description: My custom profile
trigger: null
actions:
  - type: close_process
    target: discord.exe
  - type: set_priority
    target: myapp.exe
    priority: high
  - type: power_plan
    mode: performance
schedule: null
rollback_on_exit: false
enabled: true
```

---

## Actions

### Process Actions

#### Close Process

Gracefully close a process:

```powershell
python main.py execute close_process notepad.exe
```

#### Start Process

Start a new process:

```powershell
python main.py execute start_process notepad.exe
```

#### Set Priority

Change process priority:

```powershell
python main.py execute set_priority game.exe -p priority=high
# Priorities: low, below_normal, normal, above_normal, high, realtime
```

#### Kill Process

Forcefully terminate a process (high risk):

```powershell
python main.py execute kill_process stuck.exe -y
```

### Resource Actions

#### Clear RAM

Clear system RAM cache:

```powershell
python main.py execute clear_ram system
```

#### Set CPU Affinity

Set CPU cores for a process:

```powershell
python main.py execute set_cpu_affinity game.exe -p cores=0,1,2,3
```

#### Disk Cleanup

Run disk cleanup:

```powershell
python main.py execute disk_cleanup system
```

### System Actions

#### Power Plan

Switch power plan:

```powershell
python main.py execute power_plan performance
# Plans: power_saver, balanced, performance
```

#### Display Brightness

Adjust display brightness:

```powershell
python main.py execute display_brightness display -p level=50
# Level: 0-100
```

#### Sleep

Put system to sleep:

```powershell
python main.py execute sleep system
```

#### Hibernate

Hibernate the system:

```powershell
python main.py execute hibernate system
```

---

## Safety Features

### Protected Processes

Guardian will never close these processes:

- explorer.exe (Windows Explorer)
- System (Windows System)
- Registry (Windows Registry)
- csrss.exe (Client/Server Runtime)
- Any process in `PROTECTED_PROCESSES` config

### Risk Assessment

Actions are categorized by risk level:

- **Low Risk**: Close process, set priority, display brightness
- **Medium Risk**: Power plan, disk cleanup, GPU mode
- **High Risk**: Kill process, system sleep/hibernate

### Snapshots

Before executing actions, Guardian creates snapshots:

- Process list and states
- Window positions
- System configuration
- Allows rollback if issues occur

### Rollback

Automatic rollback on failure:

```powershell
# Manual rollback
python main.py rollback
```

Rollback capabilities:

- Restart closed processes
- Restore process priorities
- Revert power plan changes
- Restore system state

---

## Integration

### Sentinel Integration

Guardian monitors system state via Sentinel:

```python
from integration import SentinelConnector

connector = SentinelConnector()
metrics = connector.get_current_metrics()
violations = connector.check_thresholds()
```

### Oracle Integration

Guardian uses Oracle patterns for decisions:

```python
from integration import OracleConnector

connector = OracleConnector()
patterns = connector.get_current_patterns()
predictions = connector.get_predictions("cpu_usage")
```

### Sage Integration

Guardian gets recommendations from Sage:

```python
from integration import SageConnector

connector = SageConnector()
recommendations = connector.get_recommendations(context)
insights = connector.get_insights()
```

---

## Examples

### Example 1: Gaming Session

```powershell
# Activate gaming profile
python main.py activate gaming

# Guardian automatically:
# - Closes Discord, Spotify, Chrome
# - Sets game to high priority
# - Switches to performance power plan
# - Maximizes GPU performance

# When done gaming, deactivate
python main.py rollback
```

### Example 2: Work Hours

```powershell
# Activate work profile
python main.py activate work

# Guardian automatically:
# - Starts Teams, Outlook
# - Closes Steam
# - Switches to balanced power plan
# - Enables focus mode
```

### Example 3: Low Battery

```powershell
# Activate power saver profile
python main.py activate power_saver

# Guardian automatically:
# - Switches to power saver plan
# - Reduces brightness to 50%
# - Closes Chrome
# - Suspends background apps
```

### Example 4: Manual Optimization

```powershell
# Close resource-heavy apps
python main.py execute close_process chrome.exe
python main.py execute close_process spotify.exe

# Boost important process
python main.py execute set_priority important.exe -p priority=high

# Switch to performance mode
python main.py execute power_plan performance

# View what was done
python main.py history
```

### Example 5: Scheduled Maintenance

```powershell
# Run disk cleanup during idle time
python main.py execute disk_cleanup system

# Clear RAM cache
python main.py execute clear_ram system
```

---

## Troubleshooting

### Action Failed

Check action history for details:

```powershell
python main.py history
```

### Rollback Failed

Check logs:

```powershell
type logs\guardian.log
```

### Profile Not Found

List available profiles:

```powershell
python main.py profiles
```

### Permission Denied

Run PowerShell as Administrator for system-level actions.

---

## Best Practices

1. **Start with manual mode** - Test actions before enabling automation
2. **Use profiles** - Create profiles for common scenarios
3. **Monitor history** - Review action history regularly
4. **Test rollback** - Verify rollback works for critical actions
5. **Protect important processes** - Add to `PROTECTED_PROCESSES`
6. **Review logs** - Check logs for issues
7. **Gradual automation** - Start with semi_auto, then fully_auto

---

## API Usage

### Python API

```python
from execution import ActionExecutor
from actions import CloseProcess

# Create executor
executor = ActionExecutor()

# Create action
action = CloseProcess(target="notepad.exe")

# Execute
result = executor.execute_action(action, user_approved=True)

if result.success:
    print(f"Success: {result.message}")
else:
    print(f"Failed: {result.error}")
```

### Profile API

```python
from profiles import ProfileManager

# Create manager
manager = ProfileManager()

# Load profile
profile = manager.get_profile("gaming")

# Activate
manager.activate_profile("gaming")

# Get active
active = manager.get_active_profile()
```

---

## Support

For issues or questions:

1. Check logs: `logs/guardian.log`
2. Review action history: `python main.py history`
3. Check configuration: `python main.py config`
4. Verify integration: Ensure Sentinel, Oracle, Sage are running

---

**Last Updated:** January 28, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
