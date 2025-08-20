#!/usr/bin/env python3
"""Debug single prediction storage to find the exact issue."""

import pandas as pd
import sys
import os

sys.path.append("/home/jc/Documents/Horse-race-ai-v2.03")

from tools.ml_training.ai_selections_generator import AISelectionsGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def debug_single_prediction():
    """Debug the first prediction that fails."""
    generator = AISelectionsGenerator()

    # Get race data
    print("Loading race data...")
    race_data = generator.get_todays_races()
    print(f"Found {len(race_data)} races")

    if len(race_data) == 0:
        print("No race data found!")
        return

    # Get first race
    first_race = race_data.iloc[0]
    print(f"\nFirst race: {first_race['horse_name']} at {first_race['race_time']}")
    print(f"Race time type: {type(first_race['race_time'])}")
    print(f"Race time value: {first_race['race_time']}")

    if hasattr(first_race["race_time"], "time"):
        race_time_value = first_race["race_time"].time()
        print(f"Extracted time: {race_time_value} (type: {type(race_time_value)})")

    # Try to create a minimal prediction record
    print("\nCreating minimal prediction...")
    prediction_data = {
        "session_id": 1,
        "race_date": first_race["race_date"],
        "course": first_race["course"],
        "race_time": (
            first_race["race_time"].time()
            if hasattr(first_race["race_time"], "time")
            else first_race["race_time"]
        ),
        "horse_name": first_race["horse_name"],
        "jockey": first_race["jockey"],
        "trainer": first_race["trainer"],
        "lr_win_prob": 0.5,
        "rf_win_prob": 0.5,
        "lr_place_prob": 0.7,
        "rf_place_prob": 0.7,
        "ensemble_win_prob": 0.5,
        "ensemble_place_prob": 0.7,
        "confidence_score": 0.8,
        "predicted_odds": 2.0,
        "current_odds": 0.1,
        "value_bet": True,
    }

    print("Prediction data:")
    for key, value in prediction_data.items():
        print(f"  {key}: {value} ({type(value)})")

    # Try to store this single prediction
    print("\nAttempting to store single prediction...")
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )

        cursor = conn.cursor()

        # Insert query
        insert_query = """
        INSERT INTO ai_predictions (
            session_id, race_date, course, race_time, horse_name, jockey, trainer,
            lr_win_prob, rf_win_prob, lr_place_prob, rf_place_prob,
            ensemble_win_prob, ensemble_place_prob, confidence_score,
            predicted_odds, current_odds, value_bet
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        values = (
            prediction_data["session_id"],
            prediction_data["race_date"],
            prediction_data["course"],
            prediction_data["race_time"],
            prediction_data["horse_name"],
            prediction_data["jockey"],
            prediction_data["trainer"],
            prediction_data["lr_win_prob"],
            prediction_data["rf_win_prob"],
            prediction_data["lr_place_prob"],
            prediction_data["rf_place_prob"],
            prediction_data["ensemble_win_prob"],
            prediction_data["ensemble_place_prob"],
            prediction_data["confidence_score"],
            prediction_data["predicted_odds"],
            prediction_data["current_odds"],
            prediction_data["value_bet"],
        )

        print(f"Values: {values}")
        cursor.execute(insert_query, values)
        conn.commit()
        print("✅ Single prediction stored successfully!")

    except Exception as e:
        print(f"❌ Error storing single prediction: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    debug_single_prediction()
