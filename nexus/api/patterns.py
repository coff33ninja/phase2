"""Patterns API endpoints."""
import sqlite3
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from config import config

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


def get_oracle_connection():
    """Get connection to Oracle database."""
    if not config.oracle_db_path.exists():
        raise HTTPException(status_code=503, detail="Oracle database not found")
    
    conn = sqlite3.connect(config.oracle_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/learned")
async def get_learned_patterns(
    limit: int = Query(default=10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    """Get learned behavior patterns.
    
    Args:
        limit: Maximum number of patterns to return
        
    Returns:
        List of pattern dictionaries
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM patterns
            WHERE timestamp > datetime('now', '-24 hours')
            ORDER BY confidence DESC
            LIMIT ?
        """, (limit,))
        
        patterns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return patterns
        
    except Exception as e:
        logger.error(f"Failed to get learned patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions")
async def get_predictions(
    metric: str = Query(default="cpu_usage"),
    horizon: int = Query(default=30, ge=5, le=120)
) -> Dict[str, Any]:
    """Get predictions for a metric.
    
    Args:
        metric: Metric name to predict
        horizon: Prediction horizon in minutes
        
    Returns:
        Prediction dictionary
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM predictions
            WHERE metric = ? AND horizon_minutes = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (metric, horizon))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return {}
        
    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(default=24, ge=1, le=168)
) -> List[Dict[str, Any]]:
    """Get detected anomalies.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        List of anomaly dictionaries
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM anomalies
            WHERE timestamp > datetime('now', ? || ' hours')
            ORDER BY severity DESC, timestamp DESC
            LIMIT 50
        """, (f'-{hours}',))
        
        anomalies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/behavior")
async def get_behavior_profile(
    profile_type: str = Query(default="current")
) -> Dict[str, Any]:
    """Get behavior profile.
    
    Args:
        profile_type: Profile type (current, gaming, work, etc.)
        
    Returns:
        Behavior profile dictionary
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM behavior_profiles
            WHERE profile_type = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (profile_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return {}
        
    except Exception as e:
        logger.error(f"Failed to get behavior profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))
