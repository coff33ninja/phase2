"""Collect and store user feedback."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from config import config


class FeedbackCollector:
    """Collect user feedback on Sage responses."""
    
    def __init__(self):
        """Initialize feedback collector."""
        self.db_path = config.feedback_db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize feedback database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_id INTEGER,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                user_action TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_feedback 
            ON feedback(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_action 
            ON feedback(user_action)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Feedback collector database initialized")
    
    def record_feedback(
        self,
        session_id: str,
        query: str,
        response: str,
        user_action: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> int:
        """Record user feedback.
        
        Args:
            session_id: Session identifier
            query: User query
            response: Sage response
            user_action: User action (accepted, rejected, modified, ignored)
            rating: Optional rating (1-5)
            comment: Optional comment
            context: Optional context dictionary
            
        Returns:
            Feedback ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO feedback 
                (session_id, query, response, user_action, rating, comment, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, query, response, user_action, rating, comment, context_json))
            
            feedback_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded feedback: {user_action} (ID: {feedback_id})")
            return feedback_id
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return -1
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics.
        
        Returns:
            Dictionary of statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total feedback count
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total = cursor.fetchone()[0]
            
            # Action breakdown
            cursor.execute("""
                SELECT user_action, COUNT(*) 
                FROM feedback 
                GROUP BY user_action
            """)
            actions = dict(cursor.fetchall())
            
            # Average rating
            cursor.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0] or 0.0
            
            # Acceptance rate
            accepted = actions.get("accepted", 0)
            acceptance_rate = (accepted / total * 100) if total > 0 else 0.0
            
            conn.close()
            
            return {
                "total_feedback": total,
                "actions": actions,
                "avg_rating": round(avg_rating, 2),
                "acceptance_rate": round(acceptance_rate, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {}
    
    def get_recent_feedback(self, limit: int = 10) -> list:
        """Get recent feedback entries.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of feedback entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, query, user_action, rating, created_at
                FROM feedback
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            feedback = []
            for row in cursor.fetchall():
                feedback.append({
                    "session_id": row[0],
                    "query": row[1],
                    "user_action": row[2],
                    "rating": row[3],
                    "created_at": row[4]
                })
            
            conn.close()
            return feedback
            
        except Exception as e:
            logger.error(f"Error getting recent feedback: {e}")
            return []
