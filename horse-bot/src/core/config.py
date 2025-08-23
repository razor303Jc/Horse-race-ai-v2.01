"""
Core configuration module for the Horse Race Handicapping AI system.
Manages application settings using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings configuration.
    
    Uses environment variables with fallback to defaults.
    """
    
    # Application Settings
    app_name: str = "Horse Race Handicapping AI"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security Settings
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    allowed_hosts: str = Field(default="*", env="ALLOWED_HOSTS")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    # Database Settings
    database_url: str = Field(env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Settings
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    
    # External API Settings
    proform_racing_api_key: Optional[str] = Field(default=None, env="PROFORM_RACING_API_KEY")
    proform_racing_base_url: str = Field(
        default="https://api.proformracing.com", 
        env="PROFORM_RACING_BASE_URL"
    )
    
    # Horse Base Web Scraping Settings (Primary Data Source)
    horse_race_base_username: Optional[str] = Field(default=None, env="HORSE_RACE_BASE_USERNAME")
    horse_race_base_password: Optional[str] = Field(default=None, env="HORSE_RACE_BASE_PASSWORD")
    horse_race_base_url: str = Field(
        default="https://www.horseracebase.com", 
        env="HORSE_RACE_BASE_URL"
    )
    
    # Weather API for track conditions
    weather_api_key: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    
    # BetDaq Betting Exchange Settings
    betdaq_api_url: str = Field(default="https://api.betdaq.com/v2.0", env="BETDAQ_API_URL")
    betdaq_username: Optional[str] = Field(default=None, env="BETDAQ_USERNAME")
    betdaq_password: Optional[str] = Field(default=None, env="BETDAQ_PASSWORD")
    betdaq_api_key: Optional[str] = Field(default=None, env="BETDAQ_API_KEY")
    
    # Betting Configuration
    betting_enabled: bool = Field(default=False, env="BETTING_ENABLED")
    max_stake_per_bet: float = Field(default=10.0, env="MAX_STAKE_PER_BET")
    max_total_exposure: float = Field(default=100.0, env="MAX_TOTAL_EXPOSURE")
    max_daily_loss: float = Field(default=50.0, env="MAX_DAILY_LOSS")
    
    # ML Model Settings
    model_storage_path: str = Field(default="./models", env="MODEL_STORAGE_PATH")
    model_cache_ttl: int = Field(default=3600, env="MODEL_CACHE_TTL")  # 1 hour
    
    # Simulation Settings
    max_simulation_runs: int = Field(default=10000, env="MAX_SIMULATION_RUNS")
    simulation_timeout_seconds: int = Field(default=30, env="SIMULATION_TIMEOUT_SECONDS")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Monitoring Settings
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Temporarily disable validators for testing
    # @field_validator('environment')
    # @classmethod
    # def validate_environment(cls, v):
    #     """Validate environment setting."""
    #     allowed_environments = ['development', 'staging', 'production']
    #     if v not in allowed_environments:
    #         raise ValueError(f'Environment must be one of: {allowed_environments}')
    #     return v
    
    # @field_validator('log_level')
    # @classmethod
    # def validate_log_level(cls, v):
    #     """Validate log level setting."""
    #     allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    #     if v.upper() not in allowed_levels:
    #         raise ValueError(f'Log level must be one of: {allowed_levels}')
    #     return v.upper()
    
    # @field_validator('allowed_hosts', 'cors_origins', mode='before')
    # @classmethod
    # def parse_hosts_list(cls, v):
    #     """Parse comma-separated host lists from environment variables."""
    #     if isinstance(v, str):
    #         return [host.strip() for host in v.split(',')]
    #     return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration instance
    """
    return Settings()
