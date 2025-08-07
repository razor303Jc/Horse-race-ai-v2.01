#!/usr/bin/env python3
"""
Simple AI Reward Analyzer - Money-Making Analysis
Analyzes AI selections for profit and provides reward signals
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_ai_performance(db_path: str = "ai_strategies_corrected.db"):
    """Analyze AI performance and calculate reward signals"""

    print("🎯 AI REWARD ALGORITHM - MONEY-MAKING ANALYSIS")
    print("=" * 60)

    conn = sqlite3.connect(db_path)

    # Get AI betting data
    try:
        query = """
        SELECT 
            s.strategy_type,
            s.bet_type,
            s.recommended_stake,
            s.recommended_odds,
            s.value_percentage,
            s.kelly_fraction,
            s.strategy_confidence,
            s.risk_rating,
            rp.actual_finish_position,
            rp.odds_decimal as market_odds,
            h.name as horse_name,
            rc.race_name,
            rc.date
        FROM ai_betting_strategies s
        JOIN ai_predictions p ON s.prediction_id = p.prediction_id
        JOIN race_participants rp ON p.participant_id = rp.participant_id
        JOIN horses h ON rp.horse_id = h.horse_id
        JOIN race_cards rc ON p.race_id = rc.race_id
        ORDER BY s.strategy_id
        """

        data = pd.read_sql_query(query, conn)
        conn.close()

        if data.empty:
            print("❌ No AI betting strategy data found")
            return

        print(f"\n📊 Analyzing {len(data):,} AI betting strategies...")

        # Calculate betting results
        results = calculate_betting_results(data)

        # Calculate reward signals
        rewards = calculate_reward_signals(data, results)

        # Display analysis
        display_analysis(data, results, rewards)

        # Save results
        save_analysis_results(data, results, rewards)

    except Exception as e:
        logger.error(f"Error analyzing AI performance: {e}")
        print(f"❌ Analysis failed: {e}")


def calculate_betting_results(data):
    """Calculate betting results for each strategy"""

    results = []
    total_stakes = 0.0
    total_profit = 0.0
    winners = 0

    for _, row in data.iterrows():
        try:
            # Get values safely
            stake = float(row.get("recommended_stake", 10))
            odds = float(row.get("market_odds", 5.0))
            finish_pos = int(row.get("actual_finish_position", 10))
            strategy_type = str(row.get("strategy_type", "unknown"))
            bet_type = str(row.get("bet_type", "win"))

            # Calculate profit/loss
            profit = 0.0

            if strategy_type == "value_bet" and bet_type == "win":
                if finish_pos == 1:
                    profit = stake * (odds - 1)
                    winners += 1
                else:
                    profit = -stake

            elif strategy_type == "each_way":
                win_stake = stake / 2
                place_stake = stake / 2

                # Win part
                if finish_pos == 1:
                    profit += win_stake * (odds - 1)
                    winners += 1
                else:
                    profit -= win_stake

                # Place part (simplified - assume 1/4 odds for places 1-3)
                if finish_pos <= 3:
                    profit += place_stake * ((odds * 0.25) - 1)
                else:
                    profit -= place_stake

            elif strategy_type == "twenty_eighty":
                if bet_type == "win" and finish_pos == 1:
                    profit = stake * (odds - 1)
                    winners += 1
                elif bet_type == "place" and finish_pos <= 3:
                    profit = stake * ((odds * 0.25) - 1)
                else:
                    profit = -stake

            elif strategy_type == "dutching":
                if finish_pos == 1:
                    profit = stake * (odds - 1)
                    winners += 1
                else:
                    profit = -stake
            else:
                # Default win bet
                if finish_pos == 1:
                    profit = stake * (odds - 1)
                    winners += 1
                else:
                    profit = -stake

            total_stakes += stake
            total_profit += profit

            results.append(
                {
                    "strategy_type": strategy_type,
                    "bet_type": bet_type,
                    "stake": stake,
                    "odds": odds,
                    "finish_position": finish_pos,
                    "profit": profit,
                    "won": 1 if profit > 0 else 0,
                }
            )

        except Exception as e:
            logger.warning(f"Error processing row: {e}")
            continue

    return {
        "individual_results": results,
        "total_stakes": total_stakes,
        "total_profit": total_profit,
        "total_winners": winners,
        "total_bets": len(results),
        "win_rate": (winners / len(results)) * 100 if results else 0,
        "roi": (total_profit / total_stakes) * 100 if total_stakes > 0 else 0,
    }


def calculate_reward_signals(data, results):
    """Calculate reward signals for the AI"""

    rewards = {
        "profit_rewards": 0.0,
        "accuracy_rewards": 0.0,
        "value_rewards": 0.0,
        "kelly_rewards": 0.0,
        "consistency_rewards": 0.0,
    }

    penalties = {
        "loss_penalties": 0.0,
        "poor_value_penalties": 0.0,
        "overconfidence_penalties": 0.0,
        "high_risk_penalties": 0.0,
    }

    # Process each betting result
    for i, result in enumerate(results["individual_results"]):
        try:
            row = data.iloc[i]

            # Profit-based rewards
            if result["profit"] > 0:
                rewards["profit_rewards"] += result["profit"] * 0.1  # 10% of profit
                rewards["accuracy_rewards"] += 5.0
            else:
                penalties["loss_penalties"] += (
                    abs(result["profit"]) * 0.05
                )  # 5% of loss

            # Value betting rewards
            value_pct = float(row.get("value_percentage", 0) or 0)
            if value_pct > 10:
                rewards["value_rewards"] += value_pct * 0.5
            elif value_pct < -5:
                penalties["poor_value_penalties"] += abs(value_pct) * 0.3

            # Kelly Criterion rewards
            kelly = float(row.get("kelly_fraction", 0) or 0)
            if 0.02 <= kelly <= 0.08:  # Optimal Kelly range
                rewards["kelly_rewards"] += kelly * 100
            elif kelly > 0.2:  # Over-betting
                penalties["overconfidence_penalties"] += (kelly - 0.2) * 50

            # Risk management
            confidence = float(row.get("strategy_confidence", 0) or 0)
            if 0.6 <= confidence <= 0.8:  # Well-calibrated
                rewards["consistency_rewards"] += 2.0
            elif confidence > 0.9:  # Overconfident
                penalties["overconfidence_penalties"] += 3.0

        except Exception as e:
            logger.warning(f"Error processing reward calculation: {e}")
            continue

    # Calculate net reward
    total_rewards = sum(rewards.values())
    total_penalties = sum(penalties.values())
    net_reward = total_rewards - total_penalties

    return {
        "rewards": rewards,
        "penalties": penalties,
        "total_rewards": total_rewards,
        "total_penalties": total_penalties,
        "net_reward": net_reward,
    }


def display_analysis(data, results, rewards):
    """Display comprehensive analysis results"""

    print(f"\n💰 PROFIT ANALYSIS:")
    print(f"  Total Stakes: £{results['total_stakes']:,.2f}")
    print(f"  Total Profit: £{results['total_profit']:,.2f}")
    print(f"  ROI: {results['roi']:.2f}%")
    print(f"  Win Rate: {results['win_rate']:.1f}%")
    print(f"  Winners: {results['total_winners']}/{results['total_bets']}")

    print(f"\n🎯 REWARD SIGNALS:")
    for reward_type, value in rewards["rewards"].items():
        print(f"  {reward_type.replace('_', ' ').title()}: {value:.2f}")

    print(f"\n⚠️ PENALTIES:")
    for penalty_type, value in rewards["penalties"].items():
        print(f"  {penalty_type.replace('_', ' ').title()}: {value:.2f}")

    print(f"\n📊 NET REWARD SCORE: {rewards['net_reward']:.2f}")

    # Strategy breakdown
    print(f"\n📈 STRATEGY PERFORMANCE:")
    df_results = pd.DataFrame(results["individual_results"])
    if not df_results.empty:
        strategy_stats = (
            df_results.groupby("strategy_type")
            .agg({"profit": ["sum", "mean", "count"], "stake": "sum", "won": "sum"})
            .round(2)
        )

        for strategy in strategy_stats.index:
            profit_sum = strategy_stats.loc[strategy, ("profit", "sum")]
            stake_sum = strategy_stats.loc[strategy, ("stake", "sum")]
            wins = strategy_stats.loc[strategy, ("won", "sum")]
            count = strategy_stats.loc[strategy, ("profit", "count")]

            roi = (profit_sum / stake_sum) * 100 if stake_sum > 0 else 0
            win_rate = (wins / count) * 100 if count > 0 else 0

            print(f"  {strategy.upper()}:")
            print(
                f"    Profit: £{profit_sum:.2f} | ROI: {roi:.1f}% | Win Rate: {win_rate:.1f}%"
            )

    # Performance grade
    grade = calculate_performance_grade(results, rewards)
    print(f"\n🏆 AI PERFORMANCE GRADE: {grade}")

    # Recommendations
    recommendations = get_recommendations(results, rewards)
    print(f"\n💡 KEY RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")


def calculate_performance_grade(results, rewards):
    """Calculate overall performance grade"""

    score = 0

    # ROI component (40% weight)
    roi = results["roi"]
    if roi > 20:
        score += 40
    elif roi > 10:
        score += 30
    elif roi > 0:
        score += 20
    elif roi > -10:
        score += 10

    # Win rate component (30% weight)
    win_rate = results["win_rate"]
    if win_rate > 40:
        score += 30
    elif win_rate > 25:
        score += 20
    elif win_rate > 15:
        score += 15
    elif win_rate > 10:
        score += 10

    # Reward signals (20% weight)
    net_reward = rewards["net_reward"]
    if net_reward > 100:
        score += 20
    elif net_reward > 50:
        score += 15
    elif net_reward > 0:
        score += 10
    elif net_reward > -50:
        score += 5

    # Risk management (10% weight)
    if results["total_stakes"] < 1000:  # Conservative staking
        score += 10
    elif results["total_stakes"] < 2000:
        score += 5

    # Grade assignment
    if score >= 85:
        return "A+ (EXCELLENT)"
    elif score >= 75:
        return "A (VERY GOOD)"
    elif score >= 65:
        return "B+ (GOOD)"
    elif score >= 55:
        return "B (AVERAGE)"
    elif score >= 45:
        return "C (BELOW AVERAGE)"
    else:
        return "D (POOR)"


def get_recommendations(results, rewards):
    """Get actionable recommendations"""

    recommendations = []

    roi = results["roi"]
    win_rate = results["win_rate"]
    net_reward = rewards["net_reward"]

    if roi > 15:
        recommendations.append("SCALE UP: Strong ROI - increase bankroll allocation")
    elif roi > 5:
        recommendations.append("CONTINUE: Positive returns - maintain current strategy")
    elif roi > -5:
        recommendations.append("OPTIMIZE: Minor tweaks needed for profitability")
    else:
        recommendations.append("REVIEW: Major strategy overhaul required")

    if win_rate < 20:
        recommendations.append("SELECTION: Improve horse selection criteria")

    if net_reward < 0:
        recommendations.append("RISK: Implement stricter risk management")

    if results["total_stakes"] > 2000:
        recommendations.append("STAKES: Consider reducing individual stake sizes")

    return recommendations


def save_analysis_results(data, results, rewards):
    """Save analysis results to file"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_strategies": len(data),
            "total_stakes": results["total_stakes"],
            "total_profit": results["total_profit"],
            "roi": results["roi"],
            "win_rate": results["win_rate"],
            "net_reward": rewards["net_reward"],
        },
        "detailed_results": results,
        "reward_analysis": rewards,
    }

    filename = f"ai_reward_analysis_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print(f"\n💾 Detailed analysis saved to: {filename}")


def main():
    """Run the AI reward analysis"""

    try:
        analyze_ai_performance()
        print("\n✅ AI Reward Analysis Complete!")
        print(
            "🎯 Use these insights to optimize the reward algorithm for maximum profit!"
        )

    except Exception as e:
        logger.error(f"Main analysis failed: {e}")
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main()
