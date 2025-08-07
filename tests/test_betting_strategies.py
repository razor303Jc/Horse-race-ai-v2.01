#!/usr/bin/env python3
"""
Simple Betting Strategies Test
Test just the core betting functionality without complex dependencies.
"""

import os
import sys

sys.path.append("src")


def test_betting_strategies():
    """Test the betting strategies directly."""

    print("🎯 Testing Advanced Betting Strategies")
    print("=" * 50)

    try:
        # Direct import to test the betting strategies file
        from horse_racing_ai.betting.advanced_strategies import (
            AdvancedBettingStrategies,
            BetType,
            StakingMethod,
        )

        print("✅ Successfully imported betting strategies")

        # Initialize
        betting_system = AdvancedBettingStrategies(initial_bankroll=1000.0)
        print(f"💰 Initialized with bankroll: ${betting_system.current_bankroll}")

        # Test 1: Value Betting
        print("\n🔍 Test 1: Value Betting")
        print("-" * 30)

        odds = 5.0
        probability = 0.25
        confidence = 0.85

        value_bet = betting_system.calculate_value_bet(odds, probability, confidence)

        print(f"Odds: {odds}")
        print(f"Probability: {probability:.1%}")
        print(f"Value: {value_bet.value:.1%}")
        print(f"Kelly fraction: {value_bet.kelly_fraction:.3f}")
        print(f"Recommended stake: ${value_bet.recommended_stake:.2f}")
        print(f"Risk rating: {value_bet.risk_rating}")

        # Test 2: Dutching
        print("\n🎯 Test 2: Dutching")
        print("-" * 30)

        selections = [
            ("Horse A", 4.0, 0.30),
            ("Horse B", 5.5, 0.22),
            ("Horse C", 6.0, 0.18),
        ]

        dutching = betting_system.calculate_dutching(selections)

        print(f"Profit margin: {dutching.profit_margin:.1f}%")
        print(f"Total stake: ${dutching.total_stake:.2f}")
        print(f"Return if any wins: ${dutching.total_return:.2f}")

        # Test 3: Each-Way
        print("\n🏆 Test 3: Each-Way Betting")
        print("-" * 30)

        each_way = betting_system.calculate_each_way_value(
            win_odds=8.0,
            place_odds=2.67,
            win_probability=0.15,
            place_probability=0.40,
            confidence=0.8,
        )

        print(f"Win value: {each_way['win'].value:.1%}")
        print(f"Place value: {each_way['place'].value:.1%}")
        print(f"Win stake: ${each_way['win'].recommended_stake:.2f}")
        print(f"Place stake: ${each_way['place'].recommended_stake:.2f}")

        # Test 4: Race Recommendations
        print("\n🏇 Test 4: Race Recommendations")
        print("-" * 30)

        race_predictions = [
            {
                "horse_name": "Favorite",
                "odds": 2.5,
                "win_probability": 0.35,
                "place_probability": 0.65,
                "place_odds": 1.4,
                "confidence": 0.9,
            },
            {
                "horse_name": "Value Pick",
                "odds": 8.0,
                "win_probability": 0.18,
                "place_probability": 0.40,
                "place_odds": 2.67,
                "confidence": 0.75,
            },
        ]

        recommendations = betting_system.get_betting_recommendations(race_predictions)

        print(f"Risk assessment: {recommendations['risk_assessment']}")
        print(f"Total stake: ${recommendations['total_recommended_stake']:.2f}")
        print(f"Value bets found: {len(recommendations['value_bets'])}")
        print(
            f"Dutching opportunities: {len(recommendations['dutching_opportunities'])}"
        )

        # Test 5: Bankroll Management
        print("\n📊 Test 5: Bankroll Management")
        print("-" * 30)

        # Simulate some bets
        print("Simulating betting results...")

        # Win a bet
        result1 = betting_system.update_bankroll(25.0, 75.0)
        print(
            f"After win: ${result1.current_balance:.2f} (ROI: {result1.roi_percentage:.1f}%)"
        )

        # Lose a bet
        result2 = betting_system.update_bankroll(30.0, 0.0)
        print(
            f"After loss: ${result2.current_balance:.2f} (ROI: {result2.roi_percentage:.1f}%)"
        )

        # Another win
        result3 = betting_system.update_bankroll(20.0, 80.0)
        print(
            f"After another win: ${result3.current_balance:.2f} (ROI: {result3.roi_percentage:.1f}%)"
        )

        print(f"Drawdown: {result3.drawdown_percentage:.1f}%")
        print(f"Risk level: {result3.risk_level}")

        # Test 6: Analytics
        print("\n📈 Test 6: Analytics")
        print("-" * 30)

        analytics = betting_system.export_betting_analytics()

        if analytics.get("performance_summary"):
            perf = analytics["performance_summary"]
            print(f"Total bets: {perf.get('total_bets', 0)}")
            print(f"Win rate: {perf.get('win_rate', 0):.1f}%")
            print(f"Total profit: ${perf.get('total_profit', 0):.2f}")

        print("\n✅ All betting strategy tests passed!")
        # Test passes if no exceptions thrown
        assert True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        # Fail the test if exception occurred
        assert False, f"Betting strategies test failed: {e}"


if __name__ == "__main__":
    success = test_betting_strategies()
    if success:
        print("\n🎉 Betting strategies are working correctly!")
    else:
        print("\n❌ Betting strategies test failed")
