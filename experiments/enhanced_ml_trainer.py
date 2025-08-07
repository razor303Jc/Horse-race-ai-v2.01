#!/usr/bin/env python3
"""
Enhanced ML Training System - Horse Racing AI v2.0
Advanced machine learning training with massive 100K+ dataset
Optimized for high-performance training with comprehensive feature engineering
"""
import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings("ignore")

# ML and preprocessing imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    ExtraTreesClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
import joblib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_ml_training.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")


class EnhancedMLTrainer:
    """
    Advanced ML training system for massive horse racing dataset.

    Features:
    - Multi-model ensemble training
    - Advanced feature engineering
    - Cross-validation and hyperparameter tuning
    - Performance analytics and comparison
    - Model persistence and deployment readiness
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.engine = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.performance_metrics = {}

        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)

        # Model configurations for ensemble
        self.model_configs = {
            "random_forest": {
                "model": RandomForestClassifier,
                "params": {
                    "n_estimators": [200, 300, 500],
                    "max_depth": [10, 15, 20, None],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "max_features": ["sqrt", "log2", None],
                },
            },
            "gradient_boosting": {
                "model": GradientBoostingClassifier,
                "params": {
                    "n_estimators": [200, 300, 500],
                    "learning_rate": [0.05, 0.1, 0.15],
                    "max_depth": [3, 5, 7],
                    "subsample": [0.8, 0.9, 1.0],
                    "max_features": ["sqrt", "log2", None],
                },
            },
            "extra_trees": {
                "model": ExtraTreesClassifier,
                "params": {
                    "n_estimators": [200, 300, 500],
                    "max_depth": [10, 15, 20, None],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                },
            },
            "neural_network": {
                "model": MLPClassifier,
                "params": {
                    "hidden_layer_sizes": [(100, 50), (200, 100), (300, 150)],
                    "activation": ["relu", "tanh"],
                    "alpha": [0.0001, 0.001, 0.01],
                    "learning_rate": ["constant", "adaptive"],
                    "max_iter": [1000],
                },
            },
            "logistic_regression": {
                "model": LogisticRegression,
                "params": {
                    "C": [0.1, 1.0, 10.0, 100.0],
                    "penalty": ["l1", "l2", "elasticnet"],
                    "solver": ["liblinear", "saga"],
                    "max_iter": [2000],
                },
            },
        }

    def connect_database(self) -> None:
        """Connect to database using environment configuration."""
        try:
            load_dotenv()
            database_url = os.getenv("DATABASE_URL")
            self.engine = create_engine(database_url)
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def load_massive_dataset(self) -> pd.DataFrame:
        """Load and prepare the massive dataset from training tables."""
        logger.info("📊 Loading massive dataset from training tables...")

        # Enhanced query with comprehensive features
        query = """
        SELECT 
            -- Race information
            rc.race_id,
            rc.race_number,
            rc.course,
            rc.race_type,
            rc.date,
            rc.distance,
            rc.surface,
            rc.prize,
            rc.runners_racecard,
            rc.runners,
            
            -- Horse details
            rd.horse_id,
            rd.name as horse_name,
            rd.age,
            rd.weight,
            rd.draw,
            rd.country,
            
            -- Performance indicators
            rd.odds_decimal,
            rd.horse_rate,
            
            -- Connections
            rd.jockey,
            rd.trainer,
            
            -- Target variable (derived from finishing position)
            CASE 
                WHEN rd.timeform_comments LIKE 'Finished: 1%' THEN 1
                WHEN rd.timeform_comments LIKE 'Finished: 2%' THEN 2
                WHEN rd.timeform_comments LIKE 'Finished: 3%' THEN 3
                ELSE 0
            END as finish_position,
            
            -- Binary win target
            CASE 
                WHEN rd.timeform_comments LIKE 'Finished: 1%' THEN 1
                ELSE 0
            END as won_race
            
        FROM races_cards rc
        JOIN racecard_details rd ON rc.race_id = rd.race_id
        WHERE rd.odds_decimal IS NOT NULL
        AND rd.odds_decimal > 0
        AND rd.name IS NOT NULL
        ORDER BY rc.date DESC, rc.race_id, rd.draw
        """

        try:
            df = pd.read_sql_query(query, self.engine)

            logger.info(f"📈 Dataset loaded: {len(df):,} records")
            logger.info(f"🏁 Unique races: {df['race_id'].nunique():,}")
            logger.info(f"🐎 Unique horses: {df['horse_id'].nunique():,}")

            return df

        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise

    def advanced_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering for enhanced model performance."""
        logger.info("🔧 Performing advanced feature engineering...")

        # Copy dataframe to avoid modifying original
        df_features = df.copy()

        # 1. Temporal features
        df_features["date"] = pd.to_datetime(df_features["date"])
        df_features["year"] = df_features["date"].dt.year
        df_features["month"] = df_features["date"].dt.month
        df_features["day_of_week"] = df_features["date"].dt.dayofweek
        df_features["quarter"] = df_features["date"].dt.quarter

        # 2. Distance analysis
        df_features["distance_category"] = pd.cut(
            df_features["distance"].fillna(1600),
            bins=[0, 1400, 1800, 2400, 3200, 10000],
            labels=["Sprint", "Mile", "Middle", "Staying", "Extreme"],
        )

        # 3. Odds-based features
        df_features["odds_decimal"] = df_features["odds_decimal"].fillna(50.0)
        df_features["odds_log"] = np.log(df_features["odds_decimal"])
        df_features["implied_probability"] = 1 / df_features["odds_decimal"]
        df_features["odds_rank"] = df_features.groupby("race_id")["odds_decimal"].rank()
        df_features["is_favorite"] = (df_features["odds_rank"] == 1).astype(int)

        # 4. Field size features
        df_features["field_size"] = df_features.groupby("race_id")["race_id"].transform(
            "count"
        )
        df_features["field_size_category"] = pd.cut(
            df_features["field_size"],
            bins=[0, 8, 12, 16, 30],
            labels=["Small", "Medium", "Large", "Very Large"],
        )

        # 5. Draw bias features
        df_features["draw_percentage"] = df_features["draw"] / df_features["field_size"]
        df_features["low_draw"] = (df_features["draw"] <= 3).astype(int)
        df_features["high_draw"] = (
            df_features["draw"] >= df_features["field_size"] - 2
        ).astype(int)

        # 6. Age features
        df_features["age"] = df_features["age"].fillna(4)
        df_features["is_young"] = (df_features["age"] <= 3).astype(int)
        df_features["is_veteran"] = (df_features["age"] >= 8).astype(int)

        # 7. Weight features
        df_features["weight"] = df_features["weight"].fillna(
            df_features["weight"].median()
        )
        df_features["weight_rank"] = df_features.groupby("race_id")["weight"].rank(
            ascending=False
        )

        # 8. Prize money features
        df_features["prize"] = df_features["prize"].fillna(0)
        df_features["prize_log"] = np.log(df_features["prize"] + 1)
        df_features["high_value_race"] = (
            df_features["prize"] > df_features["prize"].quantile(0.75)
        ).astype(int)

        # 9. Course and race type encoding
        # Label encode categorical variables
        categorical_cols = [
            "course",
            "race_type",
            "surface",
            "country",
            "distance_category",
            "field_size_category",
        ]

        for col in categorical_cols:
            if col in df_features.columns:
                df_features[col] = df_features[col].fillna("Unknown")
                le = LabelEncoder()
                df_features[f"{col}_encoded"] = le.fit_transform(df_features[col])
                self.encoders[col] = le

        # 10. Jockey and trainer performance features
        # Calculate historical performance (simplified for demo)
        jockey_stats = (
            df_features.groupby("jockey")
            .agg({"won_race": ["mean", "count"], "finish_position": "mean"})
            .round(4)
        )
        jockey_stats.columns = ["jockey_win_rate", "jockey_rides", "jockey_avg_finish"]
        df_features = df_features.merge(
            jockey_stats, left_on="jockey", right_index=True, how="left"
        )

        trainer_stats = (
            df_features.groupby("trainer")
            .agg({"won_race": ["mean", "count"], "finish_position": "mean"})
            .round(4)
        )
        trainer_stats.columns = [
            "trainer_win_rate",
            "trainer_runners",
            "trainer_avg_finish",
        ]
        df_features = df_features.merge(
            trainer_stats, left_on="trainer", right_index=True, how="left"
        )

        # 11. Horse rating features
        df_features["horse_rate"] = pd.to_numeric(
            df_features["horse_rate"], errors="coerce"
        )
        df_features["horse_rate"] = df_features["horse_rate"].fillna(
            df_features["horse_rate"].median()
        )
        df_features["horse_rate_rank"] = df_features.groupby("race_id")[
            "horse_rate"
        ].rank(ascending=False)

        # Fill any remaining NaN values
        numeric_cols = df_features.select_dtypes(include=[np.number]).columns
        df_features[numeric_cols] = df_features[numeric_cols].fillna(0)

        logger.info(
            f"✅ Feature engineering completed: {len(df_features.columns)} features"
        )

        return df_features

    def prepare_training_data(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for training."""
        logger.info("🎯 Preparing training data...")

        # Define feature columns (exclude target and identifier columns)
        exclude_cols = [
            "race_id",
            "horse_id",
            "horse_name",
            "jockey",
            "trainer",
            "date",
            "won_race",
            "finish_position",
            "timeform_comments",
            "course",
            "race_type",
            "surface",
            "country",
            "distance_category",
            "field_size_category",
        ]

        feature_cols = [col for col in df.columns if col not in exclude_cols]

        # Prepare features and target
        X = df[feature_cols].values
        y = df["won_race"].values

        logger.info(f"📊 Training data prepared:")
        logger.info(f"   Features: {X.shape[1]}")
        logger.info(f"   Samples: {X.shape[0]:,}")
        logger.info(f"   Win rate: {y.mean():.4f}")

        return X, y, feature_cols

    def train_ensemble_models(
        self, X: np.ndarray, y: np.ndarray, feature_names: List[str]
    ) -> None:
        """Train ensemble of optimized models."""
        logger.info("🤖 Training ensemble models with hyperparameter optimization...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers["robust"] = scaler

        # Train each model with hyperparameter tuning
        trained_models = []

        for model_name, config in self.model_configs.items():
            logger.info(f"🔧 Training {model_name}...")

            try:
                # Initialize model
                model_class = config["model"]

                # Use scaled data for neural networks and logistic regression
                if model_name in ["neural_network", "logistic_regression"]:
                    X_train_model = X_train_scaled
                    X_test_model = X_test_scaled
                else:
                    X_train_model = X_train
                    X_test_model = X_test

                # Hyperparameter tuning with GridSearchCV
                grid_search = GridSearchCV(
                    model_class(random_state=42),
                    config["params"],
                    cv=3,  # Reduced for speed with large dataset
                    scoring="roc_auc",
                    n_jobs=-1,
                    verbose=0,
                )

                grid_search.fit(X_train_model, y_train)
                best_model = grid_search.best_estimator_

                # Evaluate model
                y_pred = best_model.predict(X_test_model)
                y_pred_proba = best_model.predict_proba(X_test_model)[:, 1]

                # Calculate metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred),
                    "recall": recall_score(y_test, y_pred),
                    "f1": f1_score(y_test, y_pred),
                    "auc": roc_auc_score(y_test, y_pred_proba),
                    "best_params": grid_search.best_params_,
                }

                # Store model and metrics
                self.models[model_name] = best_model
                self.performance_metrics[model_name] = metrics
                trained_models.append((model_name, best_model))

                # Feature importance (if available)
                if hasattr(best_model, "feature_importances_"):
                    importance_df = pd.DataFrame(
                        {
                            "feature": feature_names,
                            "importance": best_model.feature_importances_,
                        }
                    ).sort_values("importance", ascending=False)
                    self.feature_importance[model_name] = importance_df

                logger.info(
                    f"✅ {model_name} - AUC: {metrics['auc']:.4f}, Accuracy: {metrics['accuracy']:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")
                continue

        # Create ensemble model
        if len(trained_models) >= 3:
            logger.info("🎭 Creating ensemble model...")

            ensemble_models = []
            for name, model in trained_models:
                if name in ["neural_network", "logistic_regression"]:
                    # Create pipeline with scaler for these models
                    from sklearn.pipeline import Pipeline

                    pipeline = Pipeline([("scaler", RobustScaler()), ("model", model)])
                    ensemble_models.append((name, pipeline))
                else:
                    ensemble_models.append((name, model))

            # Voting classifier
            ensemble = VotingClassifier(estimators=ensemble_models, voting="soft")

            ensemble.fit(X_train, y_train)

            # Evaluate ensemble
            y_pred_ensemble = ensemble.predict(X_test)
            y_pred_proba_ensemble = ensemble.predict_proba(X_test)[:, 1]

            ensemble_metrics = {
                "accuracy": accuracy_score(y_test, y_pred_ensemble),
                "precision": precision_score(y_test, y_pred_ensemble),
                "recall": recall_score(y_test, y_pred_ensemble),
                "f1": f1_score(y_test, y_pred_ensemble),
                "auc": roc_auc_score(y_test, y_pred_proba_ensemble),
            }

            self.models["ensemble"] = ensemble
            self.performance_metrics["ensemble"] = ensemble_metrics

            logger.info(
                f"🎭 Ensemble - AUC: {ensemble_metrics['auc']:.4f}, Accuracy: {ensemble_metrics['accuracy']:.4f}"
            )

    def save_models(self) -> None:
        """Save trained models and preprocessing objects."""
        logger.info("💾 Saving trained models...")

        try:
            # Save models
            for model_name, model in self.models.items():
                model_path = os.path.join(self.model_dir, f"{model_name}_model.joblib")
                joblib.dump(model, model_path)
                logger.info(f"✅ Saved {model_name} model")

            # Save scalers and encoders
            if self.scalers:
                scaler_path = os.path.join(self.model_dir, "scalers.joblib")
                joblib.dump(self.scalers, scaler_path)

            if self.encoders:
                encoder_path = os.path.join(self.model_dir, "encoders.joblib")
                joblib.dump(self.encoders, encoder_path)

            # Save performance metrics
            metrics_path = os.path.join(self.model_dir, "performance_metrics.joblib")
            joblib.dump(self.performance_metrics, metrics_path)

            # Save feature importance
            if self.feature_importance:
                importance_path = os.path.join(
                    self.model_dir, "feature_importance.joblib"
                )
                joblib.dump(self.feature_importance, importance_path)

            logger.info("✅ All models and preprocessing objects saved")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")
            raise

    def print_training_summary(self) -> None:
        """Print comprehensive training summary."""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 ENHANCED ML TRAINING SUMMARY")
        logger.info("=" * 80)

        if self.performance_metrics:
            # Create performance comparison
            metrics_df = pd.DataFrame(self.performance_metrics).T
            metrics_df = metrics_df[["accuracy", "precision", "recall", "f1", "auc"]]

            logger.info("\n📊 MODEL PERFORMANCE COMPARISON:")
            logger.info(metrics_df.round(4).to_string())

            # Best performing model
            best_model = metrics_df["auc"].idxmax()
            best_auc = metrics_df.loc[best_model, "auc"]

            logger.info(f"\n🏆 BEST MODEL: {best_model.upper()}")
            logger.info(f"   AUC Score: {best_auc:.4f}")
            logger.info(f"   Accuracy: {metrics_df.loc[best_model, 'accuracy']:.4f}")

            # Feature importance for best tree-based model
            tree_models = ["random_forest", "gradient_boosting", "extra_trees"]
            best_tree_model = None
            best_tree_auc = 0

            for model in tree_models:
                if model in metrics_df.index:
                    if metrics_df.loc[model, "auc"] > best_tree_auc:
                        best_tree_auc = metrics_df.loc[model, "auc"]
                        best_tree_model = model

            if best_tree_model and best_tree_model in self.feature_importance:
                logger.info(f"\n🔍 TOP 10 FEATURES ({best_tree_model.upper()}):")
                top_features = self.feature_importance[best_tree_model].head(10)
                for idx, row in top_features.iterrows():
                    logger.info(f"   {row['feature']}: {row['importance']:.4f}")

        logger.info(f"\n💾 Models saved to: {self.model_dir}/")
        logger.info("=" * 80 + "\n")

    def run_enhanced_training(self) -> None:
        """Execute complete enhanced ML training pipeline."""
        try:
            start_time = datetime.now()
            logger.info("🚀 Starting enhanced ML training on massive dataset...")

            # Connect to database
            self.connect_database()

            # Load massive dataset
            df = self.load_massive_dataset()

            # Advanced feature engineering
            df_features = self.advanced_feature_engineering(df)

            # Prepare training data
            X, y, feature_names = self.prepare_training_data(df_features)

            # Train ensemble models
            self.train_ensemble_models(X, y, feature_names)

            # Save models
            self.save_models()

            # Print summary
            self.print_training_summary()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"🎉 Enhanced ML training completed successfully!")
            logger.info(f"⏱️ Total training time: {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"💥 Enhanced training failed: {e}")
            raise


def main():
    """Main execution function."""
    try:
        trainer = EnhancedMLTrainer()
        trainer.run_enhanced_training()

    except KeyboardInterrupt:
        logger.info("🛑 Training interrupted by user")
    except Exception as e:
        logger.error(f"💥 Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
