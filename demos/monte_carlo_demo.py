#!/usr/bin/env python3
"""
Monte Carlo Simulation Demo
Test the new Monte Carlo functionality with sample data.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from enhanced_scoring_demo import (
    create_target_race_conditions,
    generate_sample_race_data,
)
from horse_racing_ai.scoring.composite_scorer import CompositeScorer
from horse_racing_ai.simulation.monte_carlo_simulator import (
    MonteCarloSimulator,
    PerformanceProfile,
)


def test_monte_carlo_simulation():
    """Test Monte Carlo simulation with sample data."""

    print("🎲 Monte Carlo Race Simulation Demo")
    print("=" * 50)

    # Generate sample data
    horses_data = generate_sample_race_data()
    race_conditions = create_target_race_conditions()

    # Run composite scoring
    print("📊 Running composite analysis...")
    composite_scorer = CompositeScorer()

    # Create betting odds for the horses
    betting_odds = {
        "Lightning Bolt": 2.8,
        "Royal Heritage": 6.5,
        "Thunder Strike": 4.2,
    }

    race_analysis = composite_scorer.score_race(
        race_data=race_conditions, horses_data=horses_data, betting_odds=betting_odds
    )

    print(f"✅ Analyzed {len(race_analysis.horse_scores)} horses")

    # Run Monte Carlo simulation
    print("\n🎲 Running Monte Carlo simulation...")
    simulator = MonteCarloSimulator(simulations=10000, random_seed=42)

    # Create performance profiles
    profiles = simulator.create_performance_profiles(race_analysis.horse_scores)

    print(f"📈 Created {len(profiles)} performance profiles:")
    for profile in profiles:
        print(f"   🐎 {profile.horse_name}:")
        print(f"      Mean Rating: {profile.mean_rating:.2f}")
        print(f"      Std Deviation: {profile.std_deviation:.2f}")
        print(f"      Z-Score: {profile.z_score:+.2f}")
        print(f"      Consistency: {profile.consistency_factor:.2%}")
        print(f"      Form Trend: {profile.form_trend:+.2f}")
        range_min, range_max = profile.performance_range
        print(f"      Range: {range_min:.1f} - {range_max:.1f}")
        print()

    # Run simulation
    mc_analysis = simulator.run_monte_carlo_simulation(profiles, "DEMO_RACE")

    # Display results
    print(f"🎯 Monte Carlo Results ({mc_analysis.simulations_run:,} simulations)")
    print(f"📊 Simulation Reliability: {mc_analysis.simulation_reliability:.1%}")
    print()

    print("🏆 Win Probabilities:")
    win_probs = mc_analysis.win_probabilities.items()
    for horse_name, prob in sorted(win_probs, key=lambda x: x[1], reverse=True):
        print(f"   {horse_name}: {prob:.1%}")

    print("\n🥉 Place Probabilities (Top 3):")
    place_probs = mc_analysis.place_probabilities.items()
    for horse_name, prob in sorted(place_probs, key=lambda x: x[1], reverse=True):
        print(f"   {horse_name}: {prob:.1%}")

    print("\n📍 Average Finishing Positions:")
    avg_positions = mc_analysis.average_positions.items()
    for horse_name, avg_pos in sorted(avg_positions, key=lambda x: x[1]):
        print(f"   {horse_name}: {avg_pos:.2f}")

    print("\n📊 Performance Confidence Intervals (95%):")
    for horse_name, (lower, upper) in mc_analysis.confidence_intervals.items():
        print(f"   {horse_name}: {lower:.1f} - {upper:.1f}")

    # Get betting recommendations
    min_prob = 0.1
    recommendations = simulator.get_betting_recommendations(
        mc_analysis, min_probability=min_prob
    )

    print("\n💰 Betting Recommendations:")
    if recommendations:
        for i, rec in enumerate(recommendations[:3]):  # Top 3 recommendations
            print(f"   {i+1}. {rec['horse_name']}")
            print(f"      Win Probability: {rec['probability']:.1%}")
            print(f"      Fair Odds: {rec['fair_odds']:.1f}")
            print(f"      Z-Score: {rec['z_score']:+.2f}")
            print(f"      Confidence: {rec['confidence']:.1%}")
            print()
    else:
        print("   No strong betting opportunities identified")

    print("✅ Monte Carlo simulation completed successfully!")
    print("🎲 The simulation provides statistical probabilities based on")
    print("   performance analysis, z-scores, and historical variance.")


if __name__ == "__main__":
    test_monte_carlo_simulation()
