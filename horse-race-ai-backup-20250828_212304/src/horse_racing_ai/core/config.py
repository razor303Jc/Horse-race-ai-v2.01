"""Core configuration module for Horse Racing AI."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    # Primary PostgreSQL database for main operations
    url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://horse_racing:secure_password_123@postgres:5432/"
        "cards_horse_racing_db",
    )
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    # PostgreSQL cache database (removed SQLite dependencies)
    cache_url: str = os.getenv(
        "CACHE_DATABASE_URL",
        "postgresql://horse_racing:secure_password_123@postgres:5432/"
        "horse_racing_cache",
    )
    dev_url: str = os.getenv(
        "DEV_DATABASE_URL",
        "postgresql://horse_racing:secure_password_123@postgres:5432/"
        "horse_racing_dev",
    )


@dataclass
class ScrapingConfig:
    """Web scraping configuration settings."""

    headless: bool = True
    timeout: int = 30000  # milliseconds
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    max_retries: int = 3
    retry_delay: int = 2  # seconds


@dataclass
class MLConfig:
    """Machine learning configuration settings."""

    model_path: Path = Path("models")
    feature_cache_path: Path = Path("cache/features")
    train_test_split: float = 0.8
    cross_validation_folds: int = 5
    random_state: int = 42


@dataclass
class NotificationConfig:
    """Notification configuration settings."""

    ntfy_url: str = "https://ntfy.sh"
    topic: Optional[str] = None
    enabled: bool = True
    priority: str = "default"  # min, low, default, high, max
    tags: Optional[list[str]] = None


@dataclass
class Config:
    """Main configuration class for Horse Racing AI."""

    # Environment
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    project_root: Path = Path(__file__).parent.parent.parent.parent
    data_dir: Path = project_root / "data"
    logs_dir: Path = project_root / "logs"
    models_dir: Path = project_root / "models"
    cache_dir: Path = project_root / "cache"

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        # Create directories if they don't exist
        for directory in [
            self.data_dir,
            self.logs_dir,
            self.models_dir,
            self.cache_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Override with environment variables if present
        if db_url := os.getenv("DATABASE_URL"):
            self.database.url = db_url

        if ntfy_topic := os.getenv("NTFY_TOPIC"):
            self.notifications.topic = ntfy_topic

        if ntfy_url := os.getenv("NTFY_URL"):
            self.notifications.ntfy_url = ntfy_url

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls()


# Global configuration instance
config = Config.from_env()
