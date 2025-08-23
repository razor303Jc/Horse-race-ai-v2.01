#!/usr/bin/env python3
"""
Minimal test of the real card AI selections query
"""

import psycopg2
import pandas as pd
import os

print("Testing real card AI selections query...")


def test_query():
    conn = psycopg2.connect(
        host="postgres",
        database="results_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )

    # Test the records query first
    print("Testing basic records query...")
    query = """
    SELECT 
        rec.race_id,
        rec.horse_name,
        rec.jockey,
        rec.trainer,
        rec.position,
        rec.horse_id,
        rec.jockey_id,
        rec.trainer_id,
        CAST(rec.starting_price AS FLOAT) as odds_decimal
    FROM records rec
    WHERE rec.position IS NOT NULL
      AND rec.starting_price IS NOT NULL
      AND CAST(rec.starting_price AS FLOAT) > 0
      AND rec.jockey_id IS NOT NULL
      AND rec.trainer_id IS NOT NULL
    LIMIT 10
    """

    df = pd.read_sql_query(query, conn)
    print(f"✅ Basic query returned {len(df)} records")
    print("Sample data:")
    print(df.head())

    # Test with stats joins
    print("\nTesting query with stats joins...")
    query_with_stats = """
    SELECT 
        rec.race_id,
        rec.horse_name,
        rec.position,
        CAST(rec.starting_price AS FLOAT) as odds_decimal,
        COALESCE(js.win_rate, 0.0) as jockey_win_pct,
        COALESCE(ts.win_rate, 0.0) as trainer_win_pct
    FROM records rec
    LEFT JOIN jockeys_stats js ON rec.jockey_id = js.jockey_id
    LEFT JOIN trainers_stats ts ON rec.trainer_id = ts.trainer_id
    WHERE rec.position IS NOT NULL
      AND rec.starting_price IS NOT NULL
      AND CAST(rec.starting_price AS FLOAT) > 0
    LIMIT 10
    """

    df_stats = pd.read_sql_query(query_with_stats, conn)
    print(f"✅ Stats query returned {len(df_stats)} records")
    print("Sample with stats:")
    print(df_stats.head())

    conn.close()
    print("✅ All queries successful!")


if __name__ == "__main__":
    test_query()
