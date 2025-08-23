#!/usr/bin/env python3
"""
Weekly Race Cards Generator for Horse Racing AI v2.0

This module creates a full week's worth of realistic fake race cards,
with daily release functionality to simulate real-world racing data flow.

Features:
- 7 days of complete race cards
- Realistic UK/Irish racing schedule patterns
- Daily race release simulation
- Comprehensive race participant data
- Progressive data availability testing
"""

import os
import logging
import random
import json
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WeeklyRaceCardsGenerator:
    """Generate and manage a full week's worth of realistic race cards"""

    def __init__(self, database_url: str = None):
        """Initialize with database connection"""
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://horse_racing_test:test_password_123@postgres:5432/horse_racing_test_db",
        )

        # UK/Irish course data with realistic daily patterns
        self.courses_by_day = {
            "monday": [
                "Brighton",
                "Catterick",
                "Leicester",
                "Plumpton",
                "Sedgefield",
                "Wolverhampton",
                "Dundalk",
                "Kempton Park",
                "Lingfield Park",
            ],
            "tuesday": [
                "Chepstow",
                "Doncaster",
                "Fakenham",
                "Newcastle",
                "Warwick",
                "Chelmsford City",
                "Southwell",
                "Bangor-on-Dee",
            ],
            "wednesday": [
                "Ascot",
                "Bath",
                "Exeter",
                "Huntingdon",
                "Market Rasen",
                "Redcar",
                "Yarmouth",
                "Navan",
                "Cork",
            ],
            "thursday": [
                "Goodwood",
                "Hamilton",
                "Ludlow",
                "Newbury",
                "Sandown Park",
                "Taunton",
                "Windsor",
                "Punchestown",
                "Leopardstown",
            ],
            "friday": [
                "Haydock Park",
                "Newmarket",
                "Pontefract",
                "Ripon",
                "Salisbury",
                "Uttoxeter",
                "York",
                "The Curragh",
                "Galway",
            ],
            "saturday": [
                "Aintree",
                "Cheltenham",
                "Epsom Downs",
                "Kempton Park",
                "Newmarket",
                "Sandown Park",
                "York",
                "Leopardstown",
                "Fairyhouse",
            ],
            "sunday": [
                "Fontwell Park",
                "Hexham",
                "Worcester",
                "Wetherby",
                "Carlisle",
                "Naas",
                "Clonmel",
                "Downpatrick",
            ],
        }

        # Realistic race types by day
        self.race_types_by_day = {
            "monday": ["Handicap", "Maiden", "Claiming", "Selling"],
            "tuesday": ["Handicap", "Maiden", "Novice", "Conditional"],
            "wednesday": ["Handicap", "Listed", "Maiden", "Novice"],
            "thursday": ["Handicap", "Listed", "Group 3", "Maiden"],
            "friday": ["Handicap", "Listed", "Group 2", "Group 3"],
            "saturday": ["Group 1", "Group 2", "Listed", "Handicap"],
            "sunday": ["Handicap", "Maiden", "Novice", "Hunter Chase"],
        }

        # UK/Irish racing surfaces
        self.surfaces = ["Turf", "All Weather", "Heavy", "Good", "Firm", "Soft"]

        # Common UK/Irish distances (in furlongs and miles)
        self.distances = [
            "5f",
            "6f",
            "7f",
            "1m",
            "1m1f",
            "1m2f",
            "1m4f",
            "1m6f",
            "2m",
            "2m4f",
            "3m",
            "3m2f",
            "2m½f",
            "1m½f",
            "7½f",
        ]

        # Prize money ranges by day (Saturday has highest prizes)
        self.prize_ranges = {
            "monday": (2000, 15000),
            "tuesday": (2500, 18000),
            "wednesday": (3000, 25000),
            "thursday": (4000, 35000),
            "friday": (5000, 50000),
            "saturday": (10000, 100000),
            "sunday": (3000, 20000),
        }

        # UK/Irish horse names
        self.horse_names = [
            "Desert Crown",
            "Golden Horde",
            "Palace Pier",
            "Mishriff",
            "Adayar",
            "Hurricane Lane",
            "Baaeed",
            "Inspiral",
            "Native Trail",
            "Coroebus",
            "Noble Truth",
            "Rebel Kingdom",
            "Thunder Moon",
            "Charlie Appleby",
            "Fantastic Moon",
            "Master Of The Seas",
            "Space Blues",
            "Poetic Flare",
            "Mac Swiney",
            "High Definition",
            "Wembley",
            "Creative Force",
            "Dragon Symbol",
            "Perfect Power",
            "Ebro River",
            "Imperial Fighter",
            "Lusail",
            "Nations Pride",
            "Wild Beauty",
            "Emily Upjohn",
            "Nashwa",
            "Tuesday",
            "Novellist",
            "Honourable Woman",
            "Sea La Rosa",
            "Tranquil Lady",
            "Magical Lagoon",
            "Sacred",
        ]

        # UK/Irish jockey names
        self.jockey_names = [
            "Ryan Moore",
            "William Buick",
            "Frankie Dettori",
            "Oisin Murphy",
            "Tom Marquand",
            "James Doyle",
            "Andrea Atzeni",
            "Pat Dobbs",
            "Jim Crowley",
            "Danny Tudhope",
            "Hollie Doyle",
            "Silvestre de Sousa",
            "Kieran Shoemark",
            "Rossa Ryan",
            "David Probert",
            "Sean Levey",
            "Hector Crouch",
            "Jason Watson",
            "Callum Rodriguez",
            "Billy Loughnane",
            "Colin Keane",
            "Donnacha O'Brien",
            "Shane Foley",
            "Chris Hayes",
            "Gary Carroll",
            "Ronan Whelan",
            "Dylan Browne McMonagle",
            "Ben Coen",
        ]

        # UK/Irish trainer names
        self.trainer_names = [
            "Charlie Appleby",
            "John Gosden",
            "Aidan O'Brien",
            "William Haggas",
            "Mark Johnston",
            "Roger Varian",
            "Andrew Balding",
            "Sir Michael Stoute",
            "Clive Cox",
            "Hugo Palmer",
            "Richard Hannon",
            "John Quinn",
            "Kevin Ryan",
            "David Simcock",
            "Ralph Beckett",
            "Archie Watson",
            "Karl Burke",
            "Ed Walker",
            "George Boughey",
            "Tom Dascombe",
            "Joseph O'Brien",
            "Dermot Weld",
            "Jim Bolger",
            "Jessica Harrington",
            "Ger Lyons",
            "Fozzy Stack",
            "Johnny Murtagh",
            "Paddy Twomey",
        ]

    def connect_to_database(self):
        """Connect to the test database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = True
            logger.info("✅ Connected to test database successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False

    def create_weekly_schema(self):
        """Create schema for weekly race card management"""
        schema_sql = """
        -- Weekly race cards tracking table
        CREATE TABLE IF NOT EXISTS weekly_race_schedule (
            schedule_id SERIAL PRIMARY KEY,
            week_start_date DATE NOT NULL,
            day_number INTEGER NOT NULL CHECK (day_number BETWEEN 1 AND 7),
            day_name VARCHAR(20) NOT NULL,
            race_date DATE NOT NULL,
            total_races INTEGER DEFAULT 0,
            races_released BOOLEAN DEFAULT FALSE,
            release_timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Daily race release log
        CREATE TABLE IF NOT EXISTS daily_race_releases (
            release_id SERIAL PRIMARY KEY,
            race_date DATE NOT NULL,
            course VARCHAR(100) NOT NULL,
            total_races INTEGER NOT NULL,
            release_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            release_status VARCHAR(20) DEFAULT 'pending' CHECK (release_status IN ('pending', 'released', 'completed'))
        );

        -- Week management tracking
        CREATE TABLE IF NOT EXISTS week_management (
            week_id SERIAL PRIMARY KEY,
            week_start_date DATE NOT NULL UNIQUE,
            week_end_date DATE NOT NULL,
            total_race_cards INTEGER DEFAULT 0,
            cards_generated INTEGER DEFAULT 0,
            cards_released INTEGER DEFAULT 0,
            week_status VARCHAR(20) DEFAULT 'planning' CHECK (week_status IN ('planning', 'generating', 'releasing', 'completed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_weekly_schedule_date ON weekly_race_schedule(race_date);
        CREATE INDEX IF NOT EXISTS idx_daily_releases_date ON daily_race_releases(race_date);
        CREATE INDEX IF NOT EXISTS idx_week_management_start ON week_management(week_start_date);
        """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(schema_sql)
            logger.info("✅ Weekly race card schema created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create weekly schema: {e}")
            return False

    def generate_weekly_schedule(self, start_date: date = None) -> Dict[str, Any]:
        """Generate a complete 7-day racing schedule"""
        if start_date is None:
            start_date = date.today()

        logger.info(f"🗓️ Generating weekly schedule starting {start_date}")

        # Clear existing schedule for this week
        with self.conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM weekly_race_schedule WHERE week_start_date = %s",
                (start_date,),
            )
            cursor.execute(
                "DELETE FROM week_management WHERE week_start_date = %s", (start_date,)
            )

        week_data = {
            "week_start": start_date,
            "week_end": start_date + timedelta(days=6),
            "days": [],
            "total_races": 0,
        }

        day_names = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        for day_num in range(7):
            current_date = start_date + timedelta(days=day_num)
            day_name = day_names[day_num]

            # Get courses for this day
            available_courses = self.courses_by_day[day_name]

            # Determine number of racing venues (more on weekends)
            if day_name in ["saturday", "sunday"]:
                num_venues = random.randint(4, 6)
            elif day_name in ["friday"]:
                num_venues = random.randint(3, 5)
            else:
                num_venues = random.randint(2, 4)

            selected_courses = random.sample(
                available_courses, min(num_venues, len(available_courses))
            )

            day_races = 0
            for course in selected_courses:
                # Races per venue (more on weekends and premium venues)
                if day_name == "saturday" and course in [
                    "Ascot",
                    "Newmarket",
                    "York",
                    "Cheltenham",
                ]:
                    races_at_venue = random.randint(7, 9)
                elif day_name in ["friday", "saturday"]:
                    races_at_venue = random.randint(6, 8)
                else:
                    races_at_venue = random.randint(4, 7)

                day_races += races_at_venue

            week_data["days"].append(
                {
                    "day_number": day_num + 1,
                    "day_name": day_name,
                    "date": current_date,
                    "courses": selected_courses,
                    "total_races": day_races,
                }
            )

            week_data["total_races"] += day_races

            # Insert into database
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO weekly_race_schedule 
                    (week_start_date, day_number, day_name, race_date, total_races)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (start_date, day_num + 1, day_name, current_date, day_races),
                )

        # Insert week management record
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO week_management 
                (week_start_date, week_end_date, total_race_cards, week_status)
                VALUES (%s, %s, %s, 'planning')
            """,
                (start_date, week_data["week_end"], week_data["total_races"]),
            )

        logger.info(
            f"✅ Generated weekly schedule: {week_data['total_races']} races across 7 days"
        )
        return week_data

    def generate_race_card_for_day(
        self, race_date: date, courses: List[str], target_races: int
    ) -> List[Dict[str, Any]]:
        """Generate complete race cards for a specific day"""
        logger.info(
            f"🏁 Generating {target_races} races for {race_date} at {len(courses)} courses"
        )

        day_name = race_date.strftime("%A").lower()
        race_types = self.race_types_by_day.get(day_name, ["Handicap", "Maiden"])
        prize_min, prize_max = self.prize_ranges.get(day_name, (5000, 25000))

        races = []
        # Use date-based race ID to ensure uniqueness
        base_id = int(race_date.strftime("%Y%m%d")) * 100
        race_id_start = base_id + len(races)

        races_per_course = target_races // len(courses)
        extra_races = target_races % len(courses)

        for course_idx, course in enumerate(courses):
            course_races = races_per_course
            if course_idx < extra_races:
                course_races += 1

            # First race time (typically 1:30 PM to 2:30 PM)
            first_race_hour = random.randint(13, 14)
            first_race_minute = random.choice([0, 15, 30, 45])
            current_time = time(first_race_hour, first_race_minute)

            for race_num in range(1, course_races + 1):
                race_id = race_id_start + len(races)

                # Generate race details
                race_type = random.choice(race_types)
                distance = random.choice(self.distances)
                surface = random.choice(self.surfaces)
                runners = random.randint(6, 16)
                prize_money = f"£{random.randint(prize_min, prize_max):,}"

                # Race class (higher on weekends)
                if day_name == "saturday":
                    race_class = random.choice(["1", "2", "3", "4"])
                elif day_name == "friday":
                    race_class = random.choice(["2", "3", "4", "5"])
                else:
                    race_class = random.choice(["3", "4", "5", "6"])

                # Age restrictions
                age_restriction = random.choice(
                    ["2yo", "3yo", "3yo+", "4yo+", "All ages"]
                )

                race_data = {
                    "race_id": race_id,
                    "race_number": race_num,
                    "race_time": current_time.strftime("%H:%M"),
                    "course": course,
                    "race_type": race_type,
                    "date": race_date,
                    "race_name": f"{course} {race_type} Stakes",
                    "class": race_class,
                    "years": age_restriction,
                    "distance": distance,
                    "surface": surface,
                    "prize": prize_money,
                    "runners_racecard": runners,
                    "runners": runners,
                    "draw": random.randint(1, runners) if runners > 1 else 1,
                    "participants": self._generate_race_participants(race_id, runners),
                }

                races.append(race_data)

                # Next race time (30-45 minutes later)
                next_minutes = current_time.minute + random.randint(30, 45)
                next_hour = current_time.hour + (next_minutes // 60)
                next_minutes = next_minutes % 60

                if next_hour < 24:
                    current_time = time(next_hour, next_minutes)
                else:
                    break  # Don't go past midnight

        logger.info(f"✅ Generated {len(races)} races for {race_date}")
        return races

    def _generate_race_participants(
        self, race_id: int, num_runners: int
    ) -> List[Dict[str, Any]]:
        """Generate race participants (horses, jockeys, trainers)"""
        participants = []

        selected_horses = random.sample(
            self.horse_names, min(num_runners, len(self.horse_names))
        )
        selected_jockeys = random.sample(
            self.jockey_names, min(num_runners, len(self.jockey_names))
        )
        selected_trainers = random.sample(
            self.trainer_names, min(num_runners, len(self.trainer_names))
        )

        for i in range(num_runners):
            # Generate realistic odds
            if i == 0:  # Favorite
                odds = random.choice(["2/1", "5/2", "3/1", "7/2"])
            elif i < 3:  # Second favorites
                odds = random.choice(["4/1", "9/2", "5/1", "11/2", "6/1"])
            else:  # Others
                odds = random.choice(
                    ["8/1", "10/1", "12/1", "14/1", "16/1", "20/1", "25/1"]
                )

            participant = {
                "race_id": race_id,
                "draw": i + 1,
                "name": selected_horses[i % len(selected_horses)],
                "jockey": selected_jockeys[i % len(selected_jockeys)],
                "trainer": selected_trainers[i % len(selected_trainers)],
                "weight_uk": f"{random.randint(8, 10)}-{random.randint(0, 13)}",
                "weight": round(random.uniform(110, 140), 2),  # Numeric weight
                "odds": odds,
                "age": random.randint(2, 8),
            }
            participants.append(participant)

        return participants

    def insert_daily_races(self, races: List[Dict[str, Any]]) -> bool:
        """Insert race cards into database"""
        try:
            logger.info(f"📝 Inserting {len(races)} race cards into database...")

            # Insert races_cards
            races_cards_data = []
            races_results_data = []
            racecard_details_data = []

            for race in races:
                # Prepare races_cards data
                race_card = {
                    "race_id": race["race_id"],
                    "race_number": race["race_number"],
                    "race_time": race["race_time"],
                    "course": race["course"],
                    "race_type": race["race_type"],
                    "date": race["date"],
                    "race_name": race["race_name"],
                    "class": race["class"],
                    "years": race["years"],
                    "distance": race["distance"],
                    "surface": race["surface"],
                    "prize": race["prize"],
                    "runners_racecard": race["runners_racecard"],
                    "runners": race["runners"],
                    "draw": race["draw"],
                }
                races_cards_data.append(race_card)

                # Prepare races_results data (same structure)
                races_results_data.append(race_card.copy())

                # Prepare racecard_details data
                for participant in race["participants"]:
                    racecard_details_data.append(participant)

            # Batch insert races_cards
            with self.conn.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO races_cards 
                    (race_id, race_number, race_time, course, race_type, date, race_name, 
                     class, years, distance, surface, prize, runners_racecard, runners, draw)
                    VALUES (%(race_id)s, %(race_number)s, %(race_time)s, %(course)s, %(race_type)s, 
                            %(date)s, %(race_name)s, %(class)s, %(years)s, %(distance)s, %(surface)s, 
                            %(prize)s, %(runners_racecard)s, %(runners)s, %(draw)s)
                """,
                    races_cards_data,
                )

                cursor.executemany(
                    """
                    INSERT INTO races_results 
                    (race_id, race_number, race_time, course, race_type, date, race_name, 
                     class, years, distance, surface, prize, runners_racecard, runners)
                    VALUES (%(race_id)s, %(race_number)s, %(race_time)s, %(course)s, %(race_type)s, 
                            %(date)s, %(race_name)s, %(class)s, %(years)s, %(distance)s, %(surface)s, 
                            %(prize)s, %(runners_racecard)s, %(runners)s)
                """,
                    races_results_data,
                )

                cursor.executemany(
                    """
                    INSERT INTO racecard_details 
                    (race_id, draw, name, jockey, trainer, weight_uk, weight, odds, age)
                    VALUES (%(race_id)s, %(draw)s, %(name)s, %(jockey)s, %(trainer)s, 
                            %(weight_uk)s, %(weight)s, %(odds)s, %(age)s)
                """,
                    racecard_details_data,
                )

            logger.info(f"✅ Successfully inserted {len(races)} race cards")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to insert race cards: {e}")
            return False

    def release_daily_races(self, race_date: date) -> Dict[str, Any]:
        """Release/publish race cards for a specific day"""
        logger.info(f"📅 Releasing race cards for {race_date}")

        try:
            # Get scheduled races for this day
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM weekly_race_schedule 
                    WHERE race_date = %s AND races_released = FALSE
                """,
                    (race_date,),
                )

                schedule = cursor.fetchone()
                if not schedule:
                    logger.warning(f"No unreleased races found for {race_date}")
                    return {
                        "status": "no_races",
                        "message": "No races scheduled for this date",
                    }

                # Generate race cards for this day
                day_courses = self.courses_by_day.get(
                    schedule["day_name"], ["Newmarket"]
                )
                races = self.generate_race_card_for_day(
                    race_date, day_courses, schedule["total_races"]
                )

                # Insert into database
                if self.insert_daily_races(races):
                    # Mark as released
                    cursor.execute(
                        """
                        UPDATE weekly_race_schedule 
                        SET races_released = TRUE, release_timestamp = CURRENT_TIMESTAMP
                        WHERE race_date = %s
                    """,
                        (race_date,),
                    )

                    # Log the release
                    for course in set(race["course"] for race in races):
                        course_races = len([r for r in races if r["course"] == course])
                        cursor.execute(
                            """
                            INSERT INTO daily_race_releases 
                            (race_date, course, total_races, release_status)
                            VALUES (%s, %s, %s, 'released')
                        """,
                            (race_date, course, course_races),
                        )

                    release_result = {
                        "status": "success",
                        "date": race_date,
                        "races_released": len(races),
                        "courses": list(set(race["course"] for race in races)),
                        "total_runners": sum(race["runners"] for race in races),
                        "release_timestamp": datetime.now(),
                    }

                    logger.info(f"✅ Released {len(races)} races for {race_date}")
                    return release_result
                else:
                    return {"status": "error", "message": "Failed to insert race data"}

        except Exception as e:
            logger.error(f"❌ Failed to release races for {race_date}: {e}")
            return {"status": "error", "message": str(e)}

    def get_week_status(self, start_date: date) -> Dict[str, Any]:
        """Get current status of weekly race schedule"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get week management info
                cursor.execute(
                    """
                    SELECT * FROM week_management WHERE week_start_date = %s
                """,
                    (start_date,),
                )
                week_info = cursor.fetchone()

                if not week_info:
                    return {"status": "not_found", "message": "Week not found"}

                # Get daily schedule
                cursor.execute(
                    """
                    SELECT * FROM weekly_race_schedule 
                    WHERE week_start_date = %s
                    ORDER BY day_number
                """,
                    (start_date,),
                )
                daily_schedule = cursor.fetchall()

                # Calculate progress
                total_days = len(daily_schedule)
                released_days = len([d for d in daily_schedule if d["races_released"]])

                status = {
                    "week_start": week_info["week_start_date"],
                    "week_end": week_info["week_end_date"],
                    "total_race_cards": week_info["total_race_cards"],
                    "progress": {
                        "days_scheduled": total_days,
                        "days_released": released_days,
                        "percentage_complete": (
                            (released_days / total_days * 100) if total_days > 0 else 0
                        ),
                    },
                    "daily_status": [dict(d) for d in daily_schedule],
                    "week_status": week_info["week_status"],
                }

                return status

        except Exception as e:
            logger.error(f"❌ Failed to get week status: {e}")
            return {"status": "error", "message": str(e)}

    def run_weekly_simulation(
        self, start_date: date = None, days_to_simulate: int = 7
    ) -> Dict[str, Any]:
        """Run complete weekly race card simulation"""
        if start_date is None:
            start_date = date.today()

        logger.info(f"🚀 Starting weekly race card simulation from {start_date}")

        # Connect to database
        if not self.connect_to_database():
            return {"status": "error", "message": "Database connection failed"}

        # Create schema
        if not self.create_weekly_schema():
            return {"status": "error", "message": "Schema creation failed"}

        # Generate weekly schedule
        week_schedule = self.generate_weekly_schedule(start_date)

        simulation_results = {
            "week_start": start_date,
            "simulation_start": datetime.now(),
            "daily_releases": [],
            "total_races_released": 0,
            "total_runners": 0,
            "courses_used": set(),
        }

        # Release races day by day
        for day_num in range(min(days_to_simulate, 7)):
            current_date = start_date + timedelta(days=day_num)

            logger.info(f"📅 Day {day_num + 1}: Releasing races for {current_date}")

            release_result = self.release_daily_races(current_date)

            if release_result["status"] == "success":
                simulation_results["daily_releases"].append(release_result)
                simulation_results["total_races_released"] += release_result[
                    "races_released"
                ]
                simulation_results["total_runners"] += release_result["total_runners"]
                simulation_results["courses_used"].update(release_result["courses"])

                logger.info(
                    f"✅ Day {day_num + 1} complete: {release_result['races_released']} races released"
                )
            else:
                logger.error(
                    f"❌ Day {day_num + 1} failed: {release_result.get('message', 'Unknown error')}"
                )

        simulation_results["courses_used"] = list(simulation_results["courses_used"])
        simulation_results["simulation_end"] = datetime.now()
        simulation_results["duration"] = (
            simulation_results["simulation_end"]
            - simulation_results["simulation_start"]
        ).total_seconds()

        logger.info(
            f"🏁 Weekly simulation complete: {simulation_results['total_races_released']} races across {len(simulation_results['courses_used'])} courses"
        )

        return simulation_results

    def close_connection(self):
        """Close database connection"""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Weekly Race Cards Generator")
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD)",
        default=date.today().isoformat(),
    )
    parser.add_argument(
        "--days", type=int, help="Number of days to simulate", default=7
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Only show status, don't generate new data",
    )

    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.start_date)
    except ValueError:
        logger.error("Invalid date format. Use YYYY-MM-DD")
        return

    generator = WeeklyRaceCardsGenerator()

    try:
        if args.status_only:
            # Just show status
            if generator.connect_to_database():
                status = generator.get_week_status(start_date)
                print("\n" + "=" * 60)
                print("WEEKLY RACE CARDS STATUS")
                print("=" * 60)
                print(json.dumps(status, indent=2, default=str))
        else:
            # Run full simulation
            results = generator.run_weekly_simulation(start_date, args.days)

            print("\n" + "=" * 60)
            print("WEEKLY RACE CARDS SIMULATION COMPLETE")
            print("=" * 60)
            print(
                f"📅 Week: {results['week_start']} to {results['week_start'] + timedelta(days=6)}"
            )
            print(f"🏁 Total Races: {results['total_races_released']}")
            print(f"🏇 Total Runners: {results['total_runners']}")
            print(f"🏟️ Courses Used: {len(results['courses_used'])}")
            print(f"⏱️ Duration: {results['duration']:.2f} seconds")
            print("\nDaily Breakdown:")
            for i, day in enumerate(results["daily_releases"]):
                print(
                    f"  Day {i+1} ({day['date']}): {day['races_released']} races at {len(day['courses'])} courses"
                )
            print("=" * 60)

    finally:
        generator.close_connection()


if __name__ == "__main__":
    main()
