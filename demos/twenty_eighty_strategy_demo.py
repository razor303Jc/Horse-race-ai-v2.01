#!/usr/bin/env python3
"""
20/80 Betting Strategy Demo
===========================

Demonstrates the new 20/80 betting strategy where:
- 20% of stake goes on the win market
- 80% of stake goes on the place market

This strategy is ideal for horses with:
- Good place prospects but uncertain win chances
- Higher place probability than win probability
- Reasonable confidence from AI predictions

Example Usage:
- If stake is $100: $20 on win, $80 on place
- Focus on top 3 horses of the day
- Risk-managed approach with bankroll protection
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.betting.advanced_strategies import (
    AdvancedBettingStrategies,
    TwentyEightyStrategy,
)


def create_sample_race_data() -> List[Dict]:
    """Create sample race data for demonstration."""
    return [
        {
            "race_id": "FLM_R3_20250804",
            "track": "Flemington",
            "race_time": "14:30",
            "distance": "1400m",
            "horses": [
                {
                    "horse_name": "Thunder Strike",
                    "barrier": 3,
                    "weight": 58.5,
                    "win_odds": 4.20,
                    "place_odds": 1.60,
                    "prediction": {
                        "win_probability": 0.28,
                        "place_probability": 0.72,
                        "confidence": 0.85,
                        "ai_rating": 8.4,
                    },
                },
                {
                    "horse_name": "Lightning Bolt",
                    "barrier": 7,
                    "weight": 57.0,
                    "win_odds": 6.50,
                    "place_odds": 2.10,
                    "prediction": {
                        "win_probability": 0.18,
                        "place_probability": 0.65,
                        "confidence": 0.78,
                        "ai_rating": 7.2,
                    },
                },
                {
                    "horse_name": "Storm Rider",
                    "barrier": 1,
                    "weight": 59.0,
                    "win_odds": 3.80,
                    "place_odds": 1.50,
                    "prediction": {
                        "win_probability": 0.32,
                        "place_probability": 0.68,
                        "confidence": 0.82,
                        "ai_rating": 8.1,
                    },
                },
            ],
        },
        {
            "race_id": "RAN_R5_20250804",
            "track": "Randwick",
            "race_time": "15:45",
            "distance": "1200m",
            "horses": [
                {
                    "horse_name": "Desert Eagle",
                    "barrier": 4,
                    "weight": 58.0,
                    "win_odds": 5.20,
                    "place_odds": 1.80,
                    "prediction": {
                        "win_probability": 0.22,
                        "place_probability": 0.70,
                        "confidence": 0.79,
                        "ai_rating": 7.8,
                    },
                },
                {
                    "horse_name": "Golden Arrow",
                    "barrier": 8,
                    "weight": 56.5,
                    "win_odds": 7.80,
                    "place_odds": 2.50,
                    "prediction": {
                        "win_probability": 0.15,
                        "place_probability": 0.58,
                        "confidence": 0.73,
                        "ai_rating": 6.9,
                    },
                },
                {
                    "horse_name": "Midnight Express",
                    "barrier": 2,
                    "weight": 57.5,
                    "win_odds": 4.60,
                    "place_odds": 1.70,
                    "prediction": {
                        "win_probability": 0.26,
                        "place_probability": 0.74,
                        "confidence": 0.87,
                        "ai_rating": 8.6,
                    },
                },
            ],
        },
    ]


def demonstrate_single_horse_strategy():
    """Demonstrate 20/80 strategy for a single horse."""
    print("\\n" + "=" * 60)
    print("🐎 SINGLE HORSE 20/80 STRATEGY DEMO")
    print("=" * 60)

    # Initialize betting system
    betting_system = AdvancedBettingStrategies(initial_bankroll=5000.0)

    # Example horse data
    horse_name = "Thunder Strike"
    total_stake = 100.0  # $100 total stake
    win_odds = 4.20
    place_odds = 1.60
    win_probability = 0.28
    place_probability = 0.72
    confidence = 0.85

    print(f"🏇 Horse: {horse_name}")
    print(f"💰 Total Stake: ${total_stake}")
    print(f"🎯 Win Odds: {win_odds}")
    print(f"🥉 Place Odds: {place_odds}")
    print(f"📊 Win Probability: {win_probability:.1%}")
    print(f"📈 Place Probability: {place_probability:.1%}")
    print(f"🔮 Confidence: {confidence:.1%}")

    # Calculate 20/80 strategy
    strategy = betting_system.calculate_twenty_eighty_strategy(
        horse_name=horse_name,
        win_odds=win_odds,
        place_odds=place_odds,
        win_probability=win_probability,
        place_probability=place_probability,
        total_stake=total_stake,
        confidence=confidence,
    )

    print(f"\\n📋 STRATEGY BREAKDOWN:")
    print(f"💵 Win Stake (20%): ${strategy.win_stake:.2f}")
    print(f"💵 Place Stake (80%): ${strategy.place_stake:.2f}")
    print(f"🏆 Potential Win Return: ${strategy.potential_win_return:.2f}")
    print(f"🥉 Potential Place Return: ${strategy.potential_place_return:.2f}")
    print(f"📊 Expected Value: ${strategy.expected_value:.2f}")
    print(f"⚠️  Risk Rating: {strategy.risk_rating}")

    # Scenario analysis
    print(f"\\n🎲 SCENARIO ANALYSIS:")
    print(
        f"📈 If horse WINS: Return ${strategy.potential_win_return:.2f} (Profit: ${strategy.potential_win_return - total_stake:.2f})"
    )
    print(
        f"🥉 If horse PLACES (not win): Return ${strategy.potential_place_return:.2f} (Profit: ${strategy.potential_place_return - total_stake:.2f})"
    )
    print(f"❌ If horse fails to place: Loss ${total_stake:.2f}")


def demonstrate_top_three_selection():
    """Demonstrate selecting top 3 horses for 20/80 strategy."""
    print("\\n" + "=" * 60)
    print("🏆 TOP 3 HORSES 20/80 STRATEGY DEMO")
    print("=" * 60)

    # Initialize betting system with larger bankroll
    betting_system = AdvancedBettingStrategies(initial_bankroll=10000.0)

    # Create sample race data
    race_data = create_sample_race_data()

    print(f"💰 Starting Bankroll: ${betting_system.current_bankroll:,.2f}")
    print(f"📅 Analyzing {len(race_data)} races for top selections...")

    # Get top 3 selections
    top_three = betting_system.get_top_three_twenty_eighty_selections(
        race_predictions=race_data,
        total_daily_bankroll=1500.0,  # $1500 total for the day
    )

    if not top_three:
        print("❌ No suitable selections found for 20/80 strategy")
        return

    print(f"\\n🎯 TOP 3 SELECTIONS IDENTIFIED:")
    print("-" * 50)

    total_stakes = 0
    total_expected_value = 0

    for i, strategy in enumerate(top_three, 1):
        print(f"\\n#{i}: {strategy.horse_name}")
        print(f"   💵 Total Stake: ${strategy.total_stake:.2f}")
        print(
            f"   💵 Win Stake: ${strategy.win_stake:.2f} | Place Stake: ${strategy.place_stake:.2f}"
        )
        print(
            f"   🎯 Win Odds: {strategy.win_odds} | Place Odds: {strategy.place_odds}"
        )
        print(f"   📊 Expected Value: ${strategy.expected_value:.2f}")
        print(f"   ⚠️  Risk Rating: {strategy.risk_rating}")

        total_stakes += strategy.total_stake
        total_expected_value += strategy.expected_value

    print(f"\\n📊 PORTFOLIO SUMMARY:")
    print(f"💰 Total Stakes: ${total_stakes:.2f}")
    print(f"📈 Combined Expected Value: ${total_expected_value:.2f}")
    print(f"📊 Expected ROI: {(total_expected_value / total_stakes) * 100:.1f}%")
    print(
        f"🏦 Remaining Bankroll: ${betting_system.current_bankroll - total_stakes:.2f}"
    )


def demonstrate_risk_scenarios():
    """Demonstrate different risk scenarios for 20/80 strategy."""
    print("\\n" + "=" * 60)
    print("⚠️  RISK SCENARIO ANALYSIS")
    print("=" * 60)

    betting_system = AdvancedBettingStrategies(initial_bankroll=5000.0)

    scenarios = [
        {
            "name": "Low Risk - High Confidence",
            "horse": "Safe Choice",
            "win_odds": 3.50,
            "place_odds": 1.40,
            "win_prob": 0.35,
            "place_prob": 0.78,
            "confidence": 0.92,
        },
        {
            "name": "Medium Risk - Good Value",
            "horse": "Value Pick",
            "win_odds": 6.20,
            "place_odds": 2.10,
            "win_prob": 0.20,
            "place_prob": 0.65,
            "confidence": 0.76,
        },
        {
            "name": "High Risk - Speculative",
            "horse": "Long Shot",
            "win_odds": 12.50,
            "place_odds": 3.80,
            "win_prob": 0.10,
            "place_prob": 0.45,
            "confidence": 0.58,
        },
    ]

    stake = 100.0

    for scenario in scenarios:
        print(f"\\n📋 {scenario['name']}: {scenario['horse']}")

        strategy = betting_system.calculate_twenty_eighty_strategy(
            horse_name=scenario["horse"],
            win_odds=scenario["win_odds"],
            place_odds=scenario["place_odds"],
            win_probability=scenario["win_prob"],
            place_probability=scenario["place_prob"],
            total_stake=stake,
            confidence=scenario["confidence"],
        )

        print(f"   📊 Expected Value: ${strategy.expected_value:.2f}")
        print(f"   ⚠️  Risk Rating: {strategy.risk_rating}")
        print(f"   🎯 Win Return: ${strategy.potential_win_return:.2f}")
        print(f"   🥉 Place Return: ${strategy.potential_place_return:.2f}")


def main():
    """Run the complete 20/80 strategy demonstration."""
    print("🏇 HORSE RACING AI v2.0 - 20/80 BETTING STRATEGY DEMO")
    print("=" * 80)
    print("This demo showcases the new 20/80 betting strategy:")
    print("• 20% of stake on WIN market")
    print("• 80% of stake on PLACE market")
    print("• Ideal for horses with strong place prospects")
    print("• Risk-managed approach with AI confidence scoring")

    try:
        # Run demonstrations
        demonstrate_single_horse_strategy()
        demonstrate_top_three_selection()
        demonstrate_risk_scenarios()

        print("\\n" + "=" * 80)
        print("✅ 20/80 STRATEGY DEMO COMPLETED SUCCESSFULLY!")
        print("🎯 Key Benefits:")
        print("  • Balanced risk between win and place markets")
        print("  • Higher probability of returns through place betting")
        print("  • AI-driven selection with confidence scoring")
        print("  • Automatic top 3 daily selection process")
        print("  • Comprehensive risk assessment")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
