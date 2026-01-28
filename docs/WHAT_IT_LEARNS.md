# What Your System Learns About You

## 📊 Data Collection (Sentinel)

### Every 30 Seconds, Sentinel Collects:

#### 1. **Process Information**
- **Process Name** (e.g., chrome.exe, discord.exe, steam.exe)
- **CPU Usage** per process
- **Memory Usage** per process
- **Thread Count**
- **Process Status** (running, sleeping, stopped)
- **Process ID (PID)**

#### 2. **System Metrics**
- CPU usage percentage and frequency
- RAM usage (total, used, available, cached)
- GPU usage, temperature, power draw
- Disk read/write speeds
- Network upload/download speeds
- Active network connections

#### 3. **Context Information**
- Time of day (morning, afternoon, evening, night)
- Day of week (weekday vs weekend)
- User activity status (active/idle)

---

## 🧠 Pattern Learning (Oracle - After 1000 Samples)

### What Oracle Will Learn:

#### 1. **Usage Patterns by Time**

**Morning (6 AM - 12 PM):**
- Which programs you typically run
- Average CPU/RAM usage
- Common activities (work, browsing, etc.)

**Afternoon (12 PM - 6 PM):**
- Peak usage times
- Resource-intensive applications
- Multitasking patterns

**Evening (6 PM - 12 AM):**
- Gaming sessions
- Entertainment apps
- Relaxation patterns

**Night (12 AM - 6 AM):**
- Background processes
- Downloads/updates
- Idle behavior

#### 2. **Application Behavior Profiles**

**Gaming Profile:**
- Detects when you're gaming (high GPU usage)
- Learns which games you play
- Typical session duration
- Resource requirements per game

**Work Profile:**
- Office applications (Word, Excel, etc.)
- Development tools (VS Code, browsers)
- Communication apps (Teams, Slack)
- Productivity patterns

**Entertainment Profile:**
- Streaming services (Netflix, YouTube)
- Media players
- Social media usage
- Content consumption patterns


#### 3. **Resource Usage Predictions**

Oracle will predict:
- **CPU usage** in next 5, 15, 30, 60 minutes
- **RAM usage** trends
- **Disk activity** patterns
- **Network bandwidth** needs

Based on:
- Historical patterns
- Time of day
- Day of week
- Currently running applications

#### 4. **Anomaly Detection**

Oracle identifies unusual behavior:
- **Unexpected high CPU usage** (possible malware or runaway process)
- **Memory leaks** (gradual RAM increase)
- **Unusual network activity** (unexpected uploads/downloads)
- **New processes** that don't match your patterns
- **Performance degradation** over time

#### 5. **Application Correlations**

Learns which apps you use together:
- "When Chrome is running, Discord is usually open"
- "Gaming sessions always start with Steam"
- "Work mode = VS Code + multiple browser tabs"
- "Video editing = high RAM + GPU usage"

---

## 🎯 What Oracle DOES with This Data

### 1. **Proactive Recommendations**

Sage (AI) will tell you:
- "You usually game at 8 PM, but your RAM is at 80%. Close some apps?"
- "Chrome is using 4GB RAM, which is higher than your usual 2GB"
- "Your CPU has been at 90% for 30 minutes, which is unusual"


### 2. **Automatic Optimization (Guardian)**

When activated, Guardian can:
- **Close background apps** before gaming
- **Adjust power settings** based on activity
- **Prioritize processes** for better performance
- **Free up RAM** when needed
- **Optimize network** for streaming/gaming

### 3. **Behavior Profiles**

Creates profiles like:
- **"Weekday Morning Work"** - Light usage, productivity apps
- **"Weekend Evening Gaming"** - High GPU, specific games
- **"Late Night Browsing"** - Low activity, media consumption

---

## 🔒 Privacy & Data Storage

### What's Stored Locally:

**Sentinel Database** (`sentinel/data/system_stats.db`):
- System metrics (CPU, RAM, GPU, etc.)
- Process names and resource usage
- Timestamps
- NO personal files or content
- NO passwords or credentials
- NO browsing history details
- NO file contents

**Oracle Database** (`oracle/data/patterns.db`):
- Learned patterns (aggregated data)
- Predictions
- Anomaly scores
- Behavior profiles
- NO raw process data (only patterns)

**Sage Database** (`sage/data/conversations.db`):
- Your questions to the AI
- AI responses
- Conversation context
- NO external transmission (except to Gemini API)

### What's Sent to Google (Gemini API):

When you chat with Sage:
- Your question
- Current system metrics (CPU%, RAM%, etc.)
- NO process names
- NO personal data
- NO file information

---

## 📈 Example Insights You'll Get

### After 1 Week:
- "You typically use 40% CPU during work hours"
- "Your RAM usage peaks at 8 PM (gaming)"
- "Chrome uses 30% of your RAM on average"

### After 1 Month:
- "Your system is 20% slower on Mondays"
- "You game 15 hours per week, mostly evenings"
- "Discord runs 80% of the time when you're active"
- "Your GPU temperature averages 65°C during gaming"

### After 3 Months:
- "Predicted: High CPU usage in 30 minutes (you usually start gaming)"
- "Anomaly detected: Unknown process using 50% CPU"
- "Recommendation: Upgrade RAM - you hit 90% usage daily"
- "Pattern: Your system slows down after 4 hours of use"

---

## 🎮 Real-World Examples

### Gaming Detection:
```
Oracle learns:
- Steam.exe starts at 8 PM on weekends
- GPU usage jumps to 80%+
- Specific game processes (e.g., csgo.exe)
- Session duration: 2-3 hours
- RAM usage: 12-16 GB

Guardian can:
- Close Chrome/Discord before gaming
- Set high-performance power mode
- Prioritize game process
- Disable Windows updates
```

### Work Pattern:
```
Oracle learns:
- VS Code opens at 9 AM weekdays
- Multiple browser tabs (documentation)
- Spotify in background
- Low GPU usage
- Moderate CPU (30-50%)

Guardian can:
- Keep productivity apps running
- Limit background processes
- Optimize for responsiveness
- Balanced power mode
```

### Streaming/Content Creation:
```
Oracle learns:
- OBS Studio = high CPU + GPU
- Multiple monitors active
- High network upload
- Long sessions (3+ hours)

Guardian can:
- Allocate maximum resources
- Close unnecessary apps
- Prioritize network bandwidth
- Monitor temperatures
```

---

## ⚙️ Control & Privacy

### You Control:
- ✅ **What's collected** (can disable specific collectors)
- ✅ **When it runs** (start/stop anytime)
- ✅ **Data retention** (can clear databases)
- ✅ **AI interactions** (optional, only when you chat)
- ✅ **Auto-optimization** (Guardian is opt-in)

### You Can:
- View all collected data in the database
- Delete any data anytime
- Disable specific metrics
- Stop collection completely
- Export your data

### The System NEVER:
- ❌ Sends data to third parties (except Gemini when you chat)
- ❌ Monitors file contents
- ❌ Tracks websites visited
- ❌ Records keystrokes
- ❌ Captures screenshots
- ❌ Accesses personal files
- ❌ Shares data with anyone

---

## 🔍 View Your Data

```powershell
# See what processes are tracked
Invoke-RestMethod http://localhost:8001/api/metrics/processes

# View current metrics
Invoke-RestMethod http://localhost:8001/api/metrics/current

# Check learned patterns (after training)
Invoke-RestMethod http://localhost:8001/api/patterns/learned

# View chat history
Invoke-RestMethod http://localhost:8001/api/chat/history
```

---

## Summary

**Your system learns:**
- ✅ Which programs you run and when
- ✅ Resource usage patterns
- ✅ Your daily/weekly routines
- ✅ Performance bottlenecks
- ✅ Unusual behavior (anomalies)

**To help you:**
- 🎯 Optimize performance automatically
- 🔮 Predict resource needs
- 🛡️ Detect problems early
- 💡 Provide intelligent recommendations
- ⚡ Improve your experience

**All data stays local** except when you explicitly chat with Sage (which uses Gemini API).
