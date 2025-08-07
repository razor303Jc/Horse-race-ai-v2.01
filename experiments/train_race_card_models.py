#!/usr/bin/env python3
"""
Race Card Prediction ML Training
Train ML models specifically on race card data (pre-race prediction)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
import joblib
import warnings

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceCardMLTrainer:
    """ML trainer for race card predictions."""

    def __init__(self, race_cards_db: str = "race_cards_prediction_data.db"):
        self.race_cards_db = race_cards_db
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        self.performance = {}

        # Create models directory
        self.models_dir = Path("trained_models/race_card_models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def load_race_card_data(self) -> pd.DataFrame:
        """Load race card data for ML training."""

        logger.info("📊 Loading race card data...")

        conn = sqlite3.connect(self.race_cards_db)

        # Comprehensive query with all available features
        query = """
        SELECT 
            rc.race_id,
            rc.course,
            rc.race_type,
            rc.distance,
            rc.surface,
            rc.field_size,
            rc.prize_money,
            rc.class_level,
            rc.weather_condition,
            rc.track_condition,
            rc.going,
            
            rce.entry_id,
            rce.horse_name,
            rce.horse_age,
            rce.horse_weight_kg,
            rce.draw,
            rce.morning_line_odds,
            rce.recent_form_rating,
            rce.speed_rating,
            rce.class_rating,
            rce.track_rating,
            rce.distance_rating,
            rce.jockey_rating,
            rce.trainer_rating,
            rce.career_starts,
            rce.career_wins,
            rce.career_places,
            rce.last_start_days,
            rce.form_string,
            rce.equipment,
            rce.comments
            
        FROM race_cards rc
        JOIN race_card_entries rce ON rc.race_id = rce.race_id
        WHERE rce.morning_line_odds IS NOT NULL
        AND rce.morning_line_odds > 0
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(f"📈 Loaded {len(df):,} race card entries")
        logger.info(f"🏁 Unique races: {df['race_id'].nunique():,}")
        logger.info(f"🏇 Unique horses: {df['horse_name'].nunique():,}")

        return df

    def engineer_race_card_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features specifically for race card prediction."""

        logger.info("🔧 Engineering race card prediction features...")

        # Create synthetic win probabilities based on odds (for training)
        # This simulates what we would predict
        df["implied_prob"] = 1.0 / df["morning_line_odds"]
        df["market_share"] = df.groupby("race_id")["implied_prob"].transform(
            lambda x: x / x.sum()
        )

        # Create target variable (simulate favorite vs field)
        df["is_favorite"] = (
            df.groupby("race_id")["morning_line_odds"]
            .transform(lambda x: x == x.min())
            .astype(int)
        )

        # Create synthetic win target based on market probabilities
        # (In real scenario, this would come from actual results)
        np.random.seed(42)  # For reproducible results
        df["won_race"] = 0
        for race_id in df["race_id"].unique():
            race_entries = df[df["race_id"] == race_id]
            probs = race_entries["market_share"].values
            # Weighted random selection based on market probabilities
            winner_idx = np.random.choice(len(probs), p=probs / probs.sum())
            winner_entry_id = race_entries.iloc[winner_idx]["entry_id"]
            df.loc[df["entry_id"] == winner_entry_id, "won_race"] = 1

        # Odds-based features
        df["log_odds"] = np.log(df["morning_line_odds"])
        df["odds_rank"] = df.groupby("race_id")["morning_line_odds"].rank()
        df["odds_percentile"] = df.groupby("race_id")["morning_line_odds"].rank(
            pct=True
        )
        df["is_outsider"] = (df["morning_line_odds"] >= 20.0).astype(int)

        # Market features
        df["market_strength"] = 1.0 / df["morning_line_odds"]

        # Competition features
        df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
        df["weight_percentile"] = df.groupby("race_id")["horse_weight_kg"].rank(
            pct=True
        )
        df["age_percentile"] = df.groupby("race_id")["horse_age"].rank(pct=True)

        # Rating features and rankings
        df["total_rating"] = (
            df["recent_form_rating"] + df["speed_rating"] + df["class_rating"]
        ) / 3
        df["form_rank"] = df.groupby("race_id")["recent_form_rating"].rank(
            ascending=False
        )
        df["speed_rank"] = df.groupby("race_id")["speed_rating"].rank(ascending=False)
        df["total_rating_rank"] = df.groupby("race_id")["total_rating"].rank(
            ascending=False
        )

        # Experience features
        df["win_rate"] = df["career_wins"] / (df["career_starts"] + 1)
        df["place_rate"] = df["career_places"] / (df["career_starts"] + 1)
        df["experience_score"] = np.log(df["career_starts"] + 1)

        # Recency features
        df["days_since_last_run"] = df["last_start_days"]
        df["freshness_score"] = 1.0 / (df["last_start_days"] + 1)

        # Form string analysis
        def analyze_form_string(form_str):
            if pd.isna(form_str) or form_str == "":
                return 0, 0, 0

            recent_wins = form_str[:3].count("1")
            recent_places = form_str[:3].count("2") + form_str[:3].count("3")
            consistency = len([x for x in form_str[:5] if x.isdigit() and int(x) <= 5])

            return recent_wins, recent_places, consistency

        form_analysis = df["form_string"].apply(analyze_form_string)
        df["recent_wins"] = [x[0] for x in form_analysis]
        df["recent_places"] = [x[1] for x in form_analysis]
        df["form_consistency"] = [x[2] for x in form_analysis]

        # Distance processing
        df["distance_numeric"] = pd.to_numeric(
            df["distance"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
        ).fillna(1600)

        # Prize money features
        df["log_prize"] = np.log(df["prize_money"] + 1)
        df["prize_per_runner"] = df["prize_money"] / df["field_size"]

        # Equipment and comments flags
        df["has_equipment"] = (~df["equipment"].isin(["", None])).astype(int)
        df["has_comments"] = (~df["comments"].isin(["", None])).astype(int)

        logger.info(
            f"✅ Feature engineering complete. Total features: {len(df.columns)}"
        )

        return df

    def prepare_training_data(self, df: pd.DataFrame):
        """Prepare features and target for ML training."""

        logger.info("🎯 Preparing training data...")

        # Encode categorical features
        encoders = {}
        categorical_features = [
            "course",
            "race_type",
            "surface",
            "class_level",
            "weather_condition",
            "track_condition",
            "going",
        ]

        for feature in categorical_features:
            le = LabelEncoder()
            df[f"{feature}_encoded"] = le.fit_transform(df[feature].fillna("Unknown"))
            encoders[feature] = le

        self.encoders = encoders

        # Select numerical features for training
        feature_columns = [
            # Basic features
            "horse_age",
            "horse_weight_kg",
            "draw",
            "field_size",
            # Odds features
            "log_odds",
            "odds_rank",
            "odds_percentile",
            "is_favorite",
            "is_outsider",
            "market_strength",
            "market_share",
            # Competition features
            "draw_percentile",
            "weight_percentile",
            "age_percentile",
            # Rating features
            "recent_form_rating",
            "speed_rating",
            "class_rating",
            "track_rating",
            "distance_rating",
            "jockey_rating",
            "trainer_rating",
            "total_rating",
            "form_rank",
            "speed_rank",
            "total_rating_rank",
            # Experience features
            "career_starts",
            "career_wins",
            "career_places",
            "win_rate",
            "place_rate",
            "experience_score",
            # Recency features
            "days_since_last_run",
            "freshness_score",
            # Form features
            "recent_wins",
            "recent_places",
            "form_consistency",
            # Race features
            "distance_numeric",
            "log_prize",
            "prize_per_runner",
            # Equipment flags
            "has_equipment",
            "has_comments",
            # Encoded categorical features
            "course_encoded",
            "race_type_encoded",
            "surface_encoded",
            "class_level_encoded",
            "weather_condition_encoded",
            "track_condition_encoded",
            "going_encoded",
        ]

        # Filter existing columns
        available_features = [col for col in feature_columns if col in df.columns]
        self.feature_names = available_features

        # Prepare features and target
        X = df[available_features].fillna(0)
        y = df["won_race"]

        logger.info(f"🔢 Training features: {len(available_features)}")
        logger.info(f"📊 Training samples: {len(X):,}")
        logger.info(f"🎯 Win rate: {y.mean():.4f}")

        return X, y

    def train_race_card_models(self, X, y):
        """Train ML models for race card prediction."""

        logger.info("🚀 Training race card prediction models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"📊 Training set: {len(X_train):,}")
        logger.info(f"📊 Test set: {len(X_test):,}")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers["feature_scaler"] = scaler

        # Model configurations optimized for race card prediction
        models_config = {
            "random_forest": RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_split=3,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(150, 75),
                activation="relu",
                alpha=0.001,
                learning_rate="adaptive",
                max_iter=800,
                random_state=42,
            ),
            "logistic_regression": LogisticRegression(
                C=1.0, penalty="l2", max_iter=1500, random_state=42
            ),
        }

        # Train each model
        for name, model in models_config.items():
            logger.info(f"🔧 Training {name}...")

            try:
                # Use scaled features for neural network
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
                    "precision": precision_score(y_test, y_pred, zero_division=0),
                    "recall": recall_score(y_test, y_pred, zero_division=0),
                    "f1": f1_score(y_test, y_pred, zero_division=0),
                    "roc_auc": roc_auc_score(y_test, y_prob),
                }

                self.models[name] = model
                self.performance[name] = metrics

                logger.info(
                    f"✅ {name} - Accuracy: {metrics['accuracy']:.3f}, AUC: {metrics['roc_auc']:.3f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {name}: {e}")

    def save_race_card_models(self):
        """Save all trained models and components."""

        logger.info("💾 Saving race card prediction models...")

        try:
            # Save models
            for name, model in self.models.items():
                model_path = self.models_dir / f"{name}_race_card.joblib"
                joblib.dump(model, model_path)

            # Save scalers and encoders
            joblib.dump(self.scalers, self.models_dir / "scalers_race_card.joblib")
            joblib.dump(self.encoders, self.models_dir / "encoders_race_card.joblib")
            joblib.dump(
                self.feature_names, self.models_dir / "features_race_card.joblib"
            )
            joblib.dump(
                self.performance, self.models_dir / "performance_race_card.joblib"
            )

            logger.info(f"✅ Models saved to {self.models_dir}")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")

    def run_complete_training(self):
        """Run complete race card ML training pipeline."""

        start_time = datetime.now()

        logger.info("🚀 RACE CARD ML TRAINING PIPELINE")
        logger.info("=" * 50)

        try:
            # Load data
            df = self.load_race_card_data()

            # Engineer features
            df = self.engineer_race_card_features(df)

            # Prepare training data
            X, y = self.prepare_training_data(df)

            # Train models
            self.train_race_card_models(X, y)

            # Save models
            self.save_race_card_models()

            # Print performance summary
            training_time = datetime.now() - start_time

            logger.info("\n🏆 RACE CARD TRAINING COMPLETE!")
            logger.info("=" * 50)
            logger.info(f"📊 Total entries: {len(df):,}")
            logger.info(f"⏱️ Training time: {training_time}")
            logger.info(f"💾 Models saved to: {self.models_dir}")

            logger.info("\n🎯 MODEL PERFORMANCE:")
            logger.info("-" * 30)
            for model_name, metrics in self.performance.items():
                logger.info(f"{model_name}:")
                logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
                logger.info(f"  AUC:      {metrics['roc_auc']:.4f}")

            return True

        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            return False


def main():
    """Main training function."""

    trainer = RaceCardMLTrainer()
    success = trainer.run_complete_training()

    if success:
        logger.info("\n✅ Race card ML models ready for predictions!")
    else:
        logger.error("\n❌ Race card training failed")


if __name__ == "__main__":
    main()
