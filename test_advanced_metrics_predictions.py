#!/usr/bin/env python3
"""
🔮 Advanced Metrics ML Predictor
===============================

Test and demonstrate the trained advanced metrics ML models.

Features:
- Load trained models from advanced metrics training
- Make predictions on current race data
- Compare with existing predictions
- Generate prediction insights

Author: AI Assistant
Date: August 20, 2025
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedMetricsPredictor:
    """Predictor using trained advanced metrics models."""
    
    def __init__(self, model_path: str = None):
        """Initialize the predictor."""
        if model_path is None:
            # Find the latest model
            models_dir = Path("models")
            model_files = list(models_dir.glob("advanced_metrics_models_*.joblib"))
            if not model_files:
                raise FileNotFoundError("No advanced metrics models found")
            model_path = str(sorted(model_files)[-1])
        
        self.model_path = model_path
        self.model_data = None
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
        self.load_models()
        
    def load_models(self):
        """Load the trained models."""
        logger.info(f"📦 Loading models from {self.model_path}")
        
        self.model_data = joblib.load(self.model_path)
        self.models = self.model_data['models']
        self.scalers = self.model_data['scalers']
        self.feature_columns = self.model_data['feature_columns']
        
        logger.info(f"✅ Loaded {len(self.models)} models")
        logger.info(f"✅ Features: {len(self.feature_columns)} columns")
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction (same as training)."""
        df = df.copy()
        
        # Convert string values to numeric
        numeric_columns = [
            'power_rating', 'speed_figure', 'pace_rating', 'form_score',
            'win_probability', 'class_adjustment', 'distance_furlongs',
            'field_size'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill NaN values in pace_rating
        df['pace_rating'] = df['pace_rating'].fillna(df['speed_figure'])
        
        # Handle any other missing values
        base_columns = [
            'power_rating', 'speed_figure', 'pace_rating', 'form_score',
            'win_probability', 'class_adjustment', 'distance_furlongs',
            'field_size'
        ]
        for col in base_columns:
            if col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
        
        # Create derived features
        df['rating_speed_ratio'] = df['power_rating'] / (df['speed_figure'] + 1)
        df['power_form_ratio'] = df['power_rating'] / (df['form_score'] + 1)
        if len(df) > 1:
            df['field_strength'] = df['field_size'] * df['power_rating'].mean()
        else:
            df['field_strength'] = df['field_size']
        df['win_prob_adjusted'] = df['win_probability'] * df['field_size']
        
        return df
        
    def predict_win_probability(self, race_data: pd.DataFrame) -> np.ndarray:
        """Predict win probabilities using ensemble model."""
        X = race_data[self.feature_columns]
        model = self.models['win_ensemble']
        
        # Use predict_proba for probability estimates
        probabilities = model.predict_proba(X)[:, 1]  # Get probability of class 1 (win)
        return probabilities
        
    def predict_finishing_position(self, race_data: pd.DataFrame) -> np.ndarray:
        """Predict finishing positions using ensemble model."""
        X = race_data[self.feature_columns]
        model = self.models['position_ensemble']
        
        positions = model.predict(X)
        return positions
        
    def predict_place_probability(self, race_data: pd.DataFrame) -> np.ndarray:
        """Predict place probabilities using ensemble model."""
        X = race_data[self.feature_columns]
        model = self.models['place_ensemble']
        
        probabilities = model.predict_proba(X)[:, 1]  # Get probability of class 1 (place)
        return probabilities
        
    def make_comprehensive_predictions(self, race_data: pd.DataFrame) -> pd.DataFrame:
        """Make comprehensive predictions for a race."""
        prepared_data = self.prepare_features(race_data)
        
        # Make predictions
        win_probs = self.predict_win_probability(prepared_data)
        positions = self.predict_finishing_position(prepared_data)
        place_probs = self.predict_place_probability(prepared_data)
        
        # Create results dataframe
        results = prepared_data[['horse_id', 'horse_name']].copy()
        results['ml_win_probability'] = win_probs
        results['ml_predicted_position'] = positions
        results['ml_place_probability'] = place_probs
        
        # Compare with original win probabilities
        if 'win_probability' in prepared_data.columns:
            results['original_win_prob'] = prepared_data['win_probability']
            results['win_prob_diff'] = results['ml_win_probability'] - results['original_win_prob']
        
        # Add power rating for reference
        if 'power_rating' in prepared_data.columns:
            results['power_rating'] = prepared_data['power_rating']
            
        return results
    
    def analyze_race_predictions(self, results: pd.DataFrame) -> Dict:
        """Analyze predictions for a race."""
        analysis = {
            'total_horses': len(results),
            'favorite_by_ml': results.loc[results['ml_win_probability'].idxmax()]['horse_name'],
            'favorite_ml_prob': results['ml_win_probability'].max(),
            'predicted_winner_position': results.loc[results['ml_predicted_position'].idxmin()]['horse_name'],
            'best_predicted_position': results['ml_predicted_position'].min(),
            'top_3_by_ml_win': results.nlargest(3, 'ml_win_probability')[['horse_name', 'ml_win_probability']].to_dict('records'),
            'top_3_by_ml_place': results.nlargest(3, 'ml_place_probability')[['horse_name', 'ml_place_probability']].to_dict('records'),
        }
        
        if 'win_prob_diff' in results.columns:
            analysis['biggest_upgrade'] = results.loc[results['win_prob_diff'].idxmax()]['horse_name']
            analysis['biggest_upgrade_diff'] = results['win_prob_diff'].max()
            analysis['biggest_downgrade'] = results.loc[results['win_prob_diff'].idxmin()]['horse_name']
            analysis['biggest_downgrade_diff'] = results['win_prob_diff'].min()
        
        return analysis


def test_with_sample_race():
    """Test the predictor with sample current race data."""
    logger.info("🏇 Testing Advanced Metrics ML Predictor")
    
    # Load current race data from consolidated dataset
    data_path = "data/ml_training_data/consolidated_training_20250820_183657.json"
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Get a sample race from current data
    current_records = []
    for record in data['current_data'][:12]:  # First 12 horses (approximately 1-2 races)
        features = record['features'].copy()
        features['horse_id'] = record['horse_id']
        features['horse_name'] = record['horse_name']
        features['race_date'] = record['race_date']
        current_records.append(features)
    
    sample_race = pd.DataFrame(current_records)
    
    logger.info(f"📊 Testing with {len(sample_race)} horses")
    
    # Initialize predictor
    predictor = AdvancedMetricsPredictor()
    
    # Make predictions
    results = predictor.make_comprehensive_predictions(sample_race)
    
    # Analyze results
    analysis = predictor.analyze_race_predictions(results)
    
    # Display results
    print("\n🎯 ADVANCED METRICS ML PREDICTIONS")
    print("=" * 50)
    print(f"Race with {analysis['total_horses']} horses")
    print(f"ML Favorite: {analysis['favorite_by_ml']} ({analysis['favorite_ml_prob']:.3f})")
    print(f"Predicted Winner: {analysis['predicted_winner_position']} (Position {analysis['best_predicted_position']:.1f})")
    
    print("\n🏆 TOP 3 WIN PROBABILITIES (ML):")
    for i, horse in enumerate(analysis['top_3_by_ml_win'], 1):
        print(f"{i}. {horse['horse_name']}: {horse['ml_win_probability']:.3f}")
    
    print("\n🥉 TOP 3 PLACE PROBABILITIES (ML):")
    for i, horse in enumerate(analysis['top_3_by_ml_place'], 1):
        print(f"{i}. {horse['horse_name']}: {horse['ml_place_probability']:.3f}")
    
    if 'biggest_upgrade' in analysis:
        print(f"\n📈 Biggest Upgrade: {analysis['biggest_upgrade']} (+{analysis['biggest_upgrade_diff']:.3f})")
        print(f"📉 Biggest Downgrade: {analysis['biggest_downgrade']} ({analysis['biggest_downgrade_diff']:.3f})")
    
    print("\n📋 DETAILED PREDICTIONS:")
    print("-" * 80)
    display_columns = ['horse_name', 'power_rating', 'ml_win_probability', 'ml_predicted_position', 'ml_place_probability']
    if 'original_win_prob' in results.columns:
        display_columns.insert(-2, 'original_win_prob')
        display_columns.insert(-2, 'win_prob_diff')
    
    # Sort by ML win probability (descending)
    display_results = results[display_columns].sort_values('ml_win_probability', ascending=False)
    
    for _, row in display_results.iterrows():
        line = f"{row['horse_name']:<20} "
        line += f"Power:{row['power_rating']:>6.1f} "
        line += f"ML Win:{row['ml_win_probability']:>6.3f} "
        if 'original_win_prob' in row:
            line += f"Orig:{row['original_win_prob']:>6.3f} "
            line += f"Diff:{row['win_prob_diff']:>+6.3f} "
        line += f"Pos:{row['ml_predicted_position']:>4.1f} "
        line += f"Place:{row['ml_place_probability']:>6.3f}"
        print(line)
    
    print("\n✅ Advanced Metrics ML predictions complete!")
    return results, analysis


def main():
    """Main function."""
    print("🔮 Advanced Metrics ML Predictor Test")
    print("====================================")
    
    try:
        results, analysis = test_with_sample_race()
        
        print(f"\n🎉 Testing completed successfully!")
        print(f"📊 Analyzed {len(results)} horses")
        print(f"🤖 Used {len(AdvancedMetricsPredictor().models)} ML models")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Testing failed: {e}")


if __name__ == "__main__":
    main()
