"""Process correlation tracking."""
import json
from pathlib import Path
from typing import Dict, List, Tuple
import sqlite3
import numpy as np
from loguru import logger


class CorrelationTracker:
    """Track correlations between processes and system metrics."""
    
    def __init__(self, db_path: Path):
        """Initialize correlation tracker.
        
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
            CREATE TABLE IF NOT EXISTS process_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_a TEXT NOT NULL,
                process_b TEXT NOT NULL,
                correlation_score REAL NOT NULL,
                co_occurrence_count INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(process_a, process_b)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metric_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_a TEXT NOT NULL,
                metric_b TEXT NOT NULL,
                correlation_score REAL NOT NULL,
                sample_count INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_a, metric_b)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Correlation tracker database initialized")
    
    def update_process_correlation(
        self,
        process_a: str,
        process_b: str,
        correlation_score: float
    ):
        """Update correlation between two processes.
        
        Args:
            process_a: First process name
            process_b: Second process name
            correlation_score: Correlation score (-1 to 1)
        """
        # Ensure consistent ordering
        if process_a > process_b:
            process_a, process_b = process_b, process_a
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO process_correlations 
            (process_a, process_b, correlation_score)
            VALUES (?, ?, ?)
            ON CONFLICT(process_a, process_b) DO UPDATE SET
                correlation_score = ?,
                co_occurrence_count = co_occurrence_count + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (process_a, process_b, correlation_score, correlation_score))
        
        conn.commit()
        conn.close()
    
    def update_metric_correlation(
        self,
        metric_a: str,
        metric_b: str,
        correlation_score: float
    ):
        """Update correlation between two metrics.
        
        Args:
            metric_a: First metric name
            metric_b: Second metric name
            correlation_score: Correlation score (-1 to 1)
        """
        # Ensure consistent ordering
        if metric_a > metric_b:
            metric_a, metric_b = metric_b, metric_a
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO metric_correlations 
            (metric_a, metric_b, correlation_score)
            VALUES (?, ?, ?)
            ON CONFLICT(metric_a, metric_b) DO UPDATE SET
                correlation_score = ?,
                sample_count = sample_count + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (metric_a, metric_b, correlation_score, correlation_score))
        
        conn.commit()
        conn.close()
    
    def get_process_correlations(
        self,
        process_name: str,
        min_score: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Get processes correlated with a given process.
        
        Args:
            process_name: Process name
            min_score: Minimum correlation score
            
        Returns:
            List of (process_name, correlation_score) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN process_a = ? THEN process_b
                    ELSE process_a
                END as other_process,
                correlation_score
            FROM process_correlations
            WHERE (process_a = ? OR process_b = ?)
                AND correlation_score >= ?
            ORDER BY correlation_score DESC
        """, (process_name, process_name, process_name, min_score))
        
        correlations = cursor.fetchall()
        conn.close()
        
        return correlations
    
    def get_metric_correlations(
        self,
        metric_name: str,
        min_score: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Get metrics correlated with a given metric.
        
        Args:
            metric_name: Metric name
            min_score: Minimum correlation score
            
        Returns:
            List of (metric_name, correlation_score) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN metric_a = ? THEN metric_b
                    ELSE metric_a
                END as other_metric,
                correlation_score
            FROM metric_correlations
            WHERE (metric_a = ? OR metric_b = ?)
                AND correlation_score >= ?
            ORDER BY correlation_score DESC
        """, (metric_name, metric_name, metric_name, min_score))
        
        correlations = cursor.fetchall()
        conn.close()
        
        return correlations
    
    def get_top_process_pairs(self, limit: int = 10) -> List[Dict]:
        """Get top correlated process pairs.
        
        Args:
            limit: Maximum number of pairs to return
            
        Returns:
            List of correlation dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT process_a, process_b, correlation_score, co_occurrence_count
            FROM process_correlations
            ORDER BY correlation_score DESC
            LIMIT ?
        """, (limit,))
        
        pairs = []
        for row in cursor.fetchall():
            pairs.append({
                "process_a": row[0],
                "process_b": row[1],
                "correlation": row[2],
                "occurrences": row[3]
            })
        
        conn.close()
        return pairs
    
    def calculate_correlation_matrix(
        self,
        data: np.ndarray,
        labels: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix from data.
        
        Args:
            data: Data matrix (samples x features)
            labels: Feature labels
            
        Returns:
            Correlation matrix as nested dictionary
        """
        corr_matrix = np.corrcoef(data.T)
        
        result = {}
        for i, label_a in enumerate(labels):
            result[label_a] = {}
            for j, label_b in enumerate(labels):
                if i != j:
                    result[label_a][label_b] = float(corr_matrix[i, j])
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get correlation statistics.
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM process_correlations")
        process_pairs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metric_correlations")
        metric_pairs = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(correlation_score) FROM process_correlations
            WHERE correlation_score > 0
        """)
        avg_process_corr = cursor.fetchone()[0] or 0.0
        
        cursor.execute("""
            SELECT AVG(correlation_score) FROM metric_correlations
            WHERE correlation_score > 0
        """)
        avg_metric_corr = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "process_pairs": process_pairs,
            "metric_pairs": metric_pairs,
            "avg_process_correlation": float(avg_process_corr),
            "avg_metric_correlation": float(avg_metric_corr)
        }
