#!/usr/bin/env python3
"""
Test suite for 20/80 Betting Strategy
====================================

Comprehensive tests for the new 20/80 betting strategy implementation.
"""

import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.betting.advanced_strategies import (
    AdvancedBettingStrategies,
    TwentyEightyStrategy,
    StakingMethod,
)


class TestTwentyEightyStrategy:
    """Test cases for 20/80 betting strategy."""

    @pytest.fixture
    def betting_system(self):
        """Create a betting system for testing."""
        return AdvancedBettingStrategies(initial_bankroll=5000.0)

    @pytest.fixture
    def sample_horse_data(self):
        """Sample horse data for testing."""
        return {
            "horse_name": "Test Horse",
            "total_stake": 100.0,
            "win_odds": 4.20,
            "place_odds": 1.60,
            "win_probability": 0.28,
            "place_probability": 0.72,
            "confidence": 0.85,
        }

    def test_twenty_eighty_calculation(self, betting_system, sample_horse_data):
        """Test basic 20/80 strategy calculation."""
        strategy = betting_system.calculate_twenty_eighty_strategy(**sample_horse_data)

        # Test stake allocation
        assert strategy.win_stake == 20.0  # 20% of 100
        assert strategy.place_stake == 80.0  # 80% of 100
        assert strategy.total_stake == 100.0

        # Test potential returns
        assert strategy.potential_win_return == 84.0  # 20 * 4.20
        assert strategy.potential_place_return == 128.0  # 80 * 1.60

        # Test expected value is positive
        assert strategy.expected_value > 0

        # Test risk rating
        assert strategy.risk_rating in ["LOW", "MEDIUM", "HIGH"]

    def test_stake_allocation_percentages(self, betting_system):
        """Test that stake allocation is always 20/80."""
        test_stakes = [50.0, 100.0, 250.0, 500.0]

        for total_stake in test_stakes:
            strategy = betting_system.calculate_twenty_eighty_strategy(
                horse_name="Test",
                win_odds=3.0,
                place_odds=1.5,
                win_probability=0.3,
                place_probability=0.7,
                total_stake=total_stake,
                confidence=0.8,
            )

            # Verify 20/80 allocation
            assert abs(strategy.win_stake - (total_stake * 0.20)) < 0.01
            assert abs(strategy.place_stake - (total_stake * 0.80)) < 0.01
            assert abs(strategy.win_stake + strategy.place_stake - total_stake) < 0.01

    def test_risk_assessment(self, betting_system):
        """Test risk assessment logic."""
        # Low risk scenario
        low_risk = betting_system.calculate_twenty_eighty_strategy(
            horse_name="Safe Horse",
            win_odds=3.0,
            place_odds=1.4,
            win_probability=0.35,
            place_probability=0.80,
            total_stake=100.0,
            confidence=0.90,
        )
        assert low_risk.risk_rating == "LOW"

        # High risk scenario - low confidence
        high_risk = betting_system.calculate_twenty_eighty_strategy(
            horse_name="Risky Horse",
            win_odds=15.0,
            place_odds=4.0,
            win_probability=0.08,
            place_probability=0.35,
            total_stake=100.0,
            confidence=0.55,
        )
        assert high_risk.risk_rating in ["MEDIUM", "HIGH"]

    def test_expected_value_calculation(self, betting_system):
        """Test expected value calculation accuracy."""
        strategy = betting_system.calculate_twenty_eighty_strategy(
            horse_name="Value Test",
            win_odds=5.0,
            place_odds=2.0,
            win_probability=0.25,
            place_probability=0.65,
            total_stake=100.0,
            confidence=0.80,
        )

        # Manual calculation
        win_stake = 20.0
        place_stake = 80.0
        win_return = win_stake * 5.0  # 100
        place_return = place_stake * 2.0  # 160

        win_ev = (0.25 * win_return) - win_stake  # 25 - 20 = 5
        place_ev = (0.65 * place_return) - place_stake  # 104 - 80 = 24
        total_ev = (win_ev + place_ev) * 0.80  # Adjusted by confidence

        assert abs(strategy.expected_value - total_ev) < 0.01

    def test_top_three_selection(self, betting_system):
        """Test top 3 selection functionality."""
        race_data = [
            {
                "race_id": "TEST_R1",
                "horses": [
                    {
                        "horse_name": "Horse A",
                        "win_odds": 4.0,
                        "place_odds": 1.6,
                        "prediction": {
                            "win_probability": 0.30,
                            "place_probability": 0.75,
                            "confidence": 0.85,
                        },
                    },
                    {
                        "horse_name": "Horse B",
                        "win_odds": 6.0,
                        "place_odds": 2.2,
                        "prediction": {
                            "win_probability": 0.20,
                            "place_probability": 0.68,
                            "confidence": 0.78,
                        },
                    },
                ],
            }
        ]

        selections = betting_system.get_top_three_twenty_eighty_selections(
            race_predictions=race_data, total_daily_bankroll=1500.0
        )

        assert len(selections) <= 3
        assert len(selections) >= 1  # Should find at least one selection

        for selection in selections:
            assert isinstance(selection, TwentyEightyStrategy)
            assert selection.total_stake > 0
            assert selection.win_stake > 0
            assert selection.place_stake > 0

    def test_bankroll_limits(self, betting_system):
        """Test that strategy respects bankroll limits."""
        # Test with excessive stake
        large_stake = betting_system.current_bankroll * 0.10  # 10% of bankroll

        strategy = betting_system.calculate_twenty_eighty_strategy(
            horse_name="Big Bet",
            win_odds=3.0,
            place_odds=1.5,
            win_probability=0.3,
            place_probability=0.7,
            total_stake=large_stake,
            confidence=0.8,
        )

        # Should flag as risky if exceeds limits
        max_allowed = (
            betting_system.current_bankroll * betting_system.max_bet_percentage
        )
        if large_stake > max_allowed:
            assert strategy.risk_rating in ["MEDIUM", "HIGH"]

    def test_scenario_outcomes(self, betting_system, sample_horse_data):
        """Test different outcome scenarios."""
        strategy = betting_system.calculate_twenty_eighty_strategy(**sample_horse_data)

        # Win scenario
        win_profit = strategy.potential_win_return - strategy.total_stake

        # Place only scenario
        place_profit = strategy.potential_place_return - strategy.total_stake

        # Fail scenario
        fail_loss = -strategy.total_stake

        # Verify calculations
        assert win_profit == 84.0 - 100.0  # -16.0
        assert place_profit == 128.0 - 100.0  # 28.0
        assert fail_loss == -100.0

    def test_confidence_adjustment(self, betting_system):
        """Test that confidence affects expected value."""
        base_params = {
            "horse_name": "Confidence Test",
            "win_odds": 4.0,
            "place_odds": 1.8,
            "win_probability": 0.3,
            "place_probability": 0.7,
            "total_stake": 100.0,
        }

        high_confidence = betting_system.calculate_twenty_eighty_strategy(
            **base_params, confidence=0.9
        )

        low_confidence = betting_system.calculate_twenty_eighty_strategy(
            **base_params, confidence=0.6
        )

        # Higher confidence should result in higher expected value
        assert high_confidence.expected_value > low_confidence.expected_value


def test_twenty_eighty_integration():
    """Integration test for 20/80 strategy."""
    print("\\n" + "=" * 50)
    print("🧪 20/80 STRATEGY INTEGRATION TEST")
    print("=" * 50)

    betting_system = AdvancedBettingStrategies(initial_bankroll=10000.0)

    # Test single horse strategy
    strategy = betting_system.calculate_twenty_eighty_strategy(
        horse_name="Integration Test Horse",
        win_odds=4.50,
        place_odds=1.70,
        win_probability=0.26,
        place_probability=0.74,
        total_stake=200.0,
        confidence=0.82,
    )

    print("✅ Single horse strategy calculated")
    print(f"   💰 Win Stake: ${strategy.win_stake}")
    print(f"   💰 Place Stake: ${strategy.place_stake}")
    print(f"   📊 Expected Value: ${strategy.expected_value:.2f}")
    print(f"   ⚠️  Risk Rating: {strategy.risk_rating}")

    # Test portfolio simulation
    results = []
    for i in range(10):
        test_strategy = betting_system.calculate_twenty_eighty_strategy(
            horse_name=f"Test Horse {i+1}",
            win_odds=3.0 + i * 0.5,
            place_odds=1.4 + i * 0.1,
            win_probability=0.35 - i * 0.02,
            place_probability=0.75 - i * 0.02,
            total_stake=100.0,
            confidence=0.85 - i * 0.03,
        )
        results.append(test_strategy.expected_value)

    avg_ev = sum(results) / len(results)
    print("✅ Portfolio simulation completed")
    print(f"   📈 Average Expected Value: ${avg_ev:.2f}")
    print(f"   📊 Total Strategies: {len(results)}")

    print("🎉 Integration test completed successfully!")


if __name__ == "__main__":
    # Run integration test
    test_twenty_eighty_integration()

    # Run pytest if available
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\\n⚠️  pytest not available, skipping unit tests")
        print("Install with: pip install pytest")
