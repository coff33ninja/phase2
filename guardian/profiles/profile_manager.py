"""Profile manager for automation profiles."""
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from models import Profile


class ProfileManager:
    """Manage automation profiles."""
    
    def __init__(self, profiles_dir: Path = Path("./profiles")):
        """Initialize profile manager.
        
        Args:
            profiles_dir: Directory containing profile files
        """
        self.profiles_dir = profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, Profile] = {}
        self.active_profile: Optional[str] = None
    
    def load_profile(self, profile_name: str) -> Optional[Profile]:
        """Load a profile from file.
        
        Args:
            profile_name: Name of profile to load
            
        Returns:
            Profile instance or None
        """
        profile_file = self.profiles_dir / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            logger.warning(f"Profile file not found: {profile_file}")
            return None
        
        try:
            with open(profile_file, 'r') as f:
                data = yaml.safe_load(f)
            
            profile = Profile(**data)
            self.profiles[profile_name] = profile
            
            logger.info(f"Loaded profile: {profile_name}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
            return None
    
    def save_profile(self, profile: Profile) -> bool:
        """Save a profile to file.
        
        Args:
            profile: Profile to save
            
        Returns:
            True if saved successfully
        """
        profile_file = self.profiles_dir / f"{profile.name}.yaml"
        
        try:
            with open(profile_file, 'w') as f:
                yaml.dump(profile.model_dump(), f, default_flow_style=False)
            
            self.profiles[profile.name] = profile
            logger.info(f"Saved profile: {profile.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile {profile.name}: {e}")
            return False
    
    def get_profile(self, profile_name: str) -> Optional[Profile]:
        """Get a profile by name.
        
        Args:
            profile_name: Profile name
            
        Returns:
            Profile instance or None
        """
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        
        return self.load_profile(profile_name)
    
    def list_profiles(self) -> List[str]:
        """List all available profiles.
        
        Returns:
            List of profile names
        """
        profiles = []
        
        # Get loaded profiles
        profiles.extend(self.profiles.keys())
        
        # Get profiles from disk
        for file in self.profiles_dir.glob("*.yaml"):
            name = file.stem
            if name not in profiles:
                profiles.append(name)
        
        return sorted(profiles)
    
    def activate_profile(self, profile_name: str) -> bool:
        """Activate a profile.
        
        Args:
            profile_name: Profile to activate
            
        Returns:
            True if activated successfully
        """
        profile = self.get_profile(profile_name)
        if not profile:
            logger.error(f"Profile not found: {profile_name}")
            return False
        
        if not profile.enabled:
            logger.warning(f"Profile {profile_name} is disabled")
            return False
        
        self.active_profile = profile_name
        logger.info(f"Activated profile: {profile_name}")
        return True
    
    def deactivate_profile(self):
        """Deactivate current profile."""
        if self.active_profile:
            logger.info(f"Deactivated profile: {self.active_profile}")
            self.active_profile = None
    
    def get_active_profile(self) -> Optional[Profile]:
        """Get currently active profile.
        
        Returns:
            Active profile or None
        """
        if self.active_profile:
            return self.get_profile(self.active_profile)
        return None
    
    def create_default_profiles(self):
        """Create default profiles if they don't exist."""
        from profiles.gaming_profile import create_gaming_profile
        from profiles.work_profile import create_work_profile
        from profiles.power_saver_profile import create_power_saver_profile
        
        # Gaming profile
        if not (self.profiles_dir / "gaming.yaml").exists():
            gaming = create_gaming_profile()
            self.save_profile(gaming)
        
        # Work profile
        if not (self.profiles_dir / "work.yaml").exists():
            work = create_work_profile()
            self.save_profile(work)
        
        # Power saver profile
        if not (self.profiles_dir / "power_saver.yaml").exists():
            power_saver = create_power_saver_profile()
            self.save_profile(power_saver)
        
        logger.info("Created default profiles")
