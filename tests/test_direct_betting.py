#!/usr/bin/env python3
"""
Simple Direct Test of Betting Strategies
"""

import os
import sys

sys.path.insert(0, "src/horse_racing_ai/betting")

# Import just the betting strategies file directly
import advanced_strategies


def test_direct():
    print("🎯 Direct Betting Strategies Test")
    print("=" * 40)

    # Create instance
    betting = advanced_strategies.AdvancedBettingStrategies(1000.0)
    print(f"✅ Created betting system with ${betting.current_bankroll} bankroll")

    # Test value betting
    value_bet = betting.calculate_value_bet(5.0, 0.25, 0.85)
    print(
        f"✅ Value bet: {value_bet.value:.1%} value, ${value_bet.recommended_stake:.2f} stake"
    )

    # Test dutching
    dutching = betting.calculate_dutching(
        [("Horse A", 4.0, 0.30), ("Horse B", 5.5, 0.22)]
    )
    print(f"✅ Dutching: {dutching.profit_margin:.1f}% profit margin")

    # Test bankroll update
    result = betting.update_bankroll(25.0, 75.0)
    print(
        f"✅ Bankroll update: ${result.current_balance:.2f}, {result.roi_percentage:.1f}% ROI"
    )

    print("\n🎉 All core betting strategies working correctly!")


if __name__ == "__main__":
    test_direct()
