#!/usr/bin/env python3
"""
Massive 100K Dataset Generator - Horse Racing AI v2.0
Ultra-high performance generator for creating 100,000 races with participants.
Optimized for maximum throughput with checkpoint/resume capability.
"""
import os
import logging
import sys
import json
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("massive_100k_generation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class GenerationStats:
    """Statistics for massive generation process."""

    races_generated: int = 0
    participants_generated: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_checkpoint: Optional[datetime] = None
    target_races: int = 100_000

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def progress_pct(self) -> float:
        return (self.races_generated / self.target_races) * 100

    @property
    def estimated_completion(self) -> Optional[datetime]:
        if self.start_time and self.races_generated > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.races_generated / elapsed
            remaining_time = (self.target_races - self.races_generated) / rate
            return datetime.now() + timedelta(seconds=remaining_time)
        return None


class Massive100KGenerator:
    """
    Ultra-high performance generator for 100,000 races.

    Features:
    - Batch processing for maximum throughput
    - Pre-generated reference data
    - Checkpoint/resume capability
    - Progress tracking and ETA
    - Memory efficient processing
    """

    def __init__(self, batch_size: int = 2000, checkpoint_interval: int = 5000):
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.connection = None
        self.cursor = None
        self.stats = GenerationStats()

        # Pre-generated reference data for performance
        self.courses = [
            "Ascot",
            "Cheltenham",
            "Newmarket",
            "York",
            "Epsom",
            "Goodwood",
            "Doncaster",
            "Chester",
            "Bath",
            "Brighton",
            "Carlisle",
            "Catterick",
            "Chepstow",
            "Fakenham",
            "Fontwell",
            "Haydock",
            "Hexham",
            "Huntingdon",
            "Kempton",
            "Leicester",
            "Lingfield",
            "Ludlow",
            "Market Rasen",
            "Newcastle",
            "Newbury",
            "Newton Abbot",
            "Nottingham",
            "Plumpton",
            "Pontefract",
            "Redcar",
            "Ripon",
            "Salisbury",
            "Sandown",
            "Sedgefield",
            "Southwell",
            "Stratford",
            "Taunton",
            "Thirsk",
            "Uttoxeter",
            "Warwick",
            "Wetherby",
            "Wincanton",
            "Windsor",
            "Wolverhampton",
            "Worcester",
        ]

        self.race_types = [
            "Flat",
            "National Hunt",
            "Hurdle",
            "Chase",
            "Bumper",
            "Maiden",
            "Handicap",
            "Stakes",
            "Listed",
            "Group 1",
            "Group 2",
            "Group 3",
            "Claiming",
            "Selling",
            "Apprentice",
            "Amateur",
            "Veteran",
        ]

        self.surfaces = ["Turf", "All Weather", "Polytrack", "Fibresand"]

        self.distances = [
            "5f",
            "5.5f",
            "6f",
            "6.5f",
            "7f",
            "7.5f",
            "1m",
            "1m1f",
            "1m2f",
            "1m3f",
            "1m4f",
            "1m5f",
            "1m6f",
            "1m7f",
            "2m",
            "2m1f",
            "2m2f",
            "2m3f",
            "2m4f",
            "2m5f",
            "3m",
            "3m1f",
            "4m",
        ]

        # Horse name components for realistic generation
        self.horse_prefixes = [
            "Royal",
            "Golden",
            "Silver",
            "Flying",
            "Dancing",
            "Mighty",
            "Swift",
            "Bold",
            "Brave",
            "Noble",
            "Wild",
            "Free",
            "Magic",
            "Thunder",
            "Lightning",
            "Star",
            "Moon",
            "Sun",
            "Fire",
            "Storm",
            "Wind",
            "Ocean",
            "River",
            "Mountain",
        ]

        self.horse_suffixes = [
            "King",
            "Queen",
            "Prince",
            "Princess",
            "Duke",
            "Duchess",
            "Lord",
            "Lady",
            "Star",
            "Spirit",
            "Dream",
            "Hope",
            "Glory",
            "Victory",
            "Legend",
            "Hero",
            "Champion",
            "Winner",
            "Runner",
            "Dancer",
            "Singer",
            "Fighter",
            "Warrior",
        ]

        self.jockey_first_names = [
            "James",
            "William",
            "Ryan",
            "Frankie",
            "Oisin",
            "Andrea",
            "Hollie",
            "Tom",
            "Danny",
            "Jamie",
            "Silvestre",
            "Jose",
            "John",
            "Paul",
            "David",
            "Richard",
            "Michael",
            "Christopher",
            "Daniel",
            "Matthew",
            "Andrew",
        ]

        self.jockey_last_names = [
            "Doyle",
            "Buick",
            "Moore",
            "Dettori",
            "Murphy",
            "Atzeni",
            "Doyle",
            "Marquand",
            "Tudhope",
            "Spencer",
            "De Sousa",
            "Luis",
            "Egan",
            "Hanagan",
            "Norton",
            "Fanning",
            "Garritty",
            "Mitchell",
            "Crowley",
            "Kingscote",
        ]

        self.trainer_names = [
            "Sir Michael Stoute",
            "John Gosden",
            "Aidan O'Brien",
            "Charlie Appleby",
            "William Haggas",
            "Mark Johnston",
            "Roger Charlton",
            "Ralph Beckett",
            "Andrew Balding",
            "Hugo Palmer",
            "Richard Hannon",
            "David Simcock",
            "James Fanshawe",
            "Stuart Williams",
            "George Baker",
            "Tom Dascombe",
            "Kevin Ryan",
            "Michael Bell",
            "Ed Dunlop",
            "Clive Cox",
        ]

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

            # Configure for high performance (basic settings only)
            self.connection.autocommit = False

            logger.info("✅ High-performance database connection established")

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

    def save_checkpoint(self) -> None:
        """Save progress checkpoint to file."""
        checkpoint_data = {
            "stats": asdict(self.stats),
            "timestamp": datetime.now().isoformat(),
        }

        with open("massive_100k_checkpoint.json", "w") as f:
            json.dump(checkpoint_data, f, indent=2, default=str)

        self.stats.last_checkpoint = datetime.now()
        logger.info(f"💾 Checkpoint saved: {self.stats.races_generated:,} races")

    def load_checkpoint(self) -> bool:
        """Load progress checkpoint from file."""
        try:
            if os.path.exists("massive_100k_checkpoint.json"):
                with open("massive_100k_checkpoint.json", "r") as f:
                    checkpoint_data = json.load(f)

                # Restore stats
                stats_data = checkpoint_data["stats"]
                self.stats.races_generated = stats_data["races_generated"]
                self.stats.participants_generated = stats_data["participants_generated"]

                if stats_data["start_time"]:
                    self.stats.start_time = datetime.fromisoformat(
                        stats_data["start_time"]
                    )

                logger.info(
                    f"📂 Checkpoint loaded: {self.stats.races_generated:,} races generated"
                )
                return True

        except Exception as e:
            logger.warning(f"⚠️ Failed to load checkpoint: {e}")

        return False

    def get_current_race_count(self) -> int:
        """Get current number of races in database."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM races")
            return self.cursor.fetchone()["count"]
        except Exception as e:
            logger.error(f"❌ Failed to get race count: {e}")
            return 0

    def generate_race_data(self, race_id: int, race_date: datetime) -> Dict:
        """Generate realistic race data."""
        return {
            "race_id": race_id,
            "race_number": random.randint(1, 8),
            "race_time": f"{random.randint(13, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
            "course": random.choice(self.courses),
            "race_type": random.choice(self.race_types),
            "date": race_date.date(),
            "race_name": f"{random.choice(self.courses)} {random.choice(['Stakes', 'Handicap', 'Maiden', 'Trophy'])}",
            "class_level": random.choice(
                ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6"]
            ),
            "years": random.choice(["2yo", "3yo", "3yo+", "4yo+", "All ages"]),
            "distance": random.choice(self.distances),
            "surface": random.choice(self.surfaces),
            "field_size": random.randint(8, 20),
            "prize_money": random.randint(5000, 500000),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def generate_participant_data(self, participant_id: int, race_id: int) -> Dict:
        """Generate realistic participant data."""
        horse_name = (
            f"{random.choice(self.horse_prefixes)} {random.choice(self.horse_suffixes)}"
        )
        jockey_name = f"{random.choice(self.jockey_first_names)} {random.choice(self.jockey_last_names)}"
        trainer_name = random.choice(self.trainer_names)

        return {
            "id": participant_id,
            "race_id": race_id,
            "horse_name": horse_name,
            "jockey_name": jockey_name,
            "trainer_name": trainer_name,
            "horse_weight_kg": round(random.uniform(400, 600), 1),
            "horse_age": random.randint(2, 12),
            "draw": random.randint(1, 20),
            "handicap_weight": round(random.uniform(50, 70), 1),
            "win_odds": round(random.uniform(1.5, 50.0), 2),
            "place_odds": round(random.uniform(1.2, 15.0), 2),
            "barrier": random.randint(1, 20),
            "finished_position": random.randint(1, 20),
            "margin": round(random.uniform(0.1, 15.0), 2),
            "time_seconds": round(random.uniform(60, 300), 2),
            "prize_money": random.randint(0, 50000),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def generate_batch(
        self, start_race_id: int, batch_size: int
    ) -> Tuple[List[Dict], List[Dict]]:
        """Generate a batch of races and participants."""
        races = []
        participants = []

        participant_id = start_race_id * 1000  # Ensure unique participant IDs

        for i in range(batch_size):
            race_id = start_race_id + i

            # Generate race date (spread over last 2 years)
            days_ago = random.randint(0, 730)
            race_date = datetime.now() - timedelta(days=days_ago)

            # Generate race data
            race_data = self.generate_race_data(race_id, race_date)
            races.append(race_data)

            # Generate participants for this race
            num_participants = random.randint(8, 18)
            for j in range(num_participants):
                participant_data = self.generate_participant_data(
                    participant_id, race_id
                )
                participants.append(participant_data)
                participant_id += 1

        return races, participants

    def insert_batch(self, races: List[Dict], participants: List[Dict]) -> None:
        """Insert batch of races and participants efficiently."""
        try:
            # Insert races
            if races:
                races_query = """
                    INSERT INTO races (
                        race_id, race_number, race_time, course, race_type, date,
                        race_name, class_level, years, distance, surface,
                        field_size, prize_money, created_at, updated_at
                    ) VALUES (
                        %(race_id)s, %(race_number)s, %(race_time)s, %(course)s,
                        %(race_type)s, %(date)s, %(race_name)s, %(class_level)s,
                        %(years)s, %(distance)s, %(surface)s, %(field_size)s,
                        %(prize_money)s, %(created_at)s, %(updated_at)s
                    ) ON CONFLICT (race_id) DO NOTHING
                """
                self.cursor.executemany(races_query, races)

            # Insert participants
            if participants:
                participants_query = """
                    INSERT INTO race_participants (
                        id, race_id, horse_name, jockey_name, trainer_name,
                        horse_weight_kg, horse_age, draw, handicap_weight,
                        win_odds, place_odds, barrier, finished_position,
                        margin, time_seconds, prize_money, created_at, updated_at
                    ) VALUES (
                        %(id)s, %(race_id)s, %(horse_name)s, %(jockey_name)s,
                        %(trainer_name)s, %(horse_weight_kg)s, %(horse_age)s,
                        %(draw)s, %(handicap_weight)s, %(win_odds)s, %(place_odds)s,
                        %(barrier)s, %(finished_position)s, %(margin)s,
                        %(time_seconds)s, %(prize_money)s, %(created_at)s, %(updated_at)s
                    ) ON CONFLICT (id) DO NOTHING
                """
                self.cursor.executemany(participants_query, participants)

            # Commit batch
            self.connection.commit()

        except Exception as e:
            logger.error(f"❌ Failed to insert batch: {e}")
            self.connection.rollback()
            raise

    def run_massive_generation(self) -> None:
        """Execute massive 100K dataset generation."""
        try:
            self.stats.start_time = datetime.now()
            logger.info("🚀 Starting massive 100K dataset generation...")

            # Connect to database
            self.connect()

            # Check for existing checkpoint
            if self.load_checkpoint():
                resume_point = self.stats.races_generated
                logger.info(f"🔄 Resuming from checkpoint: {resume_point:,} races")
            else:
                resume_point = 0
                logger.info("🆕 Starting fresh generation")

            # Get current database state
            current_race_count = self.get_current_race_count()
            logger.info(f"📊 Current database: {current_race_count:,} races")

            # Calculate starting race ID
            start_race_id = max(current_race_count + 1, resume_point + 1)

            # Main generation loop
            total_races_to_generate = self.stats.target_races - resume_point
            batches_needed = (
                total_races_to_generate + self.batch_size - 1
            ) // self.batch_size

            logger.info(f"🎯 Target: {self.stats.target_races:,} races")
            logger.info(f"📦 Batch size: {self.batch_size:,} races")
            logger.info(f"🔢 Batches needed: {batches_needed:,}")

            for batch_num in range(batches_needed):
                batch_start_race_id = start_race_id + (batch_num * self.batch_size)
                actual_batch_size = min(
                    self.batch_size,
                    total_races_to_generate - (batch_num * self.batch_size),
                )

                # Generate batch data
                races, participants = self.generate_batch(
                    batch_start_race_id, actual_batch_size
                )

                # Insert batch
                self.insert_batch(races, participants)

                # Update statistics
                self.stats.races_generated += len(races)
                self.stats.participants_generated += len(participants)

                # Progress reporting
                if batch_num % 5 == 0 or batch_num == batches_needed - 1:
                    elapsed = (datetime.now() - self.stats.start_time).total_seconds()
                    rate = self.stats.races_generated / elapsed if elapsed > 0 else 0
                    eta = self.stats.estimated_completion

                    logger.info(
                        f"📈 Progress: {self.stats.races_generated:,}/{self.stats.target_races:,} races "
                        f"({self.stats.progress_pct:.1f}%) | "
                        f"Rate: {rate:.1f} races/sec | "
                        f"ETA: {eta.strftime('%H:%M:%S') if eta else 'N/A'}"
                    )

                # Checkpoint saving
                if (batch_num + 1) % (self.checkpoint_interval // self.batch_size) == 0:
                    self.save_checkpoint()

            self.stats.end_time = datetime.now()

            # Final verification
            final_race_count = self.get_current_race_count()

            logger.info("🎉 Massive generation completed successfully!")
            logger.info(f"📊 Final statistics:")
            logger.info(f"   Races generated: {self.stats.races_generated:,}")
            logger.info(
                f"   Participants generated: {self.stats.participants_generated:,}"
            )
            logger.info(f"   Total database races: {final_race_count:,}")
            logger.info(f"⏱️ Total duration: {self.stats.duration:.2f} seconds")
            logger.info(
                f"📈 Average rate: {self.stats.races_generated/self.stats.duration:.1f} races/sec"
            )

            # Clean up checkpoint
            if os.path.exists("massive_100k_checkpoint.json"):
                os.remove("massive_100k_checkpoint.json")
                logger.info("🧹 Checkpoint file cleaned up")

        except KeyboardInterrupt:
            logger.info("🛑 Generation interrupted by user")
            self.save_checkpoint()
        except Exception as e:
            logger.error(f"💥 Generation failed: {e}")
            self.save_checkpoint()
            raise
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    try:
        # Ultra-high performance settings
        generator = Massive100KGenerator(
            batch_size=2000,  # Large batches for maximum throughput
            checkpoint_interval=5000,  # Checkpoint every 5K races
        )

        generator.run_massive_generation()

    except KeyboardInterrupt:
        logger.info("🛑 Generation interrupted by user")
    except Exception as e:
        logger.error(f"💥 Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
