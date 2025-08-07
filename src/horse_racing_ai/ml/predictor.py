"""Machine Learning predictor for horse racing outcomes."""

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import structlog
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from ..core.config import config

logger = structlog.get_logger(__name__)


@dataclass
class PredictionResult:
    """Result of a race prediction."""

    horse_name: str
    probability: float
    predicted_position: int
    confidence: float
    features_used: List[str]


@dataclass
class ModelMetrics:
    """Model performance metrics."""

    accuracy: float
    roc_auc: float
    cross_val_mean: float
    cross_val_std: float
    feature_importance: Dict[str, float]


class RacePredictor:
    """Machine learning predictor for horse racing outcomes."""

    def __init__(self, model_type: str = "random_forest") -> None:
        """Initialize the predictor.

        Args:
            model_type: Type of model to use (random_forest, gradient_boost, logistic)
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns: List[str] = []
        self.is_trained = False

        # Initialize model based on type
        self._initialize_model()

        # Ensure model directory exists
        config.models_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_model(self) -> None:
        """Initialize the ML model based on type."""
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=config.ml.random_state,
                n_jobs=-1,
            )
        elif self.model_type == "gradient_boost":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=config.ml.random_state,
            )
        elif self.model_type == "logistic":
            self.model = LogisticRegression(
                random_state=config.ml.random_state, max_iter=1000
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def prepare_features(self, race_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from race data.

        Args:
            race_data: Raw race data DataFrame

        Returns:
            Processed features DataFrame
        """
        logger.info("Preparing features from race data")
        features = race_data.copy()

        # Basic features
        numeric_features = []

        # Horse-specific features
        if "weight" in features.columns:
            numeric_features.append("weight")

        if "post_position" in features.columns:
            numeric_features.append("post_position")

        if "odds" in features.columns:
            features["log_odds"] = np.log(
                features["odds"].fillna(features["odds"].median()) + 1
            )
            numeric_features.append("log_odds")

        # Jockey/Trainer performance features (would need historical data)
        if "jockey" in features.columns:
            jockey_encoded = self.label_encoder.fit_transform(
                features["jockey"].fillna("Unknown")
            )
            features["jockey_encoded"] = jockey_encoded
            numeric_features.append("jockey_encoded")

        if "trainer" in features.columns:
            trainer_encoded = self.label_encoder.fit_transform(
                features["trainer"].fillna("Unknown")
            )
            features["trainer_encoded"] = trainer_encoded
            numeric_features.append("trainer_encoded")

        # Track conditions
        if "surface" in features.columns:
            surface_dummies = pd.get_dummies(features["surface"], prefix="surface")
            features = pd.concat([features, surface_dummies], axis=1)
            numeric_features.extend(surface_dummies.columns.tolist())

        # Distance features
        if "distance" in features.columns:
            # Convert distance to numeric (assumes format like "6F", "1M", etc.)
            features["distance_numeric"] = features["distance"].apply(
                self._parse_distance
            )
            numeric_features.append("distance_numeric")

        # Historical performance features (placeholder - would need historical data)
        features["career_starts"] = np.random.randint(
            1, 50, len(features)
        )  # Placeholder
        features["career_wins"] = np.random.randint(0, 20, len(features))  # Placeholder
        features["win_percentage"] = features["career_wins"] / features["career_starts"]
        numeric_features.extend(["career_starts", "career_wins", "win_percentage"])

        # Select only numeric features and handle missing values
        feature_df = features[numeric_features].fillna(0)

        self.feature_columns = feature_df.columns.tolist()
        logger.info(
            f"Prepared {len(self.feature_columns)} features: {self.feature_columns}"
        )

        return feature_df

    def _parse_distance(self, distance_str: str) -> float:
        """Parse distance string to numeric value in furlongs.

        Args:
            distance_str: Distance string like "6F", "1M", "1M2F"

        Returns:
            Distance in furlongs
        """
        if pd.isna(distance_str):
            return 6.0  # Default distance

        distance_str = str(distance_str).upper().strip()

        try:
            if "M" in distance_str:
                # Mile format
                miles = float(distance_str.split("M")[0])
                furlongs = miles * 8

                # Check for additional furlongs
                if "F" in distance_str:
                    additional_f = distance_str.split("M")[1].replace("F", "")
                    if additional_f:
                        furlongs += float(additional_f)

                return furlongs
            elif "F" in distance_str:
                # Furlong format
                return float(distance_str.replace("F", ""))
            else:
                # Assume numeric is in furlongs
                return float(distance_str)
        except (ValueError, IndexError):
            return 6.0  # Default fallback

    def train(
        self, training_data: pd.DataFrame, target_column: str = "finish_position"
    ) -> ModelMetrics:
        """Train the model on historical race data.

        Args:
            training_data: DataFrame with race results
            target_column: Column name containing the target variable

        Returns:
            Model performance metrics
        """
        logger.info(f"Training {self.model_type} model")

        # Prepare features
        X = self.prepare_features(training_data)
        y = training_data[target_column]

        # Convert to binary classification (win/not win)
        y_binary = (y == 1).astype(int)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y_binary,
            test_size=1 - config.ml.train_test_split,
            random_state=config.ml.random_state,
            stratify=y_binary,
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=config.ml.cross_validation_folds
        )

        # Feature importance
        if hasattr(self.model, "feature_importances_"):
            feature_importance = dict(
                zip(self.feature_columns, self.model.feature_importances_)
            )
        else:
            feature_importance = {}

        metrics = ModelMetrics(
            accuracy=accuracy,
            roc_auc=roc_auc,
            cross_val_mean=cv_scores.mean(),
            cross_val_std=cv_scores.std(),
            feature_importance=feature_importance,
        )

        self.is_trained = True

        logger.info(
            f"Model training completed - Accuracy: {accuracy:.3f}, AUC: {roc_auc:.3f}"
        )
        return metrics

    def predict_race(self, race_data: pd.DataFrame) -> List[PredictionResult]:
        """Predict outcomes for a race.

        Args:
            race_data: DataFrame with horse data for the race

        Returns:
            List of prediction results sorted by probability
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        logger.info(f"Predicting race with {len(race_data)} horses")

        # Prepare features
        X = self.prepare_features(race_data)
        X_scaled = self.scaler.transform(X)

        # Get predictions
        probabilities = self.model.predict_proba(X_scaled)[:, 1]

        # Create results
        results = []
        for i, (idx, row) in enumerate(race_data.iterrows()):
            result = PredictionResult(
                horse_name=row.get("name", f"Horse_{i + 1}"),
                probability=float(probabilities[i]),
                predicted_position=0,  # Will be set after sorting
                confidence=float(probabilities[i]),
                features_used=self.feature_columns,
            )
            results.append(result)

        # Sort by probability (highest first) and set positions
        results.sort(key=lambda x: x.probability, reverse=True)
        for i, result in enumerate(results):
            result.predicted_position = i + 1

        logger.info(
            f"Top prediction: {results[0].horse_name} ({results[0].probability:.3f})"
        )
        return results

    def save_model(self, filename: Optional[str] = None) -> Path:
        """Save the trained model to disk.

        Args:
            filename: Optional filename, defaults to model_type_timestamp

        Returns:
            Path to saved model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        if filename is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.model_type}_{timestamp}.pkl"

        model_path = config.models_dir / filename

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "label_encoder": self.label_encoder,
            "feature_columns": self.feature_columns,
            "model_type": self.model_type,
        }

        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")

        return model_path

    def load_model(self, model_path: Path) -> None:
        """Load a trained model from disk.

        Args:
            model_path: Path to the saved model
        """
        logger.info(f"Loading model from {model_path}")

        model_data = joblib.load(model_path)

        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.label_encoder = model_data["label_encoder"]
        self.feature_columns = model_data["feature_columns"]
        self.model_type = model_data["model_type"]
        self.is_trained = True

        logger.info("Model loaded successfully")

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained or not hasattr(self.model, "feature_importances_"):
            return {}

        return dict(zip(self.feature_columns, self.model.feature_importances_))
