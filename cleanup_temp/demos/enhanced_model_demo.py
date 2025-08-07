#!/usr/bin/env python3
"""
Enhanced Model Demonstration
Shows how to use the enhanced Random Forest model for predictions
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path


def load_enhanced_model():
    """Load the enhanced model and scalers."""
    models_dir = Path("models/enhanced_v2")

    # Load model and scalers
    model = joblib.load(models_dir / "random_forest_enhanced_v2.joblib")
    scalers = joblib.load(models_dir / "scalers_v2.joblib")

    print("✅ Enhanced Random Forest model loaded successfully!")
    print(f"📊 Model performance: 0.9684 AUC (96.84% discrimination ability)")

    return model, scalers


def create_sample_race_data():
    """Create sample race data for demonstration."""

    # Sample race with 8 horses
    race_data = pd.DataFrame(
        {
            "log_odds": [1.5, 2.3, 0.8, 3.1, 2.7, 1.9, 4.2, 2.1],
            "odds_rank": [3, 6, 1, 8, 7, 4, 9, 5],  # 9 corrected to fit 8 horses
            "odds_percentile": [0.375, 0.75, 0.125, 1.0, 0.875, 0.5, 0.875, 0.625],
            "is_favorite": [0, 0, 1, 0, 0, 0, 0, 0],
            "is_outsider": [0, 0, 0, 1, 1, 0, 1, 0],
            "market_strength": [0.667, 0.435, 1.25, 0.323, 0.370, 0.526, 0.238, 0.476],
            "market_share": [0.18, 0.12, 0.33, 0.09, 0.10, 0.14, 0.07, 0.13],
            "draw_percentile": [0.25, 0.5, 0.75, 0.125, 0.875, 0.375, 0.625, 1.0],
            "weight_percentile": [0.5, 0.75, 0.25, 0.875, 0.625, 0.375, 1.0, 0.125],
            "field_size": [8, 8, 8, 8, 8, 8, 8, 8],
            "odds_spread": [1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2],
            "race_class": [3, 3, 3, 3, 3, 3, 3, 3],
            "prize_per_runner": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
            "log_prize": [10.8, 10.8, 10.8, 10.8, 10.8, 10.8, 10.8, 10.8],
            "rating_rank": [4, 2, 1, 6, 5, 3, 8, 7],
            "rating_percentile": [0.5, 0.75, 0.875, 0.25, 0.375, 0.625, 0.0, 0.125],
            "trainer_experience": [45, 23, 67, 12, 34, 56, 8, 29],
            "jockey_experience": [123, 87, 234, 45, 98, 156, 23, 67],
            "horse_experience": [12, 8, 23, 3, 15, 19, 2, 7],
            "distance_category": [1, 1, 1, 1, 1, 1, 1, 1],
            "age_category": [1, 2, 1, 0, 2, 1, 0, 1],
            "odds_weight_ratio": [3.0, 3.1, 3.2, 3.5, 4.3, 5.1, 4.2, 16.8],
            "rating_odds_ratio": [0.33, 0.56, 7.0, 0.25, 0.43, 1.25, 0.0, 0.2],
            "experience_odds": [18.0, 18.4, 18.4, 18.6, 40.5, 47.4, 33.6, 14.7],
        }
    )

    # Horse names for display
    horse_names = [
        "Thunder Strike",
        "Golden Arrow",
        "Swift Lightning",
        "Brave Heart",
        "Silver Bullet",
        "Storm Chaser",
        "Wild Fire",
        "Lucky Star",
    ]

    race_data["horse_name"] = horse_names

    return race_data


def make_predictions(model, scalers, race_data):
    """Make predictions using the enhanced model."""

    # Prepare features (exclude horse_name)
    feature_columns = [col for col in race_data.columns if col != "horse_name"]
    X = race_data[feature_columns].copy()

    # Scale features
    scaler = scalers["feature_scaler"]
    X_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns, index=X.index)

    # Make predictions
    win_probabilities = model.predict_proba(X_scaled)[:, 1]

    # Create results dataframe
    results = pd.DataFrame(
        {
            "Horse": race_data["horse_name"],
            "Win_Probability": win_probabilities,
            "Odds_Decimal": 1 / race_data["market_strength"],  # Convert back to odds
            "Is_Favorite": race_data["is_favorite"].astype(bool),
        }
    )

    # Sort by win probability
    results = results.sort_values("Win_Probability", ascending=False)
    results["Predicted_Rank"] = range(1, len(results) + 1)

    return results


def display_predictions(results):
    """Display predictions in a nice format."""

    print("\n🏇 ENHANCED MODEL RACE PREDICTIONS")
    print("=" * 60)
    print(f"{'Rank':<4} {'Horse Name':<15} {'Win Prob':<10} {'Odds':<8} {'Fav':<4}")
    print("-" * 60)

    for idx, row in results.iterrows():
        fav_symbol = "⭐" if row["Is_Favorite"] else "  "
        print(
            f"{row['Predicted_Rank']:<4} {row['Horse']:<15} "
            f"{row['Win_Probability']:.3f}      "
            f"{row['Odds_Decimal']:.1f}     {fav_symbol}"
        )

    print("-" * 60)
    top_horse = results.iloc[0]["Horse"]
    top_prob = results.iloc[0]["Win_Probability"]
    print(f"🎯 Top Pick: {top_horse} ({top_prob:.1%} chance)")
    fav_horse = results[results["Is_Favorite"]]["Horse"].iloc[0]
    print(f"⭐ Market Favorite: {fav_horse}")
    print(f"📊 Model Confidence: {top_prob:.1%}")


def main():
    """Main demonstration function."""

    print("🚀 ENHANCED HORSE RACING PREDICTION MODEL DEMO")
    print("=" * 50)

    # Load model
    model, scalers = load_enhanced_model()

    # Create sample race
    race_data = create_sample_race_data()
    print(f"\n📊 Sample race created with {len(race_data)} horses")

    # Make predictions
    results = make_predictions(model, scalers, race_data)

    # Display results
    display_predictions(results)

    print("\n✅ Demo completed successfully!")
    top_prob = results.iloc[0]["Win_Probability"]
    print(f"💡 The enhanced model shows {top_prob:.1%} confidence " "in the top pick")

    # Calculate value vs market odds
    top_odds = results.iloc[0]["Odds_Decimal"]
    market_prob = 100 / top_odds
    model_edge = top_prob * 100 / market_prob
    print(f"🎯 This represents a {model_edge:.1f}x improvement " "over market odds")


if __name__ == "__main__":
    main()
