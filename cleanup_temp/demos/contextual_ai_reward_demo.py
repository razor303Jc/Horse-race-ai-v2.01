#!/usr/bin/env python3
"""
Enhanced AI Reward System with Comprehensive Contextual Data
==========================================================

This script demonstrates the enhanced AI learning system with comprehensive
contextual data for optimal betting strategy development.

Key Features:
- Rich contextual data including temporal, environmental, and market factors
- Horse-specific contextual variables for detailed analysis
- Integration with reward algorithm for optimal AI learning
- Comprehensive dataset for sophisticated ML training

Contextual Data Categories:
1. Temporal: Day of week, time of day, season, holidays
2. Market: Volatility, liquidity, betting patterns, support levels
3. Environmental: Weather impact, track bias, field dynamics
4. Horse-specific: Recent form, equipment changes, class movements
5. Connections: Trainer/jockey confidence, stable patterns
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextualAIRewardAnalyzer:
    """Analyze AI performance with comprehensive contextual data"""

    def __init__(self, database_path: str = "massive_horse_racing.db"):
        self.db_path = database_path
        self.conn = None

    def connect_database(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def analyze_contextual_factors(self) -> Dict:
        """Analyze AI performance by contextual factors"""
        if not self.conn:
            return {}

        cursor = self.conn.cursor()

        # Get AI predictions with contextual data
        cursor.execute(
            """
            SELECT 
                day_of_week, is_weekend, season, time_of_day,
                field_size, competitive_rating, market_volatility,
                weather_impact_score, track_bias_factor,
                pace_scenario, class_drop_raise,
                predicted_probability, actual_result,
                confidence_score, value_rating
            FROM ai_predictions 
            WHERE predicted_probability IS NOT NULL
            LIMIT 1000
        """
        )

        data = cursor.fetchall()
        if not data:
            logger.warning("No AI prediction data found")
            return {}

        columns = [
            "day_of_week",
            "is_weekend",
            "season",
            "time_of_day",
            "field_size",
            "competitive_rating",
            "market_volatility",
            "weather_impact_score",
            "track_bias_factor",
            "pace_scenario",
            "class_drop_raise",
            "predicted_probability",
            "actual_result",
            "confidence_score",
            "value_rating",
        ]

        df = pd.DataFrame(data, columns=columns)

        analysis = {
            "total_predictions": len(df),
            "win_rate_by_day": self._analyze_day_performance(df),
            "weekend_vs_weekday": self._analyze_weekend_performance(df),
            "seasonal_performance": self._analyze_seasonal_performance(df),
            "field_size_impact": self._analyze_field_size_impact(df),
            "market_conditions": self._analyze_market_conditions(df),
            "pace_scenario_analysis": self._analyze_pace_scenarios(df),
            "class_movement_impact": self._analyze_class_movements(df),
            "confidence_reliability": self._analyze_confidence_reliability(df),
        }

        return analysis

    def _analyze_day_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by day of week"""
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        day_stats = {}
        for day in range(7):
            day_data = df[df["day_of_week"] == day]
            if len(day_data) > 0:
                win_rate = day_data["actual_result"].mean()
                avg_confidence = day_data["confidence_score"].mean()
                avg_value = day_data["value_rating"].mean()

                day_stats[day_names[day]] = {
                    "predictions": len(day_data),
                    "win_rate": round(win_rate * 100, 1),
                    "avg_confidence": round(avg_confidence, 2),
                    "avg_value_rating": round(avg_value, 1),
                }

        return day_stats

    def _analyze_weekend_performance(self, df: pd.DataFrame) -> Dict:
        """Compare weekend vs weekday performance"""
        weekend_data = df[df["is_weekend"] == 1]
        weekday_data = df[df["is_weekend"] == 0]

        return {
            "weekend": {
                "predictions": len(weekend_data),
                "win_rate": round(weekend_data["actual_result"].mean() * 100, 1),
                "avg_confidence": round(weekend_data["confidence_score"].mean(), 2),
                "avg_market_volatility": round(
                    weekend_data["market_volatility"].mean(), 3
                ),
            },
            "weekday": {
                "predictions": len(weekday_data),
                "win_rate": round(weekday_data["actual_result"].mean() * 100, 1),
                "avg_confidence": round(weekday_data["confidence_score"].mean(), 2),
                "avg_market_volatility": round(
                    weekday_data["market_volatility"].mean(), 3
                ),
            },
        }

    def _analyze_seasonal_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by season"""
        seasons = ["Winter", "Spring", "Summer", "Autumn"]
        season_stats = {}

        for season in seasons:
            season_data = df[df["season"] == season]
            if len(season_data) > 0:
                season_stats[season] = {
                    "predictions": len(season_data),
                    "win_rate": round(season_data["actual_result"].mean() * 100, 1),
                    "avg_weather_impact": round(
                        season_data["weather_impact_score"].mean(), 3
                    ),
                    "avg_track_bias": round(season_data["track_bias_factor"].mean(), 3),
                }

        return season_stats

    def _analyze_field_size_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by field size"""
        field_ranges = {
            "Small (5-8)": (5, 8),
            "Medium (9-12)": (9, 12),
            "Large (13-16)": (13, 16),
            "Very Large (17+)": (17, 30),
        }

        field_stats = {}
        for range_name, (min_size, max_size) in field_ranges.items():
            field_data = df[
                (df["field_size"] >= min_size) & (df["field_size"] <= max_size)
            ]
            if len(field_data) > 0:
                field_stats[range_name] = {
                    "predictions": len(field_data),
                    "win_rate": round(field_data["actual_result"].mean() * 100, 1),
                    "avg_competitive_rating": round(
                        field_data["competitive_rating"].mean(), 3
                    ),
                    "avg_confidence": round(field_data["confidence_score"].mean(), 2),
                }

        return field_stats

    def _analyze_market_conditions(self, df: pd.DataFrame) -> Dict:
        """Analyze performance under different market conditions"""
        # Categorize market volatility
        low_vol = df[df["market_volatility"] < 0.3]
        med_vol = df[(df["market_volatility"] >= 0.3) & (df["market_volatility"] < 0.7)]
        high_vol = df[df["market_volatility"] >= 0.7]

        return {
            "low_volatility": {
                "predictions": len(low_vol),
                "win_rate": round(low_vol["actual_result"].mean() * 100, 1),
                "avg_value_rating": round(low_vol["value_rating"].mean(), 1),
            },
            "medium_volatility": {
                "predictions": len(med_vol),
                "win_rate": round(med_vol["actual_result"].mean() * 100, 1),
                "avg_value_rating": round(med_vol["value_rating"].mean(), 1),
            },
            "high_volatility": {
                "predictions": len(high_vol),
                "win_rate": round(high_vol["actual_result"].mean() * 100, 1),
                "avg_value_rating": round(high_vol["value_rating"].mean(), 1),
            },
        }

    def _analyze_pace_scenarios(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by pace scenario"""
        pace_scenarios = ["Strong Pace", "Moderate Pace", "Slow Pace", "Unknown"]
        pace_stats = {}

        for scenario in pace_scenarios:
            pace_data = df[df["pace_scenario"] == scenario]
            if len(pace_data) > 0:
                pace_stats[scenario] = {
                    "predictions": len(pace_data),
                    "win_rate": round(pace_data["actual_result"].mean() * 100, 1),
                    "avg_confidence": round(pace_data["confidence_score"].mean(), 2),
                }

        return pace_stats

    def _analyze_class_movements(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by class movements"""
        class_movements = ["Class Drop", "Class Rise", "Same Class", "Maiden"]
        class_stats = {}

        for movement in class_movements:
            class_data = df[df["class_drop_raise"] == movement]
            if len(class_data) > 0:
                class_stats[movement] = {
                    "predictions": len(class_data),
                    "win_rate": round(class_data["actual_result"].mean() * 100, 1),
                    "avg_value_rating": round(class_data["value_rating"].mean(), 1),
                }

        return class_stats

    def _analyze_confidence_reliability(self, df: pd.DataFrame) -> Dict:
        """Analyze how reliable AI confidence scores are"""
        # Categorize by confidence levels
        low_conf = df[df["confidence_score"] < 0.6]
        med_conf = df[(df["confidence_score"] >= 0.6) & (df["confidence_score"] < 0.8)]
        high_conf = df[df["confidence_score"] >= 0.8]

        return {
            "low_confidence": {
                "predictions": len(low_conf),
                "win_rate": round(low_conf["actual_result"].mean() * 100, 1),
                "avg_confidence": round(low_conf["confidence_score"].mean(), 2),
            },
            "medium_confidence": {
                "predictions": len(med_conf),
                "win_rate": round(med_conf["actual_result"].mean() * 100, 1),
                "avg_confidence": round(med_conf["confidence_score"].mean(), 2),
            },
            "high_confidence": {
                "predictions": len(high_conf),
                "win_rate": round(high_conf["actual_result"].mean() * 100, 1),
                "avg_confidence": round(high_conf["confidence_score"].mean(), 2),
            },
        }

    def generate_contextual_reward_signals(self) -> Dict:
        """Generate reward signals based on contextual analysis"""
        analysis = self.analyze_contextual_factors()

        if not analysis:
            return {}

        # Generate contextual rewards based on analysis
        contextual_rewards = {
            "temporal_rewards": {
                "weekend_bonus": (
                    1.2
                    if analysis.get("weekend_vs_weekday", {})
                    .get("weekend", {})
                    .get("win_rate", 0)
                    > analysis.get("weekend_vs_weekday", {})
                    .get("weekday", {})
                    .get("win_rate", 0)
                    else 0.9
                ),
                "best_day_multiplier": self._find_best_day_multiplier(
                    analysis.get("win_rate_by_day", {})
                ),
            },
            "field_size_rewards": self._calculate_field_size_rewards(
                analysis.get("field_size_impact", {})
            ),
            "market_condition_rewards": self._calculate_market_rewards(
                analysis.get("market_conditions", {})
            ),
            "pace_scenario_rewards": self._calculate_pace_rewards(
                analysis.get("pace_scenario_analysis", {})
            ),
            "confidence_reliability_bonus": self._calculate_confidence_bonus(
                analysis.get("confidence_reliability", {})
            ),
        }

        return contextual_rewards

    def _find_best_day_multiplier(self, day_stats: Dict) -> Dict:
        """Find the best performing day and create multipliers"""
        if not day_stats:
            return {}

        best_day = max(day_stats.keys(), key=lambda x: day_stats[x].get("win_rate", 0))
        worst_day = min(day_stats.keys(), key=lambda x: day_stats[x].get("win_rate", 0))

        return {
            "best_day": best_day,
            "best_multiplier": 1.3,
            "worst_day": worst_day,
            "worst_multiplier": 0.8,
        }

    def _calculate_field_size_rewards(self, field_stats: Dict) -> Dict:
        """Calculate rewards based on field size performance"""
        if not field_stats:
            return {}

        rewards = {}
        for field_range, stats in field_stats.items():
            win_rate = stats.get("win_rate", 0)
            if win_rate > 15:  # Above average
                rewards[field_range] = 1.1
            elif win_rate < 10:  # Below average
                rewards[field_range] = 0.9
            else:
                rewards[field_range] = 1.0

        return rewards

    def _calculate_market_rewards(self, market_stats: Dict) -> Dict:
        """Calculate rewards based on market conditions"""
        if not market_stats:
            return {}

        rewards = {}
        for condition, stats in market_stats.items():
            win_rate = stats.get("win_rate", 0)
            value_rating = stats.get("avg_value_rating", 0)

            # Reward high value in volatile markets
            if condition == "high_volatility" and value_rating > 15:
                rewards[condition] = 1.2
            elif condition == "low_volatility" and win_rate > 15:
                rewards[condition] = 1.1
            else:
                rewards[condition] = 1.0

        return rewards

    def _calculate_pace_rewards(self, pace_stats: Dict) -> Dict:
        """Calculate rewards based on pace scenarios"""
        if not pace_stats:
            return {}

        rewards = {}
        for scenario, stats in pace_stats.items():
            win_rate = stats.get("win_rate", 0)
            if win_rate > 15:
                rewards[scenario] = 1.1
            else:
                rewards[scenario] = 1.0

        return rewards

    def _calculate_confidence_bonus(self, conf_stats: Dict) -> Dict:
        """Calculate bonus for confidence reliability"""
        if not conf_stats:
            return {}

        high_conf_data = conf_stats.get("high_confidence", {})
        high_conf_win_rate = high_conf_data.get("win_rate", 0)

        if high_conf_win_rate > 20:
            return {"high_confidence_bonus": 1.25}
        elif high_conf_win_rate > 15:
            return {"high_confidence_bonus": 1.15}
        else:
            return {"high_confidence_bonus": 1.0}

    def print_comprehensive_analysis(self):
        """Print detailed contextual analysis"""
        if not self.connect_database():
            return

        print("\n" + "=" * 80)
        print("🧠 AI REWARD SYSTEM - COMPREHENSIVE CONTEXTUAL ANALYSIS")
        print("=" * 80)

        analysis = self.analyze_contextual_factors()

        if not analysis:
            print("❌ No data available for analysis")
            return

        print(f"\n📊 Dataset Overview:")
        print(f"   • Total AI Predictions: {analysis['total_predictions']:,}")

        # Day of week analysis
        print(f"\n📅 Performance by Day of Week:")
        for day, stats in analysis["win_rate_by_day"].items():
            print(
                f"   • {day:>9}: {stats['predictions']:>3} predictions, "
                f"{stats['win_rate']:>5.1f}% win rate, "
                f"confidence {stats['avg_confidence']:.2f}"
            )

        # Weekend vs Weekday
        print(f"\n🎯 Weekend vs Weekday Analysis:")
        weekend_stats = analysis["weekend_vs_weekday"]
        print(
            f"   • Weekend: {weekend_stats['weekend']['win_rate']:>5.1f}% win rate "
            f"({weekend_stats['weekend']['predictions']} predictions)"
        )
        print(
            f"   • Weekday: {weekend_stats['weekday']['win_rate']:>5.1f}% win rate "
            f"({weekend_stats['weekday']['predictions']} predictions)"
        )

        # Seasonal performance
        print(f"\n🌍 Seasonal Performance:")
        for season, stats in analysis["seasonal_performance"].items():
            print(
                f"   • {season:>6}: {stats['win_rate']:>5.1f}% win rate, "
                f"weather impact {stats['avg_weather_impact']:.3f}"
            )

        # Field size impact
        print(f"\n🏇 Field Size Impact:")
        for field_range, stats in analysis["field_size_impact"].items():
            print(
                f"   • {field_range:>15}: {stats['win_rate']:>5.1f}% win rate, "
                f"competitive rating {stats['avg_competitive_rating']:.3f}"
            )

        # Market conditions
        print(f"\n📈 Market Condition Analysis:")
        for condition, stats in analysis["market_conditions"].items():
            print(
                f"   • {condition.replace('_', ' ').title():>18}: {stats['win_rate']:>5.1f}% win rate, "
                f"value rating {stats['avg_value_rating']:.1f}"
            )

        # Pace scenarios
        print(f"\n⚡ Pace Scenario Analysis:")
        for scenario, stats in analysis["pace_scenario_analysis"].items():
            print(
                f"   • {scenario:>13}: {stats['win_rate']:>5.1f}% win rate "
                f"({stats['predictions']} predictions)"
            )

        # Class movements
        print(f"\n🎖️  Class Movement Impact:")
        for movement, stats in analysis["class_movement_impact"].items():
            print(
                f"   • {movement:>10}: {stats['win_rate']:>5.1f}% win rate, "
                f"value rating {stats['avg_value_rating']:.1f}"
            )

        # Confidence reliability
        print(f"\n🎯 AI Confidence Reliability:")
        for conf_level, stats in analysis["confidence_reliability"].items():
            print(
                f"   • {conf_level.replace('_', ' ').title():>16}: {stats['win_rate']:>5.1f}% win rate "
                f"(confidence {stats['avg_confidence']:.2f})"
            )

        # Generate contextual rewards
        print(f"\n🏆 CONTEXTUAL REWARD SIGNALS:")
        rewards = self.generate_contextual_reward_signals()

        print(f"\n   📅 Temporal Rewards:")
        temporal = rewards.get("temporal_rewards", {})
        print(f"      • Weekend Bonus: {temporal.get('weekend_bonus', 1.0):.2f}x")

        best_day_info = temporal.get("best_day_multiplier", {})
        if best_day_info:
            print(
                f"      • Best Day ({best_day_info.get('best_day', 'N/A')}): "
                f"{best_day_info.get('best_multiplier', 1.0):.2f}x"
            )

        print(f"\n   🏇 Field Size Rewards:")
        for field_range, multiplier in rewards.get("field_size_rewards", {}).items():
            print(f"      • {field_range}: {multiplier:.2f}x")

        print(f"\n   📈 Market Condition Rewards:")
        for condition, multiplier in rewards.get(
            "market_condition_rewards", {}
        ).items():
            print(f"      • {condition.replace('_', ' ').title()}: {multiplier:.2f}x")

        print(f"\n   🎯 Confidence Bonus:")
        conf_bonus = rewards.get("confidence_reliability_bonus", {})
        if conf_bonus:
            print(
                f"      • High Confidence: {conf_bonus.get('high_confidence_bonus', 1.0):.2f}x"
            )

        print(f"\n" + "=" * 80)
        print("🚀 CONTEXTUAL DATA PROVIDES RICH SIGNALS FOR AI LEARNING!")
        print("=" * 80)

        if self.conn:
            self.conn.close()


def main():
    """Run the contextual AI reward analysis demo"""
    print("\n🧠 CONTEXTUAL AI REWARD SYSTEM DEMONSTRATION")
    print("=" * 60)

    analyzer = ContextualAIRewardAnalyzer()
    analyzer.print_comprehensive_analysis()

    print(f"\n💡 Key Benefits of Contextual Data:")
    print(f"   • Temporal patterns reveal optimal betting times")
    print(f"   • Market conditions guide strategy selection")
    print(f"   • Field dynamics inform confidence levels")
    print(f"   • Environmental factors improve accuracy")
    print(f"   • Horse-specific context enhances predictions")
    print(f"\n🎯 This rich contextual data enables the reward algorithm")
    print(f"   to learn sophisticated betting strategies that adapt to")
    print(f"   different racing conditions and market environments!")


if __name__ == "__main__":
    main()
