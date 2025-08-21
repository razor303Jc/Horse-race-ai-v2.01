#!/usr/bin/env python3
"""
Quick Test of Enhanced Monte Carlo Betting System
================================================

Quick test to verify integration of 80/20 and Dutching strategies
with Monte Carlo simulation using sample data.

Usage: python quick_enhanced_monte_carlo_test.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from horse_racing_ai.simulation.enhanced_monte_carlo_betting import (
    EnhancedMonteCarloEngine,
)


async def quick_test():
    """Quick test of enhanced Monte Carlo system"""
    print("🧪 QUICK ENHANCED MONTE CARLO TEST")
    print("=" * 50)

    try:
        # Initialize engine with test bankroll
        engine = EnhancedMonteCarloEngine(
            default_bankroll=500.0, enable_real_data=False
        )
        print("✅ Engine initialized successfully")

        # Get sample race data
        races = await engine.get_todays_races()
        print(f"✅ Generated {len(races)} sample races")

        if races:
            # Test analysis on first race
            race_data = races[0]
            print(
                f"\n🎯 Testing analysis on: {race_data.get('race_name', 'Sample Race')}"
            )

            # Run enhanced analysis
            results = await engine.analyze_race_with_strategies(race_data, 500.0)
            print("✅ Analysis completed successfully")

            # Display formatted results
            print("\n" + "=" * 60)
            print(engine.format_enhanced_results(results))

            # Test recommendations display
            print("\n🎯 RECOMMENDATION SUMMARY:")
            if results.recommended_strategy != "No Bet":
                print(f"✅ Strategy: {results.recommended_strategy}")
                print(f"💰 Expected ROI: {results.combined_roi_estimate:.2f}%")

                if (
                    results.eighty_twenty_analysis
                    and results.eighty_twenty_analysis.suitable
                ):
                    print(
                        f"🔸 80/20 Strategy: £{results.eighty_twenty_analysis.total_stake:.2f} stake"
                    )

                if results.dutching_analysis and results.dutching_analysis.suitable:
                    print(
                        f"🔸 Dutching Strategy: £{results.dutching_analysis.total_stake:.2f} stake"
                    )
            else:
                print("❌ No betting opportunities identified")

            print("\n🎉 Test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(quick_test())
