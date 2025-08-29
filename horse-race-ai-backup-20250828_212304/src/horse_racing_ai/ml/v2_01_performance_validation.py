#!/usr/bin/env python3
"""
V2.01 Performance Validation Framework
=====================================

Implements comprehensive performance tracking and validation system
discovered in v2.01 performance_data analysis.

Features:
- Actual vs predicted result tracking
- Multiple accuracy metrics (prediction, betting, value)
- ROI and profitability analysis
- Temporal performance tracking
- Method-specific validation

Based on v2.01 performance_data.csv structure and validation approach.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Single race prediction result for validation."""

    race_id: str
    race_date: datetime
    horse_name: str
    predicted_finish_position: int
    actual_finish_position: int
    raw_rating: float
    monte_carlo_rating: float
    ai_ml_rating: float
    consensus_rating: float
    raw_win_probability: float
    monte_carlo_win_probability: float
    ai_ml_win_probability: float
    consensus_win_probability: float
    predicted_odds: float
    actual_odds: Optional[float] = None
    bet_amount: float = 0.0
    bet_return: float = 0.0
    prediction_accuracy: float = 0.0
    betting_edge: float = 0.0
    value_rating: float = 0.0


@dataclass
class MethodPerformance:
    """Performance metrics for a specific prediction method."""

    method_name: str
    total_predictions: int
    win_predictions_correct: int
    place_predictions_correct: int
    exact_position_correct: int
    mean_position_error: float
    win_prediction_accuracy: float
    place_prediction_accuracy: float
    position_prediction_accuracy: float
    correlation_with_results: float
    profit_loss: float
    roi_percentage: float
    strike_rate: float
    average_odds: float
    value_bets_placed: int
    value_bets_won: int
    confidence_scores: List[float] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report."""

    report_date: datetime
    period_start: datetime
    period_end: datetime
    total_races: int
    total_predictions: int
    method_performances: Dict[str, MethodPerformance]
    overall_accuracy: float
    overall_roi: float
    overall_profit: float
    best_performing_method: str
    prediction_reliability: float
    market_efficiency_analysis: Dict[str, float]


class V201PerformanceValidator:
    """
    Performance validation system based on v2.01 analysis.

    Tracks prediction accuracy, betting performance, and method effectiveness
    using the comprehensive approach discovered in v2.01 performance data.
    """

    def __init__(self, results_file: str = "data/validation_results.csv"):
        self.results_file = Path(results_file)
        self.prediction_results: List[PredictionResult] = []
        self.method_names = ["raw", "monte_carlo", "ai_ml", "consensus"]

        # Load existing results if available
        self._load_existing_results()

    def _load_existing_results(self) -> None:
        """Load existing validation results from file."""
        if not self.results_file.exists():
            logger.info("No existing results file found, starting fresh")
            return

        try:
            df = pd.read_csv(self.results_file)
            logger.info(f"Loaded {len(df)} existing prediction results")

            for _, row in df.iterrows():
                result = PredictionResult(
                    race_id=row["race_id"],
                    race_date=pd.to_datetime(row["race_date"]),
                    horse_name=row["horse_name"],
                    predicted_finish_position=int(row["predicted_finish_position"]),
                    actual_finish_position=int(row["actual_finish_position"]),
                    raw_rating=float(row["raw_rating"]),
                    monte_carlo_rating=float(row["monte_carlo_rating"]),
                    ai_ml_rating=float(row["ai_ml_rating"]),
                    consensus_rating=float(row["consensus_rating"]),
                    raw_win_probability=float(row["raw_win_probability"]),
                    monte_carlo_win_probability=float(
                        row["monte_carlo_win_probability"]
                    ),
                    ai_ml_win_probability=float(row["ai_ml_win_probability"]),
                    consensus_win_probability=float(row["consensus_win_probability"]),
                    predicted_odds=float(row["predicted_odds"]),
                    actual_odds=row.get("actual_odds"),
                    bet_amount=float(row.get("bet_amount", 0)),
                    bet_return=float(row.get("bet_return", 0)),
                    prediction_accuracy=float(row.get("prediction_accuracy", 0)),
                    betting_edge=float(row.get("betting_edge", 0)),
                    value_rating=float(row.get("value_rating", 0)),
                )
                self.prediction_results.append(result)

        except Exception as e:
            logger.error(f"Error loading existing results: {e}")

    def record_prediction_result(self, result: PredictionResult) -> None:
        """Record a new prediction result for validation."""
        # Calculate derived metrics
        result.prediction_accuracy = self._calculate_prediction_accuracy(result)
        result.betting_edge = self._calculate_betting_edge(result)
        result.value_rating = self._calculate_value_rating(result)

        self.prediction_results.append(result)

        # Save to file immediately
        self._save_results()

        logger.info(
            f"Recorded prediction result for {result.horse_name} in {result.race_id}"
        )

    def _calculate_prediction_accuracy(self, result: PredictionResult) -> float:
        """Calculate prediction accuracy score."""
        position_error = abs(
            result.predicted_finish_position - result.actual_finish_position
        )

        # Perfect prediction = 1.0, decreasing with position error
        accuracy = max(0, 1.0 - (position_error / 10))

        # Bonus for win/place predictions
        if result.predicted_finish_position == 1 and result.actual_finish_position == 1:
            accuracy += 0.2  # Win prediction bonus
        elif (
            result.predicted_finish_position <= 3 and result.actual_finish_position <= 3
        ):
            accuracy += 0.1  # Place prediction bonus

        return min(1.0, accuracy)

    def _calculate_betting_edge(self, result: PredictionResult) -> float:
        """Calculate betting edge based on odds vs probability."""
        if result.actual_odds is None or result.consensus_win_probability <= 0:
            return 0.0

        # Implied probability from odds
        implied_prob = 1.0 / result.actual_odds if result.actual_odds > 0 else 0

        # Edge = our probability - market probability
        edge = result.consensus_win_probability - implied_prob

        return edge

    def _calculate_value_rating(self, result: PredictionResult) -> float:
        """Calculate value rating for betting opportunities."""
        if result.actual_odds is None or result.consensus_win_probability <= 0:
            return 0.0

        # Value = (odds * our_probability) - 1
        expected_value = (result.actual_odds * result.consensus_win_probability) - 1

        return max(0, expected_value)

    def analyze_method_performance(
        self, days_back: int = 30
    ) -> Dict[str, MethodPerformance]:
        """Analyze performance of each prediction method."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_results = [
            r for r in self.prediction_results if r.race_date >= cutoff_date
        ]

        if not recent_results:
            logger.warning("No recent results found for analysis")
            return {}

        method_performances = {}

        for method in self.method_names:
            performance = self._calculate_method_metrics(recent_results, method)
            method_performances[method] = performance

        return method_performances

    def _calculate_method_metrics(
        self, results: List[PredictionResult], method: str
    ) -> MethodPerformance:
        """Calculate detailed metrics for a specific method."""
        if not results:
            return MethodPerformance(
                method_name=method,
                total_predictions=0,
                win_predictions_correct=0,
                place_predictions_correct=0,
                exact_position_correct=0,
                mean_position_error=0,
                win_prediction_accuracy=0,
                place_prediction_accuracy=0,
                position_prediction_accuracy=0,
                correlation_with_results=0,
                profit_loss=0,
                roi_percentage=0,
                strike_rate=0,
                average_odds=0,
                value_bets_placed=0,
                value_bets_won=0,
            )

        # Get method-specific data
        if method == "raw":
            probabilities = [r.raw_win_probability for r in results]
            ratings = [r.raw_rating for r in results]
        elif method == "monte_carlo":
            probabilities = [r.monte_carlo_win_probability for r in results]
            ratings = [r.monte_carlo_rating for r in results]
        elif method == "ai_ml":
            probabilities = [r.ai_ml_win_probability for r in results]
            ratings = [r.ai_ml_rating for r in results]
        else:  # consensus
            probabilities = [r.consensus_win_probability for r in results]
            ratings = [r.consensus_rating for r in results]

        # Calculate metrics
        total_predictions = len(results)

        # Win predictions (highest probability/rating in each race)
        win_predictions_correct = sum(
            1
            for r in results
            if self._was_top_pick(r, method) and r.actual_finish_position == 1
        )

        # Place predictions (top 3 probability/rating)
        place_predictions_correct = sum(
            1
            for r in results
            if self._was_place_pick(r, method) and r.actual_finish_position <= 3
        )

        # Exact position predictions
        exact_position_correct = sum(
            1
            for r in results
            if r.predicted_finish_position == r.actual_finish_position
        )

        # Position errors
        position_errors = [
            abs(r.predicted_finish_position - r.actual_finish_position) for r in results
        ]
        mean_position_error = np.mean(position_errors) if position_errors else 0

        # Accuracy rates
        win_prediction_accuracy = (
            win_predictions_correct / total_predictions if total_predictions > 0 else 0
        )
        place_prediction_accuracy = (
            place_predictions_correct / total_predictions
            if total_predictions > 0
            else 0
        )
        position_prediction_accuracy = (
            exact_position_correct / total_predictions if total_predictions > 0 else 0
        )

        # Correlation analysis
        actual_positions = [r.actual_finish_position for r in results]
        correlation_with_results = (
            abs(np.corrcoef(ratings, actual_positions)[0, 1]) if len(ratings) > 1 else 0
        )

        # Betting metrics
        total_bet = sum(r.bet_amount for r in results)
        total_return = sum(r.bet_return for r in results)
        profit_loss = total_return - total_bet
        roi_percentage = (profit_loss / total_bet * 100) if total_bet > 0 else 0

        # Strike rate (profitable bets)
        profitable_bets = sum(1 for r in results if r.bet_return > r.bet_amount)
        strike_rate = (
            profitable_bets / total_predictions if total_predictions > 0 else 0
        )

        # Average odds
        odds_data = [r.actual_odds for r in results if r.actual_odds is not None]
        average_odds = np.mean(odds_data) if odds_data else 0

        # Value betting
        value_bets = [r for r in results if r.value_rating > 0.1]
        value_bets_placed = len(value_bets)
        value_bets_won = sum(1 for r in value_bets if r.actual_finish_position == 1)

        return MethodPerformance(
            method_name=method,
            total_predictions=total_predictions,
            win_predictions_correct=win_predictions_correct,
            place_predictions_correct=place_predictions_correct,
            exact_position_correct=exact_position_correct,
            mean_position_error=mean_position_error,
            win_prediction_accuracy=win_prediction_accuracy,
            place_prediction_accuracy=place_prediction_accuracy,
            position_prediction_accuracy=position_prediction_accuracy,
            correlation_with_results=correlation_with_results,
            profit_loss=profit_loss,
            roi_percentage=roi_percentage,
            strike_rate=strike_rate,
            average_odds=average_odds,
            value_bets_placed=value_bets_placed,
            value_bets_won=value_bets_won,
            confidence_scores=probabilities,
        )

    def _was_top_pick(self, result: PredictionResult, method: str) -> bool:
        """Check if this was the top pick for the method in its race."""
        # This would require race-level analysis - simplified for now
        if method == "raw":
            return result.raw_win_probability > 0.3
        elif method == "monte_carlo":
            return result.monte_carlo_win_probability > 0.3
        elif method == "ai_ml":
            return result.ai_ml_win_probability > 0.3
        else:
            return result.consensus_win_probability > 0.3

    def _was_place_pick(self, result: PredictionResult, method: str) -> bool:
        """Check if this was a place pick for the method."""
        if method == "raw":
            return result.raw_win_probability > 0.15
        elif method == "monte_carlo":
            return result.monte_carlo_win_probability > 0.15
        elif method == "ai_ml":
            return result.ai_ml_win_probability > 0.15
        else:
            return result.consensus_win_probability > 0.15

    def generate_performance_report(self, days_back: int = 30) -> PerformanceReport:
        """Generate comprehensive performance report."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_results = [
            r for r in self.prediction_results if r.race_date >= cutoff_date
        ]

        method_performances = self.analyze_method_performance(days_back)

        # Overall metrics
        total_races = len(set(r.race_id for r in recent_results))
        total_predictions = len(recent_results)

        overall_accuracy = (
            np.mean([r.prediction_accuracy for r in recent_results])
            if recent_results
            else 0
        )
        overall_profit = sum(r.bet_return - r.bet_amount for r in recent_results)
        total_bet = sum(r.bet_amount for r in recent_results)
        overall_roi = (overall_profit / total_bet * 100) if total_bet > 0 else 0

        # Best performing method
        best_method = "consensus"
        if method_performances:
            best_method = max(
                method_performances.keys(),
                key=lambda m: method_performances[m].win_prediction_accuracy,
            )

        # Prediction reliability
        reliability_scores = [r.prediction_accuracy for r in recent_results]
        prediction_reliability = (
            np.mean(reliability_scores) if reliability_scores else 0
        )

        # Market efficiency analysis
        market_efficiency = self._analyze_market_efficiency(recent_results)

        return PerformanceReport(
            report_date=datetime.now(),
            period_start=cutoff_date,
            period_end=datetime.now(),
            total_races=total_races,
            total_predictions=total_predictions,
            method_performances=method_performances,
            overall_accuracy=overall_accuracy,
            overall_roi=overall_roi,
            overall_profit=overall_profit,
            best_performing_method=best_method,
            prediction_reliability=prediction_reliability,
            market_efficiency_analysis=market_efficiency,
        )

    def _analyze_market_efficiency(
        self, results: List[PredictionResult]
    ) -> Dict[str, float]:
        """Analyze market efficiency vs our predictions."""
        if not results:
            return {}

        # Calculate how often market favorites win vs our picks
        market_accuracy = 0
        our_accuracy = 0
        valid_comparisons = 0

        for result in results:
            if result.actual_odds is not None:
                # Assume market favorite has lowest odds
                market_pick = result.actual_odds < 3.0  # Simplified
                our_pick = result.consensus_win_probability > 0.3

                if market_pick and result.actual_finish_position == 1:
                    market_accuracy += 1
                if our_pick and result.actual_finish_position == 1:
                    our_accuracy += 1

                valid_comparisons += 1

        if valid_comparisons > 0:
            market_win_rate = market_accuracy / valid_comparisons
            our_win_rate = our_accuracy / valid_comparisons
            edge_over_market = our_win_rate - market_win_rate
        else:
            market_win_rate = our_win_rate = edge_over_market = 0

        return {
            "market_win_rate": market_win_rate,
            "our_win_rate": our_win_rate,
            "edge_over_market": edge_over_market,
            "valid_comparisons": valid_comparisons,
        }

    def _save_results(self) -> None:
        """Save all results to CSV file."""
        if not self.prediction_results:
            return

        # Prepare data for DataFrame
        data = []
        for result in self.prediction_results:
            data.append(
                {
                    "race_id": result.race_id,
                    "race_date": result.race_date.isoformat(),
                    "horse_name": result.horse_name,
                    "predicted_finish_position": result.predicted_finish_position,
                    "actual_finish_position": result.actual_finish_position,
                    "raw_rating": result.raw_rating,
                    "monte_carlo_rating": result.monte_carlo_rating,
                    "ai_ml_rating": result.ai_ml_rating,
                    "consensus_rating": result.consensus_rating,
                    "raw_win_probability": result.raw_win_probability,
                    "monte_carlo_win_probability": result.monte_carlo_win_probability,
                    "ai_ml_win_probability": result.ai_ml_win_probability,
                    "consensus_win_probability": result.consensus_win_probability,
                    "predicted_odds": result.predicted_odds,
                    "actual_odds": result.actual_odds,
                    "bet_amount": result.bet_amount,
                    "bet_return": result.bet_return,
                    "prediction_accuracy": result.prediction_accuracy,
                    "betting_edge": result.betting_edge,
                    "value_rating": result.value_rating,
                }
            )

        df = pd.DataFrame(data)

        # Ensure directory exists
        self.results_file.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(self.results_file, index=False)

    def export_performance_summary(self, filepath: str, days_back: int = 30) -> str:
        """Export detailed performance summary to file."""
        report = self.generate_performance_report(days_back)

        summary_lines = [
            "V2.01 Performance Validation Report",
            "=" * 50,
            f"Report Date: {report.report_date.strftime('%Y-%m-%d %H:%M')}",
            f"Analysis Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}",
            f"Total Races: {report.total_races}",
            f"Total Predictions: {report.total_predictions}",
            "",
            "Overall Performance:",
            f"  Accuracy: {report.overall_accuracy:.3f}",
            f"  ROI: {report.overall_roi:.2f}%",
            f"  Profit/Loss: ${report.overall_profit:.2f}",
            f"  Best Method: {report.best_performing_method}",
            f"  Prediction Reliability: {report.prediction_reliability:.3f}",
            "",
            "Method Performance Details:",
            "-" * 30,
        ]

        for method, perf in report.method_performances.items():
            summary_lines.extend(
                [
                    f"\n{method.upper()} Method:",
                    f"  Total Predictions: {perf.total_predictions}",
                    f"  Win Accuracy: {perf.win_prediction_accuracy:.3f}",
                    f"  Place Accuracy: {perf.place_prediction_accuracy:.3f}",
                    f"  Position Accuracy: {perf.position_prediction_accuracy:.3f}",
                    f"  Mean Position Error: {perf.mean_position_error:.2f}",
                    f"  ROI: {perf.roi_percentage:.2f}%",
                    f"  Strike Rate: {perf.strike_rate:.3f}",
                    f"  Correlation: {perf.correlation_with_results:.3f}",
                    f"  Value Bets: {perf.value_bets_placed} ({perf.value_bets_won} won)",
                ]
            )

        summary_lines.extend(["", "Market Efficiency Analysis:", "-" * 25])

        for metric, value in report.market_efficiency_analysis.items():
            if isinstance(value, float):
                summary_lines.append(f"  {metric}: {value:.3f}")
            else:
                summary_lines.append(f"  {metric}: {value}")

        # Write to file
        with open(filepath, "w") as f:
            f.write("\n".join(summary_lines))

        logger.info(f"Performance summary exported to {filepath}")
        return filepath


def demo_performance_validation():
    """Demonstrate the v2.01 performance validation system."""
    print("📊 V2.01 Performance Validation System Demo")
    print("=" * 60)

    # Initialize validator
    validator = V201PerformanceValidator("demo_validation_results.csv")

    # Sample prediction results
    sample_results = [
        PredictionResult(
            race_id="DEMO_001",
            race_date=datetime.now() - timedelta(days=5),
            horse_name="Thunder Bolt",
            predicted_finish_position=1,
            actual_finish_position=1,
            raw_rating=85.2,
            monte_carlo_rating=88.1,
            ai_ml_rating=82.3,
            consensus_rating=85.9,
            raw_win_probability=0.35,
            monte_carlo_win_probability=0.42,
            ai_ml_win_probability=0.38,
            consensus_win_probability=0.39,
            predicted_odds=2.5,
            actual_odds=2.8,
            bet_amount=10.0,
            bet_return=28.0,
        ),
        PredictionResult(
            race_id="DEMO_002",
            race_date=datetime.now() - timedelta(days=3),
            horse_name="Lightning Strike",
            predicted_finish_position=2,
            actual_finish_position=3,
            raw_rating=78.5,
            monte_carlo_rating=76.2,
            ai_ml_rating=80.1,
            consensus_rating=78.3,
            raw_win_probability=0.25,
            monte_carlo_win_probability=0.22,
            ai_ml_win_probability=0.28,
            consensus_win_probability=0.25,
            predicted_odds=4.0,
            actual_odds=3.8,
            bet_amount=5.0,
            bet_return=0.0,
        ),
    ]

    # Record results
    for result in sample_results:
        validator.record_prediction_result(result)

    # Generate performance report
    report = validator.generate_performance_report(days_back=7)

    print(f"\n📈 Performance Report Summary:")
    print(f"Total Races: {report.total_races}")
    print(f"Total Predictions: {report.total_predictions}")
    print(f"Overall Accuracy: {report.overall_accuracy:.3f}")
    print(f"Overall ROI: {report.overall_roi:.2f}%")
    print(f"Best Method: {report.best_performing_method}")

    print(f"\n🎯 Method Performance:")
    for method, perf in report.method_performances.items():
        print(
            f"  {method}: {perf.win_prediction_accuracy:.3f} accuracy, {perf.roi_percentage:.1f}% ROI"
        )

    # Export detailed summary
    summary_file = validator.export_performance_summary("demo_performance_summary.txt")
    print(f"\n📋 Detailed summary exported to: {summary_file}")


if __name__ == "__main__":
    demo_performance_validation()
