"""Gaming optimization profile."""
from models import Profile


def create_gaming_profile() -> Profile:
    """Create gaming optimization profile.
    
    Returns:
        Gaming Profile instance
    """
    return Profile(
        name="gaming",
        description="Optimize system for gaming performance",
        trigger="game_detected",
        actions=[
            {
                "type": "close_process",
                "target": "Discord.exe",
                "description": "Close Discord to free resources"
            },
            {
                "type": "close_process",
                "target": "Spotify.exe",
                "description": "Close Spotify to free resources"
            },
            {
                "type": "close_process",
                "target": "chrome.exe",
                "description": "Close Chrome to free RAM"
            },
            {
                "type": "power_plan",
                "parameters": {"mode": "performance"},
                "description": "Switch to performance power plan"
            },
            {
                "type": "clear_ram",
                "description": "Clear RAM cache"
            }
        ],
        rollback_on_exit=True,
        enabled=True
    )
