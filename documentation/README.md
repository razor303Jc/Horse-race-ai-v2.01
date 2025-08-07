# Horse Racing AI v2.0

A comprehensive horse racing handicapping system powered by artificial intelligence, featuring web scraping, machine learning predictions, and real-time notifications.

## Features

- 🏇 **Automated Data Collection**: Playwright-based web scraping for race data
- 🤖 **AI Predictions**: Machine learning models for race outcome prediction
- � **Advanced Betting Strategies**: 20/80 strategy with risk management and expected value optimization
- �📱 **Real-time Notifications**: NTFY integration for instant alerts
- 🐳 **Docker Support**: Containerized deployment for easy scaling
- 🧪 **Comprehensive Testing**: Full test suite with pytest
- 📊 **Performance Analytics**: Detailed model performance tracking
- 🔧 **CLI Interface**: Command-line tools for all operations

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/horseracingai/horse-racing-ai.git
   cd horse-racing-ai
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   playwright install --with-deps
   ```

4. **Install the package**:

   ```bash
   pip install -e .
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Usage

#### Command Line Interface

```bash
# Check system status
horse-racing-ai status

# Test notifications
horse-racing-ai test-notifications --topic your-topic

# Test web scraper
horse-racing-ai test-scraper

# Scrape race data
horse-racing-ai scrape-race https://example-racing-site.com --username user --password pass

# Train ML model
horse-racing-ai train-model --model-type random_forest
```

#### Python API

```python
import asyncio
from horse_racing_ai import PlaywrightScraper, RacePredictor, ntfy_client
from horse_racing_ai.betting.advanced_strategies import AdvancedBettingStrategies

# Web scraping
async def scrape_data():
    async with PlaywrightScraper() as scraper:
        page = await scraper.create_page()
        race_data = await scraper.scrape_race_data(page, "https://racing-site.com")
        return race_data

# Machine learning predictions
predictor = RacePredictor(model_type="random_forest")
# predictor.train(training_data)  # With actual training data
# predictions = predictor.predict_race(race_data)

# 20/80 Betting Strategy
betting = AdvancedBettingStrategies(initial_bankroll=5000.0)
strategy = betting.calculate_twenty_eighty_strategy(
    horse_name="Champion Horse",
    win_odds=4.20,
    place_odds=1.60,
    win_probability=0.28,
    place_probability=0.72,
    total_stake=100.0,
    confidence=0.85
)
print(f"Expected Value: ${strategy.expected_value:.2f}")

# Notifications
await ntfy_client.send_simple("Race Alert", "New race data available")
```

## Architecture

### Core Components

- **`core/`**: Configuration and shared utilities
- **`automation/`**: Playwright-based web scraping
- **`ml/`**: Machine learning models and predictions
- **`notifications/`**: NTFY notification system
- **`cli.py`**: Command-line interface

### Data Flow

1. **Data Collection**: Playwright scraper collects race data from websites
2. **Feature Engineering**: Raw data is processed into ML features
3. **Prediction**: Trained models generate race predictions
4. **Notification**: Results are sent via NTFY alerts
5. **Storage**: Data and models are persisted to disk/database

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t horse-racing-ai:v2.0 .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f horse-racing-ai
```

### Environment Variables

- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DATABASE_URL`: Database connection string
- `NTFY_TOPIC`: NTFY notification topic
- `NTFY_URL`: NTFY server URL

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`) with your settings:

```bash
# Notifications
NTFY_TOPIC=your-horse-racing-topic
NTFY_URL=https://ntfy.sh

# Database
DATABASE_URL=sqlite:///data/horse_racing.db

# Scraping
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT=30000
```

### Model Configuration

Machine learning models can be configured via:

- Model type: `random_forest`, `gradient_boost`, `logistic`
- Cross-validation folds
- Train/test split ratio
- Feature engineering parameters

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/test_scraper.py

# Run with verbose output
pytest -v
```

### Project Structure

```
src/horse_racing_ai/
├── __init__.py              # Package initialization
├── cli.py                   # Command-line interface
├── core/
│   ├── __init__.py
│   └── config.py           # Configuration management
├── automation/
│   ├── __init__.py
│   └── playwright_scraper.py  # Web scraping
├── ml/
│   ├── __init__.py
│   └── predictor.py        # Machine learning
└── notifications/
    ├── __init__.py
    └── ntfy_client.py      # NTFY notifications

tests/                      # Test suite
docs/                       # Documentation
docker/                     # Docker configurations
```

## Features in Detail

### Web Scraping

- **Playwright Integration**: Modern, reliable browser automation
- **horseracedatabase coming soon playright just a temp fix**
- **Anti-detection**: Stealth techniques and realistic user agents
- **Robust Error Handling**: Retry logic and graceful failures
- **Screenshot Capture**: Debug capabilities with page screenshots
- **Generic Login**: Flexible authentication for various sites

### Machine Learning

- **Multiple Algorithms**: Random Forest, Gradient Boosting, Logistic Regression
- **Feature Engineering**: Automatic feature extraction from race data
- **Model Persistence**: Save and load trained models
- **Performance Metrics**: Comprehensive evaluation with cross-validation
- **Prediction Confidence**: Probability-based predictions with confidence scores

### Notifications

- **NTFY Integration**: Free, open-source notification service
- **Rich Formatting**: Support for priorities, tags, and attachments
- **Batch Notifications**: Send multiple alerts efficiently
- **Customizable Alerts**: Race-specific, prediction, and system notifications

## Development Automation

Horse Racing AI v2.0 includes a comprehensive automation system for development, testing, and deployment. We provide multiple interfaces for different workflows:

### 🤖 Unified Automation Script

The main automation entry point that combines all tools:

```bash
# Quick help
./automate.py --help

# Start full development environment (Python server + browser-sync + CSS compilation)
./automate.py dev

# Run tests with watch mode
./automate.py test --watch

# Format and lint code
./automate.py format
./automate.py lint --fix

# Docker operations
./automate.py docker --build --up
./automate.py docker --down

# Database operations
./automate.py db --migrate
./automate.py db --reset  # WARNING: Destroys data

# Install all dependencies (Python + Node.js)
./automate.py install

# Run all quality checks
./automate.py check
```

### 🔧 Python Tasks (Invoke)

For Python-focused automation using `invoke`:

```bash
# List all available tasks
invoke --list

# Development tasks
invoke dev.serve              # Start development server
invoke dev.test-watch         # Test watch mode

# Code quality
invoke format                 # Format code (black + isort)
invoke lint                   # Run linting (flake8 + mypy)
invoke test                   # Run tests with coverage
invoke check                  # Run all quality checks

# Docker tasks
invoke docker.build           # Build containers
invoke docker.up              # Start containers
invoke docker.down            # Stop containers

# Database tasks
invoke db.migrate             # Run migrations
invoke db.reset --confirm     # Reset database

# File watching
invoke watch test             # Watch and run tests
invoke watch lint             # Watch and run linting
invoke watch check            # Watch and run all checks

# Utilities
invoke clean                  # Clean build artifacts
invoke install                # Install dependencies
invoke monitor                # Start monitoring
```

### 🏗️ Make Commands

Traditional Makefile interface:

```bash
# Show help
make help

# Setup and installation
make install                  # Install all dependencies
make setup                    # Complete setup for new developers

# Development
make dev                      # Start development environment
make serve                    # Start production server

# Code quality
make format                   # Format code
make format-check             # Check formatting
make lint                     # Run linting
make test                     # Run tests with coverage
make test-fast                # Run tests without coverage
make check                    # Run all quality checks

# Watching/monitoring
make watch-test               # Test watch mode
make watch-lint               # Lint watch mode
make watch-check              # Full check watch mode

# Docker
make docker-build             # Build containers
make docker-up                # Start containers
make docker-down              # Stop containers
make docker-restart           # Restart containers
make docker-clean             # Clean containers and volumes

# Database
make db-migrate               # Run migrations
make db-reset                 # Reset database (with confirmation)

# CI/CD
make ci                       # Full CI pipeline
make pre-commit               # Pre-commit checks
make pre-push                 # Pre-push checks

# Utilities
make clean                    # Clean artifacts
make security-check           # Security analysis
make docs-build               # Build documentation
make benchmark                # Performance benchmarks
```

### 🌐 Browser Development (Node.js)

For frontend development with live reloading:

```bash
# Install Node.js dependencies
npm install

# Start browser-sync with live reload
npm start

# Build CSS from SCSS with watching
npm run build:css

# Run JavaScript linting
npm run lint:js

# End-to-end testing with Playwright
npm run test:e2e

# Full development environment
npm run dev                   # Combines CSS compilation + browser-sync
```

### 🎯 VS Code Integration

Tasks are integrated with VS Code for seamless development:

**Command Palette** (`Ctrl+Shift+P`):

- `Tasks: Run Task` → Select from available automation tasks
- `Python: Run Selection/Line in Python Terminal`
- `Python: Run Current File in Terminal`

**Available VS Code Tasks**:

- **Horse Racing AI: Start Development Environment** - Full dev server
- **Horse Racing AI: Run Tests** - Run test suite
- **Horse Racing AI: Run Tests (Watch Mode)** - Continuous testing
- **Horse Racing AI: Format Code** - Auto-format codebase
- **Horse Racing AI: Lint Code** - Run linting
- **Horse Racing AI: Docker Build & Start** - Container setup
- **Horse Racing AI: Database Migration** - DB updates

**Debug Configurations**:

- **Python: Current File** - Debug active Python file
- **Python: Horse Racing AI Web Server** - Debug web server
- **Python: Playwright Scraper** - Debug scraping functionality
- **Python: Run Tests** - Debug test execution
- **Docker: Attach to Container** - Debug containerized app

### 🔍 File Watching & Auto-reload

The automation system includes comprehensive file watching:

**What's Watched**:

- Python files (`.py`) → Auto-run tests, linting, formatting
- SCSS files (`.scss`) → Auto-compile to CSS
- HTML templates → Auto-reload browser
- Configuration files → Auto-restart services
- Docker files → Auto-rebuild containers

**Features**:

- **Debounced Events** - Prevents rapid triggering
- **Intelligent Filtering** - Ignores cache/build files
- **Multi-task Coordination** - Run multiple watchers simultaneously
- **Error Recovery** - Continue watching after failures
- **Rich Console Output** - Clear status indicators

### 🐳 Docker Automation

Complete Docker workflow automation:

```bash
# Quick start
make docker-build docker-up

# Full development stack
docker-compose up -d          # PostgreSQL + Redis + pgAdmin

# Individual services
docker-compose up postgres    # Database only
docker-compose up redis       # Cache only
docker-compose up pgadmin     # DB admin interface

# Logs and monitoring
docker-compose logs -f        # Follow all logs
docker-compose logs postgres  # Database logs only

# Health checks
docker-compose ps             # Container status
```

**Services Included**:

- **PostgreSQL** - Primary database with health checks
- **Redis** - Caching and session management
- **pgAdmin** - Database administration interface
- **Horse Racing AI App** - Main application container
- **Playwright Scraper** - Isolated scraping service

### 📊 Monitoring & Logging

Built-in monitoring capabilities:

```bash
# Start comprehensive monitoring
invoke monitor
# or
make monitor

# View logs
make logs                     # Application logs
docker-compose logs -f        # Container logs

# Performance monitoring
make benchmark                # Run performance tests
```

**Monitoring Features**:

- Container health monitoring
- Database connectivity checks
- Performance metrics tracking
- Error rate monitoring
- Resource usage tracking

### 🔐 Pre-commit Hooks

Automated quality checks before commits:

```bash
# Run pre-commit checks
make pre-commit
# or
./automate.py check

# What's checked:
# ✓ Code formatting (black, isort)
# ✓ Linting (flake8, mypy, eslint)
# ✓ Fast tests (pytest with -x flag)
# ✓ Security checks (optional)
```

### 🎯 Quick Development Workflow

**For new developers**:

```bash
# 1. Complete setup
make setup

# 2. Start development
./automate.py dev
```

**Daily development**:

```bash
# Start coding (in terminal 1)
./automate.py dev

# Run tests continuously (in terminal 2)
./automate.py test --watch

# Before committing
make pre-commit
```

**Before pushing**:

```bash
make pre-push  # Full checks including slow tests
```

### 🛠️ Customization

The automation system is highly customizable:

**Environment Variables** (see `.env.example`):

- Browser-sync ports
- Scraper timeouts
- Test configurations
- Docker settings

**Configuration Files**:

- `tasks.py` - Python automation tasks
- `Makefile` - Make commands
- `package.json` - Node.js scripts
- `bs-config.js` - Browser-sync settings
- `.flake8` - Linting configuration
- `pyproject.toml` - Python project settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/horseracingai/horse-racing-ai/issues)
- **Discussions**: Join discussions on [GitHub Discussions](https://github.com/horseracingai/horse-racing-ai/discussions)

## Roadmap

- [ ] Real-time data streaming
- [ ] Advanced ML features (ensemble models, neural networks)
- [ ] Web dashboard interface
- [ ] Mobile app integration
- [ ] Cloud deployment templates
- [ ] Historical data analysis tools
- [x] **Betting strategy optimization** - 20/80 Strategy implemented ✅

---

**Note**: This system is for educational and research purposes. Please ensure compliance with all applicable laws and website terms of service when scraping data.
