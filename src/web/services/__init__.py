#!/usr/bin/env python3
"""
Enhanced Services Module
Initialize and manage all services for the Horse Racing AI v2.0 web application
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def initialize_services(app) -> Dict[str, Any]:
    """Initialize all services for the web application"""

    services = {}

    try:
        # Initialize ML Service
        from .ml_service_enhanced import EnhancedMLService

        services["ml_service"] = EnhancedMLService()
        logger.info("✅ ML Service initialized")

    except Exception as e:
        logger.warning(f"ML Service initialization failed: {e}")
        services["ml_service"] = None

    try:
        # Initialize Contextual AI Service
        from .contextual_service import ContextualAIService

        services["contextual_service"] = ContextualAIService()
        logger.info("✅ Contextual AI Service initialized")

    except Exception as e:
        logger.warning(f"Contextual AI Service initialization failed: {e}")
        services["contextual_service"] = None

    try:
        # Initialize Betting Service
        from .betting_service import BettingService

        services["betting_service"] = BettingService()
        logger.info("✅ Betting Service initialized")

    except Exception as e:
        logger.warning(f"Betting Service initialization failed: {e}")
        services["betting_service"] = None

    try:
        # Initialize Performance Service
        from .performance_service import PerformanceService

        services["performance_service"] = PerformanceService()
        logger.info("✅ Performance Service initialized")

    except Exception as e:
        logger.warning(f"Performance Service initialization failed: {e}")
        services["performance_service"] = None

    try:
        # Initialize Race Service
        from .race_service import RaceService

        services["race_service"] = RaceService()
        logger.info("✅ Race Service initialized")

    except Exception as e:
        logger.warning(f"Race Service initialization failed: {e}")
        services["race_service"] = None

    logger.info(f"🔧 Initialized {len([s for s in services.values() if s])} services")

    return services
