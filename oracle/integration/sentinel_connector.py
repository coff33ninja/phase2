"""Connector for real-time Sentinel data."""
import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from loguru import logger


class SentinelConnector:
    """Connect to Sentinel for real-time data streaming."""
    
    def __init__(self, sentinel_db_path: Path):
        """Initialize Sentinel connector.
        
        Args:
            sentinel_db_path: Path to Sentinel database
        """
        self.db_path = Path(sentinel_db_path)
        self.is_connected = False
        self.last_snapshot_id = 0
        self._callbacks = []
    
    def connect(self) -> bool:
        """Connect to Sentinel database.
        
        Returns:
            True if successful
        """
        if not self.db_path.exists():
            logger.error(f"Sentinel database not found: {self.db_path}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest snapshot ID
            cursor.execute("SELECT MAX(id) FROM snapshots")
            result = cursor.fetchone()
            self.last_snapshot_id = result[0] if result[0] else 0
            
            conn.close()
            self.is_connected = True
            logger.info("Connected to Sentinel database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Sentinel: {e}")
            return False
    
    def register_callback(self, callback: Callable):
        """Register callback for new data.
        
        Args:
            callback: Function to call with new data
        """
        self._callbacks.append(callback)
    
    def get_latest_snapshot(self) -> Optional[Dict]:
        """Get the latest snapshot from Sentinel.
        
        Returns:
            Latest snapshot data or None
        """
        if not self.is_connected:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, cpu_percent, ram_percent,
                       disk_read_mb, disk_write_mb,
                       network_sent_mb, network_recv_mb
                FROM snapshots
                ORDER BY id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "timestamp": row[1],
                    "cpu_percent": row[2],
                    "ram_percent": row[3],
                    "disk_read_mb": row[4],
                    "disk_write_mb": row[5],
                    "network_sent_mb": row[6],
                    "network_recv_mb": row[7]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest snapshot: {e}")
            return None
    
    def get_new_snapshots(self) -> list:
        """Get new snapshots since last check.
        
        Returns:
            List of new snapshots
        """
        if not self.is_connected:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, cpu_percent, ram_percent,
                       disk_read_mb, disk_write_mb,
                       network_sent_mb, network_recv_mb
                FROM snapshots
                WHERE id > ?
                ORDER BY id
            """, (self.last_snapshot_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            snapshots = []
            for row in rows:
                snapshots.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "cpu_percent": row[2],
                    "ram_percent": row[3],
                    "disk_read_mb": row[4],
                    "disk_write_mb": row[5],
                    "network_sent_mb": row[6],
                    "network_recv_mb": row[7]
                })
                self.last_snapshot_id = row[0]
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to get new snapshots: {e}")
            return []
    
    async def stream_data(self, interval_seconds: int = 60):
        """Stream data from Sentinel continuously.
        
        Args:
            interval_seconds: Polling interval
        """
        if not self.is_connected:
            logger.error("Not connected to Sentinel")
            return
        
        logger.info(f"Starting data stream (interval: {interval_seconds}s)")
        
        while True:
            try:
                new_snapshots = self.get_new_snapshots()
                
                if new_snapshots:
                    logger.info(f"Received {len(new_snapshots)} new snapshots")
                    
                    # Call registered callbacks
                    for callback in self._callbacks:
                        try:
                            callback(new_snapshots)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def get_recent_data(self, minutes: int = 60) -> list:
        """Get recent data from Sentinel.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of snapshots
        """
        if not self.is_connected:
            return []
        
        try:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, cpu_percent, ram_percent,
                       disk_read_mb, disk_write_mb,
                       network_sent_mb, network_recv_mb
                FROM snapshots
                WHERE timestamp >= ?
                ORDER BY timestamp
            """, (cutoff,))
            
            rows = cursor.fetchall()
            conn.close()
            
            snapshots = []
            for row in rows:
                snapshots.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "cpu_percent": row[2],
                    "ram_percent": row[3],
                    "disk_read_mb": row[4],
                    "disk_write_mb": row[5],
                    "network_sent_mb": row[6],
                    "network_recv_mb": row[7]
                })
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to get recent data: {e}")
            return []
    
    def disconnect(self):
        """Disconnect from Sentinel."""
        self.is_connected = False
        logger.info("Disconnected from Sentinel")
