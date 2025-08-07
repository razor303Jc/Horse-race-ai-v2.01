#!/usr/bin/env python3
"""
Enhanced ML Integration System with Real Models
Combines our real trained models with advanced scoring systems
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import logging
import joblib
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# ML imports
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import roc_auc_score, classification_report, accuracy_score

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedPrediction:
    """Enhanced prediction combining real and synthetic models"""

    horse_name: str
    win_probability: float
    place_probability: float

    # Real model predictions
    real_rf_prob: Optional[float] = None
    real_gb_prob: Optional[float] = None
    real_nn_prob: Optional[float] = None
    real_lr_prob: Optional[float] = None
    real_ensemble_prob: Optional[float] = None

    # Synthetic advanced predictions
    synthetic_ml_prob: Optional[float] = None

    # Combined analysis
    composite_score: Optional[float] = None
    confidence_level: Optional[str] = None
    value_assessment: Optional[str] = None

    # Additional insights
    odds: Optional[float] = None
    implied_probability: Optional[float] = None
    value_bet: Optional[bool] = None


class EnhancedMLIntegrationSystem:
    """
    Enhanced system integrating:
    - Real trained models from our ML training
    - Advanced synthetic model generation
    - Comprehensive prediction analysis
    - Value betting assessment
    """

    def __init__(self):
        self.models_dir = Path("trained_models")

        # Real model components
        self.real_models = {}
        self.real_scalers = {}
        self.real_encoders = {}
        self.real_features = {}
        self.real_performance = {}

        # Synthetic model components
        self.synthetic_models = {}
        self.synthetic_scaler = RobustScaler()
        self.synthetic_feature_selector = SelectKBest(f_classif, k=15)

        # Load real models
        self._load_real_models()

        # Initialize synthetic models
        self._initialize_synthetic_models()

    def _load_real_models(self):
        """Load our real trained models"""
        logger.info("📦 Loading real trained models...")

        try:
            # Load race card models (our best performers)
            race_card_dir = self.models_dir / "race_card_models"

            self.real_models["rf"] = joblib.load(
                race_card_dir / "random_forest_race_card.joblib"
            )
            self.real_models["gb"] = joblib.load(
                race_card_dir / "gradient_boosting_race_card.joblib"
            )
            self.real_models["nn"] = joblib.load(
                race_card_dir / "neural_network_race_card.joblib"
            )
            self.real_models["lr"] = joblib.load(
                race_card_dir / "logistic_regression_race_card.joblib"
            )

            self.real_scalers = joblib.load(race_card_dir / "scalers_race_card.joblib")
            self.real_encoders = joblib.load(
                race_card_dir / "encoders_race_card.joblib"
            )
            self.real_features = joblib.load(
                race_card_dir / "features_race_card.joblib"
            )
            self.real_performance = joblib.load(
                race_card_dir / "performance_race_card.joblib"
            )

            logger.info("✅ Real models loaded successfully")
            logger.info(f"📊 Real model performance:")
            for name, perf in self.real_performance.items():
                logger.info(f"   - {name}: AUC {perf['roc_auc']:.4f}")

        except Exception as e:
            logger.warning(f"⚠️ Could not load real models: {e}")

    def _initialize_synthetic_models(self):
        """Initialize synthetic advanced models"""
        logger.info("🧠 Initializing synthetic advanced models...")

        self.synthetic_models = {
            "Random Forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "Extra Trees": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=3,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
            ),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=4,
                random_state=42,
            ),
            "Logistic Regression": LogisticRegression(
                random_state=42, max_iter=5000, solver="liblinear"
            ),
            "Neural Network": MLPClassifier(
                hidden_layer_sizes=(100, 50), random_state=42, max_iter=2000
            ),
        }

        # Create ensemble
        ensemble_models = [
            (name.lower().replace(" ", "_"), model)
            for name, model in self.synthetic_models.items()
        ]
        self.synthetic_ensemble = VotingClassifier(ensemble_models, voting="soft")

        logger.info("✅ Synthetic models initialized")

    def create_comprehensive_dataset(
        self, num_samples: int = 8000
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Create comprehensive dataset combining real-world patterns with synthetic features"""
        logger.info(f"🔧 Creating comprehensive dataset with {num_samples} samples...")

        np.random.seed(42)

        # Generate base racing data with realistic patterns
        data = self._generate_realistic_racing_data(num_samples)

        # Add race card style features (matching our real model features)
        data = self._add_race_card_features(data)

        # Add advanced synthetic features
        data = self._add_advanced_synthetic_features(data)

        # Create realistic target based on multiple factors
        y = self._create_realistic_target(data)

        # Prepare feature matrix - remove non-numeric columns
        X = data.drop(
            ["horse_name", "target_helper", "form_string"], axis=1, errors="ignore"
        )

        # Ensure all columns are numeric
        for col in X.columns:
            if X[col].dtype == "object":
                logger.info(f"Converting {col} to numeric")
                X[col] = pd.to_numeric(X[col], errors="coerce")

        # Fill any NaN values
        X = X.fillna(0)

        logger.info(
            f"✅ Comprehensive dataset created: {X.shape[0]} samples, {X.shape[1]} features"
        )
        logger.info(f"🎯 Win rate: {y.mean():.1%}")

        return X, y

    def _generate_realistic_racing_data(self, num_samples: int) -> pd.DataFrame:
        """Generate realistic racing data"""

        data = {
            "horse_name": [f"Horse_{i+1}" for i in range(num_samples)],
            # Basic racing features (from our real data)
            "horse_age": np.random.choice(
                [2, 3, 4, 5, 6, 7, 8],
                num_samples,
                p=[0.15, 0.25, 0.2, 0.15, 0.1, 0.08, 0.07],
            ),
            "horse_weight_kg": np.random.normal(57, 4, num_samples),
            "draw": np.random.randint(1, 17, num_samples),
            "morning_line_odds": np.random.lognormal(1.8, 0.9, num_samples),
            "field_size": np.random.choice([8, 10, 12, 14, 16, 18], num_samples),
            # Career statistics
            "career_starts": np.random.exponential(8, num_samples).astype(int) + 1,
            "career_wins": np.random.poisson(1.5, num_samples),
            "career_places": np.random.poisson(3.0, num_samples),
            "last_start_days": np.random.exponential(25, num_samples).astype(int) + 7,
            # Ratings (matching our real features)
            "recent_form_rating": np.random.normal(75, 15, num_samples),
            "speed_rating": np.random.normal(78, 18, num_samples),
            "class_rating": np.random.normal(76, 14, num_samples),
            "track_rating": np.random.normal(74, 16, num_samples),
            "distance_rating": np.random.normal(77, 15, num_samples),
            "jockey_rating": np.random.normal(75, 12, num_samples),
            "trainer_rating": np.random.normal(76, 11, num_samples),
            # Race context
            "distance": np.random.choice([1200, 1400, 1600, 2000, 2400], num_samples),
            "prize_money": np.random.exponential(50000, num_samples) + 10000,
            "class_level": np.random.choice([1, 2, 3, 4, 5], num_samples),
            # Form string analysis
            "form_string": [self._generate_form_string() for _ in range(num_samples)],
        }

        return pd.DataFrame(data)

    def _generate_form_string(self) -> str:
        """Generate realistic form string"""
        length = np.random.randint(3, 8)
        positions = np.random.choice(
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-"],
            length,
            p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05],
        )
        return "".join(positions)

    def _add_race_card_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add features matching our real race card model"""
        logger.info("🎯 Adding race card features...")

        # Market features (key for our real models)
        data["implied_prob"] = 1.0 / data["morning_line_odds"]
        data["market_share"] = data.groupby(data.index // data["field_size"])[
            "implied_prob"
        ].transform(lambda x: x / x.sum())

        # Odds features
        data["log_odds"] = np.log(data["morning_line_odds"])
        race_groups = data.index // data["field_size"]
        data["odds_rank"] = data.groupby(race_groups)["morning_line_odds"].rank()
        data["odds_percentile"] = data.groupby(race_groups)["morning_line_odds"].rank(
            pct=True
        )
        data["is_favorite"] = (
            data.groupby(race_groups)["morning_line_odds"]
            .transform(lambda x: x == x.min())
            .astype(int)
        )
        data["is_outsider"] = (data["morning_line_odds"] >= 20.0).astype(int)
        data["market_strength"] = 1.0 / data["morning_line_odds"]

        # Competition features
        data["draw_percentile"] = data.groupby(race_groups)["draw"].rank(pct=True)
        data["weight_percentile"] = data.groupby(race_groups)["horse_weight_kg"].rank(
            pct=True
        )
        data["age_percentile"] = data.groupby(race_groups)["horse_age"].rank(pct=True)

        # Rating features
        data["total_rating"] = (
            data["recent_form_rating"] + data["speed_rating"] + data["class_rating"]
        ) / 3
        data["form_rank"] = data.groupby(race_groups)["recent_form_rating"].rank(
            ascending=False
        )
        data["speed_rank"] = data.groupby(race_groups)["speed_rating"].rank(
            ascending=False
        )
        data["total_rating_rank"] = data.groupby(race_groups)["total_rating"].rank(
            ascending=False
        )

        # Experience features
        data["win_rate"] = data["career_wins"] / (data["career_starts"] + 1)
        data["place_rate"] = data["career_places"] / (data["career_starts"] + 1)
        data["experience_score"] = np.log1p(data["career_starts"])

        # Recency features
        data["days_since_last_run"] = data["last_start_days"]
        data["freshness_score"] = 1.0 / (data["last_start_days"] + 1)

        # Form string analysis
        data["recent_wins"] = data["form_string"].apply(
            lambda x: x[:3].count("1") if x else 0
        )
        data["recent_places"] = data["form_string"].apply(
            lambda x: x[:3].count("2") + x[:3].count("3") if x else 0
        )
        data["form_consistency"] = data["form_string"].apply(
            lambda x: len([c for c in x[:5] if c.isdigit() and int(c) <= 5]) if x else 0
        )

        # Distance and prize features
        data["distance_numeric"] = data["distance"]
        data["log_prize"] = np.log(data["prize_money"] + 1)
        data["prize_per_runner"] = data["prize_money"] / data["field_size"]

        return data

    def _add_advanced_synthetic_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add advanced synthetic features for enhanced performance"""
        logger.info("⚙️ Adding advanced synthetic features...")

        # Performance composite index
        data["performance_index"] = (
            data["total_rating"] * 0.4
            + data["jockey_rating"] * 0.2
            + data["trainer_rating"] * 0.2
            + data["win_rate"] * 50 * 0.2
        )

        # Market intelligence
        data["value_indicator"] = data["total_rating"] / (
            data["morning_line_odds"] * 10
        )
        data["market_confidence"] = data["market_strength"]

        # Class and competition
        data["class_advantage"] = 6 - data["class_level"]  # Higher class = lower number
        data["competition_quality"] = (
            data["field_size"] * 0.1 + data["prize_money"] / 100000
        )

        # Form trends
        data["form_momentum"] = data["recent_form_rating"] / (data["speed_rating"] + 1)
        data["consistency_factor"] = data["form_consistency"] / 5.0

        # Track and distance suitability
        data["track_distance_combo"] = (
            data["track_rating"] * data["distance_rating"] / 100
        )
        data["conditions_fit"] = np.random.normal(0.7, 0.15, len(data))

        # Connections synergy
        data["connections_synergy"] = (
            data["jockey_rating"] * data["trainer_rating"] / 100
        )

        # Pace and positioning
        data["tactical_advantage"] = 1 / (data["draw"] + 1) + data["speed_rating"] / 200

        return data

    def _create_realistic_target(self, data: pd.DataFrame) -> pd.Series:
        """Create realistic target variable based on multiple factors"""

        # Calculate win probability based on multiple factors
        win_prob = (
            # Market opinion (40%)
            np.clip((1 - data["odds_percentile"]) * 0.8, 0, 0.4) * 0.40
            +
            # Performance rating (30%)
            np.clip((data["performance_index"] - 70) / 50, -0.2, 0.3) * 0.30
            +
            # Form and experience (20%)
            (data["win_rate"] * data["freshness_score"]) * 0.20
            +
            # Class and connections (10%)
            np.clip((data["connections_synergy"] - 70) / 30, -0.05, 0.1) * 0.10
            +
            # Random variance
            np.random.normal(0, 0.05, len(data))
        )

        # Ensure probabilities are realistic
        win_prob = np.clip(win_prob + 0.08, 0.01, 0.6)

        # Generate winners
        data["target_helper"] = win_prob
        y = np.random.binomial(1, win_prob)

        return pd.Series(y)

    def train_enhanced_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train both real-style and synthetic models"""
        logger.info("🚀 Training enhanced ML models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Feature selection and scaling for synthetic models
        self.synthetic_feature_selector.fit(X_train, y_train)
        X_train_selected = self.synthetic_feature_selector.transform(X_train)
        X_test_selected = self.synthetic_feature_selector.transform(X_test)

        X_train_scaled = self.synthetic_scaler.fit_transform(X_train_selected)
        X_test_scaled = self.synthetic_scaler.transform(X_test_selected)

        # Train synthetic models
        synthetic_results = {}
        logger.info("📊 Training synthetic models...")

        for name, model in self.synthetic_models.items():
            logger.info(f"   🎯 Training {name}...")

            model.fit(X_train_scaled, y_train)

            # Evaluate
            train_pred = model.predict_proba(X_train_scaled)[:, 1]
            test_pred = model.predict_proba(X_test_scaled)[:, 1]

            train_auc = roc_auc_score(y_train, train_pred)
            test_auc = roc_auc_score(y_test, test_pred)

            synthetic_results[name] = {
                "train_auc": train_auc,
                "test_auc": test_auc,
                "model": model,
            }

            logger.info(
                f"      📈 {name}: Train AUC {train_auc:.4f}, Test AUC {test_auc:.4f}"
            )

        # Train synthetic ensemble
        logger.info("   🏗️ Training synthetic ensemble...")
        self.synthetic_ensemble.fit(X_train_scaled, y_train)

        ensemble_test_pred = self.synthetic_ensemble.predict_proba(X_test_scaled)[:, 1]
        ensemble_auc = roc_auc_score(y_test, ensemble_test_pred)

        synthetic_results["Ensemble"] = {
            "test_auc": ensemble_auc,
            "model": self.synthetic_ensemble,
        }

        logger.info(f"      📈 Ensemble: Test AUC {ensemble_auc:.4f}")

        # Get feature importance from best synthetic model
        best_synthetic = max(synthetic_results.items(), key=lambda x: x[1]["test_auc"])
        best_model = best_synthetic[1]["model"]

        if hasattr(best_model, "feature_importances_"):
            selected_features = X.columns[self.synthetic_feature_selector.get_support()]
            feature_importance = dict(
                zip(selected_features, best_model.feature_importances_)
            )
        else:
            feature_importance = {}

        return {
            "synthetic_results": synthetic_results,
            "best_synthetic": best_synthetic[0],
            "feature_importance": feature_importance,
            "real_performance": self.real_performance,
        }

    def predict_race_comprehensive(
        self, race_data: pd.DataFrame
    ) -> List[EnhancedPrediction]:
        """Make comprehensive predictions using both real and synthetic models"""
        logger.info("🔮 Making comprehensive race predictions...")

        predictions = []

        for idx, horse_data in race_data.iterrows():
            # Real model predictions (if available)
            real_predictions = self._get_real_model_predictions(horse_data)

            # Synthetic model prediction
            synthetic_prediction = self._get_synthetic_prediction(horse_data)

            # Combine predictions
            composite_score = self._create_composite_score(
                real_predictions, synthetic_prediction
            )

            # Calculate metrics
            win_prob = composite_score
            place_prob = min(0.9, win_prob * 3.5)
            odds = horse_data.get("morning_line_odds", 5.0)
            implied_prob = 1.0 / odds

            prediction = EnhancedPrediction(
                horse_name=horse_data.get("horse_name", f"Horse_{idx}"),
                win_probability=win_prob,
                place_probability=place_prob,
                real_rf_prob=real_predictions.get("rf"),
                real_gb_prob=real_predictions.get("gb"),
                real_nn_prob=real_predictions.get("nn"),
                real_lr_prob=real_predictions.get("lr"),
                real_ensemble_prob=real_predictions.get("ensemble"),
                synthetic_ml_prob=synthetic_prediction,
                composite_score=composite_score,
                confidence_level=self._get_confidence_level(composite_score),
                value_assessment=self._assess_value(win_prob, implied_prob),
                odds=odds,
                implied_probability=implied_prob,
                value_bet=win_prob > implied_prob * 1.1,
            )

            predictions.append(prediction)

        # Sort by composite score
        predictions.sort(key=lambda x: x.composite_score or 0, reverse=True)

        return predictions

    def _get_real_model_predictions(self, horse_data: pd.Series) -> Dict[str, float]:
        """Get predictions from real trained models"""
        real_preds = {}

        if not self.real_models:
            return real_preds

        try:
            # Prepare features for real models (simplified)
            features = self._prepare_real_features(horse_data)

            # Random Forest
            if "rf" in self.real_models:
                real_preds["rf"] = float(
                    self.real_models["rf"].predict_proba(features.reshape(1, -1))[0, 1]
                )

            # Gradient Boosting
            if "gb" in self.real_models:
                real_preds["gb"] = float(
                    self.real_models["gb"].predict_proba(features.reshape(1, -1))[0, 1]
                )

            # Neural Network (needs scaling)
            if "nn" in self.real_models and "feature_scaler" in self.real_scalers:
                features_scaled = self.real_scalers["feature_scaler"].transform(
                    features.reshape(1, -1)
                )
                real_preds["nn"] = float(
                    self.real_models["nn"].predict_proba(features_scaled)[0, 1]
                )

            # Logistic Regression
            if "lr" in self.real_models:
                real_preds["lr"] = float(
                    self.real_models["lr"].predict_proba(features.reshape(1, -1))[0, 1]
                )

            # Ensemble (average of available predictions)
            if real_preds:
                real_preds["ensemble"] = np.mean(list(real_preds.values()))

        except Exception as e:
            logger.warning(f"Real model prediction failed: {e}")

        return real_preds

    def _prepare_real_features(self, horse_data: pd.Series) -> np.ndarray:
        """Prepare features for real models (simplified version)"""
        # Use available features that match our real model training
        features = [
            horse_data.get("horse_age", 4),
            horse_data.get("horse_weight_kg", 57),
            horse_data.get("draw", 8),
            horse_data.get("field_size", 12),
            horse_data.get("log_odds", 1.5),
            horse_data.get("odds_rank", 6),
            horse_data.get("odds_percentile", 0.5),
            horse_data.get("is_favorite", 0),
            horse_data.get("is_outsider", 0),
            horse_data.get("market_strength", 0.2),
            horse_data.get("market_share", 0.08),
            horse_data.get("draw_percentile", 0.5),
            horse_data.get("weight_percentile", 0.5),
            horse_data.get("age_percentile", 0.5),
            horse_data.get("recent_form_rating", 75),
            horse_data.get("speed_rating", 78),
            horse_data.get("class_rating", 76),
            horse_data.get("track_rating", 74),
            horse_data.get("distance_rating", 77),
            horse_data.get("jockey_rating", 75),
            horse_data.get("trainer_rating", 76),
            horse_data.get("total_rating", 76),
            horse_data.get("form_rank", 6),
            horse_data.get("speed_rank", 6),
            horse_data.get("total_rating_rank", 6),
            horse_data.get("career_starts", 8),
            horse_data.get("career_wins", 1),
            horse_data.get("career_places", 3),
            horse_data.get("win_rate", 0.12),
            horse_data.get("place_rate", 0.35),
            horse_data.get("experience_score", 2.0),
            horse_data.get("days_since_last_run", 21),
            horse_data.get("freshness_score", 0.045),
            horse_data.get("recent_wins", 0),
            horse_data.get("recent_places", 1),
            horse_data.get("form_consistency", 3),
            horse_data.get("distance_numeric", 1600),
            horse_data.get("log_prize", 11.0),
            horse_data.get("prize_per_runner", 4000),
        ]

        return np.array(features[:40])  # Limit to expected number of features

    def _get_synthetic_prediction(self, horse_data: pd.Series) -> float:
        """Get prediction from synthetic ensemble"""
        try:
            # Prepare features for synthetic model
            features = self._prepare_synthetic_features(horse_data)
            features_selected = self.synthetic_feature_selector.transform(
                features.reshape(1, -1)
            )
            features_scaled = self.synthetic_scaler.transform(features_selected)

            return float(self.synthetic_ensemble.predict_proba(features_scaled)[0, 1])
        except:
            return 0.15  # Default probability

    def _prepare_synthetic_features(self, horse_data: pd.Series) -> np.ndarray:
        """Prepare features for synthetic models"""
        features = [
            horse_data.get("performance_index", 75),
            horse_data.get("value_indicator", 0.15),
            horse_data.get("market_confidence", 0.2),
            horse_data.get("class_advantage", 2),
            horse_data.get("competition_quality", 1.5),
            horse_data.get("form_momentum", 1.0),
            horse_data.get("consistency_factor", 0.6),
            horse_data.get("track_distance_combo", 55),
            horse_data.get("conditions_fit", 0.7),
            horse_data.get("connections_synergy", 56),
            horse_data.get("tactical_advantage", 0.4),
            horse_data.get("win_rate", 0.12),
            horse_data.get("odds_rank", 6),
            horse_data.get("total_rating", 76),
            horse_data.get("morning_line_odds", 5.0),
        ]

        return np.array(features)

    def _create_composite_score(
        self, real_preds: Dict[str, float], synthetic_pred: float
    ) -> float:
        """Create composite score from real and synthetic predictions"""

        if real_preds and "ensemble" in real_preds:
            # Weight real models more heavily (they're trained on actual data)
            composite = real_preds["ensemble"] * 0.7 + synthetic_pred * 0.3
        else:
            # Fall back to synthetic only
            composite = synthetic_pred

        return min(0.95, max(0.01, composite))

    def _get_confidence_level(self, score: float) -> str:
        """Determine confidence level"""
        if score >= 0.5:
            return "Very High"
        elif score >= 0.3:
            return "High"
        elif score >= 0.15:
            return "Moderate"
        else:
            return "Low"

    def _assess_value(self, win_prob: float, implied_prob: float) -> str:
        """Assess betting value"""
        if win_prob > implied_prob * 1.3:
            return "Excellent Value"
        elif win_prob > implied_prob * 1.15:
            return "Good Value"
        elif win_prob > implied_prob * 1.05:
            return "Fair Value"
        else:
            return "Poor Value"

    def display_comprehensive_results(self, predictions: List[EnhancedPrediction]):
        """Display comprehensive prediction results"""
        print("\n" + "=" * 100)
        print("🏇 ENHANCED ML HORSE RACING PREDICTIONS")
        print("=" * 100)

        for i, pred in enumerate(predictions, 1):
            print(f"\n{i}. {pred.horse_name}")
            print(f"   🎯 Win Probability: {pred.win_probability:.1%}")
            print(f"   🥉 Place Probability: {pred.place_probability:.1%}")
            print(f"   🏆 Composite Score: {pred.composite_score:.1%}")
            print(f"   📊 Confidence: {pred.confidence_level}")
            print(f"   💰 Value Assessment: {pred.value_assessment}")
            print(
                f"   📈 Odds: {pred.odds:.1f} (Implied: {pred.implied_probability:.1%})"
            )

            if pred.value_bet:
                print(f"   💎 VALUE BET! 💎")

            # Real model breakdown
            if pred.real_ensemble_prob:
                print(
                    f"   🔧 Real Models: RF:{pred.real_rf_prob:.2%} GB:{pred.real_gb_prob:.2%} NN:{pred.real_nn_prob:.2%} LR:{pred.real_lr_prob:.2%}"
                )
                print(f"   🎯 Real Ensemble: {pred.real_ensemble_prob:.2%}")

            if pred.synthetic_ml_prob:
                print(f"   🧠 Synthetic ML: {pred.synthetic_ml_prob:.2%}")


def main():
    """Run enhanced ML integration demonstration"""
    logger.info("🚀 STARTING ENHANCED ML INTEGRATION DEMO")
    logger.info("=" * 70)

    # Initialize system
    system = EnhancedMLIntegrationSystem()

    # Create comprehensive dataset
    X, y = system.create_comprehensive_dataset(num_samples=6000)

    # Train enhanced models
    results = system.train_enhanced_models(X, y)

    # Display training results
    print("\n📊 TRAINING RESULTS")
    print("-" * 60)
    print("Real Model Performance (from actual training):")
    for name, perf in results["real_performance"].items():
        print(
            f"   📈 {name}: AUC {perf['roc_auc']:.4f}, Accuracy {perf['accuracy']:.4f}"
        )

    print(f"\nSynthetic Model Performance:")
    for name, result in results["synthetic_results"].items():
        if "test_auc" in result:
            print(f"   📈 {name}: Test AUC {result['test_auc']:.4f}")

    print(f"\n🏆 Best Synthetic Model: {results['best_synthetic']}")

    # Show feature importance
    if results["feature_importance"]:
        print("\n🔍 TOP SYNTHETIC FEATURES:")
        sorted_features = sorted(
            results["feature_importance"].items(), key=lambda x: x[1], reverse=True
        )[:10]
        for feature, importance in sorted_features:
            print(f"   • {feature}: {importance:.4f}")

    # Generate sample race for prediction
    race_data = X.sample(10).copy()
    race_data["horse_name"] = [f"Racehorse_{i+1}" for i in range(len(race_data))]

    # Make comprehensive predictions
    predictions = system.predict_race_comprehensive(race_data)

    # Display results
    system.display_comprehensive_results(predictions)

    logger.info("\n🎉 ENHANCED ML INTEGRATION DEMO COMPLETE!")


if __name__ == "__main__":
    main()
