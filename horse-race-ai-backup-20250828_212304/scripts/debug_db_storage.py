#!/usr/bin/env python3
"""
Debug Database Storage for AI Predictions
Quick test to identify why predictions aren't being stored
"""

import psycopg2
import pandas as pd
from datetime import datetime


def test_single_prediction():
    """Test storing a single prediction to identify the issue"""

    db_config = {
        "host": "localhost",
        "port": 5434,
        "database": "horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    try:
        with psycopg2.connect(**db_config) as connection:
            cursor = connection.cursor()

            # Test simple insert with minimal data
            test_query = """
                INSERT INTO ai_predictions (
                    race_id, horse_name, ensemble_probability
                ) VALUES (
                    %s, %s, %s
                ) RETURNING id
            """

            # Try simple test data
            cursor.execute(
                test_query,
                (
                    12345,  # race_id
                    "Test Horse",  # horse_name
                    0.85,  # ensemble_probability
                ),
            )

            result = cursor.fetchone()
            connection.commit()
            print(f"✅ Successfully stored test prediction with ID: {result[0]}")

            # Try more complex insert
            full_query = """
                INSERT INTO ai_predictions (
                    race_id, horse_name, jockey, trainer, course, race_number,
                    ensemble_probability, confidence_level, confidence_score,
                    odds_decimal, model_version, feature_count
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """

            cursor.execute(
                full_query,
                (
                    12346,  # race_id
                    "Test Horse 2",  # horse_name
                    "Test Jockey",  # jockey
                    "Test Trainer",  # trainer
                    "Test Course",  # course
                    1,  # race_number
                    0.75,  # ensemble_probability
                    "High",  # confidence_level
                    0.8,  # confidence_score
                    2.5,  # odds_decimal
                    "v2.03",  # model_version
                    17,  # feature_count
                ),
            )

            result2 = cursor.fetchone()
            connection.commit()
            print(f"✅ Successfully stored full test prediction with ID: {result2[0]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")


def check_data_sample():
    """Check what's in the actual data that might be causing issues"""

    # Load a sample of the actual prediction data to see what might be problematic
    print("\n🔍 Checking prediction data types...")

    # Import the AI generator to get sample data
    import sys
    import os

    sys.path.append("/home/jc/Documents/Horse-race-ai-v2.03/tools/ml_training")

    from ai_selections_generator import AISelectionsGenerator

    try:
        generator = AISelectionsGenerator()
        races_df = generator.get_todays_races()

        if len(races_df) > 0:
            # Check first row data types
            sample = races_df.iloc[0]
            print(
                f"Sample race_id: {sample['race_id']} (type: {type(sample['race_id'])})"
            )
            print(
                f"Sample horse_name: {sample['horse_name']} (type: {type(sample['horse_name'])})"
            )
            print(f"Sample course: {sample['course']} (type: {type(sample['course'])})")
            print(
                f"Sample race_number: {sample['race_number']} (type: {type(sample['race_number'])})"
            )

            # Check for null values that might cause issues
            print(f"\n🔍 Null value check:")
            print(f"race_id nulls: {races_df['race_id'].isnull().sum()}")
            print(f"horse_name nulls: {races_df['horse_name'].isnull().sum()}")
            print(f"course nulls: {races_df['course'].isnull().sum()}")
            print(f"race_number nulls: {races_df['race_number'].isnull().sum()}")

        else:
            print("❌ No race data available")

    except Exception as e:
        print(f"❌ Error loading race data: {e}")


if __name__ == "__main__":
    print("🧪 Testing AI Predictions Database Storage")
    print("=" * 50)

    test_single_prediction()
    check_data_sample()
