#!/usr/bin/env python3
"""
AI Predictions Pipeline Integration
==================================

Integrates AI race predictions generation into the enhanced pipeline automation.
This module handles the daily workflow of generating and storing AI predictions.

Features:
- Automated daily AI predictions generation
- Integration with pipeline timing system
- Database storage and management
- Performance monitoring and reporting
- Error handling and recovery
"""

import sys
import os
import logging
import json
import asyncio
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import psycopg2
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our AI predictions generator
from tools.ml_training.ai_race_predictions_generator import AIRacePredictionsGenerator

# Import pipeline components
try:
    from tools.ml_training.enhanced_pipeline_integration import PipelineManager
    from tools.ml_training.time_aware_ml_optimizer import TimeAwareMLOptimizer
except ImportError as e:
    logging.warning(f"Pipeline imports not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIPredictionsPipelineIntegration:
    """
    Integrates AI predictions generation into the main pipeline automation.
    """

    def __init__(
        self,
        models_dir: str = None,
        db_config: Dict[str, Any] = None,
        pipeline_config: Dict[str, Any] = None,
    ):
        """Initialize the AI predictions pipeline integration."""

        self.models_dir = models_dir
        self.db_config = db_config or self._get_default_db_config()
        self.pipeline_config = pipeline_config or self._get_default_pipeline_config()

        # Initialize components
        self.predictions_generator = AIRacePredictionsGenerator(
            models_dir=models_dir, db_config=db_config
        )

        # Pipeline integration settings
        self.daily_schedule = {
            "ai_predictions_time": time(6, 0),  # Generate predictions at 6:00 AM
            "update_predictions_time": time(8, 0),  # Update predictions at 8:00 AM
            "final_predictions_time": time(10, 0),  # Final predictions at 10:00 AM
            "results_processing_time": time(20, 0),  # Process results at 8:00 PM
        }

        # Status tracking
        self.daily_status = {
            "predictions_generated": False,
            "predictions_updated": False,
            "final_predictions_completed": False,
            "results_processed": False,
            "last_run_date": None,
            "error_count": 0,
            "last_error": None,
        }

        logger.info("🤖 AI Predictions Pipeline Integration initialized")

    def _get_default_db_config(self) -> Dict[str, Any]:
        """Get default database configuration."""
        # Check if running in Docker environment
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            # Parse Docker DATABASE_URL: postgresql://user:pass@host:port/db
            import urllib.parse as urlparse

            url = urlparse.urlparse(database_url)
            return {
                "host": url.hostname,
                "port": url.port or 5432,
                "user": url.username,
                "password": url.password,
                "database": url.path[1:],  # Remove leading '/'
            }
        else:
            # Local development configuration
            return {
                "host": "localhost",
                "port": 5432,
                "user": "horse_racing",
                "password": "secure_password_123",
                "database": "horse_racing_db",
            }

    def _get_default_pipeline_config(self) -> Dict[str, Any]:
        """Get default pipeline configuration."""
        return {
            "auto_predictions": True,
            "prediction_frequency": "daily",
            "confidence_threshold": 0.6,
            "store_individual_models": True,
            "generate_summaries": True,
            "enable_performance_tracking": True,
            "max_daily_retries": 3,
            "notification_webhook": None,
        }

    @contextmanager
    def get_db_connection(self):
        """Get database connection with context manager."""
        connection = None
        try:
            connection = psycopg2.connect(**self.db_config)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def is_new_day(self) -> bool:
        """Check if it's a new day since last run."""
        today = date.today()
        last_run = self.daily_status.get("last_run_date")

        if last_run is None:
            return True

        if isinstance(last_run, str):
            try:
                last_run = datetime.strptime(last_run, "%Y-%m-%d").date()
            except ValueError:
                return True

        return today > last_run

    def reset_daily_status(self):
        """Reset daily status for new day."""
        self.daily_status.update(
            {
                "predictions_generated": False,
                "predictions_updated": False,
                "final_predictions_completed": False,
                "results_processed": False,
                "error_count": 0,
                "last_error": None,
            }
        )
        logger.info("🔄 Daily status reset for new day")

    def should_run_ai_predictions(self, current_time: time = None) -> bool:
        """Determine if AI predictions should run now."""
        if current_time is None:
            current_time = datetime.now().time()

        # Check if it's a new day
        if self.is_new_day():
            self.reset_daily_status()

        # Check if predictions already generated today
        if self.daily_status["predictions_generated"]:
            return False

        # Check if it's time for predictions
        ai_time = self.daily_schedule["ai_predictions_time"]
        time_window = timedelta(minutes=30)  # 30-minute window

        current_datetime = datetime.combine(date.today(), current_time)
        scheduled_datetime = datetime.combine(date.today(), ai_time)

        time_diff = abs((current_datetime - scheduled_datetime).total_seconds())

        return time_diff <= time_window.total_seconds()

    def check_race_data_availability(self, race_date: date = None) -> bool:
        """Check if race data is available for prediction."""
        if race_date is None:
            race_date = date.today()

        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Check for race cards data
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT race_id) 
                    FROM race_cards 
                    WHERE race_date = %s
                """,
                    (race_date,),
                )

                race_count = cursor.fetchone()[0]

                if race_count == 0:
                    logger.warning(f"No race data found for {race_date}")
                    return False

                # Check for race entries
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM race_entries re
                    JOIN race_cards rc ON re.race_id = rc.race_id
                    WHERE rc.race_date = %s
                      AND re.odds_decimal > 0
                """,
                    (race_date,),
                )

                entry_count = cursor.fetchone()[0]

                if entry_count == 0:
                    logger.warning(f"No race entries with odds found for {race_date}")
                    return False

                logger.info(
                    f"✅ Race data available: {race_count} races, {entry_count} entries"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to check race data availability: {e}")
            return False

    def generate_daily_predictions(self, race_date: date = None) -> Dict[str, Any]:
        """Generate daily predictions with error handling and retry logic."""
        if race_date is None:
            race_date = date.today()

        logger.info(
            f"""
╭─────────────────────────────────────────╮
│       AI Predictions Pipeline          │
│                                         │
│  📅 Date: {race_date}                   │
│  🤖 Mode: Automated Daily Generation    │
│  🔄 Integration: Enhanced Pipeline      │
╰─────────────────────────────────────────╯
        """
        )

        results = {
            "success": False,
            "date": race_date.isoformat(),
            "predictions_generated": 0,
            "predictions_stored": 0,
            "races_processed": 0,
            "error_messages": [],
            "execution_time_seconds": 0,
            "retry_count": 0,
        }

        start_time = datetime.now()
        max_retries = self.pipeline_config.get("max_daily_retries", 3)

        for attempt in range(max_retries):
            try:
                results["retry_count"] = attempt

                # Step 1: Check data availability
                logger.info(
                    f"🔍 Attempt {attempt + 1}/{max_retries}: Checking data availability..."
                )
                if not self.check_race_data_availability(race_date):
                    error_msg = f"No race data available for {race_date}"
                    results["error_messages"].append(error_msg)
                    logger.warning(error_msg)

                    if attempt == max_retries - 1:
                        break

                    # Wait and retry
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue

                # Step 2: Generate predictions
                logger.info("🎯 Generating AI predictions...")
                prediction_results = (
                    self.predictions_generator.generate_daily_predictions(race_date)
                )

                # Step 3: Validate results
                if prediction_results.get("errors"):
                    error_msg = f"Prediction errors: {prediction_results['errors']}"
                    results["error_messages"].extend(prediction_results["errors"])
                    logger.error(error_msg)

                    if attempt == max_retries - 1:
                        break

                    # Wait and retry
                    await asyncio.sleep(180)  # Wait 3 minutes
                    continue

                # Step 4: Update results
                results.update(
                    {
                        "success": True,
                        "predictions_generated": prediction_results.get(
                            "predictions_generated", 0
                        ),
                        "predictions_stored": prediction_results.get(
                            "predictions_stored", 0
                        ),
                        "races_processed": prediction_results.get("total_races", 0),
                    }
                )

                # Step 5: Update daily status
                self.daily_status.update(
                    {
                        "predictions_generated": True,
                        "last_run_date": race_date.isoformat(),
                        "error_count": 0,
                        "last_error": None,
                    }
                )

                # Step 6: Store daily summary
                self.store_daily_summary(prediction_results, race_date)

                logger.info("✅ AI predictions generation completed successfully")
                break

            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                results["error_messages"].append(error_msg)
                logger.error(error_msg)

                self.daily_status["error_count"] += 1
                self.daily_status["last_error"] = error_msg

                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    break

                # Wait before retry
                await asyncio.sleep(120)  # Wait 2 minutes

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time_seconds"] = round(execution_time, 2)

        return results

    def store_daily_summary(self, prediction_results: Dict[str, Any], race_date: date):
        """Store daily summary to database."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Update daily summary
                cursor.execute(
                    "SELECT update_daily_prediction_summary(%s)", (race_date,)
                )
                conn.commit()

                logger.info("📊 Daily summary stored to database")

        except Exception as e:
            logger.error(f"Failed to store daily summary: {e}")

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        status = {
            "current_time": datetime.now().isoformat(),
            "daily_status": self.daily_status.copy(),
            "schedule": {k: v.isoformat() for k, v in self.daily_schedule.items()},
            "config": self.pipeline_config.copy(),
            "models_loaded": self.predictions_generator.is_loaded,
            "next_scheduled_run": None,
        }

        # Calculate next scheduled run
        current_time = datetime.now().time()
        ai_time = self.daily_schedule["ai_predictions_time"]

        if current_time < ai_time and not self.daily_status["predictions_generated"]:
            next_run = datetime.combine(date.today(), ai_time)
        else:
            next_run = datetime.combine(date.today() + timedelta(days=1), ai_time)

        status["next_scheduled_run"] = next_run.isoformat()

        return status

    async def run_pipeline_cycle(self):
        """Run a single pipeline cycle (called by enhanced pipeline)."""
        logger.info("🔄 Starting AI predictions pipeline cycle...")

        current_time = datetime.now().time()

        # Check if we should run predictions
        if not self.should_run_ai_predictions(current_time):
            logger.debug("⏭️ Not time for AI predictions")
            return {"skipped": True, "reason": "Not scheduled time"}

        # Check if models are loaded
        if not self.predictions_generator.is_loaded:
            logger.error("❌ ML models not loaded - cannot generate predictions")
            return {"error": "ML models not loaded"}

        # Generate predictions
        try:
            results = await self.generate_daily_predictions()

            if results["success"]:
                logger.info(
                    f"✅ Pipeline cycle completed: {results['predictions_stored']} predictions stored"
                )
            else:
                logger.error(f"❌ Pipeline cycle failed: {results['error_messages']}")

            return results

        except Exception as e:
            logger.error(f"❌ Pipeline cycle exception: {e}")
            return {"error": str(e)}

    async def continuous_monitoring(self, check_interval: int = 300):
        """Continuous monitoring loop for AI predictions."""
        logger.info(
            f"🔄 Starting AI predictions continuous monitoring (check every {check_interval}s)"
        )

        while True:
            try:
                # Run pipeline cycle
                await self.run_pipeline_cycle()

                # Wait for next check
                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    def manual_prediction_run(self, race_date: date = None) -> Dict[str, Any]:
        """Manually trigger prediction generation."""
        if race_date is None:
            race_date = date.today()

        logger.info(f"🔧 Manual prediction run triggered for {race_date}")

        # Reset daily status to allow manual run
        self.reset_daily_status()

        # Run predictions synchronously
        import asyncio

        return asyncio.run(self.generate_daily_predictions(race_date))

    def get_recent_predictions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent predictions for analysis."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT 
                        DATE(created_at) as prediction_date,
                        COUNT(*) as total_predictions,
                        COUNT(DISTINCT race_id) as total_races,
                        AVG(ensemble_probability) as avg_probability,
                        AVG(confidence_score) as avg_confidence,
                        COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence
                    FROM ai_predictions 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
                    GROUP BY DATE(created_at)
                    ORDER BY prediction_date DESC
                """

                cursor.execute(query, (days,))
                rows = cursor.fetchall()

                columns = [desc[0] for desc in cursor.description]

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent predictions: {e}")
            return []


def main():
    """Main function for AI predictions pipeline integration."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Predictions Pipeline Integration")
    parser.add_argument(
        "--mode",
        choices=["manual", "monitor", "status"],
        default="manual",
        help="Operation mode",
    )
    parser.add_argument(
        "--date", help="Date for predictions (YYYY-MM-DD)", default=None
    )
    parser.add_argument(
        "--models-dir", help="Directory containing ML models", default=None
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=300,
        help="Monitoring check interval in seconds",
    )

    args = parser.parse_args()

    # Parse date
    prediction_date = None
    if args.date:
        try:
            prediction_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            return 1

    # Initialize pipeline integration
    pipeline = AIPredictionsPipelineIntegration(models_dir=args.models_dir)

    try:
        if args.mode == "manual":
            # Manual prediction run
            results = pipeline.manual_prediction_run(prediction_date)

            if results["success"]:
                logger.info(
                    f"✅ Manual run completed: {results['predictions_stored']} predictions"
                )
                return 0
            else:
                logger.error(f"❌ Manual run failed: {results['error_messages']}")
                return 1

        elif args.mode == "monitor":
            # Continuous monitoring
            asyncio.run(pipeline.continuous_monitoring(args.check_interval))
            return 0

        elif args.mode == "status":
            # Get pipeline status
            status = pipeline.get_pipeline_status()
            logger.info("Pipeline Status:")
            logger.info(f"  Models Loaded: {status['models_loaded']}")
            logger.info(f"  Daily Status: {status['daily_status']}")
            logger.info(f"  Next Run: {status['next_scheduled_run']}")

            # Get recent predictions
            recent = pipeline.get_recent_predictions(7)
            if recent:
                logger.info("Recent Predictions:")
                for day in recent[:3]:
                    logger.info(
                        f"  {day['prediction_date']}: {day['total_predictions']} predictions, {day['total_races']} races"
                    )

            return 0

    except KeyboardInterrupt:
        logger.info("🛑 Process stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Process failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
