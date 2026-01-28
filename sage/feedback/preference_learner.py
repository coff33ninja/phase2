"""Learn user preferences from feedback."""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
from loguru import logger

from config import config


class PreferenceLearner:
    """Learn and store user preferences from feedback patterns."""
    
    def __init__(self):
        """Initialize preference learner."""
        self.db_path = config.feedback_db_path
        self._initialize_preferences_table()
    
    def _initialize_preferences_table(self):
        """Initialize preferences table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    sample_count INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing preferences table: {e}")
    
    def analyze_feedback_patterns(self) -> Dict:
        """Analyze feedback to learn user preferences.
        
        Returns:
            Dictionary of learned preferences
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all feedback
            cursor.execute("""
                SELECT user_action, rating, comment, context
                FROM feedback
            """)
            
            feedback_data = cursor.fetchall()
            conn.close()
            
            if not feedback_data:
                return {}
            
            # Analyze patterns
            preferences = {}
            
            # 1. Preferred detail level (from ratings and actions)
            detail_preference = self._analyze_detail_preference(feedback_data)
            if detail_preference:
                preferences["detail_level"] = detail_preference
            
            # 2. Action preferences (auto vs manual)
            action_preference = self._analyze_action_preference(feedback_data)
            if action_preference:
                preferences["action_style"] = action_preference
            
            # 3. Response style (technical vs simple)
            style_preference = self._analyze_style_preference(feedback_data)
            if style_preference:
                preferences["response_style"] = style_preference
            
            # 4. Notification preferences
            notification_preference = self._analyze_notification_preference(feedback_data)
            if notification_preference:
                preferences["notification_style"] = notification_preference
            
            # Save learned preferences
            for key, value in preferences.items():
                self._save_preference(key, value)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {e}")
            return {}
    
    def _analyze_detail_preference(self, feedback_data: List) -> Optional[Dict]:
        """Analyze preferred detail level."""
        # Count high ratings by detail level
        detail_ratings = {"brief": [], "moderate": [], "detailed": []}
        
        for action, rating, comment, context in feedback_data:
            if rating and rating >= 4:
                # Try to infer detail level from context
                if context:
                    try:
                        ctx = json.loads(context)
                        detail = ctx.get("detail_level", "moderate")
                        detail_ratings[detail].append(rating)
                    except:
                        pass
        
        # Find preferred detail level
        avg_ratings = {
            level: sum(ratings) / len(ratings) if ratings else 0
            for level, ratings in detail_ratings.items()
        }
        
        if max(avg_ratings.values()) > 0:
            preferred = max(avg_ratings.items(), key=lambda x: x[1])[0]
            confidence = avg_ratings[preferred] / 5.0  # Normalize to 0-1
            
            return {
                "value": preferred,
                "confidence": round(confidence, 2),
                "sample_count": len(detail_ratings[preferred])
            }
        
        return None
    
    def _analyze_action_preference(self, feedback_data: List) -> Optional[Dict]:
        """Analyze preferred action style (auto vs manual)."""
        actions = [action for action, _, _, _ in feedback_data]
        
        if not actions:
            return None
        
        # Count accepted vs rejected
        accepted = actions.count("accepted")
        rejected = actions.count("rejected")
        modified = actions.count("modified")
        
        total = len(actions)
        acceptance_rate = accepted / total if total > 0 else 0
        
        # High acceptance = prefers automation
        # Low acceptance = prefers manual control
        if acceptance_rate > 0.7:
            style = "automated"
        elif acceptance_rate < 0.3:
            style = "manual"
        else:
            style = "balanced"
        
        return {
            "value": style,
            "confidence": round(abs(acceptance_rate - 0.5) * 2, 2),
            "sample_count": total
        }
    
    def _analyze_style_preference(self, feedback_data: List) -> Optional[Dict]:
        """Analyze preferred response style."""
        # Analyze comments for style indicators
        comments = [comment for _, _, comment, _ in feedback_data if comment]
        
        if not comments:
            return None
        
        technical_keywords = ["technical", "detailed", "specific", "precise"]
        simple_keywords = ["simple", "easy", "clear", "plain"]
        
        technical_count = sum(
            1 for comment in comments
            if any(kw in comment.lower() for kw in technical_keywords)
        )
        simple_count = sum(
            1 for comment in comments
            if any(kw in comment.lower() for kw in simple_keywords)
        )
        
        if technical_count > simple_count:
            style = "technical"
            confidence = technical_count / len(comments)
        elif simple_count > technical_count:
            style = "simple"
            confidence = simple_count / len(comments)
        else:
            style = "balanced"
            confidence = 0.5
        
        return {
            "value": style,
            "confidence": round(confidence, 2),
            "sample_count": len(comments)
        }
    
    def _analyze_notification_preference(self, feedback_data: List) -> Optional[Dict]:
        """Analyze notification preferences."""
        # Default to proactive based on acceptance rate
        actions = [action for action, _, _, _ in feedback_data]
        
        if not actions:
            return None
        
        accepted = actions.count("accepted")
        total = len(actions)
        acceptance_rate = accepted / total if total > 0 else 0
        
        # High acceptance = likes proactive notifications
        if acceptance_rate > 0.6:
            style = "proactive"
        elif acceptance_rate < 0.4:
            style = "reactive"
        else:
            style = "balanced"
        
        return {
            "value": style,
            "confidence": round(abs(acceptance_rate - 0.5) * 2, 2),
            "sample_count": total
        }
    
    def _save_preference(self, key: str, value: Dict):
        """Save learned preference to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences
                (preference_key, preference_value, confidence, sample_count, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                key,
                json.dumps(value),
                value.get("confidence", 0.5),
                value.get("sample_count", 0)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved preference: {key} = {value['value']}")
            
        except Exception as e:
            logger.error(f"Error saving preference: {e}")
    
    def get_preferences(self) -> Dict:
        """Get all learned preferences.
        
        Returns:
            Dictionary of preferences
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT preference_key, preference_value, confidence, sample_count
                FROM user_preferences
            """)
            
            preferences = {}
            for row in cursor.fetchall():
                try:
                    value = json.loads(row[1])
                    preferences[row[0]] = {
                        **value,
                        "confidence": row[2],
                        "sample_count": row[3]
                    }
                except:
                    pass
            
            conn.close()
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            return {}
    
    def get_preference(self, key: str) -> Optional[Dict]:
        """Get specific preference.
        
        Args:
            key: Preference key
            
        Returns:
            Preference value or None
        """
        preferences = self.get_preferences()
        return preferences.get(key)
