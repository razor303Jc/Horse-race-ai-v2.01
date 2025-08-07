#!/usr/bin/env python3
"""
AI Profit/Loss ROI Analysis Report Generator
===========================================

Comprehensive analysis of AI system's betting performance and ROI
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np


class AIROIAnalyzer:
    def __init__(self):
        self.db_path = "./data/test_trends_performance.db"
        self.report_data = {}

    def generate_comprehensive_report(self):
        """Generate comprehensive AI profit/loss ROI report"""
        print("🎯 AI PROFIT/LOSS ROI COMPREHENSIVE ANALYSIS")
        print("=" * 60)

        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)

            # 1. Current AI Predictions Performance
            self._analyze_ai_predictions(conn)

            # 2. Betting Strategies Analysis
            self._analyze_betting_strategies(conn)

            # 3. Historical Performance
            self._analyze_historical_performance(conn)

            # 4. Generate summary and recommendations
            self._generate_summary_and_recommendations()

            # 5. Save detailed report
            self._save_detailed_report()

            conn.close()

        except Exception as e:
            print(f"❌ Error generating report: {e}")

    def _analyze_ai_predictions(self, conn):
        """Analyze AI prediction accuracy and value"""
        print("\n🤖 AI PREDICTIONS ANALYSIS")
        print("-" * 40)

        df = pd.read_sql_query("SELECT * FROM ai_predictions", conn)

        if df.empty:
            print("❌ No AI predictions data available")
            self.report_data["ai_predictions"] = {"status": "no_data"}
            return

        analysis = {
            "total_predictions": len(df),
            "avg_consensus_rating": df["consensus_rating"].mean(),
            "avg_win_probability": df["consensus_win_probability"].mean(),
            "avg_confidence": df["prediction_confidence"].mean(),
            "avg_value_rating": df["value_rating"].mean(),
            "high_confidence_count": len(df[df["prediction_confidence"] > 0.8]),
            "high_value_count": len(df[df["value_rating"] > 20.0]),
        }

        print(f"📊 Total Predictions: {analysis['total_predictions']}")
        print(f"📈 Average Consensus Rating: {analysis['avg_consensus_rating']:.2f}")
        print(f"🎯 Average Win Probability: {analysis['avg_win_probability']:.3f}")
        print(f"🔥 Average Confidence: {analysis['avg_confidence']:.2f}")
        print(f"💎 Average Value Rating: {analysis['avg_value_rating']:.1f}")
        print(
            f"⭐ High Confidence Selections (>0.8): {analysis['high_confidence_count']}"
        )
        print(f"💰 High Value Selections (>20.0): {analysis['high_value_count']}")

        # Show top predictions
        if not df.empty:
            print("\n🏆 TOP AI PREDICTIONS:")
            top_predictions = df.nlargest(3, "prediction_confidence")[
                [
                    "horse_name",
                    "consensus_rating",
                    "prediction_confidence",
                    "value_rating",
                ]
            ]
            print(top_predictions.to_string(index=False))

        self.report_data["ai_predictions"] = analysis

    def _analyze_betting_strategies(self, conn):
        """Analyze betting strategy performance"""
        print("\n💰 BETTING STRATEGIES ANALYSIS")
        print("-" * 40)

        df = pd.read_sql_query("SELECT * FROM betting_strategies", conn)

        if df.empty:
            print("❌ No betting strategies data available")
            self.report_data["betting_strategies"] = {"status": "no_data"}
            return

        # Overall analysis
        total_stake = df["recommended_stake"].sum()
        total_profit = df["profit_loss"].sum()
        overall_roi = (total_profit / total_stake * 100) if total_stake > 0 else 0

        analysis = {
            "total_strategies": len(df),
            "total_stake": total_stake,
            "total_profit": total_profit,
            "overall_roi": overall_roi,
            "avg_confidence": df["confidence_score"].mean(),
            "avg_stake": df["recommended_stake"].mean(),
            "avg_odds": df["recommended_odds"].mean(),
        }

        print(f"📊 Total Strategies Generated: {analysis['total_strategies']}")
        print(f"💷 Total Recommended Stakes: £{analysis['total_stake']:.2f}")
        print(f"📈 Total Profit/Loss: £{analysis['total_profit']:.2f}")
        print(f"🎯 Overall ROI: {analysis['overall_roi']:.2f}%")
        print(f"🔥 Average Confidence: {analysis['avg_confidence']:.2f}")
        print(f"💰 Average Stake: £{analysis['avg_stake']:.2f}")
        print(f"📊 Average Odds: {analysis['avg_odds']:.2f}")

        # Strategy type breakdown
        strategy_breakdown = (
            df.groupby("strategy_type")
            .agg(
                {
                    "recommended_stake": "sum",
                    "profit_loss": "sum",
                    "confidence_score": "mean",
                    "recommended_odds": "mean",
                }
            )
            .round(2)
        )

        print(f"\n📋 STRATEGY TYPE BREAKDOWN:")
        print(strategy_breakdown)

        # Calculate ROI per strategy type
        strategy_breakdown["roi"] = (
            strategy_breakdown["profit_loss"]
            / strategy_breakdown["recommended_stake"]
            * 100
        ).fillna(0)

        print(f"\n🎯 ROI BY STRATEGY TYPE:")
        for strategy_type, data in strategy_breakdown.iterrows():
            print(f"   {strategy_type}: {data['roi']:.2f}% ROI")

        self.report_data["betting_strategies"] = {
            **analysis,
            "strategy_breakdown": strategy_breakdown.to_dict(),
        }

    def _analyze_historical_performance(self, conn):
        """Analyze historical performance data"""
        print("\n📈 HISTORICAL PERFORMANCE ANALYSIS")
        print("-" * 40)

        # Check AI method performance
        df_methods = pd.read_sql_query("SELECT * FROM ai_method_performance", conn)
        df_strategy_perf = pd.read_sql_query("SELECT * FROM strategy_performance", conn)

        if df_methods.empty and df_strategy_perf.empty:
            print("❌ No historical performance data available yet")
            print(
                "ℹ️  This indicates the system is newly set up and needs more runtime data"
            )
            self.report_data["historical_performance"] = {
                "status": "no_historical_data",
                "recommendation": "Need to run system for longer period to collect performance data",
            }
            return

        # Analyze method performance if available
        if not df_methods.empty:
            print("🤖 AI METHOD PERFORMANCE:")
            for _, row in df_methods.iterrows():
                print(
                    f"   {row['method_name']}: {row['roi_percentage']:.2f}% ROI, "
                    f"{row['overall_accuracy']:.1%} accuracy"
                )

        # Analyze strategy performance if available
        if not df_strategy_perf.empty:
            print("🎲 STRATEGY PERFORMANCE:")
            for _, row in df_strategy_perf.iterrows():
                print(
                    f"   {row['strategy_type']}: {row['roi_percentage']:.2f}% ROI, "
                    f"{row['win_rate']:.1%} win rate"
                )

    def _generate_summary_and_recommendations(self):
        """Generate summary and recommendations"""
        print("\n🎯 SUMMARY & RECOMMENDATIONS")
        print("-" * 40)

        # Current status assessment
        ai_data = self.report_data.get("ai_predictions", {})
        betting_data = self.report_data.get("betting_strategies", {})

        if ai_data.get("status") == "no_data":
            status = "🟡 DEVELOPMENT PHASE"
            recommendations = [
                "System appears to be in early development/testing phase",
                "Need to run real race analysis to generate AI predictions",
                "Implement live data collection for actual ROI tracking",
            ]
        elif betting_data.get("total_profit", 0) == 0:
            status = "🟠 SIMULATION PHASE"
            recommendations = [
                "AI predictions are being generated successfully",
                "Betting strategies are being calculated but not executed",
                "Ready for paper trading implementation",
                "Need to enable actual bet placement for real ROI data",
            ]
        else:
            roi = betting_data.get("overall_roi", 0)
            if roi > 10:
                status = "🟢 PROFITABLE PHASE"
            elif roi > 0:
                status = "🟡 BREAK-EVEN PHASE"
            else:
                status = "🔴 LOSS PHASE"

            recommendations = [
                f"Current ROI: {roi:.2f}%",
                "Monitor performance over longer time periods",
                "Adjust confidence thresholds based on results",
            ]

        print(f"Current Status: {status}")
        print("\n📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        self.report_data["summary"] = {
            "status": status,
            "recommendations": recommendations,
            "report_date": datetime.now().isoformat(),
        }

    def _save_detailed_report(self):
        """Save detailed report to file"""
        report_file = f"ai_roi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, "w") as f:
            json.dump(self.report_data, f, indent=2, default=str)

        print(f"\n💾 Detailed report saved to: {report_file}")

    def display_quick_summary(self):
        """Display a quick summary of current AI ROI status"""
        print("\n" + "=" * 60)
        print("🚀 QUICK ROI SUMMARY")
        print("=" * 60)

        try:
            conn = sqlite3.connect(self.db_path)

            # Get counts
            predictions_count = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM ai_predictions", conn
            ).iloc[0]["count"]
            strategies_count = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM betting_strategies", conn
            ).iloc[0]["count"]

            if predictions_count > 0:
                pred_df = pd.read_sql_query(
                    "SELECT AVG(prediction_confidence) as conf FROM ai_predictions",
                    conn,
                )
                avg_confidence = pred_df.iloc[0]["conf"]
                print(
                    f"🤖 AI Predictions: {predictions_count} generated (Avg confidence: {avg_confidence:.2f})"
                )
            else:
                print("🤖 AI Predictions: None generated yet")

            if strategies_count > 0:
                stake_df = pd.read_sql_query(
                    "SELECT SUM(recommended_stake) as total, SUM(profit_loss) as profit FROM betting_strategies",
                    conn,
                )
                total_stake = stake_df.iloc[0]["total"]
                total_profit = stake_df.iloc[0]["profit"]
                roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
                print(f"💰 Betting Strategies: {strategies_count} generated")
                print(f"💷 Total Stakes: £{total_stake:.2f}")
                print(f"📈 Total P&L: £{total_profit:.2f}")
                print(f"🎯 Current ROI: {roi:.2f}%")
            else:
                print("💰 Betting Strategies: None generated yet")

            conn.close()

        except Exception as e:
            print(f"❌ Error in quick summary: {e}")


def main():
    """Main function to run AI ROI analysis"""
    analyzer = AIROIAnalyzer()

    # Display quick summary first
    analyzer.display_quick_summary()

    # Generate comprehensive report
    analyzer.generate_comprehensive_report()


if __name__ == "__main__":
    main()
