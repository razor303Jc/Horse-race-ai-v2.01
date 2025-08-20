"""
Analytics Database Integration - PostgreSQL Version
==================================================

Database operations for the comprehensive analytics system with performance
metrics calculation, ROI tracking, and historical validation.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)


class AnalyticsDatabase:
    """PostgreSQL database interface for analytics data operations."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize analytics database connection."""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            self.database_url = (
                "postgresql://horse_racing:secure_password_123@localhost:5434/"
                "horse_racing_db"
            )
        
        # Parse database URL for connection parameters
        self._parse_database_url()
        self.ensure_analytics_tables()

    def _parse_database_url(self):
        """Parse DATABASE_URL into connection parameters"""
        import urllib.parse as urlparse

        url = urlparse.urlparse(self.database_url)
        self.db_config = {
            "host": url.hostname,
            "port": url.port,
            "database": url.path[1:],  # Remove leading slash
            "user": url.username,
            "password": url.password,
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)

    def ensure_analytics_tables(self):
        """Create analytics tables if they don't exist."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Prediction results table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prediction_results (
                        id SERIAL PRIMARY KEY,
                        race_id TEXT NOT NULL,
                        horse_id TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        predicted_probability REAL NOT NULL,
                        confidence_score REAL NOT NULL,
                        actual_result INTEGER NOT NULL,
                        odds REAL,
                        stake REAL,
                        return_amount REAL,
                        track TEXT,
                        distance INTEGER,
                        race_type TEXT,
                        race_date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                # Performance metrics cache table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS performance_metrics_cache (
                        id SERIAL PRIMARY KEY,
                        metric_key TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metadata TEXT,
                        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(metric_key, start_date, end_date)
                    )
                    """
                )

                # Model weights tracking table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS model_weights_history (
                        id SERIAL PRIMARY KEY,
                        model_name TEXT NOT NULL,
                        weights_json TEXT NOT NULL,
                        performance_score REAL,
                        applied_date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                conn.commit()

    def record_prediction_result(
        self,
        race_id: str,
        horse_id: str,
        prediction_type: str,
        predicted_probability: float,
        confidence_score: float,
        actual_result: int,
        odds: Optional[float] = None,
        stake: Optional[float] = None,
        return_amount: Optional[float] = None,
        track: Optional[str] = None,
        distance: Optional[int] = None,
        race_type: Optional[str] = None,
        race_date: Optional[str] = None,
    ):
        """Record a prediction result for analytics tracking."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO prediction_results (
                            race_id, horse_id, prediction_type, 
                            predicted_probability, confidence_score, actual_result, 
                            odds, stake, return_amount, track, distance, 
                            race_type, race_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            race_id,
                            horse_id,
                            prediction_type,
                            predicted_probability,
                            confidence_score,
                            actual_result,
                            odds,
                            stake,
                            return_amount,
                            track,
                            distance,
                            race_type,
                            race_date,
                        ),
                    )
                    conn.commit()

            logger.info(
                f"Recorded prediction result for {horse_id} in race {race_id}"
            )

        except Exception as e:
            logger.error(f"Error recording prediction result: {e}")
            raise

    def get_all_prediction_results(self) -> pd.DataFrame:
        """Get all prediction results as a DataFrame."""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT * FROM prediction_results
                ORDER BY created_at DESC
                """
                return pd.read_sql_query(query, conn)

        except Exception as e:
            logger.error(f"Error retrieving prediction results: {e}")
            return pd.DataFrame()

    def get_prediction_results_by_date_range(
        self, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Get prediction results for a specific date range."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM prediction_results
                        WHERE race_date BETWEEN %s AND %s
                        ORDER BY race_date DESC, created_at DESC
                        """,
                        (start_date, end_date),
                    )
                    
                    results = cursor.fetchall()
                    return pd.DataFrame(results) if results else pd.DataFrame()

        except Exception as e:
            logger.error(
                f"Error retrieving prediction results for date range: {e}"
            )
            return pd.DataFrame()

    def calculate_accuracy_metrics(
        self, start_date: str = None, end_date: str = None
    ) -> Dict[str, float]:
        """Calculate accuracy metrics for predictions."""
        try:
            conditions = []
            params = []
            
            if start_date:
                conditions.append("race_date >= %s")
                params.append(start_date)
            if end_date:
                conditions.append("race_date <= %s")
                params.append(end_date)
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Overall accuracy
                    cursor.execute(
                        f"""
                        SELECT 
                            COUNT(*) as total,
                            SUM(actual_result) as correct
                        FROM prediction_results 
                        {where_clause}
                        """,
                        params
                    )
                    
                    result = cursor.fetchone()
                    total = result['total'] if result else 0
                    correct = result['correct'] if result else 0
                    
                    overall_accuracy = (correct / total * 100) if total > 0 else 0

                    # Accuracy by prediction type
                    cursor.execute(
                        f"""
                        SELECT 
                            prediction_type,
                            COUNT(*) as total,
                            SUM(actual_result) as correct
                        FROM prediction_results 
                        {where_clause}
                        GROUP BY prediction_type
                        """,
                        params
                    )
                    
                    type_results = cursor.fetchall()
                    type_accuracy = {}
                    
                    for row in type_results:
                        pred_type = row['prediction_type']
                        type_total = row['total']
                        type_correct = row['correct']
                        type_accuracy[f"{pred_type}_accuracy"] = (
                            (type_correct / type_total * 100) if type_total > 0 else 0
                        )

                    return {
                        "overall_accuracy": overall_accuracy,
                        "total_predictions": total,
                        "correct_predictions": correct,
                        **type_accuracy,
                    }

        except Exception as e:
            logger.error(f"Error calculating accuracy metrics: {e}")
            return {}

    def calculate_roi_metrics(
        self, start_date: str = None, end_date: str = None
    ) -> Dict[str, float]:
        """Calculate ROI metrics for betting strategy."""
        try:
            conditions = ["stake IS NOT NULL"]
            params = []
            
            if start_date:
                conditions.append("race_date >= %s")
                params.append(start_date)
            if end_date:
                conditions.append("race_date <= %s") 
                params.append(end_date)
            
            where_clause = "WHERE " + " AND ".join(conditions)

            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                        SELECT 
                            SUM(stake) as total_stake,
                            SUM(return_amount) as total_return,
                            COUNT(*) as total_bets,
                            SUM(CASE WHEN actual_result = 1 THEN 1 ELSE 0 END) as winning_bets
                        FROM prediction_results 
                        {where_clause}
                        """,
                        params
                    )
                    
                    result = cursor.fetchone()
                    
                    if not result or not result['total_stake']:
                        return {"roi": 0, "profit_loss": 0, "strike_rate": 0}

                    total_stake = float(result['total_stake'] or 0)
                    total_return = float(result['total_return'] or 0)
                    total_bets = int(result['total_bets'] or 0)
                    winning_bets = int(result['winning_bets'] or 0)

                    profit_loss = total_return - total_stake
                    roi = (profit_loss / total_stake * 100) if total_stake > 0 else 0
                    strike_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0

                    return {
                        "roi": roi,
                        "profit_loss": profit_loss,
                        "total_stake": total_stake,
                        "total_return": total_return,
                        "total_bets": total_bets,
                        "winning_bets": winning_bets,
                        "strike_rate": strike_rate,
                    }

        except Exception as e:
            logger.error(f"Error calculating ROI metrics: {e}")
            return {}

    def get_performance_summary(
        self, start_date: str = None, end_date: str = None
    ) -> Dict[str, any]:
        """Get comprehensive performance summary."""
        accuracy_metrics = self.calculate_accuracy_metrics(start_date, end_date)
        roi_metrics = self.calculate_roi_metrics(start_date, end_date)

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "accuracy": accuracy_metrics,
            "roi": roi_metrics,
            "generated_at": datetime.now().isoformat(),
        }

    def cache_performance_metric(
        self, metric_key: str, start_date: str, end_date: str, 
        metric_value: float, metadata: str = None
    ):
        """Cache a calculated performance metric."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO performance_metrics_cache 
                        (metric_key, start_date, end_date, metric_value, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (metric_key, start_date, end_date)
                        DO UPDATE SET 
                            metric_value = EXCLUDED.metric_value,
                            metadata = EXCLUDED.metadata,
                            calculated_at = CURRENT_TIMESTAMP
                        """,
                        (metric_key, start_date, end_date, metric_value, metadata)
                    )
                    conn.commit()

        except Exception as e:
            logger.error(f"Error caching performance metric: {e}")

    def get_cached_metric(
        self, metric_key: str, start_date: str, end_date: str
    ) -> Optional[float]:
        """Retrieve a cached performance metric."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT metric_value FROM performance_metrics_cache
                        WHERE metric_key = %s AND start_date = %s AND end_date = %s
                        """,
                        (metric_key, start_date, end_date)
                    )
                    
                    result = cursor.fetchone()
                    return result['metric_value'] if result else None

        except Exception as e:
            logger.error(f"Error retrieving cached metric: {e}")
            return None

    def save_model_weights(
        self, model_name: str, weights_json: str, 
        performance_score: float, applied_date: str
    ):
        """Save model weights configuration for tracking."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO model_weights_history 
                        (model_name, weights_json, performance_score, applied_date)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (model_name, weights_json, performance_score, applied_date)
                    )
                    conn.commit()

        except Exception as e:
            logger.error(f"Error saving model weights: {e}")

    def get_latest_model_weights(self, model_name: str) -> Optional[Dict]:
        """Get the latest weights for a specific model."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM model_weights_history
                        WHERE model_name = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (model_name,)
                    )
                    
                    result = cursor.fetchone()
                    return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error retrieving latest model weights: {e}")
            return None
