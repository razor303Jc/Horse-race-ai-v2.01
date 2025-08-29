#!/usr/bin/env python3
"""
Backtest Results Analyzer and Visualizer
========================================

Analyzes the detailed backtest results and provides additional insights
and visualizations of strategy performance.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np


def load_backtest_results(filename: str) -> dict:
    """Load backtest results from JSON file"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Results file {filename} not found")
        return None


def analyze_bet_patterns(results: dict):
    """Analyze betting patterns and performance"""
    print("🔍 DETAILED BET PATTERN ANALYSIS")
    print("=" * 60)

    # 80/20 Strategy Analysis
    eighty_twenty_bets = results["eighty_twenty"]["bets"]
    if eighty_twenty_bets:
        print("\n💰 80/20 STRATEGY DETAILED ANALYSIS:")

        # Calculate statistics
        profits = [bet["net_profit"] for bet in eighty_twenty_bets]
        rois = [bet["roi"] for bet in eighty_twenty_bets]
        odds = [bet["win_odds"] for bet in eighty_twenty_bets]
        places = [bet["actual_place"] for bet in eighty_twenty_bets]

        print(f"  Average Profit per Bet: £{np.mean(profits):.2f}")
        print(f"  Median Profit per Bet: £{np.median(profits):.2f}")
        print(f"  Best Single Bet: £{max(profits):.2f}")
        print(f"  Worst Single Bet: £{min(profits):.2f}")
        print(f"  Standard Deviation: £{np.std(profits):.2f}")
        print("")

        # Win/Place analysis
        wins = sum(1 for place in places if place == 1)
        places_2_3 = sum(1 for place in places if 2 <= place <= 3)
        unplaced = sum(1 for place in places if place > 3)

        print(f"  Wins: {wins} ({wins/len(places)*100:.1f}%)")
        print(f"  Places (2nd-3rd): {places_2_3} ({places_2_3/len(places)*100:.1f}%)")
        print(f"  Unplaced: {unplaced} ({unplaced/len(places)*100:.1f}%)")
        print("")

        # Odds analysis
        short_odds = sum(1 for odd in odds if odd <= 2.0)
        medium_odds = sum(1 for odd in odds if 2.0 < odd <= 4.0)
        long_odds = sum(1 for odd in odds if odd > 4.0)

        print(f"  Short Odds (≤2.0): {short_odds} bets")
        print(f"  Medium Odds (2.0-4.0): {medium_odds} bets")
        print(f"  Long Odds (>4.0): {long_odds} bets")

    # Dutching Strategy Analysis
    dutching_bets = results["dutching"]["bets"]
    if dutching_bets:
        print("\n🎯 DUTCHING STRATEGY DETAILED ANALYSIS:")

        profits = [bet["net_profit"] for bet in dutching_bets]
        rois = [bet["roi"] for bet in dutching_bets]
        successful = [bet["successful"] for bet in dutching_bets]

        print(f"  Average Profit per Bet: £{np.mean(profits):.2f}")
        print(f"  Median Profit per Bet: £{np.median(profits):.2f}")
        print(f"  Best Single Bet: £{max(profits):.2f}")
        print(f"  Worst Single Bet: £{min(profits):.2f}")
        print(f"  Standard Deviation: £{np.std(profits):.2f}")
        print("")

        # Success analysis
        success_count = sum(successful)
        print(
            f"  Successful Bets: {success_count}/{len(successful)} ({success_count/len(successful)*100:.1f}%)"
        )

        # Analyze selection counts
        selection_counts = []
        for bet in dutching_bets:
            selection_counts.append(len(bet["selections"]))

        print(f"  Average Selections per Bet: {np.mean(selection_counts):.1f}")
        print(f"  Most Selections in Single Bet: {max(selection_counts)}")


def create_performance_summary():
    """Create a visual performance summary"""
    print("\n📊 STRATEGY COMPARISON SUMMARY")
    print("=" * 60)

    # Load results
    results = load_backtest_results("backtest_results_2025-08-20.json")
    if not results:
        return

    strategies = ["80/20", "Dutching"]
    roi_values = [
        results["eighty_twenty"]["roi_percentage"],
        results["dutching"]["roi_percentage"],
    ]
    success_rates = [
        results["eighty_twenty"]["win_rate"],
        results["dutching"]["success_rate"],
    ]
    total_profits = [
        results["eighty_twenty"]["net_profit"],
        results["dutching"]["net_profit"],
    ]

    # Create simple text-based comparison
    print("Strategy      | ROI    | Success Rate | Net Profit")
    print("-" * 50)
    for i, strategy in enumerate(strategies):
        print(
            f"{strategy:<12} | {roi_values[i]:>5.1f}% | {success_rates[i]:>10.1f}% | £{total_profits[i]:>7.2f}"
        )

    print("\n🎯 KEY INSIGHTS:")
    if roi_values[0] > roi_values[1]:
        print("✅ 80/20 strategy outperformed Dutching in ROI")
    else:
        print("✅ Dutching strategy outperformed 80/20 in ROI")

    if success_rates[1] > success_rates[0]:
        print("✅ Dutching had higher success rate but lower ROI")

    if total_profits[0] > 0:
        print("✅ 80/20 strategy generated positive returns")

    if total_profits[1] < 0:
        print("⚠️ Dutching strategy had net losses")

    print("\n💡 RECOMMENDATIONS:")
    print("• Focus on 80/20 strategy for consistent profits")
    print("• Refine Dutching entry criteria to reduce losses")
    print("• Consider combining strategies based on race characteristics")
    print("• Implement stricter profit margin requirements for Dutching")


def analyze_race_characteristics():
    """Analyze performance by race characteristics"""
    results = load_backtest_results("backtest_results_2025-08-20.json")
    if not results:
        return

    print("\n🏇 RACE CHARACTERISTIC ANALYSIS")
    print("=" * 60)

    # Analyze 80/20 performance by odds ranges
    eighty_twenty_bets = results["eighty_twenty"]["bets"]

    odds_ranges = {
        "Very Short (≤1.5)": [],
        "Short (1.5-2.5)": [],
        "Medium (2.5-4.0)": [],
        "Long (>4.0)": [],
    }

    for bet in eighty_twenty_bets:
        odds = bet["win_odds"]
        if odds <= 1.5:
            odds_ranges["Very Short (≤1.5)"].append(bet)
        elif odds <= 2.5:
            odds_ranges["Short (1.5-2.5)"].append(bet)
        elif odds <= 4.0:
            odds_ranges["Medium (2.5-4.0)"].append(bet)
        else:
            odds_ranges["Long (>4.0)"].append(bet)

    print("80/20 PERFORMANCE BY ODDS RANGE:")
    print("Range              | Bets | Win Rate | Avg ROI")
    print("-" * 50)

    for range_name, bets in odds_ranges.items():
        if bets:
            win_rate = sum(1 for bet in bets if bet["successful"]) / len(bets) * 100
            avg_roi = sum(bet["roi"] for bet in bets) / len(bets)
            print(
                f"{range_name:<17} | {len(bets):>4} | {win_rate:>7.1f}% | {avg_roi:>6.1f}%"
            )

    print("\n💡 ODDS ANALYSIS INSIGHTS:")
    print("• Performance varies significantly by odds range")
    print("• Identify optimal odds range for 80/20 strategy")
    print("• Consider odds-based filters for strategy selection")


def main():
    """Main analysis function"""
    print("🎯 ENHANCED MONTE CARLO BACKTEST ANALYZER")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # Load and analyze results
    results = load_backtest_results("backtest_results_2025-08-20.json")
    if not results:
        print("❌ Could not load backtest results")
        return

    # Perform analyses
    analyze_bet_patterns(results)
    create_performance_summary()
    analyze_race_characteristics()

    print("\n✅ Analysis completed successfully!")
    print("📁 Review the detailed JSON file for complete bet-by-bet results")


if __name__ == "__main__":
    main()
