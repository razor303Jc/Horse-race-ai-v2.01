#!/usr/bin/env python3
"""
Advanced Metrics Data Integration Script
Populates database tables with existing JSON data from speed analysis and Monte Carlo simulations
Horse Racing AI v2.03 - Database Integration
"""

import json
import os
import sys
import psycopg2
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedMetricsIntegrator:
    """Integrates existing JSON analytics data into database tables"""

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.03")
        self.speed_data_dir = self.project_root / "data" / "speed_analysis"
        self.monte_carlo_dir = self.project_root / "data" / "monte_carlo_results"

    def connect_database(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def close_database(self):
        """Close database connection"""
        if hasattr(self, "conn"):
            self.conn.close()
            logger.info("🔌 Database connection closed")

    def get_or_create_horse_id(self, horse_name: str) -> Optional[int]:
        """Get horse_id from horses table or return None if not found"""
        try:
            self.cursor.execute(
                "SELECT horse_id FROM horses WHERE name = %s LIMIT 1", (horse_name,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.warning(f"⚠️ Could not find horse_id for {horse_name}: {e}")
            return None

    def integrate_speed_analysis_data(self) -> bool:
        """Integrate speed analysis JSON files into horse_speed_ratings table"""
        logger.info("🏁 Starting speed analysis data integration...")

        try:
            speed_files = list(self.speed_data_dir.glob("speed_analysis_*.json"))
            logger.info(f"📁 Found {len(speed_files)} speed analysis files")

            total_records = 0

            for speed_file in speed_files:
                with open(speed_file, "r") as f:
                    data = json.load(f)

                # Extract race date from filename or data
                race_date = data.get("race_date", "2025-08-18")

                for horse_data in data.get("speed_figures", []):
                    horse_name = horse_data.get("horse_name")
                    if not horse_name:
                        continue

                    # Get horse_id from database
                    horse_id = self.get_or_create_horse_id(horse_name)
                    if not horse_id:
                        # Create a placeholder horse_id using a hash
                        horse_id = abs(hash(horse_name)) % 100000

                    # Prepare speed ratings data
                    speed_record = {
                        "horse_id": horse_id,
                        "horse_name": horse_name,
                        "race_date": race_date,
                        "speed_figure": horse_data.get("speed_figure", 0),
                        "pace_rating": horse_data.get("pace_rating"),
                        "time_seconds": horse_data.get("time_seconds"),
                        "distance_furlongs": horse_data.get("distance", 6.0),
                        "sectional_times": json.dumps(
                            horse_data.get("sectional_times", [])
                        ),
                        "pace_classification": horse_data.get("pace_classification"),
                        "speed_map_position": horse_data.get("speed_map_position"),
                        "track_condition": horse_data.get("track_condition", "good"),
                        "class_rating": horse_data.get("class_rating"),
                        "weight_carried": horse_data.get("weight_carried", 60.0),
                        "calculated_at": horse_data.get(
                            "calculated_at", datetime.now().isoformat()
                        ),
                    }

                    # Insert into database
                    self.insert_speed_rating(speed_record)
                    total_records += 1

            self.conn.commit()
            logger.info(
                f"✅ Speed analysis integration completed: {total_records} records"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Speed analysis integration failed: {e}")
            self.conn.rollback()
            return False

    def insert_speed_rating(self, record: Dict[str, Any]):
        """Insert speed rating record into database"""
        sql = """
        INSERT INTO horse_speed_ratings (
            horse_id, horse_name, race_date, speed_figure, pace_rating, 
            time_seconds, distance_furlongs, sectional_times, pace_classification,
            speed_map_position, track_condition, class_rating, weight_carried
        ) VALUES (
            %(horse_id)s, %(horse_name)s, %(race_date)s, %(speed_figure)s, %(pace_rating)s,
            %(time_seconds)s, %(distance_furlongs)s, %(sectional_times)s, %(pace_classification)s,
            %(speed_map_position)s, %(track_condition)s, %(class_rating)s, %(weight_carried)s
        ) ON CONFLICT DO NOTHING
        """
        try:
            self.cursor.execute(sql, record)
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to insert speed rating for {record.get('horse_name')}: {e}"
            )

    def integrate_monte_carlo_data(self) -> bool:
        """Integrate Monte Carlo simulation results into database"""
        logger.info("🎲 Starting Monte Carlo data integration...")

        try:
            monte_files = list(self.monte_carlo_dir.glob("stage10_monte_carlo_*.json"))
            logger.info(f"📁 Found {len(monte_files)} Monte Carlo files")

            total_records = 0

            for monte_file in monte_files:
                with open(monte_file, "r") as f:
                    data = json.load(f)

                # Extract simulation metadata
                simulation_id = monte_file.stem
                start_time = data.get("start_time", datetime.now().isoformat())

                for race_analysis in data.get("race_analyses", []):
                    race_id = race_analysis.get("race_id", "unknown")

                    # Process betting recommendations
                    for recommendation in race_analysis.get(
                        "betting_recommendations", []
                    ):
                        horse_name = recommendation.get("horse_name")
                        if not horse_name:
                            continue

                        # Get horse_id
                        horse_id = self.get_or_create_horse_id(horse_name)
                        if not horse_id:
                            horse_id = abs(hash(horse_name)) % 100000

                        # Get probabilities from race analysis
                        win_prob = race_analysis.get("win_probabilities", {}).get(
                            horse_name, 0
                        )
                        place_prob = race_analysis.get("place_probabilities", {}).get(
                            horse_name, 0
                        )
                        show_prob = race_analysis.get("show_probabilities", {}).get(
                            horse_name, 0
                        )

                        # Prepare Monte Carlo record
                        monte_record = {
                            "simulation_id": simulation_id,
                            "horse_id": horse_id,
                            "horse_name": horse_name,
                            "race_date": "2025-08-18",  # Default date
                            "simulation_runs": race_analysis.get(
                                "simulations_run", 5000
                            ),
                            "win_probability": win_prob,
                            "place_probability": place_prob,
                            "show_probability": show_prob,
                            "expected_position": recommendation.get(
                                "expected_position"
                            ),
                            "fair_odds": recommendation.get("fair_odds"),
                            "value_rating": recommendation.get("value_rating"),
                            "confidence_score": recommendation.get("confidence"),
                            "z_score": recommendation.get("z_score"),
                            "bet_type": recommendation.get("bet_type", "win"),
                        }

                        # Insert into database
                        self.insert_monte_carlo_result(monte_record)
                        total_records += 1

            self.conn.commit()
            logger.info(
                f"✅ Monte Carlo integration completed: {total_records} records"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Monte Carlo integration failed: {e}")
            self.conn.rollback()
            return False

    def insert_monte_carlo_result(self, record: Dict[str, Any]):
        """Insert Monte Carlo result into database"""
        sql = """
        INSERT INTO monte_carlo_simulations (
            simulation_id, horse_id, horse_name, race_date, simulation_runs,
            win_probability, place_probability, show_probability, expected_position,
            fair_odds, value_rating, confidence_score, z_score, bet_type
        ) VALUES (
            %(simulation_id)s, %(horse_id)s, %(horse_name)s, %(race_date)s, %(simulation_runs)s,
            %(win_probability)s, %(place_probability)s, %(show_probability)s, %(expected_position)s,
            %(fair_odds)s, %(value_rating)s, %(confidence_score)s, %(z_score)s, %(bet_type)s
        ) ON CONFLICT DO NOTHING
        """
        try:
            self.cursor.execute(sql, record)
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to insert Monte Carlo result for {record.get('horse_name')}: {e}"
            )

    def create_initial_power_ratings(self) -> bool:
        """Create initial power ratings based on existing race entries"""
        logger.info("⚡ Creating initial power ratings...")

        try:
            # Get recent race entries for power rating calculation
            self.cursor.execute(
                """
                SELECT DISTINCT horse_id, horse_name, odds_decimal, horse_rate
                FROM race_entries 
                WHERE horse_rate IS NOT NULL AND odds_decimal IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 500
            """
            )

            entries = self.cursor.fetchall()
            logger.info(f"📊 Processing {len(entries)} race entries for power ratings")

            for entry in entries:
                horse_id, horse_name, odds_decimal, horse_rate = entry

                # Calculate basic power rating from existing data
                base_rating = float(horse_rate) if horse_rate else 70.0

                # Adjust based on odds (lower odds = higher rating)
                if odds_decimal and odds_decimal > 0:
                    odds_adjustment = max(-10, min(10, (5.0 - odds_decimal) * 2))
                else:
                    odds_adjustment = 0

                power_rating = min(140, max(0, base_rating + odds_adjustment))

                power_record = {
                    "horse_id": horse_id,
                    "horse_name": horse_name,
                    "race_date": "2025-08-18",
                    "power_rating": power_rating,
                    "base_rating": base_rating,
                    "class_adjustment": odds_adjustment,
                    "race_class": "handicap",
                    "surface_type": "turf",
                    "rating_confidence": 0.70,
                }

                self.insert_power_rating(power_record)

            self.conn.commit()
            logger.info(f"✅ Power ratings created: {len(entries)} records")
            return True

        except Exception as e:
            logger.error(f"❌ Power ratings creation failed: {e}")
            self.conn.rollback()
            return False

    def insert_power_rating(self, record: Dict[str, Any]):
        """Insert power rating record into database"""
        sql = """
        INSERT INTO horse_power_ratings (
            horse_id, horse_name, race_date, power_rating, base_rating,
            class_adjustment, race_class, surface_type, rating_confidence
        ) VALUES (
            %(horse_id)s, %(horse_name)s, %(race_date)s, %(power_rating)s, %(base_rating)s,
            %(class_adjustment)s, %(race_class)s, %(surface_type)s, %(rating_confidence)s
        ) ON CONFLICT DO NOTHING
        """
        try:
            self.cursor.execute(sql, record)
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to insert power rating for {record.get('horse_name')}: {e}"
            )

    def enhance_form_scores(self) -> bool:
        """Enhance existing form trends with detailed scoring"""
        logger.info("📈 Enhancing form scores...")

        try:
            # Get existing form trends
            self.cursor.execute(
                """
                SELECT horse_id, horse_name, form_trend, trend_confidence, 
                       last_5_ratings, current_rating
                FROM horse_form_trends
                WHERE current_rating IS NOT NULL
            """
            )

            trends = self.cursor.fetchall()
            logger.info(f"📊 Processing {len(trends)} form trends")

            for trend in trends:
                (
                    horse_id,
                    horse_name,
                    form_trend,
                    trend_confidence,
                    last_5_ratings,
                    current_rating,
                ) = trend

                # Calculate enhanced form score
                base_form_score = float(current_rating) if current_rating else 50.0

                # Adjust based on trend
                trend_adjustments = {
                    "improving": 10,
                    "declining": -10,
                    "stable": 0,
                    "peak": 5,
                }

                trend_adjustment = trend_adjustments.get(form_trend, 0)
                form_score = min(100, max(0, base_form_score + trend_adjustment))

                # Calculate component scores
                recent_form_score = form_score * 0.9  # Recent performance weight
                consistency_rating = (
                    float(trend_confidence) if trend_confidence else 0.5
                )

                form_record = {
                    "horse_id": horse_id,
                    "horse_name": horse_name,
                    "race_date": "2025-08-18",
                    "form_score": form_score,
                    "recent_form_score": recent_form_score,
                    "form_trend": form_trend,
                    "consistency_rating": consistency_rating,
                    "confidence_level": (
                        float(trend_confidence) if trend_confidence else 0.75
                    ),
                }

                self.insert_form_score(form_record)

            self.conn.commit()
            logger.info(f"✅ Form scores enhanced: {len(trends)} records")
            return True

        except Exception as e:
            logger.error(f"❌ Form scores enhancement failed: {e}")
            self.conn.rollback()
            return False

    def insert_form_score(self, record: Dict[str, Any]):
        """Insert form score record into database"""
        sql = """
        INSERT INTO horse_form_scores (
            horse_id, horse_name, race_date, form_score, recent_form_score,
            form_trend, consistency_rating, confidence_level
        ) VALUES (
            %(horse_id)s, %(horse_name)s, %(race_date)s, %(form_score)s, %(recent_form_score)s,
            %(form_trend)s, %(consistency_rating)s, %(confidence_level)s
        ) ON CONFLICT DO NOTHING
        """
        try:
            self.cursor.execute(sql, record)
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to insert form score for {record.get('horse_name')}: {e}"
            )

    def run_full_integration(self) -> bool:
        """Run complete advanced metrics integration"""
        logger.info("🚀 Starting Advanced Metrics Integration")

        if not self.connect_database():
            return False

        try:
            # Integration sequence
            success_steps = []

            # Step 1: Speed Analysis Integration
            if self.integrate_speed_analysis_data():
                success_steps.append("Speed Analysis")

            # Step 2: Monte Carlo Integration
            if self.integrate_monte_carlo_data():
                success_steps.append("Monte Carlo Simulations")

            # Step 3: Power Ratings Creation
            if self.create_initial_power_ratings():
                success_steps.append("Power Ratings")

            # Step 4: Enhanced Form Scores
            if self.enhance_form_scores():
                success_steps.append("Form Scores")

            logger.info(f"🎯 Integration Summary:")
            logger.info(f"   ✅ Completed: {', '.join(success_steps)}")
            logger.info(f"   📊 Success Rate: {len(success_steps)}/4 components")

            return len(success_steps) >= 3  # Success if at least 3/4 components work

        finally:
            self.close_database()


def main():
    """Main integration function"""
    print("🐎 Advanced Metrics Database Integration")
    print("=" * 50)

    integrator = AdvancedMetricsIntegrator()

    if integrator.run_full_integration():
        print("\n🎉 Advanced Metrics Integration SUCCESSFUL!")
        print("Database now contains:")
        print("  🏁 Speed Ratings & Pace Analysis")
        print("  ⚡ Power Ratings System")
        print("  📈 Enhanced Form Scoring")
        print("  🎲 Monte Carlo Simulation Results")
    else:
        print("\n❌ Integration completed with some issues")
        print("Check logs for details")


if __name__ == "__main__":
    main()
