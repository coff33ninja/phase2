# Sage - Gemini Integration
## Phase 2.3: Cloud Intelligence

> **Codename:** Sage  
> **Mission:** Provide wisdom and guidance  
> **Status:** 🔮 Planned

---

## 🎯 Purpose

Sage connects the local system to Gemini 2.5 Flash, providing intelligent analysis, natural language interaction, and expert recommendations. It acts as the "brain" that interprets patterns from Oracle, explains findings to users, and provides feedback to improve the local models.

## 🌐 Gemini 2.5 Flash Integration

### Why Gemini 2.5 Flash?
- **1M token context window** - Can analyze extensive system history
- **Native tool use** - Can call functions and interact with system
- **Multimodal** - Can process text, images, charts
- **Fast** - Low latency for real-time interaction
- **Cost-effective** - $0.30 per 1M input tokens

### Sage's Responsibilities

#### 1. Natural Language Understanding
- Parse user questions in plain English
- Understand context and intent
- Handle ambiguous or incomplete queries
- Support conversational follow-ups

#### 2. Intelligent Analysis
- Correlate multiple data points
- Identify root causes of issues
- Provide actionable insights
- Explain technical concepts simply

#### 3. Recommendations
- Suggest optimizations
- Explain trade-offs
- Prioritize actions by impact
- Provide step-by-step guidance

#### 4. Model Validation
- Validate Oracle's findings
- Correct false positives
- Suggest new patterns to learn
- Improve prediction accuracy

#### 5. User Communication
- Explain in user's preferred style
- Adapt complexity to user's expertise
- Provide detailed explanations when needed
- Interactive Q&A sessions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INPUT                              │
│  "Why is my system slow right now?"                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 QUERY PROCESSOR                              │
│  • Parse natural language                                   │
│  • Extract intent                                           │
│  • Identify required data                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  SENTINEL   │ │   ORACLE    │ │   SYSTEM    │
│    Data     │ │  Patterns   │ │   State     │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 CONTEXT BUILDER                              │
│  • Aggregate relevant data                                  │
│  • Format for Gemini                                        │
│  • Add historical context                                   │
│  • Include user preferences                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 GEMINI 2.5 FLASH                             │
│  • Analyze context                                          │
│  • Generate insights                                        │
│  • Create recommendations                                   │
│  • Explain reasoning                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                RESPONSE FORMATTER                            │
│  • Format for user display                                  │
│  • Add visualizations                                       │
│  • Include action buttons                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FEEDBACK LOOP                               │
│  • Record user action                                       │
│  • Update Oracle models                                     │
│  • Improve future responses                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Planned Components

### `/gemini_client`
- `client.py` - Gemini API wrapper
- `streaming.py` - Streaming response handler
- `rate_limiter.py` - API rate limiting
- `error_handler.py` - Error handling and retries
- `token_counter.py` - Token usage tracking

### `/prompts`
- `system_prompt.py` - Base system instructions
- `analysis_prompts.py` - Analysis templates
- `recommendation_prompts.py` - Recommendation templates
- `explanation_prompts.py` - Explanation templates
- `prompt_builder.py` - Dynamic prompt construction

### `/feedback`
- `feedback_collector.py` - Collect user feedback
- `model_updater.py` - Update Oracle based on feedback
- `preference_learner.py` - Learn user preferences
- `action_tracker.py` - Track recommendation outcomes

### `/conversation`
- `session_manager.py` - Manage conversation sessions
- `context_manager.py` - Maintain conversation context
- `history_store.py` - Store conversation history
- `intent_classifier.py` - Classify user intent

## 🔄 Feedback Loop

### Continuous Improvement Cycle

```
1. USER asks question
   ↓
2. SAGE gathers context from Sentinel + Oracle
   ↓
3. GEMINI analyzes and generates response
   ↓
4. USER receives recommendation
   ↓
5. USER takes action (accept/reject/modify)
   ↓
6. FEEDBACK recorded
   ↓
7. ORACLE updates models
   ↓
8. SAGE improves future responses
   ↓
9. LOOP REPEATS
```

### Learning from Interactions

```python
class FeedbackLoop:
    def record_interaction(self, query, response, user_action):
        """Track how users respond to recommendations"""
        feedback = {
            "query": query,
            "response": response,
            "user_action": user_action,  # accepted, rejected, modified
            "outcome": self.measure_outcome(),
            "context": self.get_system_context(),
            "timestamp": datetime.now()
        }
        
        # Update Oracle's models
        self.oracle.learn_from_feedback(feedback)
        
        # Improve Sage's prompts
        self.prompt_optimizer.tune(feedback)
        
        # Adjust future recommendations
        self.recommendation_engine.update(feedback)
```

## 💬 Example Interactions

### Example 1: Performance Issue
```
USER: "Why is my system slow right now?"

SAGE gathers:
- Current CPU: 78%, RAM: 22GB
- Chrome: 47 tabs (3x normal)
- VS Code: Running build process
- Oracle pattern: User typically closes Chrome before building

GEMINI response:
"Your system is slow because Chrome has 47 tabs open (3x your normal),
and you're running a build process in VS Code. Based on your patterns,
you typically close Chrome tabs before building.

Recommendations:
1. Close unused Chrome tabs (will free ~4GB RAM)
2. Pause Chrome's background sync temporarily
3. Consider scheduling builds during your lunch break (12:30-13:00)
   when you typically have lower activity

The local model has learned you prefer manual control, so I won't
auto-close anything. Would you like me to create a 'pre-build' profile
that does this automatically in the future?"

USER: "Yes, create the profile"

FEEDBACK: Accepted → Oracle learns new automation rule
```

### Example 2: Predictive Insight
```
SAGE (proactive):
"I've noticed your CPU temps have increased from 55°C to 68°C
over the past 14 days. This pattern typically indicates:
1. Dust buildup (most likely - 75% probability)
2. Thermal paste degradation (20%)
3. Fan failure (5%)

Recommendation: Clean your PC this weekend. I'll remind you
and show you a guide. Your temps should return to 55-60°C."

USER: "Remind me Saturday morning"

FEEDBACK: Accepted → Sage schedules reminder
```

### Example 3: Optimization Suggestion
```
SAGE (weekly report):
"This week's insights:

1. Gaming Performance: You could gain 15% FPS by closing Discord
   and Spotify before gaming. Want me to do this automatically?

2. Work Productivity: Chrome uses 2.5x more RAM on Mondays (research day).
   Consider using Edge for some tabs to reduce memory pressure.

3. System Health: All metrics normal. No anomalies detected.

4. Upcoming: Your typical Thursday build at 14:00 will likely cause
   lag. Consider running it at 12:30 during lunch instead."

USER: "Enable auto-close for gaming"

FEEDBACK: Accepted → Guardian creates automation rule
```

## 🔐 Privacy & Security

### Local-First Approach

**What is sent to Gemini:**
```json
{
    "type": "analysis_request",
    "summary": {
        "current_state": {
            "cpu_usage": "78%",
            "ram_usage": "22GB",
            "active_apps": ["chrome", "vscode"]
        },
        "patterns": {
            "typical_cpu": "45%",
            "typical_ram": "18GB",
            "user_habit": "closes_chrome_before_builds"
        },
        "anomaly": {
            "type": "high_resource_usage",
            "deviation": "2.5 std_dev"
        }
    },
    "query": "Why is my system slow?"
}
```

**What is NOT sent:**
- Specific file names or paths
- URLs or browsing history
- Personal data or credentials
- Exact timestamps
- IP addresses
- System serial numbers

### User Control
- Opt-in for cloud features
- Review data before sending
- Disable specific data types
- Export conversation history
- Delete all cloud data

## 🚀 Implementation Plan

### Week 5: Foundation
- [ ] Set up Gemini API client
- [ ] Implement authentication
- [ ] Create rate limiting
- [ ] Build error handling

### Week 6: Prompt Engineering
- [ ] Design system prompts
- [ ] Create analysis templates
- [ ] Build recommendation formats
- [ ] Test prompt effectiveness

### Week 7: Feedback Loop
- [ ] Implement feedback collection
- [ ] Connect to Oracle for model updates
- [ ] Build preference learning
- [ ] Create action tracking

### Week 8: Conversation Interface
- [ ] Session management
- [ ] Context maintenance
- [ ] History storage
- [ ] Multi-turn conversations

## 📊 Input/Output Format

### Input to Gemini
```json
{
    "system_context": {
        "learned_patterns": {
            "work_hours": "9:00-17:00 weekdays",
            "typical_apps": ["vscode", "chrome", "discord"],
            "resource_baseline": {
                "cpu": "40-50%",
                "ram": "16-20GB"
            }
        },
        "current_state": {
            "cpu": 78.5,
            "ram": 22.1,
            "gpu": 12.0,
            "active_processes": 156,
            "top_process": "chrome (47 tabs)"
        },
        "recent_anomalies": [
            {
                "type": "high_cpu",
                "process": "chrome",
                "deviation": "3.5 std_dev",
                "context": "unusual for this time"
            }
        ],
        "predictions": {
            "next_hour_cpu": "65-75%",
            "confidence": 0.87
        }
    },
    "user_query": "Why is my system slow right now?",
    "user_preferences": {
        "detail_level": "moderate",
        "auto_actions": false,
        "notification_style": "proactive"
    }
}
```

### Output from Gemini
```json
{
    "analysis": {
        "root_cause": "Chrome tab overload + VS Code build",
        "contributing_factors": [
            "47 Chrome tabs (3x normal)",
            "Active build process",
            "Background sync enabled"
        ],
        "severity": "moderate",
        "expected_duration": "until build completes (~5 min)"
    },
    "recommendations": [
        {
            "action": "close_chrome_tabs",
            "impact": "high",
            "effort": "low",
            "expected_improvement": "4GB RAM freed, 15% CPU reduction"
        },
        {
            "action": "schedule_builds_differently",
            "impact": "medium",
            "effort": "low",
            "expected_improvement": "avoid future slowdowns"
        }
    ],
    "explanation": "Your system is slow because...",
    "confidence": 0.92,
    "follow_up_questions": [
        "Would you like me to create an automation rule?",
        "Should I remind you before future builds?"
    ]
}
```

## 🎯 Success Metrics

### Response Quality
- **User Satisfaction:** >4/5 rating
- **Accuracy:** >90% helpful recommendations
- **Relevance:** >85% on-topic responses

### Performance
- **Response Latency:** <2 seconds
- **Token Usage:** <10K tokens per query
- **Cost:** <$0.10 per day per user

### Learning
- **Feedback Rate:** >50% of recommendations get feedback
- **Acceptance Rate:** >60% of recommendations accepted
- **Improvement:** 10% better accuracy per month

## 🔗 Integration Points

### Input from Sentinel
- Current system metrics
- Historical data summaries
- Process information

### Input from Oracle
- Learned patterns
- Predictions
- Anomaly detections
- Behavior profiles

### Output to Guardian
- Recommended actions
- Automation rules
- Optimization strategies

### Output to Nexus
- Formatted responses
- Visualizations
- Interactive elements

## 📚 Technologies

- **API:** Google AI Studio / Vertex AI
- **SDK:** google-generativeai Python package
- **Protocol:** REST API with streaming
- **Storage:** SQLite for conversation history
- **Caching:** Redis for response caching

---

**Last Updated:** January 27, 2026  
**Status:** 🔮 Planned  
**Prerequisites:** Sentinel ✅, Oracle (in progress)  
**Next Phase:** Guardian (Phase 2.4) - Auto-Tuning
