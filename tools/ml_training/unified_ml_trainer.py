#!/usr/bin/env python3
"""
🎯 Unified ML Training System - Horse Racing AI v2.02
Consolidated ML training system combining best practices from all existing trainers

This unified system replaces 8+ separate trainer implementations with a single,
configurable, high-performance training pipeline.

Features:
- Configuration-driven training modes (fast, standard, advanced, experimental)
- Consolidated feature engineering with versioning
- Multiple model support with ensemble capabilities
- Parallel processing and hyperparameter optimization
- Unified evaluation and model persistence
- Performance monitoring and benchmarking

Author: AI Assistant
Date: August 15, 2025
"""

import logging
import os
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
import psycopg2
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
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
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Class balancing imports
try:
    from imblearn.over_sampling import ADASYN, SMOTE
    from imblearn.under_sampling import RandomUnderSampler

    IMBALANCED_LEARN_AVAILABLE = True
except ImportError:
    IMBALANCED_LEARN_AVAILABLE = False
    logging.warning(
        "imbalanced-learn not available. Class balancing features disabled."
    )

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Consolidated feature engineering from all trainer implementations."""

    def __init__(self, feature_set: str = "standard"):
        """
        Initialize feature engineering with specified feature set.

        Args:
            feature_set: One of 'basic', 'standard', 'advanced', 'experimental'
        """
        self.feature_set = feature_set
        self.feature_versions = {
            "basic": self._get_basic_features,
            "standard": self._get_standard_features,
            "advanced": self._get_advanced_features,
            "experimental": self._get_experimental_features,
        }

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features based on the selected feature set.

        Args:
            df: Raw dataframe with race data

        Returns:
            DataFrame with engineered features
        """
        logger.info(f"🔧 Engineering {self.feature_set} features...")

        # Data cleaning and type conversion
        df = self._clean_data(df)

        # Create target variable first if finished_position exists
        if "finished_position" in df.columns:
            df["is_winner"] = (df["finished_position"] == 1).astype(int)

        # Apply feature engineering based on selected set
        feature_func = self.feature_versions[self.feature_set]
        df = feature_func(df)

        logger.info(
            f"✅ Feature engineering complete: {len(df)} records, {df.columns.size} features"
        )
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert data types consistently."""
        # Convert to numeric with error handling
        numeric_columns = [
            "win_odds",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "finished_position",
            "prize_money",
            "jockey_win_pct",
            "trainer_win_pct",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fill missing values with sensible defaults
        df["win_odds"] = df["win_odds"].fillna(
            df["win_odds"].median() if not df["win_odds"].isna().all() else 10.0
        )
        df["horse_age"] = df["horse_age"].fillna(4)
        df["horse_weight_kg"] = df["horse_weight_kg"].fillna(57)
        df["draw"] = df["draw"].fillna(8)
        df["prize_money"] = df["prize_money"].fillna(0)
        df["jockey_win_pct"] = df["jockey_win_pct"].fillna(0)
        df["trainer_win_pct"] = df["trainer_win_pct"].fillna(0)

        return df

    def _get_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic feature set - minimal features for fast training."""
        # Core odds features
        df["log_odds"] = np.log(df["win_odds"].clip(lower=1.01))
        df["implied_probability"] = 1 / df["win_odds"].clip(lower=1.01)
        df["is_favorite"] = (
            df.groupby("race_id")["win_odds"]
            .transform(lambda x: x == x.min())
            .astype(int)
        )

        # Performance features
        df["combined_performance"] = (df["jockey_win_pct"] + df["trainer_win_pct"]) / 2

        # Select features (is_winner will be added later)
        feature_cols = [
            "log_odds",
            "implied_probability",
            "is_favorite",
            "combined_performance",
            "horse_age",
            "horse_weight_kg",
            "draw",
        ]

        # Include is_winner if it exists, otherwise exclude it
        if "is_winner" in df.columns:
            feature_cols.append("is_winner")

        return df[feature_cols]

    def _get_standard_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standard feature set - production-quality features."""
        # Start with basic features
        df = self._get_basic_features(df)

        # Additional odds features
        df["odds_rank"] = df.groupby("race_id")["win_odds"].rank()

        # Race context features
        race_stats = (
            df.groupby("race_id")
            .agg(
                {
                    "horse_name": "count",  # field_size
                    "win_odds": ["min", "max", "mean"],
                    "prize_money": "first",
                }
            )
            .reset_index()
        )

        race_stats.columns = [
            "race_id",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "race_prize",
        ]
        df = df.merge(race_stats, on="race_id", how="left")

        # Positional features
        df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
        df["weight_percentile"] = df.groupby("race_id")["horse_weight_kg"].rank(
            pct=True
        )
        df["age_category"] = pd.cut(
            df["horse_age"], bins=[0, 3, 5, 7, 15], labels=[0, 1, 2, 3]
        )

        return df

    def _get_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature set - enhanced racing-specific features."""
        # Start with standard features
        df = self._get_standard_features(df)

        # Market dynamics
        df["is_outsider"] = (
            df.groupby("race_id")["win_odds"].rank(pct=True) > 0.8
        ).astype(int)
        df["market_strength"] = 1 / df["win_odds"]
        df["market_share"] = df.groupby("race_id")["market_strength"].transform(
            lambda x: x / x.sum() if x.sum() > 0 else 0
        )

        # Competition metrics
        df["competitive_density"] = df.groupby("race_id")["win_odds"].transform("std")

        # Interaction features
        df["odds_weight_interaction"] = df["log_odds"] * df["weight_percentile"]
        df["age_draw_interaction"] = df["horse_age"] * df["draw_percentile"]

        return df

    def _get_experimental_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Experimental feature set - cutting-edge features for research."""
        # Start with advanced features
        df = self._get_advanced_features(df)

        # Advanced market analysis
        df["price_movement"] = df.groupby("race_id")["win_odds"].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )

        # Historical performance simulation
        df["form_rating"] = (
            df["jockey_win_pct"] * 0.4 + df["trainer_win_pct"] * 0.6
        ) * 100

        # Complex interactions
        df["triple_interaction"] = (
            df["log_odds"] * df["draw_percentile"] * df["age_category"].astype(float)
        )

        return df


class UnifiedMLTrainer:
    """
    Unified ML Training System - Consolidates all trainer implementations.

    Replaces 8+ separate trainers with a single, configurable system that can operate
    in different modes for different use cases and performance requirements.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the unified ML trainer.

        Args:
            config_path: Path to YAML configuration file. If None, uses default config.
        """
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "trained_models" / "unified"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize components
        self.feature_engineer = FeatureEngineer(self.config["feature_set"])
        self.trained_models = {}
        self.model_performance = {}
        self.scaler = None

        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        logger.info(
            f"🚀 Unified ML Trainer initialized in '{self.config['mode']}' mode"
        )

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"📄 Loaded configuration from {config_path}")
        else:
            config = self._get_default_config()
            logger.info("📄 Using default configuration")

        return config

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for production mode."""
        return {
            "mode": "production",
            "feature_set": "standard",
            "models": ["RandomForest", "GradientBoosting", "Logistic"],
            "hyperparameter_tuning": False,
            "class_balancing": None,
            "ensemble_method": None,
            "parallel_training": False,
            "cross_validation_folds": 5,
            "test_size": 0.2,
            "random_state": 42,
            "performance_tracking": True,
        }

    def load_data(self) -> pd.DataFrame:
        """Load training data from the database."""
        logger.info("📊 Loading training data from database...")

        query = """
            SELECT 
                rr.*,
                js.wins as jockey_wins,
                js.runs as jockey_runs,
                js.win_percentage as jockey_win_pct,
                ts.wins as trainer_wins,
                ts.runs as trainer_runs,
                ts.win_percentage as trainer_win_pct
            FROM race_results rr
            LEFT JOIN jockey_stats js ON rr.jockey_name = js.jockey_name
            LEFT JOIN trainer_stats ts ON rr.trainer_name = ts.trainer_name
            WHERE rr.jockey_name != 'Unknown' 
            AND rr.trainer_name != 'Unknown'
            AND rr.course != 'Unknown'
            ORDER BY rr.race_date DESC, rr.race_id
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

    def train_models(self, strategy: str = "standard") -> Dict[str, Any]:
        """
        Main training entry point with configurable strategies.

        Args:
            strategy: Training strategy - 'fast', 'standard', 'advanced', 'experimental'

        Returns:
            Dictionary with training results and performance metrics
        """
        start_time = datetime.now()
        logger.info(f"🎯 Starting {strategy} training strategy...")

        # Load and prepare data
        df = self.load_data()
        df = self.feature_engineer.engineer_features(df)

        # Prepare features and target
        feature_cols = [col for col in df.columns if col != "is_winner"]
        X = df[feature_cols]
        y = df["is_winner"]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config["test_size"],
            random_state=self.config["random_state"],
            stratify=y,
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Apply class balancing if configured
        if self.config.get("class_balancing") and IMBALANCED_LEARN_AVAILABLE:
            X_train_scaled, y_train = self._apply_class_balancing(
                X_train_scaled, y_train
            )

        # Train models based on strategy
        strategies = {
            "fast": self._fast_training,
            "standard": self._standard_training,
            "advanced": self._advanced_training,
            "experimental": self._experimental_training,
        }

        training_func = strategies.get(strategy, self._standard_training)
        results = training_func(X_train_scaled, X_test_scaled, y_train, y_test)

        # Calculate total training time
        training_time = (datetime.now() - start_time).total_seconds() / 60
        results["training_time_minutes"] = training_time

        logger.info(f"🎉 Training complete in {training_time:.1f} minutes")

        # Save models and results
        self._save_training_results(results)

        return results

    def _fast_training(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Fast training with minimal models and default parameters."""
        logger.info("⚡ Fast training mode - optimized for speed")

        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=100, random_state=42, n_jobs=-1
            ),
            "Logistic": LogisticRegression(random_state=42, max_iter=1000),
        }

        return self._train_and_evaluate_models(models, X_train, X_test, y_train, y_test)

    def _standard_training(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Standard training with good balance of performance and speed."""
        logger.info("🎯 Standard training mode - balanced performance")

        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=150, learning_rate=0.1, random_state=42
            ),
            "Logistic": LogisticRegression(random_state=42, max_iter=1000),
        }

        return self._train_and_evaluate_models(models, X_train, X_test, y_train, y_test)

    def _advanced_training(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Advanced training with hyperparameter tuning and ensemble methods."""
        logger.info("🚀 Advanced training mode - hyperparameter optimization")

        base_models = {
            "RandomForest": RandomForestClassifier(random_state=42, n_jobs=-1),
            "GradientBoosting": GradientBoostingClassifier(random_state=42),
            "MLP": MLPClassifier(random_state=42, max_iter=500),
        }

        # Apply hyperparameter tuning if configured
        if self.config.get("hyperparameter_tuning"):
            base_models = self._tune_hyperparameters(base_models, X_train, y_train)

        return self._train_and_evaluate_models(
            base_models, X_train, X_test, y_train, y_test
        )

    def _experimental_training(
        self, X_train, X_test, y_train, y_test
    ) -> Dict[str, Any]:
        """Experimental training with all available models and ensemble methods."""
        logger.info("🧪 Experimental training mode - cutting-edge techniques")

        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=300, random_state=42, n_jobs=-1
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=200, random_state=42
            ),
            "ExtraTrees": ExtraTreesClassifier(
                n_estimators=200, random_state=42, n_jobs=-1
            ),
            "MLP": MLPClassifier(
                hidden_layer_sizes=(100, 50), random_state=42, max_iter=500
            ),
            "Logistic": LogisticRegression(random_state=42, max_iter=1000),
        }

        results = self._train_and_evaluate_models(
            models, X_train, X_test, y_train, y_test
        )

        # Create ensemble if configured
        if self.config.get("ensemble_method"):
            ensemble_model = self._create_ensemble(models, X_train, y_train)
            ensemble_results = self._evaluate_model(ensemble_model, X_test, y_test)
            results["models"]["Ensemble"] = ensemble_results

        return results

    def _train_and_evaluate_models(
        self, models: Dict[str, Any], X_train, X_test, y_train, y_test
    ) -> Dict[str, Any]:
        """Train and evaluate multiple models."""
        results = {
            "models": {},
            "best_model": None,
            "feature_names": (
                list(X_train.columns) if hasattr(X_train, "columns") else []
            ),
        }
        best_score = 0

        for name, model in models.items():
            logger.info(f"🔄 Training {name}...")

            # Train model
            model.fit(X_train, y_train)

            # Evaluate model
            model_results = self._evaluate_model(model, X_test, y_test)

            # Cross-validation
            cv_scores = cross_val_score(
                model,
                X_train,
                y_train,
                cv=self.config["cross_validation_folds"],
                scoring="roc_auc",
            )
            model_results["cv_auc_mean"] = cv_scores.mean()
            model_results["cv_auc_std"] = cv_scores.std()

            results["models"][name] = model_results
            self.trained_models[name] = model

            # Track best model
            if model_results["roc_auc"] > best_score:
                best_score = model_results["roc_auc"]
                results["best_model"] = name

            logger.info(f"✅ {name} - ROC AUC: {model_results['roc_auc']:.3f}")

        return results

    def _evaluate_model(self, model, X_test, y_test) -> Dict[str, float]:
        """Evaluate a single model and return performance metrics."""
        y_pred = model.predict(X_test)
        y_pred_proba = (
            model.predict_proba(X_test)[:, 1]
            if hasattr(model, "predict_proba")
            else None
        )

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
        }

        if y_pred_proba is not None:
            metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba)

        return metrics

    def _apply_class_balancing(self, X_train, y_train):
        """Apply class balancing technique if configured."""
        method = self.config["class_balancing"]
        logger.info(f"⚖️ Applying {method} class balancing...")

        if method == "smote":
            sampler = SMOTE(random_state=42)
        elif method == "adasyn":
            sampler = ADASYN(random_state=42)
        elif method == "undersample":
            sampler = RandomUnderSampler(random_state=42)
        else:
            logger.warning(f"Unknown balancing method: {method}")
            return X_train, y_train

        X_balanced, y_balanced = sampler.fit_resample(X_train, y_train)
        logger.info(f"✅ Balanced dataset: {len(y_balanced)} samples")

        return X_balanced, y_balanced

    def _create_ensemble(self, models: Dict[str, Any], X_train, y_train):
        """Create an ensemble model from trained models."""
        logger.info("🎭 Creating ensemble model...")

        estimators = [(name, model) for name, model in models.items()]
        ensemble = VotingClassifier(estimators=estimators, voting="soft")
        ensemble.fit(X_train, y_train)

        return ensemble

    def _save_training_results(self, results: Dict[str, Any]):
        """Save trained models and results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save models
        for name, model in self.trained_models.items():
            model_path = self.models_dir / f"{name}_{timestamp}.joblib"
            joblib.dump(model, model_path)
            logger.info(f"💾 Saved {name} model to {model_path}")

        # Save scaler
        if self.scaler:
            scaler_path = self.models_dir / f"scaler_{timestamp}.joblib"
            joblib.dump(self.scaler, scaler_path)

        # Save results
        results_path = self.models_dir / f"training_results_{timestamp}.yaml"
        with open(results_path, "w") as f:
            yaml.dump(results, f, default_flow_style=False)

        logger.info(f"📊 Training results saved to {results_path}")


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Unified ML Training System")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument(
        "--strategy",
        type=str,
        default="standard",
        choices=["fast", "standard", "advanced", "experimental"],
        help="Training strategy",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="production",
        choices=["production", "enhanced", "experimental"],
        help="Training mode",
    )

    args = parser.parse_args()

    # Initialize trainer
    trainer = UnifiedMLTrainer(config_path=args.config)

    # Run training
    results = trainer.train_models(strategy=args.strategy)

    # Print summary
    print(f"\n🎉 Training Complete!")
    print(f"⏱️  Training time: {results['training_time_minutes']:.1f} minutes")
    print(f"🏆 Best model: {results['best_model']}")
    print(f"📈 Best ROC AUC: {results['models'][results['best_model']]['roc_auc']:.3f}")


if __name__ == "__main__":
    main()
