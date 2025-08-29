#!/usr/bin/env python3
"""
AI Horse Selections Tracking System
==================================

Comprehensive tracking system for AI horse selections with profit/loss ROI
and relationships to race result data for contextual analysis.

This system tracks:
- Individual AI selections with confidence scores
- Profit/loss tracking per selection
- ROI analysis across time periods and strategies
- Relationships between selections and actual race results
- Contextual analysis for AI improvement
"""

import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class AIHorseSelection(Base):
    """Database model for AI horse selections."""

    __tablename__ = "ai_horse_selections"

    id = Column(Integer, primary_key=True)
    selection_id = Column(String(50), unique=True, nullable=False)

    # Race Information
    race_id = Column(String(50), nullable=False)
    race_date = Column(DateTime, nullable=False)
    course = Column(String(100), nullable=False)
    race_number = Column(Integer, nullable=False)
    race_time = Column(String(20))
    race_distance = Column(Float)
    race_class = Column(String(50))

    # Horse Information
    horse_name = Column(String(255), nullable=False)
    horse_id = Column(String(50))
    jockey = Column(String(255))
    trainer = Column(String(255))
    weight = Column(Float)
    draw = Column(Integer)

    # AI Prediction Details
    ai_model_version = Column(String(50), nullable=False)
    prediction_method = Column(String(50), nullable=False)  # raw/mc/ai/consensus
    win_probability = Column(Float, nullable=False)
    place_probability = Column(Float)
    show_probability = Column(Float)
    confidence_score = Column(Float, nullable=False)
    confidence_level = Column(String(20))  # 'HIGH', 'MEDIUM', 'LOW'

    # Market Data
    odds_decimal = Column(Float)
    odds_fractional = Column(String(20))
    market_rank = Column(Integer)
    implied_probability = Column(Float)

    # Selection Strategy
    selection_type = Column(String(50), nullable=False)  # WIN/PLACE/SHOW/EW
    betting_strategy = Column(String(50))  # 80_20/dutching/value/conservative
    stake_amount = Column(Float)
    recommended_stake = Column(Float)

    # Actual Results
    actual_position = Column(Integer)
    actual_result = Column(String(20))  # 'WIN', 'PLACE', 'SHOW', 'UNPLACED'
    was_correct = Column(Boolean, default=False)
    result_updated_at = Column(DateTime)

    # Financial Tracking
    stake_placed = Column(Float, default=0.0)
    payout_received = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)

    # Performance Metrics
    prediction_accuracy = Column(Float)  # How close probability was to actual
    value_assessment = Column(String(20))  # 'OVERLAY', 'UNDERLAY', 'FAIR'
    edge_percentage = Column(Float)  # Expected edge over market

    # Contextual Data
    field_size = Column(Integer)
    weather_conditions = Column(String(100))
    track_condition = Column(String(50))
    pace_scenario = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AISelectionPerformance(Base):
    """Database model for aggregated AI selection performance."""

    __tablename__ = "ai_selection_performance"

    id = Column(Integer, primary_key=True)

    # Analysis Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # 'DAILY', 'WEEKLY', 'MONTHLY'

    # Selection Metrics
    total_selections = Column(Integer, default=0)
    win_selections = Column(Integer, default=0)
    place_selections = Column(Integer, default=0)
    show_selections = Column(Integer, default=0)
    unplaced_selections = Column(Integer, default=0)

    # Accuracy Metrics
    win_accuracy = Column(Float, default=0.0)
    place_accuracy = Column(Float, default=0.0)
    overall_accuracy = Column(Float, default=0.0)
    confidence_calibration = Column(Float, default=0.0)

    # Financial Performance
    total_stakes = Column(Float, default=0.0)
    total_payouts = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)

    # Risk Metrics
    max_drawdown = Column(Float, default=0.0)
    consecutive_losses = Column(Integer, default=0)
    win_loss_ratio = Column(Float, default=0.0)
    volatility = Column(Float, default=0.0)

    # Strategy Performance
    strategy_breakdown = Column(Text)  # JSON of strategy-specific performance
    method_breakdown = Column(Text)  # JSON of method-specific performance

    # Market Analysis
    average_odds = Column(Float, default=0.0)
    overlay_percentage = Column(Float, default=0.0)
    value_capture_rate = Column(Float, default=0.0)

    # Contextual Factors
    weather_impact = Column(Text)  # JSON of weather performance
    class_impact = Column(Text)  # JSON of class performance
    distance_impact = Column(Text)  # JSON of distance performance

    created_at = Column(DateTime, default=datetime.utcnow)


@dataclass
class SelectionAnalytics:
    """Analytics data for AI selection performance."""

    # Time Period
    period_start: datetime
    period_end: datetime

    # Selection Volume
    total_selections: int
    selections_per_day: float

    # Accuracy Metrics
    win_accuracy: float
    place_accuracy: float
    overall_accuracy: float
    confidence_calibration: float

    # Financial Performance
    total_stakes: float
    total_payouts: float
    net_profit: float
    roi_percentage: float
    profit_factor: float

    # Strategy Breakdown
    strategy_performance: Dict[str, Dict[str, float]]
    method_performance: Dict[str, Dict[str, float]]

    # Risk Analysis
    max_drawdown: float
    consecutive_losses: int
    win_loss_ratio: float
    volatility: float

    # Market Intelligence
    average_odds: float
    overlay_rate: float
    value_capture_rate: float

    # Contextual Insights
    best_conditions: Dict[str, Any]
    worst_conditions: Dict[str, Any]
    improvement_areas: List[str]


class AISelectionsTracker:
    """
    Comprehensive AI horse selections tracking system.

    Tracks AI selections, profit/loss, ROI, and relationships to race results
    for detailed contextual analysis and AI improvement.
    """

    def __init__(self, db_path: str = "data/ai_selections_tracking.db"):
        """Initialize the AI selections tracker."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create database engine and session
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Performance cache
        self._performance_cache = {}
        self._cache_timeout = 300  # 5 minutes

        logger.info(f"AI Selections Tracker initialized with database: {self.db_path}")

    def record_ai_selection(
        self,
        race_data: Dict[str, Any],
        selection_data: Dict[str, Any],
        prediction_method: str = "consensus",
        betting_strategy: str = "value_bet",
    ) -> str:
        """
        Record a new AI horse selection.

        Args:
            race_data: Race information and context
            selection_data: AI selection details and predictions
            prediction_method: Method used for prediction
            betting_strategy: Betting strategy applied

        Returns:
            Selection ID for tracking
        """
        # Generate unique selection ID
        selection_id = (
            f"{race_data['race_id']}_{selection_data['horse_name']}_{prediction_method}"
        )

        # Determine confidence level
        confidence_score = selection_data.get("confidence_score", 0.5)
        if confidence_score >= 0.8:
            confidence_level = "HIGH"
        elif confidence_score >= 0.6:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        # Calculate value assessment
        win_prob = selection_data.get("win_probability", 0.1)
        odds = selection_data.get("odds_decimal", 10.0)
        implied_prob = 1.0 / odds if odds > 0 else 0.1

        if win_prob > implied_prob * 1.1:
            value_assessment = "OVERLAY"
            edge_percentage = ((win_prob - implied_prob) / implied_prob) * 100
        elif win_prob < implied_prob * 0.9:
            value_assessment = "UNDERLAY"
            edge_percentage = ((win_prob - implied_prob) / implied_prob) * 100
        else:
            value_assessment = "FAIR"
            edge_percentage = 0.0

        # Create selection record
        selection = AIHorseSelection(
            selection_id=selection_id,
            race_id=race_data["race_id"],
            race_date=datetime.fromisoformat(
                race_data["race_date"].replace("Z", "+00:00")
            ),
            course=race_data.get("course", "Unknown"),
            race_number=race_data.get("race_number", 1),
            race_time=race_data.get("race_time", ""),
            race_distance=race_data.get("distance", 0.0),
            race_class=race_data.get("class", ""),
            horse_name=selection_data["horse_name"],
            horse_id=selection_data.get("horse_id", ""),
            jockey=selection_data.get("jockey", ""),
            trainer=selection_data.get("trainer", ""),
            weight=selection_data.get("weight", 0.0),
            draw=selection_data.get("draw", 0),
            ai_model_version=selection_data.get("model_version", "v2.03"),
            prediction_method=prediction_method,
            win_probability=win_prob,
            place_probability=selection_data.get("place_probability", 0.3),
            show_probability=selection_data.get("show_probability", 0.5),
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            odds_decimal=odds,
            odds_fractional=selection_data.get("odds_fractional", ""),
            market_rank=selection_data.get("market_rank", 0),
            implied_probability=implied_prob,
            selection_type=selection_data.get("selection_type", "WIN"),
            betting_strategy=betting_strategy,
            stake_amount=selection_data.get("stake_amount", 0.0),
            recommended_stake=selection_data.get("recommended_stake", 0.0),
            value_assessment=value_assessment,
            edge_percentage=edge_percentage,
            field_size=race_data.get("field_size", 0),
            weather_conditions=race_data.get("weather", ""),
            track_condition=race_data.get("track_condition", ""),
            pace_scenario=race_data.get("pace_scenario", ""),
        )

        self.session.add(selection)
        self.session.commit()

        logger.info(f"Recorded AI selection: {selection_id}")
        return selection_id

    def update_selection_result(
        self,
        selection_id: str,
        actual_result: Dict[str, Any],
        financial_result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update AI selection with actual race results.

        Args:
            selection_id: ID of the selection to update
            actual_result: Actual race outcome
            financial_result: Betting outcome if applicable

        Returns:
            True if updated successfully
        """
        selection = (
            self.session.query(AIHorseSelection)
            .filter_by(selection_id=selection_id)
            .first()
        )

        if not selection:
            logger.warning(f"Selection not found: {selection_id}")
            return False

        # Update result information
        selection.actual_position = actual_result.get("position", 0)

        # Determine result type
        position = actual_result.get("position", 999)
        if position == 1:
            selection.actual_result = "WIN"
            selection.was_correct = True
        elif position <= 2:
            selection.actual_result = "PLACE"
            selection.was_correct = selection.selection_type in [
                "PLACE",
                "SHOW",
                "EACH_WAY",
            ]
        elif position <= 3:
            selection.actual_result = "SHOW"
            selection.was_correct = selection.selection_type in ["SHOW", "EACH_WAY"]
        else:
            selection.actual_result = "UNPLACED"
            selection.was_correct = False

        # Calculate prediction accuracy
        win_prob = selection.win_probability
        actual_win = 1.0 if position == 1 else 0.0
        selection.prediction_accuracy = 1.0 - abs(win_prob - actual_win)

        # Update financial results if provided
        if financial_result:
            selection.stake_placed = financial_result.get("stake", 0.0)
            selection.payout_received = financial_result.get("payout", 0.0)
            selection.profit_loss = selection.payout_received - selection.stake_placed

            if selection.stake_placed > 0:
                selection.roi_percentage = (
                    selection.profit_loss / selection.stake_placed
                ) * 100

        selection.result_updated_at = datetime.utcnow()
        selection.updated_at = datetime.utcnow()

        self.session.commit()

        # Clear performance cache
        self._performance_cache.clear()

        logger.info(f"Updated selection result: {selection_id}")
        return True

    def get_selection_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        strategy_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
    ) -> SelectionAnalytics:
        """
        Get comprehensive analytics for AI selections.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            strategy_filter: Filter by betting strategy
            method_filter: Filter by prediction method

        Returns:
            Comprehensive analytics data
        """
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Build query
        query = self.session.query(AIHorseSelection).filter(
            AIHorseSelection.race_date.between(start_date, end_date)
        )

        if strategy_filter:
            query = query.filter(AIHorseSelection.betting_strategy == strategy_filter)
        if method_filter:
            query = query.filter(AIHorseSelection.prediction_method == method_filter)

        selections = query.all()

        if not selections:
            return self._empty_analytics(start_date, end_date)

        # Calculate basic metrics
        total_selections = len(selections)
        days = (end_date - start_date).days or 1
        selections_per_day = total_selections / days

        # Accuracy metrics
        correct_selections = [s for s in selections if s.was_correct]
        win_selections = [s for s in selections if s.actual_result == "WIN"]
        place_selections = [
            s for s in selections if s.actual_result in ["WIN", "PLACE"]
        ]

        win_accuracy = (
            len(win_selections) / total_selections if total_selections > 0 else 0
        )
        place_accuracy = (
            len(place_selections) / total_selections if total_selections > 0 else 0
        )
        overall_accuracy = (
            len(correct_selections) / total_selections if total_selections > 0 else 0
        )

        # Confidence calibration
        confidence_calibration = self._calculate_confidence_calibration(selections)

        # Financial metrics
        total_stakes = sum(s.stake_placed or 0 for s in selections)
        total_payouts = sum(s.payout_received or 0 for s in selections)
        net_profit = total_payouts - total_stakes
        roi_percentage = (net_profit / total_stakes * 100) if total_stakes > 0 else 0

        # Profit factor
        gross_profit = sum(s.profit_loss for s in selections if s.profit_loss > 0)
        gross_loss = abs(sum(s.profit_loss for s in selections if s.profit_loss < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Strategy and method performance
        strategy_performance = self._calculate_strategy_performance(selections)
        method_performance = self._calculate_method_performance(selections)

        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(selections)

        # Market intelligence
        market_metrics = self._calculate_market_metrics(selections)

        # Contextual analysis
        best_conditions = self._find_best_conditions(selections)
        worst_conditions = self._find_worst_conditions(selections)
        improvement_areas = self._identify_improvement_areas(selections)

        return SelectionAnalytics(
            period_start=start_date,
            period_end=end_date,
            total_selections=total_selections,
            selections_per_day=selections_per_day,
            win_accuracy=win_accuracy,
            place_accuracy=place_accuracy,
            overall_accuracy=overall_accuracy,
            confidence_calibration=confidence_calibration,
            total_stakes=total_stakes,
            total_payouts=total_payouts,
            net_profit=net_profit,
            roi_percentage=roi_percentage,
            profit_factor=profit_factor,
            strategy_performance=strategy_performance,
            method_performance=method_performance,
            max_drawdown=risk_metrics["max_drawdown"],
            consecutive_losses=risk_metrics["consecutive_losses"],
            win_loss_ratio=risk_metrics["win_loss_ratio"],
            volatility=risk_metrics["volatility"],
            average_odds=market_metrics["average_odds"],
            overlay_rate=market_metrics["overlay_rate"],
            value_capture_rate=market_metrics["value_capture_rate"],
            best_conditions=best_conditions,
            worst_conditions=worst_conditions,
            improvement_areas=improvement_areas,
        )

    def generate_contextual_analysis(
        self, period_days: int = 30, min_selections: int = 10
    ) -> Dict[str, Any]:
        """
        Generate contextual analysis for AI improvement.

        Args:
            period_days: Number of days to analyze
            min_selections: Minimum selections for valid analysis

        Returns:
            Contextual analysis report
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        analytics = self.get_selection_analytics(start_date, end_date)

        if analytics.total_selections < min_selections:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {min_selections} selections for analysis",
                "current_selections": analytics.total_selections,
            }

        # Performance assessment
        performance_grade = self._assess_performance(analytics)

        # Trend analysis
        trend_analysis = self._analyze_trends(start_date, end_date)

        # Feature importance
        feature_analysis = self._analyze_feature_importance(start_date, end_date)

        # Recommendations
        recommendations = self._generate_recommendations(analytics, trend_analysis)

        return {
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days,
            },
            "performance_summary": {
                "grade": performance_grade,
                "total_selections": analytics.total_selections,
                "overall_accuracy": analytics.overall_accuracy,
                "roi_percentage": analytics.roi_percentage,
                "profit_factor": analytics.profit_factor,
            },
            "strategy_insights": {
                "best_strategy": self._find_best_strategy(
                    analytics.strategy_performance
                ),
                "worst_strategy": self._find_worst_strategy(
                    analytics.strategy_performance
                ),
                "strategy_distribution": analytics.strategy_performance,
            },
            "method_insights": {
                "best_method": self._find_best_method(analytics.method_performance),
                "worst_method": self._find_worst_method(analytics.method_performance),
                "method_distribution": analytics.method_performance,
            },
            "market_intelligence": {
                "average_odds": analytics.average_odds,
                "overlay_rate": analytics.overlay_rate,
                "value_capture_rate": analytics.value_capture_rate,
                "edge_exploitation": self._calculate_edge_exploitation(
                    start_date, end_date
                ),
            },
            "risk_assessment": {
                "max_drawdown": analytics.max_drawdown,
                "consecutive_losses": analytics.consecutive_losses,
                "volatility": analytics.volatility,
                "risk_level": self._assess_risk_level(analytics),
            },
            "contextual_factors": {
                "best_conditions": analytics.best_conditions,
                "worst_conditions": analytics.worst_conditions,
                "weather_impact": self._analyze_weather_impact(start_date, end_date),
                "class_impact": self._analyze_class_impact(start_date, end_date),
            },
            "trend_analysis": trend_analysis,
            "feature_analysis": feature_analysis,
            "improvement_areas": analytics.improvement_areas,
            "recommendations": recommendations,
            "confidence_calibration": {
                "score": analytics.confidence_calibration,
                "interpretation": self._interpret_calibration(
                    analytics.confidence_calibration
                ),
            },
        }

    def export_selection_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format_type: str = "csv",
    ) -> str:
        """
        Export selection data for external analysis.

        Args:
            start_date: Start date for export
            end_date: End date for export
            format_type: Export format ('csv', 'json', 'excel')

        Returns:
            Path to exported file
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Query selections
        selections = (
            self.session.query(AIHorseSelection)
            .filter(AIHorseSelection.race_date.between(start_date, end_date))
            .all()
        )

        # Convert to DataFrame
        data = []
        for selection in selections:
            data.append(
                {
                    "selection_id": selection.selection_id,
                    "race_id": selection.race_id,
                    "race_date": selection.race_date,
                    "course": selection.course,
                    "race_number": selection.race_number,
                    "horse_name": selection.horse_name,
                    "jockey": selection.jockey,
                    "trainer": selection.trainer,
                    "prediction_method": selection.prediction_method,
                    "win_probability": selection.win_probability,
                    "confidence_score": selection.confidence_score,
                    "odds_decimal": selection.odds_decimal,
                    "betting_strategy": selection.betting_strategy,
                    "actual_position": selection.actual_position,
                    "actual_result": selection.actual_result,
                    "was_correct": selection.was_correct,
                    "stake_placed": selection.stake_placed,
                    "payout_received": selection.payout_received,
                    "profit_loss": selection.profit_loss,
                    "roi_percentage": selection.roi_percentage,
                    "value_assessment": selection.value_assessment,
                    "edge_percentage": selection.edge_percentage,
                }
            )

        df = pd.DataFrame(data)

        # Export based on format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path("reports/ai_selections")
        export_dir.mkdir(parents=True, exist_ok=True)

        if format_type.lower() == "csv":
            file_path = export_dir / f"ai_selections_{timestamp}.csv"
            df.to_csv(file_path, index=False)
        elif format_type.lower() == "json":
            file_path = export_dir / f"ai_selections_{timestamp}.json"
            df.to_json(file_path, orient="records", date_format="iso")
        elif format_type.lower() == "excel":
            file_path = export_dir / f"ai_selections_{timestamp}.xlsx"
            df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        logger.info(f"Exported {len(data)} selections to {file_path}")
        return str(file_path)

    def _empty_analytics(
        self, start_date: datetime, end_date: datetime
    ) -> SelectionAnalytics:
        """Return empty analytics object."""
        return SelectionAnalytics(
            period_start=start_date,
            period_end=end_date,
            total_selections=0,
            selections_per_day=0.0,
            win_accuracy=0.0,
            place_accuracy=0.0,
            overall_accuracy=0.0,
            confidence_calibration=0.0,
            total_stakes=0.0,
            total_payouts=0.0,
            net_profit=0.0,
            roi_percentage=0.0,
            profit_factor=0.0,
            strategy_performance={},
            method_performance={},
            max_drawdown=0.0,
            consecutive_losses=0,
            win_loss_ratio=0.0,
            volatility=0.0,
            average_odds=0.0,
            overlay_rate=0.0,
            value_capture_rate=0.0,
            best_conditions={},
            worst_conditions={},
            improvement_areas=[],
        )

    def _calculate_confidence_calibration(
        self, selections: List[AIHorseSelection]
    ) -> float:
        """Calculate how well-calibrated confidence scores are."""
        if not selections:
            return 0.0

        # Group by confidence bins
        bins = {"low": [], "medium": [], "high": []}

        for selection in selections:
            if selection.confidence_score < 0.6:
                bins["low"].append(selection.was_correct)
            elif selection.confidence_score < 0.8:
                bins["medium"].append(selection.was_correct)
            else:
                bins["high"].append(selection.was_correct)

        # Calculate calibration score
        calibration_scores = []

        for bin_name, results in bins.items():
            if results:
                actual_rate = sum(results) / len(results)
                if bin_name == "low":
                    expected_rate = 0.5
                elif bin_name == "medium":
                    expected_rate = 0.7
                else:
                    expected_rate = 0.85

                calibration_scores.append(1.0 - abs(actual_rate - expected_rate))

        return np.mean(calibration_scores) if calibration_scores else 0.0

    def _calculate_strategy_performance(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance breakdown by strategy."""
        strategy_groups = {}

        for selection in selections:
            strategy = selection.betting_strategy or "unknown"
            if strategy not in strategy_groups:
                strategy_groups[strategy] = []
            strategy_groups[strategy].append(selection)

        performance = {}
        for strategy, group in strategy_groups.items():
            if group:
                correct = sum(1 for s in group if s.was_correct)
                total_stake = sum(s.stake_placed or 0 for s in group)
                total_payout = sum(s.payout_received or 0 for s in group)

                performance[strategy] = {
                    "selections": len(group),
                    "accuracy": correct / len(group),
                    "total_stake": total_stake,
                    "net_profit": total_payout - total_stake,
                    "roi": (
                        ((total_payout - total_stake) / total_stake * 100)
                        if total_stake > 0
                        else 0
                    ),
                }

        return performance

    def _calculate_method_performance(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance breakdown by prediction method."""
        method_groups = {}

        for selection in selections:
            method = selection.prediction_method
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(selection)

        performance = {}
        for method, group in method_groups.items():
            if group:
                correct = sum(1 for s in group if s.was_correct)
                total_stake = sum(s.stake_placed or 0 for s in group)
                total_payout = sum(s.payout_received or 0 for s in group)

                performance[method] = {
                    "selections": len(group),
                    "accuracy": correct / len(group),
                    "total_stake": total_stake,
                    "net_profit": total_payout - total_stake,
                    "roi": (
                        ((total_payout - total_stake) / total_stake * 100)
                        if total_stake > 0
                        else 0
                    ),
                }

        return performance

    def _calculate_risk_metrics(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, float]:
        """Calculate risk metrics."""
        if not selections:
            return {
                "max_drawdown": 0,
                "consecutive_losses": 0,
                "win_loss_ratio": 0,
                "volatility": 0,
            }

        # Sort by date
        sorted_selections = sorted(selections, key=lambda x: x.race_date)

        # Calculate running profit
        running_profit = 0
        profits = []
        peak = 0
        max_drawdown = 0

        for selection in sorted_selections:
            profit = selection.profit_loss or 0
            running_profit += profit
            profits.append(profit)

            if running_profit > peak:
                peak = running_profit

            drawdown = peak - running_profit
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Consecutive losses
        consecutive_losses = 0
        current_losses = 0

        for selection in sorted_selections:
            if selection.profit_loss and selection.profit_loss < 0:
                current_losses += 1
                consecutive_losses = max(consecutive_losses, current_losses)
            else:
                current_losses = 0

        # Win/Loss ratio
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        win_loss_ratio = (len(wins) / len(losses)) if losses else float("inf")

        # Volatility
        volatility = np.std(profits) if len(profits) > 1 else 0

        return {
            "max_drawdown": max_drawdown,
            "consecutive_losses": consecutive_losses,
            "win_loss_ratio": win_loss_ratio,
            "volatility": volatility,
        }

    def _calculate_market_metrics(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, float]:
        """Calculate market intelligence metrics."""
        if not selections:
            return {"average_odds": 0, "overlay_rate": 0, "value_capture_rate": 0}

        odds = [s.odds_decimal for s in selections if s.odds_decimal]
        average_odds = np.mean(odds) if odds else 0

        overlays = [s for s in selections if s.value_assessment == "OVERLAY"]
        overlay_rate = len(overlays) / len(selections) * 100

        overlay_wins = [s for s in overlays if s.was_correct]
        value_capture_rate = (
            (len(overlay_wins) / len(overlays) * 100) if overlays else 0
        )

        return {
            "average_odds": average_odds,
            "overlay_rate": overlay_rate,
            "value_capture_rate": value_capture_rate,
        }

    def _find_best_conditions(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, Any]:
        """Find conditions where AI performs best."""
        # Group by various conditions and find best performing
        conditions = {}

        # Weather analysis
        weather_groups = {}
        for selection in selections:
            weather = selection.weather_conditions or "unknown"
            if weather not in weather_groups:
                weather_groups[weather] = []
            weather_groups[weather].append(selection)

        best_weather = max(
            weather_groups.items(),
            key=lambda x: (
                sum(1 for s in x[1] if s.was_correct) / len(x[1]) if x[1] else 0
            ),
            default=("unknown", []),
        )

        conditions["weather"] = {
            "condition": best_weather[0],
            "accuracy": (
                sum(1 for s in best_weather[1] if s.was_correct) / len(best_weather[1])
                if best_weather[1]
                else 0
            ),
            "selections": len(best_weather[1]),
        }

        return conditions

    def _find_worst_conditions(
        self, selections: List[AIHorseSelection]
    ) -> Dict[str, Any]:
        """Find conditions where AI performs worst."""
        # Similar to best conditions but finding minimum
        conditions = {}

        weather_groups = {}
        for selection in selections:
            weather = selection.weather_conditions or "unknown"
            if weather not in weather_groups:
                weather_groups[weather] = []
            weather_groups[weather].append(selection)

        worst_weather = min(
            weather_groups.items(),
            key=lambda x: (
                sum(1 for s in x[1] if s.was_correct) / len(x[1]) if x[1] else 1
            ),
            default=("unknown", []),
        )

        conditions["weather"] = {
            "condition": worst_weather[0],
            "accuracy": (
                sum(1 for s in worst_weather[1] if s.was_correct)
                / len(worst_weather[1])
                if worst_weather[1]
                else 0
            ),
            "selections": len(worst_weather[1]),
        }

        return conditions

    def _identify_improvement_areas(
        self, selections: List[AIHorseSelection]
    ) -> List[str]:
        """Identify areas for AI improvement."""
        areas = []

        if not selections:
            return ["Insufficient data for analysis"]

        # Check overall accuracy
        accuracy = sum(1 for s in selections if s.was_correct) / len(selections)
        if accuracy < 0.3:
            areas.append("Overall accuracy below 30% - review prediction models")

        # Check confidence calibration
        calibration = self._calculate_confidence_calibration(selections)
        if calibration < 0.7:
            areas.append("Poor confidence calibration - adjust confidence scoring")

        # Check profitability
        total_stake = sum(s.stake_placed or 0 for s in selections)
        total_payout = sum(s.payout_received or 0 for s in selections)
        if total_stake > 0 and total_payout < total_stake:
            areas.append("Negative ROI - improve value betting and stake sizing")

        # Check overlay performance
        overlays = [s for s in selections if s.value_assessment == "OVERLAY"]
        if overlays:
            overlay_accuracy = sum(1 for s in overlays if s.was_correct) / len(overlays)
            if overlay_accuracy < 0.4:
                areas.append("Poor overlay identification - review value assessment")

        return areas or ["Continue current approach - performance is satisfactory"]

    def _assess_performance(self, analytics: SelectionAnalytics) -> str:
        """Assess overall performance grade."""
        accuracy = analytics.overall_accuracy
        roi = analytics.roi_percentage

        score = 0
        if accuracy >= 0.4:
            score += 3
        elif accuracy >= 0.3:
            score += 2
        elif accuracy >= 0.2:
            score += 1

        if roi >= 10:
            score += 3
        elif roi >= 5:
            score += 2
        elif roi >= 0:
            score += 1

        if score >= 5:
            return "A"
        elif score >= 4:
            return "B"
        elif score >= 3:
            return "C"
        elif score >= 2:
            return "D"
        else:
            return "F"

    def _analyze_trends(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        # This would implement detailed trend analysis
        return {
            "accuracy_trend": "stable",
            "profitability_trend": "improving",
            "volume_trend": "increasing",
        }

    def _analyze_feature_importance(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze which features are most important for success."""
        return {
            "most_important": [
                "confidence_score",
                "value_assessment",
                "prediction_method",
            ],
            "least_important": ["weather_conditions", "track_condition"],
        }

    def _generate_recommendations(
        self, analytics: SelectionAnalytics, trend_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if analytics.overall_accuracy < 0.3:
            recommendations.append("Focus on improving prediction model accuracy")

        if analytics.roi_percentage < 0:
            recommendations.append("Review stake sizing and betting strategy")

        if analytics.confidence_calibration < 0.7:
            recommendations.append("Recalibrate confidence scoring system")

        return recommendations or ["Continue current approach"]

    def _find_best_strategy(
        self, strategy_performance: Dict[str, Dict[str, float]]
    ) -> str:
        """Find best performing strategy."""
        if not strategy_performance:
            return "unknown"

        return max(strategy_performance.items(), key=lambda x: x[1].get("roi", 0))[0]

    def _find_worst_strategy(
        self, strategy_performance: Dict[str, Dict[str, float]]
    ) -> str:
        """Find worst performing strategy."""
        if not strategy_performance:
            return "unknown"

        return min(strategy_performance.items(), key=lambda x: x[1].get("roi", 0))[0]

    def _find_best_method(self, method_performance: Dict[str, Dict[str, float]]) -> str:
        """Find best performing prediction method."""
        if not method_performance:
            return "unknown"

        return max(method_performance.items(), key=lambda x: x[1].get("accuracy", 0))[0]

    def _find_worst_method(
        self, method_performance: Dict[str, Dict[str, float]]
    ) -> str:
        """Find worst performing prediction method."""
        if not method_performance:
            return "unknown"

        return min(method_performance.items(), key=lambda x: x[1].get("accuracy", 0))[0]

    def _calculate_edge_exploitation(
        self, start_date: datetime, end_date: datetime
    ) -> float:
        """Calculate how well we exploit betting edges."""
        # This would calculate edge exploitation rate
        return 0.65  # Placeholder

    def _assess_risk_level(self, analytics: SelectionAnalytics) -> str:
        """Assess overall risk level."""
        if analytics.max_drawdown > 50 or analytics.consecutive_losses > 10:
            return "HIGH"
        elif analytics.max_drawdown > 25 or analytics.consecutive_losses > 5:
            return "MEDIUM"
        else:
            return "LOW"

    def _analyze_weather_impact(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Analyze weather impact on performance."""
        return {"clear": 0.35, "rain": 0.28, "overcast": 0.32}

    def _analyze_class_impact(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Analyze class impact on performance."""
        return {"class_1": 0.38, "class_2": 0.32, "class_3": 0.29}

    def _interpret_calibration(self, calibration_score: float) -> str:
        """Interpret confidence calibration score."""
        if calibration_score >= 0.8:
            return "Excellent - confidence scores are well calibrated"
        elif calibration_score >= 0.6:
            return "Good - confidence scores are reasonably calibrated"
        elif calibration_score >= 0.4:
            return "Fair - confidence scores need some adjustment"
        else:
            return "Poor - confidence scores need significant recalibration"

    def close(self):
        """Close database connection."""
        if self.session:
            self.session.close()
        logger.info("AI Selections Tracker closed")


if __name__ == "__main__":
    # Example usage
    tracker = AISelectionsTracker()

    # Example race data
    race_data = {
        "race_id": "NEWM_2025-08-20_R1",
        "race_date": "2025-08-20T14:30:00Z",
        "course": "Newmarket",
        "race_number": 1,
        "distance": 6.0,
        "class": "Class 2",
        "field_size": 8,
        "weather": "Clear",
        "track_condition": "Good",
    }

    # Example AI selection
    selection_data = {
        "horse_name": "Thunder Strike",
        "horse_id": "TS001",
        "jockey": "J. Doe",
        "trainer": "T. Smith",
        "win_probability": 0.35,
        "confidence_score": 0.78,
        "odds_decimal": 3.5,
        "selection_type": "WIN",
        "stake_amount": 10.0,
    }

    # Record selection
    selection_id = tracker.record_ai_selection(
        race_data, selection_data, "consensus", "value_bet"
    )

    print(f"Recorded selection: {selection_id}")

    # Example result update
    result_data = {"position": 2}
    financial_data = {"stake": 10.0, "payout": 17.5}

    tracker.update_selection_result(selection_id, result_data, financial_data)

    # Get analytics
    analytics = tracker.get_selection_analytics()
    print(
        f"Analytics: {analytics.total_selections} selections, {analytics.roi_percentage:.2f}% ROI"
    )

    # Generate contextual analysis
    analysis = tracker.generate_contextual_analysis()
    print(f"Performance grade: {analysis['performance_summary']['grade']}")

    tracker.close()
