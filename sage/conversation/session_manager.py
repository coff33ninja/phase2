"""Manage conversation sessions."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from config import config


class SessionManager:
    """Manage conversation sessions and history."""
    
    def __init__(self):
        """Initialize session manager."""
        self.db_path = config.conversation_db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize conversation database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON messages(session_id)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Session manager database initialized")
    
    def create_session(self, session_id: str) -> bool:
        """Create a new session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if created successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (session_id)
                VALUES (?)
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created session: {session_id}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Session already exists: {session_id}")
            return False
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        context: Optional[Dict] = None,
        tokens_used: int = 0
    ):
        """Add a message to session.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            context: Optional context dictionary
            tokens_used: Number of tokens used
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO messages 
                (session_id, role, content, context, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, context_json, tokens_used))
            
            # Update session timestamp
            cursor.execute("""
                UPDATE sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get session message history.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role, content, context, tokens_used, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                context = json.loads(row[2]) if row[2] else None
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "context": context,
                    "tokens_used": row[3],
                    "created_at": row[4]
                })
            
            conn.close()
            
            # Return in chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent sessions.
        
        Args:
            limit: Maximum number of sessions
            
        Returns:
            List of sessions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.session_id, s.created_at, s.updated_at,
                       COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "session_id": row[0],
                    "created_at": row[1],
                    "updated_at": row[2],
                    "message_count": row[3]
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []
