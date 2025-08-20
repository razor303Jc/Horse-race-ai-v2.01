"""
BetDaq Betting Exchange API Integration

This module handles all interactions with the BetDaq betting exchange API,
including market data retrieval, odds analysis, and bet placement.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum

import httpx
from pydantic import BaseModel, Field

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BetType(Enum):
    """Bet types supported by BetDaq."""
    BACK = "B"
    LAY = "L"


class BetStatus(Enum):
    """Bet status values."""
    MATCHED = "M"
    UNMATCHED = "U"
    CANCELLED = "C"
    SETTLED = "S"


class MarketStatus(Enum):
    """Market status values."""
    ACTIVE = "A"
    SUSPENDED = "S"
    CLOSED = "C"
    SETTLED = "T"


class BetDaqCredentials(BaseModel):
    """BetDaq API credentials."""
    username: str
    password: str
    api_key: str
    base_url: str = "https://api.betdaq.com/v2.0"


class MarketSelection(BaseModel):
    """A selection within a betting market."""
    selection_id: int
    selection_name: str
    back_price: Optional[Decimal] = None
    lay_price: Optional[Decimal] = None
    back_size: Optional[Decimal] = None
    lay_size: Optional[Decimal] = None
    last_traded_price: Optional[Decimal] = None
    total_matched: Optional[Decimal] = None
    withdrawal_factor: Optional[Decimal] = None
    status: str = "ACTIVE"


class BettingMarket(BaseModel):
    """A betting market from BetDaq."""
    market_id: int
    market_name: str
    event_id: int
    event_name: str
    start_time: datetime
    market_type: str
    status: MarketStatus
    in_play: bool = False
    selections: List[MarketSelection] = Field(default_factory=list)
    total_matched: Optional[Decimal] = None
    market_commission: Optional[Decimal] = None


class BetRequest(BaseModel):
    """A bet placement request."""
    market_id: int
    selection_id: int
    bet_type: BetType
    price: Decimal
    stake: Decimal
    expected_price: Optional[Decimal] = None  # For price protection
    fill_or_kill: bool = False  # All or nothing bet


class PlacedBet(BaseModel):
    """A placed bet response."""
    bet_id: int
    market_id: int
    selection_id: int
    bet_type: BetType
    price: Decimal
    stake: Decimal
    matched_stake: Decimal
    remaining_stake: Decimal
    status: BetStatus
    placed_time: datetime
    average_price_matched: Optional[Decimal] = None


class BetDaqClient:
    """
    BetDaq betting exchange API client.
    
    Handles authentication, market data retrieval, and bet placement.
    """
    
    def __init__(self):
        self.base_url = settings.betdaq_api_url
        self.username = settings.betdaq_username
        self.password = settings.betdaq_password
        self.api_key = settings.betdaq_api_key
        self.session_token: Optional[str] = None
        self.session: Optional[httpx.AsyncClient] = None
        self.session_expires: Optional[datetime] = None
        
        # Rate limiting
        self.last_request_time = datetime.now()
        self.min_request_interval = timedelta(milliseconds=200)  # 5 requests per second max
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Initialize HTTP session and authenticate."""
        if self.session is None:
            timeout = httpx.Timeout(30.0, connect=10.0)
            self.session = httpx.AsyncClient(
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-API-Key": self.api_key,
                }
            )
        
        await self._authenticate()
    
    async def disconnect(self) -> None:
        """Close HTTP session and logout."""
        if self.session_token:
            try:
                await self._logout()
            except Exception as e:
                logger.warning(f"Error during logout: {e}")
        
        if self.session:
            await self.session.aclose()
            self.session = None
            self.session_token = None
    
    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        now = datetime.now()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = (self.min_request_interval - time_since_last).total_seconds()
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.now()
    
    async def _authenticate(self) -> None:
        """Authenticate with BetDaq API."""
        if not self.username or not self.password or not self.api_key:
            raise ValueError("BetDaq credentials not configured")
        
        # Check if we have a valid session
        if self.session_token and self.session_expires and datetime.now() < self.session_expires:
            return
        
        try:
            await self._rate_limit()
            
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = await self.session.post(
                f"{self.base_url}/auth/login",
                json=auth_data
            )
            response.raise_for_status()
            
            result = response.json()
            self.session_token = result.get("session_token")
            
            # BetDaq sessions typically last 8 hours
            self.session_expires = datetime.now() + timedelta(hours=7, minutes=45)
            
            logger.info("Successfully authenticated with BetDaq")
            
        except Exception as e:
            logger.error(f"BetDaq authentication failed: {e}")
            raise
    
    async def _logout(self) -> None:
        """Logout from BetDaq API."""
        if not self.session_token:
            return
        
        try:
            await self._rate_limit()
            
            response = await self.session.post(
                f"{self.base_url}/auth/logout",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            response.raise_for_status()
            
            self.session_token = None
            self.session_expires = None
            
            logger.info("Successfully logged out from BetDaq")
            
        except Exception as e:
            logger.error(f"BetDaq logout failed: {e}")
            raise
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request."""
        if not self.session:
            await self.connect()
        
        # Ensure we're authenticated
        await self._authenticate()
        
        await self._rate_limit()
        
        headers = kwargs.pop("headers", {})
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        try:
            response = await self.session.request(
                method,
                f"{self.base_url}/{endpoint}",
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            
            logger.debug(f"BetDaq API request: {method} /{endpoint} -> {response.status_code}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"BetDaq API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"BetDaq API request error: {e}")
            raise
    
    async def get_markets(self, event_type: str = "horse_racing") -> List[BettingMarket]:
        """
        Get available betting markets for horse racing.
        """
        try:
            params = {
                "eventTypeId": 7,  # Horse Racing event type ID
                "marketTypeCodes": ["WIN", "PLACE"],  # Win and Place markets
                "maxResults": 100
            }
            
            result = await self._make_request("GET", "markets", params=params)
            
            markets = []
            for market_data in result.get("markets", []):
                market = BettingMarket(
                    market_id=market_data["marketId"],
                    market_name=market_data["marketName"],
                    event_id=market_data["eventId"],
                    event_name=market_data["eventName"],
                    start_time=datetime.fromisoformat(market_data["startTime"]),
                    market_type=market_data["marketType"],
                    status=MarketStatus(market_data["status"]),
                    in_play=market_data.get("inPlay", False),
                    total_matched=market_data.get("totalMatched"),
                    market_commission=market_data.get("marketCommission")
                )
                markets.append(market)
            
            logger.info(f"Retrieved {len(markets)} markets from BetDaq")
            return markets
            
        except Exception as e:
            logger.error(f"Failed to get markets: {e}")
            return []
    
    async def get_market_prices(self, market_id: int) -> Optional[BettingMarket]:
        """
        Get current prices for a specific market.
        """
        try:
            result = await self._make_request("GET", f"markets/{market_id}/prices")
            
            market_data = result.get("market")
            if not market_data:
                return None
            
            # Parse selections with current prices
            selections = []
            for sel_data in market_data.get("selections", []):
                selection = MarketSelection(
                    selection_id=sel_data["selectionId"],
                    selection_name=sel_data["selectionName"],
                    back_price=sel_data.get("backPrice"),
                    lay_price=sel_data.get("layPrice"),
                    back_size=sel_data.get("backSize"),
                    lay_size=sel_data.get("laySize"),
                    last_traded_price=sel_data.get("lastTradedPrice"),
                    total_matched=sel_data.get("totalMatched"),
                    withdrawal_factor=sel_data.get("withdrawalFactor"),
                    status=sel_data.get("status", "ACTIVE")
                )
                selections.append(selection)
            
            market = BettingMarket(
                market_id=market_data["marketId"],
                market_name=market_data["marketName"],
                event_id=market_data["eventId"],
                event_name=market_data["eventName"],
                start_time=datetime.fromisoformat(market_data["startTime"]),
                market_type=market_data["marketType"],
                status=MarketStatus(market_data["status"]),
                in_play=market_data.get("inPlay", False),
                selections=selections,
                total_matched=market_data.get("totalMatched"),
                market_commission=market_data.get("marketCommission")
            )
            
            return market
            
        except Exception as e:
            logger.error(f"Failed to get market prices for {market_id}: {e}")
            return None
    
    async def place_bet(self, bet_request: BetRequest) -> Optional[PlacedBet]:
        """
        Place a bet on BetDaq.
        """
        try:
            bet_data = {
                "marketId": bet_request.market_id,
                "selectionId": bet_request.selection_id,
                "betType": bet_request.bet_type.value,
                "price": float(bet_request.price),
                "stake": float(bet_request.stake),
                "fillOrKill": bet_request.fill_or_kill
            }
            
            if bet_request.expected_price:
                bet_data["expectedPrice"] = float(bet_request.expected_price)
            
            result = await self._make_request("POST", "bets/place", json=bet_data)
            
            bet_data = result.get("bet")
            if not bet_data:
                logger.error("No bet data in response")
                return None
            
            placed_bet = PlacedBet(
                bet_id=bet_data["betId"],
                market_id=bet_data["marketId"],
                selection_id=bet_data["selectionId"],
                bet_type=BetType(bet_data["betType"]),
                price=Decimal(str(bet_data["price"])),
                stake=Decimal(str(bet_data["stake"])),
                matched_stake=Decimal(str(bet_data.get("matchedStake", 0))),
                remaining_stake=Decimal(str(bet_data.get("remainingStake", bet_data["stake"]))),
                status=BetStatus(bet_data["status"]),
                placed_time=datetime.fromisoformat(bet_data["placedTime"]),
                average_price_matched=bet_data.get("averagePriceMatched")
            )
            
            logger.info(f"Placed bet: {placed_bet.bet_id} - {bet_request.bet_type.value} "
                       f"£{bet_request.stake} @ {bet_request.price}")
            return placed_bet
            
        except Exception as e:
            logger.error(f"Failed to place bet: {e}")
            return None
    
    async def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance and exposure."""
        try:
            result = await self._make_request("GET", "account/balance")
            
            return {
                "available_balance": result.get("availableBalance"),
                "exposure": result.get("exposure"),
                "currency": result.get("currency", "GBP")
            }
            
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return None
    
    async def get_bet_history(self, from_date: Optional[datetime] = None) -> List[PlacedBet]:
        """Get betting history."""
        try:
            params = {}
            if from_date:
                params["fromDate"] = from_date.isoformat()
            
            result = await self._make_request("GET", "bets/history", params=params)
            
            bets = []
            for bet_data in result.get("bets", []):
                bet = PlacedBet(
                    bet_id=bet_data["betId"],
                    market_id=bet_data["marketId"],
                    selection_id=bet_data["selectionId"],
                    bet_type=BetType(bet_data["betType"]),
                    price=Decimal(str(bet_data["price"])),
                    stake=Decimal(str(bet_data["stake"])),
                    matched_stake=Decimal(str(bet_data.get("matchedStake", 0))),
                    remaining_stake=Decimal(str(bet_data.get("remainingStake", 0))),
                    status=BetStatus(bet_data["status"]),
                    placed_time=datetime.fromisoformat(bet_data["placedTime"]),
                    average_price_matched=bet_data.get("averagePriceMatched")
                )
                bets.append(bet)
            
            return bets
            
        except Exception as e:
            logger.error(f"Failed to get bet history: {e}")
            return []
    
    async def cancel_bet(self, bet_id: int) -> bool:
        """Cancel an unmatched bet."""
        try:
            result = await self._make_request("POST", f"bets/{bet_id}/cancel")
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to cancel bet {bet_id}: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if BetDaq API is accessible."""
        try:
            if not self.session:
                await self.connect()
            
            # Simple API call to check connectivity
            await self._make_request("GET", "account/balance")
            return True
            
        except Exception as e:
            logger.error(f"BetDaq health check failed: {e}")
            return False


# Global client instance
_betdaq_client: Optional[BetDaqClient] = None


async def get_betdaq_client() -> BetDaqClient:
    """Get or create the global BetDaq client."""
    global _betdaq_client
    
    if _betdaq_client is None:
        _betdaq_client = BetDaqClient()
        await _betdaq_client.connect()
    
    return _betdaq_client


async def close_betdaq_client() -> None:
    """Close the global BetDaq client."""
    global _betdaq_client
    
    if _betdaq_client:
        await _betdaq_client.disconnect()
        _betdaq_client = None
