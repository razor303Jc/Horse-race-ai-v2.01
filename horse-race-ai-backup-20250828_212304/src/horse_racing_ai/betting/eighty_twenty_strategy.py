"""
80/20 Betting Strategy Implementation
=====================================

Implementation of the InformRacing 80/20 system:
- 80% of stake on PLACE bet
- 20% of stake on WIN bet

This strategy maximizes profit from horses that place more often than they win.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

logger = logging.getLogger(__name__)


class StakeAllocation(Enum):
    """80/20 strategy allocation ratios"""

    CONSERVATIVE = (0.80, 0.20)  # 80% place, 20% win
    MODERATE = (0.70, 0.30)  # 70% place, 30% win
    AGGRESSIVE = (0.60, 0.40)  # 60% place, 40% win


@dataclass
class EightyTwentyBet:
    """Represents an 80/20 strategy bet with place and win components"""

    horse_name: str
    total_stake: float

    # Win component
    win_stake: float
    win_odds: float
    win_potential_return: float

    # Place component
    place_stake: float
    place_odds: float
    place_potential_return: float

    # Strategy details
    allocation_ratio: Tuple[float, float]  # (place_ratio, win_ratio)
    risk_level: str
    confidence: float

    # Potential outcomes
    win_profit: float  # If horse wins (both bets pay)
    place_profit: float  # If horse places but doesn't win (only place pays)
    loss_amount: float  # If horse doesn't place (both bets lose)

    # Performance metrics
    roi_if_win: float
    roi_if_place: float
    expected_value: float


class EightyTwentyStrategy:
    """Implementation of the 80/20 betting strategy"""

    def __init__(
        self,
        starting_bankroll: float = 1000.0,
        min_place_odds: float = 1.5,
        max_field_size: int = 12,
        commission_rate: float = 0.05,
    ):
        """
        Initialize 80/20 strategy

        Args:
            starting_bankroll: Starting bankroll amount
            min_place_odds: Minimum place odds to consider (1.5 = 1/2 in fractional)
            max_field_size: Maximum field size for races (8-12 ideal)
            commission_rate: Exchange commission rate (5% = 0.05)
        """
        self.bankroll = starting_bankroll
        self.original_bankroll = starting_bankroll
        self.min_place_odds = min_place_odds
        self.max_field_size = max_field_size
        self.commission_rate = commission_rate

        # Performance tracking
        self.total_bets = 0
        self.winning_bets = 0
        self.placing_bets = 0
        self.total_stakes = 0.0
        self.total_returns = 0.0

        # Bankroll scaling levels
        self.bankroll_levels = [
            (100, 5),  # £100+ = £5 stakes
            (200, 10),  # £200+ = £10 stakes
            (300, 15),  # £300+ = £15 stakes
            (500, 25),  # £500+ = £25 stakes
            (1000, 50),  # £1000+ = £50 stakes
        ]

    def calculate_optimal_stake(self, current_bankroll: float) -> float:
        """Calculate optimal stake based on current bankroll level"""
        for threshold, stake in reversed(self.bankroll_levels):
            if current_bankroll >= threshold:
                return stake
        return 5  # Minimum stake

    def assess_suitability(
        self, win_odds: float, place_odds: float, field_size: int, confidence: float
    ) -> Dict[str, Any]:
        """
        Assess if a race/horse is suitable for 80/20 strategy

        Returns:
            Dict with suitability assessment and recommendations
        """
        suitability_score = 0
        reasons = []
        warnings = []

        # Field size assessment (8-12 ideal)
        if 8 <= field_size <= 12:
            suitability_score += 25
            reasons.append(f"Ideal field size: {field_size} runners")
        elif field_size < 8:
            suitability_score += 15
            warnings.append(f"Small field ({field_size}) - limited place opportunities")
        else:
            suitability_score += 5
            warnings.append(f"Large field ({field_size}) - harder to place")

        # Place odds assessment
        if place_odds >= self.min_place_odds:
            suitability_score += 25
            reasons.append(f"Good place odds: {place_odds}")
        else:
            suitability_score += 5
            warnings.append(f"Short place odds: {place_odds}")

        # Win odds assessment (2/1 to 10/1 ideal)
        if 3.0 <= win_odds <= 11.0:  # 2/1 to 10/1
            suitability_score += 25
            reasons.append(f"Good win odds range: {win_odds}")
        elif win_odds < 3.0:
            suitability_score += 15
            reasons.append(f"Short-priced favorite: {win_odds}")
        else:
            suitability_score += 10
            warnings.append(f"Long odds: {win_odds} - higher risk")

        # Confidence assessment
        if confidence >= 0.7:
            suitability_score += 25
            reasons.append(f"High confidence: {confidence:.1%}")
        elif confidence >= 0.5:
            suitability_score += 15
            reasons.append(f"Moderate confidence: {confidence:.1%}")
        else:
            suitability_score += 5
            warnings.append(f"Low confidence: {confidence:.1%}")

        # Overall assessment
        if suitability_score >= 80:
            recommendation = "EXCELLENT"
        elif suitability_score >= 60:
            recommendation = "GOOD"
        elif suitability_score >= 40:
            recommendation = "FAIR"
        else:
            recommendation = "POOR"

        return {
            "suitability_score": suitability_score,
            "recommendation": recommendation,
            "reasons": reasons,
            "warnings": warnings,
            "suitable": suitability_score >= 40,
        }

    def create_eighty_twenty_bet(
        self,
        horse_name: str,
        win_odds: float,
        place_odds: float,
        win_probability: float,
        place_probability: float,
        total_stake: Optional[float] = None,
        allocation: StakeAllocation = StakeAllocation.CONSERVATIVE,
    ) -> EightyTwentyBet:
        """
        Create an 80/20 strategy bet

        Args:
            horse_name: Name of horse
            win_odds: Decimal win odds
            place_odds: Decimal place odds
            win_probability: Probability of winning (0-1)
            place_probability: Probability of placing (0-1)
            total_stake: Total stake amount (if None, calculate from bankroll)
            allocation: Stake allocation ratio

        Returns:
            EightyTwentyBet object with full analysis
        """
        # Calculate stake if not provided
        if total_stake is None:
            total_stake = self.calculate_optimal_stake(self.bankroll)

        # Get allocation ratios
        place_ratio, win_ratio = allocation.value

        # Calculate individual stakes
        place_stake = total_stake * place_ratio
        win_stake = total_stake * win_ratio

        # Calculate potential returns (after commission)
        place_gross_return = place_stake * place_odds
        place_commission = place_gross_return * self.commission_rate
        place_net_return = place_gross_return - place_commission

        win_gross_return = win_stake * win_odds
        win_commission = win_gross_return * self.commission_rate
        win_net_return = win_gross_return - win_commission

        # Calculate profits for different outcomes
        # If horse wins: both place and win bets pay
        win_profit = (place_net_return - place_stake) + (win_net_return - win_stake)

        # If horse places but doesn't win: only place bet pays
        place_profit = (place_net_return - place_stake) - win_stake

        # If horse doesn't place: both bets lose
        loss_amount = -(total_stake)

        # Calculate ROI percentages
        roi_if_win = (win_profit / total_stake) * 100
        roi_if_place = (place_profit / total_stake) * 100

        # Calculate expected value
        prob_win = win_probability
        prob_place_not_win = place_probability - win_probability
        prob_no_place = 1 - place_probability

        expected_value = (
            (prob_win * win_profit)
            + (prob_place_not_win * place_profit)
            + (prob_no_place * loss_amount)
        )

        # Risk assessment
        if place_odds >= 1.8 and win_odds <= 5.0:
            risk_level = "LOW"
        elif place_odds >= 1.5 and win_odds <= 8.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return EightyTwentyBet(
            horse_name=horse_name,
            total_stake=total_stake,
            win_stake=win_stake,
            win_odds=win_odds,
            win_potential_return=win_net_return,
            place_stake=place_stake,
            place_odds=place_odds,
            place_potential_return=place_net_return,
            allocation_ratio=(place_ratio, win_ratio),
            risk_level=risk_level,
            confidence=max(win_probability, place_probability),
            win_profit=win_profit,
            place_profit=place_profit,
            loss_amount=loss_amount,
            roi_if_win=roi_if_win,
            roi_if_place=roi_if_place,
            expected_value=expected_value,
        )

    def analyze_race_for_eighty_twenty(self, race_data: List[Dict]) -> List[Dict]:
        """
        Analyze entire race for 80/20 opportunities

        Args:
            race_data: List of horse dictionaries with odds, probabilities, etc.

        Returns:
            List of analyzed opportunities ranked by expected value
        """
        opportunities = []

        field_size = len(race_data)

        for horse_data in race_data:
            horse_name = horse_data.get("horse_name", "Unknown")
            win_odds = horse_data.get("win_odds", 0.0)
            place_odds = horse_data.get("place_odds", 0.0)
            win_prob = horse_data.get("win_probability", 0.0)
            place_prob = horse_data.get("place_probability", 0.0)
            confidence = horse_data.get("confidence", 0.0)

            # Skip if missing critical data
            if not all([win_odds > 1.0, place_odds > 1.0, place_prob > 0]):
                continue

            # Assess suitability
            suitability = self.assess_suitability(
                win_odds, place_odds, field_size, confidence
            )

            if not suitability["suitable"]:
                continue

            # Create 80/20 bet analysis
            bet = self.create_eighty_twenty_bet(
                horse_name=horse_name,
                win_odds=win_odds,
                place_odds=place_odds,
                win_probability=win_prob,
                place_probability=place_prob,
            )

            opportunities.append(
                {"bet": bet, "suitability": suitability, "horse_data": horse_data}
            )

        # Sort by expected value (highest first)
        opportunities.sort(key=lambda x: x["bet"].expected_value, reverse=True)

        return opportunities

    def execute_bet(self, bet: EightyTwentyBet) -> Dict[str, Any]:
        """
        Execute an 80/20 bet (simulation/logging)

        Args:
            bet: EightyTwentyBet to execute

        Returns:
            Dict with execution details
        """
        # Update tracking
        self.total_bets += 1
        self.total_stakes += bet.total_stake

        # Update bankroll (deduct stake)
        self.bankroll -= bet.total_stake

        execution_details = {
            "bet_id": f"80_20_{self.total_bets}",
            "horse_name": bet.horse_name,
            "total_stake": bet.total_stake,
            "place_stake": bet.place_stake,
            "win_stake": bet.win_stake,
            "execution_time": "simulated",
            "status": "placed",
            "remaining_bankroll": self.bankroll,
        }

        logger.info(f"🎯 80/20 Bet Placed: {bet.horse_name}")
        logger.info(f"   💰 Total Stake: £{bet.total_stake:.2f}")
        logger.info(f"   📍 Place: £{bet.place_stake:.2f} @ {bet.place_odds}")
        logger.info(f"   🏆 Win: £{bet.win_stake:.2f} @ {bet.win_odds}")
        logger.info(f"   📊 Expected Value: £{bet.expected_value:.2f}")

        return execution_details

    def simulate_outcome(self, bet: EightyTwentyBet, outcome: str) -> Dict[str, Any]:
        """
        Simulate bet outcome for testing

        Args:
            bet: EightyTwentyBet that was placed
            outcome: 'win', 'place', or 'lose'

        Returns:
            Dict with outcome results
        """
        if outcome == "win":
            profit = bet.win_profit
            self.winning_bets += 1
            self.placing_bets += 1
            result_msg = f"🏆 WON: Both bets pay!"

        elif outcome == "place":
            profit = bet.place_profit
            self.placing_bets += 1
            result_msg = f"📍 PLACED: Place bet pays, win bet loses"

        else:  # lose
            profit = bet.loss_amount
            result_msg = f"❌ LOST: Both bets lose"

        # Update bankroll
        self.bankroll += bet.total_stake + profit  # Return stake + profit/loss
        self.total_returns += bet.total_stake + profit

        # Calculate statistics
        win_rate = (
            (self.winning_bets / self.total_bets) * 100 if self.total_bets > 0 else 0
        )
        place_rate = (
            (self.placing_bets / self.total_bets) * 100 if self.total_bets > 0 else 0
        )
        total_pnl = self.total_returns - self.total_stakes
        roi = (total_pnl / self.total_stakes) * 100 if self.total_stakes > 0 else 0

        outcome_details = {
            "outcome": outcome,
            "profit": profit,
            "total_return": bet.total_stake + profit,
            "new_bankroll": self.bankroll,
            "result_message": result_msg,
            "cumulative_stats": {
                "total_bets": self.total_bets,
                "win_rate": win_rate,
                "place_rate": place_rate,
                "total_profit": total_pnl,
                "roi_percentage": roi,
                "bankroll_change": ((self.bankroll / self.original_bankroll) - 1) * 100,
            },
        }

        logger.info(f"📊 {result_msg}")
        logger.info(f"   💰 Profit: £{profit:.2f}")
        logger.info(f"   🏦 New Bankroll: £{self.bankroll:.2f}")
        logger.info(f"   📈 Win Rate: {win_rate:.1f}% | Place Rate: {place_rate:.1f}%")

        return outcome_details

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""

        if self.total_bets == 0:
            return {"error": "No bets placed yet"}

        win_rate = (self.winning_bets / self.total_bets) * 100
        place_rate = (self.placing_bets / self.total_bets) * 100
        total_pnl = self.total_returns - self.total_stakes
        roi = (total_pnl / self.total_stakes) * 100
        bankroll_change = ((self.bankroll / self.original_bankroll) - 1) * 100

        return {
            "strategy": "80/20",
            "total_bets": self.total_bets,
            "total_stakes": self.total_stakes,
            "total_returns": self.total_returns,
            "net_profit": total_pnl,
            "win_rate": win_rate,
            "place_rate": place_rate,
            "roi_percentage": roi,
            "starting_bankroll": self.original_bankroll,
            "current_bankroll": self.bankroll,
            "bankroll_change_percentage": bankroll_change,
            "average_stake": self.total_stakes / self.total_bets,
            "profit_per_bet": total_pnl / self.total_bets,
            "strategy_effectiveness": "PROFITABLE" if total_pnl > 0 else "LOSING",
        }


def demonstrate_eighty_twenty_system():
    """Demonstration of the 80/20 system with example scenarios"""

    print("🐎 80/20 Betting Strategy Demonstration")
    print("=" * 50)

    # Initialize strategy
    strategy = EightyTwentyStrategy(starting_bankroll=500.0)

    # Example race data
    example_race = [
        {
            "horse_name": "Thunder Strike",
            "win_odds": 3.0,  # 2/1
            "place_odds": 1.6,  # 3/5
            "win_probability": 0.33,
            "place_probability": 0.65,
            "confidence": 0.8,
        },
        {
            "horse_name": "Lightning Bolt",
            "win_odds": 5.0,  # 4/1
            "place_odds": 1.8,  # 4/5
            "win_probability": 0.20,
            "place_probability": 0.55,
            "confidence": 0.7,
        },
        {
            "horse_name": "Storm Chaser",
            "win_odds": 7.0,  # 6/1
            "place_odds": 2.0,  # 1/1
            "win_probability": 0.14,
            "place_probability": 0.45,
            "confidence": 0.6,
        },
    ]

    # Analyze race
    opportunities = strategy.analyze_race_for_eighty_twenty(example_race)

    print(f"\n📊 Found {len(opportunities)} suitable opportunities:")

    for i, opp in enumerate(opportunities[:2], 1):  # Show top 2
        bet = opp["bet"]
        suitability = opp["suitability"]

        print(f"\n{i}. {bet.horse_name}")
        print(
            f"   Suitability: {suitability['recommendation']} ({suitability['suitability_score']}/100)"
        )
        print(f"   Total Stake: £{bet.total_stake:.2f}")
        print(f"   Place Bet: £{bet.place_stake:.2f} @ {bet.place_odds} odds")
        print(f"   Win Bet: £{bet.win_stake:.2f} @ {bet.win_odds} odds")
        print(f"   Expected Value: £{bet.expected_value:.2f}")
        print(f"   If Wins: £{bet.win_profit:.2f} profit ({bet.roi_if_win:.1f}% ROI)")
        print(
            f"   If Places: £{bet.place_profit:.2f} profit ({bet.roi_if_place:.1f}% ROI)"
        )

        # Simulate placing the bet
        execution = strategy.execute_bet(bet)

        # Simulate different outcomes
        print(f"\n   🎲 Outcome Simulations:")

        # Simulate win (33% chance for Thunder Strike)
        win_result = strategy.simulate_outcome(bet, "win")
        print(f"      Win Scenario: {win_result['result_message']}")

        # Reset for place simulation
        strategy.bankroll -= bet.total_stake + win_result["profit"]
        strategy.total_returns -= bet.total_stake + win_result["profit"]
        strategy.winning_bets -= 1
        strategy.placing_bets -= 1

        place_result = strategy.simulate_outcome(bet, "place")
        print(f"      Place Scenario: {place_result['result_message']}")

    print(f"\n📈 Strategy Performance:")
    summary = strategy.get_performance_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"   {key.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"   {key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    demonstrate_eighty_twenty_system()
