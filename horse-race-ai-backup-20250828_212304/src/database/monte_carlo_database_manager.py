#!/usr/bin/env python3
"""
Monte Carlo Database Integration for Horse Racing AI v2.0
========================================================

Extends the database integration to include Monte Carlo simulation data,
analysis results, and betting recommendations with comprehensive tracking.

Features:
- Monte Carlo simulation data storage
- Performance profile tracking
- Win probability analysis
- Betting recommendation storage
- Historical simulation tracking
"""

import logging
import sqlite3
import csv
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json

import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class MonteCarloSimulation:
    """Monte Carlo simulation record"""

    id: Optional[int] = None
    race_id: str = ""
    simulation_timestamp: datetime = None
    simulations_run: int = 0
    simulation_reliability: float = 0.0
    field_size: int = 0
    field_mean_rating: float = 0.0
    field_std_deviation: float = 0.0
    simulation_parameters: str = ""  # JSON string
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MonteCarloHorseProfile:
    """Monte Carlo horse performance profile"""

    id: Optional[int] = None
    simulation_id: int = 0
    race_id: str = ""
    horse_name: str = ""
    mean_rating: float = 0.0
    std_deviation: float = 0.0
    z_score: float = 0.0
    consistency_factor: float = 0.0
    form_trend: float = 0.0
    confidence_level: float = 0.0
    performance_range_min: float = 0.0
    performance_range_max: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MonteCarloResults:
    """Monte Carlo simulation results"""

    id: Optional[int] = None
    simulation_id: int = 0
    race_id: str = ""
    horse_name: str = ""
    win_probability: float = 0.0
    place_probability: float = 0.0
    show_probability: float = 0.0
    average_position: float = 0.0
    confidence_interval_lower: float = 0.0
    confidence_interval_upper: float = 0.0
    performance_variance: float = 0.0
    simulation_rank: int = 0
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MonteCarloBettingRecommendation:
    """Monte Carlo betting recommendation"""

    id: Optional[int] = None
    simulation_id: int = 0
    race_id: str = ""
    horse_name: str = ""
    bet_type: str = ""  # win, place, each_way
    recommended_stake: float = 0.0
    recommended_odds: float = 0.0
    fair_odds: float = 0.0
    expected_value: float = 0.0
    kelly_fraction: float = 0.0
    confidence_score: float = 0.0
    risk_rating: str = ""  # LOW, MEDIUM, HIGH
    betting_value: float = 0.0
    recommendation_strength: str = ""  # WEAK, MODERATE, STRONG
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MonteCarloPerformanceTracking:
    """Monte Carlo performance tracking"""

    id: Optional[int] = None
    simulation_id: int = 0
    race_id: str = ""
    track_date: date = None
    horses_analyzed: int = 0
    predictions_made: int = 0
    betting_recommendations: int = 0
    average_confidence: float = 0.0
    high_confidence_picks: int = 0
    simulation_accuracy: float = 0.0  # Will be updated when results come in
    actual_winners_predicted: int = 0
    roi_performance: float = 0.0
    profitability_score: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None


class MonteCarloFastResultsCollector:
    """Fast results collector for Monte Carlo predictions"""

    def __init__(self, database_path: str = "data/monte_carlo_database.db"):
        self.database_path = database_path
        self.ensure_data_directory()
        self.init_database()
        logger.info(
            f"MonteCarloFastResultsCollector initialized with database: {database_path}"
        )

    def ensure_data_directory(self):
        """Ensure data directory exists"""
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

    def init_database(self):
        """Initialize Monte Carlo database tables"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Monte Carlo simulations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monte_carlo_simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id TEXT NOT NULL,
                    simulation_timestamp DATETIME NOT NULL,
                    simulations_run INTEGER NOT NULL,
                    simulation_reliability REAL NOT NULL,
                    field_size INTEGER NOT NULL,
                    field_mean_rating REAL NOT NULL,
                    field_std_deviation REAL NOT NULL,
                    simulation_parameters TEXT, -- JSON parameters
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Horse performance profiles table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monte_carlo_horse_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER NOT NULL,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    mean_rating REAL NOT NULL,
                    std_deviation REAL NOT NULL,
                    z_score REAL NOT NULL,
                    consistency_factor REAL NOT NULL,
                    form_trend REAL NOT NULL,
                    confidence_level REAL NOT NULL,
                    performance_range_min REAL NOT NULL,
                    performance_range_max REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES monte_carlo_simulations(id)
                )
            """
            )

            # Simulation results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monte_carlo_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER NOT NULL,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    win_probability REAL NOT NULL,
                    place_probability REAL NOT NULL,
                    show_probability REAL NOT NULL,
                    average_position REAL NOT NULL,
                    confidence_interval_lower REAL NOT NULL,
                    confidence_interval_upper REAL NOT NULL,
                    performance_variance REAL NOT NULL,
                    simulation_rank INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES monte_carlo_simulations(id)
                )
            """
            )

            # Betting recommendations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monte_carlo_betting_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER NOT NULL,
                    race_id TEXT NOT NULL,
                    horse_name TEXT NOT NULL,
                    bet_type TEXT NOT NULL,
                    recommended_stake REAL NOT NULL,
                    recommended_odds REAL NOT NULL,
                    fair_odds REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    kelly_fraction REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    risk_rating TEXT NOT NULL,
                    betting_value REAL NOT NULL,
                    recommendation_strength TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES monte_carlo_simulations(id)
                )
            """
            )

            # Performance tracking table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monte_carlo_performance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER NOT NULL,
                    race_id TEXT NOT NULL,
                    track_date DATE NOT NULL,
                    horses_analyzed INTEGER NOT NULL,
                    predictions_made INTEGER NOT NULL,
                    betting_recommendations INTEGER NOT NULL,
                    average_confidence REAL NOT NULL,
                    high_confidence_picks INTEGER NOT NULL,
                    simulation_accuracy REAL DEFAULT 0.0,
                    actual_winners_predicted INTEGER DEFAULT 0,
                    roi_performance REAL DEFAULT 0.0,
                    profitability_score REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES monte_carlo_simulations(id)
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_sims_race_id
                ON monte_carlo_simulations (race_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_sims_timestamp
                ON monte_carlo_simulations (simulation_timestamp)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_profiles_sim_id
                ON monte_carlo_horse_profiles (simulation_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_profiles_horse
                ON monte_carlo_horse_profiles (horse_name)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_results_sim_id
                ON monte_carlo_results (simulation_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_results_horse
                ON monte_carlo_results (horse_name)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_betting_sim_id
                ON monte_carlo_betting_recommendations (simulation_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_betting_horse
                ON monte_carlo_betting_recommendations (horse_name)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mc_tracking_date
                ON monte_carlo_performance_tracking (track_date)
            """
            )

            conn.commit()
            logger.info("Monte Carlo database tables created successfully")

    # Monte Carlo Simulation CRUD Operations
    # =====================================

    def store_monte_carlo_simulation(self, simulation: MonteCarloSimulation) -> int:
        """Store Monte Carlo simulation record"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO monte_carlo_simulations (
                    race_id, simulation_timestamp, simulations_run,
                    simulation_reliability, field_size, field_mean_rating,
                    field_std_deviation, simulation_parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    simulation.race_id,
                    simulation.simulation_timestamp or datetime.now(),
                    simulation.simulations_run,
                    simulation.simulation_reliability,
                    simulation.field_size,
                    simulation.field_mean_rating,
                    simulation.field_std_deviation,
                    simulation.simulation_parameters,
                ),
            )

            simulation_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Monte Carlo simulation stored with ID: {simulation_id}")
            return simulation_id

    def store_horse_profiles(self, profiles: List[MonteCarloHorseProfile]) -> List[int]:
        """Store Monte Carlo horse profiles"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            profile_ids = []
            for profile in profiles:
                cursor.execute(
                    """
                    INSERT INTO monte_carlo_horse_profiles (
                        simulation_id, race_id, horse_name, mean_rating, std_deviation,
                        z_score, consistency_factor, form_trend, confidence_level,
                        performance_range_min, performance_range_max
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.simulation_id,
                        profile.race_id,
                        profile.horse_name,
                        profile.mean_rating,
                        profile.std_deviation,
                        profile.z_score,
                        profile.consistency_factor,
                        profile.form_trend,
                        profile.confidence_level,
                        profile.performance_range_min,
                        profile.performance_range_max,
                    ),
                )

                profile_ids.append(cursor.lastrowid)

            conn.commit()
            logger.info(f"Stored {len(profile_ids)} horse profiles")
            return profile_ids

    def store_simulation_results(self, results: List[MonteCarloResults]) -> List[int]:
        """Store Monte Carlo simulation results"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            result_ids = []
            for result in results:
                cursor.execute(
                    """
                    INSERT INTO monte_carlo_results (
                        simulation_id, race_id, horse_name, win_probability,
                        place_probability, show_probability, average_position,
                        confidence_interval_lower, confidence_interval_upper,
                        performance_variance, simulation_rank
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.simulation_id,
                        result.race_id,
                        result.horse_name,
                        result.win_probability,
                        result.place_probability,
                        result.show_probability,
                        result.average_position,
                        result.confidence_interval_lower,
                        result.confidence_interval_upper,
                        result.performance_variance,
                        result.simulation_rank,
                    ),
                )

                result_ids.append(cursor.lastrowid)

            conn.commit()
            logger.info(f"Stored {len(result_ids)} simulation results")
            return result_ids

    def store_betting_recommendations(
        self, recommendations: List[MonteCarloBettingRecommendation]
    ) -> List[int]:
        """Store Monte Carlo betting recommendations"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            rec_ids = []
            for rec in recommendations:
                cursor.execute(
                    """
                    INSERT INTO monte_carlo_betting_recommendations (
                        simulation_id, race_id, horse_name, bet_type,
                        recommended_stake, recommended_odds, fair_odds,
                        expected_value, kelly_fraction, confidence_score,
                        risk_rating, betting_value, recommendation_strength
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        rec.simulation_id,
                        rec.race_id,
                        rec.horse_name,
                        rec.bet_type,
                        rec.recommended_stake,
                        rec.recommended_odds,
                        rec.fair_odds,
                        rec.expected_value,
                        rec.kelly_fraction,
                        rec.confidence_score,
                        rec.risk_rating,
                        rec.betting_value,
                        rec.recommendation_strength,
                    ),
                )

                rec_ids.append(cursor.lastrowid)

            conn.commit()
            logger.info(f"Stored {len(rec_ids)} betting recommendations")
            return rec_ids

    def store_performance_tracking(
        self, tracking: MonteCarloPerformanceTracking
    ) -> int:
        """Store Monte Carlo performance tracking"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO monte_carlo_performance_tracking (
                    simulation_id, race_id, track_date, horses_analyzed,
                    predictions_made, betting_recommendations, average_confidence,
                    high_confidence_picks, simulation_accuracy,
                    actual_winners_predicted, roi_performance,
                    profitability_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tracking.simulation_id,
                    tracking.race_id,
                    tracking.track_date or date.today(),
                    tracking.horses_analyzed,
                    tracking.predictions_made,
                    tracking.betting_recommendations,
                    tracking.average_confidence,
                    tracking.high_confidence_picks,
                    tracking.simulation_accuracy,
                    tracking.actual_winners_predicted,
                    tracking.roi_performance,
                    tracking.profitability_score,
                ),
            )

            tracking_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Performance tracking stored with ID: {tracking_id}")
            return tracking_id

    # Query and Analysis Methods
    # =========================

    def get_monte_carlo_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get Monte Carlo performance summary"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Overall statistics
            cursor.execute(
                """
                SELECT COUNT(*) as total_simulations,
                       AVG(simulation_reliability) as avg_reliability,
                       AVG(field_size) as avg_field_size,
                       COUNT(DISTINCT race_id) as unique_races
                FROM monte_carlo_simulations
                WHERE simulation_timestamp >= DATETIME('now', '-{} days')
            """.format(
                    days
                )
            )
            overall_stats = cursor.fetchone()

            # Prediction accuracy
            cursor.execute(
                """
                SELECT AVG(simulation_accuracy) as avg_accuracy,
                       AVG(actual_winners_predicted) as avg_winners_predicted,
                       AVG(roi_performance) as avg_roi,
                       COUNT(*) as tracked_races
                FROM monte_carlo_performance_tracking
                WHERE track_date >= DATE('now', '-{} days')
            """.format(
                    days
                )
            )
            accuracy_stats = cursor.fetchone()

            # Betting recommendations
            cursor.execute(
                """
                SELECT COUNT(*) as total_recommendations,
                       AVG(expected_value) as avg_expected_value,
                       AVG(confidence_score) as avg_confidence,
                       COUNT(CASE WHEN recommendation_strength = 'STRONG'
                                  THEN 1 END) as strong_recommendations
                FROM monte_carlo_betting_recommendations mcbr
                JOIN monte_carlo_simulations mcs ON mcbr.simulation_id = mcs.id
                WHERE mcs.simulation_timestamp >= DATETIME('now', '-{} days')
            """.format(
                    days
                )
            )
            betting_stats = cursor.fetchone()

            return {
                "period_days": days,
                "overall_statistics": {
                    "total_simulations": overall_stats[0] if overall_stats else 0,
                    "avg_reliability": overall_stats[1] if overall_stats else 0.0,
                    "avg_field_size": overall_stats[2] if overall_stats else 0.0,
                    "unique_races": overall_stats[3] if overall_stats else 0,
                },
                "accuracy_statistics": {
                    "avg_accuracy": accuracy_stats[0] if accuracy_stats else 0.0,
                    "avg_winners_predicted": (
                        accuracy_stats[1] if accuracy_stats else 0.0
                    ),
                    "avg_roi": accuracy_stats[2] if accuracy_stats else 0.0,
                    "tracked_races": accuracy_stats[3] if accuracy_stats else 0,
                },
                "betting_statistics": {
                    "total_recommendations": betting_stats[0] if betting_stats else 0,
                    "avg_expected_value": betting_stats[1] if betting_stats else 0.0,
                    "avg_confidence": betting_stats[2] if betting_stats else 0.0,
                    "strong_recommendations": betting_stats[3] if betting_stats else 0,
                },
            }

    def get_top_monte_carlo_picks(
        self, race_id: str = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top Monte Carlo picks"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT mcr.race_id, mcr.horse_name, mcr.win_probability,
                       mcr.average_position, mcp.confidence_level, mcp.z_score,
                       mcbr.expected_value, mcbr.recommendation_strength
                FROM monte_carlo_results mcr
                JOIN monte_carlo_horse_profiles mcp ON mcr.simulation_id = mcp.simulation_id 
                     AND mcr.horse_name = mcp.horse_name
                LEFT JOIN monte_carlo_betting_recommendations mcbr ON mcr.simulation_id = mcbr.simulation_id 
                     AND mcr.horse_name = mcbr.horse_name
            """

            params = []
            if race_id:
                query += " WHERE mcr.race_id = ?"
                params.append(race_id)

            query += " ORDER BY mcr.win_probability DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()

            picks = []
            for row in results:
                picks.append(
                    {
                        "race_id": row[0],
                        "horse_name": row[1],
                        "win_probability": row[2],
                        "average_position": row[3],
                        "confidence_level": row[4],
                        "z_score": row[5],
                        "expected_value": row[6] or 0.0,
                        "recommendation_strength": row[7] or "NONE",
                    }
                )

            return picks

    def export_monte_carlo_data(
        self, output_path: str = "data/monte_carlo_export.csv"
    ) -> str:
        """Export Monte Carlo data to CSV"""
        with sqlite3.connect(self.database_path) as conn:
            query = """
                SELECT mcs.race_id, mcs.simulation_timestamp, mcs.simulations_run,
                       mcs.simulation_reliability, mcr.horse_name, mcr.win_probability,
                       mcr.place_probability, mcr.average_position, mcp.z_score,
                       mcp.confidence_level, mcbr.expected_value, mcbr.recommendation_strength,
                       mcpt.simulation_accuracy, mcpt.roi_performance
                FROM monte_carlo_simulations mcs
                JOIN monte_carlo_results mcr ON mcs.id = mcr.simulation_id
                JOIN monte_carlo_horse_profiles mcp ON mcs.id = mcp.simulation_id 
                     AND mcr.horse_name = mcp.horse_name
                LEFT JOIN monte_carlo_betting_recommendations mcbr ON mcs.id = mcbr.simulation_id 
                     AND mcr.horse_name = mcbr.horse_name
                LEFT JOIN monte_carlo_performance_tracking mcpt ON mcs.id = mcpt.simulation_id
                ORDER BY mcs.simulation_timestamp DESC, mcr.win_probability DESC
            """
            df = pd.read_sql_query(query, conn)
            df.to_csv(output_path, index=False)

        logger.info(f"Monte Carlo data exported to {output_path}")
        return output_path


# Integration Manager for Monte Carlo
# ===================================


class MonteCarloIntegrationManager:
    """Integration manager for Monte Carlo simulations with database storage"""

    def __init__(self, database_path: str = "data/monte_carlo_database.db"):
        self.database_path = database_path
        self.db_manager = MonteCarloFastResultsCollector(database_path)
        # Ensure database is properly initialized
        self.db_manager.init_database()
        logger.info("MonteCarloIntegrationManager initialized")

    def process_monte_carlo_analysis(
        self, analysis, race_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and store complete Monte Carlo analysis"""
        try:
            # Extract simulation parameters
            simulation_params = {
                "simulations": analysis.simulations_run,
                "field_size": len(analysis.horse_profiles),
                "reliability_threshold": 0.8,
            }

            # Store simulation record
            simulation = MonteCarloSimulation(
                race_id=analysis.race_id,
                simulation_timestamp=datetime.now(),
                simulations_run=analysis.simulations_run,
                simulation_reliability=analysis.simulation_reliability,
                field_size=len(analysis.horse_profiles),
                field_mean_rating=sum(p.mean_rating for p in analysis.horse_profiles)
                / len(analysis.horse_profiles),
                field_std_deviation=analysis.simulation_reliability,  # Approximation
                simulation_parameters=json.dumps(simulation_params),
            )

            simulation_id = self.db_manager.store_monte_carlo_simulation(simulation)

            # Store horse profiles
            profiles = []
            for profile in analysis.horse_profiles:
                mc_profile = MonteCarloHorseProfile(
                    simulation_id=simulation_id,
                    race_id=analysis.race_id,
                    horse_name=profile.horse_name,
                    mean_rating=profile.mean_rating,
                    std_deviation=profile.std_deviation,
                    z_score=profile.z_score,
                    consistency_factor=profile.consistency_factor,
                    form_trend=profile.form_trend,
                    confidence_level=profile.confidence_level,
                    performance_range_min=profile.performance_range[0],
                    performance_range_max=profile.performance_range[1],
                )
                profiles.append(mc_profile)

            self.db_manager.store_horse_profiles(profiles)

            # Store simulation results
            results = []
            for horse_name, win_prob in analysis.win_probabilities.items():
                result = MonteCarloResults(
                    simulation_id=simulation_id,
                    race_id=analysis.race_id,
                    horse_name=horse_name,
                    win_probability=win_prob,
                    place_probability=analysis.place_probabilities.get(horse_name, 0.0),
                    show_probability=analysis.show_probabilities.get(horse_name, 0.0),
                    average_position=analysis.average_positions.get(horse_name, 0.0),
                    confidence_interval_lower=analysis.confidence_intervals.get(
                        horse_name, (0.0, 0.0)
                    )[0],
                    confidence_interval_upper=analysis.confidence_intervals.get(
                        horse_name, (0.0, 0.0)
                    )[1],
                    performance_variance=0.0,  # Calculate from performance distributions if needed
                    simulation_rank=list(analysis.win_probabilities.keys()).index(
                        horse_name
                    )
                    + 1,
                )
                results.append(result)

            self.db_manager.store_simulation_results(results)

            return {
                "success": True,
                "simulation_id": simulation_id,
                "horses_analyzed": len(analysis.horse_profiles),
                "simulations_run": analysis.simulations_run,
                "reliability": analysis.simulation_reliability,
                "message": f"Monte Carlo analysis stored for race {analysis.race_id}",
            }

        except Exception as e:
            logger.error(f"Error processing Monte Carlo analysis: {e}")
            return {"success": False, "error": str(e)}

    def store_betting_recommendations(
        self, recommendations: List[Dict[str, Any]], simulation_id: int, race_id: str
    ) -> Dict[str, Any]:
        """Store Monte Carlo betting recommendations"""
        try:
            mc_recommendations = []

            for rec in recommendations:
                mc_rec = MonteCarloBettingRecommendation(
                    simulation_id=simulation_id,
                    race_id=race_id,
                    horse_name=rec.get("horse_name", ""),
                    bet_type=rec.get("bet_type", "win"),
                    recommended_stake=rec.get("stake", 0.0),
                    recommended_odds=rec.get("odds", 0.0),
                    fair_odds=rec.get("fair_odds", 0.0),
                    expected_value=rec.get("expected_value", 0.0),
                    kelly_fraction=rec.get("kelly_fraction", 0.0),
                    confidence_score=rec.get("confidence", 0.0),
                    risk_rating=rec.get("risk_rating", "MEDIUM"),
                    betting_value=rec.get("value_rating", 0.0),
                    recommendation_strength=rec.get("strength", "MODERATE"),
                )
                mc_recommendations.append(mc_rec)

            self.db_manager.store_betting_recommendations(mc_recommendations)

            return {
                "success": True,
                "recommendations_stored": len(mc_recommendations),
                "message": f"Stored {len(mc_recommendations)} betting recommendations",
            }

        except Exception as e:
            logger.error(f"Error storing betting recommendations: {e}")
            return {"success": False, "error": str(e)}

    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive Monte Carlo performance report"""
        return self.db_manager.get_monte_carlo_performance_summary(days)

    def get_top_picks(
        self, race_id: str = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top Monte Carlo picks"""
        return self.db_manager.get_top_monte_carlo_picks(race_id, limit)


if __name__ == "__main__":
    # Test the Monte Carlo database integration
    print("🎲 Testing Monte Carlo Database Integration")
    print("=" * 50)

    # Initialize manager
    manager = MonteCarloIntegrationManager("data/test_monte_carlo.db")

    # Test performance report
    report = manager.generate_performance_report(30)
    print(f"Performance Report: {report}")

    print("✅ Monte Carlo database integration test completed!")
