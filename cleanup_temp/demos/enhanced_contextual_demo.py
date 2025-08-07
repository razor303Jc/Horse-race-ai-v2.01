#!/usr/bin/env python3
"""
Enhanced Contextual AI Reward System - Standalone Demo
=====================================================

This demonstrates the comprehensive contextual data framework for AI learning
with simulated data to show the rich contextual factors available to the
reward algorithm for optimal betting strategy development.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class EnhancedContextualRewardDemo:
    """Demonstrate comprehensive contextual data for AI reward system"""

    def __init__(self):
        self.contextual_factors = [
            "day_of_week",
            "week_of_year",
            "month",
            "season",
            "is_weekend",
            "is_holiday",
            "time_of_day",
            "race_number_on_card",
            "total_races_on_card",
            "field_size",
            "competitive_rating",
            "market_volatility",
            "weather_impact_score",
            "track_bias_factor",
            "trainer_recent_form",
            "jockey_recent_form",
            "stable_confidence",
            "media_attention_score",
            "betting_patterns_unusual",
            "pace_scenario",
            "class_drop_raise",
            "distance_change_impact",
            "weight_change_impact",
            "equipment_change",
            "first_time_headgear",
            "connections_booking_significance",
            "stable_money_confidence",
            "market_support_early",
            "market_support_late",
            "steam_moves_detected",
            "drift_detected",
            "liquidity_quality_score",
        ]

    def generate_sample_contextual_data(self, num_predictions: int = 100) -> List[Dict]:
        """Generate sample AI predictions with comprehensive contextual data"""
        predictions = []

        logger.info(
            f"Generating {num_predictions} sample AI predictions with contextual data..."
        )

        for i in range(num_predictions):
            # Generate random race date/time
            base_date = datetime(2024, 1, 1)
            race_datetime = base_date + timedelta(days=random.randint(0, 365))

            # Basic AI prediction data
            prediction = {
                "prediction_id": i + 1,
                "race_id": random.randint(1, 1000),
                "participant_id": random.randint(1, 10000),
                "predicted_probability": round(random.uniform(0.05, 0.85), 4),
                "confidence_score": round(random.uniform(0.5, 0.95), 2),
                "value_rating": round(random.uniform(-5, 25), 1),
                "form_score": round(random.uniform(0.3, 0.9), 3),
                "pace_rating": round(random.uniform(0.4, 0.95), 3),
                "class_rating": round(random.uniform(0.5, 1.0), 3),
                "actual_result": random.choice([0, 0, 0, 0, 1]),  # 20% win rate
            }

            # Enhanced contextual factors
            contextual_data = self._generate_comprehensive_context(race_datetime)
            prediction.update(contextual_data)

            predictions.append(prediction)

        return predictions

    def _generate_comprehensive_context(self, race_datetime: datetime) -> Dict:
        """Generate comprehensive contextual factors for a race"""

        # Temporal factors
        day_of_week = race_datetime.weekday()
        week_of_year = race_datetime.isocalendar()[1]
        month = race_datetime.month

        # Season mapping
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"

        is_weekend = 1 if day_of_week >= 5 else 0
        is_holiday = random.choice([0, 0, 0, 0, 1])  # 20% chance

        # Time of day
        hour = race_datetime.hour
        if hour < 12:
            time_of_day = "Morning"
        elif hour < 17:
            time_of_day = "Afternoon"
        else:
            time_of_day = "Evening"

        # Race context
        field_size = random.randint(5, 20)
        race_number = random.randint(1, 8)
        total_races = random.randint(6, 12)

        # Field and competition dynamics
        competitive_rating = self._calculate_competitive_rating(field_size)

        # Market conditions
        market_volatility = random.uniform(0.1, 0.9)
        liquidity_quality_score = random.uniform(0.3, 1.0)

        # Weather and track conditions
        weather_impact_score = random.uniform(0.0, 0.8)
        track_bias_factor = random.uniform(-0.3, 0.3)

        # Media and attention factors
        media_attention_score = random.uniform(0.1, 0.7)
        if is_weekend or is_holiday:
            media_attention_score *= 1.3

        # Market patterns
        betting_patterns_unusual = random.choice([0, 0, 0, 1])
        steam_moves_detected = random.choice([0, 0, 0, 1])
        drift_detected = random.choice([0, 0, 0, 1])

        # Support patterns
        market_support_early = random.uniform(0.2, 0.9)
        market_support_late = random.uniform(0.2, 0.9)

        # Horse-specific contextual factors
        trainer_recent_form = random.uniform(0.3, 0.9)
        jockey_recent_form = random.uniform(0.3, 0.9)
        stable_confidence = random.uniform(0.2, 0.8)
        stable_money_confidence = random.uniform(0.2, 0.8)

        # Equipment and changes
        equipment_change = random.choice([0, 0, 0, 1])
        first_time_headgear = random.choice([0, 0, 0, 0, 1])

        # Pace and class context
        pace_scenarios = ["Strong Pace", "Moderate Pace", "Slow Pace", "Unknown"]
        pace_scenario = random.choice(pace_scenarios)

        class_changes = ["Class Drop", "Class Rise", "Same Class", "Maiden"]
        class_drop_raise = random.choice(class_changes)

        # Performance impact factors
        distance_change_impact = random.uniform(-0.3, 0.3)
        weight_change_impact = random.uniform(-0.2, 0.2)
        connections_booking_significance = random.uniform(0.1, 0.8)

        return {
            "day_of_week": day_of_week,
            "week_of_year": week_of_year,
            "month": month,
            "season": season,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "time_of_day": time_of_day,
            "race_number_on_card": race_number,
            "total_races_on_card": total_races,
            "field_size": field_size,
            "competitive_rating": round(competitive_rating, 3),
            "market_volatility": round(market_volatility, 3),
            "weather_impact_score": round(weather_impact_score, 3),
            "track_bias_factor": round(track_bias_factor, 3),
            "trainer_recent_form": round(trainer_recent_form, 3),
            "jockey_recent_form": round(jockey_recent_form, 3),
            "stable_confidence": round(stable_confidence, 3),
            "media_attention_score": round(media_attention_score, 3),
            "betting_patterns_unusual": betting_patterns_unusual,
            "pace_scenario": pace_scenario,
            "class_drop_raise": class_drop_raise,
            "distance_change_impact": round(distance_change_impact, 3),
            "weight_change_impact": round(weight_change_impact, 3),
            "equipment_change": equipment_change,
            "first_time_headgear": first_time_headgear,
            "connections_booking_significance": round(
                connections_booking_significance, 3
            ),
            "stable_money_confidence": round(stable_money_confidence, 3),
            "market_support_early": round(market_support_early, 3),
            "market_support_late": round(market_support_late, 3),
            "steam_moves_detected": steam_moves_detected,
            "drift_detected": drift_detected,
            "liquidity_quality_score": round(liquidity_quality_score, 3),
        }

    def _calculate_competitive_rating(self, field_size: int) -> float:
        """Calculate competitive rating based on field dynamics"""
        base_rating = min(field_size / 20.0, 1.0)

        # Add variability based on field size sweet spots
        if 8 <= field_size <= 12:
            base_rating *= 1.1  # Optimal competitive field
        elif field_size < 6:
            base_rating *= 0.7  # Too small, less competitive
        elif field_size > 20:
            base_rating *= 0.8  # Too large, harder to assess

        return min(base_rating * random.uniform(0.8, 1.2), 1.0)

    def analyze_contextual_performance(self, predictions: List[Dict]) -> Dict:
        """Analyze AI performance by contextual factors"""
        analysis = {}

        # Day of week analysis
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        day_analysis = {}
        for day_num in range(7):
            day_predictions = [p for p in predictions if p["day_of_week"] == day_num]
            if day_predictions:
                win_rate = sum(p["actual_result"] for p in day_predictions) / len(
                    day_predictions
                )
                avg_confidence = sum(
                    p["confidence_score"] for p in day_predictions
                ) / len(day_predictions)

                day_analysis[day_names[day_num]] = {
                    "predictions": len(day_predictions),
                    "win_rate": round(win_rate * 100, 1),
                    "avg_confidence": round(avg_confidence, 2),
                }

        analysis["day_performance"] = day_analysis

        # Weekend vs weekday
        weekend_predictions = [p for p in predictions if p["is_weekend"] == 1]
        weekday_predictions = [p for p in predictions if p["is_weekend"] == 0]

        analysis["weekend_vs_weekday"] = {
            "weekend": {
                "predictions": len(weekend_predictions),
                "win_rate": round(
                    sum(p["actual_result"] for p in weekend_predictions)
                    / max(len(weekend_predictions), 1)
                    * 100,
                    1,
                ),
                "avg_market_volatility": round(
                    sum(p["market_volatility"] for p in weekend_predictions)
                    / max(len(weekend_predictions), 1),
                    3,
                ),
            },
            "weekday": {
                "predictions": len(weekday_predictions),
                "win_rate": round(
                    sum(p["actual_result"] for p in weekday_predictions)
                    / max(len(weekday_predictions), 1)
                    * 100,
                    1,
                ),
                "avg_market_volatility": round(
                    sum(p["market_volatility"] for p in weekday_predictions)
                    / max(len(weekday_predictions), 1),
                    3,
                ),
            },
        }

        # Field size analysis
        field_ranges = {
            "Small (5-8)": (5, 8),
            "Medium (9-12)": (9, 12),
            "Large (13-16)": (13, 16),
            "Very Large (17+)": (17, 30),
        }

        field_analysis = {}
        for range_name, (min_size, max_size) in field_ranges.items():
            field_predictions = [
                p for p in predictions if min_size <= p["field_size"] <= max_size
            ]
            if field_predictions:
                win_rate = sum(p["actual_result"] for p in field_predictions) / len(
                    field_predictions
                )
                avg_competitive = sum(
                    p["competitive_rating"] for p in field_predictions
                ) / len(field_predictions)

                field_analysis[range_name] = {
                    "predictions": len(field_predictions),
                    "win_rate": round(win_rate * 100, 1),
                    "avg_competitive_rating": round(avg_competitive, 3),
                }

        analysis["field_size_analysis"] = field_analysis

        # Pace scenario analysis
        pace_scenarios = ["Strong Pace", "Moderate Pace", "Slow Pace", "Unknown"]
        pace_analysis = {}

        for scenario in pace_scenarios:
            scenario_predictions = [
                p for p in predictions if p["pace_scenario"] == scenario
            ]
            if scenario_predictions:
                win_rate = sum(p["actual_result"] for p in scenario_predictions) / len(
                    scenario_predictions
                )

                pace_analysis[scenario] = {
                    "predictions": len(scenario_predictions),
                    "win_rate": round(win_rate * 100, 1),
                }

        analysis["pace_scenario_analysis"] = pace_analysis

        # Market volatility analysis
        low_vol = [p for p in predictions if p["market_volatility"] < 0.3]
        med_vol = [p for p in predictions if 0.3 <= p["market_volatility"] < 0.7]
        high_vol = [p for p in predictions if p["market_volatility"] >= 0.7]

        analysis["volatility_analysis"] = {
            "low_volatility": {
                "predictions": len(low_vol),
                "win_rate": round(
                    sum(p["actual_result"] for p in low_vol)
                    / max(len(low_vol), 1)
                    * 100,
                    1,
                ),
            },
            "medium_volatility": {
                "predictions": len(med_vol),
                "win_rate": round(
                    sum(p["actual_result"] for p in med_vol)
                    / max(len(med_vol), 1)
                    * 100,
                    1,
                ),
            },
            "high_volatility": {
                "predictions": len(high_vol),
                "win_rate": round(
                    sum(p["actual_result"] for p in high_vol)
                    / max(len(high_vol), 1)
                    * 100,
                    1,
                ),
            },
        }

        return analysis

    def generate_contextual_rewards(self, analysis: Dict) -> Dict:
        """Generate contextual reward signals based on performance analysis"""

        rewards = {
            "temporal_rewards": {},
            "field_size_rewards": {},
            "market_condition_rewards": {},
            "pace_scenario_rewards": {},
            "contextual_multipliers": {},
        }

        # Temporal rewards
        day_performance = analysis.get("day_performance", {})
        if day_performance:
            best_day = max(
                day_performance.keys(), key=lambda x: day_performance[x]["win_rate"]
            )
            worst_day = min(
                day_performance.keys(), key=lambda x: day_performance[x]["win_rate"]
            )

            rewards["temporal_rewards"] = {
                "best_day": best_day,
                "best_day_multiplier": 1.25,
                "worst_day": worst_day,
                "worst_day_multiplier": 0.85,
            }

        # Weekend bonus
        weekend_data = analysis.get("weekend_vs_weekday", {})
        if weekend_data:
            weekend_rate = weekend_data.get("weekend", {}).get("win_rate", 0)
            weekday_rate = weekend_data.get("weekday", {}).get("win_rate", 0)

            if weekend_rate > weekday_rate:
                rewards["temporal_rewards"]["weekend_bonus"] = 1.15
            else:
                rewards["temporal_rewards"]["weekend_bonus"] = 0.95

        # Field size rewards
        field_analysis = analysis.get("field_size_analysis", {})
        for field_range, stats in field_analysis.items():
            win_rate = stats.get("win_rate", 0)
            if win_rate > 22:  # Above average
                rewards["field_size_rewards"][field_range] = 1.2
            elif win_rate > 18:
                rewards["field_size_rewards"][field_range] = 1.1
            elif win_rate < 15:
                rewards["field_size_rewards"][field_range] = 0.9
            else:
                rewards["field_size_rewards"][field_range] = 1.0

        # Market volatility rewards
        vol_analysis = analysis.get("volatility_analysis", {})
        for condition, stats in vol_analysis.items():
            win_rate = stats.get("win_rate", 0)
            if win_rate > 20:
                rewards["market_condition_rewards"][condition] = 1.15
            elif win_rate < 15:
                rewards["market_condition_rewards"][condition] = 0.9
            else:
                rewards["market_condition_rewards"][condition] = 1.0

        # Pace scenario rewards
        pace_analysis = analysis.get("pace_scenario_analysis", {})
        for scenario, stats in pace_analysis.items():
            win_rate = stats.get("win_rate", 0)
            if win_rate > 20:
                rewards["pace_scenario_rewards"][scenario] = 1.1
            else:
                rewards["pace_scenario_rewards"][scenario] = 1.0

        return rewards

    def print_comprehensive_demo(self):
        """Print comprehensive contextual reward system demonstration"""

        print("\n" + "=" * 85)
        print("🧠 ENHANCED CONTEXTUAL AI REWARD SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 85)

        # Generate sample data
        predictions = self.generate_sample_contextual_data(200)

        print(
            f"\n📊 Generated {len(predictions):,} AI predictions with comprehensive contextual data"
        )
        print(f"\n🔍 Available Contextual Factors ({len(self.contextual_factors)}):")

        # Show contextual factors in groups
        temporal_factors = [
            "day_of_week",
            "week_of_year",
            "month",
            "season",
            "is_weekend",
            "is_holiday",
            "time_of_day",
        ]
        market_factors = [
            "market_volatility",
            "liquidity_quality_score",
            "betting_patterns_unusual",
            "steam_moves_detected",
            "drift_detected",
            "market_support_early",
            "market_support_late",
        ]
        field_factors = [
            "field_size",
            "competitive_rating",
            "race_number_on_card",
            "total_races_on_card",
        ]
        environmental_factors = [
            "weather_impact_score",
            "track_bias_factor",
            "media_attention_score",
        ]
        horse_factors = [
            "trainer_recent_form",
            "jockey_recent_form",
            "stable_confidence",
            "stable_money_confidence",
            "pace_scenario",
            "class_drop_raise",
            "distance_change_impact",
            "weight_change_impact",
            "equipment_change",
            "first_time_headgear",
            "connections_booking_significance",
        ]

        print(f"\n   🕐 Temporal Factors ({len(temporal_factors)}):")
        for factor in temporal_factors:
            print(f"      • {factor}")

        print(f"\n   📈 Market Factors ({len(market_factors)}):")
        for factor in market_factors:
            print(f"      • {factor}")

        print(f"\n   🏇 Field Dynamics ({len(field_factors)}):")
        for factor in field_factors:
            print(f"      • {factor}")

        print(f"\n   🌦️  Environmental Factors ({len(environmental_factors)}):")
        for factor in environmental_factors:
            print(f"      • {factor}")

        print(f"\n   🐎 Horse-Specific Factors ({len(horse_factors)}):")
        for factor in horse_factors:
            print(f"      • {factor}")

        # Analyze performance
        analysis = self.analyze_contextual_performance(predictions)

        print(f"\n📅 Performance by Day of Week:")
        for day, stats in analysis["day_performance"].items():
            print(
                f"   • {day:>9}: {stats['predictions']:>3} predictions, {stats['win_rate']:>5.1f}% win rate, confidence {stats['avg_confidence']:.2f}"
            )

        print(f"\n🎯 Weekend vs Weekday Analysis:")
        weekend_stats = analysis["weekend_vs_weekday"]
        print(
            f"   • Weekend: {weekend_stats['weekend']['win_rate']:>5.1f}% win rate ({weekend_stats['weekend']['predictions']} predictions)"
        )
        print(
            f"   • Weekday: {weekend_stats['weekday']['win_rate']:>5.1f}% win rate ({weekend_stats['weekday']['predictions']} predictions)"
        )

        print(f"\n🏇 Field Size Impact:")
        for field_range, stats in analysis["field_size_analysis"].items():
            print(
                f"   • {field_range:>15}: {stats['win_rate']:>5.1f}% win rate, competitive rating {stats['avg_competitive_rating']:.3f}"
            )

        print(f"\n⚡ Pace Scenario Analysis:")
        for scenario, stats in analysis["pace_scenario_analysis"].items():
            print(
                f"   • {scenario:>13}: {stats['win_rate']:>5.1f}% win rate ({stats['predictions']} predictions)"
            )

        print(f"\n📊 Market Volatility Impact:")
        for condition, stats in analysis["volatility_analysis"].items():
            print(
                f"   • {condition.replace('_', ' ').title():>18}: {stats['win_rate']:>5.1f}% win rate ({stats['predictions']} predictions)"
            )

        # Generate contextual rewards
        rewards = self.generate_contextual_rewards(analysis)

        print(f"\n🏆 CONTEXTUAL REWARD SIGNALS:")

        print(f"\n   📅 Temporal Rewards:")
        temporal = rewards["temporal_rewards"]
        if "best_day" in temporal:
            print(
                f"      • Best Day ({temporal['best_day']}): {temporal['best_day_multiplier']:.2f}x multiplier"
            )
            print(
                f"      • Worst Day ({temporal['worst_day']}): {temporal['worst_day_multiplier']:.2f}x multiplier"
            )
        if "weekend_bonus" in temporal:
            print(f"      • Weekend Bonus: {temporal['weekend_bonus']:.2f}x multiplier")

        print(f"\n   🏇 Field Size Rewards:")
        for field_range, multiplier in rewards["field_size_rewards"].items():
            print(f"      • {field_range}: {multiplier:.2f}x multiplier")

        print(f"\n   📈 Market Condition Rewards:")
        for condition, multiplier in rewards["market_condition_rewards"].items():
            print(
                f"      • {condition.replace('_', ' ').title()}: {multiplier:.2f}x multiplier"
            )

        print(f"\n   ⚡ Pace Scenario Rewards:")
        for scenario, multiplier in rewards["pace_scenario_rewards"].items():
            print(f"      • {scenario}: {multiplier:.2f}x multiplier")

        print(f"\n" + "=" * 85)
        print("🚀 CONTEXTUAL DATA PROVIDES RICH LEARNING SIGNALS!")
        print("=" * 85)

        print(f"\n💡 Key Benefits of Enhanced Contextual Data:")
        print(f"   • 🕐 Temporal patterns: Optimal betting times and seasonal effects")
        print(f"   • 📈 Market dynamics: Volatility-aware strategy selection")
        print(f"   • 🏇 Field composition: Competition-level adjusted confidence")
        print(f"   • 🌦️  Environmental factors: Weather and track bias integration")
        print(f"   • 🐎 Horse-specific context: Form, equipment, class movements")
        print(f"   • 🎯 Connections analysis: Trainer/jockey confidence patterns")
        print(f"   • 💰 Market patterns: Steam moves, drifts, support levels")

        print(f"\n🎯 The reward algorithm can now learn sophisticated strategies that:")
        print(f"   • Adapt to different racing conditions and environments")
        print(f"   • Recognize optimal betting opportunities by context")
        print(f"   • Adjust confidence and stake sizing based on data quality")
        print(f"   • Identify value in specific market conditions")
        print(f"   • Account for temporal and seasonal betting patterns")

        print(f"\n🧠 This rich contextual framework enables the AI to develop")
        print(f"   nuanced betting strategies that go far beyond basic form analysis!")


def main():
    """Run the enhanced contextual AI reward system demo"""
    demo = EnhancedContextualRewardDemo()
    demo.print_comprehensive_demo()


if __name__ == "__main__":
    main()
