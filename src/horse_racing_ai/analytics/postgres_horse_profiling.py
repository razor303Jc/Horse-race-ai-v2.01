"""
PostgreSQL Horse Profiling System
================================

Advanced horse profiling system using PostgreSQL for horse, race, jockey,
and trainer data. Implements progressive/plateaued/regressive classification
and detailed condition-specific performance analysis.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import logging
import os
import pandas as pd
from enum import Enum
import psycopg2
from sqlalchemy import create_engine
import json

logger = logging.getLogger(__name__)


class HorseFormTrend(Enum):
    """Horse form trend classification."""

    PROGRESSIVE = "progressive"
    PLATEAUED = "plateaued"
    REGRESSIVE = "regressive"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class ConditionProfile:
    """Profile for specific race conditions."""

    condition_name: str
    runs: int
    wins: int
    places: int
    win_rate: float
    place_rate: float
    avg_rating: float
    best_rating: float
    roi: float
    sample_size_adequate: bool


@dataclass
class HorseProfile:
    """Comprehensive horse profile with form trend and condition analysis."""

    horse_id: str
    horse_name: str
    form_trend: HorseFormTrend
    overall_stats: Dict[str, float]

    # Condition-specific profiles
    track_profiles: Dict[str, ConditionProfile]
    distance_profiles: Dict[str, ConditionProfile]
    going_profiles: Dict[str, ConditionProfile]
    class_profiles: Dict[str, ConditionProfile]
    field_size_profiles: Dict[str, ConditionProfile]
    seasonal_profiles: Dict[str, ConditionProfile]

    # Optimal conditions
    preferred_conditions: Dict[str, str]
    optimal_strike_rate: float
    optimal_sample_size: int

    # Profiling metadata
    total_runs: int
    data_quality_score: float
    last_updated: datetime
    confidence_level: str


class PostgreSQLHorseProfilingSystem:
    """
    PostgreSQL-based horse profiling system for identifying optimal race
    conditions and form trends for each horse.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5434,
        database: str = "horse_racing_db",
        user: str = "horse_racing",
        password: str = "secure_password_123",
        min_runs_for_condition: int = 3,
    ):
        """Initialize the PostgreSQL horse profiling system."""
        self.db_config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }

        self.cache_dir = (
            Path(__file__).parent.parent.parent / "ml_cache" / "horse_profiles"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Minimum sample sizes for reliable profiling
        self.min_runs_for_trend = 5
        self.min_runs_for_condition = 3
        self.adequate_sample_size = 8

        self.ensure_profiling_tables()
        logger.info("PostgreSQL Horse Profiling System initialized")

    def get_db_connection(self):
        """Get PostgreSQL database connection."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL: %s", e)
            raise

    def get_sqlalchemy_engine(self):
        """Get SQLAlchemy engine for pandas operations."""
        try:
            connection_string = (
                f"postgresql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}"
                f"/{self.db_config['database']}"
            )
            return create_engine(connection_string)
        except Exception as e:
            logger.error("Failed to create SQLAlchemy engine: %s", e)
            raise

    def ensure_profiling_tables(self):
        """Create horse profiling tables if they don't exist."""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Horse form trend tracking
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS horse_form_trends (
                            id SERIAL PRIMARY KEY,
                            horse_id VARCHAR(50) NOT NULL,
                            horse_name VARCHAR(200) NOT NULL,
                            form_trend VARCHAR(20) NOT NULL,
                            trend_confidence REAL,
                            last_5_ratings JSONB,
                            best_rating REAL,
                            current_rating REAL,
                            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(horse_id)
                        )
                    """
                    )

                    # Horse condition profiles
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS horse_condition_profiles (
                            id SERIAL PRIMARY KEY,
                            horse_id VARCHAR(50) NOT NULL,
                            condition_type VARCHAR(20) NOT NULL,
                            condition_value VARCHAR(100) NOT NULL,
                            runs INTEGER NOT NULL,
                            wins INTEGER NOT NULL,
                            places INTEGER NOT NULL,
                            win_rate REAL NOT NULL,
                            place_rate REAL NOT NULL,
                            avg_rating REAL,
                            best_rating REAL,
                            roi REAL,
                            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(horse_id, condition_type, condition_value)
                        )
                    """
                    )

                    # Optimal conditions for each horse
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS horse_optimal_conditions (
                            id SERIAL PRIMARY KEY,
                            horse_id VARCHAR(50) NOT NULL,
                            optimal_track VARCHAR(100),
                            optimal_distance VARCHAR(20),
                            optimal_going VARCHAR(20),
                            optimal_class VARCHAR(20),
                            optimal_field_size VARCHAR(20),
                            optimal_season VARCHAR(20),
                            optimal_strike_rate REAL,
                            optimal_sample_size INTEGER,
                            confidence_level VARCHAR(20),
                            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(horse_id)
                        )
                    """
                    )

                    conn.commit()
                    logger.info("Horse profiling tables ensured in PostgreSQL")

        except Exception as e:
            logger.error("Failed to create profiling tables: %s", e)
            raise

    def create_profiling_tables(self):
        """Alias for ensure_profiling_tables for backward compatibility."""
        return self.ensure_profiling_tables()

    def classify_horse_form_trend(self, horse_id: str) -> HorseFormTrend:
        """
        Classify horse's form trend as Progressive, Plateaued, or Regressive.
        """
        try:
            engine = self.get_sqlalchemy_engine()
            query = """
                SELECT 
                    r.date as race_date, 
                    rec.or_rating as rating, 
                    rec.position as finishing_position
                FROM records rec
                JOIN races r ON rec.race_id = r.race_id
                WHERE rec.horse_id = %(horse_id)s
                ORDER BY r.date DESC
                LIMIT 10
            """
            df = pd.read_sql_query(query, engine, params={"horse_id": horse_id})

            if len(df) < self.min_runs_for_trend:
                return HorseFormTrend.INSUFFICIENT_DATA

            # Get ratings (use finishing position inverse if no rating)
            ratings = []
            for _, row in df.iterrows():
                if pd.notna(row["rating"]):
                    ratings.append(row["rating"])
                else:
                    # Convert finishing position to approximate rating
                    pos = row["finishing_position"]
                    rating = max(0, 100 - (pos * 5))  # Rough conversion
                    ratings.append(rating)

            if len(ratings) < self.min_runs_for_trend:
                return HorseFormTrend.INSUFFICIENT_DATA

            latest_rating = ratings[0]
            last_5_ratings = ratings[:5]
            best_ever_rating = max(ratings)
            best_in_last_5 = max(last_5_ratings)

            # Progressive: Latest run is best ever
            if latest_rating == best_ever_rating and latest_rating > 0:
                return HorseFormTrend.PROGRESSIVE

            # Regressive: Best performance not in last 5 runs
            if best_in_last_5 < best_ever_rating:
                # Check if there's a significant decline
                recent_avg = sum(last_5_ratings[:3]) / 3  # Last 3 runs average
                if recent_avg < (best_ever_rating * 0.85):  # 15% decline threshold
                    return HorseFormTrend.REGRESSIVE

            # Default to plateaued
            return HorseFormTrend.PLATEAUED

        except (psycopg2.Error, ValueError, KeyError) as e:
            logger.error("Failed to classify form trend for %s: %s", horse_id, e)
            return HorseFormTrend.INSUFFICIENT_DATA

    def analyze_condition_profiles(
        self, horse_id: str, condition_type: str
    ) -> Dict[str, ConditionProfile]:
        """
        Analyze horse performance under specific conditions.
        """
        try:
            engine = self.get_sqlalchemy_engine()

            # Map condition types to database columns
            condition_columns = {
                "track": "r.course",
                "distance": "r.distance",
                "going": "r.surface",
                "class": "r.class",
            }

            if condition_type not in condition_columns:
                logger.error("Unknown condition type: %s", condition_type)
                return {}

            column_name = condition_columns[condition_type]

            query = f"""
                SELECT
                    {column_name} as condition_value,
                    COUNT(*) as runs,
                    SUM(CASE WHEN rec.position = 1 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN rec.position <= 3 THEN 1 ELSE 0 END) as places,
                    AVG(rec.or_rating) as avg_rating,
                    MAX(rec.or_rating) as best_rating
                FROM records rec
                JOIN races r ON rec.race_id = r.race_id
                WHERE rec.horse_id = %(horse_id)s AND {column_name} IS NOT NULL
                GROUP BY {column_name}
                HAVING COUNT(*) >= %(min_runs)s
                ORDER BY runs DESC
            """

            df = pd.read_sql_query(
                query,
                engine,
                params={"horse_id": horse_id, "min_runs": self.min_runs_for_condition},
            )

            profiles = {}

            for _, row in df.iterrows():
                condition_value = str(row["condition_value"])
                runs = int(row["runs"])
                wins = int(row["wins"])
                places = int(row["places"])

                win_rate = (wins / runs) * 100 if runs > 0 else 0
                place_rate = (places / runs) * 100 if runs > 0 else 0

                # Simple ROI estimation
                roi = (win_rate * 2.5) - 100 if win_rate > 0 else -100

                profiles[condition_value] = ConditionProfile(
                    condition_name=condition_value,
                    runs=runs,
                    wins=wins,
                    places=places,
                    win_rate=win_rate,
                    place_rate=place_rate,
                    avg_rating=row["avg_rating"] if pd.notna(row["avg_rating"]) else 0,
                    best_rating=(
                        row["best_rating"] if pd.notna(row["best_rating"]) else 0
                    ),
                    roi=roi,
                    sample_size_adequate=(runs >= self.adequate_sample_size),
                )

            return profiles

        except (psycopg2.Error, ValueError, KeyError) as e:
            logger.error(
                "Failed to analyze %s profiles for %s: %s", condition_type, horse_id, e
            )
            return {}

    def get_progressive_horses(self, min_runs: int = 5) -> List[Dict[str, str]]:
        """Get list of horses currently in progressive form."""
        try:
            engine = self.get_sqlalchemy_engine()

            # Get horses with recent data
            query = """
                SELECT DISTINCT h.horse_id, h.horse_name
                FROM horses h
                INNER JOIN records rec ON h.horse_id = rec.horse_id
                INNER JOIN races r ON rec.race_id = r.race_id
                WHERE r.date >= %(cutoff_date)s
                GROUP BY h.horse_id, h.horse_name
                HAVING COUNT(*) >= %(min_runs)s
                ORDER BY h.horse_name
            """

            cutoff_date = datetime.now() - timedelta(days=365)
            df = pd.read_sql_query(
                query,
                engine,
                params={
                    "cutoff_date": cutoff_date.strftime("%Y-%m-%d"),
                    "min_runs": min_runs,
                },
            )

            progressive_horses = []

            for _, row in df.iterrows():
                horse_id = row["horse_id"]
                horse_name = row["horse_name"]

                form_trend = self.classify_horse_form_trend(horse_id)

                if form_trend == HorseFormTrend.PROGRESSIVE:
                    progressive_horses.append(
                        {
                            "horse_id": horse_id,
                            "horse_name": horse_name,
                            "form_trend": form_trend.value,
                        }
                    )

            return progressive_horses

        except (psycopg2.Error, ValueError) as e:
            logger.error("Failed to get progressive horses: %s", e)
            return []

    def generate_horse_profile(self, horse_id: str) -> Optional[HorseProfile]:
        """Generate comprehensive profile for a horse."""
        try:
            engine = self.get_sqlalchemy_engine()

            # Get horse basic info
            horse_query = """
                SELECT horse_name FROM horses WHERE horse_id = %(horse_id)s
            """
            horse_df = pd.read_sql_query(
                horse_query, engine, params={"horse_id": horse_id}
            )

            if horse_df.empty:
                logger.warning("Horse %s not found", horse_id)
                return None

            horse_name = horse_df.iloc[0]["horse_name"]

            # Get overall stats
            stats_query = """
                SELECT
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN rec.position = 1 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN rec.position <= 3 THEN 1 ELSE 0 END) as places,
                    AVG(rec.or_rating) as avg_rating,
                    MAX(rec.or_rating) as best_rating
                FROM records rec
                WHERE rec.horse_id = %(horse_id)s
            """

            stats_df = pd.read_sql_query(
                stats_query, engine, params={"horse_id": horse_id}
            )
            stats = stats_df.iloc[0] if not stats_df.empty else {}

            total_runs = int(stats.get("total_runs", 0))

            if total_runs < self.min_runs_for_trend:
                logger.warning("Insufficient data for horse %s", horse_id)
                return None

            # Classify form trend
            form_trend = self.classify_horse_form_trend(horse_id)

            # Analyze condition profiles
            track_profiles = self.analyze_condition_profiles(horse_id, "track")
            distance_profiles = self.analyze_condition_profiles(horse_id, "distance")
            going_profiles = self.analyze_condition_profiles(horse_id, "going")
            class_profiles = self.analyze_condition_profiles(horse_id, "class")

            # Find preferred conditions (highest win rate with adequate sample)
            preferred_conditions = {}
            optimal_strike_rate = 0
            optimal_sample_size = 0

            for profile_type, profiles in [
                ("track", track_profiles),
                ("distance", distance_profiles),
                ("going", going_profiles),
                ("class", class_profiles),
            ]:
                if profiles:
                    best_profile = max(
                        profiles.values(),
                        key=lambda p: p.win_rate if p.sample_size_adequate else 0,
                    )
                    if best_profile.sample_size_adequate:
                        preferred_conditions[profile_type] = best_profile.condition_name
                        optimal_strike_rate = max(
                            optimal_strike_rate, best_profile.win_rate
                        )
                        optimal_sample_size += best_profile.runs

            # Calculate data quality score
            data_quality_score = min(1.0, total_runs / 20.0)  # Max quality at 20+ runs

            # Determine confidence level
            if total_runs >= 20 and len(preferred_conditions) >= 3:
                confidence_level = "High"
            elif total_runs >= 10 and len(preferred_conditions) >= 2:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"

            overall_stats = {
                "total_runs": total_runs,
                "wins": int(stats.get("wins", 0)),
                "places": int(stats.get("places", 0)),
                "win_rate": (
                    (int(stats.get("wins", 0)) / total_runs * 100)
                    if total_runs > 0
                    else 0
                ),
                "place_rate": (
                    (int(stats.get("places", 0)) / total_runs * 100)
                    if total_runs > 0
                    else 0
                ),
                "avg_rating": (
                    float(stats.get("avg_rating", 0))
                    if pd.notna(stats.get("avg_rating"))
                    else 0
                ),
                "best_rating": (
                    float(stats.get("best_rating", 0))
                    if pd.notna(stats.get("best_rating"))
                    else 0
                ),
            }

            return HorseProfile(
                horse_id=horse_id,
                horse_name=horse_name,
                form_trend=form_trend,
                overall_stats=overall_stats,
                track_profiles=track_profiles,
                distance_profiles=distance_profiles,
                going_profiles=going_profiles,
                class_profiles=class_profiles,
                field_size_profiles={},  # Not implemented yet
                seasonal_profiles={},  # Not implemented yet
                preferred_conditions=preferred_conditions,
                optimal_strike_rate=optimal_strike_rate,
                optimal_sample_size=optimal_sample_size,
                total_runs=total_runs,
                data_quality_score=data_quality_score,
                last_updated=datetime.now(),
                confidence_level=confidence_level,
            )

        except (psycopg2.Error, ValueError, KeyError) as e:
            logger.error("Failed to generate profile for horse %s: %s", horse_id, e)
            return None

    def save_horse_profile(self, profile: HorseProfile):
        """Save horse profile to PostgreSQL database."""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Save form trend
                    cursor.execute(
                        """
                        INSERT INTO horse_form_trends
                        (horse_id, horse_name, form_trend, trend_confidence,
                         last_5_ratings, best_rating, current_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (horse_id) DO UPDATE SET
                        horse_name = EXCLUDED.horse_name,
                        form_trend = EXCLUDED.form_trend,
                        trend_confidence = EXCLUDED.trend_confidence,
                        last_5_ratings = EXCLUDED.last_5_ratings,
                        best_rating = EXCLUDED.best_rating,
                        current_rating = EXCLUDED.current_rating,
                        calculated_at = CURRENT_TIMESTAMP
                    """,
                        (
                            profile.horse_id,
                            profile.horse_name,
                            profile.form_trend.value,
                            profile.data_quality_score,
                            json.dumps([]),  # Placeholder for last 5 ratings
                            profile.overall_stats.get("best_rating", 0),
                            profile.overall_stats.get("avg_rating", 0),
                        ),
                    )

                    # Save optimal conditions
                    cursor.execute(
                        """
                        INSERT INTO horse_optimal_conditions
                        (horse_id, optimal_track, optimal_distance, optimal_going,
                         optimal_class, optimal_strike_rate, optimal_sample_size,
                         confidence_level)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (horse_id) DO UPDATE SET
                        optimal_track = EXCLUDED.optimal_track,
                        optimal_distance = EXCLUDED.optimal_distance,
                        optimal_going = EXCLUDED.optimal_going,
                        optimal_class = EXCLUDED.optimal_class,
                        optimal_strike_rate = EXCLUDED.optimal_strike_rate,
                        optimal_sample_size = EXCLUDED.optimal_sample_size,
                        confidence_level = EXCLUDED.confidence_level,
                        calculated_at = CURRENT_TIMESTAMP
                    """,
                        (
                            profile.horse_id,
                            profile.preferred_conditions.get("track"),
                            profile.preferred_conditions.get("distance"),
                            profile.preferred_conditions.get("going"),
                            profile.preferred_conditions.get("class"),
                            profile.optimal_strike_rate,
                            profile.optimal_sample_size,
                            profile.confidence_level,
                        ),
                    )

                    conn.commit()
                    logger.info("Saved profile for horse %s", profile.horse_id)

        except Exception as e:
            logger.error("Failed to save profile for horse %s: %s", profile.horse_id, e)
            raise


# Global instance for easy import
postgres_horse_profiling = PostgreSQLHorseProfilingSystem()
