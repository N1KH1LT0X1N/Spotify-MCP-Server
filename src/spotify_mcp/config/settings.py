"""
Settings and configuration management.

Uses Pydantic for type-safe configuration with environment variable support.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from functools import lru_cache


class SpotifyConfig(BaseModel):
    """Spotify API configuration."""

    client_id: str = Field(
        default="",
        description="Spotify Client ID"
    )

    client_secret: str = Field(
        default="",
        description="Spotify Client Secret"
    )

    redirect_uri: str = Field(
        default="http://127.0.0.1:8888/callback",
        description="OAuth redirect URI"
    )

    @classmethod
    def from_env(cls) -> "SpotifyConfig":
        """Load Spotify config from environment."""
        return cls(
            client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
        )


class CacheConfig(BaseModel):
    """Cache configuration."""

    backend: str = Field(
        default="memory",
        description="Cache backend: 'memory' or 'redis'"
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL (if using Redis backend)"
    )

    max_memory_size: int = Field(
        default=1000,
        description="Maximum number of entries in memory cache",
        gt=0
    )

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate cache backend."""
        if v not in ["memory", "redis"]:
            raise ValueError("backend must be 'memory' or 'redis'")
        return v

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Load cache config from environment."""
        return cls(
            backend=os.getenv("CACHE_BACKEND", "memory"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            max_memory_size=int(os.getenv("CACHE_MAX_SIZE", "1000")),
        )


class MetricsConfig(BaseModel):
    """Metrics configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable Prometheus metrics collection"
    )

    port: int = Field(
        default=8000,
        description="Port for metrics HTTP server",
        gt=0,
        lt=65536
    )

    @classmethod
    def from_env(cls) -> "MetricsConfig":
        """Load metrics config from environment."""
        return cls(
            enabled=os.getenv("METRICS_ENABLED", "false").lower() == "true",
            port=int(os.getenv("METRICS_PORT", "8000")),
        )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    format: str = Field(
        default="human",
        description="Log format: 'human' or 'json'"
    )

    file: Optional[Path] = Field(
        default=None,
        description="Optional log file path"
    )

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        v = v.upper()
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate log format."""
        if v not in ["human", "json"]:
            raise ValueError("format must be 'human' or 'json'")
        return v

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Load logging config from environment."""
        log_file = os.getenv("LOG_FILE")
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "human"),
            file=Path(log_file) if log_file else None,
        )


class Settings(BaseModel):
    """Application settings."""

    # Sub-configurations
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # General settings
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("environment must be development, staging, or production")
        return v

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load all settings from environment variables.

        Returns:
            Settings instance with configuration from environment
        """
        return cls(
            spotify=SpotifyConfig.from_env(),
            cache=CacheConfig.from_env(),
            metrics=MetricsConfig.from_env(),
            logging=LoggingConfig.from_env(),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (singleton).

    Settings are loaded from environment variables on first call
    and cached for subsequent calls.

    Returns:
        Application settings

    Usage:
        from spotify_mcp.config import get_settings

        settings = get_settings()
        print(settings.spotify.client_id)
        print(settings.cache.backend)
    """
    return Settings.from_env()
