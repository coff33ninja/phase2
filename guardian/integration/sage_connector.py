"""Sage connector for getting AI recommendations."""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from config import config


class SageConnector:
    """Connect to Sage for AI recommendations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize Sage connector.
        
        Args:
            db_path: Path to Sage database (defaults to config)
        """
        self.db_path = db_path or config.sage_db_path
        
        if not self.db_path.exists():
            logger.warning(f"Sage database not found: {self.db_path}")
    
    def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations from Sage based on context.
        
        Args:
            context: Context dictionary with system state
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent recommendations
            cursor.execute("""
                SELECT * FROM recommendations
                WHERE timestamp > datetime('now', '-1 hour')
                AND status = 'pending'
                ORDER BY priority DESC, confidence DESC
                LIMIT 10
            """)
            
            recommendations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(recommendations)} recommendations from Sage")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations from Sage: {e}")
            return []
    
    def get_insights(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get proactive insights from Sage.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of insight dictionaries
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent insights
            cursor.execute("""
                SELECT * FROM insights
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY importance DESC, timestamp DESC
                LIMIT 20
            """, (f'-{hours}',))
            
            insights = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(insights)} insights from Sage")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get insights from Sage: {e}")
            return []
    
    def query_sage(self, question: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Query Sage with a question.
        
        Args:
            question: Question to ask Sage
            context: Optional context dictionary
            
        Returns:
            Sage's response or None
        """
        # This would typically call Sage's API or CLI
        # For now, we'll log the query
        logger.info(f"Querying Sage: {question}")
        
        # In a real implementation, this would:
        # 1. Call Sage's query endpoint
        # 2. Wait for response
        # 3. Return the answer
        
        return None
    
    def send_action_result(self, action_id: str, result: Dict[str, Any]):
        """Send action result to Sage for learning.
        
        Args:
            action_id: Action identifier
            result: Result dictionary
        """
        if not self.db_path.exists():
            logger.warning("Cannot send result: Sage database not found")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert action result
            cursor.execute("""
                INSERT INTO action_results (action_id, result, timestamp)
                VALUES (?, ?, ?)
            """, (action_id, str(result), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sent action result to Sage for action {action_id}")
            
        except Exception as e:
            logger.error(f"Failed to send action result to Sage: {e}")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences learned by Sage.
        
        Returns:
            Preferences dictionary
        """
        if not self.db_path.exists():
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get preferences
            cursor.execute("""
                SELECT * FROM user_preferences
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                preferences = dict(row)
                logger.info("Retrieved user preferences from Sage")
                return preferences
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get user preferences from Sage: {e}")
            return {}
