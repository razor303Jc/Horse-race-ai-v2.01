"""
BETDAQ API Client for Horse Racing AI System
Provides secure integration with BETDAQ betting exchange
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

try:
    from betdaq.apiclient import APIClient
    from betdaq.enums import (
        Boolean,
        OrderKillType,
        Polarity,
        SportID,
        WithdrawRepriceOption,
    )
    from betdaq.exceptions import APIError, BetdaqError
    from betdaq.filters import create_order, update_order

    BETDAQ_AVAILABLE = True
except ImportError:
    # Graceful degradation if betdaq library not installed
    BETDAQ_AVAILABLE = False
    APIClient = None
    SportID = None
    Boolean = None
    Polarity = None
    OrderKillType = None
    WithdrawRepriceOption = None


class BettingSide(Enum):
    """Betting side enumeration"""

    BACK = "back"
    LAY = "lay"


@dataclass
class BetdaqConfig:
    """Configuration for BETDAQ API integration"""

    username: str = ""
    password: str = ""
    enabled: bool = False
    max_stake_per_bet: float = 10.0
    max_daily_loss: float = 100.0
    min_odds: float = 1.5
    max_odds: float = 10.0
    min_confidence: float = 0.75
    min_value: float = 0.10
    kelly_multiplier: float = 0.25
    paper_trading: bool = True

    @classmethod
    def from_env(cls) -> "BetdaqConfig":
        """Load configuration from environment variables"""
        return cls(
            username=os.getenv("BETDAQ_USERNAME", ""),
            password=os.getenv("BETDAQ_PASSWORD", ""),
            enabled=os.getenv("BETDAQ_ENABLED", "false").lower() == "true",
            max_stake_per_bet=float(os.getenv("BETDAQ_MAX_STAKE", "10.0")),
            max_daily_loss=float(os.getenv("BETDAQ_MAX_LOSS", "100.0")),
            min_odds=float(os.getenv("BETDAQ_MIN_ODDS", "1.5")),
            max_odds=float(os.getenv("BETDAQ_MAX_ODDS", "10.0")),
            min_confidence=float(os.getenv("BETDAQ_MIN_CONFIDENCE", "0.75")),
            min_value=float(os.getenv("BETDAQ_MIN_VALUE", "0.10")),
            kelly_multiplier=float(os.getenv("BETDAQ_KELLY_MULTIPLIER", "0.25")),
            paper_trading=os.getenv("BETDAQ_PAPER_TRADING", "true").lower() == "true",
        )

    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []

        if self.enabled and not BETDAQ_AVAILABLE:
            errors.append("BETDAQ library not installed - run: pip install betdaq")

        if self.enabled and not self.username:
            errors.append("BETDAQ_USERNAME not configured")

        if self.enabled and not self.password:
            errors.append("BETDAQ_PASSWORD not configured")

        if self.max_stake_per_bet <= 0:
            errors.append("max_stake_per_bet must be positive")

        if self.max_daily_loss <= 0:
            errors.append("max_daily_loss must be positive")

        if self.min_odds >= self.max_odds:
            errors.append("min_odds must be less than max_odds")

        return errors


@dataclass
class MarketInfo:
    """Market information from BETDAQ"""

    market_id: int
    market_name: str
    start_time: datetime
    status: str
    runners: List[Dict] = field(default_factory=list)
    reset_count: int = 0
    withdrawal_seq: int = 0


@dataclass
class BetOrder:
    """Betting order information"""

    selection_id: int
    horse_name: str
    stake: float
    odds: float
    side: BettingSide
    market_id: int
    confidence: float = 0.0
    value: float = 0.0
    reference_number: Optional[int] = None
    order_id: Optional[int] = None
    status: str = "pending"
    placed_at: Optional[datetime] = None
    matched_at: Optional[datetime] = None
    pnl: float = 0.0


class BetdaqClient:
    """Main BETDAQ API client"""

    def __init__(self, config: BetdaqConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_client = None
        self.authenticated = False
        self.daily_pnl = 0.0
        self.active_orders = {}

        if not BETDAQ_AVAILABLE:
            self.logger.warning(
                "BETDAQ library not available - running in simulation mode"
            )
            return

        if self.config.enabled and self.config.username and self.config.password:
            try:
                self.api_client = APIClient(self.config.username, self.config.password)
                self.logger.info("BETDAQ client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize BETDAQ client: {e}")

    async def authenticate(self) -> bool:
        """Test API connection and authentication"""
        if not self.api_client:
            return False

        try:
            # Test with a simple API call
            sports = self.api_client.marketdata.get_sports()
            self.authenticated = True if sports else False

            if self.authenticated:
                self.logger.info("BETDAQ authentication successful")
            else:
                self.logger.error(
                    "BETDAQ authentication failed - no sports data returned"
                )

            return self.authenticated

        except Exception as e:
            self.logger.error(f"BETDAQ authentication failed: {e}")
            self.authenticated = False
            return False

    async def get_horse_racing_markets(self) -> List[MarketInfo]:
        """Get active horse racing markets"""
        if not self.authenticated:
            return []

        try:
            markets_data = self.api_client.marketdata.get_sport_markets(
                sport_ids=[SportID.HorseRacing.value],  # 100004
                include_selections=True,
                WantDirectDescendentsOnly=Boolean.F.value,
            )

            markets = []
            for market in markets_data:
                if self._is_market_active(market):
                    market_info = MarketInfo(
                        market_id=market["market_id"],
                        market_name=market["market_name"],
                        start_time=market["market_start_time"],
                        status=market.get("status", "unknown"),
                        runners=market.get("runners", []),
                        reset_count=market.get("reset_count", 0),
                        withdrawal_seq=market.get("withdrawal_sequence_number", 0),
                    )
                    markets.append(market_info)

            self.logger.info(f"Found {len(markets)} active horse racing markets")
            return markets

        except Exception as e:
            self.logger.error(f"Failed to get horse racing markets: {e}")
            return []

    async def get_market_prices(self, market_ids: List[int]) -> Dict[int, Dict]:
        """Get real-time prices for markets"""
        if not self.authenticated:
            return {}

        try:
            prices_data = self.api_client.marketdata.get_prices(
                market_ids=market_ids,
                ThresholdAmount=1.0,
                NumberForPricesRequired=-1,  # All available
                NumberAgainstPricesRequired=-1,
                WantMarketMatchedAmount=Boolean.T.value,
                WantSelectionsMatchedAmounts=Boolean.T.value,
                WantSelectionMatchedDetails=Boolean.T.value,
            )

            parsed_prices = {}
            for market in prices_data:
                market_id = market["market_id"]
                runners_prices = {}

                for runner in market.get("runners", []):
                    runner_id = runner["runner_id"]
                    book = runner.get("runner_book", {})

                    # Extract best back and lay prices
                    best_back = self._get_best_price(book.get("batb", []))
                    best_lay = self._get_best_price(book.get("batl", []))

                    runners_prices[runner_id] = {
                        "runner_name": runner["runner_name"],
                        "best_back": best_back,
                        "best_lay": best_lay,
                        "status": runner.get("runner_status", "unknown"),
                    }

                parsed_prices[market_id] = runners_prices

            return parsed_prices

        except Exception as e:
            self.logger.error(f"Failed to get market prices: {e}")
            return {}

    async def place_bet(self, bet: BetOrder, market_info: MarketInfo) -> Optional[Dict]:
        """Place a bet on BETDAQ exchange"""

        # Validate bet
        if not self._validate_bet(bet):
            return None

        # Check daily limits
        if not self._check_daily_limits():
            return None

        # Paper trading mode
        if self.config.paper_trading:
            return self._simulate_bet_placement(bet)

        # Real betting
        if not self.authenticated:
            self.logger.error("Cannot place bet - not authenticated")
            return None

        try:
            # Create BETDAQ order
            polarity = Polarity.back if bet.side == BettingSide.BACK else Polarity.lay

            order = create_order(
                SelectionId=bet.selection_id,
                Stake=bet.stake,
                Price=bet.odds,
                Polarity=polarity.value,
                ExpectedSelectionResetCount=market_info.reset_count,
                ExpectedWithdrawalSequenceNumber=market_info.withdrawal_seq,
                CancelOnInRunning=Boolean.T,
                CancelIfSelectionReset=Boolean.T,
                WithdrawalRepriceOption=WithdrawRepriceOption.Cancel,
                KillType=OrderKillType.FillOrKillDontCancel.value,
                PunterReferenceNumber=bet.reference_number
                or int(datetime.utcnow().timestamp()),
            )

            # Place order
            result = self.api_client.betting.place_orders(
                order_list=[order],
                WantAllOrNothingBehaviour=Boolean.T.value,
                receipt=True,
            )

            if result:
                order_info = result[0]
                bet.order_id = order_info["order_id"]
                bet.status = order_info.get("status", "placed")
                bet.placed_at = datetime.utcnow()

                # Store active order
                self.active_orders[bet.order_id] = bet

                self.logger.info(
                    f"Bet placed successfully: {bet.horse_name} @ {bet.odds} - Order ID: {bet.order_id}"
                )

                return {
                    "order_id": bet.order_id,
                    "status": bet.status,
                    "horse_name": bet.horse_name,
                    "stake": bet.stake,
                    "odds": bet.odds,
                    "side": bet.side.value,
                    "placed_at": bet.placed_at,
                }
            else:
                self.logger.error("Failed to place bet - no result returned")
                return None

        except BetdaqError as e:
            self.logger.error(f"BETDAQ API error placing bet: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error placing bet: {e}")
            return None

    async def get_order_status(self, order_id: int) -> Optional[Dict]:
        """Get status of a specific order"""
        if not self.authenticated:
            return None

        try:
            order_details = self.api_client.betting.get_single_order(OrderId=order_id)
            if order_details:
                return {
                    "order_id": order_details["order_id"],
                    "status": order_details["status"],
                    "matched_size": order_details.get("matched_size", 0),
                    "remaining_size": order_details.get("remaining_size", 0),
                    "matched_price": order_details.get("matched_price", 0),
                    "pnl": self._calculate_order_pnl(order_details),
                }
        except Exception as e:
            self.logger.error(f"Failed to get order status for {order_id}: {e}")
            return None

    async def cancel_order(self, order_id: int) -> bool:
        """Cancel a specific order"""
        if not self.authenticated:
            return False

        try:
            result = self.api_client.betting.cancel_orders(order_ids=[order_id])
            if result:
                self.logger.info(f"Order {order_id} cancelled successfully")
                # Update local order status
                if order_id in self.active_orders:
                    self.active_orders[order_id].status = "cancelled"
                return True
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    async def emergency_stop(self) -> bool:
        """Cancel all active orders immediately"""
        if not self.authenticated:
            return False

        try:
            result = self.api_client.betting.cancel_all_orders()
            self.logger.critical(
                f"Emergency stop executed - all orders cancelled: {result}"
            )

            # Update all local orders
            for order_id in self.active_orders:
                self.active_orders[order_id].status = "cancelled"

            return True
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
            return False

    def _validate_bet(self, bet: BetOrder) -> bool:
        """Validate bet parameters"""
        if bet.stake > self.config.max_stake_per_bet:
            self.logger.warning(
                f"Stake {bet.stake} exceeds limit {self.config.max_stake_per_bet}"
            )
            return False

        if bet.odds < self.config.min_odds or bet.odds > self.config.max_odds:
            self.logger.warning(
                f"Odds {bet.odds} outside limits {self.config.min_odds}-{self.config.max_odds}"
            )
            return False

        if bet.confidence < self.config.min_confidence:
            self.logger.warning(
                f"Confidence {bet.confidence} below minimum {self.config.min_confidence}"
            )
            return False

        if bet.value < self.config.min_value:
            self.logger.warning(
                f"Value {bet.value} below minimum {self.config.min_value}"
            )
            return False

        return True

    def _check_daily_limits(self) -> bool:
        """Check if daily loss limits exceeded"""
        if abs(self.daily_pnl) >= self.config.max_daily_loss:
            self.logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            return False
        return True

    def _simulate_bet_placement(self, bet: BetOrder) -> Dict:
        """Simulate bet placement for paper trading"""
        bet.order_id = int(datetime.utcnow().timestamp())
        bet.status = "simulated"
        bet.placed_at = datetime.utcnow()

        self.active_orders[bet.order_id] = bet

        self.logger.info(
            f"SIMULATED bet: {bet.horse_name} @ {bet.odds} - Stake: £{bet.stake}"
        )

        return {
            "order_id": bet.order_id,
            "status": bet.status,
            "horse_name": bet.horse_name,
            "stake": bet.stake,
            "odds": bet.odds,
            "side": bet.side.value,
            "placed_at": bet.placed_at,
            "simulated": True,
        }

    def _is_market_active(self, market: Dict) -> bool:
        """Check if market is active and suitable for betting"""
        status = market.get("status", "").lower()
        if status not in ["active", "open"]:
            return False

        # Check if market starts within reasonable timeframe
        start_time = market.get("market_start_time")
        if start_time:
            now = datetime.utcnow()
            time_to_start = start_time - now
            # Only consider markets starting within next 4 hours
            if (
                time_to_start.total_seconds() > 4 * 3600
                or time_to_start.total_seconds() < 0
            ):
                return False

        return True

    def _get_best_price(self, book: List) -> Optional[float]:
        """Extract best price from order book"""
        if not book:
            return None
        # Book format: [[level, price, size], ...]
        # Return the best price (level 0)
        for level, price, size in book:
            if level == 0 and size > 0:
                return float(price)
        return None

    def _calculate_order_pnl(self, order_details: Dict) -> float:
        """Calculate P&L for an order"""
        # Simplified P&L calculation
        matched_size = order_details.get("matched_size", 0)
        matched_price = order_details.get("matched_price", 0)

        if matched_size > 0 and matched_price > 0:
            # This is a simplified calculation - actual P&L depends on result
            return matched_size * (matched_price - 1)  # Potential profit for back bet

        return 0.0


# Factory function for easy initialization
def create_betdaq_client() -> BetdaqClient:
    """Create and initialize BETDAQ client from environment"""
    config = BetdaqConfig.from_env()

    # Validate configuration
    errors = config.validate()
    if errors:
        logger = logging.getLogger(__name__)
        for error in errors:
            logger.error(f"BETDAQ config error: {error}")

        if config.enabled:
            logger.error("BETDAQ integration disabled due to configuration errors")
            config.enabled = False

    return BetdaqClient(config)


# Example usage
if __name__ == "__main__":

    async def main():
        # Initialize client
        client = create_betdaq_client()

        # Test authentication
        if await client.authenticate():
            print("✅ BETDAQ authentication successful")

            # Get markets
            markets = await client.get_horse_racing_markets()
            print(f"📊 Found {len(markets)} horse racing markets")

            if markets:
                # Get prices for first market
                market = markets[0]
                prices = await client.get_market_prices([market.market_id])
                print(
                    f"💰 Prices for {market.market_name}: {len(prices.get(market.market_id, {}))} runners"
                )
        else:
            print("❌ BETDAQ authentication failed")

    # Run example
    asyncio.run(main())
