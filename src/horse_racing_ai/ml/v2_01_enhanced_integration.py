#!/usr/bin/env python3
"""
V2.01 Enhanced Racing Intelligence Integration
=============================================

Integrates all discovered v2.01 enhancements into v2.03:
- Market-based feature engineering
- Multi-rating consensus system
- Performance validation framework
- Professional-grade analytics

This module provides a unified interface to the sophisticated
racing intelligence capabilities discovered in v2.01 analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Import v2.01 enhancement modules
from .v2_01_market_features import V201MarketFeatureEngine, MarketFeatures
from .v2_01_consensus_rating import V201ConsensusRatingSystem, RaceRatingAnalysis
from .v2_01_performance_validation import (
    V201PerformanceValidator,
    PredictionResult,
    PerformanceReport,
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancedPrediction:
    """Enhanced prediction combining all v2.01 capabilities."""

    horse_name: str
    race_id: str
    # Market features
    market_features: MarketFeatures
    # Consensus ratings
    raw_rating: float
    monte_carlo_rating: float
    ai_ml_rating: float
    consensus_rating: float
    # Probabilities
    raw_win_probability: float
    monte_carlo_win_probability: float
    ai_ml_win_probability: float
    consensus_win_probability: float
    # Confidence metrics
    prediction_confidence: float
    method_agreement_score: float
    value_rating: float
    # Final recommendation
    recommended_position: int
    betting_recommendation: str
    confidence_level: str


@dataclass
class RaceAnalysisComplete:
    """Complete race analysis with all v2.01 enhancements."""

    race_id: str
    race_date: datetime
    enhanced_predictions: List[EnhancedPrediction]
    market_efficiency: float
    prediction_reliability: float
    betting_opportunities: List[Tuple[str, float, str]]  # horse, value, reason
    top_picks: List[Tuple[str, float]]  # horse, confidence
    consensus_quality: float


class V201EnhancedRacingIntelligence:
    """
    Enhanced Racing Intelligence System

    Integrates all v2.01 discoveries into a unified prediction system
    that combines market analysis, multi-method consensus, and
    comprehensive performance validation.
    """

    def __init__(self, ensemble_model=None, validation_file: str = None):
        # Initialize core components
        self.market_engine = V201MarketFeatureEngine()
        self.consensus_system = V201ConsensusRatingSystem(ensemble_model)

        if validation_file:
            self.validator = V201PerformanceValidator(validation_file)
        else:
            self.validator = V201PerformanceValidator()

        self.ensemble_model = ensemble_model

        logger.info("V2.01 Enhanced Racing Intelligence System initialized")

    def analyze_race_complete(
        self,
        race_data: pd.DataFrame,
        odds_data: Optional[pd.DataFrame] = None,
        race_context: Optional[Dict] = None,
    ) -> RaceAnalysisComplete:
        """
        Perform complete race analysis using all v2.01 enhancements.

        Args:
            race_data: Horse data for the race
            odds_data: Betting odds data (optional)
            race_context: Race conditions and context

        Returns:
            Complete enhanced race analysis
        """
        if race_context is None:
            race_context = {
                "race_id": f'RACE_{datetime.now().strftime("%Y%m%d_%H%M")}',
                "surface": "turf",
                "distance": "1m",
                "class": 3,
            }

        race_id = race_context.get("race_id", "UNKNOWN")

        logger.info(f"Starting complete race analysis for {race_id}")

        # Step 1: Market feature analysis
        if odds_data is not None:
            market_analysis = self.market_engine.calculate_market_features(
                race_data, odds_column="odds", rating_column="rating"
            )
            logger.info("Market analysis completed")
        else:
            # Generate synthetic odds for demo
            market_analysis = self._generate_synthetic_market_analysis(race_data)
            logger.info("Using synthetic market data for analysis")

        # Step 2: Multi-method consensus rating
        consensus_analysis = self.consensus_system.analyze_race(race_data, race_context)
        logger.info("Consensus rating analysis completed")

        # Step 3: Combine market and consensus data
        enhanced_predictions = self._create_enhanced_predictions(
            race_data, market_analysis, consensus_analysis
        )

        # Step 4: Calculate race-level metrics
        market_efficiency = self._calculate_market_efficiency(
            enhanced_predictions, market_analysis
        )

        prediction_reliability = consensus_analysis.prediction_reliability

        # Step 5: Identify betting opportunities
        betting_opportunities = self._identify_betting_opportunities(
            enhanced_predictions
        )

        # Step 6: Generate top picks
        top_picks = self._generate_top_picks(enhanced_predictions)

        race_analysis = RaceAnalysisComplete(
            race_id=race_id,
            race_date=datetime.now(),
            enhanced_predictions=enhanced_predictions,
            market_efficiency=market_efficiency,
            prediction_reliability=prediction_reliability,
            betting_opportunities=betting_opportunities,
            top_picks=top_picks,
            consensus_quality=consensus_analysis.consensus_quality,
        )

        logger.info(f"Complete race analysis finished for {race_id}")
        return race_analysis

    def _generate_synthetic_market_analysis(self, race_data: pd.DataFrame) -> Any:
        """Generate synthetic market analysis when odds data unavailable."""
        # Create synthetic odds based on win rates
        synthetic_odds = []

        for _, horse in race_data.iterrows():
            win_rate = horse.get("Percentage_wins", 0.1)
            # Convert win rate to approximate odds
            if win_rate > 0:
                implied_odds = min(50, max(1.5, 1 / win_rate))
            else:
                implied_odds = 20.0

            synthetic_odds.append(
                {
                    "horse_name": horse.get("name", f"Horse_{len(synthetic_odds)}"),
                    "odds": implied_odds,
                    "is_favorite": False,
                }
            )

        # Mark favorite (lowest odds)
        if synthetic_odds:
            favorite_idx = min(
                range(len(synthetic_odds)), key=lambda i: synthetic_odds[i]["odds"]
            )
            synthetic_odds[favorite_idx]["is_favorite"] = True

        # Convert to DataFrame format expected by market engine
        # Add the odds to the race data
        race_data_with_odds = race_data.copy()
        race_data_with_odds["odds_decimal"] = [so["odds"] for so in synthetic_odds]

        return self.market_engine.calculate_market_features(race_data_with_odds)

    def _create_enhanced_predictions(
        self,
        race_data: pd.DataFrame,
        market_analysis: Any,
        consensus_analysis: RaceRatingAnalysis,
    ) -> List[EnhancedPrediction]:
        """Create enhanced predictions combining all analysis."""
        enhanced_predictions = []

        for idx, (_, horse) in enumerate(race_data.iterrows()):
            horse_name = horse.get("name", f"Horse_{idx}")

            # Get consensus rating data
            consensus_rating = None
            for rating in consensus_analysis.ratings:
                if rating.horse_name == horse_name:
                    consensus_rating = rating
                    break

            if consensus_rating is None:
                logger.warning(f"No consensus rating found for {horse_name}")
                continue

            # Get market features
            market_features = None
            if hasattr(market_analysis, "market_features"):
                for features in market_analysis.market_features:
                    if features.horse_name == horse_name:
                        market_features = features
                        break

            if market_features is None:
                # Create default market features
                market_features = MarketFeatures(
                    horse_name=horse_name,
                    odds_decimal=5.0,
                    is_favorite=False,
                    odds_rank=idx + 1,
                    market_share=1.0 / len(race_data),
                    odds_percentile=50.0,
                    field_size=len(race_data),
                    prize_per_runner=1000.0,
                    rating_odds_ratio=1.0,
                    value_rating=0.0,
                    implied_probability=0.2,
                )

            # Determine recommended position
            recommended_position = idx + 1  # Default to order in data

            # Betting recommendation
            betting_rec = self._generate_betting_recommendation(
                consensus_rating, market_features
            )

            # Confidence level
            confidence_level = self._determine_confidence_level(
                consensus_rating.prediction_confidence
            )

            enhanced_prediction = EnhancedPrediction(
                horse_name=horse_name,
                race_id=consensus_analysis.race_id,
                market_features=market_features,
                raw_rating=consensus_rating.raw_rating,
                monte_carlo_rating=consensus_rating.monte_carlo_rating,
                ai_ml_rating=consensus_rating.ai_ml_rating,
                consensus_rating=consensus_rating.consensus_rating,
                raw_win_probability=consensus_rating.raw_win_probability,
                monte_carlo_win_probability=consensus_rating.monte_carlo_win_probability,
                ai_ml_win_probability=consensus_rating.ai_ml_win_probability,
                consensus_win_probability=consensus_rating.consensus_win_probability,
                prediction_confidence=consensus_rating.prediction_confidence,
                method_agreement_score=consensus_rating.method_agreement_score,
                value_rating=consensus_rating.value_rating,
                recommended_position=recommended_position,
                betting_recommendation=betting_rec,
                confidence_level=confidence_level,
            )

            enhanced_predictions.append(enhanced_prediction)

        # Sort by consensus rating
        enhanced_predictions.sort(key=lambda x: x.consensus_rating, reverse=True)

        # Update recommended positions based on ranking
        for idx, pred in enumerate(enhanced_predictions):
            pred.recommended_position = idx + 1

        return enhanced_predictions

    def _generate_betting_recommendation(
        self, consensus_rating, market_features: MarketFeatures
    ) -> str:
        """Generate betting recommendation based on analysis."""
        # Value betting logic
        if market_features.value_rating > 0.2:
            if consensus_rating.consensus_win_probability > 0.3:
                return "STRONG BET"
            elif consensus_rating.consensus_win_probability > 0.2:
                return "VALUE BET"
            else:
                return "SMALL BET"

        # High confidence logic
        elif consensus_rating.prediction_confidence > 0.8:
            if consensus_rating.consensus_win_probability > 0.4:
                return "CONFIDENT BET"
            else:
                return "PLACE BET"

        # Conservative logic
        elif consensus_rating.consensus_win_probability > 0.25:
            return "CONSIDER"
        else:
            return "AVOID"

    def _determine_confidence_level(self, confidence_score: float) -> str:
        """Determine confidence level category."""
        if confidence_score >= 0.8:
            return "HIGH"
        elif confidence_score >= 0.6:
            return "MEDIUM"
        elif confidence_score >= 0.4:
            return "LOW"
        else:
            return "VERY LOW"

    def _calculate_market_efficiency(
        self, predictions: List[EnhancedPrediction], market_analysis: Any
    ) -> float:
        """Calculate overall market efficiency score."""
        if not predictions:
            return 0.5

        # Compare our probabilities vs market implied probabilities
        efficiency_scores = []

        for pred in predictions:
            market_prob = 1.0 / pred.market_features.odds_decimal
            our_prob = pred.consensus_win_probability

            # Efficiency = how well market aligns with our assessment
            if market_prob > 0:
                alignment = 1.0 - abs(market_prob - our_prob) / max(
                    market_prob, our_prob
                )
                efficiency_scores.append(alignment)

        return np.mean(efficiency_scores) if efficiency_scores else 0.5

    def _identify_betting_opportunities(
        self, predictions: List[EnhancedPrediction]
    ) -> List[Tuple[str, float, str]]:
        """Identify the best betting opportunities."""
        opportunities = []

        for pred in predictions:
            # Value betting opportunities
            if pred.market_features.value_rating > 0.15:
                opportunities.append(
                    (
                        pred.horse_name,
                        pred.market_features.value_rating,
                        f"Value bet - {pred.betting_recommendation}",
                    )
                )

            # High confidence opportunities
            elif (
                pred.prediction_confidence > 0.75
                and pred.consensus_win_probability > 0.25
            ):
                opportunities.append(
                    (
                        pred.horse_name,
                        pred.prediction_confidence,
                        f"High confidence - {pred.confidence_level}",
                    )
                )

        # Sort by value/confidence
        opportunities.sort(key=lambda x: x[1], reverse=True)
        return opportunities[:3]  # Top 3 opportunities

    def _generate_top_picks(
        self, predictions: List[EnhancedPrediction]
    ) -> List[Tuple[str, float]]:
        """Generate top picks based on consensus analysis."""
        # Sort by consensus rating and confidence
        scored_picks = [
            (pred.horse_name, pred.consensus_rating * pred.prediction_confidence)
            for pred in predictions
        ]

        scored_picks.sort(key=lambda x: x[1], reverse=True)
        return scored_picks[:3]  # Top 3 picks

    def record_race_result(
        self,
        race_analysis: RaceAnalysisComplete,
        actual_results: Dict[str, int],  # horse_name -> finish_position
        odds_data: Optional[Dict[str, float]] = None,  # horse_name -> final_odds
    ) -> None:
        """Record actual race results for validation."""
        for pred in race_analysis.enhanced_predictions:
            if pred.horse_name in actual_results:
                actual_position = actual_results[pred.horse_name]
                actual_odds = odds_data.get(pred.horse_name) if odds_data else None

                # Create prediction result for validation
                result = PredictionResult(
                    race_id=pred.race_id,
                    race_date=race_analysis.race_date,
                    horse_name=pred.horse_name,
                    predicted_finish_position=pred.recommended_position,
                    actual_finish_position=actual_position,
                    raw_rating=pred.raw_rating,
                    monte_carlo_rating=pred.monte_carlo_rating,
                    ai_ml_rating=pred.ai_ml_rating,
                    consensus_rating=pred.consensus_rating,
                    raw_win_probability=pred.raw_win_probability,
                    monte_carlo_win_probability=pred.monte_carlo_win_probability,
                    ai_ml_win_probability=pred.ai_ml_win_probability,
                    consensus_win_probability=pred.consensus_win_probability,
                    predicted_odds=(
                        1.0 / pred.consensus_win_probability
                        if pred.consensus_win_probability > 0
                        else 50
                    ),
                    actual_odds=actual_odds,
                )

                self.validator.record_prediction_result(result)

        logger.info(f"Recorded results for race {race_analysis.race_id}")

    def get_performance_report(self, days_back: int = 30) -> PerformanceReport:
        """Get comprehensive performance report."""
        return self.validator.generate_performance_report(days_back)

    def export_race_analysis(
        self, race_analysis: RaceAnalysisComplete, filepath: str
    ) -> str:
        """Export complete race analysis to file."""
        lines = [
            "V2.01 Enhanced Race Analysis Report",
            "=" * 50,
            f"Race ID: {race_analysis.race_id}",
            f"Analysis Date: {race_analysis.race_date.strftime('%Y-%m-%d %H:%M')}",
            f"Market Efficiency: {race_analysis.market_efficiency:.3f}",
            f"Prediction Reliability: {race_analysis.prediction_reliability:.3f}",
            f"Consensus Quality: {race_analysis.consensus_quality:.3f}",
            "",
            "TOP PICKS:",
            "-" * 20,
        ]

        for idx, (horse, score) in enumerate(race_analysis.top_picks, 1):
            lines.append(f"{idx}. {horse} (Score: {score:.3f})")

        lines.extend(["", "BETTING OPPORTUNITIES:", "-" * 25])

        for horse, value, reason in race_analysis.betting_opportunities:
            lines.append(f"• {horse}: {reason} (Value: {value:.3f})")

        lines.extend(
            [
                "",
                "DETAILED PREDICTIONS:",
                "-" * 25,
                f"{'Horse':<15} {'Pos':<4} {'Rating':<7} {'Prob':<6} {'Conf':<6} {'Bet Rec':<12}",
            ]
        )

        for pred in race_analysis.enhanced_predictions:
            lines.append(
                f"{pred.horse_name:<15} {pred.recommended_position:<4} "
                f"{pred.consensus_rating:<7.1f} {pred.consensus_win_probability:<6.3f} "
                f"{pred.prediction_confidence:<6.3f} {pred.betting_recommendation:<12}"
            )

        # Write to file
        with open(filepath, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"Race analysis exported to {filepath}")
        return filepath


def demo_enhanced_racing_intelligence():
    """Demonstrate the complete v2.01 enhanced racing intelligence system."""
    print("🏇 V2.01 Enhanced Racing Intelligence Demo")
    print("=" * 60)

    # Sample race data
    sample_data = pd.DataFrame(
        {
            "name": ["Thunder Bolt", "Lightning Strike", "Storm Chaser", "Wind Runner"],
            "age": [5, 4, 6, 5],
            "Total_races": [20, 25, 30, 22],
            "Percentage_wins": [0.25, 0.20, 0.15, 0.18],
            "Percentage_placed": [0.45, 0.40, 0.35, 0.38],
            "Flat_Turf_rate": [0.28, 0.22, 0.18, 0.20],
        }
    )

    # Initialize enhanced system
    enhanced_system = V201EnhancedRacingIntelligence()

    # Perform complete analysis
    race_context = {
        "race_id": "DEMO_ENHANCED_001",
        "surface": "turf",
        "distance": "1m2f",
        "class": 3,
    }

    analysis = enhanced_system.analyze_race_complete(
        sample_data, race_context=race_context
    )

    print(f"\n🎯 Enhanced Analysis Results:")
    print(f"Race: {analysis.race_id}")
    print(f"Market Efficiency: {analysis.market_efficiency:.3f}")
    print(f"Prediction Reliability: {analysis.prediction_reliability:.3f}")
    print(f"Consensus Quality: {analysis.consensus_quality:.3f}")

    print(f"\n🏆 Top Picks:")
    for idx, (horse, score) in enumerate(analysis.top_picks, 1):
        print(f"  {idx}. {horse} (Score: {score:.3f})")

    print(f"\n💰 Betting Opportunities:")
    for horse, value, reason in analysis.betting_opportunities:
        print(f"  • {horse}: {reason} (Value: {value:.3f})")

    # Export analysis
    export_file = enhanced_system.export_race_analysis(
        analysis, "demo_enhanced_analysis.txt"
    )
    print(f"\n📋 Complete analysis exported to: {export_file}")

    # Demo result recording
    demo_results = {
        "Thunder Bolt": 2,
        "Lightning Strike": 1,
        "Storm Chaser": 4,
        "Wind Runner": 3,
    }

    enhanced_system.record_race_result(analysis, demo_results)
    print(f"\n✅ Race results recorded for validation")


if __name__ == "__main__":
    demo_enhanced_racing_intelligence()
