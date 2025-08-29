#!/usr/bin/env python3
"""
Strategy-Aware ML Integration Hub
================================

This module serves as the central integration point for incorporating 80/20 and
Dutching betting strategies into the ML models and AI selections system.

The system:
1. Extends existing ML models with strategy awareness
2. Provides strategy recommendations alongside AI predictions
3. Integrates with existing betting infrastructure
4. Enhances AI selections with strategy guidance

Features:
- Seamless integration with existing AI systems
- Strategy-aware feature engineering and modeling
- Real-time strategy recommendations
- Enhanced confidence scoring for betting opportunities
- Production-ready strategy integration

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Import existing systems
from ..integration.ai_betting_integration import (
    AIBettingIntegrationSystem,
    AIBettingResult,
    IntegratedStrategy,
)
from ..ml.enhanced_ml_models import EnhancedMLRatingSystem
from ..betting.advanced_strategies import AdvancedBettingStrategies

# Import new strategy components
from .strategy_enhanced_ai_selections import (
    StrategyEnhancedAIGenerator,
    StrategyAwareSelection,
    StrategyRaceAnalysis,
)
from ..ml.strategy_integrated_ml import (
    StrategyIntegratedMLSystem,
    BettingStrategyMLClassifier,
    IntegratedBettingPrediction,
)

logger = logging.getLogger(__name__)


@dataclass
class StrategyAwareAIResult:
    """Enhanced AI result with integrated strategy recommendations"""

    # Base AI result
    base_ai_result: AIBettingResult

    # Strategy-specific analysis
    strategy_selections: List[StrategyAwareSelection]
    race_strategy_analysis: StrategyRaceAnalysis

    # Enhanced recommendations
    primary_strategy_recommendation: str
    strategy_confidence_score: float
    expected_combined_roi: float

    # Bankroll guidance
    recommended_stakes: Dict[str, float]
    risk_adjusted_allocation: Dict[str, float]

    # Performance prediction
    success_probability: float
    profit_expectation: float


class StrategyAwareMLIntegrationHub:
    """Central hub for strategy-aware ML integration"""

    def __init__(
        self,
        initial_bankroll: float = 1000.0,
        strategy_confidence_threshold: float = 0.7,
    ):
        """
        Initialize the strategy-aware ML integration hub

        Args:
            initial_bankroll: Starting bankroll for betting calculations
            strategy_confidence_threshold: Minimum confidence for strategy recommendations
        """

        # Core systems
        self.ai_betting_system = AIBettingIntegrationSystem(
            initial_bankroll=initial_bankroll,
            ai_confidence_threshold=strategy_confidence_threshold,
        )

        self.strategy_enhanced_generator = StrategyEnhancedAIGenerator()
        self.advanced_betting = AdvancedBettingStrategies(initial_bankroll)

        # Strategy integration
        self.strategy_ml_system = None  # Will be initialized when ML system is set
        self.strategy_confidence_threshold = strategy_confidence_threshold

        # Performance tracking
        self.integration_history: List[StrategyAwareAIResult] = []
        self.strategy_performance_metrics = {
            "80/20_success_rate": 0.0,
            "dutching_success_rate": 0.0,
            "combined_roi": 0.0,
            "total_predictions": 0,
        }

        logger.info("Strategy-Aware ML Integration Hub initialized")

    def set_enhanced_ml_system(self, ml_system: EnhancedMLRatingSystem):
        """Set the enhanced ML system and create strategy integration"""

        self.ai_betting_system.set_ml_rating_system(ml_system)
        self.strategy_ml_system = StrategyIntegratedMLSystem(ml_system)

        logger.info("Enhanced ML system integrated with strategy awareness")

    def analyze_race_with_strategy_integration(
        self,
        race_data: Dict[str, Any],
        horses_data: List[Dict[str, Any]],
        betting_odds: Dict[str, float],
    ) -> StrategyAwareAIResult:
        """
        Comprehensive race analysis with full strategy integration

        Args:
            race_data: Race information
            horses_data: List of horse data
            betting_odds: Current betting odds

        Returns:
            StrategyAwareAIResult with complete analysis
        """

        logger.info(
            f"Analyzing race {race_data.get('race_id', 'Unknown')} with strategy integration"
        )

        try:
            # 1. Get base AI betting analysis
            base_ai_result = self.ai_betting_system.analyze_race_with_ai_betting(
                race_data, horses_data, betting_odds
            )

            # 2. Generate strategy-aware selections
            strategy_race_analysis = self._generate_strategy_race_analysis(
                race_data, horses_data, betting_odds
            )

            # 3. Create integrated strategy recommendations
            strategy_recommendations = self._create_integrated_strategy_recommendations(
                base_ai_result, strategy_race_analysis
            )

            # 4. Calculate enhanced metrics
            enhanced_metrics = self._calculate_enhanced_performance_metrics(
                base_ai_result, strategy_race_analysis, strategy_recommendations
            )

            # 5. Generate final result
            result = StrategyAwareAIResult(
                base_ai_result=base_ai_result,
                strategy_selections=strategy_race_analysis.strategy_selections,
                race_strategy_analysis=strategy_race_analysis,
                primary_strategy_recommendation=strategy_recommendations[
                    "primary_strategy"
                ],
                strategy_confidence_score=strategy_recommendations["confidence"],
                expected_combined_roi=strategy_recommendations["expected_roi"],
                recommended_stakes=strategy_recommendations["stakes"],
                risk_adjusted_allocation=strategy_recommendations["allocation"],
                success_probability=enhanced_metrics["success_probability"],
                profit_expectation=enhanced_metrics["profit_expectation"],
            )

            # 6. Store for tracking
            self.integration_history.append(result)
            self._update_performance_metrics(result)

            return result

        except Exception as e:
            logger.error(f"Error in strategy-aware race analysis: {e}")
            raise

    def _generate_strategy_race_analysis(
        self,
        race_data: Dict[str, Any],
        horses_data: List[Dict[str, Any]],
        betting_odds: Dict[str, float],
    ) -> StrategyRaceAnalysis:
        """Generate comprehensive strategy analysis for the race"""

        # Prepare race data for strategy analysis
        enhanced_race_data = {
            **race_data,
            "horses": horses_data,
            "odds": self._format_odds_for_strategy_analysis(betting_odds),
        }

        # Use strategy-enhanced generator to analyze race
        return self.strategy_enhanced_generator._analyze_race_with_strategies(
            enhanced_race_data
        )

    def _format_odds_for_strategy_analysis(
        self, betting_odds: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Format odds data for strategy analysis"""

        formatted_odds = {}

        for horse_name, odds in betting_odds.items():
            if isinstance(odds, dict):
                formatted_odds[horse_name] = odds
            else:
                # Assume single odds value is win odds
                formatted_odds[horse_name] = {
                    "win": float(odds),
                    "place": float(odds) / 3,  # Standard place odds approximation
                }

        return formatted_odds

    def _create_integrated_strategy_recommendations(
        self, base_ai_result: AIBettingResult, strategy_analysis: StrategyRaceAnalysis
    ) -> Dict[str, Any]:
        """Create integrated recommendations combining AI and strategy analysis"""

        recommendations = {
            "primary_strategy": "Standard Betting",
            "confidence": 0.7,
            "expected_roi": 0.0,
            "stakes": {},
            "allocation": {},
        }

        # Analyze best opportunities
        best_80_20 = strategy_analysis.best_eighty_twenty_selections
        best_dutching = strategy_analysis.best_dutching_combinations

        # Determine primary strategy
        if best_80_20 and best_80_20[0].strategy_confidence > 0.8:
            recommendations["primary_strategy"] = "80/20 Strategy"
            recommendations["confidence"] = best_80_20[0].strategy_confidence
            recommendations["expected_roi"] = best_80_20[0].expected_strategy_roi

            # Calculate stakes for 80/20 selections
            for selection in best_80_20[:3]:  # Top 3 selections
                recommendations["stakes"][selection.horse_name] = {
                    "strategy": "80/20",
                    "total_stake": selection.optimal_stake_percentage,
                    "win_stake": selection.optimal_stake_percentage * 0.2,
                    "place_stake": selection.optimal_stake_percentage * 0.8,
                }

        elif best_dutching and len(best_dutching[0]) >= 2:
            recommendations["primary_strategy"] = "Dutching Strategy"

            # Calculate combined confidence for dutching
            dutching_horses = best_dutching[0]
            avg_confidence = np.mean([h.strategy_confidence for h in dutching_horses])
            avg_roi = np.mean([h.expected_strategy_roi for h in dutching_horses])

            recommendations["confidence"] = avg_confidence
            recommendations["expected_roi"] = avg_roi

            # Calculate dutching stakes
            total_dutching_stake = sum(
                h.optimal_stake_percentage for h in dutching_horses
            )
            total_dutching_stake = min(total_dutching_stake, 0.06)  # Cap at 6%

            # Distribute stakes among dutching selections
            for selection in dutching_horses:
                stake_proportion = selection.optimal_stake_percentage / sum(
                    h.optimal_stake_percentage for h in dutching_horses
                )
                recommendations["stakes"][selection.horse_name] = {
                    "strategy": "dutching",
                    "total_stake": total_dutching_stake * stake_proportion,
                    "win_stake": total_dutching_stake * stake_proportion,
                    "place_stake": 0.0,  # Dutching typically win only
                }

        # Create allocation recommendation
        recommendations["allocation"] = self._calculate_integrated_allocation(
            recommendations, strategy_analysis
        )

        return recommendations

    def _calculate_integrated_allocation(
        self, recommendations: Dict[str, Any], strategy_analysis: StrategyRaceAnalysis
    ) -> Dict[str, float]:
        """Calculate integrated bankroll allocation"""

        allocation = {"strategy_betting": 0.0, "value_betting": 0.0, "reserve": 0.9}

        # Calculate strategy betting allocation
        total_strategy_stakes = sum(
            stake_info["total_stake"]
            for stake_info in recommendations["stakes"].values()
        )

        allocation["strategy_betting"] = min(total_strategy_stakes, 0.1)  # Max 10%

        # Add value betting allocation for other opportunities
        other_value_bets = [
            s
            for s in strategy_analysis.strategy_selections
            if (
                s.horse_name not in recommendations["stakes"]
                and s.recommended_strategy == "Value Bet"
                and s.expected_strategy_roi > 3.0
            )
        ]

        if other_value_bets:
            value_allocation = min(
                len(other_value_bets) * 0.01, 0.03
            )  # 1% per bet, max 3%
            allocation["value_betting"] = value_allocation

        # Adjust reserve
        used_allocation = allocation["strategy_betting"] + allocation["value_betting"]
        allocation["reserve"] = max(0.87, 1.0 - used_allocation)

        return allocation

    def _calculate_enhanced_performance_metrics(
        self,
        base_ai_result: AIBettingResult,
        strategy_analysis: StrategyRaceAnalysis,
        strategy_recommendations: Dict[str, Any],
    ) -> Dict[str, float]:
        """Calculate enhanced performance metrics"""

        metrics = {"success_probability": 0.7, "profit_expectation": 0.0}

        # Calculate success probability based on combined factors
        ai_confidence = base_ai_result.confidence_score
        strategy_confidence = strategy_recommendations["confidence"]
        expected_roi = strategy_recommendations["expected_roi"]

        # Weighted success probability
        combined_confidence = ai_confidence * 0.4 + strategy_confidence * 0.6

        # Adjust for ROI expectation
        roi_factor = min(expected_roi / 10.0, 1.0)  # ROI factor (10% = 1.0)

        metrics["success_probability"] = combined_confidence * (0.8 + roi_factor * 0.2)

        # Calculate profit expectation
        total_stake = sum(
            stake_info["total_stake"]
            for stake_info in strategy_recommendations["stakes"].values()
        )

        metrics["profit_expectation"] = total_stake * expected_roi / 100.0

        return metrics

    def _update_performance_metrics(self, result: StrategyAwareAIResult):
        """Update internal performance tracking metrics"""

        self.strategy_performance_metrics["total_predictions"] += 1

        # Update based on strategy type
        primary_strategy = result.primary_strategy_recommendation

        if primary_strategy == "80/20 Strategy":
            # Track 80/20 performance (placeholder - would need actual results)
            self.strategy_performance_metrics["80/20_success_rate"] = 0.65

        elif primary_strategy == "Dutching Strategy":
            # Track dutching performance (placeholder - would need actual results)
            self.strategy_performance_metrics["dutching_success_rate"] = 0.58

        # Update combined ROI (placeholder calculation)
        expected_roi = result.expected_combined_roi
        current_roi = self.strategy_performance_metrics["combined_roi"]
        total_predictions = self.strategy_performance_metrics["total_predictions"]

        # Running average
        self.strategy_performance_metrics["combined_roi"] = (
            current_roi * (total_predictions - 1) + expected_roi
        ) / total_predictions

    def get_strategy_performance_summary(self) -> Dict[str, Any]:
        """Get summary of strategy performance metrics"""

        return {
            "total_races_analyzed": len(self.integration_history),
            "strategy_performance": self.strategy_performance_metrics.copy(),
            "recent_results": [
                {
                    "race_id": result.base_ai_result.race_id,
                    "primary_strategy": result.primary_strategy_recommendation,
                    "confidence": result.strategy_confidence_score,
                    "expected_roi": result.expected_combined_roi,
                }
                for result in self.integration_history[-5:]  # Last 5 results
            ],
            "average_confidence": (
                np.mean(
                    [
                        result.strategy_confidence_score
                        for result in self.integration_history
                    ]
                )
                if self.integration_history
                else 0.0
            ),
            "average_expected_roi": (
                np.mean(
                    [
                        result.expected_combined_roi
                        for result in self.integration_history
                    ]
                )
                if self.integration_history
                else 0.0
            ),
        }

    def export_strategy_aware_analysis(
        self, result: StrategyAwareAIResult, format: str = "detailed"
    ) -> str:
        """Export strategy-aware analysis in various formats"""

        if format == "detailed":
            return self._export_detailed_strategy_analysis(result)
        elif format == "summary":
            return self._export_summary_strategy_analysis(result)
        else:
            return json.dumps(asdict(result), indent=2, default=str)

    def _export_detailed_strategy_analysis(self, result: StrategyAwareAIResult) -> str:
        """Export detailed strategy analysis"""

        output = []
        output.append("=" * 80)
        output.append("🎯 STRATEGY-AWARE AI ANALYSIS")
        output.append("=" * 80)
        output.append(f"Race: {result.base_ai_result.race_id}")
        output.append(f"Timestamp: {result.base_ai_result.timestamp}")
        output.append(f"Primary Strategy: {result.primary_strategy_recommendation}")
        output.append(f"Strategy Confidence: {result.strategy_confidence_score:.1%}")
        output.append(f"Expected ROI: {result.expected_combined_roi:.1f}%")
        output.append(f"Success Probability: {result.success_probability:.1%}")
        output.append("")

        # Risk assessment
        output.append("⚠️ RISK ASSESSMENT")
        output.append("-" * 40)
        output.append(f"Base AI Risk: {result.base_ai_result.risk_assessment}")
        output.append(f"Expected Profit: ${result.profit_expectation:.2f}")
        output.append("")

        # Recommended stakes
        if result.recommended_stakes:
            output.append("💰 RECOMMENDED STAKES")
            output.append("-" * 40)
            for horse, stake_info in result.recommended_stakes.items():
                output.append(f"{horse}:")
                output.append(f"  Strategy: {stake_info['strategy']}")
                output.append(f"  Total Stake: {stake_info['total_stake']:.1%}")
                if stake_info.get("win_stake", 0) > 0:
                    output.append(f"  Win Stake: {stake_info['win_stake']:.1%}")
                if stake_info.get("place_stake", 0) > 0:
                    output.append(f"  Place Stake: {stake_info['place_stake']:.1%}")
            output.append("")

        # Bankroll allocation
        output.append("📊 BANKROLL ALLOCATION")
        output.append("-" * 40)
        for category, percentage in result.risk_adjusted_allocation.items():
            output.append(f"{category.replace('_', ' ').title()}: {percentage:.1%}")
        output.append("")

        # Strategy selections summary
        output.append("🐎 STRATEGY SELECTIONS SUMMARY")
        output.append("-" * 40)
        for selection in result.strategy_selections[:5]:  # Top 5
            output.append(
                f"{selection.horse_name}: {selection.recommended_strategy} "
                f"({selection.confidence_tier}, ROI: {selection.expected_strategy_roi:.1f}%)"
            )

        return "\n".join(output)

    def _export_summary_strategy_analysis(self, result: StrategyAwareAIResult) -> str:
        """Export summary strategy analysis"""

        summary_parts = []
        summary_parts.append(f"Race {result.base_ai_result.race_id}")
        summary_parts.append(f"Strategy: {result.primary_strategy_recommendation}")
        summary_parts.append(f"Confidence: {result.strategy_confidence_score:.0%}")
        summary_parts.append(f"Expected ROI: {result.expected_combined_roi:.1f}%")

        if result.recommended_stakes:
            total_stake = sum(
                info["total_stake"] for info in result.recommended_stakes.values()
            )
            summary_parts.append(f"Total Stake: {total_stake:.1%}")

        return " | ".join(summary_parts)

    def train_strategy_integration(self, historical_data: List[Dict]) -> None:
        """Train the strategy integration system with historical data"""

        logger.info("Training strategy integration system...")

        if self.strategy_ml_system:
            self.strategy_ml_system.train_integrated_system(historical_data)
            logger.info("✅ Strategy integration training complete")
        else:
            logger.warning("ML system not set - cannot train strategy integration")

    def save_strategy_models(self, filepath: str) -> None:
        """Save strategy integration models"""

        if self.strategy_ml_system:
            self.strategy_ml_system.save_integrated_models(filepath)
            logger.info(f"Strategy models saved to {filepath}")
        else:
            logger.warning("No strategy ML system to save")

    def load_strategy_models(self, filepath: str) -> None:
        """Load strategy integration models"""

        if self.strategy_ml_system:
            self.strategy_ml_system.load_integrated_models(filepath)
            logger.info(f"Strategy models loaded from {filepath}")
        else:
            logger.warning("No strategy ML system to load models into")


def demonstrate_strategy_aware_integration():
    """Demonstrate the complete strategy-aware integration system"""

    logger.info("🚀 Demonstrating Strategy-Aware ML Integration Hub")

    # Create integration hub
    hub = StrategyAwareMLIntegrationHub(initial_bankroll=5000.0)

    # Create sample enhanced ML system
    enhanced_ml = EnhancedMLRatingSystem(enable_neural_networks=True)
    hub.set_enhanced_ml_system(enhanced_ml)

    # Sample race data
    race_data = {
        "race_id": "DEMO_RACE_001",
        "race_name": "Strategy Integration Demo",
        "distance": "1200m",
        "class": "Class 3",
        "field_size": 8,
    }

    horses_data = [
        {
            "name": "Strategic Star",
            "jockey": "A. Jockey",
            "weight": 57.0,
            "form": "112",
            "recent_form_score": 85,
        },
        {
            "name": "Value Hunter",
            "jockey": "B. Rider",
            "weight": 56.0,
            "form": "321",
            "recent_form_score": 78,
        },
        {
            "name": "Dutch Master",
            "jockey": "C. Pilot",
            "weight": 55.5,
            "form": "213",
            "recent_form_score": 82,
        },
    ]

    betting_odds = {"Strategic Star": 2.5, "Value Hunter": 4.2, "Dutch Master": 5.8}

    # Analyze race with strategy integration
    result = hub.analyze_race_with_strategy_integration(
        race_data, horses_data, betting_odds
    )

    # Export detailed analysis
    detailed_analysis = hub.export_strategy_aware_analysis(result, "detailed")
    print(detailed_analysis)

    # Export summary
    summary = hub.export_strategy_aware_analysis(result, "summary")
    print(f"\nSUMMARY: {summary}")

    # Show performance metrics
    performance = hub.get_strategy_performance_summary()
    print(f"\nPERFORMANCE METRICS:")
    print(json.dumps(performance, indent=2))

    return hub, result


if __name__ == "__main__":
    # Run demonstration
    demonstrate_strategy_aware_integration()
