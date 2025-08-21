"""
AI Analytics Module
==================

Comprehensive analytics and tracking for AI horse racing selections
with profit/loss ROI and contextual analysis capabilities.

Modules:
- ai_selections_tracker: Core tracking system for AI selections
- ai_selections_dashboard: Real-time monitoring dashboard
"""

from .ai_selections_tracker import (
    AISelectionsTracker,
    AIHorseSelection,
    AISelectionPerformance,
    SelectionAnalytics,
)

from .ai_selections_dashboard import initialize_dashboard

__all__ = [
    "AISelectionsTracker",
    "AIHorseSelection",
    "AISelectionPerformance",
    "SelectionAnalytics",
    "initialize_dashboard",
]

__version__ = "2.03"
