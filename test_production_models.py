#!/usr/bin/env python3
"""
Quick test of our production ML models
Tests individual predictions with the exact feature alignment
"""

import sys
from pathlib import Path

import numpy as np

# Add the production models directory to path
sys.path.append(str(Path(__file__).parent / "tools" / "trained_models" / "production"))

from production_predictor import ProductionMLPredictor


def test_production_models():
    """Test our production models with sample data"""
    print("🎯 Testing Production ML Models")
    print("=" * 50)

    # Initialize predictor
    predictor = ProductionMLPredictor()

    # Create sample horse data (the 17 features our models expect)
    sample_horses = [
        {
            "horse_name": "Champion Supreme",
            "log_odds": 1.2,  # Relatively good odds
            "implied_probability": 0.3,
            "odds_rank": 2,  # Second favorite
            "is_favorite": 0,
            "combined_performance": 0.25,  # Good jockey/trainer combo
            "field_size": 12,
            "min_odds": 2.0,
            "max_odds": 50.0,
            "avg_odds": 8.5,
            "draw_percentile": 0.3,  # Good draw
            "weight_percentile": 0.6,
            "age_category": 1,
            "horse_age": 4,
            "horse_weight_kg": 57,
            "draw": 3,
            "jockey_win_pct": 0.18,  # Good jockey
            "trainer_win_pct": 0.22,  # Good trainer
        },
        {
            "horse_name": "Longshot Larry",
            "log_odds": 3.5,  # Long odds
            "implied_probability": 0.05,
            "odds_rank": 10,  # Outsider
            "is_favorite": 0,
            "combined_performance": 0.08,  # Poor combination
            "field_size": 12,
            "min_odds": 2.0,
            "max_odds": 50.0,
            "avg_odds": 8.5,
            "draw_percentile": 0.8,  # Poor draw
            "weight_percentile": 0.9,  # Heavy weight
            "age_category": 3,
            "horse_age": 8,  # Older horse
            "horse_weight_kg": 62,
            "draw": 11,
            "jockey_win_pct": 0.05,  # Poor jockey
            "trainer_win_pct": 0.06,  # Poor trainer
        },
        {
            "horse_name": "Hot Favorite",
            "log_odds": 0.3,  # Very short odds
            "implied_probability": 0.7,
            "odds_rank": 1,  # Favorite
            "is_favorite": 1,
            "combined_performance": 0.35,  # Excellent combination
            "field_size": 12,
            "min_odds": 2.0,
            "max_odds": 50.0,
            "avg_odds": 8.5,
            "draw_percentile": 0.2,  # Excellent draw
            "weight_percentile": 0.3,  # Light weight
            "age_category": 1,
            "horse_age": 4,
            "horse_weight_kg": 55,
            "draw": 2,
            "jockey_win_pct": 0.25,  # Excellent jockey
            "trainer_win_pct": 0.28,  # Excellent trainer
        },
    ]

    # Test each model
    models_to_test = [
        "gradient_boosting",
        "random_forest",
        "neural_network",
        "logistic_regression",
    ]

    print("🐎 Horse Predictions:")
    print("-" * 50)

    for horse in sample_horses:
        print(f"\n🏇 {horse['horse_name']}:")
        print(f"   Market Odds: {1/horse['implied_probability']:.1f}")
        print(f"   Jockey Win%: {horse['jockey_win_pct']:.1%}")
        print(f"   Trainer Win%: {horse['trainer_win_pct']:.1%}")
        print(f"   Draw: {horse['draw']} / Field: {horse['field_size']}")

        print(f"   🎯 Model Predictions:")
        for model_name in models_to_test:
            try:
                win_prob = predictor.predict(horse, model_name)
                print(f"      {model_name}: {win_prob:.1%}")
            except Exception as e:
                print(f"      {model_name}: ERROR - {e}")

        # Get race predictions (just this horse for demo)
        race_predictions = predictor.predict_race([horse])
        print(f"   🏆 Best Prediction: {race_predictions[0]['win_probability']:.1%}")

    print("\n✅ Production Model Test Complete!")
    print(f"📊 Models loaded: {len(predictor.models)}")
    print(f"🎯 Features expected: {len(predictor.feature_names)}")


if __name__ == "__main__":
    test_production_models()
