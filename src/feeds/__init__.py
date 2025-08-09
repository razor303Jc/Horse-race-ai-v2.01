"""
Live Feed Integration System for Horse Racing AI v2.0

This module provides real-time feed integration capabilities for horse racing data,
replacing traditional auto-downloaders with modern live feed APIs.

Key Components:
- LiveFeedManager: Central manager for multiple feed sources
- LiveFeedSource: Abstract base class for feed implementations
- RacingPostFeed: Racing Post API integration
- TimeformFeed: Timeform API integration
- RaceData: Standardized race data structure
- FeedConfig: Configuration for feed sources

Features:
- Multi-source aggregation with intelligent failover
- Rate limiting and connection management
- Real-time health monitoring
- Asynchronous processing
- Database integration
- Error handling and recovery
"""

from .live_feed_manager import (
    LiveFeedManager,
    LiveFeedSource,
    RacingPostFeed,
    TimeformFeed,
    RaceData,
    FeedConfig,
    create_default_feed_manager,
)

__all__ = [
    "LiveFeedManager",
    "LiveFeedSource",
    "RacingPostFeed",
    "TimeformFeed",
    "RaceData",
    "FeedConfig",
    "create_default_feed_manager",
]

__version__ = "2.0.0"
__author__ = "Horse Racing AI v2.0"
__description__ = "Live feed integration system for real-time horse racing data"
