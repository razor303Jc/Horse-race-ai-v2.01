#!/usr/bin/env python3
"""
Practical Race Trends + ML Application
Demonstrates real-world application of race trends analysis combined with advanced ML predictions.
Shows how trends provide valuable insights even when ML performance is already optimal.
"""

import os
import sys
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings

warnings.filterwarnings("ignore")

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from race_trends_ml_integration import RaceTrendsMLIntegration, EnhancedPrediction

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PracticalRaceTrendsApplication:
    """
    Practical application showing how race trends analysis complements
    advanced ML predictions in real-world horse racing scenarios.
    """

    def __init__(self):
        self.trends_ml_system = RaceTrendsMLIntegration()
        logger.info("🏇 Practical Race Trends Application initialized")

    def demonstrate_practical_applications(self):
        """Demonstrate practical real-world applications"""
        logger.info("🚀 PRACTICAL RACE TRENDS + ML APPLICATIONS")
        logger.info("=" * 60)

        # Scenario 1: High-class handicap with clear patterns
        self._demo_handicap_race_analysis()

        # Scenario 2: Maiden race with form limitations
        self._demo_maiden_race_analysis()

        # Scenario 3: Course specialist analysis
        self._demo_course_specialist_analysis()

        # Scenario 4: Value betting opportunities
        self._demo_value_betting_analysis()

        logger.info("\n🎉 PRACTICAL DEMONSTRATIONS COMPLETE!")

    def _demo_handicap_race_analysis(self):
        """Demonstrate analysis of a competitive handicap race"""
        print("\n" + "=" * 70)
        print("🏆 SCENARIO 1: COMPETITIVE HANDICAP ANALYSIS")
        print("=" * 70)

        # Create realistic handicap race
        handicap_race = {
            "race_name": "Wokingham Stakes (Handicap)",
            "race_type": "handicap",
            "distance": "6f",
            "course": "Royal Ascot",
            "surface": "turf",
            "prize_money": 150000,
            "field_size": 20,
            "class": "Group 3",
        }

        print(f"🏁 Race: {handicap_race['race_name']}")
        print(f"📍 Venue: {handicap_race['course']}")
        print(f"📏 Distance: {handicap_race['distance']}")
        print(f"💰 Prize: £{handicap_race['prize_money']:,}")

        # Generate competitive field with realistic patterns
        historical_data = self._create_handicap_historical_data()

        # Analyze with trends + ML
        race_trends, predictions = self.trends_ml_system.analyze_race_with_trends(
            handicap_race, historical_data
        )

        print(f"\n📈 TRENDS ANALYSIS:")
        print(f"   🎯 Overall Edge Score: {race_trends.overall_edge_score:.1%}")
        print(f"   📊 Patterns Identified: {race_trends.total_patterns_found}")

        if race_trends.age_trends:
            for trend in race_trends.age_trends:
                print(
                    f"   🎂 Age Pattern: {trend.pattern} ({trend.confidence:.0%} confident)"
                )

        print(f"\n🏆 TOP SELECTIONS WITH TRENDS VALIDATION:")
        for i, pred in enumerate(predictions[:4], 1):
            confidence_indicator = (
                "🔥"
                if pred.confidence_rating > 0.7
                else "⚡" if pred.confidence_rating > 0.5 else "💫"
            )
            value_indicator = (
                "💎"
                if pred.betting_value > 0.15
                else "💰" if pred.betting_value > 0.05 else ""
            )

            print(f"\n{i}. {pred.horse_name} {confidence_indicator} {value_indicator}")
            print(
                f"   🎯 Combined Win Probability: {pred.combined_win_probability:.1%}"
            )
            print(f"   🤖 ML Prediction: {pred.ml_win_probability:.1%}")
            print(f"   📈 Trends Score: {pred.trend_score:.1%}")
            print(f"   🏅 Classification: {pred.prediction_tier}")
            print(f"   📊 Confidence: {pred.confidence_rating:.1%}")

            if pred.matching_patterns:
                print(f"   ✅ Pattern Match: {pred.matching_patterns[0]}")

            if pred.betting_value > 0.05:
                print(f"   💰 Betting Value: {pred.betting_value:.1%}")

        # Strategic insights
        print(f"\n🎯 STRATEGIC INSIGHTS:")
        if race_trends.overall_edge_score > 0.2:
            print(
                f"   ✅ Strong patterns identified - good race for trends-based betting"
            )
        else:
            print(f"   ⚠️ Weak patterns - rely more heavily on ML predictions")

        top_pick = predictions[0]
        if top_pick.confidence_rating > 0.7 and top_pick.betting_value > 0.1:
            print(f"   🔥 {top_pick.horse_name} shows strong ML + trends convergence")
        elif top_pick.ml_win_probability > 0.3:
            print(
                f"   🤖 {top_pick.horse_name} strong on ML metrics despite weak trends"
            )

    def _demo_maiden_race_analysis(self):
        """Demonstrate analysis of a maiden race where form is limited"""
        print("\n" + "=" * 70)
        print("🌟 SCENARIO 2: MAIDEN RACE ANALYSIS")
        print("=" * 70)

        maiden_race = {
            "race_name": "Novice Stakes (Maiden)",
            "race_type": "maiden",
            "distance": "1m",
            "course": "Newmarket",
            "surface": "turf",
            "prize_money": 25000,
            "field_size": 12,
        }

        print(f"🏁 Race: {maiden_race['race_name']}")
        print(f"📍 Venue: {maiden_race['course']}")
        print(f"💡 Challenge: Limited form data for inexperienced horses")

        # Generate maiden-specific historical data
        historical_data = self._create_maiden_historical_data()

        race_trends, predictions = self.trends_ml_system.analyze_race_with_trends(
            maiden_race, historical_data
        )

        print(f"\n📈 MAIDEN-SPECIFIC TRENDS:")
        print(f"   🎯 Overall Edge Score: {race_trends.overall_edge_score:.1%}")

        print(f"\n🌟 MAIDEN RACE INSIGHTS:")
        for i, pred in enumerate(predictions[:3], 1):
            print(f"\n{i}. {pred.horse_name}")
            print(f"   🎯 Combined Probability: {pred.combined_win_probability:.1%}")
            print(f"   🤖 ML (Limited Data): {pred.ml_win_probability:.1%}")
            print(f"   📈 Trends Boost: {pred.trend_score:.1%}")

            # In maidens, trends become more important due to limited form
            if pred.trend_score > pred.ml_win_probability:
                print(
                    f"   📊 Trends analysis provides key insights where form is limited"
                )

            if pred.matching_patterns:
                print(f"   ✅ Pattern: {pred.matching_patterns[0]}")

        print(f"\n💡 MAIDEN RACE STRATEGY:")
        print(f"   📈 Trends analysis more valuable when form data is limited")
        print(f"   🎯 Focus on breeding, trainer patterns, and physical attributes")
        print(f"   ⚡ ML predictions less reliable due to limited historical data")

    def _demo_course_specialist_analysis(self):
        """Demonstrate course specialist and track bias analysis"""
        print("\n" + "=" * 70)
        print("🏟️ SCENARIO 3: COURSE SPECIALIST ANALYSIS")
        print("=" * 70)

        specialist_race = {
            "race_name": "Chester Cup (Handicap)",
            "race_type": "handicap",
            "distance": "2m2f",
            "course": "Chester",
            "surface": "turf",
            "prize_money": 75000,
            "field_size": 16,
            "track_characteristics": "Very tight turns, unique track",
        }

        print(f"🏁 Race: {specialist_race['race_name']}")
        print(f"📍 Venue: {specialist_race['course']}")
        print(f"🎯 Special Factor: {specialist_race['track_characteristics']}")

        # Generate course-specific historical data
        historical_data = self._create_course_specialist_data()

        race_trends, predictions = self.trends_ml_system.analyze_race_with_trends(
            specialist_race, historical_data
        )

        print(f"\n🏟️ COURSE-SPECIFIC ANALYSIS:")
        print(f"   📊 Course specialists often have major advantages")
        print(f"   🎯 Track characteristics favor specific running styles")

        # Highlight course specialists
        course_specialists = [
            p for p in predictions if "course" in str(p.matching_patterns).lower()
        ]

        if course_specialists:
            print(f"\n🎯 IDENTIFIED COURSE SPECIALISTS:")
            for i, pred in enumerate(course_specialists[:3], 1):
                print(f"\n{i}. {pred.horse_name} ⭐ COURSE SPECIALIST")
                print(
                    f"   🎯 Combined Probability: {pred.combined_win_probability:.1%}"
                )
                print(f"   🏟️ Course Advantage: Significant")
                print(f"   📈 Trends Score: {pred.trend_score:.1%}")

                if pred.betting_value > 0.1:
                    print(f"   💎 Excellent Value: {pred.betting_value:.1%}")
                elif pred.betting_value > 0.05:
                    print(f"   💰 Good Value: {pred.betting_value:.1%}")

        print(f"\n🎯 COURSE SPECIALIST STRATEGY:")
        print(f"   🏟️ Prioritize horses with course experience")
        print(f"   📈 Track-specific trends often override general form")
        print(f"   💰 Course specialists frequently offer betting value")

    def _demo_value_betting_analysis(self):
        """Demonstrate value betting identification using trends + ML"""
        print("\n" + "=" * 70)
        print("💎 SCENARIO 4: VALUE BETTING ANALYSIS")
        print("=" * 70)

        value_race = {
            "race_name": "Competitive Handicap",
            "race_type": "handicap",
            "distance": "1m4f",
            "course": "York",
            "surface": "turf",
            "market_efficiency": "moderate",
        }

        print(f"🏁 Race: {value_race['race_name']}")
        print(f"💰 Focus: Identifying undervalued horses using ML + trends")

        # Generate value-rich scenario
        historical_data = self._create_value_betting_data()

        race_trends, predictions = self.trends_ml_system.analyze_race_with_trends(
            value_race, historical_data
        )

        # Identify value opportunities
        value_bets = [p for p in predictions if p.betting_value > 0.1]
        moderate_value = [p for p in predictions if 0.05 < p.betting_value <= 0.1]

        print(f"\n💎 HIGH-VALUE OPPORTUNITIES:")
        if value_bets:
            for i, pred in enumerate(value_bets, 1):
                print(f"\n{i}. {pred.horse_name} 💎 HIGH VALUE")
                print(
                    f"   🎯 Combined Win Probability: {pred.combined_win_probability:.1%}"
                )
                print(f"   💰 Betting Value: {pred.betting_value:.1%}")
                print(f"   📊 Confidence: {pred.confidence_rating:.1%}")
                print(f"   🤖 ML Prediction: {pred.ml_win_probability:.1%}")
                print(f"   📈 Trends Support: {pred.trend_score:.1%}")

                if pred.matching_patterns:
                    print(f"   ✅ Key Pattern: {pred.matching_patterns[0]}")

                # Value assessment
                if pred.confidence_rating > 0.7:
                    print(f"   🔥 STRONG RECOMMENDATION: High confidence value bet")
                elif pred.confidence_rating > 0.5:
                    print(f"   ⚡ MODERATE RECOMMENDATION: Good value opportunity")
        else:
            print(f"   ⚠️ No high-value opportunities identified")

        if moderate_value:
            print(f"\n💰 MODERATE VALUE OPPORTUNITIES:")
            for pred in moderate_value[:2]:
                print(
                    f"   • {pred.horse_name}: {pred.betting_value:.1%} value, {pred.confidence_rating:.1%} confidence"
                )

        print(f"\n🎯 VALUE BETTING STRATEGY:")
        print(f"   💎 High Value + High Confidence = Strong recommendation")
        print(f"   📊 Trends validation adds confidence to ML predictions")
        print(f"   ⚡ Consider stakes based on confidence × value product")
        print(f"   🎪 Avoid low-confidence bets regardless of apparent value")

        # Risk management advice
        top_confidence = max(predictions, key=lambda x: x.confidence_rating)
        print(f"\n🛡️ RISK MANAGEMENT:")
        print(
            f"   🔒 Highest Confidence: {top_confidence.horse_name} ({top_confidence.confidence_rating:.1%})"
        )
        print(f"   📊 Use confidence ratings for stake sizing")
        print(f"   ⚠️ Avoid bets below 50% confidence threshold")

    def _create_handicap_historical_data(self) -> List[Dict[str, Any]]:
        """Create historical data showing handicap patterns"""
        races = []
        for i in range(15):
            race = {
                "race_id": f"handicap_{i}",
                "race_name": f"Handicap Race {i}",
                "race_type": "handicap",
                "distance": "6f",
                "course": "Royal Ascot",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=30 + i * 14)).isoformat(),
                "participants": [],
            }

            # Add participants with clear age pattern (4-5 year olds win)
            for j in range(12):
                is_winner = j == 0
                participant = {
                    "horse_name": f"Handicap_Horse_{i}_{j}",
                    "age": (
                        4 if (is_winner and i < 12) else np.random.choice([3, 5, 6, 7])
                    ),
                    "weight": np.random.normal(125, 5),
                    "draw": j + 1,
                    "odds": 3.0 + j,
                    "finish_position": j + 1,
                    "days_since_last_run": 21,
                    "last_run_result": "loss",
                    "course_wins": 1 if (is_winner and i < 8) else 0,
                    "course_runs": 2,
                    "distance_wins": 1 if is_winner else 0,
                    "distance_runs": 3,
                }
                race["participants"].append(participant)
            races.append(race)
        return races

    def _create_maiden_historical_data(self) -> List[Dict[str, Any]]:
        """Create maiden race historical data with different patterns"""
        races = []
        for i in range(12):
            race = {
                "race_id": f"maiden_{i}",
                "race_name": f"Maiden Race {i}",
                "race_type": "maiden",
                "distance": "1m",
                "course": "Newmarket",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=20 + i * 10)).isoformat(),
                "participants": [],
            }

            # Maiden patterns: breeding/trainer more important
            for j in range(10):
                is_winner = j == 0
                participant = {
                    "horse_name": f"Maiden_Horse_{i}_{j}",
                    "age": 3,  # Mostly 3-year-olds in maidens
                    "weight": 126,  # Level weights
                    "draw": j + 1,
                    "odds": 2.5 + j,
                    "finish_position": j + 1,
                    "days_since_last_run": 28,
                    "last_run_result": "loss",  # All non-winners
                    "course_wins": 0,  # No previous wins
                    "course_runs": 1,
                    "distance_wins": 0,
                    "distance_runs": 1,
                    "trainer_quality": "top" if (is_winner and i < 8) else "average",
                    "breeding_index": 90 if is_winner else np.random.randint(60, 85),
                }
                race["participants"].append(participant)
            races.append(race)
        return races

    def _create_course_specialist_data(self) -> List[Dict[str, Any]]:
        """Create data showing course specialist advantages"""
        races = []
        for i in range(10):
            race = {
                "race_id": f"chester_{i}",
                "race_name": f"Chester Race {i}",
                "race_type": "handicap",
                "distance": "2m2f",
                "course": "Chester",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=25 + i * 21)).isoformat(),
                "participants": [],
            }

            # Course specialists win more often
            for j in range(12):
                is_winner = j == 0
                has_course_form = j < 4  # Top 4 have course experience

                participant = {
                    "horse_name": f"Chester_Horse_{i}_{j}",
                    "age": np.random.choice([4, 5, 6]),
                    "weight": np.random.normal(126, 4),
                    "draw": j + 1,
                    "odds": 3.0 + j,
                    "finish_position": j + 1,
                    "days_since_last_run": 28,
                    "last_run_result": "loss",
                    "course_wins": (
                        2
                        if (is_winner and has_course_form)
                        else 1 if has_course_form else 0
                    ),
                    "course_runs": 4 if has_course_form else 0,
                    "distance_wins": 1 if is_winner else 0,
                    "distance_runs": 3,
                }
                race["participants"].append(participant)
            races.append(race)
        return races

    def _create_value_betting_data(self) -> List[Dict[str, Any]]:
        """Create data for value betting scenario"""
        races = []
        for i in range(12):
            race = {
                "race_id": f"value_{i}",
                "race_name": f"Value Race {i}",
                "race_type": "handicap",
                "distance": "1m4f",
                "course": "York",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=18 + i * 12)).isoformat(),
                "participants": [],
            }

            # Create scenario where certain patterns are undervalued
            for j in range(14):
                is_winner = j == 0

                participant = {
                    "horse_name": f"Value_Horse_{i}_{j}",
                    "age": np.random.choice([4, 5, 6, 7]),
                    "weight": np.random.normal(127, 6),
                    "draw": j + 1,
                    "odds": 4.0 + j,  # Market prices
                    "finish_position": j + 1,
                    "days_since_last_run": np.random.choice([14, 21, 28]),
                    "last_run_result": "loss",
                    "course_wins": 1 if (is_winner and i < 7) else 0,
                    "course_runs": 2,
                    "distance_wins": 1 if is_winner else 0,
                    "distance_runs": 3,
                    "recent_form_trend": "improving" if is_winner else "stable",
                }
                race["participants"].append(participant)
            races.append(race)
        return races


def main():
    """Run practical race trends applications demonstration"""
    app = PracticalRaceTrendsApplication()
    app.demonstrate_practical_applications()


if __name__ == "__main__":
    main()
