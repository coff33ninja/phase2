"""Configuration management for Guardian."""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GuardianConfig(BaseSettings):
    """Guardian configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Automation Settings
    automation_level: str = Field(
        default="semi_auto",
        description="Automation level: manual, semi_auto, fully_auto"
    )
    
    # Safety Settings
    enable_rollback: bool = Field(default=True, description="Enable rollback capability")
    snapshot_before_action: bool = Field(default=True, description="Create snapshot before actions")
    max_rollback_history: int = Field(default=10, description="Maximum rollback history")
    
    # Risk Thresholds
    approval_risk_threshold: str = Field(
        default="medium",
        description="Risk level requiring approval: low, medium, high"
    )
    
    # Protected Processes
    protected_processes: str = Field(
        default="explorer.exe,System,Registry,csrss.exe",
        description="Comma-separated list of protected processes"
    )
    
    # Integration Paths
    sentinel_db_path: Path = Field(
        default=Path("../sentinel/data/system_stats.db"),
        description="Sentinel database path"
    )
    oracle_db_path: Path = Field(
        default=Path("../oracle/data/patterns.db"),
        description="Oracle database path"
    )
    sage_db_path: Path = Field(
        default=Path("../sage/data/conversations.db"),
        description="Sage database path"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path = Field(default=Path("./logs/guardian.log"), description="Log file path")
    action_log_db: Path = Field(
        default=Path("./data/actions.db"),
        description="Action log database"
    )
    
    # Profiles
    default_profile: str = Field(default="balanced", description="Default profile")
    enable_auto_profile_switching: bool = Field(
        default=True,
        description="Enable automatic profile switching"
    )
    
    # Scheduling
    enable_scheduler: bool = Field(default=True, description="Enable task scheduler")
    maintenance_window: str = Field(
        default="02:00-04:00",
        description="Maintenance window (HH:MM-HH:MM)"
    )
    
    # Performance
    max_concurrent_actions: int = Field(
        default=3,
        description="Maximum concurrent actions"
    )
    action_timeout_seconds: int = Field(
        default=30,
        description="Action timeout in seconds"
    )
    
    def __init__(self, **kwargs):
        """Initialize configuration and create directories."""
        super().__init__(**kwargs)
        
        # Create necessary directories
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.action_log_db.parent.mkdir(parents=True, exist_ok=True)
    
    def get_protected_processes_list(self) -> List[str]:
        """Get protected processes as a list.
        
        Returns:
            List of protected process names
        """
        return [p.strip() for p in self.protected_processes.split(",")]
    
    def is_process_protected(self, process_name: str) -> bool:
        """Check if a process is protected.
        
        Args:
            process_name: Process name to check
            
        Returns:
            True if process is protected
        """
        protected = self.get_protected_processes_list()
        return process_name.lower() in [p.lower() for p in protected]


# Global config instance
config = GuardianConfig()
