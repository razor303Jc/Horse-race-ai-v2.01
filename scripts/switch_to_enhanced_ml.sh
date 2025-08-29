#!/bin/bash
# Enhanced ML Pipeline Switcher
# ============================
# 
# This script switches the Docker ML training container to use the enhanced
# pipeline with 53+ features instead of the basic 6-feature pipeline.

echo "🔧 Switching to Enhanced ML Pipeline (53+ features)..."

# Check if we're in Docker environment
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
    
    # Copy enhanced pipeline to replace basic one
    if [ -f "/app/docker/ml_training/enhanced_pipeline_integration.py" ]; then
        echo "✅ Enhanced pipeline found, creating backup of basic pipeline..."
        
        # Backup original
        cp /app/docker/ml_training/pipeline_integration.py /app/docker/ml_training/pipeline_integration_basic_backup.py
        
        # Replace with enhanced version
        cp /app/docker/ml_training/enhanced_pipeline_integration.py /app/docker/ml_training/pipeline_integration.py
        
        echo "🚀 Enhanced pipeline activated!"
        echo "📊 Features upgraded: 6 basic → 53+ enhanced features"
        echo "🎯 Models upgraded: Single RandomForest → 4-model ensemble"
        echo "🧠 System upgraded: Basic ML → V2.01 Enhanced System"
        
    else
        echo "❌ Enhanced pipeline not found!"
        exit 1
    fi
else
    echo "🖥️  Running on host system"
    
    # For host system, just copy the file
    if [ -f "./docker/ml_training/enhanced_pipeline_integration.py" ]; then
        echo "✅ Enhanced pipeline found, creating backup..."
        
        # Backup original
        cp ./docker/ml_training/pipeline_integration.py ./docker/ml_training/pipeline_integration_basic_backup.py
        
        # Replace with enhanced version
        cp ./docker/ml_training/enhanced_pipeline_integration.py ./docker/ml_training/pipeline_integration.py
        
        echo "🚀 Enhanced pipeline activated!"
        echo "📊 Features upgraded: 6 basic → 53+ enhanced features"
        echo "🎯 Models upgraded: Single RandomForest → 4-model ensemble"
        echo "🧠 System upgraded: Basic ML → V2.01 Enhanced System"
        
        echo ""
        echo "🔄 To apply changes, restart the ML training container:"
        echo "   docker-compose restart ml_trainer"
        
    else
        echo "❌ Enhanced pipeline not found!"
        exit 1
    fi
fi

echo ""
echo "✅ Enhanced ML Pipeline Switch Complete!"
echo ""
echo "📋 What Changed:"
echo "   • Features: 6 basic → 53+ enhanced composite features"
echo "   • Models: RandomForest → RandomForest + GradientBoosting + NeuralNet + LogisticRegression"
echo "   • Scoring: Basic accuracy → Ensemble probabilities + confidence scoring"
echo "   • Features include: Composite scores, historical performance, betting analysis"
echo "   • Advanced capabilities: Monte Carlo simulation, consensus rating system"
echo ""
echo "🎯 Expected Performance Improvement:"
echo "   • More sophisticated feature engineering"
echo "   • Better generalization through ensemble approach"
echo "   • Advanced confidence scoring and value betting detection"
echo "   • Comprehensive performance tracking and reporting"
