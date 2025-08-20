"""
Enhanced Monte Carlo Configuration
=================================

Configuration settings for the integrated Monte Carlo simulation system.
Provides both basic and advanced simulation options with professional-grade
environmental modeling from the horse-bot engine.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulation system."""

    # Basic simulation settings
    basic_simulations: int = 2000
    basic_max_simulations: int = 5000
    basic_timeout_seconds: int = 5

    # Advanced simulation settings
    advanced_simulations: int = 15000
    advanced_max_simulations: int = 50000
    advanced_timeout_seconds: int = 30

    # Default environmental parameters
    default_track_condition: str = "good"
    default_weather_factor: float = 1.0
    default_pace_factor: float = 1.0
    default_variance_factor: float = 0.05

    # Track condition factors (from horse-bot engine)
    track_condition_factors: Optional[Dict[str, float]] = None

    # Value betting thresholds
    min_edge_threshold: float = 0.05  # 5% minimum edge
    min_probability_threshold: float = 0.15  # 15% minimum win chance

    # Reliability scoring
    min_reliability_score: float = 0.7
    high_reliability_threshold: float = 0.9

    # Performance settings
    enable_parallel_processing: bool = True
    max_concurrent_simulations: int = 4

    def __post_init__(self):
        """Initialize track condition factors if not provided."""
        if self.track_condition_factors is None:
            self.track_condition_factors = {
                "firm": 0.98,
                "good": 1.00,
                "good_to_soft": 1.02,
                "soft": 1.05,
                "heavy": 1.10,
                "very_soft": 1.15,
            }


# Global configuration instance
monte_carlo_config = MonteCarloConfig()


def get_monte_carlo_config() -> MonteCarloConfig:
    """Get the Monte Carlo configuration."""
    return monte_carlo_config


def update_monte_carlo_config(**kwargs) -> MonteCarloConfig:
    """Update Monte Carlo configuration with new values."""
    global monte_carlo_config

    for key, value in kwargs.items():
        if hasattr(monte_carlo_config, key):
            setattr(monte_carlo_config, key, value)

    return monte_carlo_config


# Integration settings for v2.03 system
MONTE_CARLO_INTEGRATION = {
    "enabled": True,
    "default_mode": "basic",
    "fallback_to_v2": True,
    # API settings
    "api_enabled": True,
    "api_rate_limit": "100/minute",
    "api_timeout": 30,
    # Database integration
    "store_results": True,
    "result_retention_days": 30,
    # Logging
    "log_level": "INFO",
    "log_performance": True,
    # Feature flags
    "enable_advanced_mode": True,
    "enable_scenario_comparison": True,
    "enable_value_betting": True,
    "enable_environmental_modeling": True,
}


# Environment-specific configurations
TRACK_CONDITIONS = {
    "firm": {
        "factor": 0.98,
        "description": "Firm ground - fastest conditions",
        "typical_variance": 0.03,
    },
    "good": {
        "factor": 1.00,
        "description": "Good ground - standard conditions",
        "typical_variance": 0.05,
    },
    "good_to_soft": {
        "factor": 1.02,
        "description": "Good to soft - slightly slower",
        "typical_variance": 0.06,
    },
    "soft": {
        "factor": 1.05,
        "description": "Soft ground - favor stamina",
        "typical_variance": 0.08,
    },
    "heavy": {
        "factor": 1.10,
        "description": "Heavy ground - significant impact",
        "typical_variance": 0.12,
    },
    "very_soft": {
        "factor": 1.15,
        "description": "Very soft - extreme conditions",
        "typical_variance": 0.15,
    },
}


WEATHER_CONDITIONS = {
    "clear": {"factor": 1.00, "description": "Clear conditions"},
    "light_wind": {"factor": 1.01, "description": "Light wind"},
    "moderate_wind": {"factor": 1.03, "description": "Moderate headwind"},
    "strong_wind": {"factor": 1.06, "description": "Strong headwind"},
    "rain": {"factor": 1.02, "description": "Light rain"},
    "heavy_rain": {"factor": 1.08, "description": "Heavy rain"},
}


RACE_CLASS_FACTORS = {
    "maiden": {"base_variance": 0.08, "description": "Maiden races"},
    "claiming": {"base_variance": 0.07, "description": "Claiming races"},
    "allowance": {"base_variance": 0.06, "description": "Allowance races"},
    "listed": {"base_variance": 0.05, "description": "Listed stakes"},
    "group3": {"base_variance": 0.04, "description": "Group 3 stakes"},
    "group2": {"base_variance": 0.035, "description": "Group 2 stakes"},
    "group1": {"base_variance": 0.03, "description": "Group 1 stakes"},
}


def get_track_condition_info(condition: str) -> Dict[str, Any]:
    """Get track condition information."""
    return TRACK_CONDITIONS.get(condition.lower(), TRACK_CONDITIONS["good"])


def get_weather_condition_info(condition: str) -> Dict[str, Any]:
    """Get weather condition information."""
    return WEATHER_CONDITIONS.get(condition.lower(), WEATHER_CONDITIONS["clear"])


def get_race_class_info(race_class: str) -> Dict[str, Any]:
    """Get race class information."""
    return RACE_CLASS_FACTORS.get(race_class.lower(), RACE_CLASS_FACTORS["allowance"])
