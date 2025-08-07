#!/usr/bin/env python3
"""
Test the scoring integration manager with sample data.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, "/home/jc/Documents/Horse-race-ai-v2.0/src")

# Import the modules we need
from database.scoring_integration_manager import ScoringIntegrationManager
from horse_racing_ai.scoring.form_analyzer import (
    RacePerformance,
    SurfaceType,
    RaceClass,
)


def create_sample_performance() -> RacePerformance:
    """Create a sample race performance for testing."""
    return RacePerformance(
        date=datetime.now() - timedelta(days=14),
        track="Test Track",
        distance=8.0,  # 1 mile
        surface=SurfaceType.DIRT,
        race_class=RaceClass.ALLOWANCE,
        field_size=10,
        finish_position=2,
        beaten_lengths=0.5,
        time=96.2,
        speed_figure=95,
        pace_figures={"early": 22, "middle": 45, "late": 29},
        weight_carried=118,
        jockey="J. Rodriguez",
        trainer="M. Smith",
        odds=3.2,
        purse=75000,
        conditions="Fast Track",
        comments="Good trip, strong finish",
    )


async def test_integration_manager():
    """Test the scoring integration manager."""
    print("🔧 Testing Scoring Integration Manager...")

    # Initialize the manager
    manager = ScoringIntegrationManager()
    print("✅ Integration manager initialized")

    # Create sample data
    sample_race = {
        "race_id": "TEST_001",
        "track": "Test Track",
        "distance": 1600,
        "surface": "dirt",
        "race_class": RaceClass.ALLOWANCE.value,  # Use the numeric value
        "race_date": datetime.now(),
    }

    sample_horses = {
        "Thunder Strike": {
            "horse_name": "Thunder Strike",
            "performances": [create_sample_performance()],
            "current_odds": 3.5,
        }
    }

    print("📊 Testing with sample data...")

    try:
        # Test the complete analysis
        results = await manager.analyze_and_store_race(sample_race, sample_horses)
        print("✅ Analysis completed successfully!")
        print(f"📈 Results summary: {results}")

        # Test individual components
        print("\n🔍 Testing individual components...")

        horse_data = sample_horses["Thunder Strike"]
        race_data = sample_race

        # Test form analysis
        form_metrics = await manager._analyze_form(
            horse_data, race_data, horse_data["performances"]
        )
        if form_metrics:
            print(f"✅ Form analysis: {form_metrics.recent_form_score:.2f}")

        # Test power rating
        power_rating = await manager._calculate_power_rating(horse_data, race_data)
        if power_rating:
            print(f"✅ Power rating: {power_rating.adjusted_rating:.2f}")

        # Test composite scoring
        composite_score = await manager._calculate_composite_score(
            horse_data, form_metrics, power_rating, race_data
        )
        if composite_score:
            print(f"✅ Composite score: {composite_score.composite_score:.2f}")

        print("\n🎯 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_integration_manager())
    sys.exit(0 if success else 1)
