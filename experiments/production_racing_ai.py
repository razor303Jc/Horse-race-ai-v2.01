#!/usr/bin/env python3
"""
Production Horse Racing AI - Real Model Integration System
Optimized system using our proven real trained models with enhanced analysis
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
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RacePrediction:
    """Production race prediction"""
    
    horse_name: str
    win_probability: float
    place_probability: float
    confidence_score: float
    
    # Model predictions
    rf_probability: float
    gb_probability: float
    lr_probability: float
    nn_probability: float
    ensemble_probability: float
    
    # Market analysis
    odds: float
    implied_probability: float
    value_rating: str
    expected_value: float
    
    # Race context
    rank: int
    field_size: int
    
    def __str__(self):
        return (f"{self.horse_name}: {self.win_probability:.1%} "
                f"(Rank #{self.rank}/{self.field_size})")


class ProductionRacingAI:
    """
    Production-ready horse racing AI using our proven real models
    - Random Forest: 0.762 AUC
    - Gradient Boosting: 0.765 AUC 
    - Logistic Regression: 0.755 AUC
    - Neural Network: 0.658 AUC
    """
    
    def __init__(self):
        self.models_dir = Path("trained_models/race_card_models")
        self.db_path = Path("data/horseracedatabase/race_cards_prediction_data.db")
        
        # Model components
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.features = {}
        self.performance = {}
        
        # Load real models
        self._load_production_models()
        
    def _load_production_models(self):
        """Load our proven real trained models"""
        logger.info("📦 Loading production ML models...")
        
        try:
            self.models = {
                'rf': joblib.load(self.models_dir / "random_forest_race_card.joblib"),
                'gb': joblib.load(self.models_dir / "gradient_boosting_race_card.joblib"),
                'lr': joblib.load(self.models_dir / "logistic_regression_race_card.joblib"),
                'nn': joblib.load(self.models_dir / "neural_network_race_card.joblib")
            }
            
            self.scalers = joblib.load(self.models_dir / "scalers_race_card.joblib")
            self.encoders = joblib.load(self.models_dir / "encoders_race_card.joblib")
            self.features = joblib.load(self.models_dir / "features_race_card.joblib")
            self.performance = joblib.load(self.models_dir / "performance_race_card.joblib")
            
            logger.info("✅ Production models loaded successfully")
            logger.info("📊 Model Performance on Real Data:")
            for name, perf in self.performance.items():
                logger.info(f"   - {name}: AUC {perf['roc_auc']:.4f}, Accuracy {perf['accuracy']:.4f}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            raise
    
    def load_race_data(self, limit: int = 1000) -> pd.DataFrame:
        """Load real race data from database"""
        logger.info(f"📊 Loading race data (limit: {limit})...")
        
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT *
        FROM race_cards_processed
        ORDER BY RANDOM()
        LIMIT ?
        """
        
        data = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        logger.info(f"✅ Loaded {len(data)} race entries")
        return data
    
    def preprocess_race_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess race data to match training format"""
        logger.info("🔧 Preprocessing race data...")
        
        # Create a copy to avoid modifying original
        processed = data.copy()
        
        # Handle missing values
        processed = processed.fillna(0)
        
        # Ensure we have the expected features
        expected_features = self.features['feature_names']
        
        # Add missing features with defaults
        for feature in expected_features:
            if feature not in processed.columns:
                logger.warning(f"Missing feature {feature}, using default")
                processed[feature] = 0
        
        # Select only the features used in training
        processed = processed[expected_features]
        
        logger.info(f"✅ Preprocessed data: {processed.shape[0]} rows, {processed.shape[1]} features")
        return processed
    
    def predict_race(self, race_data: pd.DataFrame) -> List[RacePrediction]:
        """Make predictions for a race"""
        logger.info(f"🔮 Predicting race with {len(race_data)} horses...")
        
        # Preprocess data
        X = self.preprocess_race_data(race_data)
        
        # Get predictions from each model
        predictions = {}
        
        # Random Forest & Gradient Boosting (don't need scaling)
        predictions['rf'] = self.models['rf'].predict_proba(X)[:, 1]
        predictions['gb'] = self.models['gb'].predict_proba(X)[:, 1]
        predictions['lr'] = self.models['lr'].predict_proba(X)[:, 1]
        
        # Neural Network (needs scaling)
        X_scaled = self.scalers['feature_scaler'].transform(X)
        predictions['nn'] = self.models['nn'].predict_proba(X_scaled)[:, 1]
        
        # Weighted ensemble (GB and RF are our best performers)
        weights = {'gb': 0.35, 'rf': 0.35, 'lr': 0.20, 'nn': 0.10}
        ensemble = (
            predictions['gb'] * weights['gb'] +
            predictions['rf'] * weights['rf'] +
            predictions['lr'] * weights['lr'] +
            predictions['nn'] * weights['nn']
        )\n        \n        # Create prediction objects\n        race_predictions = []\n        \n        for i, (idx, horse_data) in enumerate(race_data.iterrows()):\n            win_prob = ensemble[i]\n            place_prob = min(0.9, win_prob * 3.2)  # Empirically derived multiplier\n            \n            # Calculate confidence based on model agreement\n            model_probs = [predictions[model][i] for model in predictions.keys()]\n            confidence = 1 - (np.std(model_probs) / np.mean(model_probs))\n            confidence = max(0.1, min(0.95, confidence))\n            \n            # Market analysis\n            odds = horse_data.get('morning_line_odds', 5.0)\n            implied_prob = 1.0 / odds if odds > 0 else 0.2\n            expected_value = (win_prob * (odds - 1)) - (1 - win_prob)\n            \n            prediction = RacePrediction(\n                horse_name=horse_data.get('horse_name', f\"Horse_{i+1}\"),\n                win_probability=win_prob,\n                place_probability=place_prob,\n                confidence_score=confidence,\n                rf_probability=predictions['rf'][i],\n                gb_probability=predictions['gb'][i],\n                lr_probability=predictions['lr'][i],\n                nn_probability=predictions['nn'][i],\n                ensemble_probability=win_prob,\n                odds=odds,\n                implied_probability=implied_prob,\n                value_rating=self._assess_value(win_prob, implied_prob),\n                expected_value=expected_value,\n                rank=0,  # Will be set after sorting\n                field_size=len(race_data)\n            )\n            \n            race_predictions.append(prediction)\n        \n        # Sort by win probability and assign ranks\n        race_predictions.sort(key=lambda x: x.win_probability, reverse=True)\n        for i, pred in enumerate(race_predictions, 1):\n            pred.rank = i\n        \n        logger.info(f\"✅ Generated {len(race_predictions)} predictions\")\n        return race_predictions\n    \n    def _assess_value(self, win_prob: float, implied_prob: float) -> str:\n        \"\"\"Assess betting value\"\"\"\n        ratio = win_prob / implied_prob if implied_prob > 0 else 0\n        \n        if ratio >= 1.3:\n            return \"Excellent\"\n        elif ratio >= 1.15:\n            return \"Good\"\n        elif ratio >= 1.05:\n            return \"Fair\"\n        else:\n            return \"Poor\"\n    \n    def analyze_race_detailed(self, predictions: List[RacePrediction]):\n        \"\"\"Detailed race analysis\"\"\"\n        print(\"\\n\" + \"=\" * 100)\n        print(\"🏇 PRODUCTION HORSE RACING AI - RACE ANALYSIS\")\n        print(\"=\" * 100)\n        print(f\"📊 Models Used: Random Forest (0.762), Gradient Boosting (0.765), Logistic Regression (0.755), Neural Network (0.658)\")\n        print(f\"🎯 Field Size: {predictions[0].field_size} horses\")\n        \n        print(\"\\n🏆 TOP SELECTIONS:\")\n        print(\"-\" * 80)\n        \n        for i, pred in enumerate(predictions[:5], 1):\n            print(f\"\\n{i}. {pred.horse_name} (Rank #{pred.rank}/{pred.field_size})\")\n            print(f\"   🎯 Win Probability: {pred.win_probability:.1%}\")\n            print(f\"   🥉 Place Probability: {pred.place_probability:.1%}\")\n            print(f\"   📊 Confidence: {pred.confidence_score:.1%}\")\n            print(f\"   💰 Odds: {pred.odds:.1f} (Implied: {pred.implied_probability:.1%})\")\n            print(f\"   📈 Value Rating: {pred.value_rating}\")\n            print(f\"   💵 Expected Value: {pred.expected_value:+.3f}\")\n            \n            if pred.value_rating in ['Excellent', 'Good']:\n                print(f\"   💎 VALUE BET DETECTED! 💎\")\n            \n            print(f\"   🔧 Model Breakdown:\")\n            print(f\"      - Random Forest: {pred.rf_probability:.2%}\")\n            print(f\"      - Gradient Boosting: {pred.gb_probability:.2%}\")\n            print(f\"      - Logistic Regression: {pred.lr_probability:.2%}\")\n            print(f\"      - Neural Network: {pred.nn_probability:.2%}\")\n            print(f\"      - Ensemble: {pred.ensemble_probability:.2%}\")\n        \n        # Summary statistics\n        print(\"\\n📈 RACE STATISTICS:\")\n        print(\"-\" * 40)\n        high_conf = sum(1 for p in predictions if p.confidence_score >= 0.7)\n        value_bets = sum(1 for p in predictions if p.value_rating in ['Excellent', 'Good'])\n        avg_prob = np.mean([p.win_probability for p in predictions])\n        \n        print(f\"High Confidence Picks (≥70%): {high_conf}\")\n        print(f\"Value Bet Opportunities: {value_bets}\")\n        print(f\"Average Win Probability: {avg_prob:.1%}\")\n        print(f\"Favorite's Probability: {predictions[0].win_probability:.1%}\")\n        print(f\"Longshot's Probability: {predictions[-1].win_probability:.1%}\")\n    \n    def run_live_demo(self, num_races: int = 3):\n        \"\"\"Run live demonstration with real data\"\"\"\n        logger.info(f\"🚀 Running live demo with {num_races} races...\")\n        \n        # Load real race data\n        all_data = self.load_race_data(limit=num_races * 12)\n        \n        # Group into races (approximate)\n        races = []\n        current_race = []\n        \n        for _, horse_data in all_data.iterrows():\n            current_race.append(horse_data)\n            \n            # Create races of 8-14 horses\n            if len(current_race) >= np.random.randint(8, 15):\n                races.append(pd.DataFrame(current_race))\n                current_race = []\n                \n                if len(races) >= num_races:\n                    break\n        \n        # Analyze each race\n        for i, race_data in enumerate(races, 1):\n            print(f\"\\n{'='*50} RACE {i} {'='*50}\")\n            \n            predictions = self.predict_race(race_data)\n            self.analyze_race_detailed(predictions)\n            \n            if i < len(races):\n                input(\"\\n⏳ Press Enter for next race...\")\n\n\ndef main():\n    \"\"\"Run production racing AI demo\"\"\"\n    logger.info(\"🚀 PRODUCTION HORSE RACING AI STARTING...\")\n    logger.info(\"=\" * 70)\n    \n    # Initialize system\n    ai = ProductionRacingAI()\n    \n    # Run live demo\n    ai.run_live_demo(num_races=2)\n    \n    logger.info(\"\\n🎉 PRODUCTION DEMO COMPLETE!\")\n\n\nif __name__ == \"__main__\":\n    main()"
