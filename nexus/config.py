"""Configuration management for Nexus."""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusConfig(BaseSettings):
    """Nexus configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8001, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    
    # Integration Paths (absolute paths from project root)
    sentinel_db_path: Path = Field(
        default=Path("../sentinel/data/system_stats.db"),
        description="Sentinel database path"
    )
    oracle_db_path: Path = Field(
        default=Path("../oracle/data/patterns.db"),
        description="Oracle database path"
    )
    oracle_models_path: Path = Field(
        default=Path("../oracle/saved_models"),
        description="Oracle saved models directory"
    )
    sage_db_path: Path = Field(
        default=Path("../sage/data/conversations.db"),
        description="Sage database path"
    )
    guardian_db_path: Path = Field(
        default=Path("../guardian/data/actions.db"),
        description="Guardian database path"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path = Field(default=Path("./logs/nexus.log"), description="Log file path")
    
    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT"
    )
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8001",
        description="Comma-separated CORS origins"
    )
    
    # WebSocket
    ws_heartbeat_interval: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds"
    )
    ws_max_connections: int = Field(
        default=100,
        description="Maximum WebSocket connections"
    )
    
    # Cache
    enable_cache: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=60, description="Cache TTL in seconds")
    
    def __init__(self, **kwargs):
        """Initialize configuration and create directories."""
        super().__init__(**kwargs)
        
        # Create necessary directories
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Resolve paths to absolute
        nexus_dir = Path(__file__).parent
        self.sentinel_db_path = (nexus_dir / self.sentinel_db_path).resolve()
        self.oracle_db_path = (nexus_dir / self.oracle_db_path).resolve()
        self.oracle_models_path = (nexus_dir / self.oracle_models_path).resolve()
        self.sage_db_path = (nexus_dir / self.sage_db_path).resolve()
        self.guardian_db_path = (nexus_dir / self.guardian_db_path).resolve()
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list.
        
        Returns:
            List of CORS origin URLs
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global config instance
config = NexusConfig()
