"""
Application configuration
"""
import os
from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Benchmark IO Python API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Database
    DATABASE_URL: str = "postgres://postgres:postgres@localhost:5432/benchmark"
    DB_POOL_MIN: int = 5
    DB_POOL_MAX: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys (comma-separated)
    API_KEYS: str = "test-api-key-1,test-api-key-2"

    # API Key Roles (format: key1:role1,key2:role2)
    API_KEY_ROLES_CONFIG: str = ""

    # Export settings
    EXPORT_DIR: str = "/tmp/exports"
    EXPORT_FILE_EXPIRE_HOURS: int = 24
    EXPORT_MAX_RECORDS: int = 1000000

    @property
    def VALID_API_KEYS(self) -> Set[str]:
        """Get valid API keys as a set"""
        return set(key.strip() for key in self.API_KEYS.split(",") if key.strip())

    @property
    def API_KEY_ROLES(self) -> dict[str, str]:
        """Get API key to role mapping"""
        roles = {}
        if self.API_KEY_ROLES_CONFIG:
            for mapping in self.API_KEY_ROLES_CONFIG.split(","):
                if ":" in mapping:
                    key, role = mapping.split(":", 1)
                    roles[key.strip()] = role.strip()
        return roles


# Create settings instance
settings = Settings()
