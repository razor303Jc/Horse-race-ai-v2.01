#!/usr/bin/env python3
"""
Race Card Database Uploader
Maps and uploads race card data to PostgreSQL tables for ML training and analysis
"""

import pandas as pd
import asyncio
import asyncpg
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database connection configuration"""

    host: str = "localhost"
    port: int = 5434
    database: str = "horserace_db"
    user: str = "horserace_user"
    password: str = "horserace_password"


class RaceCardDatabaseUploader:
    """Handles mapping and uploading race card data to PostgreSQL"""

    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.connection_pool = None

        # Table creation SQL
        self.table_schemas = {
            "race_cards": """
                CREATE TABLE IF NOT EXISTS race_cards (
                    race_id BIGINT PRIMARY KEY,
                    race_number INTEGER,
                    race_time TIMESTAMP,
                    course_id INTEGER,
                    course VARCHAR(100),
                    race_type VARCHAR(50),
                    race_date DATE,
                    race_name VARCHAR(200),
                    class VARCHAR(20),
                    age_restriction VARCHAR(20),
                    distance VARCHAR(50),
                    surface VARCHAR(50),
                    prize VARCHAR(50),
                    runners_racecard INTEGER,
                    runners INTEGER,
                    draw_info VARCHAR(20),
                    ew_racecard INTEGER,
                    ew INTEGER,
                    places_ew_racecard INTEGER,
                    places_ew INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "horses": """
                CREATE TABLE IF NOT EXISTS horses (
                    horse_id BIGINT PRIMARY KEY,
                    uptodate DATE,
                    state VARCHAR(20),
                    race_id_last_race BIGINT,
                    date_last_race DATE,
                    name VARCHAR(100),
                    country VARCHAR(10),
                    age INTEGER,
                    color VARCHAR(30),
                    owner VARCHAR(200),
                    sire VARCHAR(100),
                    dam VARCHAR(100),
                    dam_sire VARCHAR(100),
                    sex VARCHAR(20),
                    total_races FLOAT,
                    wins FLOAT,
                    percentage_wins VARCHAR(10),
                    placed FLOAT,
                    percentage_placed VARCHAR(10),
                    flat_aw_races FLOAT,
                    flat_aw_wins FLOAT,
                    flat_aw_rate VARCHAR(10),
                    flat_aw_placed FLOAT,
                    flat_aw_placed_rate VARCHAR(10),
                    flat_turf_races FLOAT,
                    flat_turf_wins FLOAT,
                    flat_turf_rate VARCHAR(10),
                    flat_turf_placed FLOAT,
                    flat_turf_placed_rate VARCHAR(10),
                    chase_races FLOAT,
                    chase_wins FLOAT,
                    chase_rate VARCHAR(10),
                    chase_placed FLOAT,
                    chase_placed_rate VARCHAR(10),
                    hurdle_races FLOAT,
                    hurdle_wins FLOAT,
                    hurdle_rate VARCHAR(10),
                    hurdle_placed FLOAT,
                    hurdle_placed_rate VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "race_entries": """
                CREATE TABLE IF NOT EXISTS race_entries (
                    entry_id BIGSERIAL PRIMARY KEY,
                    race_id BIGINT REFERENCES race_cards(race_id),
                    horse_id BIGINT REFERENCES horses(horse_id),
                    horse_number INTEGER,
                    draw INTEGER,
                    country VARCHAR(10),
                    horse_name VARCHAR(100),
                    age INTEGER,
                    weight_uk VARCHAR(10),
                    weight_kg FLOAT,
                    gears VARCHAR(20),
                    horse_rate INTEGER,
                    jockey_id INTEGER,
                    jockey VARCHAR(100),
                    trainer_id INTEGER,
                    trainer VARCHAR(100),
                    favourite_position VARCHAR(10),
                    odds VARCHAR(20),
                    odds_decimal FLOAT,
                    timeform_comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(race_id, horse_id)
                );
            """,
            "data_quality_log": """
                CREATE TABLE IF NOT EXISTS data_quality_log (
                    log_id BIGSERIAL PRIMARY KEY,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    table_name VARCHAR(50),
                    records_processed INTEGER,
                    records_inserted INTEGER,
                    records_updated INTEGER,
                    records_failed INTEGER,
                    processing_time_ms INTEGER,
                    data_source VARCHAR(100),
                    status VARCHAR(20),
                    error_details TEXT
                );
            """,
        }

    async def initialize_connection_pool(self):
        """Initialize database connection pool"""
        try:
            connection_string = (
                f"postgresql://{self.config.user}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
            )

            self.connection_pool = await asyncpg.create_pool(
                connection_string, min_size=2, max_size=10, command_timeout=60
            )

            logger.info("✅ Database connection pool initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database connection: {e}")
            raise

    async def create_tables(self):
        """Create all required tables if they don't exist"""
        async with self.connection_pool.acquire() as conn:
            for table_name, schema_sql in self.table_schemas.items():
                try:
                    await conn.execute(schema_sql)
                    logger.info(f"✅ Table {table_name} ready")
                except Exception as e:
                    logger.error(f"❌ Failed to create table {table_name}: {e}")
                    raise

    async def process_race_cards_data(self, cards_data_dir: Path) -> Dict[str, Any]:
        """Process and upload all race card data"""
        start_time = datetime.now()

        try:
            # Initialize database
            await self.initialize_connection_pool()
            await self.create_tables()

            results = {
                "race_cards": {
                    "processed": 0,
                    "inserted": 0,
                    "updated": 0,
                    "failed": 0,
                },
                "horses": {"processed": 0, "inserted": 0, "updated": 0, "failed": 0},
                "race_entries": {
                    "processed": 0,
                    "inserted": 0,
                    "updated": 0,
                    "failed": 0,
                },
                "errors": [],
            }

            # Process each data type
            logger.info("🔄 Processing race cards data...")

            # 1. Process races/races.csv
            races_file = cards_data_dir / "races" / "races.csv"
            if races_file.exists():
                races_result = await self.upload_race_cards(races_file)
                results["race_cards"] = races_result
            else:
                logger.error(f"❌ Races file not found: {races_file}")
                results["errors"].append(f"Missing races file: {races_file}")

            # 2. Process horses/horses.csv
            horses_file = cards_data_dir / "horses" / "horses.csv"
            if horses_file.exists():
                horses_result = await self.upload_horses(horses_file)
                results["horses"] = horses_result
            else:
                logger.error(f"❌ Horses file not found: {horses_file}")
                results["errors"].append(f"Missing horses file: {horses_file}")

            # 3. Process racecard_details/racecard_details.csv
            entries_file = cards_data_dir / "racecard_details" / "racecard_details.csv"
            if entries_file.exists():
                entries_result = await self.upload_race_entries(entries_file)
                results["race_entries"] = entries_result
            else:
                logger.error(f"❌ Race entries file not found: {entries_file}")
                results["errors"].append(f"Missing race entries file: {entries_file}")

            # Log processing summary
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            await self.log_data_quality(results, processing_time)

            return results

        except Exception as e:
            logger.error(f"❌ Error processing race cards data: {e}")
            results["errors"].append(str(e))
            return results
        finally:
            if self.connection_pool:
                await self.connection_pool.close()

    async def upload_race_cards(self, races_file: Path) -> Dict[str, int]:
        """Upload race cards data"""
        logger.info(f"📋 Processing races from {races_file}")

        result = {"processed": 0, "inserted": 0, "updated": 0, "failed": 0}

        try:
            # Read and clean data
            df = pd.read_csv(races_file)
            result["processed"] = len(df)

            # Clean and map data
            df = self.clean_race_cards_data(df)

            async with self.connection_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        # Use UPSERT to handle duplicates
                        query = """
                            INSERT INTO race_cards (
                                race_id, race_number, race_time, course_id, course,
                                race_type, race_date, race_name, class, age_restriction,
                                distance, surface, prize, runners_racecard, runners,
                                draw_info, ew_racecard, ew, places_ew_racecard, places_ew
                            ) VALUES (
                                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                                $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                            )
                            ON CONFLICT (race_id) 
                            DO UPDATE SET
                                race_number = EXCLUDED.race_number,
                                race_time = EXCLUDED.race_time,
                                course = EXCLUDED.course,
                                race_type = EXCLUDED.race_type,
                                race_name = EXCLUDED.race_name,
                                updated_at = CURRENT_TIMESTAMP
                        """

                        await conn.execute(query, *row.values)
                        result["inserted"] += 1

                    except Exception as e:
                        logger.error(f"❌ Failed to insert race {row['race_id']}: {e}")
                        result["failed"] += 1

            logger.info(f"✅ Races upload complete: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ Error uploading races: {e}")
            result["failed"] = result["processed"]
            return result

    async def upload_horses(self, horses_file: Path) -> Dict[str, int]:
        """Upload horses data"""
        logger.info(f"🐎 Processing horses from {horses_file}")

        result = {"processed": 0, "inserted": 0, "updated": 0, "failed": 0}

        try:
            # Read and clean data
            df = pd.read_csv(horses_file)
            result["processed"] = len(df)

            # Clean and map data
            df = self.clean_horses_data(df)

            async with self.connection_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        # Use UPSERT to handle duplicates
                        query = """
                            INSERT INTO horses (
                                horse_id, uptodate, state, race_id_last_race, date_last_race,
                                name, country, age, color, owner, sire, dam, dam_sire, sex,
                                total_races, wins, percentage_wins, placed, percentage_placed,
                                flat_aw_races, flat_aw_wins, flat_aw_rate, flat_aw_placed, flat_aw_placed_rate,
                                flat_turf_races, flat_turf_wins, flat_turf_rate, flat_turf_placed, flat_turf_placed_rate,
                                chase_races, chase_wins, chase_rate, chase_placed, chase_placed_rate,
                                hurdle_races, hurdle_wins, hurdle_rate, hurdle_placed, hurdle_placed_rate
                            ) VALUES (
                                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                                $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
                                $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
                                $31, $32, $33, $34, $35, $36, $37, $38, $39
                            )
                            ON CONFLICT (horse_id)
                            DO UPDATE SET
                                uptodate = EXCLUDED.uptodate,
                                state = EXCLUDED.state,
                                race_id_last_race = EXCLUDED.race_id_last_race,
                                date_last_race = EXCLUDED.date_last_race,
                                total_races = EXCLUDED.total_races,
                                wins = EXCLUDED.wins,
                                updated_at = CURRENT_TIMESTAMP
                        """

                        await conn.execute(query, *row.values)
                        result["inserted"] += 1

                    except Exception as e:
                        logger.error(
                            f"❌ Failed to insert horse {row['horse_id']}: {e}"
                        )
                        result["failed"] += 1

            logger.info(f"✅ Horses upload complete: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ Error uploading horses: {e}")
            result["failed"] = result["processed"]
            return result

    async def upload_race_entries(self, entries_file: Path) -> Dict[str, int]:
        """Upload race entries data"""
        logger.info(f"🏇 Processing race entries from {entries_file}")

        result = {"processed": 0, "inserted": 0, "updated": 0, "failed": 0}

        try:
            # Read and clean data
            df = pd.read_csv(entries_file)
            result["processed"] = len(df)

            # Clean and map data
            df = self.clean_race_entries_data(df)

            async with self.connection_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        query = """
                            INSERT INTO race_entries (
                                race_id, horse_id, horse_number, draw, country,
                                horse_name, age, weight_uk, weight_kg, gears,
                                horse_rate, jockey_id, jockey, trainer_id, trainer,
                                favourite_position, odds, odds_decimal, timeform_comments
                            ) VALUES (
                                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                                $11, $12, $13, $14, $15, $16, $17, $18, $19
                            )
                            ON CONFLICT (race_id, horse_id)
                            DO UPDATE SET
                                horse_number = EXCLUDED.horse_number,
                                draw = EXCLUDED.draw,
                                weight_uk = EXCLUDED.weight_uk,
                                weight_kg = EXCLUDED.weight_kg,
                                odds = EXCLUDED.odds,
                                odds_decimal = EXCLUDED.odds_decimal,
                                updated_at = CURRENT_TIMESTAMP
                        """

                        await conn.execute(query, *row.values)
                        result["inserted"] += 1

                    except Exception as e:
                        logger.error(
                            f"❌ Failed to insert entry race_id={row['race_id']}, horse_id={row['horse_id']}: {e}"
                        )
                        result["failed"] += 1

            logger.info(f"✅ Race entries upload complete: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ Error uploading race entries: {e}")
            result["failed"] = result["processed"]
            return result

    def clean_race_cards_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and map race cards data"""

        # Map column names to database fields
        column_mapping = {
            "Race_ID": "race_id",
            "race_number": "race_number",
            "race_time": "race_time",
            "course_id": "course_id",
            "Course": "course",
            "Race_type": "race_type",
            "Date": "race_date",
            "Race_name": "race_name",
            "Class": "class",
            "Years": "age_restriction",
            "Distance": "distance",
            "Surface": "surface",
            "Prize": "prize",
            "Runners_racecard": "runners_racecard",
            "Runners": "runners",
            "Draw": "draw_info",
            "EW_racecard": "ew_racecard",
            "EW": "ew",
            "Places_EW_racecard": "places_ew_racecard",
            "Places_EW": "places_ew",
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Clean data types
        df["race_id"] = df["race_id"].astype(int)
        df["race_time"] = pd.to_datetime(df["race_date"] + " " + df["race_time"])
        df["race_date"] = pd.to_datetime(df["race_date"])

        # Handle NaN values
        df = df.fillna("")

        # Convert numeric columns
        numeric_columns = [
            "race_number",
            "course_id",
            "runners_racecard",
            "runners",
            "ew_racecard",
            "ew",
            "places_ew_racecard",
            "places_ew",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        return df

    def clean_horses_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and map horses data"""

        # Map column names
        column_mapping = {
            "id": "horse_id",
            "uptodate": "uptodate",
            "state": "state",
            "race_id_last_race": "race_id_last_race",
            "date_last_race": "date_last_race",
            "name": "name",
            "country": "country",
            "age": "age",
            "color": "color",
            "owner": "owner",
            "sire": "sire",
            "dam": "dam",
            "dam_sire": "dam_sire",
            "sex": "sex",
            "Total_races": "total_races",
            "Wins": "wins",
            "Percentage_wins": "percentage_wins",
            "placed": "placed",
            "Percentage_placed": "percentage_placed",
            "Flat_AW_races": "flat_aw_races",
            "Flat_AW_wins": "flat_aw_wins",
            "Flat_AW_rate": "flat_aw_rate",
            "Flat_AW_placed": "flat_aw_placed",
            "Flat_AW_placed_rate": "flat_aw_placed_rate",
            "Flat_Turf_races": "flat_turf_races",
            "Flat_Turf_wins": "flat_turf_wins",
            "Flat_Turf_rate": "flat_turf_rate",
            "Flat_Turf_placed": "flat_turf_placed",
            "Flat_Turf_placed_rate": "flat_turf_placed_rate",
            "Chase_races": "chase_races",
            "Chase_wins": "chase_wins",
            "Chase_rate": "chase_rate",
            "Chase_placed": "chase_placed",
            "Chase_placed_rate": "chase_placed_rate",
            "Hurdle_races": "hurdle_races",
            "Hurdle_wins": "hurdle_wins",
            "Hurdle_rate": "hurdle_rate",
            "Hurdle_placed": "hurdle_placed",
            "Hurdle_placed_rate": "hurdle_placed_rate",
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Clean data types
        df["horse_id"] = df["horse_id"].astype(int)
        df["uptodate"] = pd.to_datetime(df["uptodate"])
        df["date_last_race"] = pd.to_datetime(df["date_last_race"])

        # Handle NaN values
        df = df.fillna("")

        return df

    def clean_race_entries_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and map race entries data"""

        # Map column names
        column_mapping = {
            "race_id": "race_id",
            "Horse_ID": "horse_id",
            "horse_number": "horse_number",
            "Draw": "draw",
            "Country": "country",
            "Name": "horse_name",
            "Age": "age",
            "weight_uk": "weight_uk",
            "weight": "weight_kg",
            "gears": "gears",
            "Horse_rate": "horse_rate",
            "jockey_ID": "jockey_id",
            "jockey": "jockey",
            "trainer_ID": "trainer_id",
            "trainer": "trainer",
            "fav": "favourite_position",
            "odds": "odds",
            "odds_decimal": "odds_decimal",
            "Timeform_comments": "timeform_comments",
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Clean data types
        df["race_id"] = df["race_id"].astype(int)
        df["horse_id"] = df["horse_id"].astype(int)

        # Handle NaN values
        df = df.fillna("")

        # Convert numeric columns
        numeric_columns = [
            "horse_number",
            "draw",
            "age",
            "weight_kg",
            "horse_rate",
            "jockey_id",
            "trainer_id",
            "odds_decimal",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    async def log_data_quality(self, results: Dict[str, Any], processing_time: float):
        """Log data quality metrics"""
        async with self.connection_pool.acquire() as conn:
            for table_name, stats in results.items():
                if isinstance(stats, dict) and "processed" in stats:
                    await conn.execute(
                        """
                        INSERT INTO data_quality_log (
                            table_name, records_processed, records_inserted,
                            records_updated, records_failed, processing_time_ms,
                            data_source, status
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        table_name,
                        stats["processed"],
                        stats["inserted"],
                        stats["updated"],
                        stats["failed"],
                        int(processing_time),
                        "race_cards_upload",
                        "completed",
                    )


async def main():
    """Test the database uploader"""

    cards_data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/cards_data"
    )

    uploader = RaceCardDatabaseUploader()
    results = await uploader.process_race_cards_data(cards_data_dir)

    print("📊 Upload Results:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
