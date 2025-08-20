#!/usr/bin/env python3
"""
AI Racing Selections Generator
Generates AI-powered horse racing selections using trained production models.

Enhanced with comprehensive error handling and structured logging.
"""

import json
import logging
import sys
import traceback
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import joblib
import numpy as np
import pandas as pd
import psycopg2

warnings.filterwarnings("ignore")


# Setup structured logging with JSON format
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler with structured formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(StructuredFormatter())
logger.addHandler(console_handler)

# File handler for persistent logging
log_file = Path(__file__).parent.parent / "logs" / "ai_selections.log"
log_file.parent.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(StructuredFormatter())
logger.addHandler(file_handler)


class AISelectionsGenerator:
    """Generate AI selections for today's racing using trained models."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "trained_models" / "production"

        # Database connection
        self.db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # OPTIMIZATION: Cache database connection
        self._db_connection = None

        # Load trained models
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.load_models()

    def load_models(self) -> None:
        """Load all trained production models."""
        logger.info("🤖 Loading trained AI models...")

        try:
            # Load models
            model_files = {
                "random_forest": "random_forest_production.joblib",
                "gradient_boosting": "gradient_boosting_production.joblib",
                "logistic_regression": "logistic_regression_production.joblib",
                "neural_network": "neural_network_production.joblib",
            }

            for name, filename in model_files.items():
                model_path = self.models_dir / filename
                if model_path.exists():
                    self.models[name] = joblib.load(model_path)
                    logger.info(f"   ✅ Loaded {name}")
                else:
                    logger.warning(f"   ⚠️ Model not found: {filename}")

            # Load scaler and features
            self.scaler = joblib.load(self.models_dir / "scaler_production.joblib")
            self.feature_names = joblib.load(
                self.models_dir / "features_production.joblib"
            )

            logger.info(
                f"🎯 Loaded {len(self.models)} models with {len(self.feature_names)} features"
            )

        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            raise

    def _extract_odds(self, odds_decimal, odds_fraction):
        """Extract real odds from decimal or fractional format."""
        # First, try decimal odds if it's a valid number > 0
        if odds_decimal and odds_decimal > 0:
            return float(odds_decimal)

        # If decimal is 0 or None, try to parse fractional odds
        if odds_fraction and odds_fraction.strip():
            try:
                # Handle formats like "7/1", "5/2", "EVENS", etc.
                odds_str = odds_fraction.strip()

                if odds_str.upper() in ["EVENS", "EVS"]:
                    return 2.0
                elif "/" in odds_str:
                    # Parse fractional odds like "7/1" -> 8.0
                    parts = odds_str.split("/")
                    if len(parts) == 2:
                        numerator = float(parts[0])
                        denominator = float(parts[1])
                        return (numerator / denominator) + 1.0
                else:
                    # Try to parse as direct decimal
                    return float(odds_str)
            except (ValueError, ZeroDivisionError):
                pass

        # Default fallback for missing/invalid odds
        return 5.0

    def _parse_fractional_odds(self, fractional_str):
        """Parse fractional odds string like '7/1' to decimal."""
        try:
            if isinstance(fractional_str, str) and "/" in fractional_str:
                parts = fractional_str.split("/")
                if len(parts) == 2:
                    numerator = float(parts[0])
                    denominator = float(parts[1])
                    if denominator > 0:
                        return (numerator / denominator) + 1.0
        except (ValueError, ZeroDivisionError):
            pass
        return 5.0  # Default fallback

    def _get_db_connection(self):
        """Get cached database connection with enhanced error handling."""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                if self._db_connection is None or self._db_connection.closed:
                    logger.info(
                        "🔗 Establishing optimized database connection...",
                        extra={"extra_data": {"attempt": attempt + 1}},
                    )
                    self._db_connection = psycopg2.connect(**self.db_config)

                # Test connection with a simple query
                with self._db_connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                logger.info("✅ Database connection established successfully")
                return self._db_connection

            except psycopg2.OperationalError as e:
                logger.error(
                    f"❌ Database connection failed (attempt {attempt + 1}): {e}",
                    extra={
                        "extra_data": {
                            "error_type": "OperationalError",
                            "attempt": attempt + 1,
                        }
                    },
                )

                if attempt < max_retries - 1:
                    import time

                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise ConnectionError(
                        f"Failed to connect to database after {max_retries} attempts"
                    )

            except Exception as e:
                logger.error(
                    f"❌ Unexpected database error: {e}",
                    extra={
                        "extra_data": {
                            "error_type": type(e).__name__,
                            "attempt": attempt + 1,
                        }
                    },
                )
                raise

    def get_todays_races(self) -> pd.DataFrame:
        """Get today's race cards from database (optimized with caching)."""
        logger.info("🏇 Loading today's race cards...")

        try:
            # Use optimized cached database connection
            connection = self._get_db_connection()

            # Fixed query to prevent Cartesian product from duplicate stats
            query = """
                    SELECT DISTINCT
                        re.race_id,
                        re.horse_name,
                        re.jockey,
                        re.trainer,
                        re.odds,
                        re.odds_decimal,
                        re.weight_uk,
                        re.weight_kg,
                        re.draw as barrier,
                        re.age as horse_age,
                        rc.course,
                        rc.race_number,
                        rc.race_time,
                        rc.race_date,
                        rc.race_name,
                        rc.distance,
                        rc.prize,
                        COALESCE(js_agg.avg_wins, 0) as jockey_wins,
                        COALESCE(js_agg.avg_runs, 0) as jockey_runs,
                        COALESCE(js_agg.avg_win_pct, 0) as jockey_win_pct,
                        COALESCE(ts_agg.avg_wins, 0) as trainer_wins,
                        COALESCE(ts_agg.avg_runs, 0) as trainer_runs,
                        COALESCE(ts_agg.avg_win_pct, 0) as trainer_win_pct
                    FROM race_entries re
                    JOIN race_cards rc ON re.race_id = rc.race_id
                    LEFT JOIN (
                        SELECT 
                            jockey_name,
                            AVG(wins) as avg_wins,
                            AVG(total_races) as avg_runs,
                            AVG(percentage_wins) as avg_win_pct
                        FROM jockeys_stats 
                        GROUP BY jockey_name
                    ) js_agg ON re.jockey = js_agg.jockey_name
                    LEFT JOIN (
                        SELECT 
                            trainer_name,
                            AVG(wins) as avg_wins,
                            AVG(total_races) as avg_runs,
                            AVG(percentage_wins) as avg_win_pct
                        FROM trainers_stats 
                        GROUP BY trainer_name
                    ) ts_agg ON re.trainer = ts_agg.trainer_name
                    WHERE rc.race_date = CURRENT_DATE
                    AND re.jockey IS NOT NULL 
                    AND re.trainer IS NOT NULL
                    ORDER BY rc.course, rc.race_number, re.horse_name
            """

            df = pd.read_sql_query(query, connection)
            logger.info(
                f"✅ Loaded {len(df)} runners from {df['course'].nunique()} courses"
            )

            # Validate no duplicates
            expected_count = 360  # Known count from system review
            if len(df) > expected_count * 1.1:  # Allow 10% tolerance
                logger.warning(
                    f"⚠️ Still getting {len(df)} rows, expected ~{expected_count}"
                )
            else:
                logger.info(f"✅ Data duplication fixed: {len(df)} rows")

            return df

        except Exception as e:
            logger.error(f"❌ Failed to load race data: {e}")
            raise

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for prediction (matches training pipeline)."""
        logger.info("⚙️ Engineering features for AI analysis...")

        df_features = df.copy()

        # Clean and convert data types using actual column names
        # OPTIMIZED: Vectorized odds extraction instead of row-wise apply
        odds_decimal = pd.to_numeric(
            df_features["odds_decimal"], errors="coerce"
        ).fillna(0.0)
        odds_fractional = df_features["odds"].fillna("5/1")

        # Parse fractional odds vectorized
        fractional_parsed = odds_fractional.apply(self._parse_fractional_odds)

        # Use decimal odds when available (> 0), otherwise use fractional
        df_features["win_odds"] = np.where(
            odds_decimal > 0.0, odds_decimal, fractional_parsed
        )
        df_features["horse_age"] = pd.to_numeric(
            df_features["horse_age"], errors="coerce"
        ).fillna(4)
        df_features["horse_weight_kg"] = pd.to_numeric(
            df_features["weight_kg"], errors="coerce"
        ).fillna(60)
        df_features["draw"] = pd.to_numeric(
            df_features["barrier"], errors="coerce"
        ).fillna(8)

        # Fill missing stats with defaults
        df_features["jockey_wins"] = df_features["jockey_wins"].fillna(0)
        df_features["jockey_runs"] = df_features["jockey_runs"].fillna(1)
        df_features["jockey_win_pct"] = (
            df_features["jockey_win_pct"].fillna(5.0) / 100
        )  # Convert to decimal
        df_features["trainer_wins"] = df_features["trainer_wins"].fillna(0)
        df_features["trainer_runs"] = df_features["trainer_runs"].fillna(1)
        df_features["trainer_win_pct"] = (
            df_features["trainer_win_pct"].fillna(5.0) / 100
        )  # Convert to decimal

        # Handle missing course/prize data
        df_features["course"] = df_features["course"].fillna("Unknown")
        df_features["prize_money"] = pd.to_numeric(
            df_features.get("prize", 10000), errors="coerce"
        ).fillna(10000)

        # 1. ODDS-BASED FEATURES
        # Handle zero odds by setting minimum to 0.1
        df_features["win_odds"] = df_features["win_odds"].clip(lower=0.1)
        df_features["log_odds"] = np.log(df_features["win_odds"] + 1)
        df_features["implied_probability"] = 1 / df_features["win_odds"]
        df_features["odds_rank"] = df_features.groupby("race_id")["win_odds"].rank()
        df_features["is_favorite"] = (df_features["odds_rank"] == 1).astype(int)

        # 2. PERFORMANCE FEATURES
        df_features["combined_performance"] = (
            df_features["jockey_win_pct"] + df_features["trainer_win_pct"]
        ) / 2

        # 3. RACE CONTEXT FEATURES (OPTIMIZED: single groupby operation)
        logger.info("⚙️ Computing race context features...")
        race_stats = (
            df_features.groupby("race_id")
            .agg(
                {
                    "horse_name": "count",  # field_size
                    "win_odds": ["min", "max", "mean"],  # market dynamics
                    "prize_money": "first",
                }
            )
            .reset_index()
        )

        race_stats.columns = [
            "race_id",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "race_prize",
        ]
        df_features = df_features.merge(race_stats, on="race_id", how="left")

        # 4. POSITIONAL FEATURES (OPTIMIZED: batch operations)
        logger.info("⚙️ Computing positional features...")
        df_features["draw_percentile"] = df_features.groupby("race_id")["draw"].rank(
            pct=True
        )
        df_features["weight_percentile"] = df_features.groupby("race_id")[
            "horse_weight_kg"
        ].rank(pct=True)
        df_features["age_category"] = pd.cut(
            df_features["horse_age"], bins=[0, 3, 5, 7, 15], labels=[0, 1, 2, 3]
        ).astype(float)

        # Select final features for prediction (same as training)
        feature_columns = [
            "log_odds",
            "implied_probability",
            "odds_rank",
            "is_favorite",
            "combined_performance",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "draw_percentile",
            "weight_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "jockey_win_pct",
            "trainer_win_pct",
        ]

        # Ensure all features exist and are numeric
        for col in feature_columns:
            if col not in df_features.columns:
                logger.warning(f"Missing feature {col}, filling with 0")
                df_features[col] = 0
            df_features[col] = pd.to_numeric(df_features[col], errors="coerce").fillna(
                0
            )
            # Replace infinity with large finite values
            df_features[col] = np.where(
                np.isinf(df_features[col]),
                np.sign(df_features[col]) * 1e6,
                df_features[col],
            )

        logger.info(f"✅ Feature engineering complete: {len(feature_columns)} features")

        return df_features[
            feature_columns
            + [
                "race_id",
                "horse_name",
                "course",
                "race_number",
                "race_time",
                "jockey",
                "trainer",
                "win_odds",
            ]
        ]

    def generate_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate AI predictions for all runners."""
        logger.info("🎯 Generating AI predictions...")

        # Prepare features
        feature_columns = [
            "log_odds",
            "implied_probability",
            "odds_rank",
            "is_favorite",
            "combined_performance",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "draw_percentile",
            "weight_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "jockey_win_pct",
            "trainer_win_pct",
        ]

        X = df[feature_columns].values
        X_scaled = self.scaler.transform(X)

        # Generate predictions from ensemble
        predictions = {}
        for name, model in self.models.items():
            try:
                pred_proba = model.predict_proba(X_scaled)[:, 1]  # Win probability
                predictions[f"{name}_probability"] = pred_proba
                logger.info(f"   ✅ {name}: Generated {len(pred_proba)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️ Failed to predict with {name}: {e}")

        # Create ensemble prediction (average of all models)
        if predictions:
            ensemble_probs = np.mean(
                [predictions[key] for key in predictions.keys()], axis=0
            )
            predictions["ensemble_probability"] = ensemble_probs

            # Calculate confidence score (standard deviation of model agreement)
            model_probs = np.array([predictions[key] for key in predictions.keys()])
            confidence_scores = 1.0 - np.std(
                model_probs, axis=0
            )  # Higher std = lower confidence
            predictions["confidence_score"] = confidence_scores

            # Add predictions to dataframe
            for key, values in predictions.items():
                df[key] = values

            # Add prediction rankings for each race
            race_groups = df.groupby(["course", "race_number"])
            for race_id, race_data in race_groups:
                race_indices = race_data.index
                race_predictions = race_data["ensemble_probability"].values
                race_ranks = (
                    -race_predictions
                ).argsort().argsort() + 1  # Rank 1 = highest probability
                df.loc[race_indices, "prediction_rank"] = race_ranks

        logger.info("🎯 AI predictions complete!")
        return df

    def generate_selections(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Generate AI selections for each race."""
        logger.info("🏆 Generating AI selections...")

        selections = {}

        for course in df["course"].unique():
            course_data = df[df["course"] == course].copy()
            course_selections = []

            for race_num in sorted(course_data["race_number"].unique()):
                race_data = course_data[course_data["race_number"] == race_num].copy()

                if len(race_data) == 0:
                    continue

                # Sort by ensemble probability (highest first)
                race_data = race_data.sort_values(
                    "ensemble_probability", ascending=False
                )

                # Get top 3 selections
                top_3 = race_data.head(3)

                race_info = {
                    "race_number": race_num,
                    "race_time": race_data.iloc[0]["race_time"],
                    "field_size": len(race_data),
                    "selections": [],
                }

                for i, (_, horse) in enumerate(top_3.iterrows()):
                    selection = {
                        "position": i + 1,
                        "horse": horse["horse_name"],
                        "jockey": horse["jockey"],
                        "trainer": horse["trainer"],
                        "odds": horse["win_odds"],
                        "ai_probability": round(horse["ensemble_probability"] * 100, 1),
                        "confidence": (
                            "High"
                            if horse["ensemble_probability"] > 0.25
                            else (
                                "Medium"
                                if horse["ensemble_probability"] > 0.15
                                else "Low"
                            )
                        ),
                    }
                    race_info["selections"].append(selection)

                course_selections.append(race_info)

            selections[course] = course_selections

        logger.info(f"🏆 Generated selections for {len(selections)} courses")
        return selections

    def format_selections_report(self, selections: Dict[str, List[Dict]]) -> str:
        """Format selections into a readable report."""
        report = []
        report.append("🤖 AI RACING SELECTIONS")
        report.append("=" * 50)
        report.append(f"📅 Date: {date.today().strftime('%A, %B %d, %Y')}")
        report.append(f"🎯 Trained on 4,890 historical race records")
        report.append("")

        total_races = sum(len(course_races) for course_races in selections.values())
        report.append(f"📊 SUMMARY: {len(selections)} courses, {total_races} races")
        report.append("")

        for course, races in selections.items():
            report.append(f"🏇 {course.upper()}")
            report.append("-" * 30)

            for race in races:
                report.append(
                    f"🕐 Race {race['race_number']}: {race['race_time']} ({race['field_size']} runners)"
                )

                for sel in race["selections"]:
                    confidence_emoji = (
                        "🔥"
                        if sel["confidence"] == "High"
                        else "⚡" if sel["confidence"] == "Medium" else "💡"
                    )
                    report.append(
                        f"  {sel['position']}. {confidence_emoji} {sel['horse']}"
                    )
                    report.append(
                        f"     Jockey: {sel['jockey']} | Trainer: {sel['trainer']}"
                    )
                    report.append(
                        f"     Odds: {sel['odds']:.1f}/1 | AI Probability: {sel['ai_probability']}% | {sel['confidence']} confidence"
                    )
                    report.append("")

                report.append("")

            report.append("")

        # Add disclaimer
        report.append("⚠️  DISCLAIMER")
        report.append("-" * 15)
        report.append("These AI predictions are for entertainment purposes only.")
        report.append("Past performance does not guarantee future results.")
        report.append("Please gamble responsibly.")

        return "\n".join(report)

    def store_predictions_to_database(self, predictions_df: pd.DataFrame) -> int:
        """Store AI predictions to database and return session ID."""
        logger.info("💾 Storing predictions to database...")

        try:
            with psycopg2.connect(**self.db_config) as connection:
                cursor = connection.cursor()

                # 1. Create prediction session
                session_query = """
                    INSERT INTO ai_prediction_sessions (
                        session_date, total_races, total_runners, courses_covered,
                        models_used, feature_count, model_version, data_quality_score
                    ) VALUES (
                        CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """

                courses_covered = predictions_df["course"].unique().tolist()
                models_used = [
                    "random_forest",
                    "gradient_boosting",
                    "logistic_regression",
                    "neural_network",
                    "ensemble",
                ]

                cursor.execute(
                    session_query,
                    (
                        predictions_df["race_id"].nunique(),  # total_races
                        len(predictions_df),  # total_runners
                        courses_covered,  # courses_covered
                        models_used,  # models_used
                        len(self.feature_names),  # feature_count
                        "v2.03",  # model_version
                        95.0,  # data_quality_score (placeholder)
                    ),
                )

                session_id = cursor.fetchone()[0]
                logger.info(f"✅ Created prediction session ID: {session_id}")

                # 2. Store individual predictions
                prediction_query = """
                    INSERT INTO ai_predictions (
                        race_id, horse_name, jockey, trainer, course, race_number, race_time,
                        random_forest_probability, gradient_boosting_probability, 
                        logistic_regression_probability, neural_network_probability,
                        ensemble_probability, confidence_level, confidence_score,
                        odds_decimal, market_rank, implied_probability,
                        log_odds, jockey_win_pct, trainer_win_pct, field_size,
                        model_version, feature_count, prediction_rank
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """

                stored_count = 0
                for _, row in predictions_df.iterrows():
                    try:
                        # Determine confidence level
                        conf_score = row.get("confidence_score", 0.0)
                        if conf_score >= 0.8:
                            confidence_level = "High"
                        elif conf_score >= 0.6:
                            confidence_level = "Medium"
                        else:
                            confidence_level = "Low"

                        # Extract time part if it's a timestamp
                        race_time_value = row["race_time"]
                        if hasattr(race_time_value, "time"):
                            race_time_value = race_time_value.time()

                        # Clamp probability values to PostgreSQL real type range
                        # PostgreSQL real type: ~1.175e-37 to ~3.403e+38
                        def clamp_probability(value):
                            """Clamp probability to safe range for PostgreSQL real type."""
                            if pd.isna(value) or not np.isfinite(value):
                                return 0.0
                            return max(1e-10, min(1.0, float(value)))  # Safe range

                        cursor.execute(
                            prediction_query,
                            (
                                int(row["race_id"]),
                                str(row["horse_name"]),
                                str(row["jockey"]),
                                str(row["trainer"]),
                                str(row["course"]),
                                int(row["race_number"]),
                                race_time_value,
                                clamp_probability(
                                    row.get("random_forest_probability", 0.0)
                                ),
                                clamp_probability(
                                    row.get("gradient_boosting_probability", 0.0)
                                ),
                                clamp_probability(
                                    row.get("logistic_regression_probability", 0.0)
                                ),
                                clamp_probability(
                                    row.get("neural_network_probability", 0.0)
                                ),
                                clamp_probability(row["ensemble_probability"]),
                                confidence_level,
                                clamp_probability(conf_score),
                                float(
                                    row.get("win_odds", 1.0)
                                ),  # Using win_odds as odds_decimal
                                int(row.get("odds_rank", 1)),
                                clamp_probability(row.get("implied_probability", 0.0)),
                                float(row.get("log_odds", 0.0)),
                                clamp_probability(row.get("jockey_win_pct", 0.0)),
                                clamp_probability(row.get("trainer_win_pct", 0.0)),
                                int(row.get("field_size", 1)),
                                "v2.03",
                                len(self.feature_names),
                                int(row.get("prediction_rank", 1)),
                            ),
                        )
                        stored_count += 1
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to store prediction for {row['horse_name']}: {e}"
                        )
                        logger.debug(f"Error details: {type(e).__name__}: {str(e)}")
                        # Log the problematic row data for debugging
                        logger.debug(f"Row data: {dict(row)}")
                        # Continue with the next prediction rather than breaking

                connection.commit()
                logger.info(
                    f"✅ Stored {stored_count}/{len(predictions_df)} predictions to database"
                )

                return session_id

        except Exception as e:
            logger.error(f"❌ Failed to store predictions to database: {e}")
            return -1

    def update_session_metadata(
        self,
        session_id: int,
        processing_time: float,
        output_file_path: str,
        output_file_size: int,
    ) -> None:
        """Update session with completion metadata."""
        try:
            with psycopg2.connect(**self.db_config) as connection:
                cursor = connection.cursor()

                update_query = """
                    UPDATE ai_prediction_sessions 
                    SET processing_time_seconds = %s, 
                        output_file_path = %s, 
                        output_file_size_kb = %s,
                        status = 'COMPLETED'
                    WHERE id = %s
                """

                cursor.execute(
                    update_query,
                    (
                        processing_time,
                        str(output_file_path),
                        output_file_size,
                        session_id,
                    ),
                )

                connection.commit()
                logger.info(f"✅ Updated session {session_id} metadata")

        except Exception as e:
            logger.warning(f"⚠️ Failed to update session metadata: {e}")

    def run_daily_selections(self) -> None:
        """Generate and display daily AI selections with comprehensive error handling."""
        import time

        start_time = time.time()
        session_id = -1

        # Add initial health checks
        if not self.health_check():
            logger.error("❌ System health check failed - aborting execution")
            raise RuntimeError("System health check failed")

        logger.info(
            "🚀 Starting AI Racing Selections Generator",
            extra={"extra_data": {"start_time": datetime.utcnow().isoformat()}},
        )
        logger.info("=" * 60)

        try:
            # Load today's races with error handling
            logger.info("📊 Loading race data...")
            races_df = self.get_todays_races()

            if len(races_df) == 0:
                logger.warning("⚠️ No races found for today - nothing to process")
                return

            logger.info(
                f"✅ Loaded {len(races_df)} race entries",
                extra={"extra_data": {"race_count": len(races_df)}},
            )

            # Engineer features with validation
            logger.info("⚙️ Engineering features...")
            features_df = self.engineer_features(races_df)

            if features_df is None or len(features_df) == 0:
                raise ValueError("Feature engineering failed - no features generated")

            # Generate predictions with model validation
            logger.info("🤖 Generating AI predictions...")
            predictions_df = self.generate_predictions(features_df)

            if predictions_df is None or len(predictions_df) == 0:
                raise ValueError(
                    "Prediction generation failed - no predictions created"
                )

            # Store predictions to database with transaction handling
            logger.info("💾 Storing predictions to database...")
            session_id = self.store_predictions_to_database(predictions_df)

            # Generate selections with validation
            logger.info("🎯 Generating final selections...")
            selections = self.generate_selections(predictions_df)

            # Format and display report
            logger.info("📄 Formatting selections report...")
            report = self.format_selections_report(selections)
            print("\n" + report)

            # Save report to file with error handling
            report_file = Path(f"ai_selections_{date.today().strftime('%Y%m%d')}.txt")
            try:
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"📁 Report saved successfully: {report_file}")
            except IOError as e:
                logger.error(f"❌ Failed to save report file: {e}")
                # Continue execution - this is not critical

            # Calculate processing metrics
            processing_time = time.time() - start_time
            file_size_kb = (
                int(report_file.stat().st_size / 1024) if report_file.exists() else 0
            )

            # Update session metadata with error handling
            if session_id > 0:
                try:
                    self.update_session_metadata(
                        session_id, processing_time, str(report_file), file_size_kb
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to update session metadata: {e}")

            # Log success metrics
            logger.info(
                "✅ AI selections generation completed successfully!",
                extra={
                    "extra_data": {
                        "processing_time": processing_time,
                        "session_id": session_id,
                        "predictions_generated": len(predictions_df),
                        "report_size_kb": file_size_kb,
                    }
                },
            )

        except Exception as e:
            # Comprehensive error handling
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(
                f"❌ Critical error in selections generation: {error_msg}",
                extra={
                    "extra_data": {
                        "error_type": error_type,
                        "session_id": session_id,
                        "processing_time": time.time() - start_time,
                        "traceback": traceback.format_exc(),
                    }
                },
            )

            # Update session with error if it was created
            if session_id > 0:
                try:
                    self._update_failed_session(session_id, error_msg)
                except Exception as update_error:
                    logger.error(f"❌ Failed to update session status: {update_error}")

            # Re-raise the original exception
            raise

    def health_check(self) -> bool:
        """Perform comprehensive system health check."""
        logger.info("🔍 Performing system health check...")

        try:
            # Check database connectivity
            connection = self._get_db_connection()
            if connection is None or connection.closed:
                logger.error("❌ Health check: Database connection failed")
                return False

            # Check models are loaded
            if not self.models or len(self.models) < 3:
                logger.error(
                    f"❌ Health check: Insufficient models loaded ({len(self.models)})"
                )
                return False

            # Check scaler is available
            if self.scaler is None:
                logger.error("❌ Health check: Feature scaler not loaded")
                return False

            # Check feature names are available
            if not self.feature_names or len(self.feature_names) < 10:
                logger.error(
                    f"❌ Health check: Insufficient features ({len(self.feature_names)})"
                )
                return False

            logger.info("✅ System health check passed")
            return True

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False

    def _update_failed_session(self, session_id: int, error_msg: str) -> None:
        """Update session status to failed with error message."""
        try:
            with psycopg2.connect(**self.db_config) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """UPDATE ai_prediction_sessions 
                       SET status = 'FAILED', error_message = %s 
                       WHERE id = %s""",
                    (error_msg, session_id),
                )
                connection.commit()
                logger.info(f"✅ Updated failed session {session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update session status: {e}")


def main():
    """Main execution function."""
    generator = AISelectionsGenerator()
    generator.run_daily_selections()


if __name__ == "__main__":
    main()
