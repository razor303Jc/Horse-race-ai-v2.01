#!/bin/bash
# Start ML Training - 10 Cycles x 1000 Sessions
# Horse Racing AI v2.02

echo "🤖 ML Training: 10 Cycles x 1000 Sessions"
echo "=========================================="
echo ""
echo "Training Configuration:"
echo "  • 10 cycles per session (1 batch of 10)"
echo "  • 1000 total sessions"
echo "  • 10,000 total cycles"
echo "  • 5-second wait between sessions"
echo "  • Review after each session"
echo ""
echo "Estimated timing:"
echo "  • ~21 seconds per session (16s training + 5s wait)"
echo "  • ~171 sessions per hour"
echo "  • ~5.8 hours total"
echo ""

# Check if resuming
if [ "$1" = "resume" ]; then
    echo "📂 Checking for previous session..."
    python3 tools/ml_training/ml_session_manager.py resume
else
    echo "Choose an option:"
    echo "1) Wait for next auto-downloader (00:01) then start training"
    echo "2) Start training immediately with current data"
    echo "3) Run test session (10 cycles only)"
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
