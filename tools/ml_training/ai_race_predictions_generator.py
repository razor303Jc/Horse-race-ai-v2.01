#!/usr/bin/env python3
"""
AI Race Predictions and Selections Generator
===========================================

Comprehensive system for generating AI predictions and selections from race_cards data.
Uses trained ML models to create predictions and stores them in dedicated database
tables.

Features:
- Reads live race_cards data from database
- Calls ML ensemble models for predictions
- Generates individual model probabilities
- Creates confidence scores and betting recommendations
- Stores selections in ai_predictions table
- Tracks performance and provides analytics
"""

import sys
import os
import logging
import json
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, date, time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import joblib
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RacePrediction:
    """Single race prediction result."""

    horse_name: str
    race_id: int
    course: str
    race_number: int
    jockey: str
    trainer: str

    # Individual model predictions
    random_forest_prob: float
    gradient_boosting_prob: float
    logistic_regression_prob: float
    neural_network_prob: float

    # Ensemble prediction
    ensemble_prob: float
    confidence_score: float
    confidence_level: str

    # Market data
    odds_decimal: float
    market_rank: int
    implied_probability: float

    # Feature values
    log_odds: float
    jockey_win_pct: float
    trainer_win_pct: float
    field_size: int

    # Prediction ranking
    prediction_rank: int
    is_recommended: bool
    betting_recommendation: str


@dataclass
class RaceAnalysis:
    """Complete race analysis with all predictions."""

    race_id: int
    course: str
    race_number: int
    race_time: time
    race_date: date
    race_name: str
    field_size: int

    predictions: List[RacePrediction]
    top_selections: List[str]
    race_analysis: Dict[str, Any]
    confidence_distribution: Dict[str, int]


class AIRacePredictionsGenerator:
    """
    Main class for generating AI race predictions and selections.
    """

    def __init__(self, models_dir: str = None, db_config: Dict[str, Any] = None):
        """Initialize the AI predictions generator."""
        self.models_dir = Path(models_dir) if models_dir else self._find_models_dir()
        self.db_config = db_config or self._get_default_db_config()

        # ML Model components
        self.ensemble_model = None
        self.individual_models = {}
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = []
        self.is_loaded = False

        # Feature columns for prediction
        self.feature_columns = [
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

        # Load models on initialization
        self.load_models()

    def _find_models_dir(self) -> Path:
        """Find the models directory."""
        potential_paths = [
            Path("/app/models"),
            Path("/app/trained_models/priority_3a"),
            project_root / "models",
            project_root / "trained_models" / "priority_3a",
            project_root / "src" / "models",
        ]

        for path in potential_paths:
            if path.exists() and any(path.glob("*.joblib")):
                logger.info(f"Found models directory: {path}")
                return path

        # Create default directory
        default_path = project_root / "models"
        default_path.mkdir(exist_ok=True)
        logger.warning(f"Using default models directory: {default_path}")
        return default_path

    def _get_default_db_config(self) -> Dict[str, Any]:
        """Get default database configuration."""
        # Check if running in Docker environment
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            # Parse Docker DATABASE_URL: postgresql://user:pass@host:port/db
            import urllib.parse as urlparse

            url = urlparse.urlparse(database_url)
            return {
                "host": url.hostname,
                "port": url.port or 5432,
                "user": url.username,
                "password": url.password,
                "database": url.path[1:],  # Remove leading '/'
            }
        else:
            # Local development configuration
            return {
                "host": "localhost",
                "port": 5432,
                "user": "horse_racing",
                "password": "secure_password_123",
                "database": "horse_racing_db",
            }

    @contextmanager
    def get_db_connection(self):
        """Get database connection with context manager."""
        connection = None
        try:
            connection = psycopg2.connect(**self.db_config)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def load_models(self) -> bool:
        """Load trained ML models and components."""
        try:
            logger.info("🤖 Loading AI prediction models...")

            # Find latest ensemble model
            model_files = list(self.models_dir.glob("*ensemble*.joblib"))
            if not model_files:
                model_files = list(self.models_dir.glob("*.joblib"))

            if not model_files:
                logger.error("No model files found")
                return False

            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Loading model: {latest_model}")

            # Load model data
            model_data = joblib.load(latest_model)

            # Handle different model formats
            if isinstance(model_data, dict):
                self.ensemble_model = model_data.get("ensemble_model")
                self.individual_models = model_data.get("individual_models", {})
                self.scaler = model_data.get("scaler")
                self.feature_names = model_data.get("feature_names", [])
            else:
                self.ensemble_model = model_data
                self.individual_models = {}
                logger.warning("Legacy model format - individual models not available")

            # Load scaler if not in model data
            if self.scaler is None:
                scaler_files = list(self.models_dir.glob("*scaler*.joblib"))
                if scaler_files:
                    self.scaler = joblib.load(scaler_files[0])
                    logger.info("Loaded separate scaler file")

            # Load encoders
            encoder_files = list(self.models_dir.glob("*encoder*.joblib"))
            if encoder_files:
                self.label_encoders = joblib.load(encoder_files[0])
                logger.info("Loaded label encoders")

            self.is_loaded = True
            logger.info("✅ AI models loaded successfully")

            if hasattr(self.ensemble_model, "estimators"):
                logger.info(
                    f"   Ensemble components: {[name for name, _ in self.ensemble_model.estimators]}"
                )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            return False

    def get_race_cards_data(self, race_date: date = None) -> pd.DataFrame:
        """Get race cards data for prediction."""
        if race_date is None:
            race_date = date.today()

        logger.info(f"📊 Loading race cards for {race_date}")

        try:
            with self.get_db_connection() as conn:
                # Enhanced query to get comprehensive race and runner data
                query = """
                    SELECT DISTINCT
                        rc.race_id,
                        rc.race_number,
                        rc.race_time,
                        rc.race_date,
                        rc.course,
                        rc.race_name,
                        rc.class,
                        rc.distance,
                        rc.runners as field_size,
                        
                        re.horse_name,
                        re.jockey,
                        re.trainer,
                        re.odds_decimal,
                        re.weight_kg as horse_weight_kg,
                        re.draw,
                        re.age as horse_age,
                        re.owner,
                        
                        -- Calculate market metrics
                        ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY re.odds_decimal) as odds_rank,
                        CASE WHEN ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY re.odds_decimal) = 1 
                             THEN 1 ELSE 0 END as is_favorite,
                        1.0 / re.odds_decimal as implied_probability,
                        LN(re.odds_decimal) as log_odds,
                        
                        -- Get jockey stats
                        COALESCE(js.percentage_wins, 0) as jockey_win_pct,
                        COALESCE(js.wins, 0) as jockey_wins,
                        COALESCE(js.total_races, 0) as jockey_runs,
                        
                        -- Get trainer stats  
                        COALESCE(ts.percentage_wins, 0) as trainer_win_pct,
                        COALESCE(ts.wins, 0) as trainer_wins,
                        COALESCE(ts.total_races, 0) as trainer_runs
                        
                    FROM race_cards rc
                    JOIN race_entries re ON rc.race_id = re.race_id
                    LEFT JOIN jockeys_stats js ON re.jockey = js.jockey_name
                    LEFT JOIN trainers_stats ts ON re.trainer = ts.trainer_name
                    WHERE rc.race_date = %s
                      AND re.odds_decimal > 0
                      AND re.jockey IS NOT NULL
                      AND re.trainer IS NOT NULL
                    ORDER BY rc.race_id, re.odds_decimal
                """

                df = pd.read_sql_query(query, conn, params=(race_date,))

                if len(df) == 0:
                    logger.warning(f"No race data found for {race_date}")
                    return pd.DataFrame()

                logger.info(
                    f"✅ Loaded {len(df)} runners from {df['race_id'].nunique()} races"
                )
                logger.info(f"   Courses: {', '.join(df['course'].unique())}")

                return df

        except Exception as e:
            logger.error(f"❌ Failed to load race cards: {e}")
            return pd.DataFrame()

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML prediction."""
        logger.info("🔧 Engineering features for prediction...")

        if len(df) == 0:
            return df

        try:
            # Create copy to avoid modifying original
            features_df = df.copy()

            # Calculate race-level statistics for each race
            race_stats = (
                features_df.groupby("race_id")
                .agg(
                    {
                        "odds_decimal": ["min", "max", "mean", "count"],
                        "implied_probability": "sum",
                    }
                )
                .round(4)
            )

            race_stats.columns = [
                "min_odds",
                "max_odds",
                "avg_odds",
                "field_size",
                "total_implied_prob",
            ]
            race_stats = race_stats.reset_index()

            # Merge race statistics back
            features_df = features_df.merge(race_stats, on="race_id", how="left")

            # Calculate percentiles within each race
            features_df["draw_percentile"] = features_df.groupby("race_id")[
                "draw"
            ].rank(pct=True)
            features_df["weight_percentile"] = features_df.groupby("race_id")[
                "horse_weight_kg"
            ].rank(pct=True)
            features_df["odds_percentile"] = features_df.groupby("race_id")[
                "odds_decimal"
            ].rank(pct=True, ascending=False)

            # Age categories
            features_df["age_category"] = pd.cut(
                features_df["horse_age"], bins=[0, 3, 5, 8, 100], labels=[0, 1, 2, 3]
            ).astype(int)

            # Combined performance score
            features_df["jockey_performance"] = (
                features_df["jockey_win_pct"] / 100.0
            ) * 0.6
            features_df["trainer_performance"] = (
                features_df["trainer_win_pct"] / 100.0
            ) * 0.4
            features_df["combined_performance"] = (
                features_df["jockey_performance"] + features_df["trainer_performance"]
            )

            # Market rank (already calculated in SQL, but ensure it exists)
            if "market_rank" not in features_df.columns:
                features_df["market_rank"] = features_df["odds_rank"]

            # Ensure all required feature columns exist with defaults
            for col in self.feature_columns:
                if col not in features_df.columns:
                    if "pct" in col or "probability" in col:
                        features_df[col] = 0.0
                    elif "rank" in col or "size" in col or "age" in col:
                        features_df[col] = 1
                    else:
                        features_df[col] = 0.0

            # Convert percentages to decimals where needed
            features_df["jockey_win_pct"] = features_df["jockey_win_pct"] / 100.0
            features_df["trainer_win_pct"] = features_df["trainer_win_pct"] / 100.0

            # Fill any remaining NaN values
            features_df = features_df.fillna(0.0)

            logger.info(f"✅ Features engineered for {len(features_df)} runners")

            return features_df

        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            return df

    def generate_predictions(self, df: pd.DataFrame) -> List[RacePrediction]:
        """Generate AI predictions for all runners."""
        if not self.is_loaded:
            logger.error("Models not loaded - cannot generate predictions")
            return []

        if len(df) == 0:
            logger.warning("No data provided for predictions")
            return []

        logger.info(f"🎯 Generating predictions for {len(df)} runners...")

        predictions = []

        try:
            # Prepare feature matrix
            X = df[self.feature_columns].values

            # Scale features if scaler available
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
                logger.warning("No scaler available - using unscaled features")

            # Generate ensemble predictions
            ensemble_probs = self.ensemble_model.predict_proba(X_scaled)[:, 1]

            # Generate individual model predictions if available
            individual_probs = {}
            model_names = [
                "random_forest",
                "gradient_boosting",
                "logistic_regression",
                "neural_network",
            ]

            for model_name in model_names:
                if model_name in self.individual_models:
                    try:
                        model_probs = self.individual_models[model_name].predict_proba(
                            X_scaled
                        )[:, 1]
                        individual_probs[model_name] = model_probs
                    except Exception as e:
                        logger.warning(f"Failed to get {model_name} predictions: {e}")
                        individual_probs[model_name] = np.zeros(len(X_scaled))
                else:
                    individual_probs[model_name] = np.zeros(len(X_scaled))

            # Create predictions for each runner
            for idx, row in df.iterrows():
                try:
                    # Individual model probabilities
                    rf_prob = (
                        individual_probs["random_forest"][idx]
                        if "random_forest" in individual_probs
                        else 0.0
                    )
                    gb_prob = (
                        individual_probs["gradient_boosting"][idx]
                        if "gradient_boosting" in individual_probs
                        else 0.0
                    )
                    lr_prob = (
                        individual_probs["logistic_regression"][idx]
                        if "logistic_regression" in individual_probs
                        else 0.0
                    )
                    nn_prob = (
                        individual_probs["neural_network"][idx]
                        if "neural_network" in individual_probs
                        else 0.0
                    )

                    # Ensemble probability
                    ensemble_prob = ensemble_probs[idx]

                    # Calculate confidence score (based on model agreement)
                    if len(individual_probs) > 1:
                        all_probs = [
                            p for p in [rf_prob, gb_prob, lr_prob, nn_prob] if p > 0
                        ]
                        if all_probs:
                            prob_std = np.std(all_probs)
                            confidence_score = max(
                                0.1, 1.0 - (prob_std * 2)
                            )  # Higher agreement = higher confidence
                        else:
                            confidence_score = 0.5
                    else:
                        confidence_score = min(
                            0.9, ensemble_prob * 1.2
                        )  # Scale ensemble prob to confidence

                    # Confidence level
                    if confidence_score >= 0.8:
                        confidence_level = "High"
                    elif confidence_score >= 0.6:
                        confidence_level = "Medium"
                    else:
                        confidence_level = "Low"

                    # Betting recommendation
                    value_ratio = ensemble_prob / row["implied_probability"]
                    if value_ratio > 1.15 and confidence_score > 0.7:
                        betting_rec = "STRONG_BUY"
                    elif value_ratio > 1.05 and confidence_score > 0.6:
                        betting_rec = "BUY"
                    elif value_ratio < 0.85:
                        betting_rec = "AVOID"
                    else:
                        betting_rec = "HOLD"

                    # Create prediction object
                    prediction = RacePrediction(
                        horse_name=str(row["horse_name"]),
                        race_id=int(row["race_id"]),
                        course=str(row["course"]),
                        race_number=int(row["race_number"]),
                        jockey=str(row["jockey"]),
                        trainer=str(row["trainer"]),
                        random_forest_prob=float(rf_prob),
                        gradient_boosting_prob=float(gb_prob),
                        logistic_regression_prob=float(lr_prob),
                        neural_network_prob=float(nn_prob),
                        ensemble_prob=float(ensemble_prob),
                        confidence_score=float(confidence_score),
                        confidence_level=confidence_level,
                        odds_decimal=float(row["odds_decimal"]),
                        market_rank=int(row.get("odds_rank", 1)),
                        implied_probability=float(row["implied_probability"]),
                        log_odds=float(row["log_odds"]),
                        jockey_win_pct=float(row["jockey_win_pct"]),
                        trainer_win_pct=float(row["trainer_win_pct"]),
                        field_size=int(row["field_size"]),
                        prediction_rank=0,  # Will be set after sorting
                        is_recommended=(betting_rec in ["STRONG_BUY", "BUY"]),
                        betting_recommendation=betting_rec,
                    )

                    predictions.append(prediction)

                except Exception as e:
                    logger.warning(
                        f"Failed to create prediction for {row.get('horse_name', 'unknown')}: {e}"
                    )
                    continue

            # Sort by ensemble probability and set prediction ranks
            predictions.sort(key=lambda x: x.ensemble_prob, reverse=True)
            for i, pred in enumerate(predictions):
                pred.prediction_rank = i + 1

            logger.info(f"✅ Generated {len(predictions)} predictions")

            if predictions:
                top_pred = predictions[0]
                logger.info(
                    f"   Top prediction: {top_pred.horse_name} ({top_pred.ensemble_prob:.3f})"
                )

            return predictions

        except Exception as e:
            logger.error(f"❌ Prediction generation failed: {e}")
            return []

    def analyze_race(self, predictions: List[RacePrediction]) -> RaceAnalysis:
        """Analyze a single race's predictions."""
        if not predictions:
            return None

        # Group predictions by race
        race_pred = predictions[0]  # Assume all predictions are for same race

        # Top selections (top 3 by ensemble probability)
        top_selections = [p.horse_name for p in predictions[:3]]

        # Confidence distribution
        confidence_dist = {
            "High": sum(1 for p in predictions if p.confidence_level == "High"),
            "Medium": sum(1 for p in predictions if p.confidence_level == "Medium"),
            "Low": sum(1 for p in predictions if p.confidence_level == "Low"),
        }

        # Race analysis
        analysis = {
            "total_runners": len(predictions),
            "recommended_bets": sum(1 for p in predictions if p.is_recommended),
            "avg_confidence": np.mean([p.confidence_score for p in predictions]),
            "favorite_prob": predictions[0].ensemble_prob if predictions else 0.0,
            "competitive_balance": np.std([p.ensemble_prob for p in predictions]),
            "value_opportunities": sum(
                1
                for p in predictions
                if p.betting_recommendation in ["STRONG_BUY", "BUY"]
            ),
        }

        return RaceAnalysis(
            race_id=race_pred.race_id,
            course=race_pred.course,
            race_number=race_pred.race_number,
            race_time=None,  # Will be filled from DB if needed
            race_date=date.today(),
            race_name="",
            field_size=race_pred.field_size,
            predictions=predictions,
            top_selections=top_selections,
            race_analysis=analysis,
            confidence_distribution=confidence_dist,
        )

    def store_predictions_to_database(self, predictions: List[RacePrediction]) -> int:
        """Store predictions to ai_predictions table."""
        if not predictions:
            logger.warning("No predictions to store")
            return 0

        logger.info(f"💾 Storing {len(predictions)} predictions to database...")

        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert query for ai_predictions table
                insert_query = """
                    INSERT INTO ai_predictions (
                        race_id, horse_name, jockey, trainer, course, race_number,
                        random_forest_probability, gradient_boosting_probability,
                        logistic_regression_probability, neural_network_probability,
                        ensemble_probability, confidence_level, confidence_score,
                        odds_decimal, market_rank, implied_probability,
                        log_odds, jockey_win_pct, trainer_win_pct, field_size,
                        model_version, feature_count, prediction_rank
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """

                stored_count = 0
                for pred in predictions:
                    try:
                        cursor.execute(
                            insert_query,
                            (
                                pred.race_id,
                                pred.horse_name,
                                pred.jockey,
                                pred.trainer,
                                pred.course,
                                pred.race_number,
                                pred.random_forest_prob,
                                pred.gradient_boosting_prob,
                                pred.logistic_regression_prob,
                                pred.neural_network_prob,
                                pred.ensemble_prob,
                                pred.confidence_level,
                                pred.confidence_score,
                                pred.odds_decimal,
                                pred.market_rank,
                                pred.implied_probability,
                                pred.log_odds,
                                pred.jockey_win_pct,
                                pred.trainer_win_pct,
                                pred.field_size,
                                "v2.04",  # model version
                                len(self.feature_columns),  # feature count
                                pred.prediction_rank,
                            ),
                        )
                        stored_count += 1

                    except Exception as e:
                        logger.warning(
                            f"Failed to store prediction for {pred.horse_name}: {e}"
                        )
                        continue

                conn.commit()
                logger.info(f"✅ Stored {stored_count}/{len(predictions)} predictions")

                return stored_count

        except Exception as e:
            logger.error(f"❌ Failed to store predictions: {e}")
            return 0

    def generate_daily_predictions(self, race_date: date = None) -> Dict[str, Any]:
        """Generate complete daily predictions and store to database."""
        if race_date is None:
            race_date = date.today()

        logger.info(
            f"""
╭─────────────────────────────────────────╮
│     AI Race Predictions Generator      │
│                                         │
│  📅 Date: {race_date}                   │
│  🤖 ML Models: Ensemble + Individual    │
│  💾 Storage: Database Integration       │
╰─────────────────────────────────────────╯
        """
        )

        results = {
            "date": race_date.isoformat(),
            "total_races": 0,
            "total_runners": 0,
            "predictions_generated": 0,
            "predictions_stored": 0,
            "race_analyses": [],
            "summary": {},
            "errors": [],
        }

        try:
            # Step 1: Load race cards data
            logger.info("📊 Step 1: Loading race cards data...")
            race_data = self.get_race_cards_data(race_date)

            if len(race_data) == 0:
                results["errors"].append(f"No race data found for {race_date}")
                return results

            results["total_races"] = race_data["race_id"].nunique()
            results["total_runners"] = len(race_data)

            # Step 2: Engineer features
            logger.info("🔧 Step 2: Engineering features...")
            featured_data = self.engineer_features(race_data)

            # Step 3: Generate predictions for all races
            logger.info("🎯 Step 3: Generating AI predictions...")
            all_predictions = self.generate_predictions(featured_data)
            results["predictions_generated"] = len(all_predictions)

            # Step 4: Store predictions to database
            logger.info("💾 Step 4: Storing predictions to database...")
            stored_count = self.store_predictions_to_database(all_predictions)
            results["predictions_stored"] = stored_count

            # Step 5: Generate race-by-race analysis
            logger.info("📈 Step 5: Generating race analyses...")
            race_groups = {}
            for pred in all_predictions:
                race_key = (pred.race_id, pred.course, pred.race_number)
                if race_key not in race_groups:
                    race_groups[race_key] = []
                race_groups[race_key].append(pred)

            for race_key, race_predictions in race_groups.items():
                analysis = self.analyze_race(race_predictions)
                if analysis:
                    results["race_analyses"].append(
                        {
                            "race_id": analysis.race_id,
                            "course": analysis.course,
                            "race_number": analysis.race_number,
                            "field_size": analysis.field_size,
                            "top_selections": analysis.top_selections,
                            "confidence_distribution": analysis.confidence_distribution,
                            "analysis": analysis.race_analysis,
                        }
                    )

            # Step 6: Generate summary statistics
            logger.info("📊 Step 6: Generating summary statistics...")
            if all_predictions:
                high_conf_count = sum(
                    1 for p in all_predictions if p.confidence_level == "High"
                )
                recommended_count = sum(1 for p in all_predictions if p.is_recommended)
                avg_confidence = np.mean([p.confidence_score for p in all_predictions])

                results["summary"] = {
                    "high_confidence_predictions": high_conf_count,
                    "recommended_bets": recommended_count,
                    "average_confidence": round(avg_confidence, 3),
                    "models_status": "Loaded" if self.is_loaded else "Error",
                    "top_prediction": (
                        {
                            "horse": all_predictions[0].horse_name,
                            "course": all_predictions[0].course,
                            "race": all_predictions[0].race_number,
                            "probability": round(all_predictions[0].ensemble_prob, 3),
                            "confidence": round(all_predictions[0].confidence_score, 3),
                        }
                        if all_predictions
                        else None
                    ),
                }

            success_rate = (
                (stored_count / len(all_predictions) * 100) if all_predictions else 0
            )

            logger.info(
                f"""
╭─────────────────────────────────────────╮
│        Daily Predictions Complete      │
│                                         │
│  🏇 Races Processed: {results['total_races']}                │
│  🐎 Total Runners: {results['total_runners']}                  │
│  🎯 Predictions Generated: {results['predictions_generated']}            │
│  💾 Stored to Database: {results['predictions_stored']}              │
│  ✅ Success Rate: {success_rate:.1f}%                 │
│                                         │
│  System ready for race analysis!       │
╰─────────────────────────────────────────╯
            """
            )

            return results

        except Exception as e:
            logger.error(f"❌ Daily predictions generation failed: {e}")
            results["errors"].append(str(e))
            return results

    def get_predictions_for_race(self, race_id: int) -> List[RacePrediction]:
        """Get stored predictions for a specific race."""
        try:
            with self.get_db_connection() as conn:
                query = """
                    SELECT * FROM ai_predictions 
                    WHERE race_id = %s 
                    ORDER BY prediction_rank
                """

                cursor = conn.cursor()
                cursor.execute(query, (race_id,))
                rows = cursor.fetchall()

                # Get column names
                columns = [desc[0] for desc in cursor.description]

                predictions = []
                for row in rows:
                    row_dict = dict(zip(columns, row))

                    pred = RacePrediction(
                        horse_name=row_dict["horse_name"],
                        race_id=row_dict["race_id"],
                        course=row_dict["course"],
                        race_number=row_dict["race_number"],
                        jockey=row_dict["jockey"],
                        trainer=row_dict["trainer"],
                        random_forest_prob=row_dict.get(
                            "random_forest_probability", 0.0
                        ),
                        gradient_boosting_prob=row_dict.get(
                            "gradient_boosting_probability", 0.0
                        ),
                        logistic_regression_prob=row_dict.get(
                            "logistic_regression_probability", 0.0
                        ),
                        neural_network_prob=row_dict.get(
                            "neural_network_probability", 0.0
                        ),
                        ensemble_prob=row_dict["ensemble_probability"],
                        confidence_score=row_dict["confidence_score"],
                        confidence_level=row_dict["confidence_level"],
                        odds_decimal=row_dict["odds_decimal"],
                        market_rank=row_dict["market_rank"],
                        implied_probability=row_dict["implied_probability"],
                        log_odds=row_dict["log_odds"],
                        jockey_win_pct=row_dict["jockey_win_pct"],
                        trainer_win_pct=row_dict["trainer_win_pct"],
                        field_size=row_dict["field_size"],
                        prediction_rank=row_dict["prediction_rank"],
                        is_recommended=False,  # Will be calculated based on current logic
                        betting_recommendation="HOLD",  # Will be calculated
                    )

                    predictions.append(pred)

                logger.info(
                    f"Retrieved {len(predictions)} predictions for race {race_id}"
                )
                return predictions

        except Exception as e:
            logger.error(f"Failed to get predictions for race {race_id}: {e}")
            return []

    def get_daily_summary(self, race_date: date = None) -> Dict[str, Any]:
        """Get summary of daily predictions."""
        if race_date is None:
            race_date = date.today()

        try:
            with self.get_db_connection() as conn:
                # Get overall statistics
                stats_query = """
                    SELECT 
                        COUNT(*) as total_predictions,
                        COUNT(DISTINCT race_id) as total_races,
                        COUNT(DISTINCT course) as total_courses,
                        AVG(ensemble_probability) as avg_ensemble_prob,
                        AVG(confidence_score) as avg_confidence,
                        COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence_count,
                        COUNT(CASE WHEN confidence_level = 'Medium' THEN 1 END) as medium_confidence_count,
                        COUNT(CASE WHEN confidence_level = 'Low' THEN 1 END) as low_confidence_count
                    FROM ai_predictions 
                    WHERE DATE(created_at) = %s
                """

                cursor = conn.cursor()
                cursor.execute(stats_query, (race_date,))
                stats = cursor.fetchone()

                # Get top predictions
                top_query = """
                    SELECT race_id, course, race_number, horse_name, 
                           ensemble_probability, confidence_score
                    FROM ai_predictions 
                    WHERE DATE(created_at) = %s
                    ORDER BY ensemble_probability DESC 
                    LIMIT 10
                """

                cursor.execute(top_query, (race_date,))
                top_predictions = cursor.fetchall()

                summary = {
                    "date": race_date.isoformat(),
                    "statistics": {
                        "total_predictions": stats[0] or 0,
                        "total_races": stats[1] or 0,
                        "total_courses": stats[2] or 0,
                        "avg_ensemble_probability": round(stats[3] or 0, 3),
                        "avg_confidence": round(stats[4] or 0, 3),
                        "confidence_distribution": {
                            "High": stats[5] or 0,
                            "Medium": stats[6] or 0,
                            "Low": stats[7] or 0,
                        },
                    },
                    "top_predictions": [
                        {
                            "race_id": row[0],
                            "course": row[1],
                            "race_number": row[2],
                            "horse_name": row[3],
                            "ensemble_probability": round(row[4], 3),
                            "confidence_score": round(row[5], 3),
                        }
                        for row in top_predictions
                    ],
                }

                return summary

        except Exception as e:
            logger.error(f"Failed to get daily summary: {e}")
            return {"error": str(e)}


def main():
    """Main function for running AI predictions."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Race Predictions Generator")
    parser.add_argument(
        "--date", help="Date for predictions (YYYY-MM-DD)", default=None
    )
    parser.add_argument(
        "--models-dir", help="Directory containing ML models", default=None
    )
    parser.add_argument(
        "--race-id", type=int, help="Get predictions for specific race", default=None
    )
    parser.add_argument("--summary", action="store_true", help="Get daily summary only")

    args = parser.parse_args()

    # Parse date
    prediction_date = None
    if args.date:
        try:
            prediction_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            return 1
    else:
        prediction_date = date.today()

    # Initialize generator
    generator = AIRacePredictionsGenerator(models_dir=args.models_dir)

    if not generator.is_loaded:
        logger.error("Failed to load ML models")
        return 1

    try:
        if args.race_id:
            # Get predictions for specific race
            predictions = generator.get_predictions_for_race(args.race_id)
            logger.info(f"Found {len(predictions)} predictions for race {args.race_id}")
            for pred in predictions[:5]:  # Show top 5
                logger.info(
                    f"  {pred.prediction_rank}. {pred.horse_name} - {pred.ensemble_prob:.3f}"
                )

        elif args.summary:
            # Get daily summary
            summary = generator.get_daily_summary(prediction_date)
            logger.info(f"Daily Summary for {prediction_date}:")
            logger.info(
                f"  Total Predictions: {summary['statistics']['total_predictions']}"
            )
            logger.info(f"  Total Races: {summary['statistics']['total_races']}")
            logger.info(
                f"  Average Confidence: {summary['statistics']['avg_confidence']}"
            )

        else:
            # Generate full daily predictions
            results = generator.generate_daily_predictions(prediction_date)

            if results["errors"]:
                logger.error("Errors occurred:")
                for error in results["errors"]:
                    logger.error(f"  - {error}")
                return 1

            logger.info("✅ Daily predictions completed successfully")

        return 0

    except KeyboardInterrupt:
        logger.info("🛑 Process stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Process failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
