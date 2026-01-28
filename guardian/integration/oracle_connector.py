"""Oracle connector for getting ML patterns and predictions."""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from config import config


class OracleConnector:
    """Connect to Oracle for ML patterns and predictions."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize Oracle connector.
        
        Args:
            db_path: Path to Oracle database (defaults to config)
        """
        self.db_path = db_path or config.oracle_db_path
        
        if not self.db_path.exists():
            logger.warning(f"Oracle database not found: {self.db_path}")
    
    def get_current_patterns(self) -> List[Dict[str, Any]]:
        """Get current usage patterns from Oracle.
        
        Returns:
            List of pattern dictionaries
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent patterns
            cursor.execute("""
                SELECT * FROM patterns
                WHERE timestamp > datetime('now', '-1 hour')
                ORDER BY confidence DESC
                LIMIT 10
            """)
            
            patterns = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(patterns)} patterns from Oracle")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get patterns from Oracle: {e}")
            return []
    
    def get_predictions(self, metric: str, horizon_minutes: int = 30) -> Optional[Dict[str, Any]]:
        """Get predictions for a specific metric.
        
        Args:
            metric: Metric name (cpu_usage, ram_usage, etc.)
            horizon_minutes: Prediction horizon in minutes
            
        Returns:
            Prediction dictionary or None
        """
        if not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest prediction
            cursor.execute("""
                SELECT * FROM predictions
                WHERE metric = ? AND horizon_minutes = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (metric, horizon_minutes))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                prediction = dict(row)
                logger.info(f"Retrieved prediction for {metric}: {prediction}")
                return prediction
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get predictions from Oracle: {e}")
            return None
    
    def get_anomalies(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent anomalies detected by Oracle.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of anomaly dictionaries
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent anomalies
            cursor.execute("""
                SELECT * FROM anomalies
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY severity DESC, timestamp DESC
                LIMIT 20
            """, (f'-{hours}',))
            
            anomalies = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(anomalies)} anomalies from Oracle")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to get anomalies from Oracle: {e}")
            return []
    
    def get_behavior_profile(self, profile_type: str = "current") -> Optional[Dict[str, Any]]:
        """Get behavior profile from Oracle.
        
        Args:
            profile_type: Profile type (current, gaming, work, etc.)
            
        Returns:
            Profile dictionary or None
        """
        if not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get behavior profile
            cursor.execute("""
                SELECT * FROM behavior_profiles
                WHERE profile_type = ?
                ORDER BY updated_at DESC
                LIMIT 1
            """, (profile_type,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                profile = dict(row)
                logger.info(f"Retrieved behavior profile: {profile_type}")
                return profile
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get behavior profile from Oracle: {e}")
            return None
    
    def send_feedback(self, action_id: str, success: bool, impact: Dict[str, Any]):
        """Send action feedback to Oracle for model improvement.
        
        Args:
            action_id: Action identifier
            success: Whether action was successful
            impact: Impact metrics dictionary
        """
        if not self.db_path.exists():
            logger.warning("Cannot send feedback: Oracle database not found")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert feedback
            cursor.execute("""
                INSERT INTO action_feedback (action_id, success, impact, timestamp)
                VALUES (?, ?, ?, ?)
            """, (action_id, success, str(impact), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sent feedback to Oracle for action {action_id}")
            
        except Exception as e:
            logger.error(f"Failed to send feedback to Oracle: {e}")
