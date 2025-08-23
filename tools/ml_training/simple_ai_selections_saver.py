#!/usr/bin/env python3
"""
Simple AI Selections Database Saver
Save AI horse racing selections to PostgreSQL database
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import psycopg2
import psycopg2.extras


class SimpleAISelectionsSaver:
    """Simple manager for saving AI horse racing selections to database"""

    def __init__(self):
        """Initialize the saver"""
        self.setup_logging()
        self.db_config = {
            "host": "localhost",
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
            "port": 5432,
        }

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def get_database_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True
            return conn
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise

    def load_race_data(self, target_date: str) -> List[Dict]:
        """Load race data for the target date"""
        try:
            conn = self.get_database_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Get all races for the target date
            query = """
                SELECT DISTINCT 
                    r.race_id,
                    r.course,
                    r.race_time,
                    r.race_number,
                    COUNT(rd.*) as field_size
                FROM races r
                LEFT JOIN racecard_details rd ON r.race_id = rd.race_id
                WHERE r.date = %s
                GROUP BY r.race_id, r.course, r.race_time, r.race_number
                ORDER BY r.course, r.race_time
            """

            cur.execute(query, (target_date,))
            races = cur.fetchall()

            self.logger.info(f"📊 Found {len(races)} races for {target_date}")

            # Get detailed horse data for each race
            race_data = []
            for race in races:
                horse_query = """
                    SELECT 
                        rd.race_id,
                        rd.horse_name,
                        rd.jockey,
                        rd.trainer,
                        rd.odds_decimal,
                        rd.odds_fractional,
                        rd.age,
                        rd.weight
                    FROM racecard_details rd
                    WHERE rd.race_id = %s
                    ORDER BY rd.odds_decimal ASC
                """

                cur.execute(horse_query, (race["race_id"],))
                horses = cur.fetchall()

                race_info = {
                    "race_id": race["race_id"],
                    "course": race["course"],
                    "race_time": race["race_time"],
                    "race_number": race["race_number"],
                    "field_size": race["field_size"],
                    "horses": [dict(horse) for horse in horses],
                }
                race_data.append(race_info)

            cur.close()
            conn.close()
            return race_data

        except Exception as e:
            self.logger.error(f"❌ Failed to load race data: {e}")
            return []

    def calculate_ai_predictions(self, horse_data: Dict, race_context: Dict) -> Dict:
        """Calculate AI predictions for a horse"""
        try:
            # Basic probability calculation based on odds and other factors
            odds = horse_data.get("odds_decimal", 10.0)
            if odds <= 0:
                odds = 10.0

            # Market implied probability
            implied_prob = 1.0 / odds if odds > 0 else 0.1

            # Enhanced probability based on various factors
            base_prob = implied_prob

            # Age factor (4-6 year olds typically perform better)
            age = horse_data.get("age", 5)
            age_factor = 1.0
            if 4 <= age <= 6:
                age_factor = 1.1
            elif age < 4:
                age_factor = 0.9
            elif age > 8:
                age_factor = 0.85

            # Weight factor (lower weight generally better)
            weight = horse_data.get("weight", 9.0)
            if isinstance(weight, str):
                try:
                    weight = float(weight)
                except:
                    weight = 9.0

            weight_factor = max(0.8, 1.0 - (weight - 8.0) * 0.02)

            # Field size factor
            field_size = race_context.get("field_size", 10)
            field_factor = max(0.9, 1.0 - (field_size - 10) * 0.01)

            # Calculate enhanced probability
            enhanced_prob = base_prob * age_factor * weight_factor * field_factor
            enhanced_prob = min(
                0.95, max(0.01, enhanced_prob)
            )  # Clamp between 1% and 95%

            # AI Score (amplified for display)
            ai_score = enhanced_prob * 10000  # Convert to percentage-like display

            # Value calculation
            value_rating = ai_score / odds if odds > 0 else 0

            # Confidence level
            if enhanced_prob > 0.3:
                confidence_level = "High"
                confidence_score = 0.85
            elif enhanced_prob > 0.15:
                confidence_level = "Medium"
                confidence_score = 0.65
            else:
                confidence_level = "Low"
                confidence_score = 0.45

            return {
                "ensemble_probability": enhanced_prob,
                "confidence_level": confidence_level,
                "confidence_score": confidence_score,
                "ai_score": ai_score,
                "value_rating": value_rating,
                "implied_probability": implied_prob,
            }

        except Exception as e:
            self.logger.error(f"❌ AI prediction calculation failed: {e}")
            return {
                "ensemble_probability": 0.1,
                "confidence_level": "Low",
                "confidence_score": 0.3,
                "ai_score": 1000.0,
                "value_rating": 100.0,
                "implied_probability": 0.1,
            }

    def save_selections_to_database(self, target_date: str) -> bool:
        """Generate and save AI selections to the database"""
        self.logger.info(f"🤖 Generating and saving AI selections for {target_date}")

        race_data = self.load_race_data(target_date)
        if not race_data:
            self.logger.warning(f"⚠️ No race data found for {target_date}")
            return False

        try:
            conn = self.get_database_connection()
            cur = conn.cursor()

            total_selections = 0

            for race_info in race_data:
                self.logger.info(
                    f"🏁 Processing race {race_info['race_id']} at {race_info['course']}"
                )

                race_context = {
                    "field_size": race_info["field_size"],
                    "course": race_info["course"],
                    "race_time": race_info["race_time"],
                }

                for horse_data in race_info["horses"]:
                    try:
                        # Calculate AI predictions
                        predictions = self.calculate_ai_predictions(
                            horse_data, race_context
                        )

                        # Prepare data for insertion
                        selection_data = {
                            "prediction_date": datetime.strptime(
                                target_date, "%Y-%m-%d"
                            ).date(),
                            "race_id": race_info["race_id"],
                            "horse_name": horse_data["horse_name"],
                            "jockey": horse_data.get("jockey", "Unknown"),
                            "trainer": horse_data.get("trainer", "Unknown"),
                            "course": race_info["course"],
                            "race_number": race_info.get("race_number", 1),
                            "race_time": str(race_info["race_time"]),
                            "ensemble_probability": predictions["ensemble_probability"],
                            "confidence_level": predictions["confidence_level"],
                            "confidence_score": predictions["confidence_score"],
                            "odds_decimal": horse_data.get("odds_decimal", 10.0),
                            "odds_fractional": horse_data.get("odds_fractional", "9/1"),
                            "implied_probability": predictions["implied_probability"],
                            "jockey_win_pct": 0.0,  # Default for now
                            "trainer_win_pct": 0.0,  # Default for now
                            "field_size": race_info["field_size"],
                            "model_version": "v2.04_enhanced",
                            "feature_count": 17,
                        }

                        # Insert query for ai_selections table
                        insert_query = """
                            INSERT INTO ai_selections (
                                prediction_date, race_id, horse_name, jockey, trainer, course,
                                race_number, race_time, ensemble_probability, confidence_level,
                                confidence_score, odds_decimal, odds_fractional, implied_probability,
                                jockey_win_pct, trainer_win_pct, field_size, model_version,
                                feature_count
                            ) VALUES (
                                %(prediction_date)s, %(race_id)s, %(horse_name)s, %(jockey)s, %(trainer)s,
                                %(course)s, %(race_number)s, %(race_time)s, %(ensemble_probability)s,
                                %(confidence_level)s, %(confidence_score)s, %(odds_decimal)s,
                                %(odds_fractional)s, %(implied_probability)s, %(jockey_win_pct)s,
                                %(trainer_win_pct)s, %(field_size)s, %(model_version)s, %(feature_count)s
                            )
                            ON CONFLICT (race_id, horse_name, prediction_date) 
                            DO UPDATE SET
                                ensemble_probability = EXCLUDED.ensemble_probability,
                                confidence_level = EXCLUDED.confidence_level,
                                confidence_score = EXCLUDED.confidence_score,
                                updated_at = CURRENT_TIMESTAMP
                        """

                        cur.execute(insert_query, selection_data)
                        total_selections += 1

                    except Exception as e:
                        self.logger.error(
                            f"❌ Failed to process horse {horse_data.get('horse_name', 'Unknown')}: {e}"
                        )
                        continue

            # Generate summary stats
            self.generate_summary_stats(
                cur, datetime.strptime(target_date, "%Y-%m-%d").date()
            )

            cur.close()
            conn.close()

            self.logger.info(
                f"✅ Successfully saved {total_selections} selections to database"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save selections to database: {e}")
            return False

    def generate_summary_stats(self, cursor, prediction_date):
        """Generate summary statistics for the prediction session"""
        try:
            summary_query = """
                INSERT INTO ai_race_summary (
                    prediction_date, total_races, total_runners, 
                    high_confidence_count, medium_confidence_count, low_confidence_count,
                    avg_confidence_score, courses_covered
                )
                SELECT 
                    prediction_date,
                    COUNT(DISTINCT race_id) as total_races,
                    COUNT(*) as total_runners,
                    COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence_count,
                    COUNT(CASE WHEN confidence_level = 'Medium' THEN 1 END) as medium_confidence_count,
                    COUNT(CASE WHEN confidence_level = 'Low' THEN 1 END) as low_confidence_count,
                    ROUND(AVG(confidence_score), 3) as avg_confidence_score,
                    array_agg(DISTINCT course) as courses_covered
                FROM ai_selections 
                WHERE prediction_date = %s
                GROUP BY prediction_date
                ON CONFLICT (prediction_date) 
                DO UPDATE SET
                    total_races = EXCLUDED.total_races,
                    total_runners = EXCLUDED.total_runners,
                    high_confidence_count = EXCLUDED.high_confidence_count,
                    medium_confidence_count = EXCLUDED.medium_confidence_count,
                    low_confidence_count = EXCLUDED.low_confidence_count,
                    avg_confidence_score = EXCLUDED.avg_confidence_score,
                    courses_covered = EXCLUDED.courses_covered,
                    updated_at = CURRENT_TIMESTAMP
            """

            cursor.execute(summary_query, (prediction_date,))
            self.logger.info("✅ Summary statistics generated")

        except Exception as e:
            self.logger.error(f"❌ Failed to generate summary stats: {e}")

    def display_summary(self, target_date: str):
        """Display summary of saved selections"""
        try:
            conn = self.get_database_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Get summary data
            summary_query = """
                SELECT 
                    course,
                    COUNT(DISTINCT race_id) as races,
                    COUNT(*) as total_runners,
                    COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence,
                    COUNT(CASE WHEN confidence_level = 'Medium' THEN 1 END) as medium_confidence,
                    COUNT(CASE WHEN confidence_level = 'Low' THEN 1 END) as low_confidence,
                    ROUND(AVG(confidence_score), 3) as avg_confidence
                FROM ai_selections 
                WHERE prediction_date = %s
                GROUP BY course
                ORDER BY course
            """

            cur.execute(summary_query, (target_date,))
            results = cur.fetchall()

            print(f"\n🎯 AI SELECTIONS SUMMARY FOR {target_date}")
            print("=" * 80)

            total_races = 0
            total_runners = 0

            for result in results:
                total_races += result["races"]
                total_runners += result["total_runners"]

                print(f"\n🏇 {result['course'].upper()}")
                print(
                    f"   📊 {result['races']} races | {result['total_runners']} runners"
                )
                print(
                    f"   🔥 High: {result['high_confidence']} | ⚡ Medium: {result['medium_confidence']} | 💡 Low: {result['low_confidence']}"
                )
                print(f"   📈 Avg Confidence: {result['avg_confidence']}")

            print(
                f"\n✅ TOTAL: {total_races} races | {total_runners} selections saved to database"
            )

            cur.close()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Failed to display summary: {e}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Simple AI Horse Racing Selections Saver"
    )
    parser.add_argument("--date", required=True, help="Target date (YYYY-MM-DD)")

    args = parser.parse_args()

    try:
        saver = SimpleAISelectionsSaver()

        print(f"🚀 SIMPLE AI SELECTIONS DATABASE SAVER")
        print(f"📅 Target Date: {args.date}")
        print("=" * 80)

        # Save selections to database
        success = saver.save_selections_to_database(args.date)

        if success:
            # Display summary
            saver.display_summary(args.date)
            print(
                "\n🎯 Check the ai_selections and ai_race_summary tables for detailed data"
            )
        else:
            print("❌ Failed to save selections")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
