# Installation Guide

## Prerequisites

Before installing Horse Racing AI v2.0, ensure you have the following:

### Required Software

- **Docker & Docker Compose** (Recommended - easiest setup)
- **Python 3.11+** (for local development)
- **Git** (for cloning the repository)

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for data feeds and notifications

## Installation Methods

### 🐳 Method 1: Docker Installation (Recommended)

This is the fastest and most reliable way to get started.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Horse-race-handicaping-ai/Horse-race-ai-v2.0.git
cd Horse-race-ai-v2.0
```

#### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the configuration (optional)
nano .env
```

#### Step 3: Start the System

```bash
# Start all services
docker-compose up -d

# Or start with documentation
docker-compose --profile docs up -d
```

#### Step 4: Verify Installation

```bash
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f horse-racing-ai
```

#### Access Points:

- **Main Application**: http://localhost:8000
- **Documentation**: http://localhost:8001
- **Database Admin**: http://localhost:8083
- **Notifications**: http://localhost:8081

### 🐍 Method 2: Local Python Installation

For development or custom setups.

#### Step 1: Clone and Setup

```bash
git clone https://github.com/Horse-race-handicaping-ai/Horse-race-ai-v2.0.git
cd Horse-race-ai-v2.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

#### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install --with-deps
```

#### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

#### Step 4: Start the Application

```bash
# Using the main entry point
python main.py

# Or using the CLI
python -m src.horse_racing_ai.cli --help
```

## Configuration

### Environment Variables

Edit your `.env` file to customize the system:

```bash
# Application Settings
DEBUG=false
LOG_LEVEL=INFO
PORT=5002

# Database Configuration
DATABASE_URL=postgresql://horse_racing:password@localhost:5433/horse_racing_db

# Notifications (NTFY)
NTFY_TOPIC=your-horse-racing-topic
NTFY_URL=https://ntfy.sh

# Web Scraping
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT=30000

# Machine Learning
ML_MODEL_TYPE=ensemble
ML_CONFIDENCE_THRESHOLD=0.7

# Betting Configuration
BETTING_ENABLED=false
MAX_BET_AMOUNT=100
MIN_ODDS=1.5
```

### NTFY Notifications Setup

To receive real-time notifications:

1. **Choose a Topic**: Pick a unique topic name (e.g., `my-horse-racing-alerts`)
2. **Update Environment**: Set `NTFY_TOPIC` in your `.env` file
3. **Subscribe**: Install the NTFY app on your phone and subscribe to your topic
4. **Test**: Use the CLI to test notifications

```bash
# Test notifications
python -m src.horse_racing_ai.cli test-notifications --topic your-topic
```

## Quick Start

### 1. Web Interface

Navigate to http://localhost:8000 (or your configured port) to access the web dashboard:

- **Dashboard**: Overview of recent predictions and system status
- **Race Analysis**: Upload or analyze race data
- **Performance**: View model performance and statistics
- **Settings**: Configure notifications and preferences

### 2. Command Line Interface

```bash
# Check system status
python -m src.horse_racing_ai.cli status

# Test the scraper
python -m src.horse_racing_ai.cli test-scraper

# Train ML models
python -m src.horse_racing_ai.cli train-model --model-type ensemble

# Analyze a race
python -m src.horse_racing_ai.cli analyze-race --file race_data.json
```

### 3. API Usage

```python
import asyncio
from src.horse_racing_ai import PlaywrightScraper, RacePredictor

# Initialize components
predictor = RacePredictor()

# Make predictions
race_data = {...}  # Your race data
predictions = predictor.predict_race(race_data)
print(predictions)
```

## Verification

### Test the Installation

1. **Web Interface**: Navigate to http://localhost:8000
2. **Health Check**: All services should show "healthy" status
3. **Test Prediction**: Upload sample race data and get predictions
4. **Notifications**: Send a test notification

### Sample Data

The system includes sample data for testing:

```bash
# Generate test data
python generate_massive_test_data.py

# Run demo
python demos/enhanced_scoring_demo.py
```

## Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check what's using the port
netstat -tlnp | grep :8000

# Use different ports in docker-compose.yml
```

#### Permission Issues

```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

#### Browser Issues

```bash
# Reinstall Playwright browsers
playwright install --force --with-deps
```

#### Database Connection

```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Getting Help

- **Documentation**: http://localhost:8001
- **Logs**: `docker-compose logs -f`
- **Issues**: Check the GitHub repository
- **Configuration**: Review the `.env` file

## Next Steps

1. **Explore the Interface**: Familiarize yourself with the web dashboard
2. **Test Predictions**: Try the sample data or upload your own
3. **Configure Notifications**: Set up NTFY for real-time alerts
4. **Read Documentation**: Explore the full documentation for advanced features
5. **Join Development**: Check out the development guide if you want to contribute

Ready to start analyzing? Head to the [Quick Start Guide](quickstart.md)!
