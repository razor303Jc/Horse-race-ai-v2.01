#!/bin/bash
# Repository Cleanup and Organization Script
# This script organizes the messy root directory into proper structure

echo "🧹 Starting repository cleanup and organization..."

# Create organized directory structure
mkdir -p cleanup_temp/{documentation,demos,results,logs,scripts,archived}
mkdir -p src/contextual_ai/
mkdir -p experiments/
mkdir -p data/databases/
mkdir -p reports/

echo "📁 Created organized directory structure"

# Move documentation files
echo "📚 Moving documentation files..."
mv *_COMPLETE*.md cleanup_temp/documentation/ 2>/dev/null || true
mv *_SUMMARY*.md cleanup_temp/documentation/ 2>/dev/null || true
mv *_SUCCESS*.md cleanup_temp/documentation/ 2>/dev/null || true
mv *_ANALYSIS*.md cleanup_temp/documentation/ 2>/dev/null || true
mv *_REPORT*.md cleanup_temp/documentation/ 2>/dev/null || true
mv AI_ROI_RECORDS_SUMMARY.md cleanup_temp/documentation/ 2>/dev/null || true

# Move demo files
echo "🎮 Moving demo files..."
mv *_demo.py cleanup_temp/demos/ 2>/dev/null || true
mv *_integration_demo.py cleanup_temp/demos/ 2>/dev/null || true
mv enhanced_contextual_demo.py cleanup_temp/demos/ 2>/dev/null || true
mv ml_contextual_integration_demo.py cleanup_temp/demos/ 2>/dev/null || true
mv contextual_enhancement_summary.py cleanup_temp/demos/ 2>/dev/null || true

# Move result files
echo "📊 Moving result files..."
mv *.json cleanup_temp/results/ 2>/dev/null || true
mv *.txt cleanup_temp/results/ 2>/dev/null || true
mv complete_pipeline_results_*.json cleanup_temp/results/ 2>/dev/null || true
mv advanced_optimization_results_*.txt cleanup_temp/results/ 2>/dev/null || true

# Move log files
echo "📝 Moving log files..."
mv *.log cleanup_temp/logs/ 2>/dev/null || true
mv advanced_enhancement.log cleanup_temp/logs/ 2>/dev/null || true

# Move database files
echo "🗄️ Moving database files..."
mv *.db data/databases/ 2>/dev/null || true

# Move training and ML files to experiments
echo "🧠 Moving ML experiment files..."
mv *trainer*.py experiments/ 2>/dev/null || true
mv *training*.py experiments/ 2>/dev/null || true
mv *optimization*.py experiments/ 2>/dev/null || true
mv enhanced_ml_trainer.py experiments/ 2>/dev/null || true
mv profit_optimized_trainer.py experiments/ 2>/dev/null || true

# Move utility scripts
echo "🔧 Moving utility scripts..."
mv *_generator.py cleanup_temp/scripts/ 2>/dev/null || true
mv massive_dataset_generator.py src/contextual_ai/ 2>/dev/null || true
mv ai_learning_reward_system.py src/contextual_ai/ 2>/dev/null || true
mv race_data_quality_analyzer.py src/contextual_ai/ 2>/dev/null || true

# Move analysis and exploration scripts
mv *analyzer*.py cleanup_temp/scripts/ 2>/dev/null || true
mv *explorer*.py cleanup_temp/scripts/ 2>/dev/null || true
mv check_db_stats.py cleanup_temp/scripts/ 2>/dev/null || true
mv database_import.py cleanup_temp/scripts/ 2>/dev/null || true

# Move test files that don't belong in tests/
mv test_*.py tests/ 2>/dev/null || true

# Move run scripts
mv run_*.py cleanup_temp/scripts/ 2>/dev/null || true
mv *.sh cleanup_temp/scripts/ 2>/dev/null || true

# Move miscellaneous Python files
mv *_system.py cleanup_temp/archived/ 2>/dev/null || true
mv status_check.py cleanup_temp/scripts/ 2>/dev/null || true
mv time_scheduler.py cleanup_temp/archived/ 2>/dev/null || true

echo "✅ Initial cleanup complete!"
echo "📋 Summary of organization:"
echo "   📚 Documentation -> cleanup_temp/documentation/"
echo "   🎮 Demos -> cleanup_temp/demos/"
echo "   📊 Results -> cleanup_temp/results/"
echo "   📝 Logs -> cleanup_temp/logs/"
echo "   🗄️ Databases -> data/databases/"
echo "   🧠 ML Experiments -> experiments/"
echo "   🔧 Scripts -> cleanup_temp/scripts/"
echo "   📦 Archived -> cleanup_temp/archived/"
echo "   🎯 Core AI -> src/contextual_ai/"
