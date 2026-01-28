"""Action logger for audit trail."""
import sqlite3
import json
from pathlib import Path
from typing import List
from datetime import datetime
from loguru import logger as log

from models import ActionLog
from config import config


class ActionLogger:
    """Log all actions for audit trail."""
    
    def __init__(self):
        """Initialize action logger."""
        self.db_path = config.action_log_db
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize action log database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT UNIQUE NOT NULL,
                action_type TEXT NOT NULL,
                target TEXT NOT NULL,
                parameters TEXT,
                status TEXT NOT NULL,
                result TEXT,
                snapshot_id TEXT,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                user_approved BOOLEAN DEFAULT FALSE,
                rolled_back BOOLEAN DEFAULT FALSE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_action_id 
            ON action_logs(action_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON action_logs(status)
        """)
        
        conn.commit()
        conn.close()
        
        log.info("Action logger database initialized")
    
    def log_action(self, action_log: ActionLog):
        """Log an action.
        
        Args:
            action_log: ActionLog instance to save
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO action_logs
                (action_id, action_type, target, parameters, status, result,
                 snapshot_id, started_at, completed_at, user_approved, rolled_back)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action_log.action_id,
                action_log.action_type.value,
                action_log.target,
                json.dumps(action_log.parameters),
                action_log.status.value,
                json.dumps(action_log.result.model_dump()) if action_log.result else None,
                action_log.snapshot_id,
                action_log.started_at.isoformat(),
                action_log.completed_at.isoformat() if action_log.completed_at else None,
                action_log.user_approved,
                action_log.rolled_back
            ))
            
            conn.commit()
            conn.close()
            
            log.debug(f"Logged action {action_log.action_id}")
            
        except Exception as e:
            log.error(f"Failed to log action: {e}")
    
    def get_recent_actions(self, limit: int = 10) -> List[ActionLog]:
        """Get recent actions.
        
        Args:
            limit: Maximum number of actions
            
        Returns:
            List of ActionLog instances
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT action_id, action_type, target, parameters, status,
                       result, snapshot_id, started_at, completed_at,
                       user_approved, rolled_back
                FROM action_logs
                ORDER BY started_at DESC
                LIMIT ?
            """, (limit,))
            
            actions = []
            for row in cursor.fetchall():
                # Parse data
                parameters = json.loads(row[3]) if row[3] else {}
                result_data = json.loads(row[5]) if row[5] else None
                
                action_log = ActionLog(
                    action_id=row[0],
                    action_type=row[1],
                    target=row[2],
                    parameters=parameters,
                    status=row[4],
                    snapshot_id=row[6],
                    started_at=datetime.fromisoformat(row[7]),
                    completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    user_approved=bool(row[9]),
                    rolled_back=bool(row[10])
                )
                
                actions.append(action_log)
            
            conn.close()
            return actions
            
        except Exception as e:
            log.error(f"Failed to get recent actions: {e}")
            return []
    
    def get_action_stats(self) -> dict:
        """Get action statistics.
        
        Returns:
            Dictionary of statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total actions
            cursor.execute("SELECT COUNT(*) FROM action_logs")
            total = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("""
                SELECT COUNT(*) FROM action_logs
                WHERE status = 'success'
            """)
            successful = cursor.fetchone()[0]
            
            # Rollback count
            cursor.execute("""
                SELECT COUNT(*) FROM action_logs
                WHERE rolled_back = TRUE
            """)
            rolled_back = cursor.fetchone()[0]
            
            conn.close()
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                "total_actions": total,
                "successful": successful,
                "rolled_back": rolled_back,
                "success_rate": round(success_rate, 1)
            }
            
        except Exception as e:
            log.error(f"Failed to get action stats: {e}")
            return {}
