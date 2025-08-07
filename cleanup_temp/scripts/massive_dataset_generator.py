#!/usr/bin/env python3
"""
Massive Horse Racing Dataset Generator
Creates a large, realistic dataset for ML training with proper relationships and patterns
"""

import os
import sys
import random
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")


class MassiveDatasetGenerator:
    def __init__(self, db_path: str = "massive_racing_data.db"):
        self.db_path = db_path
        self.conn = None

        # UK/Ireland horse racing venues
        self.venues = [
            "Ascot",
            "Newmarket",
            "Cheltenham",
            "Epsom Downs",
            "York",
            "Goodwood",
            "Sandown Park",
            "Kempton Park",
            "Windsor",
            "Bath",
            "Brighton",
            "Carlisle",
            "Catterick",
            "Chester",
            "Doncaster",
            "Fakenham",
            "Fontwell Park",
            "Haydock Park",
            "Hexham",
            "Huntingdon",
            "Leicester",
            "Lingfield Park",
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
            "Sedgefield",
            "Southwell",
            "Stratford-upon-Avon",
            "Taunton",
            "Thirsk",
            "Uttoxeter",
            "Warwick",
            "Wetherby",
            "Wincanton",
            "Wolverhampton",
            "Worcester",
            "Yarmouth",
            "Aintree",
            "Bangor-on-Dee",
            "Chepstow",
            "Exeter",
            "Ffos Las",
            "Hereford",
            "Kelso",
            "Musselburgh",
            "Perth",
            "Ayr",
            "Hamilton Park",
            "Beverley",
            "Chepstow",
            "Cork",
            "Curragh",
            "Down Royal",
            "Downpatrick",
            "Dundalk",
            "Fairyhouse",
            "Galway",
            "Gowran Park",
            "Kilbeggan",
            "Killarney",
            "Laytown",
            "Leopardstown",
            "Limerick",
            "Listowel",
            "Naas",
            "Navan",
            "Punchestown",
            "Roscommon",
            "Sligo",
            "Thurles",
            "Tipperary",
            "Tramore",
            "Wexford",
            "Clonmel",
            "Bellewstown",
        ]

        # Race types with realistic distributions
        self.race_types = {
            "Maiden Stakes": 0.25,
            "Handicap Stakes": 0.30,
            "Novice Stakes": 0.15,
            "Selling Stakes": 0.10,
            "Claiming Stakes": 0.08,
            "Listed Stakes": 0.06,
            "Group 3 Stakes": 0.03,
            "Group 2 Stakes": 0.02,
            "Group 1 Stakes": 0.01,
        }

        # Distance ranges (in meters)
        self.distances = {
            "sprint": (1000, 1400),
            "mile": (1400, 1800),
            "middle": (1800, 2400),
            "staying": (2400, 3200),
            "extreme": (3200, 4800),
        }

        # Track conditions
        self.track_conditions = [
            "Firm",
            "Good to Firm",
            "Good",
            "Good to Soft",
            "Soft",
            "Heavy",
        ]

        # Weather conditions
        self.weather_conditions = [
            "Sunny",
            "Cloudy",
            "Overcast",
            "Light Rain",
            "Heavy Rain",
            "Windy",
        ]

        # Market simulation parameters
        self.market_types = {
            "win": {"liquidity_factor": 1.0, "overround": 1.15},
            "place": {"liquidity_factor": 0.6, "overround": 1.25},
            "each_way": {"liquidity_factor": 0.8, "overround": 1.20},
            "forecast": {"liquidity_factor": 0.3, "overround": 1.35},
            "tricast": {"liquidity_factor": 0.1, "overround": 1.50},
        }

        self.bookmakers = [
            "Bet365",
            "Ladbrokes",
            "William Hill",
            "Paddy Power",
            "Betfair",
            "Sky Bet",
            "Coral",
            "Betfred",
            "888sport",
        ]

        # Generate realistic horse names
        self.horse_prefixes = [
            "Thunder",
            "Lightning",
            "Storm",
            "Fire",
            "Golden",
            "Silver",
            "Diamond",
            "Royal",
            "Noble",
            "Brave",
            "Swift",
            "Fast",
            "Strong",
            "Mighty",
            "Bold",
            "Bright",
            "Star",
            "Moon",
            "Sun",
            "Wind",
            "River",
            "Mountain",
            "Valley",
            "Ocean",
            "Desert",
            "Forest",
            "Sky",
            "Cloud",
            "Rain",
            "Snow",
            "Ice",
            "Steel",
            "Iron",
            "Bronze",
            "Copper",
            "Jade",
            "Ruby",
            "Emerald",
            "Sapphire",
            "Pearl",
            "Tiger",
            "Lion",
            "Eagle",
            "Falcon",
            "Wolf",
            "Bear",
            "Fox",
            "Deer",
            "Horse",
            "Dragon",
            "Phoenix",
            "Griffin",
            "Unicorn",
            "Pegasus",
            "Spirit",
            "Shadow",
        ]

        self.horse_suffixes = [
            "Runner",
            "Dancer",
            "Fighter",
            "Winner",
            "Champion",
            "King",
            "Queen",
            "Prince",
            "Princess",
            "Lord",
            "Lady",
            "Duke",
            "Duchess",
            "Knight",
            "Warrior",
            "Hero",
            "Legend",
            "Star",
            "Comet",
            "Meteor",
            "Blaze",
            "Flash",
            "Bolt",
            "Arrow",
            "Sword",
            "Shield",
            "Crown",
            "Jewel",
            "Treasure",
            "Dream",
            "Hope",
            "Faith",
            "Glory",
            "Victory",
            "Triumph",
            "Success",
            "Fortune",
            "Luck",
            "Chance",
            "Destiny",
            "Magic",
            "Wonder",
            "Mystery",
            "Secret",
            "Quest",
            "Journey",
            "Adventure",
            "Explorer",
        ]

        # Jockey names
        self.jockey_names = [
            "James Doyle",
            "Ryan Moore",
            "William Buick",
            "Andrea Atzeni",
            "Jim Crowley",
            "Oisin Murphy",
            "Tom Marquand",
            "Hollie Doyle",
            "Frankie Dettori",
            "Pat Dobbs",
            "Jamie Spencer",
            "David Probert",
            "Silvestre de Sousa",
            "Daniel Tudhope",
            "Paul Hanagan",
            "Richard Kingscote",
            "Ben Curtis",
            "Clifford Lee",
            "Kevin Stott",
            "Connor Beasley",
            "Sean Levey",
            "Marco Ghiani",
            "Josephine Gordon",
            "Georgia Dobie",
            "Laura Pearson",
            "Nicola Currie",
            "Hayley Turner",
            "Emma-Jayne Wilson",
            "Saffie Osborne",
            "Billy Loughnane",
            "Jason Hart",
            "Callum Rodriguez",
            "Frederick Larson",
            "Lewis Edmunds",
            "Robert Havlin",
            "Charles Bishop",
            "Rossa Ryan",
            "Cieren Fallon",
            "Luke Morris",
            "Adam Kirby",
            "Neil Callan",
            "Jack Mitchell",
            "Shane Kelly",
            "David Egan",
        ]

        # Trainer names
        self.trainer_names = [
            "Aidan O'Brien",
            "John Gosden",
            "Charlie Appleby",
            "William Haggas",
            "Roger Varian",
            "Mark Johnston",
            "Andrew Balding",
            "Ralph Beckett",
            "Hugo Palmer",
            "Ed Walker",
            "Richard Hannon",
            "Simon Crisford",
            "Martyn Meade",
            "James Fanshawe",
            "Marcus Tregoning",
            "Michael Bell",
            "Eve Johnson Houghton",
            "Alan King",
            "Paul Nicholls",
            "Nicky Henderson",
            "Willie Mullins",
            "Gordon Elliott",
            "Henry de Bromhead",
            "Joseph O'Brien",
            "Jessica Harrington",
            "Gavin Cromwell",
            "Emmet Mullins",
            "Peter Fahey",
            "Tony Martin",
            "Shark Hanlon",
            "Michael O'Callaghan",
            "Pat Kelly",
            "Ado McGuinness",
            "Paddy Twomey",
            "Johnny Murtagh",
            "Dermot Weld",
            "Jim Bolger",
            "Kevin Prendergast",
            "Fozzy Stack",
            "Tracey Collins",
        ]

    def connect_db(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        logger.info(f"Connected to database: {self.db_path}")

    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Venues table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                location TEXT,
                track_type TEXT,
                left_right_handed TEXT
            )
        """
        )

        # Race cards table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS race_cards (
                race_id INTEGER PRIMARY KEY,
                date TEXT,
                venue_id INTEGER,
                race_number INTEGER,
                race_time TEXT,
                race_name TEXT,
                race_type TEXT,
                distance_meters INTEGER,
                track_condition TEXT,
                weather TEXT,
                prize_money INTEGER,
                num_runners INTEGER,
                FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
            )
        """
        )

        # Horses table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS horses (
                horse_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                age INTEGER,
                sex TEXT,
                rating INTEGER,
                form_rating REAL,
                career_wins INTEGER,
                career_runs INTEGER,
                earnings INTEGER
            )
        """
        )

        # Jockeys table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jockeys (
                jockey_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                skill_rating REAL,
                experience_years INTEGER,
                career_wins INTEGER,
                win_percentage REAL
            )
        """
        )

        # Trainers table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trainers (
                trainer_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                skill_rating REAL,
                stable_size INTEGER,
                career_wins INTEGER,
                win_percentage REAL
            )
        """
        )

        # Race participants table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS race_participants (
                participant_id INTEGER PRIMARY KEY,
                race_id INTEGER,
                horse_id INTEGER,
                jockey_id INTEGER,
                trainer_id INTEGER,
                draw INTEGER,
                weight_lbs INTEGER,
                odds_decimal REAL,
                form_string TEXT,
                days_since_last_run INTEGER,
                course_and_distance_wins INTEGER,
                course_wins INTEGER,
                distance_wins INTEGER,
                actual_finish_position INTEGER,
                FOREIGN KEY (race_id) REFERENCES race_cards (race_id),
                FOREIGN KEY (horse_id) REFERENCES horses (horse_id),
                FOREIGN KEY (jockey_id) REFERENCES jockeys (jockey_id),
                FOREIGN KEY (trainer_id) REFERENCES trainers (trainer_id)
            )
        """
        )

        # Market simulation tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS betting_markets (
                market_id INTEGER PRIMARY KEY,
                race_id INTEGER,
                market_type TEXT,
                total_matched REAL,
                overround REAL,
                market_timestamp TEXT,
                market_status TEXT,
                FOREIGN KEY (race_id) REFERENCES race_cards (race_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_odds (
                odds_id INTEGER PRIMARY KEY,
                market_id INTEGER,
                participant_id INTEGER,
                bookmaker TEXT,
                back_odds REAL,
                lay_odds REAL,
                back_size REAL,
                lay_size REAL,
                timestamp TEXT,
                FOREIGN KEY (market_id) REFERENCES betting_markets (market_id),
                FOREIGN KEY (participant_id) REFERENCES race_participants (participant_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS simulated_trades (
                trade_id INTEGER PRIMARY KEY,
                market_id INTEGER,
                participant_id INTEGER,
                trade_type TEXT,
                odds REAL,
                stake REAL,
                timestamp TEXT,
                profit_loss REAL,
                commission REAL,
                FOREIGN KEY (market_id) REFERENCES betting_markets (market_id),
                FOREIGN KEY (participant_id) REFERENCES race_participants (participant_id)
            )
        """
        )

        self.conn.commit()
        logger.info("Database tables created successfully")

    def generate_venues(self):
        """Generate venue data"""
        cursor = self.conn.cursor()

        for i, venue in enumerate(self.venues):
            # Assign random properties
            locations = ["England", "Ireland", "Scotland", "Wales"]
            track_types = ["Flat", "National Hunt", "All Weather"]
            handedness = ["Left", "Right", "Straight"]

            cursor.execute(
                """
                INSERT OR IGNORE INTO venues (name, location, track_type, left_right_handed)
                VALUES (?, ?, ?, ?)
            """,
                (
                    venue,
                    random.choice(locations),
                    random.choice(track_types),
                    random.choice(handedness),
                ),
            )

        self.conn.commit()
        logger.info(f"Generated {len(self.venues)} venues")

    def generate_horses(self, num_horses: int = 5000):
        """Generate horse data"""
        cursor = self.conn.cursor()

        for i in range(num_horses):
            # Generate realistic horse name
            prefix = random.choice(self.horse_prefixes)
            suffix = random.choice(self.horse_suffixes)
            name = f"{prefix} {suffix}"

            # Add number if name might be duplicate
            if random.random() < 0.3:
                name += f" {random.randint(1, 99)}"

            # Generate horse characteristics
            age = random.choices(
                [2, 3, 4, 5, 6, 7, 8, 9, 10],
                weights=[0.15, 0.25, 0.20, 0.15, 0.10, 0.08, 0.04, 0.02, 0.01],
            )[0]
            sex = random.choices(
                ["Colt", "Filly", "Gelding", "Mare", "Stallion"],
                weights=[0.25, 0.25, 0.30, 0.15, 0.05],
            )[0]

            # Rating based on age and career performance
            base_rating = random.normalvariate(75, 15)
            if age == 2:
                base_rating *= 0.9  # Younger horses typically lower rated
            elif age >= 8:
                base_rating *= 0.85  # Older horses might be declining

            rating = max(40, min(130, int(base_rating)))

            # Form rating correlated with official rating
            form_rating = rating + random.normalvariate(0, 5)
            form_rating = max(30, min(140, form_rating))

            # Career statistics based on age and ability
            career_runs = max(1, int(np.random.exponential(age * 3)))
            win_probability = min(0.4, max(0.05, (rating - 60) / 100))
            career_wins = np.random.binomial(career_runs, win_probability)

            # Earnings based on wins and rating
            base_earnings = career_wins * random.randint(5000, 50000)
            if rating > 100:  # High-class horses earn more
                base_earnings *= random.uniform(2, 5)
            earnings = int(base_earnings)

            cursor.execute(
                """
                INSERT OR IGNORE INTO horses 
                (name, age, sex, rating, form_rating, career_wins, career_runs, earnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    age,
                    sex,
                    rating,
                    form_rating,
                    career_wins,
                    career_runs,
                    earnings,
                ),
            )

        self.conn.commit()
        logger.info(f"Generated {num_horses} horses")

    def generate_jockeys(self):
        """Generate jockey data"""
        cursor = self.conn.cursor()

        for jockey in self.jockey_names:
            # Generate jockey characteristics
            experience_years = random.randint(3, 30)
            skill_rating = random.normalvariate(75, 12)
            skill_rating = max(50, min(95, skill_rating))

            # Career statistics based on experience and skill
            career_wins = int(experience_years * random.uniform(20, 150))
            total_rides = int(career_wins / random.uniform(0.08, 0.25))
            win_percentage = (career_wins / total_rides) * 100 if total_rides > 0 else 0

            cursor.execute(
                """
                INSERT OR IGNORE INTO jockeys 
                (name, skill_rating, experience_years, career_wins, win_percentage)
                VALUES (?, ?, ?, ?, ?)
            """,
                (jockey, skill_rating, experience_years, career_wins, win_percentage),
            )

        self.conn.commit()
        logger.info(f"Generated {len(self.jockey_names)} jockeys")

    def generate_trainers(self):
        """Generate trainer data"""
        cursor = self.conn.cursor()

        for trainer in self.trainer_names:
            # Generate trainer characteristics
            stable_size = random.randint(15, 200)
            skill_rating = random.normalvariate(75, 10)
            skill_rating = max(60, min(95, skill_rating))

            # Career statistics based on stable size and skill
            years_training = random.randint(5, 40)
            career_wins = int(years_training * stable_size * random.uniform(0.1, 0.4))
            total_runners = int(career_wins / random.uniform(0.12, 0.28))
            win_percentage = (
                (career_wins / total_runners) * 100 if total_runners > 0 else 0
            )

            cursor.execute(
                """
                INSERT OR IGNORE INTO trainers 
                (name, skill_rating, stable_size, career_wins, win_percentage)
                VALUES (?, ?, ?, ?, ?)
            """,
                (trainer, skill_rating, stable_size, career_wins, win_percentage),
            )

        self.conn.commit()
        logger.info(f"Generated {len(self.trainer_names)} trainers")

    def generate_race_cards(self, start_date: str = "2024-01-01", num_days: int = 365):
        """Generate race cards for specified period"""
        cursor = self.conn.cursor()

        # Get venue IDs
        cursor.execute("SELECT venue_id FROM venues")
        venue_ids = [row[0] for row in cursor.fetchall()]

        # Get next available race_id
        cursor.execute("SELECT COALESCE(MAX(race_id), 0) FROM race_cards")
        race_id = cursor.fetchone()[0] + 1

        current_date = datetime.strptime(start_date, "%Y-%m-%d")

        for day in range(num_days):
            date_str = current_date.strftime("%Y-%m-%d")

            # Number of race meetings per day (realistic distribution)
            num_meetings = random.choices(
                [0, 1, 2, 3, 4, 5], weights=[0.1, 0.3, 0.35, 0.15, 0.08, 0.02]
            )[0]

            selected_venues = random.sample(
                venue_ids, min(num_meetings, len(venue_ids))
            )

            for venue_id in selected_venues:
                # Number of races per meeting
                num_races = random.choices(
                    [4, 5, 6, 7, 8], weights=[0.1, 0.2, 0.4, 0.25, 0.05]
                )[0]

                for race_num in range(1, num_races + 1):
                    # Generate race time
                    start_hour = random.randint(13, 17)
                    start_minute = random.choice([0, 15, 30, 45])
                    race_time = f"{start_hour:02d}:{start_minute:02d}"

                    # Select race type
                    race_type = random.choices(
                        list(self.race_types.keys()),
                        weights=list(self.race_types.values()),
                    )[0]

                    # Generate race name
                    venue_name = self.venues[venue_id - 1]
                    race_name = f"{venue_name} {race_type}"

                    # Select distance
                    distance_category = random.choices(
                        ["sprint", "mile", "middle", "staying", "extreme"],
                        weights=[0.35, 0.30, 0.20, 0.12, 0.03],
                    )[0]
                    distance_range = self.distances[distance_category]
                    distance = random.randint(distance_range[0], distance_range[1])

                    # Track and weather conditions
                    track_condition = random.choices(
                        self.track_conditions,
                        weights=[0.25, 0.25, 0.25, 0.15, 0.08, 0.02],
                    )[0]
                    weather = random.choice(self.weather_conditions)

                    # Prize money based on race type
                    base_prize = {
                        "Group 1 Stakes": random.randint(200000, 1000000),
                        "Group 2 Stakes": random.randint(100000, 300000),
                        "Group 3 Stakes": random.randint(50000, 150000),
                        "Listed Stakes": random.randint(25000, 80000),
                        "Handicap Stakes": random.randint(8000, 40000),
                        "Maiden Stakes": random.randint(5000, 20000),
                        "Novice Stakes": random.randint(5000, 15000),
                        "Claiming Stakes": random.randint(3000, 12000),
                        "Selling Stakes": random.randint(2000, 8000),
                    }
                    prize_money = base_prize.get(race_type, 10000)

                    # Number of runners
                    num_runners = random.choices(
                        [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                        weights=[
                            0.05,
                            0.08,
                            0.12,
                            0.15,
                            0.18,
                            0.15,
                            0.12,
                            0.08,
                            0.04,
                            0.02,
                            0.01,
                        ],
                    )[0]

                    cursor.execute(
                        """
                        INSERT INTO race_cards 
                        (race_id, date, venue_id, race_number, race_time, race_name, race_type, 
                         distance_meters, track_condition, weather, prize_money, num_runners)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            race_id,
                            date_str,
                            venue_id,
                            race_num,
                            race_time,
                            race_name,
                            race_type,
                            distance,
                            track_condition,
                            weather,
                            prize_money,
                            num_runners,
                        ),
                    )

                    race_id += 1

            current_date += timedelta(days=1)

            # Progress update
            if day % 30 == 0:
                logger.info(f"Generated race cards for {day + 1} days")

        self.conn.commit()
        logger.info(f"Generated race cards for {num_days} days")

    def generate_race_participants(self):
        """Generate race participants with realistic relationships"""
        cursor = self.conn.cursor()

        # Get all race cards
        cursor.execute(
            "SELECT race_id, num_runners, distance_meters, race_type FROM race_cards"
        )
        races = cursor.fetchall()

        # Get all horses, jockeys, trainers
        cursor.execute("SELECT horse_id, rating, age FROM horses")
        horses = cursor.fetchall()

        cursor.execute("SELECT jockey_id, skill_rating FROM jockeys")
        jockeys = cursor.fetchall()

        cursor.execute("SELECT trainer_id, skill_rating FROM trainers")
        trainers = cursor.fetchall()

        # Get next available participant_id
        cursor.execute("SELECT COALESCE(MAX(participant_id), 0) FROM race_participants")
        participant_id = cursor.fetchone()[0] + 1

        for race_id, num_runners, distance, race_type in races:
            # Select horses for this race based on ratings and race class
            race_class_factor = {
                "Group 1 Stakes": (100, 130),
                "Group 2 Stakes": (95, 125),
                "Group 3 Stakes": (90, 120),
                "Listed Stakes": (85, 115),
                "Handicap Stakes": (60, 110),
                "Maiden Stakes": (50, 90),
                "Novice Stakes": (55, 95),
                "Claiming Stakes": (45, 85),
                "Selling Stakes": (40, 80),
            }

            rating_range = race_class_factor.get(race_type, (50, 100))
            suitable_horses = [
                h for h in horses if rating_range[0] <= h[1] <= rating_range[1]
            ]

            if len(suitable_horses) < num_runners:
                # Expand range if not enough horses
                suitable_horses = horses

            selected_horses = random.sample(
                suitable_horses, min(num_runners, len(suitable_horses))
            )

            # Generate odds based on ratings
            ratings = [h[1] for h in selected_horses]
            max_rating = max(ratings)

            for i, (horse_id, rating, age) in enumerate(selected_horses):
                # Select jockey and trainer
                jockey_id, jockey_skill = random.choice(jockeys)
                trainer_id, trainer_skill = random.choice(trainers)

                # Draw position
                draw = i + 1

                # Weight calculation
                if "Handicap" in race_type:
                    # Handicap: higher rated horses carry more weight
                    base_weight = 126 + (rating - 75)  # Pounds
                else:
                    # Level weights with allowances
                    base_weight = random.randint(118, 126)
                    if age == 2:
                        base_weight -= 7  # 2-year-old allowance
                    elif age == 3:
                        base_weight -= 3  # 3-year-old allowance

                weight = max(110, min(140, base_weight))

                # Calculate competitive rating
                competitive_rating = (
                    rating
                    + jockey_skill / 10
                    + trainer_skill / 10
                    + random.normalvariate(0, 3)
                )

                # Generate odds based on competitive rating
                rating_diff = (
                    max_rating - competitive_rating + 10
                )  # Add base to avoid negative
                raw_odds = 1 + (rating_diff / 5)  # Basic odds calculation

                # Add randomness and market inefficiencies
                odds_multiplier = random.uniform(0.7, 1.4)
                odds_decimal = max(1.1, raw_odds * odds_multiplier)

                # Generate form string
                form_chars = [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "0",
                    "F",
                    "U",
                    "P",
                ]
                form_weights = [
                    0.15,
                    0.12,
                    0.10,
                    0.08,
                    0.07,
                    0.06,
                    0.05,
                    0.04,
                    0.03,
                    0.15,
                    0.05,
                    0.05,
                    0.05,
                ]
                form_length = random.randint(3, 8)
                form_string = "".join(
                    random.choices(form_chars, weights=form_weights, k=form_length)
                )

                # Days since last run
                days_since_last_run = random.choices(
                    [7, 14, 21, 28, 35, 42, 56, 70, 84, 98, 112, 150, 200],
                    weights=[
                        0.05,
                        0.15,
                        0.20,
                        0.15,
                        0.12,
                        0.10,
                        0.08,
                        0.06,
                        0.04,
                        0.02,
                        0.02,
                        0.01,
                        0.01,
                    ],
                )[0]

                # Course and distance statistics (realistic but varied)
                course_wins = random.randint(0, min(3, rating // 30))
                distance_wins = random.randint(0, min(4, rating // 25))
                course_distance_wins = random.randint(
                    0, min(course_wins, distance_wins)
                )

                # Simulate race result based on competitive rating
                finish_position = self._simulate_race_result(
                    competitive_rating, selected_horses, i
                )

                cursor.execute(
                    """
                    INSERT INTO race_participants 
                    (participant_id, race_id, horse_id, jockey_id, trainer_id, draw, weight_lbs,
                     odds_decimal, form_string, days_since_last_run, course_and_distance_wins,
                     course_wins, distance_wins, actual_finish_position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        participant_id,
                        race_id,
                        horse_id,
                        jockey_id,
                        trainer_id,
                        draw,
                        weight,
                        odds_decimal,
                        form_string,
                        days_since_last_run,
                        course_distance_wins,
                        course_wins,
                        distance_wins,
                        finish_position,
                    ),
                )

                participant_id += 1

            # Progress update
            if race_id % 100 == 0:
                logger.info(f"Generated participants for {race_id} races")

        self.conn.commit()
        logger.info(f"Generated race participants for all races")

    def _simulate_race_result(
        self, competitive_rating: float, all_horses: List, horse_index: int
    ) -> int:
        """Simulate race result based on competitive ratings"""
        # Get all competitive ratings
        ratings = []
        for i, (horse_id, rating, age) in enumerate(all_horses):
            if i == horse_index:
                ratings.append(competitive_rating)
            else:
                # Estimate other horses' competitive ratings
                base_rating = rating + random.normalvariate(0, 5)
                ratings.append(base_rating)

        # Convert to probabilities (higher rating = better chance)
        max_rating = max(ratings)
        adjusted_ratings = [
            r - min(ratings) + 1 for r in ratings
        ]  # Ensure all positive
        probabilities = [r / sum(adjusted_ratings) for r in adjusted_ratings]

        # Add racing randomness
        race_randomness = [random.uniform(0.5, 1.5) for _ in ratings]
        final_scores = [p * r for p, r in zip(probabilities, race_randomness)]

        # Sort to get finishing positions
        indexed_scores = [(score, i) for i, score in enumerate(final_scores)]
        indexed_scores.sort(reverse=True)

        # Find position of our horse
        for position, (score, idx) in enumerate(indexed_scores):
            if idx == horse_index:
                return position + 1

        return len(all_horses)  # Fallback

    def simulate_betting_markets(self):
        """Simulate realistic betting markets for all races"""
        cursor = self.conn.cursor()

        # Get all races with participants
        cursor.execute(
            """
            SELECT DISTINCT rp.race_id, COUNT(*) as num_runners
            FROM race_participants rp
            GROUP BY rp.race_id
        """
        )
        races = cursor.fetchall()

        # Get next available IDs
        cursor.execute("SELECT COALESCE(MAX(market_id), 0) FROM betting_markets")
        market_id = cursor.fetchone()[0] + 1

        cursor.execute("SELECT COALESCE(MAX(odds_id), 0) FROM market_odds")
        odds_id = cursor.fetchone()[0] + 1

        cursor.execute("SELECT COALESCE(MAX(trade_id), 0) FROM simulated_trades")
        trade_id = cursor.fetchone()[0] + 1

        logger.info(f"Simulating markets for {len(races)} races...")

        for race_id, num_runners in races:
            # Get race participants
            cursor.execute(
                """
                SELECT participant_id, odds_decimal, actual_finish_position
                FROM race_participants
                WHERE race_id = ?
                ORDER BY odds_decimal
            """,
                (race_id,),
            )
            participants = cursor.fetchall()

            # Create markets for each type
            for market_type, config in self.market_types.items():
                # Calculate total matched based on race quality
                base_liquidity = random.uniform(10000, 100000)
                total_matched = base_liquidity * config["liquidity_factor"]

                # Market status
                market_status = "CLOSED"  # Since we have results

                # Create market
                cursor.execute(
                    """
                    INSERT INTO betting_markets
                    (market_id, race_id, market_type, total_matched, overround, market_timestamp, market_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        market_id,
                        race_id,
                        market_type,
                        total_matched,
                        config["overround"],
                        f"2024-01-01 12:00:00",  # Simplified timestamp
                        market_status,
                    ),
                )

                # Generate odds for each participant across multiple bookmakers
                for participant_id, base_odds, finish_pos in participants:
                    for bookmaker in self.bookmakers:
                        # Add bookmaker variation to odds
                        odds_variation = random.uniform(0.95, 1.05)
                        back_odds = base_odds * odds_variation

                        # Lay odds (exchange style)
                        lay_odds = back_odds * random.uniform(1.01, 1.03)

                        # Market depth
                        back_size = random.uniform(100, 5000)
                        lay_size = random.uniform(100, 3000)

                        cursor.execute(
                            """
                            INSERT INTO market_odds
                            (odds_id, market_id, participant_id, bookmaker, back_odds, lay_odds, back_size, lay_size, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                odds_id,
                                market_id,
                                participant_id,
                                bookmaker,
                                round(back_odds, 2),
                                round(lay_odds, 2),
                                round(back_size, 2),
                                round(lay_size, 2),
                                f"2024-01-01 12:00:00",
                            ),
                        )
                        odds_id += 1

                        # Simulate some trades
                        if random.random() < 0.3:  # 30% chance of trade
                            trade_type = random.choice(["BACK", "LAY"])
                            trade_odds = back_odds if trade_type == "BACK" else lay_odds
                            stake = random.uniform(10, 500)

                            # Calculate P&L based on actual result
                            if trade_type == "BACK":
                                profit_loss = (
                                    stake * (trade_odds - 1)
                                    if finish_pos == 1
                                    else -stake
                                )
                            else:  # LAY
                                profit_loss = (
                                    -stake * (trade_odds - 1)
                                    if finish_pos == 1
                                    else stake
                                )

                            commission = (
                                abs(profit_loss) * 0.05 if profit_loss > 0 else 0
                            )

                            cursor.execute(
                                """
                                INSERT INTO simulated_trades
                                (trade_id, market_id, participant_id, trade_type, odds, stake, timestamp, profit_loss, commission)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    trade_id,
                                    market_id,
                                    participant_id,
                                    trade_type,
                                    round(trade_odds, 2),
                                    round(stake, 2),
                                    f"2024-01-01 11:45:00",
                                    round(profit_loss, 2),
                                    round(commission, 2),
                                ),
                            )
                            trade_id += 1

                market_id += 1

            # Progress update
            if race_id % 100 == 0:
                logger.info(f"Simulated markets for {race_id} races")

        self.conn.commit()
        logger.info("Market simulation complete!")

    def _generate_contextual_factors(self, race_date, race_time, field_size):
        """Generate comprehensive contextual data for AI reward system."""

        # Parse date and time
        try:
            from datetime import datetime, date
            import calendar

            race_datetime = datetime.strptime(
                f"{race_date} {race_time}", "%Y-%m-%d %H:%M"
            )
        except:
            # Fallback for simulated data
            race_datetime = datetime.now()

        # Temporal factors
        day_of_week = race_datetime.weekday()  # 0=Monday, 6=Sunday
        week_of_year = race_datetime.isocalendar()[1]
        month = race_datetime.month

        # Season mapping
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"

        # Weekend/holiday detection
        is_weekend = 1 if day_of_week >= 5 else 0
        is_holiday = random.choice([0, 0, 0, 0, 1])  # 20% chance holiday

        # Time of day classification
        hour = race_datetime.hour
        if hour < 12:
            time_of_day = "Morning"
        elif hour < 17:
            time_of_day = "Afternoon"
        else:
            time_of_day = "Evening"

        # Field and competition dynamics
        competitive_rating = self._calculate_competitive_rating(field_size)

        # Market conditions
        market_volatility = random.uniform(0.1, 0.9)
        liquidity_quality_score = random.uniform(0.3, 1.0)

        # Weather and track conditions
        weather_impact_score = random.uniform(0.0, 0.8)
        track_bias_factor = random.uniform(-0.3, 0.3)

        # Media and attention factors
        media_attention_score = random.uniform(0.1, 0.7)
        if is_weekend or is_holiday:
            media_attention_score *= 1.3

        # Market patterns
        betting_patterns_unusual = random.choice([0, 0, 0, 1])
        steam_moves_detected = random.choice([0, 0, 0, 1])
        drift_detected = random.choice([0, 0, 0, 1])

        # Support patterns
        market_support_early = random.uniform(0.2, 0.9)
        market_support_late = random.uniform(0.2, 0.9)

        return {
            "day_of_week": day_of_week,
            "week_of_year": week_of_year,
            "month": month,
            "season": season,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "time_of_day": time_of_day,
            "competitive_rating": competitive_rating,
            "market_volatility": market_volatility,
            "weather_impact_score": weather_impact_score,
            "track_bias_factor": track_bias_factor,
            "media_attention_score": media_attention_score,
            "betting_patterns_unusual": betting_patterns_unusual,
            "steam_moves_detected": steam_moves_detected,
            "drift_detected": drift_detected,
            "market_support_early": market_support_early,
            "market_support_late": market_support_late,
            "liquidity_quality_score": liquidity_quality_score,
        }

    def _calculate_competitive_rating(self, field_size):
        """Calculate how competitive a race is based on field dynamics."""
        base_rating = min(field_size / 20.0, 1.0)  # Normalize to 1.0

        # Add variability based on field size sweet spots
        if 8 <= field_size <= 12:
            base_rating *= 1.1  # Optimal competitive field
        elif field_size < 6:
            base_rating *= 0.7  # Too small, less competitive
        elif field_size > 20:
            base_rating *= 0.8  # Too large, harder to assess

        return min(base_rating * random.uniform(0.8, 1.2), 1.0)

    def _generate_horse_specific_context(self, participant_id, race_context):
        """Generate horse-specific contextual factors."""

        # Trainer and jockey recent form
        trainer_recent_form = random.uniform(0.3, 0.9)
        jockey_recent_form = random.uniform(0.3, 0.9)

        # Stable confidence indicators
        stable_confidence = random.uniform(0.2, 0.8)
        stable_money_confidence = random.uniform(0.2, 0.8)

        # Equipment and changes
        equipment_change = random.choice([0, 0, 0, 1])  # 25% chance
        first_time_headgear = random.choice([0, 0, 0, 0, 1])  # 20% chance

        # Pace scenario context
        pace_scenarios = ["Strong Pace", "Moderate Pace", "Slow Pace", "Unknown"]
        pace_scenario = random.choice(pace_scenarios)

        # Class movement
        class_changes = ["Class Drop", "Class Rise", "Same Class", "Maiden"]
        class_drop_raise = random.choice(class_changes)

        # Performance impact factors
        distance_change_impact = random.uniform(-0.3, 0.3)
        weight_change_impact = random.uniform(-0.2, 0.2)

        # Connections significance
        connections_booking_significance = random.uniform(0.1, 0.8)

        return {
            "trainer_recent_form": trainer_recent_form,
            "jockey_recent_form": jockey_recent_form,
            "stable_confidence": stable_confidence,
            "stable_money_confidence": stable_money_confidence,
            "equipment_change": equipment_change,
            "first_time_headgear": first_time_headgear,
            "pace_scenario": pace_scenario,
            "class_drop_raise": class_drop_raise,
            "distance_change_impact": distance_change_impact,
            "weight_change_impact": weight_change_impact,
            "connections_booking_significance": connections_booking_significance,
        }

    def generate_ai_predictions(self):
        """Generate AI prediction data with betting strategy integration"""
        cursor = self.conn.cursor()

        # Get sample of races for prediction generation
        cursor.execute(
            """
            SELECT race_id FROM race_cards 
            ORDER BY RANDOM() 
            LIMIT 1000
        """
        )
        sample_races = cursor.fetchall()

        # Create comprehensive AI predictions table with enhanced contextual data
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_predictions (
                prediction_id INTEGER PRIMARY KEY,
                race_id INTEGER,
                participant_id INTEGER,
                predicted_probability REAL,
                confidence_score REAL,
                value_rating REAL,
                consensus_rating REAL,
                form_score REAL,
                pace_rating REAL,
                class_rating REAL,
                trainer_form REAL,
                jockey_form REAL,
                course_suitability REAL,
                distance_suitability REAL,
                going_suitability REAL,
                
                -- Enhanced contextual data for reward system
                day_of_week INTEGER,
                week_of_year INTEGER,
                month INTEGER,
                season TEXT,
                is_weekend INTEGER,
                is_holiday INTEGER,
                time_of_day TEXT,
                race_number_on_card INTEGER,
                total_races_on_card INTEGER,
                field_size INTEGER,
                competitive_rating REAL,
                market_volatility REAL,
                weather_impact_score REAL,
                track_bias_factor REAL,
                trainer_recent_form REAL,
                jockey_recent_form REAL,
                stable_confidence REAL,
                media_attention_score REAL,
                betting_patterns_unusual INTEGER,
                pace_scenario TEXT,
                class_drop_raise TEXT,
                distance_change_impact REAL,
                weight_change_impact REAL,
                equipment_change INTEGER,
                first_time_headgear INTEGER,
                connections_booking_significance REAL,
                stable_money_confidence REAL,
                market_support_early REAL,
                market_support_late REAL,
                steam_moves_detected INTEGER,
                drift_detected INTEGER,
                liquidity_quality_score REAL,
                
                prediction_timestamp TEXT,
                actual_result INTEGER,
                FOREIGN KEY (race_id) REFERENCES race_cards (race_id),
                FOREIGN KEY (participant_id) REFERENCES race_participants (participant_id)
            )
        """
        )

        # Create AI betting strategy recommendations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_betting_strategies (
                strategy_id INTEGER PRIMARY KEY,
                prediction_id INTEGER,
                race_id INTEGER,
                participant_id INTEGER,
                strategy_type TEXT,
                bet_type TEXT,
                recommended_stake REAL,
                recommended_odds REAL,
                kelly_fraction REAL,
                value_percentage REAL,
                confidence_threshold REAL,
                risk_rating TEXT,
                staking_method TEXT,
                dutching_group INTEGER,
                each_way_terms TEXT,
                twenty_eighty_allocation REAL,
                strategy_confidence REAL,
                expected_value REAL,
                bankroll_percentage REAL,
                max_loss REAL,
                profit_target REAL,
                FOREIGN KEY (prediction_id) REFERENCES ai_predictions (prediction_id),
                FOREIGN KEY (race_id) REFERENCES race_cards (race_id),
                FOREIGN KEY (participant_id) REFERENCES race_participants (participant_id)
            )
        """
        )

        # Get next available prediction_id
        cursor.execute("SELECT COALESCE(MAX(prediction_id), 0) FROM ai_predictions")
        prediction_id = cursor.fetchone()[0] + 1

        # Get next available strategy_id
        cursor.execute(
            "SELECT COALESCE(MAX(strategy_id), 0) FROM ai_betting_strategies"
        )
        strategy_id = cursor.fetchone()[0] + 1

        for (race_id,) in sample_races:
            # Get race details with additional context
            cursor.execute(
                """
                SELECT rc.race_type, rc.distance_meters, rc.track_condition, 
                       rc.weather, rc.post_time, rc.race_date,
                       (SELECT COUNT(*) FROM race_participants rp WHERE rp.race_id = rc.race_id) as field_size,
                       rc.race_number
                FROM race_cards rc
                WHERE rc.race_id = ?
            """,
                (race_id,),
            )
            race_details = cursor.fetchone()
            if not race_details:
                continue

            (
                race_type,
                distance,
                track_condition,
                weather,
                post_time,
                race_date,
                field_size,
                race_number,
            ) = race_details

            # Generate contextual factors for this race
            race_context = self._generate_contextual_factors(
                race_date, post_time, field_size
            )

            # Get participants for this race
            cursor.execute(
                """
                SELECT rp.participant_id, rp.odds_decimal, rp.actual_finish_position,
                       h.rating, h.age, h.form_rating, h.career_wins, h.career_runs,
                       j.skill_rating, j.win_percentage,
                       t.skill_rating, t.win_percentage
                FROM race_participants rp
                JOIN horses h ON rp.horse_id = h.horse_id
                JOIN jockeys j ON rp.jockey_id = j.jockey_id
                JOIN trainers t ON rp.trainer_id = t.trainer_id
                WHERE rp.race_id = ?
            """,
                (race_id,),
            )
            participants = cursor.fetchall()

            # Track value bets for dutching opportunities
            value_bets = []

            for participant_data in participants:
                (
                    participant_id,
                    odds,
                    finish_pos,
                    horse_rating,
                    age,
                    form_rating,
                    career_wins,
                    career_runs,
                    jockey_skill,
                    jockey_win_pct,
                    trainer_skill,
                    trainer_win_pct,
                ) = participant_data

                # Generate comprehensive AI analysis
                implied_prob = 1 / odds

                # Form analysis
                win_rate = career_wins / max(career_runs, 1)
                form_score = (form_rating / 100) * (1 + win_rate)

                # Pace and class ratings
                pace_rating = random.uniform(0.6, 0.95) * (horse_rating / 100)
                class_rating = min(1.0, horse_rating / 80)

                # Trainer and jockey form
                trainer_form = trainer_skill / 100
                jockey_form = jockey_skill / 100

                # Course and distance suitability
                distance_factor = 1.0
                if distance < 1400:  # Sprint
                    distance_factor = (
                        random.uniform(0.8, 1.0)
                        if age <= 5
                        else random.uniform(0.7, 0.9)
                    )
                elif distance > 2400:  # Staying
                    distance_factor = (
                        random.uniform(0.9, 1.0)
                        if age >= 4
                        else random.uniform(0.8, 0.9)
                    )

                course_suitability = random.uniform(0.8, 1.0)
                distance_suitability = distance_factor

                # Going suitability
                going_factor = 1.0
                if track_condition in ["Heavy", "Soft"]:
                    going_factor = random.uniform(0.8, 1.1)
                elif track_condition == "Firm":
                    going_factor = random.uniform(0.9, 1.05)

                going_suitability = going_factor

                # AI predicted probability combining all factors
                base_prob = implied_prob
                ai_adjustment = (
                    form_score * 0.25
                    + pace_rating * 0.2
                    + class_rating * 0.15
                    + trainer_form * 0.15
                    + jockey_form * 0.1
                    + course_suitability * 0.08
                    + distance_suitability * 0.05
                    + going_suitability * 0.02
                )

                predicted_prob = base_prob * ai_adjustment
                predicted_prob = max(0.01, min(0.99, predicted_prob))

                # AI confidence based on data quality
                confidence = min(
                    0.95,
                    (
                        0.6
                        + (career_runs / 50) * 0.1
                        + (jockey_skill / 100) * 0.1
                        + (trainer_skill / 100) * 0.1
                        + random.uniform(0, 0.05)
                    ),
                )

                # Value calculation
                fair_odds = 1 / predicted_prob
                value_percentage = (
                    ((fair_odds - odds) / odds) * 100 if fair_odds > odds else 0
                )

                # Consensus rating
                consensus_rating = random.uniform(50, 95)

                # Generate horse-specific contextual factors
                horse_context = self._generate_horse_specific_context(
                    participant_id, race_context
                )

                # Insert comprehensive AI prediction with full contextual data
                cursor.execute(
                    """
                    INSERT INTO ai_predictions
                    (prediction_id, race_id, participant_id, predicted_probability, 
                     confidence_score, value_rating, consensus_rating, form_score,
                     pace_rating, class_rating, trainer_form, jockey_form,
                     course_suitability, distance_suitability, going_suitability,
                     day_of_week, week_of_year, month, season, is_weekend, is_holiday,
                     time_of_day, race_number_on_card, total_races_on_card, field_size,
                     competitive_rating, market_volatility, weather_impact_score,
                     track_bias_factor, trainer_recent_form, jockey_recent_form,
                     stable_confidence, media_attention_score, betting_patterns_unusual,
                     pace_scenario, class_drop_raise, distance_change_impact,
                     weight_change_impact, equipment_change, first_time_headgear,
                     connections_booking_significance, stable_money_confidence,
                     market_support_early, market_support_late, steam_moves_detected,
                     drift_detected, liquidity_quality_score, prediction_timestamp, 
                     actual_result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        prediction_id,
                        race_id,
                        participant_id,
                        round(predicted_prob, 4),
                        round(confidence, 2),
                        round(value_percentage, 1),
                        round(consensus_rating, 1),
                        round(form_score, 3),
                        round(pace_rating, 3),
                        round(class_rating, 3),
                        round(trainer_form, 3),
                        round(jockey_form, 3),
                        round(course_suitability, 3),
                        round(distance_suitability, 3),
                        round(going_suitability, 3),
                        # Contextual factors
                        race_context["day_of_week"],
                        race_context["week_of_year"],
                        race_context["month"],
                        race_context["season"],
                        race_context["is_weekend"],
                        race_context["is_holiday"],
                        race_context["time_of_day"],
                        race_number,
                        12,  # Typical total races on card
                        field_size,
                        round(race_context["competitive_rating"], 3),
                        round(race_context["market_volatility"], 3),
                        round(race_context["weather_impact_score"], 3),
                        round(race_context["track_bias_factor"], 3),
                        round(horse_context["trainer_recent_form"], 3),
                        round(horse_context["jockey_recent_form"], 3),
                        round(horse_context["stable_confidence"], 3),
                        round(race_context["media_attention_score"], 3),
                        race_context["betting_patterns_unusual"],
                        horse_context["pace_scenario"],
                        horse_context["class_drop_raise"],
                        round(horse_context["distance_change_impact"], 3),
                        round(horse_context["weight_change_impact"], 3),
                        horse_context["equipment_change"],
                        horse_context["first_time_headgear"],
                        round(horse_context["connections_booking_significance"], 3),
                        round(horse_context["stable_money_confidence"], 3),
                        round(race_context["market_support_early"], 3),
                        round(race_context["market_support_late"], 3),
                        race_context["steam_moves_detected"],
                        race_context["drift_detected"],
                        round(race_context["liquidity_quality_score"], 3),
                        "2024-01-01 10:00:00",
                        1 if finish_pos == 1 else 0,
                    ),
                )

                # Generate betting strategy recommendations
                strategies_generated = []

                # 1. VALUE BETTING STRATEGY
                if value_percentage > 5 and confidence > 0.7:
                    kelly_fraction = self._calculate_kelly_fraction(
                        predicted_prob, odds
                    )
                    if kelly_fraction > 0:  # Only bet if Kelly is positive
                        stake = min(kelly_fraction * 1000, 50)  # Max £50 stake

                        strategy_confidence = confidence * (value_percentage / 20)
                        risk_rating = "LOW" if value_percentage > 15 else "MEDIUM"
                        expected_value = stake * (value_percentage / 100)

                        cursor.execute(
                            """
                            INSERT INTO ai_betting_strategies
                            (strategy_id, prediction_id, race_id, participant_id, strategy_type,
                             bet_type, recommended_stake, recommended_odds, kelly_fraction,
                             value_percentage, confidence_threshold, risk_rating, staking_method,
                             strategy_confidence, expected_value, bankroll_percentage, max_loss)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                strategy_id,
                                prediction_id,
                                race_id,
                                participant_id,
                                "value_bet",
                                "win",
                                round(stake, 2),
                                round(odds, 2),
                                round(kelly_fraction, 3),
                                round(value_percentage, 1),
                                0.7,
                                risk_rating,
                                "kelly",
                                round(strategy_confidence, 2),
                                round(expected_value, 2),
                                round(kelly_fraction * 100, 1),
                                round(stake, 2),
                            ),
                        )
                        strategy_id += 1
                        strategies_generated.append("value_bet")
                        value_bets.append((participant_id, predicted_prob, odds, stake))

                # 2. EACH-WAY STRATEGY
                if confidence > 0.65 and odds > 3.0 and predicted_prob > 0.15:
                    each_way_stake = min(25, confidence * 30)
                    each_way_terms = "1/4 odds 1-2-3"

                    cursor.execute(
                        """
                        INSERT INTO ai_betting_strategies
                        (strategy_id, prediction_id, race_id, participant_id, strategy_type,
                         bet_type, recommended_stake, recommended_odds, confidence_threshold,
                         risk_rating, staking_method, each_way_terms, strategy_confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            strategy_id,
                            prediction_id,
                            race_id,
                            participant_id,
                            "each_way",
                            "each_way",
                            round(each_way_stake, 2),
                            round(odds, 2),
                            0.65,
                            "MEDIUM",
                            "percentage",
                            each_way_terms,
                            round(confidence, 2),
                        ),
                    )
                    strategy_id += 1
                    strategies_generated.append("each_way")

                # 3. 20/80 STRATEGY (High confidence selections)
                if confidence > 0.85 and predicted_prob > 0.25:
                    total_stake = min(40, confidence * 45)
                    win_allocation = total_stake * 0.2  # 20% on win
                    place_allocation = total_stake * 0.8  # 80% on place

                    # Win component
                    cursor.execute(
                        """
                        INSERT INTO ai_betting_strategies
                        (strategy_id, prediction_id, race_id, participant_id, strategy_type,
                         bet_type, recommended_stake, recommended_odds, confidence_threshold,
                         risk_rating, staking_method, twenty_eighty_allocation, strategy_confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            strategy_id,
                            prediction_id,
                            race_id,
                            participant_id,
                            "twenty_eighty",
                            "win",
                            round(win_allocation, 2),
                            round(odds, 2),
                            0.85,
                            "LOW",
                            "fixed",
                            20.0,
                            round(confidence, 2),
                        ),
                    )
                    strategy_id += 1

                    # Place component
                    place_odds = odds * 0.25  # Approximate place odds
                    cursor.execute(
                        """
                        INSERT INTO ai_betting_strategies
                        (strategy_id, prediction_id, race_id, participant_id, strategy_type,
                         bet_type, recommended_stake, recommended_odds, confidence_threshold,
                         risk_rating, staking_method, twenty_eighty_allocation, strategy_confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            strategy_id,
                            prediction_id,
                            race_id,
                            participant_id,
                            "twenty_eighty",
                            "place",
                            round(place_allocation, 2),
                            round(place_odds, 2),
                            0.85,
                            "LOW",
                            "fixed",
                            80.0,
                            round(confidence, 2),
                        ),
                    )
                    strategy_id += 1
                    strategies_generated.append("twenty_eighty")

                prediction_id += 1

            # 4. DUTCHING STRATEGY (Multiple selections in same race)
            if len(value_bets) >= 2:
                dutching_group = race_id
                total_stake = 100  # Total stake to distribute

                # Calculate dutching stakes
                total_prob = sum([prob for _, prob, _, _ in value_bets])

                for i, (part_id, prob, odds_val, _) in enumerate(
                    value_bets[:3]
                ):  # Max 3 horses
                    dutching_stake = (prob / total_prob) * total_stake

                    cursor.execute(
                        """
                        INSERT INTO ai_betting_strategies
                        (strategy_id, prediction_id, race_id, participant_id, strategy_type,
                         bet_type, recommended_stake, recommended_odds, dutching_group,
                         risk_rating, staking_method, strategy_confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            strategy_id,
                            prediction_id - len(participants) + i,
                            race_id,
                            part_id,
                            "dutching",
                            "win",
                            round(dutching_stake, 2),
                            round(odds_val, 2),
                            dutching_group,
                            "MEDIUM",
                            "proportional",
                            0.75,
                        ),
                    )
                    strategy_id += 1

                prediction_id += 1

        self.conn.commit()
        logger.info(
            f"Generated {prediction_id - 1} AI predictions with {strategy_id - 1} betting strategies and full contextual data"
        )

    def generate_complete_dataset(
        self,
        num_horses: int = 10000,
        start_date: str = "2023-01-01",
        num_days: int = 730,
        include_markets: bool = True,
    ):
        """Generate complete massive dataset"""
        logger.info("🚀 Starting massive dataset generation...")

        self.connect_db()
        self.create_tables()

        logger.info("📍 Generating venues...")
        self.generate_venues()

        logger.info(f"🐎 Generating {num_horses} horses...")
        self.generate_horses(num_horses)

        logger.info("👨‍💼 Generating jockeys...")
        self.generate_jockeys()

        logger.info("👨‍🏫 Generating trainers...")
        self.generate_trainers()

        logger.info(f"🏁 Generating race cards for {num_days} days...")
        self.generate_race_cards(start_date, num_days)

        logger.info("🏇 Generating race participants...")
        self.generate_race_participants()

        if include_markets:
            logger.info("💰 Simulating betting markets...")
            self.simulate_betting_markets()

            logger.info("🤖 Generating AI predictions...")
            self.generate_ai_predictions()

        # Get final statistics
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM race_cards")
        total_races = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM race_participants")
        total_participants = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM horses")
        total_horses = cursor.fetchone()[0]

        if include_markets:
            cursor.execute("SELECT COUNT(*) FROM betting_markets")
            total_markets = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM simulated_trades")
            total_trades = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM ai_predictions")
            total_predictions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM ai_betting_strategies")
            total_strategies = cursor.fetchone()[0]

            # Get strategy breakdown
            cursor.execute(
                """
                SELECT strategy_type, COUNT(*) as count, AVG(recommended_stake) as avg_stake
                FROM ai_betting_strategies 
                GROUP BY strategy_type
            """
            )
            strategy_breakdown = cursor.fetchall()
        else:
            total_markets = 0
            total_trades = 0
            total_predictions = 0
            total_strategies = 0
            strategy_breakdown = []

        self.conn.close()

        logger.info("🎉 MASSIVE DATASET GENERATION COMPLETE!")
        logger.info("📊 Final Statistics:")
        logger.info(f"   🏁 Total Races: {total_races:,}")
        logger.info(f"   🏇 Total Participants: {total_participants:,}")
        logger.info(f"   🐎 Total Horses: {total_horses:,}")
        logger.info(f"   👨‍💼 Total Jockeys: {len(self.jockey_names)}")
        logger.info(f"   👨‍🏫 Total Trainers: {len(self.trainer_names)}")
        logger.info(f"   📍 Total Venues: {len(self.venues)}")
        if include_markets:
            logger.info(f"   💰 Total Markets: {total_markets:,}")
            logger.info(f"   📈 Total Trades: {total_trades:,}")
            logger.info(f"   🤖 AI Predictions: {total_predictions:,}")
            logger.info(f"   🎯 AI Betting Strategies: {total_strategies:,}")
            logger.info("   📊 Strategy Breakdown:")
            for strategy_type, count, avg_stake in strategy_breakdown:
                logger.info(
                    f"      • {strategy_type}: {count} selections, avg £{avg_stake:.2f}"
                )
        logger.info(f"   💾 Database: {self.db_path}")


def main():
    """Main function to generate massive dataset with market simulation"""
    generator = MassiveDatasetGenerator("massive_racing_data_with_markets.db")

    # Generate complete dataset with betting markets
    generator.generate_complete_dataset(
        num_horses=5000,  # Smaller dataset for faster generation
        start_date="2024-01-01",
        num_days=180,  # 6 months
        include_markets=True,  # Include betting market simulation
    )

    # Generate additional market analysis
    print("\n🎯 AI BETTING STRATEGIES & MARKET SIMULATION COMPLETE!")
    print("📊 Available data includes:")
    print("   • Race results with realistic form")
    print("   • Multi-bookmaker odds and market depth")
    print("   • Simulated trading data with P&L")
    print("   • Comprehensive AI predictions with detailed analysis")
    print("   • AI-generated betting strategy recommendations:")
    print("     ⭐ Value Betting with Kelly Criterion staking")
    print("     ⭐ Each-Way strategies for longer odds")
    print("     ⭐ 20/80 Strategy (20% win, 80% place)")
    print("     ⭐ Dutching across multiple selections")
    print("     ⭐ Kelly Criterion optimal stake sizing")
    print("   • Complete betting exchange simulation")
    print("\n💡 This dataset is perfect for:")
    print("   • Training ML models on realistic data")
    print("   • Backtesting sophisticated betting strategies")
    print("   • Testing AI prediction accuracy")
    print("   • Market efficiency analysis")
    print("   • Strategy performance validation")
    print("   • Risk management system testing")


def quick_market_demo():
    """Generate a quick demo with just market simulation"""
    generator = MassiveDatasetGenerator("demo_markets.db")

    # Generate smaller dataset for demonstration
    generator.generate_complete_dataset(
        num_horses=1000,
        start_date="2024-08-01",
        num_days=7,  # 1 week
        include_markets=True,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("🎯 Running quick market demonstration...")
        quick_market_demo()
    else:
        print("🚀 Running full dataset generation with markets...")
        main()
