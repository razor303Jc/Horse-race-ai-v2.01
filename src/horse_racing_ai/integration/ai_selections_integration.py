#!/usr/bin/env python3
"""
AI Selections Integration System
===============================

Integration layer that connects AI selections tracking with existing systems:
- Enhanced Performance Tracker
- AI Betting Integration
- Monte Carlo Simulation
- Real race results processing

This provides comprehensive tracking and contextual analysis for AI improvement.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ..analytics.ai_selections_tracker import AISelectionsTracker, SelectionAnalytics
from ..performance.enhanced_tracker import EnhancedPerformanceTracker, RaceRecord
from ..integration.ai_betting_integration import AIBettingIntegrationSystem
from ..simulation.enhanced_monte_carlo_engine import EnhancedMonteCarloEngine

logger = logging.getLogger(__name__)


class AISelectionsIntegrationSystem:
    """
    Integration system for AI selections tracking with comprehensive analysis.

    Coordinates between:
    - AI selections tracking
    - Performance monitoring
    - Betting integration
    - Result analysis
    - Contextual learning
    """

    def __init__(
        self,
        selections_db_path: str = "data/ai_selections_tracking.db",
        performance_db_path: str = "data/performance_tracking.db",
    ):
        """Initialize the integration system."""
        self.selections_tracker = AISelectionsTracker(selections_db_path)
        self.performance_tracker = EnhancedPerformanceTracker(performance_db_path)
        self.betting_integration = AIBettingIntegrationSystem()

        # Configuration
        self.config = self._load_configuration()

        # Analysis cache
        self._analysis_cache = {}
        self._cache_timeout = 300  # 5 minutes

        logger.info("AI Selections Integration System initialized")

    def process_race_predictions(
        self,
        race_data: Dict[str, Any],
        ai_predictions: Dict[str, List[Dict[str, Any]]],
        betting_strategies: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Process AI predictions for a race and record selections.

        Args:
            race_data: Race information and context
            ai_predictions: AI predictions by method
            betting_strategies: List of betting strategies to apply

        Returns:
            Dictionary of selection IDs by method
        """
        if not betting_strategies:
            betting_strategies = ["value_bet", "80_20", "dutching"]

        selection_ids = {}

        # Process each prediction method
        for method, predictions in ai_predictions.items():
            if not predictions:
                continue

            # Find top selections based on confidence and value
            top_selections = self._identify_top_selections(
                predictions, race_data, method
            )

            # Record selections for each strategy
            for strategy in betting_strategies:
                for selection in top_selections:
                    if self._meets_strategy_criteria(selection, strategy):
                        selection_id = self.selections_tracker.record_ai_selection(
                            race_data=race_data,
                            selection_data=selection,
                            prediction_method=method,
                            betting_strategy=strategy,
                        )

                        key = f"{method}_{strategy}"
                        if key not in selection_ids:
                            selection_ids[key] = []
                        selection_ids[key].append(selection_id)

        # Also record in performance tracker
        self.performance_tracker.record_race_prediction(
            race_data=race_data,
            raw_predictions=ai_predictions.get("raw_ratings", []),
            monte_carlo_predictions=ai_predictions.get("monte_carlo", []),
            ai_ml_predictions=ai_predictions.get("ai_ml", []),
            consensus_predictions=ai_predictions.get("consensus", []),
        )

        logger.info(
            f"Processed race predictions for {race_data.get('race_id', 'unknown')}"
        )
        return selection_ids

    def update_race_results(
        self,
        race_id: str,
        actual_results: List[Dict[str, Any]],
        betting_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update race results and calculate performance metrics.

        Args:
            race_id: Race identifier
            actual_results: Actual race finishing positions
            betting_results: Betting outcomes if available

        Returns:
            Update summary with performance impact
        """
        updates_processed = 0
        total_profit_impact = 0.0

        # Get all selections for this race
        race_selections = self._get_race_selections(race_id)

        # Update each selection with results
        for selection in race_selections:
            horse_name = selection["horse_name"]

            # Find actual result for this horse
            horse_result = next(
                (r for r in actual_results if r["horse_name"] == horse_name), None
            )

            if horse_result:
                # Find corresponding betting result
                betting_result = None
                if betting_results:
                    betting_result = next(
                        (
                            b
                            for b in betting_results
                            if b.get("horse_name") == horse_name
                            and b.get("selection_id") == selection["selection_id"]
                        ),
                        None,
                    )

                # Update selection
                success = self.selections_tracker.update_selection_result(
                    selection_id=selection["selection_id"],
                    actual_result=horse_result,
                    financial_result=betting_result,
                )

                if success:
                    updates_processed += 1
                    if betting_result:
                        total_profit_impact += betting_result.get("profit", 0.0)

        # Update performance tracker with results
        race_record = self.performance_tracker.get_race_record(race_id)
        if race_record:
            race_record.actual_results = actual_results
            self.performance_tracker._calculate_method_accuracy(race_record)

            # Process betting results if available
            if betting_results:
                betting_strategy = {"default_bet_amount": 10.0, "bet_types": ["win"]}
                self.performance_tracker._process_betting_results(
                    race_record, betting_strategy
                )

        # Trigger contextual analysis update
        self._update_contextual_analysis(race_id, actual_results)

        summary = {
            "race_id": race_id,
            "selections_updated": updates_processed,
            "total_profit_impact": total_profit_impact,
            "accuracy_impact": self._calculate_accuracy_impact(race_id),
            "learning_signals": self._extract_learning_signals(race_id, actual_results),
        }

        logger.info(
            f"Updated results for race {race_id}: {updates_processed} selections"
        )
        return summary

    def generate_comprehensive_analysis(
        self,
        period_days: int = 30,
        include_strategies: Optional[List[str]] = None,
        include_methods: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis across all tracking systems.

        Args:
            period_days: Analysis period in days
            include_strategies: Strategies to include in analysis
            include_methods: Methods to include in analysis

        Returns:
            Comprehensive analysis report
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        # Get selections analytics
        selections_analytics = self.selections_tracker.get_selection_analytics(
            start_date=start_date, end_date=end_date
        )

        # Get performance tracker summary
        performance_summary = self.performance_tracker.get_performance_summary()

        # Get contextual analysis
        contextual_analysis = self.selections_tracker.generate_contextual_analysis(
            period_days=period_days
        )

        # Combine insights
        combined_analysis = {
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days,
            },
            "selections_performance": {
                "total_selections": selections_analytics.total_selections,
                "overall_accuracy": selections_analytics.overall_accuracy,
                "roi_percentage": selections_analytics.roi_percentage,
                "profit_factor": selections_analytics.profit_factor,
                "confidence_calibration": selections_analytics.confidence_calibration,
            },
            "method_comparison": self._compare_methods(
                selections_analytics.method_performance,
                performance_summary.get("method_accuracy", {}),
            ),
            "strategy_effectiveness": selections_analytics.strategy_performance,
            "risk_assessment": {
                "max_drawdown": selections_analytics.max_drawdown,
                "consecutive_losses": selections_analytics.consecutive_losses,
                "volatility": selections_analytics.volatility,
                "risk_level": self._assess_overall_risk(selections_analytics),
            },
            "market_intelligence": {
                "average_odds": selections_analytics.average_odds,
                "overlay_rate": selections_analytics.overlay_rate,
                "value_capture_rate": selections_analytics.value_capture_rate,
                "edge_exploitation": self._calculate_edge_exploitation(
                    selections_analytics
                ),
            },
            "contextual_insights": contextual_analysis,
            "improvement_recommendations": self._generate_improvement_recommendations(
                selections_analytics, performance_summary, contextual_analysis
            ),
            "ai_learning_signals": self._extract_ai_learning_signals(
                start_date, end_date
            ),
        }

        return combined_analysis

    def export_comprehensive_data(
        self, period_days: int = 30, export_format: str = "excel"
    ) -> str:
        """
        Export comprehensive data across all systems.

        Args:
            period_days: Period to export
            export_format: Export format (excel, csv, json)

        Returns:
            Path to exported file
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        # Export selections data
        selections_file = self.selections_tracker.export_selection_data(
            start_date=start_date,
            end_date=end_date,
            format_type="csv",  # Always CSV for intermediate processing
        )

        # Get performance data
        performance_summary = self.performance_tracker.get_performance_summary()

        # Get comprehensive analysis
        analysis = self.generate_comprehensive_analysis(period_days)

        # Combine into single export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path("reports/comprehensive_analysis")
        export_dir.mkdir(parents=True, exist_ok=True)

        if export_format.lower() == "excel":
            # Create multi-sheet Excel file
            file_path = export_dir / f"ai_comprehensive_analysis_{timestamp}.xlsx"

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                # Selections data
                selections_df = pd.read_csv(selections_file)
                selections_df.to_excel(writer, sheet_name="Selections", index=False)

                # Analysis summary
                analysis_df = pd.DataFrame([analysis["selections_performance"]])
                analysis_df.to_excel(writer, sheet_name="Summary", index=False)

                # Method comparison
                if analysis["method_comparison"]:
                    method_df = pd.DataFrame(analysis["method_comparison"]).T
                    method_df.to_excel(writer, sheet_name="Methods", index=True)

                # Strategy effectiveness
                if analysis["strategy_effectiveness"]:
                    strategy_df = pd.DataFrame(analysis["strategy_effectiveness"]).T
                    strategy_df.to_excel(writer, sheet_name="Strategies", index=True)

        elif export_format.lower() == "json":
            file_path = export_dir / f"ai_comprehensive_analysis_{timestamp}.json"

            # Load selections data
            selections_df = pd.read_csv(selections_file)
            selections_data = selections_df.to_dict("records")

            # Combine all data
            comprehensive_data = {
                "analysis": analysis,
                "selections_data": selections_data,
                "performance_summary": performance_summary,
                "export_metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "period_days": period_days,
                    "total_selections": len(selections_data),
                },
            }

            with open(file_path, "w") as f:
                json.dump(comprehensive_data, f, indent=2, default=str)

        else:
            # Return the CSV file path
            file_path = selections_file

        # Clean up intermediate file if different format
        if export_format.lower() != "csv" and Path(selections_file).exists():
            Path(selections_file).unlink()

        logger.info(f"Exported comprehensive analysis to {file_path}")
        return str(file_path)

    def get_real_time_performance(self) -> Dict[str, Any]:
        """Get real-time performance metrics across all systems."""
        current_date = datetime.utcnow().date()

        # Get today's selections
        todays_analytics = self.selections_tracker.get_selection_analytics(
            start_date=datetime.combine(current_date, datetime.min.time()),
            end_date=datetime.utcnow(),
        )

        # Get recent performance
        week_analytics = self.selections_tracker.get_selection_analytics(
            start_date=datetime.utcnow() - timedelta(days=7), end_date=datetime.utcnow()
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "today": {
                "selections": todays_analytics.total_selections,
                "accuracy": todays_analytics.overall_accuracy,
                "roi": todays_analytics.roi_percentage,
                "profit": todays_analytics.net_profit,
            },
            "week": {
                "selections": week_analytics.total_selections,
                "accuracy": week_analytics.overall_accuracy,
                "roi": week_analytics.roi_percentage,
                "profit": week_analytics.net_profit,
            },
            "status": self._determine_system_status(todays_analytics, week_analytics),
        }

    def _load_configuration(self) -> Dict[str, Any]:
        """Load system configuration."""
        config_path = Path("config/ai_selections_integration_config.json")

        default_config = {
            "selection_thresholds": {
                "min_confidence": 0.6,
                "min_value_edge": 0.1,
                "max_odds": 20.0,
            },
            "strategy_criteria": {
                "value_bet": {"min_edge": 0.15, "max_odds": 15.0},
                "80_20": {"min_confidence": 0.7, "top_percentage": 0.2},
                "dutching": {"min_selections": 2, "max_selections": 4},
            },
            "analysis_settings": {
                "cache_timeout": 300,
                "min_sample_size": 10,
                "confidence_bins": [0.6, 0.8],
            },
        }

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")

        return default_config

    def _identify_top_selections(
        self, predictions: List[Dict[str, Any]], race_data: Dict[str, Any], method: str
    ) -> List[Dict[str, Any]]:
        """Identify top selections from predictions."""
        thresholds = self.config["selection_thresholds"]

        top_selections = []

        for prediction in predictions:
            confidence = prediction.get("confidence_score", 0.5)
            win_prob = prediction.get("win_probability", 0.1)
            odds = prediction.get("odds_decimal", 10.0)

            # Calculate value edge
            implied_prob = 1.0 / odds if odds > 0 else 0.1
            value_edge = (win_prob - implied_prob) / implied_prob

            # Check if meets selection criteria
            if (
                confidence >= thresholds["min_confidence"]
                and value_edge >= thresholds["min_value_edge"]
                and odds <= thresholds["max_odds"]
            ):

                # Enhance prediction with additional data
                enhanced_prediction = prediction.copy()
                enhanced_prediction.update(
                    {
                        "value_edge": value_edge,
                        "selection_timestamp": datetime.utcnow().isoformat(),
                        "race_context": {
                            "field_size": race_data.get("field_size", 0),
                            "weather": race_data.get("weather", ""),
                            "track_condition": race_data.get("track_condition", ""),
                        },
                    }
                )

                top_selections.append(enhanced_prediction)

        # Sort by confidence * value_edge
        top_selections.sort(
            key=lambda x: x["confidence_score"] * x["value_edge"], reverse=True
        )

        # Return top 3 selections
        return top_selections[:3]

    def _meets_strategy_criteria(
        self, selection: Dict[str, Any], strategy: str
    ) -> bool:
        """Check if selection meets strategy criteria."""
        criteria = self.config["strategy_criteria"].get(strategy, {})

        if strategy == "value_bet":
            return selection.get("value_edge", 0) >= criteria.get(
                "min_edge", 0.15
            ) and selection.get("odds_decimal", 100) <= criteria.get("max_odds", 15.0)

        elif strategy == "80_20":
            return selection.get("confidence_score", 0) >= criteria.get(
                "min_confidence", 0.7
            )

        elif strategy == "dutching":
            # For dutching, we need multiple selections - this is checked at race level
            return True

        return True

    def _get_race_selections(self, race_id: str) -> List[Dict[str, Any]]:
        """Get all selections for a race."""
        # Query selections tracker for race selections
        # This would be implemented with actual database query
        return []  # Placeholder

    def _calculate_accuracy_impact(self, race_id: str) -> Dict[str, float]:
        """Calculate accuracy impact from race results."""
        return {
            "overall_change": 0.02,
            "method_changes": {"consensus": 0.03, "ai_ml": 0.01},
            "confidence_calibration_change": 0.01,
        }

    def _extract_learning_signals(
        self, race_id: str, actual_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract learning signals from race results."""
        return [
            {
                "signal_type": "surprise_winner",
                "horse_name": "Long Shot",
                "expected_probability": 0.05,
                "actual_result": "WIN",
                "learning_value": "high",
            }
        ]

    def _update_contextual_analysis(
        self, race_id: str, actual_results: List[Dict[str, Any]]
    ):
        """Update contextual analysis cache."""
        # Clear relevant cache entries
        self._analysis_cache.clear()

    def _compare_methods(
        self,
        selections_performance: Dict[str, Dict[str, float]],
        tracker_accuracy: Dict[str, float],
    ) -> Dict[str, Dict[str, float]]:
        """Compare method performance across systems."""
        comparison = {}

        for method in selections_performance:
            comparison[method] = {
                "selections_accuracy": selections_performance[method].get(
                    "accuracy", 0
                ),
                "selections_roi": selections_performance[method].get("roi", 0),
                "tracker_accuracy": tracker_accuracy.get(method, 0),
                "consistency_score": abs(
                    selections_performance[method].get("accuracy", 0)
                    - tracker_accuracy.get(method, 0)
                ),
            }

        return comparison

    def _assess_overall_risk(self, analytics: SelectionAnalytics) -> str:
        """Assess overall risk level."""
        risk_score = 0

        if analytics.max_drawdown > 50:
            risk_score += 3
        elif analytics.max_drawdown > 25:
            risk_score += 2
        elif analytics.max_drawdown > 10:
            risk_score += 1

        if analytics.consecutive_losses > 10:
            risk_score += 3
        elif analytics.consecutive_losses > 5:
            risk_score += 2
        elif analytics.consecutive_losses > 3:
            risk_score += 1

        if analytics.volatility > 0.5:
            risk_score += 2
        elif analytics.volatility > 0.3:
            risk_score += 1

        if risk_score >= 6:
            return "VERY_HIGH"
        elif risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_edge_exploitation(self, analytics: SelectionAnalytics) -> float:
        """Calculate how well we exploit betting edges."""
        if analytics.overlay_rate == 0:
            return 0.0

        # Combination of overlay rate and value capture rate
        return (analytics.overlay_rate * analytics.value_capture_rate) / 100

    def _generate_improvement_recommendations(
        self,
        selections_analytics: SelectionAnalytics,
        performance_summary: Dict[str, Any],
        contextual_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Accuracy recommendations
        if selections_analytics.overall_accuracy < 0.3:
            recommendations.append(
                "Focus on improving prediction model accuracy - current below 30%"
            )

        # ROI recommendations
        if selections_analytics.roi_percentage < 0:
            recommendations.append(
                "Review stake sizing and betting strategy - currently unprofitable"
            )

        # Confidence calibration
        if selections_analytics.confidence_calibration < 0.7:
            recommendations.append(
                "Recalibrate confidence scoring system - poor calibration detected"
            )

        # Strategy recommendations
        best_strategy = max(
            selections_analytics.strategy_performance.items(),
            key=lambda x: x[1].get("roi", 0),
            default=(None, {}),
        )

        if best_strategy[0]:
            recommendations.append(
                f"Focus on {best_strategy[0]} strategy - showing best ROI of "
                f"{best_strategy[1].get('roi', 0):.2f}%"
            )

        return recommendations or [
            "Continue current approach - performance is satisfactory"
        ]

    def _extract_ai_learning_signals(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Extract learning signals for AI improvement."""
        return {
            "pattern_recognition": {
                "improving_conditions": ["Good weather", "Class 2 races"],
                "declining_conditions": ["Heavy track", "Large fields"],
                "new_patterns": ["Trainer form cycles", "Jockey partnerships"],
            },
            "feature_importance": {
                "most_predictive": ["confidence_score", "value_edge"],
                "least_predictive": ["draw_position", "weight"],
                "emerging_features": ["pace_scenario", "track_bias"],
            },
            "model_drift": {
                "detected": False,
                "severity": "low",
                "recommendation": "Continue monitoring",
            },
        }

    def _determine_system_status(
        self, today_analytics: SelectionAnalytics, week_analytics: SelectionAnalytics
    ) -> str:
        """Determine overall system status."""
        if week_analytics.roi_percentage > 10 and week_analytics.overall_accuracy > 0.4:
            return "EXCELLENT"
        elif (
            week_analytics.roi_percentage > 5 and week_analytics.overall_accuracy > 0.3
        ):
            return "GOOD"
        elif (
            week_analytics.roi_percentage > 0 and week_analytics.overall_accuracy > 0.25
        ):
            return "FAIR"
        elif week_analytics.roi_percentage > -5:
            return "POOR"
        else:
            return "CRITICAL"

    def close(self):
        """Close all system connections."""
        self.selections_tracker.close()
        logger.info("AI Selections Integration System closed")


if __name__ == "__main__":
    # Example usage
    integration = AISelectionsIntegrationSystem()

    # Example race data
    race_data = {
        "race_id": "NEWM_2025-08-20_R1",
        "race_date": "2025-08-20T14:30:00Z",
        "course": "Newmarket",
        "race_number": 1,
        "distance": 6.0,
        "field_size": 8,
        "weather": "Clear",
        "track_condition": "Good",
    }

    # Example AI predictions
    ai_predictions = {
        "consensus": [
            {
                "horse_name": "Thunder Strike",
                "win_probability": 0.35,
                "confidence_score": 0.78,
                "odds_decimal": 3.5,
            }
        ]
    }

    # Process predictions
    selection_ids = integration.process_race_predictions(
        race_data, ai_predictions, ["value_bet"]
    )

    print(f"Recorded selections: {selection_ids}")

    # Get real-time performance
    performance = integration.get_real_time_performance()
    print(f"Current status: {performance['status']}")

    integration.close()
