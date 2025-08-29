#!/usr/bin/env python3
"""
🎯 Simple Real Data Check for August 20, 2025
=============================================

Quick check of today's race data and test basic functionality.
"""

import psycopg2
import pandas as pd
from datetime import date


def simple_data_check():
    """Simple check of today's data."""
    print(f"🔍 Checking race data for {date.today()}")

    # Database connection
    conn = psycopg2.connect(
        host="localhost",
        port="5434",
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    try:
        # Simple query to check race cards
        print("\n📅 Race Cards for Today:")
        query1 = """
            SELECT course, race_number, race_time, race_name
            FROM race_cards 
            WHERE race_date = CURRENT_DATE
            ORDER BY course, race_number
        """
        df1 = pd.read_sql_query(query1, conn)
        print(f"Found {len(df1)} races")

        if len(df1) > 0:
            for course in df1["course"].unique():
                course_races = df1[df1["course"] == course]
                print(f"  📍 {course}: {len(course_races)} races")

        # Check race entries
        print("\n🐎 Race Entries:")
        query2 = """
            SELECT COUNT(*) as total_entries
            FROM race_entries re
            JOIN race_cards rc ON re.race_id = rc.race_id
            WHERE rc.race_date = CURRENT_DATE
        """
        df2 = pd.read_sql_query(query2, conn)
        print(f"Found {df2.iloc[0]['total_entries']} total entries")

        # Check advanced metrics availability
        print("\n📊 Advanced Metrics Check:")

        # Power ratings
        query3 = """
            SELECT COUNT(*) as count
            FROM horse_power_ratings
            WHERE race_date = CURRENT_DATE
        """
        df3 = pd.read_sql_query(query3, conn)
        print(f"  Power ratings: {df3.iloc[0]['count']} records")

        # Speed ratings
        query4 = """
            SELECT COUNT(*) as count
            FROM horse_speed_ratings
            WHERE race_date = CURRENT_DATE
        """
        df4 = pd.read_sql_query(query4, conn)
        print(f"  Speed ratings: {df4.iloc[0]['count']} records")

        # Monte Carlo
        query5 = """
            SELECT COUNT(*) as count
            FROM monte_carlo_simulations
            WHERE race_date = CURRENT_DATE
        """
        df5 = pd.read_sql_query(query5, conn)
        print(f"  Monte Carlo: {df5.iloc[0]['count']} records")

        # Sample data check
        if len(df1) > 0:
            print("\n🔍 Sample Race Entry with Metrics:")
            sample_query = """
                SELECT 
                    rc.course,
                    rc.race_number,
                    re.horse_name,
                    re.jockey,
                    re.win_odds,
                    pr.power_rating,
                    sr.speed_figure,
                    mc.win_probability
                FROM race_cards rc
                JOIN race_entries re ON rc.race_id = re.race_id
                LEFT JOIN horse_power_ratings pr ON re.horse_name = pr.horse_name 
                    AND rc.race_date = pr.race_date
                LEFT JOIN horse_speed_ratings sr ON re.horse_name = sr.horse_name 
                    AND rc.race_date = sr.race_date
                LEFT JOIN monte_carlo_simulations mc ON re.horse_name = mc.horse_name 
                    AND rc.race_date = mc.race_date
                WHERE rc.race_date = CURRENT_DATE
                LIMIT 5
            """
            sample_df = pd.read_sql_query(sample_query, conn)

            for _, row in sample_df.iterrows():
                print(f"  {row['horse_name']} ({row['course']} R{row['race_number']})")
                print(f"    Jockey: {row['jockey']}, Odds: {row['win_odds']}")
                print(f"    Power: {row['power_rating']}, Speed: {row['speed_figure']}")
                print(f"    MC Win Prob: {row['win_probability']}")
                print()

    finally:
        conn.close()


if __name__ == "__main__":
    simple_data_check()
