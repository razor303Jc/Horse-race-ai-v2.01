#!/usr/bin/env python3
"""
Results Database Ensemble Training Script
========================================

Trains ensemble models on actual race results with schema-corrected queries.
"""

import sys
import logging
import json
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import joblib

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import course mapper
from src.horse_racing_ai.ml.course_mapper import CourseMapper

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ResultsEnsembleTrainer:
    """Ensemble trainer for results database with corrected schema."""

    def __init__(self, models_dir: str = "/app/models"):
        """Initialize the trainer."""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Database configuration for results database
        self.db_config = {
            "host": "postgres",
            "port": 5432,
            "user": "horse_racing",
            "password": "secure_password_123",
            "database": "results_horse_racing_db",
        }

        # Model configurations
        self.model_configs = {
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
            ),
            "logistic_regression": LogisticRegression(
                random_state=42, max_iter=1000, solver="lbfgs"
            ),
        }

    def get_db_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)

    def load_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Load race results data for training with corrected schema."""
        logger.info("🏁 Loading race results data from results database...")

        query = """
            SELECT DISTINCT
                r.race_id,
                r.race_number,
                r.date as race_date,
                r.course,
                r.race_name,
                r.class,
                r.distance,
                rec.horse_name,
                rec.jockey,
                rec.trainer,
                rec.position,
                CAST(rec.starting_price AS FLOAT) as odds_decimal,
                CAST(rec.weight AS FLOAT) as horse_weight_kg,
                CAST(rec.age AS INT) as horse_age,
                
                -- Calculate market metrics (simplified)
                ROW_NUMBER() OVER (
                    PARTITION BY r.race_id ORDER BY CAST(rec.starting_price AS FLOAT)
                ) as odds_rank,
                CASE WHEN ROW_NUMBER() OVER (
                    PARTITION BY r.race_id ORDER BY CAST(rec.starting_price AS FLOAT)
                ) = 1 THEN 1 ELSE 0 END as is_favorite,
                1.0 / CAST(rec.starting_price AS FLOAT) as implied_probability,
                LN(CAST(rec.starting_price AS FLOAT)) as log_odds,
                
                -- Get jockey stats
                COALESCE(js.win_rate, 0) as jockey_win_pct,
                COALESCE(js.wins, 0) as jockey_wins,
                COALESCE(js.runs, 0) as jockey_runs,
                
                -- Get trainer stats
                COALESCE(ts.win_rate, 0) as trainer_win_pct,
                COALESCE(ts.wins, 0) as trainer_wins,
                COALESCE(ts.runs, 0) as trainer_runs,
                
                -- Race level stats
                COUNT(*) OVER (PARTITION BY r.race_id) as field_size
                
            FROM races r
            JOIN records rec ON r.race_id = rec.race_id
            LEFT JOIN jockeys_stats js ON rec.jockey = js.jockey_name
            LEFT JOIN trainers_stats ts ON rec.trainer = ts.trainer_name
            WHERE rec.position IS NOT NULL
              AND rec.starting_price IS NOT NULL
              AND CAST(rec.starting_price AS FLOAT) > 0
              AND rec.jockey IS NOT NULL
              AND rec.trainer IS NOT NULL
            ORDER BY r.race_id, CAST(rec.starting_price AS FLOAT)
        """

        try:
            with self.get_db_connection() as conn:
                df = pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return pd.DataFrame(), pd.Series()

        logger.info(
            f"✅ Loaded {len(df)} horse records from {df['race_id'].nunique()} races"
        )
        logger.info(f"   Courses: {', '.join(df['course'].unique()[:5])}...")

        # Create target variable (winner = 1, others = 0)
        target = (df["position"] == 1).astype(int)

        logger.info("📊 Target distribution:")
        logger.info(f"   Winners: {target.sum()} ({target.mean()*100:.1f}%)")
        non_winners = (~target.astype(bool)).sum()
        logger.info(f"   Non-winners: {non_winners} ({(1-target.mean())*100:.1f}%)")

        return df, target

    def engineer_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Engineer features for training with course mapping."""
        logger.info("🛠️ Engineering features...")

        features_df = df.copy()

        # Map courses to numerical values
        logger.info("🏁 Mapping courses to numerical IDs...")
        features_df["course_id"] = features_df["course"].apply(
            CourseMapper.get_course_id
        )

        # Log course mappings for verification
        unique_courses = features_df[["course", "course_id"]].drop_duplicates()
        for _, row in unique_courses.iterrows():
            logger.info(f"   {row['course']} -> ID {row['course_id']}")

        # Calculate race-level statistics
        race_stats = (
            features_df.groupby("race_id")
            .agg(
                {
                    "odds_decimal": ["min", "max", "mean"],
                    "implied_probability": "sum",
                    "horse_age": "mean",
                    "horse_weight_kg": "mean",
                }
            )
            .round(4)
        )

        race_stats.columns = [
            "min_odds",
            "max_odds",
            "avg_odds",
            "total_implied_prob",
            "avg_age",
            "avg_weight",
        ]
        race_stats = race_stats.reset_index()

        # Merge race statistics
        features_df = features_df.merge(race_stats, on="race_id", how="left")

        # Calculate percentiles within each race
        race_groups = features_df.groupby("race_id")
        features_df["weight_percentile"] = race_groups["horse_weight_kg"].rank(pct=True)
        features_df["odds_percentile"] = race_groups["odds_decimal"].rank(
            pct=True, ascending=False
        )
        features_df["age_percentile"] = race_groups["horse_age"].rank(pct=True)

        # Age categories
        features_df["age_category"] = pd.cut(
            features_df["horse_age"], bins=[0, 3, 5, 8, 100], labels=[0, 1, 2, 3]
        ).astype(int)

        # Performance metrics
        features_df["jockey_performance"] = features_df["jockey_win_pct"] / 100.0
        features_df["trainer_performance"] = features_df["trainer_win_pct"] / 100.0
        features_df["combined_performance"] = (
            features_df["jockey_performance"] * 0.6
            + features_df["trainer_performance"] * 0.4
        )

        # Market efficiency features
        features_df["odds_value"] = features_df["implied_probability"] - (
            1.0 / features_df["total_implied_prob"]
        )
        features_df["market_efficiency"] = abs(features_df["total_implied_prob"] - 1.0)

        # Distance-based features
        try:
            features_df["distance_numeric"] = pd.to_numeric(
                features_df["distance"], errors="coerce"
            )
            features_df["distance_category"] = (
                pd.cut(
                    features_df["distance_numeric"],
                    bins=[0, 1200, 1600, 2000, 5000],
                    labels=[0, 1, 2, 3],
                )
                .fillna(1)
                .astype(int)
            )
        except:
            features_df["distance_category"] = 1

        # Class-based features
        features_df["class_numeric"] = pd.to_numeric(
            features_df["class"].str.extract(r"(\d+)")[0], errors="coerce"
        ).fillna(4)

        # Final feature selection (includes course_id)
        feature_columns = [
            "log_odds",
            "implied_probability",
            "odds_rank",
            "is_favorite",
            "combined_performance",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "weight_percentile",
            "odds_percentile",
            "age_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "course_id",
            "jockey_win_pct",
            "trainer_win_pct",
            "jockey_performance",
            "trainer_performance",
            "odds_value",
            "market_efficiency",
            "distance_category",
            "class_numeric",
        ]

        # Ensure all columns exist and fill NaN values
        for col in feature_columns:
            if col not in features_df.columns:
                features_df[col] = 0.0

        features_df["jockey_win_pct"] = features_df["jockey_win_pct"] / 100.0
        features_df["trainer_win_pct"] = features_df["trainer_win_pct"] / 100.0
        features_df = features_df.fillna(0.0)

        # Select final features
        final_features_df = features_df[feature_columns].copy()

        logger.info(
            f"✅ Engineered {len(feature_columns)} features for {len(final_features_df)} records"
        )

        return final_features_df, feature_columns

    def optimize_ensemble_weights(
        self, X: pd.DataFrame, y: pd.Series, cv_folds: int = 5
    ) -> Dict[str, Any]:
        """Optimize ensemble weights using cross-validation."""
        logger.info("🎯 Optimizing ensemble weights with cross-validation...")

        # Prepare cross-validation
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train individual models and get cross-validation scores
        individual_scores = {}
        models_for_voting = []

        for name, model in self.model_configs.items():
            logger.info(f"   Training {name}...")

            # Cross-validation scores
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring="roc_auc")
            individual_scores[name] = {
                "mean_auc": cv_scores.mean(),
                "std_auc": cv_scores.std(),
                "scores": cv_scores.tolist(),
            }

            # Train on full dataset for voting
            model.fit(X_scaled, y)
            models_for_voting.append((name, model))

            logger.info(f"     AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        # Calculate optimized weights based on individual performance
        weights = {}
        total_score = sum(scores["mean_auc"] for scores in individual_scores.values())

        for name, scores in individual_scores.items():
            # Weight based on AUC performance and inverse of standard deviation
            weight = (scores["mean_auc"] / total_score) * (
                1.0 / (scores["std_auc"] + 0.01)
            )
            weights[name] = weight

        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {name: w / total_weight for name, w in weights.items()}

        # Test ensemble
        weighted_ensemble = VotingClassifier(
            estimators=models_for_voting,
            voting="soft",
            weights=list(normalized_weights.values()),
        )
        weighted_ensemble.fit(X_scaled, y)

        # Ensemble cross-validation
        ensemble_cv_scores = cross_val_score(
            weighted_ensemble, X_scaled, y, cv=cv, scoring="roc_auc"
        )

        optimization_results = {
            "individual_scores": individual_scores,
            "optimized_weights": normalized_weights,
            "ensemble_auc": ensemble_cv_scores.mean(),
            "ensemble_std": ensemble_cv_scores.std(),
            "cv_folds": cv_folds,
            "total_samples": len(X),
            "positive_samples": y.sum(),
            "scaler": scaler,
            "ensemble_model": weighted_ensemble,
        }

        logger.info("✅ Ensemble optimization completed")
        logger.info("📊 Optimized weights:")
        for name, weight in normalized_weights.items():
            logger.info(f"   {name}: {weight:.4f}")
        logger.info(
            f"📈 Ensemble AUC: {ensemble_cv_scores.mean():.4f} ± {ensemble_cv_scores.std():.4f}"
        )

        return optimization_results

    def evaluate_model(self, model, X: np.ndarray, y: pd.Series) -> Dict[str, Any]:
        """Comprehensive model evaluation."""
        logger.info("📊 Evaluating model performance...")

        # Predictions
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)[:, 1]

        # Calculate metrics
        auc_score = roc_auc_score(y, y_pred_proba)
        classification_rep = classification_report(y, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y, y_pred)

        evaluation_results = {
            "auc_score": auc_score,
            "classification_report": classification_rep,
            "confusion_matrix": conf_matrix.tolist(),
            "accuracy": classification_rep["accuracy"],
            "precision": classification_rep["1"]["precision"],
            "recall": classification_rep["1"]["recall"],
            "f1_score": classification_rep["1"]["f1-score"],
        }

        logger.info(f"   AUC Score: {auc_score:.4f}")
        logger.info(f"   Accuracy: {classification_rep['accuracy']:.4f}")
        logger.info(f"   Precision: {classification_rep['1']['precision']:.4f}")
        logger.info(f"   Recall: {classification_rep['1']['recall']:.4f}")
        logger.info(f"   F1-Score: {classification_rep['1']['f1-score']:.4f}")

        return evaluation_results

    def train_optimized_ensemble(self, save_model: bool = True) -> Dict[str, Any]:
        """Train the optimized ensemble model."""
        logger.info("🚀 Starting optimized ensemble training...")

        # Load training data
        df, target = self.load_training_data()

        if df.empty:
            logger.error("❌ No training data loaded!")
            return {}

        # Engineer features
        features_df, feature_columns = self.engineer_features(df)
        X = features_df[feature_columns]

        # Optimize ensemble
        optimization_results = self.optimize_ensemble_weights(X, target)

        # Final evaluation
        scaler = optimization_results["scaler"]
        ensemble_model = optimization_results["ensemble_model"]
        X_scaled = scaler.transform(X)

        final_evaluation = self.evaluate_model(ensemble_model, X_scaled, target)

        # Prepare final model data
        final_model_data = {
            "ensemble_model": ensemble_model,
            "individual_models": dict(self.model_configs.items()),
            "scaler": scaler,
            "feature_names": feature_columns,
            "optimization_results": optimization_results,
            "evaluation_results": final_evaluation,
            "training_metadata": {
                "training_date": datetime.now().isoformat(),
                "training_samples": len(X),
                "feature_count": len(feature_columns),
                "target_distribution": target.value_counts().to_dict(),
                "model_version": "v2.04_results_optimized",
            },
        }

        if save_model:
            model_path = self.save_optimized_model(final_model_data)
            logger.info(f"💾 Optimized model saved to: {model_path}")

        # Generate training report
        self.generate_training_summary(final_model_data)

        return final_model_data

    def save_optimized_model(self, model_data: Dict[str, Any]) -> str:
        """Save the optimized model."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"results_optimized_ensemble_{timestamp}.joblib"
        model_path = self.models_dir / model_filename

        joblib.dump(model_data, model_path)

        # Also save a latest version
        latest_path = self.models_dir / "results_optimized_ensemble_latest.joblib"
        joblib.dump(model_data, latest_path)

        return str(model_path)

    def generate_training_summary(self, model_data: Dict[str, Any]) -> None:
        """Generate comprehensive training summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🏆 RESULTS DATABASE ENSEMBLE TRAINING COMPLETE")
        logger.info("=" * 60)

        # Training summary
        metadata = model_data["training_metadata"]
        logger.info(f"📅 Training Date: {metadata['training_date']}")
        logger.info(f"📊 Training Samples: {metadata['training_samples']}")
        logger.info(f"🎯 Features Used: {metadata['feature_count']}")
        logger.info(f"🏆 Winners: {metadata['target_distribution'].get(1, 0)}")
        logger.info(f"🥈 Non-winners: {metadata['target_distribution'].get(0, 0)}")

        # Performance metrics
        eval_results = model_data["evaluation_results"]
        logger.info("\n📈 PERFORMANCE METRICS:")
        logger.info(f"   AUC Score: {eval_results['auc_score']:.4f}")
        logger.info(f"   Accuracy: {eval_results['accuracy']:.4f}")
        logger.info(f"   Precision: {eval_results['precision']:.4f}")
        logger.info(f"   Recall: {eval_results['recall']:.4f}")
        logger.info(f"   F1-Score: {eval_results['f1_score']:.4f}")

        # Optimized weights
        weights = model_data["optimization_results"]["optimized_weights"]
        logger.info("\n⚖️ OPTIMIZED WEIGHTS:")
        for model, weight in weights.items():
            logger.info(f"   {model}: {weight:.4f}")

        # Individual model performance
        individual_scores = model_data["optimization_results"]["individual_scores"]
        logger.info("\n🎯 INDIVIDUAL MODEL PERFORMANCE:")
        for model, scores in individual_scores.items():
            logger.info(
                f"   {model}: {scores['mean_auc']:.4f} ± {scores['std_auc']:.4f}"
            )

        ensemble_auc = model_data["optimization_results"]["ensemble_auc"]
        ensemble_std = model_data["optimization_results"]["ensemble_std"]
        logger.info(
            f"\n🏅 ENSEMBLE PERFORMANCE: {ensemble_auc:.4f} ± {ensemble_std:.4f}"
        )

        logger.info("\n🎉 Model is ready for production use!")
        logger.info("=" * 60)


def main():
    """Main training function."""
    logger.info("🏇 Starting Results Database Ensemble Training...")

    try:
        # Initialize trainer
        trainer = ResultsEnsembleTrainer()

        # Train optimized ensemble
        model_data = trainer.train_optimized_ensemble(save_model=True)

        if model_data:
            logger.info("✅ Results database ensemble training completed successfully!")
            return model_data
        else:
            logger.error("❌ Training failed - no data loaded")
            return None

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    if result:
        print("\n🎉 Training completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Training failed!")
        sys.exit(1)
