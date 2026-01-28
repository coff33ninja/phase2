"""Configuration management for Oracle."""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class OracleConfig(BaseSettings):
    """Oracle configuration settings."""
    
    # Paths
    sentinel_db_path: Path = Field(
        default=Path("../sentinel/data/system_stats.db"),
        description="Path to Sentinel database"
    )
    model_dir: Path = Field(
        default=Path("saved_models"),
        description="Directory for saved models"
    )
    pattern_db_path: Path = Field(
        default=Path("data/patterns.db"),
        description="Path to pattern database"
    )
    
    # Training Configuration
    training_window_days: int = Field(default=30, ge=1)
    min_training_samples: int = Field(default=1000, ge=100)
    batch_size: int = Field(default=32, ge=1)
    epochs: int = Field(default=50, ge=1)
    learning_rate: float = Field(default=0.001, gt=0)
    
    # Prediction Configuration
    prediction_horizons: List[int] = Field(
        default=[5, 15, 30, 60],
        description="Prediction horizons in minutes"
    )
    confidence_threshold: float = Field(default=0.7, ge=0, le=1)
    
    # Anomaly Detection
    anomaly_contamination: float = Field(default=0.1, ge=0, le=0.5)
    anomaly_threshold: float = Field(default=0.8, ge=0, le=1)
    
    # Performance
    max_inference_time_ms: int = Field(default=100, ge=1)
    model_update_interval_hours: int = Field(default=24, ge=1)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: Path = Field(default=Path("logs/oracle.log"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
config = OracleConfig()
