#!/usr/bin/env python3
"""
Advanced Ensemble System - Simplified Version
Focuses on multiple model training with ensemble methods
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
import warnings

warnings.filterwarnings("ignore")

# ML Libraries
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split,
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
)

# Class Balancing
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE

# Database
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")


class AdvancedEnsembleTrainer:
    """Advanced ensemble training with multiple algorithms."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        self.ensemble_model = None

    def create_enhanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create enhanced features for better model performance."""
        logger.info("🔧 Creating enhanced features...")

        df_enhanced = df.copy()

        # Market analysis features
        if "odds_decimal" in df_enhanced.columns:
            df_enhanced["log_odds"] = np.log(df_enhanced["odds_decimal"])
            df_enhanced["odds_rank"] = df_enhanced.groupby("race_id")[
                "odds_decimal"
            ].rank()
            df_enhanced["odds_percentile"] = df_enhanced.groupby("race_id")[
                "odds_decimal"
            ].rank(pct=True)
            df_enhanced["is_favorite"] = (df_enhanced["odds_rank"] == 1).astype(int)
            df_enhanced["is_outsider"] = (df_enhanced["odds_percentile"] > 0.8).astype(
                int
            )

            # Market strength and share
            df_enhanced["market_strength"] = 1 / df_enhanced["odds_decimal"]
            race_total_strength = df_enhanced.groupby("race_id")[
                "market_strength"
            ].transform("sum")
            df_enhanced["market_share"] = (
                df_enhanced["market_strength"] / race_total_strength
            )

        # Positional features
        if "draw" in df_enhanced.columns:
            df_enhanced["draw_percentile"] = df_enhanced.groupby("race_id")[
                "draw"
            ].rank(pct=True)

        if "weight" in df_enhanced.columns:
            df_enhanced["weight_percentile"] = df_enhanced.groupby("race_id")[
                "weight"
            ].rank(pct=True)

        # Race context
        if "runners" in df_enhanced.columns:
            df_enhanced["field_size"] = df_enhanced["runners"]
            df_enhanced["odds_spread"] = df_enhanced.groupby("race_id")[
                "odds_decimal"
            ].transform(lambda x: x.max() - x.min())

        # Horse quality features
        if "horse_rate" in df_enhanced.columns:
            df_enhanced["rating_rank"] = df_enhanced.groupby("race_id")[
                "horse_rate"
            ].rank(ascending=False)
            df_enhanced["rating_percentile"] = df_enhanced.groupby("race_id")[
                "horse_rate"
            ].rank(pct=True)

        # Interaction features
        if "odds_decimal" in df_enhanced.columns and "weight" in df_enhanced.columns:
            df_enhanced["odds_weight_ratio"] = (
                df_enhanced["odds_decimal"] / df_enhanced["weight"]
            )

        if (
            "horse_rate" in df_enhanced.columns
            and "odds_decimal" in df_enhanced.columns
        ):
            df_enhanced["rating_odds_ratio"] = (
                df_enhanced["horse_rate"] / df_enhanced["odds_decimal"]
            )

        # Categorical encoding
        categorical_cols = [
            "course",
            "race_type",
            "surface",
            "race_class",
            "jockey",
            "trainer",
        ]
        for col in categorical_cols:
            if col in df_enhanced.columns:
                le = LabelEncoder()
                df_enhanced[f"{col}_encoded"] = le.fit_transform(
                    df_enhanced[col].astype(str)
                )

        logger.info(
            f"✅ Enhanced features created: {df.shape[1]} -> {df_enhanced.shape[1]} features"
        )
        return df_enhanced

    def create_base_models(self) -> Dict[str, Any]:
        """Create diverse base models for ensemble."""
        logger.info("🤖 Creating base models...")

        models = {
            "random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42
            ),
            "extra_trees": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
            ),
            "logistic_regression": LogisticRegression(
                class_weight="balanced", max_iter=1000, random_state=42
            ),
        }

        logger.info(f"✅ Created {len(models)} base models")
        return models

    def train_with_balancing(self, X: pd.DataFrame, y: pd.Series):
        """Train models with advanced balancing techniques."""
        logger.info("🚀 Training ensemble models with balancing...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns
        )
        X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

        self.scalers["feature_scaler"] = scaler

        # Try different balancing methods
        balancing_methods = {
            "smote": SMOTE(random_state=42),
            "borderline_smote": BorderlineSMOTE(random_state=42),
            "adasyn": ADASYN(random_state=42),
        }

        best_balancer = None
        best_balance_score = 0

        logger.info("🔍 Testing balancing methods...")
        for balance_name, balancer in balancing_methods.items():
            try:
                X_balanced, y_balanced = balancer.fit_resample(X_train_scaled, y_train)

                # Quick test with Random Forest
                test_rf = RandomForestClassifier(n_estimators=50, random_state=42)
                cv_scores = cross_val_score(
                    test_rf, X_balanced, y_balanced, cv=3, scoring="roc_auc"
                )
                avg_score = cv_scores.mean()

                logger.info(f"   {balance_name}: CV AUC = {avg_score:.4f}")

                if avg_score > best_balance_score:
                    best_balance_score = avg_score
                    best_balancer = balancer

            except Exception as e:
                logger.warning(f"   {balance_name} failed: {str(e)}")

        # Apply best balancing
        if best_balancer:
            X_train_balanced, y_train_balanced = best_balancer.fit_resample(
                X_train_scaled, y_train
            )
            logger.info(
                f"✅ Using best balancing method with CV AUC: {best_balance_score:.4f}"
            )
        else:
            X_train_balanced, y_train_balanced = X_train_scaled, y_train
            logger.warning(
                "⚠️  No balancing method worked, proceeding without balancing"
            )

        # Train models
        base_models = self.create_base_models()
        trained_models = {}
        model_performances = {}

        for model_name, model in base_models.items():
            try:
                start_time = datetime.now()
                logger.info(f"🔄 Training {model_name}...")

                # Train model
                model.fit(X_train_balanced, y_train_balanced)

                # Evaluate
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

                # Calculate metrics
                auc = roc_auc_score(y_test, y_pred_proba)
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)

                # Cross-validation
                cv_scores = cross_val_score(
                    model, X_train_balanced, y_train_balanced, cv=5, scoring="roc_auc"
                )
                cv_auc = cv_scores.mean()
                cv_std = cv_scores.std()

                training_time = (datetime.now() - start_time).total_seconds()

                # Store results
                trained_models[model_name] = model
                model_performances[model_name] = {
                    "auc": auc,
                    "cv_auc": cv_auc,
                    "cv_std": cv_std,
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "training_time": training_time,
                }

                logger.info(
                    f"✅ {model_name}: AUC={auc:.4f}, CV_AUC={cv_auc:.4f}±{cv_std:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ {model_name} training failed: {str(e)}")
                continue

        # Create ensemble
        if len(trained_models) >= 3:
            logger.info("🎭 Creating ensemble model...")

            # Select top models for ensemble
            sorted_models = sorted(
                model_performances.items(), key=lambda x: x[1]["cv_auc"], reverse=True
            )
            top_models = sorted_models[: min(5, len(sorted_models))]

            ensemble_estimators = [
                (name, trained_models[name]) for name, _ in top_models
            ]

            self.ensemble_model = VotingClassifier(
                estimators=ensemble_estimators, voting="soft"
            )

            self.ensemble_model.fit(X_train_balanced, y_train_balanced)

            # Evaluate ensemble
            y_ensemble_pred = self.ensemble_model.predict(X_test_scaled)
            y_ensemble_proba = self.ensemble_model.predict_proba(X_test_scaled)[:, 1]

            ensemble_auc = roc_auc_score(y_test, y_ensemble_proba)
            ensemble_accuracy = accuracy_score(y_test, y_ensemble_pred)

            model_performances["ensemble"] = {
                "auc": ensemble_auc,
                "accuracy": ensemble_accuracy,
                "models_used": [name for name, _ in top_models],
            }

            logger.info(
                f"🎭 Ensemble: AUC={ensemble_auc:.4f}, Models: {[name for name, _ in top_models]}"
            )

        self.models = trained_models
        self.performance_metrics = model_performances

        return {
            "models": trained_models,
            "ensemble": self.ensemble_model,
            "performance": model_performances,
            "scalers": self.scalers,
            "test_data": (X_test_scaled, y_test),
        }


def main():
    """Main execution function."""
    logger.info("🚀 Advanced Ensemble System - Phase 2")
    logger.info("=" * 50)

    # Load environment
    load_dotenv()

    # Database connection
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/racing_data"
    )

    try:
        engine = create_engine(db_url)
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return

    # Load data with optimized query
    query = """
    SELECT 
        rc.race_id,
        rc.course,
        rc.race_type,
        rc.distance,
        rc.surface,
        rc.prize,
        rc.class as race_class,
        rc.runners,
        rd.horse_id,
        rd.name as horse_name,
        rd.age,
        rd.weight,
        rd.draw,
        rd.odds_decimal,
        rd.jockey,
        rd.trainer,
        CAST(rd.horse_rate as NUMERIC) as horse_rate,
        -- Synthetic target
        CASE 
            WHEN ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY rd.odds_decimal) = 1 
                 AND RANDOM() < 0.7 THEN 1
            WHEN ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY rd.odds_decimal) > 3 
                 AND RANDOM() < 0.1 THEN 1
            ELSE 0
        END as won
    FROM races_cards rc
    JOIN racecard_details rd ON rc.race_id = rd.race_id
    WHERE rc.race_id IS NOT NULL 
      AND rd.odds_decimal IS NOT NULL 
      AND rd.horse_rate IS NOT NULL
      AND rd.horse_rate != ''
      AND rd.horse_rate != '-'
    LIMIT 50000
    """

    try:
        logger.info("📊 Loading data...")
        df = pd.read_sql(query, engine)
        logger.info(f"   Loaded {len(df)} records")

        # Initialize trainer
        trainer = AdvancedEnsembleTrainer()

        # Create enhanced features
        df_enhanced = trainer.create_enhanced_features(df)

        # Prepare features and target
        exclude_cols = [
            "won",
            "race_id",
            "horse_id",
            "horse_name",
            "course",
            "race_type",
            "surface",
            "race_class",
            "jockey",
            "trainer",
            "distance",
            "prize",
        ]
        feature_cols = [col for col in df_enhanced.columns if col not in exclude_cols]

        X = df_enhanced[feature_cols].copy()
        y = df_enhanced["won"].copy()

        logger.info(f"📈 Dataset prepared: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"   Win rate: {y.mean():.3f}")

        # Train ensemble
        results = trainer.train_with_balancing(X, y)

        # Save models
        models_dir = Path("models/advanced_ensemble_v2")
        models_dir.mkdir(parents=True, exist_ok=True)

        # Save individual models
        for model_name, model in results["models"].items():
            joblib.dump(model, models_dir / f"{model_name}_v2.joblib")

        # Save ensemble
        if results["ensemble"]:
            joblib.dump(results["ensemble"], models_dir / "ensemble_v2.joblib")

        # Save scalers
        joblib.dump(results["scalers"], models_dir / "scalers_v2.joblib")

        # Save performance
        import json

        with open(models_dir / "performance_v2.json", "w") as f:
            perf_json = {}
            for model_name, metrics in results["performance"].items():
                perf_json[model_name] = {}
                for key, value in metrics.items():
                    if isinstance(value, (np.float64, np.float32)):
                        perf_json[model_name][key] = float(value)
                    elif isinstance(value, (np.int64, np.int32)):
                        perf_json[model_name][key] = int(value)
                    else:
                        perf_json[model_name][key] = value
            json.dump(perf_json, f, indent=2)

        # Results summary
        logger.info("\n🏆 ADVANCED ENSEMBLE RESULTS")
        logger.info("=" * 40)

        best_individual = max(
            results["performance"].items(),
            key=lambda x: x[1].get("cv_auc", 0) if x[0] != "ensemble" else 0,
        )

        logger.info(f"🥇 Best Individual: {best_individual[0]}")
        logger.info(
            f"   CV AUC: {best_individual[1]['cv_auc']:.4f} ± {best_individual[1]['cv_std']:.4f}"
        )
        logger.info(f"   Test AUC: {best_individual[1]['auc']:.4f}")

        if "ensemble" in results["performance"]:
            ens = results["performance"]["ensemble"]
            logger.info(f"\n🎭 Ensemble Model:")
            logger.info(f"   AUC: {ens['auc']:.4f}")
            logger.info(f"   Models: {', '.join(ens['models_used'])}")

        logger.info(f"\n✅ Advanced ensemble training complete!")
        logger.info(f"💾 Models saved to: {models_dir}")

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
