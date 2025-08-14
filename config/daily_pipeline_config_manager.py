#!/usr/bin/env python3
"""
🔧 Daily Pipeline Configuration Manager
Manages configuration for the complete daily automation pipeline

Author: AI Assistant
Date: August 11, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path


def create_default_config():
    """Create default configuration for daily pipeline."""

    config = {
        "pipeline": {
            "name": "Horse Racing Daily Automation",
            "version": "2.0",
            "description": "Complete daily pipeline from data download to contextual analysis",
        },
        "schedule": {
            "download_time": "06:01",
            "relationships_time": "00:30",
            "analysis_time": "01:00",
            "reporting_time": "02:00",
            "cleanup_time": "03:00",
        },
        "data_sources": {
            "enabled": ["racing_post", "betfair", "timeform", "sporting_life"],
            "primary_source": "racing_post",
            "backup_sources": ["betfair", "timeform"],
            "retry_attempts": 3,
            "timeout_minutes": 30,
            "rate_limit_delay": 2,
        },
        "processing": {
            "batch_size": 1000,
            "parallel_workers": 4,
            "validation_threshold": 0.95,
            "quality_checks": {
                "missing_data_threshold": 0.1,
                "duplicate_threshold": 0.05,
                "outlier_detection": True,
            },
        },
        "relationships": {
            "jockey_assignment": {
                "enabled": True,
                "realism_weight": 0.8,
                "performance_based": True,
            },
            "trainer_assignment": {
                "enabled": True,
                "regional_preference": True,
                "success_rate_weight": 0.7,
            },
            "course_assignment": {
                "enabled": True,
                "uk_irish_only": True,
                "distance_matching": True,
            },
        },
        "ml_models": {
            "retrain_threshold": 100,
            "model_types": [
                "random_forest",
                "gradient_boosting",
                "neural_network",
                "ensemble",
            ],
            "validation_split": 0.2,
            "cross_validation_folds": 5,
            "feature_importance_tracking": True,
            "model_comparison": True,
        },
        "contextual_analysis": {
            "trend_analysis": {
                "enabled": True,
                "lookback_days": 30,
                "seasonality_detection": True,
            },
            "performance_insights": {
                "enabled": True,
                "statistical_significance": 0.05,
                "confidence_intervals": True,
            },
            "market_analysis": {
                "enabled": True,
                "odds_movement_tracking": True,
                "value_betting_opportunities": True,
            },
        },
        "reporting": {
            "formats": ["markdown", "html", "json", "pdf"],
            "charts_enabled": True,
            "interactive_plots": True,
            "mkdocs_integration": True,
            "archive_reports": True,
            "retention_days": 365,
        },
        "notifications": {
            "email": {
                "enabled": False,
                "recipients": [],
                "smtp_server": "",
                "smtp_port": 587,
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#horse-racing-ai",
            },
            "discord": {"enabled": False, "webhook_url": ""},
        },
        "monitoring": {
            "health_checks": True,
            "performance_monitoring": True,
            "error_tracking": True,
            "metrics_collection": True,
            "alerting": {
                "pipeline_failure": True,
                "data_quality_issues": True,
                "model_performance_degradation": True,
            },
        },
        "storage": {
            "database": {
                "host": "localhost",
                "port": 5433,
                "name": "horse_racing_db",
                "user": "horse_racing",
                "backup_enabled": True,
                "backup_schedule": "daily",
            },
            "file_storage": {
                "reports_path": "reports",
                "logs_path": "logs",
                "models_path": "trained_models",
                "cache_path": "cache",
            },
        },
        "security": {
            "api_key_rotation": True,
            "encryption_enabled": True,
            "audit_logging": True,
            "access_control": True,
        },
        "development": {
            "debug_mode": False,
            "test_mode": False,
            "dry_run": False,
            "verbose_logging": True,
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "created_by": "AI Assistant",
            "last_updated": datetime.now().isoformat(),
            "version_history": [],
        },
    }

    return config


def save_config(config: dict, config_path: Path):
    """Save configuration to file."""
    config_path.parent.mkdir(exist_ok=True, parents=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved to: {config_path}")


def load_config(config_path: Path) -> dict:
    """Load configuration from file."""
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    else:
        return create_default_config()


def update_config(config_path: Path, updates: dict):
    """Update existing configuration."""
    config = load_config(config_path)

    def deep_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    config = deep_update(config, updates)
    config["metadata"]["last_updated"] = datetime.now().isoformat()

    save_config(config, config_path)
    return config


def main():
    """Main configuration setup."""
    project_root = Path(__file__).parent
    config_dir = project_root / "config"
    config_path = config_dir / "daily_pipeline_config.json"

    # Create default configuration
    config = create_default_config()
    save_config(config, config_path)

    # Create environment-specific configs
    environments = ["development", "staging", "production"]

    for env in environments:
        env_config = config.copy()
        env_config["development"]["debug_mode"] = env == "development"
        env_config["development"]["test_mode"] = env != "production"

        env_config_path = config_dir / f"daily_pipeline_config_{env}.json"
        save_config(env_config, env_config_path)

    print(
        f"""
🎉 Daily Pipeline Configuration Complete!

Configuration files created:
- Main config: {config_path}
- Development: {config_dir}/daily_pipeline_config_development.json
- Staging: {config_dir}/daily_pipeline_config_staging.json
- Production: {config_dir}/daily_pipeline_config_production.json

Next steps:
1. Review and customize the configuration files
2. Set environment variables for sensitive data
3. Run the daily pipeline orchestrator
4. Monitor logs and adjust as needed
"""
    )


if __name__ == "__main__":
    main()
