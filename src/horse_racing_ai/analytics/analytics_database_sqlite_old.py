"""
Analytics Database Integration
=============================

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
    """Database interface for analytics data operations."""

    def __init__(self, database_url: str = None):
        """Initialize analytics database connection."""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            self.database_url = "postgresql://horse_racing:secure_password_123@localhost:5434/horse_racing_db"
        
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
                        prediction_type TEXT NOT NULL,  -- 'win', 'place'
                        predicted_probability REAL NOT NULL,
                        confidence_score REAL NOT NULL,
                        actual_result INTEGER NOT NULL,  -- 1 if correct, 0 if incorrect
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_key TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT,  -- JSON string for additional data
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(metric_key, start_date, end_date)
                )
            """
            )

            # Model weights tracking table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_weights_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    weights_json TEXT NOT NULL,  -- JSON string of weights
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
        odds: float = None,
        stake: float = None,
        return_amount: float = None,
        track: str = None,
        distance: int = None,
        race_type: str = None,
        race_date: str = None,
    ):
        """Record a prediction result for analytics tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO prediction_results (
                        race_id, horse_id, prediction_type, predicted_probability,
                        confidence_score, actual_result, odds, stake, return_amount,
                        track, distance, race_type, race_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        except Exception as e:
            logger.error(f"Failed to record prediction result: {e}")
            raise

    def get_prediction_results(
        self,
        start_date: datetime,
        end_date: datetime,
        prediction_type: str = None,
        track: str = None,
    ) -> pd.DataFrame:
        """Get prediction results for analysis."""
        try:
            query = """
                SELECT * FROM prediction_results 
                WHERE race_date BETWEEN ? AND ?
            """
            params = [start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")]

            if prediction_type:
                query += " AND prediction_type = ?"
                params.append(prediction_type)

            if track:
                query += " AND track = ?"
                params.append(track)

            query += " ORDER BY race_date, race_id"

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)

            return df

        except Exception as e:
            logger.error(f"Failed to get prediction results: {e}")
            return pd.DataFrame()

    def calculate_accuracy_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Calculate accuracy metrics for the given period."""
        try:
            df = self.get_prediction_results(start_date, end_date)

            if df.empty:
                return self._empty_metrics()

            # Overall accuracy
            overall_accuracy = df["actual_result"].mean()

            # Win prediction accuracy
            win_df = df[df["prediction_type"] == "win"]
            win_accuracy = win_df["actual_result"].mean() if not win_df.empty else 0.0

            # Place prediction accuracy
            place_df = df[df["prediction_type"] == "place"]
            place_accuracy = (
                place_df["actual_result"].mean() if not place_df.empty else 0.0
            )

            # Precision, Recall, F1 (treating as binary classification)
            true_positives = df[df["actual_result"] == 1].shape[0]
            false_positives = df[df["actual_result"] == 0].shape[0]
            false_negatives = 0  # We don't track missed opportunities

            precision = (
                true_positives / (true_positives + false_positives)
                if (true_positives + false_positives) > 0
                else 0.0
            )
            recall = overall_accuracy  # Same as accuracy for our use case
            f1_score = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            # Confidence correlation
            confidence_corr = df["confidence_score"].corr(df["actual_result"])
            if pd.isna(confidence_corr):
                confidence_corr = 0.0

            return {
                "overall_accuracy": overall_accuracy,
                "win_prediction_accuracy": win_accuracy,
                "place_prediction_accuracy": place_accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "confidence_correlation": confidence_corr,
                "total_predictions": len(df),
                "correct_predictions": true_positives,
            }

        except Exception as e:
            logger.error(f"Failed to calculate accuracy metrics: {e}")
            return self._empty_metrics()

    def calculate_financial_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Calculate financial performance metrics."""
        try:
            df = self.get_prediction_results(start_date, end_date)

            # Filter for records with betting data
            betting_df = df.dropna(subset=["stake", "return_amount"])

            if betting_df.empty:
                return self._empty_financial_metrics()

            total_staked = betting_df["stake"].sum()
            total_returns = betting_df["return_amount"].sum()
            profit_loss = total_returns - total_staked
            roi_percentage = (
                (profit_loss / total_staked * 100) if total_staked > 0 else 0.0
            )

            # Hit rate (percentage of winning bets)
            winning_bets = betting_df[betting_df["return_amount"] > betting_df["stake"]]
            hit_rate = (
                len(winning_bets) / len(betting_df) if len(betting_df) > 0 else 0.0
            )

            # Calculate returns for Sharpe ratio
            betting_df["bet_return"] = (
                betting_df["return_amount"] - betting_df["stake"]
            ) / betting_df["stake"]

            # Sharpe ratio (assuming risk-free rate of 2%)
            mean_return = betting_df["bet_return"].mean()
            std_return = betting_df["bet_return"].std()
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            sharpe_ratio = (
                (mean_return - risk_free_rate) / std_return if std_return > 0 else 0.0
            )

            # Maximum drawdown
            betting_df["cumulative_pnl"] = betting_df["bet_return"].cumsum()
            rolling_max = betting_df["cumulative_pnl"].expanding().max()
            drawdown = betting_df["cumulative_pnl"] - rolling_max
            max_drawdown = drawdown.min()

            # Volatility
            volatility = std_return if pd.notna(std_return) else 0.0

            # Sortino ratio (downside volatility only)
            negative_returns = betting_df[betting_df["bet_return"] < 0]["bet_return"]
            downside_std = (
                negative_returns.std() if len(negative_returns) > 0 else std_return
            )
            sortino_ratio = (
                (mean_return - risk_free_rate) / downside_std
                if downside_std > 0
                else 0.0
            )

            # Value at Risk (95th percentile)
            var_95 = betting_df["bet_return"].quantile(0.05)  # 5th percentile for VaR

            return {
                "total_bets": len(betting_df),
                "total_staked": total_staked,
                "total_returns": total_returns,
                "profit_loss": profit_loss,
                "roi_percentage": roi_percentage,
                "hit_rate": hit_rate,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "volatility": volatility,
                "sortino_ratio": sortino_ratio,
                "value_at_risk": var_95,
            }

        except Exception as e:
            logger.error(f"Failed to calculate financial metrics: {e}")
            return self._empty_financial_metrics()

    def get_performance_by_segment(
        self, start_date: datetime, end_date: datetime, segment_type: str
    ) -> Dict[str, Dict[str, float]]:
        """Get performance metrics segmented by track, distance, race_type, etc."""
        try:
            df = self.get_prediction_results(start_date, end_date)

            if df.empty or segment_type not in df.columns:
                return {}

            results = {}

            for segment_value in df[segment_type].dropna().unique():
                segment_df = df[df[segment_type] == segment_value]

                # Calculate basic metrics for this segment
                accuracy = segment_df["actual_result"].mean()
                total_predictions = len(segment_df)
                correct_predictions = segment_df["actual_result"].sum()

                # Financial metrics if available
                betting_segment = segment_df.dropna(subset=["stake", "return_amount"])
                if not betting_segment.empty:
                    total_staked = betting_segment["stake"].sum()
                    total_returns = betting_segment["return_amount"].sum()
                    profit_loss = total_returns - total_staked
                    roi = (
                        (profit_loss / total_staked * 100) if total_staked > 0 else 0.0
                    )
                    hit_rate = len(
                        betting_segment[
                            betting_segment["return_amount"] > betting_segment["stake"]
                        ]
                    ) / len(betting_segment)
                else:
                    total_staked = 0.0
                    total_returns = 0.0
                    profit_loss = 0.0
                    roi = 0.0
                    hit_rate = 0.0

                results[str(segment_value)] = {
                    "accuracy": accuracy,
                    "total_predictions": total_predictions,
                    "correct_predictions": correct_predictions,
                    "total_staked": total_staked,
                    "total_returns": total_returns,
                    "profit_loss": profit_loss,
                    "roi_percentage": roi,
                    "hit_rate": hit_rate,
                }

            return results

        except Exception as e:
            logger.error(f"Failed to get performance by segment: {e}")
            return {}

    def cache_metric(
        self,
        metric_key: str,
        start_date: datetime,
        end_date: datetime,
        metric_value: float,
        metadata: str = None,
    ):
        """Cache a calculated metric for faster retrieval."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO performance_metrics_cache
                    (metric_key, start_date, end_date, metric_value, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        metric_key,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                        metric_value,
                        metadata,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to cache metric: {e}")

    def get_cached_metric(
        self, metric_key: str, start_date: datetime, end_date: datetime
    ) -> Optional[Tuple[float, str]]:
        """Retrieve a cached metric value."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT metric_value, metadata FROM performance_metrics_cache
                    WHERE metric_key = ? AND start_date = ? AND end_date = ?
                """,
                    (
                        metric_key,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                    ),
                )

                result = cursor.fetchone()
                if result:
                    return result[0], result[1]

        except Exception as e:
            logger.error(f"Failed to get cached metric: {e}")

        return None

    def record_model_weights(
        self,
        model_name: str,
        weights_dict: Dict,
        performance_score: float,
        applied_date: datetime,
    ):
        """Record model weights for optimization tracking."""
        try:
            import json

            weights_json = json.dumps(weights_dict)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO model_weights_history
                    (model_name, weights_json, performance_score, applied_date)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        model_name,
                        weights_json,
                        performance_score,
                        applied_date.strftime("%Y-%m-%d"),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to record model weights: {e}")

    def get_model_weights_history(self, model_name: str, limit: int = 10) -> List[Dict]:
        """Get historical model weights for optimization analysis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT weights_json, performance_score, applied_date, created_at
                    FROM model_weights_history
                    WHERE model_name = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (model_name, limit),
                )

                results = []
                for row in cursor.fetchall():
                    import json

                    weights = json.loads(row[0])
                    results.append(
                        {
                            "weights": weights,
                            "performance_score": row[1],
                            "applied_date": row[2],
                            "created_at": row[3],
                        }
                    )

                return results

        except Exception as e:
            logger.error(f"Failed to get model weights history: {e}")
            return []

    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty accuracy metrics structure."""
        return {
            "overall_accuracy": 0.0,
            "win_prediction_accuracy": 0.0,
            "place_prediction_accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "confidence_correlation": 0.0,
            "total_predictions": 0,
            "correct_predictions": 0,
        }

    def _empty_financial_metrics(self) -> Dict[str, float]:
        """Return empty financial metrics structure."""
        return {
            "total_bets": 0,
            "total_staked": 0.0,
            "total_returns": 0.0,
            "profit_loss": 0.0,
            "roi_percentage": 0.0,
            "hit_rate": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sortino_ratio": 0.0,
            "value_at_risk": 0.0,
        }


# Global instance for easy import
analytics_db = AnalyticsDatabase()
