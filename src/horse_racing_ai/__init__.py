"""
Horse Racing AI v2.0
====================
A comprehensive horse racing handicapping system with AI-powered predictions.
"""

__version__ = "2.0.0"
__author__ = "Horse Racing AI Team"
__email__ = "contact@horseracingai.com"

from .automation.playwright_scraper import PlaywrightScraper
from .core.config import Config
from .ml.predictor import RacePredictor
from .notifications.ntfy_client import NTFYClient
from .scoring.composite_scorer import CompositeScorer
from .scoring.form_analyzer import EnhancedFormAnalyzer
from .scoring.power_ratings import PowerRatingSystem

__all__ = [
    "Config",
    "PlaywrightScraper",
    "RacePredictor",
    "NTFYClient",
    "EnhancedFormAnalyzer",
    "PowerRatingSystem",
    "CompositeScorer",
]
