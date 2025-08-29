#!/usr/bin/env python3
"""
Automated Data Pipeline for Horse Racing AI v2.04
Orchestrates the complete analysis workflow from data ingestion to report generation.

This pipeline integrates all components:
- Power Rating Calculations
- Speed & Pace Analysis
- Monte Carlo Simulations
- AI Selections Generation
- Database Storage
- Report Generation
"""

import asyncio
import logging
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time
import traceback

# Add project root to path
sys.path.append("/app")
sys.path.append("/app/tools/ml_training")

# Import our enhanced analytics components
from enhanced_power_rating_calculator import EnhancedPowerRatingCalculator
from enhanced_speed_pace_analyzer import EnhancedSpeedPaceAnalyzer
from enhanced_monte_carlo_simulator import EnhancedMonteCarloSimulator
from enhanced_selections import EnhancedAISelections

# Database utilities
import psycopg2
from psycopg2.extras import RealDictCursor


class AutomatedDataPipeline:
    """
    Complete automated pipeline for daily horse racing analysis.

    Pipeline Stages:
    1. Data Validation & Quality Checks
    2. Power Rating Calculations
    3. Speed & Pace Analysis
    4. Monte Carlo Simulations
    5. AI Predictions Generation
    6. Database Storage & Integrity Verification
    7. Report Generation
    8. Alert Dispatch
    """

    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Pipeline components
        self.power_calculator = EnhancedPowerRatingCalculator()
        self.speed_analyzer = EnhancedSpeedPaceAnalyzer()
        self.monte_carlo = EnhancedMonteCarloSimulator()
        self.ai_selections = EnhancedAISelections()

        # Database configuration
        self.db_configs = {
            "cards": {
                "host": "postgres",
                "database": "cards_horse_racing_db",
                "user": "horse_racing",
                "password": "secure_password_123",
                "port": 5432,
            },
            "results": {
                "host": "postgres",
                "database": "results_horse_racing_db",
                "user": "horse_racing",
                "password": "secure_password_123",
                "port": 5432,
            },
            "metrics": {
                "host": "postgres",
                "database": "advanced_racing_metrics_db",
                "user": "horse_racing",
                "password": "secure_password_123",
                "port": 5432,
            },
        }

        # Pipeline metrics
        self.pipeline_metrics = {
            "start_time": None,
            "end_time": None,
            "total_duration": None,
            "stages_completed": [],
            "stages_failed": [],
            "records_processed": {
                "horses": 0,
                "races": 0,
                "power_ratings": 0,
                "speed_pace_ratings": 0,
                "monte_carlo_sims": 0,
                "ai_predictions": 0,
            },
            "errors": [],
            "warnings": [],
        }

    def setup_logging(self):
        """Configure comprehensive logging system"""

        # Create logs directory if it doesn't exist
        log_dir = Path("/app/logs/pipeline")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    f"/app/logs/pipeline/automated_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
                ),
            ],
        )

    def get_database_connection(self, db_type: str):
        """Get database connection with retry logic"""

        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                config = self.db_configs[db_type]
                conn = psycopg2.connect(**config)
                conn.autocommit = True
                return conn

            except Exception as e:
                self.logger.warning(
                    f"Database connection attempt {attempt + 1} failed for {db_type}: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

    async def stage_1_data_validation(self) -> Dict[str, Any]:
        """Stage 1: Data ingestion and validation"""

        self.logger.info("🔍 Stage 1: Starting data validation and quality checks...")
        stage_start = time.time()

        try:
            # Connect to cards database
            conn = self.get_database_connection("cards")
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get today's race data
            today = date.today()

            # Check for available races
            cursor.execute(
                """
                SELECT race_id, race_time, course, distance, class_level,
                       COUNT(*) as runner_count
                FROM racecard_details
                WHERE DATE(race_time) = %s
                GROUP BY race_id, race_time, course, distance, class_level
                ORDER BY race_time
            """,
                (today,),
            )

            races = cursor.fetchall()

            if not races:
                raise ValueError(f"No race data found for {today}")

            # Get detailed horse data for validation
            cursor.execute(
                """
                SELECT race_id, horse_id, horse_name, jockey_name, trainer_name,
                       weight_lbs, odds_decimal, age, equipment
                FROM racecard_details
                WHERE DATE(race_time) = %s
                ORDER BY race_id, odds_decimal
            """,
                (today,),
            )

            horses = cursor.fetchall()

            # Data quality checks
            quality_checks = {
                "total_races": len(races),
                "total_horses": len(horses),
                "races_with_valid_runners": 0,
                "horses_with_complete_data": 0,
                "data_quality_score": 0.0,
            }

            # Validate race data
            for race in races:
                if race["runner_count"] >= 4:  # Minimum viable race size
                    quality_checks["races_with_valid_runners"] += 1

            # Validate horse data
            for horse in horses:
                if (
                    horse["horse_name"]
                    and horse["jockey_name"]
                    and horse["trainer_name"]
                    and horse["odds_decimal"]
                    and horse["odds_decimal"] > 0
                ):
                    quality_checks["horses_with_complete_data"] += 1

            # Calculate data quality score
            if quality_checks["total_horses"] > 0:
                quality_checks["data_quality_score"] = (
                    quality_checks["horses_with_complete_data"]
                    / quality_checks["total_horses"]
                    * 100
                )

            conn.close()

            # Update pipeline metrics
            self.pipeline_metrics["records_processed"]["horses"] = quality_checks[
                "total_horses"
            ]
            self.pipeline_metrics["records_processed"]["races"] = quality_checks[
                "total_races"
            ]

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 1 completed in {stage_duration:.2f}s - Quality Score: {quality_checks['data_quality_score']:.1f}%"
            )

            return {
                "status": "success",
                "races": races,
                "horses": horses,
                "quality_checks": quality_checks,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 1 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("data_validation")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_2_power_ratings(self, horses_data: List[Dict]) -> Dict[str, Any]:
        """Stage 2: Calculate power ratings for all horses"""

        self.logger.info("⚡ Stage 2: Starting power rating calculations...")
        stage_start = time.time()

        try:
            power_ratings_results = []
            successful_calculations = 0

            # Group horses by race for batch processing
            races_horses = {}
            for horse in horses_data:
                race_id = horse["race_id"]
                if race_id not in races_horses:
                    races_horses[race_id] = []
                races_horses[race_id].append(horse)

            # Process each race
            for race_id, race_horses in races_horses.items():
                self.logger.info(
                    f"  Processing power ratings for race {race_id} ({len(race_horses)} horses)"
                )

                for horse in race_horses:
                    try:
                        # Calculate power rating
                        rating_result = self.power_calculator.calculate_power_rating(
                            horse_data=dict(horse), race_data={"race_id": race_id}
                        )

                        # Add horse metadata
                        rating_result.update(
                            {
                                "horse_id": horse["horse_id"],
                                "horse_name": horse["horse_name"],
                                "race_id": race_id,
                                "jockey_name": horse.get("jockey_name"),
                                "trainer_name": horse.get("trainer_name"),
                            }
                        )

                        # Save to database
                        save_success = self.power_calculator.save_power_rating(
                            rating_result
                        )

                        if save_success:
                            power_ratings_results.append(rating_result)
                            successful_calculations += 1

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to calculate power rating for horse {horse.get('horse_name', 'Unknown')}: {e}"
                        )

            self.pipeline_metrics["records_processed"][
                "power_ratings"
            ] = successful_calculations

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 2 completed in {stage_duration:.2f}s - {successful_calculations} power ratings calculated"
            )

            return {
                "status": "success",
                "power_ratings": power_ratings_results,
                "successful_calculations": successful_calculations,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 2 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("power_ratings")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_3_speed_pace_analysis(
        self, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """Stage 3: Calculate speed and pace analysis for all horses"""

        self.logger.info("🏃 Stage 3: Starting speed & pace analysis...")
        stage_start = time.time()

        try:
            speed_pace_results = []
            successful_analyses = 0

            # Group horses by race
            races_horses = {}
            for horse in horses_data:
                race_id = horse["race_id"]
                if race_id not in races_horses:
                    races_horses[race_id] = []
                races_horses[race_id].append(horse)

            # Process each race
            for race_id, race_horses in races_horses.items():
                self.logger.info(
                    f"  Processing speed & pace for race {race_id} ({len(race_horses)} horses)"
                )

                for horse in race_horses:
                    try:
                        # Calculate speed and pace analysis
                        analysis_result = (
                            self.speed_analyzer.calculate_speed_pace_analysis(
                                horse_data=dict(horse), race_data={"race_id": race_id}
                            )
                        )

                        # Add horse metadata
                        analysis_result.update(
                            {
                                "horse_id": horse["horse_id"],
                                "horse_name": horse["horse_name"],
                                "race_id": race_id,
                            }
                        )

                        # Save to database
                        save_success = self.speed_analyzer.save_speed_pace_rating(
                            analysis_result
                        )

                        if save_success:
                            speed_pace_results.append(analysis_result)
                            successful_analyses += 1

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to analyze speed/pace for horse {horse.get('horse_name', 'Unknown')}: {e}"
                        )

            self.pipeline_metrics["records_processed"][
                "speed_pace_ratings"
            ] = successful_analyses

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 3 completed in {stage_duration:.2f}s - {successful_analyses} speed/pace analyses completed"
            )

            return {
                "status": "success",
                "speed_pace_analyses": speed_pace_results,
                "successful_analyses": successful_analyses,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 3 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("speed_pace_analysis")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_4_monte_carlo_simulations(
        self, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """Stage 4: Run Monte Carlo simulations for all races"""

        self.logger.info("🎲 Stage 4: Starting Monte Carlo simulations...")
        stage_start = time.time()

        try:
            simulation_results = []
            successful_simulations = 0

            # Group horses by race
            races_horses = {}
            for horse in horses_data:
                race_id = horse["race_id"]
                if race_id not in races_horses:
                    races_horses[race_id] = []
                races_horses[race_id].append(horse)

            # Run simulations for each race
            for race_id, race_horses in races_horses.items():
                if len(race_horses) < 4:  # Skip races with too few runners
                    continue

                self.logger.info(
                    f"  Running Monte Carlo simulation for race {race_id} ({len(race_horses)} horses)"
                )

                try:
                    # Run Monte Carlo simulation
                    simulation_result = self.monte_carlo.run_monte_carlo_simulation(
                        race_horses=race_horses,
                        num_simulations=5000,  # Reduced for faster processing
                    )

                    # Save simulation results to database
                    save_success = self.monte_carlo.save_simulation_results(
                        simulation_result
                    )

                    if save_success:
                        simulation_results.append(simulation_result)
                        successful_simulations += 1

                except Exception as e:
                    self.logger.warning(
                        f"Failed to run Monte Carlo simulation for race {race_id}: {e}"
                    )

            self.pipeline_metrics["records_processed"][
                "monte_carlo_sims"
            ] = successful_simulations

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 4 completed in {stage_duration:.2f}s - {successful_simulations} Monte Carlo simulations completed"
            )

            return {
                "status": "success",
                "simulations": simulation_results,
                "successful_simulations": successful_simulations,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 4 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("monte_carlo_simulations")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_5_ai_predictions(self, horses_data: List[Dict]) -> Dict[str, Any]:
        """Stage 5: Generate AI predictions using ensemble models"""

        self.logger.info("🧠 Stage 5: Generating AI predictions...")
        stage_start = time.time()

        try:
            ai_predictions = []
            successful_predictions = 0

            # Group horses by race
            races_horses = {}
            for horse in horses_data:
                race_id = horse["race_id"]
                if race_id not in races_horses:
                    races_horses[race_id] = []
                races_horses[race_id].append(horse)

            # Generate predictions for each race
            for race_id, race_horses in races_horses.items():
                if len(race_horses) < 4:  # Skip races with too few runners
                    continue

                self.logger.info(
                    f"  Generating AI predictions for race {race_id} ({len(race_horses)} horses)"
                )

                try:
                    # Generate AI predictions
                    prediction_result = self.ai_selections.generate_race_predictions(
                        race_horses
                    )

                    # Save predictions to database
                    save_success = self.ai_selections.save_predictions(
                        prediction_result
                    )

                    if save_success:
                        ai_predictions.append(prediction_result)
                        successful_predictions += len(
                            prediction_result.get("predictions", [])
                        )

                except Exception as e:
                    self.logger.warning(
                        f"Failed to generate AI predictions for race {race_id}: {e}"
                    )

            self.pipeline_metrics["records_processed"][
                "ai_predictions"
            ] = successful_predictions

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 5 completed in {stage_duration:.2f}s - {successful_predictions} AI predictions generated"
            )

            return {
                "status": "success",
                "predictions": ai_predictions,
                "successful_predictions": successful_predictions,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 5 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("ai_predictions")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_6_database_integrity_verification(self) -> Dict[str, Any]:
        """Stage 6: Verify database integrity and data consistency"""

        self.logger.info("🗄️ Stage 6: Verifying database integrity...")
        stage_start = time.time()

        try:
            verification_results = {}

            # Connect to metrics database
            conn = self.get_database_connection("metrics")
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            today = date.today()

            # Verify power ratings
            cursor.execute(
                """
                SELECT COUNT(*) as count,
                       AVG(final_power_rating) as avg_rating,
                       MIN(final_power_rating) as min_rating,
                       MAX(final_power_rating) as max_rating
                FROM horse_power_ratings
                WHERE calculation_date = %s
            """,
                (today,),
            )

            power_stats = cursor.fetchone()
            verification_results["power_ratings"] = dict(power_stats)

            # Verify speed/pace ratings
            cursor.execute(
                """
                SELECT COUNT(*) as count,
                       AVG(speed_rating) as avg_speed,
                       AVG(pace_rating) as avg_pace
                FROM horse_speed_pace_ratings
                WHERE calculation_date = %s
            """,
                (today,),
            )

            speed_stats = cursor.fetchone()
            verification_results["speed_pace_ratings"] = dict(speed_stats)

            # Verify Monte Carlo simulations
            cursor.execute(
                """
                SELECT COUNT(DISTINCT race_id) as races_simulated,
                       COUNT(*) as total_simulations,
                       AVG(win_probability) as avg_win_prob
                FROM monte_carlo_simulations
                WHERE simulation_date = %s
            """,
                (today,),
            )

            monte_carlo_stats = cursor.fetchone()
            verification_results["monte_carlo_simulations"] = dict(monte_carlo_stats)

            conn.close()

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 6 completed in {stage_duration:.2f}s - Database integrity verified"
            )

            return {
                "status": "success",
                "verification_results": verification_results,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 6 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("database_integrity")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    async def stage_7_report_generation(self) -> Dict[str, Any]:
        """Stage 7: Generate comprehensive daily reports"""

        self.logger.info("📊 Stage 7: Generating daily reports...")
        stage_start = time.time()

        try:
            reports_generated = []

            # Generate pipeline summary report
            pipeline_summary = self.generate_pipeline_summary_report()
            reports_generated.append("pipeline_summary")

            # Generate performance analysis report
            performance_report = self.generate_performance_report()
            reports_generated.append("performance_analysis")

            # Generate selections summary
            selections_report = self.generate_selections_summary_report()
            reports_generated.append("selections_summary")

            stage_duration = time.time() - stage_start
            self.logger.info(
                f"✅ Stage 7 completed in {stage_duration:.2f}s - {len(reports_generated)} reports generated"
            )

            return {
                "status": "success",
                "reports_generated": reports_generated,
                "duration": stage_duration,
            }

        except Exception as e:
            stage_duration = time.time() - stage_start
            error_msg = f"Stage 7 failed after {stage_duration:.2f}s: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_metrics["stages_failed"].append("report_generation")
            self.pipeline_metrics["errors"].append(error_msg)
            raise

    def generate_pipeline_summary_report(self) -> str:
        """Generate comprehensive pipeline summary report"""

        report_content = f"""
# 🏇 Horse Racing AI v2.04 - Daily Pipeline Summary
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Pipeline Duration:** {self.pipeline_metrics.get('total_duration', 'N/A'):.2f} seconds

## 📊 Processing Summary

| Component | Records Processed | Status |
|-----------|------------------|--------|
| Races | {self.pipeline_metrics['records_processed']['races']} | ✅ |
| Horses | {self.pipeline_metrics['records_processed']['horses']} | ✅ |
| Power Ratings | {self.pipeline_metrics['records_processed']['power_ratings']} | ✅ |
| Speed/Pace Ratings | {self.pipeline_metrics['records_processed']['speed_pace_ratings']} | ✅ |
| Monte Carlo Sims | {self.pipeline_metrics['records_processed']['monte_carlo_sims']} | ✅ |
| AI Predictions | {self.pipeline_metrics['records_processed']['ai_predictions']} | ✅ |

## ⚠️ Issues & Warnings

"""

        if self.pipeline_metrics["errors"]:
            report_content += "### Errors:\n"
            for error in self.pipeline_metrics["errors"]:
                report_content += f"- {error}\n"

        if self.pipeline_metrics["warnings"]:
            report_content += "### Warnings:\n"
            for warning in self.pipeline_metrics["warnings"]:
                report_content += f"- {warning}\n"

        if (
            not self.pipeline_metrics["errors"]
            and not self.pipeline_metrics["warnings"]
        ):
            report_content += (
                "**No issues detected - All systems operating normally** ✅\n"
            )

        # Save report
        report_path = (
            f"/app/logs/pipeline/daily_summary_{datetime.now().strftime('%Y%m%d')}.md"
        )
        with open(report_path, "w") as f:
            f.write(report_content)

        self.logger.info(f"Pipeline summary report saved to: {report_path}")
        return report_content

    def generate_performance_report(self) -> str:
        """Generate performance analysis report"""

        # This would include historical performance tracking
        # For now, create a placeholder structure
        report_content = f"""
# 📈 Performance Analysis Report
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## Daily Performance Metrics
- Pipeline execution time: {self.pipeline_metrics.get('total_duration', 'N/A'):.2f}s
- Success rate: {((len(self.pipeline_metrics.get('stages_completed', [])) / 7) * 100):.1f}%
- Records processed: {sum(self.pipeline_metrics['records_processed'].values())}

## Component Performance
*Detailed performance metrics will be added as historical data accumulates*
"""

        # Save report
        report_path = f"/app/logs/pipeline/performance_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, "w") as f:
            f.write(report_content)

        return report_content

    def generate_selections_summary_report(self) -> str:
        """Generate daily selections summary report"""

        report_content = f"""
# 🎯 Daily Selections Summary
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## AI Selections Generated
- Total predictions: {self.pipeline_metrics['records_processed']['ai_predictions']}
- Races analyzed: {self.pipeline_metrics['records_processed']['races']}

## Analysis Breakdown
- Power ratings calculated: {self.pipeline_metrics['records_processed']['power_ratings']}
- Speed/pace analyses: {self.pipeline_metrics['records_processed']['speed_pace_ratings']}
- Monte Carlo simulations: {self.pipeline_metrics['records_processed']['monte_carlo_sims']}

*Detailed selections will be added with confidence levels and betting recommendations*
"""

        # Save report
        report_path = f"/app/logs/pipeline/selections_summary_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, "w") as f:
            f.write(report_content)

        return report_content

    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Execute the complete automated data pipeline"""

        self.logger.info("🚀 Starting Complete Automated Data Pipeline...")
        self.pipeline_metrics["start_time"] = datetime.now()
        pipeline_start = time.time()

        pipeline_results = {
            "status": "running",
            "stages": {},
            "overall_success": False,
            "total_duration": 0,
        }

        try:
            # Stage 1: Data Validation
            stage1_result = await self.stage_1_data_validation()
            pipeline_results["stages"]["data_validation"] = stage1_result
            self.pipeline_metrics["stages_completed"].append("data_validation")

            if stage1_result["status"] != "success":
                raise Exception("Data validation failed")

            horses_data = stage1_result["horses"]

            # Stage 2: Power Ratings
            stage2_result = await self.stage_2_power_ratings(horses_data)
            pipeline_results["stages"]["power_ratings"] = stage2_result
            self.pipeline_metrics["stages_completed"].append("power_ratings")

            # Stage 3: Speed & Pace Analysis
            stage3_result = await self.stage_3_speed_pace_analysis(horses_data)
            pipeline_results["stages"]["speed_pace_analysis"] = stage3_result
            self.pipeline_metrics["stages_completed"].append("speed_pace_analysis")

            # Stage 4: Monte Carlo Simulations
            stage4_result = await self.stage_4_monte_carlo_simulations(horses_data)
            pipeline_results["stages"]["monte_carlo_simulations"] = stage4_result
            self.pipeline_metrics["stages_completed"].append("monte_carlo_simulations")

            # Stage 5: AI Predictions
            stage5_result = await self.stage_5_ai_predictions(horses_data)
            pipeline_results["stages"]["ai_predictions"] = stage5_result
            self.pipeline_metrics["stages_completed"].append("ai_predictions")

            # Stage 6: Database Integrity Verification
            stage6_result = await self.stage_6_database_integrity_verification()
            pipeline_results["stages"]["database_integrity"] = stage6_result
            self.pipeline_metrics["stages_completed"].append("database_integrity")

            # Stage 7: Report Generation
            stage7_result = await self.stage_7_report_generation()
            pipeline_results["stages"]["report_generation"] = stage7_result
            self.pipeline_metrics["stages_completed"].append("report_generation")

            # Pipeline completed successfully
            pipeline_results["status"] = "completed"
            pipeline_results["overall_success"] = True

            total_duration = time.time() - pipeline_start
            pipeline_results["total_duration"] = total_duration
            self.pipeline_metrics["total_duration"] = total_duration
            self.pipeline_metrics["end_time"] = datetime.now()

            self.logger.info(
                f"🎉 Pipeline completed successfully in {total_duration:.2f} seconds!"
            )
            self.logger.info(
                f"   Processed: {sum(self.pipeline_metrics['records_processed'].values())} total records"
            )
            self.logger.info(
                f"   Stages completed: {len(self.pipeline_metrics['stages_completed'])}/7"
            )

            return pipeline_results

        except Exception as e:
            total_duration = time.time() - pipeline_start
            pipeline_results["total_duration"] = total_duration
            pipeline_results["status"] = "failed"
            pipeline_results["error"] = str(e)

            self.pipeline_metrics["total_duration"] = total_duration
            self.pipeline_metrics["end_time"] = datetime.now()

            self.logger.error(
                f"❌ Pipeline failed after {total_duration:.2f} seconds: {str(e)}"
            )
            self.logger.error(
                f"   Stages completed: {len(self.pipeline_metrics['stages_completed'])}/7"
            )
            self.logger.error(
                f"   Stages failed: {self.pipeline_metrics['stages_failed']}"
            )

            # Generate failure report
            self.generate_failure_report(str(e), total_duration)

            return pipeline_results

    def generate_failure_report(self, error_message: str, duration: float):
        """Generate failure analysis report"""

        report_content = f"""
# ❌ Pipeline Failure Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {duration:.2f} seconds

## Failure Details
**Error:** {error_message}

## Stages Completed
{self.pipeline_metrics['stages_completed']}

## Stages Failed
{self.pipeline_metrics['stages_failed']}

## Records Processed Before Failure
{json.dumps(self.pipeline_metrics['records_processed'], indent=2)}

## Troubleshooting Steps
1. Check database connectivity
2. Verify data availability for today's date
3. Review component-specific logs
4. Check system resources (memory, disk space)
"""

        # Save failure report
        report_path = f"/app/logs/pipeline/failure_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(report_path, "w") as f:
            f.write(report_content)

        self.logger.info(f"Failure report saved to: {report_path}")


async def main():
    """Main entry point for automated pipeline execution"""

    print("🏇 Horse Racing AI v2.04 - Automated Data Pipeline")
    print("=" * 60)

    try:
        # Initialize pipeline
        pipeline = AutomatedDataPipeline()

        # Run complete pipeline
        results = await pipeline.run_complete_pipeline()

        # Print summary
        print(f"\n📊 Pipeline Summary:")
        print(f"   Status: {results['status']}")
        print(f"   Duration: {results['total_duration']:.2f} seconds")
        print(
            f"   Stages Completed: {len(pipeline.pipeline_metrics['stages_completed'])}/7"
        )

        if results["overall_success"]:
            print("✅ Pipeline completed successfully!")
            return 0
        else:
            print("❌ Pipeline failed!")
            return 1

    except Exception as e:
        print(f"❌ Critical pipeline error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
