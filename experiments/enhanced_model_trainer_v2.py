#!/usr/bin/env python3
"""
Enhanced ML Model Training - Simplified Version
Focuses on available columns with advanced optimizations
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any
import joblib
from pathlib import Path

# Core ML Libraries
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    StratifiedKFold,
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

# Class Balancing
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler

# Database
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_model_training_v2.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedModelTrainerV2:
    """Enhanced ML training optimized for available data schema."""

    def __init__(self):
        self.engine = None
        self.models = {}
        self.best_models = {}
        self.scalers = {}
        self.performance = {}
        self.feature_importance = {}

        # Configuration
        self.config = {
            "sample_size": 30000,
            "test_size": 0.2,
            "random_state": 42,
            "cv_folds": 5,
            "balancing_method": "smote",
            "hyperparameter_method": "randomized",
            "n_iter_search": 15,
        }

        # Ensure models directory exists
        os.makedirs("models", exist_ok=True)
        os.makedirs("models/enhanced_v2", exist_ok=True)

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

    def load_training_data(self, sample_size: int = None) -> pd.DataFrame:
        """Load training data with available columns."""
        logger.info("📊 Loading training data...")

        sample_size = sample_size or self.config["sample_size"]

        # Query with available columns only
        query = f"""
        SELECT 
            rc.race_id,
            rc.course,
            rc.race_type,
            rc.distance,
            rc.surface,
            rc.prize,
            rc.class,
            rc.runners,
            rd.horse_id,
            rd.name as horse_name,
            rd.age,
            rd.weight,
            rd.draw,
            rd.odds_decimal,
            rd.jockey,
            rd.trainer,
            rd.horse_rate as official_rating,
            rd.country
        FROM races_cards rc
        JOIN racecard_details rd ON rc.race_id = rd.race_id
        WHERE rd.odds_decimal IS NOT NULL 
        AND rd.odds_decimal > 0
        AND rd.odds_decimal < 1000
        ORDER BY RANDOM()
        LIMIT {sample_size}
        """

        try:
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"📈 Loaded {len(df):,} training records")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load training data: {e}")
            raise

    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create synthetic winners based on odds probability."""
        logger.info("🎯 Creating synthetic target variable...")

        def select_winner_per_race(race_group):
            """Select one winner per race based on odds."""
            race_group = race_group.copy()

            # Convert odds to probabilities
            race_group["win_prob"] = 1 / race_group["odds_decimal"]
            total_prob = race_group["win_prob"].sum()
            race_group["norm_prob"] = race_group["win_prob"] / total_prob

            # Select winner (70% favorite, 30% upset)
            if np.random.random() < 0.7:
                winner_idx = race_group["norm_prob"].idxmax()
            else:
                winner_idx = np.random.choice(
                    race_group.index, p=race_group["norm_prob"].values
                )

            race_group["is_winner"] = 0
            race_group.loc[winner_idx, "is_winner"] = 1

            return race_group[["race_id", "horse_id", "odds_decimal", "is_winner"]]

        # Create winners for each race
        winners_df = df.groupby("race_id", group_keys=False).apply(
            select_winner_per_race
        )

        # Merge back with original data
        df = df.merge(
            winners_df[["race_id", "horse_id", "is_winner"]],
            on=["race_id", "horse_id"],
            how="left",
        )

        wins = df["is_winner"].sum()
        total = len(df)
        win_rate = wins / total

        logger.info(
            f"📊 Synthetic win rate: {win_rate:.4f} ({wins:,} wins from {total:,} entries)"
        )
        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from available data."""
        logger.info("🔧 Engineering features...")

        # Convert to numeric
        numeric_columns = [
            "odds_decimal",
            "age",
            "weight",
            "draw",
            "prize",
            "distance",
            "official_rating",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 1. ODDS FEATURES
        df["log_odds"] = np.log(df["odds_decimal"].clip(lower=1.01))
        df["odds_rank"] = df.groupby("race_id")["odds_decimal"].rank(method="min")
        df["odds_percentile"] = df.groupby("race_id")["odds_decimal"].rank(pct=True)
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)
        df["is_outsider"] = (df["odds_percentile"] > 0.8).astype(int)

        # Market strength
        df["market_strength"] = 1 / df["odds_decimal"]
        df["market_share"] = df.groupby("race_id")["market_strength"].transform(
            lambda x: x / x.sum() if x.sum() > 0 else 0
        )

        # 2. POSITIONAL FEATURES
        df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
        df["weight_percentile"] = df.groupby("race_id")["weight"].rank(pct=True)

        # 3. RACE DYNAMICS
        df["field_size"] = df.groupby("race_id")["race_id"].transform("count")
        df["odds_spread"] = df.groupby("race_id")["odds_decimal"].transform("std")

        # 4. CLASS & PRIZE
        class_extract = df["class"].astype(str).str.extract(r"(\d+)", expand=False)
        df["race_class"] = pd.to_numeric(class_extract.fillna(5), errors="coerce")
        df["prize_per_runner"] = df["prize"] / df["field_size"]
        df["log_prize"] = np.log1p(df["prize"])

        # 5. RATING FEATURES
        if "official_rating" in df.columns:
            df["official_rating"] = df["official_rating"].fillna(
                df["official_rating"].median()
            )
            df["rating_rank"] = df.groupby("race_id")["official_rating"].rank(
                ascending=False
            )
            df["rating_percentile"] = df.groupby("race_id")["official_rating"].rank(
                pct=True
            )
        else:
            df["rating_rank"] = 0
            df["rating_percentile"] = 0.5

        # 6. EXPERIENCE INDICATORS
        df["trainer_experience"] = df.groupby("trainer")["race_id"].transform("count")
        df["jockey_experience"] = df.groupby("jockey")["race_id"].transform("count")
        df["horse_experience"] = df.groupby("horse_id")["race_id"].transform("count")

        # 7. DISTANCE CATEGORY
        df["distance_category"] = pd.cut(
            df["distance"],
            bins=[0, 1400, 1800, 2400, 3200, 10000],
            labels=[0, 1, 2, 3, 4],
        ).astype(float)

        # 8. AGE CATEGORY
        df["age_category"] = pd.cut(
            df["age"], bins=[0, 3, 5, 7, 15], labels=[0, 1, 2, 3]
        ).astype(float)

        # 9. INTERACTION FEATURES
        df["odds_weight_ratio"] = df["log_odds"] / (df["weight_percentile"] + 0.001)
        df["rating_odds_ratio"] = df["rating_percentile"] / (
            df["odds_percentile"] + 0.001
        )
        df["experience_odds"] = np.log1p(df["horse_experience"]) * df["log_odds"]

        # Select features for training
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
            "odds_spread",
            "race_class",
            "prize_per_runner",
            "log_prize",
            "rating_rank",
            "rating_percentile",
            "trainer_experience",
            "jockey_experience",
            "horse_experience",
            "distance_category",
            "age_category",
            "odds_weight_ratio",
            "rating_odds_ratio",
            "experience_odds",
        ]

        # Keep available features
        available_features = [col for col in feature_columns if col in df.columns]
        df_features = df[available_features + ["is_winner"]].copy()

        # Handle missing values
        df_features = df_features.fillna(df_features.median(numeric_only=True))

        logger.info(
            f"✅ Feature engineering completed: {len(available_features)} features"
        )
        return df_features

    def balance_dataset(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Apply SMOTE balancing."""
        logger.info(f"🔄 Applying {self.config['balancing_method']} class balancing...")

        original_ratio = y.value_counts()
        logger.info(f"📊 Original: {dict(original_ratio)}")

        try:
            if self.config["balancing_method"] == "smote":
                sampler = SMOTE(random_state=self.config["random_state"], k_neighbors=3)
            elif self.config["balancing_method"] == "adasyn":
                sampler = ADASYN(random_state=self.config["random_state"])
            else:
                return X, y

            X_balanced, y_balanced = sampler.fit_resample(X, y)
            new_ratio = pd.Series(y_balanced).value_counts()
            logger.info(f"📊 Balanced: {dict(new_ratio)}")

            return pd.DataFrame(X_balanced, columns=X.columns), pd.Series(y_balanced)
        except Exception as e:
            logger.warning(f"⚠️ Balancing failed: {e}")
            return X, y

    def get_hyperparameter_grids(self) -> Dict[str, Dict]:
        """Hyperparameter grids."""
        return {
            "random_forest": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "class_weight": ["balanced", None],
            },
            "gradient_boosting": {
                "n_estimators": [100, 200],
                "learning_rate": [0.1, 0.15, 0.2],
                "max_depth": [3, 5, 7],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 2],
            },
            "neural_network": {
                "hidden_layer_sizes": [(50,), (100,), (50, 50)],
                "activation": ["relu", "tanh"],
                "alpha": [0.001, 0.01],
                "learning_rate": ["constant", "adaptive"],
            },
        }

    def train_enhanced_models(self, X: pd.DataFrame, y: pd.Series):
        """Train enhanced models."""
        logger.info("🤖 Training enhanced models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config["test_size"],
            random_state=self.config["random_state"],
            stratify=y,
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns
        )
        X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
        self.scalers["feature_scaler"] = scaler

        # Balance dataset
        X_train_balanced, y_train_balanced = self.balance_dataset(
            X_train_scaled, y_train
        )

        # Base models
        models = {
            "random_forest": RandomForestClassifier(
                random_state=self.config["random_state"]
            ),
            "gradient_boosting": GradientBoostingClassifier(
                random_state=self.config["random_state"]
            ),
            "neural_network": MLPClassifier(
                random_state=self.config["random_state"], max_iter=1000
            ),
        }

        param_grids = self.get_hyperparameter_grids()
        cv = StratifiedKFold(
            n_splits=self.config["cv_folds"],
            shuffle=True,
            random_state=self.config["random_state"],
        )

        # Train and tune models
        for model_name, model in models.items():
            try:
                logger.info(f"🔧 Training {model_name}...")

                # Hyperparameter tuning
                search = RandomizedSearchCV(
                    model,
                    param_grids[model_name],
                    cv=cv,
                    scoring="roc_auc",
                    n_jobs=-1,
                    verbose=0,
                    n_iter=self.config["n_iter_search"],
                    random_state=self.config["random_state"],
                )

                search.fit(X_train_balanced, y_train_balanced)
                best_model = search.best_estimator_

                # Predictions
                y_pred = best_model.predict(X_test_scaled)
                y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

                # Metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, zero_division=0),
                    "recall": recall_score(y_test, y_pred, zero_division=0),
                    "f1": f1_score(y_test, y_pred, zero_division=0),
                    "auc": roc_auc_score(y_test, y_pred_proba),
                    "best_params": search.best_params_,
                }

                # Cross-validation
                cv_scores = cross_val_score(
                    best_model,
                    X_train_balanced,
                    y_train_balanced,
                    cv=3,
                    scoring="roc_auc",
                )
                metrics["cv_auc_mean"] = cv_scores.mean()
                metrics["cv_auc_std"] = cv_scores.std()

                # Feature importance
                if hasattr(best_model, "feature_importances_"):
                    importance_df = pd.DataFrame(
                        {
                            "feature": X.columns,
                            "importance": best_model.feature_importances_,
                        }
                    ).sort_values("importance", ascending=False)
                    self.feature_importance[model_name] = importance_df

                self.models[model_name] = best_model
                self.performance[model_name] = metrics

                logger.info(
                    f"✅ {model_name}: AUC={metrics['auc']:.4f}, CV={metrics['cv_auc_mean']:.4f}±{metrics['cv_auc_std']:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")

    def create_ensemble(self, X: pd.DataFrame, y: pd.Series):
        """Create ensemble model."""
        logger.info("🎭 Creating ensemble...")

        try:
            if len(self.models) >= 2:
                # Get best models
                sorted_models = sorted(
                    self.performance.items(), key=lambda x: x[1]["auc"], reverse=True
                )

                top_models = [
                    (name, self.models[name]) for name, _ in sorted_models[:3]
                ]

                ensemble = VotingClassifier(estimators=top_models, voting="soft")

                # Quick evaluation
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )

                ensemble.fit(X_train, y_train)
                y_pred_proba = ensemble.predict_proba(X_test)[:, 1]

                ensemble_auc = roc_auc_score(y_test, y_pred_proba)

                self.models["ensemble"] = ensemble
                self.performance["ensemble"] = {"auc": ensemble_auc}

                logger.info(f"✅ Ensemble AUC: {ensemble_auc:.4f}")

        except Exception as e:
            logger.error(f"❌ Ensemble creation failed: {e}")

    def save_models(self):
        """Save all models."""
        logger.info("💾 Saving enhanced models...")

        try:
            models_dir = Path("models/enhanced_v2")

            # Save models
            for name, model in self.models.items():
                model_path = models_dir / f"{name}_enhanced_v2.joblib"
                joblib.dump(model, str(model_path))

            # Save scalers
            if self.scalers:
                joblib.dump(self.scalers, str(models_dir / "scalers_v2.joblib"))

            # Save feature importance
            for name, importance_df in self.feature_importance.items():
                importance_df.to_csv(
                    models_dir / f"{name}_importance_v2.csv", index=False
                )

            # Save performance
            import json

            with open(models_dir / "performance_v2.json", "w") as f:
                # Convert numpy types to native Python types for JSON serialization
                performance_json = {}
                for model_name, metrics in self.performance.items():
                    performance_json[model_name] = {}
                    for metric_name, value in metrics.items():
                        if isinstance(value, (np.integer, np.floating)):
                            performance_json[model_name][metric_name] = float(value)
                        elif isinstance(value, dict):
                            performance_json[model_name][metric_name] = value
                        else:
                            performance_json[model_name][metric_name] = value
                json.dump(performance_json, f, indent=2)

            logger.info("✅ All models saved successfully")

        except Exception as e:
            logger.error(f"❌ Save failed: {e}")

    def print_summary(self):
        """Print comprehensive summary."""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 ENHANCED MODEL TRAINING SUMMARY V2")
        logger.info("=" * 80)

        # Performance comparison
        logger.info("\n📊 ENHANCED MODEL PERFORMANCE:")
        for model_name, metrics in sorted(
            self.performance.items(), key=lambda x: x[1]["auc"], reverse=True
        ):
            logger.info(f"\n🤖 {model_name.upper()}:")
            logger.info(f"   AUC:       {metrics['auc']:.4f}")
            if "accuracy" in metrics:
                logger.info(f"   Accuracy:  {metrics['accuracy']:.4f}")
                logger.info(f"   Precision: {metrics['precision']:.4f}")
                logger.info(f"   Recall:    {metrics['recall']:.4f}")
                logger.info(f"   F1:        {metrics['f1']:.4f}")

            if "cv_auc_mean" in metrics:
                logger.info(
                    f"   CV AUC:    {metrics['cv_auc_mean']:.4f}±{metrics['cv_auc_std']:.4f}"
                )

        # Best model
        best_model = max(
            self.performance.keys(), key=lambda x: self.performance[x]["auc"]
        )
        best_auc = self.performance[best_model]["auc"]

        logger.info(f"\n🏆 BEST ENHANCED MODEL: {best_model.upper()}")
        logger.info(f"   Best AUC: {best_auc:.4f}")

        # Feature importance for best model
        if best_model in self.feature_importance:
            logger.info(f"\n📈 TOP 10 FEATURES ({best_model}):")
            top_features = self.feature_importance[best_model].head(10)
            for _, row in top_features.iterrows():
                logger.info(f"   {row['feature']}: {row['importance']:.4f}")

        logger.info("\n💾 Enhanced models saved to: ./models/enhanced_v2/")
        logger.info("=" * 80)

    def run_enhancement_pipeline(self):
        """Execute complete enhancement pipeline."""
        try:
            start_time = datetime.now()
            logger.info("🚀 Starting enhanced ML training pipeline V2...")

            # Connect and load data
            self.connect_database()
            df = self.load_training_data()

            # Create target and engineer features
            df = self.create_target_variable(df)
            df = self.engineer_features(df)

            # Prepare training data
            feature_columns = [col for col in df.columns if col != "is_winner"]
            X = df[feature_columns].copy()
            y = df["is_winner"].copy()

            logger.info(
                f"🎯 Training data: {X.shape[0]:,} samples, {X.shape[1]} features"
            )

            # Train models
            self.train_enhanced_models(X, y)

            # Create ensemble
            self.create_ensemble(X, y)

            # Save models
            self.save_models()

            # Print summary
            self.print_summary()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"\n🎉 Enhanced training V2 completed in {duration:.2f} seconds!"
            )

        except Exception as e:
            logger.error(f"💥 Enhanced training failed: {e}")
            raise


def main():
    """Main function."""
    trainer = EnhancedModelTrainerV2()
    trainer.run_enhancement_pipeline()


if __name__ == "__main__":
    main()
