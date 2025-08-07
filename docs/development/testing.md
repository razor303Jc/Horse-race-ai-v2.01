# Testing Guide

## Overview

Horse Racing AI v2.0 includes a comprehensive testing suite designed to ensure reliability, accuracy, and performance across all system components. This guide covers how to run tests, write new tests, and understand the testing architecture.

## Test Structure

### Test Categories

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_scoring.py     # Scoring system tests
│   ├── test_ml.py          # Machine learning tests
│   ├── test_simulation.py  # Monte Carlo simulation tests
│   └── test_web.py         # Web interface tests
├── integration/            # Integration tests
│   ├── test_api.py         # API endpoint tests
│   ├── test_database.py    # Database integration tests
│   └── test_workflow.py    # End-to-end workflow tests
├── performance/            # Performance and load tests
│   ├── test_prediction_speed.py
│   └── test_memory_usage.py
├── fixtures/               # Test data and fixtures
│   ├── sample_races.json
│   └── test_horses.json
└── conftest.py            # Pytest configuration and fixtures
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_scoring.py

# Run tests with specific pattern
pytest -k "test_form_analyzer"

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

### Development Test Workflow

```bash
# Run tests continuously during development
pytest --watch

# Run only failed tests from last run
pytest --lf

# Run tests with debugging
pytest --pdb

# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Test Configuration

### pytest.ini Configuration

```ini
[tool:pytest]
minversion = 7.0
addopts =
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow tests (> 5 seconds)
    requires_network: Tests requiring internet connection
    requires_browser: Tests requiring Playwright browser
```

### Environment Setup for Testing

```bash
# Test environment variables
export TESTING=true
export DEBUG=false
export DATABASE_URL=sqlite:///test.db
export NTFY_TOPIC=test-topic
export ML_MODEL_TYPE=random_forest  # Faster for testing
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_scoring.py
import pytest
from src.horse_racing_ai.scoring.form_analyzer import EnhancedFormAnalyzer
from tests.fixtures.sample_data import sample_horse_data

class TestEnhancedFormAnalyzer:

    def setup_method(self):
        """Setup for each test method."""
        self.analyzer = EnhancedFormAnalyzer()

    def test_form_analysis_basic(self):
        """Test basic form analysis functionality."""
        horse_data = sample_horse_data()
        result = self.analyzer.analyze_form(horse_data)

        assert 'form_score' in result
        assert 0 <= result['form_score'] <= 10
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1

    def test_form_analysis_with_empty_data(self):
        """Test form analysis with empty data."""
        empty_data = {'recent_runs': []}
        result = self.analyzer.analyze_form(empty_data)

        assert result['form_score'] == 0
        assert result['confidence'] < 0.3

    @pytest.mark.parametrize("recent_form,expected_min_score", [
        ([1, 1, 1], 8.0),  # Consistent winner
        ([1, 2, 3], 6.0),  # Improving form
        ([3, 2, 1], 7.0),  # Declining but recent win
        ([5, 5, 5], 3.0),  # Consistent poor form
    ])
    def test_form_scoring_patterns(self, recent_form, expected_min_score):
        """Test form scoring with different patterns."""
        horse_data = {
            'recent_runs': [{'position': pos} for pos in recent_form]
        }
        result = self.analyzer.analyze_form(horse_data)
        assert result['form_score'] >= expected_min_score
```

### Integration Test Example

```python
# tests/integration/test_api.py
import pytest
import requests
from tests.fixtures.sample_data import sample_race_data

@pytest.mark.integration
class TestAPIEndpoints:

    @pytest.fixture(autouse=True)
    def setup_api_client(self, api_base_url):
        """Setup API client for testing."""
        self.base_url = api_base_url

    def test_health_endpoint(self):
        """Test API health check."""
        response = requests.get(f"{self.base_url}/api/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'

    def test_race_analysis_endpoint(self):
        """Test race analysis API."""
        race_data = sample_race_data()

        response = requests.post(
            f"{self.base_url}/api/analyze",
            json=race_data,
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 200
        result = response.json()

        assert 'predictions' in result
        assert 'horses' in result['predictions']
        assert len(result['predictions']['horses']) > 0

        # Validate prediction structure
        horse_prediction = result['predictions']['horses'][0]
        assert 'win_probability' in horse_prediction
        assert 'place_probability' in horse_prediction
        assert 'confidence' in horse_prediction
```

### Performance Test Example

```python
# tests/performance/test_prediction_speed.py
import pytest
import time
from src.horse_racing_ai.ml.predictor import RacePredictor
from tests.fixtures.sample_data import large_race_dataset

@pytest.mark.performance
class TestPredictionPerformance:

    def setup_method(self):
        """Setup predictor for performance testing."""
        self.predictor = RacePredictor(model_type="random_forest")

    def test_single_race_prediction_speed(self):
        """Test single race prediction performance."""
        race_data = sample_race_data()

        start_time = time.time()
        result = self.predictor.predict_race(race_data)
        end_time = time.time()

        prediction_time = end_time - start_time
        assert prediction_time < 2.0  # Should complete in under 2 seconds
        assert result is not None

    @pytest.mark.slow
    def test_batch_prediction_performance(self):
        """Test batch prediction performance."""
        races = large_race_dataset(num_races=100)

        start_time = time.time()
        for race in races:
            self.predictor.predict_race(race)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_race = total_time / len(races)

        assert avg_time_per_race < 1.0  # Average under 1 second per race
```

## Test Fixtures and Data

### Sample Data Fixtures

```python
# tests/fixtures/sample_data.py
import json
from pathlib import Path

def sample_horse_data():
    """Generate sample horse data for testing."""
    return {
        'name': 'Test Horse',
        'age': 4,
        'weight': 126,
        'recent_runs': [
            {'date': '2025-07-01', 'position': 1, 'time': 72.5},
            {'date': '2025-06-15', 'position': 2, 'time': 73.1},
            {'date': '2025-06-01', 'position': 1, 'time': 72.8}
        ],
        'speed_figures': [95, 92, 94],
        'class_ratings': [85, 83, 86]
    }

def sample_race_data():
    """Generate sample race data for testing."""
    return {
        'race_id': 'test_race_001',
        'date': '2025-08-04',
        'distance': 1200,
        'surface': 'turf',
        'class': 3,
        'horses': [
            sample_horse_data(),
            {
                'name': 'Second Horse',
                'age': 5,
                'weight': 124,
                'recent_runs': [
                    {'date': '2025-07-01', 'position': 2, 'time': 73.0},
                    {'date': '2025-06-15', 'position': 1, 'time': 72.9}
                ]
            }
        ]
    }

def load_fixture_data(filename):
    """Load fixture data from JSON file."""
    fixture_path = Path(__file__).parent / filename
    with open(fixture_path, 'r') as f:
        return json.load(f)
```

### Pytest Fixtures

```python
# tests/conftest.py
import pytest
import tempfile
import asyncio
from src.horse_racing_ai.core.config import config

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_database():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        config.database_url = f"sqlite:///{tmp.name}"
        yield tmp.name

@pytest.fixture
def api_base_url():
    """API base URL for integration tests."""
    return "http://localhost:8000"

@pytest.fixture
def mock_race_data():
    """Mock race data for testing."""
    return {
        'horses': [
            {'name': 'Horse A', 'odds': 2.5},
            {'name': 'Horse B', 'odds': 3.0},
            {'name': 'Horse C', 'odds': 4.5}
        ],
        'conditions': {
            'distance': 1200,
            'surface': 'turf'
        }
    }
```

## Mocking and Test Doubles

### Database Mocking

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('src.horse_racing_ai.core.database.get_connection') as mock_conn:
        mock_conn.return_value = Mock()
        yield mock_conn

def test_with_mock_database(mock_database):
    """Test function using mocked database."""
    # Your test code here
    pass
```

### API Mocking

```python
import pytest
from unittest.mock import patch, Mock

@patch('requests.get')
def test_external_api_call(mock_get):
    """Test external API call with mocking."""
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {'status': 'success'}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Your test code here
    result = some_function_that_calls_api()
    assert result['status'] == 'success'
```

## Test Coverage

### Coverage Configuration

```python
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */venv/*
    */migrations/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

### Coverage Targets

- **Overall Coverage**: 85% minimum
- **Core Components**: 90% minimum
- **Critical Paths**: 95% minimum
- **New Code**: 90% minimum

## Continuous Integration

### GitHub Actions Test Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Data Management

### Test Database Setup

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def test_database():
    """Setup test database with sample data."""
    # Create test database
    db_url = "sqlite:///test.db"
    engine = create_engine(db_url)

    # Create tables
    Base.metadata.create_all(engine)

    # Insert test data
    with engine.connect() as conn:
        # Insert sample data here
        pass

    yield engine

    # Cleanup
    os.unlink("test.db")
```

### Sample Data Generation

```python
# tests/utils/data_generator.py
def generate_test_horses(count=10):
    """Generate test horse data."""
    horses = []
    for i in range(count):
        horse = {
            'name': f'Test Horse {i+1}',
            'age': random.randint(3, 8),
            'weight': random.randint(110, 140),
            'recent_form': [random.randint(1, 10) for _ in range(5)]
        }
        horses.append(horse)
    return horses
```

## Best Practices

### Test Organization

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Single Responsibility**: One concept per test
3. **Descriptive Names**: Test names should explain what they test
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Keep unit tests under 1 second

### Test Data

1. **Minimal Data**: Use minimal data needed for the test
2. **Realistic Data**: Use realistic data for integration tests
3. **Edge Cases**: Test boundary conditions and edge cases
4. **Error Conditions**: Test error handling and invalid inputs

### Debugging Tests

```python
# Debug failing tests
pytest --pdb  # Drop into debugger on failure
pytest -s     # Show print statements
pytest -v     # Verbose output
pytest --tb=short  # Shorter traceback format
```

## Running Tests in Docker

```bash
# Run tests in Docker container
docker-compose -f docker-compose.test.yml up --build

# Run specific test file
docker-compose -f docker-compose.test.yml run --rm test pytest tests/unit/test_scoring.py

# Run with coverage
docker-compose -f docker-compose.test.yml run --rm test pytest --cov=src
```

This comprehensive testing guide ensures the reliability and quality of the Horse Racing AI v2.0 system. Regular testing helps maintain code quality and catch issues early in the development process.
