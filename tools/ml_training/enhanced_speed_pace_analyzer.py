#!/usr/bin/env python3
"""
Enhanced Speed & Pace Analysis Calculator with Database Integration
=================================================================

Advanced speed and pace analysis system that calculates comprehensive
speed metrics and saves them to the advanced_racing_metrics_db database.

Created: August 24, 2025
"""

import os
import sys
import logging
import uuid
import json
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


class EnhancedSpeedPaceAnalyzer:
    """Enhanced speed and pace analyzer with database integration"""

    def __init__(self):
        """Initialize the analyzer"""
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

    def calculate_speed_rating(self, horse_data: Dict, race_data: Dict) -> float:
        """Calculate speed rating based on various factors"""
        # Base speed rating from market assessment
        odds = horse_data.get("odds_decimal", 6.0)

        # Convert to float safely
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None or odds <= 0:
            odds = 6.0

        # Market-based speed assessment (0-120 scale)
        # Better odds = higher speed expectation
        if odds <= 1.5:
            base_speed = 110.0  # Exceptional speed expectation
        elif odds <= 2.5:
            base_speed = 100.0  # High speed expectation
        elif odds <= 4.0:
            base_speed = 90.0  # Good speed expectation
        elif odds <= 8.0:
            base_speed = 80.0  # Average speed expectation
        elif odds <= 15.0:
            base_speed = 70.0  # Below average speed
        else:
            base_speed = 60.0  # Poor speed expectation

        # Age adjustment for speed
        age = horse_data.get("age", 4)
        if age == 3:
            age_factor = 0.95  # Young horses developing speed
        elif age in [4, 5]:
            age_factor = 1.0  # Peak speed age
        elif age in [6, 7]:
            age_factor = 0.98  # Experienced but slightly slower
        else:
            age_factor = 0.92  # Aging affecting speed

        # Weight factor (lighter = potentially faster)
        weight = horse_data.get("weight", 140)
        if isinstance(weight, (str, type(None))):
            weight = 140

        if weight < 130:
            weight_factor = 1.05
        elif weight < 140:
            weight_factor = 1.02
        elif weight < 150:
            weight_factor = 1.0
        else:
            weight_factor = 0.97

        final_speed = base_speed * age_factor * weight_factor

        return min(120.0, max(40.0, final_speed))

    def calculate_pace_rating(self, horse_data: Dict, race_data: Dict) -> float:
        """Calculate pace rating and style"""
        # Pace rating based on horse characteristics
        odds = horse_data.get("odds_decimal", 6.0)

        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None or odds <= 0:
            odds = 6.0

        # Base pace rating (0-120 scale)
        if odds <= 2.0:
            base_pace = 95.0  # Excellent pace management
        elif odds <= 4.0:
            base_pace = 85.0  # Good pace ability
        elif odds <= 8.0:
            base_pace = 75.0  # Average pace handling
        elif odds <= 15.0:
            base_pace = 65.0  # Below average pace
        else:
            base_pace = 55.0  # Poor pace management

        # Distance factor affects pace requirements
        # This would be enhanced with actual distance data
        distance_factor = 1.0  # Placeholder - would vary by distance

        return min(120.0, max(30.0, base_pace * distance_factor))

    def determine_pace_style(self, horse_data: Dict, race_data: Dict) -> str:
        """Determine the horse's preferred pace style"""
        # Simplified pace style determination
        # In a real system, this would analyze historical running patterns

        odds = horse_data.get("odds_decimal", 6.0)
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None or odds <= 0:
            odds = 6.0

        age = horse_data.get("age", 4)

        # Very simplified pace style logic
        if odds <= 3.0 and age >= 5:
            return "front_runner"  # Experienced favorites often lead
        elif odds <= 6.0:
            return "mid_pack"  # Solid contenders often track
        else:
            return "closer"  # Longshots often need to close

    def calculate_sectional_ratings(self, horse_data: Dict) -> Dict[str, float]:
        """Calculate early, middle, and late pace ratings"""
        pace_style = self.determine_pace_style(horse_data, {})
        base_rating = 75.0

        if pace_style == "front_runner":
            return {
                "early_pace_rating": base_rating + 15.0,
                "middle_pace_rating": base_rating + 5.0,
                "late_pace_rating": base_rating - 10.0,
            }
        elif pace_style == "mid_pack":
            return {
                "early_pace_rating": base_rating,
                "middle_pace_rating": base_rating + 10.0,
                "late_pace_rating": base_rating + 5.0,
            }
        else:  # closer
            return {
                "early_pace_rating": base_rating - 15.0,
                "middle_pace_rating": base_rating - 5.0,
                "late_pace_rating": base_rating + 20.0,
            }

    def calculate_pace_versatility(self, horse_data: Dict) -> float:
        """Calculate pace versatility score"""
        # Higher rated horses tend to be more versatile
        odds = horse_data.get("odds_decimal", 6.0)
        if isinstance(odds, Decimal):
            odds = float(odds)
        elif odds is None or odds <= 0:
            odds = 6.0

        # Versatility decreases with higher odds
        versatility = max(0.3, min(1.0, 1.2 - (odds / 10.0)))
        return versatility

    def calculate_finishing_speed_index(self, horse_data: Dict) -> float:
        """Calculate finishing speed index"""
        pace_style = self.determine_pace_style(horse_data, {})
        base_index = 75.0

        if pace_style == "closer":
            return base_index + 20.0  # Closers have better finishing speed
        elif pace_style == "mid_pack":
            return base_index + 10.0  # Mid-pack can finish well
        else:
            return base_index - 5.0  # Front runners may tire

    def calculate_track_bias_factor(self, race_data: Dict) -> float:
        """Calculate track bias factor (placeholder)"""
        # In a real system, this would analyze recent results for bias
        return 0.0  # Neutral bias assumed

    def calculate_going_suitability(self, horse_data: Dict, race_data: Dict) -> float:
        """Calculate going condition suitability"""
        # Simplified going suitability - would use historical data
        # Assume good going suits most horses
        return 0.85

    def calculate_speed_pace_analysis(self, horse_data: Dict, race_data: Dict) -> Dict:
        """Calculate comprehensive speed and pace analysis for a horse"""

        # Calculate main ratings
        speed_rating = self.calculate_speed_rating(horse_data, race_data)
        pace_rating = self.calculate_pace_rating(horse_data, race_data)
        finishing_speed_index = self.calculate_finishing_speed_index(horse_data)

        # Determine pace style
        pace_style = self.determine_pace_style(horse_data, race_data)

        # Calculate sectional ratings
        sectionals = self.calculate_sectional_ratings(horse_data)

        # Calculate additional metrics
        pace_versatility = self.calculate_pace_versatility(horse_data)
        track_bias = self.calculate_track_bias_factor(race_data)
        going_suitability = self.calculate_going_suitability(horse_data, race_data)

        # Create sectional times JSON (placeholder data)
        sectional_times = {
            "furlong_1": None,
            "furlong_2": None,
            "furlong_3": None,
            "furlong_4": None,
            "final_furlong": None,
            "note": "Sectional data not available - using estimated values",
        }

        return {
            "horse_id": horse_data.get("horse_id", 0),
            "horse_name": horse_data.get("horse_name", ""),
            "race_id": race_data.get("race_id"),
            "speed_rating": speed_rating,
            "pace_rating": pace_rating,
            "finishing_speed_index": finishing_speed_index,
            "pace_style": pace_style,
            "early_pace_rating": sectionals["early_pace_rating"],
            "middle_pace_rating": sectionals["middle_pace_rating"],
            "late_pace_rating": sectionals["late_pace_rating"],
            "sectional_times": json.dumps(sectional_times),
            "pace_versatility_score": pace_versatility,
            "track_bias_factor": track_bias,
            "going_suitability": going_suitability,
        }

    def save_speed_pace_analysis(self, analysis_data: Dict) -> bool:
        """Save speed and pace analysis to database"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            insert_sql = """
                INSERT INTO horse_speed_pace_ratings (
                    horse_id, horse_name, race_id, calculation_date,
                    speed_rating, pace_rating, finishing_speed_index,
                    pace_style, early_pace_rating, middle_pace_rating,
                    late_pace_rating, sectional_times, pace_versatility_score,
                    track_bias_factor, going_suitability
                ) VALUES (
                    %(horse_id)s, %(horse_name)s, %(race_id)s, CURRENT_DATE,
                    %(speed_rating)s, %(pace_rating)s, %(finishing_speed_index)s,
                    %(pace_style)s, %(early_pace_rating)s, %(middle_pace_rating)s,
                    %(late_pace_rating)s, %(sectional_times)s, %(pace_versatility_score)s,
                    %(track_bias_factor)s, %(going_suitability)s
                )
            """

            cursor.execute(insert_sql, analysis_data)
            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save speed/pace analysis: {e}")
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
        """Process all races for today and calculate speed/pace analysis"""
        self.logger.info(
            f"⚡ Starting speed/pace analysis for {target_date or 'today'}"
        )

        races = self.get_todays_race_data(target_date)

        if not races:
            self.logger.warning("⚠️ No race data found")
            return {"success": False, "message": "No race data found"}

        total_analyses = 0
        successful_saves = 0

        for race in races:
            self.logger.info(
                f"🏁 Processing race {race['race_id']} at {race['course']}"
            )

            for horse in race["horses"]:
                try:
                    # Calculate speed/pace analysis
                    analysis = self.calculate_speed_pace_analysis(horse, race)

                    # Save to database
                    if self.save_speed_pace_analysis(analysis):
                        successful_saves += 1
                        self.logger.info(
                            f"✅ Saved analysis for {horse['horse_name']}: "
                            f"Speed {analysis['speed_rating']:.1f}, "
                            f"Pace {analysis['pace_rating']:.1f}, "
                            f"Style: {analysis['pace_style']}"
                        )
                    else:
                        self.logger.error(
                            f"❌ Failed to save analysis for {horse['horse_name']}"
                        )

                    total_analyses += 1

                except Exception as e:
                    self.logger.error(
                        f"❌ Error processing {horse.get('horse_name', 'Unknown')}: {e}"
                    )

        success_rate = (
            (successful_saves / total_analyses * 100) if total_analyses > 0 else 0
        )

        result = {
            "success": True,
            "total_horses": total_analyses,
            "successful_saves": successful_saves,
            "success_rate": success_rate,
            "races_processed": len(races),
        }

        self.logger.info(f"🎯 Speed/pace analysis complete:")
        self.logger.info(f"   📊 Total horses: {total_analyses}")
        self.logger.info(f"   ✅ Successful saves: {successful_saves}")
        self.logger.info(f"   📈 Success rate: {success_rate:.1f}%")
        self.logger.info(f"   🏁 Races processed: {len(races)}")

        return result

    def get_speed_pace_summary(self, race_id: int = None) -> List[Dict]:
        """Get speed and pace analysis summary"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            if race_id:
                query = """
                    SELECT horse_name, speed_rating, pace_rating, pace_style,
                           finishing_speed_index, early_pace_rating, middle_pace_rating,
                           late_pace_rating, pace_versatility_score, created_at
                    FROM horse_speed_pace_ratings
                    WHERE race_id = %s
                    ORDER BY speed_rating DESC
                """
                cursor.execute(query, (race_id,))
            else:
                query = """
                    SELECT horse_name, speed_rating, pace_rating, pace_style,
                           finishing_speed_index, early_pace_rating, middle_pace_rating,
                           late_pace_rating, pace_versatility_score, race_id, created_at
                    FROM horse_speed_pace_ratings
                    WHERE calculation_date = CURRENT_DATE
                    ORDER BY speed_rating DESC
                    LIMIT 20
                """
                cursor.execute(query)

            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"❌ Failed to get speed/pace summary: {e}")
            return []


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Speed & Pace Analyzer")
    parser.add_argument(
        "--date",
        type=str,
        help="Target date (YYYY-MM-DD)",
        default=date.today().strftime("%Y-%m-%d"),
    )
    parser.add_argument("--race-id", type=int, help="Specific race ID to analyze")
    parser.add_argument(
        "--summary", action="store_true", help="Show speed/pace summary"
    )

    args = parser.parse_args()

    analyzer = EnhancedSpeedPaceAnalyzer()

    if args.summary:
        print("\\n⚡ SPEED & PACE ANALYSIS SUMMARY")
        print("=" * 50)
        analyses = analyzer.get_speed_pace_summary(args.race_id)

        for i, analysis in enumerate(analyses, 1):
            print(f"{i}. {analysis['horse_name']}")
            print(f"   ⚡ Speed Rating: {analysis['speed_rating']:.1f}")
            print(f"   🏃 Pace Rating: {analysis['pace_rating']:.1f}")
            print(f"   🎯 Pace Style: {analysis['pace_style']}")
            print(f"   🏃‍♂️ Finishing Speed: {analysis['finishing_speed_index']:.1f}")
            print(
                f"   📊 Early/Mid/Late: {analysis['early_pace_rating']:.1f}/"
                f"{analysis['middle_pace_rating']:.1f}/{analysis['late_pace_rating']:.1f}"
            )
            print(f"   🔄 Versatility: {analysis['pace_versatility_score']:.2f}")
            if args.race_id is None:
                print(f"   🏁 Race ID: {analysis['race_id']}")
            print()
    else:
        result = analyzer.process_todays_races(args.date)

        if result["success"]:
            print("\\n✅ SPEED & PACE ANALYSIS COMPLETE!")
            print(f"📊 Processed {result['total_horses']} horses")
            print(f"✅ Saved {result['successful_saves']} analyses")
            print(f"📈 Success rate: {result['success_rate']:.1f}%")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()
