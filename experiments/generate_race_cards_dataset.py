#!/usr/bin/env python3
"""
Race Card Generator from Historical Data
Converts 25K historical races into pre-race cards (without results) for ML training
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceCardGenerator:
    """Generate race cards from historical race data."""

    def __init__(self, source_db: str = "massive_racing_data_with_markets.db"):
        self.source_db = source_db
        self.target_db = "race_cards_prediction_data.db"

    def create_prediction_database(self):
        """Create database for race card prediction data."""

        logger.info("🏗️ Creating race cards prediction database...")

        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()

        # Race cards table (pre-race information)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS race_cards (
            race_id INTEGER PRIMARY KEY,
            race_number TEXT,
            race_time TEXT,
            course TEXT,
            race_type TEXT,
            date DATE,
            race_name TEXT,
            class_level TEXT,
            years TEXT,
            distance TEXT,
            surface TEXT,
            field_size INTEGER,
            prize_money INTEGER,
            weather_condition TEXT DEFAULT 'good',
            track_condition TEXT DEFAULT 'good',
            going TEXT DEFAULT 'good',
            rail_position TEXT DEFAULT 'true',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Race card details table (horse entries without results)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS race_card_entries (
            entry_id INTEGER PRIMARY KEY,
            race_id INTEGER,
            horse_name TEXT,
            jockey_name TEXT,
            trainer_name TEXT,
            horse_weight_kg REAL,
            horse_age INTEGER,
            draw INTEGER,
            handicap_weight REAL,
            barrier INTEGER,
            morning_line_odds REAL,
            form_string TEXT,
            last_start_days INTEGER,
            career_starts INTEGER,
            career_wins INTEGER,
            career_places INTEGER,
            recent_form_rating INTEGER DEFAULT 50,
            speed_rating INTEGER DEFAULT 50,
            class_rating INTEGER DEFAULT 50,
            track_rating INTEGER DEFAULT 50,
            distance_rating INTEGER DEFAULT 50,
            jockey_rating INTEGER DEFAULT 50,
            trainer_rating INTEGER DEFAULT 50,
            equipment TEXT DEFAULT '',
            comments TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (race_id) REFERENCES race_cards(race_id)
        )
        """
        )

        # Predictions table (for storing ML predictions)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS ml_predictions (
            prediction_id INTEGER PRIMARY KEY,
            race_id INTEGER,
            entry_id INTEGER,
            model_name TEXT,
            win_probability REAL,
            place_probability REAL,
            predicted_odds REAL,
            confidence_score REAL,
            prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (race_id) REFERENCES race_cards(race_id),
            FOREIGN KEY (entry_id) REFERENCES race_card_entries(entry_id)
        )
        """
        )

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_race_cards_date ON race_cards(date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_race_cards_course ON race_cards(course)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_entries_race_id ON race_card_entries(race_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_predictions_race_id ON ml_predictions(race_id)"
        )

        conn.commit()
        conn.close()

        logger.info("✅ Race cards prediction database created")

    def extract_race_cards(self, limit: int = 25000):
        """Extract race cards from historical data."""

        logger.info(f"📊 Extracting {limit:,} race cards from historical data...")

        # Connect to source database
        source_conn = sqlite3.connect(self.source_db)

        # Get random sample of races
        query = """
        SELECT DISTINCT race_id 
        FROM races 
        ORDER BY RANDOM() 
        LIMIT ?
        """
        race_ids = pd.read_sql_query(query, source_conn, params=[limit])

        logger.info(f"📋 Selected {len(race_ids)} races for conversion")

        # Extract race information
        race_query = """
        SELECT * FROM races 
        WHERE race_id IN ({})
        """.format(
            ",".join(["?"] * len(race_ids))
        )

        races_df = pd.read_sql_query(
            race_query, source_conn, params=race_ids["race_id"].tolist()
        )

        # Extract participant information (without results)
        participants_query = """
        SELECT 
            race_id,
            horse_name,
            jockey_name,
            trainer_name,
            horse_weight_kg,
            horse_age,
            draw,
            handicap_weight,
            barrier,
            win_odds as morning_line_odds,
            form_rating as recent_form_rating,
            speed_rating,
            class_rating
        FROM race_participants 
        WHERE race_id IN ({})
        AND finished_position IS NOT NULL
        """.format(
            ",".join(["?"] * len(race_ids))
        )

        participants_df = pd.read_sql_query(
            participants_query, source_conn, params=race_ids["race_id"].tolist()
        )

        source_conn.close()

        logger.info(f"🏇 Extracted {len(participants_df)} horse entries")

        return races_df, participants_df

    def enhance_race_cards(self, races_df, participants_df):
        """Add realistic race card enhancements."""

        logger.info("🔧 Enhancing race cards with additional data...")

        # Add race card specific fields
        races_df["going"] = np.random.choice(
            ["good", "soft", "heavy", "firm"],
            size=len(races_df),
            p=[0.6, 0.2, 0.1, 0.1],
        )
        races_df["rail_position"] = np.random.choice(
            ["true", "out 2m", "out 4m"], size=len(races_df), p=[0.8, 0.15, 0.05]
        )

        # Generate realistic form strings
        def generate_form_string():
            form_length = random.randint(3, 8)
            form_chars = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "X", "F"]
            return "".join(random.choices(form_chars, k=form_length))

        participants_df["form_string"] = [
            generate_form_string() for _ in range(len(participants_df))
        ]

        # Generate career statistics
        participants_df["career_starts"] = np.random.randint(
            1, 50, size=len(participants_df)
        )
        participants_df["career_wins"] = np.random.randint(
            0, participants_df["career_starts"] // 3 + 1, size=len(participants_df)
        )
        participants_df["career_places"] = np.random.randint(
            participants_df["career_wins"],
            participants_df["career_starts"] + 1,
            size=len(participants_df),
        )

        # Last start days
        participants_df["last_start_days"] = np.random.randint(
            7, 365, size=len(participants_df)
        )

        # Additional ratings
        participants_df["track_rating"] = np.random.randint(
            30, 80, size=len(participants_df)
        )
        participants_df["distance_rating"] = np.random.randint(
            30, 80, size=len(participants_df)
        )
        participants_df["jockey_rating"] = np.random.randint(
            40, 90, size=len(participants_df)
        )
        participants_df["trainer_rating"] = np.random.randint(
            40, 90, size=len(participants_df)
        )

        # Equipment and comments
        equipment_options = ["", "Blinkers", "Visor", "Tongue Tie", "Lugging Bit"]
        participants_df["equipment"] = np.random.choice(
            equipment_options, size=len(participants_df), p=[0.6, 0.15, 0.1, 0.1, 0.05]
        )

        comments = [
            "",
            "First-up",
            "Second-up",
            "Resuming",
            "On trial",
            "Improved fitness",
        ]
        participants_df["comments"] = np.random.choice(
            comments, size=len(participants_df), p=[0.5, 0.15, 0.1, 0.1, 0.1, 0.05]
        )

        logger.info("✅ Race card enhancements complete")

        return races_df, participants_df

    def save_race_cards(self, races_df, participants_df):
        """Save race cards to prediction database."""

        logger.info("💾 Saving race cards to prediction database...")

        conn = sqlite3.connect(self.target_db)

        # Select only columns that exist in our target schema
        race_columns = [
            "race_id",
            "race_number",
            "race_time",
            "course",
            "race_type",
            "date",
            "race_name",
            "class_level",
            "years",
            "distance",
            "surface",
            "field_size",
            "prize_money",
            "weather_condition",
            "track_condition",
            "going",
            "rail_position",
        ]

        # Filter races dataframe to only include existing columns
        races_filtered = races_df[
            [col for col in race_columns if col in races_df.columns]
        ].copy()

        # Add missing columns with defaults
        if "going" not in races_filtered.columns:
            races_filtered["going"] = "good"
        if "rail_position" not in races_filtered.columns:
            races_filtered["rail_position"] = "true"

        # Select participant columns
        participant_columns = [
            "race_id",
            "horse_name",
            "jockey_name",
            "trainer_name",
            "horse_weight_kg",
            "horse_age",
            "draw",
            "handicap_weight",
            "barrier",
            "morning_line_odds",
            "form_string",
            "last_start_days",
            "career_starts",
            "career_wins",
            "career_places",
            "recent_form_rating",
            "speed_rating",
            "class_rating",
            "track_rating",
            "distance_rating",
            "jockey_rating",
            "trainer_rating",
            "equipment",
            "comments",
        ]

        # Filter participants dataframe
        participants_filtered = participants_df[
            [col for col in participant_columns if col in participants_df.columns]
        ].copy()

        # Save race cards
        races_filtered.to_sql("race_cards", conn, if_exists="append", index=False)

        # Save race card entries
        participants_filtered.to_sql(
            "race_card_entries", conn, if_exists="append", index=False
        )

        conn.close()

        logger.info(
            f"✅ Saved {len(races_filtered)} race cards and {len(participants_filtered)} entries"
        )

    def generate_race_cards_dataset(self, limit: int = 25000):
        """Complete race cards generation process."""

        start_time = datetime.now()

        logger.info("🚀 RACE CARDS DATASET GENERATION")
        logger.info("=" * 50)

        try:
            # 1. Create database
            self.create_prediction_database()

            # 2. Extract race data
            races_df, participants_df = self.extract_race_cards(limit)

            # 3. Enhance race cards
            races_df, participants_df = self.enhance_race_cards(
                races_df, participants_df
            )

            # 4. Save to database
            self.save_race_cards(races_df, participants_df)

            # 5. Generate summary
            conn = sqlite3.connect(self.target_db)

            race_count = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM race_cards", conn
            ).iloc[0]["count"]
            entry_count = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM race_card_entries", conn
            ).iloc[0]["count"]

            courses_count = pd.read_sql_query(
                "SELECT COUNT(DISTINCT course) as count FROM race_cards", conn
            ).iloc[0]["count"]

            conn.close()

            duration = datetime.now() - start_time

            logger.info("\n🎉 RACE CARDS GENERATION COMPLETE!")
            logger.info("=" * 50)
            logger.info(f"📊 Race Cards: {race_count:,}")
            logger.info(f"🏇 Horse Entries: {entry_count:,}")
            logger.info(f"🏟️ Unique Courses: {courses_count:,}")
            logger.info(f"⏱️ Generation Time: {duration}")
            logger.info(f"💾 Database: {self.target_db}")

            # Database size
            db_size = Path(self.target_db).stat().st_size / (1024 * 1024)
            logger.info(f"📁 Database Size: {db_size:.1f}MB")

            return True

        except Exception as e:
            logger.error(f"❌ Race cards generation failed: {e}")
            return False


def main():
    """Main function to generate race cards dataset."""

    generator = RaceCardGenerator()
    success = generator.generate_race_cards_dataset(limit=25000)

    if success:
        logger.info("\n✅ Ready for ML prediction training!")
        logger.info(
            "🎯 Use this dataset for training ML models on race card prediction"
        )
    else:
        logger.error("\n❌ Failed to generate race cards dataset")


if __name__ == "__main__":
    main()
