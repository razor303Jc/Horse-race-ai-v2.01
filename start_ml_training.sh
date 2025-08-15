#!/bin/bash
# ML Training Startup Script
# Horse Racing AI v2.02

echo "🎯 ML TRAINING AUTOMATION STARTUP"
echo "=================================="

# Check if we want to wait for auto-downloader or start immediately
echo
echo "Options:"
echo "1. Wait for next auto-downloader run at 00:01, then start ML training"
echo "2. Start ML training immediately with existing data"
echo "3. Run quick test (10 cycles only)"
echo

read -p "Choose option (1/2/3): " choice

case $choice in
    1)
        echo "⏰ Will wait for auto-downloader at 00:01, then start 100 ML cycles"
        python3 tools/ml_training/ml_training_orchestrator.py
        ;;
    2)
        echo "🚀 Starting ML training immediately with existing data"
        python3 -c "
import asyncio
import sys
from pathlib import Path

sys.path.append('tools/ml_training')

async def run_immediate():
    try:
        from automated_ml_cycle_manager import MLTrainingCycleManager
        manager = MLTrainingCycleManager()
        await manager.run_training_cycles()
    except Exception as e:
        print(f'Error: {e}')

# Create directories
Path('logs').mkdir(exist_ok=True)
Path('results/ml_performance').mkdir(parents=True, exist_ok=True)

asyncio.run(run_immediate())
"
        ;;
    3)
        echo "🧪 Running quick test with 10 cycles"
        python3 -c "
import asyncio
import sys
from pathlib import Path

sys.path.append('tools/ml_training')

async def run_test():
    try:
        from automated_ml_cycle_manager import MLTrainingCycleManager
        manager = MLTrainingCycleManager()
        
        # Test parameters
        manager.target_cycles = 10
        manager.cycles_per_batch = 5
        manager.target_batches = 2
        
        await manager.run_training_cycles()
    except Exception as e:
        print(f'Error: {e}')

# Create directories
Path('logs').mkdir(exist_ok=True)
Path('results/ml_performance').mkdir(parents=True, exist_ok=True)

asyncio.run(run_test())
"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo
echo "✅ ML Training automation completed!"
echo "📊 Check results/ml_performance/ for detailed metrics"
echo "📋 Check logs/ for training logs"
