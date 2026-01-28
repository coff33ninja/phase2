# Sage Usage Guide

## Quick Start

### 1. Setup
```powershell
# Run setup script
.\setup.ps1

# Add your Gemini API key to .env
# GEMINI_API_KEY=your_api_key_here
```

### 2. Check Status
```powershell
python main.py status
```

### 3. Ask Questions
```powershell
# Simple query
python main.py query "Why is my system slow?"

# With session ID
python main.py query "How is my CPU usage?" --session-id my-session
```

## CLI Commands

### query
Ask Sage a question about your system.

```powershell
# Interactive mode
python main.py query

# Direct query
python main.py query "What's using the most RAM?"

# Continue conversation
python main.py query "Can you explain more?" --session-id session_20260127_120000
```

### status
Show Sage configuration and integration status.

```powershell
python main.py status
```

### history
Show recent conversation sessions.

```powershell
# Show last 10 sessions
python main.py history

# Show last 20 sessions
python main.py history --limit 20
```

### show
Display messages from a specific session.

```powershell
# Show session messages
python main.py show session_20260127_120000

# Show last 100 messages
python main.py show session_20260127_120000 --limit 100
```

## Example Queries

### Performance Analysis
```
"Why is my system slow right now?"
"What's causing high CPU usage?"
"Is my RAM usage normal?"
"Why is my disk so busy?"
```

### Optimization
```
"How can I improve performance?"
"What processes should I close?"
"Should I upgrade my RAM?"
"How can I reduce CPU temperature?"
```

### Predictions
```
"Will my system handle this workload?"
"When should I expect high usage?"
"What's my typical resource usage?"
```

### Troubleshooting
```
"Why did my system crash?"
"What's causing this error?"
"Is this behavior normal?"
"Should I be concerned about this?"
```

## Configuration

### Environment Variables (.env)

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.7
MAX_OUTPUT_TOKENS=2048

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_TOKENS_PER_MINUTE=1000000

# Caching (optional)
ENABLE_REDIS_CACHE=false
REDIS_HOST=localhost
REDIS_PORT=6379

# Integration
SENTINEL_DB_PATH=../sentinel/data/system_stats.db
ORACLE_PATTERNS_DB_PATH=../oracle/data/patterns.db
```

## Integration with Sentinel and Oracle

Sage automatically connects to:
- **Sentinel**: For current system metrics
- **Oracle**: For learned patterns and predictions

Make sure both are running and have collected data:

```powershell
# Check Sentinel
cd ../sentinel
python main.py status

# Check Oracle
cd ../oracle
python main.py status
```

## API Key Setup

### Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```

### Verify API Key
```powershell
python main.py status
```

Should show: `API Key: Set`

## Tips

### Better Responses
- Be specific in your questions
- Provide context when needed
- Use follow-up questions in same session
- Check Sentinel/Oracle data is available

### Cost Management
- Monitor token usage in responses
- Use shorter queries when possible
- Adjust MAX_OUTPUT_TOKENS if needed
- Check costs: ~$0.30 per 1M input tokens

### Troubleshooting

**"API Key not set"**
- Add GEMINI_API_KEY to .env file
- Restart terminal/reload environment

**"Sentinel database not found"**
- Run Sentinel first to collect data
- Check SENTINEL_DB_PATH in .env

**"Oracle database not found"**
- Run Oracle training first
- Check ORACLE_PATTERNS_DB_PATH in .env

**Rate limit errors**
- Reduce MAX_REQUESTS_PER_MINUTE
- Wait a minute and try again
- Check your API quota

## Advanced Usage

### Python API
```python
from gemini_client import GeminiClient
from context import ContextAggregator
from prompts import PromptBuilder

# Initialize
client = GeminiClient()
context_agg = ContextAggregator()

# Get context
context = await context_agg.get_system_context()

# Build prompt
prompt = PromptBuilder.build_analysis_prompt(
    query="Why is my system slow?",
    system_state=context["system_state"],
    patterns=context["patterns"]
)

# Generate response
result = await client.generate_response(prompt, context=context)
print(result["response"])
```

### Streaming Responses
```python
async for chunk in client.generate_streaming_response(prompt):
    print(chunk, end="", flush=True)
```

## Next Steps

- Explore conversation history
- Try different query types
- Monitor token usage
- Provide feedback on responses
- Check integration with Guardian (Phase 2.4)

---

**Need Help?**
- Check logs in `logs/sage.log`
- Review IMPLEMENTATION_CHECKLIST.md
- See README.md for architecture details
