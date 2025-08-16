#!/bin/bash
# Start ML Training - 50 Cycles x 2000 Sessions
# Horse Racing AI v2.02

echo "🤖 ML Training: 50 Cycles x 2000 Sessions"
echo "=========================================="
echo ""
echo "Training Configuration:"
echo "  • 50 cycles per session (5 batches of 10)"
echo "  • 2000 total sessions"
echo "  • 100,000 total cycles"
echo "  • Review after each session"
echo ""
echo "Estimated timing:"
echo "  • ~1.5 minutes per session"
echo "  • ~40 sessions per hour"
echo "  • ~50 hours total (2+ days)"
echo ""

# Check if resuming
if [ "$1" = "resume" ]; then
    echo "📂 Checking for previous session..."
    python3 tools/ml_training/ml_session_manager.py resume
else
    echo "Choose an option:"
    echo "1) Wait for next auto-downloader (00:01) then start training"
    echo "2) Start training immediately with current data"
    echo "3) Run test session (5 cycles only)"
    echo "4) Resume from checkpoint"
    echo ""
    read -p "Enter choice (1-4): " choice

    case $choice in
        1)
            echo "⏰ Waiting for auto-downloader at 00:01..."
            python3 tools/ml_training/ml_training_orchestrator.py --wait-for-download
            ;;
        2)
            echo "🚀 Starting training immediately..."
            python3 tools/ml_training/ml_session_manager.py
            ;;
        3)
            echo "🧪 Running test session..."
            python3 tools/ml_training/automated_ml_cycle_manager.py --test-mode
            ;;
        4)
            echo "📂 Resuming from checkpoint..."
            python3 tools/ml_training/ml_session_manager.py resume
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
fi

echo ""
echo "✅ Training session completed!"
echo "📊 Check results in: results/ml_sessions/"
