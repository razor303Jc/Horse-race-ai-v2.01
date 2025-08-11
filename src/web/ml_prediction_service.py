#!/usr/bin/env python3
"""
🚀 ML Prediction Service for Horse Racing API

Standalone ML prediction module for integration with existing API server.
Loads Priority 3A ensemble models and provides prediction functions.

Features:
- Load ensemble models with 98.86% AUC performance
- Feature engineering pipeline
- Single horse predictions
- Full race predictions
- Model health monitoring
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)


class MLPredictionService:
    """ML Prediction service for horse racing."""

    def __init__(self, models_dir: str = "/app/trained_models/priority_3a"):
        """Initialize the ML prediction service."""
        self.models_dir = Path(models_dir)
        self.ensemble_model = None
        self.label_encoders = {}
        self.model_metadata = {}
        self.model_timestamp = None
        self.is_loaded = False

        # Load models on initialization
        self.load_models()

    def load_models(self) -> bool:
        """Load the trained ensemble model and encoders."""
        try:
            if not self.models_dir.exists():
                logger.error(f"Models directory not found: {self.models_dir}")
                return False

            # Find the most recent ensemble model
            ensemble_files = list(self.models_dir.glob("ensemble_*.joblib"))
            if not ensemble_files:
                logger.error("No ensemble model files found")
                return False

            latest_ensemble = max(ensemble_files, key=lambda x: x.stat().st_mtime)
            self.model_timestamp = latest_ensemble.stem.split("_")[-1]

            logger.info(f"Loading ensemble model: {latest_ensemble}")
            self.ensemble_model = joblib.load(latest_ensemble)

            # Load encoders
            encoders_file = self.models_dir / f"encoders_{self.model_timestamp}.joblib"
            if encoders_file.exists():
                self.label_encoders = joblib.load(encoders_file)
                logger.info(f"Loaded encoders: {encoders_file}")
            else:
                self.label_encoders = {}
                logger.warning("No encoders file found, using empty encoders")

            # Load metadata
            metadata_file = self.models_dir / f"results_{self.model_timestamp}.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    self.model_metadata = json.load(f)
                logger.info(f"Loaded metadata: {metadata_file}")
            else:
                self.model_metadata = {}
                logger.warning("No metadata file found")

            self.is_loaded = True
            logger.info("✅ ML models loaded successfully")
            logger.info(
                f"   Ensemble components: {[name for name, _ in self.ensemble_model.estimators]}"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {e}")
            self.is_loaded = False
            return False

    def engineer_features(self, horse_data: Dict) -> pd.DataFrame:
        """Engineer features for prediction matching training pipeline."""

        # Convert to DataFrame
        df = pd.DataFrame([horse_data])

        # Basic features with defaults
        df["horse_age"] = df.get("horse_age", 5)
        df["draw"] = df.get("draw", 8)
        df["win_odds"] = df.get("win_odds", 5.0)
        df["place_odds"] = df.get("place_odds", df.get("win_odds", 5.0) / 2)
        df["barrier"] = df.get("barrier", df.get("draw", 8))
        df["margin"] = df.get("margin", 0.0)
        df["horse_weight_kg"] = df.get("horse_weight_kg", 485)
        df["handicap_weight"] = df.get("handicap_weight", 58)

        # Performance stats with defaults
        df["jockey_win_pct"] = df.get("jockey_win_pct", 10.0)
        df["jockey_place_pct"] = df.get("jockey_place_pct", 25.0)
        df["trainer_win_pct"] = df.get("trainer_win_pct", 10.0)
        df["trainer_place_pct"] = df.get("trainer_place_pct", 25.0)

        # Ensure numeric types
        for col in [
            "horse_age",
            "draw",
            "win_odds",
            "place_odds",
            "barrier",
            "margin",
            "horse_weight_kg",
            "handicap_weight",
            "jockey_win_pct",
            "jockey_place_pct",
            "trainer_win_pct",
            "trainer_place_pct",
        ]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fill any remaining NaN values
        df = df.fillna(
            {
                "horse_age": 5,
                "draw": 8,
                "win_odds": 5.0,
                "place_odds": 2.5,
                "barrier": 8,
                "margin": 0.0,
                "horse_weight_kg": 485,
                "handicap_weight": 58,
                "jockey_win_pct": 10.0,
                "jockey_place_pct": 25.0,
                "trainer_win_pct": 10.0,
                "trainer_place_pct": 25.0,
            }
        )

        # Odds-based features
        df["is_favorite"] = (df["win_odds"] <= 3.0).astype(int)
        df["high_odds"] = (df["win_odds"] >= 10.0).astype(int)
        df["log_odds"] = np.log(df["win_odds"].clip(lower=1.01))
        df["implied_prob"] = 1 / df["win_odds"].clip(lower=1.01)

        # Safe ratio calculations
        place_odds_safe = df["place_odds"].fillna(df["win_odds"]).clip(lower=0.1)
        df["odds_ratio"] = df["win_odds"] / place_odds_safe

        weight_denom = (
            df["handicap_weight"].fillna(df["horse_weight_kg"]).clip(lower=30)
        )
        df["weight_ratio"] = df["horse_weight_kg"] / weight_denom

        # Age and position features
        df["age_squared"] = df["horse_age"] ** 2
        df["draw_squared"] = df["draw"] ** 2
        df["barrier_squared"] = df["barrier"] ** 2

        # Combined performance features
        df["jockey_trainer_combo"] = df["jockey_win_pct"] * df["trainer_win_pct"]
        df["combined_place_pct"] = (
            df["jockey_place_pct"] + df["trainer_place_pct"]
        ) / 2

        # Categorical encoding
        course = horse_data.get("course", "Unknown")
        if self.label_encoders and "course" in self.label_encoders:
            try:
                df["course_encoded"] = self.label_encoders["course"].transform([course])
            except ValueError:
                # Handle unseen course
                df["course_encoded"] = 0
        else:
            df["course_encoded"] = 0

        # Select feature columns (matching training)
        feature_columns = [
            "horse_age",
            "draw",
            "win_odds",
            "place_odds",
            "barrier",
            "margin",
            "horse_weight_kg",
            "handicap_weight",
            "jockey_win_pct",
            "jockey_place_pct",
            "trainer_win_pct",
            "trainer_place_pct",
            "is_favorite",
            "high_odds",
            "log_odds",
            "implied_prob",
            "odds_ratio",
            "weight_ratio",
            "age_squared",
            "draw_squared",
            "barrier_squared",
            "jockey_trainer_combo",
            "combined_place_pct",
            "course_encoded",
        ]

        return df[feature_columns]

    def predict_horse(self, horse_data: Dict) -> Dict:
        """Predict win probability for a single horse."""

        if not self.is_loaded:
            return {"success": False, "error": "Models not loaded"}

        try:
            # Engineer features
            features = self.engineer_features(horse_data)

            # Make ensemble prediction
            win_probability = self.ensemble_model.predict_proba(features.values)[0, 1]
            win_prediction = self.ensemble_model.predict(features.values)[0]

            # Get individual model predictions
            model_components = {}
            for name, model in self.ensemble_model.estimators:
                component_prob = model.predict_proba(features.values)[0, 1]
                model_components[name] = float(component_prob)

            # Generate insights
            confidence_level = self._get_confidence_level(win_probability)
            implied_odds = 1 / win_probability if win_probability > 0 else float("inf")
            win_odds = horse_data.get("win_odds", 5.0)
            recommendation = self._get_betting_recommendation(win_probability, win_odds)

            return {
                "success": True,
                "horse_name": horse_data.get("horse_name", "Unknown"),
                "win_probability": float(win_probability),
                "win_prediction": bool(win_prediction),
                "confidence_level": confidence_level,
                "implied_odds": float(implied_odds),
                "recommendation": recommendation,
                "model_components": model_components,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"success": False, "error": str(e)}

    def predict_race(self, horses: List[Dict], race_info: Dict = None) -> Dict:
        """Predict win probabilities for all horses in a race."""

        if not self.is_loaded:
            return {"success": False, "error": "Models not loaded"}

        try:
            predictions = []

            # Predict for each horse
            for horse in horses:
                prediction = self.predict_horse(horse)
                if prediction["success"]:
                    predictions.append(prediction)

            # Sort by win probability
            predictions.sort(key=lambda x: x["win_probability"], reverse=True)

            # Generate race summary
            if predictions:
                total_prob = sum(p["win_probability"] for p in predictions)
                favorite = predictions[0]
                outsider = predictions[-1]

                race_summary = {
                    "favorite": f"{favorite['horse_name']} ({favorite['win_probability']:.1%})",
                    "outsider": f"{outsider['horse_name']} ({outsider['win_probability']:.1%})",
                    "field_size": len(predictions),
                    "total_probability": f"{total_prob:.1%}",
                    "market_efficiency": (
                        "Efficient" if 0.95 <= total_prob <= 1.05 else "Inefficient"
                    ),
                }
            else:
                race_summary = {"error": "No successful predictions"}

            return {
                "success": True,
                "predictions": predictions,
                "race_summary": race_summary,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Race prediction failed: {e}")
            return {"success": False, "error": str(e)}

    def get_model_status(self) -> Dict:
        """Get model health and performance information."""

        if not self.is_loaded:
            return {"status": "unhealthy", "message": "Models not loaded"}

        try:
            status_info = {
                "status": "healthy",
                "model_timestamp": self.model_timestamp,
                "ensemble_components": [
                    name for name, _ in self.ensemble_model.estimators
                ],
                "feature_count": 24,
                "encoders_loaded": len(self.label_encoders),
                "metadata_available": bool(self.model_metadata),
                "startup_time": datetime.now().isoformat(),
            }

            if self.model_metadata:
                # Add performance metrics
                ensemble_perf = self.model_metadata.get("ensemble_performance", {})
                if ensemble_perf:
                    test_metrics = ensemble_perf.get("test_metrics", {})
                    status_info["ensemble_auc"] = test_metrics.get("roc_auc", 0)
                    status_info["ensemble_accuracy"] = test_metrics.get("accuracy", 0)

                # Add individual model performance
                model_performance = self.model_metadata.get("model_performance", {})
                status_info["model_performance"] = {
                    name: perf.get("test_metrics", {}).get("roc_auc", 0)
                    for name, perf in model_performance.items()
                }

            return status_info

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {"status": "error", "message": str(e)}

    def _get_confidence_level(self, probability: float) -> str:
        """Determine confidence level based on probability."""
        if probability >= 0.8 or probability <= 0.1:
            return "Very High"
        elif probability >= 0.7 or probability <= 0.2:
            return "High"
        elif probability >= 0.6 or probability <= 0.3:
            return "Medium"
        else:
            return "Low"

    def _get_betting_recommendation(self, probability: float, odds: float) -> str:
        """Generate betting recommendation based on probability and odds."""
        implied_prob = 1 / odds if odds > 0 else 0
        value = probability - implied_prob

        if value > 0.1:
            return f"Strong Value Bet - Model: {probability:.1%} vs Market: {implied_prob:.1%}"
        elif value > 0.05:
            return f"Value Bet - Slight edge detected"
        elif value > -0.05:
            return f"Fair Odds - No significant edge"
        elif value > -0.1:
            return f"Overpriced - Market odds too short"
        else:
            return f"Avoid - Significantly overpriced"


# Global ML service instance
ml_service = None


def get_ml_service() -> MLPredictionService:
    """Get or create the global ML service instance."""
    global ml_service
    if ml_service is None:
        ml_service = MLPredictionService()
    return ml_service


# Convenience functions for API integration
def predict_horse(horse_data: Dict) -> Dict:
    """Predict win probability for a single horse."""
    service = get_ml_service()
    return service.predict_horse(horse_data)


def predict_race(horses: List[Dict], race_info: Dict = None) -> Dict:
    """Predict win probabilities for all horses in a race."""
    service = get_ml_service()
    return service.predict_race(horses, race_info)


def get_model_status() -> Dict:
    """Get model health and performance information."""
    service = get_ml_service()
    return service.get_model_status()


if __name__ == "__main__":
    # Test the ML service
    print("🚀 Testing ML Prediction Service...")

    service = MLPredictionService()

    # Test single horse prediction
    test_horse = {
        "horse_name": "Test Runner",
        "horse_age": 5,
        "draw": 3,
        "win_odds": 4.5,
        "jockey_win_pct": 15.0,
        "trainer_win_pct": 18.0,
        "course": "Flemington",
    }

    result = service.predict_horse(test_horse)
    print("Test prediction result:", result)

    # Test model status
    status = service.get_model_status()
    print("Model status:", status)
