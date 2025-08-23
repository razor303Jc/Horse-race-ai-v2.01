#!/usr/bin/env python3
"""
Comprehensive Test Data Generator for Horse Racing AI v2.0

Generates massive amounts of realistic fake data for testing:
- 50,000+ races across multiple years
- Realistic horses, jockeys, trainers
- Complete race results and statistics
- Proper relationships between all entities
- Optimized for test environment database
"""

import os
import sys
import random
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass
import uuid
from decimal import Decimal
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RaceData:
    """Container for race information"""

    race_id: int
    race_number: int
    race_time: str
    course: str
    race_type: str
    date: date
    race_name: str
    class_level: str
    years: str
    distance: str
    surface: str
    prize: str
    runners_racecard: int
    runners: int
    draw: int


@dataclass
class HorseData:
    """Container for horse information"""

    horse_id: int
    name: str
    country: str
    age: int
    color: str
    owner: str
    sire: str
    dam: str
    sex: str
    total_races: int
    wins: int
    percentage_wins: float
    placed: int
    percentage_placed: float
    flat_turf_races: int
    flat_turf_wins: int
    flat_turf_rate: float


@dataclass
class JockeyData:
    """Container for jockey information"""

    jockey_id: int
    name: str
    country: str
    total_races: int
    wins: int
    percentage_wins: float
    placed: int
    percentage_placed: float


@dataclass
class TrainerData:
    """Container for trainer information"""

    trainer_id: int
    name: str
    country: str
    location: str
    total_races: int
    wins: int
    percentage_wins: float
    placed: int
    percentage_placed: float


class TestDataGenerator:
    """Generates massive amounts of realistic horse racing test data"""

    def __init__(self, database_url: str = None):
        """Initialize with test database connection"""
        self.database_url = (
            database_url
            or "postgresql://horse_racing_test:test_password_123@postgres:5432/horse_racing_test_db"
        )
        self.connection = None

        # Data generation parameters
        self.total_races = 50000
        self.years_back = 5
        self.courses_count = 60
        self.horses_count = 15000
        self.jockeys_count = 800
        self.trainers_count = 1200

        # Realistic data pools
        self.courses = [
            "Ascot",
            "Cheltenham",
            "Newmarket",
            "Epsom",
            "Doncaster",
            "York",
            "Goodwood",
            "Chester",
            "Bath",
            "Brighton",
            "Carlisle",
            "Catterick",
            "Chepstow",
            "Exeter",
            "Fakenham",
            "Fontwell",
            "Hamilton",
            "Haydock",
            "Hereford",
            "Hexham",
            "Huntingdon",
            "Kempton",
            "Leicester",
            "Lingfield",
            "Ludlow",
            "Market Rasen",
            "Musselburgh",
            "Newcastle",
            "Newbury",
            "Newton Abbot",
            "Nottingham",
            "Perth",
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
            "Towcester",
            "Uttoxeter",
            "Warwick",
            "Wetherby",
            "Wincanton",
            "Windsor",
            "Wolverhampton",
            "Worcester",
            "Yarmouth",
            "Aintree",
            "Bangor",
            "Cartmel",
            "Cork",
            "Curragh",
            "Downpatrick",
            "Fairyhouse",
            "Galway",
        ]

        self.race_types = ["Flat", "Hurdle", "Chase", "National Hunt Flat", "Bumper"]
        self.surfaces = ["Turf", "All Weather", "Polytrack", "Fibresand"]
        self.horse_colors = [
            "Bay",
            "Chestnut",
            "Brown",
            "Black",
            "Grey",
            "Roan",
            "Dun",
            "Palomino",
        ]
        self.countries = ["GB", "IRE", "FR", "USA", "AUS", "GER", "ITA", "JPN"]
        self.genders = ["Colt", "Filly", "Gelding", "Mare", "Stallion", "Horse"]

        # Name generators
        self.horse_name_parts = {
            "prefix": [
                "Royal",
                "Golden",
                "Silver",
                "Mighty",
                "Swift",
                "Noble",
                "Thunder",
                "Lightning",
                "Fire",
                "Ice",
                "Storm",
                "Wind",
                "Star",
                "Moon",
                "Sun",
                "Diamond",
                "Crystal",
                "Magic",
                "Mystic",
                "Secret",
                "Hidden",
                "Flying",
                "Dancing",
                "Singing",
            ],
            "suffix": [
                "King",
                "Queen",
                "Prince",
                "Princess",
                "Lord",
                "Lady",
                "Knight",
                "Warrior",
                "Spirit",
                "Dream",
                "Hope",
                "Glory",
                "Victory",
                "Champion",
                "Hero",
                "Legend",
                "Storm",
                "Thunder",
                "Lightning",
                "Flame",
                "Blaze",
                "Flash",
                "Arrow",
                "Bullet",
            ],
        }

        self.jockey_first_names = [
            "Ryan",
            "William",
            "Frankie",
            "Oisin",
            "Tom",
            "James",
            "Danny",
            "Andrea",
            "Hollie",
            "Sean",
            "Jim",
            "Jamie",
            "Adam",
            "Ben",
            "Charlie",
            "David",
            "Harry",
            "Jack",
            "Luke",
            "Mark",
            "Paul",
            "Richard",
            "Sam",
            "Tony",
            "Kevin",
            "Martin",
            "Michael",
            "Neil",
            "Rachel",
            "Hayley",
            "Laura",
            "Nicola",
            "Sarah",
            "Emma",
            "Katie",
            "Josephine",
        ]

        self.jockey_last_names = [
            "Moore",
            "Dettori",
            "Murphy",
            "Marquand",
            "Buick",
            "Doyle",
            "Tudhope",
            "Atzeni",
            "Crowley",
            "Kirby",
            "Norton",
            "Fanning",
            "Hanagan",
            "Spencer",
            "Shoemark",
            "Carson",
            "Levey",
            "Mitchell",
            "Watson",
            "Dawson",
            "Bishop",
            "Garritty",
            "Gray",
            "Hart",
            "Haynes",
            "Kingscote",
            "Morris",
            "Mullen",
            "Probert",
            "Quinn",
            "Rawlinson",
            "Ryan",
        ]

    def connect_database(self):
        """Connect to the test database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.connection.autocommit = False
            logger.info("✅ Connected to test database successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise

    def create_database_schema(self):
        """Create all required database tables"""
        logger.info("🏗️ Creating database schema...")

        schema_sql = """
        -- Core racing tables
        
        CREATE TABLE IF NOT EXISTS races_cards (
            race_id SERIAL PRIMARY KEY,
            race_number INTEGER,
            race_time VARCHAR(10),
            course VARCHAR(100),
            race_type VARCHAR(50),
            date DATE,
            race_name VARCHAR(200),
            class VARCHAR(10),
            years VARCHAR(20),
            distance VARCHAR(20),
            surface VARCHAR(30),
            prize VARCHAR(50),
            runners_racecard INTEGER,
            runners INTEGER,
            draw INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS races_results (
            race_id SERIAL PRIMARY KEY,
            race_number INTEGER,
            race_time VARCHAR(10),
            course VARCHAR(100),
            race_type VARCHAR(50),
            date DATE,
            race_name VARCHAR(200),
            class VARCHAR(10),
            years VARCHAR(20),
            distance VARCHAR(20),
            surface VARCHAR(30),
            prize VARCHAR(50),
            runners_racecard INTEGER,
            runners INTEGER,
            draw INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS horses_cards (
            horse_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            country VARCHAR(5),
            age INTEGER,
            color VARCHAR(30),
            owner VARCHAR(200),
            sire VARCHAR(100),
            dam VARCHAR(100),
            sex VARCHAR(20),
            total_races INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            percentage_wins DECIMAL(5,2) DEFAULT 0.00,
            placed INTEGER DEFAULT 0,
            percentage_placed DECIMAL(5,2) DEFAULT 0.00,
            flat_turf_races INTEGER DEFAULT 0,
            flat_turf_wins INTEGER DEFAULT 0,
            flat_turf_rate DECIMAL(5,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS horses_results (
            horse_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            country VARCHAR(5),
            age INTEGER,
            color VARCHAR(30),
            owner VARCHAR(200),
            sire VARCHAR(100),
            dam VARCHAR(100),
            sex VARCHAR(20),
            total_races INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            percentage_wins DECIMAL(5,2) DEFAULT 0.00,
            placed INTEGER DEFAULT 0,
            percentage_placed DECIMAL(5,2) DEFAULT 0.00,
            flat_turf_races INTEGER DEFAULT 0,
            flat_turf_wins INTEGER DEFAULT 0,
            flat_turf_rate DECIMAL(5,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jockeys_stats (
            jockey_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            country VARCHAR(5),
            total_races INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            percentage_wins DECIMAL(5,2) DEFAULT 0.00,
            placed INTEGER DEFAULT 0,
            percentage_placed DECIMAL(5,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trainers_stats (
            trainer_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            country VARCHAR(5),
            location VARCHAR(100),
            total_races INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            percentage_wins DECIMAL(5,2) DEFAULT 0.00,
            placed INTEGER DEFAULT 0,
            percentage_placed DECIMAL(5,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS racecard_details (
            id SERIAL PRIMARY KEY,
            race_id INTEGER,
            horse_number VARCHAR(5),
            draw INTEGER,
            horse_id INTEGER,
            country VARCHAR(5),
            name VARCHAR(100),
            age INTEGER,
            weight_uk VARCHAR(10),
            weight DECIMAL(6,2),
            gears VARCHAR(10),
            horse_rate VARCHAR(10),
            jockey_id INTEGER,
            jockey VARCHAR(100),
            trainer_id INTEGER,
            trainer VARCHAR(100),
            fav VARCHAR(10),
            odds VARCHAR(20),
            odds_decimal DECIMAL(8,2),
            timeform_comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            race_id INTEGER,
            place INTEGER,
            horse_number VARCHAR(5),
            name VARCHAR(100),
            age INTEGER,
            weight VARCHAR(10),
            jockey VARCHAR(100),
            trainer VARCHAR(100),
            odds VARCHAR(20),
            time VARCHAR(20),
            margin VARCHAR(20),
            prize_money VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_races_cards_date ON races_cards(date);
        CREATE INDEX IF NOT EXISTS idx_races_cards_course ON races_cards(course);
        CREATE INDEX IF NOT EXISTS idx_horses_cards_name ON horses_cards(name);
        CREATE INDEX IF NOT EXISTS idx_jockeys_stats_name ON jockeys_stats(name);
        CREATE INDEX IF NOT EXISTS idx_trainers_stats_name ON trainers_stats(name);
        CREATE INDEX IF NOT EXISTS idx_racecard_details_race_id ON racecard_details(race_id);
        CREATE INDEX IF NOT EXISTS idx_records_race_id ON records(race_id);
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(schema_sql)
            self.connection.commit()
            logger.info("✅ Database schema created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create schema: {e}")
            self.connection.rollback()
            raise

    def generate_horse_name(self) -> str:
        """Generate a realistic horse name"""
        if random.random() < 0.7:  # 70% compound names
            prefix = random.choice(self.horse_name_parts["prefix"])
            suffix = random.choice(self.horse_name_parts["suffix"])
            return f"{prefix} {suffix}"
        else:  # 30% single names with variations
            name = random.choice(
                self.horse_name_parts["prefix"] + self.horse_name_parts["suffix"]
            )
            if random.random() < 0.3:
                return (
                    f"{name} {random.choice(['Boy', 'Girl', 'Star', 'Lady', 'Lord'])}"
                )
            return name

    def generate_jockey_name(self) -> str:
        """Generate a realistic jockey name"""
        first = random.choice(self.jockey_first_names)
        last = random.choice(self.jockey_last_names)
        return f"{first} {last}"

    def generate_trainer_name(self) -> str:
        """Generate a realistic trainer name"""
        first = random.choice(self.jockey_first_names)
        last = random.choice(self.jockey_last_names)
        if random.random() < 0.1:  # 10% chance of title
            title = random.choice(["Sir", "Lady", "Dr", "Mr", "Mrs", "Miss"])
            return f"{title} {first} {last}"
        return f"{first} {last}"

    def generate_race_name(self, course: str, race_type: str) -> str:
        """Generate a realistic race name"""
        prefixes = [
            "Maiden",
            "Handicap",
            "Stakes",
            "Trophy",
            "Cup",
            "Classic",
            "Festival",
            "Championship",
        ]
        suffixes = [
            "Stakes",
            "Handicap",
            "Trophy",
            "Cup",
            "Race",
            "Challenge",
            "Classic",
        ]

        if random.random() < 0.3:  # 30% course-named races
            prefix = random.choice(prefixes)
            return f"{course} {prefix}"
        elif random.random() < 0.2:  # 20% sponsored races
            sponsor = random.choice(
                ["Coral", "Ladbrokes", "Paddy Power", "Sky Bet", "William Hill"]
            )
            suffix = random.choice(suffixes)
            return f"{sponsor} {suffix}"
        else:
            return f"{random.choice(prefixes)} {random.choice(suffixes)}"

    def generate_horses(self) -> List[HorseData]:
        """Generate realistic horse data"""
        logger.info(f"🐎 Generating {self.horses_count} horses...")
        horses = []

        for i in range(self.horses_count):
            # Generate realistic racing stats
            total_races = random.randint(1, 50)
            wins = random.randint(0, min(total_races, 15))
            placed = random.randint(wins, min(total_races, wins + 10))

            # Calculate percentages
            win_rate = (wins / total_races * 100) if total_races > 0 else 0
            place_rate = (placed / total_races * 100) if total_races > 0 else 0

            # Flat turf specific stats
            flat_races = random.randint(0, total_races)
            flat_wins = random.randint(0, min(flat_races, wins))
            flat_rate = (flat_wins / flat_races * 100) if flat_races > 0 else 0

            horse = HorseData(
                horse_id=i + 1,
                name=self.generate_horse_name(),
                country=random.choice(self.countries),
                age=random.randint(2, 12),
                color=random.choice(self.horse_colors),
                owner=f"{random.choice(self.jockey_first_names)} {random.choice(self.jockey_last_names)} Racing",
                sire=self.generate_horse_name(),
                dam=self.generate_horse_name(),
                sex=random.choice(self.genders),
                total_races=total_races,
                wins=wins,
                percentage_wins=round(win_rate, 2),
                placed=placed,
                percentage_placed=round(place_rate, 2),
                flat_turf_races=flat_races,
                flat_turf_wins=flat_wins,
                flat_turf_rate=round(flat_rate, 2),
            )
            horses.append(horse)

            if (i + 1) % 1000 == 0:
                logger.info(f"   Generated {i + 1}/{self.horses_count} horses...")

        return horses

    def generate_jockeys(self) -> List[JockeyData]:
        """Generate realistic jockey data"""
        logger.info(f"🏇 Generating {self.jockeys_count} jockeys...")
        jockeys = []

        for i in range(self.jockeys_count):
            # Professional jockeys have higher ride counts
            if i < 50:  # Top 50 jockeys
                total_races = random.randint(200, 2000)
                win_rate = random.uniform(15, 25)
            elif i < 200:  # Good jockeys
                total_races = random.randint(100, 500)
                win_rate = random.uniform(8, 18)
            else:  # Other jockeys
                total_races = random.randint(20, 200)
                win_rate = random.uniform(3, 12)

            wins = int(total_races * win_rate / 100)
            placed = int(total_races * random.uniform(30, 50) / 100)

            jockey = JockeyData(
                jockey_id=i + 1,
                name=self.generate_jockey_name(),
                country=random.choice(self.countries[:4]),  # Mainly GB, IRE, FR, USA
                total_races=total_races,
                wins=wins,
                percentage_wins=round(win_rate, 2),
                placed=placed,
                percentage_placed=round((placed / total_races * 100), 2),
            )
            jockeys.append(jockey)

        return jockeys

    def generate_trainers(self) -> List[TrainerData]:
        """Generate realistic trainer data"""
        logger.info(f"👨‍🏫 Generating {self.trainers_count} trainers...")
        trainers = []

        locations = [
            "Newmarket",
            "Lambourn",
            "Middleham",
            "Malton",
            "Epsom",
            "Kingsclere",
            "Upper Lambourn",
            "East Everleigh",
            "Whatcombe",
            "Beckhampton",
        ]

        for i in range(self.trainers_count):
            # Top trainers have more runners
            if i < 100:  # Top 100 trainers
                total_races = random.randint(300, 1500)
                win_rate = random.uniform(12, 22)
            elif i < 400:  # Good trainers
                total_races = random.randint(100, 400)
                win_rate = random.uniform(6, 15)
            else:  # Other trainers
                total_races = random.randint(20, 150)
                win_rate = random.uniform(2, 10)

            wins = int(total_races * win_rate / 100)
            placed = int(total_races * random.uniform(25, 45) / 100)

            trainer = TrainerData(
                trainer_id=i + 1,
                name=self.generate_trainer_name(),
                country=random.choice(self.countries[:4]),
                location=random.choice(locations),
                total_races=total_races,
                wins=wins,
                percentage_wins=round(win_rate, 2),
                placed=placed,
                percentage_placed=round((placed / total_races * 100), 2),
            )
            trainers.append(trainer)

        return trainers

    def generate_races(self) -> List[RaceData]:
        """Generate realistic race data over multiple years"""
        logger.info(
            f"🏁 Generating {self.total_races} races over {self.years_back} years..."
        )
        races = []

        # Generate races across date range
        start_date = date.today() - timedelta(days=self.years_back * 365)
        end_date = date.today()

        current_id = 1
        for _ in range(self.total_races):
            # Random date in range
            days_diff = (end_date - start_date).days
            race_date = start_date + timedelta(days=random.randint(0, days_diff))

            # Skip some Sundays (fewer races)
            if race_date.weekday() == 6 and random.random() < 0.7:
                continue

            course = random.choice(self.courses)
            race_type = random.choice(self.race_types)

            # Generate race details
            race_number = random.randint(1, 8)
            hour = random.randint(13, 17)  # 1 PM to 5 PM
            minute = random.choice([0, 15, 30, 45])
            race_time = f"{hour:02d}:{minute:02d}"

            # Runners vary by race type and course
            if course in ["Ascot", "Cheltenham", "Newmarket"]:
                runners = random.randint(8, 20)
            else:
                runners = random.randint(4, 16)

            # Distance varies by race type
            if race_type == "Flat":
                distances = ["5f", "6f", "7f", "1m", "1m2f", "1m4f", "1m6f", "2m"]
            else:
                distances = ["2m", "2m4f", "2m6f", "3m", "3m2f", "3m4f"]

            # Prize money varies by course prestige
            if course in ["Ascot", "Cheltenham", "Newmarket", "Epsom"]:
                prize_base = random.randint(15000, 150000)
            else:
                prize_base = random.randint(3000, 25000)

            race = RaceData(
                race_id=current_id,
                race_number=race_number,
                race_time=race_time,
                course=course,
                race_type=race_type,
                date=race_date,
                race_name=self.generate_race_name(course, race_type),
                class_level=random.choice(["1", "2", "3", "4", "5", "6"]),
                years=random.choice(["2yo", "3yo", "4yo+", "3yo+", "2-3yo"]),
                distance=random.choice(distances),
                surface=random.choice(self.surfaces),
                prize=f"£{prize_base:,}",
                runners_racecard=runners,
                runners=runners
                - random.randint(0, 2),  # Slight variation for actual runners
                draw=random.randint(1, 20),
            )
            races.append(race)
            current_id += 1

            if len(races) % 5000 == 0:
                logger.info(f"   Generated {len(races)}/{self.total_races} races...")

        return races[: self.total_races]

    def insert_data_batch(self, table: str, data: List[Dict], batch_size: int = 1000):
        """Insert data in batches for performance"""
        logger.info(f"📝 Inserting {len(data)} records into {table}...")

        if not data:
            return

        # Get column names from first record
        columns = list(data[0].keys())

        # Create INSERT statement
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({placeholders})
        """

        try:
            with self.connection.cursor() as cursor:
                for i in range(0, len(data), batch_size):
                    batch = data[i : i + batch_size]
                    values = [tuple(record[col] for col in columns) for record in batch]
                    cursor.executemany(insert_sql, values)

                    if (i + batch_size) % 5000 == 0:
                        logger.info(
                            f"   Inserted {min(i + batch_size, len(data))}/{len(data)} records..."
                        )

            self.connection.commit()
            logger.info(f"✅ Successfully inserted {len(data)} records into {table}")

        except Exception as e:
            logger.error(f"❌ Failed to insert data into {table}: {e}")
            self.connection.rollback()
            raise

    def generate_race_participants(
        self,
        races: List[RaceData],
        horses: List[HorseData],
        jockeys: List[JockeyData],
        trainers: List[TrainerData],
    ):
        """Generate racecard details and results for all races"""
        logger.info("🏇 Generating race participants and results...")

        racecard_data = []
        records_data = []

        for race_idx, race in enumerate(races):
            # Select random participants for this race
            race_horses = random.sample(horses, min(race.runners, len(horses)))

            # Generate racecard details
            for pos, horse in enumerate(race_horses, 1):
                jockey = random.choice(jockeys)
                trainer = random.choice(trainers)

                # Generate realistic odds
                if pos == 1:  # Favorite
                    odds_decimal = round(random.uniform(1.5, 4.0), 2)
                    fav = "1st"
                elif pos <= 3:  # Other fancied horses
                    odds_decimal = round(random.uniform(3.0, 8.0), 2)
                    fav = f"{pos}nd" if pos == 2 else f"{pos}rd"
                else:
                    odds_decimal = round(random.uniform(6.0, 50.0), 2)
                    fav = None

                # Convert to fractional odds for display
                if odds_decimal <= 2.0:
                    odds_frac = f"{int((odds_decimal-1)*10)}/10"
                elif odds_decimal <= 3.0:
                    odds_frac = f"{int((odds_decimal-1)*4)}/4"
                else:
                    odds_frac = f"{int(odds_decimal-1)}/1"

                # Weight in stones and pounds
                weight_stones = random.randint(8, 12)
                weight_pounds = random.randint(0, 13)
                weight_uk = f"{weight_stones}-{weight_pounds}"
                weight_kg = round(weight_stones * 6.35 + weight_pounds * 0.45, 2)

                racecard_detail = {
                    "race_id": race.race_id,
                    "horse_number": str(pos),
                    "draw": pos if race.race_type == "Flat" else None,
                    "horse_id": horse.horse_id,
                    "country": horse.country,
                    "name": horse.name,
                    "age": horse.age,
                    "weight_uk": weight_uk,
                    "weight": weight_kg,
                    "gears": random.choice(["b", "p", "t", "h", "v", "NULL"]),
                    "horse_rate": (
                        str(random.randint(40, 120)) if random.random() > 0.1 else "-"
                    ),
                    "jockey_id": jockey.jockey_id,
                    "jockey": jockey.name,
                    "trainer_id": trainer.trainer_id,
                    "trainer": trainer.name,
                    "fav": fav,
                    "odds": odds_frac,
                    "odds_decimal": odds_decimal,
                    "timeform_comments": f"Form comment for {horse.name} in this race.",
                }
                racecard_data.append(racecard_detail)

            # Generate race results (first 4 places)
            finishing_order = list(range(1, min(race.runners + 1, 5)))
            random.shuffle(finishing_order)

            for place, horse_num in enumerate(finishing_order[:4], 1):
                if horse_num <= len(race_horses):
                    horse = race_horses[horse_num - 1]
                    jockey = next(
                        (
                            rd["jockey"]
                            for rd in racecard_data
                            if rd["race_id"] == race.race_id
                            and rd["horse_id"] == horse.horse_id
                        ),
                        "Unknown Jockey",
                    )
                    trainer = next(
                        (
                            rd["trainer"]
                            for rd in racecard_data
                            if rd["race_id"] == race.race_id
                            and rd["horse_id"] == horse.horse_id
                        ),
                        "Unknown Trainer",
                    )

                    # Generate race time and margins
                    if place == 1:
                        time_str = f"{random.randint(60, 180)}.{random.randint(10, 99)}"
                        margin = "Won"
                        prize_amount = "£" + f"{random.randint(5000, 50000):,}"
                    else:
                        margin_lengths = [
                            f"{random.randint(1, 10)}l",
                            f"{random.randint(1, 5)}¼l",
                            f"{random.randint(1, 3)}½l",
                            "nk",
                            "shd",
                            "hd",
                        ]
                        margin = random.choice(margin_lengths)
                        time_str = ""
                        prize_amount = "£" + f"{random.randint(500, 5000):,}"

                    result = {
                        "race_id": race.race_id,
                        "place": place,
                        "horse_number": str(horse_num),
                        "name": horse.name,
                        "age": horse.age,
                        "weight": next(
                            (
                                rd["weight_uk"]
                                for rd in racecard_data
                                if rd["race_id"] == race.race_id
                                and rd["horse_id"] == horse.horse_id
                            ),
                            "9-0",
                        ),
                        "jockey": jockey,
                        "trainer": trainer,
                        "odds": next(
                            (
                                rd["odds"]
                                for rd in racecard_data
                                if rd["race_id"] == race.race_id
                                and rd["horse_id"] == horse.horse_id
                            ),
                            "10/1",
                        ),
                        "time": time_str,
                        "margin": margin,
                        "prize_money": prize_amount,
                    }
                    records_data.append(result)

            if (race_idx + 1) % 1000 == 0:
                logger.info(
                    f"   Generated participants for {race_idx + 1}/{len(races)} races..."
                )

        # Insert the data
        self.insert_data_batch("racecard_details", racecard_data)
        self.insert_data_batch("records", records_data)

    def clear_existing_data(self):
        """Clear all existing data from tables"""
        logger.info("🧹 Clearing existing test data...")

        tables = [
            "records",
            "racecard_details",
            "trainers_stats",
            "jockeys_stats",
            "horses_results",
            "horses_cards",
            "races_results",
            "races_cards",
        ]

        try:
            with self.connection.cursor() as cursor:
                for table in tables:
                    cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
            self.connection.commit()
            logger.info("✅ Existing data cleared successfully")
        except Exception as e:
            logger.error(f"❌ Failed to clear data: {e}")
            self.connection.rollback()
            raise

    def generate_all_data(self):
        """Generate complete test dataset"""
        logger.info("🚀 Starting massive test data generation...")
        logger.info(
            f"📊 Target: {self.total_races:,} races, {self.horses_count:,} horses, {self.jockeys_count} jockeys, {self.trainers_count} trainers"
        )

        start_time = datetime.now()

        try:
            # Connect and setup
            self.connect_database()
            self.create_database_schema()
            self.clear_existing_data()

            # Generate core entities
            horses = self.generate_horses()
            jockeys = self.generate_jockeys()
            trainers = self.generate_trainers()
            races = self.generate_races()

            # Convert to dict format for database insertion
            horses_dict = [
                {
                    "name": h.name,
                    "country": h.country,
                    "age": h.age,
                    "color": h.color,
                    "owner": h.owner,
                    "sire": h.sire,
                    "dam": h.dam,
                    "sex": h.sex,
                    "total_races": h.total_races,
                    "wins": h.wins,
                    "percentage_wins": h.percentage_wins,
                    "placed": h.placed,
                    "percentage_placed": h.percentage_placed,
                    "flat_turf_races": h.flat_turf_races,
                    "flat_turf_wins": h.flat_turf_wins,
                    "flat_turf_rate": h.flat_turf_rate,
                }
                for h in horses
            ]

            jockeys_dict = [
                {
                    "name": j.name,
                    "country": j.country,
                    "total_races": j.total_races,
                    "wins": j.wins,
                    "percentage_wins": j.percentage_wins,
                    "placed": j.placed,
                    "percentage_placed": j.percentage_placed,
                }
                for j in jockeys
            ]

            trainers_dict = [
                {
                    "name": t.name,
                    "country": t.country,
                    "location": t.location,
                    "total_races": t.total_races,
                    "wins": t.wins,
                    "percentage_wins": t.percentage_wins,
                    "placed": t.placed,
                    "percentage_placed": t.percentage_placed,
                }
                for t in trainers
            ]

            races_cards_dict = [
                {
                    "race_number": r.race_number,
                    "race_time": r.race_time,
                    "course": r.course,
                    "race_type": r.race_type,
                    "date": r.date,
                    "race_name": r.race_name,
                    "class": r.class_level,
                    "years": r.years,
                    "distance": r.distance,
                    "surface": r.surface,
                    "prize": r.prize,
                    "runners_racecard": r.runners_racecard,
                    "runners": r.runners,
                    "draw": r.draw,
                }
                for r in races
            ]

            races_results_dict = [
                {
                    "race_number": r.race_number,
                    "race_time": r.race_time,
                    "course": r.course,
                    "race_type": r.race_type,
                    "date": r.date,
                    "race_name": r.race_name,
                    "class": r.class_level,
                    "years": r.years,
                    "distance": r.distance,
                    "surface": r.surface,
                    "prize": r.prize,
                    "runners_racecard": r.runners_racecard,
                    "runners": r.runners,
                }
                for r in races
            ]

            # Insert core data
            self.insert_data_batch("horses_cards", horses_dict)
            self.insert_data_batch(
                "horses_results", horses_dict
            )  # Duplicate for results table
            self.insert_data_batch("jockeys_stats", jockeys_dict)
            self.insert_data_batch("trainers_stats", trainers_dict)
            self.insert_data_batch("races_cards", races_cards_dict)
            self.insert_data_batch(
                "races_results", races_results_dict
            )  # Without draw column

            # Generate race participants and results
            self.generate_race_participants(races, horses, jockeys, trainers)

            # Final statistics
            end_time = datetime.now()
            duration = end_time - start_time

            logger.info("🎉 MASSIVE TEST DATA GENERATION COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"📊 Generated Data Summary:")
            logger.info(f"   🏁 Races: {len(races):,}")
            logger.info(f"   🐎 Horses: {len(horses):,}")
            logger.info(f"   🏇 Jockeys: {len(jockeys):,}")
            logger.info(f"   👨‍🏫 Trainers: {len(trainers):,}")
            logger.info(f"   📝 Race entries: ~{len(races) * 12:,}")
            logger.info(f"   🏆 Race results: ~{len(races) * 4:,}")
            logger.info(f"⏱️ Generation time: {duration}")
            logger.info(f"🎯 Test database ready for comprehensive testing!")

        except Exception as e:
            logger.error(f"❌ Data generation failed: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate massive test data for Horse Racing AI"
    )
    parser.add_argument(
        "--races", type=int, default=50000, help="Number of races to generate"
    )
    parser.add_argument("--database-url", type=str, help="Test database URL")
    parser.add_argument(
        "--quick", action="store_true", help="Quick test with 1000 races"
    )

    args = parser.parse_args()

    if args.quick:
        args.races = 1000
        logger.info("🚀 Quick test mode: 1000 races")

    # Initialize generator
    generator = TestDataGenerator(args.database_url)
    if args.races != 50000:
        generator.total_races = args.races
        generator.horses_count = min(args.races, 15000)

    # Generate all data
    generator.generate_all_data()


if __name__ == "__main__":
    main()
