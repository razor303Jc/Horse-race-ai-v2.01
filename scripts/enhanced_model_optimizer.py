#!/usr/bin/env python3
"""
Enhanced ML Model Training with Advanced Optimizations
Implements class balancing, hyperparameter tuning, advanced features, and ensemble methods
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
from imblearn.combine import SMOTETomek

# Database
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_model_training.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedModelTrainer:
    """Advanced ML training with comprehensive optimizations."""

    def __init__(self):
        self.engine = None
        self.models = {}
        self.best_models = {}
        self.scalers = {}
        self.encoders = {}
        self.performance = {}
        self.feature_importance = {}

        # Enhanced configuration
        self.config = {
            "sample_size": 50000,
            "test_size": 0.2,
            "random_state": 42,
            "cv_folds": 5,
            "balancing_method": "smote",  # smote, adasyn, undersample, class_weight
            "hyperparameter_method": "randomized",  # grid, randomized
            "n_iter_search": 20,
        }

        # Ensure models directory exists
        os.makedirs("models", exist_ok=True)
        os.makedirs("models/enhanced", exist_ok=True)

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
        """Load training data with enhanced features."""
        logger.info("📊 Loading enhanced training data...")

        sample_size = sample_size or self.config["sample_size"]

        # Enhanced query with actual available columns
        query = f"""
        SELECT 
            rc.race_id,
            rc.course,
            rc.race_type,
            rc.distance,
            rc.surface,
            rc.prize,
            rc.class,
            rc.date,
            rc.race_name,
            rc.years,
            rc.runners,
            rd.race_id as detail_race_id,
            rd.horse_id,
            rd.name as horse_name,
            rd.age,
            rd.weight,
            rd.draw,
            rd.odds_decimal,
            rd.jockey,
            rd.trainer,
            rd.horse_rate as official_rating,
            rd.fav,
            rd.country,
            rd.gears,
            rd.timeform_comments as form_comments
        FROM races_cards rc
        JOIN racecard_details rd ON rc.race_id = rd.race_id
        WHERE rd.odds_decimal IS NOT NULL 
        AND rd.odds_decimal > 0
        ORDER BY RANDOM()
        LIMIT {sample_size}
        """

        try:
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"📈 Loaded {len(df):,} enhanced training records")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load training data: {e}")
            raise

    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variable based on odds probability (synthetic winners)."""
        logger.info("🎯 Creating synthetic target variable based on odds...")

        # Create winners based on odds probability within each race
        # Lower odds = higher probability of winning

        def select_winners_per_race(race_group):
            """Select winner for each race based on odds probability."""
            # Convert odds to probabilities
            race_group = race_group.copy()
            race_group["win_probability"] = 1 / race_group["odds_decimal"]

            # Normalize probabilities within race
            total_prob = race_group["win_probability"].sum()
            race_group["normalized_prob"] = race_group["win_probability"] / total_prob

            # Add some randomness but bias toward favorites
            # 70% chance for mathematical favorite, 30% for upset
            if np.random.random() < 0.7:
                # Favorite wins
                winner_idx = race_group["normalized_prob"].idxmax()
            else:
                # Random selection with probability weighting
                winner_idx = np.random.choice(
                    race_group.index, p=race_group["normalized_prob"].values
                )

            race_group["is_winner"] = 0
            race_group.loc[winner_idx, "is_winner"] = 1

            return race_group

        # Apply winner selection to each race
        df_with_winners = (
            df.groupby("race_id").apply(select_winners_per_race).reset_index(drop=True)
        )

        wins = df_with_winners["is_winner"].sum()
        total = len(df_with_winners)
        win_rate = wins / total

        logger.info(
            f"📊 Synthetic win rate: {win_rate:.4f} ({wins:,} wins from {total:,} entries)"
        )
        return df_with_winners

    def engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering with sophisticated racing features."""
        logger.info("🔧 Engineering advanced features...")

        # Convert string columns to numeric safely
        numeric_columns = ["odds_decimal", "age", "weight", "draw", "prize", "distance"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 1. ODDS ANALYSIS (Enhanced)
        df["log_odds"] = np.log(df["odds_decimal"].clip(lower=1.01))
        df["odds_rank"] = df.groupby("race_id")["odds_decimal"].rank(method="min")
        df["odds_percentile"] = df.groupby("race_id")["odds_decimal"].rank(pct=True)
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)
        df["is_outsider"] = (df["odds_percentile"] > 0.8).astype(int)

        # Market strength indicators
        df["market_strength"] = 1 / df["odds_decimal"]
        df["market_share"] = df.groupby("race_id")["market_strength"].transform(
            lambda x: x / x.sum()
        )

        # 2. POSITIONAL ANALYSIS (Enhanced)
        df["draw_advantage"] = df.groupby(["course", "distance"])["draw"].transform(
            lambda x: x.rank(pct=True)
        )
        df["weight_burden"] = df.groupby("race_id")["weight"].transform(
            lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
        )

        # 3. RACE DYNAMICS
        race_size = df.groupby("race_id").size()
        df["field_size"] = df["race_id"].map(race_size)
        df["competitive_density"] = df.groupby("race_id")["odds_decimal"].transform(
            "std"
        )

        # 4. FORM & PERFORMANCE INDICATORS
        # Handle form string analysis safely
        df["form"] = df["form"].fillna("").astype(str)
        df["recent_form_score"] = df["form"].apply(self._calculate_form_score)
        df["form_consistency"] = df["form"].apply(self._calculate_form_consistency)

        # 5. CLASS & QUALITY INDICATORS
        df["race_class_numeric"] = (
            df["class"].fillna("5").astype(str).str.extract("(\d+)").astype(float)
        )
        df["prize_per_runner"] = df["prize"] / df["field_size"]
        df["class_drop"] = df.groupby("horse_id")["race_class_numeric"].diff().fillna(0)

        # 6. TRAINER & JOCKEY ANALYSIS
        df["trainer_success_rate"] = df.groupby("trainer")["is_winner"].transform(
            "mean"
        )
        df["jockey_success_rate"] = df.groupby("jockey")["is_winner"].transform("mean")

        # 7. DISTANCE & COURSE SUITABILITY
        df["distance_category"] = pd.cut(
            df["distance"],
            bins=[0, 1400, 1800, 2400, 3200, 10000],
            labels=["sprint", "mile", "middle", "staying", "extreme"],
        )
        df["course_experience"] = df.groupby(["horse_id", "course"]).cumcount()

        # 8. AGE & EXPERIENCE FACTORS
        df["age_advantage"] = df.groupby("distance_category")["age"].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )
        df["experience_factor"] = np.log1p(df.groupby("horse_id").cumcount())

        # 9. GOING & CONDITIONS
        going_mapping = {
            "Heavy": 1,
            "Soft": 2,
            "Good to Soft": 3,
            "Good": 4,
            "Good to Firm": 5,
            "Firm": 6,
            "Hard": 7,
        }
        df["going_numeric"] = df["going"].map(going_mapping).fillna(4)
        df["going_preference"] = df.groupby("horse_id")["going_numeric"].transform(
            "mean"
        )

        # 10. INTERACTION FEATURES
        df["odds_weight_interaction"] = df["log_odds"] * df["weight_burden"]
        df["age_distance_interaction"] = df["age"] * np.log1p(df["distance"])
        df["class_draw_interaction"] = df["race_class_numeric"] * df["draw_advantage"]

        # Select final features for training
        feature_columns = [
            "log_odds",
            "odds_rank",
            "odds_percentile",
            "is_favorite",
            "is_outsider",
            "market_strength",
            "market_share",
            "draw_advantage",
            "weight_burden",
            "field_size",
            "competitive_density",
            "recent_form_score",
            "form_consistency",
            "race_class_numeric",
            "prize_per_runner",
            "class_drop",
            "trainer_success_rate",
            "jockey_success_rate",
            "course_experience",
            "age_advantage",
            "experience_factor",
            "going_numeric",
            "going_preference",
            "odds_weight_interaction",
            "age_distance_interaction",
            "class_draw_interaction",
        ]

        # Keep only features that exist and have valid data
        available_features = [col for col in feature_columns if col in df.columns]
        df_features = df[available_features + ["is_winner"]].copy()

        # Handle missing values
        df_features = df_features.fillna(df_features.median(numeric_only=True))

        logger.info(
            f"✅ Advanced feature engineering completed: {len(available_features)} features"
        )
        return df_features

    def _calculate_form_score(self, form_string: str) -> float:
        """Calculate weighted form score from form string."""
        if not form_string or form_string == "":
            return 0.0

        score = 0.0
        weight = 1.0

        for char in form_string[:6]:  # Look at last 6 runs
            if char.isdigit():
                position = int(char)
                if position == 1:
                    score += 10 * weight
                elif position == 2:
                    score += 6 * weight
                elif position == 3:
                    score += 4 * weight
                elif position <= 5:
                    score += 2 * weight
                else:
                    score += 1 * weight
            elif char in ["F", "U", "P"]:  # Fell, Unseated, Pulled up
                score += 0

            weight *= 0.8  # Decay weight for older runs

        return score

    def _calculate_form_consistency(self, form_string: str) -> float:
        """Calculate form consistency score."""
        if not form_string or len(form_string) < 3:
            return 0.0

        positions = []
        for char in form_string[:5]:
            if char.isdigit():
                positions.append(int(char))

        if len(positions) < 2:
            return 0.0

        # Calculate coefficient of variation (lower = more consistent)
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)

        if mean_pos == 0:
            return 0.0

        cv = std_pos / mean_pos
        consistency = max(0, 1 - cv)  # Convert to consistency score

        return consistency

    def balance_dataset(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Apply class balancing techniques."""
        logger.info(f"🔄 Applying {self.config['balancing_method']} class balancing...")

        original_ratio = y.value_counts()
        logger.info(f"📊 Original class distribution: {dict(original_ratio)}")

        if self.config["balancing_method"] == "smote":
            sampler = SMOTE(random_state=self.config["random_state"], k_neighbors=3)
        elif self.config["balancing_method"] == "adasyn":
            sampler = ADASYN(random_state=self.config["random_state"])
        elif self.config["balancing_method"] == "undersample":
            sampler = RandomUnderSampler(random_state=self.config["random_state"])
        elif self.config["balancing_method"] == "smote_tomek":
            sampler = SMOTETomek(random_state=self.config["random_state"])
        else:
            logger.info("⚠️ No balancing applied - using class weights")
            return X, y

        try:
            X_balanced, y_balanced = sampler.fit_resample(X, y)
            new_ratio = pd.Series(y_balanced).value_counts()
            logger.info(f"📊 Balanced class distribution: {dict(new_ratio)}")

            return pd.DataFrame(X_balanced, columns=X.columns), pd.Series(y_balanced)
        except Exception as e:
            logger.warning(f"⚠️ Balancing failed: {e}, using original data")
            return X, y

    def get_hyperparameter_grids(self) -> Dict[str, Dict]:
        """Define hyperparameter grids for tuning."""
        return {
            "random_forest": {
                "n_estimators": [100, 200, 300, 500],
                "max_depth": [10, 20, 30, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None],
                "class_weight": ["balanced", "balanced_subsample", None],
            },
            "gradient_boosting": {
                "n_estimators": [100, 200, 300],
                "learning_rate": [0.05, 0.1, 0.15, 0.2],
                "max_depth": [3, 5, 7, 9],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "subsample": [0.8, 0.9, 1.0],
            },
            "neural_network": {
                "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50), (100, 100)],
                "activation": ["relu", "tanh"],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate": ["constant", "adaptive"],
                "max_iter": [500, 1000],
            },
        }

    def tune_hyperparameters(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict:
        """Perform hyperparameter tuning."""
        logger.info("🎛️ Starting hyperparameter tuning...")

        # Base models
        models = {
            "random_forest": RandomForestClassifier(
                random_state=self.config["random_state"]
            ),
            "gradient_boosting": GradientBoostingClassifier(
                random_state=self.config["random_state"]
            ),
            "neural_network": MLPClassifier(random_state=self.config["random_state"]),
        }

        param_grids = self.get_hyperparameter_grids()
        best_models = {}

        # Cross-validation setup
        cv = StratifiedKFold(
            n_splits=self.config["cv_folds"],
            shuffle=True,
            random_state=self.config["random_state"],
        )

        for model_name, model in models.items():
            logger.info(f"🔧 Tuning {model_name}...")

            try:
                if self.config["hyperparameter_method"] == "grid":
                    search = GridSearchCV(
                        model,
                        param_grids[model_name],
                        cv=cv,
                        scoring="roc_auc",
                        n_jobs=-1,
                        verbose=1,
                    )
                else:
                    search = RandomizedSearchCV(
                        model,
                        param_grids[model_name],
                        cv=cv,
                        scoring="roc_auc",
                        n_jobs=-1,
                        verbose=1,
                        n_iter=self.config["n_iter_search"],
                        random_state=self.config["random_state"],
                    )

                search.fit(X_train, y_train)
                best_models[model_name] = search.best_estimator_

                logger.info(f"✅ {model_name} - Best AUC: {search.best_score_:.4f}")
                logger.info(f"   Best params: {search.best_params_}")

            except Exception as e:
                logger.error(f"❌ Failed to tune {model_name}: {e}")
                best_models[model_name] = model  # Use default

        return best_models

    def train_enhanced_models(self, X: pd.DataFrame, y: pd.Series):
        """Train enhanced models with all optimizations."""
        logger.info("🤖 Training enhanced ML models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config["test_size"],
            random_state=self.config["random_state"],
            stratify=y,
        )

        # Scale features
        logger.info("📏 Scaling features...")
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test), columns=X_test.columns, index=X_test.index
        )
        self.scalers["feature_scaler"] = scaler

        # Apply class balancing
        X_train_balanced, y_train_balanced = self.balance_dataset(
            X_train_scaled, y_train
        )

        # Hyperparameter tuning
        self.best_models = self.tune_hyperparameters(X_train_balanced, y_train_balanced)

        # Train and evaluate models
        logger.info("🎯 Training and evaluating models...")

        for model_name, model in self.best_models.items():
            try:
                logger.info(f"🔧 Training {model_name}...")

                # Train model
                model.fit(X_train_balanced, y_train_balanced)

                # Predictions
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

                # Calculate metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, zero_division=0),
                    "recall": recall_score(y_test, y_pred, zero_division=0),
                    "f1": f1_score(y_test, y_pred, zero_division=0),
                    "auc": roc_auc_score(y_test, y_pred_proba),
                }

                # Cross-validation score
                cv_scores = cross_val_score(
                    model, X_train_balanced, y_train_balanced, cv=5, scoring="roc_auc"
                )
                metrics["cv_auc_mean"] = cv_scores.mean()
                metrics["cv_auc_std"] = cv_scores.std()

                # Feature importance (if available)
                if hasattr(model, "feature_importances_"):
                    importance_df = pd.DataFrame(
                        {"feature": X.columns, "importance": model.feature_importances_}
                    ).sort_values("importance", ascending=False)
                    self.feature_importance[model_name] = importance_df

                self.models[model_name] = model
                self.performance[model_name] = metrics

                logger.info(
                    f"✅ {model_name}: AUC={metrics['auc']:.4f}, CV_AUC={metrics['cv_auc_mean']:.4f}±{metrics['cv_auc_std']:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")

    def create_ensemble_model(self, X: pd.DataFrame, y: pd.Series):
        """Create ensemble model from best performing models."""
        logger.info("🎭 Creating ensemble model...")

        try:
            # Get top performing models
            sorted_models = sorted(
                self.performance.items(), key=lambda x: x[1]["auc"], reverse=True
            )

            top_models = []
            for model_name, metrics in sorted_models[:3]:  # Top 3 models
                if model_name in self.models:
                    top_models.append((model_name, self.models[model_name]))

            if len(top_models) >= 2:
                # Create voting ensemble
                ensemble = VotingClassifier(estimators=top_models, voting="soft")

                # Split for ensemble training
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )

                # Train ensemble
                ensemble.fit(X_train, y_train)

                # Evaluate ensemble
                y_pred = ensemble.predict(X_test)
                y_pred_proba = ensemble.predict_proba(X_test)[:, 1]

                ensemble_metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, zero_division=0),
                    "recall": recall_score(y_test, y_pred, zero_division=0),
                    "f1": f1_score(y_test, y_pred, zero_division=0),
                    "auc": roc_auc_score(y_test, y_pred_proba),
                }

                self.models["ensemble"] = ensemble
                self.performance["ensemble"] = ensemble_metrics

                logger.info(f"✅ Ensemble: AUC={ensemble_metrics['auc']:.4f}")

        except Exception as e:
            logger.error(f"❌ Failed to create ensemble: {e}")

    def save_enhanced_models(self):
        """Save all enhanced models and artifacts."""
        logger.info("💾 Saving enhanced models...")

        try:
            models_dir = Path("models/enhanced")

            # Save models
            for name, model in self.models.items():
                model_path = models_dir / f"{name}_enhanced.joblib"
                joblib.dump(model, str(model_path))
                logger.info(f"✅ Saved {name} to {model_path}")

            # Save scalers
            if self.scalers:
                scalers_path = models_dir / "scalers_enhanced.joblib"
                joblib.dump(self.scalers, str(scalers_path))

            # Save feature importance
            for name, importance_df in self.feature_importance.items():
                importance_path = models_dir / f"{name}_feature_importance.csv"
                importance_df.to_csv(importance_path, index=False)

            # Save performance metrics
            import json

            metrics_path = models_dir / "enhanced_performance.json"
            with open(metrics_path, "w") as f:
                json.dump(self.performance, f, indent=2)

            logger.info("✅ All enhanced models saved successfully")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")

    def print_enhancement_summary(self):
        """Print comprehensive enhancement summary."""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 ENHANCED MODEL TRAINING SUMMARY")
        logger.info("=" * 80)

        # Model performance comparison
        logger.info("\n📊 ENHANCED MODEL PERFORMANCE:")
        for model_name, metrics in sorted(
            self.performance.items(), key=lambda x: x[1]["auc"], reverse=True
        ):
            logger.info(f"\n🤖 {model_name.upper()}:")
            logger.info(f"   AUC:       {metrics['auc']:.4f}")
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

        logger.info("\n💾 Enhanced models saved to: ./models/enhanced/")
        logger.info("=" * 80)

    def run_enhancement_pipeline(self):
        """Execute complete enhancement pipeline."""
        try:
            start_time = datetime.now()
            logger.info("🚀 Starting enhanced ML training pipeline...")

            # Connect and load data
            self.connect_database()
            df = self.load_training_data()

            # Create target and engineer features
            df = self.create_target_variable(df)
            df = self.engineer_advanced_features(df)

            # Prepare training data
            feature_columns = [col for col in df.columns if col != "is_winner"]
            X = df[feature_columns].copy()
            y = df["is_winner"].copy()

            logger.info(
                f"🎯 Training data prepared: {X.shape[0]:,} samples, {X.shape[1]} features"
            )

            # Train enhanced models
            self.train_enhanced_models(X, y)

            # Create ensemble
            self.create_ensemble_model(X, y)

            # Save models
            self.save_enhanced_models()

            # Print summary
            self.print_enhancement_summary()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"\n🎉 Enhanced training completed in {duration:.2f} seconds!")

        except Exception as e:
            logger.error(f"💥 Enhanced training failed: {e}")
            raise


def main():
    """Main function."""
    trainer = EnhancedModelTrainer()
    trainer.run_enhancement_pipeline()


if __name__ == "__main__":
    main()
