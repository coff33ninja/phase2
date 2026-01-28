"""Profiles module."""
from profiles.profile_manager import ProfileManager
from profiles.gaming_profile import create_gaming_profile
from profiles.work_profile import create_work_profile
from profiles.power_saver_profile import create_power_saver_profile

__all__ = [
    "ProfileManager",
    "create_gaming_profile",
    "create_work_profile",
    "create_power_saver_profile",
]
