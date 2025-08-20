#!/usr/bin/env python3
"""
Enhanced AI Selections with Betting Strategy Integration
=======================================================

This module extends the Enhanced AI Selections Generator to include 80/20 and
Dutching betting strategy recommendations directly in the AI predictions.

The system integrates betting strategies at the prediction level, allowing the
ML models to be aware of profitable betting opportunities and factor them into
their recommendations.

Features:
- Strategy-aware AI selections
- Betting strategy recommendations integrated with predictions
- Enhanced confidence scoring based on strategy suitability
- Real-time strategy opportunity identification
- Comprehensive betting guidance

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Import enhanced AI selections
from ..enhanced_ai_selections_generator import EnhancedAISelectionsGenerator

# Import betting strategies
from ..betting.eighty_twenty_strategy import (
    EightyTwentyStrategy,
    EightyTwentyBet,
    StakeAllocation,
)
from ..betting.reduced_stake_dutching import (
    ReducedStakeDutching,
    DutchingResult,
    DutchingSelection,
    DutchingPlan,
)

# Import strategy integration
from .strategy_integrated_ml import (
    StrategyIntegratedMLSystem,
    BettingStrategyMLClassifier,
    IntegratedBettingPrediction,
)

logger = logging.getLogger(__name__)


@dataclass
class StrategyAwareSelection:
    """AI selection enhanced with betting strategy recommendations"""

    # Basic selection info
    horse_name: str
    race_id: str

    # Standard AI predictions
    win_probability: float
    place_probability: float
    ai_confidence: float
    predicted_rating: float

    # Strategy recommendations
    recommended_strategy: str
    strategy_confidence: float
    expected_strategy_roi: float
    optimal_stake_percentage: float

    # Detailed betting guidance
    eighty_twenty_suitable: bool
    dutching_suitable: bool
    strategy_reasoning: List[str]
    betting_advice: str

    # Enhanced metrics
    value_rating: float
    risk_assessment: str
    confidence_tier: str


@dataclass
class StrategyRaceAnalysis:
    """Complete race analysis with strategy recommendations"""

    race_id: str
    race_info: Dict[str, Any]

    # Individual horse selections
    strategy_selections: List[StrategyAwareSelection]

    # Race-level strategy recommendations
    best_eighty_twenty_selections: List[StrategyAwareSelection]
    best_dutching_combinations: List[List[StrategyAwareSelection]]

    # Overall race assessment
    race_strategy_rating: str
    total_opportunity_score: float
    recommended_approach: str
    bankroll_allocation: Dict[str, float]


class StrategyEnhancedAIGenerator(EnhancedAISelectionsGenerator):
    """Enhanced AI generator with integrated betting strategy recommendations"""

    def __init__(self):
        super().__init__()

        # Initialize betting strategies
        self.eighty_twenty_strategy = EightyTwentyStrategy()
        self.dutching_strategy = ReducedStakeDutching()

        # Initialize strategy ML classifier
        self.strategy_classifier = BettingStrategyMLClassifier()

        # Strategy integration settings
        self.strategy_confidence_threshold = 0.65
        self.min_strategy_roi = 3.0
        self.max_strategy_risk = "MEDIUM"

        logger.info("Strategy-Enhanced AI Generator initialized")

    def generate_strategy_aware_selections(
        self, target_date: str = None
    ) -> StrategyRaceAnalysis:
        """Generate AI selections with integrated betting strategy recommendations"""

        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"🎯 Generating strategy-aware selections for {target_date}")

        try:
            # Get race data
            race_data = self._get_race_data(target_date)
            if not race_data:
                logger.warning(f"No race data found for {target_date}")
                return self._create_empty_analysis(target_date)

            # Process each race with strategy integration
            all_strategy_analyses = []

            for race in race_data:
                race_analysis = self._analyze_race_with_strategies(race)
                all_strategy_analyses.append(race_analysis)

            # Return the first race analysis (or combine multiple races)
            if all_strategy_analyses:
                return all_strategy_analyses[0]  # For now, return first race
            else:
                return self._create_empty_analysis(target_date)

        except Exception as e:
            logger.error(f"Error generating strategy-aware selections: {e}")
            return self._create_empty_analysis(target_date)

    def _analyze_race_with_strategies(self, race_data: Dict) -> StrategyRaceAnalysis:
        """Analyze a single race with strategy integration"""

        race_id = race_data.get("race_id", "Unknown")
        horses = race_data.get("horses", [])

        logger.info(f"Analyzing race {race_id} with {len(horses)} horses")

        # Generate strategy-aware selections for each horse
        strategy_selections = []

        for horse in horses:
            selection = self._create_strategy_aware_selection(horse, race_data)
            strategy_selections.append(selection)

        # Identify best opportunities
        best_eighty_twenty = self._identify_best_eighty_twenty_selections(
            strategy_selections
        )

        best_dutching = self._identify_best_dutching_combinations(
            strategy_selections, race_data
        )

        # Generate race-level recommendations
        race_strategy_rating, opportunity_score, recommended_approach = (
            self._assess_race_strategy_potential(strategy_selections)
        )

        # Calculate bankroll allocation
        bankroll_allocation = self._calculate_race_bankroll_allocation(
            best_eighty_twenty, best_dutching
        )

        return StrategyRaceAnalysis(
            race_id=race_id,
            race_info=race_data,
            strategy_selections=strategy_selections,
            best_eighty_twenty_selections=best_eighty_twenty,
            best_dutching_combinations=best_dutching,
            race_strategy_rating=race_strategy_rating,
            total_opportunity_score=opportunity_score,
            recommended_approach=recommended_approach,
            bankroll_allocation=bankroll_allocation,
        )

    def _create_strategy_aware_selection(
        self, horse_data: Dict, race_data: Dict
    ) -> StrategyAwareSelection:
        """Create a strategy-aware selection for a single horse"""

        horse_name = horse_data.get("name", "Unknown")

        # Get basic AI prediction (from parent class methods)
        try:
            basic_prediction = self._generate_enhanced_prediction(horse_data, race_data)
        except:
            # Fallback prediction
            basic_prediction = {
                "win_probability": 0.15,
                "place_probability": 0.35,
                "confidence": 0.70,
                "predicted_rating": 75.0,
            }

        # Get odds data
        odds_data = self._extract_odds_data(horse_data, race_data)

        # Analyze strategy suitability
        strategy_analysis = self._analyze_strategy_suitability(
            horse_data, race_data, odds_data
        )

        # Determine recommended strategy
        recommended_strategy, strategy_confidence, expected_roi = (
            self._determine_recommended_strategy(strategy_analysis, basic_prediction)
        )

        # Calculate optimal stake
        optimal_stake = self._calculate_optimal_stake_percentage(
            expected_roi, strategy_confidence, basic_prediction["confidence"]
        )

        # Generate betting advice
        betting_advice = self._generate_betting_advice(
            strategy_analysis, recommended_strategy, expected_roi
        )

        # Assess value and risk
        value_rating = self._calculate_value_rating(
            basic_prediction, odds_data, expected_roi
        )

        risk_assessment = self._assess_selection_risk(
            strategy_analysis, basic_prediction, odds_data
        )

        confidence_tier = self._determine_confidence_tier(
            basic_prediction["confidence"], strategy_confidence
        )

        return StrategyAwareSelection(
            horse_name=horse_name,
            race_id=race_data.get("race_id", "Unknown"),
            win_probability=basic_prediction["win_probability"],
            place_probability=basic_prediction["place_probability"],
            ai_confidence=basic_prediction["confidence"],
            predicted_rating=basic_prediction["predicted_rating"],
            recommended_strategy=recommended_strategy,
            strategy_confidence=strategy_confidence,
            expected_strategy_roi=expected_roi,
            optimal_stake_percentage=optimal_stake,
            eighty_twenty_suitable=strategy_analysis.get(
                "eighty_twenty_suitable", False
            ),
            dutching_suitable=strategy_analysis.get("dutching_suitable", False),
            strategy_reasoning=strategy_analysis.get("reasoning", []),
            betting_advice=betting_advice,
            value_rating=value_rating,
            risk_assessment=risk_assessment,
            confidence_tier=confidence_tier,
        )

    def _extract_odds_data(self, horse_data: Dict, race_data: Dict) -> Dict:
        """Extract odds data for strategy analysis"""

        horse_name = horse_data.get("name", "Unknown")

        # Try to get odds from various sources
        win_odds = (
            horse_data.get("win_odds")
            or horse_data.get("odds")
            or race_data.get("odds", {}).get(horse_name, {}).get("win")
            or 5.0  # Default
        )

        place_odds = (
            horse_data.get("place_odds")
            or race_data.get("odds", {}).get(horse_name, {}).get("place")
            or win_odds / 3  # Standard place odds approximation
        )

        return {horse_name: {"win": float(win_odds), "place": float(place_odds)}}

    def _analyze_strategy_suitability(
        self, horse_data: Dict, race_data: Dict, odds_data: Dict
    ) -> Dict:
        """Analyze betting strategy suitability for a horse"""

        horse_name = horse_data.get("name", "Unknown")
        win_odds = odds_data.get(horse_name, {}).get("win", 5.0)
        place_odds = odds_data.get(horse_name, {}).get("place", win_odds / 3)

        analysis = {
            "eighty_twenty_suitable": False,
            "dutching_suitable": False,
            "reasoning": [],
        }

        # 80/20 Strategy Analysis
        if win_odds <= 1.8:
            analysis["eighty_twenty_suitable"] = True
            analysis["reasoning"].append(
                "Very short odds - excellent for 80/20 strategy"
            )
        elif win_odds >= 6.0:
            analysis["eighty_twenty_suitable"] = True
            analysis["reasoning"].append("Long odds with place value potential")

        # Check place advantage
        place_probability = horse_data.get("place_probability", 0.35)
        win_probability = horse_data.get("win_probability", 0.15)

        if place_probability > win_probability * 1.5:
            analysis["eighty_twenty_suitable"] = True
            analysis["reasoning"].append("Strong place probability advantage")

        # Dutching Strategy Analysis
        field_size = race_data.get("field_size", 10)

        if 2.0 <= win_odds <= 8.0 and field_size >= 8:
            analysis["dutching_suitable"] = True
            analysis["reasoning"].append("Good odds range and field size for dutching")

        # Market competition analysis for dutching
        race_odds = race_data.get("odds", {})
        if len(race_odds) >= 3:
            competitive_horses = sum(
                1 for odds in race_odds.values() if odds.get("win", 10) < 6.0
            )
            if competitive_horses >= 3:
                analysis["dutching_suitable"] = True
                analysis["reasoning"].append("Multiple competitive horses for dutching")

        return analysis

    def _determine_recommended_strategy(
        self, strategy_analysis: Dict, prediction: Dict
    ) -> Tuple[str, float, float]:
        """Determine the best strategy recommendation"""

        eighty_twenty_suitable = strategy_analysis.get("eighty_twenty_suitable", False)
        dutching_suitable = strategy_analysis.get("dutching_suitable", False)

        win_prob = prediction["win_probability"]
        confidence = prediction["confidence"]

        if eighty_twenty_suitable and win_prob > 0.2:
            # High confidence 80/20 recommendation
            strategy_confidence = min(confidence * 1.2, 0.95)
            expected_roi = 8.0 if confidence > 0.8 else 5.0
            return "80/20 Strategy", strategy_confidence, expected_roi

        elif dutching_suitable and confidence > 0.7:
            # Dutching recommendation
            strategy_confidence = confidence * 0.9
            expected_roi = 4.0 if confidence > 0.8 else 2.0
            return "Dutching Strategy", strategy_confidence, expected_roi

        elif win_prob > 0.25 and confidence > 0.8:
            # Standard value bet
            strategy_confidence = confidence
            expected_roi = 3.0
            return "Value Bet", strategy_confidence, expected_roi

        else:
            # No strong recommendation
            return "Consider", confidence * 0.7, 0.0

    def _calculate_optimal_stake_percentage(
        self, expected_roi: float, strategy_confidence: float, ai_confidence: float
    ) -> float:
        """Calculate optimal stake as percentage of bankroll"""

        if expected_roi <= 0:
            return 0.0

        # Kelly-inspired calculation
        edge = expected_roi / 100.0
        combined_confidence = (strategy_confidence + ai_confidence) / 2

        # Conservative Kelly fraction
        kelly_fraction = edge * combined_confidence * 0.3  # Conservative multiplier

        # Cap at reasonable limits
        optimal_stake = min(kelly_fraction, 0.05)  # Max 5% of bankroll
        optimal_stake = max(optimal_stake, 0.01) if expected_roi > 2.0 else 0.0

        return optimal_stake

    def _generate_betting_advice(
        self, strategy_analysis: Dict, recommended_strategy: str, expected_roi: float
    ) -> str:
        """Generate human-readable betting advice"""

        advice_parts = []

        if recommended_strategy == "80/20 Strategy":
            advice_parts.append("🎯 80/20 Strategy recommended")
            advice_parts.append("Split stake: 20% win, 80% place")

        elif recommended_strategy == "Dutching Strategy":
            advice_parts.append("🎲 Consider for dutching combination")
            advice_parts.append("Best used with 2-3 other selections")

        elif recommended_strategy == "Value Bet":
            advice_parts.append("💰 Standard value betting opportunity")

        else:
            advice_parts.append("⚠️ Limited betting value identified")

        if expected_roi > 5.0:
            advice_parts.append(f"Strong ROI potential: {expected_roi:.1f}%")
        elif expected_roi > 2.0:
            advice_parts.append(f"Moderate ROI potential: {expected_roi:.1f}%")

        # Add key reasoning
        reasoning = strategy_analysis.get("reasoning", [])
        if reasoning:
            advice_parts.append(f"Key factor: {reasoning[0]}")

        return " | ".join(advice_parts)

    def _calculate_value_rating(
        self, prediction: Dict, odds_data: Dict, expected_roi: float
    ) -> float:
        """Calculate overall value rating (0-100)"""

        win_prob = prediction["win_probability"]
        confidence = prediction["confidence"]

        # Get implied probability from odds
        odds_values = list(odds_data.values())
        if odds_values:
            win_odds = odds_values[0].get("win", 5.0)
            implied_prob = 1.0 / win_odds

            # Value calculation
            value = max(0, win_prob - implied_prob)

            # Combine factors for rating
            value_rating = (
                value * 300  # Pure value
                + expected_roi * 2  # Strategy ROI
                + confidence * 50  # AI confidence
            )

            return min(value_rating, 100.0)

        return 50.0  # Default rating

    def _assess_selection_risk(
        self, strategy_analysis: Dict, prediction: Dict, odds_data: Dict
    ) -> str:
        """Assess overall risk level for the selection"""

        confidence = prediction["confidence"]
        win_prob = prediction["win_probability"]

        # Get odds
        odds_values = list(odds_data.values())
        win_odds = odds_values[0].get("win", 5.0) if odds_values else 5.0

        # Risk factors
        risk_score = 0

        if confidence < 0.7:
            risk_score += 2
        if win_prob < 0.15:
            risk_score += 2
        if win_odds > 8.0:
            risk_score += 1
        if not (
            strategy_analysis.get("eighty_twenty_suitable")
            or strategy_analysis.get("dutching_suitable")
        ):
            risk_score += 1

        if risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_confidence_tier(
        self, ai_confidence: float, strategy_confidence: float
    ) -> str:
        """Determine confidence tier for the selection"""

        combined_confidence = (ai_confidence + strategy_confidence) / 2

        if combined_confidence >= 0.85:
            return "PREMIUM"
        elif combined_confidence >= 0.75:
            return "HIGH"
        elif combined_confidence >= 0.65:
            return "MODERATE"
        else:
            return "LOW"

    def _identify_best_eighty_twenty_selections(
        self, selections: List[StrategyAwareSelection]
    ) -> List[StrategyAwareSelection]:
        """Identify the best 80/20 strategy selections"""

        eighty_twenty_selections = [
            s
            for s in selections
            if s.recommended_strategy == "80/20 Strategy" and s.eighty_twenty_suitable
        ]

        # Sort by strategy confidence and expected ROI
        eighty_twenty_selections.sort(
            key=lambda x: (x.strategy_confidence, x.expected_strategy_roi), reverse=True
        )

        # Return top 3
        return eighty_twenty_selections[:3]

    def _identify_best_dutching_combinations(
        self, selections: List[StrategyAwareSelection], race_data: Dict
    ) -> List[List[StrategyAwareSelection]]:
        """Identify the best dutching combinations"""

        dutching_candidates = [
            s
            for s in selections
            if s.dutching_suitable and s.strategy_confidence > 0.65
        ]

        if len(dutching_candidates) < 2:
            return []

        # Sort by combined score
        dutching_candidates.sort(
            key=lambda x: x.strategy_confidence * x.expected_strategy_roi, reverse=True
        )

        # Create combinations
        combinations = []

        # 2-horse combination
        if len(dutching_candidates) >= 2:
            combinations.append(dutching_candidates[:2])

        # 3-horse combination if field is large enough
        field_size = race_data.get("field_size", 10)
        if len(dutching_candidates) >= 3 and field_size >= 12:
            combinations.append(dutching_candidates[:3])

        return combinations

    def _assess_race_strategy_potential(
        self, selections: List[StrategyAwareSelection]
    ) -> Tuple[str, float, str]:
        """Assess overall race strategy potential"""

        if not selections:
            return "POOR", 0.0, "AVOID"

        # Calculate metrics
        avg_confidence = np.mean([s.strategy_confidence for s in selections])
        max_roi = max([s.expected_strategy_roi for s in selections])
        strategy_count = sum(
            1
            for s in selections
            if s.recommended_strategy in ["80/20 Strategy", "Dutching Strategy"]
        )

        # Opportunity score
        opportunity_score = (
            avg_confidence * 30 + min(max_roi, 15) * 4 + min(strategy_count, 5) * 8
        )

        # Race rating
        if opportunity_score >= 80:
            race_rating = "EXCELLENT"
        elif opportunity_score >= 60:
            race_rating = "GOOD"
        elif opportunity_score >= 40:
            race_rating = "MODERATE"
        else:
            race_rating = "POOR"

        # Recommended approach
        if strategy_count >= 3:
            approach = "MULTIPLE STRATEGIES"
        elif max_roi > 8.0:
            approach = "FOCUS BETTING"
        elif avg_confidence > 0.75:
            approach = "SELECTIVE BETTING"
        else:
            approach = "CAREFUL CONSIDERATION"

        return race_rating, opportunity_score, approach

    def _calculate_race_bankroll_allocation(
        self,
        eighty_twenty_selections: List[StrategyAwareSelection],
        dutching_combinations: List[List[StrategyAwareSelection]],
    ) -> Dict[str, float]:
        """Calculate recommended bankroll allocation for the race"""

        allocation = {
            "80/20_strategy": 0.0,
            "dutching_strategy": 0.0,
            "value_bets": 0.0,
            "reserve": 0.85,  # Keep 85% in reserve
        }

        # Allocate for 80/20 strategies
        if eighty_twenty_selections:
            total_80_20_stake = sum(
                s.optimal_stake_percentage for s in eighty_twenty_selections
            )
            allocation["80/20_strategy"] = min(total_80_20_stake, 0.08)  # Max 8%

        # Allocate for dutching
        if dutching_combinations:
            # Estimate dutching allocation (typically 3-5% per combination)
            dutching_allocation = len(dutching_combinations) * 0.04
            allocation["dutching_strategy"] = min(dutching_allocation, 0.06)  # Max 6%

        # Adjust reserve
        used_allocation = allocation["80/20_strategy"] + allocation["dutching_strategy"]
        allocation["reserve"] = max(0.85, 1.0 - used_allocation)

        return allocation

    def _get_race_data(self, target_date: str) -> List[Dict]:
        """Get race data for target date (placeholder - integrate with actual data source)"""

        # This would integrate with the actual database or data source
        # For now, return sample data

        sample_race = {
            "race_id": f"R_{target_date}_001",
            "field_size": 10,
            "class_rating": 80,
            "prize_money": 25000,
            "horses": [
                {
                    "name": f"Horse_{i}",
                    "win_probability": np.random.uniform(0.05, 0.4),
                    "place_probability": np.random.uniform(0.2, 0.7),
                    "win_odds": np.random.uniform(2.0, 15.0),
                    "form_rating": np.random.uniform(60, 95),
                }
                for i in range(10)
            ],
            "odds": {},
        }

        # Generate odds data
        for horse in sample_race["horses"]:
            horse_name = horse["name"]
            win_odds = horse["win_odds"]
            sample_race["odds"][horse_name] = {"win": win_odds, "place": win_odds / 3}

        return [sample_race]

    def _generate_enhanced_prediction(self, horse_data: Dict, race_data: Dict) -> Dict:
        """Generate enhanced prediction (placeholder - integrate with parent class)"""

        # This would call the parent class's enhanced prediction methods
        # For now, return reasonable estimates

        base_rating = horse_data.get("form_rating", 75)
        win_prob = horse_data.get("win_probability", 0.15)
        place_prob = horse_data.get("place_probability", 0.35)

        return {
            "win_probability": win_prob,
            "place_probability": place_prob,
            "confidence": np.random.uniform(0.65, 0.9),
            "predicted_rating": base_rating,
        }

    def _create_empty_analysis(self, target_date: str) -> StrategyRaceAnalysis:
        """Create empty analysis when no data available"""

        return StrategyRaceAnalysis(
            race_id=f"NO_DATA_{target_date}",
            race_info={},
            strategy_selections=[],
            best_eighty_twenty_selections=[],
            best_dutching_combinations=[],
            race_strategy_rating="NO_DATA",
            total_opportunity_score=0.0,
            recommended_approach="NO_RACING",
            bankroll_allocation={"reserve": 1.0},
        )

    def export_strategy_selections(
        self, analysis: StrategyRaceAnalysis, format: str = "detailed"
    ) -> str:
        """Export strategy selections in various formats"""

        if format == "detailed":
            return self._export_detailed_analysis(analysis)
        elif format == "summary":
            return self._export_summary_analysis(analysis)
        else:
            return self._export_json_analysis(analysis)

    def _export_detailed_analysis(self, analysis: StrategyRaceAnalysis) -> str:
        """Export detailed strategy analysis"""

        output = []
        output.append("=" * 80)
        output.append("🎯 STRATEGY-ENHANCED AI SELECTIONS")
        output.append("=" * 80)
        output.append(f"Race: {analysis.race_id}")
        output.append(f"Strategy Rating: {analysis.race_strategy_rating}")
        output.append(f"Opportunity Score: {analysis.total_opportunity_score:.1f}/100")
        output.append(f"Recommended Approach: {analysis.recommended_approach}")
        output.append("")

        # Bankroll allocation
        output.append("💰 BANKROLL ALLOCATION")
        output.append("-" * 40)
        for strategy, percentage in analysis.bankroll_allocation.items():
            output.append(f"{strategy.replace('_', ' ').title()}: {percentage:.1%}")
        output.append("")

        # Individual selections
        output.append("🐎 INDIVIDUAL SELECTIONS")
        output.append("-" * 40)

        for selection in analysis.strategy_selections:
            output.append(f"\n{selection.horse_name}")
            output.append(f"  Strategy: {selection.recommended_strategy}")
            output.append(
                f"  Confidence: {selection.confidence_tier} ({selection.strategy_confidence:.1%})"
            )
            output.append(f"  Expected ROI: {selection.expected_strategy_roi:.1f}%")
            output.append(f"  Optimal Stake: {selection.optimal_stake_percentage:.1%}")
            output.append(f"  Risk: {selection.risk_assessment}")
            output.append(f"  Advice: {selection.betting_advice}")

        # Best 80/20 selections
        if analysis.best_eighty_twenty_selections:
            output.append("\n🎯 TOP 80/20 STRATEGY SELECTIONS")
            output.append("-" * 40)
            for i, selection in enumerate(analysis.best_eighty_twenty_selections, 1):
                output.append(
                    f"{i}. {selection.horse_name} - ROI: {selection.expected_strategy_roi:.1f}%"
                )

        # Best dutching combinations
        if analysis.best_dutching_combinations:
            output.append("\n🎲 DUTCHING COMBINATIONS")
            output.append("-" * 40)
            for i, combination in enumerate(analysis.best_dutching_combinations, 1):
                horses = [s.horse_name for s in combination]
                output.append(f"{i}. {' + '.join(horses)}")

        return "\n".join(output)

    def _export_summary_analysis(self, analysis: StrategyRaceAnalysis) -> str:
        """Export summary analysis"""

        output = []
        output.append(f"Race {analysis.race_id} - {analysis.race_strategy_rating}")

        if analysis.best_eighty_twenty_selections:
            top_80_20 = analysis.best_eighty_twenty_selections[0]
            output.append(
                f"🎯 Best 80/20: {top_80_20.horse_name} ({top_80_20.expected_strategy_roi:.1f}% ROI)"
            )

        if analysis.best_dutching_combinations:
            top_dutching = analysis.best_dutching_combinations[0]
            horses = [s.horse_name for s in top_dutching]
            output.append(f"🎲 Best Dutching: {' + '.join(horses)}")

        output.append(
            f"💰 Total Allocation: {sum(v for k, v in analysis.bankroll_allocation.items() if k != 'reserve'):.1%}"
        )

        return " | ".join(output)

    def _export_json_analysis(self, analysis: StrategyRaceAnalysis) -> str:
        """Export analysis as JSON"""

        return json.dumps(asdict(analysis), indent=2, default=str)


def demonstrate_strategy_enhanced_ai():
    """Demonstrate the strategy-enhanced AI system"""

    logger.info("🚀 Demonstrating Strategy-Enhanced AI Selections")

    # Create enhanced generator
    generator = StrategyEnhancedAIGenerator()

    # Generate strategy-aware selections
    analysis = generator.generate_strategy_aware_selections()

    # Export detailed analysis
    detailed_report = generator.export_strategy_selections(analysis, "detailed")
    print(detailed_report)

    # Export summary
    summary_report = generator.export_strategy_selections(analysis, "summary")
    print(f"\nSUMMARY: {summary_report}")

    return analysis


if __name__ == "__main__":
    # Run demonstration
    demonstrate_strategy_enhanced_ai()
