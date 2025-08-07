#!/usr/bin/env python3
"""
ML Training Pipeline for Horse Racing AI v2.0

This script trains machine learning models using the generated fake data:
- Feature engineering from race and horse data
- Multiple ML models (Random Forest, XGBoost, Neural Networks)
- Cross-validation and performance evaluation
- Model persistence for production use
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, date
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import warnings

warnings.filterwarnings("ignore")

# Setup environment
os.environ["DATABASE_URL"] = (
    "postgresql://horse_racing_test:test_password_123@localhost:5434/horse_racing_test_db"
)

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from src.database.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MLTrainingPipeline:
    """Machine Learning Training Pipeline for Horse Racing Predictions"""

    def __init__(self):
        """Initialize the ML training pipeline"""
        self.db = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        self.training_results = {}

    def initialize_database(self):
        """Initialize database connection"""
        logger.info("🔗 Initializing database connection...")
        self.db = DatabaseManager()

        summary = self.db.get_database_summary()
        logger.info(
            f"📊 Database: {summary['tables']['races_cards']} races, "
            f"{summary['tables']['racecard_details']} participants"
        )

    def extract_features(self) -> pd.DataFrame:
        """Extract and engineer features from the database"""
        logger.info("🔍 Extracting features from race data...")

        # Get all race data with participants
        races_query = """
            SELECT 
                rc.*,
                rd.name as horse_name,
                rd.jockey,
                rd.trainer,
                rd.weight,
                rd.odds,
                rd.draw,
                hc.age,
                hc.total_races,
                hc.wins,
                hc.percentage_wins,
                hc.placed,
                hc.percentage_placed,
                hc.flat_turf_races,
                hc.flat_turf_wins,
                hc.flat_turf_rate
            FROM races_cards rc
            JOIN racecard_details rd ON rc.race_id = rd.race_id
            LEFT JOIN horses_cards hc ON rd.name = hc.name
            ORDER BY rc.date DESC, rc.race_time ASC
        """

        df = pd.DataFrame(self.db.execute_query(races_query))
        logger.info(f"📈 Extracted {len(df)} race entries")

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for machine learning"""
        logger.info("⚙️ Engineering features...")

        # Convert date and time features
        df["date"] = pd.to_datetime(df["date"])
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month

        # Convert race_time to minutes from midnight
        df["race_time_str"] = df["race_time"].astype(str)
        df["race_hour"] = df["race_time_str"].str[:2].astype(int)
        df["race_minute"] = df["race_time_str"].str[3:5].astype(int)
        df["race_minutes_from_midnight"] = df["race_hour"] * 60 + df["race_minute"]

        # Clean and convert numeric features
        df["runners"] = pd.to_numeric(df["runners"], errors="coerce").fillna(0)
        df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(4)
        df["total_races"] = pd.to_numeric(df["total_races"], errors="coerce").fillna(0)
        df["wins"] = pd.to_numeric(df["wins"], errors="coerce").fillna(0)
        df["percentage_wins"] = pd.to_numeric(
            df["percentage_wins"], errors="coerce"
        ).fillna(0)
        df["placed"] = pd.to_numeric(df["placed"], errors="coerce").fillna(0)
        df["percentage_placed"] = pd.to_numeric(
            df["percentage_placed"], errors="coerce"
        ).fillna(0)
        df["flat_turf_races"] = pd.to_numeric(
            df["flat_turf_races"], errors="coerce"
        ).fillna(0)
        df["flat_turf_wins"] = pd.to_numeric(
            df["flat_turf_wins"], errors="coerce"
        ).fillna(0)
        df["flat_turf_rate"] = pd.to_numeric(
            df["flat_turf_rate"], errors="coerce"
        ).fillna(0)
        df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(5)

        # Parse weight (assuming format like "9-10" or "10-2")
        df["weight_str"] = df["weight"].astype(str)
        df["weight_stones"] = df["weight_str"].str.split("-").str[0]
        df["weight_pounds"] = df["weight_str"].str.split("-").str[1]
        df["weight_stones"] = pd.to_numeric(
            df["weight_stones"], errors="coerce"
        ).fillna(9)
        df["weight_pounds"] = pd.to_numeric(
            df["weight_pounds"], errors="coerce"
        ).fillna(0)
        df["total_weight_lbs"] = df["weight_stones"] * 14 + df["weight_pounds"]

        # Parse odds (assuming format like "3/1" or "7/2")
        df["odds_str"] = df["odds"].astype(str)
        df["odds_numerator"] = df["odds_str"].str.split("/").str[0]
        df["odds_denominator"] = df["odds_str"].str.split("/").str[1]
        df["odds_numerator"] = pd.to_numeric(
            df["odds_numerator"], errors="coerce"
        ).fillna(3)
        df["odds_denominator"] = pd.to_numeric(
            df["odds_denominator"], errors="coerce"
        ).fillna(1)
        df["odds_decimal"] = (df["odds_numerator"] / df["odds_denominator"]) + 1
        df["implied_probability"] = 1 / df["odds_decimal"]

        # Feature engineering
        df["form_rating"] = (df["percentage_wins"] * 0.6) + (
            df["percentage_placed"] * 0.4
        )
        df["experience_rating"] = np.log1p(df["total_races"]) * 10
        df["weight_burden"] = df["total_weight_lbs"] - 126  # 9 stone is typical
        df["draw_advantage"] = np.where(
            df["draw"] <= 3, 1, 0
        )  # Low draws often advantageous

        # Course and race type encoding
        course_encoder = LabelEncoder()
        df["course_encoded"] = course_encoder.fit_transform(
            df["course"].fillna("Unknown")
        )
        self.encoders["course"] = course_encoder

        race_type_encoder = LabelEncoder()
        df["race_type_encoded"] = race_type_encoder.fit_transform(
            df["race_type"].fillna("Unknown")
        )
        self.encoders["race_type"] = race_type_encoder

        surface_encoder = LabelEncoder()
        df["surface_encoded"] = surface_encoder.fit_transform(
            df["surface"].fillna("Turf")
        )
        self.encoders["surface"] = surface_encoder

        # Create target variable (simulate win probability based on odds and form)
        # For training purposes, create realistic win outcomes
        np.random.seed(42)  # For reproducible results

        # Higher probability for horses with better odds and form
        win_probability = (
            df["implied_probability"] * 0.4
            + (df["form_rating"] / 100) * 0.3
            + (1 / (df["draw"] + 1)) * 0.1
            + np.random.normal(0, 0.1, len(df))
        )

        # Normalize probabilities within each race
        race_groups = df.groupby("race_id")
        normalized_probs = []
        for race_id, group in race_groups:
            group_probs = win_probability[group.index]
            group_probs = np.maximum(group_probs, 0.01)  # Minimum probability
            group_probs = group_probs / group_probs.sum()
            normalized_probs.extend(group_probs)

        df["win_probability"] = normalized_probs

        # Create binary win target (simulate actual winners)
        df["is_winner"] = 0
        for race_id, group in race_groups:
            # Get normalized probabilities for this race
            probs = df.loc[group.index, "win_probability"].values
            # Ensure they sum to exactly 1 (handle floating point precision)
            if abs(probs.sum() - 1.0) > 1e-6:
                probs = probs / probs.sum()
            winner_idx = np.random.choice(group.index, p=probs)
            df.loc[winner_idx, "is_winner"] = 1

        logger.info(
            f"✅ Feature engineering complete: {len(df)} entries, {df['is_winner'].sum()} winners"
        )

        return df

    def prepare_training_data(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for training"""
        logger.info("📊 Preparing training data...")

        # Select features for training
        feature_columns = [
            "runners",
            "age",
            "total_races",
            "wins",
            "percentage_wins",
            "percentage_placed",
            "flat_turf_races",
            "flat_turf_wins",
            "flat_turf_rate",
            "draw",
            "total_weight_lbs",
            "odds_decimal",
            "implied_probability",
            "form_rating",
            "experience_rating",
            "weight_burden",
            "draw_advantage",
            "course_encoded",
            "race_type_encoded",
            "surface_encoded",
            "day_of_week",
            "month",
            "race_minutes_from_midnight",
        ]

        # Ensure all feature columns exist
        available_features = [col for col in feature_columns if col in df.columns]
        missing_features = [col for col in feature_columns if col not in df.columns]

        if missing_features:
            logger.warning(f"Missing features: {missing_features}")

        X = df[available_features].copy()
        y = df["is_winner"].copy()

        # Handle missing values
        X = X.fillna(X.mean())

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        self.scalers["features"] = scaler
        self.feature_names = available_features

        logger.info(
            f"📈 Training data prepared: {X_scaled.shape[0]} samples, {X_scaled.shape[1]} features"
        )
        logger.info(
            f"🎯 Target distribution: {(y == 1).sum()} winners, {(y == 0).sum()} non-winners"
        )

        return X_scaled, y.values, available_features

    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train multiple ML models"""
        logger.info("🤖 Training machine learning models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Define models
        models_config = {
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, max_depth=6, random_state=42
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
            ),
        }

        results = {}

        for model_name, model in models_config.items():
            logger.info(f"🔧 Training {model_name}...")

            # Train model
            model.fit(X_train, y_train)

            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            auc_score = roc_auc_score(y_test, y_pred_proba)

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring="accuracy"
            )

            results[model_name] = {
                "model": model,
                "accuracy": accuracy,
                "auc_score": auc_score,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "classification_report": classification_report(
                    y_test, y_pred, output_dict=True
                ),
            }

            # Store model
            self.models[model_name] = model

            logger.info(
                f"✅ {model_name}: Accuracy={accuracy:.3f}, AUC={auc_score:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}"
            )

        self.training_results = results
        return results

    def save_models(self):
        """Save trained models and preprocessing objects"""
        logger.info("💾 Saving trained models...")

        models_dir = "trained_models"
        os.makedirs(models_dir, exist_ok=True)

        # Save models
        for model_name, model in self.models.items():
            model_path = f"{models_dir}/{model_name}_model.joblib"
            joblib.dump(model, model_path)
            logger.info(f"💾 Saved {model_name} to {model_path}")

        # Save preprocessing objects
        joblib.dump(self.scalers, f"{models_dir}/scalers.joblib")
        joblib.dump(self.encoders, f"{models_dir}/encoders.joblib")
        joblib.dump(self.feature_names, f"{models_dir}/feature_names.joblib")

        # Save training results
        import json

        results_for_json = {}
        for model_name, result in self.training_results.items():
            results_for_json[model_name] = {
                "accuracy": result["accuracy"],
                "auc_score": result["auc_score"],
                "cv_mean": result["cv_mean"],
                "cv_std": result["cv_std"],
            }

        with open(f"{models_dir}/training_results.json", "w") as f:
            json.dump(results_for_json, f, indent=2)

        logger.info(f"💾 All models and metadata saved to {models_dir}/")

    def generate_training_report(self):
        """Generate comprehensive training report"""
        logger.info("📊 Generating training report...")

        print("\n" + "🏁" * 60)
        print("🤖 MACHINE LEARNING TRAINING RESULTS")
        print("🏁" * 60)

        print(f"📅 Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Features Used: {len(self.feature_names)}")
        print(f"🎯 Models Trained: {len(self.models)}")

        print("\n📊 MODEL PERFORMANCE SUMMARY:")
        print("-" * 60)

        for model_name, result in self.training_results.items():
            print(f"\n🤖 {model_name.upper().replace('_', ' ')}")
            print(f"   ✅ Accuracy: {result['accuracy']:.3f}")
            print(f"   📈 AUC Score: {result['auc_score']:.3f}")
            print(f"   🔄 Cross-Val: {result['cv_mean']:.3f} ± {result['cv_std']:.3f}")

            # Feature importance for tree-based models
            if hasattr(result["model"], "feature_importances_"):
                importances = result["model"].feature_importances_
                top_features_idx = np.argsort(importances)[-5:][::-1]
                print(f"   🔝 Top Features:")
                for idx in top_features_idx:
                    print(f"      {self.feature_names[idx]}: {importances[idx]:.3f}")

        # Find best model
        best_model_name = max(
            self.training_results.keys(),
            key=lambda x: self.training_results[x]["auc_score"],
        )
        best_score = self.training_results[best_model_name]["auc_score"]

        print(f"\n🏆 BEST MODEL: {best_model_name.upper().replace('_', ' ')}")
        print(f"🎯 Best AUC Score: {best_score:.3f}")

        print("\n💾 Models saved to 'trained_models/' directory")
        print("🏁" * 60)

    def run_complete_training(self):
        """Run the complete ML training pipeline"""
        logger.info("🚀 Starting ML Training Pipeline")
        logger.info("=" * 60)

        try:
            # Initialize database
            self.initialize_database()

            # Extract features
            df = self.extract_features()

            # Engineer features
            df_engineered = self.engineer_features(df)

            # Prepare training data
            X, y, features = self.prepare_training_data(df_engineered)

            # Train models
            self.train_models(X, y)

            # Save models
            self.save_models()

            # Generate report
            self.generate_training_report()

            logger.info("🎉 ML Training Pipeline completed successfully!")

        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise
        finally:
            if self.db:
                self.db.close()


if __name__ == "__main__":
    # Run the training pipeline
    trainer = MLTrainingPipeline()
    trainer.run_complete_training()
