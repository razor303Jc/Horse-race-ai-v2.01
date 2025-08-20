"""
Automated Betting Strategy Service

This service implements intelligent betting strategies using AI predictions
and BetDaq market analysis for the Horse Race Handicapping AI.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field
from .betdaq_client import (
    get_betdaq_client, BetRequest, BetType, BettingMarket, 
    MarketSelection, PlacedBet, MarketStatus
)
from .data_provider import get_data_provider
from .simulated_providers import get_simulated_data_provider, get_simulated_betdaq_client
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BettingStrategy(Enum):
    """Available betting strategies."""
    VALUE_BETTING = "value"          # Bet when odds exceed calculated probability
    ARBITRAGE = "arbitrage"          # Risk-free betting across markets
    MATCHED_BETTING = "matched"      # Back and lay strategy
    AI_PREDICTIONS = "ai_predictions" # Use ML model predictions
    CONSERVATIVE = "conservative"    # Low-risk betting
    AGGRESSIVE = "aggressive"        # High-risk, high-reward


class RiskLevel(Enum):
    """Risk tolerance levels."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class BettingConfiguration(BaseModel):
    """Betting configuration settings."""
    strategy: BettingStrategy
    risk_level: RiskLevel
    max_stake_per_bet: Decimal
    max_total_exposure: Decimal
    min_odds: Decimal = Decimal("1.5")
    max_odds: Decimal = Decimal("10.0")
    min_value_threshold: Decimal = Decimal("0.05")  # 5% value required
    max_bets_per_race: int = 2
    max_daily_loss: Decimal
    stop_loss_threshold: Decimal = Decimal("0.8")  # Stop at 80% of daily limit
    simulation_mode: bool = True  # Use simulated data by default


class BettingOpportunity(BaseModel):
    """A betting opportunity identified by the strategy."""
    race_id: str
    horse_name: str
    market_id: int
    selection_id: int
    recommended_bet_type: BetType
    recommended_odds: Decimal
    recommended_stake: Decimal
    confidence_score: float  # 0-1
    value_percentage: float
    reasoning: str
    ai_prediction_probability: Optional[float] = None
    market_probability: Optional[float] = None


class BettingSession(BaseModel):
    """A betting session record."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    strategy: BettingStrategy
    total_stakes: Decimal = Decimal("0")
    total_winnings: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")
    bets_placed: List[PlacedBet] = Field(default_factory=list)
    opportunities_identified: int = 0
    opportunities_taken: int = 0
    success_rate: float = 0.0


class BettingEngine:
    """
    Core betting engine that analyzes markets and executes betting strategies.
    """
    
    def __init__(self, config: BettingConfiguration):
        self.config = config
        self.daily_loss = Decimal("0")
        self.daily_stakes = Decimal("0")
        self.active_exposure = Decimal("0")
        self.current_session: Optional[BettingSession] = None
        
        # Performance tracking
        self.total_bets = 0
        self.winning_bets = 0
        self.total_profit = Decimal("0")
        
    async def start_session(self) -> str:
        """Start a new betting session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = BettingSession(
            session_id=session_id,
            start_time=datetime.now(),
            strategy=self.config.strategy
        )
        
        logger.info(f"Started betting session: {session_id} with strategy: {self.config.strategy.value}")
        return session_id
    
    async def end_session(self) -> Optional[BettingSession]:
        """End the current betting session."""
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.net_profit = self.current_session.total_winnings - self.current_session.total_stakes
        
        if self.current_session.opportunities_identified > 0:
            self.current_session.success_rate = (
                self.current_session.opportunities_taken / self.current_session.opportunities_identified
            )
        
        logger.info(f"Ended betting session: {self.current_session.session_id}")
        logger.info(f"Net profit: £{self.current_session.net_profit}")
        
        session = self.current_session
        self.current_session = None
        return session
    
    async def analyze_markets(self) -> List[BettingOpportunity]:
        """
        Analyze current markets for betting opportunities.
        """
        opportunities = []
        
        try:
            # Get client and data provider (simulated or real)
            if self.config.simulation_mode:
                betdaq = get_simulated_betdaq_client()
                data_provider = get_simulated_data_provider()
                logger.info("Using simulated providers for market analysis")
            else:
                betdaq = await get_betdaq_client()
                data_provider = get_data_provider()
                logger.info("Using real providers for market analysis")
            
            # Get available markets
            markets = await betdaq.get_markets("horse_racing")
            logger.info(f"Analyzing {len(markets)} markets for opportunities")
            
            for market in markets:
                # Skip if market is not active or too close to start
                if hasattr(market, 'status') and market.status != MarketStatus.ACTIVE:
                    continue
                elif isinstance(market, dict) and market.get('status', '').upper() != 'ACTIVE':
                    continue
                
                start_time = market.start_time if hasattr(market, 'start_time') else datetime.fromisoformat(market['start_time'])
                time_to_start = (start_time - datetime.now()).total_seconds()
                if time_to_start < 300:  # Skip if less than 5 minutes to start
                    continue
                
                # Get detailed prices for this market
                market_id = market.market_id if hasattr(market, 'market_id') else market['market_id']
                market_prices = await betdaq.get_market_prices(market_id)
                if not market_prices:
                    continue
                
                # Get race data from our data provider
                event_name = market.event_name if hasattr(market, 'event_name') else market['event_name']
                race_data = await self._get_race_data(event_name, start_time, data_provider)
                
                # Analyze each selection in the market
                selections = market_prices.get('selections', []) if isinstance(market_prices, dict) else market_prices.selections
                for selection in selections:
                    opportunity = await self._analyze_selection(
                        market_prices, selection, race_data
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        if self.current_session:
                            self.current_session.opportunities_identified += 1
            
            # Sort opportunities by confidence score
            opportunities.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"Found {len(opportunities)} betting opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing markets: {e}")
            return []
    
    async def _get_race_data(self, event_name: str, start_time: datetime, data_provider=None) -> Optional[Dict[str, Any]]:
        """Get race data from our data provider."""
        try:
            if data_provider is None:
                if self.config.simulation_mode:
                    data_provider = get_simulated_data_provider()
                else:
                    data_provider = get_data_provider()
            
            # Try to match the market to our race data
            date_str = start_time.strftime("%Y-%m-%d")
            races = await data_provider.get_races_by_date(date_str)
            
            # Find matching race by name and time
            for race in races:
                if event_name.lower() in race.get("track_name", "").lower():
                    return race
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting race data: {e}")
            return None
    
    async def _analyze_selection(
        self, 
        market: Any,  # Can be BettingMarket or dict
        selection: Any,  # Can be MarketSelection or dict
        race_data: Optional[Dict[str, Any]]
    ) -> Optional[BettingOpportunity]:
        """
        Analyze a specific selection for betting value.
        """
        try:
            # Handle both object and dict formats
            if isinstance(selection, dict):
                selection_id = selection.get("selection_id")
                selection_name = selection.get("selection_name")
                back_price = Decimal(str(selection.get("back_price", 0)))
            else:
                selection_id = selection.selection_id
                selection_name = selection.selection_name
                back_price = selection.back_price
            
            # Skip if no back price available
            if not back_price or back_price <= 0:
                return None
            
            # Calculate market implied probability
            market_probability = 1.0 / float(back_price)
            
            # Get AI prediction if we have race data
            ai_probability = None
            if race_data and self.config.strategy == BettingStrategy.AI_PREDICTIONS:
                ai_probability = await self._get_ai_prediction(race_data, selection_name)
            
            # Extract market info
            if isinstance(market, dict):
                market_id = market.get("market_id")
                event_id = market.get("event_id", market_id)
            else:
                market_id = market.market_id
                event_id = market.event_id
            
            # Apply strategy-specific analysis
            if self.config.strategy == BettingStrategy.VALUE_BETTING:
                return await self._value_betting_analysis(
                    market_id, event_id, selection_id, selection_name, back_price,
                    market_probability, ai_probability, race_data
                )
            
            elif self.config.strategy == BettingStrategy.AI_PREDICTIONS and ai_probability:
                return await self._ai_prediction_analysis(
                    market_id, event_id, selection_id, selection_name, back_price,
                    market_probability, ai_probability, race_data
                )
            
            elif self.config.strategy == BettingStrategy.CONSERVATIVE:
                return await self._conservative_analysis(
                    market_id, event_id, selection_id, selection_name, back_price,
                    market_probability, race_data
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing selection: {e}")
            return None
    
    async def _get_ai_prediction(self, race_data: Dict[str, Any], horse_name: str) -> Optional[float]:
        """
        Get AI prediction probability for a horse.
        TODO: Integrate with ML prediction service when implemented.
        """
        # Placeholder - will integrate with ML service
        # For now, use simple form-based probability
        
        try:
            horses = race_data.get("horses", [])
            for horse in horses:
                if horse.get("name", "").lower() == horse_name.lower():
                    # Simple form analysis - this will be replaced with ML
                    form = horse.get("form", "")
                    if form:
                        recent_form = form[:3]  # Last 3 runs
                        wins = recent_form.count("1")
                        places = recent_form.count("2") + recent_form.count("3")
                        
                        # Basic probability based on recent form
                        if wins >= 2:
                            return 0.3  # 30% chance
                        elif wins >= 1:
                            return 0.2  # 20% chance
                        elif places >= 2:
                            return 0.15  # 15% chance
                        else:
                            return 0.1  # 10% chance
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting AI prediction: {e}")
            return None
    
    async def _value_betting_analysis(
        self,
        market_id: str,
        event_id: str,
        selection_id: int,
        selection_name: str,
        back_price: Decimal,
        market_probability: float,
        ai_probability: Optional[float],
        race_data: Optional[Dict[str, Any]]
    ) -> Optional[BettingOpportunity]:
        """Analyze for value betting opportunities."""
        
        # Use AI probability if available, otherwise use form analysis
        estimated_probability = ai_probability or await self._estimate_probability(selection_name, race_data)
        
        if not estimated_probability:
            return None
        
        # Calculate value
        value = (estimated_probability * float(back_price)) - 1.0
        value_percentage = value * 100
        
        # Check if this meets our value threshold
        if value < float(self.config.min_value_threshold):
            return None
        
        # Check odds are within our range
        if back_price < self.config.min_odds or back_price > self.config.max_odds:
            return None
        
        # Calculate stake using Kelly Criterion (modified for safety)
        kelly_fraction = value / (float(back_price) - 1.0)
        safe_kelly = kelly_fraction * 0.25  # Use 25% of Kelly for safety
        
        # Calculate recommended stake
        recommended_stake = min(
            self.config.max_stake_per_bet,
            self.config.max_total_exposure * Decimal(str(safe_kelly))
        )
        
        if recommended_stake < Decimal("1.0"):  # Minimum £1 bet
            return None
        
        confidence_score = min(value * 2, 1.0)  # Cap at 1.0
        
        return BettingOpportunity(
            race_id=f"{event_id}",
            horse_name=selection_name,
            market_id=int(market_id.split('_')[-1]) if market_id.startswith('sim_') else int(market_id),
            selection_id=selection_id,
            recommended_bet_type=BetType.BACK,
            recommended_odds=back_price,
            recommended_stake=recommended_stake,
            confidence_score=confidence_score,
            value_percentage=value_percentage,
            reasoning=f"Value bet: {value_percentage:.1f}% value identified",
            ai_prediction_probability=ai_probability,
            market_probability=market_probability
        )
    
    async def _ai_prediction_analysis(
        self,
        market: BettingMarket,
        selection: MarketSelection,
        market_probability: float,
        ai_probability: float,
        race_data: Optional[Dict[str, Any]]
    ) -> Optional[BettingOpportunity]:
        """Analyze using AI predictions."""
        
        # Only bet if AI probability significantly exceeds market probability
        probability_edge = ai_probability - market_probability
        
        if probability_edge < 0.05:  # Need at least 5% edge
            return None
        
        # Check odds constraints
        if selection.back_price < self.config.min_odds or selection.back_price > self.config.max_odds:
            return None
        
        # Calculate stake based on edge and confidence
        edge_percentage = probability_edge / market_probability
        stake_multiplier = min(edge_percentage, 0.5)  # Cap at 50% of max stake
        
        recommended_stake = self.config.max_stake_per_bet * Decimal(str(stake_multiplier))
        
        if recommended_stake < Decimal("1.0"):
            return None
        
        confidence_score = min(probability_edge * 10, 1.0)
        
        return BettingOpportunity(
            race_id=f"{market.event_id}",
            horse_name=selection.selection_name,
            market_id=market.market_id,
            selection_id=selection.selection_id,
            recommended_bet_type=BetType.BACK,
            recommended_odds=selection.back_price,
            recommended_stake=recommended_stake,
            confidence_score=confidence_score,
            value_percentage=(probability_edge * 100),
            reasoning=f"AI prediction: {ai_probability:.1%} vs market {market_probability:.1%}",
            ai_prediction_probability=ai_probability,
            market_probability=market_probability
        )
    
    async def _conservative_analysis(
        self,
        market: BettingMarket,
        selection: MarketSelection,
        market_probability: float,
        race_data: Optional[Dict[str, Any]]
    ) -> Optional[BettingOpportunity]:
        """Conservative betting analysis - only bet on strong favorites with good form."""
        
        # Only bet on favorites (odds < 3.0)
        if selection.back_price > Decimal("3.0"):
            return None
        
        # Check if horse has good recent form
        if not race_data:
            return None
        
        horses = race_data.get("horses", [])
        for horse in horses:
            if horse.get("name", "").lower() == selection.selection_name.lower():
                form = horse.get("form", "")
                if len(form) >= 3:
                    recent_form = form[:3]
                    # Only bet if horse has won recently or has strong form
                    if recent_form.count("1") >= 1 and recent_form.count("1") + recent_form.count("2") >= 2:
                        
                        # Small, conservative stake
                        recommended_stake = min(
                            Decimal("10.0"),  # Max £10 for conservative bets
                            self.config.max_stake_per_bet * Decimal("0.3")
                        )
                        
                        if recommended_stake < Decimal("1.0"):
                            return None
                        
                        return BettingOpportunity(
                            race_id=f"{market.event_id}",
                            horse_name=selection.selection_name,
                            market_id=market.market_id,
                            selection_id=selection.selection_id,
                            recommended_bet_type=BetType.BACK,
                            recommended_odds=selection.back_price,
                            recommended_stake=recommended_stake,
                            confidence_score=0.7,
                            value_percentage=5.0,  # Conservative estimate
                            reasoning=f"Conservative bet on favorite with good form: {form[:3]}",
                            market_probability=market_probability
                        )
        
        return None
    
    async def _estimate_probability(self, selection_name: str, race_data: Optional[Dict[str, Any]]) -> Optional[float]:
        """
        Estimate win probability based on available data.
        This is a placeholder - will be replaced with ML predictions.
        """
        if not race_data:
            return None
        
        try:
            horses = race_data.get("horses", [])
            total_horses = len(horses)
            
            for horse in horses:
                if horse.get("name", "").lower() == selection_name.lower():
                    # Simple probability estimation based on form and stats
                    base_probability = 1.0 / total_horses  # Equal probability base
                    
                    # Adjust based on form
                    form = horse.get("form", "")
                    if form:
                        recent_wins = form[:5].count("1")
                        recent_places = form[:5].count("2") + form[:5].count("3")
                        
                        # Boost probability for good form
                        form_multiplier = 1.0 + (recent_wins * 0.5) + (recent_places * 0.2)
                        base_probability *= form_multiplier
                    
                    # Adjust based on jockey/trainer (simplified)
                    jockey = horse.get("jockey", "")
                    if "Dettori" in jockey or "Moore" in jockey:  # Top jockeys
                        base_probability *= 1.2
                    
                    return min(base_probability, 0.5)  # Cap at 50%
            
            return None
            
        except Exception as e:
            logger.error(f"Error estimating probability: {e}")
            return None
    
    async def execute_opportunity(self, opportunity: BettingOpportunity) -> Optional[PlacedBet]:
        """
        Execute a betting opportunity.
        """
        try:
            # Check risk management constraints
            if not await self._check_risk_constraints(opportunity):
                logger.warning(f"Risk constraints failed for {opportunity.horse_name}")
                return None
            
            # Create bet request
            bet_request = {
                "market_id": str(opportunity.market_id),
                "selection_id": opportunity.selection_id,
                "bet_type": opportunity.recommended_bet_type.value if hasattr(opportunity.recommended_bet_type, 'value') else str(opportunity.recommended_bet_type),
                "price": float(opportunity.recommended_odds),
                "stake": float(opportunity.recommended_stake),
                "expected_price": float(opportunity.recommended_odds * Decimal("0.95"))  # 5% price protection
            }
            
            # Place the bet using appropriate client
            if self.config.simulation_mode:
                betdaq = get_simulated_betdaq_client()
            else:
                betdaq = await get_betdaq_client()
            
            placed_bet_dict = await betdaq.place_bet(bet_request)
            
            if placed_bet_dict and "error" not in placed_bet_dict:
                # Convert to PlacedBet object for compatibility
                placed_bet = PlacedBet(
                    bet_id=placed_bet_dict["bet_id"],
                    market_id=int(placed_bet_dict["market_id"]),
                    selection_id=placed_bet_dict["selection_id"],
                    bet_type=BetType(placed_bet_dict["bet_type"]),
                    requested_odds=Decimal(str(placed_bet_dict["requested_odds"])),
                    matched_odds=Decimal(str(placed_bet_dict["matched_odds"])),
                    stake=Decimal(str(placed_bet_dict["matched_stake"])),
                    remaining_stake=Decimal("0"),  # Assume fully matched for simplicity
                    potential_profit=Decimal(str(placed_bet_dict.get("potential_profit", 0))),
                    status="MATCHED",
                    timestamp=datetime.now()
                )
                
                # Update session tracking
                if self.current_session:
                    self.current_session.bets_placed.append(placed_bet)
                    self.current_session.total_stakes += placed_bet.stake
                    self.current_session.opportunities_taken += 1
                
                # Update daily tracking
                self.daily_stakes += placed_bet.stake
                self.active_exposure += placed_bet.stake
                
                logger.info(f"Successfully placed bet: {placed_bet.bet_id} on {opportunity.horse_name}")
                return placed_bet
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing opportunity for {opportunity.horse_name}: {e}")
            return None
    
    async def _check_risk_constraints(self, opportunity: BettingOpportunity) -> bool:
        """Check if the opportunity meets risk management constraints."""
        
        # Check daily loss limit
        if self.daily_loss >= self.config.max_daily_loss * self.config.stop_loss_threshold:
            logger.warning("Daily stop-loss threshold reached")
            return False
        
        # Check total exposure
        if self.active_exposure + opportunity.recommended_stake > self.config.max_total_exposure:
            logger.warning("Total exposure limit would be exceeded")
            return False
        
        # Check individual bet size
        if opportunity.recommended_stake > self.config.max_stake_per_bet:
            logger.warning("Stake exceeds maximum per bet")
            return False
        
        # Check odds range
        if (opportunity.recommended_odds < self.config.min_odds or 
            opportunity.recommended_odds > self.config.max_odds):
            logger.warning("Odds outside acceptable range")
            return False
        
        return True
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        
        win_rate = (self.winning_bets / self.total_bets * 100) if self.total_bets > 0 else 0
        
        return {
            "total_bets": self.total_bets,
            "winning_bets": self.winning_bets,
            "win_rate": win_rate,
            "total_profit": float(self.total_profit),
            "daily_stakes": float(self.daily_stakes),
            "daily_loss": float(self.daily_loss),
            "active_exposure": float(self.active_exposure),
            "current_session": self.current_session.dict() if self.current_session else None
        }


# Global betting engine instance
_betting_engine: Optional[BettingEngine] = None


def get_betting_engine(config: Optional[BettingConfiguration] = None) -> BettingEngine:
    """Get or create the global betting engine."""
    global _betting_engine
    
    if _betting_engine is None and config:
        _betting_engine = BettingEngine(config)
    
    return _betting_engine
