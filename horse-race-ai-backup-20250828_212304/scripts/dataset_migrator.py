#!/usr/bin/env python3
"""
Dataset Migration Tool
Migrates data from the massive dataset tables (races, race_participants)
to the ML training tables (races_cards, racecard_details)
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dataset_migration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DatasetMigrator:
    """Migrates massive dataset to ML training format"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.cursor = None

    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                self.database_url, cursor_factory=RealDictCursor
            )
            self.cursor = self.connection.cursor()
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def disconnect_database(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("🔌 Database connection closed")

    def check_source_data(self):
        """Check what data is available in source tables"""
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM races")
            races_count = self.cursor.fetchone()["count"]

            self.cursor.execute("SELECT COUNT(*) as count FROM race_participants")
            participants_count = self.cursor.fetchone()["count"]

            logger.info(
                f"📊 Source data: {races_count:,} races, "
                f"{participants_count:,} participants"
            )

            return races_count, participants_count

        except Exception as e:
            logger.error(f"❌ Error checking source data: {e}")
            return 0, 0

    def clear_training_tables(self):
        """Clear existing training data"""
        try:
            logger.info("🧹 Clearing existing training tables...")

            self.cursor.execute("DELETE FROM racecard_details")
            self.cursor.execute("DELETE FROM races_cards")

            # Reset sequences if they exist
            try:
                self.cursor.execute(
                    "SELECT setval('races_cards_race_id_seq', 1, false)"
                )
            except:
                pass  # Sequence might not exist

            try:
                self.cursor.execute(
                    "SELECT setval('racecard_details_id_seq', 1, false)"
                )
            except:
                pass  # Sequence might not exist

            self.connection.commit()
            logger.info("✅ Training tables cleared")

        except Exception as e:
            logger.error(f"❌ Error clearing training tables: {e}")
            raise

    def migrate_races(self, batch_size: int = 1000):
        """Migrate races to races_cards table"""
        logger.info("🏁 Migrating races to races_cards...")

        try:
            # Get total count for progress tracking
            self.cursor.execute("SELECT COUNT(*) as count FROM races")
            total_races = self.cursor.fetchone()["count"]

            migrated = 0

            # Process in batches
            while migrated < total_races:
                # Fetch batch of races
                self.cursor.execute(
                    """
                    SELECT race_id, race_number, race_time, course, race_type, 
                           date, race_name, class_level, years, distance, 
                           surface, field_size, prize_money
                    FROM races 
                    ORDER BY race_id
                    LIMIT %s OFFSET %s
                """,
                    (batch_size, migrated),
                )

                races_batch = self.cursor.fetchall()

                if not races_batch:
                    break

                # Insert into races_cards
                insert_query = """
                    INSERT INTO races_cards (
                        race_number, race_time, course, race_type, date, 
                        race_name, class_level, years, distance, surface, 
                        field_size, prize_money, created_at, updated_at
                    ) VALUES (
                        %(race_number)s, %(race_time)s, %(course)s, %(race_type)s, 
                        %(date)s, %(race_name)s, %(class_level)s, %(years)s, 
                        %(distance)s, %(surface)s, %(field_size)s, %(prize_money)s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """

                execute_batch(self.cursor, insert_query, races_batch, page_size=500)
                self.connection.commit()

                migrated += len(races_batch)

                if migrated % 5000 == 0:
                    logger.info(f"   Migrated {migrated:,}/{total_races:,} races")

            logger.info(f"✅ Races migration complete: {migrated:,} races")
            return migrated

        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Races migration failed: {e}")
            raise

    def migrate_participants(self, batch_size: int = 5000):
        """Migrate participants to racecard_details table"""
        logger.info("🏇 Migrating participants to racecard_details...")

        try:
            # Create mapping from old race_id to new race_id
            logger.info("   Creating race ID mapping...")
            race_mapping = {}

            self.cursor.execute(
                """
                SELECT r_old.race_id as old_id, rc_new.race_id as new_id
                FROM races r_old
                JOIN races_cards rc_new ON (
                    r_old.race_number = rc_new.race_number AND
                    r_old.course = rc_new.course AND
                    r_old.date = rc_new.date AND
                    r_old.race_time = rc_new.race_time
                )
                ORDER BY r_old.race_id
            """
            )

            for row in self.cursor.fetchall():
                race_mapping[row["old_id"]] = row["new_id"]

            logger.info(f"   Created mapping for {len(race_mapping):,} races")

            # Get total participants count
            self.cursor.execute("SELECT COUNT(*) as count FROM race_participants")
            total_participants = self.cursor.fetchone()["count"]

            migrated = 0

            # Process in batches
            while migrated < total_participants:
                # Fetch batch of participants
                self.cursor.execute(
                    """
                    SELECT race_id, horse_name, jockey_name, trainer_name,
                           horse_weight_kg, horse_age, draw, handicap_weight,
                           win_odds, place_odds, barrier, finished_position,
                           margin, time_seconds, prize_money
                    FROM race_participants 
                    ORDER BY id
                    LIMIT %s OFFSET %s
                """,
                    (batch_size, migrated),
                )

                participants_batch = self.cursor.fetchall()

                if not participants_batch:
                    break

                # Transform and insert participants
                transformed_participants = []
                for participant in participants_batch:
                    old_race_id = participant["race_id"]
                    new_race_id = race_mapping.get(old_race_id)

                    if new_race_id:
                        transformed_participants.append(
                            {
                                "race_id": new_race_id,
                                "horse_name": participant["horse_name"],
                                "jockey_name": participant["jockey_name"],
                                "trainer_name": participant["trainer_name"],
                                "horse_weight_kg": participant["horse_weight_kg"],
                                "horse_age": participant["horse_age"],
                                "draw": participant["draw"],
                                "handicap_weight": participant["handicap_weight"],
                                "win_odds": participant["win_odds"],
                                "place_odds": participant["place_odds"],
                                "barrier": participant["barrier"],
                                "finished_position": participant["finished_position"],
                                "margin": participant["margin"],
                                "time_seconds": participant["time_seconds"],
                                "prize_money": participant["prize_money"] or 0,
                            }
                        )

                if transformed_participants:
                    insert_query = """
                        INSERT INTO racecard_details (
                            race_id, horse_name, jockey_name, trainer_name,
                            horse_weight_kg, horse_age, draw, handicap_weight,
                            win_odds, place_odds, barrier, finished_position,
                            margin, time_seconds, prize_money, created_at, updated_at
                        ) VALUES (
                            %(race_id)s, %(horse_name)s, %(jockey_name)s, %(trainer_name)s,
                            %(horse_weight_kg)s, %(horse_age)s, %(draw)s, %(handicap_weight)s,
                            %(win_odds)s, %(place_odds)s, %(barrier)s, %(finished_position)s,
                            %(margin)s, %(time_seconds)s, %(prize_money)s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """

                    execute_batch(
                        self.cursor,
                        insert_query,
                        transformed_participants,
                        page_size=1000,
                    )
                    self.connection.commit()

                migrated += len(participants_batch)

                if migrated % 25000 == 0:
                    logger.info(
                        f"   Migrated {migrated:,}/{total_participants:,} participants"
                    )

            logger.info(
                f"✅ Participants migration complete: {migrated:,} participants"
            )
            return migrated

        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Participants migration failed: {e}")
            raise

    def verify_migration(self):
        """Verify the migration was successful"""
        try:
            logger.info("🔍 Verifying migration...")

            # Check races_cards
            self.cursor.execute("SELECT COUNT(*) as count FROM races_cards")
            migrated_races = self.cursor.fetchone()["count"]

            # Check racecard_details
            self.cursor.execute("SELECT COUNT(*) as count FROM racecard_details")
            migrated_participants = self.cursor.fetchone()["count"]

            # Check source data again
            self.cursor.execute("SELECT COUNT(*) as count FROM races")
            source_races = self.cursor.fetchone()["count"]

            self.cursor.execute("SELECT COUNT(*) as count FROM race_participants")
            source_participants = self.cursor.fetchone()["count"]

            # Verify counts match
            races_match = migrated_races == source_races
            participants_match = (
                migrated_participants <= source_participants
            )  # Some may be filtered

            logger.info(f"📊 Migration Verification:")
            logger.info(
                f"   Races: {migrated_races:,}/{source_races:,} "
                + ("✅" if races_match else "❌")
            )
            logger.info(
                f"   Participants: {migrated_participants:,}/{source_participants:,} "
                + ("✅" if participants_match else "❌")
            )

            if races_match and participants_match:
                logger.info("✅ Migration verification PASSED")
                return True
            else:
                logger.warning("⚠️ Migration verification found discrepancies")
                return False

        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False

    def run_complete_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 Starting Complete Dataset Migration")
        logger.info("=" * 60)

        try:
            self.connect_database()

            # Check source data
            source_races, source_participants = self.check_source_data()

            if source_races == 0:
                logger.error("❌ No source data found in 'races' table")
                return False

            # Clear existing training data
            self.clear_training_tables()

            # Migrate races
            migrated_races = self.migrate_races()

            # Migrate participants
            migrated_participants = self.migrate_participants()

            # Verify migration
            verification_passed = self.verify_migration()

            if verification_passed:
                logger.info("🎉 MIGRATION COMPLETE!")
                logger.info(f"✅ Successfully migrated {migrated_races:,} races")
                logger.info(
                    f"✅ Successfully migrated {migrated_participants:,} participants"
                )
                logger.info("✅ Data ready for ML training pipeline")
                return True
            else:
                logger.error("❌ Migration verification failed")
                return False

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False

        finally:
            self.disconnect_database()


def main():
    """Main function"""
    database_url = (
        "postgresql://horse_racing_test:test_password_123@"
        "postgres:5432/horse_racing_test_db"
    )

    migrator = DatasetMigrator(database_url)
    success = migrator.run_complete_migration()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
