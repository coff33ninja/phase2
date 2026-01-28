"""Metrics API endpoints."""
import sqlite3
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from loguru import logger

from config import config

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


def get_sentinel_connection():
    """Get connection to Sentinel database."""
    if not config.sentinel_db_path.exists():
        raise HTTPException(status_code=503, detail="Sentinel database not found")
    
    conn = sqlite3.connect(config.sentinel_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/current")
async def get_current_metrics() -> Dict[str, Any]:
    """Get current system metrics.
    
    Returns:
        Current metrics dictionary
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM system_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return {}
        
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_metrics_history(
    hours: int = Query(default=1, ge=1, le=168),
    metric: Optional[str] = Query(default=None)
) -> List[Dict[str, Any]]:
    """Get historical metrics.
    
    Args:
        hours: Number of hours to look back (1-168)
        metric: Specific metric to retrieve (optional)
        
    Returns:
        List of metric data points
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        if metric:
            cursor.execute(f"""
                SELECT timestamp, {metric} as value
                FROM system_metrics
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp ASC
            """, (f'-{hours}',))
        else:
            cursor.execute("""
                SELECT * FROM system_metrics
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp ASC
            """, (f'-{hours}',))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def get_processes(
    limit: int = Query(default=20, ge=1, le=100)
) -> List[Dict[str, Any]]:
    """Get current process list.
    
    Args:
        limit: Maximum number of processes to return
        
    Returns:
        List of process dictionaries
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM processes
            WHERE timestamp > datetime('now', '-5 minutes')
            ORDER BY cpu_percent DESC
            LIMIT ?
        """, (limit,))
        
        processes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return processes
        
    except Exception as e:
        logger.error(f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary with averages and peaks.
    
    Returns:
        Summary statistics dictionary
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                AVG(cpu_usage) as avg_cpu,
                MAX(cpu_usage) as peak_cpu,
                AVG(ram_usage) as avg_ram,
                MAX(ram_usage) as peak_ram,
                AVG(gpu_usage) as avg_gpu,
                MAX(gpu_usage) as peak_gpu,
                COUNT(*) as data_points
            FROM system_metrics
            WHERE timestamp > datetime('now', '-1 hour')
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return {}
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
