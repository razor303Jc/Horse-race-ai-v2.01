"""
Shared test fixtures and configuration for pytest.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.main import app
from src.core.config import get_settings
from src.database.connection import get_db
from src.models.database import Base
from src.simulation.monte_carlo import HorseSimulationData, SimulationParameters


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings():
    """Test settings configuration."""
    test_settings = get_settings()
    test_settings.database_url = "sqlite+aiosqlite:///./test.db"
    test_settings.redis_url = "redis://redis:6379/15"  # Test database
    test_settings.debug = True
    return test_settings


@pytest.fixture
async def db_engine(settings):
    """Create test database engine."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client for API testing."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    return Mock(spec=AsyncSession)


@pytest.fixture
def sample_horse_data():
    """Sample horse data for testing."""
    return [
        HorseSimulationData(
            horse_id=1,
            name="Thunder Bolt",
            win_probability=0.25,
            place_probability=0.45,
            show_probability=0.65,
            speed_rating=95.0,
            form_rating=88.0,
            weight_carried=58.5,
            jockey_skill=92.0,
            trainer_skill=87.0
        ),
        HorseSimulationData(
            horse_id=2,
            name="Lightning Strike",
            win_probability=0.30,
            place_probability=0.50,
            show_probability=0.70,
            speed_rating=98.0,
            form_rating=91.0,
            weight_carried=59.0,
            jockey_skill=95.0,
            trainer_skill=90.0
        ),
        HorseSimulationData(
            horse_id=3,
            name="Swift Runner",
            win_probability=0.20,
            place_probability=0.40,
            show_probability=0.60,
            speed_rating=90.0,
            form_rating=85.0,
            weight_carried=57.0,
            jockey_skill=88.0,
            trainer_skill=85.0
        )
    ]


@pytest.fixture
def sample_simulation_params():
    """Sample simulation parameters for testing."""
    return SimulationParameters(
        num_runs=100,  # Reduced for faster tests
        race_distance=1600,
        track_condition="good",
        weather_factor=1.0,
        pace_factor=1.0,
        random_seed=42
    )


@pytest.fixture
def mock_prediction_data():
    """Mock prediction data for ML tests."""
    return {
        "features": np.random.rand(100, 10),
        "targets": np.random.randint(0, 8, 100),
        "horse_ids": list(range(1, 101)),
        "race_ids": list(range(1, 101))
    }


@pytest.fixture
def mock_race_data():
    """Mock race data for testing."""
    return {
        "id": 1,
        "name": "Test Race",
        "date": "2024-01-15",
        "track": "Test Track",
        "distance": 1600,
        "surface": "turf",
        "condition": "good",
        "purse": 50000,
        "race_class": "Grade 1"
    }


@pytest.fixture
def mock_horse_data():
    """Mock horse data for testing."""
    return {
        "id": 1,
        "name": "Test Horse",
        "age": 4,
        "sex": "gelding",
        "color": "bay",
        "sire": "Test Sire",
        "dam": "Test Dam",
        "trainer_id": 1,
        "owner": "Test Owner"
    }


@pytest.fixture
def mock_jockey_data():
    """Mock jockey data for testing."""
    return {
        "id": 1,
        "name": "Test Jockey",
        "weight": 52.0,
        "wins": 150,
        "starts": 800,
        "win_percentage": 18.75
    }


@pytest.fixture(autouse=True)
def reset_random_state():
    """Reset numpy random state for reproducible tests."""
    np.random.seed(42)
    yield
    np.random.seed()


@pytest.fixture
def ml_test_data():
    """Generate test data for ML model testing."""
    n_samples = 1000
    n_features = 15
    
    # Generate synthetic horse racing features
    features = np.random.rand(n_samples, n_features)
    
    # Generate targets (finishing positions 1-8)
    targets = np.random.randint(1, 9, n_samples)
    
    return {
        "X": features,
        "y": targets,
        "feature_names": [
            "speed_rating", "form_rating", "weight_carried",
            "jockey_skill", "trainer_skill", "track_condition",
            "distance", "surface", "class_level", "age",
            "recent_performance", "earnings", "starts",
            "wins", "places"
        ]
    }


class AsyncContextManager:
    """Helper class for async context manager testing."""
    
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aaxit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def async_context_manager():
    """Factory for creating async context managers in tests."""
    return AsyncContextManager
