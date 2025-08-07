#!/usr/bin/env python3
"""
Fixed Dataset Migrator - Horse Racing AI v2.0
Migrates massive dataset from races/race_participants to races_cards/racecard_details
with correct column mapping based on actual table structure.
"""
import os
import logging
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dataset_migration.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    """Statistics for migration process."""

    races_migrated: int = 0
    participants_migrated: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class FixedDatasetMigrator:
    """
    Migrates data from massive dataset tables to training tables
    with correct column mapping.

    Source Tables:
    - races: race_id, race_number, race_time, course, race_type, date,
             race_name, class_level, years, distance, surface, prize,
             runners_racecard, runners, draw, created_at
    - race_participants: id, race_id, horse_name, jockey_name, trainer_name,
                        horse_weight_kg, horse_age, draw, handicap_weight,
                        win_odds, place_odds, barrier, finished_position,
                        timeform_rating, created_at

    Target Tables:
    - races_cards: race_id, race_number, race_time, course, race_type, date,
                   race_name, class, years, distance, surface, prize,
                   runners_racecard, runners, draw, created_at
    - racecard_details: id, race_id, horse_number, draw, horse_id, country,
                       name, age, weight_uk, weight, gears, horse_rate,
                       jockey_id, jockey, trainer_id, trainer, fav, odds,
                       odds_decimal, timeform_comments, created_at
    """

    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.connection = None
        self.cursor = None
        self.stats = MigrationStats()

    def connect(self) -> None:
        """Connect to database using environment configuration."""
        load_dotenv()

        try:
            database_url = os.getenv("DATABASE_URL")

            # Parse DATABASE_URL for psycopg2
            if database_url.startswith("postgresql://"):
                import urllib.parse

                result = urllib.parse.urlparse(database_url)

                self.connection = psycopg2.connect(
                    host=result.hostname,
                    database=result.path[1:],
                    user=result.username,
                    password=result.password,
                    port=result.port,
                )
            else:
                raise ValueError("Unsupported database URL format")

            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

            logger.info("✅ Database connection established")

        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("🔌 Database connection closed")

    def clear_training_tables(self) -> None:
        """Clear existing data from training tables."""
        try:
            logger.info("🧹 Clearing training tables...")

            # Clear data
            self.cursor.execute("DELETE FROM racecard_details")
            self.cursor.execute("DELETE FROM races_cards")

            # Reset sequences if they exist
            try:
                self.cursor.execute(
                    "SELECT setval('races_cards_race_id_seq', 1, false)"
                )
            except Exception:
                pass  # Sequence might not exist

            try:
                self.cursor.execute(
                    "SELECT setval('racecard_details_id_seq', 1, false)"
                )
            except Exception:
                pass  # Sequence might not exist

            self.connection.commit()
            logger.info("✅ Training tables cleared")

        except Exception as e:
            logger.error(f"❌ Failed to clear training tables: {e}")
            self.connection.rollback()
            raise

    def get_source_counts(self) -> Tuple[int, int]:
        """Get count of records in source tables."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM races")
            races_count = self.cursor.fetchone()["count"]

            self.cursor.execute("SELECT COUNT(*) FROM race_participants")
            participants_count = self.cursor.fetchone()["count"]

            return races_count, participants_count

        except Exception as e:
            logger.error(f"❌ Failed to get source counts: {e}")
            raise

    def migrate_races(self) -> Dict[int, int]:
        """
        Migrate races from source to training table.
        Returns mapping of old race_id to new race_id.
        """
        logger.info("🏁 Starting races migration...")
        race_id_mapping = {}

        try:
            # Get all races from source table
            self.cursor.execute(
                """
                SELECT race_id, race_number, race_time, course, race_type,
                       date, race_name, class_level, years, distance,
                       surface, field_size, prize_money, created_at
                FROM races
                ORDER BY race_id
            """
            )

            races = self.cursor.fetchall()
            logger.info(f"📊 Found {len(races)} races to migrate")

            # Process in batches
            for i in range(0, len(races), self.batch_size):
                batch = races[i : i + self.batch_size]

                for race in batch:
                    # Insert into races_cards with column mapping
                    insert_query = """
                        INSERT INTO races_cards (
                            race_number, race_time, course, race_type, date,
                            race_name, class, years, distance, surface,
                            prize, runners_racecard, runners, draw, created_at
                        ) VALUES (
                            %(race_number)s, %(race_time)s, %(course)s,
                            %(race_type)s, %(date)s, %(race_name)s,
                            %(class_level)s, %(years)s, %(distance)s,
                            %(surface)s, %(prize_money)s, %(field_size)s,
                            %(field_size)s, NULL, %(created_at)s
                        ) RETURNING race_id
                    """

                    self.cursor.execute(insert_query, race)
                    new_race_id = self.cursor.fetchone()["race_id"]
                    race_id_mapping[race["race_id"]] = new_race_id

                self.connection.commit()
                self.stats.races_migrated += len(batch)

                if i % (self.batch_size * 10) == 0:
                    logger.info(f"📈 Migrated {self.stats.races_migrated} races...")

            logger.info(
                f"✅ Completed races migration: {self.stats.races_migrated} races"
            )
            return race_id_mapping

        except Exception as e:
            logger.error(f"❌ Failed to migrate races: {e}")
            self.connection.rollback()
            raise

    def migrate_participants(self, race_id_mapping: Dict[int, int]) -> None:
        """Migrate race participants to racecard_details."""
        logger.info("🐎 Starting participants migration...")

        try:
            # Get all participants from source table
            self.cursor.execute(
                """
                SELECT id, race_id, horse_name, jockey_name, trainer_name,
                       horse_weight_kg, horse_age, draw, handicap_weight,
                       win_odds, place_odds, barrier, finished_position,
                       margin, time_seconds, prize_money, created_at
                FROM race_participants
                ORDER BY race_id, id
            """
            )

            participants = self.cursor.fetchall()
            logger.info(f"📊 Found {len(participants)} participants to migrate")

            # Process in batches
            for i in range(0, len(participants), self.batch_size):
                batch = participants[i : i + self.batch_size]
                batch_data = []

                for participant in batch:
                    old_race_id = participant["race_id"]
                    new_race_id = race_id_mapping.get(old_race_id)

                    if not new_race_id:
                        logger.warning(
                            f"⚠️ Skipping participant {participant['id']}: "
                            f"race_id {old_race_id} not found in mapping"
                        )
                        continue

                    # Map participant data to racecard_details columns
                    participant_data = {
                        "race_id": new_race_id,
                        "horse_number": str(participant["id"])[
                            :5
                        ],  # Truncate to 5 chars
                        "draw": participant["draw"],
                        "horse_id": participant["id"],  # Use original ID as horse_id
                        "country": "UK",  # Default country (max 5 chars)
                        "name": (
                            participant["horse_name"][:100]
                            if participant["horse_name"]
                            else None
                        ),
                        "age": participant["horse_age"],
                        "weight_uk": (
                            f"{participant['horse_weight_kg']}kg"[:10]
                            if participant["horse_weight_kg"]
                            else None
                        ),
                        "weight": (
                            float(participant["horse_weight_kg"])
                            if participant["horse_weight_kg"]
                            else None
                        ),
                        "gears": None,  # Not available in source
                        "horse_rate": (
                            str(participant["margin"])[:10]
                            if participant["margin"]
                            else None
                        ),
                        "jockey_id": None,  # Not available in source
                        "jockey": (
                            participant["jockey_name"][:100]
                            if participant["jockey_name"]
                            else None
                        ),
                        "trainer_id": None,  # Not available in source
                        "trainer": (
                            participant["trainer_name"][:100]
                            if participant["trainer_name"]
                            else None
                        ),
                        "fav": None,  # Not available in source
                        "odds": (
                            str(participant["win_odds"])[:20]
                            if participant["win_odds"]
                            else None
                        ),
                        "odds_decimal": (
                            float(participant["win_odds"])
                            if participant["win_odds"]
                            else None
                        ),
                        "timeform_comments": (
                            f"Finished: {participant['finished_position']}"
                            if participant["finished_position"]
                            else None
                        ),
                        "created_at": participant["created_at"],
                    }

                    batch_data.append(participant_data)

                if batch_data:
                    # Bulk insert
                    insert_query = """
                        INSERT INTO racecard_details (
                            race_id, horse_number, draw, horse_id, country,
                            name, age, weight_uk, weight, gears, horse_rate,
                            jockey_id, jockey, trainer_id, trainer, fav, odds,
                            odds_decimal, timeform_comments, created_at
                        ) VALUES (
                            %(race_id)s, %(horse_number)s, %(draw)s, %(horse_id)s,
                            %(country)s, %(name)s, %(age)s, %(weight_uk)s,
                            %(weight)s, %(gears)s, %(horse_rate)s, %(jockey_id)s,
                            %(jockey)s, %(trainer_id)s, %(trainer)s, %(fav)s,
                            %(odds)s, %(odds_decimal)s, %(timeform_comments)s,
                            %(created_at)s
                        )
                    """

                    self.cursor.executemany(insert_query, batch_data)
                    self.connection.commit()
                    self.stats.participants_migrated += len(batch_data)

                if i % (self.batch_size * 10) == 0:
                    logger.info(
                        f"📈 Migrated {self.stats.participants_migrated} participants..."
                    )

            logger.info(
                f"✅ Completed participants migration: "
                f"{self.stats.participants_migrated} participants"
            )

        except Exception as e:
            logger.error(f"❌ Failed to migrate participants: {e}")
            self.connection.rollback()
            raise

    def verify_migration(self) -> None:
        """Verify migration results."""
        try:
            # Get counts from training tables
            self.cursor.execute("SELECT COUNT(*) FROM races_cards")
            target_races_count = self.cursor.fetchone()["count"]

            self.cursor.execute("SELECT COUNT(*) FROM racecard_details")
            target_participants_count = self.cursor.fetchone()["count"]

            logger.info("📊 Migration Verification:")
            logger.info(f"   Races migrated: {self.stats.races_migrated}")
            logger.info(f"   Races in target: {target_races_count}")
            logger.info(f"   Participants migrated: {self.stats.participants_migrated}")
            logger.info(f"   Participants in target: {target_participants_count}")

            if target_races_count == self.stats.races_migrated:
                logger.info("✅ Race migration verified")
            else:
                logger.warning("⚠️ Race count mismatch")

            if target_participants_count == self.stats.participants_migrated:
                logger.info("✅ Participant migration verified")
            else:
                logger.warning("⚠️ Participant count mismatch")

        except Exception as e:
            logger.error(f"❌ Failed to verify migration: {e}")
            raise

    def run_migration(self) -> None:
        """Execute complete migration process."""
        try:
            self.stats.start_time = datetime.now()
            logger.info("🚀 Starting dataset migration...")

            # Connect to database
            self.connect()

            # Get source data counts
            source_races, source_participants = self.get_source_counts()
            logger.info(
                f"📊 Source data: {source_races} races, {source_participants} participants"
            )

            # Clear training tables
            self.clear_training_tables()

            # Migrate races first (to get ID mapping)
            race_id_mapping = self.migrate_races()

            # Migrate participants using race ID mapping
            self.migrate_participants(race_id_mapping)

            # Verify migration
            self.verify_migration()

            self.stats.end_time = datetime.now()

            logger.info("🎉 Migration completed successfully!")
            logger.info(f"⏱️ Total duration: {self.stats.duration:.2f} seconds")
            logger.info(
                f"📈 Migration rate: {self.stats.races_migrated/self.stats.duration:.1f} races/sec"
            )

        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            raise
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    try:
        migrator = FixedDatasetMigrator(batch_size=1000)
        migrator.run_migration()

    except KeyboardInterrupt:
        logger.info("🛑 Migration interrupted by user")
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
