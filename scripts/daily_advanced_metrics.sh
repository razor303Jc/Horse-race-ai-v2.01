#!/bin/bash
# Advanced Metrics Daily Automation Script
# Run this script daily to generate fresh metrics and retrain ML models

cd /home/jc/Documents/Horse-race-ai-v2.03

echo "🐎 Daily Advanced Metrics Generation - $(date)"
echo "=================================================="

# Generate current race metrics
echo "📊 Generating current race metrics..."
python3 tools/quick_metrics_generator.py

# Generate historical metrics if new results data available
echo "🏆 Processing historical results..."
python3 run_batch_historical_metrics.py

# Run ML model training with new features
echo "🤖 Training ML models with advanced features..."
python3 -c "
from src.horse_racing_ai.training.ml_trainer import MLTrainer
trainer = MLTrainer()
trainer.train_with_advanced_features()
"

# Update predictions with new models
echo "🔮 Updating predictions..."
python3 -c "
from src.horse_racing_ai.prediction.advanced_predictor import AdvancedPredictor
predictor = AdvancedPredictor()
predictor.generate_daily_predictions()
"

echo "✅ Daily advanced metrics pipeline complete!"
