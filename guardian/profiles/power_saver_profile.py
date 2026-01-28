"""Power saver profile for battery conservation."""
from models import Profile


def create_power_saver_profile() -> Profile:
    """Create power saver profile.
    
    Returns:
        Power Saver Profile instance
    """
    return Profile(
        name="power_saver",
        description="Conserve battery power",
        trigger="battery_low",
        actions=[
            {
                "type": "power_plan",
                "parameters": {"mode": "power_saver"},
                "description": "Switch to power saver mode"
            },
            {
                "type": "display_brightness",
                "parameters": {"level": 50},
                "description": "Reduce brightness to 50%"
            },
            {
                "type": "close_process",
                "target": "chrome.exe",
                "description": "Close Chrome to save power"
            },
            {
                "type": "close_process",
                "target": "Discord.exe",
                "description": "Close Discord to save power"
            }
        ],
        rollback_on_exit=True,
        enabled=True
    )
