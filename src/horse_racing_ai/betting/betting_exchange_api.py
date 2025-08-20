#!/usr/bin/env python3
"""
Betting Exchange API Integration
===============================

Integrates with major betting exchanges (Betfair, Smarkets, etc.) for automated
betting execution of 80/20 and Dutching strategies.

Features:
- Multi-exchange support
- Automated bet placement
- Risk management
- Real-time market monitoring
- Position management
- Settlement tracking

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import requests
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
import threading
import time
import hashlib
import hmac
import base64
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BetPlacement:
    """Bet placement order"""

    bet_id: str
    market_id: str
    runner_id: str
    horse_name: str
    bet_type: str  # "BACK", "LAY"
    odds: float
    stake: float
    strategy_type: str  # "80/20", "dutching"
    race_id: str
    placement_time: datetime
    status: str = "PENDING"  # "PENDING", "MATCHED", "UNMATCHED", "CANCELLED"
    matched_amount: float = 0.0
    average_matched_odds: float = 0.0


@dataclass
class MarketPosition:
    """Current market position"""

    market_id: str
    race_id: str
    strategy_type: str
    total_stake: float
    potential_profit: float
    potential_loss: float
    bets: List[BetPlacement]
    status: str = "ACTIVE"  # "ACTIVE", "SETTLED", "CANCELLED"


@dataclass
class ExchangeBalance:
    """Account balance information"""

    available_balance: float
    exposure: float
    total_balance: float
    currency: str = "GBP"
    last_update: datetime = None


class BetfairAPI:
    """Betfair Exchange API integration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session_token = None
        self.app_key = config.get("app_key", "")
        self.username = config.get("username", "")
        self.password = config.get("password", "")

        # API endpoints
        self.auth_url = "https://identitysso.betfair.com/api"
        self.betting_url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
        self.accounts_url = "https://api.betfair.com/exchange/account/json-rpc/v1"

        logger.info("Betfair API initialized")

    def authenticate(self) -> bool:
        """Authenticate with Betfair"""
        try:
            login_data = {"username": self.username, "password": self.password}

            headers = {
                "X-Application": self.app_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }

            response = self.session.post(
                f"{self.auth_url}/login", data=login_data, headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "SUCCESS":
                    self.session_token = result.get("token")
                    logger.info("Betfair authentication successful")
                    return True

            logger.error(f"Betfair authentication failed: {response.text}")
            return False

        except Exception as e:
            logger.error(f"Error authenticating with Betfair: {e}")
            return False

    def _make_request(
        self, url: str, method: str, params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Make authenticated API request"""
        if not self.session_token:
            if not self.authenticate():
                return None

        headers = {
            "X-Application": self.app_key,
            "X-Authentication": self.session_token,
            "Content-Type": "application/json",
        }

        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1}

        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if "result" in result:
                return result["result"]
            else:
                logger.error(f"API error: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def get_account_balance(self) -> Optional[ExchangeBalance]:
        """Get account balance"""
        try:
            result = self._make_request(
                self.accounts_url, "AccountAPING/v1.0/getAccountFunds"
            )

            if result:
                return ExchangeBalance(
                    available_balance=float(result.get("availableToBetBalance", 0.0)),
                    exposure=float(result.get("exposure", 0.0)),
                    total_balance=float(result.get("availableToBetBalance", 0.0))
                    + float(result.get("exposure", 0.0)),
                    last_update=datetime.now(),
                )

            return None

        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None

    def get_market_odds(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get current market odds"""
        try:
            params = {
                "marketIds": [market_id],
                "priceProjection": {
                    "priceData": ["EX_BEST_OFFERS", "EX_TRADED"],
                    "virtualise": False,
                },
            }

            result = self._make_request(
                self.betting_url, "SportsAPING/v1.0/listMarketBook", params
            )

            if result and len(result) > 0:
                return result[0]

            return None

        except Exception as e:
            logger.error(f"Error getting market odds: {e}")
            return None

    def place_bet(
        self, market_id: str, runner_id: str, bet_type: str, odds: float, stake: float
    ) -> Optional[BetPlacement]:
        """Place a bet"""
        try:
            instruction = {
                "selectionId": runner_id,
                "handicap": 0,
                "side": bet_type,  # "BACK" or "LAY"
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": stake,
                    "price": odds,
                    "persistenceType": "LAPSE",
                },
            }

            params = {"marketId": market_id, "instructions": [instruction]}

            result = self._make_request(
                self.betting_url, "SportsAPING/v1.0/placeOrders", params
            )

            if result and result.get("status") == "SUCCESS":
                instruction_result = result.get("instructionReports", [{}])[0]

                if instruction_result.get("status") == "SUCCESS":
                    bet_id = instruction_result.get("betId")

                    return BetPlacement(
                        bet_id=bet_id,
                        market_id=market_id,
                        runner_id=runner_id,
                        horse_name="",  # To be filled by caller
                        bet_type=bet_type,
                        odds=odds,
                        stake=stake,
                        strategy_type="",  # To be filled by caller
                        race_id="",  # To be filled by caller
                        placement_time=datetime.now(),
                        status=(
                            "MATCHED"
                            if instruction_result.get("sizeMatched", 0) > 0
                            else "UNMATCHED"
                        ),
                        matched_amount=float(instruction_result.get("sizeMatched", 0)),
                    )

            logger.error(f"Bet placement failed: {result}")
            return None

        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            return None

    def cancel_bet(self, market_id: str, bet_id: str) -> bool:
        """Cancel a bet"""
        try:
            params = {"marketId": market_id, "instructions": [{"betId": bet_id}]}

            result = self._make_request(
                self.betting_url, "SportsAPING/v1.0/cancelOrders", params
            )

            if result and result.get("status") == "SUCCESS":
                return True

            return False

        except Exception as e:
            logger.error(f"Error cancelling bet: {e}")
            return False

    def get_current_orders(self, market_id: str = None) -> List[BetPlacement]:
        """Get current unmatched orders"""
        try:
            params = {}
            if market_id:
                params["marketIds"] = [market_id]

            result = self._make_request(
                self.betting_url, "SportsAPING/v1.0/listCurrentOrders", params
            )

            bets = []
            if result:
                for order in result.get("currentOrders", []):
                    bet = BetPlacement(
                        bet_id=order.get("betId"),
                        market_id=order.get("marketId"),
                        runner_id=str(order.get("selectionId")),
                        horse_name="",
                        bet_type=order.get("side"),
                        odds=float(order.get("priceSize", {}).get("price", 0)),
                        stake=float(order.get("priceSize", {}).get("size", 0)),
                        strategy_type="",
                        race_id="",
                        placement_time=datetime.fromisoformat(
                            order.get("placedDate").replace("Z", "+00:00")
                        ),
                        status=order.get("status"),
                        matched_amount=float(order.get("sizeMatched", 0)),
                    )
                    bets.append(bet)

            return bets

        except Exception as e:
            logger.error(f"Error getting current orders: {e}")
            return []


class BettingExchangeIntegrator:
    """Main betting exchange integration system"""

    def __init__(self, config_path: str = "config/betting_exchange_config.json"):
        self.config = self._load_config(config_path)
        self.exchanges = {}
        self.positions = {}
        self.active_bets = {}
        self.balance_cache = {}

        # Initialize exchanges
        self._init_exchanges()

        # Risk management
        self.max_daily_stake = self.config.get("risk_management", {}).get(
            "max_daily_stake", 200.0
        )
        self.max_single_stake = self.config.get("risk_management", {}).get(
            "max_single_stake", 50.0
        )
        self.daily_stake_used = 0.0

        logger.info("Betting Exchange Integrator initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load betting exchange configuration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {
                "exchanges": {
                    "betfair": {
                        "enabled": True,
                        "app_key": "",
                        "username": "",
                        "password": "",
                        "commission_rate": 0.05,
                    }
                },
                "risk_management": {
                    "max_daily_stake": 200.0,
                    "max_single_stake": 50.0,
                    "max_exposure": 500.0,
                    "stop_loss_percentage": 20.0,
                },
            }

    def _init_exchanges(self):
        """Initialize exchange connections"""
        exchanges_config = self.config.get("exchanges", {})

        # Initialize Betfair
        betfair_config = exchanges_config.get("betfair", {})
        if betfair_config.get("enabled", False):
            self.exchanges["betfair"] = BetfairAPI(betfair_config)

            # Test authentication
            if self.exchanges["betfair"].authenticate():
                logger.info("Betfair exchange connected successfully")
            else:
                logger.error("Failed to connect to Betfair exchange")

    def place_strategy_bets(
        self,
        strategy_type: str,
        race_id: str,
        market_id: str,
        selections: List[Dict[str, Any]],
    ) -> Optional[MarketPosition]:
        """Place bets for a strategy"""
        try:
            # Risk checks
            total_stake = sum(sel.get("stake", 0) for sel in selections)

            if not self._check_risk_limits(total_stake):
                logger.warning(f"Strategy bets rejected due to risk limits")
                return None

            # Check balance
            if not self._check_balance(total_stake):
                logger.warning(f"Insufficient balance for strategy bets")
                return None

            # Place bets
            placed_bets = []
            for selection in selections:
                bet = self._place_single_bet(
                    market_id=market_id,
                    runner_id=selection.get("runner_id"),
                    horse_name=selection.get("horse_name", ""),
                    bet_type="BACK",  # Assuming back bets for strategies
                    odds=selection.get("odds"),
                    stake=selection.get("stake"),
                    strategy_type=strategy_type,
                    race_id=race_id,
                )

                if bet:
                    placed_bets.append(bet)
                    self.active_bets[bet.bet_id] = bet
                else:
                    logger.error(
                        f"Failed to place bet for {selection.get('horse_name')}"
                    )

            if placed_bets:
                # Create market position
                position = MarketPosition(
                    market_id=market_id,
                    race_id=race_id,
                    strategy_type=strategy_type,
                    total_stake=sum(bet.stake for bet in placed_bets),
                    potential_profit=self._calculate_potential_profit(placed_bets),
                    potential_loss=sum(bet.stake for bet in placed_bets),
                    bets=placed_bets,
                )

                self.positions[market_id] = position
                self.daily_stake_used += position.total_stake

                logger.info(
                    f"Placed {len(placed_bets)} bets for {strategy_type} strategy"
                )
                return position

            return None

        except Exception as e:
            logger.error(f"Error placing strategy bets: {e}")
            return None

    def _place_single_bet(
        self,
        market_id: str,
        runner_id: str,
        horse_name: str,
        bet_type: str,
        odds: float,
        stake: float,
        strategy_type: str,
        race_id: str,
    ) -> Optional[BetPlacement]:
        """Place a single bet"""
        try:
            # Use primary exchange (Betfair)
            exchange = self.exchanges.get("betfair")
            if not exchange:
                logger.error("No exchange available for betting")
                return None

            bet = exchange.place_bet(market_id, runner_id, bet_type, odds, stake)

            if bet:
                # Fill in additional details
                bet.horse_name = horse_name
                bet.strategy_type = strategy_type
                bet.race_id = race_id

                logger.info(f"Bet placed: {horse_name} - £{stake} @ {odds}")

            return bet

        except Exception as e:
            logger.error(f"Error placing single bet: {e}")
            return None

    def _check_risk_limits(self, stake_amount: float) -> bool:
        """Check if bet is within risk limits"""
        # Check daily stake limit
        if self.daily_stake_used + stake_amount > self.max_daily_stake:
            logger.warning(
                f"Daily stake limit exceeded: {self.daily_stake_used + stake_amount} > {self.max_daily_stake}"
            )
            return False

        # Check single stake limit
        if stake_amount > self.max_single_stake:
            logger.warning(
                f"Single stake limit exceeded: {stake_amount} > {self.max_single_stake}"
            )
            return False

        return True

    def _check_balance(self, required_amount: float) -> bool:
        """Check if sufficient balance is available"""
        try:
            exchange = self.exchanges.get("betfair")
            if not exchange:
                return False

            balance = exchange.get_account_balance()
            if balance and balance.available_balance >= required_amount:
                return True

            logger.warning(
                f"Insufficient balance: {balance.available_balance if balance else 0} < {required_amount}"
            )
            return False

        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return False

    def _calculate_potential_profit(self, bets: List[BetPlacement]) -> float:
        """Calculate potential profit from bets"""
        max_profit = 0.0

        for bet in bets:
            if bet.bet_type == "BACK":
                profit = (bet.odds - 1) * bet.stake
                if profit > max_profit:
                    max_profit = profit

        return max_profit

    def cancel_strategy_bets(self, market_id: str) -> bool:
        """Cancel all bets for a market"""
        try:
            position = self.positions.get(market_id)
            if not position:
                return False

            exchange = self.exchanges.get("betfair")
            if not exchange:
                return False

            cancelled_count = 0
            for bet in position.bets:
                if bet.status in ["PENDING", "UNMATCHED"]:
                    if exchange.cancel_bet(market_id, bet.bet_id):
                        bet.status = "CANCELLED"
                        cancelled_count += 1

            if cancelled_count > 0:
                position.status = "CANCELLED"
                logger.info(f"Cancelled {cancelled_count} bets for market {market_id}")

            return cancelled_count > 0

        except Exception as e:
            logger.error(f"Error cancelling strategy bets: {e}")
            return False

    def update_bet_status(self, market_id: str = None):
        """Update status of active bets"""
        try:
            exchange = self.exchanges.get("betfair")
            if not exchange:
                return

            current_orders = exchange.get_current_orders(market_id)

            # Update active bets
            for bet_id, bet in self.active_bets.items():
                # Find matching order
                matching_order = next(
                    (order for order in current_orders if order.bet_id == bet_id), None
                )

                if matching_order:
                    bet.status = matching_order.status
                    bet.matched_amount = matching_order.matched_amount
                elif bet.status == "PENDING":
                    # Bet not found in current orders, likely matched
                    bet.status = "MATCHED"

            logger.debug(f"Updated status for {len(self.active_bets)} active bets")

        except Exception as e:
            logger.error(f"Error updating bet status: {e}")

    def get_position_summary(self) -> Dict[str, Any]:
        """Get summary of all positions"""
        summary = {
            "total_positions": len(self.positions),
            "total_stake": sum(pos.total_stake for pos in self.positions.values()),
            "potential_profit": sum(
                pos.potential_profit for pos in self.positions.values()
            ),
            "potential_loss": sum(
                pos.potential_loss for pos in self.positions.values()
            ),
            "daily_stake_used": self.daily_stake_used,
            "daily_stake_remaining": self.max_daily_stake - self.daily_stake_used,
            "positions": [],
        }

        for position in self.positions.values():
            pos_summary = {
                "market_id": position.market_id,
                "race_id": position.race_id,
                "strategy_type": position.strategy_type,
                "total_stake": position.total_stake,
                "potential_profit": position.potential_profit,
                "status": position.status,
                "bets_count": len(position.bets),
            }
            summary["positions"].append(pos_summary)

        return summary

    def get_balance_info(self) -> Optional[ExchangeBalance]:
        """Get current balance information"""
        try:
            exchange = self.exchanges.get("betfair")
            if exchange:
                return exchange.get_account_balance()
            return None
        except Exception as e:
            logger.error(f"Error getting balance info: {e}")
            return None


# Configuration file creation
def create_betting_exchange_config():
    """Create example betting exchange configuration"""
    config = {
        "exchanges": {
            "betfair": {
                "enabled": True,
                "app_key": "YOUR_BETFAIR_APP_KEY",
                "username": "YOUR_BETFAIR_USERNAME",
                "password": "YOUR_BETFAIR_PASSWORD",
                "commission_rate": 0.05,
                "delay_factor": 1.0,
            },
            "smarkets": {
                "enabled": False,
                "api_token": "YOUR_SMARKETS_TOKEN",
                "commission_rate": 0.02,
            },
        },
        "risk_management": {
            "max_daily_stake": 200.0,
            "max_single_stake": 50.0,
            "max_exposure": 500.0,
            "stop_loss_percentage": 20.0,
            "max_consecutive_losses": 5,
            "min_balance_threshold": 100.0,
        },
        "strategy_settings": {
            "80/20": {"max_odds": 10.0, "min_odds": 2.0, "default_stake": 15.0},
            "dutching": {
                "max_selections": 4,
                "min_total_probability": 0.7,
                "default_total_stake": 25.0,
            },
        },
    }

    config_path = "config/betting_exchange_config.json"
    os.makedirs("config", exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"Created betting exchange config: {config_path}")
    return config_path


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)

    # Create config if not exists
    create_betting_exchange_config()

    # Initialize integrator
    integrator = BettingExchangeIntegrator()

    # Example strategy bet placement
    selections = [
        {"runner_id": "12345", "horse_name": "Test Horse", "odds": 4.5, "stake": 15.0}
    ]

    # This would place actual bets in production
    print("Betting exchange integrator initialized")
    print(f"Daily stake limit: £{integrator.max_daily_stake}")
    print(f"Single stake limit: £{integrator.max_single_stake}")

    # Get balance info
    balance = integrator.get_balance_info()
    if balance:
        print(f"Available balance: £{balance.available_balance}")
    else:
        print("Balance information not available (demo mode)")
