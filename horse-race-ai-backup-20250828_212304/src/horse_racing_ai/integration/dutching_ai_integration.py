"""
Dutching AI Integration Layer

Integrates the reduced stake dutching strategy with the Enhanced AI Selections
system to provide profitable multi-horse betting recommendations.

This module bridges AI confidence scoring with dutching calculations to identify
and execute optimal multi-selection betting opportunities.

Author: Horse Racing AI System
Date: August 2025
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
from dataclasses import dataclass
import json

# Import dutching components
from ..betting.reduced_stake_dutching import (
    ReducedStakeDutching,
    DutchingSelection,
    DutchingPlan,
    DutchingResult,
    create_dutching_selection,
)

logger = logging.getLogger(__name__)


@dataclass
class DutchingRecommendation:
    """Represents a dutching recommendation with AI analysis"""

    plan: DutchingPlan
    ai_analysis: Dict
    risk_assessment: Dict
    execution_guidance: Dict
    confidence_breakdown: Dict

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "plan": self.plan.to_dict(),
            "ai_analysis": self.ai_analysis,
            "risk_assessment": self.risk_assessment,
            "execution_guidance": self.execution_guidance,
            "confidence_breakdown": self.confidence_breakdown,
            "timestamp": str(self.plan.race_id),
        }


class DutchingAIIntegration:
    """
    Integrates dutching strategy with AI selections to provide intelligent
    multi-horse betting recommendations.
    """

    def __init__(
        self,
        min_selections: int = 2,
        max_selections: int = 4,
        min_ai_confidence: float = 65.0,
        min_profit_margin: float = 8.0,
        confidence_threshold_adjustment: float = 5.0,
    ):
        """
        Initialize dutching AI integration

        Args:
            min_selections: Minimum number of selections for dutching
            max_selections: Maximum number of selections for dutching
            min_ai_confidence: Minimum AI confidence threshold
            min_profit_margin: Minimum profit margin required
            confidence_threshold_adjustment: Confidence boost for dutching
        """
        self.min_selections = min_selections
        self.max_selections = max_selections
        self.min_ai_confidence = min_ai_confidence
        self.min_profit_margin = min_profit_margin
        self.confidence_threshold_adjustment = confidence_threshold_adjustment

        # Initialize dutching strategy
        self.dutching_strategy = ReducedStakeDutching(
            min_profit_margin=min_profit_margin,
            max_selections=max_selections,
            min_ai_confidence=min_ai_confidence,
        )

        logger.info(
            f"DutchingAIIntegration initialized: "
            f"min_confidence={min_ai_confidence}%, "
            f"min_profit={min_profit_margin}%"
        )

    def convert_ai_selections_to_dutching(
        self, ai_selections: List[Dict]
    ) -> List[DutchingSelection]:
        """
        Convert AI selections to dutching selections

        Args:
            ai_selections: List of AI selection dictionaries

        Returns:
            List of DutchingSelection objects
        """
        dutching_selections = []

        for i, selection in enumerate(ai_selections):
            try:
                # Extract required fields with fallbacks
                horse_name = selection.get("horse_name", f"Horse_{i+1}")
                odds = float(selection.get("odds", 0.0))

                # Calculate combined AI confidence
                ai_confidence = self._calculate_combined_confidence(selection)

                # Create selection ID
                selection_id = selection.get("selection_id", f"SEL_{i+1:03d}")

                # Extract optional fields
                jockey = selection.get("jockey")
                trainer = selection.get("trainer")

                # Validate minimum requirements
                if odds <= 1.0:
                    logger.warning(f"Skipping {horse_name}: invalid odds {odds}")
                    continue

                if ai_confidence < self.min_ai_confidence:
                    logger.warning(
                        f"Skipping {horse_name}: "
                        f"low confidence {ai_confidence:.1f}%"
                    )
                    continue

                dutching_selection = create_dutching_selection(
                    horse_name=horse_name,
                    odds=odds,
                    ai_confidence=ai_confidence,
                    selection_id=selection_id,
                    jockey=jockey,
                    trainer=trainer,
                )

                dutching_selections.append(dutching_selection)

            except Exception as e:
                logger.error(f"Error converting selection {i}: {str(e)}")
                continue

        logger.info(
            f"Converted {len(dutching_selections)} AI selections "
            f"to dutching selections"
        )

        return dutching_selections

    def _calculate_combined_confidence(self, selection: Dict) -> float:
        """
        Calculate combined AI confidence from multiple components

        Args:
            selection: AI selection dictionary

        Returns:
            Combined confidence score
        """
        # Extract individual confidence scores
        form_confidence = selection.get("form_confidence", 0.0)
        track_confidence = selection.get("track_confidence", 0.0)
        jockey_confidence = selection.get("jockey_confidence", 0.0)
        value_confidence = selection.get("value_confidence", 0.0)
        weather_confidence = selection.get("weather_confidence", 0.0)

        # Use overall confidence if available, otherwise calculate weighted average
        if "ai_confidence" in selection:
            base_confidence = float(selection["ai_confidence"])
        elif "overall_confidence" in selection:
            base_confidence = float(selection["overall_confidence"])
        else:
            # Weighted combination of individual components
            confidence_scores = [
                form_confidence * 0.3,  # Form is most important
                track_confidence * 0.25,  # Track conditions significant
                jockey_confidence * 0.2,  # Jockey performance important
                value_confidence * 0.15,  # Value analysis
                weather_confidence * 0.1,  # Weather impact
            ]
            base_confidence = sum(confidence_scores)

        # Apply dutching confidence adjustment (dutching reduces individual risk)
        adjusted_confidence = min(
            100.0, base_confidence + self.confidence_threshold_adjustment
        )

        return adjusted_confidence

    def identify_dutching_opportunities(
        self, race_data: Dict
    ) -> List[DutchingRecommendation]:
        """
        Identify profitable dutching opportunities from race data

        Args:
            race_data: Complete race data with AI selections

        Returns:
            List of dutching recommendations
        """
        recommendations = []

        try:
            # Extract AI selections
            ai_selections = race_data.get("ai_selections", [])
            if not ai_selections:
                logger.warning("No AI selections found in race data")
                return recommendations

            # Convert to dutching selections
            dutching_selections = self.convert_ai_selections_to_dutching(ai_selections)

            if len(dutching_selections) < self.min_selections:
                logger.info(
                    f"Insufficient selections for dutching: "
                    f"{len(dutching_selections)} < {self.min_selections}"
                )
                return recommendations

            # Generate combinations of different sizes
            for combo_size in range(
                self.min_selections,
                min(len(dutching_selections) + 1, self.max_selections + 1),
            ):

                combinations = self._generate_selection_combinations(
                    dutching_selections, combo_size
                )

                for combination in combinations:
                    recommendation = self._evaluate_dutching_combination(
                        combination, race_data
                    )

                    if recommendation:
                        recommendations.append(recommendation)

            # Sort by profit margin and confidence
            recommendations.sort(
                key=lambda x: (x.plan.profit_margin, x.plan.strategy_confidence),
                reverse=True,
            )

            logger.info(f"Generated {len(recommendations)} dutching recommendations")

        except Exception as e:
            logger.error(f"Error identifying dutching opportunities: {str(e)}")

        return recommendations

    def _generate_selection_combinations(
        self, selections: List[DutchingSelection], size: int
    ) -> List[List[DutchingSelection]]:
        """Generate combinations of selections for dutching"""
        from itertools import combinations

        if size > len(selections):
            return []

        return [list(combo) for combo in combinations(selections, size)]

    def _evaluate_dutching_combination(
        self, selections: List[DutchingSelection], race_data: Dict
    ) -> Optional[DutchingRecommendation]:
        """
        Evaluate a specific combination of selections for dutching

        Args:
            selections: List of selections to evaluate
            race_data: Complete race data

        Returns:
            DutchingRecommendation if profitable, None otherwise
        """
        try:
            # Assess suitability
            assessment = self.dutching_strategy.assess_dutching_suitability(selections)

            if not assessment["suitable"]:
                return None

            # Calculate dutching plan with standard budget
            result, plan = self.dutching_strategy.calculate_optimal_stakes(
                selections, Decimal("100.00")
            )

            if result != DutchingResult.SUCCESS or not plan:
                return None

            # Set race ID
            plan.race_id = race_data.get("race_id", "UNKNOWN")

            # Generate AI analysis
            ai_analysis = self._generate_ai_analysis(selections, race_data)

            # Assess risk
            risk_assessment = self._assess_risk(plan, selections, race_data)

            # Generate execution guidance
            execution_guidance = self._generate_execution_guidance(
                plan, risk_assessment
            )

            # Create confidence breakdown
            confidence_breakdown = self._create_confidence_breakdown(
                selections, assessment
            )

            recommendation = DutchingRecommendation(
                plan=plan,
                ai_analysis=ai_analysis,
                risk_assessment=risk_assessment,
                execution_guidance=execution_guidance,
                confidence_breakdown=confidence_breakdown,
            )

            return recommendation

        except Exception as e:
            logger.error(f"Error evaluating dutching combination: {str(e)}")
            return None

    def _generate_ai_analysis(
        self, selections: List[DutchingSelection], race_data: Dict
    ) -> Dict:
        """Generate AI analysis for dutching selections"""
        return {
            "selection_analysis": [
                {
                    "horse_name": sel.horse_name,
                    "ai_confidence": sel.ai_confidence,
                    "odds": sel.odds,
                    "implied_probability": round(1.0 / sel.odds * 100, 2),
                    "value_rating": (
                        "High"
                        if sel.ai_confidence > 75
                        else "Medium" if sel.ai_confidence > 65 else "Low"
                    ),
                }
                for sel in selections
            ],
            "race_context": {
                "race_type": race_data.get("race_type", "Unknown"),
                "distance": race_data.get("distance", "Unknown"),
                "going": race_data.get("going", "Unknown"),
                "prize_money": race_data.get("prize_money", "Unknown"),
            },
            "strategy_rationale": (
                f"Dutching {len(selections)} selections with combined "
                f"confidence of {sum(s.ai_confidence for s in selections) / len(selections):.1f}% "
                f"provides risk-reduced profit opportunity"
            ),
        }

    def _assess_risk(
        self, plan: DutchingPlan, selections: List[DutchingSelection], race_data: Dict
    ) -> Dict:
        """Assess risk factors for dutching plan"""
        # Calculate risk metrics
        confidence_std = self._calculate_confidence_std(selections)
        odds_range = max(s.odds for s in selections) - min(s.odds for s in selections)

        risk_level = "Low"
        if confidence_std > 10 or odds_range > 3.0:
            risk_level = "Medium"
        if confidence_std > 15 or odds_range > 5.0:
            risk_level = "High"

        return {
            "overall_risk": risk_level,
            "confidence_consistency": (
                "High"
                if confidence_std < 8
                else "Medium" if confidence_std < 15 else "Low"
            ),
            "odds_distribution": (
                "Narrow"
                if odds_range < 2.0
                else "Medium" if odds_range < 4.0 else "Wide"
            ),
            "market_exposure": len(selections),
            "profit_certainty": "Guaranteed" if plan.profit_margin > 0 else "None",
            "bankroll_impact": f"{(float(plan.total_stake) / 100.0) * 100:.1f}% of budget",
        }

    def _calculate_confidence_std(self, selections: List[DutchingSelection]) -> float:
        """Calculate standard deviation of AI confidence scores"""
        if len(selections) < 2:
            return 0.0

        confidences = [s.ai_confidence for s in selections]
        mean = sum(confidences) / len(confidences)
        variance = sum((c - mean) ** 2 for c in confidences) / len(confidences)
        return variance**0.5

    def _generate_execution_guidance(
        self, plan: DutchingPlan, risk_assessment: Dict
    ) -> Dict:
        """Generate execution guidance for dutching plan"""
        return {
            "recommended_action": (
                "Execute" if risk_assessment["overall_risk"] != "High" else "Caution"
            ),
            "timing": "Place bets close to race start for best odds",
            "stake_management": f"Total stake: £{plan.total_stake:.2f}",
            "profit_expectation": f"Guaranteed profit: £{plan.guaranteed_profit:.2f}",
            "monitoring": "Monitor odds changes before race start",
            "exit_strategy": "No exit needed - guaranteed profit regardless of winner",
        }

    def _create_confidence_breakdown(
        self, selections: List[DutchingSelection], assessment: Dict
    ) -> Dict:
        """Create detailed confidence breakdown"""
        return {
            "individual_confidences": [
                {
                    "horse": sel.horse_name,
                    "confidence": sel.ai_confidence,
                    "contribution": sel.ai_confidence / len(selections),
                }
                for sel in selections
            ],
            "average_confidence": sum(s.ai_confidence for s in selections)
            / len(selections),
            "confidence_range": (
                min(s.ai_confidence for s in selections),
                max(s.ai_confidence for s in selections),
            ),
            "suitability_score": assessment.get("confidence_score", 0.0),
            "profit_confidence": 100.0 if assessment.get("suitable", False) else 0.0,
        }

    def format_dutching_recommendation(
        self, recommendation: DutchingRecommendation
    ) -> str:
        """Format dutching recommendation for display"""
        output = []
        output.append("🎯 DUTCHING RECOMMENDATION")
        output.append("=" * 60)
        output.append("")

        # Plan summary
        plan = recommendation.plan
        output.append("DUTCHING PLAN SUMMARY:")
        output.append(f"  • Total Stake: £{plan.total_stake:.2f}")
        output.append(f"  • Guaranteed Profit: £{plan.guaranteed_profit:.2f}")
        output.append(f"  • Profit Margin: {plan.profit_margin:.2f}%")
        output.append(f"  • ROI: {plan.roi_percentage:.2f}%")
        output.append(f"  • Strategy Confidence: {plan.strategy_confidence:.1f}%")
        output.append("")

        # Stakes breakdown
        output.append("STAKE ALLOCATION:")
        for stake in plan.selections:
            output.append(f"  • {stake.selection.horse_name}:")
            output.append(f"    - Odds: {stake.selection.odds:.2f}")
            output.append(f"    - Stake: £{stake.stake:.2f}")
            output.append(f"    - Potential Return: £{stake.potential_return:.2f}")
            output.append(f"    - AI Confidence: {stake.selection.ai_confidence:.1f}%")
        output.append("")

        # Risk assessment
        risk = recommendation.risk_assessment
        output.append(f"RISK ASSESSMENT: {risk['overall_risk']}")
        output.append(f"  • Confidence Consistency: {risk['confidence_consistency']}")
        output.append(f"  • Odds Distribution: {risk['odds_distribution']}")
        output.append(f"  • Profit Certainty: {risk['profit_certainty']}")
        output.append("")

        # Execution guidance
        guidance = recommendation.execution_guidance
        output.append(f"EXECUTION GUIDANCE: {guidance['recommended_action']}")
        output.append(f"  • {guidance['timing']}")
        output.append(f"  • {guidance['profit_expectation']}")
        output.append(f"  • {guidance['monitoring']}")

        return "\n".join(output)
