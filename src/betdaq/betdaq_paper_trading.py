"""
BETDAQ Paper Trading System
Simulates betting without real money for testing and validation
"""

import asyncio
import json
import logging
import random
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .betdaq_client import BetdaqConfig, BetOrder, BettingSide, MarketInfo


@dataclass
class PaperTradingConfig:
    """Configuration for paper trading"""

    starting_balance: float = 1000.0
    track_performance: bool = True
    simulate_market_movements: bool = True
    realistic_matching: bool = True
    commission_rate: float = 0.02  # 2% commission like real BETDAQ
    save_to_database: bool = True
    database_path: str = "paper_trading.db"


@dataclass
class PaperAccount:
    """Virtual account for paper trading"""

    balance: float = 1000.0
    total_staked: float = 0.0
    total_won: float = 0.0
    total_lost: float = 0.0
    total_commission: float = 0.0
    bets_placed: int = 0
    bets_won: int = 0
    bets_lost: int = 0
    daily_pnl: float = 0.0
    session_start: datetime = field(default_factory=datetime.now)

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.bets_placed == 0:
            return 0.0
        return (self.bets_won / self.bets_placed) * 100

    @property
    def roi(self) -> float:
        """Calculate return on investment"""
        if self.total_staked == 0:
            return 0.0
        net_profit = self.total_won - self.total_lost - self.total_commission
        return (net_profit / self.total_staked) * 100


class BetStatus(Enum):
    """Paper trading bet status"""

    PENDING = "pending"
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    CANCELLED = "cancelled"
    WON = "won"
    LOST = "lost"
    VOID = "void"


@dataclass
class PaperBet:
    """Paper trading bet record"""

    bet_id: str
    selection_id: int
    horse_name: str
    race_name: str
    market_id: int
    stake: float
    requested_odds: float
    matched_odds: float
    side: BettingSide
    status: BetStatus
    placed_at: datetime
    matched_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    pnl: float = 0.0
    commission: float = 0.0
    confidence: float = 0.0
    value: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["side"] = self.side.value
        data["status"] = self.status.value
        data["placed_at"] = self.placed_at.isoformat()
        if self.matched_at:
            data["matched_at"] = self.matched_at.isoformat()
        if self.settled_at:
            data["settled_at"] = self.settled_at.isoformat()
        return data


class PaperTradingEngine:
    """Paper trading simulation engine"""

    def __init__(self, config: PaperTradingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.account = PaperAccount(balance=config.starting_balance)
        self.active_bets: Dict[str, PaperBet] = {}
        self.settled_bets: Dict[str, PaperBet] = {}
        self.market_prices: Dict[int, Dict] = {}
        self.db_path = Path(config.database_path)

        if config.save_to_database:
            self._init_database()

    def _init_database(self):
        """Initialize SQLite database for paper trading records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create paper trading tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_bets (
                    bet_id TEXT PRIMARY KEY,
                    selection_id INTEGER,
                    horse_name TEXT,
                    race_name TEXT,
                    market_id INTEGER,
                    stake REAL,
                    requested_odds REAL,
                    matched_odds REAL,
                    side TEXT,
                    status TEXT,
                    placed_at TEXT,
                    matched_at TEXT,
                    settled_at TEXT,
                    pnl REAL,
                    commission REAL,
                    confidence REAL,
                    value REAL
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_account_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    balance REAL,
                    daily_pnl REAL,
                    total_staked REAL,
                    total_won REAL,
                    total_lost REAL,
                    bets_placed INTEGER,
                    bets_won INTEGER,
                    win_rate REAL,
                    roi REAL
                )
            """
            )

            conn.commit()
            conn.close()
            self.logger.info("Paper trading database initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")

    async def place_bet(
        self, order: BetOrder, market_info: MarketInfo
    ) -> Optional[PaperBet]:
        """Place a paper trading bet"""

        # Validate bet
        if not self._validate_bet(order):
            return None

        # Check account balance
        if self.account.balance < order.stake:
            self.logger.warning(
                f"Insufficient balance: {self.account.balance} < {order.stake}"
            )
            return None

        # Create paper bet
        bet_id = (
            f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{order.selection_id}"
        )

        paper_bet = PaperBet(
            bet_id=bet_id,
            selection_id=order.selection_id,
            horse_name=order.horse_name,
            race_name=market_info.market_name,
            market_id=order.market_id,
            stake=order.stake,
            requested_odds=order.odds,
            matched_odds=order.odds,  # In paper trading, assume immediate match
            side=order.side,
            status=(
                BetStatus.MATCHED
                if self.config.realistic_matching
                else BetStatus.PENDING
            ),
            placed_at=datetime.now(),
            matched_at=datetime.now() if self.config.realistic_matching else None,
            confidence=order.confidence,
            value=order.value,
        )

        # Update account
        self.account.balance -= order.stake
        self.account.total_staked += order.stake
        self.account.bets_placed += 1

        # Store bet
        self.active_bets[bet_id] = paper_bet

        # Save to database
        if self.config.save_to_database:
            await self._save_bet_to_db(paper_bet)

        self.logger.info(
            f"Paper bet placed: {paper_bet.horse_name} @ {paper_bet.matched_odds} - Stake: £{paper_bet.stake}"
        )
        return paper_bet

    def _validate_bet(self, order: BetOrder) -> bool:
        """Validate bet parameters"""
        if order.stake <= 0:
            self.logger.warning("Invalid stake amount")
            return False

        if order.odds < 1.01 or order.odds > 1000:
            self.logger.warning("Invalid odds")
            return False

        return True

    async def simulate_race_result(
        self, market_id: int, winning_selection_id: int = None
    ):
        """Simulate race result and settle bets"""

        market_bets = [
            bet for bet in self.active_bets.values() if bet.market_id == market_id
        ]

        if not market_bets:
            return

        # If no winner specified, simulate random result based on odds
        if winning_selection_id is None:
            winning_selection_id = self._simulate_race_winner(market_bets)

        for bet in market_bets:
            await self._settle_bet(bet, winning_selection_id)

    def _simulate_race_winner(self, bets: List[PaperBet]) -> int:
        """Simulate race winner based on implied probabilities from odds"""

        if not bets:
            return None

        # Calculate implied probabilities
        runners = {}
        for bet in bets:
            if bet.selection_id not in runners:
                implied_prob = 1.0 / bet.matched_odds
                runners[bet.selection_id] = implied_prob

        # Normalize probabilities
        total_prob = sum(runners.values())
        if total_prob > 0:
            for selection_id in runners:
                runners[selection_id] /= total_prob

        # Random selection based on probabilities
        rand = random.random()
        cumulative = 0.0

        for selection_id, prob in runners.items():
            cumulative += prob
            if rand <= cumulative:
                return selection_id

        # Fallback to first selection
        return list(runners.keys())[0] if runners else bets[0].selection_id

    async def _settle_bet(self, bet: PaperBet, winning_selection_id: int):
        """Settle a paper trading bet"""

        # Determine if bet won
        if bet.side == BettingSide.BACK:
            won = bet.selection_id == winning_selection_id
        else:  # LAY
            won = bet.selection_id != winning_selection_id

        # Calculate P&L
        if won:
            if bet.side == BettingSide.BACK:
                gross_profit = bet.stake * (bet.matched_odds - 1)
            else:  # LAY
                gross_profit = bet.stake

            commission = gross_profit * self.config.commission_rate
            net_profit = gross_profit - commission

            bet.pnl = net_profit
            bet.commission = commission
            bet.status = BetStatus.WON

            # Update account
            self.account.balance += bet.stake + net_profit
            self.account.total_won += net_profit
            self.account.total_commission += commission
            self.account.bets_won += 1

        else:
            if bet.side == BettingSide.BACK:
                bet.pnl = -bet.stake
            else:  # LAY
                bet.pnl = -bet.stake * (bet.matched_odds - 1)

            bet.status = BetStatus.LOST

            # Update account
            self.account.total_lost += abs(bet.pnl)
            self.account.bets_lost += 1

        bet.settled_at = datetime.now()

        # Move to settled bets
        self.settled_bets[bet.bet_id] = bet
        del self.active_bets[bet.bet_id]

        # Update daily P&L
        self.account.daily_pnl += bet.pnl

        # Save to database
        if self.config.save_to_database:
            await self._update_bet_in_db(bet)
            await self._save_account_snapshot()

        result = "WON" if won else "LOST"
        self.logger.info(
            f"Bet settled: {bet.horse_name} - {result} - P&L: £{bet.pnl:.2f}"
        )

    async def _save_bet_to_db(self, bet: PaperBet):
        """Save bet to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            bet_data = bet.to_dict()
            cursor.execute(
                """
                INSERT INTO paper_bets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    bet_data["bet_id"],
                    bet_data["selection_id"],
                    bet_data["horse_name"],
                    bet_data["race_name"],
                    bet_data["market_id"],
                    bet_data["stake"],
                    bet_data["requested_odds"],
                    bet_data["matched_odds"],
                    bet_data["side"],
                    bet_data["status"],
                    bet_data["placed_at"],
                    bet_data.get("matched_at"),
                    bet_data.get("settled_at"),
                    bet_data["pnl"],
                    bet_data["commission"],
                    bet_data["confidence"],
                    bet_data["value"],
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to save bet to database: {e}")

    async def _update_bet_in_db(self, bet: PaperBet):
        """Update bet in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            bet_data = bet.to_dict()
            cursor.execute(
                """
                UPDATE paper_bets 
                SET status=?, settled_at=?, pnl=?, commission=?
                WHERE bet_id=?
            """,
                (
                    bet_data["status"],
                    bet_data.get("settled_at"),
                    bet_data["pnl"],
                    bet_data["commission"],
                    bet_data["bet_id"],
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to update bet in database: {e}")

    async def _save_account_snapshot(self):
        """Save account snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO paper_account_history 
                (timestamp, balance, daily_pnl, total_staked, total_won, total_lost,
                 bets_placed, bets_won, win_rate, roi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    self.account.balance,
                    self.account.daily_pnl,
                    self.account.total_staked,
                    self.account.total_won,
                    self.account.total_lost,
                    self.account.bets_placed,
                    self.account.bets_won,
                    self.account.win_rate,
                    self.account.roi,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to save account snapshot: {e}")

    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        return {
            "account": asdict(self.account),
            "active_bets": len(self.active_bets),
            "settled_bets": len(self.settled_bets),
            "win_rate": self.account.win_rate,
            "roi": self.account.roi,
            "profit_loss": self.account.total_won
            - self.account.total_lost
            - self.account.total_commission,
        }

    async def export_results(self, filepath: str):
        """Export paper trading results to JSON"""
        try:
            summary = self.get_performance_summary()

            all_bets = {}
            for bet in list(self.active_bets.values()) + list(
                self.settled_bets.values()
            ):
                all_bets[bet.bet_id] = bet.to_dict()

            export_data = {
                "summary": summary,
                "bets": all_bets,
                "exported_at": datetime.now().isoformat(),
            }

            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"Paper trading results exported to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")

    def reset_account(self):
        """Reset account for new session"""
        self.account = PaperAccount(balance=self.config.starting_balance)
        self.active_bets.clear()
        self.settled_bets.clear()
        self.logger.info("Paper trading account reset")


# Example usage and testing
async def main():
    """Example paper trading session"""

    config = PaperTradingConfig(
        starting_balance=1000.0, realistic_matching=True, save_to_database=True
    )

    engine = PaperTradingEngine(config)

    # Example market and bet
    market_info = MarketInfo(
        market_id=12345,
        market_name="2:30 Newmarket - Win",
        start_time=datetime.now() + timedelta(minutes=30),
        status="active",
    )

    order = BetOrder(
        selection_id=67890,
        horse_name="Thunder Bolt",
        stake=10.0,
        odds=3.5,
        side=BettingSide.BACK,
        market_id=12345,
        confidence=0.85,
        value=0.15,
    )

    # Place bet
    bet = await engine.place_bet(order, market_info)
    if bet:
        print(f"Bet placed: {bet.bet_id}")

    # Simulate race result
    await engine.simulate_race_result(12345, winning_selection_id=67890)

    # Get summary
    summary = engine.get_performance_summary()
    print(f"Performance: {summary}")


if __name__ == "__main__":
    asyncio.run(main())
