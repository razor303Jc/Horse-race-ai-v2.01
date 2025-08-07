#!/usr/bin/env python3
"""
Test AI Performance Comparison GUI Features
==========================================

Simple script to test the new AI performance comparison features in the web GUI.
This creates mock ML models and trains them for demonstration purposes.
"""

import json

# Set up path for imports
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem
from src.horse_racing_ai.scoring.composite_scorer import CompositeScorer
from src.horse_racing_ai.scoring.form_analyzer import (
    RaceClass,
    RacePerformance,
    SurfaceType,
)


def create_mock_training_data(num_samples: int = 100) -> pd.DataFrame:
    """Create mock training data for ML models."""
    print(f"🎲 Creating {num_samples} mock training samples...")

    # Generate synthetic horse racing data
    np.random.seed(42)

    data = []
    for i in range(num_samples):
        # Generate realistic horse racing features
        composite_score = np.random.normal(75, 15)
        form_score = np.random.normal(70, 12)
        power_rating = np.random.normal(100, 20)
        speed_score = np.random.normal(80, 10)
        class_score = np.random.normal(75, 15)
        consistency_score = np.random.uniform(0.3, 0.9)
        conditions_score = np.random.normal(75, 10)
        confidence_level = np.random.uniform(0.5, 0.95)

        # Additional features
        avg_position_last_5 = np.random.uniform(1, 8)
        best_position_last_5 = np.random.randint(1, 4)
        worst_position_last_5 = np.random.randint(5, 12)
        avg_speed_figure = np.random.normal(85, 12)
        max_speed_figure = avg_speed_figure + np.random.uniform(5, 15)
        speed_consistency = np.random.uniform(2, 10)

        # Race-specific features
        race_distance = np.random.choice([6, 7, 8, 9, 10, 12])
        field_size = np.random.randint(6, 14)
        betting_odds = np.random.lognormal(1.5, 0.8)

        # Create target rating (simplified relationship)
        target_rating = (
            composite_score * 0.3
            + form_score * 0.2
            + power_rating * 0.2
            + speed_score * 0.15
            + (1.0 / avg_position_last_5) * 20
            + max_speed_figure * 0.1
            + consistency_score * 10
            + np.random.normal(0, 5)  # Add some noise
        )

        row = {
            "composite_score": composite_score,
            "form_score": form_score,
            "power_rating": power_rating,
            "speed_score": speed_score,
            "class_score": class_score,
            "consistency_score": consistency_score,
            "conditions_score": conditions_score,
            "confidence_level": confidence_level,
            "avg_position_last_5": avg_position_last_5,
            "best_position_last_5": best_position_last_5,
            "worst_position_last_5": worst_position_last_5,
            "position_improvement": np.random.uniform(-0.5, 0.5),
            "avg_speed_figure": avg_speed_figure,
            "max_speed_figure": max_speed_figure,
            "speed_consistency": speed_consistency,
            "speed_trend": np.random.uniform(-2, 2),
            "avg_beaten_lengths": np.random.uniform(0, 8),
            "min_beaten_lengths": np.random.uniform(0, 2),
            "performance_volatility": np.random.uniform(1, 5),
            "jockey_consistency": np.random.uniform(0.7, 1.0),
            "trainer_consistency": np.random.uniform(0.8, 1.0),
            "distance_specialization": np.random.uniform(0.3, 0.9),
            "class_progression": np.random.uniform(-0.2, 0.2),
            "surface_versatility": np.random.uniform(0.5, 1.0),
            "condition_adaptability": np.random.uniform(0.6, 1.0),
            "days_since_last_race": np.random.randint(7, 90),
            "racing_frequency": np.random.uniform(0.05, 0.3),
            "layoff_factor": np.random.randint(7, 90),
            "race_distance": race_distance,
            "field_size": field_size,
            "race_class_numeric": np.random.uniform(1, 5),
            "surface_dirt": np.random.choice([0, 1]),
            "surface_turf": np.random.choice([0, 1]),
            "surface_synthetic": np.random.choice([0, 1]),
            "betting_odds": betting_odds,
            "log_odds": np.log(betting_odds + 1),
            "market_confidence": 1.0 / betting_odds,
            "form_power_interaction": form_score * power_rating / 100.0,
            "speed_class_interaction": speed_score * class_score / 100.0,
            "consistency_confidence": consistency_score * confidence_level,
            "target_rating": target_rating,
        }

        data.append(row)

    df = pd.DataFrame(data)
    print(f"✅ Created training data with shape: {df.shape}")
    return df


def train_mock_ml_models():
    """Train mock ML models for demonstration."""
    print("🤖 Training Mock ML Models for GUI Demo")
    print("=" * 50)

    # Create ML rating system
    ml_system = EnhancedMLRatingSystem(enable_neural_networks=False)
    print("✅ ML Rating System initialized")

    # Create training data
    training_data = create_mock_training_data(200)

    # Train models
    print("🚀 Training ML models...")
    model_performances = ml_system.train_models(
        training_data, target_column="target_rating"
    )

    # Display results
    print("\n📊 Model Training Results:")
    for model_name, performance in model_performances.items():
        print(f"  {model_name}:")
        print(f"    - R² Score: {performance.r2_score:.3f}")
        print(f"    - RMSE: {performance.rmse:.3f}")
        print(f"    - MAE: {performance.mae:.3f}")
        print(
            f"    - CV Mean: {performance.cross_val_mean:.3f} ± {performance.cross_val_std:.3f}"
        )

    # Save models for web GUI to use
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    model_path = ml_system.save_enhanced_models("gui_demo_models")
    print(f"\n💾 Models saved to: {model_path}")

    # Create a simple test to show prediction capabilities
    print("\n🎯 Testing Prediction Capabilities:")

    # Use first few rows as test data
    test_features = training_data.head(3).drop(columns=["target_rating"])

    # Make predictions using ensemble model
    if "ensemble" in ml_system.models:
        predictions = ml_system.models["ensemble"].predict(test_features)
        actual_values = training_data.head(3)["target_rating"].values

        print("Sample Predictions vs Actual:")
        for i, (pred, actual) in enumerate(zip(predictions, actual_values)):
            print(
                f"  Horse {i+1}: Predicted={pred:.2f}, Actual={actual:.2f}, Error={abs(pred-actual):.2f}"
            )

    # Update AI performance metrics with mock data
    print("\n📈 Simulating AI Performance History...")

    # Simulate some successful predictions
    for i in range(10):
        # Create mock performance update
        mock_predictions = []
        mock_results = []

        for j in range(8):  # 8 horses per race
            from src.horse_racing_ai.ml.enhanced_ml_models import MLModelPrediction

            # Create realistic mock prediction
            win_prob = np.random.beta(2, 8)  # Skewed toward lower probabilities
            place_prob = min(0.8, win_prob + np.random.uniform(0.1, 0.3))

            pred = MLModelPrediction(
                horse_name=f"Test Horse {j+1}",
                predicted_rating=np.random.normal(75, 15),
                predicted_z_score=np.random.normal(0, 1),
                confidence_score=np.random.uniform(0.6, 0.9),
                win_probability=win_prob,
                place_probability=place_prob,
                show_probability=min(0.9, place_prob + 0.1),
                expected_position=j + 1 + np.random.uniform(-2, 2),
                performance_range=(65, 85),
                model_features={},
                prediction_factors=[
                    "Good form",
                    "Class advantage",
                    "Distance specialist",
                ],
            )
            mock_predictions.append(pred)

            # Create mock result
            actual_position = max(1, min(12, int(np.random.exponential(4))))
            mock_results.append({"finish_position": actual_position})

        # Update AI performance
        ml_system.update_ai_performance(mock_predictions, mock_results)

    # Display final performance metrics
    performance_report = ml_system.get_ai_performance_report()
    print(f"\n🏆 Final AI Performance Metrics:")
    print(f"  Total Predictions: {performance_report['total_predictions']}")
    print(f"  Win Accuracy: {performance_report['win_accuracy']:.1%}")
    print(f"  Place Accuracy: {performance_report['place_accuracy']:.1%}")
    print(f"  Average Accuracy: {performance_report['average_accuracy']:.1%}")

    print("\n✅ Mock ML Models Successfully Trained and Ready for GUI!")
    print("\n🌐 You can now test the AI Performance Comparison feature in the web GUI:")
    print("   1. Start the web server: python web_gui.py")
    print("   2. Open http://localhost:5001 in your browser")
    print("   3. Select a race and click 'AI Performance Comparison'")
    print("   4. Compare Raw Ratings vs Monte Carlo vs AI ML Models")

    return ml_system


if __name__ == "__main__":
    train_mock_ml_models()
