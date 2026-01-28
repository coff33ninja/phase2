"""Update Oracle models based on feedback."""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from config import config


class ModelUpdater:
    """Send feedback to Oracle for model improvement."""
    
    def __init__(self):
        """Initialize model updater."""
        self.oracle_db = config.oracle_patterns_db_path
    
    def send_feedback_to_oracle(
        self,
        feedback_id: int,
        query: str,
        response: str,
        user_action: str,
        context: Optional[Dict] = None
    ) -> bool:
        """Send feedback to Oracle for model updates.
        
        Args:
            feedback_id: Feedback identifier
            query: User query
            response: Sage response
            user_action: User action (accepted, rejected, modified, ignored)
            context: Optional context dictionary
            
        Returns:
            True if feedback was sent successfully
        """
        if not self.oracle_db.exists():
            logger.warning(f"Oracle database not found: {self.oracle_db}")
            return False
        
        try:
            conn = sqlite3.connect(self.oracle_db)
            cursor = conn.cursor()
            
            # Create feedback table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sage_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    user_action TEXT NOT NULL,
                    context TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert feedback
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO sage_feedback 
                (feedback_id, query, response, user_action, context)
                VALUES (?, ?, ?, ?, ?)
            """, (feedback_id, query, response, user_action, context_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sent feedback {feedback_id} to Oracle")
            return True
            
        except Exception as e:
            logger.error(f"Error sending feedback to Oracle: {e}")
            return False
    
    def get_unprocessed_feedback_count(self) -> int:
        """Get count of unprocessed feedback in Oracle.
        
        Returns:
            Number of unprocessed feedback entries
        """
        if not self.oracle_db.exists():
            return 0
        
        try:
            conn = sqlite3.connect(self.oracle_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM sage_feedback
                WHERE processed = FALSE
            """)
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting unprocessed feedback count: {e}")
            return 0
    
    def mark_feedback_processed(self, feedback_id: int) -> bool:
        """Mark feedback as processed in Oracle.
        
        Args:
            feedback_id: Feedback identifier
            
        Returns:
            True if marked successfully
        """
        if not self.oracle_db.exists():
            return False
        
        try:
            conn = sqlite3.connect(self.oracle_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sage_feedback
                SET processed = TRUE
                WHERE feedback_id = ?
            """, (feedback_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Marked feedback {feedback_id} as processed")
            return True
            
        except Exception as e:
            logger.error(f"Error marking feedback as processed: {e}")
            return False
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback sent to Oracle.
        
        Returns:
            Dictionary with feedback statistics
        """
        if not self.oracle_db.exists():
            return {
                "total": 0,
                "processed": 0,
                "pending": 0
            }
        
        try:
            conn = sqlite3.connect(self.oracle_db)
            cursor = conn.cursor()
            
            # Total feedback
            cursor.execute("SELECT COUNT(*) FROM sage_feedback")
            total = cursor.fetchone()[0]
            
            # Processed feedback
            cursor.execute("""
                SELECT COUNT(*) FROM sage_feedback
                WHERE processed = TRUE
            """)
            processed = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total": total,
                "processed": processed,
                "pending": total - processed
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback summary: {e}")
            return {
                "total": 0,
                "processed": 0,
                "pending": 0
            }
