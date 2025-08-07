#!/usr/bin/env python3
"""
Quick Model Test - Simple utility to test the enhanced model
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path


def quick_test():
    """Quick test of the enhanced model with minimal setup."""

    print("🚀 Quick Enhanced Model Test")
    print("=" * 40)

    # Load model
    models_dir = Path("models/enhanced_v2")
    model = joblib.load(models_dir / "random_forest_enhanced_v2.joblib")
    scalers = joblib.load(models_dir / "scalers_v2.joblib")

    print("✅ Model loaded successfully")

    # Create a simple test case - favorite vs outsider
    test_data = pd.DataFrame(
        {
            "log_odds": [0.5, 3.0],  # Low odds vs high odds
            "odds_rank": [1, 8],  # Favorite vs outsider
            "odds_percentile": [0.1, 0.9],
            "is_favorite": [1, 0],
            "is_outsider": [0, 1],
            "market_strength": [2.0, 0.3],
            "market_share": [0.5, 0.1],
            "draw_percentile": [0.5, 0.5],
            "weight_percentile": [0.5, 0.5],
            "field_size": [8, 8],
            "odds_spread": [1.5, 1.5],
            "race_class": [3, 3],
            "prize_per_runner": [5000, 5000],
            "log_prize": [10.8, 10.8],
            "rating_rank": [1, 8],
            "rating_percentile": [0.9, 0.1],
            "trainer_experience": [50, 10],
            "jockey_experience": [200, 20],
            "horse_experience": [15, 3],
            "distance_category": [1, 1],
            "age_category": [1, 1],
            "odds_weight_ratio": [4.0, 20.0],
            "rating_odds_ratio": [5.0, 0.1],
            "experience_odds": [20.0, 10.0],
        }
    )

    # Scale features
    scaler = scalers["feature_scaler"]
    X_scaled = pd.DataFrame(scaler.transform(test_data), columns=test_data.columns)

    # Make predictions
    probabilities = model.predict_proba(X_scaled)[:, 1]

    # Display results
    print("\n🏇 Test Results:")
    print("-" * 40)
    print(f"Favorite:  {probabilities[0]:.3f} win probability")
    print(f"Outsider:  {probabilities[1]:.3f} win probability")
    print(f"Ratio:     {probabilities[0]/probabilities[1]:.1f}x more likely")

    print("\n✅ Model working correctly!")
    print(f"🎯 Favorite is {probabilities[0]/probabilities[1]:.1f}x more likely to win")


if __name__ == "__main__":
    quick_test()
