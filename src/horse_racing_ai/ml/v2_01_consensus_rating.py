#!/usr/bin/env python3
"""
V2.01 Multi-Rating Consensus System
==================================

Implements the sophisticated 4-rating system discovered in v2.01:
- raw_rating: Base statistical rating
- monte_carlo_rating: Simulation-based rating
- ai_ml_rating: Machine learning rating
- consensus_rating: Weighted combination

Based on v2.01 performance_data analysis showing multi-method approach.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class HorseRating:
    """Multi-dimensional rating for a single horse."""

    horse_name: str
    raw_rating: float
    monte_carlo_rating: float
    ai_ml_rating: float
    consensus_rating: float
    raw_win_probability: float
    monte_carlo_win_probability: float
    ai_ml_win_probability: float
    consensus_win_probability: float
    prediction_confidence: float
    method_agreement_score: float
    prediction_consistency: float
    value_rating: float


@dataclass
class RaceRatingAnalysis:
    """Complete rating analysis for a race."""

    race_id: str
    ratings: List[HorseRating]
    method_correlations: Dict[str, float]
    consensus_quality: float
    prediction_reliability: float


class RatingMethod(ABC):
    """Abstract base class for rating methods."""

    @abstractmethod
    def calculate_rating(self, horse_data: pd.Series, race_context: Dict) -> float:
        """Calculate rating for a horse."""
        pass

    @abstractmethod
    def calculate_win_probability(
        self, rating: float, field_ratings: List[float]
    ) -> float:
        """Calculate win probability from rating."""
        pass


class RawStatisticalRating(RatingMethod):
    """Raw statistical rating based on historical performance."""

    def calculate_rating(self, horse_data: pd.Series, race_context: Dict) -> float:
        """Calculate raw statistical rating."""
        # Base factors
        win_rate = horse_data.get("Percentage_wins", 0.1)
        place_rate = horse_data.get("Percentage_placed", 0.2)
        total_races = horse_data.get("Total_races", 1)
        age = horse_data.get("age", 5)

        # Experience factor
        experience_factor = min(total_races / 20, 1.0)

        # Age curve (peak around 4-6 years)
        age_factor = max(0.6, 1.0 - abs(age - 5) * 0.1)

        # Surface-specific performance
        surface_factor = 1.0
        if race_context.get("surface") == "turf":
            surface_factor = horse_data.get("Flat_Turf_rate", 0.1) / 0.2
        elif race_context.get("surface") == "aw":
            surface_factor = horse_data.get("Flat_AW_rate", 0.1) / 0.2

        # Combine factors (scale to 40-120 range)
        raw_score = (
            win_rate * 50  # Win rate contribution
            + place_rate * 30  # Place rate contribution
            + experience_factor * 20  # Experience bonus
            + age_factor * 10  # Age adjustment
            + surface_factor * 10  # Surface suitability
        )

        return max(40, min(120, raw_score))

    def calculate_win_probability(
        self, rating: float, field_ratings: List[float]
    ) -> float:
        """Calculate win probability using exponential model."""
        if not field_ratings:
            return 0.5

        # Convert ratings to exponential weights
        weights = [np.exp(r / 20) for r in field_ratings]
        horse_weight = np.exp(rating / 20)

        # Normalize to probability
        total_weight = sum(weights)
        return horse_weight / total_weight if total_weight > 0 else 0


class MonteCarloRating(RatingMethod):
    """Monte Carlo simulation-based rating."""

    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations

    def calculate_rating(self, horse_data: pd.Series, race_context: Dict) -> float:
        """Calculate Monte Carlo rating through simulation."""
        # Base rating from raw statistics
        base_rating = horse_data.get("raw_rating", 70)

        # Performance variance factors
        consistency = 1.0 - (horse_data.get("form_consistency", 0.1))
        recent_form = horse_data.get("Percentage_wins", 0.1)

        # Simulate performance variations
        simulated_performances = []

        for _ in range(self.n_simulations):
            # Add random variation based on consistency
            variation = np.random.normal(0, consistency * 15)

            # Form trend factor
            form_factor = np.random.normal(recent_form * 10, 5)

            # Race day factors (track conditions, etc.)
            race_day_factor = np.random.normal(0, 3)

            performance = base_rating + variation + form_factor + race_day_factor
            simulated_performances.append(performance)

        # Return mean of simulations
        mc_rating = np.mean(simulated_performances)
        return max(40, min(120, mc_rating))

    def calculate_win_probability(
        self, rating: float, field_ratings: List[float]
    ) -> float:
        """Calculate win probability through head-to-head simulations."""
        if not field_ratings:
            return 0.5

        wins = 0

        for _ in range(self.n_simulations):
            # Simulate race performance for all horses
            horse_performance = np.random.normal(rating, 8)

            field_performances = [np.random.normal(r, 8) for r in field_ratings]

            # Check if this horse won
            if horse_performance >= max(field_performances):
                wins += 1

        return wins / self.n_simulations


class AIMLRating(RatingMethod):
    """AI/ML-based rating using ensemble predictions."""

    def __init__(self, ensemble_model=None):
        self.ensemble_model = ensemble_model

    def calculate_rating(self, horse_data: pd.Series, race_context: Dict) -> float:
        """Calculate AI/ML rating using trained models."""
        if self.ensemble_model is None:
            # Fallback to enhanced statistical model
            return self._enhanced_statistical_rating(horse_data, race_context)

        # Use actual ensemble model prediction
        features = self._prepare_features(horse_data, race_context)
        prediction = self.ensemble_model.predict_proba([features])[0][1]

        # Convert probability to rating scale
        return 40 + (prediction * 80)

    def _enhanced_statistical_rating(
        self, horse_data: pd.Series, race_context: Dict
    ) -> float:
        """Enhanced statistical model when ML model not available."""
        # Multiple performance dimensions
        speed_rating = horse_data.get("Flat_Turf_rate", 0.1) * 100
        class_rating = horse_data.get("Percentage_placed", 0.2) * 100
        consistency_rating = (1.0 - horse_data.get("form_consistency", 0.2)) * 50

        # Recent form weighting
        win_rate = horse_data.get("Percentage_wins", 0.1)
        recent_form_weight = min(win_rate * 2, 1.0)

        # Weighted combination
        ai_rating = (
            speed_rating * 0.4
            + class_rating * 0.3
            + consistency_rating * 0.2
            + recent_form_weight * 10
        )

        return max(40, min(120, ai_rating))

    def _prepare_features(
        self, horse_data: pd.Series, race_context: Dict
    ) -> List[float]:
        """Prepare features for ML model."""
        # Standard feature preparation for ensemble model
        features = [
            horse_data.get("age", 5),
            horse_data.get("Total_races", 10),
            horse_data.get("Percentage_wins", 0.1),
            horse_data.get("Percentage_placed", 0.2),
            horse_data.get("Flat_Turf_rate", 0.1),
            # Add more features as needed
        ]
        return features

    def calculate_win_probability(
        self, rating: float, field_ratings: List[float]
    ) -> float:
        """Calculate win probability using softmax transformation."""
        if not field_ratings:
            return 0.5

        # Softmax with temperature scaling
        temperature = 15
        exp_ratings = [np.exp(r / temperature) for r in field_ratings]
        exp_horse = np.exp(rating / temperature)

        total_exp = sum(exp_ratings)
        return exp_horse / total_exp if total_exp > 0 else 0


class V201ConsensusRatingSystem:
    """
    Multi-method consensus rating system based on v2.01 analysis.

    Combines raw statistical, Monte Carlo, and AI/ML ratings using
    the approach discovered in v2.01 performance data.
    """

    def __init__(self, ensemble_model=None, n_simulations: int = 1000):
        # Initialize rating methods
        self.raw_method = RawStatisticalRating()
        self.monte_carlo_method = MonteCarloRating(n_simulations)
        self.ai_ml_method = AIMLRating(ensemble_model)

        # Consensus weights (based on v2.01 analysis)
        self.consensus_weights = {"raw": 0.25, "monte_carlo": 0.35, "ai_ml": 0.40}

    def analyze_race(
        self, race_data: pd.DataFrame, race_context: Dict = None
    ) -> RaceRatingAnalysis:
        """
        Perform complete multi-method rating analysis for a race.

        Args:
            race_data: DataFrame with horse data
            race_context: Race conditions and context

        Returns:
            Complete rating analysis with all methods
        """
        if race_context is None:
            race_context = {"surface": "turf", "distance": "1m", "class": 3}

        logger.info(
            f"Analyzing race with {len(race_data)} runners using v2.01 consensus system"
        )

        # Calculate ratings for all horses using each method
        horse_ratings = []
        all_raw_ratings = []
        all_mc_ratings = []
        all_ai_ratings = []

        # First pass: calculate individual ratings
        for _, horse in race_data.iterrows():
            raw_rating = self.raw_method.calculate_rating(horse, race_context)
            mc_rating = self.monte_carlo_method.calculate_rating(horse, race_context)
            ai_rating = self.ai_ml_method.calculate_rating(horse, race_context)

            all_raw_ratings.append(raw_rating)
            all_mc_ratings.append(mc_rating)
            all_ai_ratings.append(ai_rating)

        # Second pass: calculate probabilities and consensus
        for idx, (_, horse) in enumerate(race_data.iterrows()):
            raw_rating = all_raw_ratings[idx]
            mc_rating = all_mc_ratings[idx]
            ai_rating = all_ai_ratings[idx]

            # Calculate consensus rating
            consensus_rating = (
                self.consensus_weights["raw"] * raw_rating
                + self.consensus_weights["monte_carlo"] * mc_rating
                + self.consensus_weights["ai_ml"] * ai_rating
            )

            # Calculate win probabilities
            raw_prob = self.raw_method.calculate_win_probability(
                raw_rating, all_raw_ratings
            )
            mc_prob = self.monte_carlo_method.calculate_win_probability(
                mc_rating, all_mc_ratings
            )
            ai_prob = self.ai_ml_method.calculate_win_probability(
                ai_rating, all_ai_ratings
            )

            # Consensus probability
            consensus_prob = (
                self.consensus_weights["raw"] * raw_prob
                + self.consensus_weights["monte_carlo"] * mc_prob
                + self.consensus_weights["ai_ml"] * ai_prob
            )

            # Calculate agreement and confidence metrics
            ratings = [raw_rating, mc_rating, ai_rating]
            probabilities = [raw_prob, mc_prob, ai_prob]

            method_agreement = (
                1.0 - (np.std(probabilities) / np.mean(probabilities))
                if np.mean(probabilities) > 0
                else 0
            )
            prediction_confidence = min(method_agreement * 1.2, 1.0)
            prediction_consistency = (
                1.0 - (np.std(ratings) / np.mean(ratings))
                if np.mean(ratings) > 0
                else 0
            )

            # Value rating (simplified)
            expected_odds = 1 / consensus_prob if consensus_prob > 0 else 50
            value_rating = max(
                0, (expected_odds - 5) / expected_odds
            )  # Assume odds of 5.0 as baseline

            horse_rating = HorseRating(
                horse_name=horse.get("name", f"Horse_{idx}"),
                raw_rating=raw_rating,
                monte_carlo_rating=mc_rating,
                ai_ml_rating=ai_rating,
                consensus_rating=consensus_rating,
                raw_win_probability=raw_prob,
                monte_carlo_win_probability=mc_prob,
                ai_ml_win_probability=ai_prob,
                consensus_win_probability=consensus_prob,
                prediction_confidence=prediction_confidence,
                method_agreement_score=method_agreement,
                prediction_consistency=prediction_consistency,
                value_rating=value_rating,
            )

            horse_ratings.append(horse_rating)

        # Calculate method correlations
        correlations = self._calculate_method_correlations(horse_ratings)

        # Overall analysis quality metrics
        consensus_quality = np.mean([hr.method_agreement_score for hr in horse_ratings])
        prediction_reliability = np.mean(
            [hr.prediction_confidence for hr in horse_ratings]
        )

        return RaceRatingAnalysis(
            race_id=race_context.get("race_id", "UNKNOWN"),
            ratings=horse_ratings,
            method_correlations=correlations,
            consensus_quality=consensus_quality,
            prediction_reliability=prediction_reliability,
        )

    def _calculate_method_correlations(
        self, horse_ratings: List[HorseRating]
    ) -> Dict[str, float]:
        """Calculate correlations between different rating methods."""
        raw_ratings = [hr.raw_rating for hr in horse_ratings]
        mc_ratings = [hr.monte_carlo_rating for hr in horse_ratings]
        ai_ratings = [hr.ai_ml_rating for hr in horse_ratings]

        correlations = {}

        try:
            correlations["raw_vs_mc"] = np.corrcoef(raw_ratings, mc_ratings)[0, 1]
            correlations["raw_vs_ai"] = np.corrcoef(raw_ratings, ai_ratings)[0, 1]
            correlations["mc_vs_ai"] = np.corrcoef(mc_ratings, ai_ratings)[0, 1]
        except:
            # Handle edge cases with insufficient variance
            correlations = {"raw_vs_mc": 0.5, "raw_vs_ai": 0.5, "mc_vs_ai": 0.5}

        return correlations

    def export_ratings_analysis(
        self, analysis: RaceRatingAnalysis, filepath: str
    ) -> str:
        """Export complete ratings analysis to CSV."""
        ratings_data = []

        for rating in analysis.ratings:
            ratings_data.append(
                {
                    "horse_name": rating.horse_name,
                    "raw_rating": rating.raw_rating,
                    "monte_carlo_rating": rating.monte_carlo_rating,
                    "ai_ml_rating": rating.ai_ml_rating,
                    "consensus_rating": rating.consensus_rating,
                    "raw_win_probability": rating.raw_win_probability,
                    "monte_carlo_win_probability": rating.monte_carlo_win_probability,
                    "ai_ml_win_probability": rating.ai_ml_win_probability,
                    "consensus_win_probability": rating.consensus_win_probability,
                    "prediction_confidence": rating.prediction_confidence,
                    "method_agreement_score": rating.method_agreement_score,
                    "prediction_consistency": rating.prediction_consistency,
                    "value_rating": rating.value_rating,
                }
            )

        df = pd.DataFrame(ratings_data)
        df.to_csv(filepath, index=False)

        logger.info(f"Ratings analysis exported to {filepath}")
        return filepath

    def get_consensus_rankings(
        self, analysis: RaceRatingAnalysis
    ) -> List[Tuple[str, float]]:
        """Get horses ranked by consensus rating."""
        rankings = [
            (rating.horse_name, rating.consensus_rating) for rating in analysis.ratings
        ]
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def get_high_confidence_picks(
        self, analysis: RaceRatingAnalysis, min_confidence: float = 0.7
    ) -> List[HorseRating]:
        """Get horses with high prediction confidence."""
        high_confidence = [
            rating
            for rating in analysis.ratings
            if rating.prediction_confidence >= min_confidence
        ]
        high_confidence.sort(key=lambda x: x.consensus_rating, reverse=True)
        return high_confidence


def demo_consensus_system():
    """Demonstrate the v2.01 consensus rating system."""
    print("🏆 V2.01 Multi-Rating Consensus System Demo")
    print("=" * 60)

    # Sample race data
    sample_data = pd.DataFrame(
        {
            "name": [
                "Thunder Bolt",
                "Lightning Strike",
                "Storm Chaser",
                "Wind Runner",
                "Rain Dancer",
            ],
            "age": [5, 4, 6, 5, 7],
            "Total_races": [20, 25, 30, 22, 28],
            "Percentage_wins": [0.25, 0.20, 0.15, 0.18, 0.12],
            "Percentage_placed": [0.45, 0.40, 0.35, 0.38, 0.32],
            "Flat_Turf_rate": [0.28, 0.22, 0.18, 0.20, 0.14],
            "form_consistency": [0.1, 0.15, 0.2, 0.12, 0.18],
        }
    )

    # Initialize consensus system
    consensus_system = V201ConsensusRatingSystem()

    # Analyze race
    race_context = {
        "race_id": "DEMO_RACE_001",
        "surface": "turf",
        "distance": "1m2f",
        "class": 3,
    }

    analysis = consensus_system.analyze_race(sample_data, race_context)

    print(f"\n🎯 Race Analysis Results:")
    print(f"Race ID: {analysis.race_id}")
    print(f"Consensus Quality: {analysis.consensus_quality:.3f}")
    print(f"Prediction Reliability: {analysis.prediction_reliability:.3f}")

    print(f"\n📊 Method Correlations:")
    for method_pair, correlation in analysis.method_correlations.items():
        print(f"  {method_pair}: {correlation:.3f}")

    print(f"\n🏇 Horse Ratings:")
    print("-" * 100)
    print(
        f"{'Horse':<15} {'Raw':<6} {'MC':<6} {'AI':<6} {'Consensus':<9} {'Prob':<6} {'Conf':<6}"
    )
    print("-" * 100)

    for rating in sorted(
        analysis.ratings, key=lambda x: x.consensus_rating, reverse=True
    ):
        print(
            f"{rating.horse_name:<15} {rating.raw_rating:<6.1f} {rating.monte_carlo_rating:<6.1f} "
            f"{rating.ai_ml_rating:<6.1f} {rating.consensus_rating:<9.1f} "
            f"{rating.consensus_win_probability:<6.3f} {rating.prediction_confidence:<6.3f}"
        )

    # High confidence picks
    high_conf = consensus_system.get_high_confidence_picks(analysis, min_confidence=0.6)

    if high_conf:
        print(f"\n🎯 High Confidence Picks:")
        for pick in high_conf:
            print(
                f"  {pick.horse_name}: Rating={pick.consensus_rating:.1f}, "
                f"Probability={pick.consensus_win_probability:.3f}, "
                f"Confidence={pick.prediction_confidence:.3f}"
            )
    else:
        print(f"\n🎯 No high confidence picks identified")


if __name__ == "__main__":
    demo_consensus_system()
