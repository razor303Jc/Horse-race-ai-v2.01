#!/usr/bin/env python3
"""
Simple AI Selection Data Test
=============================

Test script to check database connectivity and insert simple test data
"""

import psycopg2
import logging
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connections and basic operations"""

    # Source database
    source_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="results_horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    # Target database
    target_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="advanced_racing_metrics_db",
        user="horse_racing",
        password="secure_password_123",
    )

    print("✅ Database connections successful")

    # Test source data
    cursor = source_conn.cursor()
    cursor.execute(
        """
        SELECT r.race_id, r.course, r.date, rec.name, rec.place, rec.sp
        FROM races r 
        JOIN records rec ON r.race_id = rec.race_id
        WHERE r.date >= '2025-08-20'
        LIMIT 5
    """
    )

    source_data = cursor.fetchall()
    print(f"\n📊 Source data sample ({len(source_data)} records):")
    for row in source_data:
        print(
            f"  Race {row[0]}: {row[3]} at {row[1]} - Position: {row[4]}, SP: {row[5]}"
        )

    # Check target table structure
    cursor = target_conn.cursor()
    cursor.execute(
        """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'betting_performance_tracker'
        ORDER BY ordinal_position
    """
    )

    columns = cursor.fetchall()
    print(f"\n🎯 Betting Performance Tracker columns ({len(columns)}):")
    for col in columns:
        print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]}")

    # Test simple insert
    test_insert_sql = """
    INSERT INTO betting_performance_tracker 
    (selection_date, race_id, horse_name, ai_prediction_probability, 
     confidence_level, recommended_stake, value_rating, starting_price_decimal,
     finishing_position, race_result, gross_return, net_profit_loss, roi_percentage)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(
            test_insert_sql,
            (
                date.today(),
                999999,  # Test race ID
                "Test Horse",
                0.25,
                "MEDIUM",
                10.0,
                2.5,
                4.0,
                3,
                "PLACE",
                10.0,
                0.0,
                0.0,
            ),
        )
        target_conn.commit()
        print("✅ Test insert successful")

        # Clean up test record
        cursor.execute("DELETE FROM betting_performance_tracker WHERE race_id = 999999")
        target_conn.commit()
        print("✅ Test cleanup successful")

    except Exception as e:
        print(f"❌ Test insert failed: {e}")
        target_conn.rollback()

    # Check current data counts
    cursor.execute("SELECT COUNT(*) FROM betting_performance_tracker")
    bet_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ai_predictions")
    pred_count = cursor.fetchone()[0]

    print(f"\n📈 Current data counts:")
    print(f"  Betting Performance Records: {bet_count}")
    print(f"  AI Predictions: {pred_count}")

    source_conn.close()
    target_conn.close()


if __name__ == "__main__":
    test_database_connection()
