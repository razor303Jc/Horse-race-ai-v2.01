#!/usr/bin/env python3
"""
Simple Enhanced ML Training - Horse Racing AI v2.0
Training ML models on the migrated massive dataset with simplified approach
"""
import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("simple_ml_training.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class SimpleMLTrainer:
    """Simple but effective ML training on massive dataset."""

    def __init__(self):
        self.engine = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.performance = {}

        # Ensure models directory exists
        os.makedirs("models", exist_ok=True)

    def connect_database(self) -> None:
        """Connect to database."""
        try:
            load_dotenv()
            database_url = os.getenv("DATABASE_URL")
            self.engine = create_engine(database_url)
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def load_training_data(self) -> pd.DataFrame:
        """Load training data from migrated tables."""
        logger.info("📊 Loading training data...")

        # Simple query to get essential features
        query = """
        SELECT 
            rc.race_id,
            rc.course,
            rc.race_type,
            rc.distance,
            rc.surface,
            rc.prize,
            rd.race_id as detail_race_id,
            rd.horse_id,
            rd.name as horse_name,
            rd.age,
            rd.weight,
            rd.draw,
            rd.odds_decimal,
            rd.jockey,
            rd.trainer,
            rd.timeform_comments
        FROM races_cards rc
        JOIN racecard_details rd ON rc.race_id = rd.race_id
        WHERE rd.odds_decimal IS NOT NULL 
        AND rd.odds_decimal > 0
        LIMIT 50000
        """

        try:
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"📈 Loaded {len(df):,} training records")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            raise

    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create win/loss target from timeform comments."""
        logger.info("🎯 Creating target variable...")

        # Extract finishing position from timeform comments
        df["finish_position"] = (
            df["timeform_comments"].str.extract(r"Finished: (\d+)").astype(float)
        )

        # Create binary win target
        df["won_race"] = (df["finish_position"] == 1).astype(int)

        # Remove records without finish position
        df = df.dropna(subset=["finish_position"])

        win_rate = df["won_race"].mean()
        logger.info(
            f"📊 Win rate: {win_rate:.4f} ({df['won_race'].sum():,} wins from {len(df):,} races)"
        )

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Simple but effective feature engineering."""
        logger.info("🔧 Engineering features...")

        # Fill missing values and ensure numeric types
        df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(4)
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(60)
        df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(1)
        df["distance"] = pd.to_numeric(df["distance"], errors="coerce").fillna(1600)
        df["prize"] = pd.to_numeric(df["prize"], errors="coerce").fillna(10000)
        df["odds_decimal"] = pd.to_numeric(df["odds_decimal"], errors="coerce")

        # Remove invalid odds
        df = df[df["odds_decimal"] > 0]

        # Odds-based features
        df["odds_log"] = np.log(df["odds_decimal"])
        df["implied_prob"] = 1 / df["odds_decimal"]

        # Race-level features
        race_stats = (
            df.groupby("race_id")
            .agg(
                {
                    "race_id": "count",  # field size
                    "odds_decimal": "min",  # best odds in race
                }
            )
            .rename(columns={"race_id": "field_size", "odds_decimal": "best_odds"})
        )

        df = df.merge(race_stats, on="race_id", how="left")

        # Positional features
        df["odds_rank"] = df.groupby("race_id")["odds_decimal"].rank()
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)
        df["draw_percentage"] = df["draw"] / df["field_size"]

        # Age categories
        df["is_young"] = (df["age"] <= 3).astype(int)
        df["is_veteran"] = (df["age"] >= 8).astype(int)

        # Prize categories
        df["prize_log"] = np.log(df["prize"])
        df["high_value"] = (df["prize"] > df["prize"].quantile(0.75)).astype(int)

        # Encode categorical variables
        categorical_cols = ["course", "race_type", "surface", "jockey", "trainer"]

        for col in categorical_cols:
            df[col] = df[col].fillna("Unknown")
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col])
            self.encoders[col] = le

        logger.info(f"✅ Feature engineering completed: {len(df.columns)} columns")
        return df

    def prepare_training_data(self, df: pd.DataFrame):
        """Prepare features and target for training."""
        logger.info("🎯 Preparing training data...")

        # Define feature columns
        feature_cols = [
            "age",
            "weight",
            "draw",
            "distance",
            "prize_log",
            "odds_log",
            "implied_prob",
            "field_size",
            "odds_rank",
            "is_favorite",
            "draw_percentage",
            "is_young",
            "is_veteran",
            "high_value",
            "course_encoded",
            "race_type_encoded",
            "surface_encoded",
            "jockey_encoded",
            "trainer_encoded",
        ]

        # Prepare features and target
        X = df[feature_cols].values
        y = df["won_race"].values

        logger.info(f"📊 Training data shape: {X.shape}")
        logger.info(f"📊 Feature count: {len(feature_cols)}")
        logger.info(f"📊 Sample count: {len(y):,}")
        logger.info(f"📊 Win rate: {y.mean():.4f}")

        return X, y, feature_cols

    def train_models(self, X, y, feature_names):
        """Train multiple ML models."""
        logger.info("🤖 Training ML models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features for neural network
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers["standard"] = scaler

        # Model configurations
        models_to_train = {
            "random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation="relu",
                alpha=0.001,
                max_iter=500,
                random_state=42,
            ),
        }

        # Train each model
        for model_name, model in models_to_train.items():
            logger.info(f"🔧 Training {model_name}...")

            try:
                # Use scaled data for neural network
                if model_name == "neural_network":
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]

                # Calculate metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred),
                    "recall": recall_score(y_test, y_pred),
                    "f1": f1_score(y_test, y_pred),
                    "auc": roc_auc_score(y_test, y_pred_proba),
                }

                # Store model and metrics
                self.models[model_name] = model
                self.performance[model_name] = metrics

                logger.info(
                    f"✅ {model_name}: Accuracy={metrics['accuracy']:.4f}, AUC={metrics['auc']:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")

    def save_models(self):
        """Save trained models."""
        logger.info("💾 Saving models...")

        try:
            import os
            from pathlib import Path

            # Ensure models directory exists with proper permissions
            models_dir = Path("./models")
            models_dir.mkdir(exist_ok=True, mode=0o755)

            # Save models
            for name, model in self.models.items():
                model_path = models_dir / f"{name}_model.joblib"
                joblib.dump(model, str(model_path))
                logger.info(f"✅ Saved {name} model to {model_path}")

            # Save scalers and encoders
            if self.scalers:
                scalers_path = models_dir / "scalers.joblib"
                joblib.dump(self.scalers, str(scalers_path))
                logger.info(f"✅ Saved scalers to {scalers_path}")
            if self.encoders:
                encoders_path = models_dir / "encoders.joblib"
                joblib.dump(self.encoders, str(encoders_path))
                logger.info(f"✅ Saved encoders to {encoders_path}")

            # Save performance metrics
            joblib.dump(self.performance, "models/performance.joblib")

            logger.info("✅ Models saved successfully")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")

    def print_summary(self):
        """Print training summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 ML TRAINING SUMMARY - MASSIVE DATASET")
        logger.info("=" * 60)

        if self.performance:
            logger.info("\n📊 MODEL PERFORMANCE:")
            for model_name, metrics in self.performance.items():
                logger.info(f"\n🤖 {model_name.upper()}:")
                logger.info(f"   Accuracy:  {metrics['accuracy']:.4f}")
                logger.info(f"   Precision: {metrics['precision']:.4f}")
                logger.info(f"   Recall:    {metrics['recall']:.4f}")
                logger.info(f"   F1 Score:  {metrics['f1']:.4f}")
                logger.info(f"   AUC:       {metrics['auc']:.4f}")

            # Best model
            best_model = max(
                self.performance.keys(), key=lambda x: self.performance[x]["auc"]
            )
            best_auc = self.performance[best_model]["auc"]

            logger.info(f"\n🏆 BEST MODEL: {best_model.upper()}")
            logger.info(f"   Best AUC: {best_auc:.4f}")

        logger.info(f"\n💾 Models saved to: ./models/")
        logger.info("=" * 60)

    def run_training(self):
        """Execute complete training pipeline."""
        try:
            start_time = datetime.now()
            logger.info("🚀 Starting ML training on massive dataset...")

            # Connect and load data
            self.connect_database()
            df = self.load_training_data()

            # Create target and engineer features
            df = self.create_target_variable(df)
            df = self.engineer_features(df)

            # Prepare training data
            X, y, feature_names = self.prepare_training_data(df)

            # Train models
            self.train_models(X, y, feature_names)

            # Save models
            self.save_models()

            # Print summary
            self.print_summary()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"\n🎉 Training completed in {duration:.2f} seconds!")

        except Exception as e:
            logger.error(f"💥 Training failed: {e}")
            raise


def main():
    """Main execution function."""
    try:
        trainer = SimpleMLTrainer()
        trainer.run_training()

    except KeyboardInterrupt:
        logger.info("🛑 Training interrupted by user")
    except Exception as e:
        logger.error(f"💥 Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
