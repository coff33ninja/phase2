"""Aggregate context from Sentinel and Oracle."""
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Optional, List, AsyncIterator
from datetime import datetime, timedelta
from loguru import logger

from config import config


class ContextAggregator:
    """Aggregate context from multiple sources."""
    
    def __init__(self):
        """Initialize context aggregator."""
        self.sentinel_db = config.sentinel_db_path
        self.oracle_db = config.oracle_patterns_db_path
        self._streaming = False
    
    async def get_system_context(self) -> Dict:
        """Get complete system context.
        
        Returns:
            Dictionary containing system state, patterns, anomalies, predictions
        """
        context = {
            "system_state": self._get_current_state(),
            "patterns": self._get_learned_patterns(),
            "anomalies": self._get_recent_anomalies(),
            "predictions": self._get_predictions()
        }
        
        return context
    
    def _get_current_state(self) -> Optional[Dict]:
        """Get current system state from Sentinel.
        
        Returns:
            Current system metrics or None
        """
        if not self.sentinel_db.exists():
            logger.warning(f"Sentinel database not found: {self.sentinel_db}")
            return None
        
        try:
            conn = sqlite3.connect(self.sentinel_db)
            cursor = conn.cursor()
            
            # Get most recent metrics
            cursor.execute("""
                SELECT cpu_percent, ram_used_gb, gpu_usage, 
                       disk_read_mb, disk_write_mb,
                       network_sent_mb, network_recv_mb
                FROM system_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "cpu": round(row[0], 1),
                    "ram": round(row[1], 1),
                    "gpu": round(row[2], 1) if row[2] else 0,
                    "disk": {
                        "read_mb": round(row[3], 1),
                        "write_mb": round(row[4], 1)
                    },
                    "network": {
                        "sent_mb": round(row[5], 1),
                        "recv_mb": round(row[6], 1)
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current state: {e}")
            return None
    
    def _get_learned_patterns(self) -> Optional[Dict]:
        """Get learned patterns from Oracle.
        
        Returns:
            Learned patterns or None
        """
        if not self.oracle_db.exists():
            logger.warning(f"Oracle database not found: {self.oracle_db}")
            return None
        
        try:
            conn = sqlite3.connect(self.oracle_db)
            cursor = conn.cursor()
            
            # Get behavior profiles
            cursor.execute("""
                SELECT profile_name, data
                FROM behavior_profiles
                ORDER BY updated_at DESC
                LIMIT 5
            """)
            
            profiles = {}
            for row in cursor.fetchall():
                profiles[row[0]] = row[1]
            
            conn.close()
            
            return {
                "profiles": profiles,
                "count": len(profiles)
            }
            
        except Exception as e:
            logger.error(f"Error getting patterns: {e}")
            return None
    
    def _get_recent_anomalies(self) -> List[Dict]:
        """Get recent anomalies from Oracle.
        
        Returns:
            List of recent anomalies
        """
        # Placeholder - would query Oracle's anomaly detection results
        return []
    
    def _get_predictions(self) -> Optional[Dict]:
        """Get predictions from Oracle.
        
        Returns:
            Predictions or None
        """
        # Placeholder - would query Oracle's prediction results
        return None

    
    async def stream_system_context(
        self,
        interval_seconds: int = 5
    ) -> AsyncIterator[Dict]:
        """Stream system context updates in real-time.
        
        Args:
            interval_seconds: Update interval in seconds
            
        Yields:
            System context dictionaries
        """
        self._streaming = True
        logger.info(f"Started streaming context (interval: {interval_seconds}s)")
        
        while self._streaming:
            try:
                context = await self.get_system_context()
                yield context
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in context streaming: {e}")
                await asyncio.sleep(1)
    
    def stop_streaming(self):
        """Stop context streaming."""
        self._streaming = False
        logger.info("Stopped streaming context")
    
    def _get_historical_state(self, hours: int = 24) -> Optional[List[Dict]]:
        """Get historical system state.
        
        Args:
            hours: Number of hours of history
            
        Returns:
            List of historical states or None
        """
        if not self.sentinel_db.exists():
            return None
        
        try:
            conn = sqlite3.connect(self.sentinel_db)
            cursor = conn.cursor()
            
            # Calculate time threshold
            threshold = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT timestamp, cpu_percent, ram_used_gb, gpu_usage
                FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, (threshold.isoformat(),))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "timestamp": row[0],
                    "cpu": round(row[1], 1),
                    "ram": round(row[2], 1),
                    "gpu": round(row[3], 1) if row[3] else 0
                })
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"Error getting historical state: {e}")
            return None
    
    def _get_process_info(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get top processes information.
        
        Args:
            limit: Number of top processes
            
        Returns:
            List of process info or None
        """
        if not self.sentinel_db.exists():
            return None
        
        try:
            conn = sqlite3.connect(self.sentinel_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, cpu_percent, memory_mb
                FROM process_metrics
                WHERE timestamp = (SELECT MAX(timestamp) FROM process_metrics)
                ORDER BY cpu_percent DESC
                LIMIT ?
            """, (limit,))
            
            processes = []
            for row in cursor.fetchall():
                processes.append({
                    "name": row[0],
                    "cpu": round(row[1], 1),
                    "memory_mb": round(row[2], 1)
                })
            
            conn.close()
            return processes
            
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return None
