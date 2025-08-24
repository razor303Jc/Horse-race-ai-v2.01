#!/usr/bin/env python3
"""
Enhanced Power Rating Calculator with Database Integration
=========================================================

Advanced power rating system that calculates comprehensive ratings
and saves them to the advanced_racing_metrics_db database.

Created: August 24, 2025
"""

import os
import sys
import logging
import uuid
import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

# Add the project root to the path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)


class EnhancedPowerRatingCalculator:
    """Enhanced power rating calculator with database integration"""

    def __init__(self):
        """Initialize the calculator"""
        self.setup_logging()
        self.db_config = {
            "host": "postgres",
            "database": "advanced_racing_metrics_db",
            "user": "horse_racing",
            "password": "secure_password_123",
            "port": 5432,
        }
        self.cards_db_config = {
            "host": "postgres",
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

    def get_database_connection(self, use_cards_db=False):
        """Get database connection"""
        try:
            config = self.cards_db_config if use_cards_db else self.db_config
            conn = psycopg2.connect(**config)
            conn.autocommit = True
            return conn
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise

    def calculate_base_power_rating(self, horse_data: Dict) -> float:
        """Calculate base power rating from horse characteristics"""
        # Base rating starts at 75 (average)
        base_rating = 75.0

        # Age factor (peak at 4-5 years)
        age = horse_data.get("age", 4)
        if age == 3:
            age_factor = 0.95  # Young horse potential
        elif age in [4, 5]:
            age_factor = 1.0  # Peak age
        elif age in [6, 7]:
            age_factor = 0.98  # Experienced
        else:
            age_factor = 0.92  # Declining

        # Weight factor (lighter is generally better for handicaps)
        weight = horse_data.get("weight", 140)
        if weight < 130:
            weight_factor = 1.05  # Very light weight advantage
        elif weight < 140:
            weight_factor = 1.02  # Light weight advantage
        elif weight < 150:
            weight_factor = 1.0  # Average weight
        else:
            weight_factor = 0.97  # Heavy weight disadvantage

        # Apply factors
        base_rating = base_rating * age_factor * weight_factor

        return base_rating

    def calculate_speed_component(self, horse_data: Dict) -> float:
        """Calculate speed component of power rating"""
        # This would integrate with historical speed figures if available
        # For now, use odds as proxy for market assessment
        odds = horse_data.get("odds_decimal", 6.0)

        # Convert to float safely
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None:
            odds = 6.0

        # Convert odds to probability and then to speed rating
        implied_prob = 1.0 / odds if odds > 0 else 0.1

        # Scale to 0-30 speed component
        speed_component = min(30.0, implied_prob * 120)

        return speed_component

    def calculate_form_component(self, horse_data: Dict) -> float:
        """Calculate form component based on recent performances"""
        # This would analyze last 3-5 runs if data available
        # For now, use a simplified version based on market position

        odds = horse_data.get("odds_decimal", 6.0)

        # Convert to float safely
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None:
            odds = 6.0

        # Form component based on market confidence
        if odds <= 2.0:
            form_component = 25.0  # Excellent recent form
        elif odds <= 4.0:
            form_component = 20.0  # Good form
        elif odds <= 8.0:
            form_component = 15.0  # Average form
        elif odds <= 15.0:
            form_component = 10.0  # Poor form
        else:
            form_component = 5.0  # Very poor form

        return form_component

    def calculate_class_component(self, race_data: Dict) -> float:
        """Calculate class component based on race quality"""
        # This would analyze the quality of the race
        # For now, use a base class rating

        # Assume most races are similar class for this demo
        class_component = 15.0

        return class_component

    def calculate_consistency_component(self, horse_data: Dict) -> float:
        """Calculate consistency component"""
        # This would analyze variance in recent performances
        # For now, use odds as consistency indicator

        odds = horse_data.get("odds_decimal", 6.0)

        # Convert to float safely
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None:
            odds = 6.0

        # More consistent horses tend to have more stable odds
        if odds <= 3.0:
            consistency = 10.0  # Very consistent
        elif odds <= 6.0:
            consistency = 8.0  # Fairly consistent
        elif odds <= 12.0:
            consistency = 6.0  # Somewhat consistent
        else:
            consistency = 4.0  # Inconsistent

        return consistency

    def calculate_adjustments(
        self, horse_data: Dict, race_data: Dict
    ) -> Dict[str, float]:
        """Calculate various adjustments to base rating"""
        adjustments = {}

        # Age adjustment
        age = horse_data.get("age", 4)
        if age == 3:
            adjustments["age_adjustment"] = 2.0  # Young horse bonus
        elif age > 7:
            adjustments["age_adjustment"] = -3.0  # Aging penalty
        else:
            adjustments["age_adjustment"] = 0.0

        # Weight adjustment
        weight = horse_data.get("weight", 140)
        if weight < 130:
            adjustments["weight_adjustment"] = 3.0
        elif weight > 150:
            adjustments["weight_adjustment"] = -2.0
        else:
            adjustments["weight_adjustment"] = 0.0

        # Track condition adjustment (placeholder)
        adjustments["track_condition_adjustment"] = 0.0

        # Distance adjustment (placeholder)
        adjustments["distance_adjustment"] = 0.0

        return adjustments

    def calculate_power_rating(self, horse_data: Dict, race_data: Dict) -> Dict:
        """Calculate comprehensive power rating for a horse"""

        # Calculate base components
        base_rating = self.calculate_base_power_rating(horse_data)
        speed_component = self.calculate_speed_component(horse_data)
        form_component = self.calculate_form_component(horse_data)
        class_component = self.calculate_class_component(race_data)
        consistency_component = self.calculate_consistency_component(horse_data)

        # Calculate adjustments
        adjustments = self.calculate_adjustments(horse_data, race_data)

        # Calculate final rating
        final_rating = (
            base_rating
            + speed_component
            + form_component
            + class_component
            + consistency_component
            + sum(adjustments.values())
        )

        # Calculate confidence based on data quality
        odds_for_conf = horse_data.get("odds_decimal", 6.0)
        if isinstance(odds_for_conf, Decimal):
            odds_for_conf = float(odds_for_conf)
        elif odds_for_conf is None:
            odds_for_conf = 6.0

        confidence = min(1.0, max(0.3, 0.8 + (1.0 / odds_for_conf) * 0.2))

        return {
            "horse_id": horse_data.get("horse_id", 0),
            "horse_name": horse_data.get("horse_name", ""),
            "jockey_id": horse_data.get("jockey_id", 0),
            "jockey_name": horse_data.get("jockey", ""),
            "trainer_id": horse_data.get("trainer_id", 0),
            "trainer_name": horse_data.get("trainer", ""),
            "race_id": race_data.get("race_id"),
            "base_power_rating": base_rating,
            "speed_component": speed_component,
            "form_component": form_component,
            "class_component": class_component,
            "consistency_component": consistency_component,
            "age_adjustment": adjustments["age_adjustment"],
            "weight_adjustment": adjustments["weight_adjustment"],
            "track_condition_adjustment": adjustments["track_condition_adjustment"],
            "distance_adjustment": adjustments["distance_adjustment"],
            "final_power_rating": final_rating,
            "rating_confidence": confidence,
        }

    def save_power_rating(self, rating_data: Dict) -> bool:
        """Save power rating to database"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            insert_sql = """
                INSERT INTO horse_power_ratings (
                    horse_id, horse_name, jockey_id, jockey_name,
                    trainer_id, trainer_name, race_id, calculation_date,
                    base_power_rating, speed_component, form_component,
                    class_component, consistency_component, age_adjustment,
                    weight_adjustment, track_condition_adjustment, distance_adjustment,
                    final_power_rating, rating_confidence
                ) VALUES (
                    %(horse_id)s, %(horse_name)s, %(jockey_id)s, %(jockey_name)s,
                    %(trainer_id)s, %(trainer_name)s, %(race_id)s, CURRENT_DATE,
                    %(base_power_rating)s, %(speed_component)s, %(form_component)s,
                    %(class_component)s, %(consistency_component)s, %(age_adjustment)s,
                    %(weight_adjustment)s, %(track_condition_adjustment)s, %(distance_adjustment)s,
                    %(final_power_rating)s, %(rating_confidence)s
                )
            """

            cursor.execute(insert_sql, rating_data)
            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save power rating: {e}")
            return False

    def get_todays_race_data(self, target_date: str = None) -> List[Dict]:
        """Get today's race data from cards database"""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")

        try:
            conn = self.get_database_connection(use_cards_db=True)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Get races for the date
            race_query = """
                SELECT race_id, course, race_time
                FROM races 
                WHERE date = %s
                ORDER BY race_time
            """

            cursor.execute(race_query, (target_date,))
            races = cursor.fetchall()

            all_race_data = []

            for race in races:
                # Get horses in this race
                horse_query = """
                    SELECT 
                        rd.horse_id,
                        rd.name as horse_name,
                        rd.jockey_id,
                        rd.jockey,
                        rd.trainer_id,
                        rd.trainer,
                        rd.age,
                        rd.weight,
                        rd.odds_decimal,
                        rd.odds
                    FROM racecard_details rd
                    WHERE rd.race_id = %s
                    ORDER BY rd.odds_decimal ASC
                """

                cursor.execute(horse_query, (race["race_id"],))
                horses = cursor.fetchall()

                race_data = {
                    "race_id": race["race_id"],
                    "course": race["course"],
                    "race_time": race["race_time"],
                    "horses": [dict(horse) for horse in horses],
                }

                all_race_data.append(race_data)

            conn.close()
            return all_race_data

        except Exception as e:
            self.logger.error(f"❌ Failed to get race data: {e}")
            return []

    def process_todays_races(self, target_date: str = None) -> Dict:
        """Process all races for today and calculate power ratings"""
        self.logger.info(
            f"🔥 Starting power rating calculations for {target_date or 'today'}"
        )

        races = self.get_todays_race_data(target_date)

        if not races:
            self.logger.warning("⚠️ No race data found")
            return {"success": False, "message": "No race data found"}

        total_ratings = 0
        successful_saves = 0

        for race in races:
            self.logger.info(
                f"🏁 Processing race {race['race_id']} at {race['course']}"
            )

            for horse in race["horses"]:
                try:
                    # Calculate power rating
                    rating = self.calculate_power_rating(horse, race)

                    # Save to database
                    if self.save_power_rating(rating):
                        successful_saves += 1
                        self.logger.info(
                            f"✅ Saved rating for {horse['horse_name']}: {rating['final_power_rating']:.1f}"
                        )
                    else:
                        self.logger.error(
                            f"❌ Failed to save rating for {horse['horse_name']}"
                        )

                    total_ratings += 1

                except Exception as e:
                    self.logger.error(
                        f"❌ Error processing {horse.get('horse_name', 'Unknown')}: {e}"
                    )

        success_rate = (
            (successful_saves / total_ratings * 100) if total_ratings > 0 else 0
        )

        result = {
            "success": True,
            "total_horses": total_ratings,
            "successful_saves": successful_saves,
            "success_rate": success_rate,
            "races_processed": len(races),
        }

        self.logger.info(f"🎯 Power rating calculation complete:")
        self.logger.info(f"   📊 Total horses: {total_ratings}")
        self.logger.info(f"   ✅ Successful saves: {successful_saves}")
        self.logger.info(f"   📈 Success rate: {success_rate:.1f}%")
        self.logger.info(f"   🏁 Races processed: {len(races)}")

        return result

    def get_power_rating_summary(self, race_id: int = None) -> List[Dict]:
        """Get power rating summary for a race or all recent ratings"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            if race_id:
                query = """
                    SELECT horse_name, final_power_rating, rating_confidence,
                           speed_component, form_component, class_component,
                           consistency_component, created_at
                    FROM horse_power_ratings
                    WHERE race_id = %s
                    ORDER BY final_power_rating DESC
                """
                cursor.execute(query, (race_id,))
            else:
                query = """
                    SELECT horse_name, final_power_rating, rating_confidence,
                           speed_component, form_component, class_component,
                           consistency_component, race_id, created_at
                    FROM horse_power_ratings
                    WHERE calculation_date = CURRENT_DATE
                    ORDER BY final_power_rating DESC
                    LIMIT 20
                """
                cursor.execute(query)

            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"❌ Failed to get power rating summary: {e}")
            return []


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Power Rating Calculator")
    parser.add_argument(
        "--date",
        type=str,
        help="Target date (YYYY-MM-DD)",
        default=date.today().strftime("%Y-%m-%d"),
    )
    parser.add_argument("--race-id", type=int, help="Specific race ID to analyze")
    parser.add_argument(
        "--summary", action="store_true", help="Show power rating summary"
    )

    args = parser.parse_args()

    calculator = EnhancedPowerRatingCalculator()

    if args.summary:
        print("\\n🔥 POWER RATING SUMMARY")
        print("=" * 50)
        ratings = calculator.get_power_rating_summary(args.race_id)

        for i, rating in enumerate(ratings, 1):
            print(f"{i}. {rating['horse_name']}")
            print(f"   🔥 Power Rating: {rating['final_power_rating']:.1f}")
            print(f"   💎 Confidence: {rating['rating_confidence']:.2f}")
            print(f"   ⚡ Speed: {rating['speed_component']:.1f}")
            print(f"   📈 Form: {rating['form_component']:.1f}")
            print(f"   🏆 Class: {rating['class_component']:.1f}")
            print(f"   🎯 Consistency: {rating['consistency_component']:.1f}")
            if args.race_id is None:
                print(f"   🏁 Race ID: {rating['race_id']}")
            print()
    else:
        result = calculator.process_todays_races(args.date)

        if result["success"]:
            print("\\n✅ POWER RATING CALCULATION COMPLETE!")
            print(f"📊 Processed {result['total_horses']} horses")
            print(f"✅ Saved {result['successful_saves']} ratings")
            print(f"📈 Success rate: {result['success_rate']:.1f}%")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()
