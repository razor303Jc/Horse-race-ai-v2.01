#!/usr/bin/env python3
"""
Real ML Training Pipeline Integration
Replaces simulation with actual model training using current data
"""

import logging
import time
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor

# Add project paths
project_root = Path("/app")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools"))

# Import training components
try:
    from v2_01_ensemble_trainer import V201EnsemblePredictor
except ImportError:
    # Fallback to basic training if v2.01 not available
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealMLTrainingPipeline:
    """Real ML Training Pipeline with database integration"""

    def __init__(self):
        self.logger = logger
        self.is_running = False
        self.models_path = Path("/app/models")
        self.trained_models_path = Path("/app/trained_models")
        self.db_config = {
            "host": "postgres",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        }

        # Ensure directories exist
        self.models_path.mkdir(exist_ok=True)
        self.trained_models_path.mkdir(exist_ok=True)

    def check_database_connection(self):
        """Check if database is accessible and has data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Check if we have race data
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM horses")
            horse_count = cursor.fetchone()[0]

            conn.close()

            self.logger.info(
                f"📊 Database status: {race_count} races, {record_count} records, {horse_count} horses"
            )

            return race_count > 0 and record_count > 0

        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False

    def load_training_data(self):
        """Load training data from PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)

            # Load race data with records for training
            query = """
            SELECT 
                r.race_id,
                r.course,
                r.distance,
                r.race_type,
                r.runners,
                rec.horse,
                rec.position,
                rec.age,
                rec.or_rating,
                rec.weight,
                rec.jockey,
                rec.trainer,
                rec.fav,
                rec.sp,
                h.horse_name,
                h.sex,
                h.color
            FROM races r
            JOIN records rec ON r.race_id = rec.race_id
            LEFT JOIN horses h ON rec.horse = h.horse_name
            WHERE rec.position IS NOT NULL
            ORDER BY r.race_id, rec.position
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            self.logger.info(f"📊 Loaded {len(df)} training records from database")
            return df

        except Exception as e:
            self.logger.error(f"❌ Failed to load training data: {e}")
            return None

    def prepare_features(self, df):
        """Prepare features for ML training"""
        try:
            # Create target variable (win = position 1)
            df["won"] = (df["position"] == 1).astype(int)

            # Prepare numeric features
            features = []

            # Add age if available
            if "age" in df.columns:
                df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0)
                features.append("age")

            # Add rating if available
            if "or_rating" in df.columns:
                df["or_rating"] = pd.to_numeric(
                    df["or_rating"], errors="coerce"
                ).fillna(0)
                features.append("or_rating")

            # Add runners count
            if "runners" in df.columns:
                df["runners"] = pd.to_numeric(df["runners"], errors="coerce").fillna(0)
                features.append("runners")

            # Add favorite status
            if "fav" in df.columns:
                df["is_favorite"] = (df["fav"] == 1).astype(int)
                features.append("is_favorite")

            # Add SP (starting price) if available
            if "sp" in df.columns:
                df["sp"] = pd.to_numeric(df["sp"], errors="coerce").fillna(0)
                features.append("sp")

            # Encode categorical features
            if "race_type" in df.columns:
                df["is_flat"] = (
                    df["race_type"].str.contains("Flat", na=False).astype(int)
                )
                features.append("is_flat")

            if "sex" in df.columns:
                df["is_male"] = df["sex"].isin(["Colt", "Gelding", "Horse"]).astype(int)
                features.append("is_male")

            self.logger.info(f"📊 Prepared {len(features)} features: {features}")

            return df[features + ["won"]].dropna()

        except Exception as e:
            self.logger.error(f"❌ Feature preparation failed: {e}")
            return None

    def train_models(self, training_data):
        """Train ML models with current data"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, roc_auc_score
            import joblib

            # Prepare training data
            feature_cols = [col for col in training_data.columns if col != "won"]
            X = training_data[feature_cols]
            y = training_data["won"]

            if len(X) < 10:
                self.logger.warning("⚠️ Insufficient training data for ML")
                return False

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            models_trained = 0

            # Train Random Forest
            self.logger.info("🌲 Training Random Forest model...")
            rf_model = RandomForestClassifier(
                n_estimators=100, max_depth=10, min_samples_split=5, random_state=42
            )
            rf_model.fit(X_train, y_train)

            # Evaluate Random Forest
            rf_pred = rf_model.predict(X_test)
            rf_prob = rf_model.predict_proba(X_test)[:, 1]
            rf_accuracy = accuracy_score(y_test, rf_pred)
            rf_auc = roc_auc_score(y_test, rf_prob)

            # Save Random Forest model
            rf_path = (
                self.models_path
                / f'random_forest_win_predictor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.joblib'
            )
            joblib.dump(rf_model, rf_path)
            self.logger.info(
                f"✅ Random Forest: Accuracy={rf_accuracy:.3f}, AUC={rf_auc:.3f}, Saved to {rf_path}"
            )
            models_trained += 1

            # Train Logistic Regression
            self.logger.info("📈 Training Logistic Regression model...")
            lr_model = LogisticRegression(random_state=42, max_iter=1000)
            lr_model.fit(X_train, y_train)

            # Evaluate Logistic Regression
            lr_pred = lr_model.predict(X_test)
            lr_prob = lr_model.predict_proba(X_test)[:, 1]
            lr_accuracy = accuracy_score(y_test, lr_pred)
            lr_auc = roc_auc_score(y_test, lr_prob)

            # Save Logistic Regression model
            lr_path = (
                self.models_path
                / f'logistic_regression_win_{datetime.now().strftime("%Y%m%d_%H%M%S")}.joblib'
            )
            joblib.dump(lr_model, lr_path)
            self.logger.info(
                f"✅ Logistic Regression: Accuracy={lr_accuracy:.3f}, AUC={lr_auc:.3f}, Saved to {lr_path}"
            )
            models_trained += 1

            # Create ensemble
            self.logger.info("🤝 Creating ensemble model...")
            ensemble_predictions = (rf_prob + lr_prob) / 2
            ensemble_pred = (ensemble_predictions > 0.5).astype(int)
            ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
            ensemble_auc = roc_auc_score(y_test, ensemble_predictions)

            # Save ensemble metadata
            ensemble_metadata = {
                "timestamp": datetime.now().isoformat(),
                "training_records": len(training_data),
                "features": feature_cols,
                "models": {
                    "random_forest": {
                        "accuracy": rf_accuracy,
                        "auc": rf_auc,
                        "path": str(rf_path),
                    },
                    "logistic_regression": {
                        "accuracy": lr_accuracy,
                        "auc": lr_auc,
                        "path": str(lr_path),
                    },
                    "ensemble": {"accuracy": ensemble_accuracy, "auc": ensemble_auc},
                },
            }

            metadata_path = self.models_path / "latest_training_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(ensemble_metadata, f, indent=2)

            self.logger.info(
                f"🎯 Ensemble: Accuracy={ensemble_accuracy:.3f}, AUC={ensemble_auc:.3f}"
            )
            self.logger.info(f"✅ Training completed: {models_trained} models trained")

            return models_trained > 0

        except Exception as e:
            self.logger.error(f"❌ Model training failed: {e}")
            self.logger.error(traceback.format_exc())
            return False

    def run_real_training_cycle(self):
        """Execute a real training cycle with current data"""
        self.logger.info("🧠 Starting REAL ML training cycle...")

        try:
            # Check database connection and data availability
            if not self.check_database_connection():
                self.logger.warning(
                    "⚠️ No database connection or data available, skipping training"
                )
                return False

            # Load training data from database
            raw_data = self.load_training_data()
            if raw_data is None or len(raw_data) == 0:
                self.logger.warning("⚠️ No training data available")
                return False

            # Prepare features
            training_data = self.prepare_features(raw_data)
            if training_data is None or len(training_data) == 0:
                self.logger.warning("⚠️ Feature preparation failed or no valid data")
                return False

            # Train models
            success = self.train_models(training_data)

            if success:
                self.logger.info("✅ Real ML training cycle completed successfully")
                return True
            else:
                self.logger.error("❌ ML training cycle failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Training cycle error: {e}")
            self.logger.error(traceback.format_exc())
            return False

    def run(self):
        """Run the real ML training pipeline"""
        self.logger.info("🚀 Real ML Training Pipeline starting...")
        self.is_running = True

        try:
            while self.is_running:
                # Run real training cycle
                training_success = self.run_real_training_cycle()

                if training_success:
                    self.logger.info(
                        "🎯 Training successful, waiting 30 minutes before next cycle..."
                    )
                    wait_time = 1800  # 30 minutes
                else:
                    self.logger.info(
                        "⚠️ Training failed, waiting 10 minutes before retry..."
                    )
                    wait_time = 600  # 10 minutes

                # Wait before next cycle
                time.sleep(wait_time)

        except KeyboardInterrupt:
            self.logger.info("🛑 Real ML Training Pipeline stopped")
        except Exception as e:
            self.logger.error(f"❌ Pipeline error: {e}")
        finally:
            self.is_running = False


if __name__ == "__main__":
    pipeline = RealMLTrainingPipeline()
    pipeline.run()
