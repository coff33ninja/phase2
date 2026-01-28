"""Data loader for Sentinel database."""
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from loguru import logger


class SentinelDataLoader:
    """Load and prepare data from Sentinel database."""
    
    def __init__(self, db_path: Path):
        """Initialize data loader.
        
        Args:
            db_path: Path to Sentinel database
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Sentinel database not found: {db_path}")
    
    def load_time_series(
        self,
        days: int = 30,
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """Load time series data from Sentinel.
        
        Args:
            days: Number of days to load
            metrics: List of metrics to load (None for all)
            
        Returns:
            DataFrame with time series data
        """
        if metrics is None:
            metrics = ["cpu_percent", "ram_percent", "gpu_percent"]
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        
        # Join system_snapshots with metric tables
        query = """
            SELECT 
                s.timestamp,
                c.usage_percent as cpu_percent,
                r.usage_percent as ram_percent,
                d.read_mbps as disk_read_mb,
                d.write_mbps as disk_write_mb,
                n.download_mbps as network_recv_mb,
                n.upload_mbps as network_sent_mb,
                COALESCE(g.usage_percent, 0) as gpu_percent
            FROM system_snapshots s
            LEFT JOIN cpu_metrics c ON s.id = c.snapshot_id
            LEFT JOIN ram_metrics r ON s.id = r.snapshot_id
            LEFT JOIN disk_metrics d ON s.id = d.snapshot_id
            LEFT JOIN network_metrics n ON s.id = n.snapshot_id
            LEFT JOIN gpu_metrics g ON s.id = g.snapshot_id
            WHERE s.timestamp >= ?
            ORDER BY s.timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        logger.info(f"Loaded {len(df)} samples from Sentinel")
        return df
    
    def create_sequences(
        self,
        data: np.ndarray,
        sequence_length: int = 60,
        prediction_horizons: List[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training.
        
        Args:
            data: Time series data (samples, features)
            sequence_length: Length of input sequences
            prediction_horizons: Prediction horizons in steps
            
        Returns:
            Tuple of (X sequences, y targets)
        """
        if prediction_horizons is None:
            prediction_horizons = [5, 15, 30, 60]
        
        X, y = [], []
        max_horizon = max(prediction_horizons)
        
        for i in range(len(data) - sequence_length - max_horizon):
            X.append(data[i:i + sequence_length])
            
            targets = []
            for horizon in prediction_horizons:
                targets.append(data[i + sequence_length + horizon, 0])
            y.append(targets)
        
        return np.array(X), np.array(y)
    
    def get_statistics(self) -> dict:
        """Get database statistics.
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM system_snapshots")
        total_samples = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
        min_time, max_time = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_samples": total_samples,
            "earliest_timestamp": min_time,
            "latest_timestamp": max_time
        }
