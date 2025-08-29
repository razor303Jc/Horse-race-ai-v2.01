#!/usr/bin/env python3
"""
Enhanced Ensemble Training Script - Results Database Optimization
================================================================

Advanced training script that:
1. Trains on actual race results from results_horse_racing_db
2. Optimizes ensemble weighting using advanced techniques
3. Performs cross-validation and hyperparameter tuning
4. Implements adaptive weighting based on confidence scores
5. Exports optimized models for production use
"""

import sys
import logging
import json
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sklearn.model_selection import cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.ml.v2_01_ensemble_predictor import V201EnsemblePredictor

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedEnsembleTrainer:
    """Advanced ensemble trainer with optimization capabilities."""

    def __init__(self, models_dir: str = None):
        """Initialize the enhanced trainer."""
        self.models_dir = Path(models_dir) if models_dir else project_root / "models"
        self.models_dir.mkdir(exist_ok=True)

        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "user": "horse_racing",
            "password": "secure_password_123",
            "database": "results_horse_racing_db",  # Use results database
        }

        # Initialize V201EnsemblePredictor
        self.predictor = V201EnsemblePredictor(models_dir=str(self.models_dir))

        # Training parameters
        self.optimization_results = {}
        self.feature_importance_results = {}

    def get_db_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)

    def load_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Load race results data for training."""
        logger.info("🏁 Loading race results data from results database...")

        query = """
            SELECT DISTINCT
                r.race_id,
                r.race_number,
                r.race_date,
                r.course,
                r.race_name,
                r.class,
                r.distance,
                rec.horse_name,
                rec.jockey,
                rec.trainer,
                rec.position,
                rec.odds_decimal,
                rec.weight_kg as horse_weight_kg,
                rec.draw,
                rec.age as horse_age,
                
                -- Calculate market metrics
                ROW_NUMBER() OVER (
                    PARTITION BY r.race_id ORDER BY rec.odds_decimal
                ) as odds_rank,
                CASE WHEN ROW_NUMBER() OVER (
                    PARTITION BY r.race_id ORDER BY rec.odds_decimal
                ) = 1 THEN 1 ELSE 0 END as is_favorite,
                1.0 / rec.odds_decimal as implied_probability,
                LN(rec.odds_decimal) as log_odds,
                
                -- Get jockey stats
                COALESCE(js.percentage_wins, 0) as jockey_win_pct,
                COALESCE(js.wins, 0) as jockey_wins,
                COALESCE(js.total_races, 0) as jockey_runs,
                
                -- Get trainer stats
                COALESCE(ts.percentage_wins, 0) as trainer_win_pct,
                COALESCE(ts.wins, 0) as trainer_wins,
                COALESCE(ts.total_races, 0) as trainer_runs,
                
                -- Race level stats
                COUNT(*) OVER (PARTITION BY r.race_id) as field_size
                
            FROM races r
            JOIN records rec ON r.race_id = rec.race_id
            LEFT JOIN jockeys_stats js ON rec.jockey = js.jockey_name
            LEFT JOIN trainers_stats ts ON rec.trainer = ts.trainer_name
            WHERE rec.position IS NOT NULL
              AND rec.odds_decimal > 0
              AND rec.jockey IS NOT NULL
              AND rec.trainer IS NOT NULL
            ORDER BY r.race_id, rec.odds_decimal
        """

        with self.get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)

        records_count = len(df)
        races_count = df["race_id"].nunique()
        logger.info(f"✅ Loaded {records_count} horse records from {races_count} races")
        logger.info(f"   Courses: {', '.join(df['course'].unique())}")

        # Create target variable (winner = 1, others = 0)
        target = (df["position"] == 1).astype(int)

        logger.info(f"📊 Target distribution:")
        logger.info(f"   Winners: {target.sum()} ({target.mean()*100:.1f}%)")
        logger.info(
            f"   Non-winners: {(~target.astype(bool)).sum()} ({(1-target.mean())*100:.1f}%)"
        )

        return df, target

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer comprehensive features for training."""
        logger.info("🛠️ Engineering comprehensive features...")

        features_df = df.copy()

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
        features_df["draw_percentile"] = features_df.groupby("race_id")["draw"].rank(
            pct=True
        )
        features_df["weight_percentile"] = features_df.groupby("race_id")[
            "horse_weight_kg"
        ].rank(pct=True)
        features_df["odds_percentile"] = features_df.groupby("race_id")[
            "odds_decimal"
        ].rank(pct=True, ascending=False)
        features_df["age_percentile"] = features_df.groupby("race_id")[
            "horse_age"
        ].rank(pct=True)

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

        # Distance-based features (if distance is numeric)
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

        # Final feature selection
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
            "draw_percentile",
            "weight_percentile",
            "odds_percentile",
            "age_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "jockey_win_pct",
            "trainer_win_pct",
            "jockey_performance",
            "trainer_performance",
            "odds_value",
            "market_efficiency",
            "distance_category",
            "class_numeric",
        ]

        # Ensure all columns exist
        for col in feature_columns:
            if col not in features_df.columns:
                features_df[col] = 0.0

        # Convert percentages and fill NaN values
        features_df["jockey_win_pct"] = features_df["jockey_win_pct"] / 100.0
        features_df["trainer_win_pct"] = features_df["trainer_win_pct"] / 100.0
        features_df = features_df.fillna(0.0)

        # Select final features
        final_features_df = features_df[
            feature_columns + ["race_id", "horse_name"]
        ].copy()

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

        for name, model in self.predictor.model_configs.items():
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

        # Test different voting strategies
        voting_strategies = ["soft", "hard"]
        voting_results = {}

        for strategy in voting_strategies:
            logger.info(f"   Testing {strategy} voting...")

            voting_clf = VotingClassifier(estimators=models_for_voting, voting=strategy)

            cv_scores = cross_val_score(
                voting_clf, X_scaled, y, cv=cv, scoring="roc_auc"
            )
            voting_results[strategy] = {
                "mean_auc": cv_scores.mean(),
                "std_auc": cv_scores.std(),
                "scores": cv_scores.tolist(),
            }

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

        optimization_results = {
            "individual_scores": individual_scores,
            "voting_results": voting_results,
            "optimized_weights": normalized_weights,
            "cv_folds": cv_folds,
            "total_samples": len(X),
            "positive_samples": y.sum(),
            "scaler": scaler,
        }

        logger.info("✅ Ensemble optimization completed")
        logger.info("📊 Optimized weights:")
        for name, weight in normalized_weights.items():
            logger.info(f"   {name}: {weight:.4f}")

        return optimization_results

    def train_optimized_ensemble(self, save_model: bool = True) -> Dict[str, Any]:
        """Train the optimized ensemble model."""
        logger.info("🚀 Starting optimized ensemble training...")

        # Load training data
        df, target = self.load_training_data()

        # Engineer features
        features_df, feature_columns = self.engineer_features(df)
        X = features_df[feature_columns]

        # Optimize ensemble
        optimization_results = self.optimize_ensemble_weights(X, target)

        # Train final ensemble with optimized weights
        logger.info("🎯 Training final optimized ensemble...")

        # Use V201EnsemblePredictor but with optimized configuration
        scaler = optimization_results["scaler"]
        X_scaled = scaler.transform(X)

        # Train individual models
        trained_models = {}
        for name, model in self.predictor.model_configs.items():
            logger.info(f"   Training final {name}...")
            model.fit(X_scaled, target)
            trained_models[name] = model

        # Create optimized ensemble
        weights = list(optimization_results["optimized_weights"].values())
        weighted_ensemble = VotingClassifier(
            estimators=list(trained_models.items()), voting="soft", weights=weights
        )
        weighted_ensemble.fit(X_scaled, target)

        # Final evaluation
        final_evaluation = self.evaluate_model(weighted_ensemble, X_scaled, target)

        # Prepare final model data
        final_model_data = {
            "ensemble_model": weighted_ensemble,
            "individual_models": trained_models,
            "scaler": scaler,
            "feature_names": feature_columns,
            "optimization_results": optimization_results,
            "evaluation_results": final_evaluation,
            "training_metadata": {
                "training_date": datetime.now().isoformat(),
                "training_samples": len(X),
                "feature_count": len(feature_columns),
                "target_distribution": target.value_counts().to_dict(),
                "model_version": "v2.04_optimized",
            },
        }

        if save_model:
            model_path = self.save_optimized_model(final_model_data)
            logger.info(f"💾 Optimized model saved to: {model_path}")

        # Generate training report
        self.generate_training_report(final_model_data)

        return final_model_data

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

    def save_optimized_model(self, model_data: Dict[str, Any]) -> str:
        """Save the optimized model."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"optimized_ensemble_v204_{timestamp}.joblib"
        model_path = self.models_dir / model_filename

        joblib.dump(model_data, model_path)

        # Also save a latest version
        latest_path = self.models_dir / "optimized_ensemble_latest.joblib"
        joblib.dump(model_data, latest_path)

        return str(model_path)

    def generate_training_report(self, model_data: Dict[str, Any]) -> None:
        """Generate comprehensive training report."""
        logger.info("📋 Generating training report...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.models_dir / f"training_report_{timestamp}.json"

        # Prepare report data
        report = {
            "training_summary": model_data["training_metadata"],
            "optimization_results": {
                "individual_scores": model_data["optimization_results"][
                    "individual_scores"
                ],
                "voting_results": model_data["optimization_results"]["voting_results"],
                "optimized_weights": model_data["optimization_results"][
                    "optimized_weights"
                ],
            },
            "evaluation_results": {
                "auc_score": model_data["evaluation_results"]["auc_score"],
                "accuracy": model_data["evaluation_results"]["accuracy"],
                "precision": model_data["evaluation_results"]["precision"],
                "recall": model_data["evaluation_results"]["recall"],
                "f1_score": model_data["evaluation_results"]["f1_score"],
            },
            "feature_importance": self.get_feature_importance(model_data),
            "model_configuration": {
                "ensemble_voting": "soft",
                "cross_validation_folds": model_data["optimization_results"][
                    "cv_folds"
                ],
                "feature_count": len(model_data["feature_names"]),
                "model_types": list(model_data["individual_models"].keys()),
            },
        }

        # Save report
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📄 Training report saved to: {report_path}")

        # Print summary
        self.print_training_summary(report)

    def get_feature_importance(self, model_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from trained models."""
        feature_names = model_data["feature_names"]

        # Get importance from Random Forest (if available)
        if "random_forest" in model_data["individual_models"]:
            rf_model = model_data["individual_models"]["random_forest"]
            if hasattr(rf_model, "feature_importances_"):
                importance_dict = {}
                for i, importance in enumerate(rf_model.feature_importances_):
                    if i < len(feature_names):
                        importance_dict[feature_names[i]] = float(importance)
                return dict(
                    sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                )

        return {}

    def print_training_summary(self, report: Dict[str, Any]) -> None:
        """Print formatted training summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🏆 OPTIMIZED ENSEMBLE TRAINING COMPLETE")
        logger.info("=" * 60)

        # Training summary
        metadata = report["training_summary"]
        logger.info(f"📅 Training Date: {metadata['training_date']}")
        logger.info(f"📊 Training Samples: {metadata['training_samples']}")
        logger.info(f"🎯 Features Used: {metadata['feature_count']}")
        logger.info(f"🏆 Winners: {metadata['target_distribution'].get(1, 0)}")
        logger.info(f"🥈 Non-winners: {metadata['target_distribution'].get(0, 0)}")

        # Performance metrics
        eval_results = report["evaluation_results"]
        logger.info("\n📈 PERFORMANCE METRICS:")
        logger.info(f"   AUC Score: {eval_results['auc_score']:.4f}")
        logger.info(f"   Accuracy: {eval_results['accuracy']:.4f}")
        logger.info(f"   Precision: {eval_results['precision']:.4f}")
        logger.info(f"   Recall: {eval_results['recall']:.4f}")
        logger.info(f"   F1-Score: {eval_results['f1_score']:.4f}")

        # Optimized weights
        weights = report["optimization_results"]["optimized_weights"]
        logger.info("\n⚖️ OPTIMIZED WEIGHTS:")
        for model, weight in weights.items():
            logger.info(f"   {model}: {weight:.4f}")

        # Top features
        feature_importance = report.get("feature_importance", {})
        if feature_importance:
            logger.info("\n🔝 TOP FEATURES:")
            for i, (feature, importance) in enumerate(
                list(feature_importance.items())[:10]
            ):
                logger.info(f"   {i+1:2d}. {feature:<25} {importance:.4f}")

        logger.info("\n🎉 Model is ready for production use!")
        logger.info("=" * 60)


def main():
    """Main training function."""
    logger.info("🏇 Starting Enhanced Ensemble Training with Results Database...")

    try:
        # Initialize trainer
        trainer = EnhancedEnsembleTrainer()

        # Train optimized ensemble
        model_data = trainer.train_optimized_ensemble(save_model=True)

        logger.info("✅ Enhanced ensemble training completed successfully!")

        return model_data

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    if result:
        print("\n🎉 Training completed successfully!")
    else:
        print("\n❌ Training failed!")
        sys.exit(1)
