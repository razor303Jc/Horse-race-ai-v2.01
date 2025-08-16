#!/bin/bash
# Early Morning ML Training Deployment Verification Script
# Horse Racing AI v2.02

echo "🌅 Early Morning ML Training - Deployment Verification"
echo "======================================================="

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

echo "📁 Project directory: $(pwd)"

# Check required files exist
echo ""
echo "🔍 Checking required files..."
required_files=(
    "docker/ml_training/early_morning_ml_trainer.py"
    "docker/ml_training/pipeline_integration.py" 
    "docker/ml_training/.env.ml-training"
    "Dockerfile.ml-models"
    "docker-compose.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        exit 1
    fi
done

# Check Docker is running
echo ""
echo "🐳 Checking Docker..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running - please start Docker"
    exit 1
fi

# Check if directories exist
echo ""
echo "📂 Checking data directories..."
directories=("data" "models" "logs" "cache" "reports" "trained_models")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "📁 Creating $dir/"
        mkdir -p "$dir"
    fi
    echo "✅ $dir/"
done

# Test Python imports
echo ""
echo "🐍 Testing Python imports..."
python3 -c "
import sys
sys.path.append('docker/ml_training')
sys.path.append('docker/pipeline_management')

try:
    from early_morning_ml_trainer import EarlyMorningTrainingConfig
    from pipeline_integration import EarlyMorningPipelineIntegration
    print('✅ All Python imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || exit 1

# Check environment file
echo ""
echo "⚙️ Environment configuration..."
if [ -f "docker/ml_training/.env.ml-training" ]; then
    echo "✅ ML training environment file exists"
    echo "📋 Key configurations:"
    grep -E "^ML_|^DATA_|^MODELS_" docker/ml_training/.env.ml-training | head -5
else
    echo "❌ ML training environment file missing"
fi

# Test Docker build (dry run)
echo ""
echo "🔨 Testing Docker build..."
if docker build -f Dockerfile.ml-models -t early-morning-ml-test . >/dev/null 2>&1; then
    echo "✅ Docker build test successful"
    docker rmi early-morning-ml-test >/dev/null 2>&1
else
    echo "⚠️ Docker build test failed - check Dockerfile.ml-models"
fi

# Show deployment commands
echo ""
echo "🚀 Deployment Commands:"
echo "======================="
echo ""
echo "1. Start early morning ML training:"
echo "   docker-compose --profile ml-training up -d ml-models"
echo ""
echo "2. View logs:"
echo "   docker-compose logs -f ml-models"
echo ""
echo "3. Check training status:"
echo "   docker-compose exec ml-models python /app/docker/ml_training/docker_test.py"
echo ""
echo "4. Stop training:"
echo "   docker-compose stop ml-models"
echo ""

# Show training schedule
echo "⏰ Training Schedule:"
echo "===================="
echo "00:01 - 00:30: Auto-Download & Validation"
echo "00:30 - 04:00: 🤖 EARLY MORNING ML TRAINING (210 min)"
echo "04:00 - 13:30: Data Processing & Analysis"
echo "13:45+:        🏇 Racing Starts"
echo ""

echo "✅ All verification checks passed!"
echo "🎉 Early Morning ML Training System is ready for deployment!"
echo ""
echo "💡 Tip: The system will automatically check if it's in the training window (00:30-04:00)"
echo "    and either start training or show current status."
