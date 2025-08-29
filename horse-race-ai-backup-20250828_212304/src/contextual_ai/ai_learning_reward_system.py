#!/usr/bin/env python3
"""
AI Learning & Reward Optimization System
Implements advanced reward signals to train the AI for profit maximization
Enhanced with race quality and data quality analysis
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from typing import Dict, List, Tuple
from race_data_quality_analyzer import RaceDataQualityAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AILearningRewardSystem:
    """
    Advanced AI learning system that uses reward signals to optimize for profit.

    This system analyzes AI performance and provides detailed feedback to improve:
    - Selection accuracy
    - Value identification
    - Risk management
    - Stake optimization
    - Strategy refinement
    """

    def __init__(self, db_path: str = "ai_strategies_corrected.db"):
        self.db_path = db_path
        self.race_analyzer = RaceDataQualityAnalyzer(db_path)
        self.learning_metrics = {
            "profit_target": 200,  # £200 monthly profit target
            "roi_target": 15,  # 15% ROI target
            "win_rate_target": 30,  # 30% win rate target
            "max_drawdown": 500,  # Max £500 loss tolerance
        }

        self.reward_weights = {
            "profit_weight": 1.0,  # Direct profit reward
            "accuracy_weight": 0.8,  # Selection accuracy
            "value_weight": 1.2,  # Value betting skill
            "consistency_weight": 0.6,  # Prediction consistency
            "risk_weight": 0.9,  # Risk management
            "data_quality_weight": 0.7,  # Race quality adaptation
        }

        # Race quality thresholds for different strategies
        self.quality_thresholds = {
            "high_quality": 75,  # Races with score > 75
            "medium_quality": 50,  # Races with score 50-75
            "low_quality": 25,  # Races with score < 50
        }

    def analyze_and_learn(self) -> Dict:
        """Main analysis function that provides learning feedback"""

        logger.info("🧠 Starting AI Learning & Reward Analysis...")

        # Core performance analysis
        profit_analysis = self.analyze_profit_performance()
        selection_analysis = self.analyze_selection_accuracy()
        value_analysis = self.analyze_value_identification()
        risk_analysis = self.analyze_risk_management()

        # NEW: Race quality performance analysis
        quality_analysis = self._analyze_race_quality_performance()

        # Generate learning signals
        learning_signals = self._generate_learning_signals(
            profit_analysis,
            selection_analysis,
            value_analysis,
            risk_analysis,
            quality_analysis,
        )

        # Create improvement plan
        improvement_plan = self.create_improvement_plan(learning_signals)

        # Display comprehensive analysis
        self.display_learning_analysis(
            profit_analysis,
            selection_analysis,
            value_analysis,
            risk_analysis,
            quality_analysis,
            learning_signals,
            improvement_plan,
        )

        return {
            "profit_analysis": profit_analysis,
            "selection_analysis": selection_analysis,
            "value_analysis": value_analysis,
            "risk_analysis": risk_analysis,
            "quality_analysis": quality_analysis,
            "learning_signals": learning_signals,
            "improvement_plan": improvement_plan,
            "timestamp": datetime.now().isoformat(),
        }

    def _load_ai_performance(self) -> pd.DataFrame:
        """Load AI performance data"""

        conn = sqlite3.connect(self.db_path)

        query = """
        SELECT 
            p.predicted_probability,
            p.confidence_score,
            p.value_rating,
            p.form_score,
            p.pace_rating,
            p.class_rating,
            p.actual_result,
            s.strategy_type,
            s.bet_type,
            s.recommended_stake,
            s.recommended_odds,
            s.value_percentage,
            s.kelly_fraction,
            s.strategy_confidence,
            s.risk_rating,
            rp.odds_decimal as market_odds,
            rp.actual_finish_position,
            h.name as horse_name,
            h.rating as horse_rating,
            rc.race_name,
            rc.prize_money
        FROM ai_predictions p
        JOIN ai_betting_strategies s ON p.prediction_id = s.prediction_id
        JOIN race_participants rp ON p.participant_id = rp.participant_id
        JOIN horses h ON rp.horse_id = h.horse_id
        JOIN race_cards rc ON p.race_id = rc.race_id
        """

        data = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(f"Loaded {len(data)} AI performance records")
        return data

    def analyze_profit_performance(self) -> Dict:
        """Analyze profit and ROI performance"""

        performance_data = self._load_ai_performance()

        if performance_data.empty:
            return {"error": "No performance data available"}

        # Calculate total profit/loss
        total_stakes = performance_data["recommended_stake"].sum()
        winning_bets = performance_data[performance_data["actual_result"] == 1]
        losing_bets = performance_data[performance_data["actual_result"] == 0]

        total_winnings = (
            winning_bets["recommended_stake"] * (winning_bets["recommended_odds"] - 1)
        ).sum()
        total_losses = losing_bets["recommended_stake"].sum()

        net_profit = total_winnings - total_losses
        roi = (net_profit / total_stakes * 100) if total_stakes > 0 else 0

        # Profit gap from target
        profit_gap = max(0, self.learning_metrics["profit_target"] - net_profit)

        return {
            "total_stakes": round(total_stakes, 2),
            "total_winnings": round(total_winnings, 2),
            "total_losses": round(total_losses, 2),
            "net_profit": round(net_profit, 2),
            "roi": round(roi, 2),
            "profit_gap": round(profit_gap, 2),
            "win_count": len(winning_bets),
            "lose_count": len(losing_bets),
            "total_bets": len(performance_data),
        }

    def analyze_selection_accuracy(self) -> Dict:
        """Analyze selection accuracy and confidence"""

        performance_data = self._load_ai_performance()

        if performance_data.empty:
            return {"error": "No performance data available"}

        # Overall accuracy
        accuracy = performance_data["actual_result"].sum() / len(performance_data) * 100

        # High confidence accuracy (confidence > 0.8)
        high_conf = performance_data[performance_data["confidence_score"] > 0.8]
        high_confidence_accuracy = (
            (high_conf["actual_result"].sum() / len(high_conf) * 100)
            if len(high_conf) > 0
            else 0
        )

        # Accuracy gap from target
        accuracy_gap = max(0, self.learning_metrics["win_rate_target"] - accuracy)

        # Confidence analysis
        avg_confidence = performance_data["confidence_score"].mean()

        return {
            "accuracy": round(accuracy, 2),
            "high_confidence_accuracy": round(high_confidence_accuracy, 2),
            "accuracy_gap": round(accuracy_gap, 2),
            "avg_confidence": round(avg_confidence, 3),
            "high_confidence_bets": len(high_conf),
            "confidence_distribution": {
                "low": len(
                    performance_data[performance_data["confidence_score"] < 0.6]
                ),
                "medium": len(
                    performance_data[
                        (performance_data["confidence_score"] >= 0.6)
                        & (performance_data["confidence_score"] < 0.8)
                    ]
                ),
                "high": len(
                    performance_data[performance_data["confidence_score"] >= 0.8]
                ),
            },
        }

    def analyze_value_identification(self) -> Dict:
        """Analyze value betting identification skills"""

        conn = sqlite3.connect(self.db_path)

        # Get value betting strategies
        query = """
            SELECT abs.value_percentage, ap.actual_result, abs.recommended_stake
            FROM ai_betting_strategies abs
            JOIN ai_predictions ap ON abs.prediction_id = ap.prediction_id
            WHERE abs.strategy_type = 'value_bet' AND abs.value_percentage > 0
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return {
                "value_bets_count": 0,
                "value_success_rate": 0,
                "avg_value_percentage": 0,
                "value_profit": 0,
            }

        # Value betting success rate
        value_success_rate = df["actual_result"].sum() / len(df) * 100
        avg_value_percentage = df["value_percentage"].mean()

        # Value betting profit
        value_profit = 0
        for _, bet in df.iterrows():
            if bet["actual_result"] == 1:
                value_profit += bet["recommended_stake"] * (
                    bet["value_percentage"] / 100
                )
            else:
                value_profit -= bet["recommended_stake"]

        return {
            "value_bets_count": len(df),
            "value_success_rate": round(value_success_rate, 2),
            "avg_value_percentage": round(avg_value_percentage, 2),
            "value_profit": round(value_profit, 2),
        }

    def analyze_risk_management(self) -> Dict:
        """Analyze risk management performance"""

        performance_data = self._load_ai_performance()

        if performance_data.empty:
            return {"error": "No performance data available"}

        # Calculate consecutive losses
        consecutive_losses = 0
        max_consecutive_losses = 0
        current_losses = 0

        for result in performance_data["actual_result"]:
            if result == 0:  # Loss
                current_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
            else:
                current_losses = 0

        # Risk distribution
        stakes = performance_data["recommended_stake"]
        high_risk_bets = len(stakes[stakes > 30])  # Stakes > £30 considered high risk
        high_risk_percentage = (
            (high_risk_bets / len(stakes) * 100) if len(stakes) > 0 else 0
        )

        # Risk score (lower is better)
        risk_score = 100 - (max_consecutive_losses * 10) - (high_risk_percentage * 0.5)

        return {
            "max_consecutive_losses": max_consecutive_losses,
            "high_risk_percentage": round(high_risk_percentage, 2),
            "high_risk_bets": high_risk_bets,
            "avg_stake": round(stakes.mean(), 2),
            "max_stake": round(stakes.max(), 2),
            "risk_score": round(max(0, risk_score), 2),
        }

    def _analyze_confidence_calibration(self, conf_df: pd.DataFrame) -> Dict:
        """Analyze how well AI confidence matches actual results"""

        if conf_df.empty:
            return {"calibration_error": 100, "overconfidence": True}

        # Bin confidence levels
        conf_df["conf_bin"] = pd.cut(
            conf_df["confidence"],
            bins=[0, 0.3, 0.5, 0.7, 0.9, 1.0],
            labels=["Low", "Med-Low", "Medium", "Med-High", "High"],
        )

        calibration_data = (
            conf_df.groupby("conf_bin")["actual_result"].agg(["mean", "count"]).round(3)
        )

        # Calculate calibration error
        expected_rates = {
            "Low": 0.2,
            "Med-Low": 0.4,
            "Medium": 0.6,
            "Med-High": 0.8,
            "High": 0.9,
        }
        calibration_error = 0

        for bin_name, expected_rate in expected_rates.items():
            if bin_name in calibration_data.index:
                actual_rate = calibration_data.loc[bin_name, "mean"]
                calibration_error += abs(expected_rate - actual_rate)

        calibration_error = (calibration_error / len(expected_rates)) * 100

        return {
            "calibration_error": calibration_error,
            "calibration_data": calibration_data.to_dict(),
            "overconfidence": calibration_error > 20,
        }

    def _analyze_race_quality_performance(self) -> Dict:
        """Analyze AI performance across different race quality levels"""

        conn = sqlite3.connect(self.db_path)

        # Get AI predictions with race and result data
        query = """
            SELECT 
                ap.race_id,
                ap.predicted_probability,
                ap.confidence_score,
                ap.actual_result,
                abs.strategy_type,
                abs.recommended_stake,
                abs.recommended_odds,
                rc.race_type,
                h.age,
                h.career_runs
            FROM ai_predictions ap
            JOIN ai_betting_strategies abs ON ap.prediction_id = abs.prediction_id
            JOIN race_cards rc ON ap.race_id = rc.race_id
            JOIN race_participants rp ON ap.participant_id = rp.participant_id
            JOIN horses h ON rp.horse_id = h.horse_id
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return {"error": "No AI betting data found"}

        # Analyze race quality for each unique race
        race_quality_data = {}
        unique_races = df["race_id"].unique()

        logger.info(f"Analyzing race quality for {len(unique_races)} races...")

        for race_id in unique_races:
            try:
                quality_analysis = self.race_analyzer.analyze_race_quality(race_id)
                if "error" not in quality_analysis:
                    race_quality_data[race_id] = {
                        "quality_score": quality_analysis["overall_quality"],
                        "confidence": quality_analysis["prediction_confidence"],
                        "race_type": quality_analysis["race_type"],
                        "recommendations": quality_analysis["recommendations"],
                    }
            except Exception as e:
                logger.warning(f"Failed to analyze race {race_id}: {e}")

        # Categorize races by quality and analyze performance
        performance_by_quality = {
            "high_quality": {"bets": [], "profits": [], "accuracy": []},
            "medium_quality": {"bets": [], "profits": [], "accuracy": []},
            "low_quality": {"bets": [], "profits": [], "accuracy": []},
        }

        # Categorize each bet by race quality
        for _, bet in df.iterrows():
            race_id = bet["race_id"]
            if race_id not in race_quality_data:
                continue

            quality_score = race_quality_data[race_id]["quality_score"]

            # Determine quality category
            if quality_score >= self.quality_thresholds["high_quality"]:
                category = "high_quality"
            elif quality_score >= self.quality_thresholds["medium_quality"]:
                category = "medium_quality"
            else:
                category = "low_quality"

            # Calculate profit/loss
            stake = bet["recommended_stake"] or 0
            odds = bet["recommended_odds"] or 1

            if bet["actual_result"] == 1:  # Winner
                profit = stake * (odds - 1)
            else:
                profit = -stake

            performance_by_quality[category]["bets"].append(bet)
            performance_by_quality[category]["profits"].append(profit)
            performance_by_quality[category]["accuracy"].append(bet["actual_result"])

        # Calculate summary statistics
        quality_summary = {}
        for category, data in performance_by_quality.items():
            if data["bets"]:
                total_stakes = sum(
                    bet["recommended_stake"] or 0 for bet in data["bets"]
                )
                total_profit = sum(data["profits"])
                roi = (total_profit / total_stakes * 100) if total_stakes > 0 else 0
                accuracy = (
                    (sum(data["accuracy"]) / len(data["accuracy"]) * 100)
                    if data["accuracy"]
                    else 0
                )

                quality_summary[category] = {
                    "bet_count": len(data["bets"]),
                    "total_stakes": round(total_stakes, 2),
                    "total_profit": round(total_profit, 2),
                    "roi": round(roi, 2),
                    "accuracy": round(accuracy, 2),
                    "avg_stake": (
                        round(total_stakes / len(data["bets"]), 2)
                        if data["bets"]
                        else 0
                    ),
                }

        # Generate race quality insights
        insights = self._generate_race_quality_insights(
            quality_summary, race_quality_data
        )

        return {
            "quality_performance": quality_summary,
            "race_analysis_summary": {
                "total_races_analyzed": len(race_quality_data),
                "avg_quality_score": round(
                    np.mean([r["quality_score"] for r in race_quality_data.values()]), 2
                ),
                "quality_distribution": self._categorize_race_distribution(
                    race_quality_data
                ),
            },
            "insights": insights,
            "recommendations": self._generate_quality_based_recommendations(
                quality_summary
            ),
        }

    def _categorize_race_distribution(self, race_quality_data: Dict) -> Dict:
        """Categorize race distribution by quality"""
        distribution = {"high_quality": 0, "medium_quality": 0, "low_quality": 0}

        for race_data in race_quality_data.values():
            quality = race_data["quality_score"]
            if quality >= self.quality_thresholds["high_quality"]:
                distribution["high_quality"] += 1
            elif quality >= self.quality_thresholds["medium_quality"]:
                distribution["medium_quality"] += 1
            else:
                distribution["low_quality"] += 1

        return distribution

    def _generate_race_quality_insights(
        self, quality_summary: Dict, race_data: Dict
    ) -> List[str]:
        """Generate insights from race quality analysis"""
        insights = []

        # ROI comparison across quality levels
        high_roi = quality_summary.get("high_quality", {}).get("roi", 0)
        medium_roi = quality_summary.get("medium_quality", {}).get("roi", 0)
        low_roi = quality_summary.get("low_quality", {}).get("roi", 0)

        if high_roi > medium_roi > low_roi:
            insights.append(
                "✅ AI performs progressively better on higher quality races"
            )
        elif low_roi > high_roi:
            insights.append("⚠️ Unexpected: AI performing better on low-quality races")
            insights.append(
                "🔍 May indicate overconfidence on quality races or market inefficiencies"
            )

        # Accuracy insights
        high_acc = quality_summary.get("high_quality", {}).get("accuracy", 0)
        low_acc = quality_summary.get("low_quality", {}).get("accuracy", 0)

        if high_acc - low_acc > 10:
            insights.append(
                f"🎯 Significant accuracy improvement on quality races (+{high_acc-low_acc:.1f}%)"
            )
        elif abs(high_acc - low_acc) < 5:
            insights.append(
                "📊 Similar accuracy across race qualities - model may need refinement"
            )

        # Identify problematic race types
        race_types_low_quality = []
        for race_id, data in race_data.items():
            if data["quality_score"] < self.quality_thresholds["medium_quality"]:
                race_types_low_quality.append(data["race_type"])

        if race_types_low_quality:
            common_low_quality = max(
                set(race_types_low_quality), key=race_types_low_quality.count
            )
            insights.append(
                f"🚨 Most common low-quality race type: {common_low_quality}"
            )

        return insights

    def _generate_quality_based_recommendations(
        self, quality_summary: Dict
    ) -> List[str]:
        """Generate specific recommendations based on quality analysis"""
        recommendations = []

        # Stake size recommendations
        high_roi = quality_summary.get("high_quality", {}).get("roi", 0)
        low_roi = quality_summary.get("low_quality", {}).get("roi", 0)

        if high_roi > 10 and low_roi < -5:
            recommendations.append("💰 INCREASE stakes on high-quality races")
            recommendations.append("⚠️ REDUCE or AVOID low-quality races")

        # Filtering recommendations
        low_accuracy = quality_summary.get("low_quality", {}).get("accuracy", 0)
        if low_accuracy < 20:
            recommendations.append(
                "🚫 Implement strict filters to avoid low-quality races"
            )
            recommendations.append("📊 Focus model training on medium+ quality races")

        # Strategy recommendations
        high_count = quality_summary.get("high_quality", {}).get("bet_count", 0)
        total_bets = sum(cat.get("bet_count", 0) for cat in quality_summary.values())

        if high_count / total_bets < 0.3:
            recommendations.append("🔍 Seek more high-quality betting opportunities")
            recommendations.append("📈 Prioritize race selection over quantity")

        return recommendations

    def _generate_learning_signals(
        self,
        profit_analysis: Dict,
        selection_analysis: Dict,
        value_analysis: Dict,
        risk_analysis: Dict,
        quality_analysis: Dict,
    ) -> Dict:
        """Generate learning signals for AI improvement"""

        signals = {
            "profit_signals": {},
            "selection_signals": {},
            "value_signals": {},
            "risk_signals": {},
            "quality_signals": {},
            "overall_signals": {},
        }

        # Profit signals
        if profit_analysis["roi"] < 0:
            signals["profit_signals"]["negative_roi"] = abs(profit_analysis["roi"]) * -1
        else:
            signals["profit_signals"]["positive_roi"] = profit_analysis["roi"]

        if profit_analysis["profit_gap"] > 0:
            signals["profit_signals"]["profit_deficit"] = (
                profit_analysis["profit_gap"] * -0.1
            )

        # Selection signals
        if selection_analysis["accuracy"] < self.learning_metrics["win_rate_target"]:
            signals["selection_signals"]["low_accuracy"] = (
                selection_analysis["accuracy_gap"] * -0.5
            )
        else:
            signals["selection_signals"]["good_accuracy"] = (
                selection_analysis["accuracy"] * 0.3
            )

        # Value signals
        if value_analysis["value_success_rate"] < 30:
            signals["value_signals"]["poor_value_detection"] = -10
        else:
            signals["value_signals"]["good_value_detection"] = (
                value_analysis["value_success_rate"] * 0.2
            )

        # Risk signals
        if risk_analysis["max_consecutive_losses"] > 5:
            signals["risk_signals"]["high_consecutive_losses"] = -20

        if risk_analysis["high_risk_percentage"] > 30:
            signals["risk_signals"]["excessive_risk"] = -15

        # Quality signals (NEW)
        if "error" not in quality_analysis:
            quality_perf = quality_analysis.get("quality_performance", {})

            # Reward better performance on high-quality races
            high_quality_roi = quality_perf.get("high_quality", {}).get("roi", 0)
            if high_quality_roi > 15:
                signals["quality_signals"]["excellent_quality_performance"] = (
                    high_quality_roi * 0.5
                )
            elif high_quality_roi < -10:
                signals["quality_signals"]["poor_quality_performance"] = (
                    high_quality_roi * 0.3
                )

            # Penalize poor performance on low-quality races (should avoid these)
            low_quality_roi = quality_perf.get("low_quality", {}).get("roi", 0)
            if low_quality_roi < -15:
                signals["quality_signals"]["excessive_low_quality_losses"] = -25

            # Reward race selection wisdom
            high_quality_bets = quality_perf.get("high_quality", {}).get("bet_count", 0)
            total_bets = sum(cat.get("bet_count", 0) for cat in quality_perf.values())

            if total_bets > 0:
                quality_ratio = high_quality_bets / total_bets
                if quality_ratio > 0.5:  # More than 50% on quality races
                    signals["quality_signals"]["good_race_selection"] = 10
                elif quality_ratio < 0.2:  # Less than 20% on quality races
                    signals["quality_signals"]["poor_race_selection"] = -15

        # Overall performance signal (updated to include quality)
        quality_component = 0
        if "error" not in quality_analysis:
            quality_perf = quality_analysis.get("quality_performance", {})
            high_roi = quality_perf.get("high_quality", {}).get("roi", 0)
            quality_component = max(-20, min(20, high_roi * 0.5))

        overall_score = (
            profit_analysis["roi"] * 0.3
            + selection_analysis["accuracy"] * 0.25
            + value_analysis["value_success_rate"] * 0.2
            + risk_analysis["risk_score"] * 0.1
            + quality_component * 0.15
        )

        signals["overall_signals"]["performance_score"] = overall_score

        return signals

    def _calculate_reward_adjustments(self, learning_signals: Dict) -> Dict:
        """Calculate specific reward adjustments for AI learning"""

        adjustments = {
            "immediate_rewards": {},
            "learning_multipliers": {},
            "penalty_reductions": {},
            "bonus_opportunities": {},
        }

        # Immediate rewards based on current performance
        overall_score = learning_signals["overall_signals"].get("performance_score", 0)

        if overall_score > 50:
            adjustments["immediate_rewards"]["performance_bonus"] = overall_score * 2
        elif overall_score > 0:
            adjustments["immediate_rewards"]["progress_reward"] = overall_score
        else:
            adjustments["immediate_rewards"]["improvement_needed"] = overall_score * -1

        # Learning multipliers for different aspects
        adjustments["learning_multipliers"] = {
            "profit_focus": 2.0 if overall_score < 0 else 1.0,
            "accuracy_focus": (
                1.5
                if learning_signals["selection_signals"].get("low_accuracy", 0) < 0
                else 1.0
            ),
            "value_focus": (
                1.8
                if learning_signals["value_signals"].get("poor_value_detection", 0)
                else 1.0
            ),
            "risk_focus": (
                1.3
                if learning_signals["risk_signals"].get("excessive_risk", 0)
                else 1.0
            ),
        }

        return adjustments

    def create_improvement_plan(self, learning_signals: Dict) -> Dict:
        """Create specific improvement plan based on learning signals"""

        plan = {
            "immediate_actions": [],
            "training_priorities": [],
            "strategy_adjustments": [],
            "monitoring_targets": [],
        }

        # Analyze signals and create actionable plan
        profit_signals = learning_signals.get("profit_signals", {})
        selection_signals = learning_signals.get("selection_signals", {})
        quality_signals = learning_signals.get("quality_signals", {})

        # Profit-based actions
        if "negative_roi" in profit_signals:
            plan["immediate_actions"].append(
                "URGENT: Reduce stake sizes until profitability improves"
            )
            plan["training_priorities"].append(
                "Retrain prediction models with focus on accuracy"
            )

        if "profit_deficit" in profit_signals:
            plan["strategy_adjustments"].append(
                "Implement more conservative betting approach"
            )

        # Selection-based actions
        if "low_accuracy" in selection_signals:
            plan["training_priorities"].append("Focus on improving selection accuracy")
            plan["immediate_actions"].append("Filter out low-confidence predictions")

        # Quality-based actions
        if "poor_race_selection" in quality_signals:
            plan["immediate_actions"].append("Implement race quality filters")
            plan["strategy_adjustments"].append("Focus on high-quality races only")

        if "excellent_quality_performance" in quality_signals:
            plan["strategy_adjustments"].append("Increase stakes on high-quality races")

        # Monitoring targets
        plan["monitoring_targets"] = [
            f"Target ROI: {self.learning_metrics['roi_target']}%",
            f"Target Accuracy: {self.learning_metrics['win_rate_target']}%",
            f"Target Monthly Profit: £{self.learning_metrics['profit_target']}",
            "Maximum Drawdown: £500",
        ]

        return plan

    def display_learning_analysis(
        self,
        profit_analysis: Dict,
        selection_analysis: Dict,
        value_analysis: Dict,
        risk_analysis: Dict,
        quality_analysis: Dict,
        learning_signals: Dict,
        improvement_plan: Dict,
    ):
        """Display comprehensive learning analysis"""

        print("🤖 AI LEARNING & REWARD ANALYSIS")
        print("=" * 50)

        # Profit Analysis
        print("\n💰 PROFIT LEARNING ANALYSIS:")
        print(f"  Total P&L: £{profit_analysis['net_profit']}")
        print(
            f"  Current ROI: {profit_analysis['roi']:.2f}% (Target: {self.learning_metrics['roi_target']}%)"
        )
        print(f"  Profit Gap: £{profit_analysis['profit_gap']}")
        print(
            f"  Win Rate: {profit_analysis['win_count']}/{profit_analysis['total_bets']}"
        )

        # Selection Analysis
        print("\n🎯 SELECTION LEARNING ANALYSIS:")
        print(
            f"  Accuracy: {selection_analysis['accuracy']:.1f}% (Target: {self.learning_metrics['win_rate_target']}%)"
        )
        print(f"  Average Confidence: {selection_analysis['avg_confidence']:.3f}")
        print(
            f"  High Confidence Accuracy: {selection_analysis['high_confidence_accuracy']:.1f}%"
        )
        print(f"  High Confidence Bets: {selection_analysis['high_confidence_bets']}")

        # Value Analysis
        print("\n💎 VALUE IDENTIFICATION ANALYSIS:")
        print(f"  Value Bets: {value_analysis['value_bets_count']}")
        print(f"  Value Success Rate: {value_analysis['value_success_rate']:.1f}%")
        print(f"  Average Value: {value_analysis['avg_value_percentage']:.1f}%")

        # Risk Analysis
        print("\n⚠️ RISK MANAGEMENT ANALYSIS:")
        print(f"  Max Consecutive Losses: {risk_analysis['max_consecutive_losses']}")
        print(f"  High Risk Bets: {risk_analysis['high_risk_percentage']:.1f}%")
        print(f"  Risk Score: {risk_analysis['risk_score']:.1f}/100")

        # Quality Analysis
        if "error" not in quality_analysis:
            print("\n🏇 RACE QUALITY ANALYSIS:")
            quality_perf = quality_analysis.get("quality_performance", {})
            for quality_level, metrics in quality_perf.items():
                print(
                    f"  {quality_level.replace('_', ' ').title()}: ROI {metrics['roi']:.1f}%, "
                    f"Accuracy {metrics['accuracy']:.1f}%, Bets {metrics['bet_count']}"
                )

        # Learning Signals
        print("\n🧠 LEARNING SIGNALS:")
        for category, signals in learning_signals.items():
            if signals:
                print(f"  {category.replace('_', ' ').title()}: {list(signals.keys())}")

        # Improvement Plan
        print("\n📋 IMPROVEMENT PLAN:")
        for action in improvement_plan["immediate_actions"]:
            print(f"  🚨 IMMEDIATE: {action}")
        for priority in improvement_plan["training_priorities"]:
            print(f"  🎯 TRAINING: {priority}")
        for adjustment in improvement_plan["strategy_adjustments"]:
            print(f"  ⚙️ STRATEGY: {adjustment}")

    def _save_learning_results(self, results: Dict):
        """Save learning results for future reference"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_learning_analysis_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Learning analysis saved to: {filename}")


def main():
    """Run the AI learning and reward optimization"""

    try:
        system = AILearningRewardSystem()
        results = system.analyze_and_learn()

        print(f"\n✅ AI Learning Analysis Complete!")
        print(
            f"🎯 The AI now has detailed feedback to improve its money-making ability!"
        )
        print(f"🔄 Use these learning signals to retrain and optimize the models!")

    except Exception as e:
        logger.error(f"Learning analysis failed: {e}")
        print(f"❌ Learning analysis failed: {e}")


if __name__ == "__main__":
    main()
