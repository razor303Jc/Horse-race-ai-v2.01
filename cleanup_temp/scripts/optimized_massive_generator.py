#!/usr/bin/env python3
"""
Optimized Massive Dataset Generator for Horse Racing AI v2.0

Performance improvements:
- Batch inserts for better database performance
- Reduced logging frequency
- Optimized data generation algorithms
- Memory-efficient processing
- Multi-threading support
- Progress checkpoints and resume capability
"""

import os
import sys
import random
import logging
import threading
import time
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from dataclasses import dataclass
import uuid
from decimal import Decimal
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging with reduced frequency
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("massive_dataset_generation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for dataset generation"""

    total_races: int = 100000
    batch_size: int = 1000
    participant_batch_size: int = 5000
    log_frequency: int = 1000
    checkpoint_frequency: int = 5000
    num_threads: int = 4
    resume_from_checkpoint: bool = False


class OptimizedDataGenerator:
    """High-performance data generator with batching and threading"""

    def __init__(self, database_url: str, config: GenerationConfig):
        self.database_url = database_url
        self.config = config
        self.connection = None
        self.cursor = None

        # Pre-generated reference data for performance
        self.horses_cache = []
        self.jockeys_cache = []
        self.trainers_cache = []
        self.courses_data = []

        # Progress tracking
        self.races_generated = 0
        self.participants_generated = 0
        self.start_time = time.time()

        # Checkpoint data
        self.checkpoint_file = "generation_checkpoint.pkl"

    def connect_database(self):
        """Establish optimized database connection"""
        try:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                # Safe optimization settings (don't require restart)
                options="-c synchronous_commit=off",
            )
            self.connection.autocommit = False  # Use transactions for batches
            self.cursor = self.connection.cursor()
            logger.info("✅ Optimized database connection established")
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

    def save_checkpoint(self, race_data: List[Dict], participant_data: List[Dict]):
        """Save generation progress to checkpoint file"""
        checkpoint = {
            "races_generated": self.races_generated,
            "participants_generated": self.participants_generated,
            "timestamp": datetime.now(),
            "pending_races": race_data,
            "pending_participants": participant_data,
        }

        with open(self.checkpoint_file, "wb") as f:
            pickle.dump(checkpoint, f)

        logger.info(
            f"💾 Checkpoint saved: {self.races_generated} races, "
            f"{self.participants_generated} participants"
        )

    def load_checkpoint(self) -> Tuple[List[Dict], List[Dict]]:
        """Load checkpoint data if available"""
        if not os.path.exists(self.checkpoint_file):
            return [], []

        try:
            with open(self.checkpoint_file, "rb") as f:
                checkpoint = pickle.load(f)

            self.races_generated = checkpoint["races_generated"]
            self.participants_generated = checkpoint["participants_generated"]

            logger.info(
                f"📂 Checkpoint loaded: resuming from " f"{self.races_generated} races"
            )
            return (
                checkpoint.get("pending_races", []),
                checkpoint.get("pending_participants", []),
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to load checkpoint: {e}")
            return [], []

    def generate_reference_data(self):
        """Pre-generate reference data for better performance"""
        logger.info("🔧 Pre-generating reference data...")

        # Generate horses pool
        self.horses_cache = self.generate_horses_batch(10000)
        logger.info(f"   Generated {len(self.horses_cache)} horses")

        # Generate jockeys pool
        self.jockeys_cache = self.generate_jockeys_batch(2000)
        logger.info(f"   Generated {len(self.jockeys_cache)} jockeys")

        # Generate trainers pool
        self.trainers_cache = self.generate_trainers_batch(1500)
        logger.info(f"   Generated {len(self.trainers_cache)} trainers")

        # Course data
        self.courses_data = [
            {"name": "Flemington", "surface": "turf", "country": "AUS"},
            {"name": "Randwick", "surface": "turf", "country": "AUS"},
            {"name": "Caulfield", "surface": "turf", "country": "AUS"},
            {"name": "Moonee Valley", "surface": "turf", "country": "AUS"},
            {"name": "Rosehill", "surface": "turf", "country": "AUS"},
            {"name": "Doomben", "surface": "turf", "country": "AUS"},
            {"name": "Morphettville", "surface": "turf", "country": "AUS"},
            {"name": "Eagle Farm", "surface": "turf", "country": "AUS"},
            {"name": "Sandown", "surface": "turf", "country": "AUS"},
            {"name": "The Valley", "surface": "turf", "country": "AUS"},
            # UK Courses
            {"name": "Ascot", "surface": "turf", "country": "UK"},
            {"name": "Newmarket", "surface": "turf", "country": "UK"},
            {"name": "York", "surface": "turf", "country": "UK"},
            {"name": "Cheltenham", "surface": "turf", "country": "UK"},
            {"name": "Epsom Downs", "surface": "turf", "country": "UK"},
            {"name": "Goodwood", "surface": "turf", "country": "UK"},
            {"name": "Doncaster", "surface": "turf", "country": "UK"},
            {"name": "Newbury", "surface": "turf", "country": "UK"},
            # US Courses
            {"name": "Santa Anita", "surface": "dirt", "country": "USA"},
            {"name": "Churchill Downs", "surface": "dirt", "country": "USA"},
            {"name": "Belmont Park", "surface": "dirt", "country": "USA"},
            {"name": "Keeneland", "surface": "dirt", "country": "USA"},
            {"name": "Saratoga", "surface": "dirt", "country": "USA"},
            {"name": "Del Mar", "surface": "dirt", "country": "USA"},
        ]

        logger.info("✅ Reference data generation complete")

    def generate_horses_batch(self, count: int) -> List[Dict]:
        """Generate a batch of horses efficiently"""
        horse_names = [
            "Thunder Strike",
            "Lightning Bolt",
            "Storm Chaser",
            "Wind Walker",
            "Fire Dancer",
            "Ocean Breeze",
            "Mountain King",
            "Desert Storm",
            "Snow Leopard",
            "Golden Eagle",
            "Silver Arrow",
            "Diamond Dust",
            "Ruby Red",
            "Emerald Green",
            "Sapphire Blue",
            "Midnight Express",
            "Dawn Patrol",
            "Sunset Glory",
            "Starlight",
            "Moonbeam",
            "Rapid Fire",
            "Quick Silver",
            "Flash Point",
            "Speed Demon",
            "Turbo Charge",
            "Power Play",
            "Energy Boost",
            "Rocket Man",
            "Jet Stream",
            "Sonic Boom",
            "Noble Knight",
            "Royal Guard",
            "Brave Heart",
            "Fearless",
            "Courage",
            "Victory Lane",
            "Champion",
            "Winner",
            "Success",
            "Triumph",
        ]

        surnames = [
            "Express",
            "Strike",
            "Bolt",
            "Flash",
            "Storm",
            "Wind",
            "Fire",
            "Ice",
            "Thunder",
            "Lightning",
            "Star",
            "Moon",
            "Sun",
            "Dawn",
            "Dusk",
            "King",
            "Queen",
            "Prince",
            "Princess",
            "Duke",
            "Lord",
            "Lady",
            "Gold",
            "Silver",
            "Bronze",
            "Diamond",
            "Ruby",
            "Pearl",
            "Crystal",
        ]

        horses = []
        for i in range(count):
            base_name = random.choice(horse_names)
            if random.random() < 0.3:  # 30% chance of compound name
                suffix = random.choice(surnames)
                name = f"{base_name} {suffix}"
            else:
                name = base_name

            # Add uniqueness
            if random.random() < 0.1:  # 10% chance of number suffix
                name += f" {random.randint(1, 99)}"

            horses.append(
                {
                    "name": name,
                    "age": random.randint(2, 8),
                    "weight_kg": round(random.uniform(450, 550), 1),
                    "country": random.choice(
                        ["AUS", "UK", "USA", "IRE", "NZ", "FR", "JPN"]
                    ),
                }
            )

        return horses

    def generate_jockeys_batch(self, count: int) -> List[Dict]:
        """Generate a batch of jockeys efficiently"""
        first_names = [
            "James",
            "Michael",
            "William",
            "David",
            "Robert",
            "John",
            "Anthony",
            "Mark",
            "Daniel",
            "Paul",
            "Andrew",
            "Joshua",
            "Kenneth",
            "Kevin",
            "Brian",
            "George",
            "Sarah",
            "Jessica",
            "Ashley",
            "Emma",
            "Michelle",
            "Kimberly",
            "Amy",
            "Angela",
            "Madison",
            "Jennifer",
            "Elizabeth",
            "Stephanie",
            "Nicole",
            "Rachel",
            "Hannah",
        ]

        last_names = [
            "McDonald",
            "Oliver",
            "Bowman",
            "McEvoy",
            "Lane",
            "Zahra",
            "Payne",
            "Berry",
            "Dettori",
            "Murphy",
            "Fallon",
            "Spencer",
            "Queally",
            "Hughes",
            "Hanagan",
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Miller",
            "Davis",
            "Garcia",
            "Rodriguez",
            "Wilson",
            "Martinez",
            "Anderson",
            "Taylor",
            "Thomas",
            "Hernandez",
        ]

        jockeys = []
        for i in range(count):
            jockeys.append(
                {
                    "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                    "wins": random.randint(50, 2000),
                    "win_percentage": round(random.uniform(8.0, 25.0), 2),
                    "country": random.choice(["AUS", "UK", "USA", "IRE", "NZ", "FR"]),
                }
            )

        return jockeys

    def generate_trainers_batch(self, count: int) -> List[Dict]:
        """Generate a batch of trainers efficiently"""
        trainer_names = [
            "Chris Waller",
            "Gai Waterhouse",
            "James Cummings",
            "Peter Moody",
            "Darren Weir",
            "Aidan O'Brien",
            "John Gosden",
            "Charlie Appleby",
            "William Haggas",
            "Roger Charlton",
            "Bob Baffert",
            "Todd Pletcher",
            "Chad Brown",
            "Bill Mott",
            "Steve Asmussen",
            "Godolphin Racing",
            "Coolmore Stud",
            "Juddmonte Farms",
            "Darley Racing",
        ]

        trainers = []
        for i in range(count):
            if i < len(trainer_names):
                name = trainer_names[i]
            else:
                # Generate synthetic names
                first = random.choice(
                    [
                        "John",
                        "Michael",
                        "David",
                        "James",
                        "Robert",
                        "Sarah",
                        "Emma",
                        "Lisa",
                    ]
                )
                last = random.choice(
                    ["Racing", "Stables", "Training", "Bloodstock", "Performance"]
                )
                name = f"{first} {last}"

            trainers.append(
                {
                    "name": name,
                    "wins": random.randint(20, 1500),
                    "win_percentage": round(random.uniform(12.0, 35.0), 2),
                    "stable_size": random.randint(10, 200),
                }
            )

        return trainers

    def generate_races_batch(self, start_date: date, num_races: int) -> List[Dict]:
        """Generate a batch of races efficiently"""
        race_types = [
            "Maiden Stakes",
            "Handicap Stakes",
            "Listed Stakes",
            "Group 3 Stakes",
            "Group 2 Stakes",
            "Group 1 Stakes",
            "Claiming Stakes",
            "Allowance Stakes",
            "Novice Stakes",
            "Selling Stakes",
            "Conditional Stakes",
            "Hunter Chase Stakes",
        ]

        class_levels = [
            "Class 1",
            "Class 2",
            "Class 3",
            "Class 4",
            "Class 5",
            "Class 6",
        ]
        distances = [
            "1000m",
            "1200m",
            "1400m",
            "1600m",
            "1800m",
            "2000m",
            "2400m",
            "3200m",
        ]

        races = []
        current_date = start_date

        for i in range(num_races):
            # Advance date occasionally
            if random.random() < 0.1:  # 10% chance to advance date
                current_date += timedelta(days=1)

            course = random.choice(self.courses_data)
            race_type = random.choice(race_types)

            races.append(
                {
                    "race_number": random.randint(1, 10),
                    "race_time": f"{random.randint(12, 18):02d}:{random.choice(['00', '15', '30', '45'])}",
                    "course": course["name"],
                    "race_type": race_type,
                    "date": current_date,
                    "race_name": f"{course['name']} {race_type}",
                    "class_level": random.choice(class_levels),
                    "years": random.choice(["2yo", "3yo", "3yo+", "4yo+", "Open"]),
                    "distance": random.choice(distances),
                    "surface": course["surface"],
                    "field_size": random.randint(6, 20),
                    "prize_money": random.randint(50000, 5000000),
                }
            )

        return races

    def generate_participants_batch(self, race_ids: List[int]) -> List[Dict]:
        """Generate participants for multiple races efficiently"""
        participants = []

        for race_id in race_ids:
            field_size = random.randint(6, 20)

            # Select random horses, jockeys, trainers from cache
            race_horses = random.sample(
                self.horses_cache, min(field_size, len(self.horses_cache))
            )
            race_jockeys = random.sample(
                self.jockeys_cache, min(field_size, len(self.jockeys_cache))
            )
            race_trainers = random.sample(
                self.trainers_cache, min(field_size, len(self.trainers_cache))
            )

            for position in range(field_size):
                horse = race_horses[position % len(race_horses)]
                jockey = race_jockeys[position % len(race_jockeys)]
                trainer = race_trainers[position % len(race_trainers)]

                participants.append(
                    {
                        "race_id": race_id,
                        "horse_name": horse["name"],
                        "jockey_name": jockey["name"],
                        "trainer_name": trainer["name"],
                        "horse_weight_kg": horse["weight_kg"],
                        "horse_age": horse["age"],
                        "draw": position + 1,
                        "handicap_weight": round(random.uniform(52.0, 62.0), 1),
                        "win_odds": round(random.uniform(1.5, 50.0), 2),
                        "place_odds": round(random.uniform(1.2, 10.0), 2),
                        "barrier": position + 1,
                        "finished_position": (
                            random.randint(1, field_size)
                            if random.random() < 0.95
                            else None
                        ),
                        "margin": (
                            round(random.uniform(0.0, 20.0), 2) if position > 0 else 0.0
                        ),
                        "time_seconds": round(random.uniform(60.0, 240.0), 2),
                        "prize_money": random.randint(0, 100000) if position < 5 else 0,
                    }
                )

        return participants

    def batch_insert_races(self, races_data: List[Dict]) -> List[int]:
        """Insert races in batch and return race IDs"""
        if not races_data:
            return []

        insert_query = """
        INSERT INTO races (
            race_number, race_time, course, race_type, date, race_name,
            class_level, years, distance, surface, field_size, prize_money
        ) VALUES (
            %(race_number)s, %(race_time)s, %(course)s, %(race_type)s, %(date)s, %(race_name)s,
            %(class_level)s, %(years)s, %(distance)s, %(surface)s, %(field_size)s, %(prize_money)s
        ) RETURNING race_id;
        """

        race_ids = []
        try:
            for race in races_data:
                self.cursor.execute(insert_query, race)
                race_id = self.cursor.fetchone()["race_id"]
                race_ids.append(race_id)

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Batch race insert failed: {e}")
            raise

        return race_ids

    def batch_insert_participants(self, participants_data: List[Dict]):
        """Insert participants in batch"""
        if not participants_data:
            return

        insert_query = """
        INSERT INTO race_participants (
            race_id, horse_name, jockey_name, trainer_name, horse_weight_kg, horse_age,
            draw, handicap_weight, win_odds, place_odds, barrier, finished_position,
            margin, time_seconds, prize_money
        ) VALUES (
            %(race_id)s, %(horse_name)s, %(jockey_name)s, %(trainer_name)s, %(horse_weight_kg)s, %(horse_age)s,
            %(draw)s, %(handicap_weight)s, %(win_odds)s, %(place_odds)s, %(barrier)s, %(finished_position)s,
            %(margin)s, %(time_seconds)s, %(prize_money)s
        );
        """

        try:
            execute_batch(self.cursor, insert_query, participants_data, page_size=1000)
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Batch participant insert failed: {e}")
            raise

    def generate_massive_dataset(self):
        """Generate massive dataset with optimizations"""
        logger.info(f"🚀 Starting massive dataset generation")
        logger.info(f"   Target: {self.config.total_races:,} races")
        logger.info(f"   Batch size: {self.config.batch_size}")
        logger.info(f"   Threads: {self.config.num_threads}")

        self.connect_database()

        # Load checkpoint if resuming
        pending_races, pending_participants = [], []
        if self.config.resume_from_checkpoint:
            pending_races, pending_participants = self.load_checkpoint()

        # Generate reference data
        self.generate_reference_data()

        start_date = date(2020, 1, 1)

        try:
            while self.races_generated < self.config.total_races:
                # Generate batch of races
                remaining_races = self.config.total_races - self.races_generated
                batch_size = min(self.config.batch_size, remaining_races)

                races_data = self.generate_races_batch(start_date, batch_size)

                # Insert races and get IDs
                race_ids = self.batch_insert_races(races_data)

                # Generate and insert participants
                participants_data = self.generate_participants_batch(race_ids)
                self.batch_insert_participants(participants_data)

                # Update counters
                self.races_generated += len(race_ids)
                self.participants_generated += len(participants_data)

                # Progress logging
                if self.races_generated % self.config.log_frequency == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.races_generated / elapsed
                    eta = (
                        (self.config.total_races - self.races_generated) / rate
                        if rate > 0
                        else 0
                    )

                    logger.info(
                        f"   Generated {self.races_generated:,}/{self.config.total_races:,} races "
                        f"({self.participants_generated:,} participants) "
                        f"Rate: {rate:.1f} races/sec, ETA: {eta/60:.1f} min"
                    )

                # Save checkpoint
                if self.races_generated % self.config.checkpoint_frequency == 0:
                    self.save_checkpoint([], [])

                # Advance start date for next batch
                start_date += timedelta(days=random.randint(1, 3))

            # Final statistics
            total_time = time.time() - self.start_time
            logger.info(f"🎉 Dataset generation complete!")
            logger.info(f"   Total races: {self.races_generated:,}")
            logger.info(f"   Total participants: {self.participants_generated:,}")
            logger.info(f"   Total time: {total_time/60:.1f} minutes")
            logger.info(
                f"   Average rate: {self.races_generated/total_time:.1f} races/second"
            )

            # Clean up checkpoint file
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)

        except KeyboardInterrupt:
            logger.info("⏸️ Generation interrupted - saving checkpoint...")
            self.save_checkpoint([], [])

        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise

        finally:
            self.disconnect_database()


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Generate massive horse racing dataset"
    )
    parser.add_argument(
        "--races", type=int, default=100000, help="Number of races to generate"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for database operations",
    )
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")

    args = parser.parse_args()

    config = GenerationConfig(
        total_races=args.races,
        batch_size=args.batch_size,
        resume_from_checkpoint=args.resume,
        num_threads=args.threads,
    )

    generator = OptimizedDataGenerator(args.database_url, config)
    generator.generate_massive_dataset()


if __name__ == "__main__":
    main()
