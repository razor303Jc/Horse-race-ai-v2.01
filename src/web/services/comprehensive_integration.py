"""
Horse Racing AI v2.0 - Comprehensive Integration Service
Integrates all system components into the web application
"""

import sys
import os
from pathlib import Path
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all the comprehensive system components
try:
    # BETDAQ Integration
    from src.betdaq.betdaq_ai_integration import BETDAQAIIntegration
    from src.betdaq.betdaq_betting_coordinator import BETDAQBettingCoordinator
    from src.betdaq.betdaq_client import BETDAQClient
    from src.betdaq.betdaq_live_betting import BETDAQLiveBetting
    from src.betdaq.betdaq_paper_trading import BETDAQPaperTrading

    # Contextual AI
    from src.contextual_ai.ai_learning_reward_system import AILearningRewardSystem
    from src.contextual_ai.race_data_quality_analyzer import RaceDataQualityAnalyzer

    # Database Management
    from src.database.database_manager_fixed import DatabaseManager
    from src.database.horse_racing_db import HorseRacingDB
    from src.database.monte_carlo_database_manager import MonteCarloDBManager
    from src.database.scoring_database_manager import ScoringDatabaseManager
    from src.database.trends_performance_database_manager import (
        TrendsPerformanceDBManager,
    )

    # Core Horse Racing AI
    from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem
    from src.horse_racing_ai.ml.ai_trainer import AITrainer
    from src.horse_racing_ai.ml.predictor import Predictor

    # Betting Strategies
    from src.horse_racing_ai.betting.advanced_strategies import (
        AdvancedBettingStrategies,
    )

    # Analysis and Scoring
    from src.horse_racing_ai.analysis.race_trends_analyzer import RaceTrendsAnalyzer
    from src.horse_racing_ai.scoring.composite_scorer import CompositeScorer
    from src.horse_racing_ai.scoring.form_analyzer import EnhancedFormAnalyzer
    from src.horse_racing_ai.scoring.power_ratings import PowerRatingSystem

    # Simulation
    from src.horse_racing_ai.simulation.monte_carlo_simulator import MonteCarloSimulator

    # Performance Tracking
    from src.horse_racing_ai.performance.enhanced_ai_tracker import EnhancedAITracker
    from src.horse_racing_ai.performance.enhanced_tracker import EnhancedTracker

    # Notifications
    from src.horse_racing_ai.notifications.enhanced_notification_manager import (
        EnhancedNotificationManager,
    )
    from src.horse_racing_ai.notifications.ntfy_client import NtfyClient

    # Integration
    from src.horse_racing_ai.integration.ai_betting_integration import (
        AIBettingIntegration,
    )

except ImportError as e:
    logging.warning(f"Some imports failed: {e}")


class ComprehensiveSystemIntegration:
    """
    Comprehensive integration service that brings together ALL system components
    for the web application.
    """

    def __init__(self):
        """Initialize the comprehensive integration system"""
        self.logger = logging.getLogger(__name__)

        # System status
        self.is_initialized = False
        self.components_status = {}
        self.last_update = None

        # Initialize core components
        self.ml_system = None
        self.betting_system = None
        self.database_manager = None
        self.contextual_ai = None
        self.betdaq_integration = None
        self.performance_tracker = None
        self.notification_manager = None

        # System metrics
        self.system_metrics = {
            "ml_accuracy": 0.0,
            "betting_roi": 0.0,
            "total_races_analyzed": 0,
            "active_bets": 0,
            "system_uptime": 0,
            "contextual_enhancement": 0.0,
        }

    async def initialize_system(self):
        """Initialize all system components"""
        try:
            self.logger.info("🚀 Initializing Comprehensive System Integration...")

            # Initialize ML System
            await self._initialize_ml_system()

            # Initialize Database Systems
            await self._initialize_database_systems()

            # Initialize Contextual AI
            await self._initialize_contextual_ai()

            # Initialize BETDAQ Integration
            await self._initialize_betdaq_integration()

            # Initialize Betting Strategies
            await self._initialize_betting_system()

            # Initialize Performance Tracking
            await self._initialize_performance_tracking()

            # Initialize Notifications
            await self._initialize_notifications()

            self.is_initialized = True
            self.last_update = datetime.now()
            self.logger.info(
                "✅ Comprehensive System Integration initialized successfully!"
            )

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize system: {e}")
            self.logger.error(traceback.format_exc())
            return False

    async def _initialize_ml_system(self):
        """Initialize ML components"""
        try:
            self.ml_system = {
                "enhanced_ml": EnhancedMLRatingSystem(),
                "ai_trainer": AITrainer(),
                "predictor": Predictor(),
                "form_analyzer": EnhancedFormAnalyzer(),
                "power_ratings": PowerRatingSystem(),
                "composite_scorer": CompositeScorer(),
                "race_trends": RaceTrendsAnalyzer(),
            }

            self.components_status["ml_system"] = "active"
            self.logger.info("✅ ML System initialized")

        except Exception as e:
            self.components_status["ml_system"] = f"error: {e}"
            self.logger.error(f"❌ ML System initialization failed: {e}")

    async def _initialize_database_systems(self):
        """Initialize database components"""
        try:
            self.database_manager = {
                "main_db": DatabaseManager(),
                "horse_racing_db": HorseRacingDB(),
                "monte_carlo_db": MonteCarloDBManager(),
                "scoring_db": ScoringDatabaseManager(),
                "trends_db": TrendsPerformanceDBManager(),
            }

            self.components_status["database_system"] = "active"
            self.logger.info("✅ Database Systems initialized")

        except Exception as e:
            self.components_status["database_system"] = f"error: {e}"
            self.logger.error(f"❌ Database Systems initialization failed: {e}")

    async def _initialize_contextual_ai(self):
        """Initialize contextual AI components"""
        try:
            self.contextual_ai = {
                "reward_system": AILearningRewardSystem(),
                "data_quality": RaceDataQualityAnalyzer(),
            }

            self.components_status["contextual_ai"] = "active"
            self.logger.info("✅ Contextual AI initialized")

        except Exception as e:
            self.components_status["contextual_ai"] = f"error: {e}"
            self.logger.error(f"❌ Contextual AI initialization failed: {e}")

    async def _initialize_betdaq_integration(self):
        """Initialize BETDAQ components"""
        try:
            self.betdaq_integration = {
                "ai_integration": BETDAQAIIntegration(),
                "betting_coordinator": BETDAQBettingCoordinator(),
                "client": BETDAQClient(),
                "live_betting": BETDAQLiveBetting(),
                "paper_trading": BETDAQPaperTrading(),
            }

            self.components_status["betdaq_integration"] = "active"
            self.logger.info("✅ BETDAQ Integration initialized")

        except Exception as e:
            self.components_status["betdaq_integration"] = f"error: {e}"
            self.logger.error(f"❌ BETDAQ Integration initialization failed: {e}")

    async def _initialize_betting_system(self):
        """Initialize betting strategy components"""
        try:
            self.betting_system = {
                "advanced_strategies": AdvancedBettingStrategies(),
                "ai_betting_integration": AIBettingIntegration(),
                "monte_carlo": MonteCarloSimulator(),
            }

            self.components_status["betting_system"] = "active"
            self.logger.info("✅ Betting System initialized")

        except Exception as e:
            self.components_status["betting_system"] = f"error: {e}"
            self.logger.error(f"❌ Betting System initialization failed: {e}")

    async def _initialize_performance_tracking(self):
        """Initialize performance tracking components"""
        try:
            self.performance_tracker = {
                "enhanced_ai_tracker": EnhancedAITracker(),
                "enhanced_tracker": EnhancedTracker(),
            }

            self.components_status["performance_tracking"] = "active"
            self.logger.info("✅ Performance Tracking initialized")

        except Exception as e:
            self.components_status["performance_tracking"] = f"error: {e}"
            self.logger.error(f"❌ Performance Tracking initialization failed: {e}")

    async def _initialize_notifications(self):
        """Initialize notification components"""
        try:
            self.notification_manager = {
                "enhanced_manager": EnhancedNotificationManager(),
                "ntfy_client": NtfyClient(),
            }

            self.components_status["notification_system"] = "active"
            self.logger.info("✅ Notification System initialized")

        except Exception as e:
            self.components_status["notification_system"] = f"error: {e}"
            self.logger.error(f"❌ Notification System initialization failed: {e}")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "is_initialized": self.is_initialized,
            "components_status": self.components_status,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "system_metrics": self.system_metrics,
            "uptime_minutes": (
                (datetime.now() - self.last_update).total_seconds() / 60
                if self.last_update
                else 0
            ),
        }

    async def analyze_race(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive race analysis using all system components"""
        try:
            if not self.is_initialized:
                await self.initialize_system()

            results = {
                "race_id": race_data.get("race_id"),
                "timestamp": datetime.now().isoformat(),
                "analysis": {},
            }

            # ML Analysis
            if self.ml_system:
                ml_results = await self._perform_ml_analysis(race_data)
                results["analysis"]["ml_predictions"] = ml_results

            # Contextual AI Enhancement
            if self.contextual_ai:
                contextual_results = await self._perform_contextual_analysis(race_data)
                results["analysis"]["contextual_enhancement"] = contextual_results

            # Betting Strategy Analysis
            if self.betting_system:
                betting_results = await self._perform_betting_analysis(
                    race_data, results["analysis"]
                )
                results["analysis"]["betting_strategies"] = betting_results

            # Performance Tracking
            if self.performance_tracker:
                performance_results = await self._track_performance(results)
                results["analysis"]["performance_metrics"] = performance_results

            return results

        except Exception as e:
            self.logger.error(f"❌ Race analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _perform_ml_analysis(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform ML analysis on race data"""
        try:
            # Enhanced ML predictions
            ml_predictions = {}

            if "enhanced_ml" in self.ml_system:
                ml_predictions["enhanced_ml_ratings"] = self.ml_system[
                    "enhanced_ml"
                ].predict_race_ratings(race_data)

            if "race_trends" in self.ml_system:
                ml_predictions["race_trends"] = self.ml_system[
                    "race_trends"
                ].analyze_race_trends(race_data)

            if "composite_scorer" in self.ml_system:
                ml_predictions["composite_scores"] = self.ml_system[
                    "composite_scorer"
                ].score_race_horses(race_data)

            return ml_predictions

        except Exception as e:
            self.logger.error(f"❌ ML analysis failed: {e}")
            return {"error": str(e)}

    async def _perform_contextual_analysis(
        self, race_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform contextual AI analysis"""
        try:
            contextual_results = {}

            if "reward_system" in self.contextual_ai:
                contextual_results["ai_reward_analysis"] = self.contextual_ai[
                    "reward_system"
                ].analyze_race_context(race_data)

            if "data_quality" in self.contextual_ai:
                contextual_results["data_quality"] = self.contextual_ai[
                    "data_quality"
                ].analyze_data_quality(race_data)

            return contextual_results

        except Exception as e:
            self.logger.error(f"❌ Contextual analysis failed: {e}")
            return {"error": str(e)}

    async def _perform_betting_analysis(
        self, race_data: Dict[str, Any], analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform betting strategy analysis"""
        try:
            betting_results = {}

            if "advanced_strategies" in self.betting_system:
                betting_results["strategy_recommendations"] = self.betting_system[
                    "advanced_strategies"
                ].analyze_betting_opportunities(race_data, analysis_results)

            if "monte_carlo" in self.betting_system:
                betting_results["monte_carlo_simulation"] = self.betting_system[
                    "monte_carlo"
                ].simulate_race_outcomes(race_data, analysis_results)

            return betting_results

        except Exception as e:
            self.logger.error(f"❌ Betting analysis failed: {e}")
            return {"error": str(e)}

    async def _track_performance(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track system performance"""
        try:
            performance_results = {}

            if "enhanced_ai_tracker" in self.performance_tracker:
                performance_results["ai_performance"] = self.performance_tracker[
                    "enhanced_ai_tracker"
                ].track_prediction_performance(analysis_results)

            # Update system metrics
            self.system_metrics["total_races_analyzed"] += 1
            self.system_metrics["last_analysis"] = datetime.now().isoformat()

            return performance_results

        except Exception as e:
            self.logger.error(f"❌ Performance tracking failed: {e}")
            return {"error": str(e)}

    async def get_live_betdaq_status(self) -> Dict[str, Any]:
        """Get live BETDAQ status and opportunities"""
        try:
            if not self.betdaq_integration:
                return {"status": "not_initialized"}

            status = {}

            if "live_betting" in self.betdaq_integration:
                status["live_markets"] = self.betdaq_integration[
                    "live_betting"
                ].get_live_markets()

            if "paper_trading" in self.betdaq_integration:
                status["paper_trading"] = self.betdaq_integration[
                    "paper_trading"
                ].get_trading_status()

            return status

        except Exception as e:
            self.logger.error(f"❌ BETDAQ status check failed: {e}")
            return {"error": str(e)}

    async def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for the web dashboard"""
        try:
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "system_status": await self.get_system_status(),
                "recent_races": [],
                "live_opportunities": [],
                "performance_summary": {},
                "alerts": [],
            }

            # Add system metrics
            dashboard_data["system_metrics"] = self.system_metrics

            # Add component statuses
            dashboard_data["component_health"] = self.components_status

            return dashboard_data

        except Exception as e:
            self.logger.error(f"❌ Dashboard data generation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


# Global instance
comprehensive_integration = ComprehensiveSystemIntegration()


async def get_integration_service():
    """Get the comprehensive integration service instance"""
    if not comprehensive_integration.is_initialized:
        await comprehensive_integration.initialize_system()
    return comprehensive_integration
