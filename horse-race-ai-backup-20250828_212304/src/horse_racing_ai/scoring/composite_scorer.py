"""
Composite Scoring System for Horse Racing
========================================

Combines form analysis and power ratings with additional scoring factors
for comprehensive horse evaluation.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import structlog

from .form_analyzer import EnhancedFormAnalyzer, FormMetrics, RacePerformance
from .power_ratings import PowerRating, PowerRatingSystem

logger = structlog.get_logger(__name__)


@dataclass
class CompositeScore:
    """Complete composite scoring result."""

    horse_name: str

    # Core scores
    form_score: float  # 0-100
    power_rating: float  # 0-150
    composite_score: float  # 0-100 final score

    # Component breakdowns
    speed_score: float
    class_score: float
    consistency_score: float
    form_trend_score: float
    conditions_score: float

    # Probability and confidence
    win_probability: float
    place_probability: float
    show_probability: float
    confidence_level: float

    # Rankings
    composite_rank: int
    power_rating_rank: int
    form_rank: int

    # Additional insights
    key_factors: List[str]
    concerns: List[str]
    betting_value: float  # Value assessment vs odds

    # Detailed breakdown
    factors_breakdown: Dict[str, float]


@dataclass
class RaceAnalysis:
    """Complete race analysis with all horses."""

    race_id: str
    race_conditions: Dict[str, Any]
    horse_scores: List[CompositeScore]
    race_insights: Dict[str, Any]
    pace_scenario: str
    track_bias: str
    key_angles: List[str]


class CompositeScorer:
    """
    Advanced composite scoring system that combines multiple analysis methods.

    Features:
    - Form analysis integration
    - Power rating calculations
    - Value assessment vs betting odds
    - Pace scenario analysis
    - Track bias considerations
    - Confidence-weighted scoring
    - Multi-factor rankings
    """

    def __init__(self):
        """Initialize the composite scoring system."""
        self.form_analyzer = EnhancedFormAnalyzer()
        self.power_rating_system = PowerRatingSystem()
        self._initialize_scoring_weights()

    def _initialize_scoring_weights(self) -> None:
        """Initialize weights for composite score calculation."""
        self.composite_weights = {
            "power_rating": 0.40,  # Primary rating system
            "form_score": 0.25,  # Recent form emphasis
            "speed_score": 0.15,  # Speed figures
            "class_score": 0.10,  # Class analysis
            "conditions_score": 0.10,  # Track/distance suitability
        }

    def score_race(
        self,
        race_data: Dict[str, Any],
        horses_data: Dict[str, List[RacePerformance]],
        betting_odds: Optional[Dict[str, float]] = None,
    ) -> RaceAnalysis:
        """
        Score all horses in a race with comprehensive analysis.

        Args:
            race_data: Race conditions and metadata
            horses_data: Historical performance data for each horse
            betting_odds: Current betting odds for value assessment

        Returns:
            Complete race analysis with horse scores and insights
        """
        logger.info(f"Scoring race: {race_data.get('race_id', 'Unknown')}")

        horse_scores = []

        for horse_name, performances in horses_data.items():
            # Calculate individual horse score
            score = self.score_horse(
                horse_name=horse_name,
                performances=performances,
                race_conditions=race_data,
                betting_odds=betting_odds.get(horse_name) if betting_odds else None,
            )
            horse_scores.append(score)

        # Sort by composite score
        horse_scores.sort(key=lambda x: x.composite_score, reverse=True)

        # Assign rankings
        self._assign_rankings(horse_scores)

        # Calculate probabilities
        self._calculate_win_probabilities(horse_scores)

        # Analyze race dynamics
        race_insights = self._analyze_race_dynamics(horse_scores, race_data)

        return RaceAnalysis(
            race_id=race_data.get("race_id", "unknown"),
            race_conditions=race_data,
            horse_scores=horse_scores,
            race_insights=race_insights,
            pace_scenario=race_insights.get("pace_scenario", "moderate"),
            track_bias=race_insights.get("track_bias", "neutral"),
            key_angles=race_insights.get("key_angles", []),
        )

    def score_horse(
        self,
        horse_name: str,
        performances: List[RacePerformance],
        race_conditions: Dict[str, Any],
        betting_odds: Optional[float] = None,
        additional_factors: Optional[Dict[str, Any]] = None,
    ) -> CompositeScore:
        """
        Generate comprehensive score for a single horse.

        Args:
            horse_name: Name of the horse
            performances: Historical race performances
            race_conditions: Upcoming race conditions
            betting_odds: Current betting odds
            additional_factors: Equipment changes, layoffs, etc.

        Returns:
            Complete composite score with breakdown
        """
        logger.debug(f"Scoring horse: {horse_name}")

        if not performances:
            return self._default_composite_score(horse_name)

        # Get form analysis
        form_metrics = self.form_analyzer.analyze_horse_form(
            horse_name, performances, race_conditions
        )

        # Get power rating
        power_rating = self.power_rating_system.calculate_power_rating(
            horse_name, performances, race_conditions, additional_factors
        )

        # Calculate component scores
        speed_score = self._calculate_speed_score(form_metrics, power_rating)
        class_score = self._calculate_class_score(form_metrics, power_rating)
        consistency_score = self._calculate_consistency_score(form_metrics)
        form_trend_score = self._calculate_form_trend_score(form_metrics)
        conditions_score = self._calculate_conditions_score(
            form_metrics, race_conditions
        )

        # Calculate form score (0-100)
        form_score = (
            form_metrics.recent_form_score * 40
            + form_metrics.consistency_index * 30
            + form_metrics.condition_suitability * 30
        )

        # Calculate composite score
        composite_score = self._calculate_composite_score(
            {
                "power_rating": power_rating.adjusted_rating / 150.0 * 100.0,
                "form_score": form_score,
                "speed_score": speed_score,
                "class_score": class_score,
                "conditions_score": conditions_score,
            }
        )

        # Identify key factors and concerns
        key_factors = self._identify_key_factors(form_metrics, power_rating)
        concerns = self._identify_concerns(form_metrics, power_rating, performances)

        # Calculate betting value
        betting_value = (
            self._calculate_betting_value(composite_score, betting_odds)
            if betting_odds
            else 0.0
        )

        # Create factors breakdown
        factors_breakdown = {
            "form_metrics": form_score,
            "power_rating": power_rating.adjusted_rating,
            "speed_component": speed_score,
            "class_component": class_score,
            "consistency_component": consistency_score,
            "conditions_component": conditions_score,
            "confidence": form_metrics.confidence_level * 100,
        }

        # Add power rating breakdown
        factors_breakdown.update(power_rating.factors_breakdown)

        return CompositeScore(
            horse_name=horse_name,
            form_score=form_score,
            power_rating=power_rating.adjusted_rating,
            composite_score=composite_score,
            speed_score=speed_score,
            class_score=class_score,
            consistency_score=consistency_score,
            form_trend_score=form_trend_score,
            conditions_score=conditions_score,
            win_probability=0.0,  # Calculated later in race context
            place_probability=0.0,
            show_probability=0.0,
            confidence_level=form_metrics.confidence_level,
            composite_rank=0,  # Assigned after all horses scored
            power_rating_rank=0,
            form_rank=0,
            key_factors=key_factors,
            concerns=concerns,
            betting_value=betting_value,
            factors_breakdown=factors_breakdown,
        )

    def _calculate_speed_score(
        self, form_metrics: FormMetrics, power_rating: PowerRating
    ) -> float:
        """Calculate speed component score (0-100)."""
        speed_score = (
            (form_metrics.speed_rating * 0.6 + power_rating.speed_component * 0.4)
            * 100
            / 120
        )  # Normalize to 0-100

        return min(100.0, max(0.0, speed_score))

    def _calculate_class_score(
        self, form_metrics: FormMetrics, power_rating: PowerRating
    ) -> float:
        """Calculate class component score (0-100)."""
        class_score = (
            (form_metrics.class_rating * 0.7 + power_rating.class_component * 0.3)
            * 100
            / 120
        )  # Normalize to 0-100

        return min(100.0, max(0.0, class_score))

    def _calculate_consistency_score(self, form_metrics: FormMetrics) -> float:
        """Calculate consistency score (0-100)."""
        consistency_score = (
            form_metrics.consistency_index * 60 + form_metrics.reliability_score * 40
        ) * 100

        return min(100.0, max(0.0, consistency_score))

    def _calculate_form_trend_score(self, form_metrics: FormMetrics) -> float:
        """Calculate form trend score (0-100)."""
        # Compare recent form vs seasonal form to determine trend
        recent_vs_seasonal = form_metrics.recent_form_score / max(
            0.1, form_metrics.seasonal_form_score
        )

        # Convert to 0-100 scale
        if recent_vs_seasonal > 1.2:
            return 80.0  # Strong positive trend
        elif recent_vs_seasonal > 1.1:
            return 65.0  # Positive trend
        elif recent_vs_seasonal > 0.9:
            return 50.0  # Stable
        elif recent_vs_seasonal > 0.8:
            return 35.0  # Declining
        else:
            return 20.0  # Poor trend

    def _calculate_conditions_score(
        self, form_metrics: FormMetrics, race_conditions: Dict[str, Any]
    ) -> float:
        """Calculate conditions suitability score (0-100)."""
        conditions_score = (
            form_metrics.condition_suitability * 40
            + form_metrics.distance_suitability * 30
            + form_metrics.trip_efficiency * 30
        ) * 100

        return min(100.0, max(0.0, conditions_score))

    def _calculate_composite_score(self, components: Dict[str, float]) -> float:
        """Calculate final composite score."""
        weighted_sum = sum(
            components.get(factor, 50.0) * weight
            for factor, weight in self.composite_weights.items()
        )

        return min(100.0, max(0.0, weighted_sum))

    def _identify_key_factors(
        self, form_metrics: FormMetrics, power_rating: PowerRating
    ) -> List[str]:
        """Identify key positive factors for the horse."""
        factors = []

        if form_metrics.recent_form_score > 0.7:
            factors.append("Strong recent form")

        if form_metrics.speed_rating > 90:
            factors.append("High speed rating")

        if form_metrics.consistency_index > 0.7:
            factors.append("Consistent performer")

        if form_metrics.condition_suitability > 0.7:
            factors.append("Suits conditions")

        if form_metrics.distance_suitability > 0.7:
            factors.append("Distance specialist")

        if form_metrics.combo_efficiency > 0.7:
            factors.append("Strong jockey/trainer combo")

        # Check power rating adjustments for positive factors
        for factor, value in power_rating.factors_breakdown.items():
            if factor.startswith("adj_") and value > 2.0:
                factor_name = factor.replace("adj_", "").replace("_", " ").title()
                factors.append(f"Positive {factor_name}")

        return factors

    def _identify_concerns(
        self,
        form_metrics: FormMetrics,
        power_rating: PowerRating,
        performances: List[RacePerformance],
    ) -> List[str]:
        """Identify potential concerns or negatives."""
        concerns = []

        if form_metrics.recent_form_score < 0.3:
            concerns.append("Poor recent form")

        if form_metrics.consistency_index < 0.4:
            concerns.append("Inconsistent")

        if form_metrics.condition_suitability < 0.4:
            concerns.append("Conditions unsuitable")

        if form_metrics.confidence_level < 0.5:
            concerns.append("Limited data confidence")

        # Check for layoff
        if performances:
            last_run = max(performances, key=lambda x: x.date)
            days_since_last = (datetime.now() - last_run.date).days
            if days_since_last > 90:
                concerns.append("Long layoff")

        # Check power rating adjustments for negative factors
        for factor, value in power_rating.factors_breakdown.items():
            if factor.startswith("adj_") and value < -2.0:
                factor_name = factor.replace("adj_", "").replace("_", " ").title()
                concerns.append(f"Negative {factor_name}")

        return concerns

    def _calculate_betting_value(self, composite_score: float, odds: float) -> float:
        """Calculate betting value assessment."""
        if odds <= 0:
            return 0.0

        # Convert composite score to implied probability
        implied_prob = composite_score / 100.0

        # Convert odds to bookmaker probability
        if odds >= 1.0:  # Decimal odds
            book_prob = 1.0 / odds
        else:  # Fractional odds (assume odds < 1 means fractional)
            book_prob = 1.0 / (odds + 1.0)

        # Value = (True probability / Bookmaker probability) - 1
        if book_prob > 0:
            value = (implied_prob / book_prob) - 1.0
        else:
            value = 0.0

        return max(-1.0, min(2.0, value))  # Cap between -100% and +200%

    def _assign_rankings(self, horse_scores: List[CompositeScore]) -> None:
        """Assign rankings to horses."""
        # Composite ranking (already sorted)
        for i, score in enumerate(horse_scores):
            score.composite_rank = i + 1

        # Power rating ranking
        power_sorted = sorted(horse_scores, key=lambda x: x.power_rating, reverse=True)
        for i, score in enumerate(power_sorted):
            score.power_rating_rank = i + 1

        # Form ranking
        form_sorted = sorted(horse_scores, key=lambda x: x.form_score, reverse=True)
        for i, score in enumerate(form_sorted):
            score.form_rank = i + 1

    def _calculate_win_probabilities(self, horse_scores: List[CompositeScore]) -> None:
        """Calculate win, place, and show probabilities."""
        # Simple probability calculation based on scores
        total_score = sum(score.composite_score for score in horse_scores)

        if total_score == 0:
            # Equal probabilities if no scores
            equal_prob = 1.0 / len(horse_scores) if horse_scores else 0.0
            for score in horse_scores:
                score.win_probability = equal_prob
                score.place_probability = min(1.0, equal_prob * 2.5)
                score.show_probability = min(1.0, equal_prob * 4.0)
        else:
            for score in horse_scores:
                # Win probability proportional to score
                score.win_probability = score.composite_score / total_score

                # Place and show probabilities (higher for stronger horses)
                score.place_probability = min(1.0, score.win_probability * 2.5)
                score.show_probability = min(1.0, score.win_probability * 4.0)

    def _analyze_race_dynamics(
        self, horse_scores: List[CompositeScore], race_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze overall race dynamics and insights."""
        insights = {}

        # Pace scenario analysis
        pace_scenario = self._analyze_pace_scenario(horse_scores)
        insights["pace_scenario"] = pace_scenario

        # Track bias (placeholder)
        insights["track_bias"] = "neutral"

        # Key angles
        key_angles = []

        # Look for value horses
        value_horses = [
            score
            for score in horse_scores
            if score.betting_value > 0.2 and score.composite_rank <= 5
        ]
        if value_horses:
            key_angles.append(
                f"Value play: {', '.join(h.horse_name for h in value_horses)}"
            )

        # Look for form horses
        form_horses = [
            score
            for score in horse_scores
            if score.form_trend_score > 70 and score.composite_rank <= 6
        ]
        if form_horses:
            key_angles.append(
                f"Form angle: {', '.join(h.horse_name for h in form_horses)}"
            )

        insights["key_angles"] = key_angles

        # Race competitiveness
        top_scores = [score.composite_score for score in horse_scores[:3]]
        if len(top_scores) >= 2:
            competitiveness = (
                (top_scores[1] / top_scores[0]) if top_scores[0] > 0 else 0
            )
            insights["competitiveness"] = (
                "very competitive" if competitiveness > 0.85 else "moderate"
            )
        else:
            insights["competitiveness"] = "unclear"

        return insights

    def _analyze_pace_scenario(self, horse_scores: List[CompositeScore]) -> str:
        """Analyze likely pace scenario."""
        # Simplified pace analysis
        # Would need actual pace figures for proper analysis

        high_speed_horses = sum(1 for score in horse_scores if score.speed_score > 75)
        total_horses = len(horse_scores)

        if total_horses == 0:
            return "unknown"
        elif high_speed_horses / total_horses > 0.6:
            return "fast pace likely"
        elif high_speed_horses / total_horses < 0.3:
            return "slow pace likely"
        else:
            return "moderate pace"

    def _default_composite_score(self, horse_name: str) -> CompositeScore:
        """Return default score when no data available."""
        return CompositeScore(
            horse_name=horse_name,
            form_score=50.0,
            power_rating=50.0,
            composite_score=50.0,
            speed_score=50.0,
            class_score=50.0,
            consistency_score=50.0,
            form_trend_score=50.0,
            conditions_score=50.0,
            win_probability=0.0,
            place_probability=0.0,
            show_probability=0.0,
            confidence_level=0.1,
            composite_rank=0,
            power_rating_rank=0,
            form_rank=0,
            key_factors=[],
            concerns=["No performance data"],
            betting_value=0.0,
            factors_breakdown={"no_data": True},
        )
