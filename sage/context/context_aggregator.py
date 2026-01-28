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
            Dictionary containing system state, patterns, anomalies, predictions, and training status
        """
        context = {
            "system_state": self._get_current_state(),
            "patterns": self._get_learned_patterns(),
            "anomalies": self._get_recent_anomalies(),
            "predictions": self._get_predictions(),
            "training_status": self._get_training_status()
        }
        
        return context
    
    def _get_training_status(self) -> Dict:
        """Get Oracle training readiness status.
        
        Returns:
            Training status information
        """
        status = {
            "oracle_trained": self.oracle_db.exists(),
            "sentinel_active": self.sentinel_db.exists(),
            "ready_for_training": False,
            "data_collection_hours": 0,
            "snapshot_count": 0,
            "min_hours_needed": 1.0,
            "min_samples_needed": 1000,
            "recommended_hours": 24.0
        }
        
        if not self.sentinel_db.exists():
            return status
        
        try:
            conn = sqlite3.connect(self.sentinel_db)
            cursor = conn.cursor()
            
            # Get snapshot count
            cursor.execute("SELECT COUNT(*) FROM system_snapshots")
            status["snapshot_count"] = cursor.fetchone()[0]
            
            # Get time range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
            min_time, max_time = cursor.fetchone()
            
            if min_time and max_time:
                start = datetime.fromisoformat(min_time)
                end = datetime.fromisoformat(max_time)
                duration_hours = (end - start).total_seconds() / 3600
                status["data_collection_hours"] = round(duration_hours, 1)
                
                # Check if ready for training
                if (duration_hours >= status["min_hours_needed"] and 
                    status["snapshot_count"] >= status["min_samples_needed"]):
                    status["ready_for_training"] = True
            
            conn.close()
        except Exception as e:
            logger.error(f"Error getting training status: {e}")
        
        return status
    
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
            
            # Get most recent metrics from Sentinel's normalized schema
            cursor.execute("""
                SELECT 
                    c.usage_percent as cpu_percent,
                    r.used_gb as ram_used_gb,
                    g.usage_percent as gpu_usage,
                    d.read_mbps as disk_read_mb,
                    d.write_mbps as disk_write_mb,
                    n.download_mbps as network_recv_mb,
                    n.upload_mbps as network_sent_mb
                FROM system_snapshots s
                LEFT JOIN cpu_metrics c ON c.snapshot_id = s.id
                LEFT JOIN ram_metrics r ON r.snapshot_id = s.id
                LEFT JOIN gpu_metrics g ON g.snapshot_id = s.id
                LEFT JOIN disk_metrics d ON d.snapshot_id = s.id
                LEFT JOIN network_metrics n ON n.snapshot_id = s.id
                ORDER BY s.timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "cpu": round(row[0], 1) if row[0] else 0,
                    "ram": round(row[1], 1) if row[1] else 0,
                    "gpu": round(row[2], 1) if row[2] else 0,
                    "disk": {
                        "read_mb": round(row[3], 1) if row[3] else 0,
                        "write_mb": round(row[4], 1) if row[4] else 0
                    },
                    "network": {
                        "recv_mb": round(row[5], 1) if row[5] else 0,
                        "sent_mb": round(row[6], 1) if row[6] else 0
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
