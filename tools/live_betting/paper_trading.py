#!/usr/bin/env python3
"""
📈 Paper Trading System for Horse Racing
========================================

Advanced paper trading system that:
1. Executes betting signals from pre-race pipeline
2. Tracks performance and P&L
3. Manages virtual bankroll
4. Provides detailed analytics and reporting

Integrated with live betting signals for real-world testing.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/paper_trading.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PaperTradingSystem:
    """Complete paper trading system for horse racing bets"""

    def __init__(self, initial_bankroll: float = 10000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll

        # Database for tracking trades
        self.db_path = Path("/app/data/live_betting/paper_trading.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Trading parameters
        self.max_risk_per_bet = 0.05  # 5% max per bet
        self.min_bet_amount = 10.0
        self.max_bet_amount = 500.0

        # Performance tracking
        self.stats = {
            "total_bets": 0,
            "winning_bets": 0,
            "total_staked": 0.0,
            "total_returns": 0.0,
            "profit_loss": 0.0,
            "roi": 0.0,
            "strike_rate": 0.0,
            "avg_odds": 0.0,
            "best_win": 0.0,
            "worst_loss": 0.0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
        }

        self.initialize_database()
        self.load_existing_stats()

        logger.info(
            f"📈 Paper Trading System initialized with ${self.current_bankroll:,.2f}"
        )

    def initialize_database(self):
        """Initialize SQLite database for trade tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Bets table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    race_name TEXT NOT NULL,
                    horse_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    horse_number INTEGER,
                    bet_type TEXT NOT NULL,
                    stake_amount REAL NOT NULL,
                    odds REAL NOT NULL,
                    confidence REAL NOT NULL,
                    value_ratio REAL NOT NULL,
                    bet_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    race_time TIMESTAMP,
                    status TEXT DEFAULT 'PENDING',
                    result TEXT,
                    payout REAL DEFAULT 0.0,
                    profit_loss REAL DEFAULT 0.0,
                    reasoning TEXT
                )
            """
            )

            # Portfolio snapshots table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bankroll REAL NOT NULL,
                    total_staked REAL NOT NULL,
                    total_returns REAL NOT NULL,
                    profit_loss REAL NOT NULL,
                    total_bets INTEGER NOT NULL,
                    winning_bets INTEGER NOT NULL,
                    roi REAL NOT NULL,
                    strike_rate REAL NOT NULL
                )
            """
            )

            conn.commit()
            conn.close()

            logger.info("💾 Database initialized successfully")

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")

    def load_existing_stats(self):
        """Load existing performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get basic stats
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'WON' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(stake_amount) as total_staked,
                    SUM(payout) as total_returns,
                    SUM(profit_loss) as profit_loss,
                    AVG(odds) as avg_odds,
                    MAX(profit_loss) as best_win,
                    MIN(profit_loss) as worst_loss
                FROM bets 
                WHERE status = 'SETTLED'
            """
            )

            row = cursor.fetchone()
            if row and row[0] > 0:  # Has data
                self.stats.update(
                    {
                        "total_bets": row[0] or 0,
                        "winning_bets": row[1] or 0,
                        "total_staked": row[2] or 0.0,
                        "total_returns": row[3] or 0.0,
                        "profit_loss": row[4] or 0.0,
                        "avg_odds": row[5] or 0.0,
                        "best_win": row[6] or 0.0,
                        "worst_loss": row[7] or 0.0,
                    }
                )

                # Calculate derived stats
                if self.stats["total_bets"] > 0:
                    self.stats["strike_rate"] = (
                        self.stats["winning_bets"] / self.stats["total_bets"]
                    )

                if self.stats["total_staked"] > 0:
                    self.stats["roi"] = (
                        self.stats["profit_loss"] / self.stats["total_staked"]
                    )

                # Update current bankroll
                self.current_bankroll = (
                    self.initial_bankroll + self.stats["profit_loss"]
                )

            conn.close()
            logger.info(
                f"📊 Loaded existing stats: {self.stats['total_bets']} bets, P&L: ${self.stats['profit_loss']:,.2f}"
            )

        except Exception as e:
            logger.error(f"❌ Error loading stats: {e}")

    def calculate_bet_size(self, signal: Dict) -> float:
        """Calculate optimal bet size using Kelly criterion modified approach"""
        try:
            confidence = signal.get("confidence", 0.5)
            value_ratio = signal.get("value_ratio", 1.0)
            recommended_stake = signal.get("recommended_stake", 0.02)
            odds = signal.get("odds", 2.0)

            # Kelly fraction calculation
            win_prob = confidence
            loss_prob = 1 - win_prob
            net_odds = odds - 1  # Net profit per unit staked

            if net_odds > 0 and win_prob > 0:
                kelly_fraction = (win_prob * net_odds - loss_prob) / net_odds
                kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            else:
                kelly_fraction = 0.02

            # Combine Kelly with signal recommendation
            final_fraction = (kelly_fraction * 0.6) + (recommended_stake * 0.4)

            # Apply risk management
            final_fraction = min(final_fraction, self.max_risk_per_bet)

            # Calculate absolute amount
            bet_amount = self.current_bankroll * final_fraction
            bet_amount = max(self.min_bet_amount, min(bet_amount, self.max_bet_amount))

            # Ensure we don't bet more than available
            bet_amount = min(bet_amount, self.current_bankroll * 0.8)

            return round(bet_amount, 2)

        except Exception as e:
            logger.error(f"❌ Error calculating bet size: {e}")
            return self.min_bet_amount

    def place_bet(self, signal: Dict, race_info: Dict) -> bool:
        """Place a paper bet based on betting signal"""
        try:
            bet_amount = self.calculate_bet_size(signal)

            if bet_amount < self.min_bet_amount:
                logger.warning(f"⚠️ Bet amount too small: ${bet_amount:.2f}")
                return False

            if bet_amount > self.current_bankroll:
                logger.warning(
                    f"⚠️ Insufficient bankroll: ${bet_amount:.2f} > ${self.current_bankroll:.2f}"
                )
                return False

            # Record the bet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO bets (
                    race_id, race_name, horse_id, horse_name, horse_number,
                    bet_type, stake_amount, odds, confidence, value_ratio,
                    race_time, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    race_info.get("id", "unknown"),
                    race_info.get("race_name", "Unknown Race"),
                    signal.get("horse_id", "unknown"),
                    signal.get("horse_name", "Unknown Horse"),
                    signal.get("number", 0),
                    signal.get("bet_type", "WIN"),
                    bet_amount,
                    signal.get("odds", 2.0),
                    signal.get("confidence", 0.5),
                    signal.get("value_ratio", 1.0),
                    race_info.get("start_time"),
                    signal.get("reasoning", "No reasoning provided"),
                ),
            )

            bet_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Update bankroll (reserve stake)
            self.current_bankroll -= bet_amount

            logger.info(
                f"✅ Bet placed: #{signal.get('number')} {signal.get('horse_name')}"
            )
            logger.info(
                f"   💰 Stake: ${bet_amount:.2f} @ {signal.get('odds', 0):.1f}/1"
            )
            logger.info(f"   🎯 Confidence: {signal.get('confidence', 0):.1%}")
            logger.info(f"   💼 Remaining bankroll: ${self.current_bankroll:.2f}")

            return True

        except Exception as e:
            logger.error(f"❌ Error placing bet: {e}")
            return False

    def settle_bet(
        self, bet_id: int, result: str, finishing_position: int = None
    ) -> float:
        """Settle a bet with race result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get bet details
            cursor.execute("SELECT * FROM bets WHERE id = ?", (bet_id,))
            bet = cursor.fetchone()

            if not bet:
                logger.error(f"❌ Bet {bet_id} not found")
                return 0.0

            bet_dict = {
                "id": bet[0],
                "stake_amount": bet[7],
                "odds": bet[8],
                "bet_type": bet[6],
                "horse_name": bet[5],
            }

            payout = 0.0
            profit_loss = 0.0

            # Calculate payout based on result
            if result == "WON":
                if bet_dict["bet_type"] == "WIN":
                    payout = bet_dict["stake_amount"] * bet_dict["odds"]
                elif bet_dict["bet_type"] == "PLACE":
                    # Place odds typically 1/4 to 1/5 of win odds
                    place_odds = max(1.2, bet_dict["odds"] / 4)
                    payout = bet_dict["stake_amount"] * place_odds
                profit_loss = payout - bet_dict["stake_amount"]

            elif result == "PLACED" and bet_dict["bet_type"] == "PLACE":
                place_odds = max(1.2, bet_dict["odds"] / 4)
                payout = bet_dict["stake_amount"] * place_odds
                profit_loss = payout - bet_dict["stake_amount"]

            else:  # Lost
                payout = 0.0
                profit_loss = -bet_dict["stake_amount"]

            # Update bet record
            cursor.execute(
                """
                UPDATE bets 
                SET status = 'SETTLED', result = ?, payout = ?, profit_loss = ?
                WHERE id = ?
            """,
                (result, payout, profit_loss, bet_id),
            )

            conn.commit()
            conn.close()

            # Update bankroll
            self.current_bankroll += payout

            # Update stats
            self.update_stats()

            logger.info(f"🏁 Bet settled: {bet_dict['horse_name']} - {result}")
            logger.info(
                f"   💰 P&L: ${profit_loss:+.2f} | Bankroll: ${self.current_bankroll:.2f}"
            )

            return profit_loss

        except Exception as e:
            logger.error(f"❌ Error settling bet: {e}")
            return 0.0

    def update_stats(self):
        """Update performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Recalculate all stats
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'WON' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(stake_amount) as total_staked,
                    SUM(payout) as total_returns,
                    SUM(profit_loss) as profit_loss,
                    AVG(odds) as avg_odds,
                    MAX(profit_loss) as best_win,
                    MIN(profit_loss) as worst_loss
                FROM bets 
                WHERE status = 'SETTLED'
            """
            )

            row = cursor.fetchone()
            if row and row[0] > 0:
                self.stats.update(
                    {
                        "total_bets": row[0] or 0,
                        "winning_bets": row[1] or 0,
                        "total_staked": row[2] or 0.0,
                        "total_returns": row[3] or 0.0,
                        "profit_loss": row[4] or 0.0,
                        "avg_odds": row[5] or 0.0,
                        "best_win": row[6] or 0.0,
                        "worst_loss": row[7] or 0.0,
                    }
                )

                # Calculate derived stats
                if self.stats["total_bets"] > 0:
                    self.stats["strike_rate"] = (
                        self.stats["winning_bets"] / self.stats["total_bets"]
                    )

                if self.stats["total_staked"] > 0:
                    self.stats["roi"] = (
                        self.stats["profit_loss"] / self.stats["total_staked"]
                    )

            # Save portfolio snapshot
            cursor.execute(
                """
                INSERT INTO portfolio_snapshots (
                    bankroll, total_staked, total_returns, profit_loss,
                    total_bets, winning_bets, roi, strike_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.current_bankroll,
                    self.stats["total_staked"],
                    self.stats["total_returns"],
                    self.stats["profit_loss"],
                    self.stats["total_bets"],
                    self.stats["winning_bets"],
                    self.stats["roi"],
                    self.stats["strike_rate"],
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")

    def process_betting_signals(self, signals_file: str):
        """Process betting signals from pre-race pipeline"""
        try:
            signals_path = Path(signals_file)
            if not signals_path.exists():
                logger.error(f"❌ Signals file not found: {signals_file}")
                return

            with open(signals_path, "r") as f:
                signals = json.load(f)

            if not signals:
                logger.info("📭 No betting signals found")
                return

            logger.info(f"🎯 Processing {len(signals)} betting signals...")

            placed_bets = 0
            total_stake = 0.0

            for signal in signals:
                # Simulate race info (would come from pre-race pipeline)
                race_info = {
                    "id": f"race_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    "race_name": f"Race {signal.get('number', 1)}",
                    "start_time": datetime.now() + timedelta(hours=1),
                }

                if self.place_bet(signal, race_info):
                    placed_bets += 1
                    total_stake += self.calculate_bet_size(signal)

            logger.info(f"✅ Placed {placed_bets} bets totaling ${total_stake:.2f}")

        except Exception as e:
            logger.error(f"❌ Error processing signals: {e}")

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        try:
            report = {
                "summary": {
                    "current_bankroll": self.current_bankroll,
                    "initial_bankroll": self.initial_bankroll,
                    "total_profit_loss": self.stats["profit_loss"],
                    "percentage_return": (
                        (self.current_bankroll - self.initial_bankroll)
                        / self.initial_bankroll
                    )
                    * 100,
                    "total_bets": self.stats["total_bets"],
                    "winning_bets": self.stats["winning_bets"],
                    "strike_rate": self.stats["strike_rate"],
                    "roi": self.stats["roi"],
                    "avg_odds": self.stats["avg_odds"],
                    "total_staked": self.stats["total_staked"],
                },
                "best_performance": {
                    "best_win": self.stats["best_win"],
                    "worst_loss": self.stats["worst_loss"],
                },
                "recent_activity": self.get_recent_bets(),
                "monthly_performance": self.get_monthly_performance(),
                "bet_type_analysis": self.get_bet_type_analysis(),
            }

            return report

        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return {}

    def get_recent_bets(self, limit: int = 10) -> List[Dict]:
        """Get recent betting activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT horse_name, bet_type, stake_amount, odds, result, profit_loss, bet_time
                FROM bets 
                WHERE status = 'SETTLED'
                ORDER BY bet_time DESC 
                LIMIT ?
            """,
                (limit,),
            )

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "horse_name": row[0],
                    "bet_type": row[1],
                    "stake": row[2],
                    "odds": row[3],
                    "result": row[4],
                    "profit_loss": row[5],
                    "date": row[6],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"❌ Error getting recent bets: {e}")
            return []

    def get_monthly_performance(self) -> List[Dict]:
        """Get monthly performance breakdown"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    strftime('%Y-%m', bet_time) as month,
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'WON' THEN 1 ELSE 0 END) as wins,
                    SUM(stake_amount) as total_staked,
                    SUM(profit_loss) as profit_loss,
                    AVG(odds) as avg_odds
                FROM bets 
                WHERE status = 'SETTLED'
                GROUP BY strftime('%Y-%m', bet_time)
                ORDER BY month DESC
                LIMIT 12
            """
            )

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "month": row[0],
                    "total_bets": row[1],
                    "wins": row[2],
                    "strike_rate": row[2] / row[1] if row[1] > 0 else 0,
                    "total_staked": row[3],
                    "profit_loss": row[4],
                    "roi": row[4] / row[3] if row[3] > 0 else 0,
                    "avg_odds": row[5],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"❌ Error getting monthly performance: {e}")
            return []

    def get_bet_type_analysis(self) -> Dict:
        """Analyze performance by bet type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    bet_type,
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'WON' THEN 1 ELSE 0 END) as wins,
                    SUM(stake_amount) as total_staked,
                    SUM(profit_loss) as profit_loss,
                    AVG(odds) as avg_odds
                FROM bets 
                WHERE status = 'SETTLED'
                GROUP BY bet_type
            """
            )

            rows = cursor.fetchall()
            conn.close()

            analysis = {}
            for row in rows:
                bet_type = row[0]
                analysis[bet_type] = {
                    "total_bets": row[1],
                    "wins": row[2],
                    "strike_rate": row[2] / row[1] if row[1] > 0 else 0,
                    "total_staked": row[3],
                    "profit_loss": row[4],
                    "roi": row[4] / row[3] if row[3] > 0 else 0,
                    "avg_odds": row[5],
                }

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing bet types: {e}")
            return {}

    def print_dashboard(self):
        """Print trading dashboard to console"""
        report = self.generate_performance_report()

        print("\n" + "=" * 80)
        print("📈 PAPER TRADING DASHBOARD")
        print("=" * 80)

        summary = report.get("summary", {})
        print(f"💰 Current Bankroll: ${summary.get('current_bankroll', 0):,.2f}")
        print(f"📊 Total P&L: ${summary.get('total_profit_loss', 0):+,.2f}")
        print(f"📈 Return: {summary.get('percentage_return', 0):+.2f}%")
        print(
            f"🎯 Bets: {summary.get('total_bets', 0)} ({summary.get('winning_bets', 0)} wins)"
        )
        print(f"⚡ Strike Rate: {summary.get('strike_rate', 0):.1%}")
        print(f"💎 ROI: {summary.get('roi', 0):+.1%}")
        print(f"🎲 Avg Odds: {summary.get('avg_odds', 0):.1f}/1")

        # Recent bets
        recent = report.get("recent_activity", [])
        if recent:
            print(f"\n🕐 RECENT BETS (Last {len(recent)}):")
            for bet in recent[:5]:
                result_emoji = "✅" if bet["result"] == "WON" else "❌"
                print(
                    f"   {result_emoji} {bet['horse_name']} ({bet['bet_type']}) @ {bet['odds']:.1f}/1 - ${bet['profit_loss']:+.2f}"
                )

        print("=" * 80)


def main():
    """Main execution for testing"""
    trading_system = PaperTradingSystem()
    trading_system.print_dashboard()


if __name__ == "__main__":
    main()
