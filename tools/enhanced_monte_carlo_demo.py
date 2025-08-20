#!/usr/bin/env python3
"""
Enhanced Monte Carlo Simulation Demo
===================================

Demonstrates the integration of horse-bot's advanced Monte Carlo engine
with v2.03 system, showing both basic and advanced simulation modes.
"""

import asyncio
import json
import time
from typing import Dict, List, Any

# Import the enhanced Monte Carlo integration
try:
    from src.horse_racing_ai.simulation.monte_carlo_integration import (
        monte_carlo_integration,
    )
    from src.horse_racing_ai.simulation.enhanced_monte_carlo_engine import (
        AdvancedSimulationParameters,
    )
except ImportError:
    print("⚠️  Unable to import enhanced Monte Carlo modules")
    print("   Make sure you're running from the project root directory")
    exit(1)


def create_sample_race_data() -> List[Dict[str, Any]]:
    """Create sample race data for demonstration."""
    return [
        {
            "name": "Thunder Strike",
            "jockey": "J. Spencer",
            "trainer": "M. Johnston",
            "weight_carried": 58.5,
            "odds": 3.5,
            "speed_rating": 85.0,
            "form_rating": 82.0,
            "jockey_skill": 88.0,
            "trainer_skill": 85.0,
            "recent_form": [1, 3, 2, 1, 4],
            "win_probability": 0.25,
        },
        {
            "name": "Royal Ascent",
            "jockey": "W. Buick",
            "trainer": "C. Appleby",
            "weight_carried": 59.0,
            "odds": 4.2,
            "speed_rating": 83.0,
            "form_rating": 85.0,
            "jockey_skill": 92.0,
            "trainer_skill": 90.0,
            "recent_form": [2, 1, 3, 2, 1],
            "win_probability": 0.22,
        },
        {
            "name": "Desert Wind",
            "jockey": "R. Moore",
            "trainer": "A. O'Brien",
            "weight_carried": 57.0,
            "odds": 5.5,
            "speed_rating": 81.0,
            "form_rating": 79.0,
            "jockey_skill": 95.0,
            "trainer_skill": 93.0,
            "recent_form": [3, 2, 1, 4, 2],
            "win_probability": 0.18,
        },
        {
            "name": "Lightning Bolt",
            "jockey": "F. Dettori",
            "trainer": "J. Gosden",
            "weight_carried": 60.0,
            "odds": 6.0,
            "speed_rating": 80.0,
            "form_rating": 83.0,
            "jockey_skill": 90.0,
            "trainer_skill": 88.0,
            "recent_form": [4, 1, 2, 3, 1],
            "win_probability": 0.16,
        },
        {
            "name": "Midnight Express",
            "jockey": "P. Hanagan",
            "trainer": "R. Hannon",
            "weight_carried": 56.5,
            "odds": 8.0,
            "speed_rating": 78.0,
            "form_rating": 76.0,
            "jockey_skill": 82.0,
            "trainer_skill": 80.0,
            "recent_form": [5, 3, 4, 2, 3],
            "win_probability": 0.12,
        },
        {
            "name": "Golden Arrow",
            "jockey": "T. Marquand",
            "trainer": "W. Haggas",
            "weight_carried": 58.0,
            "odds": 12.0,
            "speed_rating": 75.0,
            "form_rating": 74.0,
            "jockey_skill": 85.0,
            "trainer_skill": 82.0,
            "recent_form": [6, 4, 5, 3, 4],
            "win_probability": 0.07,
        },
    ]


async def demo_basic_simulation():
    """Demonstrate basic Monte Carlo simulation."""
    print("\n🎯 BASIC MONTE CARLO SIMULATION")
    print("=" * 50)

    horses = create_sample_race_data()
    start_time = time.time()

    # Run basic simulation
    results = await monte_carlo_integration.run_simulation(
        horses=horses, mode="basic", custom_params={"num_runs": 2000}
    )

    execution_time = (time.time() - start_time) * 1000

    print(f"⏱️  Execution Time: {execution_time:.0f}ms")
    print(f"🔄 Simulations Run: {results['simulations_run']}")
    print(f"📊 Reliability: {results['reliability']:.1%}")
    print()

    print("🏆 TOP PICKS:")
    for pick in results["top_picks"][:3]:
        print(
            f"   {pick['rank']}. {pick['horse_name']:<15} "
            f"{pick['win_probability']:.1%} ({pick['confidence']})"
        )

    print()
    print("📈 WIN PROBABILITIES:")
    for horse_name, prob in sorted(
        results["win_probabilities"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {horse_name:<15} {prob:.1%}")


async def demo_advanced_simulation():
    """Demonstrate advanced Monte Carlo simulation."""
    print("\n🎯 ADVANCED MONTE CARLO SIMULATION")
    print("=" * 50)

    horses = create_sample_race_data()
    start_time = time.time()

    # Advanced simulation with environmental factors
    custom_params = {
        "num_runs": 15000,
        "track_condition": "soft",
        "weather_factor": 1.05,  # Slight headwind
        "race_distance": 1400,
        "variance_factor": 0.06,
        "enable_environmental_modeling": True,
    }

    results = await monte_carlo_integration.run_simulation(
        horses=horses, mode="advanced", custom_params=custom_params
    )

    execution_time = (time.time() - start_time) * 1000

    print(f"⏱️  Execution Time: {execution_time:.0f}ms")
    print(f"🔄 Simulations Run: {results['simulations_run']}")
    print(f"📊 Reliability: {results['reliability']:.1%}")
    print(f"🌧️  Track Condition: {custom_params['track_condition'].title()}")
    print(f"💨 Weather Factor: {custom_params['weather_factor']}")
    print()

    print("🏆 ADVANCED ANALYSIS:")
    for pick in results["top_picks"][:3]:
        print(
            f"   {pick['rank']}. {pick['horse_name']:<15} "
            f"{pick['win_probability']:.1%} ({pick['confidence']})"
        )

    print()
    print("💰 VALUE BETS:")
    if results.get("value_bets"):
        for bet in results["value_bets"][:3]:
            print(
                f"   {bet['horse_name']:<15} "
                f"Edge: {bet['edge']:.1%} "
                f"Odds: {bet['odds']:.1f} "
                f"({bet['confidence']})"
            )
    else:
        print("   No value bets identified")

    print()
    print("📊 RACE ANALYSIS:")
    risk = results.get("risk_assessment", {})
    print(f"   Competitiveness: {risk.get('competitiveness', 'unknown').title()}")
    print(f"   Predictability: {risk.get('predictability', 'unknown').title()}")
    print(f"   Strategy: {risk.get('betting_strategy', 'unknown').title()}")

    if results.get("confidence_intervals"):
        print()
        print("📈 CONFIDENCE INTERVALS (95%):")
        for horse_name, (lower, upper) in list(results["confidence_intervals"].items())[
            :3
        ]:
            print(f"   {horse_name:<15} [{lower:.1f} - {upper:.1f}]")


async def demo_scenario_comparison():
    """Demonstrate scenario comparison analysis."""
    print("\n🎯 SCENARIO COMPARISON ANALYSIS")
    print("=" * 50)

    horses = create_sample_race_data()

    # Define different scenarios
    scenarios = [
        {
            "name": "good_conditions",
            "mode": "advanced",
            "parameters": {
                "num_runs": 10000,
                "track_condition": "good",
                "weather_factor": 1.0,
                "race_distance": 1600,
            },
        },
        {
            "name": "soft_track",
            "mode": "advanced",
            "parameters": {
                "num_runs": 10000,
                "track_condition": "soft",
                "weather_factor": 1.0,
                "race_distance": 1600,
            },
        },
        {
            "name": "heavy_conditions",
            "mode": "advanced",
            "parameters": {
                "num_runs": 10000,
                "track_condition": "heavy",
                "weather_factor": 1.08,  # Strong headwind
                "race_distance": 1600,
            },
        },
    ]

    start_time = time.time()
    results = await monte_carlo_integration.run_comparative_analysis(horses, scenarios)
    execution_time = (time.time() - start_time) * 1000

    print(f"⏱️  Total Execution Time: {execution_time:.0f}ms")
    print()

    # Show results for each scenario
    for scenario_name in ["good_conditions", "soft_track", "heavy_conditions"]:
        if scenario_name in results:
            scenario_result = results[scenario_name]
            print(f"📊 {scenario_name.upper().replace('_', ' ')}:")

            # Show top 3 horses for this scenario
            top_horses = sorted(
                scenario_result["win_probabilities"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]

            for i, (horse_name, prob) in enumerate(top_horses, 1):
                print(f"   {i}. {horse_name:<15} {prob:.1%}")
            print()

    # Show comparative analysis
    if "comparative_analysis" in results:
        comp_analysis = results["comparative_analysis"]
        print("🔄 BIGGEST PROBABILITY CHANGES:")
        for change in comp_analysis["biggest_probability_changes"][:3]:
            print(f"   {change['horse']:<15} ±{change['change']:.1%}")


def show_simulation_modes():
    """Show available simulation modes."""
    print("\n🎯 AVAILABLE SIMULATION MODES")
    print("=" * 50)

    modes = monte_carlo_integration.get_simulation_modes()

    for mode in modes:
        print(f"\n📊 {mode['name'].upper()}")
        print(f"   Mode: {mode['mode']}")
        print(f"   Description: {mode['description']}")
        print(f"   Max Runs: {mode['max_runs']:,}")
        print(f"   Runtime: {mode['typical_runtime']}")
        print("   Features:")
        for feature in mode["features"]:
            print(f"     • {feature}")


async def main():
    """Run the complete Monte Carlo demonstration."""
    print("🎯 ENHANCED MONTE CARLO SIMULATION DEMO")
    print("=" * 60)
    print("Integrating horse-bot's advanced Monte Carlo engine with v2.03")
    print()

    # Show available modes
    show_simulation_modes()

    # Demo basic simulation
    await demo_basic_simulation()

    # Demo advanced simulation
    await demo_advanced_simulation()

    # Demo scenario comparison
    await demo_scenario_comparison()

    print("\n✅ DEMONSTRATION COMPLETE")
    print("=" * 50)
    print("The enhanced Monte Carlo system provides:")
    print("• Basic mode: Fast probability analysis (< 1 second)")
    print("• Advanced mode: Professional environmental modeling (2-10 seconds)")
    print("• Scenario comparison: Multi-condition analysis")
    print("• Value betting: Edge identification and recommendations")
    print("• Risk assessment: Competitiveness and predictability analysis")
    print("• Statistical rigor: Confidence intervals and reliability scoring")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("   Check that all required modules are installed and accessible")
