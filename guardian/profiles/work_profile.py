"""Work productivity profile."""
from models import Profile


def create_work_profile() -> Profile:
    """Create work productivity profile.
    
    Returns:
        Work Profile instance
    """
    return Profile(
        name="work",
        description="Optimize system for work productivity",
        trigger="work_hours",
        actions=[
            {
                "type": "close_process",
                "target": "Steam.exe",
                "description": "Close Steam during work hours"
            },
            {
                "type": "close_process",
                "target": "EpicGamesLauncher.exe",
                "description": "Close Epic Games Launcher"
            },
            {
                "type": "power_plan",
                "parameters": {"mode": "balanced"},
                "description": "Switch to balanced power plan"
            }
        ],
        schedule="weekdays 9:00-17:00",
        rollback_on_exit=False,
        enabled=True
    )
