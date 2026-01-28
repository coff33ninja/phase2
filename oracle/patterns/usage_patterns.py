"""Usage pattern storage and retrieval."""
import json
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime
from loguru import logger


class UsagePatternStore:
    """Store and retrieve resource usage patterns."""
    
    def __init__(self, db_path: Path):
        """Initialize usage pattern store.
        
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
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                time_period TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                occurrence_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pattern_type 
            ON usage_patterns(pattern_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_time_period 
            ON usage_patterns(time_period)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Usage pattern database initialized")
    
    def store_pattern(
        self,
        pattern_type: str,
        time_period: str,
        pattern_data: Dict,
        confidence: float = 0.0
    ) -> int:
        """Store a usage pattern.
        
        Args:
            pattern_type: Type of pattern (e.g., 'cpu_usage', 'ram_usage')
            time_period: Time period (e.g., 'morning', 'afternoon', 'weekday')
            pattern_data: Pattern data dictionary
            confidence: Confidence score (0-1)
            
        Returns:
            Pattern ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute("""
            SELECT id, occurrence_count FROM usage_patterns
            WHERE pattern_type = ? AND time_period = ?
        """, (pattern_type, time_period))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing pattern
            pattern_id, count = existing
            cursor.execute("""
                UPDATE usage_patterns
                SET pattern_data = ?,
                    confidence = ?,
                    occurrence_count = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(pattern_data), confidence, count + 1, pattern_id))
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO usage_patterns 
                (pattern_type, time_period, pattern_data, confidence)
                VALUES (?, ?, ?, ?)
            """, (pattern_type, time_period, json.dumps(pattern_data), confidence))
            pattern_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored pattern: {pattern_type} - {time_period}")
        return pattern_id
    
    def get_pattern(
        self,
        pattern_type: str,
        time_period: str
    ) -> Optional[Dict]:
        """Get a specific usage pattern.
        
        Args:
            pattern_type: Type of pattern
            time_period: Time period
            
        Returns:
            Pattern data or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_data, confidence, occurrence_count, updated_at
            FROM usage_patterns
            WHERE pattern_type = ? AND time_period = ?
        """, (pattern_type, time_period))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "data": json.loads(row[0]),
                "confidence": row[1],
                "occurrence_count": row[2],
                "updated_at": row[3]
            }
        return None
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Dict]:
        """Get all patterns of a specific type.
        
        Args:
            pattern_type: Type of pattern
            
        Returns:
            List of patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT time_period, pattern_data, confidence, occurrence_count
            FROM usage_patterns
            WHERE pattern_type = ?
            ORDER BY confidence DESC
        """, (pattern_type,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "time_period": row[0],
                "data": json.loads(row[1]),
                "confidence": row[2],
                "occurrence_count": row[3]
            })
        
        conn.close()
        return patterns
    
    def get_patterns_by_time(self, time_period: str) -> List[Dict]:
        """Get all patterns for a specific time period.
        
        Args:
            time_period: Time period
            
        Returns:
            List of patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, pattern_data, confidence, occurrence_count
            FROM usage_patterns
            WHERE time_period = ?
            ORDER BY confidence DESC
        """, (time_period,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "pattern_type": row[0],
                "data": json.loads(row[1]),
                "confidence": row[2],
                "occurrence_count": row[3]
            })
        
        conn.close()
        return patterns
    
    def get_all_patterns(self) -> List[Dict]:
        """Get all stored patterns.
        
        Returns:
            List of all patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, time_period, pattern_data, 
                   confidence, occurrence_count, updated_at
            FROM usage_patterns
            ORDER BY updated_at DESC
        """)
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "pattern_type": row[0],
                "time_period": row[1],
                "data": json.loads(row[2]),
                "confidence": row[3],
                "occurrence_count": row[4],
                "updated_at": row[5]
            })
        
        conn.close()
        return patterns
    
    def get_statistics(self) -> Dict:
        """Get pattern statistics.
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usage_patterns")
        total_patterns = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT pattern_type) FROM usage_patterns")
        unique_types = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM usage_patterns")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(occurrence_count) FROM usage_patterns")
        total_occurrences = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_patterns": total_patterns,
            "unique_types": unique_types,
            "avg_confidence": float(avg_confidence),
            "total_occurrences": total_occurrences
        }
