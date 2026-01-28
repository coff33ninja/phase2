"""User behavior profile storage and management."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sqlite3
from loguru import logger


class BehaviorProfileManager:
    """Manage user behavior profiles learned from patterns."""
    
    def __init__(self, db_path: Path):
        """Initialize behavior profile manager.
        
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
            CREATE TABLE IF NOT EXISTS behavior_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT UNIQUE NOT NULL,
                profile_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sample_count INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profile_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observation_data TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES behavior_profiles(id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Behavior profile database initialized")
    
    def create_profile(
        self,
        profile_name: str,
        profile_data: Dict
    ) -> int:
        """Create a new behavior profile.
        
        Args:
            profile_name: Name of the profile
            profile_data: Profile data dictionary
            
        Returns:
            Profile ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO behavior_profiles (profile_name, profile_data)
                VALUES (?, ?)
            """, (profile_name, json.dumps(profile_data)))
            
            profile_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created behavior profile: {profile_name}")
            return profile_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Profile already exists: {profile_name}")
            cursor.execute(
                "SELECT id FROM behavior_profiles WHERE profile_name = ?",
                (profile_name,)
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def update_profile(
        self,
        profile_name: str,
        profile_data: Dict
    ):
        """Update an existing behavior profile.
        
        Args:
            profile_name: Name of the profile
            profile_data: Updated profile data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE behavior_profiles
            SET profile_data = ?,
                updated_at = CURRENT_TIMESTAMP,
                sample_count = sample_count + 1
            WHERE profile_name = ?
        """, (json.dumps(profile_data), profile_name))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated behavior profile: {profile_name}")
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Get a behavior profile by name.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Profile data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT profile_data, sample_count, updated_at
            FROM behavior_profiles
            WHERE profile_name = ?
        """, (profile_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "data": json.loads(row[0]),
                "sample_count": row[1],
                "updated_at": row[2]
            }
        return None
    
    def list_profiles(self) -> List[Dict]:
        """List all behavior profiles.
        
        Returns:
            List of profile summaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT profile_name, sample_count, created_at, updated_at
            FROM behavior_profiles
            ORDER BY updated_at DESC
        """)
        
        profiles = []
        for row in cursor.fetchall():
            profiles.append({
                "name": row[0],
                "sample_count": row[1],
                "created_at": row[2],
                "updated_at": row[3]
            })
        
        conn.close()
        return profiles
    
    def add_observation(
        self,
        profile_name: str,
        observation: Dict
    ):
        """Add an observation to a profile.
        
        Args:
            profile_name: Name of the profile
            observation: Observation data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM behavior_profiles WHERE profile_name = ?",
            (profile_name,)
        )
        row = cursor.fetchone()
        
        if row:
            profile_id = row[0]
            cursor.execute("""
                INSERT INTO profile_observations (profile_id, observation_data)
                VALUES (?, ?)
            """, (profile_id, json.dumps(observation)))
            conn.commit()
        
        conn.close()
    
    def get_profile_statistics(self) -> Dict:
        """Get statistics about all profiles.
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM behavior_profiles")
        total_profiles = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(sample_count) FROM behavior_profiles")
        total_samples = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM profile_observations")
        total_observations = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_profiles": total_profiles,
            "total_samples": total_samples,
            "total_observations": total_observations
        }
