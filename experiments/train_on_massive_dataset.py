#!/usr/bin/env python3
"""
ML Training on Massive Dataset - Horse Racing AI v2.0
Train ML models using comprehensive SQLite databases with 125K races

Features:
- Connects to our massive SQLite databases
- Advanced feature engineering
- Multiple ML model training
- Performance evaluation and comparison
- Model persistence for production use
"""

import os
import sys
import logging
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
from pathlib import Path
import joblib

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("massive_dataset_training.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class MassiveDatasetMLTrainer:
    """
    ML Training system for massive horse racing dataset using SQLite databases.

    Uses our comprehensive databases:
    - massive_racing_data_with_markets.db (353MB) - main race data
    - ai_strategies_corrected.db (2.8MB) - AI strategies
    - production_training.db (28KB) - training sessions
    """

    def __init__(self, models_dir: str = "trained_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Database connections
        self.main_db = None
        self.strategies_db = None
        self.training_db = None

        # ML components
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        self.performance_metrics = {}

        # Database paths
        self.db_paths = {
            "main": "massive_racing_data_with_markets.db",
            "strategies": "ai_strategies_corrected.db",
            "training": "production_training.db",
        }

    def connect_databases(self) -> None:
        """Connect to all SQLite databases."""
        try:
            self.main_db = sqlite3.connect(self.db_paths["main"])
            self.strategies_db = sqlite3.connect(self.db_paths["strategies"])
            self.training_db = sqlite3.connect(self.db_paths["training"])

            logger.info("✅ Connected to all SQLite databases")

            # Log database sizes
            for name, path in self.db_paths.items():
                size_mb = os.path.getsize(path) / (1024 * 1024)
                logger.info(f"📊 {name} database: {size_mb:.1f}MB")

        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def load_massive_dataset(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load comprehensive dataset from massive racing database.

        Args:
            sample_size: Optional limit for testing (None = all data)
        """
        logger.info("📊 Loading massive dataset from SQLite databases...")

        # Enhanced query to get comprehensive features
        query = """
        SELECT 
            -- Race information
            r.race_id,
            r.race_number,
            r.course,
            r.race_type,
            r.date,
            r.distance,
            r.surface,
            r.prize_money,
            r.field_size,
            r.class_level,
            r.weather_condition,
            r.track_condition,
            
            -- Horse details
            rp.id as participant_id,
            rp.horse_name,
            rp.horse_age,
            rp.horse_weight_kg,
            rp.draw,
            rp.win_odds,
            rp.jockey_name,
            rp.trainer_name,
            rp.finished_position,
            rp.form_rating,
            rp.speed_rating,
            rp.class_rating,
            rp.market_percentage,
            
            -- Market data (synthetic enhancements)
            CASE WHEN rp.win_odds <= 3.0 THEN 1 ELSE 0 END as is_favorite,
            CASE WHEN rp.win_odds >= 20.0 THEN 1 ELSE 0 END as is_outsider,
            
            -- Target variables
            CASE WHEN rp.finished_position = 1 THEN 1 ELSE 0 END as won_race,
            rp.finished_position
            
        FROM races r
        JOIN race_participants rp ON r.race_id = rp.race_id
        WHERE rp.win_odds IS NOT NULL
        AND rp.win_odds > 0
        AND rp.horse_name IS NOT NULL
        AND rp.horse_name != ''
        """

        if sample_size:
            query += f" LIMIT {sample_size}"

        try:
            df = pd.read_sql_query(query, self.main_db)
            logger.info(f"📈 Loaded {len(df):,} training records from massive dataset")

            # Basic data validation
            logger.info(f"🏇 Unique horses: {df['horse_name'].nunique():,}")
            logger.info(f"🏁 Unique races: {df['race_id'].nunique():,}")
            logger.info(f"🏟️ Unique courses: {df['course'].nunique():,}")
            logger.info(f"🎯 Win rate: {df['won_race'].mean():.3f}")

            return df

        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Advanced feature engineering for horse racing predictions.
        """
        logger.info("🔧 Engineering advanced features...")

        # Copy dataframe to avoid modifying original
        features_df = df.copy()

        # 1. Odds-based features
        features_df["log_odds"] = np.log(features_df["win_odds"])
        features_df["odds_rank"] = features_df.groupby("race_id")["win_odds"].rank()
        features_df["odds_percentile"] = features_df.groupby("race_id")[
            "win_odds"
        ].rank(pct=True)

        # 2. Market strength indicators
        features_df["market_strength"] = 1.0 / features_df["win_odds"]
        features_df["total_market"] = features_df.groupby("race_id")[
            "market_strength"
        ].transform("sum")
        features_df["market_share"] = (
            features_df["market_strength"] / features_df["total_market"]
        )

        # 3. Field size and competition
        features_df["field_size_calc"] = features_df.groupby("race_id")[
            "participant_id"
        ].transform("count")
        features_df["draw_percentile"] = features_df.groupby("race_id")["draw"].rank(
            pct=True
        )

        # 4. Weight and age features
        features_df["weight_percentile"] = features_df.groupby("race_id")[
            "horse_weight_kg"
        ].rank(pct=True)
        features_df["age_category"] = pd.cut(
            features_df["horse_age"], bins=[0, 3, 5, 8, 20], labels=[1, 2, 3, 4]
        )

        # 5. Distance categories
        features_df["distance_category"] = pd.cut(
            features_df["distance"].astype(str).str.extract("(\d+)")[0].astype(float),
            bins=[0, 1200, 1600, 2000, 10000],
            labels=[1, 2, 3, 4],
        )

        # 6. Prize and class indicators
        features_df["log_prize"] = np.log(features_df["prize_money"] + 1)
        features_df["prize_per_runner"] = (
            features_df["prize_money"] / features_df["field_size"]
        )

        # 7. Historical performance (simplified)
        features_df["horse_experience"] = (
            features_df.groupby("horse_name").cumcount() + 1
        )
        features_df["trainer_experience"] = (
            features_df.groupby("trainer_name").cumcount() + 1
        )
        features_df["jockey_experience"] = (
            features_df.groupby("jockey_name").cumcount() + 1
        )

        # 8. Rating features (available in our data)
        features_df["rating_rank"] = features_df.groupby("race_id")["form_rating"].rank(
            ascending=False
        )
        features_df["rating_percentile"] = features_df.groupby("race_id")[
            "form_rating"
        ].rank(pct=True)

        # 9. Interaction features
        features_df["odds_weight_ratio"] = features_df["win_odds"] / (
            features_df["horse_weight_kg"] + 1
        )
        features_df["rating_odds_ratio"] = (
            features_df["form_rating"] / features_df["win_odds"]
        )

        # 10. Course and surface encoding
        le_course = LabelEncoder()
        le_surface = LabelEncoder()
        le_race_type = LabelEncoder()

        features_df["course_encoded"] = le_course.fit_transform(
            features_df["course"].fillna("Unknown")
        )
        features_df["surface_encoded"] = le_surface.fit_transform(
            features_df["surface"].fillna("Turf")
        )
        features_df["race_type_encoded"] = le_race_type.fit_transform(
            features_df["race_type"].fillna("Flat")
        )

        # Store encoders
        self.encoders = {
            "course": le_course,
            "surface": le_surface,
            "race_type": le_race_type,
        }

        logger.info(
            f"✅ Feature engineering complete. Features: {len(features_df.columns)}"
        )

        return features_df

    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for ML training.
        """
        logger.info("🎯 Preparing training data...")

        # Select numerical features for training
        feature_columns = [
            "log_odds",
            "odds_rank",
            "odds_percentile",
            "is_favorite",
            "is_outsider",
            "market_strength",
            "market_share",
            "draw_percentile",
            "weight_percentile",
            "field_size",
            "age_category",
            "distance_category",
            "log_prize",
            "prize_per_runner",
            "horse_experience",
            "trainer_experience",
            "jockey_experience",
            "odds_weight_ratio",
            "rating_odds_ratio",
            "course_encoded",
            "surface_encoded",
            "race_type_encoded",
        ]

        # Add rating features if available
        if "rating_rank" in df.columns:
            feature_columns.extend(["rating_rank", "rating_percentile"])

        # Filter existing columns
        available_features = [col for col in feature_columns if col in df.columns]

        # Prepare features
        X = df[available_features].copy()

        # Handle missing values
        X = X.fillna(X.median())

        # Target variable
        y = df["won_race"]

        # Store feature names
        self.feature_names = available_features

        logger.info(f"🔢 Training features: {len(available_features)}")
        logger.info(f"📊 Training samples: {len(X):,}")
        logger.info(f"🎯 Win rate: {y.mean():.3f}")

        return X, y

    def train_models(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train multiple ML models with the massive dataset.
        """
        logger.info("🚀 Training ML models on massive dataset...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"📊 Training set: {len(X_train):,} samples")
        logger.info(f"📊 Test set: {len(X_test):,} samples")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Store scaler
        self.scalers["feature_scaler"] = scaler

        # Model configurations
        models_config = {
            "random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42
            ),
            "extra_trees": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1,
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(200, 100),
                activation="relu",
                alpha=0.001,
                learning_rate="adaptive",
                max_iter=1000,
                random_state=42,
            ),
            "logistic_regression": LogisticRegression(
                C=1.0, penalty="l2", max_iter=2000, random_state=42
            ),
        }

        # Train each model
        for name, model in models_config.items():
            logger.info(f"🔧 Training {name}...")

            try:
                # Train model
                if name == "neural_network":
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    y_prob = model.predict_proba(X_test_scaled)[:, 1]
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_prob = model.predict_proba(X_test)[:, 1]

                # Calculate metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred),
                    "recall": recall_score(y_test, y_pred),
                    "f1": f1_score(y_test, y_pred),
                    "roc_auc": roc_auc_score(y_test, y_prob),
                }

                # Store model and metrics
                self.models[name] = model
                self.performance_metrics[name] = metrics

                logger.info(
                    f"✅ {name} - Accuracy: {metrics['accuracy']:.3f}, ROC-AUC: {metrics['roc_auc']:.3f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {name}: {e}")

        # Create ensemble model
        self._create_ensemble_model(X_train, y_train, X_test, y_test)

    def _create_ensemble_model(self, X_train, y_train, X_test, y_test) -> None:
        """Create ensemble model from trained models."""
        logger.info("🎭 Creating ensemble model...")

        try:
            # Select best performing models for ensemble
            estimators = []
            for name, model in self.models.items():
                if name != "neural_network":  # Exclude neural network for ensemble
                    estimators.append((name, model))

            # Create voting classifier
            ensemble = VotingClassifier(estimators=estimators, voting="soft")
            ensemble.fit(X_train, y_train)

            # Evaluate ensemble
            y_pred = ensemble.predict(X_test)
            y_prob = ensemble.predict_proba(X_test)[:, 1]

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_prob),
            }

            self.models["ensemble"] = ensemble
            self.performance_metrics["ensemble"] = metrics

            logger.info(
                f"✅ Ensemble - Accuracy: {metrics['accuracy']:.3f}, ROC-AUC: {metrics['roc_auc']:.3f}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to create ensemble: {e}")

    def save_models(self) -> None:
        """Save all trained models and components."""
        logger.info("💾 Saving trained models...")

        try:
            # Save models
            for name, model in self.models.items():
                model_path = self.models_dir / f"{name}_massive_dataset.joblib"
                joblib.dump(model, model_path)
                logger.info(f"💾 Saved {name} model")

            # Save scalers and encoders
            scalers_path = self.models_dir / "scalers_massive_dataset.joblib"
            joblib.dump(self.scalers, scalers_path)

            encoders_path = self.models_dir / "encoders_massive_dataset.joblib"
            joblib.dump(self.encoders, encoders_path)

            # Save feature names
            features_path = self.models_dir / "feature_names_massive_dataset.joblib"
            joblib.dump(self.feature_names, features_path)

            # Save performance metrics
            metrics_path = (
                self.models_dir / "performance_metrics_massive_dataset.joblib"
            )
            joblib.dump(self.performance_metrics, metrics_path)

            logger.info(f"✅ All models saved to {self.models_dir}")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")

    def print_performance_summary(self) -> None:
        """Print performance summary of all models."""
        logger.info("\n" + "=" * 60)
        logger.info("🏆 MODEL PERFORMANCE SUMMARY")
        logger.info("=" * 60)

        for model_name, metrics in self.performance_metrics.items():
            logger.info(f"\n🤖 {model_name.upper()}")
            logger.info("-" * 40)
            for metric, value in metrics.items():
                logger.info(f"{metric:>15}: {value:.4f}")

        # Find best model
        best_model = max(
            self.performance_metrics.items(), key=lambda x: x[1]["roc_auc"]
        )

        logger.info(f"\n🥇 BEST MODEL: {best_model[0].upper()}")
        logger.info(f"🎯 ROC-AUC: {best_model[1]['roc_auc']:.4f}")
        logger.info("=" * 60)

    def run_complete_training(self, sample_size: Optional[int] = None) -> None:
        """
        Run the complete ML training pipeline.

        Args:
            sample_size: Optional limit for testing (None = all data)
        """
        start_time = datetime.now()

        logger.info("🚀 MASSIVE DATASET ML TRAINING PIPELINE")
        logger.info("=" * 60)

        try:
            # 1. Connect to databases
            self.connect_databases()

            # 2. Load massive dataset
            df = self.load_massive_dataset(sample_size)

            # 3. Engineer features
            df_features = self.engineer_features(df)

            # 4. Prepare training data
            X, y = self.prepare_training_data(df_features)

            # 5. Train models
            self.train_models(X, y)

            # 6. Save models
            self.save_models()

            # 7. Print summary
            self.print_performance_summary()

            training_time = datetime.now() - start_time
            logger.info(f"\n🎉 TRAINING COMPLETE!")
            logger.info(f"⏱️ Total time: {training_time}")
            logger.info(f"📊 Models trained on {len(df):,} records")
            logger.info(f"💾 Models saved to: {self.models_dir}")

        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            raise
        finally:
            # Close database connections
            if self.main_db:
                self.main_db.close()
            if self.strategies_db:
                self.strategies_db.close()
            if self.training_db:
                self.training_db.close()


def main():
    """Main training function."""
    trainer = MassiveDatasetMLTrainer()

    # For testing, use sample_size=10000. For full training, use None
    sample_size = None  # Use None for full dataset training

    trainer.run_complete_training(sample_size=sample_size)


if __name__ == "__main__":
    main()
