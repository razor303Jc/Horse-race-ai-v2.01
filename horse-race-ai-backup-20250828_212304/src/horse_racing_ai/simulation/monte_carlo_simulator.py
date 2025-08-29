#!/usr/bin/env python3
"""
Monte Carlo Race Simulation System
=================================

Implements Monte Carlo simulation for horse racing analysis with z-scores
and performance modeling based on historical ratings and variance.
Now integrated with real data collection via Playwright auto-download system.
"""

import asyncio
import json
import logging
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

# Try to load environment variables if available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use os.environ directly
    pass

# Add parent directories to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to import real data collection modules
try:
    sys.path.append(str(project_root))
    from enhanced_playwright_auto_download import EnhancedPlaywrightAutoDownload
    from real_data_integration_manager import RealDataIntegrationManager

    REAL_DATA_AVAILABLE = True
except ImportError:
    # Fallback if modules not available
    EnhancedPlaywrightAutoDownload = None
    RealDataIntegrationManager = None
    REAL_DATA_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PerformanceProfile:
    """Performance profile for a horse based on historical data."""

    horse_name: str
    mean_rating: float  # Average performance rating
    std_deviation: float  # Standard deviation of performances
    z_score: float  # Z-score relative to field
    consistency_factor: float  # How consistent the horse is (0-1)
    form_trend: float  # Recent form trend (-1 to 1)
    confidence_level: float  # Confidence in the analysis (0-1)
    performance_range: Tuple[float, float]  # Min/max expected performance


@dataclass
class SimulationResult:
    """Result of a single race simulation."""

    horse_name: str
    finish_position: int
    performance_rating: float
    z_score: float
    winning_margin: Optional[float] = None


@dataclass
class MonteCarloAnalysis:
    """Complete Monte Carlo analysis results."""

    race_id: str
    simulations_run: int
    horse_profiles: List[PerformanceProfile]
    win_probabilities: Dict[str, float]
    place_probabilities: Dict[str, float]  # Top 3
    show_probabilities: Dict[str, float]  # Top 4
    average_positions: Dict[str, float]
    performance_distributions: Dict[str, List[float]]
    confidence_intervals: Dict[str, Tuple[float, float]]
    simulation_reliability: float


class MonteCarloSimulator:
    """Monte Carlo simulation engine for horse racing analysis."""

    def __init__(self, simulations: int = 10000, random_seed: Optional[int] = None):
        """Initialize the Monte Carlo simulator.

        Args:
            simulations: Number of simulations to run
            random_seed: Random seed for reproducible results
        """
        self.simulations = simulations
        self.random = random.Random(random_seed)
        np.random.seed(random_seed)

        # Performance modeling parameters
        self.baseline_variance = 5.0  # Base variance in performance
        self.consistency_impact = 0.3  # How much consistency affects variance
        self.form_impact = 0.15  # How much form trend affects mean
        self.field_interaction = 0.1  # Field interaction effect

        logger.info(f"Initialized Monte Carlo simulator with {simulations} simulations")

    def create_performance_profiles(
        self,
        horse_scores: List,  # CompositeScore objects
        historical_variance: Optional[Dict[str, float]] = None,
    ) -> List[PerformanceProfile]:
        """Create performance profiles from composite scores."""

        profiles = []
        ratings = [score.composite_score for score in horse_scores]

        # Calculate field statistics for z-score computation
        field_mean = float(np.mean(ratings))
        field_std = max(float(np.std(ratings)), 1.0)  # Avoid division by zero

        logger.debug(f"Field statistics: mean={field_mean:.2f}, std={field_std:.2f}")

        for score in horse_scores:
            # Calculate z-score relative to field
            z_score = (score.composite_score - field_mean) / field_std

            # Estimate performance variance from consistency and confidence
            base_variance = self.baseline_variance

            # Adjust variance based on consistency (more consistent = less variance)
            consistency_factor = 1.0 - score.confidence_level
            consistency_adjustment = consistency_factor * self.consistency_impact
            performance_variance = base_variance * (1.0 + consistency_adjustment)

            # Use historical variance if available
            if historical_variance and score.horse_name in historical_variance:
                historical_var = historical_variance[score.horse_name]
                performance_variance = (performance_variance + historical_var) / 2

            # Calculate form trend from recent performance indicators
            form_trend = self._calculate_form_trend(score)

            # Performance range (95% confidence interval)
            form_adjustment = form_trend * self.form_impact * 10
            performance_mean = score.composite_score + form_adjustment
            range_multiplier = 1.96  # 95% CI
            perf_range = (
                performance_mean - (range_multiplier * performance_variance),
                performance_mean + (range_multiplier * performance_variance),
            )

            profile = PerformanceProfile(
                horse_name=score.horse_name,
                mean_rating=performance_mean,
                std_deviation=performance_variance,
                z_score=z_score,
                consistency_factor=score.confidence_level,
                form_trend=form_trend,
                confidence_level=score.confidence_level,
                performance_range=perf_range,
            )

            profiles.append(profile)

            logger.debug(
                f"Profile for {score.horse_name}: "
                f"mean={performance_mean:.2f}, std={performance_variance:.2f}, "
                f"z_score={z_score:.2f}"
            )

        return profiles

    def run_monte_carlo_simulation(
        self, profiles: List[PerformanceProfile], race_id: str = "MC_SIMULATION"
    ) -> MonteCarloAnalysis:
        """Run Monte Carlo simulation for the race."""

        logger.info(
            f"Running {self.simulations} Monte Carlo simulations "
            f"for {len(profiles)} horses"
        )

        # Initialize tracking structures
        win_counts = {profile.horse_name: 0 for profile in profiles}
        place_counts = {profile.horse_name: 0 for profile in profiles}  # Top 3
        show_counts = {profile.horse_name: 0 for profile in profiles}  # Top 4
        position_sums = {profile.horse_name: 0 for profile in profiles}
        performance_records = {profile.horse_name: [] for profile in profiles}

        # Run simulations
        for sim_num in range(self.simulations):
            if sim_num % 1000 == 0:
                logger.debug(f"Simulation {sim_num}/{self.simulations}")

            # Simulate race
            race_results = self._simulate_single_race(profiles)

            # Record results
            for i, result in enumerate(race_results):
                horse_name = result.horse_name
                position = result.finish_position
                performance = result.performance_rating

                # Update position tracking
                position_sums[horse_name] += position
                performance_records[horse_name].append(performance)

                # Update win/place/show counts
                if position == 1:
                    win_counts[horse_name] += 1
                if position <= 3:
                    place_counts[horse_name] += 1
                if position <= 4:
                    show_counts[horse_name] += 1

        # Calculate probabilities and statistics
        win_probabilities = {
            name: count / self.simulations for name, count in win_counts.items()
        }

        place_probabilities = {
            name: count / self.simulations for name, count in place_counts.items()
        }

        show_probabilities = {
            name: count / self.simulations for name, count in show_counts.items()
        }

        average_positions = {
            name: position_sum / self.simulations
            for name, position_sum in position_sums.items()
        }

        # Calculate confidence intervals for performance
        confidence_intervals = {}
        for name, performances in performance_records.items():
            if performances:
                ci_lower = np.percentile(performances, 2.5)
                ci_upper = np.percentile(performances, 97.5)
                confidence_intervals[name] = (float(ci_lower), float(ci_upper))
            else:
                confidence_intervals[name] = (0.0, 0.0)

        # Calculate simulation reliability
        reliability = self._calculate_simulation_reliability(
            profiles, performance_records
        )

        analysis = MonteCarloAnalysis(
            race_id=race_id,
            simulations_run=self.simulations,
            horse_profiles=profiles,
            win_probabilities=win_probabilities,
            place_probabilities=place_probabilities,
            show_probabilities=show_probabilities,
            average_positions=average_positions,
            performance_distributions=performance_records,
            confidence_intervals=confidence_intervals,
            simulation_reliability=reliability,
        )

        logger.info(f"Monte Carlo simulation completed. Reliability: {reliability:.2%}")

        return analysis

    def _simulate_single_race(
        self, profiles: List[PerformanceProfile]
    ) -> List[SimulationResult]:
        """Simulate a single race with the given profiles."""

        race_results = []

        # Generate performance for each horse
        for profile in profiles:
            # Sample from normal distribution
            base_performance = np.random.normal(
                profile.mean_rating, profile.std_deviation
            )

            # Add random field interaction effects
            interaction_variance = self.field_interaction * profile.std_deviation
            field_effect = np.random.normal(0, interaction_variance)

            # Final performance with bounds
            final_performance = max(0, base_performance + field_effect)

            # Calculate z-score for this performance
            field_mean = np.mean([p.mean_rating for p in profiles])
            field_std_dev = np.std([p.mean_rating for p in profiles])
            field_std = max(float(field_std_dev), 1.0)
            performance_z_score = (final_performance - field_mean) / field_std

            race_results.append(
                SimulationResult(
                    horse_name=profile.horse_name,
                    finish_position=0,  # Will be set after sorting
                    performance_rating=float(final_performance),
                    z_score=float(performance_z_score),
                )
            )

        # Sort by performance (highest first) and assign positions
        race_results.sort(key=lambda x: x.performance_rating, reverse=True)

        for i, result in enumerate(race_results):
            result.finish_position = i + 1

            # Calculate winning margin for winner
            if i == 0 and len(race_results) > 1:
                margin = result.performance_rating - race_results[1].performance_rating
                result.winning_margin = float(margin)

        return race_results

    def _calculate_form_trend(self, score) -> float:
        """Calculate form trend from composite score attributes."""

        # Use key factors and concerns to determine trend
        has_key_factors = hasattr(score, "key_factors")
        positive_factors = len(score.key_factors) if has_key_factors else 0
        negative_factors = len(score.concerns) if hasattr(score, "concerns") else 0

        # Normalize to -1 to 1 range
        if positive_factors + negative_factors == 0:
            return 0.0

        factor_sum = positive_factors + negative_factors
        trend = (positive_factors - negative_factors) / max(factor_sum, 1)
        return max(-1.0, min(1.0, trend))

    def _calculate_simulation_reliability(
        self,
        profiles: List[PerformanceProfile],
        performance_records: Dict[str, List[float]],
    ) -> float:
        """Calculate reliability of the simulation results."""

        # Base reliability on confidence levels and data quality
        confidence_scores = [profile.confidence_level for profile in profiles]
        avg_confidence = float(np.mean(confidence_scores))

        # Check variance convergence
        variance_stability = 0.0
        if performance_records:
            variances = []
            for performances in performance_records.values():
                if len(performances) > 100:  # Need sufficient samples
                    # Check if variance has stabilized
                    early_var = np.var(performances[: len(performances) // 2])
                    late_var = np.var(performances[len(performances) // 2 :])
                    max_var = max(float(early_var), float(late_var), 1.0)
                    var_diff = abs(float(early_var) - float(late_var))
                    stability = 1.0 - var_diff / max_var
                    variances.append(max(0.0, min(1.0, float(stability))))

            if variances:
                variance_stability = float(np.mean(variances))

        # Combine factors
        reliability = avg_confidence * 0.6 + variance_stability * 0.4

        return max(0.0, min(1.0, reliability))

    def get_betting_recommendations(
        self,
        analysis: MonteCarloAnalysis,
        min_probability: float = 0.15,
        min_value: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """Generate betting recommendations from Monte Carlo analysis."""

        recommendations = []

        for horse_name in analysis.win_probabilities:
            win_prob = analysis.win_probabilities[horse_name]

            # Find corresponding profile for additional data
            profile = next(
                (p for p in analysis.horse_profiles if p.horse_name == horse_name), None
            )

            if not profile:
                continue

            # Calculate value based on probability vs typical odds
            if win_prob >= min_probability:
                # Estimate fair odds
                fair_odds = 1.0 / win_prob if win_prob > 0 else 999.0

                recommendation = {
                    "horse_name": horse_name,
                    "bet_type": "win",
                    "probability": win_prob,
                    "fair_odds": fair_odds,
                    "confidence": profile.confidence_level,
                    "z_score": profile.z_score,
                    "average_position": analysis.average_positions[horse_name],
                    "performance_range": profile.performance_range,
                    "reliability": analysis.simulation_reliability,
                }

                recommendations.append(recommendation)

        # Sort by probability descending
        recommendations.sort(key=lambda x: x["probability"], reverse=True)

        return recommendations


def create_monte_carlo_analysis(
    horse_scores: List,
    race_id: str = "MC_ANALYSIS",
    simulations: int = 10000,
    historical_variance: Optional[Dict[str, float]] = None,
) -> MonteCarloAnalysis:
    """Convenience function to create Monte Carlo analysis from horse scores."""

    simulator = MonteCarloSimulator(simulations=simulations)
    profiles = simulator.create_performance_profiles(horse_scores, historical_variance)
    analysis = simulator.run_monte_carlo_simulation(profiles, race_id)

    return analysis
