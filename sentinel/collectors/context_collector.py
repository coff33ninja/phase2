"""
System context collector
Collects contextual information about system state and user activity
"""
import psutil
from datetime import datetime
from typing import Optional
from collectors.base import BaseCollector
from models import SystemContext


class ContextCollector(BaseCollector):
    """Collects system context information"""
    
    def __init__(self):
        super().__init__("Context")
        self._idle_threshold_seconds = 300  # 5 minutes
    
    async def collect(self) -> SystemContext:
        """Collect system context"""
        now = datetime.now()
        
        # Determine time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Get day of week
        day_of_week = now.strftime("%A")
        
        # Detect user activity
        user_active = self._is_user_active()
        
        # Detect user action (basic heuristic)
        user_action = self._detect_user_action()
        
        return SystemContext(
            user_active=user_active,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            user_action=user_action
        )
    
    def _is_user_active(self) -> bool:
        """
        Detect if user is actively using the system
        Uses heuristics like recent process activity, network usage, etc.
        """
        try:
            # Check if there are recent user processes
            user_processes = 0
            for proc in psutil.process_iter(['name', 'create_time']):
                try:
                    # Check for common user applications
                    name = proc.info['name'].lower()
                    if any(app in name for app in ['chrome', 'firefox', 'edge', 'code', 'notepad', 
                                                     'explorer', 'discord', 'slack', 'teams']):
                        user_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # If there are active user processes, consider user active
            if user_processes > 0:
                return True
            
            # Check CPU usage as indicator
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 10:  # More than 10% CPU usage
                return True
            
            return False
            
        except Exception:
            return True  # Default to active if we can't determine
    
    def _detect_user_action(self) -> Optional[str]:
        """
        Detect what the user might be doing
        This is a basic heuristic based on running processes
        """
        try:
            actions = []
            
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name'].lower()
                    
                    # Detect common activities
                    if any(browser in name for browser in ['chrome', 'firefox', 'edge', 'brave']):
                        actions.append('browsing')
                    elif any(ide in name for ide in ['code', 'pycharm', 'visual studio', 'sublime']):
                        actions.append('coding')
                    elif any(game in name for game in ['game', 'steam', 'epic']):
                        actions.append('gaming')
                    elif any(media in name for media in ['vlc', 'spotify', 'itunes', 'media player']):
                        actions.append('media')
                    elif any(comm in name for comm in ['discord', 'slack', 'teams', 'zoom', 'skype']):
                        actions.append('communication')
                    elif any(office in name for office in ['word', 'excel', 'powerpoint', 'outlook']):
                        actions.append('office_work')
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Return most common action or None
            if actions:
                # Return the first detected action (could be improved with frequency counting)
                return actions[0]
            
            return None
            
        except Exception:
            return None
