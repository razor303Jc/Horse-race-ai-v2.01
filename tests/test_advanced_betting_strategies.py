"""
Advanced Betting Strategies Test Suite

This module tests the advanced betting strategies including:
- Kelly Criterion implementation
- Value betting calculations
- Staking methods (fixed, proportional, Kelly)
- Risk management features
- Portfolio optimization
"""

import sys
from pathlib import Path
from typing import Dict, List

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from horse_racing_ai.betting.advanced_strategies import (
    AdvancedBettingStrategies,
    BetType,
    StakingMethod,
)


@pytest.fixture
def betting_system():
    """Create a betting system for testing."""
    return AdvancedBettingStrategies(initial_bankroll=1000.0)


@pytest.fixture
def sample_horse_data():
    """Create sample horse data for testing."""
    return {
        "Thunder Strike": {
            "odds": 3.5,
            "confidence": 0.85,
            "ai_prediction": 0.35,
            "form_score": 8.2,
        },
        "Lightning Bolt": {
            "odds": 2.8,
            "confidence": 0.72,
            "ai_prediction": 0.42,
            "form_score": 7.8,
        },
        "Storm Rider": {
            "odds": 5.2,
            "confidence": 0.68,
            "ai_prediction": 0.25,
            "form_score": 6.9,
        },
    }


def test_initialization(betting_system):
    """Test betting system initialization."""
    assert betting_system.current_bankroll == 1000.0
    assert betting_system.initial_bankroll == 1000.0
    assert betting_system.total_wagered == 0.0
    assert betting_system.total_returned == 0.0
    assert len(betting_system.bet_history) == 0


def test_value_betting_calculation(betting_system, sample_horse_data):
    """Test value betting calculation."""
    horse_data = sample_horse_data["Thunder Strike"]

    # Calculate value bet
    value_bet = betting_system.calculate_value_bet(
        odds=horse_data["odds"],
        true_probability=horse_data["ai_prediction"],
        confidence=horse_data["confidence"],
    )

    # Should return a BettingOpportunity object
    assert hasattr(value_bet, "value")
    assert hasattr(value_bet, "kelly_fraction")
    assert hasattr(value_bet, "recommended_stake")

    # Value should be calculated correctly
    # Implied prob = 1/3.5 = 0.286, true prob = 0.35, so value = (0.35/0.286) - 1 ≈ 0.22
    assert value_bet.value > 0  # Should be a value bet


def test_dutching_calculation(betting_system, sample_horse_data):
    """Test dutching calculation."""
    # Prepare multiple selections for dutching (format: horse, odds, probability)
    selections = []
    for horse, data in sample_horse_data.items():
        selections.append((horse, data["odds"], data["ai_prediction"]))

    # Calculate dutching
    dutch_calc = betting_system.calculate_dutching(selections=selections)

    # Should return a DutchingCalculation object
    assert hasattr(dutch_calc, "total_stake")
    assert hasattr(dutch_calc, "total_return")
    assert hasattr(dutch_calc, "profit_margin")


def test_betting_recommendations(betting_system, sample_horse_data):
    """Test betting recommendations functionality."""
    # Convert sample data to expected format
    race_predictions = []
    for horse, data in sample_horse_data.items():
        race_predictions.append(
            {
                "horse_name": horse,
                "odds": data["odds"],
                "win_probability": data["ai_prediction"],
                "confidence": data["confidence"],
            }
        )

    # Get betting recommendations
    recommendations = betting_system.get_betting_recommendations(
        race_predictions=race_predictions
    )

    # Should return a dict with recommendations
    assert isinstance(recommendations, dict)
    assert "value_bets" in recommendations
    assert "bankroll_status" in recommendations


def test_bankroll_update(betting_system):
    """Test bankroll update functionality."""
    initial_bankroll = betting_system.current_bankroll

    # Simulate a winning bet
    bankroll_state = betting_system.update_bankroll(stake=50.0, payout=150.0)

    # Check that bankroll increased correctly
    assert betting_system.current_bankroll == initial_bankroll - 50.0 + 150.0
    assert bankroll_state.current_balance == betting_system.current_bankroll


def test_analytics_export(betting_system, sample_horse_data):
    """Test analytics export functionality."""
    # First, simulate some betting activity
    betting_system.update_bankroll(stake=30.0, payout=90.0)  # Winning bet
    betting_system.update_bankroll(stake=25.0, payout=0.0)  # Losing bet

    # Export analytics
    analytics = betting_system.export_betting_analytics()

    # Should contain analytics data
    assert isinstance(analytics, dict)
    assert "performance_summary" in analytics
    assert "bankroll_management" in analytics
