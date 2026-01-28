# Guardian - Auto-Tuning & Optimization
## Phase 2.4: Intelligent Automation

> **Codename:** Guardian  
> **Mission:** Protect and optimize  
> **Status:** 🛡️ In Development

---

## 🎯 Purpose

Guardian is the autonomous execution engine that takes insights from Oracle and recommendations from Sage and automatically optimizes your system. It acts as the "hands" that implement optimizations safely, with rollback capabilities and user-defined boundaries.

## 🛡️ Core Responsibilities

### 1. Process Management
- **Auto-close applications** based on patterns (e.g., close Discord before gaming)
- **Auto-start applications** when needed (e.g., start monitoring tools)
- **Process prioritization** (adjust CPU priority for important tasks)
- **Resource limiting** (cap memory/CPU for specific processes)

### 2. Resource Optimization
- **RAM management** (clear cache, suspend inactive tabs)
- **CPU allocation** (adjust process priorities)
- **GPU optimization** (switch power modes, close GPU-heavy apps)
- **Disk optimization** (schedule defrag, clear temp files)

### 3. Task Scheduling
- **Maintenance windows** (run updates during idle time)
- **Backup scheduling** (automatic backups when system is idle)
- **Cleanup tasks** (clear temp files, browser cache)
- **Performance monitoring** (periodic health checks)

### 4. Power Management
- **Dynamic power plans** (performance vs battery saver)
- **Component power states** (GPU, CPU, display)
- **Sleep/hibernate scheduling** (based on usage patterns)

### 5. Safety & Rollback
- **Pre-action snapshots** (save system state before changes)
- **Automatic rollback** (revert if issues detected)
- **User approval modes** (ask before critical actions)
- **Action logging** (complete audit trail)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER PREFERENCES                          │
│  • Automation level (off, ask, auto)                        │
│  • Protected processes (never close)                        │
│  • Allowed actions (whitelist/blacklist)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORACLE PATTERNS                             │
│  • User behavior profiles                                   │
│  • Resource usage patterns                                  │
│  • Performance baselines                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                SAGE RECOMMENDATIONS                          │
│  • Optimization suggestions                                 │
│  • Priority rankings                                        │
│  • Expected impact                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ACTION VALIDATOR                            │
│  • Check user preferences                                   │
│  • Verify safety constraints                                │
│  • Estimate risk level                                      │
│  • Request approval if needed                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ACTION EXECUTOR                             │
│  • Create system snapshot                                   │
│  • Execute optimization                                     │
│  • Monitor for issues                                       │
│  • Log results                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FEEDBACK LOOP                               │
│  • Measure impact                                           │
│  • Update Oracle models                                     │
│  • Refine future actions                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Components

### `/actions`
- `process_actions.py` - Process management (close, start, priority)
- `resource_actions.py` - Resource optimization (RAM, CPU, GPU)
- `system_actions.py` - System-level actions (power, cleanup)
- `scheduler_actions.py` - Task scheduling and automation
- `base_action.py` - Abstract base class for all actions

### `/profiles`
- `profile_manager.py` - Manage automation profiles
- `gaming_profile.py` - Gaming optimization profile
- `work_profile.py` - Work productivity profile
- `power_saver_profile.py` - Battery saving profile
- `custom_profile.py` - User-defined profiles

### `/safety`
- `validator.py` - Validate actions before execution
- `snapshot.py` - Create system snapshots
- `rollback.py` - Rollback failed actions
- `risk_assessor.py` - Assess action risk levels

### `/execution`
- `executor.py` - Execute validated actions
- `monitor.py` - Monitor action results
- `logger.py` - Log all actions and results

### `/integration`
- `oracle_connector.py` - Get patterns from Oracle
- `sage_connector.py` - Get recommendations from Sage
- `sentinel_connector.py` - Monitor system state

## 🔄 Action Flow

### Example: Gaming Profile Activation

```
1. USER: Starts a game (detected by Sentinel)
   ↓
2. ORACLE: Recognizes gaming pattern
   ↓
3. SAGE: Recommends "Close Discord, Spotify, Chrome"
   ↓
4. GUARDIAN: Validates actions
   - Check: Discord not in protected list ✓
   - Check: User preference allows auto-close ✓
   - Risk: Low (can restart easily) ✓
   ↓
5. GUARDIAN: Creates snapshot
   - Save: Open applications list
   - Save: Window positions
   - Save: Process states
   ↓
6. GUARDIAN: Executes actions
   - Close Discord (saved state)
   - Close Spotify (saved state)
   - Close Chrome (saved tabs)
   - Set game to High priority
   - Switch to Performance power plan
   ↓
7. GUARDIAN: Monitors results
   - Check: Game FPS improved? ✓
   - Check: RAM freed? ✓
   - Check: No crashes? ✓
   ↓
8. GUARDIAN: Logs success
   - Action: gaming_profile_activated
   - Impact: +15% FPS, -4GB RAM
   - User satisfaction: (awaiting feedback)
   ↓
9. ORACLE: Updates model
   - Learn: Gaming profile successful
   - Confidence: Increase for future
```

## 🎮 Automation Profiles

### Gaming Profile
```python
{
    "name": "Gaming",
    "trigger": "game_detected",
    "actions": [
        {"type": "close_process", "target": "Discord.exe"},
        {"type": "close_process", "target": "Spotify.exe"},
        {"type": "close_process", "target": "chrome.exe"},
        {"type": "set_priority", "target": "game.exe", "priority": "high"},
        {"type": "power_plan", "mode": "performance"},
        {"type": "gpu_mode", "mode": "max_performance"}
    ],
    "rollback_on_exit": true
}
```

### Work Profile
```python
{
    "name": "Work",
    "trigger": "work_hours",
    "actions": [
        {"type": "start_process", "target": "Teams.exe"},
        {"type": "start_process", "target": "Outlook.exe"},
        {"type": "close_process", "target": "Steam.exe"},
        {"type": "power_plan", "mode": "balanced"},
        {"type": "notification_mode", "mode": "focus"}
    ],
    "schedule": "weekdays 9:00-17:00"
}
```

### Power Saver Profile
```python
{
    "name": "PowerSaver",
    "trigger": "battery_low",
    "actions": [
        {"type": "power_plan", "mode": "power_saver"},
        {"type": "display_brightness", "level": 50},
        {"type": "close_process", "target": "chrome.exe"},
        {"type": "suspend_background_apps", "except": ["essential"]},
        {"type": "gpu_mode", "mode": "power_saving"}
    ],
    "threshold": "battery < 20%"
}
```

## � Safety Features

### User Consent Levels
1. **Manual** - Ask before every action
2. **Semi-Auto** - Ask for high-risk actions only
3. **Fully Auto** - Execute all validated actions

### Protected Processes
- User-defined list of processes that should never be closed
- System-critical processes (explorer.exe, etc.)
- Processes with unsaved work

### Risk Assessment
- **Low Risk**: Easily reversible (close app, change priority)
- **Medium Risk**: Requires restart (power plan, GPU mode)
- **High Risk**: System-level changes (registry, services)

### Rollback Capabilities
- Automatic rollback on failure
- Manual rollback via CLI
- Rollback history (last 10 actions)

## 📊 Action Logging

Every action is logged with:
- Timestamp
- Action type
- Target (process, resource, etc.)
- Parameters
- Result (success/failure)
- Impact metrics (RAM freed, FPS gained, etc.)
- User feedback (if provided)

## 🚀 Implementation Plan

### Week 1: Foundation
- [x] Project structure
- [ ] Base action class
- [ ] Action validator
- [ ] Safety system (snapshot, rollback)
- [ ] Configuration management

### Week 2: Core Actions
- [ ] Process management actions
- [ ] Resource optimization actions
- [ ] System-level actions
- [ ] Action executor

### Week 3: Profiles & Integration
- [ ] Profile manager
- [ ] Pre-built profiles (gaming, work, power saver)
- [ ] Oracle connector
- [ ] Sage connector
- [ ] Sentinel connector

### Week 4: Testing & Polish
- [ ] Unit tests
- [ ] Integration tests
- [ ] Safety tests
- [ ] CLI interface
- [ ] Documentation

## 📚 Technologies

- **Process Management:** psutil, win32api, win32process
- **System Control:** WMI, PowerShell
- **Task Scheduling:** Windows Task Scheduler, APScheduler
- **Configuration:** Pydantic, YAML
- **Logging:** loguru, SQLite
- **CLI:** Click, Rich

## 🎯 Success Metrics

### Performance
- **Action Execution:** <500ms per action
- **Rollback Time:** <2 seconds
- **System Overhead:** <1% CPU, <100MB RAM

### Effectiveness
- **Success Rate:** >95% of actions complete successfully
- **User Satisfaction:** >4/5 rating
- **Impact Accuracy:** Within 10% of predicted improvement

### Safety
- **False Positives:** <5% (actions blocked unnecessarily)
- **Rollback Success:** >99% of rollbacks successful
- **Zero Data Loss:** No user data lost from Guardian actions

---

**Last Updated:** January 28, 2026  
**Status:** 🛡️ In Development  
**Prerequisites:** Sentinel ✅, Oracle ✅, Sage ✅  
**Next Phase:** Nexus (Phase 2.5) - Dashboard

