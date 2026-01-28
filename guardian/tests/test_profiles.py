"""Tests for Guardian profile system."""
import pytest
from pathlib import Path

from profiles.profile_manager import ProfileManager
from profiles.gaming_profile import create_gaming_profile
from profiles.work_profile import create_work_profile
from profiles.power_saver_profile import create_power_saver_profile
from models import Profile


class TestProfileManager:
    """Test profile manager."""
    
    def test_create_profile_manager(self, temp_dir):
        """Test profile manager creation."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        
        assert manager.profiles_dir.exists()
        assert manager.active_profile is None
    
    def test_save_and_load_profile(self, temp_dir, sample_profile):
        """Test saving and loading profiles."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        
        # Save profile
        success = manager.save_profile(sample_profile)
        assert success is True
        
        # Load profile
        loaded = manager.load_profile(sample_profile.name)
        assert loaded is not None
        assert loaded.name == sample_profile.name
        assert loaded.description == sample_profile.description
    
    def test_get_profile(self, temp_dir, sample_profile):
        """Test getting a profile."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.save_profile(sample_profile)
        
        profile = manager.get_profile(sample_profile.name)
        
        assert profile is not None
        assert profile.name == sample_profile.name
    
    def test_list_profiles(self, temp_dir, sample_profile):
        """Test listing profiles."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.save_profile(sample_profile)
        
        profiles = manager.list_profiles()
        
        assert len(profiles) > 0
        assert sample_profile.name in profiles
    
    def test_activate_profile(self, temp_dir, sample_profile):
        """Test profile activation."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.save_profile(sample_profile)
        
        success = manager.activate_profile(sample_profile.name)
        
        assert success is True
        assert manager.active_profile == sample_profile.name
    
    def test_activate_nonexistent_profile(self, temp_dir):
        """Test activating nonexistent profile."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        
        success = manager.activate_profile("nonexistent")
        
        assert success is False
    
    def test_deactivate_profile(self, temp_dir, sample_profile):
        """Test profile deactivation."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.save_profile(sample_profile)
        manager.activate_profile(sample_profile.name)
        
        manager.deactivate_profile()
        
        assert manager.active_profile is None
    
    def test_get_active_profile(self, temp_dir, sample_profile):
        """Test getting active profile."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.save_profile(sample_profile)
        manager.activate_profile(sample_profile.name)
        
        active = manager.get_active_profile()
        
        assert active is not None
        assert active.name == sample_profile.name


class TestBuiltInProfiles:
    """Test built-in profiles."""
    
    def test_gaming_profile(self):
        """Test gaming profile creation."""
        profile = create_gaming_profile()
        
        assert profile.name == "gaming"
        assert len(profile.actions) > 0
        assert profile.enabled is True
        assert profile.rollback_on_exit is True
    
    def test_work_profile(self):
        """Test work profile creation."""
        profile = create_work_profile()
        
        assert profile.name == "work"
        assert len(profile.actions) > 0
        assert profile.enabled is True
    
    def test_power_saver_profile(self):
        """Test power saver profile creation."""
        profile = create_power_saver_profile()
        
        assert profile.name == "power_saver"
        assert len(profile.actions) > 0
        assert profile.enabled is True
    
    def test_create_default_profiles(self, temp_dir):
        """Test creating all default profiles."""
        manager = ProfileManager(profiles_dir=temp_dir / "profiles")
        manager.create_default_profiles()
        
        profiles = manager.list_profiles()
        
        assert "gaming" in profiles
        assert "work" in profiles
        assert "power_saver" in profiles
