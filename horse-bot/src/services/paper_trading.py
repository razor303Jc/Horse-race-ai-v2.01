"""
Paper Trading Service

Simulates betting operations without real money for testing strategies
and validating the system before going live.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import uuid

from pydantic import BaseModel, Field
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PaperBetStatus(str, Enum):
    """Paper bet status enumeration."""
    PENDING = "pending"
    MATCHED = "matched"
    PARTIALLY_MATCHED = "partially_matched"
    CANCELLED = "cancelled"
    SETTLED = "settled"


class PaperBetType(str, Enum):
    """Paper bet type enumeration."""
    BACK = "back"
    LAY = "lay"


class PaperBet(BaseModel):
    """Paper trading bet model."""
    bet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    market_id: str
    selection_id: str
    selection_name: str
    bet_type: PaperBetType
    stake: Decimal
    odds: Decimal
    potential_profit: Decimal
    potential_liability: Decimal
    status: PaperBetStatus = PaperBetStatus.PENDING
    placed_at: datetime = Field(default_factory=datetime.now)
    matched_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    matched_amount: Decimal = Decimal('0')
    profit_loss: Optional[Decimal] = None
    strategy_name: Optional[str] = None
    confidence: Optional[float] = None


class PaperMarket(BaseModel):
    """Paper trading market model."""
    market_id: str
    event_name: str
    market_name: str
    start_time: datetime
    in_play: bool = False
    status: str = "OPEN"
    selections: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    winner: Optional[str] = None
    settled: bool = False


class PaperTradingSession(BaseModel):
    """Paper trading session model."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    starting_balance: Decimal
    current_balance: Decimal
    total_bets: int = 0
    winning_bets: int = 0
    losing_bets: int = 0
    total_profit_loss: Decimal = Decimal('0')
    strategy_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    active: bool = True


class PaperTradingEngine:
    """
    Paper trading engine for testing betting strategies without real money.
    """
    
    def __init__(self, starting_balance: Decimal = Decimal('1000')):
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.bets: Dict[str, PaperBet] = {}
        self.markets: Dict[str, PaperMarket] = {}
        self.sessions: Dict[str, PaperTradingSession] = {}
        self.current_session: Optional[PaperTradingSession] = None
        
        # Performance tracking
        self.daily_pnl: Dict[str, Decimal] = {}
        self.strategy_stats: Dict[str, Dict[str, Any]] = {}
        
    def start_session(self, name: str, starting_balance: Optional[Decimal] = None) -> str:
        """Start a new paper trading session."""
        if starting_balance is None:
            starting_balance = self.starting_balance
            
        session = PaperTradingSession(
            name=name,
            starting_balance=starting_balance,
            current_balance=starting_balance
        )
        
        self.sessions[session.session_id] = session
        self.current_session = session
        self.current_balance = starting_balance
        
        logger.info(f"Started paper trading session: {name} with balance: £{starting_balance}")
        return session.session_id
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """End the current paper trading session."""
        if not self.current_session:
            return None
            
        self.current_session.end_time = datetime.now()
        self.current_session.current_balance = self.current_balance
        self.current_session.active = False
        
        # Calculate session performance
        performance = self._calculate_session_performance(self.current_session)
        
        logger.info(f"Ended paper trading session: {self.current_session.name}")
        logger.info(f"Session P&L: £{performance['total_pnl']}")
        logger.info(f"Win Rate: {performance['win_rate']:.1f}%")
        
        self.current_session = None
        return performance
    
    async def place_bet(
        self,
        market_id: str,
        selection_id: str,
        selection_name: str,
        bet_type: PaperBetType,
        stake: Decimal,
        odds: Decimal,
        strategy_name: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> PaperBet:
        """Place a paper bet."""
        
        # Calculate potential profit/liability
        if bet_type == PaperBetType.BACK:
            potential_profit = stake * (odds - 1)
            potential_liability = stake
        else:  # LAY
            potential_profit = stake
            potential_liability = stake * (odds - 1)
        
        # Check if we have sufficient balance
        if potential_liability > self.current_balance:
            raise ValueError(f"Insufficient balance. Need £{potential_liability}, have £{self.current_balance}")
        
        bet = PaperBet(
            market_id=market_id,
            selection_id=selection_id,
            selection_name=selection_name,
            bet_type=bet_type,
            stake=stake,
            odds=odds,
            potential_profit=potential_profit,
            potential_liability=potential_liability,
            strategy_name=strategy_name,
            confidence=confidence
        )
        
        # Simulate immediate matching for paper trading
        bet.status = PaperBetStatus.MATCHED
        bet.matched_at = datetime.now()
        bet.matched_amount = stake
        
        # Reserve balance
        self.current_balance -= potential_liability
        
        self.bets[bet.bet_id] = bet
        
        # Update session stats
        if self.current_session:
            self.current_session.total_bets += 1
        
        logger.info(f"Placed paper bet: {bet_type.value} £{stake} on {selection_name} at {odds}")
        return bet
    
    def create_market(
        self,
        market_id: str,
        event_name: str,
        market_name: str,
        start_time: datetime,
        selections: List[Dict[str, Any]]
    ) -> PaperMarket:
        """Create a paper trading market."""
        
        market = PaperMarket(
            market_id=market_id,
            event_name=event_name,
            market_name=market_name,
            start_time=start_time
        )
        
        # Add selections
        for selection in selections:
            market.selections[selection['id']] = {
                'name': selection['name'],
                'odds': selection.get('odds', 2.0),
                'won': False
            }
        
        self.markets[market_id] = market
        logger.info(f"Created paper market: {event_name} - {market_name}")
        return market
    
    def settle_market(self, market_id: str, winner_id: str) -> Dict[str, Any]:
        """Settle a market and calculate bet outcomes."""
        
        if market_id not in self.markets:
            raise ValueError(f"Market {market_id} not found")
        
        market = self.markets[market_id]
        market.winner = winner_id
        market.settled = True
        market.status = "CLOSED"
        
        # Mark winner
        for selection_id in market.selections:
            market.selections[selection_id]['won'] = (selection_id == winner_id)
        
        # Settle all bets for this market
        settled_bets = []
        total_pnl = Decimal('0')
        
        for bet in self.bets.values():
            if bet.market_id == market_id and bet.status == PaperBetStatus.MATCHED:
                pnl = self._settle_bet(bet, winner_id)
                total_pnl += pnl
                settled_bets.append(bet)
        
        # Update session stats
        if self.current_session:
            for bet in settled_bets:
                if bet.profit_loss > 0:
                    self.current_session.winning_bets += 1
                elif bet.profit_loss < 0:
                    self.current_session.losing_bets += 1
                
                self.current_session.total_profit_loss += bet.profit_loss
        
        logger.info(f"Settled market {market.event_name} - Winner: {market.selections[winner_id]['name']}")
        logger.info(f"Total P&L from {len(settled_bets)} bets: £{total_pnl}")
        
        return {
            'market_id': market_id,
            'winner': market.selections[winner_id]['name'],
            'settled_bets': len(settled_bets),
            'total_pnl': total_pnl,
            'new_balance': self.current_balance
        }
    
    def _settle_bet(self, bet: PaperBet, winner_id: str) -> Decimal:
        """Settle an individual bet and return P&L."""
        
        bet.status = PaperBetStatus.SETTLED
        bet.settled_at = datetime.now()
        
        # Determine if bet won
        bet_won = False
        
        if bet.bet_type == PaperBetType.BACK:
            bet_won = (bet.selection_id == winner_id)
        else:  # LAY
            bet_won = (bet.selection_id != winner_id)
        
        # Calculate profit/loss
        if bet_won:
            bet.profit_loss = bet.potential_profit
            self.current_balance += bet.potential_liability + bet.potential_profit
        else:
            bet.profit_loss = -bet.potential_liability
            # Liability already deducted when bet was placed
        
        # Update daily P&L
        today = datetime.now().date().isoformat()
        if today not in self.daily_pnl:
            self.daily_pnl[today] = Decimal('0')
        self.daily_pnl[today] += bet.profit_loss
        
        # Update strategy stats
        if bet.strategy_name:
            if bet.strategy_name not in self.strategy_stats:
                self.strategy_stats[bet.strategy_name] = {
                    'total_bets': 0,
                    'winning_bets': 0,
                    'total_pnl': Decimal('0'),
                    'total_stake': Decimal('0')
                }
            
            stats = self.strategy_stats[bet.strategy_name]
            stats['total_bets'] += 1
            stats['total_stake'] += bet.stake
            stats['total_pnl'] += bet.profit_loss
            
            if bet.profit_loss > 0:
                stats['winning_bets'] += 1
        
        return bet.profit_loss
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        
        total_bets = len([b for b in self.bets.values() if b.status == PaperBetStatus.SETTLED])
        winning_bets = len([b for b in self.bets.values() if b.status == PaperBetStatus.SETTLED and b.profit_loss > 0])
        
        total_pnl = sum(b.profit_loss for b in self.bets.values() if b.profit_loss is not None)
        total_stake = sum(b.stake for b in self.bets.values() if b.status == PaperBetStatus.SETTLED)
        
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        roi = (total_pnl / total_stake * 100) if total_stake > 0 else 0
        
        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'total_pnl': total_pnl,
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': total_bets - winning_bets,
            'win_rate': win_rate,
            'roi': roi,
            'daily_pnl': dict(self.daily_pnl),
            'strategy_stats': dict(self.strategy_stats),
            'sessions': len(self.sessions)
        }
    
    def _calculate_session_performance(self, session: PaperTradingSession) -> Dict[str, Any]:
        """Calculate performance metrics for a session."""
        
        session_bets = [b for b in self.bets.values() 
                       if b.placed_at >= session.start_time and 
                       (session.end_time is None or b.placed_at <= session.end_time)]
        
        settled_bets = [b for b in session_bets if b.status == PaperBetStatus.SETTLED]
        winning_bets = [b for b in settled_bets if b.profit_loss > 0]
        
        total_pnl = sum(b.profit_loss for b in settled_bets if b.profit_loss is not None)
        total_stake = sum(b.stake for b in settled_bets)
        
        win_rate = (len(winning_bets) / len(settled_bets) * 100) if settled_bets else 0
        roi = (total_pnl / total_stake * 100) if total_stake > 0 else 0
        
        return {
            'session_name': session.name,
            'duration': session.end_time - session.start_time if session.end_time else None,
            'starting_balance': session.starting_balance,
            'ending_balance': session.current_balance,
            'total_pnl': total_pnl,
            'total_bets': len(settled_bets),
            'winning_bets': len(winning_bets),
            'win_rate': win_rate,
            'roi': roi
        }
    
    def export_results(self, filename: Optional[str] = None) -> str:
        """Export trading results to JSON file."""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"paper_trading_results_{timestamp}.json"
        
        results = {
            'summary': self.get_performance_summary(),
            'bets': [bet.dict() for bet in self.bets.values()],
            'markets': [market.dict() for market in self.markets.values()],
            'sessions': [session.dict() for session in self.sessions.values()]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Exported paper trading results to {filename}")
        return filename


# Global paper trading engine instance
_paper_trading_engine: Optional[PaperTradingEngine] = None


def get_paper_trading_engine() -> PaperTradingEngine:
    """Get or create the global paper trading engine."""
    global _paper_trading_engine
    
    if _paper_trading_engine is None:
        starting_balance = Decimal(str(settings.betdaq_max_daily_loss * 10))  # 10x daily loss limit
        _paper_trading_engine = PaperTradingEngine(starting_balance)
    
    return _paper_trading_engine


async def create_demo_session() -> str:
    """Create a demo paper trading session with sample data."""
    
    engine = get_paper_trading_engine()
    session_id = engine.start_session("Demo Session", Decimal('1000'))
    
    # Create sample markets
    now = datetime.now()
    
    # Race 1
    market1 = engine.create_market(
        market_id="market_001",
        event_name="Newmarket 14:30",
        market_name="Winner",
        start_time=now + timedelta(hours=1),
        selections=[
            {'id': 'horse_1', 'name': 'Thunder Bolt', 'odds': 3.5},
            {'id': 'horse_2', 'name': 'Lightning Fast', 'odds': 2.8},
            {'id': 'horse_3', 'name': 'Storm Chaser', 'odds': 4.2},
            {'id': 'horse_4', 'name': 'Wind Runner', 'odds': 6.0}
        ]
    )
    
    # Place some demo bets
    await engine.place_bet(
        market_id="market_001",
        selection_id="horse_2",
        selection_name="Lightning Fast",
        bet_type=PaperBetType.BACK,
        stake=Decimal('50'),
        odds=Decimal('2.8'),
        strategy_name="Value Betting",
        confidence=0.75
    )
    
    await engine.place_bet(
        market_id="market_001",
        selection_id="horse_1",
        selection_name="Thunder Bolt",
        bet_type=PaperBetType.LAY,
        stake=Decimal('30'),
        odds=Decimal('3.5'),
        strategy_name="Lay Favorite",
        confidence=0.65
    )
    
    logger.info("Created demo paper trading session with sample bets")
    return session_id
