#!/usr/bin/env python3
"""
🎯 Priority 3A: Production Model Demo

Demonstrates how to use the trained ensemble model for live predictions.
Shows the complete pipeline from data input to prediction output.

Usage:
    python3 tools/ml_pipeline/production_demo.py
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path


def load_production_models(timestamp="20250810_203957"):
    """Load the trained ensemble model and encoders."""
    models_dir = Path.cwd() / "trained_models" / "priority_3a"
    
    # Load ensemble model (best performer)
    ensemble_path = models_dir / f"ensemble_{timestamp}.joblib"
    ensemble_model = joblib.load(ensemble_path)
    
    # Load encoders
    encoders_path = models_dir / f"encoders_{timestamp}.joblib"
    encoders = joblib.load(encoders_path)
    
    print("✅ Loaded production ensemble model")
    print(f"   Components: {[name for name, _ in ensemble_model.estimators]}")
    
    return ensemble_model, encoders


def create_sample_prediction_data():
    """Create sample horse racing data for prediction."""
    # Example race data (realistic values)
    sample_data = {
        'horse_age': 5,
        'draw': 3,
        'win_odds': 4.5,
        'place_odds': 2.1,
        'barrier': 3,
        'margin': 1.5,  # Previous race margin
        'horse_weight_kg': 485,
        'handicap_weight': 58,
        'jockey_win_pct': 12.5,
        'jockey_place_pct': 28.3,
        'trainer_win_pct': 15.2,
        'trainer_place_pct': 32.1,
        'course': 'Flemington'
    }
    
    return pd.DataFrame([sample_data])


def engineer_features_for_prediction(df, encoders):
    """Engineer features for prediction (matching training pipeline)."""
    df_features = df.copy()
    
    # Odds-based features
    df_features['is_favorite'] = (df_features['win_odds'] <= 3.0).astype(int)
    df_features['high_odds'] = (df_features['win_odds'] >= 10.0).astype(int)
    df_features['log_odds'] = np.log(df_features['win_odds'].clip(lower=1.01))
    df_features['implied_prob'] = 1 / df_features['win_odds'].clip(lower=1.01)
    
    # Safe ratio calculations
    place_odds_safe = df_features['place_odds'].fillna(df_features['win_odds']).clip(lower=0.1)
    df_features['odds_ratio'] = df_features['win_odds'] / place_odds_safe
    
    weight_denom = df_features['handicap_weight'].fillna(df_features['horse_weight_kg']).clip(lower=30)
    df_features['weight_ratio'] = df_features['horse_weight_kg'] / weight_denom
    
    # Age and position features
    df_features['age_squared'] = df_features['horse_age'] ** 2
    df_features['draw_squared'] = df_features['draw'] ** 2
    df_features['barrier_squared'] = df_features['barrier'] ** 2
    
    # Combined performance features
    df_features['jockey_trainer_combo'] = df_features['jockey_win_pct'] * df_features['trainer_win_pct']
    df_features['combined_place_pct'] = (df_features['jockey_place_pct'] + df_features['trainer_place_pct']) / 2
    
    # Categorical encoding
    if 'course' in encoders:
        try:
            df_features['course_encoded'] = encoders['course'].transform(df_features['course'].astype(str))
        except ValueError:
            # Handle unseen course (use mode or default value)
            df_features['course_encoded'] = 0
    
    # Select feature columns (matching training)
    feature_columns = [
        'horse_age', 'draw', 'win_odds', 'place_odds', 'barrier', 'margin',
        'horse_weight_kg', 'handicap_weight', 'jockey_win_pct', 'jockey_place_pct',
        'trainer_win_pct', 'trainer_place_pct', 'is_favorite', 'high_odds',
        'log_odds', 'implied_prob', 'odds_ratio', 'weight_ratio', 'age_squared',
        'draw_squared', 'barrier_squared', 'jockey_trainer_combo', 'combined_place_pct',
        'course_encoded'
    ]
    
    return df_features[feature_columns]


def make_prediction_demo():
    """Demonstrate complete prediction pipeline."""
    print("🚀 Priority 3A: Production Model Demo")
    print("=" * 50)
    
    # Load trained models
    ensemble_model, encoders = load_production_models()
    
    # Create sample data
    print("\n📊 Sample Race Data:")
    sample_df = create_sample_prediction_data()
    for col, val in sample_df.iloc[0].items():
        print(f"   {col:18}: {val}")
    
    # Engineer features
    print("\n⚙️ Engineering features...")
    features = engineer_features_for_prediction(sample_df, encoders)
    print(f"   Features created: {len(features.columns)}")
    
    # Make prediction
    print("\n🎯 Making predictions...")
    win_probability = ensemble_model.predict_proba(features)[0, 1]
    win_prediction = ensemble_model.predict(features)[0]
    
    # Display results
    print(f"\n🏆 Prediction Results:")
    print(f"   Win Probability: {win_probability:.1%}")
    print(f"   Win Prediction: {'🏆 WINNER' if win_prediction else '❌ Non-winner'}")
    print(f"   Implied Odds: {1/win_probability:.1f}")
    print(f"   Model Confidence: {'High' if win_probability > 0.7 or win_probability < 0.3 else 'Medium'}")
    
    # Show model components
    print(f"\n🎭 Ensemble Components:")
    for name, model in ensemble_model.estimators:
        component_prob = model.predict_proba(features)[0, 1]
        print(f"   {name:18}: {component_prob:.1%}")
    
    print(f"\n✅ Demo complete - Model ready for production!")


if __name__ == "__main__":
    make_prediction_demo()
