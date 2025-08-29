"""
BETDAQ Live Betting System
Real money betting with comprehensive risk management
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .betdaq_client import BetdaqClient, BetdaqConfig, BetOrder, BettingSide, MarketInfo


class OrderStatus(Enum):
    """Live order status"""

    PENDING = "pending"
    MATCHED = "matched"
    PARTIALLY_MATCHED = "partially_matched"
    UNMATCHED = "unmatched"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    VOID = "void"


@dataclass
class LiveOrder:
    """Live betting order"""

    order_id: Optional[int]
    bet_order: BetOrder
    status: OrderStatus
    matched_amount: float = 0.0
    unmatched_amount: float = 0.0
    average_matched_price: float = 0.0
    placed_at: Optional[datetime] = None
    last_update: Optional[datetime] = None
    cancellation_attempts: int = 0

    @property
    def is_fully_matched(self) -> bool:
        """Check if order is fully matched"""
        return abs(self.matched_amount - self.bet_order.stake) < 0.01

    @property
    def is_active(self) -> bool:
        """Check if order is still active"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_MATCHED]


@dataclass
class RiskLimits:
    """Risk management limits"""

    max_stake_per_bet: float = 10.0
    max_total_exposure: float = 100.0
    max_daily_loss: float = 200.0
    max_orders_per_race: int = 3
    min_odds: float = 1.5
    max_odds: float = 20.0
    stop_loss_percentage: float = 10.0  # Stop trading if daily loss exceeds this %
    max_bet_frequency: int = 10  # Max bets per hour

    def validate_bet(
        self, order: BetOrder, current_exposure: float, daily_pnl: float
    ) -> Tuple[bool, List[str]]:
        """Validate bet against risk limits"""
        errors = []

        if order.stake > self.max_stake_per_bet:
            errors.append(f"Stake {order.stake} exceeds limit {self.max_stake_per_bet}")

        if current_exposure + order.stake > self.max_total_exposure:
            errors.append(
                f"Total exposure would exceed limit {self.max_total_exposure}"
            )

        if daily_pnl < -self.max_daily_loss:
            errors.append(f"Daily loss limit reached: {daily_pnl}")

        if order.odds < self.min_odds or order.odds > self.max_odds:
            errors.append(
                f"Odds {order.odds} outside limits {self.min_odds}-{self.max_odds}"
            )

        return len(errors) == 0, errors


class LiveBettingEngine:
    """Live betting engine with comprehensive risk management"""

    def __init__(self, betdaq_client: BetdaqClient, risk_limits: RiskLimits = None):
        self.client = betdaq_client
        self.risk_limits = risk_limits or RiskLimits()
        self.logger = logging.getLogger(__name__)

        # Trading state
        self.active_orders: Dict[int, LiveOrder] = {}
        self.completed_orders: Dict[int, LiveOrder] = {}
        self.daily_pnl = 0.0
        self.total_exposure = 0.0
        self.session_start = datetime.now()

        # Emergency controls
        self.trading_enabled = True
        self.emergency_stop_triggered = False

        # Monitoring
        self.bet_frequency_tracker = []

    async def place_bet(
        self, order: BetOrder, market_info: MarketInfo
    ) -> Optional[LiveOrder]:
        """Place a live bet with full risk management"""

        # Pre-flight checks
        if not self._pre_flight_checks(order):
            return None

        # Risk validation
        valid, errors = self.risk_limits.validate_bet(
            order, self.total_exposure, self.daily_pnl
        )
        if not valid:
            self.logger.warning(f"Bet rejected by risk limits: {', '.join(errors)}")
            return None

        # Frequency check
        if not self._check_bet_frequency():
            self.logger.warning("Bet rejected: frequency limit exceeded")
            return None

        try:
            # Place order via BETDAQ API
            if self.client.config.paper_trading:
                # Simulate order placement for paper trading
                order_id = self._generate_mock_order_id()
                api_result = {
                    "order_id": order_id,
                    "status": "matched",
                    "matched_amount": order.stake,
                    "average_price": order.odds,
                }
            else:
                # Real API call
                api_result = await self._place_order_via_api(order, market_info)
                if not api_result:
                    return None

            # Create live order
            live_order = LiveOrder(
                order_id=api_result["order_id"],
                bet_order=order,
                status=(
                    OrderStatus.MATCHED
                    if api_result["status"] == "matched"
                    else OrderStatus.PENDING
                ),
                matched_amount=api_result.get("matched_amount", 0.0),
                unmatched_amount=order.stake - api_result.get("matched_amount", 0.0),
                average_matched_price=api_result.get("average_price", order.odds),
                placed_at=datetime.now(),
                last_update=datetime.now(),
            )

            # Store order
            self.active_orders[live_order.order_id] = live_order

            # Update exposure
            self.total_exposure += order.stake

            # Track frequency
            self.bet_frequency_tracker.append(datetime.now())

            self.logger.info(
                f"Live bet placed: {order.horse_name} @ {order.odds} - "
                f"Stake: £{order.stake} - Order ID: {live_order.order_id}"
            )

            return live_order

        except Exception as e:
            self.logger.error(f"Failed to place live bet: {e}")
            return None

    def _pre_flight_checks(self, order: BetOrder) -> bool:
        """Perform pre-flight safety checks"""

        if not self.trading_enabled:
            self.logger.warning("Trading is disabled")
            return False

        if self.emergency_stop_triggered:
            self.logger.warning("Emergency stop is active")
            return False

        if not self.client.authenticated:
            self.logger.warning("BETDAQ client not authenticated")
            return False

        if order.stake <= 0:
            self.logger.warning("Invalid stake amount")
            return False

        return True

    def _check_bet_frequency(self) -> bool:
        """Check betting frequency limits"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # Remove old entries
        self.bet_frequency_tracker = [
            timestamp
            for timestamp in self.bet_frequency_tracker
            if timestamp > hour_ago
        ]

        # Check frequency
        return len(self.bet_frequency_tracker) < self.risk_limits.max_bet_frequency

    def _generate_mock_order_id(self) -> int:
        """Generate mock order ID for paper trading"""
        return int(datetime.now().timestamp() * 1000) % 1000000

    async def _place_order_via_api(
        self, order: BetOrder, market_info: MarketInfo
    ) -> Optional[Dict]:
        """Place order via BETDAQ API"""
        try:
            # This would use the actual BETDAQ API
            # Implementation depends on the specific betdaq library methods

            # For now, return mock result
            return {
                "order_id": self._generate_mock_order_id(),
                "status": "matched",
                "matched_amount": order.stake,
                "average_price": order.odds,
            }

        except Exception as e:
            self.logger.error(f"API order placement failed: {e}")
            return None

    async def cancel_bet(self, order_id: int) -> bool:
        """Cancel an active bet"""

        if order_id not in self.active_orders:
            self.logger.warning(f"Order {order_id} not found in active orders")
            return False

        live_order = self.active_orders[order_id]

        if not live_order.is_active:
            self.logger.warning(f"Order {order_id} is not active")
            return False

        try:
            live_order.cancellation_attempts += 1

            if self.client.config.paper_trading:
                # Simulate cancellation
                success = True
            else:
                # Real API call
                success = await self._cancel_order_via_api(order_id)

            if success:
                live_order.status = OrderStatus.CANCELLED
                live_order.last_update = datetime.now()

                # Update exposure
                self.total_exposure -= live_order.unmatched_amount

                # Move to completed orders
                self.completed_orders[order_id] = live_order
                del self.active_orders[order_id]

                self.logger.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                self.logger.error(f"Failed to cancel order {order_id}")
                return False

        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def _cancel_order_via_api(self, order_id: int) -> bool:
        """Cancel order via BETDAQ API"""
        try:
            # This would use the actual BETDAQ API cancellation method
            return True
        except Exception as e:
            self.logger.error(f"API order cancellation failed: {e}")
            return False

    async def update_order_status(self, order_id: int) -> bool:
        """Update order status from BETDAQ API"""

        if order_id not in self.active_orders:
            return False

        try:
            if self.client.config.paper_trading:
                # Mock update for paper trading
                return True

            # Real API call to get order status
            order_status = await self._get_order_status_via_api(order_id)

            if order_status:
                live_order = self.active_orders[order_id]

                # Update order details
                live_order.matched_amount = order_status.get(
                    "matched_amount", live_order.matched_amount
                )
                live_order.unmatched_amount = order_status.get(
                    "unmatched_amount", live_order.unmatched_amount
                )
                live_order.average_matched_price = order_status.get(
                    "average_price", live_order.average_matched_price
                )
                live_order.last_update = datetime.now()

                # Update status
                api_status = order_status.get("status", "")
                if api_status == "matched":
                    live_order.status = OrderStatus.MATCHED
                elif api_status == "partially_matched":
                    live_order.status = OrderStatus.PARTIALLY_MATCHED
                elif api_status == "cancelled":
                    live_order.status = OrderStatus.CANCELLED

                # If order is no longer active, move to completed
                if not live_order.is_active:
                    self.completed_orders[order_id] = live_order
                    del self.active_orders[order_id]

                return True

        except Exception as e:
            self.logger.error(f"Failed to update order {order_id} status: {e}")
            return False

    async def _get_order_status_via_api(self, order_id: int) -> Optional[Dict]:
        """Get order status via BETDAQ API"""
        try:
            # This would use the actual BETDAQ API method to get order status
            return {
                "status": "matched",
                "matched_amount": 10.0,
                "unmatched_amount": 0.0,
                "average_price": 3.5,
            }
        except Exception as e:
            self.logger.error(f"API order status check failed: {e}")
            return None

    async def monitor_orders(self):
        """Monitor all active orders"""

        for order_id in list(self.active_orders.keys()):
            await self.update_order_status(order_id)
            await asyncio.sleep(0.1)  # Small delay between API calls

    async def settle_bet(self, order_id: int, result: Dict):
        """Settle a completed bet with race result"""

        if order_id not in self.completed_orders:
            self.logger.warning(f"Order {order_id} not found in completed orders")
            return

        live_order = self.completed_orders[order_id]

        # Determine if bet won
        winning_selection_id = result.get("winner_selection_id")
        if winning_selection_id is None:
            return

        if live_order.bet_order.side == BettingSide.BACK:
            won = live_order.bet_order.selection_id == winning_selection_id
        else:  # LAY
            won = live_order.bet_order.selection_id != winning_selection_id

        # Calculate P&L
        if won:
            if live_order.bet_order.side == BettingSide.BACK:
                gross_profit = live_order.matched_amount * (
                    live_order.average_matched_price - 1
                )
            else:  # LAY
                gross_profit = live_order.matched_amount

            commission = gross_profit * 0.02  # 2% BETDAQ commission
            net_profit = gross_profit - commission

        else:
            if live_order.bet_order.side == BettingSide.BACK:
                net_profit = -live_order.matched_amount
            else:  # LAY
                net_profit = -live_order.matched_amount * (
                    live_order.average_matched_price - 1
                )

        # Update P&L
        live_order.bet_order.pnl = net_profit
        self.daily_pnl += net_profit

        # Update exposure
        self.total_exposure -= live_order.matched_amount

        result_text = "WON" if won else "LOST"
        self.logger.info(
            f"Bet settled: {live_order.bet_order.horse_name} - {result_text} - "
            f"P&L: £{net_profit:.2f}"
        )

        # Check if emergency stop needed due to losses
        await self._check_emergency_stop()

    async def _check_emergency_stop(self):
        """Check if emergency stop should be triggered"""

        loss_percentage = abs(self.daily_pnl) / self.risk_limits.max_daily_loss * 100

        if loss_percentage >= self.risk_limits.stop_loss_percentage:
            await self.emergency_stop("Daily loss limit reached")

    async def emergency_stop(self, reason: str = "Manual trigger"):
        """Emergency stop - cancel all orders and disable trading"""

        self.logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        self.emergency_stop_triggered = True
        self.trading_enabled = False

        # Cancel all active orders
        cancel_tasks = []
        for order_id in list(self.active_orders.keys()):
            cancel_tasks.append(self.cancel_bet(order_id))

        if cancel_tasks:
            await asyncio.gather(*cancel_tasks, return_exceptions=True)

        self.logger.critical(
            f"Emergency stop completed - {len(cancel_tasks)} orders cancelled"
        )

    def get_trading_summary(self) -> Dict:
        """Get current trading summary"""

        total_orders = len(self.active_orders) + len(self.completed_orders)

        return {
            "session_start": self.session_start.isoformat(),
            "trading_enabled": self.trading_enabled,
            "emergency_stop": self.emergency_stop_triggered,
            "daily_pnl": self.daily_pnl,
            "total_exposure": self.total_exposure,
            "active_orders": len(self.active_orders),
            "completed_orders": len(self.completed_orders),
            "total_orders": total_orders,
            "risk_limits": {
                "max_stake_per_bet": self.risk_limits.max_stake_per_bet,
                "max_total_exposure": self.risk_limits.max_total_exposure,
                "max_daily_loss": self.risk_limits.max_daily_loss,
            },
        }

    async def enable_trading(self):
        """Re-enable trading after emergency stop"""
        if self.emergency_stop_triggered:
            self.emergency_stop_triggered = False
            self.trading_enabled = True
            self.logger.info("Trading re-enabled after emergency stop")

    def reset_session(self):
        """Reset session for new trading day"""
        self.daily_pnl = 0.0
        self.total_exposure = 0.0
        self.session_start = datetime.now()
        self.bet_frequency_tracker.clear()
        self.trading_enabled = True
        self.emergency_stop_triggered = False

        # Clear completed orders (keep active ones)
        self.completed_orders.clear()

        self.logger.info("Trading session reset")


# Integration with AI system
class AILiveBettingInterface:
    """Interface between AI predictions and live betting"""

    def __init__(self, betting_engine: LiveBettingEngine):
        self.betting_engine = betting_engine
        self.logger = logging.getLogger(__name__)

    async def process_ai_prediction(
        self, prediction: Dict, market_info: MarketInfo
    ) -> Optional[LiveOrder]:
        """Process AI prediction and potentially place live bet"""

        # Extract prediction data
        confidence = prediction.get("confidence", 0.0)
        predicted_odds = prediction.get("predicted_odds", 0.0)
        horse_name = prediction.get("horse_name", "")
        selection_id = prediction.get("selection_id", 0)

        # Only consider high-confidence predictions
        min_confidence = (
            self.betting_engine.risk_limits.min_odds / 10
        )  # Dynamic threshold
        if confidence < min_confidence:
            return None

        # Calculate value bet
        current_odds = prediction.get("current_odds", predicted_odds)
        value = self._calculate_value(predicted_odds, current_odds)

        # Only bet if significant value
        if value < 0.1:  # 10% minimum edge
            return None

        # Calculate stake using Kelly Criterion
        stake = self._calculate_kelly_stake(confidence, value, current_odds)

        # Create bet order
        order = BetOrder(
            selection_id=selection_id,
            horse_name=horse_name,
            stake=stake,
            odds=current_odds,
            side=BettingSide.BACK,
            market_id=market_info.market_id,
            confidence=confidence,
            value=value,
        )

        # Place bet
        return await self.betting_engine.place_bet(order, market_info)

    def _calculate_value(self, predicted_odds: float, current_odds: float) -> float:
        """Calculate betting value"""
        if predicted_odds <= 1.0 or current_odds <= 1.0:
            return 0.0

        implied_prob = 1.0 / predicted_odds
        market_prob = 1.0 / current_odds

        # Value = (true_probability * market_odds - 1) / (market_odds - 1)
        return (implied_prob * current_odds - 1) / (current_odds - 1)

    def _calculate_kelly_stake(
        self, confidence: float, value: float, odds: float
    ) -> float:
        """Calculate optimal stake using Kelly Criterion"""

        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = confidence, q = 1-confidence

        b = odds - 1
        p = confidence
        q = 1 - confidence

        kelly_fraction = (b * p - q) / b

        # Conservative approach - use 25% of Kelly
        conservative_fraction = kelly_fraction * 0.25

        # Convert to stake amount
        max_stake = self.betting_engine.risk_limits.max_stake_per_bet
        stake = min(max_stake, max(1.0, conservative_fraction * max_stake))

        return round(stake, 2)


# Example usage
async def main():
    """Example live betting session"""

    # Setup
    config = BetdaqConfig(
        username="demo_user",
        password="demo_pass",
        paper_trading=True,  # Start with paper trading
        enabled=True,
    )

    client = BetdaqClient(config)
    await client.authenticate()

    risk_limits = RiskLimits(
        max_stake_per_bet=20.0, max_daily_loss=100.0, max_total_exposure=200.0
    )

    betting_engine = LiveBettingEngine(client, risk_limits)
    ai_interface = AILiveBettingInterface(betting_engine)

    # Example AI prediction
    prediction = {
        "horse_name": "Lightning Strike",
        "selection_id": 12345,
        "confidence": 0.85,
        "predicted_odds": 3.0,
        "current_odds": 4.5,
        "value": 0.25,
    }

    market_info = MarketInfo(
        market_id=67890,
        market_name="3:30 Ascot - Win",
        start_time=datetime.now() + timedelta(minutes=15),
        status="active",
    )

    # Process prediction
    live_order = await ai_interface.process_ai_prediction(prediction, market_info)

    if live_order:
        print(f"Live bet placed: {live_order.order_id}")

        # Monitor order
        await betting_engine.monitor_orders()

        # Get summary
        summary = betting_engine.get_trading_summary()
        print(f"Trading summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())
