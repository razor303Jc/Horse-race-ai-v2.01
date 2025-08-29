#!/usr/bin/env python3
"""
Dutching Strategy Implementation for Horse Racing AI
===================================================

Comprehensive implementation of Dutch betting strategies including:
- Equal stake dutching
- Reduced stake dutching
- Set-amount dutching
- Multi-race dutching
- Integration with AI selections and value assessment

Based on ProfitDuel's comprehensive dutching methodology:
https://www.profitduel.com/blog/what-is-dutching
"""

import logging
import math
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)


class DutchingMethod(Enum):
    """Types of dutching strategies available."""

    EQUAL_STAKE = "equal_stake"  # Same stake on all selections
    REDUCED_STAKE = "reduced_stake"  # Optimized stakes for guaranteed profit
    SET_AMOUNT = "set_amount"  # Fixed total stake distributed optimally
    PERCENTAGE_BANK = "percentage_bank"  # Percentage of bankroll distributed
    AI_WEIGHTED = "ai_weighted"  # AI confidence-weighted distribution


class DutchingRisk(Enum):
    """Risk levels for dutching strategies."""

    CONSERVATIVE = "conservative"  # Lower stakes, guaranteed profits
    MODERATE = "moderate"  # Balanced risk/reward
    AGGRESSIVE = "aggressive"  # Higher stakes, maximum profit potential


@dataclass
class DutchSelection:
    """Individual selection for dutching."""

    horse_name: str
    odds: float  # Decimal odds (e.g., 4.0 for 3/1)
    back_odds: Optional[float] = None  # Back odds if different
    lay_odds: Optional[float] = None  # Lay odds for matched betting
    ai_confidence: Optional[float] = None  # AI confidence score (0-1)
    value_rating: Optional[float] = None  # Value assessment (0-1)
    form_rating: Optional[float] = None  # Form rating (0-1)
    track_rating: Optional[float] = None  # Track rating (0-1)
    jockey_rating: Optional[float] = None  # Jockey rating (0-1)
    going_rating: Optional[float] = None  # Going rating (0-1)

    def __post_init__(self):
        """Validate selection data."""
        if self.odds <= 1.0:
            raise ValueError(f"Invalid odds for {self.horse_name}: {self.odds}")

        # Set back_odds to odds if not provided
        if self.back_odds is None:
            self.back_odds = self.odds


@dataclass
class DutchStake:
    """Calculated stake for a dutch selection."""

    horse_name: str
    stake_amount: float
    expected_return: float
    expected_profit: float
    win_probability: float
    stake_percentage: float


@dataclass
class DutchingResult:
    """Result of dutching calculation."""

    method: DutchingMethod
    total_stake: float
    expected_profit: float
    profit_margin: float
    risk_level: DutchingRisk
    stakes: List[DutchStake]
    is_profitable: bool
    overround: float
    true_odds_total: float

    # Performance metrics
    max_profit: float = 0.0
    min_profit: float = 0.0
    profit_range: float = 0.0
    roi_percentage: float = 0.0

    # Risk metrics
    bankroll_risk: float = 0.0
    max_loss: float = 0.0
    confidence_score: float = 0.0

    def __post_init__(self):
        """Calculate derived metrics."""
        if self.stakes:
            profits = [stake.expected_profit for stake in self.stakes]
            self.max_profit = max(profits)
            self.min_profit = min(profits)
            self.profit_range = self.max_profit - self.min_profit

            if self.total_stake > 0:
                self.roi_percentage = (self.expected_profit / self.total_stake) * 100


class DutchingStrategy:
    """Advanced dutching strategy implementation."""

    def __init__(
        self,
        commission_rate: float = 0.05,
        min_profit_margin: float = 0.02,
        max_selections: int = 6,
        default_risk_level: DutchingRisk = DutchingRisk.MODERATE,
    ):
        """
        Initialize dutching strategy.

        Args:
            commission_rate: Exchange commission rate (default 5%)
            min_profit_margin: Minimum profit margin required (default 2%)
            max_selections: Maximum selections in a dutch (default 6)
            default_risk_level: Default risk level for calculations
        """
        self.commission_rate = commission_rate
        self.min_profit_margin = min_profit_margin
        self.max_selections = max_selections
        self.default_risk_level = default_risk_level

        logger.info(
            f"Initialized DutchingStrategy with "
            f"{commission_rate*100:.1f}% commission"
        )

    def calculate_implied_probability(self, odds: float) -> float:
        """Calculate implied probability from decimal odds."""
        return 1.0 / odds if odds > 0 else 0.0

    def calculate_overround(self, selections: List[DutchSelection]) -> float:
        """Calculate total overround for selections."""
        total_probability = sum(
            self.calculate_implied_probability(sel.odds) for sel in selections
        )
        return total_probability

    def check_profitability(
        self, selections: List[DutchSelection]
    ) -> Tuple[bool, float]:
        """Check if dutching is profitable for given selections."""
        overround = self.calculate_overround(selections)

        # Dutching is profitable when overround < 1.0 (less than 100%)
        is_profitable = overround < (1.0 - self.min_profit_margin)
        profit_margin = 1.0 - overround

        return is_profitable, profit_margin

    def equal_stake_dutch(
        self, selections: List[DutchSelection], stake_per_selection: float
    ) -> DutchingResult:
        """
        Calculate equal stake dutching.

        Args:
            selections: List of selections to dutch
            stake_per_selection: Fixed stake for each selection
        """
        if len(selections) > self.max_selections:
            raise ValueError(
                f"Too many selections: {len(selections)} > {self.max_selections}"
            )

        total_stake = stake_per_selection * len(selections)
        stakes = []

        for selection in selections:
            net_odds = selection.odds * (1 - self.commission_rate)
            expected_return = stake_per_selection * net_odds
            expected_profit = expected_return - total_stake
            win_probability = self.calculate_implied_probability(selection.odds)
            stake_percentage = (stake_per_selection / total_stake) * 100

            stakes.append(
                DutchStake(
                    horse_name=selection.horse_name,
                    stake_amount=stake_per_selection,
                    expected_return=expected_return,
                    expected_profit=expected_profit,
                    win_probability=win_probability,
                    stake_percentage=stake_percentage,
                )
            )

        # Calculate overall metrics
        overround = self.calculate_overround(selections)
        is_profitable, profit_margin = self.check_profitability(selections)
        expected_profit = stakes[0].expected_profit if stakes else 0.0

        return DutchingResult(
            method=DutchingMethod.EQUAL_STAKE,
            total_stake=total_stake,
            expected_profit=expected_profit,
            profit_margin=profit_margin,
            risk_level=self.default_risk_level,
            stakes=stakes,
            is_profitable=is_profitable,
            overround=overround,
            true_odds_total=overround,
        )

    def reduced_stake_dutch(
        self, selections: List[DutchSelection], target_profit: float
    ) -> DutchingResult:
        """
        Calculate reduced stake dutching for guaranteed profit.

        Args:
            selections: List of selections to dutch
            target_profit: Target profit amount
        """
        if len(selections) > self.max_selections:
            raise ValueError(
                f"Too many selections: {len(selections)} > {self.max_selections}"
            )

        is_profitable, profit_margin = self.check_profitability(selections)
        if not is_profitable:
            logger.warning("Selections not profitable for dutching")

        # Calculate proportional stakes for equal profit
        total_inverse_odds = sum(1 / sel.odds for sel in selections)
        stakes = []
        total_stake = 0.0

        for selection in selections:
            # Calculate stake needed for target profit
            net_odds = selection.odds * (1 - self.commission_rate)
            stake_proportion = (1 / selection.odds) / total_inverse_odds

            # Stake calculation for equal profit across all selections
            stake_needed = (
                target_profit
                + (
                    target_profit / profit_margin
                    if profit_margin > 0
                    else target_profit
                )
            ) * stake_proportion

            expected_return = stake_needed * net_odds
            expected_profit = (
                expected_return
                - (stake_needed / stake_proportion)
                * total_inverse_odds
                * stake_proportion
            )
            win_probability = self.calculate_implied_probability(selection.odds)

            stakes.append(
                DutchStake(
                    horse_name=selection.horse_name,
                    stake_amount=stake_needed,
                    expected_return=expected_return,
                    expected_profit=target_profit,  # Should be equal for all
                    win_probability=win_probability,
                    stake_percentage=0.0,  # Will calculate after total known
                )
            )

            total_stake += stake_needed

        # Update stake percentages
        for stake in stakes:
            stake.stake_percentage = (stake.stake_amount / total_stake) * 100

        overround = self.calculate_overround(selections)

        return DutchingResult(
            method=DutchingMethod.REDUCED_STAKE,
            total_stake=total_stake,
            expected_profit=target_profit,
            profit_margin=profit_margin,
            risk_level=self.default_risk_level,
            stakes=stakes,
            is_profitable=is_profitable,
            overround=overround,
            true_odds_total=overround,
        )

    def set_amount_dutch(
        self, selections: List[DutchSelection], total_stake: float
    ) -> DutchingResult:
        """
        Calculate set amount dutching with fixed total stake.

        Args:
            selections: List of selections to dutch
            total_stake: Fixed total stake to distribute
        """
        if len(selections) > self.max_selections:
            raise ValueError(
                f"Too many selections: {len(selections)} > {self.max_selections}"
            )

        is_profitable, profit_margin = self.check_profitability(selections)

        # Calculate optimal stake distribution
        total_inverse_odds = sum(1 / sel.odds for sel in selections)
        stakes = []

        for selection in selections:
            # Proportional staking based on inverse odds
            stake_proportion = (1 / selection.odds) / total_inverse_odds
            stake_amount = total_stake * stake_proportion

            net_odds = selection.odds * (1 - self.commission_rate)
            expected_return = stake_amount * net_odds
            expected_profit = expected_return - total_stake
            win_probability = self.calculate_implied_probability(selection.odds)
            stake_percentage = (stake_amount / total_stake) * 100

            stakes.append(
                DutchStake(
                    horse_name=selection.horse_name,
                    stake_amount=stake_amount,
                    expected_return=expected_return,
                    expected_profit=expected_profit,
                    win_probability=win_probability,
                    stake_percentage=stake_percentage,
                )
            )

        # Expected profit should be similar for all selections in optimal dutching
        expected_profit = stakes[0].expected_profit if stakes else 0.0
        overround = self.calculate_overround(selections)

        return DutchingResult(
            method=DutchingMethod.SET_AMOUNT,
            total_stake=total_stake,
            expected_profit=expected_profit,
            profit_margin=profit_margin,
            risk_level=self.default_risk_level,
            stakes=stakes,
            is_profitable=is_profitable,
            overround=overround,
            true_odds_total=overround,
        )

    def ai_weighted_dutch(
        self,
        selections: List[DutchSelection],
        total_stake: float,
        confidence_weight: float = 0.4,
        value_weight: float = 0.3,
        odds_weight: float = 0.3,
    ) -> DutchingResult:
        """
        Calculate AI-weighted dutching using confidence scores.

        Args:
            selections: List of selections with AI data
            total_stake: Total stake to distribute
            confidence_weight: Weight for AI confidence in distribution
            value_weight: Weight for value rating in distribution
            odds_weight: Weight for odds-based distribution
        """
        if len(selections) > self.max_selections:
            raise ValueError(
                f"Too many selections: {len(selections)} > {self.max_selections}"
            )

        # Calculate composite scores for each selection
        composite_scores = []
        for selection in selections:
            confidence_score = selection.ai_confidence or 0.5
            value_score = selection.value_rating or 0.5
            odds_score = min(
                1.0, 1.0 / (selection.odds / 10)
            )  # Normalize odds influence

            composite_score = (
                confidence_score * confidence_weight
                + value_score * value_weight
                + odds_score * odds_weight
            )
            composite_scores.append(composite_score)

        # Normalize scores for stake distribution
        total_score = sum(composite_scores)
        stakes = []

        for i, selection in enumerate(selections):
            stake_proportion = composite_scores[i] / total_score
            stake_amount = total_stake * stake_proportion

            net_odds = selection.odds * (1 - self.commission_rate)
            expected_return = stake_amount * net_odds
            expected_profit = expected_return - total_stake
            win_probability = self.calculate_implied_probability(selection.odds)
            stake_percentage = (stake_amount / total_stake) * 100

            stakes.append(
                DutchStake(
                    horse_name=selection.horse_name,
                    stake_amount=stake_amount,
                    expected_return=expected_return,
                    expected_profit=expected_profit,
                    win_probability=win_probability,
                    stake_percentage=stake_percentage,
                )
            )

        is_profitable, profit_margin = self.check_profitability(selections)

        # Calculate weighted expected profit
        weighted_expected_profit = sum(
            stake.expected_profit * stake.stake_percentage / 100 for stake in stakes
        )

        overround = self.calculate_overround(selections)

        return DutchingResult(
            method=DutchingMethod.AI_WEIGHTED,
            total_stake=total_stake,
            expected_profit=weighted_expected_profit,
            profit_margin=profit_margin,
            risk_level=self.default_risk_level,
            stakes=stakes,
            is_profitable=is_profitable,
            overround=overround,
            true_odds_total=overround,
        )

    def calculate_kelly_stakes(
        self,
        selections: List[DutchSelection],
        bankroll: float,
        max_kelly_fraction: float = 0.25,
    ) -> DutchingResult:
        """
        Calculate Kelly Criterion stakes for dutching.

        Args:
            selections: List of selections with probability estimates
            bankroll: Available bankroll
            max_kelly_fraction: Maximum fraction of bankroll to risk
        """
        stakes = []
        total_stake = 0.0

        for selection in selections:
            # Use AI confidence as true probability estimate
            true_probability = selection.ai_confidence or (1.0 / selection.odds)
            implied_probability = self.calculate_implied_probability(selection.odds)

            # Kelly formula: f = (bp - q) / b
            # where b = odds-1, p = true probability, q = 1-p
            b = selection.odds - 1
            p = true_probability
            q = 1 - p

            kelly_fraction = (b * p - q) / b
            kelly_fraction = max(0, min(kelly_fraction, max_kelly_fraction))

            stake_amount = bankroll * kelly_fraction

            net_odds = selection.odds * (1 - self.commission_rate)
            expected_return = stake_amount * net_odds
            expected_profit = expected_return - stake_amount
            win_probability = true_probability

            stakes.append(
                DutchStake(
                    horse_name=selection.horse_name,
                    stake_amount=stake_amount,
                    expected_return=expected_return,
                    expected_profit=expected_profit,
                    win_probability=win_probability,
                    stake_percentage=0.0,  # Will calculate after total known
                )
            )

            total_stake += stake_amount

        # Update stake percentages
        for stake in stakes:
            stake.stake_percentage = (
                (stake.stake_amount / total_stake) * 100 if total_stake > 0 else 0
            )

        is_profitable, profit_margin = self.check_profitability(selections)
        overround = self.calculate_overround(selections)

        # Expected profit is probabilistic for Kelly
        expected_profit = sum(
            stake.expected_profit * stake.win_probability for stake in stakes
        )

        return DutchingResult(
            method=DutchingMethod.PERCENTAGE_BANK,
            total_stake=total_stake,
            expected_profit=expected_profit,
            profit_margin=profit_margin,
            risk_level=DutchingRisk.MODERATE,
            stakes=stakes,
            is_profitable=is_profitable,
            overround=overround,
            true_odds_total=overround,
        )

    def assess_dutching_suitability(
        self, selections: List[DutchSelection]
    ) -> Dict[str, Any]:
        """
        Assess suitability of selections for dutching.

        Returns:
            Dictionary with suitability metrics
        """
        if len(selections) < 2:
            return {
                "suitable": False,
                "reason": "Need at least 2 selections for dutching",
                "score": 0.0,
            }

        if len(selections) > self.max_selections:
            return {
                "suitable": False,
                "reason": f"Too many selections: {len(selections)} > {self.max_selections}",
                "score": 0.0,
            }

        # Check overround
        overround = self.calculate_overround(selections)
        is_profitable, profit_margin = self.check_profitability(selections)

        # Calculate suitability score
        score_factors = {
            "overround": max(0, 1.0 - overround) * 40,  # Lower overround = better
            "field_size": min(20, len(selections) * 4),  # Optimal field size
            "odds_range": self._assess_odds_range(selections) * 20,
            "ai_confidence": self._assess_ai_confidence(selections) * 20,
        }

        suitability_score = sum(score_factors.values())

        return {
            "suitable": is_profitable and suitability_score >= 60,
            "score": suitability_score,
            "profit_margin": profit_margin,
            "overround": overround,
            "factors": score_factors,
            "recommendation": self._get_recommendation(
                suitability_score, is_profitable
            ),
        }

    def _assess_odds_range(self, selections: List[DutchSelection]) -> float:
        """Assess if odds range is suitable for dutching."""
        odds_list = [sel.odds for sel in selections]
        min_odds, max_odds = min(odds_list), max(odds_list)

        # Optimal range is roughly 2.0 to 8.0
        if min_odds >= 1.5 and max_odds <= 10.0:
            return 1.0
        elif min_odds >= 1.2 and max_odds <= 15.0:
            return 0.7
        else:
            return 0.3

    def _assess_ai_confidence(self, selections: List[DutchSelection]) -> float:
        """Assess AI confidence levels for selections."""
        confidences = [sel.ai_confidence for sel in selections if sel.ai_confidence]

        if not confidences:
            return 0.5  # Neutral if no AI data

        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)

        # Prefer high average confidence with reasonable minimum
        if avg_confidence >= 0.7 and min_confidence >= 0.5:
            return 1.0
        elif avg_confidence >= 0.6 and min_confidence >= 0.4:
            return 0.7
        else:
            return 0.4

    def _get_recommendation(self, score: float, is_profitable: bool) -> str:
        """Get recommendation based on suitability assessment."""
        if not is_profitable:
            return "NOT RECOMMENDED - Negative expected value"
        elif score >= 80:
            return "HIGHLY RECOMMENDED - Excellent dutching opportunity"
        elif score >= 60:
            return "RECOMMENDED - Good dutching opportunity"
        elif score >= 40:
            return "CONSIDER - Marginal dutching opportunity"
        else:
            return "NOT RECOMMENDED - Poor dutching conditions"

    def generate_dutching_report(self, result: DutchingResult) -> str:
        """Generate comprehensive dutching report."""
        report = []
        report.append(f"🎯 DUTCHING STRATEGY REPORT")
        report.append(f"=" * 50)
        report.append(f"Method: {result.method.value.upper()}")
        report.append(f"Total Stake: £{result.total_stake:.2f}")
        report.append(f"Expected Profit: £{result.expected_profit:.2f}")
        report.append(f"ROI: {result.roi_percentage:.1f}%")
        report.append(f"Risk Level: {result.risk_level.value.upper()}")
        report.append(f"Profitable: {'✅ YES' if result.is_profitable else '❌ NO'}")
        report.append(
            f"Overround: {result.overround:.3f} ({result.overround*100:.1f}%)"
        )
        report.append("")

        report.append("📊 STAKE BREAKDOWN:")
        report.append("-" * 30)
        for stake in result.stakes:
            report.append(f"{stake.horse_name}:")
            report.append(
                f"  Stake: £{stake.stake_amount:.2f} ({stake.stake_percentage:.1f}%)"
            )
            report.append(f"  Expected Return: £{stake.expected_return:.2f}")
            report.append(f"  Expected Profit: £{stake.expected_profit:.2f}")
            report.append(f"  Win Probability: {stake.win_probability:.1%}")
            report.append("")

        return "\n".join(report)


class DutchingPortfolio:
    """Manage multiple dutching opportunities across races."""

    def __init__(
        self, max_daily_stake: float = 1000.0, max_race_allocation: float = 0.2
    ):
        """
        Initialize dutching portfolio manager.

        Args:
            max_daily_stake: Maximum daily stake across all dutching
            max_race_allocation: Maximum allocation to single race (20% default)
        """
        self.max_daily_stake = max_daily_stake
        self.max_race_allocation = max_race_allocation
        self.active_dutches: List[DutchingResult] = []
        self.daily_stake_used = 0.0

    def add_dutch_opportunity(self, race_id: str, result: DutchingResult) -> bool:
        """
        Add dutching opportunity to portfolio.

        Returns:
            True if added successfully, False if rejected
        """
        # Check allocation limits
        max_stake_for_race = self.max_daily_stake * self.max_race_allocation

        if result.total_stake > max_stake_for_race:
            logger.warning(
                f"Dutch stake too large for race {race_id}: £{result.total_stake:.2f}"
            )
            return False

        if (self.daily_stake_used + result.total_stake) > self.max_daily_stake:
            logger.warning(
                f"Would exceed daily stake limit: £{self.daily_stake_used + result.total_stake:.2f}"
            )
            return False

        # Add to portfolio
        result.race_id = race_id
        self.active_dutches.append(result)
        self.daily_stake_used += result.total_stake

        logger.info(f"Added dutch for race {race_id}: £{result.total_stake:.2f} stake")
        return True

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of dutching portfolio."""
        if not self.active_dutches:
            return {
                "total_races": 0,
                "total_stake": 0.0,
                "expected_profit": 0.0,
                "average_roi": 0.0,
            }

        total_stake = sum(d.total_stake for d in self.active_dutches)
        total_expected_profit = sum(d.expected_profit for d in self.active_dutches)
        average_roi = (
            (total_expected_profit / total_stake * 100) if total_stake > 0 else 0
        )

        return {
            "total_races": len(self.active_dutches),
            "total_stake": total_stake,
            "expected_profit": total_expected_profit,
            "average_roi": average_roi,
            "daily_allocation_used": (self.daily_stake_used / self.max_daily_stake)
            * 100,
        }
