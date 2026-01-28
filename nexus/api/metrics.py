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
        Current metrics dictionary with CPU, RAM, GPU, Disk, Network
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        # Get latest snapshot
        cursor.execute("""
            SELECT id, timestamp FROM system_snapshots
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        if not snapshot:
            conn.close()
            return {}
        
        snapshot_id = snapshot['id']
        result = {
            'timestamp': snapshot['timestamp'],
            'snapshot_id': snapshot_id
        }
        
        # Get CPU metrics
        cursor.execute("""
            SELECT usage_percent, frequency_mhz, temperature_celsius
            FROM cpu_metrics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        cpu = cursor.fetchone()
        if cpu:
            result['cpu'] = dict(cpu)
        
        # Get RAM metrics
        cursor.execute("""
            SELECT total_gb, used_gb, available_gb, cached_gb, usage_percent
            FROM ram_metrics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        ram = cursor.fetchone()
        if ram:
            result['ram'] = dict(ram)
        
        # Get GPU metrics
        cursor.execute("""
            SELECT name, usage_percent, memory_used_gb, memory_total_gb, 
                   temperature_celsius, power_draw_watts
            FROM gpu_metrics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        gpus = cursor.fetchall()
        if gpus:
            result['gpu'] = [dict(gpu) for gpu in gpus]
        
        # Get Disk metrics
        cursor.execute("""
            SELECT read_mbps, write_mbps, queue_length, usage_percent
            FROM disk_metrics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        disk = cursor.fetchone()
        if disk:
            result['disk'] = dict(disk)
        
        # Get Network metrics
        cursor.execute("""
            SELECT download_mbps, upload_mbps, connections_active
            FROM network_metrics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        network = cursor.fetchone()
        if network:
            result['network'] = dict(network)
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_metrics_history(
    hours: int = Query(default=1, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=1000)
) -> List[Dict[str, Any]]:
    """Get historical metrics.
    
    Args:
        hours: Number of hours to look back (1-168)
        limit: Maximum number of data points to return
        
    Returns:
        List of metric data points with timestamp and all metrics
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        # Get snapshots with all metrics joined
        cursor.execute("""
            SELECT 
                s.timestamp,
                c.usage_percent as cpu_usage,
                c.temperature_celsius as cpu_temp,
                r.usage_percent as ram_usage,
                r.used_gb as ram_used,
                d.read_mbps as disk_read,
                d.write_mbps as disk_write,
                n.download_mbps as net_download,
                n.upload_mbps as net_upload
            FROM system_snapshots s
            LEFT JOIN cpu_metrics c ON s.id = c.snapshot_id
            LEFT JOIN ram_metrics r ON s.id = r.snapshot_id
            LEFT JOIN disk_metrics d ON s.id = d.snapshot_id
            LEFT JOIN network_metrics n ON s.id = n.snapshot_id
            WHERE s.timestamp > datetime('now', '-' || ? || ' hours')
            ORDER BY s.timestamp ASC
            LIMIT ?
        """, (hours, limit))
        
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
        List of process dictionaries sorted by CPU usage
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        # Get latest snapshot
        cursor.execute("""
            SELECT id FROM system_snapshots
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        if not snapshot:
            conn.close()
            return []
        
        # Get processes from latest snapshot
        cursor.execute("""
            SELECT name, pid, cpu_percent, memory_mb, threads, status
            FROM process_info
            WHERE snapshot_id = ?
            ORDER BY cpu_percent DESC
            LIMIT ?
        """, (snapshot['id'], limit))
        
        processes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return processes
        
    except Exception as e:
        logger.error(f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_metrics_summary(
    hours: int = Query(default=1, ge=1, le=24)
) -> Dict[str, Any]:
    """Get metrics summary with averages and peaks.
    
    Args:
        hours: Number of hours to summarize (1-24)
    
    Returns:
        Summary statistics dictionary
    """
    try:
        conn = get_sentinel_connection()
        cursor = conn.cursor()
        
        # Get CPU summary
        cursor.execute("""
            SELECT 
                AVG(c.usage_percent) as avg_cpu,
                MAX(c.usage_percent) as peak_cpu,
                AVG(c.temperature_celsius) as avg_cpu_temp
            FROM system_snapshots s
            JOIN cpu_metrics c ON s.id = c.snapshot_id
            WHERE s.timestamp > datetime('now', '-' || ? || ' hours')
        """, (hours,))
        cpu_summary = dict(cursor.fetchone())
        
        # Get RAM summary
        cursor.execute("""
            SELECT 
                AVG(r.usage_percent) as avg_ram,
                MAX(r.usage_percent) as peak_ram,
                AVG(r.used_gb) as avg_ram_used
            FROM system_snapshots s
            JOIN ram_metrics r ON s.id = r.snapshot_id
            WHERE s.timestamp > datetime('now', '-' || ? || ' hours')
        """, (hours,))
        ram_summary = dict(cursor.fetchone())
        
        # Get snapshot count
        cursor.execute("""
            SELECT COUNT(*) as data_points
            FROM system_snapshots
            WHERE timestamp > datetime('now', '-' || ? || ' hours')
        """, (hours,))
        count = cursor.fetchone()['data_points']
        
        conn.close()
        
        return {
            **cpu_summary,
            **ram_summary,
            'data_points': count,
            'hours': hours
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
