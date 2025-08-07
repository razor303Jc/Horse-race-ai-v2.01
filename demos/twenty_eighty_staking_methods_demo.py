#!/usr/bin/env python3
"""
20/80 Bet Type with Different Staking Methods Demo
=================================================

Demonstrates how the 20/80 bet type can be combined with various staking methods.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.betting.advanced_strategies import (
    AdvancedBettingStrategies,
    StakingMethod,
)


def demonstrate_staking_methods():
    """Demonstrate 20/80 bet type with different staking methods."""

    print("🎯 20/80 BET TYPE WITH DIFFERENT STAKING METHODS")
    print("=" * 60)

    # Sample horse data
    horse_data = {
        "horse_name": "Thunder Strike",
        "win_odds": 4.20,
        "place_odds": 1.60,
        "win_probability": 0.28,
        "place_probability": 0.72,
        "confidence": 0.85,
    }

    betting = AdvancedBettingStrategies(initial_bankroll=5000.0)

    # Different staking methods with 20/80 bet type
    staking_methods = [
        (StakingMethod.FIXED, "Fixed amount"),
        (StakingMethod.PERCENTAGE, "Percentage of bankroll"),
        (StakingMethod.KELLY, "Kelly Criterion"),
        (StakingMethod.PROPORTIONAL, "Proportional to value"),
    ]

    print(f"🏇 Horse: {horse_data['horse_name']}")
    print(
        f"🎲 Win Odds: {horse_data['win_odds']} | Place Odds: {horse_data['place_odds']}"
    )
    print(
        f"📊 Win Prob: {horse_data['win_probability']:.1%} | Place Prob: {horse_data['place_probability']:.1%}"
    )
    print(f"🎯 Confidence: {horse_data['confidence']:.1%}")
    print()

    for staking_method, description in staking_methods:
        print(f"📈 STAKING METHOD: {description.upper()}")
        print("-" * 40)

        # Calculate 20/80 strategy with different staking methods
        strategy = betting.calculate_twenty_eighty_strategy(
            horse_name=horse_data["horse_name"],
            win_odds=horse_data["win_odds"],
            place_odds=horse_data["place_odds"],
            win_probability=horse_data["win_probability"],
            place_probability=horse_data["place_probability"],
            confidence=horse_data["confidence"],
            staking_method=staking_method,
        )

        print(f"💰 Total Stake: ${strategy.total_stake:.2f}")
        print(f"  ├─ Win Stake (20%): ${strategy.win_stake:.2f}")
        print(f"  └─ Place Stake (80%): ${strategy.place_stake:.2f}")
        print(f"📊 Expected Value: ${strategy.expected_value:.2f}")
        print(f"⚠️  Risk Rating: {strategy.risk_rating}")
        print(f"🎯 Bet Type: {strategy.bet_type.value}")
        print(f"📐 Staking Method: {strategy.staking_method.value}")

        # Calculate potential returns
        roi = (strategy.expected_value / strategy.total_stake) * 100
        print(f"📈 Expected ROI: {roi:.1f}%")
        print()

    # Comparison table
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Method':<15} {'Total Stake':<12} {'Win/Place':<15} {'EV':<8} {'ROI'}")
    print("-" * 60)

    for staking_method, description in staking_methods:
        strategy = betting.calculate_twenty_eighty_strategy(
            horse_name=horse_data["horse_name"],
            win_odds=horse_data["win_odds"],
            place_odds=horse_data["place_odds"],
            win_probability=horse_data["win_probability"],
            place_probability=horse_data["place_probability"],
            confidence=horse_data["confidence"],
            staking_method=staking_method,
        )

        roi = (strategy.expected_value / strategy.total_stake) * 100
        win_place = f"${strategy.win_stake:.0f}/${strategy.place_stake:.0f}"

        print(
            f"{staking_method.value:<15} ${strategy.total_stake:<11.2f} {win_place:<15} ${strategy.expected_value:<7.2f} {roi:>5.1f}%"
        )

    print()
    print("🎉 Demo completed! The 20/80 bet type works with any staking method.")


def demonstrate_portfolio_example():
    """Demonstrate portfolio with mixed staking methods."""

    print("\n🏆 PORTFOLIO EXAMPLE: MIXED STAKING METHODS")
    print("=" * 60)

    betting = AdvancedBettingStrategies(initial_bankroll=10000.0)

    # Portfolio with different horses and staking methods
    portfolio = [
        {
            "horse": "Safe Bet",
            "win_odds": 2.50,
            "place_odds": 1.30,
            "win_prob": 0.45,
            "place_prob": 0.85,
            "confidence": 0.90,
            "staking": StakingMethod.FIXED,
            "reason": "Conservative approach",
        },
        {
            "horse": "Value Pick",
            "win_odds": 6.00,
            "place_odds": 2.20,
            "win_prob": 0.22,
            "place_prob": 0.55,
            "confidence": 0.75,
            "staking": StakingMethod.KELLY,
            "reason": "High value opportunity",
        },
        {
            "horse": "Steady Eddie",
            "win_odds": 3.80,
            "place_odds": 1.80,
            "win_prob": 0.30,
            "place_prob": 0.68,
            "confidence": 0.80,
            "staking": StakingMethod.PERCENTAGE,
            "reason": "Balanced allocation",
        },
    ]

    total_ev = 0.0
    total_stake = 0.0

    for i, selection in enumerate(portfolio, 1):
        print(f"🏇 SELECTION #{i}: {selection['horse']}")
        print(
            f"📐 Staking Method: {selection['staking'].value} ({selection['reason']})"
        )

        strategy = betting.calculate_twenty_eighty_strategy(
            horse_name=selection["horse"],
            win_odds=selection["win_odds"],
            place_odds=selection["place_odds"],
            win_probability=selection["win_prob"],
            place_probability=selection["place_prob"],
            confidence=selection["confidence"],
            staking_method=selection["staking"],
        )

        print(
            f"💰 Stake: ${strategy.total_stake:.2f} (${strategy.win_stake:.2f} win, ${strategy.place_stake:.2f} place)"
        )
        print(f"📊 Expected Value: ${strategy.expected_value:.2f}")
        print(f"⚠️  Risk: {strategy.risk_rating}")

        total_ev += strategy.expected_value
        total_stake += strategy.total_stake
        print()

    portfolio_roi = (total_ev / total_stake) * 100 if total_stake > 0 else 0

    print("📊 PORTFOLIO SUMMARY")
    print("-" * 30)
    print(f"Total Stake: ${total_stake:.2f}")
    print(f"Total Expected Value: ${total_ev:.2f}")
    print(f"Portfolio ROI: {portfolio_roi:.1f}%")
    print(f"Bankroll Usage: {(total_stake / betting.current_bankroll) * 100:.1f}%")


if __name__ == "__main__":
    demonstrate_staking_methods()
    demonstrate_portfolio_example()
