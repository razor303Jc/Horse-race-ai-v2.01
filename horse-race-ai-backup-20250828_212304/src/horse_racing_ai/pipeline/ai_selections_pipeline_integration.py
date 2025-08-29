#!/usr/bin/env python3
"""
AI Selections Pipeline Integration
=================================

Integrates AI selections tracking into the main horse racing pipeline.
This script coordinates between:
- Pipeline execution
- AI selections recording
- Result updates
- Performance analysis
- Dashboard updates
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

from horse_racing_ai.analytics.ai_selections_tracker import AISelectionsTracker
from horse_racing_ai.integration.ai_selections_integration import (
    AISelectionsIntegrationSystem,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineAISelectionsIntegrator:
    """
    Integrates AI selections tracking into the pipeline workflow.
    """

    def __init__(self, config_path: str = None):
        """Initialize the pipeline integrator."""
        self.config_path = config_path or "config/comprehensive_pipeline_config.json"
        self.config = self._load_config()

        # Initialize AI selections system
        ai_config = self.config.get("ai_selections_tracking", {})
        self.selections_db_path = ai_config.get(
            "database_path", "data/ai_selections_tracking.db"
        )
        self.performance_db_path = ai_config.get(
            "performance_database_path", "data/performance_tracking.db"
        )

        # Initialize components
        self.tracker = AISelectionsTracker(self.selections_db_path)
        self.integration_system = None  # Will be initialized when needed

    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def is_enabled(self) -> bool:
        """Check if AI selections tracking is enabled."""
        return self.config.get("ai_selections_tracking", {}).get("enabled", False)

    async def process_pipeline_predictions(
        self, predictions_data: Dict[str, Any]
    ) -> None:
        """
        Process predictions from the pipeline and record AI selections.

        Args:
            predictions_data: Dictionary containing race predictions from pipeline
        """
        if not self.is_enabled():
            logger.info("AI selections tracking is disabled")
            return

        try:
            logger.info("Processing pipeline predictions for AI selections tracking")

            # Initialize integration system if needed
            if not self.integration_system:
                self.integration_system = AISelectionsIntegrationSystem(
                    selections_db_path=self.selections_db_path,
                    performance_db_path=self.performance_db_path,
                )

            # Process each race in the predictions
            for race_id, race_data in predictions_data.get("races", {}).items():
                await self._process_race_predictions(race_id, race_data)

            logger.info("Completed processing pipeline predictions")

        except Exception as e:
            logger.error(f"Error processing pipeline predictions: {e}")
            raise

    async def _process_race_predictions(
        self, race_id: str, race_data: Dict[str, Any]
    ) -> None:
        """Process predictions for a single race."""
        try:
            # Extract race information
            race_info = {
                "race_id": race_id,
                "race_date": race_data.get("race_date"),
                "course": race_data.get("course"),
                "race_number": race_data.get("race_number"),
                "distance": race_data.get("distance"),
                "class": race_data.get("class"),
                "field_size": len(race_data.get("horses", [])),
                "weather": race_data.get("weather"),
                "track_condition": race_data.get("track_condition"),
            }

            # Process each horse's predictions
            for horse_data in race_data.get("horses", []):
                if self._should_record_selection(horse_data):
                    await self._record_horse_selection(race_info, horse_data)

        except Exception as e:
            logger.error(f"Error processing race {race_id}: {e}")

    def _should_record_selection(self, horse_data: Dict[str, Any]) -> bool:
        """Determine if a horse selection should be recorded."""
        criteria = self.config.get("ai_selections_tracking", {}).get(
            "selection_criteria", {}
        )

        # Check minimum confidence
        confidence = horse_data.get("confidence_score", 0.0)
        if confidence < criteria.get("min_confidence", 0.6):
            return False

        # Check value edge
        value_edge = horse_data.get("value_edge", 0.0)
        if value_edge < criteria.get("min_value_edge", 0.1):
            return False

        # Check odds range
        odds = horse_data.get("odds_decimal", 0.0)
        if odds > criteria.get("max_odds", 20.0) or odds < criteria.get(
            "min_odds", 1.5
        ):
            return False

        return True

    async def _record_horse_selection(
        self, race_info: Dict[str, Any], horse_data: Dict[str, Any]
    ) -> None:
        """Record a horse selection."""
        try:
            # Prepare selection data
            selection_data = {
                "horse_name": horse_data.get("horse_name"),
                "barrier": horse_data.get("barrier"),
                "jockey": horse_data.get("jockey"),
                "trainer": horse_data.get("trainer"),
                "weight": horse_data.get("weight"),
                "odds_decimal": horse_data.get("odds_decimal"),
                "form": horse_data.get("form"),
                "confidence_score": horse_data.get("confidence_score"),
                "win_probability": horse_data.get("win_probability"),
                "place_probability": horse_data.get("place_probability"),
                "value_edge": horse_data.get("value_edge"),
                "prediction_method": horse_data.get("prediction_method", "pipeline"),
                "stake_amount": self._calculate_stake(horse_data),
            }

            # Determine betting strategy
            strategy = self._determine_strategy(horse_data)

            # Record the selection
            selection_id = self.tracker.record_ai_selection(
                race_data=race_info,
                selection_data=selection_data,
                prediction_method=selection_data["prediction_method"],
                betting_strategy=strategy,
            )

            logger.info(f"Recorded AI selection: {selection_id}")

        except Exception as e:
            logger.error(f"Error recording horse selection: {e}")

    def _calculate_stake(self, horse_data: Dict[str, Any]) -> float:
        """Calculate stake amount based on strategy and confidence."""
        # Default base stake
        base_stake = 10.0

        # Adjust based on confidence
        confidence = horse_data.get("confidence_score", 0.5)
        value_edge = horse_data.get("value_edge", 0.0)

        # Kelly criterion inspired sizing
        kelly_fraction = min(value_edge * confidence, 0.05)  # Max 5% of bankroll

        return base_stake * (1 + kelly_fraction * 10)  # Scale appropriately

    def _determine_strategy(self, horse_data: Dict[str, Any]) -> str:
        """Determine the appropriate betting strategy."""
        confidence = horse_data.get("confidence_score", 0.5)
        value_edge = horse_data.get("value_edge", 0.0)
        odds = horse_data.get("odds_decimal", 5.0)

        strategies = self.config.get("ai_selections_tracking", {}).get(
            "betting_strategies", {}
        )

        # Check for 80/20 strategy
        if confidence >= strategies.get("80_20", {}).get("min_confidence", 0.8):
            return "80_20"

        # Check for conservative strategy
        if confidence >= strategies.get("conservative", {}).get(
            "min_confidence", 0.75
        ) and odds <= strategies.get("conservative", {}).get("max_odds", 5.0):
            return "conservative"

        # Check for value betting
        if value_edge >= strategies.get("value_bet", {}).get("min_edge", 0.1):
            return "value_bet"

        # Default strategy
        return "value_bet"

    async def update_race_results(self, results_data: Dict[str, Any]) -> None:
        """
        Update AI selections with race results.

        Args:
            results_data: Dictionary containing race results
        """
        if not self.is_enabled():
            return

        try:
            logger.info("Updating AI selections with race results")

            # Initialize integration system if needed
            if not self.integration_system:
                self.integration_system = AISelectionsIntegrationSystem(
                    selections_db_path=self.selections_db_path,
                    performance_db_path=self.performance_db_path,
                )

            # Process results using integration system
            await self.integration_system.update_race_results(results_data)

            logger.info("Completed updating AI selections with results")

        except Exception as e:
            logger.error(f"Error updating race results: {e}")
            raise

    async def generate_performance_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive performance analysis."""
        if not self.is_enabled():
            return {}

        try:
            logger.info("Generating AI selections performance analysis")

            # Get analytics from tracker
            analytics = self.tracker.get_selection_analytics()

            # Generate contextual analysis
            contextual_analysis = self.tracker.generate_contextual_analysis()

            # Combine results
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analytics": (
                    analytics.__dict__ if hasattr(analytics, "__dict__") else analytics
                ),
                "contextual_analysis": contextual_analysis,
                "configuration": self.config.get("ai_selections_tracking", {}),
            }

            logger.info("Completed performance analysis generation")
            return analysis

        except Exception as e:
            logger.error(f"Error generating performance analysis: {e}")
            return {}

    def get_dashboard_url(self) -> str:
        """Get the AI selections dashboard URL."""
        dashboard_config = self.config.get("ai_selections_tracking", {}).get(
            "dashboard", {}
        )
        host = dashboard_config.get("host", "localhost")
        port = dashboard_config.get("port", 5001)

        # Convert 0.0.0.0 to localhost for external access
        if host == "0.0.0.0":
            host = "localhost"

        return f"http://{host}:{port}"


async def main():
    """Main function for testing the integration."""
    integrator = PipelineAISelectionsIntegrator()

    if not integrator.is_enabled():
        print("AI selections tracking is not enabled in configuration")
        return

    print(f"AI Selections Pipeline Integration initialized")
    print(f"Dashboard URL: {integrator.get_dashboard_url()}")
    print(f"Selections DB: {integrator.selections_db_path}")
    print(f"Performance DB: {integrator.performance_db_path}")

    # Test with sample data
    sample_predictions = {
        "races": {
            "TEST_2025-08-21_R1": {
                "race_date": "2025-08-21T14:30:00Z",
                "course": "Test Course",
                "race_number": 1,
                "distance": 6.0,
                "class": "Class 2",
                "weather": "Clear",
                "track_condition": "Good",
                "horses": [
                    {
                        "horse_name": "Test Horse 1",
                        "barrier": 3,
                        "jockey": "Test Jockey",
                        "trainer": "Test Trainer",
                        "weight": 58.5,
                        "odds_decimal": 4.5,
                        "form": "12x23",
                        "confidence_score": 0.75,
                        "win_probability": 0.22,
                        "place_probability": 0.45,
                        "value_edge": 0.12,
                        "prediction_method": "pipeline_ensemble",
                    }
                ],
            }
        }
    }

    await integrator.process_pipeline_predictions(sample_predictions)

    # Generate analysis
    analysis = await integrator.generate_performance_analysis()
    print(f"Generated analysis with {len(analysis)} components")


if __name__ == "__main__":
    asyncio.run(main())
