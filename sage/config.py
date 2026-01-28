"""Configuration management for Sage."""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SageConfig(BaseSettings):
    """Sage configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Gemini API Configuration
    gemini_api_key: str = Field(default="", description="Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model to use")
    
    # Rate Limiting
    max_requests_per_minute: int = Field(default=60, description="Max API requests per minute")
    max_tokens_per_minute: int = Field(default=1000000, description="Max tokens per minute")
    
    # Response Configuration
    max_output_tokens: int = Field(default=2048, description="Max output tokens")
    temperature: float = Field(default=0.7, description="Response temperature")
    top_p: float = Field(default=0.95, description="Top-p sampling")
    top_k: int = Field(default=40, description="Top-k sampling")
    
    # Caching
    enable_redis_cache: bool = Field(default=False, description="Enable Redis caching")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    # Database
    conversation_db_path: Path = Field(
        default=Path("./data/conversations.db"),
        description="Conversation database path"
    )
    feedback_db_path: Path = Field(
        default=Path("./data/feedback.db"),
        description="Feedback database path"
    )
    
    # Integration
    sentinel_db_path: Path = Field(
        default=Path("../sentinel/data/system_stats.db"),
        description="Sentinel database path"
    )
    oracle_patterns_db_path: Path = Field(
        default=Path("../oracle/data/patterns.db"),
        description="Oracle patterns database path"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path = Field(default=Path("./logs/sage.log"), description="Log file path")
    
    # User Preferences
    default_detail_level: str = Field(
        default="moderate",
        description="Default detail level (brief, moderate, detailed)"
    )
    enable_proactive_insights: bool = Field(
        default=True,
        description="Enable proactive insights"
    )
    enable_auto_actions: bool = Field(
        default=False,
        description="Enable automatic actions"
    )
    
    def __init__(self, **kwargs):
        """Initialize configuration and create directories."""
        super().__init__(**kwargs)
        
        # Create necessary directories
        self.conversation_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = SageConfig()
