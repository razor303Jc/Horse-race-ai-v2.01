#!/usr/bin/env python3
"""
Quick database statistics check
"""

import psycopg2
import os
from dotenv import load_dotenv


def main():
    load_dotenv()

    # Use the DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return

    try:
        # Connect using SQLAlchemy engine like the training script
        from sqlalchemy import create_engine, text

        engine = create_engine(database_url)

        print("🗄️  DATABASE STATISTICS SUMMARY")
        print("=" * 50)

        with engine.connect() as conn:
            # Total races
            result = conn.execute(text("SELECT COUNT(*) FROM races_cards"))
            total_races = result.fetchone()[0]

            # Total participants
            result = conn.execute(text("SELECT COUNT(*) FROM racecard_details"))
            total_participants = result.fetchone()[0]

            # Check table structure first
            try:
                result = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'races_cards'"
                    )
                )
                columns = [row[0] for row in result.fetchall()]
                has_training_data = "is_training_data" in columns
            except:
                has_training_data = False

            if has_training_data:
                # Training data races
                result = conn.execute(
                    text(
                        "SELECT COUNT(*) FROM races_cards WHERE is_training_data = true"
                    )
                )
                training_races = result.fetchone()[0]

                # Training participants
                training_query = text(
                    """
                    SELECT COUNT(*) FROM racecard_details rd 
                    JOIN races_cards rc ON rd.race_id = rc.race_id 
                    WHERE rc.is_training_data = true
                """
                )
                result = conn.execute(training_query)
                training_participants = result.fetchone()[0]
            else:
                # All data is potentially training data
                training_races = total_races
                training_participants = total_participants

            # Recent generation stats
            try:
                recent_query = text(
                    "SELECT COUNT(*) FROM races_cards WHERE created_at >= CURRENT_DATE"
                )
                result = conn.execute(recent_query)
                todays_races = result.fetchone()[0]
            except:
                todays_races = 0

        print(f"📊 COMPLETE DATASET:")
        print(f"   Total Races: {total_races:,}")
        print(f"   Total Participants: {total_participants:,}")
        print(f"   Training Races: {training_races:,}")
        print(f"   Training Participants: {training_participants:,}")
        print(f"   Generated Today: {todays_races:,}")

        print(f"\n🎯 ML TRAINING READY:")
        print(f"   Available for Training: {training_races:,} races")
        print(f"   Participant Records: {training_participants:,}")
        print(
            f"   Data Quality: {'✅ EXCELLENT' if training_races > 100000 else '⚠️  MODERATE'}"
        )

        print("\n✅ Database statistics retrieved successfully!")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


if __name__ == "__main__":
    main()
