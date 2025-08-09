#!/usr/bin/env python3
"""
Docker-specific configuration and utilities for the Horse Racing Auto Downloader
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class DockerDownloadConfig:
    """Docker-optimized configuration for respectful downloading"""

    # Timing configuration
    daily_run_time: str = "00:01"  # Run at 00:01 daily
    max_runtime_minutes: int = 60  # Maximum runtime before timeout

    # Respectful scraping settings
    page_delay_seconds: float = 3.0  # Delay between page requests
    retry_delay_seconds: float = 5.0  # Delay before retrying
    max_retries: int = 3  # Maximum retry attempts

    # Docker-optimized browser settings
    headless: bool = True  # Always headless in Docker
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    viewport_width: int = 1920
    viewport_height: int = 1080

    # Rate limiting (more conservative in containers)
    requests_per_minute: int = 12  # Slightly reduced for container stability
    concurrent_pages: int = 1  # Only one page at a time

    # Container-specific data storage
    output_directory: str = "/app/data/daily_downloads"
    backup_directory: str = "/app/data/daily_downloads/backups"
    log_directory: str = "/app/logs"

    # Success criteria
    minimum_races_required: int = 10  # Minimum races needed for success
    minimum_horses_per_race: int = 4  # Minimum horses per race

    # Docker-specific memory and performance settings
    memory_limit_mb: int = 2048  # Memory limit for browser
    disable_images: bool = True  # Disable images to save bandwidth/memory
    disable_javascript_harmony: bool = True  # Reduce JS processing
    single_process: bool = True  # Use single process for containers


def get_docker_browser_args() -> list[str]:
    """Get optimized browser arguments for Docker containers"""
    return [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--disable-javascript-harmony-shipping",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-ipc-flooding-protection",
        "--memory-pressure-off",
        "--max_old_space_size=4096",
        "--single-process",
        "--disable-default-apps",
        "--disable-sync",
        "--disable-translate",
        "--hide-scrollbars",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-default-apps",
    ]


def setup_docker_directories() -> Dict[str, Path]:
    """Set up required directories for Docker container"""
    # Use different paths based on environment
    if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true":
        # Running in Docker container
        base_path = Path("/app")
    else:
        # Running locally for testing
        base_path = Path.cwd()

    directories = {
        "output": base_path / "data" / "daily_downloads",
        "backup": base_path / "data" / "daily_downloads" / "backups",
        "logs": base_path / "logs",
        "cache": base_path / "cache",
        "temp": Path("/tmp/horserace_downloads"),
    }

    for name, path in directories.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {path}")
        except PermissionError:
            print(f"⚠️  Permission denied creating: {path}")
        except Exception as e:
            print(f"❌ Failed to create {path}: {e}")

    return directories


def get_docker_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration for Docker"""
    return {
        "PLAYWRIGHT_BROWSERS_PATH": "/app/.playwright",
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/app",
        "TZ": os.getenv("TZ", "UTC"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "HEADLESS": "true",  # Force headless in Docker
        "DISABLE_GPU": "true",
        "DISABLE_IMAGES": "true",
    }


def validate_docker_setup() -> bool:
    """Validate that Docker environment is properly set up"""
    checks = {}

    # Check Playwright installation
    try:
        from playwright.async_api import async_playwright

        checks["playwright"] = True
    except ImportError:
        checks["playwright"] = False

    # Check required directories
    required_dirs = ["/app/data", "/app/logs", "/app/.playwright"]
    for dir_path in required_dirs:
        checks[f"dir_{dir_path}"] = Path(dir_path).exists()

    # Check environment variables
    required_env = ["HORSERACE_DB_USERNAME", "HORSERACE_DB_PASSWORD"]
    for env_var in required_env:
        checks[f"env_{env_var}"] = os.getenv(env_var) is not None

    # Print validation results
    print("🔧 Docker Environment Validation:")
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}: {'OK' if result else 'MISSING'}")
        if not result:
            all_good = False

    return all_good


if __name__ == "__main__":
    print("🐳 Docker Configuration Setup")

    # Set up directories
    dirs = setup_docker_directories()

    # Validate setup
    is_valid = validate_docker_setup()

    if is_valid:
        print("✅ Docker environment is ready for auto downloading!")
    else:
        print("❌ Docker environment needs attention before running auto downloader")
