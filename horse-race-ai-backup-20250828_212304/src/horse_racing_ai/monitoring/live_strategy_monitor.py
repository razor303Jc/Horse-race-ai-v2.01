#!/usr/bin/env python3
"""
Live Strategy Performance Monitoring System
===========================================

Real-time monitoring and performance tracking for 80/20 and Dutching strategies.
Provides live integration with racing data feeds and comprehensive analytics.

Features:
- Real-time strategy performance tracking
- ROI monitoring and analysis
- Risk assessment and alerts
- Strategy optimization recommendations
- Live race integration
- Performance dashboard data
- Automated reporting

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
import threading
import time
from pathlib import Path

# Import strategy systems
from ..integration.strategy_aware_ml_hub import StrategyAwareMLIntegrationHub
from ..betting.eighty_twenty_strategy import EightyTwentyStrategy
from ..betting.reduced_stake_dutching import ReducedStakeDutching
from ..database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class StrategyPerformanceMetrics:
    """Performance metrics for a betting strategy"""

    strategy_name: str
    total_bets: int
    winning_bets: int
    losing_bets: int
    total_stake: float
    total_returns: float
    net_profit: float
    roi_percentage: float
    strike_rate: float
    avg_odds: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    last_updated: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "strategy_name": self.strategy_name,
            "total_bets": self.total_bets,
            "winning_bets": self.winning_bets,
            "losing_bets": self.losing_bets,
            "total_stake": self.total_stake,
            "total_returns": self.total_returns,
            "net_profit": self.net_profit,
            "roi_percentage": self.roi_percentage,
            "strike_rate": self.strike_rate,
            "avg_odds": self.avg_odds,
            "max_drawdown": self.max_drawdown,
            "profit_factor": self.profit_factor,
            "sharpe_ratio": self.sharpe_ratio,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class LiveStrategyOpportunity:
    """Real-time strategy opportunity"""

    race_id: str
    course: str
    race_time: datetime
    strategy_type: str  # '80/20' or 'dutching'
    horse_selections: List[str]
    recommended_stakes: List[float]
    expected_roi: float
    confidence_score: float
    risk_level: str
    market_conditions: Dict
    created_at: datetime
    executed: bool = False
    result: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "race_id": self.race_id,
            "course": self.course,
            "race_time": self.race_time.isoformat(),
            "strategy_type": self.strategy_type,
            "horse_selections": self.horse_selections,
            "recommended_stakes": self.recommended_stakes,
            "expected_roi": self.expected_roi,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "market_conditions": self.market_conditions,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed,
            "result": self.result,
        }


class StrategyPerformanceDatabase:
    """Database manager for strategy performance tracking"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize performance tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            # Strategy performance table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT NOT NULL,
                    race_id TEXT NOT NULL,
                    race_date DATE NOT NULL,
                    course TEXT,
                    horse_selections TEXT,  -- JSON array
                    stakes TEXT,  -- JSON array
                    odds TEXT,  -- JSON array
                    result TEXT,  -- 'win', 'lose', 'partial'
                    stake_amount REAL,
                    return_amount REAL,
                    profit_loss REAL,
                    roi_percentage REAL,
                    execution_time TIMESTAMP,
                    market_conditions TEXT,  -- JSON
                    confidence_score REAL,
                    risk_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Daily performance summary
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    strategy_name TEXT NOT NULL,
                    total_bets INTEGER,
                    winning_bets INTEGER,
                    total_stake REAL,
                    total_returns REAL,
                    net_profit REAL,
                    roi_percentage REAL,
                    strike_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, strategy_name)
                )
            """
            )

            # Live opportunities table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS live_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    course TEXT,
                    race_time TIMESTAMP,
                    strategy_type TEXT,
                    horse_selections TEXT,  -- JSON
                    recommended_stakes TEXT,  -- JSON
                    expected_roi REAL,
                    confidence_score REAL,
                    risk_level TEXT,
                    market_conditions TEXT,  -- JSON
                    executed BOOLEAN DEFAULT FALSE,
                    result TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Performance alerts table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT,  -- 'high_roi', 'drawdown', 'opportunity'
                    strategy_name TEXT,
                    message TEXT,
                    severity TEXT,  -- 'info', 'warning', 'critical'
                    data TEXT,  -- JSON
                    acknowledged BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def record_strategy_result(
        self,
        race_id: str,
        strategy_name: str,
        selections: List[str],
        stakes: List[float],
        odds: List[float],
        result: str,
        stake_amount: float,
        return_amount: float,
        **kwargs,
    ):
        """Record a strategy execution result"""
        with sqlite3.connect(self.db_path) as conn:
            profit_loss = return_amount - stake_amount
            roi = (profit_loss / stake_amount * 100) if stake_amount > 0 else 0

            conn.execute(
                """
                INSERT INTO strategy_performance 
                (strategy_name, race_id, race_date, course, horse_selections, 
                 stakes, odds, result, stake_amount, return_amount, profit_loss,
                 roi_percentage, execution_time, market_conditions, confidence_score,
                 risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    strategy_name,
                    race_id,
                    kwargs.get("race_date", datetime.now().date()),
                    kwargs.get("course", ""),
                    json.dumps(selections),
                    json.dumps(stakes),
                    json.dumps(odds),
                    result,
                    stake_amount,
                    return_amount,
                    profit_loss,
                    roi,
                    datetime.now(),
                    json.dumps(kwargs.get("market_conditions", {})),
                    kwargs.get("confidence_score", 0.0),
                    kwargs.get("risk_level", "medium"),
                ),
            )

    def get_strategy_performance(
        self, strategy_name: str, days: int = 30
    ) -> StrategyPerformanceMetrics:
        """Get performance metrics for a strategy"""
        with sqlite3.connect(self.db_path) as conn:
            since_date = datetime.now() - timedelta(days=days)

            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(stake_amount) as total_stake,
                    SUM(return_amount) as total_returns,
                    AVG(CASE WHEN odds != '[]' THEN 
                        CAST(SUBSTR(odds, 2, LENGTH(odds)-2) AS REAL) ELSE 0 END) as avg_odds
                FROM strategy_performance 
                WHERE strategy_name = ? AND execution_time >= ?
            """,
                (strategy_name, since_date),
            )

            row = cursor.fetchone()
            if not row or row[0] == 0:
                return StrategyPerformanceMetrics(
                    strategy_name=strategy_name,
                    total_bets=0,
                    winning_bets=0,
                    losing_bets=0,
                    total_stake=0.0,
                    total_returns=0.0,
                    net_profit=0.0,
                    roi_percentage=0.0,
                    strike_rate=0.0,
                    avg_odds=0.0,
                    max_drawdown=0.0,
                    profit_factor=0.0,
                    sharpe_ratio=0.0,
                    last_updated=datetime.now(),
                )

            total_bets, winning_bets, total_stake, total_returns, avg_odds = row
            losing_bets = total_bets - winning_bets
            net_profit = total_returns - total_stake
            roi_percentage = (net_profit / total_stake * 100) if total_stake > 0 else 0
            strike_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0

            # Calculate additional metrics
            max_drawdown = self._calculate_max_drawdown(strategy_name, since_date)
            profit_factor = self._calculate_profit_factor(strategy_name, since_date)
            sharpe_ratio = self._calculate_sharpe_ratio(strategy_name, since_date)

            return StrategyPerformanceMetrics(
                strategy_name=strategy_name,
                total_bets=total_bets,
                winning_bets=winning_bets,
                losing_bets=losing_bets,
                total_stake=total_stake or 0.0,
                total_returns=total_returns or 0.0,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                strike_rate=strike_rate,
                avg_odds=avg_odds or 0.0,
                max_drawdown=max_drawdown,
                profit_factor=profit_factor,
                sharpe_ratio=sharpe_ratio,
                last_updated=datetime.now(),
            )

    def _calculate_max_drawdown(
        self, strategy_name: str, since_date: datetime
    ) -> float:
        """Calculate maximum drawdown for strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT profit_loss FROM strategy_performance 
                WHERE strategy_name = ? AND execution_time >= ?
                ORDER BY execution_time
            """,
                (strategy_name, since_date),
            )

            profits = [row[0] for row in cursor.fetchall()]
            if not profits:
                return 0.0

            # Calculate running balance
            running_balance = np.cumsum(profits)

            # Calculate drawdown
            peak = np.maximum.accumulate(running_balance)
            drawdown = (running_balance - peak) / np.maximum(
                peak, 1
            )  # Avoid division by zero

            return float(np.min(drawdown) * 100)  # Return as percentage

    def _calculate_profit_factor(
        self, strategy_name: str, since_date: datetime
    ) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as gross_profit,
                    SUM(CASE WHEN profit_loss < 0 THEN ABS(profit_loss) ELSE 0 END) as gross_loss
                FROM strategy_performance 
                WHERE strategy_name = ? AND execution_time >= ?
            """,
                (strategy_name, since_date),
            )

            row = cursor.fetchone()
            if row and row[1] and row[1] > 0:
                return row[0] / row[1]
            return 0.0

    def _calculate_sharpe_ratio(
        self, strategy_name: str, since_date: datetime
    ) -> float:
        """Calculate Sharpe ratio for strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT roi_percentage FROM strategy_performance 
                WHERE strategy_name = ? AND execution_time >= ?
            """,
                (strategy_name, since_date),
            )

            returns = [row[0] for row in cursor.fetchall()]
            if len(returns) < 2:
                return 0.0

            returns_array = np.array(returns)
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)

            return float(mean_return / std_return) if std_return > 0 else 0.0

    def record_live_opportunity(self, opportunity: LiveStrategyOpportunity):
        """Record a live strategy opportunity"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO live_opportunities 
                (race_id, course, race_time, strategy_type, horse_selections,
                 recommended_stakes, expected_roi, confidence_score, risk_level,
                 market_conditions, executed, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    opportunity.race_id,
                    opportunity.course,
                    opportunity.race_time,
                    opportunity.strategy_type,
                    json.dumps(opportunity.horse_selections),
                    json.dumps(opportunity.recommended_stakes),
                    opportunity.expected_roi,
                    opportunity.confidence_score,
                    opportunity.risk_level,
                    json.dumps(opportunity.market_conditions),
                    opportunity.executed,
                    json.dumps(opportunity.result) if opportunity.result else None,
                ),
            )

    def add_performance_alert(
        self,
        alert_type: str,
        strategy_name: str,
        message: str,
        severity: str = "info",
        data: Dict = None,
    ):
        """Add a performance alert"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO performance_alerts 
                (alert_type, strategy_name, message, severity, data)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    alert_type,
                    strategy_name,
                    message,
                    severity,
                    json.dumps(data) if data else None,
                ),
            )


class LiveStrategyMonitor:
    """Live monitoring system for betting strategies"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = (
                "/home/jc/Documents/Horse-race-ai-v2.03/data/strategy_performance.db"
            )

        self.db = StrategyPerformanceDatabase(db_path)
        self.strategy_hub = StrategyAwareMLIntegrationHub()
        self.eighty_twenty = EightyTwentyStrategy()
        self.dutching = ReducedStakeDutching()
        self.db_manager = DatabaseManager()

        # Monitoring configuration
        self.monitoring_active = False
        self.alert_thresholds = {
            "high_roi_threshold": 15.0,  # Alert if ROI > 15%
            "drawdown_threshold": -10.0,  # Alert if drawdown < -10%
            "low_confidence_threshold": 0.3,  # Alert if confidence < 30%
            "min_opportunities_per_day": 3,
        }

        # Performance tracking
        self.daily_opportunities = {"80/20": [], "dutching": []}
        self.real_time_metrics = {}

        logger.info("Live Strategy Monitor initialized")

    def start_monitoring(self):
        """Start live monitoring"""
        self.monitoring_active = True
        logger.info("🔄 Starting live strategy monitoring...")

        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()

        logger.info("✅ Live monitoring started")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Live monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for new opportunities
                self._scan_for_opportunities()

                # Update performance metrics
                self._update_real_time_metrics()

                # Check for alerts
                self._check_performance_alerts()

                # Sleep before next check
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _scan_for_opportunities(self):
        """Scan for new strategy opportunities"""
        try:
            # Get today's race cards
            today = datetime.now().strftime("%Y-%m-%d")

            query = """
            SELECT DISTINCT race_id, course, race_time, race_class, going, 
                   distance_yards
            FROM races 
            WHERE race_date = ? AND race_time > ?
            ORDER BY race_time
            LIMIT 10
            """

            current_time = datetime.now().strftime("%H:%M:%S")
            races = self.db_manager.execute_query(query, (today, current_time))

            if not races:
                return

            for race in races:
                race_dict = dict(race)
                self._analyze_race_for_opportunities(race_dict)

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")

    def _analyze_race_for_opportunities(self, race: Dict):
        """Analyze a single race for strategy opportunities"""
        try:
            race_id = race["race_id"]

            # Get race runners
            runners_query = """
            SELECT horse_name, jockey_name, official_rating, starting_price_decimal,
                   jockey_claim, weight_carried
            FROM race_results 
            WHERE race_id = ?
            """

            runners = self.db_manager.execute_query(runners_query, (race_id,))
            if not runners or len(runners) < 3:
                return

            runners_list = [dict(runner) for runner in runners]

            # Analyze for 80/20 opportunities
            eighty_twenty_opp = self._check_eighty_twenty_opportunity(
                race, runners_list
            )
            if eighty_twenty_opp:
                self.daily_opportunities["80/20"].append(eighty_twenty_opp)
                self.db.record_live_opportunity(eighty_twenty_opp)
                logger.info(f"🎯 80/20 opportunity found for race {race_id}")

            # Analyze for dutching opportunities
            dutching_opp = self._check_dutching_opportunity(race, runners_list)
            if dutching_opp:
                self.daily_opportunities["dutching"].append(dutching_opp)
                self.db.record_live_opportunity(dutching_opp)
                logger.info(f"🎲 Dutching opportunity found for race {race_id}")

        except Exception as e:
            logger.error(f"Error analyzing race {race.get('race_id', 'unknown')}: {e}")

    def _check_eighty_twenty_opportunity(
        self, race: Dict, runners: List[Dict]
    ) -> Optional[LiveStrategyOpportunity]:
        """Check for 80/20 strategy opportunity"""
        try:
            # Look for horses with odds >= 4.0 and high ratings
            suitable_horses = []

            for runner in runners:
                odds = runner.get("starting_price_decimal", 0)
                rating = runner.get("official_rating", 0)

                if odds >= 4.0 and rating >= 70:
                    # Calculate confidence using strategy hub
                    confidence = self._calculate_horse_confidence(runner, race)

                    if confidence > 0.6:  # High confidence threshold
                        suitable_horses.append(
                            {
                                "name": runner["horse_name"],
                                "odds": odds,
                                "rating": rating,
                                "confidence": confidence,
                            }
                        )

            if suitable_horses:
                # Select best candidate
                best_horse = max(suitable_horses, key=lambda x: x["confidence"])

                # Calculate expected ROI
                place_probability = (
                    best_horse["confidence"] * 0.7
                )  # Estimate place probability
                place_odds = best_horse["odds"] / 3  # Rough place odds estimate
                expected_roi = (place_probability * place_odds - 1) * 100

                if expected_roi > 5.0:  # Minimum 5% expected ROI
                    return LiveStrategyOpportunity(
                        race_id=race["race_id"],
                        course=race["course"],
                        race_time=datetime.strptime(
                            f"{datetime.now().date()} {race['race_time']}",
                            "%Y-%m-%d %H:%M:%S",
                        ),
                        strategy_type="80/20",
                        horse_selections=[best_horse["name"]],
                        recommended_stakes=[10.0],  # Standard stake
                        expected_roi=expected_roi,
                        confidence_score=best_horse["confidence"],
                        risk_level="medium",
                        market_conditions={
                            "field_size": len(runners),
                            "race_class": race.get("race_class", ""),
                            "going": race.get("going", ""),
                        },
                        created_at=datetime.now(),
                    )

            return None

        except Exception as e:
            logger.error(f"Error checking 80/20 opportunity: {e}")
            return None

    def _check_dutching_opportunity(
        self, race: Dict, runners: List[Dict]
    ) -> Optional[LiveStrategyOpportunity]:
        """Check for dutching strategy opportunity"""
        try:
            if len(runners) < 4:
                return None

            # Sort by rating and select top 4
            sorted_runners = sorted(
                runners, key=lambda x: x.get("official_rating", 0), reverse=True
            )
            top_runners = sorted_runners[:4]

            # Calculate total inverse odds
            total_inverse_odds = 0
            valid_runners = []

            for runner in top_runners:
                odds = runner.get("starting_price_decimal", 0)
                if odds > 0:
                    total_inverse_odds += 1.0 / odds
                    confidence = self._calculate_horse_confidence(runner, race)
                    valid_runners.append(
                        {
                            "name": runner["horse_name"],
                            "odds": odds,
                            "confidence": confidence,
                        }
                    )

            # Check if dutching is profitable
            if (
                len(valid_runners) >= 3 and total_inverse_odds < 0.9
            ):  # Leave margin for profit
                # Calculate stakes
                stakes = []
                total_stake = 40.0  # Standard total stake

                for runner in valid_runners:
                    stake = (total_stake / runner["odds"]) / total_inverse_odds
                    stakes.append(round(stake, 2))

                # Calculate expected ROI
                avg_confidence = np.mean([r["confidence"] for r in valid_runners])
                expected_roi = (
                    ((1.0 - total_inverse_odds) / total_inverse_odds)
                    * avg_confidence
                    * 100
                )

                if expected_roi > 3.0:  # Minimum 3% expected ROI for dutching
                    return LiveStrategyOpportunity(
                        race_id=race["race_id"],
                        course=race["course"],
                        race_time=datetime.strptime(
                            f"{datetime.now().date()} {race['race_time']}",
                            "%Y-%m-%d %H:%M:%S",
                        ),
                        strategy_type="dutching",
                        horse_selections=[r["name"] for r in valid_runners],
                        recommended_stakes=stakes,
                        expected_roi=expected_roi,
                        confidence_score=avg_confidence,
                        risk_level="low" if len(valid_runners) >= 4 else "medium",
                        market_conditions={
                            "field_size": len(runners),
                            "total_inverse_odds": total_inverse_odds,
                            "race_class": race.get("race_class", ""),
                            "going": race.get("going", ""),
                        },
                        created_at=datetime.now(),
                    )

            return None

        except Exception as e:
            logger.error(f"Error checking dutching opportunity: {e}")
            return None

    def _calculate_horse_confidence(self, runner: Dict, race: Dict) -> float:
        """Calculate confidence score for a horse"""
        try:
            # Simple confidence calculation based on rating and conditions
            rating = runner.get("official_rating", 70)
            jockey_claim = runner.get("jockey_claim", 0)

            # Base confidence from rating
            base_confidence = min(1.0, rating / 100.0)

            # Adjust for jockey claim
            jockey_adjustment = 1.0 - (
                jockey_claim * 0.02
            )  # Reduce confidence for claiming jockeys

            # Adjust for race conditions (simple heuristic)
            race_class = race.get("race_class", "")
            class_adjustment = 1.0
            if "MAIDEN" in race_class.upper():
                class_adjustment = 0.9
            elif "HANDICAP" in race_class.upper():
                class_adjustment = 1.0
            elif "GRADED" in race_class.upper():
                class_adjustment = 1.1

            final_confidence = base_confidence * jockey_adjustment * class_adjustment
            return min(1.0, max(0.0, final_confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default moderate confidence

    def _update_real_time_metrics(self):
        """Update real-time performance metrics"""
        try:
            # Get performance for both strategies
            eighty_twenty_metrics = self.db.get_strategy_performance("80/20", days=30)
            dutching_metrics = self.db.get_strategy_performance("dutching", days=30)

            self.real_time_metrics = {
                "80/20": eighty_twenty_metrics.to_dict(),
                "dutching": dutching_metrics.to_dict(),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error updating real-time metrics: {e}")

    def _check_performance_alerts(self):
        """Check for performance alerts"""
        try:
            for strategy_name in ["80/20", "dutching"]:
                metrics = self.db.get_strategy_performance(strategy_name)

                # High ROI alert
                if metrics.roi_percentage > self.alert_thresholds["high_roi_threshold"]:
                    self.db.add_performance_alert(
                        "high_roi",
                        strategy_name,
                        f"Exceptional performance: {metrics.roi_percentage:.1f}% ROI",
                        "info",
                        {"roi": metrics.roi_percentage},
                    )

                # Drawdown alert
                if metrics.max_drawdown < self.alert_thresholds["drawdown_threshold"]:
                    self.db.add_performance_alert(
                        "drawdown",
                        strategy_name,
                        f"High drawdown detected: {metrics.max_drawdown:.1f}%",
                        "warning",
                        {"drawdown": metrics.max_drawdown},
                    )

                # Low opportunities alert
                daily_opps = len(
                    self.daily_opportunities.get(
                        strategy_name.replace("/20", "_twenty"), []
                    )
                )
                if daily_opps < self.alert_thresholds["min_opportunities_per_day"]:
                    self.db.add_performance_alert(
                        "low_opportunities",
                        strategy_name,
                        f"Low opportunity count: {daily_opps} today",
                        "info",
                        {"opportunity_count": daily_opps},
                    )

        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")

    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        try:
            # Get current metrics
            eighty_twenty_metrics = self.db.get_strategy_performance("80/20", days=30)
            dutching_metrics = self.db.get_strategy_performance("dutching", days=30)

            # Get today's opportunities
            today_opportunities = {
                "80/20": len(self.daily_opportunities.get("80/20", [])),
                "dutching": len(self.daily_opportunities.get("dutching", [])),
            }

            # Get recent alerts
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT alert_type, strategy_name, message, severity, created_at
                    FROM performance_alerts 
                    WHERE created_at >= date('now', '-7 days')
                    ORDER BY created_at DESC
                    LIMIT 20
                """
                )
                recent_alerts = [
                    dict(zip([col[0] for col in cursor.description], row))
                    for row in cursor.fetchall()
                ]

            return {
                "strategy_performance": {
                    "80/20": eighty_twenty_metrics.to_dict(),
                    "dutching": dutching_metrics.to_dict(),
                },
                "today_opportunities": today_opportunities,
                "recent_alerts": recent_alerts,
                "monitoring_status": {
                    "active": self.monitoring_active,
                    "last_scan": datetime.now().isoformat(),
                },
                "real_time_metrics": self.real_time_metrics,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def execute_opportunity(
        self, opportunity: LiveStrategyOpportunity, execution_result: Dict
    ) -> bool:
        """Record execution of a strategy opportunity"""
        try:
            # Update opportunity as executed
            opportunity.executed = True
            opportunity.result = execution_result

            # Record in database
            total_stake = sum(opportunity.recommended_stakes)
            total_return = execution_result.get("total_return", 0.0)
            result_type = execution_result.get("result", "lose")

            self.db.record_strategy_result(
                race_id=opportunity.race_id,
                strategy_name=opportunity.strategy_type,
                selections=opportunity.horse_selections,
                stakes=opportunity.recommended_stakes,
                odds=execution_result.get("odds", []),
                result=result_type,
                stake_amount=total_stake,
                return_amount=total_return,
                race_date=opportunity.race_time.date(),
                course=opportunity.course,
                confidence_score=opportunity.confidence_score,
                risk_level=opportunity.risk_level,
                market_conditions=opportunity.market_conditions,
            )

            logger.info(
                f"✅ Recorded {opportunity.strategy_type} execution for race {opportunity.race_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error executing opportunity: {e}")
            return False


def main():
    """Main function for testing live monitoring"""
    # Initialize monitoring
    monitor = LiveStrategyMonitor()

    try:
        # Start monitoring
        monitor.start_monitoring()

        logger.info("🎯 Live Strategy Monitoring System Started")
        logger.info("📊 Monitoring 80/20 and Dutching strategies...")

        # Run for a test period
        for i in range(10):  # Test for 10 cycles
            time.sleep(30)

            # Get dashboard data
            dashboard = monitor.get_dashboard_data()

            logger.info(f"📈 Dashboard Update {i+1}:")
            logger.info(
                f"  80/20 Opportunities: {dashboard.get('today_opportunities', {}).get('80/20', 0)}"
            )
            logger.info(
                f"  Dutching Opportunities: {dashboard.get('today_opportunities', {}).get('dutching', 0)}"
            )

            # Show performance metrics
            perf_80_20 = dashboard.get("strategy_performance", {}).get("80/20", {})
            perf_dutching = dashboard.get("strategy_performance", {}).get(
                "dutching", {}
            )

            logger.info(f"  80/20 ROI: {perf_80_20.get('roi_percentage', 0):.2f}%")
            logger.info(
                f"  Dutching ROI: {perf_dutching.get('roi_percentage', 0):.2f}%"
            )

        # Stop monitoring
        monitor.stop_monitoring()
        logger.info("✅ Live monitoring test completed")

    except KeyboardInterrupt:
        monitor.stop_monitoring()
        logger.info("⏹️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        monitor.stop_monitoring()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    main()
