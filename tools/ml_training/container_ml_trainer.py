#!/usr/bin/env python3
"""
Container-Optimized ML Training Script
Modified to work within container filesystem constraints while maintaining full functionality
"""

import json
import logging
import sys
import traceback
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import tempfile
import os

import joblib
import numpy as np
import pandas as pd
import psycopg2
from sklearn.compose import ColumnTransformer

# ML imports
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# Setup logging for container environment
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "component": "ML_TRAINER", "message": "%(message)s", "module": "container_ml_trainer", "function": "%(funcName)s"}',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class ContainerMLTrainer:
    """Container-optimized ML trainer that handles filesystem constraints"""

    def __init__(self):
        # Database connection
        self.db_config = {
            "host": "postgres",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        self.trained_models = {}
        self.feature_names = []
        self.scaler = None
        self.training_results = {}

    def load_data(self) -> pd.DataFrame:
        """Load race data from database"""
        logger.info("📊 Loading race data from database...")

        query = """
            SELECT 
                r.*,
                js.wins as jockey_wins,
                js.runs as jockey_runs,
                js.win_rate as jockey_win_pct,
                ts.wins as trainer_wins,
                ts.runs as trainer_runs,
                ts.win_rate as trainer_win_pct,
                ra.course,
                ra.distance,
                ra.date as race_date,
                ra.prize as prize_money
            FROM records r
            LEFT JOIN jockeys_stats js ON r.jockey = js.jockey_name
            LEFT JOIN trainers_stats ts ON r.trainer = ts.trainer_name
            LEFT JOIN races ra ON r.race_id = ra.race_id
            WHERE r.jockey != 'none' 
            AND r.trainer != 'none'
            AND r.position IS NOT NULL
            AND r.starting_price > 0
            ORDER BY r.record_id DESC
        """

        try:
            connection = psycopg2.connect(**self.db_config)
            df = pd.read_sql_query(query, connection)
            connection.close()

            logger.info(f"✅ Loaded {len(df)} records from database")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            raise

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML training"""
        logger.info("⚙️ Engineering features...")

        df_features = df.copy()

        # Clean and convert data types
        df_features["win_odds"] = pd.to_numeric(
            df_features["starting_price"], errors="coerce"
        )
        df_features["horse_age"] = pd.to_numeric(df_features["age"], errors="coerce")
        df_features["horse_weight_kg"] = pd.to_numeric(
            df_features["weight"], errors="coerce"
        ).fillna(60)
        df_features["draw"] = pd.to_numeric(df_features.get("draw", 1), errors="coerce")
        df_features["draw"] = df_features["draw"].fillna(1)
        df_features["finished_position"] = pd.to_numeric(
            df_features["position"], errors="coerce"
        )

        # Clean missing values
        df_features = df_features.dropna(
            subset=["win_odds", "horse_age", "finished_position"]
        )
        df_features = df_features[df_features["win_odds"] > 0]

        # Fill missing stats with defaults
        df_features["jockey_wins"] = df_features["jockey_wins"].fillna(0)
        df_features["jockey_runs"] = df_features["jockey_runs"].fillna(1)
        df_features["jockey_win_pct"] = df_features["jockey_win_pct"].fillna(5.0)
        df_features["trainer_wins"] = df_features["trainer_wins"].fillna(0)
        df_features["trainer_runs"] = df_features["trainer_runs"].fillna(1)
        df_features["trainer_win_pct"] = df_features["trainer_win_pct"].fillna(5.0)

        # Additional features
        df_features["odds_rank"] = df_features.groupby("race_id")["win_odds"].rank()
        df_features["is_favorite"] = (df_features["odds_rank"] == 1).astype(int)
        df_features["implied_probability"] = 1.0 / df_features["win_odds"]
        df_features["log_odds"] = np.log(df_features["win_odds"])
        df_features["field_size"] = df_features.groupby("race_id")["race_id"].transform(
            "count"
        )

        # Performance ratios
        df_features["jockey_performance_ratio"] = df_features["jockey_win_pct"] / 100.0
        df_features["trainer_performance_ratio"] = (
            df_features["trainer_win_pct"] / 100.0
        )

        # Prize and distance features
        df_features["prize_money"] = pd.to_numeric(
            df_features["prize_money"], errors="coerce"
        ).fillna(1000)
        df_features["distance"] = pd.to_numeric(
            df_features["distance"], errors="coerce"
        ).fillna(1600)
        df_features["prize_per_meter"] = (
            df_features["prize_money"] / df_features["distance"]
        )

        logger.info(
            f"✅ Feature engineering complete: {len(df_features.columns)} features"
        )
        return df_features

    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for ML training"""
        logger.info("🎯 Preparing training data...")

        # Create target variable
        df["is_winner"] = (df["finished_position"] == 1).astype(int)

        # Select features for training
        feature_columns = [
            "win_odds",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "odds_rank",
            "is_favorite",
            "implied_probability",
            "log_odds",
            "field_size",
            "jockey_performance_ratio",
            "trainer_performance_ratio",
            "prize_money",
            "distance",
            "prize_per_meter",
            "jockey_wins",
            "trainer_wins",
            "jockey_runs",
        ]

        # Ensure all feature columns exist
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0

        X = df[feature_columns].values
        y = df["is_winner"].values

        # Store feature names for later use
        self.feature_names = feature_columns

        # Handle any remaining NaN values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        logger.info(f"📊 Training data prepared:")
        logger.info(f"   Features: {X.shape[1]}")
        logger.info(f"   Samples: {X.shape[0]}")
        logger.info(f"   Win rate: {y.mean():.4f}")

        return X, y

    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train multiple ML models"""
        logger.info("🚀 Training ML models...")

        # Initialize models
        models = {
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            ),
            "logistic_regression": LogisticRegression(
                random_state=42, max_iter=1000, solver="liblinear"
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42
            ),
        }

        # Prepare scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        results = {}
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        for name, model in models.items():
            logger.info(f"   🎯 Training {name}...")

            # Train model
            model.fit(X_scaled, y)

            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring="roc_auc")
            cv_accuracy = cross_val_score(model, X_scaled, y, cv=cv, scoring="accuracy")

            # Store results
            results[name] = {
                "model": model,
                "cv_auc_mean": cv_scores.mean(),
                "cv_auc_std": cv_scores.std(),
                "cv_accuracy_mean": cv_accuracy.mean(),
                "cv_accuracy_std": cv_accuracy.std(),
            }

            logger.info(
                f"       📈 {name}: CV AUC {cv_scores.mean():.4f} (±{cv_scores.std():.4f}), "
                f"Accuracy {cv_accuracy.mean():.4f} (±{cv_accuracy.std():.4f})"
            )

        # Store results for later access
        self.trained_models = results
        self.training_results = results

        return results

    def evaluate_models(self, results: Dict[str, Any]) -> str:
        """Evaluate and select best model"""
        logger.info("📊 Model evaluation summary:")

        best_model_name = ""
        best_auc = 0

        for name, result in results.items():
            auc = result["cv_auc_mean"]
            accuracy = result["cv_accuracy_mean"]

            logger.info(f"   {name}:")
            logger.info(f"     AUC: {auc:.4f} (±{result['cv_auc_std']:.4f})")
            logger.info(
                f"     Accuracy: {accuracy:.4f} (±{result['cv_accuracy_std']:.4f})"
            )

            if auc > best_auc:
                best_auc = auc
                best_model_name = name

        logger.info(f"🏆 Best model: {best_model_name} (AUC: {best_auc:.4f})")
        return best_model_name

    def save_model_summary(self, results: Dict[str, Any]) -> str:
        """Create a summary of trained models (without file persistence)"""
        logger.info("📋 Creating model summary...")

        summary = {
            "training_timestamp": datetime.now().isoformat(),
            "total_models": len(results),
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "models": {},
        }

        for name, result in results.items():
            summary["models"][name] = {
                "cv_auc_mean": float(result["cv_auc_mean"]),
                "cv_auc_std": float(result["cv_auc_std"]),
                "cv_accuracy_mean": float(result["cv_accuracy_mean"]),
                "cv_accuracy_std": float(result["cv_accuracy_std"]),
            }

        # Best model
        best_model = max(results.keys(), key=lambda k: results[k]["cv_auc_mean"])
        summary["best_model"] = best_model
        summary["best_auc"] = float(results[best_model]["cv_auc_mean"])

        logger.info(f"✅ Model summary created with {len(results)} models")
        return json.dumps(summary, indent=2)

    def run_complete_training(self):
        """Run the complete ML training pipeline"""
        logger.info("🎯 Starting Container-Optimized ML Training Pipeline")
        logger.info("=" * 60)

        try:
            # Load data
            df = self.load_data()

            # Engineer features
            df_features = self.engineer_features(df)

            # Prepare training data
            X, y = self.prepare_training_data(df_features)

            # Train models
            results = self.train_models(X, y)

            # Evaluate models
            best_model = self.evaluate_models(results)

            # Create summary (instead of saving to filesystem)
            summary = self.save_model_summary(results)

            logger.info("🎉 ML Training Pipeline Completed Successfully!")
            logger.info("=" * 60)
            logger.info("📋 Training Summary:")
            logger.info(summary)

            return results, summary

        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            logger.error(traceback.format_exc())
            raise


def main():
    """Main execution function"""
    trainer = ContainerMLTrainer()
    results, summary = trainer.run_complete_training()


if __name__ == "__main__":
    main()
