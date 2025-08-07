#!/usr/bin/env python3
"""
Advanced Betting Strategies Demonstration
Comprehensive demonstration of dutching, value betting, staking systems, and AI integration.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_advanced_betting_strategies():
    """Demonstrate the complete advanced betting strategies system."""

    print("🎯 Advanced Betting Strategies Demonstration")
    print("=" * 60)

    try:
        # Import the betting strategies
        from src.horse_racing_ai.betting.advanced_strategies import (
            AdvancedBettingStrategies,
            BetType,
            StakingMethod,
        )
        from src.horse_racing_ai.integration.ai_betting_integration import (
            AIBettingIntegrationSystem,
        )

        print("✅ Successfully imported advanced betting modules")

        # Initialize the systems
        betting_strategies = AdvancedBettingStrategies(initial_bankroll=1000.0)
        ai_integration = AIBettingIntegrationSystem(initial_bankroll=1000.0)

        print(f"💰 Initialized with bankroll: ${betting_strategies.current_bankroll}")
        print()

        # Demonstrate Value Betting
        print("🔍 DEMONSTRATION 1: Value Betting Analysis")
        print("-" * 40)

        # Example: Horse with odds 5.0 but AI predicts 25% win probability
        odds = 5.0
        true_probability = 0.25
        confidence = 0.85

        value_bet = betting_strategies.calculate_value_bet(
            odds, true_probability, confidence
        )

        print(f"Horse: Premium Pick")
        print(f"Bookmaker odds: {odds:.1f}")
        print(f"AI win probability: {true_probability:.1%}")
        print(f"AI confidence: {confidence:.1%}")
        print(f"Betting value: {value_bet.value:.1%}")
        print(f"Kelly fraction: {value_bet.kelly_fraction:.3f}")
        print(f"Recommended stake: ${value_bet.recommended_stake:.2f}")
        print(f"Risk rating: {value_bet.risk_rating}")
        print(f"Potential profit: ${value_bet.recommended_stake * (odds - 1):.2f}")
        print()

        # Demonstrate Dutching
        print("🎯 DEMONSTRATION 2: Dutching Strategy")
        print("-" * 40)

        # Example: Multiple selections for guaranteed profit
        selections = [
            ("Thunder Strike", 4.0, 0.30),  # Horse, odds, probability
            ("Lightning Bolt", 5.5, 0.22),
            ("Storm Runner", 6.0, 0.18),
        ]

        dutching = betting_strategies.calculate_dutching(selections)

        if dutching.profit_margin > 0:
            print("Dutching Opportunity Found!")
            print(f"Profit margin: {dutching.profit_margin:.1f}%")
            print(f"Total stake: ${dutching.total_stake:.2f}")
            print(f"Guaranteed return: ${dutching.total_return:.2f}")
            print(f"ROI if any selection wins: {dutching.roi_if_win:.1f}%")
            print("Individual stakes:")
            for selection in dutching.selections:
                print(
                    f"  {selection['horse']}: ${selection['stake']:.2f} "
                    f"(odds {selection['odds']:.1f})"
                )
        else:
            print("No dutching opportunity - market too efficient")
        print()

        # Demonstrate Staking Methods
        print("💡 DEMONSTRATION 3: Staking Method Comparison")
        print("-" * 40)

        kelly_fraction = 0.08  # 8% Kelly
        betting_value = 0.15  # 15% value

        for method in StakingMethod:
            stake = betting_strategies._calculate_stake(
                kelly_fraction, betting_value, method
            )
            percentage = (stake / betting_strategies.current_bankroll) * 100
            print(f"{method.value:12s}: ${stake:6.2f} ({percentage:4.1f}% of bankroll)")
        print()

        # Demonstrate Each-Way Betting
        print("🏆 DEMONSTRATION 4: Each-Way Analysis")
        print("-" * 40)

        win_odds = 8.0
        place_odds = 2.67  # Typically 1/3 of win odds
        win_probability = 0.15
        place_probability = 0.40

        each_way = betting_strategies.calculate_each_way_value(
            win_odds, place_odds, win_probability, place_probability, 0.8
        )

        print(f"Horse: Long Shot Special")
        print(
            f"Win bet  - Value: {each_way['win'].value:.1%}, "
            f"Stake: ${each_way['win'].recommended_stake:.2f}"
        )
        print(
            f"Place bet - Value: {each_way['place'].value:.1%}, "
            f"Stake: ${each_way['place'].recommended_stake:.2f}"
        )
        total_stake = (
            each_way["win"].recommended_stake + each_way["place"].recommended_stake
        )
        print(f"Total each-way stake: ${total_stake:.2f}")
        print()

        # Demonstrate Race Analysis
        print("🏇 DEMONSTRATION 5: Complete Race Analysis")
        print("-" * 40)

        # Simulate a race with multiple horses
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
                "horse_name": "Second Choice",
                "odds": 4.0,
                "win_probability": 0.25,
                "place_probability": 0.55,
                "place_odds": 1.8,
                "confidence": 0.85,
            },
            {
                "horse_name": "Value Pick",
                "odds": 8.0,
                "win_probability": 0.18,
                "place_probability": 0.40,
                "place_odds": 2.67,
                "confidence": 0.75,
            },
            {
                "horse_name": "Long Shot",
                "odds": 15.0,
                "win_probability": 0.08,
                "place_probability": 0.25,
                "place_odds": 5.0,
                "confidence": 0.65,
            },
        ]

        recommendations = betting_strategies.get_betting_recommendations(
            race_predictions
        )

        print(f"Risk assessment: {recommendations['risk_assessment']}")
        print(
            f"Total recommended stake: ${recommendations['total_recommended_stake']:.2f}"
        )
        print()

        if recommendations["value_bets"]:
            print("Value Betting Opportunities:")
            for i, bet in enumerate(recommendations["value_bets"], 1):
                print(
                    f"  {i}. {bet.horse_name} - Value: {bet.value:.1%}, "
                    f"Stake: ${bet.recommended_stake:.2f}"
                )

        if recommendations["dutching_opportunities"]:
            print("Dutching Opportunities:")
            for i, dutch in enumerate(recommendations["dutching_opportunities"], 1):
                print(
                    f"  {i}. {len(dutch.selections)} horses - "
                    f"Profit: {dutch.profit_margin:.1f}%"
                )

        if recommendations["each_way_bets"]:
            print("Each-Way Opportunities:")
            for i, ew in enumerate(recommendations["each_way_bets"], 1):
                print(
                    f"  {i}. {ew['win'].horse_name} - "
                    f"Total stake: ${ew['win'].recommended_stake + ew['place'].recommended_stake:.2f}"
                )
        print()

        # Demonstrate Bankroll Management
        print("📊 DEMONSTRATION 6: Bankroll Management")
        print("-" * 40)

        # Simulate some betting results
        print("Simulating betting results...")

        # Winning bet
        betting_strategies.update_bankroll(25.0, 75.0)  # $25 stake, $75 return
        print(f"After winning bet: ${betting_strategies.current_bankroll:.2f}")

        # Losing bet
        betting_strategies.update_bankroll(30.0, 0.0)  # $30 stake, $0 return
        print(f"After losing bet: ${betting_strategies.current_bankroll:.2f}")

        # Another winning bet
        betting_strategies.update_bankroll(20.0, 80.0)  # $20 stake, $80 return
        print(f"After another win: ${betting_strategies.current_bankroll:.2f}")

        # Get bankroll status
        bankroll_status = betting_strategies._get_current_bankroll_status()
        print()
        print("Current Bankroll Status:")
        print(f"  Balance: ${bankroll_status.current_balance:.2f}")
        print(f"  Net profit: ${bankroll_status.net_profit:.2f}")
        print(f"  ROI: {bankroll_status.roi_percentage:.1f}%")
        print(f"  Drawdown: {bankroll_status.drawdown_percentage:.1f}%")
        print(f"  Risk level: {bankroll_status.risk_level}")
        print()

        # Demonstrate Analytics
        print("📈 DEMONSTRATION 7: Betting Analytics")
        print("-" * 40)

        analytics = betting_strategies.export_betting_analytics()

        if analytics.get("performance_summary"):
            perf = analytics["performance_summary"]
            print("Performance Summary:")
            print(f"  Total bets: {perf.get('total_bets', 0)}")
            print(f"  Win rate: {perf.get('win_rate', 0):.1f}%")
            print(f"  Total profit: ${perf.get('total_profit', 0):.2f}")
            print(f"  ROI: {perf.get('roi', 0):.1f}%")

        if analytics.get("risk_metrics"):
            risk = analytics["risk_metrics"]
            print("Risk Metrics:")
            print(f"  Max drawdown: {risk.get('max_drawdown', 0):.1f}%")
            print(f"  Current risk: {risk.get('current_risk_level', 'Unknown')}")
        print()

        # Demonstrate AI Integration
        print("🤖 DEMONSTRATION 8: AI Integration")
        print("-" * 40)

        # Create mock race data
        race_data = {
            "race_id": "demo_race_001",
            "track": "Churchill Downs",
            "distance": "1200m",
            "surface": "turf",
        }

        horses_data = [
            {
                "name": "AI Favorite",
                "recent_form_score": 85,
                "speed_rating": 95,
                "class_rating": 80,
            },
            {
                "name": "Value Selection",
                "recent_form_score": 75,
                "speed_rating": 88,
                "class_rating": 75,
            },
            {
                "name": "Dark Horse",
                "recent_form_score": 70,
                "speed_rating": 82,
                "class_rating": 70,
            },
        ]

        betting_odds = {"AI Favorite": 2.8, "Value Selection": 5.5, "Dark Horse": 12.0}

        # Run AI integration analysis
        integration_result = ai_integration.analyze_race_with_ai_betting(
            race_data, horses_data, betting_odds
        )

        print(f"AI Analysis completed for: {integration_result.race_id}")
        print(f"Overall confidence: {integration_result.confidence_score:.1%}")
        print(f"Risk assessment: {integration_result.risk_assessment}")
        print(
            f"Bankroll impact: {integration_result.bankroll_impact['percentage_of_bankroll']:.1f}%"
        )
        print()

        # Get integration analytics
        integration_analytics = ai_integration.get_integration_analytics()
        print("Integration Analytics:")
        if integration_analytics.get("integration_summary"):
            summary = integration_analytics["integration_summary"]
            print(f"  Races analyzed: {summary.get('total_races_analyzed', 0)}")
            print(f"  Average confidence: {summary.get('average_confidence', 0):.1%}")
            print(f"  Average risk: {summary.get('average_risk_level', 'Unknown')}")

        print()
        print("🎉 Advanced Betting Strategies Demonstration Complete!")
        print("=" * 60)
        print()
        print("KEY FEATURES DEMONSTRATED:")
        print("✅ Value Betting with Kelly Criterion")
        print("✅ Dutching for Guaranteed Profits")
        print("✅ Multiple Staking Methods")
        print("✅ Each-Way Betting Analysis")
        print("✅ Comprehensive Race Analysis")
        print("✅ Dynamic Bankroll Management")
        print("✅ Performance Analytics")
        print("✅ AI-Betting Integration")
        print()
        print("💡 All systems are now integrated into the Horse Racing AI v2.0!")
        print("🌐 Access via web interface: http://localhost:5002")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all modules are properly installed")
        return False
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return False

    return True


def create_betting_strategies_summary():
    """Create a comprehensive summary of betting strategies implementation."""

    summary = {
        "implementation_status": "COMPLETE",
        "timestamp": "2024-01-15",
        "components": {
            "advanced_strategies": {
                "file": "src/horse_racing_ai/betting/advanced_strategies.py",
                "lines": 611,
                "features": [
                    "Value Betting with Kelly Criterion",
                    "Dutching Calculations",
                    "Multiple Staking Methods (Kelly, Fixed, Percentage, Proportional)",
                    "Each-Way Betting Analysis",
                    "Dynamic Bankroll Management",
                    "Risk Assessment",
                    "Performance Analytics",
                ],
            },
            "ai_integration": {
                "file": "src/horse_racing_ai/integration/ai_betting_integration.py",
                "features": [
                    "AI Prediction to Betting Format Conversion",
                    "Confidence-Based Filtering",
                    "Comprehensive Race Analysis",
                    "Performance Tracking",
                    "Integration Analytics",
                ],
            },
            "web_interface": {
                "file": "web_gui.py",
                "new_endpoints": [
                    "/api/advanced-betting-strategies/<race_index>",
                    "/api/betting-analytics",
                    "/api/update-bankroll",
                    "/api/staking-calculator",
                    "/api/ai-betting-integration/<race_index>",
                    "/api/ai-betting-results",
                ],
            },
            "enhanced_tracker": {
                "file": "src/horse_racing_ai/performance/enhanced_tracker.py",
                "integration": "integrate_betting_strategies method with comprehensive analysis",
            },
        },
        "betting_strategies": {
            "value_betting": {
                "description": "Identifies bets where AI probability exceeds implied odds probability",
                "calculation": "Value = (True Probability / Implied Probability) - 1",
                "stake_sizing": "Kelly Criterion with safety multiplier",
            },
            "dutching": {
                "description": "Bet on multiple selections to guarantee profit regardless of winner",
                "requirement": "Combined implied probability < 1.0",
                "profit_calculation": "Profit Margin = (1 - Total Implied Probability) * 100",
            },
            "staking_methods": {
                "kelly": "Optimal growth rate based on edge and odds",
                "fixed": "Fixed amount per bet for consistent exposure",
                "percentage": "Fixed percentage of bankroll",
                "proportional": "Stake proportional to betting value",
            },
            "each_way": {
                "description": "Split stake between win and place bets",
                "use_case": "Longer odds horses with good place chances",
            },
        },
        "bankroll_management": {
            "features": [
                "Real-time balance tracking",
                "Drawdown monitoring",
                "ROI calculation",
                "Risk level assessment",
                "Recommended maximum bet sizing",
            ],
            "safety_limits": {
                "max_bet_percentage": "5% of bankroll per bet",
                "max_race_exposure": "15% of bankroll per race",
                "kelly_multiplier": "0.25 (quarter Kelly for safety)",
            },
        },
        "integration_points": {
            "ai_predictions": "Converts AI confidence and probabilities to betting format",
            "performance_tracking": "Enhanced tracker monitors betting effectiveness",
            "web_interface": "Complete API for accessing all betting features",
            "risk_management": "Multi-layer risk assessment and control",
        },
        "usage_examples": {
            "basic_value_bet": "calculate_value_bet(odds=5.0, probability=0.25, confidence=0.85)",
            "dutching": "calculate_dutching([(horse1, odds1, prob1), (horse2, odds2, prob2)])",
            "race_analysis": "get_betting_recommendations(race_predictions)",
            "bankroll_update": "update_bankroll(stake=25.0, payout=75.0)",
        },
    }

    # Save summary to file
    summary_file = Path("BETTING_STRATEGIES_IMPLEMENTATION_SUMMARY.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"📄 Implementation summary saved to: {summary_file}")
    return summary


if __name__ == "__main__":
    print("🚀 Starting Advanced Betting Strategies Demonstration...")
    print()

    # Run the demonstration
    success = demonstrate_advanced_betting_strategies()

    if success:
        print()
        print("📋 Creating implementation summary...")
        create_betting_strategies_summary()
        print()
        print("✅ All demonstrations completed successfully!")
    else:
        print("❌ Demonstration failed - check error messages above")
