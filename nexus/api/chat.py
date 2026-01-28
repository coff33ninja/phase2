"""Chat API endpoints for Sage integration."""
import sqlite3
import subprocess
import json
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from config import config
from api.metrics import get_current_metrics

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    context: Dict[str, Any] = {}


def get_sage_connection():
    """Get connection to Sage database."""
    if not config.sage_db_path.exists():
        raise HTTPException(status_code=503, detail="Sage database not found")
    
    conn = sqlite3.connect(config.sage_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/message")
async def send_message(chat_message: ChatMessage) -> Dict[str, Any]:
    """Send a message to Sage with current system context.
    
    Args:
        chat_message: Message and context
        
    Returns:
        Response from Sage
    """
    try:
        # Get current system metrics to provide context
        try:
            current_metrics = await get_current_metrics()
            
            # Format metrics for Sage
            context_str = f"""
Current System State:
- CPU: {current_metrics.get('cpu', {}).get('usage_percent', 'N/A')}% @ {current_metrics.get('cpu', {}).get('frequency_mhz', 'N/A')} MHz
- RAM: {current_metrics.get('ram', {}).get('usage_percent', 'N/A')}% ({current_metrics.get('ram', {}).get('used_gb', 'N/A')} GB / {current_metrics.get('ram', {}).get('total_gb', 'N/A')} GB)
"""
            
            # Add GPU info if available
            if current_metrics.get('gpu'):
                for gpu in current_metrics['gpu']:
                    context_str += f"- GPU ({gpu.get('name', 'Unknown')}): {gpu.get('usage_percent', 'N/A')}% @ {gpu.get('temperature_celsius', 'N/A')}°C\n"
            
            # Add disk and network
            disk = current_metrics.get('disk', {})
            network = current_metrics.get('network', {})
            context_str += f"- Disk: Read {disk.get('read_mbps', 0):.1f} MB/s, Write {disk.get('write_mbps', 0):.1f} MB/s\n"
            context_str += f"- Network: ↓ {network.get('download_mbps', 0):.1f} MB/s, ↑ {network.get('upload_mbps', 0):.1f} MB/s\n"
            
            # Combine user message with context
            full_message = f"{context_str}\nUser Question: {chat_message.message}"
            
        except Exception as e:
            logger.warning(f"Could not fetch metrics for context: {e}")
            full_message = chat_message.message
        
        # Call Sage CLI directly
        sage_dir = Path(__file__).parent.parent.parent / "sage"
        sage_python = sage_dir / ".venv" / "Scripts" / "python.exe"
        
        if not sage_python.exists():
            raise HTTPException(
                status_code=503, 
                detail="Sage not installed. Run setup-all.ps1 first."
            )
        
        # Execute Sage query command
        result = subprocess.run(
            [str(sage_python), "main.py", "query", full_message],
            cwd=str(sage_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"Sage error: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Sage query failed: {result.stderr}"
            )
        
        # Parse Sage response
        response_text = result.stdout.strip()
        
        return {
            "response": response_text,
            "confidence": 0.85,  # Gemini 2.5 Flash is highly confident
            "suggestions": [],
            "context": chat_message.context
        }
        
    except subprocess.TimeoutExpired:
        logger.error("Sage query timeout")
        raise HTTPException(status_code=504, detail="Sage query timeout")
    except Exception as e:
        logger.error(f"Failed to send message to Sage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get conversation history.
    
    Args:
        limit: Maximum number of messages to return
        
    Returns:
        List of conversation messages from recent sessions
    """
    try:
        conn = get_sage_connection()
        cursor = conn.cursor()
        
        # Get recent messages from all sessions
        cursor.execute("""
            SELECT session_id, role, content, created_at, tokens_used
            FROM messages
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights(
    hours: int = 24
) -> List[Dict[str, Any]]:
    """Get proactive insights from Sage.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        List of insights
    """
    try:
        conn = get_sage_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insights
            WHERE timestamp > datetime('now', ? || ' hours')
            ORDER BY importance DESC, timestamp DESC
            LIMIT 20
        """, (f'-{hours}',))
        
        insights = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))
