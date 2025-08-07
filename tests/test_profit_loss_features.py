#!/usr/bin/env python3
"""
Test script to generate sample betting data for profit/loss tracking and race records.
This will populate the EnhancedPerformanceTracker with realistic data.
"""

import datetime
import os
import random
import sqlite3
import sys
from decimal import Decimal

import numpy as np

sys.path.append(".")
sys.path.append("src")

try:
    from src.horse_racing_ai.performance.enhanced_tracker import (
        AIRewardMetrics,
        BettingResult,
        EnhancedPerformanceTracker,
        RaceRecord,
    )

    print("✅ Successfully imported enhanced performance tracker")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def generate_sample_betting_data():
    """Generate realistic sample betting data for testing."""

    tracker = EnhancedPerformanceTracker()
    print("🔄 Generating sample betting data...")

    # Generate 50 race records with various outcomes
    methods = ["raw_ratings", "monte_carlo", "ai_ml", "consensus"]
    tracks = ["Belmont", "Churchill", "Santa Anita", "Gulfstream", "Keeneland"]
    surfaces = ["dirt", "turf", "synthetic"]
    bet_types = ["win", "place", "show"]

    for i in range(50):
        # Generate realistic race data
        race_id = f"R{i+1:03d}_{random.choice(tracks)}"
        race_date = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(1, 90)
        )
        track = random.choice(tracks)
        method = random.choice(methods)

        # Generate horse performance features
        features = {
            "speed_rating": random.uniform(85, 105),
            "class_rating": random.uniform(70, 100),
            "jockey_win_rate": random.uniform(0.1, 0.3),
            "trainer_win_rate": random.uniform(0.15, 0.35),
            "distance_performance": random.uniform(0.8, 1.2),
            "track_condition_rating": random.uniform(0.9, 1.1),
            "recent_form": random.uniform(0.7, 1.3),
            "weight_carried": random.uniform(115, 135),
            "post_position": random.randint(1, 12),
            "odds": random.uniform(2.0, 15.0),
        }

        # Generate prediction scores
        confidence = random.uniform(0.6, 0.95)
        predicted_probability = confidence * random.uniform(0.8, 1.2)

        # Simulate betting outcome (higher confidence = higher win probability)
        win_probability = confidence * 0.4  # Max 38% win rate for high confidence
        place_probability = confidence * 0.6  # Max 57% place rate

        bet_type = random.choice(bet_types)
        if random.random() < win_probability:
            actual_result = "win"
            payout = features["odds"] * 2.0  # Win payout
        elif random.random() < place_probability and bet_type in ["place", "show"]:
            actual_result = "place"
            payout = features["odds"] * 0.8  # Place payout
        else:
            actual_result = "loss"
            payout = 0.0

        # Standard bet size
        bet_amount = 20.0
        profit_loss = payout - bet_amount
        roi_percentage = (profit_loss / bet_amount) * 100 if bet_amount > 0 else 0

        # Create betting result
        betting_result = BettingResult(
            horse_name=f"Horse_{i+1}",
            race_id=race_id,
            race_date=race_date,
            bet_type=bet_type,
            bet_amount=bet_amount,
            odds=features["odds"],
            predicted_probability=predicted_probability,
            confidence_score=confidence,
            actual_result=actual_result,
            payout=payout,
            profit_loss=profit_loss,
            roi_percentage=roi_percentage,
            prediction_method=method,
        )

        # Create simplified horse data for race record
        horses = [
            {
                "name": f"Horse_{i+1}",
                "post_position": features["post_position"],
                "odds": features["odds"],
                "weight": features["weight_carried"],
                "jockey": f"Jockey_{random.randint(1, 20)}",
                "trainer": f"Trainer_{random.randint(1, 15)}",
            }
        ]

        # Create prediction data
        predictions = [
            {
                "horse": f"Horse_{i+1}",
                "score": confidence,
                "probability": predicted_probability,
                "confidence": confidence,
            }
        ]

        # Create race record
        race_record = RaceRecord(
            race_id=race_id,
            race_date=race_date,
            track=track,
            distance=random.choice([1000, 1200, 1400, 1600, 1800, 2000]),
            surface=random.choice(surfaces),
            race_class=f"Class {random.randint(1, 6)}",
            field_size=random.randint(6, 14),
            total_purse=random.uniform(25000, 100000),
            # Race data
            horses=horses,
            raw_ratings_predictions=predictions if method == "raw_ratings" else [],
            monte_carlo_predictions=predictions if method == "monte_carlo" else [],
            ai_ml_predictions=predictions if method == "ai_ml" else [],
            consensus_predictions=predictions,
            # Results
            actual_results=[
                {
                    "horse": f"Horse_{i+1}",
                    "finish_position": (
                        1
                        if actual_result == "win"
                        else (2 if actual_result == "place" else random.randint(3, 8))
                    ),
                    "time": f"{random.randint(60, 90)}.{random.randint(10, 99)}",
                }
            ],
            # Performance metrics
            method_accuracy={method: 1.0 if actual_result in ["win", "place"] else 0.0},
            method_profits={method: profit_loss},
            method_roi={method: roi_percentage},
            # Betting data
            betting_results=[betting_result],
            total_wagered=bet_amount,
            total_returned=payout,
            net_profit=profit_loss,
            race_roi=roi_percentage,
        )

        # Record the data
        tracker.betting_results.append(betting_result)
        tracker.race_records.append(race_record)

        if (i + 1) % 10 == 0:
            print(f"   Generated {i+1}/50 records...")

    print("✅ Sample betting data generation complete!")
    print(f"📊 Total records: {len(tracker.betting_results)}")

    # Display summary
    total_profit = sum(result.profit_loss for result in tracker.betting_results)
    total_wagered = sum(result.bet_amount for result in tracker.betting_results)
    roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0

    win_count = sum(
        1 for result in tracker.betting_results if result.actual_result == "win"
    )
    place_count = sum(
        1
        for result in tracker.betting_results
        if result.actual_result in ["win", "place"]
    )
    win_rate = (win_count / len(tracker.betting_results)) * 100
    place_rate = (place_count / len(tracker.betting_results)) * 100

    print(f"\n📈 Performance Summary:")
    print(f"   Total Profit/Loss: ${total_profit:.2f}")
    print(f"   Total Wagered: ${total_wagered:.2f}")
    print(f"   ROI: {roi:.2f}%")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Place Rate: {place_rate:.1f}%")

    return tracker


def main():
    """Main execution function."""
    print("🐎 Horse Racing AI - Profit/Loss Testing Suite")
    print("=" * 60)

    # Generate sample data
    tracker = generate_sample_betting_data()

    print("\n🎯 Testing profit/loss analysis...")
    analysis = tracker.get_performance_summary()

    print("✅ Analysis complete:")
    print(f"   AI metrics calculated: {hasattr(analysis, 'ai_metrics')}")
    print("   Performance summary generated")

    print("\n📋 Testing race records...")
    records = tracker.export_for_ai_analysis()

    print("✅ Race records complete:")
    print(f"   Total records: {len(tracker.race_records)}")
    print(f"   Betting results: {len(tracker.betting_results)}")
    print(f"   AI export data available: {bool(records)}")

    print("\n🌐 Web interface ready for testing!")
    print("   Navigate to: http://127.0.0.1:5003")
    print("   Click 'Profit/Loss Tracking' to see financial analysis")
    print("   Click 'Complete Race Records' to see AI data for reward algorithm")


if __name__ == "__main__":
    main()
