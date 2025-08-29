"""
BETDAQ Betting Coordinator
Unified interface for both paper trading and live betting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from .betdaq_client import BetdaqClient, BetdaqConfig, BetOrder, BettingSide, MarketInfo
from .betdaq_live_betting import (
    AILiveBettingInterface,
    LiveBettingEngine,
    LiveOrder,
    RiskLimits,
)
from .betdaq_paper_trading import PaperBet, PaperTradingConfig, PaperTradingEngine


class TradingMode(Enum):
    """Trading mode selection"""

    PAPER = "paper"
    LIVE = "live"
    DISABLED = "disabled"


class BettingCoordinator:
    """Unified coordinator for paper trading and live betting"""

    def __init__(
        self,
        betdaq_client: BetdaqClient,
        trading_mode: TradingMode = TradingMode.PAPER,
        paper_config: PaperTradingConfig = None,
        risk_limits: RiskLimits = None,
    ):

        self.client = betdaq_client
        self.trading_mode = trading_mode
        self.logger = logging.getLogger(__name__)

        # Initialize engines based on mode
        self.paper_engine = None
        self.live_engine = None
        self.ai_interface = None

        if trading_mode == TradingMode.PAPER:
            self.paper_engine = PaperTradingEngine(paper_config or PaperTradingConfig())
            self.logger.info("Initialized in PAPER TRADING mode")

        elif trading_mode == TradingMode.LIVE:
            self.live_engine = LiveBettingEngine(
                betdaq_client, risk_limits or RiskLimits()
            )
            self.ai_interface = AILiveBettingInterface(self.live_engine)
            self.logger.info("Initialized in LIVE BETTING mode")

        # Performance tracking
        self.session_start = datetime.now()
        self.total_bets_placed = 0
        self.mode_switches = []

    async def place_bet(
        self, order: BetOrder, market_info: MarketInfo
    ) -> Optional[Union[PaperBet, LiveOrder]]:
        """Place bet in current mode"""

        if self.trading_mode == TradingMode.DISABLED:
            self.logger.warning("Trading is disabled")
            return None

        if self.trading_mode == TradingMode.PAPER and self.paper_engine:
            bet = await self.paper_engine.place_bet(order, market_info)
            if bet:
                self.total_bets_placed += 1
                await self._log_bet_placed(bet, "PAPER")
            return bet

        elif self.trading_mode == TradingMode.LIVE and self.live_engine:
            live_order = await self.live_engine.place_bet(order, market_info)
            if live_order:
                self.total_bets_placed += 1
                await self._log_bet_placed(live_order, "LIVE")
            return live_order

        return None

    async def process_ai_prediction(
        self, prediction: Dict, market_info: MarketInfo
    ) -> Optional[Union[PaperBet, LiveOrder]]:
        """Process AI prediction and place bet if criteria met"""

        if self.trading_mode == TradingMode.DISABLED:
            return None

        # Convert AI prediction to bet order
        order = await self._ai_prediction_to_order(prediction, market_info)
        if not order:
            return None

        if self.trading_mode == TradingMode.PAPER and self.paper_engine:
            return await self.paper_engine.place_bet(order, market_info)

        elif self.trading_mode == TradingMode.LIVE and self.ai_interface:
            return await self.ai_interface.process_ai_prediction(
                prediction, market_info
            )

        return None

    async def _ai_prediction_to_order(
        self, prediction: Dict, market_info: MarketInfo
    ) -> Optional[BetOrder]:
        """Convert AI prediction to bet order"""

        # Extract required fields
        confidence = prediction.get("confidence", 0.0)
        predicted_odds = prediction.get("predicted_odds", 0.0)
        current_odds = prediction.get("current_odds", predicted_odds)
        horse_name = prediction.get("horse_name", "")
        selection_id = prediction.get("selection_id", 0)

        # Validation
        if confidence < 0.7:  # Minimum confidence threshold
            return None

        if not horse_name or selection_id == 0:
            self.logger.warning("Missing horse name or selection ID in prediction")
            return None

        # Calculate value
        value = self._calculate_value(predicted_odds, current_odds)
        if value < 0.05:  # Minimum 5% edge
            return None

        # Calculate stake
        stake = self._calculate_stake(confidence, value, current_odds)

        return BetOrder(
            selection_id=selection_id,
            horse_name=horse_name,
            stake=stake,
            odds=current_odds,
            side=BettingSide.BACK,
            market_id=market_info.market_id,
            confidence=confidence,
            value=value,
        )

    def _calculate_value(self, predicted_odds: float, current_odds: float) -> float:
        """Calculate betting value"""
        if predicted_odds <= 1.0 or current_odds <= 1.0:
            return 0.0

        implied_prob = 1.0 / predicted_odds
        market_prob = 1.0 / current_odds

        return (implied_prob * current_odds - 1) / (current_odds - 1)

    def _calculate_stake(self, confidence: float, value: float, odds: float) -> float:
        """Calculate optimal stake"""

        # Base stake calculation
        if self.trading_mode == TradingMode.PAPER:
            max_stake = 20.0  # Paper trading can be more aggressive
        else:
            max_stake = (
                self.live_engine.risk_limits.max_stake_per_bet
                if self.live_engine
                else 10.0
            )

        # Kelly Criterion with conservative multiplier
        b = odds - 1
        p = confidence
        q = 1 - confidence

        kelly_fraction = (b * p - q) / b
        conservative_fraction = kelly_fraction * 0.25  # 25% of Kelly

        stake = min(max_stake, max(1.0, conservative_fraction * max_stake))
        return round(stake, 2)

    async def switch_mode(
        self,
        new_mode: TradingMode,
        paper_config: PaperTradingConfig = None,
        risk_limits: RiskLimits = None,
    ) -> bool:
        """Switch trading mode"""

        if new_mode == self.trading_mode:
            self.logger.info(f"Already in {new_mode.value} mode")
            return True

        # Log mode switch
        self.mode_switches.append(
            {
                "from": self.trading_mode.value,
                "to": new_mode.value,
                "timestamp": datetime.now().isoformat(),
                "reason": "manual_switch",
            }
        )

        # Handle live to paper switch
        if self.trading_mode == TradingMode.LIVE and self.live_engine:
            active_orders = len(self.live_engine.active_orders)
            if active_orders > 0:
                self.logger.warning(
                    f"Switching from LIVE to {new_mode.value} with {active_orders} active orders"
                )

        # Update mode
        old_mode = self.trading_mode
        self.trading_mode = new_mode

        # Initialize new engines
        if new_mode == TradingMode.PAPER:
            self.paper_engine = PaperTradingEngine(paper_config or PaperTradingConfig())
            self.live_engine = None
            self.ai_interface = None

        elif new_mode == TradingMode.LIVE:
            if not self.client.authenticated:
                self.logger.error(
                    "Cannot switch to LIVE mode - client not authenticated"
                )
                self.trading_mode = old_mode
                return False

            self.live_engine = LiveBettingEngine(
                self.client, risk_limits or RiskLimits()
            )
            self.ai_interface = AILiveBettingInterface(self.live_engine)
            self.paper_engine = None

        elif new_mode == TradingMode.DISABLED:
            self.paper_engine = None
            self.live_engine = None
            self.ai_interface = None

        self.logger.info(f"Switched from {old_mode.value} to {new_mode.value} mode")
        return True

    async def emergency_stop(self, reason: str = "Manual trigger"):
        """Emergency stop for all trading"""

        self.logger.critical(f"EMERGENCY STOP: {reason}")

        # Stop live trading if active
        if self.live_engine:
            await self.live_engine.emergency_stop(reason)

        # Switch to disabled mode
        await self.switch_mode(TradingMode.DISABLED)

        self.logger.critical("All trading stopped")

    async def simulate_race_result(
        self, market_id: int, winning_selection_id: int = None
    ):
        """Simulate race result (paper trading only)"""

        if self.trading_mode == TradingMode.PAPER and self.paper_engine:
            await self.paper_engine.simulate_race_result(
                market_id, winning_selection_id
            )
        else:
            self.logger.warning("Race simulation only available in paper trading mode")

    async def settle_race(self, market_id: int, result: Dict):
        """Settle race bets with actual result"""

        if self.trading_mode == TradingMode.LIVE and self.live_engine:
            # Settle all orders for this market
            for order_id, live_order in self.live_engine.completed_orders.items():
                if live_order.bet_order.market_id == market_id:
                    await self.live_engine.settle_bet(order_id, result)

        elif self.trading_mode == TradingMode.PAPER and self.paper_engine:
            winning_selection_id = result.get("winner_selection_id")
            await self.paper_engine.simulate_race_result(
                market_id, winning_selection_id
            )

    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""

        base_summary = {
            "trading_mode": self.trading_mode.value,
            "session_start": self.session_start.isoformat(),
            "total_bets_placed": self.total_bets_placed,
            "mode_switches": len(self.mode_switches),
            "mode_switch_history": self.mode_switches[-5:],  # Last 5 switches
        }

        if self.trading_mode == TradingMode.PAPER and self.paper_engine:
            paper_summary = self.paper_engine.get_performance_summary()
            base_summary.update({"paper_trading": paper_summary})

        elif self.trading_mode == TradingMode.LIVE and self.live_engine:
            live_summary = self.live_engine.get_trading_summary()
            base_summary.update({"live_trading": live_summary})

        return base_summary

    async def _log_bet_placed(self, bet: Union[PaperBet, LiveOrder], mode: str):
        """Log bet placement for monitoring"""

        if isinstance(bet, PaperBet):
            message = (
                f"{mode} BET: {bet.horse_name} @ {bet.matched_odds} - "
                f"Stake: £{bet.stake} - Confidence: {bet.confidence:.2%}"
            )
        else:  # LiveOrder
            message = (
                f"{mode} BET: {bet.bet_order.horse_name} @ {bet.bet_order.odds} - "
                f"Stake: £{bet.bet_order.stake} - ID: {bet.order_id}"
            )

        self.logger.info(message)

    async def export_session_data(self, filepath: str):
        """Export complete session data"""

        session_data = {
            "session_summary": self.get_performance_summary(),
            "export_timestamp": datetime.now().isoformat(),
        }

        # Add engine-specific data
        if self.paper_engine:
            paper_data = {
                "account": self.paper_engine.account.__dict__,
                "active_bets": [
                    bet.to_dict() for bet in self.paper_engine.active_bets.values()
                ],
                "settled_bets": [
                    bet.to_dict() for bet in self.paper_engine.settled_bets.values()
                ],
            }
            session_data["paper_trading_data"] = paper_data

        if self.live_engine:
            live_data = {
                "trading_summary": self.live_engine.get_trading_summary(),
                "active_orders": len(self.live_engine.active_orders),
                "completed_orders": len(self.live_engine.completed_orders),
            }
            session_data["live_trading_data"] = live_data

        # Save to file
        try:
            with open(filepath, "w") as f:
                json.dump(session_data, f, indent=2, default=str)

            self.logger.info(f"Session data exported to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to export session data: {e}")

    async def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring loop"""

        self.logger.info(f"Starting monitoring loop (interval: {interval}s)")

        while True:
            try:
                # Monitor live orders if in live mode
                if self.trading_mode == TradingMode.LIVE and self.live_engine:
                    await self.live_engine.monitor_orders()

                # Performance check
                summary = self.get_performance_summary()

                # Log periodic summary
                if self.total_bets_placed > 0 and self.total_bets_placed % 10 == 0:
                    self.logger.info(f"Session update: {summary}")

                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)


# Example usage and testing
async def main():
    """Example betting coordinator usage"""

    # Setup BETDAQ client
    config = BetdaqConfig(
        username="demo_user", password="demo_pass", paper_trading=True, enabled=True
    )

    client = BetdaqClient(config)
    await client.authenticate()

    # Initialize coordinator in paper trading mode
    coordinator = BettingCoordinator(
        betdaq_client=client,
        trading_mode=TradingMode.PAPER,
        paper_config=PaperTradingConfig(starting_balance=1000.0),
    )

    # Example AI prediction
    prediction = {
        "horse_name": "Thunder Strike",
        "selection_id": 12345,
        "confidence": 0.82,
        "predicted_odds": 2.8,
        "current_odds": 3.5,
        "value": 0.18,
    }

    market_info = MarketInfo(
        market_id=67890,
        market_name="4:15 Cheltenham - Win",
        start_time=datetime.now() + timedelta(minutes=20),
        status="active",
    )

    # Process AI prediction
    bet = await coordinator.process_ai_prediction(prediction, market_info)
    if bet:
        print(f"Bet placed: {bet}")

    # Simulate race result
    await coordinator.simulate_race_result(67890, winning_selection_id=12345)

    # Get performance summary
    summary = coordinator.get_performance_summary()
    print(f"Performance: {summary}")

    # Switch to live mode (demo only)
    success = await coordinator.switch_mode(TradingMode.LIVE)
    print(f"Mode switch success: {success}")

    # Export session data
    await coordinator.export_session_data("session_export.json")


if __name__ == "__main__":
    asyncio.run(main())
