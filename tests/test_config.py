"""
Test suite for the core configuration module.

This module tests the configuration system including:
- Environment variable loading
- Configuration validation
- Default value handling
- Directory creation
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.horse_racing_ai.core.config import Config, DatabaseConfig, ScrapingConfig


class TestConfig:
    """Test the core configuration system."""

    def test_default_config_values(self):
        """Test that default configuration values are properly set."""
        config = Config()

        # Test default values
        assert config.debug is False
        assert config.log_level == "INFO"
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.scraping, ScrapingConfig)

    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        # Set environment variables
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test_db"

        try:
            config = Config()

            assert config.debug is True
            assert config.log_level == "DEBUG"
            assert config.database.url == "postgresql://test:test@localhost/test_db"

        finally:
            # Clean up environment variables
            os.environ.pop("DEBUG", None)
            os.environ.pop("LOG_LEVEL", None)
            os.environ.pop("DATABASE_URL", None)

    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("", False),
        ]

        for env_value, expected in test_cases:
            os.environ["DEBUG"] = env_value
            try:
                config = Config()
                assert (
                    config.debug == expected
                ), f"Expected {expected} for '{env_value}'"
            finally:
                os.environ.pop("DEBUG", None)

    def test_directory_creation(self):
        """Test that required directories are created."""
        config = Config()

        # Check that directories exist
        assert config.data_dir.exists()
        assert config.logs_dir.exists()
        assert config.models_dir.exists()
        assert config.cache_dir.exists()

    def test_ntfy_configuration(self):
        """Test NTFY notification configuration."""
        os.environ["NTFY_TOPIC"] = "test-topic"
        os.environ["NTFY_URL"] = "https://custom-ntfy.sh"

        try:
            config = Config()

            assert config.notifications.topic == "test-topic"
            assert config.notifications.ntfy_url == "https://custom-ntfy.sh"

        finally:
            os.environ.pop("NTFY_TOPIC", None)
            os.environ.pop("NTFY_URL", None)

    def test_database_config_defaults(self):
        """Test database configuration defaults."""
        db_config = DatabaseConfig()

        assert "postgresql://" in db_config.url
        assert db_config.echo is False
        assert db_config.pool_size == 5
        assert db_config.max_overflow == 10

    def test_scraping_config_defaults(self):
        """Test scraping configuration defaults."""
        scraping_config = ScrapingConfig()

        assert scraping_config.headless is True
        assert scraping_config.timeout == 30000
        assert scraping_config.max_retries == 3
        assert scraping_config.retry_delay == 2

    def test_config_from_env_classmethod(self):
        """Test configuration creation from environment."""
        os.environ["DEBUG"] = "true"

        try:
            config = Config.from_env()
            assert config.debug is True

        finally:
            os.environ.pop("DEBUG", None)

    def test_config_paths_are_absolute(self):
        """Test that all configuration paths are absolute."""
        config = Config()

        assert config.project_root.is_absolute()
        assert config.data_dir.is_absolute()
        assert config.logs_dir.is_absolute()
        assert config.models_dir.is_absolute()
        assert config.cache_dir.is_absolute()
