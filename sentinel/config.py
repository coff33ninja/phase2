"""
Configuration management for Phase 2.1
Loads settings from environment variables and provides defaults
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class CollectionIntervals(BaseModel):
    """Data collection interval configuration"""
    high_frequency: int = Field(default=1, description="High-frequency collection (seconds)")
    medium_frequency: int = Field(default=5, description="Medium-frequency collection (seconds)")
    low_frequency: int = Field(default=30, description="Low-frequency collection (seconds)")
    very_low_frequency: int = Field(default=300, description="Very low-frequency collection (seconds)")


class StorageConfig(BaseModel):
    """Storage configuration"""
    database_path: Path = Field(default=Path("./data/system_stats.db"))
    data_retention_days: int = Field(default=90)
    
    def ensure_directories(self):
        """Create necessary directories"""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


class PrivacyConfig(BaseModel):
    """Privacy and security settings"""
    send_to_gemini: bool = Field(default=False)
    anonymize_data: bool = Field(default=True)


class SystemConfig(BaseModel):
    """System resource limits"""
    log_level: str = Field(default="INFO")
    max_cpu_overhead: float = Field(default=2.0, description="Maximum CPU overhead percentage")
    max_ram_mb: int = Field(default=500, description="Maximum RAM usage in MB")


class GeminiConfig(BaseModel):
    """Gemini API configuration"""
    api_key: Optional[str] = Field(default=None)
    model: str = Field(default="gemini-2.5-flash")
    
    @property
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return self.api_key is not None and len(self.api_key) > 0


class Config(BaseModel):
    """Main configuration class"""
    intervals: CollectionIntervals = Field(default_factory=CollectionIntervals)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            intervals=CollectionIntervals(
                high_frequency=int(os.getenv("COLLECTION_INTERVAL_HIGH", "1")),
                medium_frequency=int(os.getenv("COLLECTION_INTERVAL_MEDIUM", "5")),
                low_frequency=int(os.getenv("COLLECTION_INTERVAL_LOW", "30")),
                very_low_frequency=int(os.getenv("COLLECTION_INTERVAL_VERY_LOW", "300"))
            ),
            storage=StorageConfig(
                database_path=Path(os.getenv("DATABASE_PATH", "./data/system_stats.db")),
                data_retention_days=int(os.getenv("DATA_RETENTION_DAYS", "90"))
            ),
            privacy=PrivacyConfig(
                send_to_gemini=os.getenv("SEND_TO_GEMINI", "false").lower() == "true",
                anonymize_data=os.getenv("ANONYMIZE_DATA", "true").lower() == "true"
            ),
            system=SystemConfig(
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                max_cpu_overhead=float(os.getenv("MAX_CPU_OVERHEAD", "2.0")),
                max_ram_mb=int(os.getenv("MAX_RAM_MB", "500"))
            ),
            gemini=GeminiConfig(
                api_key=os.getenv("GEMINI_API_KEY"),
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            )
        )
    
    def initialize(self):
        """Initialize configuration (create directories, etc.)"""
        self.storage.ensure_directories()


# Global configuration instance
config = Config.load()
config.initialize()
