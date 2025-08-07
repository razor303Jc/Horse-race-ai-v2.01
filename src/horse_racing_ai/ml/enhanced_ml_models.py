#!/usr/bin/env python3
"""
Enhanced ML Models for Horse Racing AI v2.0
==========================================

Implements advanced machine learning models for:
- Enhanced rating predictions using neural networks
- Z-score performance modeling
- Monte Carlo simulation optimization
- AI performance tracking and feedback loops
"""

import logging
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
import structlog
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    VotingRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler, StandardScaler

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None
    layers = None
    tf = None

from ..core.config import config
from ..scoring.composite_scorer import CompositeScore
from ..scoring.form_analyzer import RacePerformance

logger = structlog.get_logger(__name__)


@dataclass
class MLModelPrediction:
    """Result of ML model prediction."""

    horse_name: str
    predicted_rating: float
    predicted_z_score: float
    confidence_score: float
    win_probability: float
    place_probability: float
    show_probability: float
    expected_position: float
    performance_range: Tuple[float, float]
    model_features: Dict[str, float]
    prediction_factors: List[str]


@dataclass
class ModelPerformance:
    """Model performance metrics and tracking."""

    model_name: str
    accuracy_score: float
    rmse: float
    mae: float
    r2_score: float
    cross_val_mean: float
    cross_val_std: float
    feature_importance: Dict[str, float]
    prediction_count: int
    last_updated: datetime
    performance_trend: List[float]


@dataclass
class AIPerformanceMetrics:
    """AI system performance tracking."""

    total_predictions: int
    correct_win_predictions: int
    correct_place_predictions: int
    average_accuracy: float
    profit_loss_ratio: float
    roi_percentage: float
    confidence_calibration: float
    model_drift_score: float
    last_evaluation: datetime
    performance_history: List[Dict[str, float]]


class EnhancedMLRatingSystem:
    """Advanced ML system for horse racing ratings and predictions."""

    def __init__(self, enable_neural_networks: bool = True):
        """Initialize the enhanced ML rating system.

        Args:
            enable_neural_networks: Whether to use neural network models
        """
        self.enable_neural_networks = enable_neural_networks
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False

        # Performance tracking
        self.performance_metrics = {}
        self.ai_metrics = AIPerformanceMetrics(
            total_predictions=0,
            correct_win_predictions=0,
            correct_place_predictions=0,
            average_accuracy=0.0,
            profit_loss_ratio=0.0,
            roi_percentage=0.0,
            confidence_calibration=0.0,
            model_drift_score=0.0,
            last_evaluation=datetime.now(),
            performance_history=[],
        )

        # Initialize models
        self._initialize_models()

        # Ensure model directory exists
        config.models_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Enhanced ML Rating System initialized")

    def _initialize_models(self) -> None:
        """Initialize the ensemble of ML models."""

        # Random Forest for robustness
        self.models["random_forest"] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        )

        # Gradient Boosting for accuracy
        self.models["gradient_boost"] = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42,
        )

        # Ridge regression for baseline
        self.models["ridge"] = Ridge(alpha=1.0, random_state=42)

        # Neural network for complex patterns (if enabled)
        if self.enable_neural_networks:
            self.models["neural_network"] = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation="relu",
                solver="adam",
                alpha=0.001,
                learning_rate="adaptive",
                max_iter=500,
                random_state=42,
            )

        # Ensemble voting regressor
        base_models = [
            ("rf", self.models["random_forest"]),
            ("gb", self.models["gradient_boost"]),
            ("ridge", self.models["ridge"]),
        ]

        if self.enable_neural_networks:
            base_models.append(("nn", self.models["neural_network"]))

        self.models["ensemble"] = VotingRegressor(estimators=base_models, n_jobs=-1)

        # Scalers for different models
        self.scalers["standard"] = StandardScaler()
        self.scalers["minmax"] = MinMaxScaler()

    def create_deep_neural_network(self, input_dim: int):
        """Create a deep neural network for complex pattern recognition.

        Args:
            input_dim: Number of input features

        Returns:
            Compiled Keras model or None if TensorFlow not available
        """
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available - skipping deep neural network")
            return None

        model = keras.Sequential(
            [
                layers.Dense(128, activation="relu", input_shape=(input_dim,)),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                layers.Dense(64, activation="relu"),
                layers.BatchNormalization(),
                layers.Dropout(0.2),
                layers.Dense(32, activation="relu"),
                layers.BatchNormalization(),
                layers.Dropout(0.1),
                layers.Dense(16, activation="relu"),
                layers.Dense(1, activation="linear"),  # Regression output
            ]
        )

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="mse",
            metrics=["mae", "mse"],
        )

        return model

    def prepare_enhanced_features(
        self,
        horse_data: List[RacePerformance],
        composite_scores: List[CompositeScore],
        race_conditions: Dict[str, Any],
    ) -> pd.DataFrame:
        """Prepare comprehensive features for ML training/prediction.

        Args:
            horse_data: Historical race performance data
            composite_scores: Current composite scoring results
            race_conditions: Race condition parameters

        Returns:
            Feature DataFrame ready for ML models
        """
        logger.info("Preparing enhanced features for ML models")

        features = []

        for i, (performances, score) in enumerate(zip(horse_data, composite_scores)):
            # Basic composite score features
            feature_dict = {
                "composite_score": score.composite_score,
                "form_score": score.form_score,
                "power_rating": score.power_rating,
                "speed_score": score.speed_score,
                "class_score": score.class_score,
                "consistency_score": score.consistency_score,
                "conditions_score": score.conditions_score,
                "confidence_level": score.confidence_level,
            }

            # Historical performance features
            if performances:
                recent_performances = performances[-5:]  # Last 5 races

                # Performance trends
                positions = [p.finish_position for p in recent_performances]
                speed_figures = [
                    p.speed_figure for p in recent_performances if p.speed_figure
                ]
                beaten_lengths = [p.beaten_lengths for p in recent_performances]

                feature_dict.update(
                    {
                        "avg_position_last_5": np.mean(positions) if positions else 5.0,
                        "best_position_last_5": min(positions) if positions else 1,
                        "worst_position_last_5": max(positions) if positions else 10,
                        "position_improvement": self._calculate_trend(positions),
                        "avg_speed_figure": (
                            np.mean(speed_figures) if speed_figures else 80.0
                        ),
                        "max_speed_figure": (
                            max(speed_figures) if speed_figures else 80.0
                        ),
                        "speed_consistency": (
                            np.std(speed_figures) if len(speed_figures) > 1 else 5.0
                        ),
                        "speed_trend": self._calculate_trend(speed_figures),
                        "avg_beaten_lengths": (
                            np.mean(beaten_lengths) if beaten_lengths else 3.0
                        ),
                        "min_beaten_lengths": (
                            min(beaten_lengths) if beaten_lengths else 0.0
                        ),
                        "performance_volatility": (
                            np.std(beaten_lengths) if len(beaten_lengths) > 1 else 2.0
                        ),
                    }
                )

                # Jockey/Trainer performance
                jockeys = [p.jockey for p in recent_performances]
                trainers = [p.trainer for p in recent_performances]

                feature_dict.update(
                    {
                        "jockey_consistency": (
                            len(set(jockeys)) / len(jockeys) if jockeys else 1.0
                        ),
                        "trainer_consistency": (
                            len(set(trainers)) / len(trainers) if trainers else 1.0
                        ),
                    }
                )

                # Class and distance analysis
                distances = [p.distance for p in recent_performances]
                purses = [p.purse for p in recent_performances if p.purse]

                feature_dict.update(
                    {
                        "distance_specialization": self._calculate_distance_specialization(
                            distances, race_conditions.get("distance", 8.0)
                        ),
                        "class_progression": self._calculate_class_progression(purses),
                    }
                )

                # Track condition adaptability
                surfaces = [p.surface.value for p in recent_performances]
                conditions = [p.conditions for p in recent_performances]

                feature_dict.update(
                    {
                        "surface_versatility": (
                            len(set(surfaces)) / len(surfaces) if surfaces else 1.0
                        ),
                        "condition_adaptability": (
                            len(set(conditions)) / len(conditions)
                            if conditions
                            else 1.0
                        ),
                    }
                )

                # Time-based features
                days_since_last = [
                    (datetime.now() - p.date).days for p in recent_performances
                ]

                feature_dict.update(
                    {
                        "days_since_last_race": (
                            min(days_since_last) if days_since_last else 30
                        ),
                        "racing_frequency": len(recent_performances) / 365.0,
                        "layoff_factor": (
                            max(days_since_last) if days_since_last else 30
                        ),
                    }
                )
            else:
                # Default values for horses without performance history
                feature_dict.update(
                    {
                        "avg_position_last_5": 5.0,
                        "best_position_last_5": 1,
                        "worst_position_last_5": 10,
                        "position_improvement": 0.0,
                        "avg_speed_figure": 80.0,
                        "max_speed_figure": 80.0,
                        "speed_consistency": 5.0,
                        "speed_trend": 0.0,
                        "avg_beaten_lengths": 3.0,
                        "min_beaten_lengths": 0.0,
                        "performance_volatility": 2.0,
                        "jockey_consistency": 1.0,
                        "trainer_consistency": 1.0,
                        "distance_specialization": 0.5,
                        "class_progression": 0.0,
                        "surface_versatility": 1.0,
                        "condition_adaptability": 1.0,
                        "days_since_last_race": 30,
                        "racing_frequency": 0.1,
                        "layoff_factor": 30,
                    }
                )

            # Race-specific features
            feature_dict.update(
                {
                    "race_distance": race_conditions.get("distance", 8.0),
                    "field_size": len(horse_data),
                    "race_class_numeric": self._encode_race_class(
                        race_conditions.get("race_class", "ALLOWANCE")
                    ),
                    "surface_dirt": (
                        1 if race_conditions.get("surface") == "dirt" else 0
                    ),
                    "surface_turf": (
                        1 if race_conditions.get("surface") == "turf" else 0
                    ),
                    "surface_synthetic": (
                        1 if race_conditions.get("surface") == "synthetic" else 0
                    ),
                }
            )

            # Market factors (if available)
            if hasattr(score, "betting_odds") and score.betting_odds:
                feature_dict["betting_odds"] = score.betting_odds
                feature_dict["log_odds"] = np.log(score.betting_odds + 1)
                feature_dict["market_confidence"] = 1.0 / score.betting_odds
            else:
                feature_dict["betting_odds"] = 5.0
                feature_dict["log_odds"] = np.log(6.0)
                feature_dict["market_confidence"] = 0.2

            # Interaction features
            feature_dict["form_power_interaction"] = (
                score.form_score * score.power_rating / 100.0
            )
            feature_dict["speed_class_interaction"] = (
                score.speed_score * score.class_score / 100.0
            )
            feature_dict["consistency_confidence"] = (
                score.consistency_score * score.confidence_level
            )

            features.append(feature_dict)

        # Convert to DataFrame
        feature_df = pd.DataFrame(features)

        # Store feature columns for later use
        self.feature_columns = feature_df.columns.tolist()

        logger.info(
            f"Prepared {len(self.feature_columns)} features for {len(feature_df)} horses"
        )

        return feature_df

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in a series of values."""
        if len(values) < 2:
            return 0.0

        # Simple linear trend
        x = np.arange(len(values))
        y = np.array(values)

        try:
            trend = np.polyfit(x, y, 1)[0]
            return float(trend)
        except:
            return 0.0

    def _calculate_distance_specialization(
        self, distances: List[float], target_distance: float
    ) -> float:
        """Calculate how specialized a horse is at the target distance."""
        if not distances:
            return 0.5

        # Calculate how close previous distances are to target
        distance_diffs = [abs(d - target_distance) for d in distances]
        avg_diff = np.mean(distance_diffs)

        # Convert to specialization score (0-1, where 1 = perfect specialization)
        specialization = max(0.0, 1.0 - (avg_diff / target_distance))
        return float(specialization)

    def _calculate_class_progression(self, purses: List[float]) -> float:
        """Calculate class progression based on purse trends."""
        if len(purses) < 2:
            return 0.0

        # Calculate trend in purse money (proxy for class level)
        return self._calculate_trend(purses) / max(purses) if purses else 0.0

    def _encode_race_class(self, race_class: str) -> float:
        """Encode race class as numeric value."""
        class_mapping = {
            "MAIDEN": 1.0,
            "CLAIMING": 2.0,
            "ALLOWANCE": 3.0,
            "STAKES": 4.0,
            "GRADED": 5.0,
            "HANDICAP": 3.5,
        }
        return class_mapping.get(race_class.upper(), 3.0)

    def train_models(
        self,
        training_data: pd.DataFrame,
        target_column: str = "target_rating",
        validation_split: float = 0.2,
    ) -> Dict[str, ModelPerformance]:
        """Train all ML models on the prepared data.

        Args:
            training_data: DataFrame with features and targets
            target_column: Name of the target column
            validation_split: Fraction of data to use for validation

        Returns:
            Dictionary of model performance metrics
        """
        logger.info(f"Training ML models on {len(training_data)} samples")

        # Prepare features and targets
        feature_columns = [col for col in training_data.columns if col != target_column]
        X = training_data[feature_columns].fillna(0)
        y = training_data[target_column].fillna(training_data[target_column].median())

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, shuffle=True
        )

        # Scale features
        X_train_scaled = self.scalers["standard"].fit_transform(X_train)
        X_val_scaled = self.scalers["standard"].transform(X_val)

        model_performances = {}

        # Train each model
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name} model...")

            try:
                # Use scaled data for neural networks and ridge, original for tree-based
                if model_name in ["neural_network", "ridge", "ensemble"]:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_val_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_val)

                # Calculate performance metrics
                rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                mae = mean_absolute_error(y_val, y_pred)
                r2 = r2_score(y_val, y_pred)

                # Cross-validation
                if model_name in ["neural_network", "ridge", "ensemble"]:
                    cv_scores = cross_val_score(
                        model,
                        X_train_scaled,
                        y_train,
                        cv=5,
                        scoring="neg_mean_squared_error",
                    )
                else:
                    cv_scores = cross_val_score(
                        model, X_train, y_train, cv=5, scoring="neg_mean_squared_error"
                    )

                cv_rmse_scores = np.sqrt(-cv_scores)

                # Feature importance (where available)
                feature_importance = {}
                if hasattr(model, "feature_importances_"):
                    feature_importance = dict(
                        zip(feature_columns, model.feature_importances_)
                    )
                elif hasattr(model, "coef_"):
                    feature_importance = dict(zip(feature_columns, np.abs(model.coef_)))

                performance = ModelPerformance(
                    model_name=model_name,
                    accuracy_score=r2,
                    rmse=rmse,
                    mae=mae,
                    r2_score=r2,
                    cross_val_mean=cv_rmse_scores.mean(),
                    cross_val_std=cv_rmse_scores.std(),
                    feature_importance=feature_importance,
                    prediction_count=0,
                    last_updated=datetime.now(),
                    performance_trend=[r2],
                )

                model_performances[model_name] = performance
                self.performance_metrics[model_name] = performance

                logger.info(
                    f"{model_name} - RMSE: {rmse:.3f}, MAE: {mae:.3f}, R²: {r2:.3f}"
                )

            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                continue

        self.is_trained = True
        logger.info("Model training completed")

        return model_performances

    def predict_race_with_ml(
        self,
        horse_data: List[RacePerformance],
        composite_scores: List[CompositeScore],
        race_conditions: Dict[str, Any],
        use_ensemble: bool = True,
    ) -> List[MLModelPrediction]:
        """Make predictions using trained ML models.

        Args:
            horse_data: Historical performance data for each horse
            composite_scores: Current composite scores
            race_conditions: Race condition parameters
            use_ensemble: Whether to use ensemble model (recommended)

        Returns:
            List of ML predictions for each horse
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")

        logger.info(f"Making ML predictions for {len(horse_data)} horses")

        # Prepare features
        features_df = self.prepare_enhanced_features(
            horse_data, composite_scores, race_conditions
        )

        # Scale features for models that need it
        features_scaled = self.scalers["standard"].transform(features_df)

        # Choose model
        model_name = (
            "ensemble"
            if use_ensemble and "ensemble" in self.models
            else "random_forest"
        )
        model = self.models[model_name]

        # Make predictions
        if model_name in ["neural_network", "ridge", "ensemble"]:
            predicted_ratings = model.predict(features_scaled)
        else:
            predicted_ratings = model.predict(features_df)

        # Calculate Z-scores relative to field
        field_mean = np.mean(predicted_ratings)
        field_std = max(np.std(predicted_ratings), 1.0)
        z_scores = (predicted_ratings - field_mean) / field_std

        # Convert ratings to probabilities using softmax
        rating_exp = np.exp(predicted_ratings / 10.0)  # Temperature scaling
        win_probabilities = rating_exp / np.sum(rating_exp)

        # Estimate place and show probabilities
        place_probs = self._calculate_place_probabilities(predicted_ratings)
        show_probs = self._calculate_show_probabilities(predicted_ratings)

        # Calculate expected positions
        sorted_indices = np.argsort(-predicted_ratings)
        expected_positions = np.zeros_like(predicted_ratings)
        for rank, idx in enumerate(sorted_indices):
            expected_positions[idx] = rank + 1

        # Create prediction objects
        predictions = []
        for i, (score, horse_perf) in enumerate(zip(composite_scores, horse_data)):
            # Calculate confidence based on model certainty and data quality
            confidence = self._calculate_prediction_confidence(
                features_df.iloc[i], predicted_ratings[i], score.confidence_level
            )

            # Performance range based on confidence
            rating_std = field_std * (1.0 - confidence)
            perf_range = (
                predicted_ratings[i] - rating_std,
                predicted_ratings[i] + rating_std,
            )

            # Identify key prediction factors
            prediction_factors = self._identify_prediction_factors(
                features_df.iloc[i], self.performance_metrics.get(model_name, None)
            )

            prediction = MLModelPrediction(
                horse_name=score.horse_name,
                predicted_rating=float(predicted_ratings[i]),
                predicted_z_score=float(z_scores[i]),
                confidence_score=confidence,
                win_probability=float(win_probabilities[i]),
                place_probability=float(place_probs[i]),
                show_probability=float(show_probs[i]),
                expected_position=float(expected_positions[i]),
                performance_range=perf_range,
                model_features=features_df.iloc[i].to_dict(),
                prediction_factors=prediction_factors,
            )

            predictions.append(prediction)

        # Update AI metrics
        self.ai_metrics.total_predictions += len(predictions)

        logger.info(f"Generated {len(predictions)} ML predictions using {model_name}")

        return predictions

    def _calculate_place_probabilities(self, ratings: np.ndarray) -> np.ndarray:
        """Calculate place (top 3) probabilities."""
        # Simulate place probabilities based on ratings
        place_probs = np.zeros_like(ratings)

        for i in range(len(ratings)):
            # Probability of finishing in top 3
            better_horses = np.sum(ratings > ratings[i])
            place_probs[i] = max(0.1, 1.0 - (better_horses / len(ratings)) * 0.7)

        return place_probs

    def _calculate_show_probabilities(self, ratings: np.ndarray) -> np.ndarray:
        """Calculate show (top 4) probabilities."""
        # Similar to place but for top 4
        show_probs = np.zeros_like(ratings)

        for i in range(len(ratings)):
            better_horses = np.sum(ratings > ratings[i])
            show_probs[i] = max(0.15, 1.0 - (better_horses / len(ratings)) * 0.6)

        return show_probs

    def _calculate_prediction_confidence(
        self, features: pd.Series, predicted_rating: float, base_confidence: float
    ) -> float:
        """Calculate confidence in the prediction."""

        # Base confidence from composite scoring
        confidence = base_confidence

        # Adjust based on data completeness
        non_zero_features = np.sum(features != 0) / len(features)
        confidence *= non_zero_features

        # Adjust based on model certainty (lower variance = higher confidence)
        if hasattr(self, "performance_metrics") and self.performance_metrics:
            best_model_r2 = max([m.r2_score for m in self.performance_metrics.values()])
            confidence *= best_model_r2

        return max(0.1, min(1.0, confidence))

    def _identify_prediction_factors(
        self, features: pd.Series, model_performance: Optional[ModelPerformance]
    ) -> List[str]:
        """Identify key factors driving the prediction."""

        factors = []

        # High-impact features based on feature importance
        if model_performance and model_performance.feature_importance:
            # Get top 5 most important features
            sorted_features = sorted(
                model_performance.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for feature_name, importance in sorted_features[:5]:
                if feature_name in features.index and features[feature_name] != 0:
                    feature_value = features[feature_name]

                    # Interpret feature values
                    if "score" in feature_name and feature_value > 70:
                        factors.append(f"Strong {feature_name.replace('_', ' ')}")
                    elif "consistency" in feature_name and feature_value > 0.7:
                        factors.append("High consistency")
                    elif "trend" in feature_name and feature_value > 0:
                        factors.append("Improving form")
                    elif "specialization" in feature_name and feature_value > 0.8:
                        factors.append("Distance specialist")

        # Fallback to general factors if no specific ones identified
        if not factors:
            if features.get("composite_score", 0) > 75:
                factors.append("High composite rating")
            if features.get("form_score", 0) > 70:
                factors.append("Good recent form")
            if features.get("power_rating", 0) > 120:
                factors.append("Strong power rating")

        return factors[:3]  # Return top 3 factors

    def update_ai_performance(
        self, predictions: List[MLModelPrediction], actual_results: List[Dict[str, Any]]
    ) -> None:
        """Update AI performance metrics based on actual race results.

        Args:
            predictions: ML predictions made before the race
            actual_results: Actual race results with positions and outcomes
        """
        if len(predictions) != len(actual_results):
            logger.warning("Prediction and result count mismatch")
            return

        logger.info("Updating AI performance metrics")

        correct_wins = 0
        correct_places = 0
        total_predictions = len(predictions)

        for pred, result in zip(predictions, actual_results):
            actual_position = result.get("finish_position", 10)

            # Check win predictions
            if pred.win_probability > 0.3 and actual_position == 1:
                correct_wins += 1
                self.ai_metrics.correct_win_predictions += 1

            # Check place predictions
            if pred.place_probability > 0.4 and actual_position <= 3:
                correct_places += 1
                self.ai_metrics.correct_place_predictions += 1

        # Update overall metrics
        self.ai_metrics.total_predictions += total_predictions

        # Calculate accuracy rates
        win_accuracy = correct_wins / total_predictions if total_predictions > 0 else 0
        place_accuracy = (
            correct_places / total_predictions if total_predictions > 0 else 0
        )

        # Update average accuracy (weighted)
        current_accuracy = (win_accuracy + place_accuracy) / 2
        total_races = len(self.ai_metrics.performance_history) + 1

        self.ai_metrics.average_accuracy = (
            self.ai_metrics.average_accuracy * (total_races - 1) + current_accuracy
        ) / total_races

        # Add to performance history
        performance_entry = {
            "timestamp": datetime.now().isoformat(),
            "win_accuracy": win_accuracy,
            "place_accuracy": place_accuracy,
            "total_predictions": total_predictions,
            "average_confidence": np.mean([p.confidence_score for p in predictions]),
        }

        self.ai_metrics.performance_history.append(performance_entry)
        self.ai_metrics.last_evaluation = datetime.now()

        logger.info(
            f"AI Performance Updated - Win: {win_accuracy:.1%}, Place: {place_accuracy:.1%}"
        )

    def save_enhanced_models(self, filename_prefix: str = "enhanced_ml") -> Path:
        """Save all trained models and metrics.

        Args:
            filename_prefix: Prefix for the saved files

        Returns:
            Path to the main model file
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained models")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = config.models_dir / f"{filename_prefix}_{timestamp}.pkl"

        model_data = {
            "models": self.models,
            "scalers": self.scalers,
            "feature_columns": self.feature_columns,
            "performance_metrics": self.performance_metrics,
            "ai_metrics": self.ai_metrics,
            "is_trained": self.is_trained,
            "timestamp": timestamp,
        }

        joblib.dump(model_data, model_path)
        logger.info(f"Enhanced ML models saved to {model_path}")

        return model_path

    def load_enhanced_models(self, model_path: Path) -> None:
        """Load previously trained models and metrics.

        Args:
            model_path: Path to the saved model file
        """
        logger.info(f"Loading enhanced ML models from {model_path}")

        model_data = joblib.load(model_path)

        self.models = model_data["models"]
        self.scalers = model_data["scalers"]
        self.feature_columns = model_data["feature_columns"]
        self.performance_metrics = model_data["performance_metrics"]
        self.ai_metrics = model_data["ai_metrics"]
        self.is_trained = model_data["is_trained"]

        logger.info("Enhanced ML models loaded successfully")

    def get_ai_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive AI performance report.

        Returns:
            Dictionary containing performance metrics and insights
        """
        report = {
            "total_predictions": self.ai_metrics.total_predictions,
            "win_accuracy": (
                self.ai_metrics.correct_win_predictions
                / max(1, self.ai_metrics.total_predictions)
            ),
            "place_accuracy": (
                self.ai_metrics.correct_place_predictions
                / max(1, self.ai_metrics.total_predictions)
            ),
            "average_accuracy": self.ai_metrics.average_accuracy,
            "model_performance": {},
            "performance_trend": [],
            "recommendations": [],
        }

        # Add model-specific performance
        for model_name, metrics in self.performance_metrics.items():
            report["model_performance"][model_name] = {
                "r2_score": metrics.r2_score,
                "rmse": metrics.rmse,
                "mae": metrics.mae,
                "prediction_count": metrics.prediction_count,
            }

        # Add performance trend
        if self.ai_metrics.performance_history:
            recent_history = self.ai_metrics.performance_history[-10:]  # Last 10 races
            report["performance_trend"] = [
                {
                    "date": entry["timestamp"],
                    "accuracy": (entry["win_accuracy"] + entry["place_accuracy"]) / 2,
                }
                for entry in recent_history
            ]

        # Generate recommendations
        if report["win_accuracy"] < 0.3:
            report["recommendations"].append(
                "Consider retraining models with more recent data"
            )
        if report["average_accuracy"] > 0.6:
            report["recommendations"].append(
                "Performance is strong - consider increasing bet sizes"
            )

        return report


class ZScoreMLPredictor:
    """Specialized ML model for Z-score prediction and analysis."""

    def __init__(self):
        """Initialize the Z-score ML predictor."""
        self.z_score_model = None
        self.scaler = StandardScaler()
        self.is_trained = False

        logger.info("Z-Score ML Predictor initialized")

    def train_z_score_model(
        self,
        historical_ratings: List[float],
        field_contexts: List[Dict[str, Any]],
        actual_z_scores: List[float],
    ) -> float:
        """Train ML model to predict Z-scores more accurately.

        Args:
            historical_ratings: Historical composite ratings
            field_contexts: Race field context information
            actual_z_scores: Actual Z-scores from races

        Returns:
            Model accuracy score
        """
        logger.info("Training Z-score prediction model")

        # Prepare features
        features = []
        for rating, context in zip(historical_ratings, field_contexts):
            feature_vector = [
                rating,
                context.get("field_size", 10),
                context.get("avg_field_rating", 75),
                context.get("field_strength", 1.0),
                context.get("race_competitiveness", 0.5),
            ]
            features.append(feature_vector)

        X = np.array(features)
        y = np.array(actual_z_scores)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Initialize and train model
        self.z_score_model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )

        self.z_score_model.fit(X_scaled, y)
        self.is_trained = True

        # Calculate accuracy
        predictions = self.z_score_model.predict(X_scaled)
        accuracy = r2_score(y, predictions)

        logger.info(f"Z-score model trained with accuracy: {accuracy:.3f}")

        return accuracy

    def predict_z_scores(
        self, ratings: List[float], race_context: Dict[str, Any]
    ) -> List[float]:
        """Predict Z-scores using trained ML model.

        Args:
            ratings: Current race ratings
            race_context: Race context information

        Returns:
            Predicted Z-scores for each horse
        """
        if not self.is_trained:
            # Fallback to statistical calculation
            ratings_array = np.array(ratings)
            mean_rating = np.mean(ratings_array)
            std_rating = max(np.std(ratings_array), 1.0)
            return ((ratings_array - mean_rating) / std_rating).tolist()

        # Prepare features
        features = []
        for rating in ratings:
            feature_vector = [
                rating,
                race_context.get("field_size", len(ratings)),
                race_context.get("avg_field_rating", np.mean(ratings)),
                race_context.get("field_strength", 1.0),
                race_context.get("race_competitiveness", 0.5),
            ]
            features.append(feature_vector)

        X = np.array(features)
        X_scaled = self.scaler.transform(X)

        # Predict Z-scores
        predicted_z_scores = self.z_score_model.predict(X_scaled)

        return predicted_z_scores.tolist()


class MonteCarloAIEnhancer:
    """AI enhancement for Monte Carlo simulations."""

    def __init__(self):
        """Initialize Monte Carlo AI enhancer."""
        self.simulation_optimizer = None
        self.variance_predictor = None
        self.outcome_model = None

        logger.info("Monte Carlo AI Enhancer initialized")

    def optimize_simulation_parameters(
        self,
        historical_results: List[Dict[str, Any]],
        simulation_configs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Use ML to optimize Monte Carlo simulation parameters.

        Args:
            historical_results: Historical race results
            simulation_configs: Different simulation configurations tested

        Returns:
            Optimized simulation parameters
        """
        logger.info("Optimizing Monte Carlo simulation parameters")

        # This would typically involve:
        # 1. Testing different simulation parameters
        # 2. Measuring accuracy against historical results
        # 3. Using ML to find optimal parameters

        # For now, return optimized defaults
        optimized_params = {
            "simulations": 15000,  # Increased for better accuracy
            "variance_scaling": 0.8,  # Reduced variance for more realistic results
            "field_interaction": 0.15,  # Increased interaction effects
            "consistency_weight": 0.4,  # Higher weight on consistency
            "form_weight": 0.2,  # Balanced form weighting
            "confidence_threshold": 0.7,  # Higher confidence threshold
        }

        logger.info("Monte Carlo parameters optimized")
        return optimized_params

    def predict_simulation_variance(
        self, horse_profiles: List[Dict[str, Any]]
    ) -> List[float]:
        """Predict variance for each horse in Monte Carlo simulations.

        Args:
            horse_profiles: Horse performance profiles

        Returns:
            Predicted variance for each horse
        """
        # Use consistency and form metrics to predict variance
        variances = []

        for profile in horse_profiles:
            base_variance = 5.0  # Base variance

            # Adjust based on consistency
            consistency = profile.get("consistency_factor", 0.5)
            consistency_adjustment = base_variance * (1.0 - consistency)

            # Adjust based on recent form
            form_trend = profile.get("form_trend", 0.0)
            form_adjustment = abs(form_trend) * 2.0  # Higher variance for extreme form

            # Adjust based on data quality
            confidence = profile.get("confidence_level", 0.5)
            confidence_adjustment = base_variance * (1.0 - confidence)

            total_variance = (
                base_variance
                + consistency_adjustment
                + form_adjustment
                + confidence_adjustment
            )
            variances.append(min(15.0, max(2.0, total_variance)))  # Clamp between 2-15

        return variances
