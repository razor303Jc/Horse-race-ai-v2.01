#!/usr/bin/env python3
"""
Clean weight data in cards database - replace '-' with '.' in weight columns
"""

import psycopg2
import os


def clean_weight_data():
    """Clean weight data by replacing '-' with '.'"""
    print("🧹 Cleaning weight data in cards database...")

    conn = psycopg2.connect(
        host="postgres",
        database="cards_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )

    try:
        cursor = conn.cursor()

        # Check current weight data issues
        cursor.execute(
            """
            SELECT COUNT(*) FROM racecard_details 
            WHERE weight LIKE '%-%'
        """
        )
        count_with_dash = cursor.fetchone()[0]
        print(f"📊 Found {count_with_dash} records with '-' in weight")

        if count_with_dash > 0:
            # Update weight data: replace '-' with '.'
            cursor.execute(
                """
                UPDATE racecard_details 
                SET weight = REPLACE(weight, '-', '.') 
                WHERE weight LIKE '%-%'
            """
            )

            updated_count = cursor.rowcount
            conn.commit()
            print(f"✅ Updated {updated_count} weight records")

            # Verify the fix
            cursor.execute(
                """
                SELECT COUNT(*) FROM racecard_details 
                WHERE weight LIKE '%-%'
            """
            )
            remaining_issues = cursor.fetchone()[0]
            print(f"🔍 Remaining records with '-': {remaining_issues}")

        else:
            print("✅ No weight data issues found")

    except Exception as e:
        print(f"❌ Error cleaning weight data: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    clean_weight_data()
