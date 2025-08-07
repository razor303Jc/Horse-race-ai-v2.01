#!/usr/bin/env python3
"""
Test Enhanced Contextual AI Predictions Generation
=================================================

This script generates enhanced AI predictions with comprehensive contextual data
and demonstrates the contextual reward system analysis.
"""

import sqlite3
import sys
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_enhanced_ai_predictions():
    """Test the enhanced AI predictions with contextual data"""

    # Connect to database
    db_path = "massive_horse_racing.db"
    if not os.path.exists(db_path):
        logger.error(
            f"Database {db_path} not found. Please generate the basic dataset first."
        )
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if we have basic data
        cursor.execute("SELECT COUNT(*) FROM race_cards")
        race_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM race_participants")
        participant_count = cursor.fetchone()[0]

        logger.info(
            f"Found {race_count:,} races and {participant_count:,} participants"
        )

        if race_count == 0:
            logger.error("No race data found. Please generate basic dataset first.")
            return False

        # Create enhanced AI predictions table
        logger.info("Creating enhanced AI predictions table...")
        cursor.execute("DROP TABLE IF EXISTS ai_predictions")
        cursor.execute("DROP TABLE IF EXISTS ai_betting_strategies")

        cursor.execute(
            """
            CREATE TABLE ai_predictions (
                prediction_id INTEGER PRIMARY KEY,
                race_id INTEGER,
                participant_id INTEGER,
                predicted_probability REAL,
                confidence_score REAL,
                value_rating REAL,
                consensus_rating REAL,
                form_score REAL,
                pace_rating REAL,
                class_rating REAL,
                trainer_form REAL,
                jockey_form REAL,
                course_suitability REAL,
                distance_suitability REAL,
                going_suitability REAL,
                
                -- Enhanced contextual data for reward system
                day_of_week INTEGER,
                week_of_year INTEGER,
                month INTEGER,
                season TEXT,
                is_weekend INTEGER,
                is_holiday INTEGER,
                time_of_day TEXT,
                race_number_on_card INTEGER,
                total_races_on_card INTEGER,
                field_size INTEGER,
                competitive_rating REAL,
                market_volatility REAL,
                weather_impact_score REAL,
                track_bias_factor REAL,
                trainer_recent_form REAL,
                jockey_recent_form REAL,
                stable_confidence REAL,
                media_attention_score REAL,
                betting_patterns_unusual INTEGER,
                pace_scenario TEXT,
                class_drop_raise TEXT,
                distance_change_impact REAL,
                weight_change_impact REAL,
                equipment_change INTEGER,
                first_time_headgear INTEGER,
                connections_booking_significance REAL,
                stable_money_confidence REAL,
                market_support_early REAL,
                market_support_late REAL,
                steam_moves_detected INTEGER,
                drift_detected INTEGER,
                liquidity_quality_score REAL,
                
                prediction_timestamp TEXT,
                actual_result INTEGER,
                FOREIGN KEY (race_id) REFERENCES race_cards (race_id),
                FOREIGN KEY (participant_id) REFERENCES race_participants (participant_id)
            )
        """
        )

        # Generate sample contextual AI predictions
        logger.info("Generating sample contextual AI predictions...")

        # Get sample races
        cursor.execute(
            """
            SELECT rc.race_id, rc.race_date, rc.post_time, rc.race_number,
                   COUNT(rp.participant_id) as field_size
            FROM race_cards rc
            JOIN race_participants rp ON rc.race_id = rp.race_id
            GROUP BY rc.race_id
            ORDER BY RANDOM()
            LIMIT 50
        """
        )

        sample_races = cursor.fetchall()
        logger.info(f"Selected {len(sample_races)} races for prediction generation")

        import random
        from datetime import datetime

        prediction_id = 1

        for race_id, race_date, post_time, race_number, field_size in sample_races:
            # Generate contextual factors
            race_datetime = datetime.strptime(
                f"{race_date} {post_time}", "%Y-%m-%d %H:%M"
            )

            day_of_week = race_datetime.weekday()
            week_of_year = race_datetime.isocalendar()[1]
            month = race_datetime.month

            # Season mapping
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Autumn"

            is_weekend = 1 if day_of_week >= 5 else 0
            is_holiday = random.choice([0, 0, 0, 0, 1])

            hour = race_datetime.hour
            if hour < 12:
                time_of_day = "Morning"
            elif hour < 17:
                time_of_day = "Afternoon"
            else:
                time_of_day = "Evening"

            # Get participants for this race
            cursor.execute(
                """
                SELECT rp.participant_id, rp.odds_decimal, rp.actual_finish_position,
                       h.rating, h.form_rating, h.career_wins, h.career_runs,
                       j.skill_rating, t.skill_rating
                FROM race_participants rp
                JOIN horses h ON rp.horse_id = h.horse_id
                JOIN jockeys j ON rp.jockey_id = j.jockey_id
                JOIN trainers t ON rp.trainer_id = t.trainer_id
                WHERE rp.race_id = ?
            """,
                (race_id,),
            )

            participants = cursor.fetchall()

            for participant_data in participants:
                (
                    participant_id,
                    odds,
                    finish_pos,
                    horse_rating,
                    form_rating,
                    career_wins,
                    career_runs,
                    jockey_skill,
                    trainer_skill,
                ) = participant_data

                # Generate AI analysis
                implied_prob = 1 / odds
                win_rate = career_wins / max(career_runs, 1)
                form_score = (form_rating / 100) * (1 + win_rate)
                pace_rating = random.uniform(0.6, 0.95) * (horse_rating / 100)
                class_rating = min(1.0, horse_rating / 80)
                trainer_form = trainer_skill / 100
                jockey_form = jockey_skill / 100

                course_suitability = random.uniform(0.8, 1.0)
                distance_suitability = random.uniform(0.8, 1.0)
                going_suitability = random.uniform(0.8, 1.1)

                # AI predicted probability
                ai_adjustment = (
                    form_score * 0.25
                    + pace_rating * 0.2
                    + class_rating * 0.15
                    + trainer_form * 0.15
                    + jockey_form * 0.1
                    + course_suitability * 0.08
                    + distance_suitability * 0.05
                    + going_suitability * 0.02
                )

                predicted_prob = implied_prob * ai_adjustment
                predicted_prob = max(0.01, min(0.99, predicted_prob))

                confidence = min(0.95, random.uniform(0.5, 0.9))
                value_percentage = random.uniform(-5, 25)
                consensus_rating = random.uniform(50, 95)

                # Enhanced contextual data
                competitive_rating = min(field_size / 20.0, 1.0) * random.uniform(
                    0.8, 1.2
                )
                market_volatility = random.uniform(0.1, 0.9)
                weather_impact_score = random.uniform(0.0, 0.8)
                track_bias_factor = random.uniform(-0.3, 0.3)
                trainer_recent_form = random.uniform(0.3, 0.9)
                jockey_recent_form = random.uniform(0.3, 0.9)
                stable_confidence = random.uniform(0.2, 0.8)
                media_attention_score = random.uniform(0.1, 0.7)
                betting_patterns_unusual = random.choice([0, 0, 0, 1])

                pace_scenarios = [
                    "Strong Pace",
                    "Moderate Pace",
                    "Slow Pace",
                    "Unknown",
                ]
                pace_scenario = random.choice(pace_scenarios)

                class_changes = ["Class Drop", "Class Rise", "Same Class", "Maiden"]
                class_drop_raise = random.choice(class_changes)

                distance_change_impact = random.uniform(-0.3, 0.3)
                weight_change_impact = random.uniform(-0.2, 0.2)
                equipment_change = random.choice([0, 0, 0, 1])
                first_time_headgear = random.choice([0, 0, 0, 0, 1])
                connections_booking_significance = random.uniform(0.1, 0.8)
                stable_money_confidence = random.uniform(0.2, 0.8)
                market_support_early = random.uniform(0.2, 0.9)
                market_support_late = random.uniform(0.2, 0.9)
                steam_moves_detected = random.choice([0, 0, 0, 1])
                drift_detected = random.choice([0, 0, 0, 1])
                liquidity_quality_score = random.uniform(0.3, 1.0)

                # Insert comprehensive AI prediction
                cursor.execute(
                    """
                    INSERT INTO ai_predictions (
                        prediction_id, race_id, participant_id, predicted_probability,
                        confidence_score, value_rating, consensus_rating, form_score,
                        pace_rating, class_rating, trainer_form, jockey_form,
                        course_suitability, distance_suitability, going_suitability,
                        day_of_week, week_of_year, month, season, is_weekend, is_holiday,
                        time_of_day, race_number_on_card, total_races_on_card, field_size,
                        competitive_rating, market_volatility, weather_impact_score,
                        track_bias_factor, trainer_recent_form, jockey_recent_form,
                        stable_confidence, media_attention_score, betting_patterns_unusual,
                        pace_scenario, class_drop_raise, distance_change_impact,
                        weight_change_impact, equipment_change, first_time_headgear,
                        connections_booking_significance, stable_money_confidence,
                        market_support_early, market_support_late, steam_moves_detected,
                        drift_detected, liquidity_quality_score, prediction_timestamp,
                        actual_result
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        prediction_id,
                        race_id,
                        participant_id,
                        round(predicted_prob, 4),
                        round(confidence, 2),
                        round(value_percentage, 1),
                        round(consensus_rating, 1),
                        round(form_score, 3),
                        round(pace_rating, 3),
                        round(class_rating, 3),
                        round(trainer_form, 3),
                        round(jockey_form, 3),
                        round(course_suitability, 3),
                        round(distance_suitability, 3),
                        round(going_suitability, 3),
                        day_of_week,
                        week_of_year,
                        month,
                        season,
                        is_weekend,
                        is_holiday,
                        time_of_day,
                        race_number,
                        12,
                        field_size,
                        round(competitive_rating, 3),
                        round(market_volatility, 3),
                        round(weather_impact_score, 3),
                        round(track_bias_factor, 3),
                        round(trainer_recent_form, 3),
                        round(jockey_recent_form, 3),
                        round(stable_confidence, 3),
                        round(media_attention_score, 3),
                        betting_patterns_unusual,
                        pace_scenario,
                        class_drop_raise,
                        round(distance_change_impact, 3),
                        round(weight_change_impact, 3),
                        equipment_change,
                        first_time_headgear,
                        round(connections_booking_significance, 3),
                        round(stable_money_confidence, 3),
                        round(market_support_early, 3),
                        round(market_support_late, 3),
                        steam_moves_detected,
                        drift_detected,
                        round(liquidity_quality_score, 3),
                        "2024-01-01 10:00:00",
                        1 if finish_pos == 1 else 0,
                    ),
                )

                prediction_id += 1

        conn.commit()
        logger.info(
            f"Generated {prediction_id - 1} enhanced AI predictions with contextual data"
        )

        # Verify data
        cursor.execute("SELECT COUNT(*) FROM ai_predictions")
        total_predictions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT season) FROM ai_predictions")
        seasons = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT pace_scenario) FROM ai_predictions")
        pace_scenarios = cursor.fetchone()[0]

        logger.info(
            f"✅ Verification: {total_predictions:,} predictions, {seasons} seasons, {pace_scenarios} pace scenarios"
        )

        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error generating enhanced AI predictions: {e}")
        return False


def main():
    """Main execution function"""
    print("🚀 ENHANCED CONTEXTUAL AI PREDICTIONS GENERATOR")
    print("=" * 60)

    if test_enhanced_ai_predictions():
        print("\n✅ Enhanced AI predictions generated successfully!")
        print("\nNow running contextual reward analysis...")

        # Import and run the contextual analysis
        try:
            from contextual_ai_reward_demo import ContextualAIRewardAnalyzer

            analyzer = ContextualAIRewardAnalyzer()
            analyzer.print_comprehensive_analysis()
        except Exception as e:
            logger.error(f"Error running contextual analysis: {e}")
    else:
        print("\n❌ Failed to generate enhanced AI predictions")


if __name__ == "__main__":
    main()
