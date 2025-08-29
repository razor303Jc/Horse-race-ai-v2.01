#!/usr/bin/env python3
"""
Trends & Performance Database Manager for Horse Racing AI v2.0
============================================================

Database operations for race trends analysis, AI betting performance,
and strategy effectiveness tracking.

Features:
- Race trends analysis storage and retrieval
- AI prediction performance tracking
- Betting strategy effectiveness monitoring
- ROI and strike rate calculations
- Performance pattern analysis
"""

import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RaceTrend:
    """Individual race trend data"""

    race_id: str
    trend_category: (
        str  # age, weight, draw, form, price, seasonal, course_form, distance_form
    )
    trend_type: str
    pattern_description: str
    confidence_score: float
    edge_value: float
    sample_size: int
    historical_strike_rate: float = 0.0
    significance_level: float = 0.0


@dataclass
class RaceAnalysisTrends:
    """Complete race analysis with trend data"""

    race_id: str
    track: str
    race_date: date
    distance: float
    surface: str
    race_class: str
    total_trends_identified: int
    high_confidence_trends: int
    overall_edge_rating: float
    trend_strength: str
    age_trends_count: int = 0
    age_trends_edge: float = 0.0
    weight_trends_count: int = 0
    weight_trends_edge: float = 0.0
    draw_trends_count: int = 0
    draw_trends_edge: float = 0.0
    form_trends_count: int = 0
    form_trends_edge: float = 0.0
    price_trends_count: int = 0
    price_trends_edge: float = 0.0
    seasonal_trends_count: int = 0
    seasonal_trends_edge: float = 0.0
    course_form_trends_count: int = 0
    course_form_trends_edge: float = 0.0
    distance_form_trends_count: int = 0
    distance_form_trends_edge: float = 0.0


@dataclass
class HorseTrendScore:
    """Horse scoring against race trends"""

    race_id: str
    horse_name: str
    overall_trend_score: float
    trend_rank: int
    trend_confidence: float
    age_trend_score: float = 0.0
    weight_trend_score: float = 0.0
    draw_trend_score: float = 0.0
    form_trend_score: float = 0.0
    price_trend_score: float = 0.0
    seasonal_trend_score: float = 0.0
    course_form_trend_score: float = 0.0
    distance_form_trend_score: float = 0.0
    positive_trends_count: int = 0
    negative_trends_count: int = 0
    neutral_trends_count: int = 0


@dataclass
class AIPrediction:
    """AI prediction record with performance tracking"""

    race_id: str
    horse_name: str
    raw_rating: float
    monte_carlo_rating: float
    ai_ml_rating: float
    consensus_rating: float
    raw_win_probability: float
    monte_carlo_win_probability: float
    ai_ml_win_probability: float
    consensus_win_probability: float
    prediction_confidence: float
    method_agreement_score: float
    prediction_consistency: float
    betting_odds: float
    implied_probability: float
    value_rating: float
    actual_finish_position: Optional[int] = None
    prediction_accuracy: float = 0.0
    prediction_timestamp: datetime = None


@dataclass
class BettingStrategy:
    """Betting strategy recommendation and result"""

    race_id: str
    horse_name: str
    strategy_type: str  # value_bet, dutching, each_way, twenty_eighty
    bet_type: str  # win, place, show, exacta, trifecta
    recommended_stake: float
    recommended_odds: float
    expected_value: float
    kelly_fraction: float
    confidence_score: float
    risk_rating: str
    staking_method: str
    staking_multiplier: float = 1.0
    actual_stake: float = 0.0
    actual_odds: float = 0.0
    bet_placed: bool = False
    actual_result: Optional[str] = None
    payout: float = 0.0
    profit_loss: float = 0.0
    roi_percentage: float = 0.0
    strategy_timestamp: datetime = None


@dataclass
class MethodPerformance:
    """AI method performance metrics"""

    method_name: str
    calculation_date: date
    total_predictions: int
    correct_predictions: int
    win_accuracy: float
    place_accuracy: float
    overall_accuracy: float
    total_bets: int = 0
    winning_bets: int = 0
    total_wagered: float = 0.0
    total_returned: float = 0.0
    net_profit: float = 0.0
    roi_percentage: float = 0.0
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    maximum_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    confidence_calibration: float = 0.0
    prediction_consistency: float = 0.0
    method_agreement: float = 0.0


@dataclass
class StrategyPerformance:
    """Betting strategy effectiveness metrics"""

    strategy_type: str
    calculation_date: date
    total_opportunities: int
    strategies_used: int
    usage_rate: float
    total_profit: float
    total_stakes: float
    roi_percentage: float
    win_rate: float
    average_odds: float
    value_capture_rate: float = 0.0
    dutching_efficiency: float = 0.0
    kelly_accuracy: float = 0.0
    maximum_loss: float = 0.0
    maximum_drawdown: float = 0.0
    volatility: float = 0.0
    consecutive_losses: int = 0
    high_confidence_success: float = 0.0
    medium_confidence_success: float = 0.0
    low_confidence_success: float = 0.0


class TrendsPerformanceDatabaseManager:
    """Database manager for trends and performance data"""

    def __init__(self, db_path: str = "data/trends_performance.db"):
        """Initialize database manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f"TrendsPerformanceDatabaseManager initialized with {db_path}")

    def _create_tables(self):
        """Create all necessary database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Race trends table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS race_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    trend_category TEXT NOT NULL,
                    trend_type TEXT NOT NULL,
                    pattern_description TEXT,
                    confidence_score REAL NOT NULL DEFAULT 0.0,
                    edge_value REAL NOT NULL DEFAULT 0.0,
                    sample_size INTEGER NOT NULL DEFAULT 0,
                    historical_strike_rate REAL DEFAULT 0.0,
                    significance_level REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_race_trends_race_id ON race_trends (race_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_race_trends_category ON race_trends (trend_category)"
            )

            # Race analysis trends table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS race_analysis_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL UNIQUE,
                    track TEXT,
                    race_date DATE,
                    distance REAL,
                    surface TEXT,
                    race_class TEXT,
                    total_trends_identified INTEGER NOT NULL DEFAULT 0,
                    high_confidence_trends INTEGER NOT NULL DEFAULT 0,
                    overall_edge_rating REAL NOT NULL DEFAULT 0.0,
                    trend_strength TEXT DEFAULT 'WEAK',
                    age_trends_count INTEGER DEFAULT 0,
                    age_trends_edge REAL DEFAULT 0.0,
                    weight_trends_count INTEGER DEFAULT 0,
                    weight_trends_edge REAL DEFAULT 0.0,
                    draw_trends_count INTEGER DEFAULT 0,
                    draw_trends_edge REAL DEFAULT 0.0,
                    form_trends_count INTEGER DEFAULT 0,
                    form_trends_edge REAL DEFAULT 0.0,
                    price_trends_count INTEGER DEFAULT 0,
                    price_trends_edge REAL DEFAULT 0.0,
                    seasonal_trends_count INTEGER DEFAULT 0,
                    seasonal_trends_edge REAL DEFAULT 0.0,
                    course_form_trends_count INTEGER DEFAULT 0,
                    course_form_trends_edge REAL DEFAULT 0.0,
                    distance_form_trends_count INTEGER DEFAULT 0,
                    distance_form_trends_edge REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Horse trend scores table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS horse_trend_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    overall_trend_score REAL NOT NULL DEFAULT 0.0,
                    trend_rank INTEGER DEFAULT 0,
                    trend_confidence REAL DEFAULT 0.0,
                    age_trend_score REAL DEFAULT 0.0,
                    weight_trend_score REAL DEFAULT 0.0,
                    draw_trend_score REAL DEFAULT 0.0,
                    form_trend_score REAL DEFAULT 0.0,
                    price_trend_score REAL DEFAULT 0.0,
                    seasonal_trend_score REAL DEFAULT 0.0,
                    course_form_trend_score REAL DEFAULT 0.0,
                    distance_form_trend_score REAL DEFAULT 0.0,
                    positive_trends_count INTEGER DEFAULT 0,
                    negative_trends_count INTEGER DEFAULT 0,
                    neutral_trends_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(race_id, horse_name)
                )
            """
            )

            # AI predictions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_rating REAL DEFAULT 0.0,
                    monte_carlo_rating REAL DEFAULT 0.0,
                    ai_ml_rating REAL DEFAULT 0.0,
                    consensus_rating REAL DEFAULT 0.0,
                    raw_win_probability REAL DEFAULT 0.0,
                    monte_carlo_win_probability REAL DEFAULT 0.0,
                    ai_ml_win_probability REAL DEFAULT 0.0,
                    consensus_win_probability REAL DEFAULT 0.0,
                    prediction_confidence REAL DEFAULT 0.0,
                    method_agreement_score REAL DEFAULT 0.0,
                    prediction_consistency REAL DEFAULT 0.0,
                    betting_odds REAL DEFAULT 0.0,
                    implied_probability REAL DEFAULT 0.0,
                    value_rating REAL DEFAULT 0.0,
                    actual_finish_position INTEGER DEFAULT NULL,
                    prediction_accuracy REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(race_id, horse_name)
                )
            """
            )

            # Betting strategies table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS betting_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    strategy_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    strategy_type TEXT NOT NULL,
                    bet_type TEXT NOT NULL,
                    recommended_stake REAL DEFAULT 0.0,
                    recommended_odds REAL DEFAULT 0.0,
                    expected_value REAL DEFAULT 0.0,
                    kelly_fraction REAL DEFAULT 0.0,
                    confidence_score REAL DEFAULT 0.0,
                    risk_rating TEXT DEFAULT 'MEDIUM',
                    staking_method TEXT DEFAULT 'percentage',
                    staking_multiplier REAL DEFAULT 1.0,
                    actual_stake REAL DEFAULT 0.0,
                    actual_odds REAL DEFAULT 0.0,
                    bet_placed INTEGER DEFAULT 0,
                    actual_result TEXT DEFAULT NULL,
                    payout REAL DEFAULT 0.0,
                    profit_loss REAL DEFAULT 0.0,
                    roi_percentage REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # AI method performance table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_method_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_name TEXT NOT NULL,
                    calculation_date DATE NOT NULL,
                    total_predictions INTEGER NOT NULL DEFAULT 0,
                    correct_predictions INTEGER NOT NULL DEFAULT 0,
                    win_accuracy REAL DEFAULT 0.0,
                    place_accuracy REAL DEFAULT 0.0,
                    overall_accuracy REAL DEFAULT 0.0,
                    total_bets INTEGER DEFAULT 0,
                    winning_bets INTEGER DEFAULT 0,
                    total_wagered REAL DEFAULT 0.0,
                    total_returned REAL DEFAULT 0.0,
                    net_profit REAL DEFAULT 0.0,
                    roi_percentage REAL DEFAULT 0.0,
                    win_rate REAL DEFAULT 0.0,
                    average_win REAL DEFAULT 0.0,
                    average_loss REAL DEFAULT 0.0,
                    profit_factor REAL DEFAULT 0.0,
                    maximum_drawdown REAL DEFAULT 0.0,
                    sharpe_ratio REAL DEFAULT 0.0,
                    confidence_calibration REAL DEFAULT 0.0,
                    prediction_consistency REAL DEFAULT 0.0,
                    method_agreement REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(method_name, calculation_date)
                )
            """
            )

            # Strategy performance table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_type TEXT NOT NULL,
                    calculation_date DATE NOT NULL,
                    total_opportunities INTEGER NOT NULL DEFAULT 0,
                    strategies_used INTEGER NOT NULL DEFAULT 0,
                    usage_rate REAL DEFAULT 0.0,
                    total_profit REAL DEFAULT 0.0,
                    total_stakes REAL DEFAULT 0.0,
                    roi_percentage REAL DEFAULT 0.0,
                    win_rate REAL DEFAULT 0.0,
                    average_odds REAL DEFAULT 0.0,
                    value_capture_rate REAL DEFAULT 0.0,
                    dutching_efficiency REAL DEFAULT 0.0,
                    kelly_accuracy REAL DEFAULT 0.0,
                    maximum_loss REAL DEFAULT 0.0,
                    maximum_drawdown REAL DEFAULT 0.0,
                    volatility REAL DEFAULT 0.0,
                    consecutive_losses INTEGER DEFAULT 0,
                    high_confidence_success REAL DEFAULT 0.0,
                    medium_confidence_success REAL DEFAULT 0.0,
                    low_confidence_success REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(strategy_type, calculation_date)
                )
            """
            )

            conn.commit()
            logger.info("Database tables created successfully")

    # Race Trends Methods
    # =======================================

    def save_race_trend(self, trend: RaceTrend) -> int:
        """Save a race trend pattern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO race_trends (
                    race_id, trend_category, trend_type, pattern_description,
                    confidence_score, edge_value, sample_size,
                    historical_strike_rate, significance_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    trend.race_id,
                    trend.trend_category,
                    trend.trend_type,
                    trend.pattern_description,
                    trend.confidence_score,
                    trend.edge_value,
                    trend.sample_size,
                    trend.historical_strike_rate,
                    trend.significance_level,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_race_analysis_trends(self, analysis: RaceAnalysisTrends) -> int:
        """Save complete race analysis with trends"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO race_analysis_trends (
                    race_id, track, race_date, distance, surface, race_class,
                    total_trends_identified, high_confidence_trends,
                    overall_edge_rating, trend_strength,
                    age_trends_count, age_trends_edge,
                    weight_trends_count, weight_trends_edge,
                    draw_trends_count, draw_trends_edge,
                    form_trends_count, form_trends_edge,
                    price_trends_count, price_trends_edge,
                    seasonal_trends_count, seasonal_trends_edge,
                    course_form_trends_count, course_form_trends_edge,
                    distance_form_trends_count, distance_form_trends_edge
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis.race_id,
                    analysis.track,
                    analysis.race_date.isoformat() if analysis.race_date else None,
                    analysis.distance,
                    analysis.surface,
                    analysis.race_class,
                    analysis.total_trends_identified,
                    analysis.high_confidence_trends,
                    analysis.overall_edge_rating,
                    analysis.trend_strength,
                    analysis.age_trends_count,
                    analysis.age_trends_edge,
                    analysis.weight_trends_count,
                    analysis.weight_trends_edge,
                    analysis.draw_trends_count,
                    analysis.draw_trends_edge,
                    analysis.form_trends_count,
                    analysis.form_trends_edge,
                    analysis.price_trends_count,
                    analysis.price_trends_edge,
                    analysis.seasonal_trends_count,
                    analysis.seasonal_trends_edge,
                    analysis.course_form_trends_count,
                    analysis.course_form_trends_edge,
                    analysis.distance_form_trends_count,
                    analysis.distance_form_trends_edge,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_horse_trend_score(self, score: HorseTrendScore) -> int:
        """Save horse trend scoring data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO horse_trend_scores (
                    race_id, horse_name, overall_trend_score, trend_rank,
                    trend_confidence, age_trend_score, weight_trend_score,
                    draw_trend_score, form_trend_score, price_trend_score,
                    seasonal_trend_score, course_form_trend_score,
                    distance_form_trend_score, positive_trends_count,
                    negative_trends_count, neutral_trends_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    score.race_id,
                    score.horse_name,
                    score.overall_trend_score,
                    score.trend_rank,
                    score.trend_confidence,
                    score.age_trend_score,
                    score.weight_trend_score,
                    score.draw_trend_score,
                    score.form_trend_score,
                    score.price_trend_score,
                    score.seasonal_trend_score,
                    score.course_form_trend_score,
                    score.distance_form_trend_score,
                    score.positive_trends_count,
                    score.negative_trends_count,
                    score.neutral_trends_count,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    # AI Performance Methods
    # =======================================

    def save_ai_prediction(self, prediction: AIPrediction) -> int:
        """Save AI prediction data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            timestamp = prediction.prediction_timestamp or datetime.now()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ai_predictions (
                    race_id, horse_name, prediction_timestamp,
                    raw_rating, monte_carlo_rating, ai_ml_rating, consensus_rating,
                    raw_win_probability, monte_carlo_win_probability,
                    ai_ml_win_probability, consensus_win_probability,
                    prediction_confidence, method_agreement_score,
                    prediction_consistency, betting_odds, implied_probability,
                    value_rating, actual_finish_position, prediction_accuracy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    prediction.race_id,
                    prediction.horse_name,
                    timestamp.isoformat(),
                    prediction.raw_rating,
                    prediction.monte_carlo_rating,
                    prediction.ai_ml_rating,
                    prediction.consensus_rating,
                    prediction.raw_win_probability,
                    prediction.monte_carlo_win_probability,
                    prediction.ai_ml_win_probability,
                    prediction.consensus_win_probability,
                    prediction.prediction_confidence,
                    prediction.method_agreement_score,
                    prediction.prediction_consistency,
                    prediction.betting_odds,
                    prediction.implied_probability,
                    prediction.value_rating,
                    prediction.actual_finish_position,
                    prediction.prediction_accuracy,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_betting_strategy(self, strategy: BettingStrategy) -> int:
        """Save betting strategy data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            timestamp = strategy.strategy_timestamp or datetime.now()
            cursor.execute(
                """
                INSERT INTO betting_strategies (
                    race_id, horse_name, strategy_timestamp, strategy_type, bet_type,
                    recommended_stake, recommended_odds, expected_value,
                    kelly_fraction, confidence_score, risk_rating,
                    staking_method, staking_multiplier, actual_stake,
                    actual_odds, bet_placed, actual_result, payout,
                    profit_loss, roi_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    strategy.race_id,
                    strategy.horse_name,
                    timestamp.isoformat(),
                    strategy.strategy_type,
                    strategy.bet_type,
                    strategy.recommended_stake,
                    strategy.recommended_odds,
                    strategy.expected_value,
                    strategy.kelly_fraction,
                    strategy.confidence_score,
                    strategy.risk_rating,
                    strategy.staking_method,
                    strategy.staking_multiplier,
                    strategy.actual_stake,
                    strategy.actual_odds,
                    1 if strategy.bet_placed else 0,
                    strategy.actual_result,
                    strategy.payout,
                    strategy.profit_loss,
                    strategy.roi_percentage,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_method_performance(self, performance: MethodPerformance) -> int:
        """Save AI method performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ai_method_performance (
                    method_name, calculation_date, total_predictions,
                    correct_predictions, win_accuracy, place_accuracy,
                    overall_accuracy, total_bets, winning_bets,
                    total_wagered, total_returned, net_profit,
                    roi_percentage, win_rate, average_win, average_loss,
                    profit_factor, maximum_drawdown, sharpe_ratio,
                    confidence_calibration, prediction_consistency, method_agreement
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    performance.method_name,
                    performance.calculation_date.isoformat(),
                    performance.total_predictions,
                    performance.correct_predictions,
                    performance.win_accuracy,
                    performance.place_accuracy,
                    performance.overall_accuracy,
                    performance.total_bets,
                    performance.winning_bets,
                    performance.total_wagered,
                    performance.total_returned,
                    performance.net_profit,
                    performance.roi_percentage,
                    performance.win_rate,
                    performance.average_win,
                    performance.average_loss,
                    performance.profit_factor,
                    performance.maximum_drawdown,
                    performance.sharpe_ratio,
                    performance.confidence_calibration,
                    performance.prediction_consistency,
                    performance.method_agreement,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_strategy_performance(self, performance: StrategyPerformance) -> int:
        """Save betting strategy performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO strategy_performance (
                    strategy_type, calculation_date, total_opportunities,
                    strategies_used, usage_rate, total_profit, total_stakes,
                    roi_percentage, win_rate, average_odds, value_capture_rate,
                    dutching_efficiency, kelly_accuracy, maximum_loss,
                    maximum_drawdown, volatility, consecutive_losses,
                    high_confidence_success, medium_confidence_success,
                    low_confidence_success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    performance.strategy_type,
                    performance.calculation_date.isoformat(),
                    performance.total_opportunities,
                    performance.strategies_used,
                    performance.usage_rate,
                    performance.total_profit,
                    performance.total_stakes,
                    performance.roi_percentage,
                    performance.win_rate,
                    performance.average_odds,
                    performance.value_capture_rate,
                    performance.dutching_efficiency,
                    performance.kelly_accuracy,
                    performance.maximum_loss,
                    performance.maximum_drawdown,
                    performance.volatility,
                    performance.consecutive_losses,
                    performance.high_confidence_success,
                    performance.medium_confidence_success,
                    performance.low_confidence_success,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    # Query Methods
    # =======================================

    def get_race_trends(self, race_id: str) -> List[RaceTrend]:
        """Get all trends for a specific race"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT race_id, trend_category, trend_type, pattern_description,
                       confidence_score, edge_value, sample_size,
                       historical_strike_rate, significance_level
                FROM race_trends
                WHERE race_id = ?
                ORDER BY confidence_score DESC
            """,
                (race_id,),
            )

            trends = []
            for row in cursor.fetchall():
                trends.append(
                    RaceTrend(
                        race_id=row[0],
                        trend_category=row[1],
                        trend_type=row[2],
                        pattern_description=row[3],
                        confidence_score=row[4],
                        edge_value=row[5],
                        sample_size=row[6],
                        historical_strike_rate=row[7],
                        significance_level=row[8],
                    )
                )
            return trends

    def get_race_analysis_trends(self, race_id: str) -> Optional[RaceAnalysisTrends]:
        """Get race analysis with trends"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT race_id, track, race_date, distance, surface, race_class,
                       total_trends_identified, high_confidence_trends,
                       overall_edge_rating, trend_strength,
                       age_trends_count, age_trends_edge,
                       weight_trends_count, weight_trends_edge,
                       draw_trends_count, draw_trends_edge,
                       form_trends_count, form_trends_edge,
                       price_trends_count, price_trends_edge,
                       seasonal_trends_count, seasonal_trends_edge,
                       course_form_trends_count, course_form_trends_edge,
                       distance_form_trends_count, distance_form_trends_edge
                FROM race_analysis_trends
                WHERE race_id = ?
            """,
                (race_id,),
            )

            row = cursor.fetchone()
            if row:
                return RaceAnalysisTrends(
                    race_id=row[0],
                    track=row[1],
                    race_date=datetime.fromisoformat(row[2]).date() if row[2] else None,
                    distance=row[3],
                    surface=row[4],
                    race_class=row[5],
                    total_trends_identified=row[6],
                    high_confidence_trends=row[7],
                    overall_edge_rating=row[8],
                    trend_strength=row[9],
                    age_trends_count=row[10],
                    age_trends_edge=row[11],
                    weight_trends_count=row[12],
                    weight_trends_edge=row[13],
                    draw_trends_count=row[14],
                    draw_trends_edge=row[15],
                    form_trends_count=row[16],
                    form_trends_edge=row[17],
                    price_trends_count=row[18],
                    price_trends_edge=row[19],
                    seasonal_trends_count=row[20],
                    seasonal_trends_edge=row[21],
                    course_form_trends_count=row[22],
                    course_form_trends_edge=row[23],
                    distance_form_trends_count=row[24],
                    distance_form_trends_edge=row[25],
                )
            return None

    def get_method_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get method performance summary for recent period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT method_name, 
                       AVG(overall_accuracy) as avg_accuracy,
                       AVG(roi_percentage) as avg_roi,
                       AVG(win_rate) as avg_win_rate,
                       AVG(profit_factor) as avg_profit_factor,
                       AVG(maximum_drawdown) as avg_drawdown,
                       COUNT(*) as records_count
                FROM ai_method_performance
                WHERE calculation_date >= DATE('now', '-{} days')
                GROUP BY method_name
                ORDER BY avg_roi DESC
            """.format(
                    days
                )
            )

            summary = {}
            for row in cursor.fetchall():
                summary[row[0]] = {
                    "avg_accuracy": row[1],
                    "avg_roi": row[2],
                    "avg_win_rate": row[3],
                    "avg_profit_factor": row[4],
                    "avg_drawdown": row[5],
                    "records_count": row[6],
                }
            return summary

    def get_strategy_effectiveness_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get strategy effectiveness summary for recent period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT strategy_type,
                       AVG(roi_percentage) as avg_roi,
                       AVG(win_rate) as avg_win_rate,
                       AVG(usage_rate) as avg_usage_rate,
                       AVG(value_capture_rate) as avg_value_capture,
                       SUM(total_profit) as total_profit,
                       SUM(total_stakes) as total_stakes,
                       COUNT(*) as records_count
                FROM strategy_performance
                WHERE calculation_date >= DATE('now', '-{} days')
                GROUP BY strategy_type
                ORDER BY avg_roi DESC
            """.format(
                    days
                )
            )

            summary = {}
            for row in cursor.fetchall():
                summary[row[0]] = {
                    "avg_roi": row[1],
                    "avg_win_rate": row[2],
                    "avg_usage_rate": row[3],
                    "avg_value_capture": row[4],
                    "total_profit": row[5],
                    "total_stakes": row[6],
                    "overall_roi": (row[5] / row[6] * 100) if row[6] > 0 else 0,
                    "records_count": row[7],
                }
            return summary

    def get_comprehensive_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        method_summary = self.get_method_performance_summary(days)
        strategy_summary = self.get_strategy_effectiveness_summary(days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Overall statistics
            cursor.execute(
                """
                SELECT COUNT(DISTINCT race_id) as total_races,
                       COUNT(*) as total_predictions,
                       AVG(prediction_accuracy) as avg_accuracy
                FROM ai_predictions
                WHERE prediction_timestamp >= DATETIME('now', '-{} days')
            """.format(
                    days
                )
            )
            overall_stats = cursor.fetchone()

            # Betting statistics
            cursor.execute(
                """
                SELECT COUNT(*) as total_bets,
                       SUM(actual_stake) as total_stakes,
                       SUM(payout) as total_payouts,
                       SUM(profit_loss) as total_profit,
                       AVG(roi_percentage) as avg_roi,
                       COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as winning_bets
                FROM betting_strategies
                WHERE strategy_timestamp >= DATETIME('now', '-{} days')
                AND bet_placed = 1
            """.format(
                    days
                )
            )
            betting_stats = cursor.fetchone()

            # Trends statistics
            cursor.execute(
                """
                SELECT COUNT(DISTINCT race_id) as races_with_trends,
                       AVG(total_trends_identified) as avg_trends_per_race,
                       AVG(overall_edge_rating) as avg_edge_rating,
                       COUNT(CASE WHEN trend_strength = 'STRONG' THEN 1 END) as strong_trend_races
                FROM race_analysis_trends
                WHERE created_at >= DATETIME('now', '-{} days')
            """.format(
                    days
                )
            )
            trends_stats = cursor.fetchone()

        # Calculate win rate safely
        win_rate = 0.0
        if betting_stats and betting_stats[0] and betting_stats[5] is not None:
            win_rate = betting_stats[5] / betting_stats[0] * 100

        return {
            "period_days": days,
            "overall_statistics": {
                "total_races": overall_stats[0] if overall_stats else 0,
                "total_predictions": overall_stats[1] if overall_stats else 0,
                "avg_prediction_accuracy": overall_stats[2] if overall_stats else 0.0,
            },
            "betting_statistics": {
                "total_bets": betting_stats[0] if betting_stats else 0,
                "total_stakes": betting_stats[1] if betting_stats else 0.0,
                "total_payouts": betting_stats[2] if betting_stats else 0.0,
                "total_profit": betting_stats[3] if betting_stats else 0.0,
                "avg_roi": betting_stats[4] if betting_stats else 0.0,
                "winning_bets": betting_stats[5] if betting_stats else 0,
                "win_rate": win_rate,
            },
            "trends_statistics": {
                "races_with_trends": trends_stats[0] if trends_stats else 0,
                "avg_trends_per_race": trends_stats[1] if trends_stats else 0.0,
                "avg_edge_rating": trends_stats[2] if trends_stats else 0.0,
                "strong_trend_races": trends_stats[3] if trends_stats else 0,
            },
            "method_performance": method_summary,
            "strategy_effectiveness": strategy_summary,
        }

    def export_performance_data(
        self, output_path: str = "data/performance_export.csv"
    ) -> str:
        """Export comprehensive performance data to CSV"""
        with sqlite3.connect(self.db_path) as conn:
            # Export AI predictions with results
            query = """
                SELECT ap.*, rat.overall_edge_rating, rat.trend_strength
                FROM ai_predictions ap
                LEFT JOIN race_analysis_trends rat ON ap.race_id = rat.race_id
                ORDER BY ap.prediction_timestamp DESC
            """
            df = pd.read_sql_query(query, conn)
            df.to_csv(output_path, index=False)

        logger.info(f"Performance data exported to {output_path}")
        return output_path
