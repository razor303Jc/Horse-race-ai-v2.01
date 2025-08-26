"""
Horse Profiling System
=====================

Advanced horse profiling system implementing progressive/plateaued/regressive
classification and detailed condition-specific performance analysis.

Based on concepts from:
- bet4bettor.com/profiling-racehorse-performance/
- informracing.com/horse-profiling-find-the-preferred-race-conditions-for-every-horse/
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
import os
import pandas as pd
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

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


class HorseProfilingSystem:
    """
    Advanced horse profiling system for identifying optimal race conditions
    and form trends for each horse.
    """

    def __init__(self, db_config: Dict[str, str] = None):
        """Initialize the horse profiling system with PostgreSQL."""
        if db_config is None:
            self.db_config = {
                "host": os.getenv("POSTGRES_HOST", "postgres"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "database": os.getenv("POSTGRES_DB", "cards_horse_racing_db"),
                "user": os.getenv("POSTGRES_USER", "horse_racing"),
                "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
            }
        else:
            self.db_config = db_config

        self.cache_dir = (
            Path(__file__).parent.parent.parent / "ml_cache" / "horse_profiles"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ensure_profiling_tables()

        # Minimum sample sizes for reliable profiling
        self.min_runs_for_trend = 5
        self.min_runs_for_condition = 3
        self.adequate_sample_size = 8
        logger.info("Horse Profiling System initialized with PostgreSQL")

    def get_db_connection(self):
        """Get PostgreSQL database connection."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
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
            logger.error(f"Failed to create SQLAlchemy engine: {e}")
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
            logger.error(f"Failed to create profiling tables: {e}")

    def classify_horse_form_trend(self, horse_id: str) -> HorseFormTrend:
        """
        Classify horse's form trend as Progressive, Plateaued, or Regressive.

        Progressive: Best-ever performance on latest outing
        Plateaued: Best performance in last 5 runs (not latest)
        Regressive: Not run to best rating in last 5 runs
        """
        try:
            # Get horse's last 10 race results with ratings
            engine = self.get_sqlalchemy_engine()
            query = """
                SELECT race_date, rating, finishing_position
                FROM records
                WHERE horse_id = %s
                ORDER BY race_date DESC
                LIMIT 10
            """
            df = pd.read_sql_query(query, engine, params=[horse_id])

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

            # Plateaued: Consistent form, best in last 5 but not latest
            if best_in_last_5 == best_ever_rating and latest_rating != best_in_last_5:
                return HorseFormTrend.PLATEAUED

            # Default classification based on recent consistency
            if len(last_5_ratings) >= 3:
                variance = pd.Series(last_5_ratings[:3]).var()
                if variance < 100:  # Low variance = consistent = plateaued
                    return HorseFormTrend.PLATEAUED
                elif ratings[0] > ratings[1]:  # Latest better than previous
                    return HorseFormTrend.PROGRESSIVE
                else:
                    return HorseFormTrend.REGRESSIVE

            return HorseFormTrend.PLATEAUED

        except Exception as e:
            logger.error(f"Failed to classify form trend for horse {horse_id}: {e}")
            return HorseFormTrend.INSUFFICIENT_DATA

    def analyze_condition_performance(
        self, horse_id: str, condition_type: str
    ) -> Dict[str, ConditionProfile]:
        """
        Analyze horse's performance under different conditions.

        Args:
            horse_id: Horse identifier
            condition_type: Type of condition (track, distance, going, class, etc.)
        """
        try:
            engine = self.get_sqlalchemy_engine()
            # Map condition types to database columns
            condition_columns = {
                "track": "track",
                "distance": "distance",
                "going": "going",
                "class": "race_class",
                "field_size": "CASE WHEN field_size <= 8 THEN 'Small (≤8)' "
                "WHEN field_size <= 12 THEN 'Medium (9-12)' "
                "ELSE 'Large (13+)' END",
                "season": "CASE WHEN EXTRACT(month FROM race_date) IN (3,4,5) THEN 'Spring' "
                "WHEN EXTRACT(month FROM race_date) IN (6,7,8) THEN 'Summer' "
                "WHEN EXTRACT(month FROM race_date) IN (9,10,11) THEN 'Autumn' "
                "ELSE 'Winter' END",
            }

            if condition_type not in condition_columns:
                logger.error(f"Unknown condition type: {condition_type}")
                return {}

            column_expr = condition_columns[condition_type]

            query = f"""
                SELECT 
                    {column_expr} as condition_value,
                    COUNT(*) as runs,
                    SUM(CASE WHEN finishing_position = 1 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN finishing_position <= 3 THEN 1 ELSE 0 END) as places,
                    AVG(rating) as avg_rating,
                    MAX(rating) as best_rating,
                    AVG(CASE WHEN finishing_position = 1 THEN odds ELSE 0 END) as avg_winning_odds
                FROM records 
                WHERE horse_id = %s AND {column_expr} IS NOT NULL
                GROUP BY {column_expr}
                HAVING COUNT(*) >= %s
                ORDER BY runs DESC
            """

            df = pd.read_sql_query(
                query, engine, params=[horse_id, self.min_runs_for_condition]
            )

            profiles = {}

            for _, row in df.iterrows():
                condition_value = str(row["condition_value"])
                runs = int(row["runs"])
                wins = int(row["wins"])
                places = int(row["places"])

                win_rate = (wins / runs) * 100 if runs > 0 else 0
                place_rate = (places / runs) * 100 if runs > 0 else 0

                # Calculate ROI (rough estimate)
                avg_winning_odds = (
                    row["avg_winning_odds"] if pd.notna(row["avg_winning_odds"]) else 0
                )
                roi = (
                    ((wins * avg_winning_odds) - runs) / runs * 100
                    if runs > 0 and avg_winning_odds > 0
                    else 0
                )

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
                    sample_size_adequate=runs >= self.adequate_sample_size,
                )

            return profiles

        except Exception as e:
            logger.error(
                f"Failed to analyze {condition_type} performance for horse {horse_id}: {e}"
            )
            return {}

    def find_optimal_conditions(
        self, horse_id: str
    ) -> Tuple[Dict[str, str], float, int]:
        """
        Find the optimal race conditions for a horse by analyzing
        combinations of factors that produce the highest strike rate.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get all race data for the horse
                query = """
                    SELECT track, distance, going, race_class, field_size,
                           strftime('%m', race_date) as month,
                           finishing_position, rating, odds
                    FROM race_results 
                    WHERE horse_id = ?
                    ORDER BY race_date DESC
                """
                df = pd.read_sql_query(query, conn, params=[horse_id])

            if len(df) < self.adequate_sample_size:
                return {}, 0.0, 0

            # Find individual optimal conditions
            optimal_conditions = {}

            # Track
            track_performance = (
                df.groupby("track")
                .agg({"finishing_position": ["count", lambda x: (x == 1).sum()]})
                .round(2)
            )
            track_performance.columns = ["runs", "wins"]
            track_performance["win_rate"] = (
                track_performance["wins"] / track_performance["runs"]
            ) * 100
            track_performance = track_performance[
                track_performance["runs"] >= self.min_runs_for_condition
            ]

            if not track_performance.empty:
                best_track = track_performance["win_rate"].idxmax()
                optimal_conditions["track"] = best_track

            # Distance
            distance_performance = (
                df.groupby("distance")
                .agg({"finishing_position": ["count", lambda x: (x == 1).sum()]})
                .round(2)
            )
            distance_performance.columns = ["runs", "wins"]
            distance_performance["win_rate"] = (
                distance_performance["wins"] / distance_performance["runs"]
            ) * 100
            distance_performance = distance_performance[
                distance_performance["runs"] >= self.min_runs_for_condition
            ]

            if not distance_performance.empty:
                best_distance = distance_performance["win_rate"].idxmax()
                optimal_conditions["distance"] = str(best_distance)

            # Going
            going_performance = (
                df.groupby("going")
                .agg({"finishing_position": ["count", lambda x: (x == 1).sum()]})
                .round(2)
            )
            going_performance.columns = ["runs", "wins"]
            going_performance["win_rate"] = (
                going_performance["wins"] / going_performance["runs"]
            ) * 100
            going_performance = going_performance[
                going_performance["runs"] >= self.min_runs_for_condition
            ]

            if not going_performance.empty:
                best_going = going_performance["win_rate"].idxmax()
                optimal_conditions["going"] = best_going

            # Class
            class_performance = (
                df.groupby("race_class")
                .agg({"finishing_position": ["count", lambda x: (x == 1).sum()]})
                .round(2)
            )
            class_performance.columns = ["runs", "wins"]
            class_performance["win_rate"] = (
                class_performance["wins"] / class_performance["runs"]
            ) * 100
            class_performance = class_performance[
                class_performance["runs"] >= self.min_runs_for_condition
            ]

            if not class_performance.empty:
                best_class = class_performance["win_rate"].idxmax()
                optimal_conditions["class"] = str(best_class)

            # Calculate combined optimal strike rate
            if optimal_conditions:
                # Filter for races matching optimal conditions
                filtered_df = df.copy()
                for condition, value in optimal_conditions.items():
                    if condition == "track":
                        filtered_df = filtered_df[filtered_df["track"] == value]
                    elif condition == "distance":
                        filtered_df = filtered_df[filtered_df["distance"] == int(value)]
                    elif condition == "going":
                        filtered_df = filtered_df[filtered_df["going"] == value]
                    elif condition == "class":
                        filtered_df = filtered_df[
                            filtered_df["race_class"] == int(value)
                        ]

                if len(filtered_df) > 0:
                    optimal_wins = (filtered_df["finishing_position"] == 1).sum()
                    optimal_runs = len(filtered_df)
                    optimal_strike_rate = (optimal_wins / optimal_runs) * 100
                    return optimal_conditions, optimal_strike_rate, optimal_runs

            return {}, 0.0, 0

        except Exception as e:
            logger.error(f"Failed to find optimal conditions for horse {horse_id}: {e}")
            return {}, 0.0, 0

    def generate_horse_profile(
        self, horse_id: str, horse_name: str = None
    ) -> HorseProfile:
        """Generate comprehensive profile for a horse."""
        try:
            # Get overall statistics
            with sqlite3.connect(self.db_path) as conn:
                overall_query = """
                    SELECT 
                        COUNT(*) as total_runs,
                        SUM(CASE WHEN finishing_position = 1 THEN 1 ELSE 0 END) as wins,
                        SUM(CASE WHEN finishing_position <= 3 THEN 1 ELSE 0 END) as places,
                        AVG(rating) as avg_rating,
                        MAX(rating) as best_rating,
                        MIN(race_date) as first_run,
                        MAX(race_date) as last_run
                    FROM race_results 
                    WHERE horse_id = ?
                """
                overall_df = pd.read_sql_query(overall_query, conn, params=[horse_id])

            if overall_df.empty or overall_df.iloc[0]["total_runs"] == 0:
                logger.warning(f"No race data found for horse {horse_id}")
                return None

            stats = overall_df.iloc[0]
            overall_stats = {
                "total_runs": int(stats["total_runs"]),
                "wins": int(stats["wins"]),
                "places": int(stats["places"]),
                "win_rate": (
                    (stats["wins"] / stats["total_runs"]) * 100
                    if stats["total_runs"] > 0
                    else 0
                ),
                "place_rate": (
                    (stats["places"] / stats["total_runs"]) * 100
                    if stats["total_runs"] > 0
                    else 0
                ),
                "avg_rating": (
                    stats["avg_rating"] if pd.notna(stats["avg_rating"]) else 0
                ),
                "best_rating": (
                    stats["best_rating"] if pd.notna(stats["best_rating"]) else 0
                ),
            }

            # Classify form trend
            form_trend = self.classify_horse_form_trend(horse_id)

            # Analyze condition-specific performance
            track_profiles = self.analyze_condition_performance(horse_id, "track")
            distance_profiles = self.analyze_condition_performance(horse_id, "distance")
            going_profiles = self.analyze_condition_performance(horse_id, "going")
            class_profiles = self.analyze_condition_performance(horse_id, "class")
            field_size_profiles = self.analyze_condition_performance(
                horse_id, "field_size"
            )
            seasonal_profiles = self.analyze_condition_performance(horse_id, "season")

            # Find optimal conditions
            preferred_conditions, optimal_strike_rate, optimal_sample_size = (
                self.find_optimal_conditions(horse_id)
            )

            # Calculate data quality score
            data_quality_score = min(
                100, (stats["total_runs"] / 20) * 100
            )  # 20 runs = 100% quality

            # Determine confidence level
            if stats["total_runs"] >= 20:
                confidence_level = "High"
            elif stats["total_runs"] >= 10:
                confidence_level = "Medium"
            elif stats["total_runs"] >= 5:
                confidence_level = "Low"
            else:
                confidence_level = "Very Low"

            return HorseProfile(
                horse_id=horse_id,
                horse_name=horse_name or f"Horse_{horse_id}",
                form_trend=form_trend,
                overall_stats=overall_stats,
                track_profiles=track_profiles,
                distance_profiles=distance_profiles,
                going_profiles=going_profiles,
                class_profiles=class_profiles,
                field_size_profiles=field_size_profiles,
                seasonal_profiles=seasonal_profiles,
                preferred_conditions=preferred_conditions,
                optimal_strike_rate=optimal_strike_rate,
                optimal_sample_size=optimal_sample_size,
                total_runs=int(stats["total_runs"]),
                data_quality_score=data_quality_score,
                last_updated=datetime.now(),
                confidence_level=confidence_level,
            )

        except Exception as e:
            logger.error(f"Failed to generate profile for horse {horse_id}: {e}")
            return None

    def get_progressive_horses(self, min_runs: int = 5) -> List[Dict]:
        """Get list of horses with progressive form trends."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get horses with sufficient recent runs
                query = """
                    SELECT DISTINCT horse_id, 
                           COUNT(*) as total_runs,
                           MAX(race_date) as last_run_date
                    FROM race_results 
                    WHERE race_date >= date('now', '-90 days')
                    GROUP BY horse_id
                    HAVING COUNT(*) >= ?
                    ORDER BY total_runs DESC
                """
                df = pd.read_sql_query(query, conn, params=[min_runs])

            progressive_horses = []

            for _, row in df.iterrows():
                horse_id = row["horse_id"]
                form_trend = self.classify_horse_form_trend(horse_id)

                if form_trend == HorseFormTrend.PROGRESSIVE:
                    progressive_horses.append(
                        {
                            "horse_id": horse_id,
                            "total_runs": row["total_runs"],
                            "last_run_date": row["last_run_date"],
                            "form_trend": form_trend.value,
                        }
                    )

            return progressive_horses

        except Exception as e:
            logger.error(f"Failed to get progressive horses: {e}")
            return []

    def save_horse_profile(self, profile: HorseProfile):
        """Save horse profile to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Save form trend
                conn.execute(
                    """
                    INSERT OR REPLACE INTO horse_form_trends 
                    (horse_id, horse_name, form_trend, trend_confidence, 
                     best_rating, current_rating)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.horse_id,
                        profile.horse_name,
                        profile.form_trend.value,
                        profile.data_quality_score / 100,
                        profile.overall_stats["best_rating"],
                        profile.overall_stats["avg_rating"],
                    ),
                )

                # Save optimal conditions
                conn.execute(
                    """
                    INSERT OR REPLACE INTO horse_optimal_conditions
                    (horse_id, optimal_track, optimal_distance, optimal_going,
                     optimal_class, optimal_strike_rate, optimal_sample_size,
                     confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        except Exception as e:
            logger.error(f"Failed to save profile for horse {profile.horse_id}: {e}")


# Global instance for easy import
horse_profiling_system = HorseProfilingSystem()
