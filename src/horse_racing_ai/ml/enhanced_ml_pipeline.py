#!/usr/bin/env python3
"""
Enhanced ML Pipeline Integration
===============================

Integrates the v2.01-inspired ensemble predictor with the v2.03 pipeline.
Provides enhanced prediction capabilities with 4-model ensemble approach.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np
import structlog

from .v2_01_ensemble_predictor import (
    V201EnsemblePredictor,
    EnsembleResults,
    EnsemblePrediction,
)

logger = structlog.get_logger(__name__)


class EnhancedMLPipeline:
    """Enhanced ML pipeline that integrates v2.01 ensemble approach with v2.03."""

    def __init__(
        self,
        models_dir: str = "/app/models",
        cache_dir: str = "/app/ml_cache",
        enable_ensemble: bool = True,
    ):
        """
        Initialize enhanced ML pipeline.

        Args:
            models_dir: Directory for storing trained models
            cache_dir: Directory for ML cache and intermediate results
            enable_ensemble: Whether to use ensemble prediction (recommended)
        """
        self.models_dir = Path(models_dir)
        self.cache_dir = Path(cache_dir)
        self.enable_ensemble = enable_ensemble

        # Initialize ensemble predictor
        self.ensemble_predictor = V201EnsemblePredictor(str(self.models_dir))

        # Pipeline state
        self.is_trained = False
        self.training_metadata = {}
        self.last_prediction_time = None

        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_and_prepare_data(
        self, data_dir: str = "/app/data/preprocessed"
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Load and prepare training data from v2.03 preprocessed files."""
        logger.info("Loading training data from v2.03 pipeline...")

        data_path = Path(data_dir)

        # Load horses data
        horses_file = data_path / "cards_data/horses/horses.csv"
        if not horses_file.exists():
            raise FileNotFoundError(f"Horses data not found: {horses_file}")

        horses_df = pd.read_csv(horses_file)
        logger.info(f"Loaded {len(horses_df)} horse records")

        # Load additional data sources if available
        data_sources = {
            "jockeys": data_path / "cards_data/jockeys_stats/jockeys_stats.csv",
            "trainers": data_path / "cards_data/trainers_stats/trainers_stats.csv",
            "races": data_path / "cards_data/races/races.csv",
            "records": data_path / "cards_data/records/records.csv",
        }

        additional_data = {}
        for source_name, source_path in data_sources.items():
            if source_path.exists():
                additional_data[source_name] = pd.read_csv(source_path)
                logger.info(
                    f"Loaded {len(additional_data[source_name])} {source_name} records"
                )

        # Create target variable (win probability based on performance)
        # This is a simplified approach - in production would use actual race results
        target = self._create_training_target(horses_df)

        return horses_df, target

    def _create_training_target(self, horses_df: pd.DataFrame) -> pd.Series:
        """Create training target from horse performance data."""
        # Multi-factor target creation based on v2.01 analysis

        # Factor 1: Win percentage (primary factor)
        win_factor = horses_df["Percentage_wins"].fillna(0)

        # Factor 2: Recent form (if available)
        form_factor = horses_df["Percentage_placed"].fillna(0)

        # Factor 3: Experience vs success ratio
        experience_factor = horses_df["Total_races"].fillna(0) / (
            horses_df["age"].fillna(5) + 1
        )

        # Composite score
        composite_score = 0.5 * win_factor + 0.3 * form_factor + 0.2 * experience_factor

        # Create binary target (top performers vs others)
        threshold = composite_score.quantile(0.6)  # Top 40% as winners
        target = (composite_score > threshold).astype(int)

        logger.info(
            f"Created target with distribution: {target.value_counts().to_dict()}"
        )
        return target

    def train_enhanced_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """Train the enhanced ensemble models."""
        if self.is_trained and not force_retrain:
            logger.info("Models already trained. Use force_retrain=True to retrain.")
            return self.training_metadata

        logger.info("🚀 Starting enhanced ML training...")

        # Load data
        X_data, y_data = self.load_and_prepare_data()

        # Train ensemble
        training_results = self.ensemble_predictor.train_ensemble(X_data, y_data)

        if not training_results:
            raise RuntimeError("Ensemble training failed")

        # Save training metadata
        self.training_metadata = {
            "training_timestamp": datetime.now().isoformat(),
            "data_size": len(X_data),
            "feature_count": len(self.ensemble_predictor.feature_names),
            "target_distribution": y_data.value_counts().to_dict(),
            "model_performance": training_results,
            "ensemble_enabled": self.enable_ensemble,
        }

        # Save metadata to cache
        metadata_file = (
            self.cache_dir
            / f"training_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(metadata_file, "w") as f:
            json.dump(self.training_metadata, f, indent=2)

        self.is_trained = True
        logger.info(
            f"✅ Enhanced ML training completed. Metadata saved to {metadata_file}"
        )

        return training_results

    def predict_race(
        self,
        race_data: pd.DataFrame,
        race_id: str = None,
        include_confidence: bool = True,
    ) -> Dict[str, Any]:
        """
        Make predictions for a race using enhanced ensemble.

        Args:
            race_data: DataFrame with horse data for the race
            race_id: Optional race identifier
            include_confidence: Whether to include confidence metrics

        Returns:
            Dictionary with predictions and metadata
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")

        logger.info(f"Making enhanced predictions for race {race_id or 'UNKNOWN'}")

        # Make ensemble predictions
        results = self.ensemble_predictor.predict_race(race_data, race_id)

        # Convert to v2.03 compatible format
        predictions = []
        for pred in results.predictions:
            prediction_dict = {
                "horse_name": pred.horse_name,
                "ml_rank": pred.ml_rank,
                "ensemble_probability": pred.ensemble_prob,
                "individual_models": {
                    "random_forest": pred.rf_prob,
                    "gradient_boosting": pred.gb_prob,
                    "neural_network": pred.nn_prob,
                    "logistic_regression": pred.lr_prob,
                },
                "confidence": pred.confidence,
                "value_bet": pred.value_bet,
                "rating_scores": {
                    "form_rating": pred.recent_form_rating,
                    "speed_rating": pred.speed_rating,
                    "class_rating": pred.class_rating,
                },
            }

            if include_confidence:
                prediction_dict["prediction_factors"] = self._get_prediction_factors(
                    pred
                )

            predictions.append(prediction_dict)

        # Create response
        response = {
            "race_id": race_id or "UNKNOWN",
            "prediction_timestamp": datetime.now().isoformat(),
            "predictions": predictions,
            "race_summary": {
                "horse_count": len(predictions),
                "high_confidence_predictions": results.confidence_distribution.get(
                    "high", 0
                ),
                "value_bets_identified": results.value_bets_count,
                "top_contenders": [p["horse_name"] for p in predictions[:3]],
            },
            "model_info": {
                "ensemble_models": list(self.ensemble_predictor.models.keys()),
                "feature_count": len(self.ensemble_predictor.feature_names),
                "training_date": self.training_metadata.get("training_timestamp"),
                "v201_compatible": True,
            },
        }

        if include_confidence:
            response["feature_importance"] = [
                {
                    "feature": feat.feature_name,
                    "importance": feat.importance_score,
                    "rank": feat.rank,
                }
                for feat in results.feature_importance
            ]

        self.last_prediction_time = datetime.now()

        # Cache prediction result
        self._cache_prediction_result(response)

        return response

    def _get_prediction_factors(self, prediction: EnsemblePrediction) -> List[str]:
        """Get human-readable prediction factors."""
        factors = []

        if prediction.ensemble_prob > 0.7:
            factors.append("Strong ensemble consensus")
        if prediction.confidence > 0.8:
            factors.append("High model agreement")
        if prediction.value_bet:
            factors.append("Value betting opportunity")
        if prediction.recent_form_rating > 25:
            factors.append("Strong recent form")
        if prediction.speed_rating > 20:
            factors.append("Good speed rating")

        return factors

    def _cache_prediction_result(self, result: Dict[str, Any]) -> None:
        """Cache prediction result for analysis."""
        try:
            cache_file = (
                self.cache_dir
                / f"prediction_{result['race_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(cache_file, "w") as f:
                json.dump(result, f, indent=2)
            logger.debug(f"Cached prediction to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache prediction: {e}")

    def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive model status."""
        status = {
            "is_trained": self.is_trained,
            "ensemble_enabled": self.enable_ensemble,
            "models_directory": str(self.models_dir),
            "cache_directory": str(self.cache_dir),
            "last_prediction_time": (
                self.last_prediction_time.isoformat()
                if self.last_prediction_time
                else None
            ),
        }

        if self.is_trained:
            status.update(
                {
                    "ensemble_models": list(self.ensemble_predictor.models.keys()),
                    "feature_count": len(self.ensemble_predictor.feature_names),
                    "training_metadata": self.training_metadata,
                }
            )

        return status

    def export_model_for_production(self, export_path: str = None) -> str:
        """Export trained model for production deployment."""
        if not self.is_trained:
            raise ValueError("No trained model to export")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if export_path is None:
            export_path = self.models_dir / f"production_ensemble_{timestamp}.joblib"
        else:
            export_path = Path(export_path)

        # Save ensemble model
        model_path = self.ensemble_predictor.save_ensemble(str(export_path))

        # Create production metadata
        production_metadata = {
            "model_path": model_path,
            "export_timestamp": datetime.now().isoformat(),
            "model_type": "v2.01_enhanced_ensemble",
            "version": "2.03",
            "training_metadata": self.training_metadata,
            "deployment_ready": True,
        }

        metadata_path = export_path.parent / f"production_metadata_{timestamp}.json"
        with open(metadata_path, "w") as f:
            json.dump(production_metadata, f, indent=2)

        logger.info(f"✅ Production model exported to {model_path}")
        logger.info(f"✅ Production metadata saved to {metadata_path}")

        return model_path

    def compare_with_v2_01_archive(
        self, archive_predictions_file: str
    ) -> Dict[str, Any]:
        """Compare current ensemble with v2.01 archived predictions."""
        try:
            archive_df = pd.read_csv(archive_predictions_file)

            comparison = {
                "archive_file": archive_predictions_file,
                "archive_records": len(archive_df),
                "comparison_timestamp": datetime.now().isoformat(),
                "feature_analysis": {},
                "model_compatibility": True,
            }

            # Analyze feature compatibility
            if "rf_prob" in archive_df.columns:
                comparison["feature_analysis"]["has_random_forest"] = True
            if "gb_prob" in archive_df.columns:
                comparison["feature_analysis"]["has_gradient_boosting"] = True
            if "nn_prob" in archive_df.columns:
                comparison["feature_analysis"]["has_neural_network"] = True
            if "lr_prob" in archive_df.columns:
                comparison["feature_analysis"]["has_logistic_regression"] = True

            # Analyze prediction distribution
            if "ensemble_prob" in archive_df.columns:
                comparison["archive_ensemble_stats"] = {
                    "mean_probability": float(archive_df["ensemble_prob"].mean()),
                    "std_probability": float(archive_df["ensemble_prob"].std()),
                    "min_probability": float(archive_df["ensemble_prob"].min()),
                    "max_probability": float(archive_df["ensemble_prob"].max()),
                }

            logger.info(f"✅ Compared with v2.01 archive: {comparison}")
            return comparison

        except Exception as e:
            logger.error(f"❌ Failed to compare with archive: {e}")
            return {"error": str(e)}
