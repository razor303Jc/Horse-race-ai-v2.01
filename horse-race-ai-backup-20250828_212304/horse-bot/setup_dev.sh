#!/bin/bash

# Development setup script for Horse Race Handicapping AI
# This script sets up the development environment and installs dependencies

set -e  # Exit on any error

echo "🏇 Setting up Horse Race Handicapping AI Development Environment"
echo "================================================================"

# Check if Python 3.11+ is available
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 11 ]); then
    echo "❌ Python 3.11+ is required. Found Python $python_version"
    echo "Please install Python 3.11 or higher and try again."
    exit 1
fi

echo "✅ Python $python_version found"

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the horse-bot directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "🔧 Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install the package in development mode
echo "🔧 Installing package in development mode..."
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@postgres:5432/horse_racing_dev
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# API Configuration
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Configuration
ML_MODEL_PATH=./models
ML_BATCH_SIZE=32
ML_CACHE_SIZE=1000

# Simulation Configuration
DEFAULT_SIMULATION_RUNS=10000
MAX_SIMULATION_RUNS=100000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# External APIs (if needed)
# WEATHER_API_KEY=your-weather-api-key
# RACING_DATA_API_KEY=your-racing-data-api-key
EOF
    echo "✅ .env file created. Please update with your actual configuration."
else
    echo "✅ .env file already exists"
fi

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"

# Create necessary directories
echo "🔧 Creating necessary directories..."
mkdir -p logs
mkdir -p models
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/external
echo "✅ Directories created"

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update the .env file with your database and Redis configuration"
    echo "2. Set up your PostgreSQL database"
    echo "3. Set up Redis (optional, but recommended)"
    echo "4. Run 'python -m pytest' to run all tests"
    echo "5. Run 'python src/main.py' to start the development server"
    echo ""
    echo "🔧 Useful commands:"
    echo "- Activate venv: source venv/bin/activate"
    echo "- Run tests: python -m pytest"
    echo "- Run with coverage: python -m pytest --cov=src"
    echo "- Start dev server: uvicorn src.main:app --reload"
    echo "- Format code: black src/ tests/"
    echo "- Lint code: flake8 src/ tests/"
    echo ""
else
    echo "⚠️  Some tests failed. Please check the output above and fix any issues."
    echo "The development environment is set up, but there may be configuration issues."
fi
