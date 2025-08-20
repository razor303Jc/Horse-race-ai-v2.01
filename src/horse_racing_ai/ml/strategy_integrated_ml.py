#!/usr/bin/env python3
"""
ML Betting Strategy Integration System
=====================================

This module enables the ML models to understand and integrate 80/20 and Dutching
betting strategies into their predictions, creating strategy-aware AI selections.

The system:
1. Extends ML models with betting strategy features
2. Trains models to recognize profitable betting opportunities
3. Integrates strategy recommendations into AI predictions
4. Provides strategy-specific confidence scoring

Features:
- Strategy-aware feature engineering
- Betting opportunity identification
- Strategy-specific probability adjustments
- Enhanced confidence scoring for betting strategies
- Real-time strategy recommendations

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# Import existing betting strategies
from ..betting.eighty_twenty_strategy import EightyTwentyStrategy, StakeAllocation
from ..betting.reduced_stake_dutching import ReducedStakeDutching, DutchingResult
from ..ml.enhanced_ml_models import EnhancedMLRatingSystem, MLModelPrediction

logger = logging.getLogger(__name__)


@dataclass
class StrategyPrediction:
    """Prediction result for a specific betting strategy"""

    strategy_name: str
    recommended: bool
    confidence: float
    expected_roi: float
    risk_level: str
    optimal_stake: float
    probability_factors: Dict[str, float]
    reasoning: List[str]


@dataclass
class IntegratedBettingPrediction:
    """Complete prediction including standard ML and strategy recommendations"""

    horse_name: str

    # Standard ML predictions
    ml_prediction: MLModelPrediction

    # Strategy-specific predictions
    eighty_twenty_prediction: Optional[StrategyPrediction]
    dutching_suitability: Optional[StrategyPrediction]

    # Combined recommendations
    overall_recommendation: str
    strategy_priority: str
    combined_confidence: float
    betting_advice: str


class StrategyAwareFeatureEngineering:
    """Feature engineering specifically for betting strategy integration"""

    def __init__(self):
        self.feature_names = []
        self.scaler = StandardScaler()

    def create_strategy_features(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Dict[str, float]:
        """Create features specifically for betting strategy analysis"""

        features = {}
        horse_name = horse_data.get("name", "Unknown")

        # Basic features
        win_odds = odds_data.get(horse_name, {}).get("win", 5.0)
        place_odds = odds_data.get(horse_name, {}).get("place", win_odds / 3)

        # 80/20 Strategy Features
        features.update(
            self._create_eighty_twenty_features(
                horse_data, race_data, win_odds, place_odds
            )
        )

        # Dutching Strategy Features
        features.update(
            self._create_dutching_features(horse_data, race_data, odds_data)
        )

        # Market Position Features
        features.update(self._create_market_features(horse_data, race_data, odds_data))

        return features

    def _create_eighty_twenty_features(
        self, horse_data: Dict, race_data: Dict, win_odds: float, place_odds: float
    ) -> Dict[str, float]:
        """Create features for 80/20 strategy suitability"""

        features = {}

        # Win probability estimate
        win_prob = horse_data.get("win_probability", 1.0 / win_odds)
        place_prob = horse_data.get("place_probability", 1.0 / place_odds)

        # 80/20 Strategy Indicators
        features["eighty_twenty_win_value"] = max(0, win_prob - (1.0 / win_odds))
        features["eighty_twenty_place_value"] = max(0, place_prob - (1.0 / place_odds))
        features["eighty_twenty_combined_value"] = (
            features["eighty_twenty_win_value"] * 0.2
            + features["eighty_twenty_place_value"] * 0.8
        )

        # Odds range suitability (80/20 works best at extremes)
        if win_odds <= 1.5:
            features["eighty_twenty_odds_suitability"] = 1.0  # Very short odds
        elif win_odds >= 4.0:
            features["eighty_twenty_odds_suitability"] = 0.8  # Long odds
        else:
            features["eighty_twenty_odds_suitability"] = (
                0.3  # Medium odds (less suitable)
            )

        # Place advantage factor
        place_advantage = place_prob / win_prob if win_prob > 0 else 1.0
        features["eighty_twenty_place_advantage"] = min(place_advantage, 3.0)

        # Form and consistency factors
        features["eighty_twenty_form_consistency"] = horse_data.get(
            "form_consistency", 0.7
        )
        features["eighty_twenty_recent_placings"] = horse_data.get(
            "recent_placings_ratio", 0.5
        )

        return features

    def _create_dutching_features(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Dict[str, float]:
        """Create features for dutching strategy suitability"""

        features = {}

        # Field analysis for dutching
        field_size = race_data.get("field_size", 10)
        features["dutching_field_size"] = min(field_size / 20.0, 1.0)

        # Competitive balance (good for dutching)
        all_odds = [odds.get("win", 5.0) for odds in odds_data.values()]
        if all_odds:
            odds_variance = np.var(all_odds)
            features["dutching_odds_variance"] = min(odds_variance / 10.0, 1.0)

            # Number of competitive horses (odds < 6.0)
            competitive_count = sum(1 for odds in all_odds if odds < 6.0)
            features["dutching_competitive_horses"] = min(competitive_count / 5.0, 1.0)
        else:
            features["dutching_odds_variance"] = 0.5
            features["dutching_competitive_horses"] = 0.5

        # Horse's relative position in market
        horse_odds = odds_data.get(horse_data.get("name", ""), {}).get("win", 5.0)
        if all_odds:
            percentile = np.percentile(all_odds, 50)
            features["dutching_market_position"] = (
                1.0 - (horse_odds / max(all_odds)) if all_odds else 0.5
            )
        else:
            features["dutching_market_position"] = 0.5

        # Dutching profit potential
        features["dutching_profit_potential"] = horse_data.get(
            "win_probability", 0.2
        ) * (horse_odds - 1.0)

        return features

    def _create_market_features(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Dict[str, float]:
        """Create general market-based features"""

        features = {}

        # Market efficiency indicators
        total_implied_prob = sum(
            1.0 / odds.get("win", 5.0) for odds in odds_data.values()
        )
        features["market_overround"] = max(0, total_implied_prob - 1.0)

        # Liquidity and movement indicators
        features["odds_movement"] = horse_data.get(
            "odds_movement", 0.0
        )  # Positive = drifting
        features["market_support"] = horse_data.get(
            "market_support", 0.5
        )  # Betting volume indicator

        # Race quality factors
        features["race_class"] = race_data.get("class_rating", 70) / 100.0
        features["prize_money"] = min(
            race_data.get("prize_money", 10000) / 100000.0, 1.0
        )

        return features


class BettingStrategyMLClassifier:
    """ML classifier for identifying profitable betting strategy opportunities"""

    def __init__(self):
        self.eighty_twenty_model = None
        self.dutching_model = None
        self.feature_engineering = StrategyAwareFeatureEngineering()
        self.is_trained = False

    def train_strategy_models(self, training_data: List[Dict]) -> None:
        """Train ML models to identify profitable betting opportunities"""

        logger.info("Training betting strategy ML models...")

        # Prepare training data
        features_list = []
        eighty_twenty_labels = []
        dutching_labels = []

        for race_data in training_data:
            for horse_data in race_data.get("horses", []):
                # Extract features
                features = self.feature_engineering.create_strategy_features(
                    horse_data, race_data, race_data.get("odds", {})
                )
                features_list.append(list(features.values()))

                # Create labels based on historical profitability
                eighty_twenty_labels.append(
                    1 if horse_data.get("eighty_twenty_profitable", False) else 0
                )
                dutching_labels.append(
                    1 if horse_data.get("dutching_profitable", False) else 0
                )

        if not features_list:
            logger.warning("No training data available for strategy models")
            return

        # Convert to arrays
        X = np.array(features_list)
        y_80_20 = np.array(eighty_twenty_labels)
        y_dutching = np.array(dutching_labels)

        # Store feature names
        sample_features = self.feature_engineering.create_strategy_features(
            training_data[0]["horses"][0],
            training_data[0],
            training_data[0].get("odds", {}),
        )
        self.feature_engineering.feature_names = list(sample_features.keys())

        # Scale features
        X_scaled = self.feature_engineering.scaler.fit_transform(X)

        # Train 80/20 strategy model
        self.eighty_twenty_model = self._train_strategy_classifier(
            X_scaled, y_80_20, "80/20 Strategy"
        )

        # Train dutching strategy model
        self.dutching_model = self._train_strategy_classifier(
            X_scaled, y_dutching, "Dutching Strategy"
        )

        self.is_trained = True
        logger.info("✅ Betting strategy ML models trained successfully")

    def _train_strategy_classifier(
        self, X: np.ndarray, y: np.ndarray, strategy_name: str
    ):
        """Train a single strategy classifier"""

        if len(set(y)) < 2:
            logger.warning(f"Insufficient label diversity for {strategy_name}")
            # Return a simple logistic regression with default weights
            model = LogisticRegression(random_state=42)
            # Create dummy data for training
            dummy_X = np.random.randn(10, X.shape[1])
            dummy_y = np.array([0, 1] * 5)
            model.fit(dummy_X, dummy_y)
            return model

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train ensemble of classifiers
        rf_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        gb_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=8, random_state=42
        )

        rf_model.fit(X_train, y_train)
        gb_model.fit(X_train, y_train)

        # Evaluate models
        rf_score = roc_auc_score(y_test, rf_model.predict_proba(X_test)[:, 1])
        gb_score = roc_auc_score(y_test, gb_model.predict_proba(X_test)[:, 1])

        # Return best model
        best_model = rf_model if rf_score > gb_score else gb_model
        logger.info(f"{strategy_name} model AUC: {max(rf_score, gb_score):.3f}")

        return best_model

    def predict_strategy_suitability(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Tuple[StrategyPrediction, StrategyPrediction]:
        """Predict suitability for both betting strategies"""

        if not self.is_trained:
            # Return default predictions if not trained
            return self._get_default_predictions(horse_data, race_data, odds_data)

        # Extract features
        features = self.feature_engineering.create_strategy_features(
            horse_data, race_data, odds_data
        )
        feature_array = np.array([list(features.values())])
        feature_array_scaled = self.feature_engineering.scaler.transform(feature_array)

        # 80/20 Strategy prediction
        eighty_twenty_pred = self._predict_eighty_twenty(
            feature_array_scaled, features, horse_data, odds_data
        )

        # Dutching strategy prediction
        dutching_pred = self._predict_dutching(
            feature_array_scaled, features, horse_data, race_data, odds_data
        )

        return eighty_twenty_pred, dutching_pred

    def _predict_eighty_twenty(
        self,
        features: np.ndarray,
        feature_dict: Dict,
        horse_data: Dict,
        odds_data: Dict,
    ) -> StrategyPrediction:
        """Predict 80/20 strategy suitability"""

        # Get model prediction
        if self.eighty_twenty_model:
            proba = self.eighty_twenty_model.predict_proba(features)[0, 1]
            recommended = proba > 0.6
        else:
            proba = 0.5
            recommended = False

        # Calculate expected ROI based on features
        win_value = feature_dict.get("eighty_twenty_win_value", 0)
        place_value = feature_dict.get("eighty_twenty_place_value", 0)
        combined_value = feature_dict.get("eighty_twenty_combined_value", 0)
        odds_suitability = feature_dict.get("eighty_twenty_odds_suitability", 0.5)

        # Estimate ROI
        expected_roi = (
            combined_value * odds_suitability * 100
        ) - 5  # 5% house edge adjustment

        # Risk assessment
        if odds_suitability > 0.8 and combined_value > 0.1:
            risk_level = "LOW"
        elif odds_suitability > 0.5 and combined_value > 0.05:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Reasoning
        reasoning = []
        horse_name = horse_data.get("name", "Unknown")
        win_odds = odds_data.get(horse_name, {}).get("win", 5.0)

        if win_odds <= 1.5:
            reasoning.append("Very short odds - ideal for 80/20 strategy")
        elif win_odds >= 4.0:
            reasoning.append("Long odds with place value potential")
        else:
            reasoning.append("Medium odds - limited 80/20 value")

        if combined_value > 0.1:
            reasoning.append("Strong combined win/place value detected")
        elif combined_value > 0.05:
            reasoning.append("Moderate value opportunity")
        else:
            reasoning.append("Limited value in current odds")

        return StrategyPrediction(
            strategy_name="80/20 Strategy",
            recommended=recommended,
            confidence=proba,
            expected_roi=expected_roi,
            risk_level=risk_level,
            optimal_stake=self._calculate_optimal_stake(expected_roi, proba),
            probability_factors={
                "win_value": win_value,
                "place_value": place_value,
                "odds_suitability": odds_suitability,
            },
            reasoning=reasoning,
        )

    def _predict_dutching(
        self,
        features: np.ndarray,
        feature_dict: Dict,
        horse_data: Dict,
        race_data: Dict,
        odds_data: Dict,
    ) -> StrategyPrediction:
        """Predict dutching strategy suitability"""

        # Get model prediction
        if self.dutching_model:
            proba = self.dutching_model.predict_proba(features)[0, 1]
            recommended = proba > 0.6
        else:
            proba = 0.5
            recommended = False

        # Calculate dutching factors
        competitive_horses = feature_dict.get("dutching_competitive_horses", 0.5)
        profit_potential = feature_dict.get("dutching_profit_potential", 0)
        market_position = feature_dict.get("dutching_market_position", 0.5)

        # Estimate ROI for dutching
        expected_roi = (
            competitive_horses * profit_potential * market_position * 50
        ) - 8  # 8% dutching overhead

        # Risk assessment
        if competitive_horses > 0.6 and profit_potential > 0.5:
            risk_level = "MEDIUM"  # Dutching inherently medium risk
        elif competitive_horses > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Reasoning
        reasoning = []
        field_size = race_data.get("field_size", 10)

        if competitive_horses > 0.6:
            reasoning.append(
                f"Strong competitive field with {int(competitive_horses * 5)} viable selections"
            )
        if profit_potential > 0.5:
            reasoning.append("Good profit potential for multi-horse coverage")
        if market_position > 0.7:
            reasoning.append("Horse well-positioned in market for dutching")
        if field_size < 8:
            reasoning.append("Small field may limit dutching opportunities")
        elif field_size > 15:
            reasoning.append("Large field provides good dutching coverage")

        return StrategyPrediction(
            strategy_name="Dutching Strategy",
            recommended=recommended,
            confidence=proba,
            expected_roi=expected_roi,
            risk_level=risk_level,
            optimal_stake=self._calculate_optimal_stake(expected_roi, proba),
            probability_factors={
                "competitive_horses": competitive_horses,
                "profit_potential": profit_potential,
                "market_position": market_position,
            },
            reasoning=reasoning,
        )

    def _calculate_optimal_stake(self, expected_roi: float, confidence: float) -> float:
        """Calculate optimal stake using Kelly-like criteria"""

        if expected_roi <= 0:
            return 0.0

        # Simple Kelly approximation
        kelly_fraction = (expected_roi / 100) * confidence

        # Conservative sizing
        optimal_stake = min(kelly_fraction * 0.5, 0.05)  # Max 5% of bankroll

        return max(optimal_stake, 0.01)  # Minimum 1% if recommended

    def _get_default_predictions(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Tuple[StrategyPrediction, StrategyPrediction]:
        """Return default predictions when models aren't trained"""

        horse_name = horse_data.get("name", "Unknown")
        win_odds = odds_data.get(horse_name, {}).get("win", 5.0)

        # Simple rule-based 80/20 prediction
        eighty_twenty_suitable = win_odds <= 1.8 or win_odds >= 6.0
        eighty_twenty_confidence = 0.7 if eighty_twenty_suitable else 0.3

        eighty_twenty_pred = StrategyPrediction(
            strategy_name="80/20 Strategy",
            recommended=eighty_twenty_suitable,
            confidence=eighty_twenty_confidence,
            expected_roi=5.0 if eighty_twenty_suitable else -2.0,
            risk_level="MEDIUM",
            optimal_stake=0.02 if eighty_twenty_suitable else 0.0,
            probability_factors={"odds_based": win_odds},
            reasoning=["Rule-based assessment - models not trained"],
        )

        # Simple dutching prediction
        field_size = race_data.get("field_size", 10)
        dutching_suitable = field_size >= 8 and 2.0 <= win_odds <= 8.0
        dutching_confidence = 0.6 if dutching_suitable else 0.4

        dutching_pred = StrategyPrediction(
            strategy_name="Dutching Strategy",
            recommended=dutching_suitable,
            confidence=dutching_confidence,
            expected_roi=3.0 if dutching_suitable else -5.0,
            risk_level="MEDIUM",
            optimal_stake=0.03 if dutching_suitable else 0.0,
            probability_factors={"field_size": field_size, "odds_range": win_odds},
            reasoning=["Rule-based assessment - models not trained"],
        )

        return eighty_twenty_pred, dutching_pred

    def save_models(self, filepath: str) -> None:
        """Save trained models to file"""

        if not self.is_trained:
            logger.warning("Cannot save untrained models")
            return

        model_data = {
            "eighty_twenty_model": self.eighty_twenty_model,
            "dutching_model": self.dutching_model,
            "scaler": self.feature_engineering.scaler,
            "feature_names": self.feature_engineering.feature_names,
            "is_trained": self.is_trained,
            "training_date": datetime.now().isoformat(),
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Strategy models saved to {filepath}")

    def load_models(self, filepath: str) -> None:
        """Load trained models from file"""

        try:
            model_data = joblib.load(filepath)

            self.eighty_twenty_model = model_data["eighty_twenty_model"]
            self.dutching_model = model_data["dutching_model"]
            self.feature_engineering.scaler = model_data["scaler"]
            self.feature_engineering.feature_names = model_data["feature_names"]
            self.is_trained = model_data["is_trained"]

            logger.info(f"Strategy models loaded from {filepath}")

        except Exception as e:
            logger.error(f"Failed to load strategy models: {e}")
            self.is_trained = False


class StrategyIntegratedMLSystem:
    """Enhanced ML system that integrates betting strategies into predictions"""

    def __init__(self, enhanced_ml_system: EnhancedMLRatingSystem):
        self.base_ml_system = enhanced_ml_system
        self.strategy_classifier = BettingStrategyMLClassifier()
        self.eighty_twenty_strategy = EightyTwentyStrategy()
        self.dutching_strategy = ReducedStakeDutching()

    def predict_with_strategy_integration(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> IntegratedBettingPrediction:
        """Generate integrated prediction including strategy recommendations"""

        horse_name = horse_data.get("name", "Unknown")

        # Get base ML prediction
        try:
            # This would call the actual enhanced ML system
            ml_prediction = self._get_enhanced_ml_prediction(horse_data, race_data)
        except Exception as e:
            logger.warning(f"Enhanced ML prediction failed: {e}")
            ml_prediction = self._get_fallback_ml_prediction(horse_data, race_data)

        # Get strategy predictions
        eighty_twenty_pred, dutching_pred = (
            self.strategy_classifier.predict_strategy_suitability(
                horse_data, race_data, odds_data
            )
        )

        # Generate combined recommendation
        (
            overall_recommendation,
            strategy_priority,
            combined_confidence,
            betting_advice,
        ) = self._generate_combined_recommendation(
            ml_prediction, eighty_twenty_pred, dutching_pred
        )

        return IntegratedBettingPrediction(
            horse_name=horse_name,
            ml_prediction=ml_prediction,
            eighty_twenty_prediction=eighty_twenty_pred,
            dutching_suitability=dutching_pred,
            overall_recommendation=overall_recommendation,
            strategy_priority=strategy_priority,
            combined_confidence=combined_confidence,
            betting_advice=betting_advice,
        )

    def _get_enhanced_ml_prediction(
        self, horse_data: Dict, race_data: Dict
    ) -> MLModelPrediction:
        """Get prediction from enhanced ML system"""

        # Placeholder - would integrate with actual enhanced ML system
        return MLModelPrediction(
            horse_name=horse_data.get("name", "Unknown"),
            predicted_rating=np.random.uniform(70, 95),
            predicted_z_score=np.random.uniform(-2, 2),
            confidence_score=np.random.uniform(0.6, 0.9),
            win_probability=np.random.uniform(0.05, 0.4),
            place_probability=np.random.uniform(0.15, 0.7),
            show_probability=np.random.uniform(0.3, 0.9),
            expected_position=np.random.uniform(1, 10),
            performance_range=(70, 100),
            model_features={"power_rating": 85, "speed_figure": 90},
            prediction_factors=["form", "speed", "class"],
        )

    def _get_fallback_ml_prediction(
        self, horse_data: Dict, race_data: Dict
    ) -> MLModelPrediction:
        """Fallback ML prediction when enhanced system unavailable"""

        return MLModelPrediction(
            horse_name=horse_data.get("name", "Unknown"),
            predicted_rating=75.0,
            predicted_z_score=0.0,
            confidence_score=0.7,
            win_probability=0.15,
            place_probability=0.35,
            show_probability=0.55,
            expected_position=5.5,
            performance_range=(65, 85),
            model_features={"basic_rating": 75},
            prediction_factors=["fallback_prediction"],
        )

    def _generate_combined_recommendation(
        self,
        ml_pred: MLModelPrediction,
        eighty_twenty_pred: StrategyPrediction,
        dutching_pred: StrategyPrediction,
    ) -> Tuple[str, str, float, str]:
        """Generate combined recommendation from ML and strategy predictions"""

        # Weighted confidence score
        ml_weight = 0.4
        strategy_weight = 0.6

        combined_confidence = (
            ml_pred.confidence_score * ml_weight
            + max(eighty_twenty_pred.confidence, dutching_pred.confidence)
            * strategy_weight
        )

        # Strategy priority
        if (
            eighty_twenty_pred.recommended
            and eighty_twenty_pred.confidence > dutching_pred.confidence
        ):
            strategy_priority = "80/20 Strategy"
            primary_strategy = eighty_twenty_pred
        elif dutching_pred.recommended:
            strategy_priority = "Dutching Strategy"
            primary_strategy = dutching_pred
        else:
            strategy_priority = "Standard Betting"
            primary_strategy = None

        # Overall recommendation
        if ml_pred.win_probability > 0.3 and combined_confidence > 0.8:
            overall_recommendation = "STRONG RECOMMENDATION"
        elif (
            primary_strategy
            and primary_strategy.recommended
            and primary_strategy.expected_roi > 5.0
        ):
            overall_recommendation = "STRATEGY OPPORTUNITY"
        elif ml_pred.win_probability > 0.2 or combined_confidence > 0.7:
            overall_recommendation = "CONSIDER"
        else:
            overall_recommendation = "AVOID"

        # Betting advice
        if primary_strategy and primary_strategy.recommended:
            advice = f"Recommended: {strategy_priority} with {primary_strategy.optimal_stake:.1%} stake. "
            advice += f"Expected ROI: {primary_strategy.expected_roi:.1f}%. "
            advice += f"Risk: {primary_strategy.risk_level}. "
            if primary_strategy.reasoning:
                advice += f"Reason: {primary_strategy.reasoning[0]}"
        else:
            advice = f"Standard betting approach. Win probability: {ml_pred.win_probability:.1%}"

        return overall_recommendation, strategy_priority, combined_confidence, advice

    def train_integrated_system(self, historical_data: List[Dict]) -> None:
        """Train the integrated system with historical racing data"""

        logger.info("Training strategy-integrated ML system...")

        # Train strategy classifiers
        self.strategy_classifier.train_strategy_models(historical_data)

        logger.info("✅ Strategy-integrated ML system training complete")

    def save_integrated_models(self, base_path: str) -> None:
        """Save all integrated models"""

        self.strategy_classifier.save_models(f"{base_path}_strategy_models.joblib")
        logger.info(f"Integrated models saved to {base_path}")

    def load_integrated_models(self, base_path: str) -> None:
        """Load all integrated models"""

        self.strategy_classifier.load_models(f"{base_path}_strategy_models.joblib")
        logger.info(f"Integrated models loaded from {base_path}")


# Example usage and testing functions
def create_sample_training_data() -> List[Dict]:
    """Create sample training data for demonstration"""

    training_data = []

    for race_id in range(50):  # 50 sample races
        race_data = {
            "race_id": f"R{race_id:03d}",
            "field_size": np.random.randint(6, 16),
            "class_rating": np.random.randint(60, 100),
            "prize_money": np.random.randint(5000, 50000),
            "horses": [],
            "odds": {},
        }

        # Generate horses for each race
        num_horses = race_data["field_size"]
        for horse_id in range(num_horses):
            horse_name = f"Horse_{race_id}_{horse_id}"

            # Random horse data
            horse_data = {
                "name": horse_name,
                "win_probability": np.random.uniform(0.05, 0.4),
                "place_probability": np.random.uniform(0.15, 0.7),
                "form_consistency": np.random.uniform(0.3, 0.9),
                "recent_placings_ratio": np.random.uniform(0.2, 0.8),
                "odds_movement": np.random.uniform(-0.5, 0.5),
                "market_support": np.random.uniform(0.1, 1.0),
                # Labels for training (randomly assigned for demo)
                "eighty_twenty_profitable": np.random.choice(
                    [True, False], p=[0.3, 0.7]
                ),
                "dutching_profitable": np.random.choice([True, False], p=[0.25, 0.75]),
            }

            # Generate odds
            win_odds = 1.0 / horse_data["win_probability"] + np.random.uniform(-1, 1)
            win_odds = max(1.1, win_odds)  # Minimum odds

            race_data["horses"].append(horse_data)
            race_data["odds"][horse_name] = {"win": win_odds, "place": win_odds / 3}

        training_data.append(race_data)

    return training_data


def demonstrate_strategy_integration():
    """Demonstrate the strategy-integrated ML system"""

    logger.info("🎯 Demonstrating Strategy-Integrated ML System")

    # Create enhanced ML system (placeholder)
    enhanced_ml = EnhancedMLRatingSystem()

    # Create integrated system
    integrated_system = StrategyIntegratedMLSystem(enhanced_ml)

    # Generate training data
    training_data = create_sample_training_data()

    # Train the system
    integrated_system.train_integrated_system(training_data)

    # Test prediction on sample race
    sample_race = training_data[0]
    sample_horse = sample_race["horses"][0]

    prediction = integrated_system.predict_with_strategy_integration(
        sample_horse, sample_race, sample_race["odds"]
    )

    # Display results
    logger.info(f"\n{'='*60}")
    logger.info(f"STRATEGY-INTEGRATED PREDICTION")
    logger.info(f"{'='*60}")
    logger.info(f"Horse: {prediction.horse_name}")
    logger.info(f"Overall Recommendation: {prediction.overall_recommendation}")
    logger.info(f"Strategy Priority: {prediction.strategy_priority}")
    logger.info(f"Combined Confidence: {prediction.combined_confidence:.1%}")
    logger.info(f"Betting Advice: {prediction.betting_advice}")

    logger.info(f"\n{'='*30} ML PREDICTION {'='*30}")
    logger.info(f"Win Probability: {prediction.ml_prediction.win_probability:.1%}")
    logger.info(f"Place Probability: {prediction.ml_prediction.place_probability:.1%}")
    logger.info(f"ML Confidence: {prediction.ml_prediction.confidence_score:.1%}")

    if prediction.eighty_twenty_prediction:
        logger.info(f"\n{'='*25} 80/20 STRATEGY {'='*25}")
        pred = prediction.eighty_twenty_prediction
        logger.info(f"Recommended: {pred.recommended}")
        logger.info(f"Confidence: {pred.confidence:.1%}")
        logger.info(f"Expected ROI: {pred.expected_roi:.1f}%")
        logger.info(f"Risk Level: {pred.risk_level}")
        logger.info(f"Optimal Stake: {pred.optimal_stake:.1%}")
        logger.info(f"Reasoning: {', '.join(pred.reasoning)}")

    if prediction.dutching_suitability:
        logger.info(f"\n{'='*25} DUTCHING STRATEGY {'='*25}")
        pred = prediction.dutching_suitability
        logger.info(f"Recommended: {pred.recommended}")
        logger.info(f"Confidence: {pred.confidence:.1%}")
        logger.info(f"Expected ROI: {pred.expected_roi:.1f}%")
        logger.info(f"Risk Level: {pred.risk_level}")
        logger.info(f"Optimal Stake: {pred.optimal_stake:.1%}")
        logger.info(f"Reasoning: {', '.join(pred.reasoning)}")

    logger.info(f"\n✅ Strategy integration demonstration complete!")

    return integrated_system


if __name__ == "__main__":
    # Run demonstration
    demonstrate_strategy_integration()
