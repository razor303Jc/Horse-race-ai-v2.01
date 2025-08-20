"""
Reduced Stake Dutching Strategy Implementation

Implements the reduced stake dutching betting strategy which calculates
optimized stakes based on odds to guarantee profit regardless of which selection wins.

Based on ProfitDuel's dutching guide:
https://www.profitduel.com/blog/what-is-dutching

Author: Horse Racing AI System
Date: August 2025
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DutchingResult(Enum):
    """Result status of dutching calculation"""

    SUCCESS = "success"
    INSUFFICIENT_SELECTIONS = "insufficient_selections"
    NO_PROFIT_OPPORTUNITY = "no_profit_opportunity"
    INVALID_ODDS = "invalid_odds"
    INSUFFICIENT_BANKROLL = "insufficient_bankroll"


@dataclass
class DutchingSelection:
    """Represents a selection for dutching"""

    horse_name: str
    odds: float
    ai_confidence: float
    selection_id: str
    jockey: Optional[str] = None
    trainer: Optional[str] = None

    def __post_init__(self):
        """Validate selection data"""
        if self.odds <= 1.0:
            raise ValueError(f"Odds must be > 1.0, got {self.odds}")
        if not 0 <= self.ai_confidence <= 100:
            msg = f"AI confidence must be 0-100, got {self.ai_confidence}"
            raise ValueError(msg)


@dataclass
class DutchingStake:
    """Represents calculated stake for a selection"""

    selection: DutchingSelection
    stake: Decimal
    potential_return: Decimal
    guaranteed_profit: Decimal

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "horse_name": self.selection.horse_name,
            "odds": self.selection.odds,
            "ai_confidence": self.selection.ai_confidence,
            "stake": float(self.stake),
            "potential_return": float(self.potential_return),
            "guaranteed_profit": float(self.guaranteed_profit),
            "selection_id": self.selection.selection_id,
        }


@dataclass
class DutchingPlan:
    """Complete dutching betting plan"""

    selections: List[DutchingStake]
    total_stake: Decimal
    guaranteed_profit: Decimal
    profit_margin: float
    roi_percentage: float
    race_id: str
    strategy_confidence: float

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "selections": [s.to_dict() for s in self.selections],
            "total_stake": float(self.total_stake),
            "guaranteed_profit": float(self.guaranteed_profit),
            "profit_margin": self.profit_margin,
            "roi_percentage": self.roi_percentage,
            "race_id": self.race_id,
            "strategy_confidence": self.strategy_confidence,
            "selection_count": len(self.selections),
        }


class ReducedStakeDutching:
    """
    Implements reduced stake dutching strategy for guaranteed profit betting.

    This strategy calculates optimal stakes across multiple selections to ensure
    profit regardless of which selection wins, based on their odds.
    """

    def __init__(
        self,
        min_profit_margin: float = 5.0,
        max_selections: int = 4,
        min_ai_confidence: float = 60.0,
        precision: int = 2,
    ):
        """Initialize dutching strategy"""
        self.min_profit_margin = min_profit_margin
        self.max_selections = max_selections
        self.min_ai_confidence = min_ai_confidence
        self.precision = precision

        logger.info(
            f"ReducedStakeDutching initialized: "
            f"{min_profit_margin}% min profit margin"
        )

    def validate_selections(
        self, selections: List[DutchingSelection]
    ) -> Tuple[bool, str]:
        """Validate selections for dutching suitability"""
        if len(selections) < 2:
            return False, "Need at least 2 selections for dutching"

        if len(selections) > self.max_selections:
            return False, f"Too many selections (max {self.max_selections})"

        for selection in selections:
            if selection.ai_confidence < self.min_ai_confidence:
                msg = (
                    f"Selection {selection.horse_name} has "
                    f"insufficient AI confidence"
                )
                return False, msg

            if selection.odds <= 1.0:
                msg = f"Invalid odds for {selection.horse_name}: " f"{selection.odds}"
                return False, msg

        return True, "Selections validated successfully"

    def calculate_dutching_opportunity(
        self, selections: List[DutchingSelection]
    ) -> Tuple[bool, float]:
        """Check if selections present a profitable dutching opportunity"""
        # Calculate total implied probability
        total_implied_probability = sum(
            1.0 / selection.odds for selection in selections
        )

        # For profit, total implied probability must be less than 1.0
        is_profitable = total_implied_probability < 1.0

        logger.info(
            f"Dutching opportunity: "
            f"implied_prob={total_implied_probability:.4f}, "
            f"profitable={is_profitable}"
        )

        return is_profitable, total_implied_probability

    def calculate_optimal_stakes(
        self, selections: List[DutchingSelection], total_budget: Decimal
    ) -> Tuple[DutchingResult, Optional[DutchingPlan]]:
        """Calculate optimal stakes for reduced stake dutching"""
        try:
            # Validate inputs
            is_valid, error_msg = self.validate_selections(selections)
            if not is_valid:
                logger.error(f"Selection validation failed: {error_msg}")
                return DutchingResult.INSUFFICIENT_SELECTIONS, None

            # Check profitability
            is_profitable, total_implied_prob = self.calculate_dutching_opportunity(
                selections
            )
            if not is_profitable:
                logger.warning(
                    f"No profit opportunity - implied probability: "
                    f"{total_implied_prob:.4f}"
                )
                return DutchingResult.NO_PROFIT_OPPORTUNITY, None

            # Calculate optimal stakes using reduced stake method
            stakes = []
            total_stake_required = Decimal("0")

            # Calculate stake for each selection
            for selection in selections:
                # Stake = (Total Budget / Odds) / Total Implied Probability
                stake = (total_budget / Decimal(str(selection.odds))) / Decimal(
                    str(total_implied_prob)
                )
                stake = stake.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                potential_return = stake * Decimal(str(selection.odds))

                stakes.append(
                    {
                        "selection": selection,
                        "stake": stake,
                        "potential_return": potential_return,
                    }
                )

                total_stake_required += stake

            # Calculate guaranteed profit (return from any win minus total stakes)
            guaranteed_profit = stakes[0]["potential_return"] - total_stake_required

            # Verify profit margin meets minimum requirement
            profit_margin = (
                float(guaranteed_profit) / float(total_stake_required)
            ) * 100
            if profit_margin < self.min_profit_margin:
                logger.warning(
                    f"Profit margin {profit_margin:.2f}% below "
                    f"minimum {self.min_profit_margin}%"
                )
                return DutchingResult.NO_PROFIT_OPPORTUNITY, None

            # Create dutching stakes
            dutching_stakes = []
            for stake_info in stakes:
                dutching_stake = DutchingStake(
                    selection=stake_info["selection"],
                    stake=stake_info["stake"],
                    potential_return=stake_info["potential_return"],
                    guaranteed_profit=guaranteed_profit,
                )
                dutching_stakes.append(dutching_stake)

            # Calculate strategy confidence based on AI confidence of selections
            strategy_confidence = sum(s.ai_confidence for s in selections) / len(
                selections
            )

            # Create dutching plan
            plan = DutchingPlan(
                selections=dutching_stakes,
                total_stake=total_stake_required,
                guaranteed_profit=guaranteed_profit,
                profit_margin=profit_margin,
                roi_percentage=(float(guaranteed_profit) / float(total_stake_required))
                * 100,
                race_id="",  # To be set by caller
                strategy_confidence=strategy_confidence,
            )

            logger.info(
                f"Dutching plan: {len(selections)} selections, "
                f"£{total_stake_required} stake, "
                f"£{guaranteed_profit} profit, "
                f"{profit_margin:.2f}% margin"
            )

            return DutchingResult.SUCCESS, plan

        except Exception as e:
            logger.error(f"Error calculating dutching stakes: {str(e)}")
            return DutchingResult.INVALID_ODDS, None

    def assess_dutching_suitability(self, selections: List[DutchingSelection]) -> Dict:
        """Assess how suitable selections are for dutching"""
        assessment = {
            "suitable": False,
            "confidence_score": 0.0,
            "reasons": [],
            "warnings": [],
            "selection_count": len(selections),
        }

        try:
            # Check basic requirements
            if len(selections) < 2:
                assessment["reasons"].append("Need at least 2 selections for dutching")
                return assessment

            # Check AI confidence levels
            avg_confidence = sum(s.ai_confidence for s in selections) / len(selections)
            if avg_confidence < self.min_ai_confidence:
                assessment["warnings"].append(
                    f"Average AI confidence {avg_confidence:.1f}% " f"below threshold"
                )

            # Check odds distribution
            odds_range = max(s.odds for s in selections) - min(
                s.odds for s in selections
            )
            if odds_range < 1.0:
                assessment["warnings"].append(
                    "Narrow odds range may limit profit potential"
                )

            # Check profitability
            is_profitable, total_implied_prob = self.calculate_dutching_opportunity(
                selections
            )
            if not is_profitable:
                assessment["reasons"].append(
                    f"No profit opportunity (implied prob: "
                    f"{total_implied_prob:.3f})"
                )
                return assessment

            # Calculate potential profit margin
            profit_margin = ((1.0 - total_implied_prob) / total_implied_prob) * 100

            assessment["suitable"] = True
            assessment["confidence_score"] = min(
                100.0, avg_confidence * (profit_margin / 10.0)
            )
            assessment["profit_margin_estimate"] = profit_margin
            assessment["total_implied_probability"] = total_implied_prob

            if profit_margin > 15.0:
                assessment["reasons"].append("Excellent profit opportunity")
            elif profit_margin > 10.0:
                assessment["reasons"].append("Good profit opportunity")
            elif profit_margin > 5.0:
                assessment["reasons"].append("Moderate profit opportunity")
            else:
                assessment["warnings"].append("Low profit margin")

        except Exception as e:
            logger.error(f"Error in suitability assessment: {str(e)}")
            assessment["reasons"].append(f"Assessment error: {str(e)}")

        return assessment

    def format_dutching_plan(self, plan: DutchingPlan) -> str:
        """Format dutching plan for display"""
        output = []
        output.append("🎯 REDUCED STAKE DUTCHING PLAN")
        output.append("=" * 50)
        output.append(f"Total Stake: £{plan.total_stake:.2f}")
        output.append(f"Guaranteed Profit: £{plan.guaranteed_profit:.2f}")
        output.append(f"Profit Margin: {plan.profit_margin:.2f}%")
        output.append(f"ROI: {plan.roi_percentage:.2f}%")
        output.append(f"Strategy Confidence: {plan.strategy_confidence:.1f}%")
        output.append("")

        output.append("STAKE BREAKDOWN:")
        output.append("-" * 30)

        for stake in plan.selections:
            output.append(f"{stake.selection.horse_name}:")
            output.append(f"  Odds: {stake.selection.odds:.2f}")
            output.append(f"  Stake: £{stake.stake:.2f}")
            output.append(f"  Return: £{stake.potential_return:.2f}")
            output.append(f"  AI Confidence: " f"{stake.selection.ai_confidence:.1f}%")
            output.append("")

        return "\n".join(output)


def create_dutching_selection(
    horse_name: str,
    odds: float,
    ai_confidence: float,
    selection_id: str,
    jockey: str = None,
    trainer: str = None,
) -> DutchingSelection:
    """Helper function to create a dutching selection"""
    return DutchingSelection(
        horse_name=horse_name,
        odds=odds,
        ai_confidence=ai_confidence,
        selection_id=selection_id,
        jockey=jockey,
        trainer=trainer,
    )


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create test selections
    selections = [
        create_dutching_selection("Thunder Strike", 3.5, 75.0, "TS001"),
        create_dutching_selection("Lightning Bolt", 4.2, 70.0, "LB002"),
        create_dutching_selection("Storm Chaser", 5.0, 65.0, "SC003"),
    ]

    # Initialize dutching strategy
    dutching = ReducedStakeDutching(min_profit_margin=5.0)

    # Assess suitability
    assessment = dutching.assess_dutching_suitability(selections)
    print("Suitability Assessment:", assessment)

    if assessment["suitable"]:
        # Calculate dutching plan
        result, plan = dutching.calculate_optimal_stakes(selections, Decimal("100.00"))

        if result == DutchingResult.SUCCESS:
            print(dutching.format_dutching_plan(plan))
        else:
            print(f"Dutching calculation failed: {result}")
    else:
        print("Selections not suitable for dutching")
