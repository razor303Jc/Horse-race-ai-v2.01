# Development Setup

## Prerequisites for Development

### Required Software

- **Python 3.11+** with pip and venv
- **Docker & Docker Compose** for containerized development
- **Git** for version control
- **Node.js 18+** (optional, for advanced frontend development)

### Recommended Tools

- **VS Code** with Python and Docker extensions
- **Docker Desktop** for easier container management
- **pgAdmin** or **DBeaver** for database management
- **Postman** or **Insomnia** for API testing

## Development Environment Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/Horse-race-handicaping-ai/Horse-race-ai-v2.0.git
cd Horse-race-ai-v2.0

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install Playwright browsers
playwright install --with-deps
```

### 2. Configure Development Environment

```bash
# Copy environment template
cp .env.example .env.dev

# Edit development configuration
nano .env.dev
```

Development `.env.dev` example:

```bash
# Development Configuration
DEBUG=true
LOG_LEVEL=DEBUG
PORT=5002

# Development Database
DATABASE_URL=postgresql://horse_racing:dev_password@localhost:5433/horse_racing_dev

# Development Notifications
NTFY_TOPIC=dev-horse-racing-alerts
NTFY_URL=https://ntfy.sh

# Development Scraping
SCRAPER_HEADLESS=false  # See browser for debugging
SCRAPER_TIMEOUT=60000   # Longer timeout for debugging

# Development ML
ML_MODEL_TYPE=random_forest  # Faster for development
ML_CONFIDENCE_THRESHOLD=0.5
```

### 3. Start Development Services

```bash
# Start database and supporting services
docker-compose -f docker-compose.yml up -d postgres redis ntfy

# Or start everything for full development
docker-compose --profile dev up -d
```

### 4. Run Application Locally

```bash
# Using main entry point
python main.py

# Using web GUI directly
python web_gui.py

# Using CLI for testing
python -m src.horse_racing_ai.cli --help
```

## Development Workflow

### Project Structure

```
Horse-race-ai-v2.0/
├── src/horse_racing_ai/        # Main application code
│   ├── automation/             # Web scraping with Playwright
│   ├── betting/               # Betting strategies and risk management
│   ├── core/                  # Configuration and utilities
│   ├── ml/                    # Machine learning models
│   ├── notifications/         # NTFY notification system
│   ├── scoring/               # Enhanced scoring algorithms
│   ├── simulation/            # Monte Carlo simulation
│   └── cli.py                 # Command-line interface
├── src/web/                   # Web application
│   └── web_gui.py            # Flask web interface
├── src/betdaq/               # BETDAQ betting exchange integration
├── tests/                    # Test suite
├── demos/                    # Example scripts and demonstrations
├── docs/                     # Documentation source
├── templates/                # HTML templates
├── data/                     # Sample and test data
└── docker/                   # Docker configurations
```

### Core Components

#### 1. Scoring System (`src/horse_racing_ai/scoring/`)

**Enhanced Form Analyzer**

```python
from src.horse_racing_ai.scoring.form_analyzer import EnhancedFormAnalyzer

# Initialize analyzer
analyzer = EnhancedFormAnalyzer()

# Analyze horse performance
horse_data = {...}  # Horse performance data
analysis = analyzer.analyze_form(horse_data)
print(f"Form Score: {analysis['form_score']}")
```

**Power Ratings**

```python
from src.horse_racing_ai.scoring.power_ratings import PowerRatingCalculator

# Calculate power ratings
calculator = PowerRatingCalculator()
rating = calculator.calculate_power_rating(horse_data, race_context)
print(f"Power Rating: {rating['total_rating']}")
```

#### 2. Machine Learning (`src/horse_racing_ai/ml/`)

**Training Models**

```python
from src.horse_racing_ai.ml.predictor import RacePredictor

# Initialize and train
predictor = RacePredictor(model_type="ensemble")
predictor.train(training_data)

# Make predictions
predictions = predictor.predict_race(race_data)
```

**Enhanced ML Models**

```python
from enhanced_ml_models import EnhancedMLRatingSystem

# Advanced ML system
ml_system = EnhancedMLRatingSystem()
ml_system.train(training_data)
predictions = ml_system.predict_race_outcomes(race_data)
```

#### 3. Monte Carlo Simulation (`src/horse_racing_ai/simulation/`)

```python
from src.horse_racing_ai.simulation.monte_carlo_simulator import MonteCarloSimulator

# Run simulation
simulator = MonteCarloSimulator()
results = simulator.simulate_race(race_data, num_simulations=10000)
print(f"Win Probability: {results['win_probabilities']}")
```

#### 4. Web Automation (`src/horse_racing_ai/automation/`)

```python
from src.horse_racing_ai.automation.playwright_scraper import PlaywrightScraper

# Web scraping
async with PlaywrightScraper() as scraper:
    page = await scraper.create_page()
    data = await scraper.scrape_race_data(page, url)
```

## Development Tools

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/test_scoring.py

# Run with verbose output
pytest -v

# Run integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Run all quality checks
python automate.py check
```

### Database Development

```bash
# Access development database
docker exec -it horse_racing_postgres psql -U horse_racing -d horse_racing_dev

# View database admin
# Navigate to http://localhost:8083
# Email: admin@horse-racing.localhost
# Password: admin123
```

### Debugging

**Debug Configuration (VS Code)**

```json
{
  "name": "Debug Web App",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/main.py",
  "env": {
    "DEBUG": "true",
    "LOG_LEVEL": "DEBUG"
  },
  "console": "integratedTerminal"
}
```

**Logging Setup**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## API Development

### RESTful API Endpoints

**Core Endpoints**

```bash
# Health check
GET /api/health

# Analyze race
POST /api/analyze
Content-Type: application/json
{
    "horses": [...],
    "race_conditions": {...}
}

# Get predictions
GET /api/predictions/{race_id}

# Model performance
GET /api/performance
```

**Example API Usage**

```python
import requests

# Analyze a race
race_data = {
    "horses": [
        {"name": "Thunder Bolt", "recent_form": [1, 2, 1, 3]},
        {"name": "Lightning Strike", "recent_form": [2, 1, 1, 2]}
    ],
    "race_conditions": {
        "distance": 1200,
        "surface": "turf",
        "class": 3
    }
}

response = requests.post(
    "http://localhost:8000/api/analyze",
    json=race_data
)
predictions = response.json()
```

### Adding New Features

#### 1. Create New Scoring Component

```python
# src/horse_racing_ai/scoring/my_new_scorer.py
from typing import Dict, Any

class MyNewScorer:
    def __init__(self):
        pass

    def calculate_score(self, horse_data: Dict[str, Any]) -> float:
        """Calculate custom score for a horse."""
        # Your scoring logic here
        return score
```

#### 2. Integrate with Main System

```python
# Update src/horse_racing_ai/scoring/__init__.py
from .my_new_scorer import MyNewScorer

# Update composite scorer to include new component
```

#### 3. Add Tests

```python
# tests/test_my_new_scorer.py
import pytest
from src.horse_racing_ai.scoring.my_new_scorer import MyNewScorer

def test_my_new_scorer():
    scorer = MyNewScorer()
    horse_data = {...}
    score = scorer.calculate_score(horse_data)
    assert score > 0
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = some_expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Memory Optimization

```python
# Use generators for large datasets
def process_large_dataset():
    for item in large_dataset:
        yield process_item(item)

# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
memory_usage = process.memory_info().rss / 1024 / 1024  # MB
print(f"Memory usage: {memory_usage:.2f} MB")
```

### Database Optimization

```sql
-- Create indexes for performance
CREATE INDEX idx_horse_name ON horses(name);
CREATE INDEX idx_race_date ON races(date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM races WHERE date > '2025-01-01';
```

## Deployment

### Local Development Deployment

```bash
# Build and run locally
docker-compose -f docker-compose.yml up --build

# Test deployment
curl http://localhost:8000/api/health
```

### Production Deployment

```bash
# Build production image
docker build -t horse-racing-ai:production .

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing Guidelines

### Code Standards

1. **Follow PEP 8**: Use Black for formatting
2. **Type Hints**: Add type hints to all functions
3. **Docstrings**: Document all classes and functions
4. **Tests**: Write tests for all new features
5. **Error Handling**: Implement proper error handling

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new scoring algorithm"

# Push and create pull request
git push origin feature/new-feature
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Error handling is implemented
- [ ] API changes are documented

## Troubleshooting Development Issues

### Common Issues

**Import Errors**

```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

**Database Connection Issues**

```bash
# Check database status
docker-compose ps postgres

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
```

**Port Conflicts**

```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Permission Issues**

```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

## Next Steps

1. **🔧 Setup Environment**: Follow the setup instructions above
2. **🎯 Pick a Task**: Check GitHub issues for contribution opportunities
3. **📖 Read Code**: Explore the codebase to understand the architecture
4. **🧪 Write Tests**: Start with simple test cases
5. **🚀 Submit PR**: Follow the contribution guidelines

Happy coding! 🏇
