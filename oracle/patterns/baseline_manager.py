"""Dynamic baseline calculation and management."""
import json
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from loguru import logger


class BaselineManager:
    """Manage dynamic baselines for system metrics."""
    
    def __init__(self, db_path: Path):
        """Initialize baseline manager.
        
        Args:
            db_path: Path to pattern database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                time_context TEXT NOT NULL,
                baseline_value REAL NOT NULL,
                std_deviation REAL NOT NULL,
                min_value REAL NOT NULL,
                max_value REAL NOT NULL,
                sample_count INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_name, time_context)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metric_name 
            ON baselines(metric_name)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Baseline manager database initialized")
    
    def update_baseline(
        self,
        metric_name: str,
        time_context: str,
        values: List[float]
    ):
        """Update baseline for a metric.
        
        Args:
            metric_name: Name of the metric
            time_context: Time context (e.g., 'weekday_morning', 'weekend_evening')
            values: List of observed values
        """
        if not values:
            return
        
        values_array = np.array(values)
        baseline = float(np.mean(values_array))
        std_dev = float(np.std(values_array))
        min_val = float(np.min(values_array))
        max_val = float(np.max(values_array))
        sample_count = len(values)
        
        # Calculate confidence based on sample count
        confidence = min(1.0, sample_count / 1000.0)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO baselines 
            (metric_name, time_context, baseline_value, std_deviation,
             min_value, max_value, sample_count, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(metric_name, time_context) DO UPDATE SET
                baseline_value = ?,
                std_deviation = ?,
                min_value = ?,
                max_value = ?,
                sample_count = sample_count + ?,
                confidence = ?,
                updated_at = CURRENT_TIMESTAMP
        """, (
            metric_name, time_context, baseline, std_dev,
            min_val, max_val, sample_count, confidence,
            baseline, std_dev, min_val, max_val, sample_count, confidence
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated baseline: {metric_name} - {time_context}")
    
    def get_baseline(
        self,
        metric_name: str,
        time_context: str
    ) -> Optional[Dict]:
        """Get baseline for a metric.
        
        Args:
            metric_name: Name of the metric
            time_context: Time context
            
        Returns:
            Baseline data or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT baseline_value, std_deviation, min_value, max_value,
                   sample_count, confidence, updated_at
            FROM baselines
            WHERE metric_name = ? AND time_context = ?
        """, (metric_name, time_context))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "baseline": row[0],
                "std_deviation": row[1],
                "min_value": row[2],
                "max_value": row[3],
                "sample_count": row[4],
                "confidence": row[5],
                "updated_at": row[6]
            }
        return None
    
    def get_all_baselines(self, metric_name: str) -> List[Dict]:
        """Get all baselines for a metric across time contexts.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            List of baseline data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT time_context, baseline_value, std_deviation,
                   min_value, max_value, confidence
            FROM baselines
            WHERE metric_name = ?
            ORDER BY time_context
        """, (metric_name,))
        
        baselines = []
        for row in cursor.fetchall():
            baselines.append({
                "time_context": row[0],
                "baseline": row[1],
                "std_deviation": row[2],
                "min_value": row[3],
                "max_value": row[4],
                "confidence": row[5]
            })
        
        conn.close()
        return baselines
    
    def is_anomaly(
        self,
        metric_name: str,
        time_context: str,
        value: float,
        std_threshold: float = 3.0
    ) -> bool:
        """Check if a value is anomalous based on baseline.
        
        Args:
            metric_name: Name of the metric
            time_context: Time context
            value: Value to check
            std_threshold: Number of standard deviations for anomaly
            
        Returns:
            True if anomalous, False otherwise
        """
        baseline = self.get_baseline(metric_name, time_context)
        
        if not baseline or baseline['confidence'] < 0.5:
            return False
        
        deviation = abs(value - baseline['baseline'])
        threshold = std_threshold * baseline['std_deviation']
        
        return deviation > threshold
    
    def get_expected_range(
        self,
        metric_name: str,
        time_context: str,
        std_multiplier: float = 2.0
    ) -> Optional[tuple]:
        """Get expected range for a metric.
        
        Args:
            metric_name: Name of the metric
            time_context: Time context
            std_multiplier: Standard deviation multiplier
            
        Returns:
            Tuple of (min, max) or None
        """
        baseline = self.get_baseline(metric_name, time_context)
        
        if not baseline:
            return None
        
        margin = std_multiplier * baseline['std_deviation']
        min_expected = baseline['baseline'] - margin
        max_expected = baseline['baseline'] + margin
        
        return (min_expected, max_expected)
    
    def get_time_context(self, timestamp: datetime = None) -> str:
        """Get time context string for a timestamp.
        
        Args:
            timestamp: Timestamp (defaults to now)
            
        Returns:
            Time context string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        is_weekend = timestamp.weekday() >= 5
        hour = timestamp.hour
        
        if hour < 6:
            time_of_day = "night"
        elif hour < 12:
            time_of_day = "morning"
        elif hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"
        
        day_type = "weekend" if is_weekend else "weekday"
        
        return f"{day_type}_{time_of_day}"
    
    def get_statistics(self) -> Dict:
        """Get baseline statistics.
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM baselines")
        total_baselines = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT metric_name) FROM baselines")
        unique_metrics = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM baselines")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(sample_count) FROM baselines")
        total_samples = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_baselines": total_baselines,
            "unique_metrics": unique_metrics,
            "avg_confidence": float(avg_confidence),
            "total_samples": total_samples
        }
