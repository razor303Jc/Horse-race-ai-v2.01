#!/usr/bin/env python3
"""
Enhanced Ensemble ML Predictor (v2.01 Inspired)
==============================================

Implements the ensemble prediction approach discovered in v2.01 archive:
- 4-model ensemble: Random Forest, Gradient Boosting, Neural Network, Logistic Regression
- Individual model probabilities with ensemble aggregation
- Confidence scoring and value betting analysis
- Feature importance tracking with top features: draw, rating_rank, market_share
"""

import logging
import json
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import structlog
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = structlog.get_logger(__name__)


@dataclass
class EnsemblePrediction:
    """Single horse prediction result from ensemble."""

    horse_name: str
    race_id: str
    morning_line_odds: float
    recent_form_rating: float
    speed_rating: float
    class_rating: float
    rf_prob: float  # Random Forest probability
    gb_prob: float  # Gradient Boosting probability
    nn_prob: float  # Neural Network probability
    lr_prob: float  # Logistic Regression probability
    ensemble_prob: float  # Final ensemble probability
    ml_rank: int  # ML-based ranking
    odds_rank: int  # Odds-based ranking
    confidence: float  # Prediction confidence (0-1)
    value_bet: bool  # Whether this is a value betting opportunity


@dataclass
class FeatureImportance:
    """Feature importance analysis."""

    feature_name: str
    importance_score: float
    rank: int


@dataclass
class EnsembleResults:
    """Complete ensemble prediction results."""

    predictions: List[EnsemblePrediction]
    feature_importance: List[FeatureImportance]
    model_performance: Dict[str, Dict[str, float]]
    confidence_distribution: Dict[str, int]
    value_bets_count: int


class V201EnsemblePredictor:
    """Enhanced ensemble predictor based on v2.01 approach."""

    def __init__(self, models_dir: str = "/app/models"):
        self.models_dir = Path(models_dir)
        self.models = {}
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False

        # Model configurations (based on v2.01 analysis)
        self.model_configs = {
            "random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                max_features="sqrt",
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                min_samples_split=10,
                min_samples_leaf=5,
                subsample=0.8,
                random_state=42,
            ),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation="relu",
                solver="adam",
                alpha=0.001,
                learning_rate="adaptive",
                max_iter=500,
                random_state=42,
                early_stopping=True,
            ),
            "logistic_regression": LogisticRegression(
                random_state=42, max_iter=1000, solver="lbfgs"
            ),
        }

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training and prediction."""
        logger.info("Preparing features for ensemble prediction...")

        features = data.copy()

        # Core numeric features (based on v2.01 analysis)
        numeric_columns = [
            "age",
            "Total_races",
            "Wins",
            "Percentage_wins",
            "placed",
            "Percentage_placed",
            "Flat_AW_races",
            "Flat_AW_wins",
            "Flat_AW_rate",
            "Flat_AW_placed",
            "Flat_AW_placed_rate",
            "Flat_Turf_races",
            "Flat_Turf_wins",
            "Flat_Turf_rate",
            "Flat_Turf_placed",
            "Flat_Turf_placed_rate",
            "Chase_races",
            "Chase_wins",
            "Chase_rate",
            "Chase_placed",
            "Chase_placed_rate",
            "Hurdle_races",
            "Hurdle_wins",
            "Hurdle_rate",
            "Hurdle_placed",
            "Hurdle_placed_rate",
        ]

        # Select only numeric features that exist
        available_features = [col for col in numeric_columns if col in features.columns]
        features_df = features[available_features].copy()

        # Convert to numeric, coercing errors to NaN
        for col in features_df.columns:
            features_df[col] = pd.to_numeric(features_df[col], errors="coerce")

        # Handle missing values
        features_df = features_df.fillna(0)

        # Engineer additional features (based on v2.01 insights)
        if "Wins" in features_df.columns and "Total_races" in features_df.columns:
            features_df["win_rate"] = features_df["Wins"] / (
                features_df["Total_races"] + 1
            )

        if "placed" in features_df.columns and "Total_races" in features_df.columns:
            features_df["place_rate"] = features_df["placed"] / (
                features_df["Total_races"] + 1
            )

        # Form-based features
        if (
            "Percentage_wins" in features_df.columns
            and "Percentage_placed" in features_df.columns
        ):
            features_df["form_consistency"] = (
                features_df["Percentage_placed"] - features_df["Percentage_wins"]
            )

        # Class and distance features
        if (
            "Flat_Turf_rate" in features_df.columns
            and "Flat_AW_rate" in features_df.columns
        ):
            features_df["surface_preference"] = (
                features_df["Flat_Turf_rate"] - features_df["Flat_AW_rate"]
            )

        # Age-based features
        if "age" in features_df.columns:
            features_df["age_squared"] = features_df["age"] ** 2
            features_df["experience_age_ratio"] = features_df["Total_races"] / (
                features_df["age"] + 1
            )

        # Ensure all values are numeric
        features_df = features_df.select_dtypes(include=[np.number])

        self.feature_names = list(features_df.columns)
        logger.info(
            f"Prepared {len(self.feature_names)} features: {self.feature_names[:10]}..."
        )

        return features_df

    def train_ensemble(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train the ensemble model with individual model tracking."""
        logger.info("🚀 Training ensemble model (v2.01 approach)...")

        # Prepare data
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train individual models
        model_results = {}
        trained_estimators = []

        for name, model in self.model_configs.items():
            logger.info(f"Training {name}...")

            try:
                # Train model
                model.fit(X_train, y_train)

                # Evaluate model
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]

                # Calculate metrics
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, zero_division=0),
                    "recall": recall_score(y_test, y_pred, zero_division=0),
                    "f1_score": f1_score(y_test, y_pred, zero_division=0),
                    "roc_auc": roc_auc_score(y_test, y_pred_proba),
                }

                # Cross-validation
                cv_scores = cross_val_score(
                    model, X_train, y_train, cv=5, scoring="roc_auc"
                )
                metrics["cv_mean"] = cv_scores.mean()
                metrics["cv_std"] = cv_scores.std()

                model_results[name] = metrics
                trained_estimators.append((name, model))
                self.models[name] = model

                logger.info(
                    f"✅ {name}: AUC={metrics['roc_auc']:.4f}, Accuracy={metrics['accuracy']:.4f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {name}: {e}")
                continue

        # Create ensemble
        if len(trained_estimators) >= 2:
            self.ensemble_model = VotingClassifier(
                estimators=trained_estimators,
                voting="soft",  # Use probability-based voting
            )
            self.ensemble_model.fit(X_train, y_train)

            # Evaluate ensemble
            ensemble_pred = self.ensemble_model.predict(X_test)
            ensemble_proba = self.ensemble_model.predict_proba(X_test)[:, 1]

            ensemble_metrics = {
                "accuracy": accuracy_score(y_test, ensemble_pred),
                "precision": precision_score(y_test, ensemble_pred, zero_division=0),
                "recall": recall_score(y_test, ensemble_pred, zero_division=0),
                "f1_score": f1_score(y_test, ensemble_pred, zero_division=0),
                "roc_auc": roc_auc_score(y_test, ensemble_proba),
            }

            model_results["ensemble"] = ensemble_metrics
            self.is_trained = True

            logger.info(
                f"✅ Ensemble: AUC={ensemble_metrics['roc_auc']:.4f}, Accuracy={ensemble_metrics['accuracy']:.4f}"
            )
        else:
            logger.error("❌ Not enough models trained for ensemble")
            return {}

        return model_results

    def predict_race(
        self, race_data: pd.DataFrame, race_id: str = None
    ) -> EnsembleResults:
        """Make ensemble predictions for a race."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        logger.info(f"Making ensemble predictions for {len(race_data)} horses...")

        # Prepare features
        X = self.prepare_features(race_data)
        X_scaled = self.scaler.transform(X)

        # Get individual model predictions
        predictions = []

        for idx, (_, horse_data) in enumerate(race_data.iterrows()):
            horse_features = X_scaled[idx : idx + 1]

            # Individual model probabilities
            rf_prob = (
                self.models["random_forest"].predict_proba(horse_features)[0, 1]
                if "random_forest" in self.models
                else 0.0
            )
            gb_prob = (
                self.models["gradient_boosting"].predict_proba(horse_features)[0, 1]
                if "gradient_boosting" in self.models
                else 0.0
            )
            nn_prob = (
                self.models["neural_network"].predict_proba(horse_features)[0, 1]
                if "neural_network" in self.models
                else 0.0
            )
            lr_prob = (
                self.models["logistic_regression"].predict_proba(horse_features)[0, 1]
                if "logistic_regression" in self.models
                else 0.0
            )

            # Ensemble probability
            ensemble_prob = self.ensemble_model.predict_proba(horse_features)[0, 1]

            # Calculate confidence (based on model agreement)
            individual_probs = [
                p for p in [rf_prob, gb_prob, nn_prob, lr_prob] if p > 0
            ]
            confidence = (
                1.0 - np.std(individual_probs) if len(individual_probs) > 1 else 0.5
            )

            # Create prediction
            prediction = EnsemblePrediction(
                horse_name=horse_data.get("name", f"Horse_{idx}"),
                race_id=race_id or "unknown",
                morning_line_odds=0.0,  # Would need odds data
                recent_form_rating=horse_data.get("Percentage_wins", 0.0) * 100,
                speed_rating=horse_data.get("Flat_Turf_rate", 0.0) * 100,
                class_rating=horse_data.get("Percentage_placed", 0.0) * 100,
                rf_prob=rf_prob,
                gb_prob=gb_prob,
                nn_prob=nn_prob,
                lr_prob=lr_prob,
                ensemble_prob=ensemble_prob,
                ml_rank=0,  # Will be set after sorting
                odds_rank=0,  # Would need odds data
                confidence=confidence,
                value_bet=confidence > 0.7
                and ensemble_prob > 0.6,  # Simple value bet logic
            )

            predictions.append(prediction)

        # Sort by ensemble probability and assign ranks
        predictions.sort(key=lambda x: x.ensemble_prob, reverse=True)
        for i, pred in enumerate(predictions):
            pred.ml_rank = i + 1

        # Calculate feature importance (from Random Forest if available)
        feature_importance = []
        if "random_forest" in self.models:
            importances = self.models["random_forest"].feature_importances_
            for i, importance in enumerate(importances):
                feature_importance.append(
                    FeatureImportance(
                        feature_name=self.feature_names[i],
                        importance_score=importance,
                        rank=i + 1,
                    )
                )
            feature_importance.sort(key=lambda x: x.importance_score, reverse=True)

        # Calculate confidence distribution
        confidence_distribution = {
            "high": sum(1 for p in predictions if p.confidence > 0.7),
            "medium": sum(1 for p in predictions if 0.4 <= p.confidence <= 0.7),
            "low": sum(1 for p in predictions if p.confidence < 0.4),
        }

        # Count value bets
        value_bets_count = sum(1 for p in predictions if p.value_bet)

        # Get model performance (from last training)
        model_performance = {}
        for name, model in self.models.items():
            model_performance[name] = {
                "model_type": type(model).__name__,
                "n_features": len(self.feature_names),
            }

        return EnsembleResults(
            predictions=predictions,
            feature_importance=feature_importance[:10],  # Top 10 features
            model_performance=model_performance,
            confidence_distribution=confidence_distribution,
            value_bets_count=value_bets_count,
        )

    def save_ensemble(self, filepath: str = None) -> str:
        """Save the trained ensemble model."""
        if not self.is_trained:
            raise ValueError("No trained model to save")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if filepath is None:
            filepath = self.models_dir / f"v201_ensemble_{timestamp}.joblib"
        else:
            filepath = Path(filepath)

        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save ensemble data
        ensemble_data = {
            "ensemble_model": self.ensemble_model,
            "individual_models": self.models,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "timestamp": timestamp,
            "model_configs": {
                name: str(model) for name, model in self.model_configs.items()
            },
        }

        joblib.dump(ensemble_data, filepath)
        logger.info(f"✅ Ensemble model saved to {filepath}")

        return str(filepath)

    def load_ensemble(self, filepath: str) -> bool:
        """Load a trained ensemble model."""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                logger.error(f"Model file not found: {filepath}")
                return False

            ensemble_data = joblib.load(filepath)

            self.ensemble_model = ensemble_data["ensemble_model"]
            self.models = ensemble_data["individual_models"]
            self.scaler = ensemble_data["scaler"]
            self.feature_names = ensemble_data["feature_names"]
            self.is_trained = True

            logger.info(f"✅ Ensemble model loaded from {filepath}")
            logger.info(f"   Models: {list(self.models.keys())}")
            logger.info(f"   Features: {len(self.feature_names)}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load ensemble model: {e}")
            return False

    def export_predictions(self, results: EnsembleResults, filepath: str) -> str:
        """Export predictions to CSV format (v2.01 compatible)."""
        # Convert predictions to DataFrame
        predictions_data = []
        for pred in results.predictions:
            predictions_data.append(
                {
                    "race_id": pred.race_id,
                    "horse_name": pred.horse_name,
                    "morning_line_odds": pred.morning_line_odds,
                    "recent_form_rating": pred.recent_form_rating,
                    "speed_rating": pred.speed_rating,
                    "class_rating": pred.class_rating,
                    "rf_prob": pred.rf_prob,
                    "gb_prob": pred.gb_prob,
                    "nn_prob": pred.nn_prob,
                    "lr_prob": pred.lr_prob,
                    "ensemble_prob": pred.ensemble_prob,
                    "ml_rank": pred.ml_rank,
                    "odds_rank": pred.odds_rank,
                    "confidence": pred.confidence,
                    "value_bet": pred.value_bet,
                }
            )

        df = pd.DataFrame(predictions_data)

        # Save to CSV
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)

        logger.info(f"✅ Predictions exported to {filepath}")
        return str(filepath)

    def get_model_summary(self) -> Dict[str, Any]:
        """Get comprehensive model summary."""
        if not self.is_trained:
            return {"status": "Not trained"}

        summary = {
            "status": "Trained",
            "individual_models": list(self.models.keys()),
            "ensemble_components": (
                len(self.ensemble_model.estimators) if self.ensemble_model else 0
            ),
            "feature_count": len(self.feature_names),
            "features": self.feature_names[:10],  # Top 10 features
            "model_configs": {
                name: {"type": type(model).__name__, "params": model.get_params()}
                for name, model in self.models.items()
            },
        }

        return summary
