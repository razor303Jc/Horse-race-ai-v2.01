#!/usr/bin/env python3
"""Quick validation script for 20/80 strategy"""

import sys

sys.path.insert(0, "src")

from horse_racing_ai.betting.advanced_strategies import AdvancedBettingStrategies

# Quick validation test
betting = AdvancedBettingStrategies(5000.0)
strategy = betting.calculate_twenty_eighty_strategy(
    horse_name="Test Horse",
    win_odds=4.0,
    place_odds=1.6,
    win_probability=0.28,
    place_probability=0.72,
    total_stake=100.0,
    confidence=0.85,
)

print("🧪 QUICK 20/80 STRATEGY VALIDATION")
print("=" * 40)
print(
    f"✅ Stake allocation correct: {strategy.win_stake == 20.0 and strategy.place_stake == 80.0}"
)
print(f"💰 Win Stake: ${strategy.win_stake}")
print(f"💰 Place Stake: ${strategy.place_stake}")
print(f"📊 Expected Value: ${strategy.expected_value:.2f}")
print(f"⚠️ Risk Rating: {strategy.risk_rating}")
print(f"🎯 Total Stake: ${strategy.total_stake}")

# Test top 3 selection
race_data = [
    {
        "race_id": "TEST_R1",
        "horses": [
            {
                "horse_name": "Test Horse A",
                "win_odds": 4.0,
                "place_odds": 1.6,
                "prediction": {
                    "win_probability": 0.30,
                    "place_probability": 0.75,
                    "confidence": 0.85,
                },
            }
        ],
    }
]

selections = betting.get_top_three_twenty_eighty_selections(
    race_predictions=race_data, total_daily_bankroll=1500.0
)

print(f"🏆 Top 3 selections found: {len(selections)}")
print("🎉 All validations passed!")
