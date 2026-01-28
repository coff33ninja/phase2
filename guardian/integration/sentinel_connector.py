"""Sentinel connector for monitoring system state."""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from config import config


class SentinelConnector:
    """Connect to Sentinel for system monitoring."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize Sentinel connector.
        
        Args:
            db_path: Path to Sentinel database (defaults to config)
        """
        self.db_path = db_path or config.sentinel_db_path
        
        if not self.db_path.exists():
            logger.warning(f"Sentinel database not found: {self.db_path}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics from Sentinel.
        
        Returns:
            Dictionary of current metrics
        """
        if not self.db_path.exists():
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest metrics
            cursor.execute("""
                SELECT * FROM system_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                metrics = dict(row)
                logger.debug("Retrieved current metrics from Sentinel")
                return metrics
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get current metrics from Sentinel: {e}")
            return {}
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get current process list from Sentinel.
        
        Returns:
            List of process dictionaries
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest process snapshot
            cursor.execute("""
                SELECT * FROM processes
                WHERE timestamp > datetime('now', '-5 minutes')
                ORDER BY cpu_percent DESC
                LIMIT 50
            """)
            
            processes = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(f"Retrieved {len(processes)} processes from Sentinel")
            return processes
            
        except Exception as e:
            logger.error(f"Failed to get process list from Sentinel: {e}")
            return []
    
    def get_resource_usage(self, resource: str, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get resource usage history from Sentinel.
        
        Args:
            resource: Resource type (cpu, ram, gpu, disk, network)
            minutes: Number of minutes to look back
            
        Returns:
            List of usage data points
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get resource history
            cursor.execute(f"""
                SELECT timestamp, {resource}_usage as value
                FROM system_metrics
                WHERE timestamp > datetime('now', ? || ' minutes')
                ORDER BY timestamp ASC
            """, (f'-{minutes}',))
            
            data = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(f"Retrieved {len(data)} {resource} data points from Sentinel")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get resource usage from Sentinel: {e}")
            return []
    
    def get_system_context(self) -> Dict[str, Any]:
        """Get current system context from Sentinel.
        
        Returns:
            Context dictionary with active window, processes, etc.
        """
        if not self.db_path.exists():
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest context
            cursor.execute("""
                SELECT * FROM system_context
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                context = dict(row)
                logger.debug("Retrieved system context from Sentinel")
                return context
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get system context from Sentinel: {e}")
            return {}
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if any metrics exceed thresholds.
        
        Returns:
            List of threshold violations
        """
        metrics = self.get_current_metrics()
        violations = []
        
        # Check CPU
        if metrics.get('cpu_usage', 0) > 90:
            violations.append({
                'metric': 'cpu_usage',
                'value': metrics['cpu_usage'],
                'threshold': 90,
                'severity': 'high'
            })
        
        # Check RAM
        if metrics.get('ram_usage', 0) > 85:
            violations.append({
                'metric': 'ram_usage',
                'value': metrics['ram_usage'],
                'threshold': 85,
                'severity': 'high'
            })
        
        # Check GPU
        if metrics.get('gpu_usage', 0) > 95:
            violations.append({
                'metric': 'gpu_usage',
                'value': metrics['gpu_usage'],
                'threshold': 95,
                'severity': 'medium'
            })
        
        # Check disk
        if metrics.get('disk_usage', 0) > 90:
            violations.append({
                'metric': 'disk_usage',
                'value': metrics['disk_usage'],
                'threshold': 90,
                'severity': 'medium'
            })
        
        if violations:
            logger.warning(f"Found {len(violations)} threshold violations")
        
        return violations
    
    def is_system_idle(self, threshold_minutes: int = 5) -> bool:
        """Check if system is idle.
        
        Args:
            threshold_minutes: Minutes of low activity to consider idle
            
        Returns:
            True if system is idle
        """
        metrics = self.get_current_metrics()
        
        # Simple idle check based on CPU and input activity
        cpu_usage = metrics.get('cpu_usage', 100)
        
        # System is idle if CPU < 10% and no recent input
        is_idle = cpu_usage < 10
        
        logger.debug(f"System idle check: {is_idle} (CPU: {cpu_usage}%)")
        return is_idle
