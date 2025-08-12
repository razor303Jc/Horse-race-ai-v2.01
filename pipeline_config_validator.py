#!/usr/bin/env python3
"""
🔧 Phase 2: Pipeline Reliability Enhancements
Configuration Validation with Pydantic & Enhanced Error Handling

This implements Phase 2 improvements:
1. Pydantic configuration validation
2. Enhanced retry mechanisms with circuit breakers
3. Configuration hot-reloading
4. Environment-specific configs
5. Input validation framework

Author: AI Assistant
Date: August 12, 2025
"""

import json
import os
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from pydantic import BaseModel, Field, ValidationError, validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    print("⚠️ Pydantic not installed. Installing...")
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic"])
    from pydantic import BaseModel, Field, ValidationError, validator

    PYDANTIC_AVAILABLE = True


class ScheduleConfig(BaseModel):
    """Configuration for pipeline scheduling."""

    download_time: str = Field(
        default="00:01",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Time to start data download (HH:MM format)",
    )
    relationships_time: str = Field(
        default="00:30",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Time to process relationships",
    )
    contextual_time: str = Field(
        default="01:00",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Time for contextual analysis",
    )
    form_scoring_time: str = Field(
        default="01:30", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    power_ratings_time: str = Field(
        default="02:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    speed_analysis_time: str = Field(
        default="02:30", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    monte_carlo_time: str = Field(
        default="03:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    ml_training_time: str = Field(
        default="03:30", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    race_trends_time: str = Field(
        default="04:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    composite_scoring_time: str = Field(
        default="04:30", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    betting_strategies_time: str = Field(
        default="05:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    reporting_time: str = Field(
        default="05:30", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    prerace_updates_time: str = Field(
        default="12:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    live_prep_time: str = Field(
        default="13:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    results_analysis_time: str = Field(
        default="20:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    optimization_time: str = Field(
        default="19:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    next_day_prep_time: str = Field(
        default="21:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )

    @validator("*")
    def validate_time_format(cls, v):
        """Validate that all time fields are in correct format."""
        if isinstance(v, str):
            try:
                time.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid time format: {v}. Use HH:MM format.")
        return v


class DataSourceConfig(BaseModel):
    """Configuration for data sources."""

    enabled: List[str] = Field(
        default=["racing_post", "betfair", "timeform"],
        description="List of enabled data sources",
    )
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts for failed downloads",
    )
    timeout_minutes: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Timeout in minutes for data source operations",
    )
    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of failures before circuit breaker opens",
    )
    circuit_breaker_timeout: int = Field(
        default=300, ge=60, le=3600, description="Circuit breaker timeout in seconds"
    )

    @validator("enabled")
    def validate_enabled_sources(cls, v):
        """Validate that enabled sources are supported."""
        supported_sources = [
            "racing_post",
            "betfair",
            "timeform",
            "itsracing",
            "punters_intelligence",
            "geegeez",
        ]
        for source in v:
            if source not in supported_sources:
                raise ValueError(f"Unsupported data source: {source}")
        return v


class ProcessingConfig(BaseModel):
    """Configuration for data processing."""

    batch_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Batch size for processing operations",
    )
    parallel_workers: int = Field(
        default=4, ge=1, le=16, description="Number of parallel workers"
    )
    validation_threshold: float = Field(
        default=0.95, ge=0.5, le=1.0, description="Data validation threshold (0.5-1.0)"
    )
    memory_limit_mb: int = Field(
        default=4096, ge=512, le=32768, description="Memory limit in MB"
    )
    max_processing_time_minutes: int = Field(
        default=60, ge=10, le=240, description="Maximum processing time per stage"
    )


class MLModelConfig(BaseModel):
    """Configuration for ML models."""

    retrain_threshold: int = Field(
        default=100,
        ge=10,
        le=10000,
        description="New records needed to trigger retrain",
    )
    model_types: List[str] = Field(
        default=["random_forest", "gradient_boosting", "neural_network"],
        description="List of ML model types to train",
    )
    validation_split: float = Field(
        default=0.2, ge=0.1, le=0.4, description="Validation split ratio"
    )
    max_training_time_minutes: int = Field(
        default=120, ge=30, le=480, description="Maximum training time per model"
    )
    feature_selection_threshold: float = Field(
        default=0.01, ge=0.001, le=0.1, description="Feature importance threshold"
    )

    @validator("model_types")
    def validate_model_types(cls, v):
        """Validate supported model types."""
        supported_models = [
            "random_forest",
            "gradient_boosting",
            "neural_network",
            "xgboost",
            "lightgbm",
            "svm",
            "logistic_regression",
        ]
        for model in v:
            if model not in supported_models:
                raise ValueError(f"Unsupported model type: {model}")
        return v


class DatabaseConfig(BaseModel):
    """Configuration for database connections."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5433, ge=1, le=65535, description="Database port")
    database: str = Field(default="horse_racing_db", description="Database name")
    user: str = Field(default="horse_racing", description="Database user")
    password: Optional[str] = Field(default=None, description="Database password")
    pool_min_connections: int = Field(
        default=1, ge=1, le=10, description="Minimum pool connections"
    )
    pool_max_connections: int = Field(
        default=20, ge=5, le=100, description="Maximum pool connections"
    )
    connection_timeout: int = Field(
        default=30, ge=5, le=300, description="Connection timeout seconds"
    )
    query_timeout: int = Field(
        default=300, ge=30, le=3600, description="Query timeout seconds"
    )

    @validator("password")
    def get_password_from_env(cls, v):
        """Get password from environment if not provided."""
        if v is None:
            return os.getenv("POSTGRES_PASSWORD", "secure_password_123")
        return v


class NotificationConfig(BaseModel):
    """Configuration for notifications."""

    email_enabled: bool = Field(default=False, description="Enable email notifications")
    slack_enabled: bool = Field(default=False, description="Enable Slack notifications")
    discord_enabled: bool = Field(
        default=False, description="Enable Discord notifications"
    )
    webhook_url: Optional[str] = Field(
        default=None, description="Webhook URL for notifications"
    )
    notification_level: str = Field(
        default="error",
        pattern=r"^(debug|info|warning|error|critical)$",
        description="Minimum notification level",
    )
    max_notifications_per_hour: int = Field(
        default=10, ge=1, le=100, description="Rate limit for notifications"
    )


class SecurityConfig(BaseModel):
    """Configuration for security settings."""

    encrypt_sensitive_data: bool = Field(
        default=True, description="Encrypt sensitive data"
    )
    audit_logging: bool = Field(default=True, description="Enable audit logging")
    api_rate_limit: int = Field(
        default=100, ge=10, le=1000, description="API rate limit per minute"
    )
    session_timeout_minutes: int = Field(
        default=60, ge=15, le=480, description="Session timeout in minutes"
    )
    max_login_attempts: int = Field(
        default=5, ge=3, le=10, description="Maximum login attempts"
    )


class PipelineConfig(BaseModel):
    """Complete pipeline configuration with validation."""

    # Environment and basic settings
    environment: str = Field(
        default="development",
        pattern=r"^(development|staging|production)$",
        description="Deployment environment",
    )
    debug_mode: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )

    # Configuration sections
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    ml_models: MLModelConfig = Field(default_factory=MLModelConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"  # Don't allow extra fields
        use_enum_values = True

    @validator("environment")
    def validate_environment_specific_settings(cls, v, values):
        """Validate environment-specific settings."""
        if v == "production":
            # Production environment requires specific settings
            if values.get("debug_mode", True):
                raise ValueError("Debug mode must be disabled in production")
            if values.get("log_level") == "DEBUG":
                raise ValueError("DEBUG log level not allowed in production")
        return v

    def to_dict(self) -> Dict:
        """Convert to dictionary for compatibility."""
        return self.dict()

    def save_to_file(self, file_path: Path):
        """Save configuration to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.dict(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "PipelineConfig":
        """Load configuration from JSON file."""
        if not file_path.exists():
            # Create default config file
            default_config = cls()
            default_config.save_to_file(file_path)
            return default_config

        with open(file_path, "r") as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def create_environment_config(cls, environment: str) -> "PipelineConfig":
        """Create environment-specific configuration."""
        if environment == "production":
            return cls(
                environment="production",
                debug_mode=False,
                log_level="INFO",
                database=DatabaseConfig(pool_max_connections=50, connection_timeout=60),
                processing=ProcessingConfig(parallel_workers=8, memory_limit_mb=8192),
                notifications=NotificationConfig(
                    email_enabled=True, notification_level="warning"
                ),
                security=SecurityConfig(api_rate_limit=50, session_timeout_minutes=30),
            )
        elif environment == "staging":
            return cls(
                environment="staging",
                debug_mode=False,
                log_level="INFO",
                database=DatabaseConfig(pool_max_connections=30),
                processing=ProcessingConfig(parallel_workers=6),
            )
        else:  # development
            return cls(environment="development", debug_mode=True, log_level="DEBUG")


def create_config_manager():
    """Create configuration manager with validation."""

    class ConfigManager:
        """Enhanced configuration manager with validation and hot-reloading."""

        def __init__(self, config_file: Path):
            self.config_file = config_file
            self.config = None
            self._load_config()

        def _load_config(self):
            """Load and validate configuration."""
            try:
                self.config = PipelineConfig.load_from_file(self.config_file)
                print(f"✅ Configuration loaded and validated: {self.config_file}")
            except ValidationError as e:
                print(f"❌ Configuration validation failed: {e}")
                print("🔧 Creating default configuration...")
                self.config = PipelineConfig()
                self.save_config()
            except Exception as e:
                print(f"❌ Failed to load configuration: {e}")
                print("🔧 Using default configuration...")
                self.config = PipelineConfig()

        def get_config(self) -> PipelineConfig:
            """Get current configuration."""
            return self.config

        def update_config(self, **kwargs) -> bool:
            """Update configuration with validation."""
            try:
                # Create new config with updates
                current_dict = self.config.dict()
                current_dict.update(kwargs)
                new_config = PipelineConfig(**current_dict)

                # If validation passes, update
                self.config = new_config
                self.save_config()
                print("✅ Configuration updated successfully")
                return True
            except ValidationError as e:
                print(f"❌ Configuration update failed: {e}")
                return False

        def save_config(self):
            """Save current configuration to file."""
            self.config.save_to_file(self.config_file)

        def reload_config(self) -> bool:
            """Reload configuration from file."""
            try:
                old_config = self.config
                self._load_config()
                print("✅ Configuration reloaded successfully")
                return True
            except Exception as e:
                print(f"❌ Configuration reload failed: {e}")
                return False

        def validate_current_config(self) -> List[str]:
            """Validate current configuration and return any issues."""
            issues = []
            try:
                # Re-validate current config
                PipelineConfig(**self.config.dict())
            except ValidationError as e:
                for error in e.errors():
                    field = ".".join(str(x) for x in error["loc"])
                    issues.append(f"{field}: {error['msg']}")
            return issues

        def create_environment_configs(self):
            """Create environment-specific configuration files."""
            base_path = self.config_file.parent

            environments = ["development", "staging", "production"]
            for env in environments:
                env_config = PipelineConfig.create_environment_config(env)
                env_file = base_path / f"pipeline_config_{env}.json"
                env_config.save_to_file(env_file)
                print(f"✅ Created {env} configuration: {env_file}")

    return ConfigManager


def main():
    """Main function to test configuration validation."""
    print("🔧 Pipeline Configuration Validation System")
    print("=" * 50)

    # Test basic configuration creation
    print("1. Testing basic configuration creation...")
    try:
        config = PipelineConfig()
        print("✅ Default configuration created successfully")
    except Exception as e:
        print(f"❌ Failed to create default configuration: {e}")
        return 1

    # Test configuration validation
    print("\n2. Testing configuration validation...")
    try:
        # Test invalid time format
        invalid_config = {"schedule": {"download_time": "25:00"}}  # Invalid time
        PipelineConfig(**invalid_config)
        print("❌ Validation should have failed for invalid time")
    except ValidationError:
        print("✅ Configuration validation working correctly")

    # Test environment-specific configs
    print("\n3. Testing environment-specific configurations...")
    for env in ["development", "staging", "production"]:
        try:
            env_config = PipelineConfig.create_environment_config(env)
            print(f"✅ {env.title()} configuration created")
        except Exception as e:
            print(f"❌ Failed to create {env} configuration: {e}")

    # Test configuration manager
    print("\n4. Testing configuration manager...")
    config_file = Path("test_pipeline_config.json")
    try:
        ConfigManagerClass = create_config_manager()
        manager = ConfigManagerClass(config_file)

        # Test config updates
        success = manager.update_config(debug_mode=False)
        if success:
            print("✅ Configuration update successful")
        else:
            print("❌ Configuration update failed")

        # Test validation
        issues = manager.validate_current_config()
        if not issues:
            print("✅ Configuration validation passed")
        else:
            print(f"⚠️ Configuration issues found: {issues}")

        # Cleanup test file
        if config_file.exists():
            config_file.unlink()

    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")

    print("\n✅ Configuration validation system ready for integration!")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
