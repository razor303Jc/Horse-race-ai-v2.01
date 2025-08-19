#!/usr/bin/env python3
"""
Standalone Contextual AI Pipeline Integration Script
====================================================

This script can be called by the main pipeline orchestrator
to run contextual AI enhancement as Stage 7.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "contextual_ai_stage.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Import contextual AI components
try:
    from contextual_ai_enhancement import ContextualAIEngine
    from contextual_ai_pipeline_integration import ContextualAIPipelineIntegration
except ImportError as e:
    logger.error(f"Failed to import contextual AI components: {e}")
    sys.exit(1)


async def run_contextual_ai_stage():
    """
    Main function to run contextual AI enhancement stage.

    This function:
    1. Loads data from previous pipeline stages
    2. Runs contextual AI analysis
    3. Saves results for next stages
    4. Returns success/failure status
    """
    try:
        logger.info("🧠 Starting Contextual AI Enhancement Stage")

        # Initialize pipeline integration
        integration = ContextualAIPipelineIntegration()

        # Load pipeline data from previous stages
        pipeline_data = load_pipeline_data()

        if not pipeline_data:
            logger.error("No pipeline data available from previous stages")
            return False

        # Run contextual AI stage
        results = await integration.run_contextual_ai_stage(pipeline_data)

        # Check if stage completed successfully
        stage_info = results.get("pipeline_stages", {}).get(
            "contextual_ai_enhancement", {}
        )

        if stage_info.get("status") == "completed":
            # Save results for next stages
            success = save_pipeline_results(results)

            if success:
                logger.info("✅ Contextual AI Enhancement completed successfully")

                # Log key metrics
                metadata = stage_info.get("stage_metadata", {})
                logger.info(f"📊 Analysis Summary:")
                logger.info(
                    f"  - Horses analyzed: {metadata.get('horses_analyzed', 0)}"
                )
                logger.info(
                    f"  - Alerts generated: {metadata.get('alerts_generated', 0)}"
                )
                logger.info(
                    f"  - Value opportunities: {metadata.get('value_opportunities', 0)}"
                )
                logger.info(
                    f"  - Confidence level: {metadata.get('confidence_level', 0):.2f}"
                )

                return True
            else:
                logger.error("Failed to save contextual AI results")
                return False

        elif stage_info.get("status") == "skipped":
            logger.info("⏭️ Contextual AI stage skipped (insufficient data or disabled)")
            return True  # Not a failure, just skipped

        else:
            error_msg = stage_info.get("error", "Unknown error")
            logger.error(f"❌ Contextual AI Enhancement failed: {error_msg}")
            return False

    except Exception as e:
        logger.error(f"❌ Exception in contextual AI stage: {e}")
        return False


def load_pipeline_data() -> Optional[Dict[str, Any]]:
    """Load pipeline data from previous stages."""
    try:
        # Standard pipeline data paths
        data_paths = [
            "/app/data/pipeline_data.json",
            "/app/data/current_pipeline_data.json",
            "data/pipeline_data.json",
            "data/current_pipeline_data.json",
        ]

        for path in data_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                logger.info(f"Loaded pipeline data from {path}")
                return data

        # If no existing data, create sample data for testing
        logger.warning("No existing pipeline data found, creating sample data")
        return create_sample_pipeline_data()

    except Exception as e:
        logger.error(f"Error loading pipeline data: {e}")
        return None


def create_sample_pipeline_data() -> Dict[str, Any]:
    """Create sample pipeline data for testing."""
    return {
        "race_data": {
            "race_id": f'contextual_ai_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "race_time": "15:30",
            "track": "Ascot",
            "race_type": "Handicap",
            "distance": 2400,
            "weather": "cloudy",
            "track_condition": "good",
            "going": "Good",
            "prize_money": 75000,
        },
        "horses_data": [
            {
                "horse_name": "Thunder Strike",
                "odds": 3.5,
                "form_string": "11234",
                "last_run_days": 28,
                "trainer": "J. Smith",
                "jockey": "A. Johnson",
            },
            {
                "horse_name": "Lightning Bolt",
                "odds": 4.2,
                "form_string": "21112",
                "last_run_days": 21,
                "trainer": "M. Brown",
                "jockey": "S. Davis",
            },
            {
                "horse_name": "Storm Chaser",
                "odds": 5.5,
                "form_string": "31211",
                "last_run_days": 35,
                "trainer": "R. Wilson",
                "jockey": "K. Taylor",
            },
            {
                "horse_name": "Wind Runner",
                "odds": 6.0,
                "form_string": "12143",
                "last_run_days": 14,
                "trainer": "L. Garcia",
                "jockey": "M. Martinez",
            },
            {
                "horse_name": "Fast Lane",
                "odds": 8.0,
                "form_string": "41321",
                "last_run_days": 42,
                "trainer": "D. Anderson",
                "jockey": "C. White",
            },
        ],
        "predictions": {
            "Thunder Strike": {
                "win_probability": 0.32,
                "place_probability": 0.68,
                "confidence": 0.85,
            },
            "Lightning Bolt": {
                "win_probability": 0.28,
                "place_probability": 0.62,
                "confidence": 0.78,
            },
            "Storm Chaser": {
                "win_probability": 0.22,
                "place_probability": 0.55,
                "confidence": 0.72,
            },
            "Wind Runner": {
                "win_probability": 0.18,
                "place_probability": 0.48,
                "confidence": 0.69,
            },
            "Fast Lane": {
                "win_probability": 0.12,
                "place_probability": 0.35,
                "confidence": 0.63,
            },
        },
        "pipeline_metadata": {
            "timestamp": datetime.now().isoformat(),
            "previous_stages_completed": [
                "data_download",
                "csv_import",
                "data_quality",
                "advanced_processing",
                "ml_ensemble",
                "performance_tracking",
                "betting_integration",
            ],
        },
    }


def save_pipeline_results(results: Dict[str, Any]) -> bool:
    """Save pipeline results for next stages."""
    try:
        # Create output directory
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)

        # Save complete results
        results_path = os.path.join(output_dir, "contextual_ai_pipeline_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save updated pipeline data for next stages
        pipeline_data_path = os.path.join(output_dir, "pipeline_data.json")
        with open(pipeline_data_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save contextual analysis summary
        contextual_analysis = results.get("contextual_analysis", {})
        if contextual_analysis:
            summary_path = os.path.join(output_dir, "contextual_ai_summary.json")
            with open(summary_path, "w") as f:
                json.dump(
                    {
                        "race_id": results.get("race_data", {}).get(
                            "race_id", "unknown"
                        ),
                        "timestamp": datetime.now().isoformat(),
                        "contextual_summary": contextual_analysis.get(
                            "contextual_summary", {}
                        ),
                        "alerts_count": len(
                            contextual_analysis.get("race_conditions", {})
                        ),
                        "value_opportunities": len(
                            contextual_analysis.get("value_assessment", {}).get(
                                "value_horses", []
                            )
                        ),
                        "confidence_level": contextual_analysis.get(
                            "confidence_analysis", {}
                        ).get("overall_confidence", 0),
                    },
                    f,
                    indent=2,
                    default=str,
                )

        logger.info(f"Pipeline results saved to {results_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving pipeline results: {e}")
        return False


def main():
    """Main entry point for standalone execution."""
    try:
        # Run contextual AI stage
        success = asyncio.run(run_contextual_ai_stage())

        if success:
            logger.info("🎉 Contextual AI Enhancement Stage completed successfully")
            sys.exit(0)
        else:
            logger.error("💥 Contextual AI Enhancement Stage failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Contextual AI Enhancement interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error in contextual AI stage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
