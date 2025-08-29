#!/usr/bin/env python3
"""
Advanced Betting Strategies for Horse Racing AI
==============================================

Comprehensive betting strategies including:
- Value betting with Kelly Criterion
- Dutching calculator for multiple selections
- Staking systems and bankroll management
- Risk-adjusted position sizing
"""

import logging
import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class BetType(Enum):
    """Types of bets available."""

    WIN = "win"
    PLACE = "place"
    SHOW = "show"
    EACH_WAY = "each_way"
    EXACTA = "exacta"
    TRIFECTA = "trifecta"
    TWENTY_EIGHTY = "twenty_eighty"  # 20% win, 80% place


class StakingMethod(Enum):
    """Staking methods for bet sizing."""

    FIXED = "fixed"
    PERCENTAGE = "percentage"
    KELLY = "kelly"
    PROPORTIONAL = "proportional"
    FIBONACCI = "fibonacci"


@dataclass
class BettingOpportunity:
    """Individual betting opportunity with value assessment."""

    horse_name: str
    odds: float  # Decimal odds
    true_probability: float  # Model-derived probability
    confidence: float  # Confidence in the prediction (0-1)
    bet_type: BetType
    value: float  # Betting value percentage
    kelly_fraction: float  # Kelly criterion fraction
    recommended_stake: float  # Recommended stake amount
    max_stake: float  # Maximum safe stake
    risk_rating: str  # LOW, MEDIUM, HIGH


@dataclass
class DutchingCalculation:
    """Dutch betting calculation for multiple selections."""

    selections: List[Dict[str, Any]]  # List of {horse, odds, stake}
    total_stake: float
    total_return: float  # Guaranteed return if any selection wins
    profit_margin: float  # Profit percentage
    break_even_probability: float  # Combined probability needed to break even
    roi_if_win: float  # Return on investment if successful


@dataclass
class BankrollState:
    """Current bankroll state and management."""

    current_balance: float
    starting_balance: float
    peak_balance: float
    drawdown_percentage: float
    total_wagered: float
    total_returned: float
    net_profit: float
    roi_percentage: float
    risk_level: str
    recommended_max_bet: float


@dataclass
class TwentyEightyStrategy:
    """20/80 betting strategy: 20% win, 80% place."""

    horse_name: str
    total_stake: float
    win_stake: float  # 20% of total
    place_stake: float  # 80% of total
    win_odds: float
    place_odds: float
    win_probability: float
    place_probability: float
    confidence: float
    potential_win_return: float
    potential_place_return: float
    expected_value: float
    risk_rating: str
    bet_type: BetType = BetType.TWENTY_EIGHTY
    staking_method: StakingMethod = StakingMethod.PERCENTAGE


class AdvancedBettingStrategies:
    """Advanced betting strategies with AI integration."""

    def __init__(self, initial_bankroll: float = 1000.0):
        """Initialize the betting strategies system.

        Args:
            initial_bankroll: Starting bankroll amount
        """
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.peak_bankroll = initial_bankroll
        self.total_wagered = 0.0
        self.total_returned = 0.0
        self.bet_history: List[Dict[str, Any]] = []

        # Risk management settings
        self.max_bet_percentage = 0.05  # Max 5% of bankroll per bet
        self.kelly_multiplier = 0.25  # Quarter Kelly for safety
        self.min_value_threshold = 0.1  # 10% minimum value to bet
        self.max_risk_per_race = 0.15  # Max 15% of bankroll per race

        logger.info("Advanced Betting Strategies initialized")

    def calculate_value_bet(
        self, odds: float, true_probability: float, confidence: float = 1.0
    ) -> BettingOpportunity:
        """Calculate value betting opportunity.

        Args:
            odds: Decimal odds offered
            true_probability: Model's true win probability
            confidence: Confidence in the prediction (0-1)

        Returns:
            BettingOpportunity with full analysis
        """
        # Calculate implied probability from odds
        implied_probability = 1.0 / odds

        # Calculate betting value
        value = (true_probability / implied_probability) - 1.0

        # Adjust value by confidence
        adjusted_value = value * confidence

        # Kelly Criterion calculation
        # Kelly = (bp - q) / b
        # Where: b = odds-1, p = true_probability, q = 1-p
        b = odds - 1  # Net odds
        p = true_probability * confidence  # Adjusted probability
        q = 1 - p

        kelly_fraction = (b * p - q) / b if b > 0 else 0
        kelly_fraction = max(0, kelly_fraction)  # Never negative

        # Apply Kelly multiplier for safety
        safe_kelly = kelly_fraction * self.kelly_multiplier

        # Calculate recommended stake
        recommended_stake = self._calculate_stake(
            safe_kelly, adjusted_value, StakingMethod.KELLY
        )

        # Maximum safe stake (percentage of bankroll)
        max_stake = self.current_bankroll * self.max_bet_percentage

        # Risk assessment
        risk_rating = self._assess_risk(kelly_fraction, adjusted_value, confidence)

        return BettingOpportunity(
            horse_name="",  # To be filled by caller
            odds=odds,
            true_probability=true_probability,
            confidence=confidence,
            bet_type=BetType.WIN,
            value=adjusted_value,
            kelly_fraction=safe_kelly,
            recommended_stake=min(recommended_stake, max_stake),
            max_stake=max_stake,
            risk_rating=risk_rating,
        )

    def calculate_dutching(
        self, selections: List[Tuple[str, float, float]]  # (horse, odds, probability)
    ) -> DutchingCalculation:
        """Calculate Dutch betting to guarantee profit.

        Args:
            selections: List of (horse_name, odds, probability) tuples

        Returns:
            DutchingCalculation with stakes and expected returns
        """
        if len(selections) < 2:
            raise ValueError("Dutching requires at least 2 selections")

        # Calculate total implied probability
        total_implied_prob = sum(1.0 / odds for _, odds, _ in selections)

        if total_implied_prob >= 1.0:
            # No arbitrage opportunity
            return DutchingCalculation(
                selections=[],
                total_stake=0.0,
                total_return=0.0,
                profit_margin=-1.0,
                break_even_probability=total_implied_prob,
                roi_if_win=-1.0,
            )

        # Calculate profit margin
        profit_margin = (1.0 - total_implied_prob) * 100

        # Determine total stake (percentage of bankroll for dutching)
        max_dutching_stake = self.current_bankroll * self.max_risk_per_race
        total_stake = max_dutching_stake

        # Calculate individual stakes
        dutching_selections = []
        total_return = 0.0

        for horse, odds, probability in selections:
            # Proportional stake based on implied probability
            implied_prob = 1.0 / odds
            stake_fraction = implied_prob / total_implied_prob
            stake = total_stake * stake_fraction

            # Expected return if this selection wins
            expected_return = stake * odds
            if total_return == 0.0:
                total_return = expected_return

            dutching_selections.append(
                {
                    "horse": horse,
                    "odds": odds,
                    "probability": probability,
                    "stake": stake,
                    "return_if_win": expected_return,
                }
            )

        # Calculate ROI
        roi_if_win = ((total_return - total_stake) / total_stake) * 100

        return DutchingCalculation(
            selections=dutching_selections,
            total_stake=total_stake,
            total_return=total_return,
            profit_margin=profit_margin,
            break_even_probability=total_implied_prob,
            roi_if_win=roi_if_win,
        )

    def calculate_each_way_value(
        self,
        win_odds: float,
        place_odds: float,
        win_probability: float,
        place_probability: float,
        confidence: float = 1.0,
    ) -> Dict[str, BettingOpportunity]:
        """Calculate each-way betting value.

        Args:
            win_odds: Decimal odds for win
            place_odds: Decimal odds for place
            win_probability: Model's win probability
            place_probability: Model's place probability
            confidence: Confidence in predictions

        Returns:
            Dictionary with 'win' and 'place' BettingOpportunity objects
        """
        win_bet = self.calculate_value_bet(win_odds, win_probability, confidence)
        place_bet = self.calculate_value_bet(place_odds, place_probability, confidence)

        # Adjust each-way stakes (typically equal stakes)
        ew_stake = min(win_bet.recommended_stake, place_bet.recommended_stake) / 2

        win_bet.recommended_stake = ew_stake
        win_bet.bet_type = BetType.WIN

        place_bet.recommended_stake = ew_stake
        place_bet.bet_type = BetType.PLACE

        return {"win": win_bet, "place": place_bet}

    def _calculate_stake(
        self, kelly_fraction: float, value: float, method: StakingMethod
    ) -> float:
        """Calculate stake amount based on staking method.

        Args:
            kelly_fraction: Kelly criterion fraction
            value: Betting value
            method: Staking method to use

        Returns:
            Stake amount
        """
        if method == StakingMethod.KELLY:
            return self.current_bankroll * kelly_fraction

        elif method == StakingMethod.FIXED:
            return min(20.0, self.current_bankroll * 0.02)  # Fixed $20 or 2%

        elif method == StakingMethod.PERCENTAGE:
            return self.current_bankroll * 0.03  # 3% of bankroll

        elif method == StakingMethod.PROPORTIONAL:
            # Stake proportional to value
            base_stake = self.current_bankroll * 0.02
            return base_stake * (1 + max(0, value))

        else:  # Default to percentage
            return self.current_bankroll * 0.02

    def _assess_risk(
        self, kelly_fraction: float, value: float, confidence: float
    ) -> str:
        """Assess risk level of a betting opportunity.

        Args:
            kelly_fraction: Kelly criterion fraction
            value: Betting value
            confidence: Prediction confidence

        Returns:
            Risk level: LOW, MEDIUM, HIGH
        """
        # Multiple risk factors
        risk_factors = []

        # Kelly fraction risk
        if kelly_fraction > 0.1:
            risk_factors.append("HIGH_KELLY")
        elif kelly_fraction > 0.05:
            risk_factors.append("MEDIUM_KELLY")

        # Value risk
        if value < 0.05:
            risk_factors.append("LOW_VALUE")
        elif value > 0.5:
            risk_factors.append("HIGH_VALUE")

        # Confidence risk
        if confidence < 0.7:
            risk_factors.append("LOW_CONFIDENCE")

        # Overall assessment
        if len(risk_factors) >= 2 or "HIGH_KELLY" in risk_factors:
            return "HIGH"
        elif len(risk_factors) == 1:
            return "MEDIUM"
        else:
            return "LOW"

    def update_bankroll(self, stake: float, payout: float) -> BankrollState:
        """Update bankroll after a bet result.

        Args:
            stake: Amount wagered
            payout: Amount returned (0 if lost)

        Returns:
            Updated BankrollState
        """
        # Update totals
        self.total_wagered += stake
        self.total_returned += payout

        # Update current bankroll
        self.current_bankroll = self.current_bankroll - stake + payout

        # Update peak
        if self.current_bankroll > self.peak_bankroll:
            self.peak_bankroll = self.current_bankroll

        # Calculate metrics
        drawdown = (
            (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        ) * 100
        net_profit = self.total_returned - self.total_wagered
        roi = (net_profit / self.total_wagered) * 100 if self.total_wagered > 0 else 0

        # Risk assessment
        risk_level = "LOW"
        if drawdown > 20:
            risk_level = "HIGH"
        elif drawdown > 10:
            risk_level = "MEDIUM"

        # Recommended max bet
        recommended_max = self.current_bankroll * self.max_bet_percentage

        # Record bet
        self.bet_history.append(
            {
                "stake": stake,
                "payout": payout,
                "profit": payout - stake,
                "bankroll_after": self.current_bankroll,
                "roi": roi,
                "drawdown": drawdown,
            }
        )

        return BankrollState(
            current_balance=self.current_bankroll,
            starting_balance=self.initial_bankroll,
            peak_balance=self.peak_bankroll,
            drawdown_percentage=drawdown,
            total_wagered=self.total_wagered,
            total_returned=self.total_returned,
            net_profit=net_profit,
            roi_percentage=roi,
            risk_level=risk_level,
            recommended_max_bet=recommended_max,
        )

    def get_betting_recommendations(
        self, race_predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get comprehensive betting recommendations for a race.

        Args:
            race_predictions: List of horse predictions with odds and probabilities

        Returns:
            Dictionary with all betting recommendations
        """
        recommendations = {
            "value_bets": [],
            "dutching_opportunities": [],
            "each_way_bets": [],
            "bankroll_status": self._get_current_bankroll_status(),
            "risk_assessment": "LOW",
            "total_recommended_stake": 0.0,
        }

        # Find value betting opportunities
        for prediction in race_predictions:
            if (
                prediction.get("odds", 0) > 1.0
                and prediction.get("win_probability", 0) > 0
            ):
                value_bet = self.calculate_value_bet(
                    odds=prediction["odds"],
                    true_probability=prediction["win_probability"],
                    confidence=prediction.get("confidence", 0.8),
                )

                value_bet.horse_name = prediction["horse_name"]

                # Only recommend if above value threshold
                if value_bet.value > self.min_value_threshold:
                    recommendations["value_bets"].append(value_bet)
                    recommendations[
                        "total_recommended_stake"
                    ] += value_bet.recommended_stake

        # Find dutching opportunities (top 2-3 horses with combined value)
        top_selections = sorted(
            race_predictions, key=lambda x: x.get("win_probability", 0), reverse=True
        )[:3]

        if len(top_selections) >= 2:
            selections = [
                (pred["horse_name"], pred["odds"], pred["win_probability"])
                for pred in top_selections
                if pred.get("odds", 0) > 1.0
            ]

            if len(selections) >= 2:
                dutching = self.calculate_dutching(selections)
                if dutching.profit_margin > 0:
                    recommendations["dutching_opportunities"].append(dutching)

        # Each-way opportunities for longer odds with place potential
        for prediction in race_predictions:
            if (
                prediction.get("odds", 0) > 4.0
                and prediction.get("place_probability", 0) > 0.3
            ):

                place_odds = prediction.get("place_odds", prediction["odds"] / 3)
                ew_bets = self.calculate_each_way_value(
                    win_odds=prediction["odds"],
                    place_odds=place_odds,
                    win_probability=prediction["win_probability"],
                    place_probability=prediction["place_probability"],
                    confidence=prediction.get("confidence", 0.8),
                )

                if ew_bets["win"].value > 0.05 or ew_bets["place"].value > 0.1:
                    ew_bets["win"].horse_name = prediction["horse_name"]
                    ew_bets["place"].horse_name = prediction["horse_name"]
                    recommendations["each_way_bets"].append(ew_bets)

        # Overall risk assessment
        total_risk = recommendations["total_recommended_stake"] / self.current_bankroll
        if total_risk > 0.15:
            recommendations["risk_assessment"] = "HIGH"
        elif total_risk > 0.08:
            recommendations["risk_assessment"] = "MEDIUM"

        return recommendations

    def _get_current_bankroll_status(self) -> BankrollState:
        """Get current bankroll status."""
        drawdown = (
            (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        ) * 100
        net_profit = self.total_returned - self.total_wagered
        roi = (net_profit / self.total_wagered) * 100 if self.total_wagered > 0 else 0

        risk_level = "LOW"
        if drawdown > 20:
            risk_level = "HIGH"
        elif drawdown > 10:
            risk_level = "MEDIUM"

        return BankrollState(
            current_balance=self.current_bankroll,
            starting_balance=self.initial_bankroll,
            peak_balance=self.peak_bankroll,
            drawdown_percentage=drawdown,
            total_wagered=self.total_wagered,
            total_returned=self.total_returned,
            net_profit=net_profit,
            roi_percentage=roi,
            risk_level=risk_level,
            recommended_max_bet=self.current_bankroll * self.max_bet_percentage,
        )

    def export_betting_analytics(self) -> Dict[str, Any]:
        """Export comprehensive betting analytics for AI analysis.

        Returns:
            Dictionary with detailed analytics
        """
        if not self.bet_history:
            return {"message": "No betting history available"}

        # Calculate performance metrics
        profits = [bet["profit"] for bet in self.bet_history]
        roi_history = [bet["roi"] for bet in self.bet_history]

        # Win/loss analysis
        wins = len([p for p in profits if p > 0])
        losses = len([p for p in profits if p < 0])
        win_rate = wins / len(profits) if profits else 0

        # Profit analysis
        avg_win = np.mean([p for p in profits if p > 0]) if wins > 0 else 0
        avg_loss = np.mean([p for p in profits if p < 0]) if losses > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        # Risk metrics
        profit_volatility = np.std(profits) if len(profits) > 1 else 0
        max_consecutive_losses = self._calculate_max_consecutive_losses()

        return {
            "performance_summary": {
                "total_bets": len(self.bet_history),
                "win_rate": win_rate * 100,
                "total_profit": sum(profits),
                "average_profit_per_bet": np.mean(profits),
                "roi": roi_history[-1] if roi_history else 0,
                "profit_factor": profit_factor,
            },
            "risk_metrics": {
                "profit_volatility": profit_volatility,
                "max_drawdown": max(bet["drawdown"] for bet in self.bet_history),
                "max_consecutive_losses": max_consecutive_losses,
                "current_risk_level": self._get_current_bankroll_status().risk_level,
            },
            "bankroll_management": {
                "starting_bankroll": self.initial_bankroll,
                "current_bankroll": self.current_bankroll,
                "peak_bankroll": self.peak_bankroll,
                "total_wagered": self.total_wagered,
                "betting_frequency": len(self.bet_history),
            },
            "strategy_effectiveness": {
                "kelly_criterion_usage": sum(
                    1 for bet in self.bet_history if bet.get("method") == "kelly"
                ),
                "value_bet_success": self._calculate_value_bet_success_rate(),
                "dutching_profitability": self._calculate_dutching_profitability(),
            },
        }

    def _calculate_max_consecutive_losses(self) -> int:
        """Calculate maximum consecutive losses."""
        if not self.bet_history:
            return 0

        max_consecutive = 0
        current_consecutive = 0

        for bet in self.bet_history:
            if bet["profit"] <= 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _calculate_value_bet_success_rate(self) -> float:
        """Calculate success rate of value bets."""
        # This would be enhanced with actual bet tagging
        value_bets = [bet for bet in self.bet_history if bet.get("type") == "value"]
        if not value_bets:
            return 0.0

        successful = len([bet for bet in value_bets if bet["profit"] > 0])
        return (successful / len(value_bets)) * 100

    def _calculate_dutching_profitability(self) -> float:
        """Calculate profitability of dutching strategies."""
        # This would be enhanced with actual bet tagging
        dutching_bets = [
            bet for bet in self.bet_history if bet.get("type") == "dutching"
        ]
        if not dutching_bets:
            return 0.0

        total_profit = sum(bet["profit"] for bet in dutching_bets)
        total_stake = sum(bet["stake"] for bet in dutching_bets)
        return (total_profit / total_stake) * 100 if total_stake > 0 else 0.0

    def calculate_twenty_eighty_strategy(
        self,
        horse_name: str,
        win_odds: float,
        place_odds: float,
        win_probability: float,
        place_probability: float,
        total_stake: Optional[float] = None,
        confidence: float = 1.0,
        staking_method: StakingMethod = StakingMethod.PERCENTAGE,
    ) -> TwentyEightyStrategy:
        """Calculate 20/80 betting strategy: 20% win, 80% place.

        This strategy splits the total stake with 20% on win market and 80% on
        place market. Ideal for horses with good place chances but uncertain
        win prospects.

        Args:
            horse_name: Name of the horse
            win_odds: Decimal odds for win market
            place_odds: Decimal odds for place market
            win_probability: AI predicted win probability (0-1)
            place_probability: AI predicted place probability (0-1)
            total_stake: Total amount to stake (calculated if None)
            confidence: Confidence in predictions (0-1)
            staking_method: Method to calculate stake size if not provided

        Returns:
            TwentyEightyStrategy with full analysis
        """
        # Calculate total stake if not provided
        if total_stake is None:
            # Use value betting to determine appropriate stake
            place_value = (place_probability * place_odds) - 1.0

            # For Kelly, calculate proper Kelly fraction for place bet
            if staking_method == StakingMethod.KELLY:
                # Kelly = (bp - q) / b for place bet
                b = place_odds - 1
                p = place_probability * confidence
                q = 1 - p
                kelly_fraction = (b * p - q) / b if b > 0 else 0
                kelly_fraction = max(0, kelly_fraction) * self.kelly_multiplier
                total_stake = self.current_bankroll * kelly_fraction
            else:
                total_stake = self._calculate_stake(
                    kelly_fraction=0.0,  # Not using Kelly for this
                    value=place_value,
                    method=staking_method,
                )

        # Ensure minimum stake
        total_stake = max(total_stake, 1.0)  # Minimum $1 stake

        # Calculate stake allocation
        win_stake = total_stake * 0.20  # 20% on win
        place_stake = total_stake * 0.80  # 80% on place

        # Calculate potential returns
        potential_win_return = win_stake * win_odds
        potential_place_return = place_stake * place_odds

        # Calculate expected values
        win_ev = (win_probability * potential_win_return) - win_stake
        place_ev = (place_probability * potential_place_return) - place_stake
        total_ev = win_ev + place_ev

        # Adjust for confidence
        adjusted_ev = total_ev * confidence

        # Risk assessment
        risk_factors = []

        # Check if place probability significantly higher than win probability
        place_advantage = (
            place_probability / win_probability if win_probability > 0 else 0
        )
        if place_advantage < 1.5:
            risk_factors.append("LOW_PLACE_ADVANTAGE")

        # Check if place odds are too low
        if place_odds < 1.2:
            risk_factors.append("LOW_PLACE_ODDS")

        # Check overall confidence
        if confidence < 0.7:
            risk_factors.append("LOW_CONFIDENCE")

        # Check if total stake exceeds bankroll limits
        if total_stake > self.current_bankroll * self.max_bet_percentage:
            risk_factors.append("EXCESSIVE_STAKE")

        # Assess overall risk
        if len(risk_factors) >= 2:
            risk_rating = "HIGH"
        elif len(risk_factors) == 1:
            risk_rating = "MEDIUM"
        else:
            risk_rating = "LOW"

        logger.info(
            f"20/80 Strategy for {horse_name}: ${win_stake:.2f} win, "
            f"${place_stake:.2f} place, EV: ${adjusted_ev:.2f}"
        )

        return TwentyEightyStrategy(
            horse_name=horse_name,
            total_stake=total_stake,
            win_stake=win_stake,
            place_stake=place_stake,
            win_odds=win_odds,
            place_odds=place_odds,
            win_probability=win_probability,
            place_probability=place_probability,
            confidence=confidence,
            potential_win_return=potential_win_return,
            potential_place_return=potential_place_return,
            expected_value=adjusted_ev,
            risk_rating=risk_rating,
            bet_type=BetType.TWENTY_EIGHTY,
            staking_method=staking_method,
        )

    def get_top_three_twenty_eighty_selections(
        self,
        race_predictions: List[Dict[str, Any]],
        total_daily_bankroll: Optional[float] = None,
    ) -> List[TwentyEightyStrategy]:
        """Get top 3 horses for 20/80 strategy based on AI predictions.

        This method identifies the best 3 horses of the day based on combined
        win and place value, then applies the 20/80 strategy.

        Args:
            race_predictions: List of race prediction dictionaries
            total_daily_bankroll: Total amount allocated for the day's betting

        Returns:
            List of top 3 TwentyEightyStrategy selections
        """
        if total_daily_bankroll is None:
            total_daily_bankroll = (
                self.current_bankroll * 0.15
            )  # 15% of bankroll max per day

        # Individual stake per horse (divide daily budget by 3)
        stake_per_horse = total_daily_bankroll / 3

        # Ensure individual stakes don't exceed limits
        max_individual_stake = self.current_bankroll * self.max_bet_percentage
        stake_per_horse = min(stake_per_horse, max_individual_stake)

        all_selections = []

        # Process all horses from all races
        for race in race_predictions:
            race_id = race.get("race_id", "Unknown")
            horses = race.get("horses", [])

            for horse in horses:
                horse_name = horse.get("horse_name", "Unknown")

                # Get AI prediction data
                prediction = horse.get("prediction", {})
                win_prob = prediction.get("win_probability", 0)
                place_prob = prediction.get("place_probability", 0)
                confidence = prediction.get("confidence", 0)

                # Get odds (use AI rating as proxy if odds not available)
                win_odds = horse.get(
                    "win_odds", 1.0 / win_prob if win_prob > 0 else 10.0
                )
                place_odds = horse.get(
                    "place_odds", win_odds * 0.3
                )  # Approximate place odds

                # Only consider horses with reasonable confidence and place advantage
                if (
                    confidence > 0.6
                    and place_prob > win_prob * 1.2
                    and place_prob > 0.3
                ):
                    # Calculate 20/80 strategy
                    strategy = self.calculate_twenty_eighty_strategy(
                        horse_name=f"{horse_name} (Race: {race_id})",
                        win_odds=win_odds,
                        place_odds=place_odds,
                        win_probability=win_prob,
                        place_probability=place_prob,
                        total_stake=stake_per_horse,
                        confidence=confidence,
                        staking_method=StakingMethod.FIXED,  # Fixed stake per horse
                    )

                    # Add selection value score for ranking
                    selection_value = strategy.expected_value * confidence * place_prob

                    all_selections.append(
                        {
                            "strategy": strategy,
                            "selection_value": selection_value,
                            "race_id": race_id,
                        }
                    )

        # Sort by selection value (highest first)
        all_selections.sort(key=lambda x: x["selection_value"], reverse=True)

        # Return top 3 strategies
        top_three = [selection["strategy"] for selection in all_selections[:3]]

        if top_three:
            total_allocated = sum(strategy.total_stake for strategy in top_three)
            logger.info(
                f"Top 3 20/80 selections identified. "
                f"Total allocated: ${total_allocated:.2f}"
            )

            for i, strategy in enumerate(top_three, 1):
                logger.info(
                    f"#{i}: {strategy.horse_name} - "
                    f"EV: ${strategy.expected_value:.2f}, "
                    f"Risk: {strategy.risk_rating}"
                )

        return top_three
