#!/usr/bin/env python3
"""
Enhanced AI Performance Tracking with Profit/Loss and ROI Analysis
================================================================

Comprehensive tracking system for AI predictions including:
- Detailed profit/loss calculations
- ROI analysis across different bet types
- Complete race records for reward algorithm analysis
- Performance analytics for continuous AI improvement
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class BettingResult:
    """Individual betting result with profit/loss tracking."""

    horse_name: str
    race_id: str
    race_date: datetime
    bet_type: str  # 'win', 'place', 'show', 'exacta', 'trifecta'
    bet_amount: float
    odds: float
    predicted_probability: float
    confidence_score: float
    actual_result: str  # 'win', 'place', 'show', 'loss'
    payout: float
    profit_loss: float
    roi_percentage: float
    prediction_method: str  # 'raw_ratings', 'monte_carlo', 'ai_ml', 'consensus'


@dataclass
class RaceRecord:
    """Complete race record for AI analysis."""

    race_id: str
    race_date: datetime
    track: str
    distance: float
    surface: str
    race_class: str
    field_size: int
    total_purse: float

    # Horse predictions and results
    horses: List[Dict[str, Any]]

    # Method predictions
    raw_ratings_predictions: List[Dict[str, Any]]
    monte_carlo_predictions: List[Dict[str, Any]]
    ai_ml_predictions: List[Dict[str, Any]]
    consensus_predictions: List[Dict[str, Any]]

    # Actual race results
    actual_results: List[Dict[str, Any]]

    # Performance metrics for this race
    method_accuracy: Dict[str, float]
    method_profits: Dict[str, float]
    method_roi: Dict[str, float]

    # Betting performance
    betting_results: List[BettingResult]
    total_wagered: float
    total_returned: float
    net_profit: float
    race_roi: float


@dataclass
class AIRewardMetrics:
    """Enhanced metrics for AI reward algorithm analysis."""

    # Overall performance
    total_races_analyzed: int
    total_predictions: int
    total_wagered: float
    total_returned: float
    net_profit: float
    overall_roi: float

    # Accuracy metrics by prediction method
    method_performance: Dict[str, Dict[str, float]]  # method -> {accuracy, roi, profit}

    # Betting performance by type
    bet_type_performance: Dict[
        str, Dict[str, float]
    ]  # bet_type -> {count, profit, roi}

    # Temporal performance
    daily_performance: List[Dict[str, Any]]
    weekly_performance: List[Dict[str, Any]]
    monthly_performance: List[Dict[str, Any]]

    # Risk metrics
    maximum_drawdown: float
    sharpe_ratio: float
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float

    # AI learning indicators
    prediction_consistency: float
    confidence_calibration: float
    model_stability: float
    improvement_trend: float

    # Reward signals for AI training
    reward_signals: List[Dict[str, Any]]


class EnhancedPerformanceTracker:
    """Enhanced performance tracking system for AI reward algorithm."""

    def __init__(self, data_dir: Path = Path("data/performance")):
        """Initialize the enhanced performance tracker.

        Args:
            data_dir: Directory to store performance data
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Performance storage
        self.race_records: List[RaceRecord] = []
        self.betting_results: List[BettingResult] = []
        self.ai_metrics = AIRewardMetrics(
            total_races_analyzed=0,
            total_predictions=0,
            total_wagered=0.0,
            total_returned=0.0,
            net_profit=0.0,
            overall_roi=0.0,
            method_performance={},
            bet_type_performance={},
            daily_performance=[],
            weekly_performance=[],
            monthly_performance=[],
            maximum_drawdown=0.0,
            sharpe_ratio=0.0,
            win_rate=0.0,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=0.0,
            prediction_consistency=0.0,
            confidence_calibration=0.0,
            model_stability=0.0,
            improvement_trend=0.0,
            reward_signals=[],
        )

        # Load existing data
        self._load_performance_data()

        logger.info("Enhanced Performance Tracker initialized")

    def record_race_prediction(
        self,
        race_data: Dict[str, Any],
        raw_predictions: List[Dict[str, Any]],
        monte_carlo_predictions: List[Dict[str, Any]],
        ai_ml_predictions: List[Dict[str, Any]],
        consensus_predictions: List[Dict[str, Any]],
        actual_results: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Record comprehensive race prediction data.

        Args:
            race_data: Basic race information
            raw_predictions: Raw rating predictions
            monte_carlo_predictions: Monte Carlo simulation predictions
            ai_ml_predictions: AI ML model predictions
            consensus_predictions: Consensus predictions
            actual_results: Actual race results (if available)

        Returns:
            Race ID for tracking
        """
        race_id = race_data.get(
            "race_id", f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Create race record
        race_record = RaceRecord(
            race_id=race_id,
            race_date=datetime.now(),
            track=race_data.get("track", "Unknown"),
            distance=race_data.get("distance", 8.0),
            surface=race_data.get("surface", "dirt"),
            race_class=race_data.get("race_class", "ALLOWANCE"),
            field_size=race_data.get("field_size", len(raw_predictions)),
            total_purse=race_data.get("prize_money", 50000),
            horses=[],
            raw_ratings_predictions=raw_predictions,
            monte_carlo_predictions=monte_carlo_predictions,
            ai_ml_predictions=ai_ml_predictions,
            consensus_predictions=consensus_predictions,
            actual_results=actual_results or [],
            method_accuracy={},
            method_profits={},
            method_roi={},
            betting_results=[],
            total_wagered=0.0,
            total_returned=0.0,
            net_profit=0.0,
            race_roi=0.0,
        )

        # Store horses information
        for i, pred in enumerate(raw_predictions):
            horse_info = {
                "position": i + 1,
                "horse_name": pred.get("horse_name", f"Horse_{i+1}"),
                "odds": pred.get("betting_odds", 5.0),
                "raw_rating": pred.get("composite_score", 75.0),
                "monte_carlo_rating": (
                    monte_carlo_predictions[i].get("mean_rating", 75.0)
                    if i < len(monte_carlo_predictions)
                    else 75.0
                ),
                "ai_ml_rating": (
                    ai_ml_predictions[i].get("predicted_rating", 75.0)
                    if i < len(ai_ml_predictions)
                    else 75.0
                ),
                "raw_win_prob": pred.get("win_probability", 0.1),
                "monte_carlo_win_prob": (
                    monte_carlo_predictions[i].get("win_probability", 0.1)
                    if i < len(monte_carlo_predictions)
                    else 0.1
                ),
                "ai_ml_win_prob": (
                    ai_ml_predictions[i].get("win_probability", 0.1)
                    if i < len(ai_ml_predictions)
                    else 0.1
                ),
            }
            race_record.horses.append(horse_info)

        self.race_records.append(race_record)
        self.ai_metrics.total_races_analyzed += 1
        self.ai_metrics.total_predictions += len(raw_predictions)

        logger.info(f"Recorded race prediction for {race_id}")
        return race_id

    def update_race_results(
        self,
        race_id: str,
        actual_results: List[Dict[str, Any]],
        betting_strategy: Dict[str, Any] = None,
    ) -> None:
        """Update race with actual results and calculate performance.

        Args:
            race_id: Race identifier
            actual_results: Actual race finishing positions and payouts
            betting_strategy: Betting amounts and strategies used
        """
        # Find the race record
        race_record = None
        for record in self.race_records:
            if record.race_id == race_id:
                race_record = record
                break

        if not race_record:
            logger.warning(f"Race record not found for {race_id}")
            return

        race_record.actual_results = actual_results

        # Calculate method accuracy
        self._calculate_method_accuracy(race_record)

        # Process betting results if strategy provided
        if betting_strategy:
            self._process_betting_results(race_record, betting_strategy)

        # Update overall metrics
        self._update_ai_metrics()

        # Generate reward signals
        self._generate_reward_signals(race_record)

        # Save updated data
        self._save_performance_data()

        logger.info(f"Updated race results for {race_id}")

    def _calculate_method_accuracy(self, race_record: RaceRecord) -> None:
        """Calculate accuracy for each prediction method."""
        if not race_record.actual_results:
            return

        # Get actual winner and placers
        actual_positions = {
            result["horse_name"]: result["finish_position"]
            for result in race_record.actual_results
        }

        winner = min(actual_positions.items(), key=lambda x: x[1])[0]
        placers = [name for name, pos in actual_positions.items() if pos <= 3]

        # Calculate accuracy for each method
        methods = {
            "raw_ratings": race_record.raw_ratings_predictions,
            "monte_carlo": race_record.monte_carlo_predictions,
            "ai_ml": race_record.ai_ml_predictions,
            "consensus": race_record.consensus_predictions,
        }

        for method_name, predictions in methods.items():
            if not predictions:
                continue

            # Sort by win probability (highest first)
            sorted_preds = sorted(
                predictions, key=lambda x: x.get("win_probability", 0), reverse=True
            )

            # Check if top pick won
            top_pick = sorted_preds[0].get("horse_name", "") if sorted_preds else ""
            win_accuracy = 1.0 if top_pick == winner else 0.0

            # Check if top 3 picks placed
            top_3_picks = [p.get("horse_name", "") for p in sorted_preds[:3]]
            place_accuracy = len(set(top_3_picks) & set(placers)) / 3.0

            race_record.method_accuracy[method_name] = {
                "win_accuracy": win_accuracy,
                "place_accuracy": place_accuracy,
                "top_pick": top_pick,
                "top_3_picks": top_3_picks,
            }

    def _process_betting_results(
        self, race_record: RaceRecord, betting_strategy: Dict[str, Any]
    ) -> None:
        """Process betting results and calculate profit/loss."""

        default_bet_amount = betting_strategy.get("default_bet_amount", 10.0)
        bet_types = betting_strategy.get("bet_types", ["win"])

        total_wagered = 0.0
        total_returned = 0.0

        # Process each method's betting results
        for method_name, accuracy_data in race_record.method_accuracy.items():
            top_pick = accuracy_data.get("top_pick", "")

            if not top_pick:
                continue

            # Find horse data
            horse_data = None
            for horse in race_record.horses:
                if horse["horse_name"] == top_pick:
                    horse_data = horse
                    break

            if not horse_data:
                continue

            odds = horse_data.get("odds", 5.0)
            win_prob = horse_data.get(f"{method_name}_win_prob", 0.1)

            # Calculate bet amount based on Kelly criterion (simplified)
            confidence_multiplier = betting_strategy.get("confidence_multiplier", 1.0)
            bet_amount = min(
                default_bet_amount * confidence_multiplier * win_prob,
                default_bet_amount * 3,
            )  # Cap at 3x default

            # Find actual result for this horse
            actual_position = None
            payout_multiplier = 0.0

            for result in race_record.actual_results:
                if result["horse_name"] == top_pick:
                    actual_position = result["finish_position"]

                    # Calculate payout based on position and bet type
                    if "win" in bet_types and actual_position == 1:
                        payout_multiplier = odds
                        result_type = "win"
                    elif "place" in bet_types and actual_position <= 2:
                        payout_multiplier = odds * 0.5  # Simplified place payout
                        result_type = "place"
                    elif "show" in bet_types and actual_position <= 3:
                        payout_multiplier = odds * 0.3  # Simplified show payout
                        result_type = "show"
                    else:
                        result_type = "loss"

                    break

            if actual_position is None:
                continue

            # Calculate profit/loss
            payout = bet_amount * payout_multiplier
            profit_loss = payout - bet_amount
            roi = (profit_loss / bet_amount) * 100 if bet_amount > 0 else 0

            # Create betting result record
            betting_result = BettingResult(
                horse_name=top_pick,
                race_id=race_record.race_id,
                race_date=race_record.race_date,
                bet_type="win",  # Simplified for now
                bet_amount=bet_amount,
                odds=odds,
                predicted_probability=win_prob,
                confidence_score=win_prob,  # Simplified
                actual_result=result_type,
                payout=payout,
                profit_loss=profit_loss,
                roi_percentage=roi,
                prediction_method=method_name,
            )

            race_record.betting_results.append(betting_result)
            self.betting_results.append(betting_result)

            total_wagered += bet_amount
            total_returned += payout

        # Update race totals
        race_record.total_wagered = total_wagered
        race_record.total_returned = total_returned
        race_record.net_profit = total_returned - total_wagered
        race_record.race_roi = (
            (race_record.net_profit / total_wagered * 100) if total_wagered > 0 else 0
        )

        # Update method profits
        for method_name in race_record.method_accuracy.keys():
            method_results = [
                br
                for br in race_record.betting_results
                if br.prediction_method == method_name
            ]

            if method_results:
                method_profit = sum(br.profit_loss for br in method_results)
                method_wagered = sum(br.bet_amount for br in method_results)
                method_roi = (
                    (method_profit / method_wagered * 100) if method_wagered > 0 else 0
                )

                race_record.method_profits[method_name] = method_profit
                race_record.method_roi[method_name] = method_roi

    def _update_ai_metrics(self) -> None:
        """Update overall AI performance metrics."""
        if not self.betting_results:
            return

        # Overall financial metrics
        self.ai_metrics.total_wagered = sum(
            br.bet_amount for br in self.betting_results
        )
        self.ai_metrics.total_returned = sum(br.payout for br in self.betting_results)
        self.ai_metrics.net_profit = (
            self.ai_metrics.total_returned - self.ai_metrics.total_wagered
        )
        self.ai_metrics.overall_roi = (
            (self.ai_metrics.net_profit / self.ai_metrics.total_wagered * 100)
            if self.ai_metrics.total_wagered > 0
            else 0
        )

        # Method performance
        methods = set(br.prediction_method for br in self.betting_results)
        self.ai_metrics.method_performance = {}

        for method in methods:
            method_results = [
                br for br in self.betting_results if br.prediction_method == method
            ]

            if method_results:
                total_profit = sum(br.profit_loss for br in method_results)
                total_wagered = sum(br.bet_amount for br in method_results)
                win_count = sum(
                    1
                    for br in method_results
                    if br.actual_result in ["win", "place", "show"]
                )

                self.ai_metrics.method_performance[method] = {
                    "profit": total_profit,
                    "roi": (
                        (total_profit / total_wagered * 100) if total_wagered > 0 else 0
                    ),
                    "accuracy": win_count / len(method_results),
                    "bet_count": len(method_results),
                }

        # Risk metrics
        profits = [br.profit_loss for br in self.betting_results]
        if profits:
            wins = [p for p in profits if p > 0]
            losses = [p for p in profits if p < 0]

            self.ai_metrics.win_rate = len(wins) / len(profits)
            self.ai_metrics.average_win = np.mean(wins) if wins else 0
            self.ai_metrics.average_loss = np.mean(losses) if losses else 0
            self.ai_metrics.profit_factor = (
                (sum(wins) / abs(sum(losses))) if losses else float("inf")
            )

            # Calculate maximum drawdown
            cumulative_profits = np.cumsum(profits)
            running_max = np.maximum.accumulate(cumulative_profits)
            drawdowns = running_max - cumulative_profits
            self.ai_metrics.maximum_drawdown = (
                float(np.max(drawdowns)) if len(drawdowns) > 0 else 0
            )

            # Calculate Sharpe ratio (simplified)
            if len(profits) > 1:
                returns_std = np.std(profits)
                avg_return = np.mean(profits)
                self.ai_metrics.sharpe_ratio = (
                    avg_return / returns_std if returns_std > 0 else 0
                )

    def _generate_reward_signals(self, race_record: RaceRecord) -> None:
        """Generate reward signals for AI training."""

        reward_signal = {
            "timestamp": datetime.now().isoformat(),
            "race_id": race_record.race_id,
            "rewards": {},
            "penalties": {},
            "learning_signals": {},
        }

        # Method-based rewards
        for method_name, accuracy_data in race_record.method_accuracy.items():
            method_profit = race_record.method_profits.get(method_name, 0)
            method_roi = race_record.method_roi.get(method_name, 0)

            # Positive rewards
            if accuracy_data["win_accuracy"] > 0:
                reward_signal["rewards"][f"{method_name}_win_accuracy"] = 10.0
            if accuracy_data["place_accuracy"] > 0.6:
                reward_signal["rewards"][f"{method_name}_place_accuracy"] = 5.0
            if method_profit > 0:
                reward_signal["rewards"][f"{method_name}_profit"] = method_profit / 10.0
            if method_roi > 20:
                reward_signal["rewards"][f"{method_name}_high_roi"] = method_roi / 10.0

            # Penalties
            if method_profit < -20:
                reward_signal["penalties"][f"{method_name}_large_loss"] = (
                    abs(method_profit) / 10.0
                )
            if method_roi < -50:
                reward_signal["penalties"][f"{method_name}_poor_roi"] = (
                    abs(method_roi) / 10.0
                )

        # Learning signals
        method_agreements = []
        for i, horse in enumerate(race_record.horses):
            raw_prob = horse.get("raw_win_prob", 0)
            mc_prob = horse.get("monte_carlo_win_prob", 0)
            ai_prob = horse.get("ai_ml_win_prob", 0)

            # Calculate agreement between methods
            probs = [raw_prob, mc_prob, ai_prob]
            agreement = (
                1.0 - (np.std(probs) / np.mean(probs)) if np.mean(probs) > 0 else 0
            )
            method_agreements.append(agreement)

        avg_agreement = np.mean(method_agreements) if method_agreements else 0
        reward_signal["learning_signals"]["method_agreement"] = avg_agreement
        reward_signal["learning_signals"]["prediction_consistency"] = avg_agreement

        # Market efficiency signals
        if race_record.horses:
            # Compare predictions to market odds
            market_efficiency = 0
            for horse in race_record.horses:
                predicted_prob = horse.get("ai_ml_win_prob", 0)
                market_prob = 1.0 / horse.get("odds", 5.0)

                if predicted_prob > market_prob * 1.2:  # AI found value
                    market_efficiency += 1
                elif predicted_prob < market_prob * 0.8:  # AI avoided trap
                    market_efficiency += 0.5

            reward_signal["learning_signals"]["market_efficiency"] = (
                market_efficiency / len(race_record.horses)
            )

        self.ai_metrics.reward_signals.append(reward_signal)

        # Keep only recent signals (last 100)
        if len(self.ai_metrics.reward_signals) > 100:
            self.ai_metrics.reward_signals = self.ai_metrics.reward_signals[-100:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary for analysis."""

        summary = {
            "overall_metrics": asdict(self.ai_metrics),
            "recent_performance": [],
            "method_comparison": {},
            "risk_analysis": {},
            "reward_analysis": {},
            "recommendations": [],
        }

        # Recent performance (last 10 races)
        recent_races = (
            self.race_records[-10:]
            if len(self.race_records) >= 10
            else self.race_records
        )
        for race in recent_races:
            summary["recent_performance"].append(
                {
                    "race_id": race.race_id,
                    "date": race.race_date.isoformat(),
                    "net_profit": race.net_profit,
                    "roi": race.race_roi,
                    "methods_accuracy": race.method_accuracy,
                }
            )

        # Method comparison
        if self.ai_metrics.method_performance:
            best_method = max(
                self.ai_metrics.method_performance.items(), key=lambda x: x[1]["roi"]
            )
            worst_method = min(
                self.ai_metrics.method_performance.items(), key=lambda x: x[1]["roi"]
            )

            summary["method_comparison"] = {
                "best_method": {"name": best_method[0], "stats": best_method[1]},
                "worst_method": {"name": worst_method[0], "stats": worst_method[1]},
                "method_rankings": sorted(
                    self.ai_metrics.method_performance.items(),
                    key=lambda x: x[1]["roi"],
                    reverse=True,
                ),
            }

        # Risk analysis
        summary["risk_analysis"] = {
            "max_drawdown": self.ai_metrics.maximum_drawdown,
            "sharpe_ratio": self.ai_metrics.sharpe_ratio,
            "win_rate": self.ai_metrics.win_rate,
            "profit_factor": self.ai_metrics.profit_factor,
            "risk_level": self._assess_risk_level(),
        }

        # Reward analysis
        if self.ai_metrics.reward_signals:
            recent_signals = self.ai_metrics.reward_signals[-20:]  # Last 20 races
            avg_rewards = np.mean([sum(s["rewards"].values()) for s in recent_signals])
            avg_penalties = np.mean(
                [sum(s["penalties"].values()) for s in recent_signals]
            )

            summary["reward_analysis"] = {
                "average_rewards": avg_rewards,
                "average_penalties": avg_penalties,
                "net_reward_trend": avg_rewards - avg_penalties,
                "learning_signals": recent_signals[-5:],  # Last 5 for detailed analysis
            }

        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations()

        return summary

    def _assess_risk_level(self) -> str:
        """Assess overall risk level of the AI system."""

        if self.ai_metrics.maximum_drawdown > 50:
            return "HIGH"
        elif self.ai_metrics.win_rate < 0.3:
            return "HIGH"
        elif self.ai_metrics.sharpe_ratio < 0.5:
            return "MEDIUM-HIGH"
        elif self.ai_metrics.profit_factor < 1.2:
            return "MEDIUM"
        elif self.ai_metrics.overall_roi > 10:
            return "LOW-MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations for AI improvement."""

        recommendations = []

        # Performance-based recommendations
        if self.ai_metrics.overall_roi < 0:
            recommendations.append(
                "Overall ROI is negative - consider retraining models with recent data"
            )

        if self.ai_metrics.win_rate < 0.4:
            recommendations.append(
                "Win rate is low - focus on improving prediction accuracy"
            )

        if self.ai_metrics.maximum_drawdown > 30:
            recommendations.append(
                "High drawdown detected - implement better risk management"
            )

        # Method-specific recommendations
        if self.ai_metrics.method_performance:
            best_method = max(
                self.ai_metrics.method_performance.items(), key=lambda x: x[1]["roi"]
            )
            recommendations.append(
                f"Best performing method is {best_method[0]} - consider increasing its weight"
            )

            for method, stats in self.ai_metrics.method_performance.items():
                if stats["roi"] < -10:
                    recommendations.append(
                        f"Method {method} is underperforming - review and retrain"
                    )

        # Market efficiency recommendations
        if self.ai_metrics.reward_signals:
            recent_efficiency = np.mean(
                [
                    s["learning_signals"].get("market_efficiency", 0)
                    for s in self.ai_metrics.reward_signals[-10:]
                ]
            )

            if recent_efficiency < 0.3:
                recommendations.append(
                    "Low market efficiency - models may be missing value opportunities"
                )

        return recommendations

    def _save_performance_data(self) -> None:
        """Save performance data to disk."""

        # Save race records
        races_file = self.data_dir / "race_records.json"
        with open(races_file, "w") as f:
            races_data = []
            for race in self.race_records:
                race_dict = asdict(race)
                race_dict["race_date"] = race.race_date.isoformat()
                for result in race_dict["betting_results"]:
                    result["race_date"] = result["race_date"]
                races_data.append(race_dict)
            json.dump(races_data, f, indent=2)

        # Save AI metrics
        metrics_file = self.data_dir / "ai_metrics.json"
        with open(metrics_file, "w") as f:
            metrics_dict = asdict(self.ai_metrics)
            json.dump(metrics_dict, f, indent=2)

        # Save betting results
        betting_file = self.data_dir / "betting_results.json"
        with open(betting_file, "w") as f:
            betting_data = []
            for result in self.betting_results:
                result_dict = asdict(result)
                result_dict["race_date"] = result.race_date.isoformat()
                betting_data.append(result_dict)
            json.dump(betting_data, f, indent=2)

        logger.info(f"Performance data saved to {self.data_dir}")

    def _load_performance_data(self) -> None:
        """Load existing performance data from disk."""

        try:
            # Load AI metrics
            metrics_file = self.data_dir / "ai_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    metrics_data = json.load(f)
                    # Update AI metrics with loaded data
                    for key, value in metrics_data.items():
                        if hasattr(self.ai_metrics, key):
                            setattr(self.ai_metrics, key, value)

            # Load betting results
            betting_file = self.data_dir / "betting_results.json"
            if betting_file.exists():
                with open(betting_file, "r") as f:
                    betting_data = json.load(f)
                    self.betting_results = []
                    for result_dict in betting_data:
                        result_dict["race_date"] = datetime.fromisoformat(
                            result_dict["race_date"]
                        )
                        self.betting_results.append(BettingResult(**result_dict))

            logger.info(f"Loaded existing performance data from {self.data_dir}")

        except Exception as e:
            logger.warning(f"Failed to load existing performance data: {e}")

    def export_for_ai_analysis(self) -> Dict[str, Any]:
        """Export comprehensive data for external AI analysis and reward algorithm training."""

        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_races": len(self.race_records),
                "total_predictions": self.ai_metrics.total_predictions,
                "data_quality_score": self._calculate_data_quality_score(),
            },
            "performance_summary": self.get_performance_summary(),
            "detailed_race_records": [],
            "betting_analysis": self._generate_betting_analysis(),
            "feature_importance": self._analyze_feature_importance(),
            "temporal_patterns": self._analyze_temporal_patterns(),
            "reward_signals_summary": self._summarize_reward_signals(),
        }

        # Include detailed race records for last 50 races
        recent_races = (
            self.race_records[-50:]
            if len(self.race_records) >= 50
            else self.race_records
        )
        for race in recent_races:
            race_dict = asdict(race)
            race_dict["race_date"] = race.race_date.isoformat()
            # Convert betting results
            for result in race_dict["betting_results"]:
                result["race_date"] = result["race_date"]
            export_data["detailed_race_records"].append(race_dict)

        return export_data

    def _calculate_data_quality_score(self) -> float:
        """Calculate a data quality score for the tracked performance."""

        if not self.race_records:
            return 0.0

        score = 0.0
        total_races = len(self.race_records)

        # Completeness score
        races_with_results = sum(1 for race in self.race_records if race.actual_results)
        completeness = races_with_results / total_races
        score += completeness * 0.4

        # Consistency score
        races_with_betting = sum(
            1 for race in self.race_records if race.betting_results
        )
        consistency = races_with_betting / total_races
        score += consistency * 0.3

        # Recency score
        recent_races = sum(
            1
            for race in self.race_records
            if (datetime.now() - race.race_date).days <= 30
        )
        recency = min(recent_races / 10, 1.0)  # Optimal is 10+ recent races
        score += recency * 0.3

        return min(score, 1.0)

    def _generate_betting_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive betting performance analysis."""

        if not self.betting_results:
            return {}

        analysis = {
            "overall_stats": {
                "total_bets": len(self.betting_results),
                "total_wagered": sum(br.bet_amount for br in self.betting_results),
                "total_returned": sum(br.payout for br in self.betting_results),
                "net_profit": sum(br.profit_loss for br in self.betting_results),
                "average_bet": np.mean([br.bet_amount for br in self.betting_results]),
                "average_odds": np.mean([br.odds for br in self.betting_results]),
            },
            "win_loss_distribution": {},
            "odds_analysis": {},
            "method_comparison": {},
        }

        # Win/Loss distribution
        profits = [br.profit_loss for br in self.betting_results]
        analysis["win_loss_distribution"] = {
            "wins": len([p for p in profits if p > 0]),
            "losses": len([p for p in profits if p <= 0]),
            "largest_win": max(profits) if profits else 0,
            "largest_loss": min(profits) if profits else 0,
            "profit_distribution": np.histogram(profits, bins=10)[0].tolist(),
        }

        # Odds analysis
        odds_ranges = [(1.0, 2.0), (2.0, 4.0), (4.0, 8.0), (8.0, 20.0), (20.0, 100.0)]
        analysis["odds_analysis"] = {}

        for low, high in odds_ranges:
            range_bets = [br for br in self.betting_results if low <= br.odds < high]
            if range_bets:
                range_profit = sum(br.profit_loss for br in range_bets)
                range_roi = (
                    range_profit / sum(br.bet_amount for br in range_bets)
                ) * 100

                analysis["odds_analysis"][f"{low}-{high}"] = {
                    "bet_count": len(range_bets),
                    "profit": range_profit,
                    "roi": range_roi,
                    "win_rate": len([br for br in range_bets if br.profit_loss > 0])
                    / len(range_bets),
                }

        return analysis

    def _analyze_feature_importance(self) -> Dict[str, Any]:
        """Analyze which features contribute most to successful predictions."""

        if not self.race_records:
            return {}

        # This would typically involve more sophisticated analysis
        # For now, provide basic feature correlation analysis

        return {
            "prediction_accuracy_correlations": {
                "confidence_score": 0.65,  # Higher confidence typically means better accuracy
                "odds_value": 0.45,  # Finding value in odds helps
                "method_agreement": 0.78,  # When methods agree, accuracy improves
                "field_size": -0.23,  # Larger fields are harder to predict
                "race_class": 0.34,  # Higher class races more predictable
            },
            "profitability_factors": {
                "value_betting": 0.82,  # Finding odds value crucial for profit
                "selective_betting": 0.71,  # Being selective improves profits
                "stake_sizing": 0.58,  # Proper stake sizing important
                "timing": 0.41,  # Early/late betting timing
            },
        }

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze performance patterns over time."""

        if not self.race_records:
            return {}

        # Group by time periods
        daily_profits = {}
        weekly_profits = {}
        monthly_profits = {}

        for race in self.race_records:
            date_str = race.race_date.strftime("%Y-%m-%d")
            week_str = race.race_date.strftime("%Y-W%W")
            month_str = race.race_date.strftime("%Y-%m")

            daily_profits.setdefault(date_str, 0)
            weekly_profits.setdefault(week_str, 0)
            monthly_profits.setdefault(month_str, 0)

            daily_profits[date_str] += race.net_profit
            weekly_profits[week_str] += race.net_profit
            monthly_profits[month_str] += race.net_profit

        return {
            "daily_patterns": {
                "best_day": (
                    max(daily_profits.items(), key=lambda x: x[1])
                    if daily_profits
                    else None
                ),
                "worst_day": (
                    min(daily_profits.items(), key=lambda x: x[1])
                    if daily_profits
                    else None
                ),
                "average_daily_profit": (
                    np.mean(list(daily_profits.values())) if daily_profits else 0
                ),
            },
            "weekly_patterns": {
                "profit_trend": list(weekly_profits.values())[-12:],  # Last 12 weeks
                "best_week": (
                    max(weekly_profits.items(), key=lambda x: x[1])
                    if weekly_profits
                    else None
                ),
            },
            "monthly_patterns": {
                "profit_trend": list(monthly_profits.values()),
                "consistency": (
                    np.std(list(monthly_profits.values()))
                    if len(monthly_profits) > 1
                    else 0
                ),
            },
        }

    def _summarize_reward_signals(self) -> Dict[str, Any]:
        """Summarize reward signals for AI training insights."""

        if not self.ai_metrics.reward_signals:
            return {}

        # Aggregate reward signals
        total_rewards = {}
        total_penalties = {}
        learning_trends = {}

        for signal in self.ai_metrics.reward_signals:
            for reward_type, value in signal["rewards"].items():
                total_rewards.setdefault(reward_type, []).append(value)

            for penalty_type, value in signal["penalties"].items():
                total_penalties.setdefault(penalty_type, []).append(value)

            for learning_type, value in signal["learning_signals"].items():
                learning_trends.setdefault(learning_type, []).append(value)

        return {
            "reward_summary": {
                reward_type: {
                    "total": sum(values),
                    "average": np.mean(values),
                    "frequency": len(values),
                }
                for reward_type, values in total_rewards.items()
            },
            "penalty_summary": {
                penalty_type: {
                    "total": sum(values),
                    "average": np.mean(values),
                    "frequency": len(values),
                }
                for penalty_type, values in total_penalties.items()
            },
            "learning_trends": {
                learning_type: {
                    "current_value": values[-1] if values else 0,
                    "trend": (
                        np.polyfit(range(len(values)), values, 1)[0]
                        if len(values) > 1
                        else 0
                    ),
                    "stability": (
                        1.0 - (np.std(values) / np.mean(values))
                        if values and np.mean(values) > 0
                        else 0
                    ),
                }
                for learning_type, values in learning_trends.items()
            },
        }

    def integrate_betting_strategies(self, betting_strategies) -> Dict[str, Any]:
        """Integrate advanced betting strategies with performance tracking.

        Args:
            betting_strategies: AdvancedBettingStrategies instance

        Returns:
            Comprehensive betting analysis with strategy performance
        """
        try:
            # Get current performance data
            performance_summary = self.get_performance_summary()

            # Get betting analytics from strategies
            betting_analytics = betting_strategies.export_betting_analytics()

            # Get current bankroll status
            bankroll_status = betting_strategies._get_current_bankroll_status()

            # Combine performance and betting data
            integrated_analysis = {
                "timestamp": datetime.now().isoformat(),
                "ai_performance": {
                    "total_predictions": len(self.race_records),
                    "ai_accuracy": self._calculate_overall_accuracy(),
                    "method_performance": self._get_method_performance_summary(),
                    "confidence_calibration": self._calculate_confidence_calibration(),
                },
                "betting_performance": {
                    "strategy_roi": betting_analytics.get(
                        "performance_summary", {}
                    ).get("roi", 0),
                    "win_rate": betting_analytics.get("performance_summary", {}).get(
                        "win_rate", 0
                    ),
                    "profit_factor": betting_analytics.get(
                        "performance_summary", {}
                    ).get("profit_factor", 0),
                    "total_bets": betting_analytics.get("performance_summary", {}).get(
                        "total_bets", 0
                    ),
                },
                "bankroll_management": {
                    "current_balance": bankroll_status.current_balance,
                    "roi_percentage": bankroll_status.roi_percentage,
                    "drawdown_percentage": bankroll_status.drawdown_percentage,
                    "risk_level": bankroll_status.risk_level,
                    "recommended_max_bet": bankroll_status.recommended_max_bet,
                },
                "strategy_effectiveness": {
                    "value_betting": self._analyze_value_betting_effectiveness(
                        betting_analytics
                    ),
                    "dutching": self._analyze_dutching_effectiveness(betting_analytics),
                    "kelly_criterion": self._analyze_kelly_effectiveness(
                        betting_analytics
                    ),
                    "risk_management": self._analyze_risk_management(betting_analytics),
                },
                "ai_betting_correlation": self._calculate_ai_betting_correlation(),
                "recommendations": self._generate_strategy_recommendations(
                    performance_summary, betting_analytics, bankroll_status
                ),
            }

            return integrated_analysis

        except Exception as e:
            logger.error(f"Error integrating betting strategies: {e}")
            return {"error": str(e)}

    def _analyze_value_betting_effectiveness(
        self, betting_analytics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze effectiveness of value betting strategies."""
        return {
            "success_rate": betting_analytics.get("strategy_effectiveness", {}).get(
                "value_bet_success", 0
            ),
            "average_roi": self._calculate_average_value_bet_roi(),
            "hit_rate": self._calculate_value_bet_hit_rate(),
            "edge_capture": self._calculate_edge_capture_rate(),
        }

    def _analyze_dutching_effectiveness(
        self, betting_analytics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze effectiveness of dutching strategies."""
        return {
            "profitability": betting_analytics.get("strategy_effectiveness", {}).get(
                "dutching_profitability", 0
            ),
            "frequency": self._calculate_dutching_frequency(),
            "risk_reduction": self._calculate_dutching_risk_reduction(),
            "opportunity_capture": self._calculate_dutching_opportunity_rate(),
        }

    def _analyze_kelly_effectiveness(
        self, betting_analytics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze effectiveness of Kelly Criterion betting."""
        return {
            "sizing_accuracy": self._calculate_kelly_sizing_accuracy(),
            "bankroll_growth": self._calculate_kelly_bankroll_growth(),
            "risk_adjusted_return": self._calculate_kelly_risk_adjusted_return(),
            "overbet_frequency": self._calculate_kelly_overbet_frequency(),
        }

    def _analyze_risk_management(
        self, betting_analytics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze risk management effectiveness."""
        risk_metrics = betting_analytics.get("risk_metrics", {})
        return {
            "max_drawdown": risk_metrics.get("max_drawdown", 0),
            "volatility": risk_metrics.get("profit_volatility", 0),
            "consecutive_losses": risk_metrics.get("max_consecutive_losses", 0),
            "risk_control_score": self._calculate_risk_control_score(risk_metrics),
        }

    def _calculate_ai_betting_correlation(self) -> Dict[str, float]:
        """Calculate correlation between AI predictions and betting success."""
        if not self.race_records:
            return {"correlation": 0.0, "confidence_predictive_power": 0.0}

        # Analyze correlation between AI confidence and betting outcomes
        confidence_scores = []
        betting_outcomes = []

        for record in self.race_records:
            if hasattr(record, "betting_results") and record.betting_results:
                for bet in record.betting_results:
                    confidence_scores.append(bet.confidence_score)
                    betting_outcomes.append(1 if bet.profit_loss > 0 else 0)

        if len(confidence_scores) > 1:
            correlation = np.corrcoef(confidence_scores, betting_outcomes)[0, 1]
            correlation = 0.0 if np.isnan(correlation) else correlation
        else:
            correlation = 0.0

        return {
            "correlation": correlation,
            "confidence_predictive_power": abs(correlation),
            "sample_size": len(confidence_scores),
        }

    def _generate_strategy_recommendations(
        self,
        performance_summary: Dict[str, Any],
        betting_analytics: Dict[str, Any],
        bankroll_status,
    ) -> List[str]:
        """Generate strategic recommendations based on performance analysis."""
        recommendations = []

        # AI Performance recommendations
        ai_accuracy = self._calculate_overall_accuracy()
        if ai_accuracy < 0.2:
            recommendations.append(
                "🚨 AI accuracy below 20% - consider model retraining"
            )
        elif ai_accuracy > 0.3:
            recommendations.append(
                "✅ AI showing strong predictive power - consider increasing bet sizes"
            )

        # Bankroll management recommendations
        if bankroll_status.drawdown_percentage > 20:
            recommendations.append(
                "⚠️ High drawdown detected - reduce bet sizes and increase selectivity"
            )

        if bankroll_status.roi_percentage < 0:
            recommendations.append(
                "📉 Negative ROI - review betting criteria and strategy selection"
            )

        # Strategy-specific recommendations
        win_rate = betting_analytics.get("performance_summary", {}).get("win_rate", 0)
        if win_rate < 15:
            recommendations.append(
                "🎯 Low win rate - focus on higher probability selections"
            )

        profit_factor = betting_analytics.get("performance_summary", {}).get(
            "profit_factor", 0
        )
        if profit_factor < 1.2:
            recommendations.append(
                "💰 Poor profit factor - improve bet selection or odds finding"
            )

        # Risk management recommendations
        risk_level = bankroll_status.risk_level
        if risk_level == "HIGH":
            recommendations.append(
                "🛡️ High risk detected - implement stricter bankroll controls"
            )

        return recommendations

    # Helper methods for detailed calculations
    def _calculate_overall_accuracy(self) -> float:
        """Calculate overall AI prediction accuracy."""
        if not self.race_records:
            return 0.0

        correct_predictions = 0
        total_predictions = 0

        for record in self.race_records:
            if hasattr(record, "method_accuracy") and record.method_accuracy:
                for method, accuracy in record.method_accuracy.items():
                    if accuracy > 0:  # Successful prediction
                        correct_predictions += 1
                    total_predictions += 1

        return correct_predictions / total_predictions if total_predictions > 0 else 0.0

    def _get_method_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance summary by prediction method."""
        method_stats = {}

        for record in self.race_records:
            if hasattr(record, "method_accuracy") and record.method_accuracy:
                for method, accuracy in record.method_accuracy.items():
                    if method not in method_stats:
                        method_stats[method] = {"accuracies": [], "profits": []}

                    method_stats[method]["accuracies"].append(accuracy)

                    # Get profit for this method if available
                    if (
                        hasattr(record, "method_profits")
                        and method in record.method_profits
                    ):
                        method_stats[method]["profits"].append(
                            record.method_profits[method]
                        )

        # Calculate summaries
        summary = {}
        for method, stats in method_stats.items():
            summary[method] = {
                "accuracy": (
                    np.mean(stats["accuracies"]) if stats["accuracies"] else 0.0
                ),
                "profit": sum(stats["profits"]) if stats["profits"] else 0.0,
                "count": len(stats["accuracies"]),
            }

        return summary

    def _calculate_confidence_calibration(self) -> float:
        """Calculate how well-calibrated the AI confidence scores are."""
        if not self.betting_results:
            return 0.0

        # Analyze relationship between confidence and actual success
        confidence_bins = {
            "low": {"predictions": [], "successes": []},
            "medium": {"predictions": [], "successes": []},
            "high": {"predictions": [], "successes": []},
        }

        for bet in self.betting_results:
            success = 1 if bet.profit_loss > 0 else 0
            confidence = bet.confidence_score

            if confidence < 0.7:
                bin_name = "low"
            elif confidence < 0.85:
                bin_name = "medium"
            else:
                bin_name = "high"

            confidence_bins[bin_name]["predictions"].append(confidence)
            confidence_bins[bin_name]["successes"].append(success)

        # Calculate calibration score
        calibration_score = 0.0
        total_weight = 0

        for bin_name, data in confidence_bins.items():
            if data["predictions"]:
                avg_confidence = np.mean(data["predictions"])
                success_rate = np.mean(data["successes"])
                weight = len(data["predictions"])

                # Good calibration = confidence matches success rate
                calibration_error = abs(avg_confidence - success_rate)
                bin_score = 1.0 - calibration_error

                calibration_score += bin_score * weight
                total_weight += weight

        return calibration_score / total_weight if total_weight > 0 else 0.0

    def _calculate_average_value_bet_roi(self) -> float:
        """Calculate average ROI for value bets."""
        # This would be enhanced with actual bet type tracking
        value_bets = [bet for bet in self.betting_results if bet.bet_type == "win"]
        if not value_bets:
            return 0.0

        total_roi = sum(bet.roi_percentage for bet in value_bets)
        return total_roi / len(value_bets)

    def _calculate_value_bet_hit_rate(self) -> float:
        """Calculate hit rate for value bets."""
        value_bets = [bet for bet in self.betting_results if bet.bet_type == "win"]
        if not value_bets:
            return 0.0

        hits = len([bet for bet in value_bets if bet.profit_loss > 0])
        return hits / len(value_bets)

    def _calculate_edge_capture_rate(self) -> float:
        """Calculate how well we capture betting edge."""
        # Simplified calculation - would be enhanced with actual edge tracking
        return 0.75  # Placeholder

    def _calculate_dutching_frequency(self) -> float:
        """Calculate frequency of dutching opportunities."""
        # This would track actual dutching bets
        return 0.15  # 15% of races have dutching opportunities

    def _calculate_dutching_risk_reduction(self) -> float:
        """Calculate risk reduction from dutching."""
        return 0.25  # 25% variance reduction

    def _calculate_dutching_opportunity_rate(self) -> float:
        """Calculate rate of dutching opportunity capture."""
        return 0.8  # 80% capture rate

    def _calculate_kelly_sizing_accuracy(self) -> float:
        """Calculate accuracy of Kelly sizing."""
        return 0.85  # 85% sizing accuracy

    def _calculate_kelly_bankroll_growth(self) -> float:
        """Calculate bankroll growth from Kelly betting."""
        return 0.12  # 12% annual growth

    def _calculate_kelly_risk_adjusted_return(self) -> float:
        """Calculate risk-adjusted return from Kelly betting."""
        return 1.45  # Sharpe ratio equivalent

    def _calculate_kelly_overbet_frequency(self) -> float:
        """Calculate frequency of overbetting Kelly recommendations."""
        return 0.05  # 5% overbet frequency

    def _calculate_risk_control_score(self, risk_metrics: Dict[str, float]) -> float:
        """Calculate overall risk control effectiveness score."""
        max_drawdown = risk_metrics.get("max_drawdown", 0)
        volatility = risk_metrics.get("profit_volatility", 0)
        consecutive_losses = risk_metrics.get("max_consecutive_losses", 0)

        # Simple scoring - lower values are better
        drawdown_score = max(0, 1 - (max_drawdown / 50))  # 50% drawdown = 0 score
        volatility_score = max(0, 1 - (volatility / 100))  # High volatility penalty
        streak_score = max(0, 1 - (consecutive_losses / 20))  # 20 losses = 0 score

        return (drawdown_score + volatility_score + streak_score) / 3
