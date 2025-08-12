#!/usr/bin/env python3
"""
AI Reward Algorithm - Money-Making Analysis System
Analyzes AI selections, calculates rewards/penalties, and optimizes for profit
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIRewardAnalyzer:
    """
    Advanced reward algorithm that analyzes AI selections for profit optimization.

    Features:
    - Profit-based reward calculation
    - Kelly Criterion optimization
    - Risk-adjusted returns
    - Market efficiency analysis
    - Selection quality scoring
    - Strategy performance tracking
    """

    def __init__(self, db_path: str = "ai_strategies_corrected.db"):
        self.db_path = db_path
        self.reward_history = []
        self.profit_targets = {
            "daily": 50,  # £50 daily target
            "weekly": 350,  # £350 weekly target
            "monthly": 1500,  # £1500 monthly target
        }
        self.risk_limits = {
            "max_daily_loss": 100,  # Max £100 daily loss
            "max_stake_per_bet": 50,  # Max £50 per bet
            "max_bankroll_risk": 0.1,  # Max 10% bankroll risk
        }

    def connect_db(self):
        """Connect to database"""
        return sqlite3.connect(self.db_path)

    def analyze_ai_selections(self) -> Dict:
        """Comprehensive analysis of AI selections for reward calculation"""

        conn = self.connect_db()

        # Get all AI predictions and strategies
        ai_data = pd.read_sql_query(
            """
            SELECT 
                p.prediction_id,
                p.race_id,
                p.participant_id,
                p.predicted_probability,
                p.confidence_score,
                p.value_rating,
                p.form_score,
                p.pace_rating,
                p.class_rating,
                s.strategy_type,
                s.bet_type,
                s.recommended_stake,
                s.recommended_odds,
                s.kelly_fraction,
                s.value_percentage,
                s.risk_rating,
                s.strategy_confidence,
                s.expected_value,
                rp.odds_decimal as market_odds,
                rp.actual_finish_position,
                h.name as horse_name,
                rc.race_name,
                rc.date
            FROM ai_predictions p
            JOIN ai_betting_strategies s ON p.prediction_id = s.prediction_id
            JOIN race_participants rp ON p.participant_id = rp.participant_id
            JOIN horses h ON rp.horse_id = h.horse_id
            JOIN race_cards rc ON p.race_id = rc.race_id
            ORDER BY p.prediction_id
        """,
            conn,
        )

        conn.close()

        if ai_data.empty:
            logger.warning("No AI selection data found")
            return {"error": "No data available"}

        # Calculate rewards and penalties
        reward_analysis = self._calculate_reward_signals(ai_data)

        # Analyze profit potential
        profit_analysis = self._analyze_profit_potential(ai_data)

        # Market efficiency analysis
        market_analysis = self._analyze_market_efficiency(ai_data)

        # Strategy performance
        strategy_performance = self._analyze_strategy_performance(ai_data)

        # Generate recommendations
        recommendations = self._generate_recommendations(ai_data)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_selections": len(ai_data),
            "reward_analysis": reward_analysis,
            "profit_analysis": profit_analysis,
            "market_analysis": market_analysis,
            "strategy_performance": strategy_performance,
            "recommendations": recommendations,
            "summary": self._generate_summary(
                ai_data, reward_analysis, profit_analysis
            ),
        }

    def _calculate_reward_signals(self, data: pd.DataFrame) -> Dict:
        """Calculate reward signals based on profit potential and accuracy"""

        rewards = {
            "accuracy_rewards": 0.0,
            "value_rewards": 0.0,
            "kelly_rewards": 0.0,
            "profit_rewards": 0.0,
            "confidence_rewards": 0.0,
        }

        penalties = {
            "poor_predictions": 0.0,
            "overconfidence": 0.0,
            "negative_value": 0.0,
            "high_risk": 0.0,
        }

        # Simulate betting results
        for _, row in data.iterrows():
            actual_finish = row["actual_finish_position"]
            predicted_prob = row["predicted_probability"]
            market_odds = row["market_odds"]
            stake = float(row["recommended_stake"])
            strategy_type = row["strategy_type"]

            # Calculate if bet would have won
            if strategy_type == "value_bet" and actual_finish == 1:
                # Win bet
                profit = stake * (market_odds - 1)
                rewards["profit_rewards"] += float(
                    profit * 0.1
                )  # 10% of profit as reward
                rewards["accuracy_rewards"] += 10.0
            elif strategy_type == "each_way" and actual_finish <= 3:
                # Each-way place
                place_profit = (
                    stake * 0.25 * (market_odds - 1)
                )  # Simplified place calculation
                rewards["profit_rewards"] += float(place_profit * 0.1)
                rewards["accuracy_rewards"] += 5.0
            else:
                # Losing bet
                loss = stake
                penalties["poor_predictions"] += float(
                    loss * 0.05
                )  # 5% of loss as penalty

            # Value betting rewards
            value_pct = row.get("value_percentage", 0) or 0
            if value_pct > 10:
                rewards["value_rewards"] += value_pct * 0.5
            elif value_pct < 0:
                penalties["negative_value"] += abs(value_pct) * 0.3

            # Kelly Criterion rewards
            kelly_fraction = row.get("kelly_fraction", 0) or 0
            if 0 < kelly_fraction < 0.1:  # Good Kelly sizing
                rewards["kelly_rewards"] += kelly_fraction * 100
            elif kelly_fraction > 0.2:  # Over-betting
                penalties["overconfidence"] += (kelly_fraction - 0.2) * 50

            # Confidence calibration
            confidence = row["confidence_score"]
            if 0.6 <= confidence <= 0.8:  # Well-calibrated confidence
                rewards["confidence_rewards"] += 2
            elif confidence > 0.9:  # Overconfident
                penalties["overconfidence"] += 3

        return {
            "rewards": rewards,
            "penalties": penalties,
            "net_reward": sum(rewards.values()) - sum(penalties.values()),
        }

    def _analyze_profit_potential(self, data: pd.DataFrame) -> Dict:
        """Analyze potential profit from AI selections"""

        total_stakes = data["recommended_stake"].sum()

        # Simulate actual betting results
        simulated_results = []

        for _, row in data.iterrows():
            actual_finish = row["actual_finish_position"]
            market_odds = row["market_odds"]
            stake = row["recommended_stake"]
            strategy_type = row["strategy_type"]
            bet_type = row["bet_type"]

            if strategy_type == "value_bet" and bet_type == "win":
                if actual_finish == 1:
                    profit = stake * (market_odds - 1)
                else:
                    profit = -stake
            elif strategy_type == "each_way":
                win_stake = stake / 2
                place_stake = stake / 2

                win_profit = (
                    win_stake * (market_odds - 1) if actual_finish == 1 else -win_stake
                )
                place_profit = (
                    place_stake * 0.25 * (market_odds - 1)
                    if actual_finish <= 3
                    else -place_stake
                )
                profit = win_profit + place_profit
            elif strategy_type == "twenty_eighty":
                if bet_type == "win" and actual_finish == 1:
                    profit = stake * (market_odds - 1)
                elif bet_type == "place" and actual_finish <= 3:
                    profit = stake * 0.25 * (market_odds - 1)  # Simplified place odds
                else:
                    profit = -stake
            else:
                # Default win bet
                profit = stake * (market_odds - 1) if actual_finish == 1 else -stake

            simulated_results.append(
                {
                    "strategy_type": strategy_type,
                    "bet_type": bet_type,
                    "stake": stake,
                    "profit": profit,
                    "roi": (profit / stake) * 100,
                }
            )

        results_df = pd.DataFrame(simulated_results)

        total_profit = results_df["profit"].sum()
        total_roi = (total_profit / total_stakes) * 100
        win_rate = len(results_df[results_df["profit"] > 0]) / len(results_df)

        # Strategy breakdown
        strategy_breakdown = (
            results_df.groupby("strategy_type")
            .agg({"profit": ["sum", "mean", "count"], "stake": "sum", "roi": "mean"})
            .round(2)
        )

        return {
            "total_stakes": round(total_stakes, 2),
            "total_profit": round(total_profit, 2),
            "total_roi": round(total_roi, 2),
            "win_rate": round(win_rate * 100, 2),
            "profitable_strategies": len(results_df[results_df["profit"] > 0]),
            "losing_strategies": len(results_df[results_df["profit"] < 0]),
            "strategy_breakdown": strategy_breakdown.to_dict(),
            "best_strategy": results_df.groupby("strategy_type")["profit"]
            .sum()
            .idxmax(),
            "worst_strategy": results_df.groupby("strategy_type")["profit"]
            .sum()
            .idxmin(),
        }

    def _analyze_market_efficiency(self, data: pd.DataFrame) -> Dict:
        """Analyze how well AI identifies market inefficiencies"""

        value_opportunities = 0
        correct_value_calls = 0
        market_beat_rate = 0

        for _, row in data.iterrows():
            predicted_prob = row["predicted_probability"]
            market_prob = 1 / row["market_odds"]
            actual_finish = row["actual_finish_position"]

            # Check if AI found value (predicted prob > market prob)
            if predicted_prob > market_prob * 1.1:  # 10% threshold
                value_opportunities += 1
                if actual_finish == 1:  # And horse actually won
                    correct_value_calls += 1

            # Check if AI beat market assessment
            if predicted_prob > market_prob and actual_finish == 1:
                market_beat_rate += 1
            elif predicted_prob < market_prob and actual_finish > 3:
                market_beat_rate += 1  # Correctly avoided poor value

        efficiency_score = (
            (correct_value_calls / value_opportunities * 100)
            if value_opportunities > 0
            else 0
        )
        market_beat_pct = (market_beat_rate / len(data)) * 100

        return {
            "value_opportunities_found": value_opportunities,
            "correct_value_calls": correct_value_calls,
            "value_accuracy": round(efficiency_score, 2),
            "market_beat_percentage": round(market_beat_pct, 2),
            "edge_detected": efficiency_score > 50,
            "market_efficiency_score": round(efficiency_score, 1),
        }

    def _analyze_strategy_performance(self, data: pd.DataFrame) -> Dict:
        """Analyze performance by strategy type"""

        strategy_stats = {}

        for strategy in data["strategy_type"].unique():
            strategy_data = data[data["strategy_type"] == strategy]

            # Calculate strategy-specific metrics
            avg_confidence = strategy_data["strategy_confidence"].mean()
            avg_value = (
                strategy_data["value_percentage"].mean()
                if "value_percentage" in strategy_data.columns
                else 0
            )
            total_stake = strategy_data["recommended_stake"].sum()

            # Simulated returns for this strategy
            strategy_profit = 0
            winners = 0

            for _, row in strategy_data.iterrows():
                if row["actual_finish_position"] == 1:
                    strategy_profit += row["recommended_stake"] * (
                        row["market_odds"] - 1
                    )
                    winners += 1
                else:
                    strategy_profit -= row["recommended_stake"]

            strategy_roi = (
                (strategy_profit / total_stake) * 100 if total_stake > 0 else 0
            )
            win_rate = (winners / len(strategy_data)) * 100

            strategy_stats[strategy] = {
                "selections": len(strategy_data),
                "total_stake": round(total_stake, 2),
                "profit": round(strategy_profit, 2),
                "roi": round(strategy_roi, 2),
                "win_rate": round(win_rate, 2),
                "avg_confidence": round(avg_confidence, 3),
                "avg_value": round(avg_value, 2),
                "profitable": strategy_profit > 0,
            }

        return strategy_stats

    def _generate_recommendations(self, data: pd.DataFrame) -> List[Dict]:
        """Generate actionable recommendations for profit optimization"""

        recommendations = []

        # High-value opportunities
        high_value = data[data["value_percentage"] > 15]
        if not high_value.empty:
            recommendations.append(
                {
                    "type": "HIGH_VALUE_OPPORTUNITIES",
                    "priority": "HIGH",
                    "message": f"Found {len(high_value)} high-value selections (>15% edge)",
                    "action": "Increase stakes on these selections",
                    "selections": high_value[
                        [
                            "horse_name",
                            "race_name",
                            "value_percentage",
                            "recommended_stake",
                        ]
                    ].to_dict("records")[:5],
                }
            )

        # Kelly Criterion optimization
        optimal_kelly = data[
            (data["kelly_fraction"] > 0.02) & (data["kelly_fraction"] < 0.08)
        ]
        if not optimal_kelly.empty:
            recommendations.append(
                {
                    "type": "OPTIMAL_KELLY_SIZING",
                    "priority": "MEDIUM",
                    "message": f"{len(optimal_kelly)} selections have optimal Kelly sizing (2-8%)",
                    "action": "These are well-sized bets - maintain current stakes",
                }
            )

        # Risk management
        high_risk = data[data["recommended_stake"] > 40]
        if not high_risk.empty:
            recommendations.append(
                {
                    "type": "RISK_MANAGEMENT",
                    "priority": "HIGH",
                    "message": f"{len(high_risk)} selections exceed £40 stake limit",
                    "action": "Reduce stakes to manage risk",
                }
            )

        # Strategy focus
        strategy_profits = (
            data.groupby("strategy_type")
            .apply(
                lambda x: x["recommended_stake"].sum()
                * 0.1  # Simplified profit estimate
            )
            .sort_values(ascending=False)
        )

        best_strategy = strategy_profits.index[0]
        recommendations.append(
            {
                "type": "STRATEGY_FOCUS",
                "priority": "MEDIUM",
                "message": f"'{best_strategy}' strategy shows highest profit potential",
                "action": f"Focus more resources on {best_strategy} selections",
            }
        )

        return recommendations

    def _generate_summary(
        self, data: pd.DataFrame, rewards: Dict, profits: Dict
    ) -> Dict:
        """Generate comprehensive summary for reward algorithm"""

        return {
            "ai_performance_grade": self._calculate_performance_grade(rewards, profits),
            "profit_potential": (
                "HIGH"
                if profits["total_roi"] > 10
                else "MEDIUM" if profits["total_roi"] > 0 else "LOW"
            ),
            "risk_assessment": (
                "LOW"
                if profits["win_rate"] > 30
                else "MEDIUM" if profits["win_rate"] > 15 else "HIGH"
            ),
            "market_edge": (
                "STRONG"
                if rewards["net_reward"] > 100
                else "MODERATE" if rewards["net_reward"] > 0 else "WEAK"
            ),
            "bankroll_impact": f"£{profits['total_profit']} projected profit from £{profits['total_stakes']} stakes",
            "recommendation": self._get_main_recommendation(profits, rewards),
        }

    def _calculate_performance_grade(self, rewards: Dict, profits: Dict) -> str:
        """Calculate overall AI performance grade"""

        score = 0

        # Profit performance (40% weight)
        if profits["total_roi"] > 20:
            score += 40
        elif profits["total_roi"] > 10:
            score += 30
        elif profits["total_roi"] > 0:
            score += 20

        # Reward signals (30% weight)
        net_reward = rewards["net_reward"]
        if net_reward > 200:
            score += 30
        elif net_reward > 100:
            score += 25
        elif net_reward > 0:
            score += 15

        # Win rate (20% weight)
        if profits["win_rate"] > 40:
            score += 20
        elif profits["win_rate"] > 25:
            score += 15
        elif profits["win_rate"] > 15:
            score += 10

        # Risk management (10% weight)
        if profits["total_stakes"] < 500:  # Conservative staking
            score += 10
        elif profits["total_stakes"] < 1000:
            score += 7

        if score >= 85:
            return "A+"
        elif score >= 75:
            return "A"
        elif score >= 65:
            return "B+"
        elif score >= 55:
            return "B"
        elif score >= 45:
            return "C"
        else:
            return "D"

    def _get_main_recommendation(self, profits: Dict, rewards: Dict) -> str:
        """Get main actionable recommendation"""

        if profits["total_roi"] > 15:
            return "SCALE UP: Strong profit signals - increase bankroll allocation"
        elif profits["total_roi"] > 5:
            return "CONTINUE: Positive returns - maintain current approach"
        elif profits["total_roi"] > -5:
            return "OPTIMIZE: Minor adjustments needed for profitability"
        else:
            return "REVIEW: Significant strategy changes required"


def main():
    """Run comprehensive AI reward analysis"""

    print("🎯 AI REWARD ALGORITHM - MONEY-MAKING ANALYSIS")
    print("=" * 60)

    analyzer = AIRewardAnalyzer()
    results = analyzer.analyze_ai_selections()

    if "error" in results:
        print(f"❌ {results['error']}")
        return

    # Display results
    print(f"\n📊 ANALYSIS SUMMARY ({results['timestamp']})")
    print(f"Total AI Selections: {results['total_selections']:,}")

    print(f"\n💰 PROFIT ANALYSIS:")
    profit = results["profit_analysis"]
    print(f"  Total Stakes: £{profit['total_stakes']:,.2f}")
    print(f"  Projected Profit: £{profit['total_profit']:,.2f}")
    print(f"  ROI: {profit['total_roi']:.2f}%")
    print(f"  Win Rate: {profit['win_rate']:.1f}%")
    print(f"  Best Strategy: {profit['best_strategy']}")

    print(f"\n🎯 REWARD SIGNALS:")
    rewards = results["reward_analysis"]["rewards"]
    penalties = results["reward_analysis"]["penalties"]
    print(f"  Profit Rewards: {rewards['profit_rewards']:.1f}")
    print(f"  Value Rewards: {rewards['value_rewards']:.1f}")
    print(f"  Kelly Rewards: {rewards['kelly_rewards']:.1f}")
    print(f"  Net Reward Score: {results['reward_analysis']['net_reward']:.1f}")

    print(f"\n📈 MARKET EFFICIENCY:")
    market = results["market_analysis"]
    print(f"  Value Opportunities: {market['value_opportunities_found']}")
    print(f"  Correct Value Calls: {market['correct_value_calls']}")
    print(f"  Market Beat Rate: {market['market_beat_percentage']:.1f}%")
    print(f"  Efficiency Score: {market['market_efficiency_score']:.1f}")

    print(f"\n🏆 PERFORMANCE SUMMARY:")
    summary = results["summary"]
    print(f"  AI Grade: {summary['ai_performance_grade']}")
    print(f"  Profit Potential: {summary['profit_potential']}")
    print(f"  Risk Level: {summary['risk_assessment']}")
    print(f"  Market Edge: {summary['market_edge']}")
    print(f"  Main Recommendation: {summary['recommendation']}")

    print(f"\n💡 KEY RECOMMENDATIONS:")
    for i, rec in enumerate(results["recommendations"][:3], 1):
        print(f"  {i}. [{rec['priority']}] {rec['message']}")
        print(f"     Action: {rec['action']}")

    # Save detailed results
    with open(
        f"ai_reward_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w"
    ) as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed analysis saved to file")
    print("=" * 60)


if __name__ == "__main__":
    main()
