#!/usr/bin/env python3
"""
AI Selections Strategy Optimizer
Analyze performance data to optimize betting strategies
"""

import logging
import sys
import psycopg2
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """AI Selections betting strategy optimization"""

    def __init__(self):
        self.db_config = {
            "host": "postgres",
            "port": "5432",
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def get_performance_data(self) -> pd.DataFrame:
        """Get all AI performance data for analysis"""
        logger.info("📊 Loading performance data...")

        try:
            conn = psycopg2.connect(**self.db_config)
            query = """
                SELECT 
                    horse_name,
                    course,
                    race_date,
                    ai_win_probability,
                    ai_confidence_score,
                    actual_starting_price,
                    win_prediction_correct,
                    place_prediction_correct,
                    roi_if_backed,
                    model_name,
                    model_version,
                    actual_position,
                    ai_selection_type
                FROM ai_selections_performance
                ORDER BY race_date, ai_win_probability DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            logger.info(f"✅ Loaded {len(df)} performance records")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load performance data: {e}")
            return pd.DataFrame()

    def probability_threshold_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by probability thresholds"""
        logger.info("🎯 Analyzing probability thresholds...")

        thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
        results = []

        for threshold in thresholds:
            subset = df[df["ai_win_probability"] >= threshold]

            if len(subset) == 0:
                continue

            total_bets = len(subset)
            winners = subset["win_prediction_correct"].sum()
            win_rate = winners / total_bets if total_bets > 0 else 0
            total_roi = subset["roi_if_backed"].sum()
            avg_roi = total_roi / total_bets if total_bets > 0 else 0
            avg_odds = subset["actual_starting_price"].mean()

            results.append(
                {
                    "threshold": threshold,
                    "selections": total_bets,
                    "winners": winners,
                    "win_rate": round(win_rate * 100, 2),
                    "total_roi": round(total_roi, 2),
                    "avg_roi_per_bet": round(avg_roi, 2),
                    "avg_odds": round(avg_odds, 2),
                    "profitability": "PROFIT" if total_roi > 0 else "LOSS",
                }
            )

        return {
            "threshold_analysis": results,
            "best_threshold": (
                max(results, key=lambda x: x["total_roi"]) if results else None
            ),
        }

    def course_performance_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by course"""
        logger.info("🏇 Analyzing course performance...")

        course_analysis = (
            df.groupby("course")
            .agg(
                {
                    "horse_name": "count",
                    "win_prediction_correct": ["sum", "mean"],
                    "roi_if_backed": ["sum", "mean"],
                    "ai_win_probability": "mean",
                    "actual_starting_price": "mean",
                }
            )
            .round(2)
        )

        course_analysis.columns = [
            "selections",
            "winners",
            "win_rate",
            "total_roi",
            "avg_roi",
            "avg_probability",
            "avg_odds",
        ]

        course_analysis["win_rate"] = (course_analysis["win_rate"] * 100).round(2)
        course_analysis = course_analysis[course_analysis["selections"] >= 3]
        course_analysis = course_analysis.sort_values("total_roi", ascending=False)

        return {
            "course_performance": course_analysis.to_dict("index"),
            "best_courses": course_analysis.head(5).index.tolist(),
            "worst_courses": course_analysis.tail(3).index.tolist(),
        }

    def odds_range_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by odds ranges"""
        logger.info("💰 Analyzing odds ranges...")

        # Define odds ranges
        bins = [0, 2, 3, 4, 6, 10, float("inf")]
        labels = ["1.0-2.0", "2.0-3.0", "3.0-4.0", "4.0-6.0", "6.0-10.0", "10.0+"]

        df["odds_range"] = pd.cut(
            df["actual_starting_price"], bins=bins, labels=labels, include_lowest=True
        )

        odds_analysis = (
            df.groupby("odds_range")
            .agg(
                {
                    "horse_name": "count",
                    "win_prediction_correct": ["sum", "mean"],
                    "roi_if_backed": ["sum", "mean"],
                    "ai_win_probability": "mean",
                }
            )
            .round(2)
        )

        odds_analysis.columns = [
            "selections",
            "winners",
            "win_rate",
            "total_roi",
            "avg_roi",
            "avg_probability",
        ]
        odds_analysis["win_rate"] = (odds_analysis["win_rate"] * 100).round(2)

        return {
            "odds_analysis": odds_analysis.to_dict("index"),
            "profitable_ranges": odds_analysis[
                odds_analysis["total_roi"] > 0
            ].index.tolist(),
        }

    def staking_strategy_simulation(self, df: pd.DataFrame) -> Dict:
        """Simulate different staking strategies"""
        logger.info("📈 Simulating staking strategies...")

        strategies = {}

        # Level stakes (£1 per bet)
        level_roi = df["roi_if_backed"].sum()
        strategies["level_stakes"] = {
            "total_roi": round(level_roi, 2),
            "avg_roi_per_bet": round(level_roi / len(df), 2),
            "description": "£1 per bet",
        }

        # Probability-weighted stakes
        df["prob_stake"] = df["ai_win_probability"] * 2  # Max £2 stake
        df["prob_weighted_roi"] = (
            df["prob_stake"]
            * (df["actual_starting_price"] - 1)
            * df["win_prediction_correct"]
            - df["prob_stake"]
        )

        prob_roi = df["prob_weighted_roi"].sum()
        strategies["probability_weighted"] = {
            "total_roi": round(prob_roi, 2),
            "avg_roi_per_bet": round(prob_roi / len(df), 2),
            "description": "Stake = probability × 2",
        }

        # Kelly Criterion (simplified)
        df["edge"] = df["ai_win_probability"] - (1 / df["actual_starting_price"])
        df["kelly_fraction"] = np.where(
            df["edge"] > 0, df["edge"] / (df["actual_starting_price"] - 1), 0
        )
        df["kelly_stake"] = np.clip(df["kelly_fraction"] * 100, 0, 10)  # Max £10
        df["kelly_roi"] = (
            df["kelly_stake"]
            * (df["actual_starting_price"] - 1)
            * df["win_prediction_correct"]
            - df["kelly_stake"]
        )

        kelly_roi = df["kelly_roi"].sum()
        strategies["kelly_criterion"] = {
            "total_roi": round(kelly_roi, 2),
            "avg_roi_per_bet": round(kelly_roi / len(df), 2),
            "description": "Kelly Criterion (max £10)",
        }

        return strategies

    def generate_optimization_recommendations(self, analyses: Dict) -> List[str]:
        """Generate actionable optimization recommendations"""
        recommendations = []

        # Probability threshold recommendations
        threshold_data = analyses.get("probability_analysis", {})
        best_threshold = threshold_data.get("best_threshold")
        if best_threshold:
            recommendations.append(
                f"🎯 PROBABILITY FILTER: Only bet on selections with "
                f"≥{best_threshold['threshold']*100:.0f}% probability "
                f"({best_threshold['selections']} bets, "
                f"£{best_threshold['total_roi']} ROI)"
            )

        # Course recommendations
        course_data = analyses.get("course_analysis", {})
        best_courses = course_data.get("best_courses", [])
        if best_courses:
            recommendations.append(
                f"🏇 COURSE FOCUS: Prioritize {', '.join(best_courses[:3])} "
                f"courses for best performance"
            )

        # Odds range recommendations
        odds_data = analyses.get("odds_analysis", {})
        profitable_ranges = odds_data.get("profitable_ranges", [])
        if profitable_ranges:
            recommendations.append(
                f"💰 ODDS FILTER: Focus on odds ranges: "
                f"{', '.join(profitable_ranges)} for profitability"
            )

        # Staking recommendations
        staking_data = analyses.get("staking_analysis", {})
        best_strategy = max(staking_data.items(), key=lambda x: x[1]["total_roi"])
        recommendations.append(
            f"📊 STAKING: Use {best_strategy[0]} strategy "
            f"(£{best_strategy[1]['total_roi']} ROI)"
        )

        return recommendations

    def display_analysis_results(self, analyses: Dict):
        """Display formatted analysis results"""
        logger.info("📊 STRATEGY OPTIMIZATION RESULTS")
        logger.info("=" * 60)

        # Probability thresholds
        prob_data = analyses.get("probability_analysis", {})
        if prob_data:
            logger.info("\n🎯 PROBABILITY THRESHOLD ANALYSIS:")
            for result in prob_data["threshold_analysis"]:
                logger.info(
                    f"   ≥{result['threshold']*100:.0f}%: "
                    f"{result['selections']} bets, {result['win_rate']}% wins, "
                    f"£{result['total_roi']} ROI ({result['profitability']})"
                )

        # Course performance
        course_data = analyses.get("course_analysis", {})
        if course_data:
            logger.info("\n🏇 TOP PERFORMING COURSES:")
            for course in course_data["best_courses"][:5]:
                perf = course_data["course_performance"][course]
                logger.info(
                    f"   {course}: {perf['selections']} bets, "
                    f"{perf['win_rate']}% wins, £{perf['total_roi']} ROI"
                )

        # Staking strategies
        staking_data = analyses.get("staking_analysis", {})
        if staking_data:
            logger.info("\n📊 STAKING STRATEGY COMPARISON:")
            for strategy, data in staking_data.items():
                logger.info(
                    f"   {strategy.title()}: £{data['total_roi']} total ROI "
                    f"({data['description']})"
                )

        # Recommendations
        recommendations = analyses.get("recommendations", [])
        if recommendations:
            logger.info("\n💡 OPTIMIZATION RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"   {i}. {rec}")

        logger.info("=" * 60)

    def run_complete_analysis(self) -> Dict:
        """Run complete strategy optimization analysis"""
        logger.info("🚀 Starting strategy optimization analysis...")

        # Load data
        df = self.get_performance_data()
        if df.empty:
            logger.error("❌ No performance data available")
            return {}

        analyses = {}

        # Run all analyses
        analyses["probability_analysis"] = self.probability_threshold_analysis(df)
        analyses["course_analysis"] = self.course_performance_analysis(df)
        analyses["odds_analysis"] = self.odds_range_analysis(df)
        analyses["staking_analysis"] = self.staking_strategy_simulation(df)

        # Generate recommendations
        analyses["recommendations"] = self.generate_optimization_recommendations(
            analyses
        )

        # Display results
        self.display_analysis_results(analyses)

        return analyses


def main():
    optimizer = StrategyOptimizer()
    results = optimizer.run_complete_analysis()
    return results


if __name__ == "__main__":
    main()
