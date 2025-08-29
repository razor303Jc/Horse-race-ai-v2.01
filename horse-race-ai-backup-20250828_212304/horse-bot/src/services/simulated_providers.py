"""
Simulated Data Provider

Provides simulated race data and market information for testing
without requiring real API connections.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from .market_simulator import get_market_simulator, MarketSimulator
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SimulatedDataProvider:
    """
    Data provider that serves simulated race and market data
    compatible with the existing data provider interface.
    """
    
    def __init__(self):
        self.simulator: Optional[MarketSimulator] = None
        self._is_connected = False
    
    async def connect(self):
        """Initialize connection to simulator."""
        if not self._is_connected:
            self.simulator = await get_market_simulator()
            self._is_connected = True
            logger.info("Connected to market simulator")
    
    async def disconnect(self):
        """Disconnect from simulator."""
        self._is_connected = False
        logger.info("Disconnected from market simulator")
    
    async def get_races_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """Get races for a specific date from simulator."""
        
        await self.connect()
        
        try:
            # Parse date
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Get all available markets
            markets = await self.simulator.get_available_markets()
            
            # Filter markets for target date and convert to race format
            races = []
            for market_info in markets:
                market_start = datetime.fromisoformat(market_info["start_time"])
                
                if market_start.date() == target_date.date():
                    # Get detailed race data
                    race_data = await self.simulator.get_race_data(market_info["market_id"])
                    if race_data:
                        races.append(race_data)
            
            logger.info(f"Retrieved {len(races)} simulated races for {date_str}")
            return races
            
        except Exception as e:
            logger.error(f"Error getting races by date: {e}")
            return []
    
    async def get_today_races(self) -> List[Dict[str, Any]]:
        """Get today's races from simulator."""
        today = datetime.now().strftime("%Y-%m-%d")
        return await self.get_races_by_date(today)
    
    async def get_market_data(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed market data for a specific market."""
        
        await self.connect()
        
        try:
            market_prices = await self.simulator.get_market_prices(market_id)
            return market_prices
            
        except Exception as e:
            logger.error(f"Error getting market data for {market_id}: {e}")
            return None
    
    async def get_live_odds(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get live odds for a market (alias for get_market_data)."""
        return await self.get_market_data(market_id)
    
    async def search_markets(self, search_term: str) -> List[Dict[str, Any]]:
        """Search markets by name or track."""
        
        await self.connect()
        
        try:
            all_markets = await self.simulator.get_available_markets()
            
            # Filter markets by search term
            matching_markets = []
            for market in all_markets:
                if search_term.lower() in market["event_name"].lower():
                    matching_markets.append(market)
            
            return matching_markets
            
        except Exception as e:
            logger.error(f"Error searching markets: {e}")
            return []
    
    async def get_historical_results(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get historical race results (simulated)."""
        
        await self.connect()
        
        try:
            results = []
            
            # Generate historical results for last N days
            for day_offset in range(1, days_back + 1):
                result_date = datetime.now() - timedelta(days=day_offset)
                
                # Simulate 3-5 races per day
                num_races = 4
                for race_num in range(1, num_races + 1):
                    result = {
                        "date": result_date.strftime("%Y-%m-%d"),
                        "track": "Historical Track",
                        "race_number": race_num,
                        "winner": f"Historical Winner {race_num}",
                        "winning_odds": round(2.0 + (race_num * 0.5), 2),
                        "runners": race_num + 4  # 5-8 runners
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting historical results: {e}")
            return []


# BetDaq-compatible simulated client
class SimulatedBetDaqClient:
    """
    Simulated BetDaq client that provides the same interface
    as the real client but uses simulated data.
    """
    
    def __init__(self):
        self.simulator: Optional[MarketSimulator] = None
        self._is_connected = False
        self.placed_bets: List[Dict[str, Any]] = []
    
    async def connect(self):
        """Connect to simulator."""
        if not self._is_connected:
            self.simulator = await get_market_simulator()
            self._is_connected = True
            logger.info("Connected to simulated BetDaq")
    
    async def disconnect(self):
        """Disconnect from simulator."""
        self._is_connected = False
        logger.info("Disconnected from simulated BetDaq")
    
    async def get_markets(self, sport: str = "horse_racing") -> List[Dict[str, Any]]:
        """Get available markets."""
        
        await self.connect()
        
        try:
            markets = await self.simulator.get_available_markets()
            
            # Convert to BetDaq format
            betdaq_markets = []
            for market in markets:
                betdaq_markets.append({
                    "market_id": market["market_id"],
                    "event_id": f"event_{market['market_id']}",
                    "event_name": market["event_name"],
                    "start_time": datetime.fromisoformat(market["start_time"]),
                    "status": market["state"].upper(),
                    "market_type": "WIN",
                    "total_matched": market["total_matched"]
                })
            
            return betdaq_markets
            
        except Exception as e:
            logger.error(f"Error getting simulated markets: {e}")
            return []
    
    async def get_market_prices(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market prices."""
        
        await self.connect()
        
        try:
            return await self.simulator.get_market_prices(market_id)
            
        except Exception as e:
            logger.error(f"Error getting market prices: {e}")
            return None
    
    async def place_bet(self, bet_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Place a simulated bet."""
        
        await self.connect()
        
        try:
            # Extract bet details
            market_id = bet_request.get("market_id")
            selection_id = bet_request.get("selection_id")
            bet_type = bet_request.get("bet_type", "BACK")
            odds = Decimal(str(bet_request.get("price", 0)))
            stake = Decimal(str(bet_request.get("stake", 0)))
            
            # Place bet through simulator
            result = await self.simulator.place_simulated_bet(
                market_id, selection_id, bet_type, odds, stake
            )
            
            if "error" not in result:
                # Store bet for tracking
                self.placed_bets.append(result)
                logger.info(f"Simulated bet placed: {result['bet_id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error placing simulated bet: {e}")
            return {"error": str(e)}
    
    async def get_bet_status(self, bet_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a placed bet."""
        
        # Find bet in our placed bets
        for bet in self.placed_bets:
            if bet["bet_id"] == bet_id:
                # Check if market has been settled
                market_id = bet["market_id"]
                result = await self.simulator.get_settled_result(market_id)
                
                if result:
                    # Calculate settlement
                    selection_id = bet["selection_id"]
                    winning_selection_id = result["winning_selection_id"]
                    
                    if selection_id == winning_selection_id:
                        # Winning bet
                        profit = float(bet["potential_profit"])
                        bet.update({
                            "status": "WON",
                            "settlement": "WINNER",
                            "profit_loss": profit
                        })
                    else:
                        # Losing bet
                        bet.update({
                            "status": "LOST",
                            "settlement": "LOSER",
                            "profit_loss": -float(bet["matched_stake"])
                        })
                
                return bet
        
        return None
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get simulated account balance."""
        
        # Calculate P&L from placed bets
        total_stakes = sum(float(bet.get("matched_stake", 0)) for bet in self.placed_bets)
        total_winnings = sum(
            float(bet.get("profit_loss", 0)) 
            for bet in self.placed_bets 
            if bet.get("profit_loss", 0) > 0
        )
        
        return {
            "balance": 10000.0,  # Start with £10k simulation balance
            "available": 10000.0 - total_stakes,
            "total_stakes": total_stakes,
            "total_winnings": total_winnings,
            "profit_loss": total_winnings - total_stakes
        }


# Global instances
_simulated_data_provider: Optional[SimulatedDataProvider] = None
_simulated_betdaq_client: Optional[SimulatedBetDaqClient] = None


def get_simulated_data_provider() -> SimulatedDataProvider:
    """Get or create the global simulated data provider."""
    global _simulated_data_provider
    
    if _simulated_data_provider is None:
        _simulated_data_provider = SimulatedDataProvider()
    
    return _simulated_data_provider


def get_simulated_betdaq_client() -> SimulatedBetDaqClient:
    """Get or create the global simulated BetDaq client."""
    global _simulated_betdaq_client
    
    if _simulated_betdaq_client is None:
        _simulated_betdaq_client = SimulatedBetDaqClient()
    
    return _simulated_betdaq_client
