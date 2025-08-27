#!/usr/bin/env python3
"""
Enhanced Performance API Endpoints
=================================

Real-time performance tracking API endpoints that connect to PostgreSQL
and serve AI selection profit/loss data for the web app.
"""

import psycopg2
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PerformanceAPI:
    """API class for performance data from PostgreSQL"""

    def __init__(self):
        self.db_params = {
            "host": "postgres",  # Docker service name
            "port": 5432,
            "database": "advanced_racing_metrics_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def get_database_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_params)

    def get_performance_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get overall performance metrics
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_predictions,
                    COUNT(*) FILTER (WHERE hit_rate_contribution = true) as correct_predictions,
                    COUNT(*) FILTER (WHERE race_result = 'WIN') as wins,
                    COUNT(*) FILTER (WHERE race_result = 'PLACE') as places,
                    SUM(actual_stake_placed) as total_stakes,
                    SUM(gross_return) as total_returns,
                    SUM(net_profit_loss) as total_profit_loss,
                    AVG(roi_percentage) as avg_roi,
                    AVG(starting_price_decimal) as avg_starting_price,
                    MIN(selection_date) as period_start,
                    MAX(selection_date) as period_end,
                    MAX(running_roi) as latest_running_roi
                FROM betting_performance_tracker
                WHERE selection_date >= CURRENT_DATE - INTERVAL '%s days'
            """,
                (days_back,),
            )

            overall_stats = cursor.fetchone()

            # Get confidence level breakdown
            cursor.execute(
                """
                SELECT 
                    confidence_level,
                    COUNT(*) as total_bets,
                    COUNT(*) FILTER (WHERE hit_rate_contribution = true) as successful_bets,
                    SUM(net_profit_loss) as profit_loss,
                    AVG(roi_percentage) as avg_roi,
                    SUM(actual_stake_placed) as total_stakes
                FROM betting_performance_tracker
                WHERE selection_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY confidence_level
                ORDER BY confidence_level
            """,
                (days_back,),
            )

            confidence_breakdown = cursor.fetchall()

            # Get daily performance for charts
            cursor.execute(
                """
                SELECT 
                    selection_date,
                    COUNT(*) as daily_bets,
                    COUNT(*) FILTER (WHERE hit_rate_contribution = true) as daily_wins,
                    SUM(net_profit_loss) as daily_profit,
                    AVG(roi_percentage) as daily_roi
                FROM betting_performance_tracker
                WHERE selection_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY selection_date
                ORDER BY selection_date
            """,
                (days_back,),
            )

            daily_performance = cursor.fetchall()

            # Get best and worst performers
            cursor.execute(
                """
                SELECT horse_name, race_result, net_profit_loss, roi_percentage, 
                       starting_price_decimal, confidence_level, selection_date
                FROM betting_performance_tracker
                WHERE selection_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY net_profit_loss DESC
                LIMIT 10
            """,
                (days_back,),
            )

            best_performers = cursor.fetchall()

            cursor.execute(
                """
                SELECT horse_name, race_result, net_profit_loss, roi_percentage, 
                       starting_price_decimal, confidence_level, selection_date
                FROM betting_performance_tracker
                WHERE selection_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY net_profit_loss ASC
                LIMIT 10
            """,
                (days_back,),
            )

            worst_performers = cursor.fetchall()

            # Calculate derived metrics
            if overall_stats:
                total_pred = overall_stats["total_predictions"] or 0
                correct_pred = overall_stats["correct_predictions"] or 0
                wins = overall_stats["wins"] or 0
                places = overall_stats["places"] or 0
                total_stakes = float(overall_stats["total_stakes"] or 0)
                total_returns = float(overall_stats["total_returns"] or 0)
                total_profit = float(overall_stats["total_profit_loss"] or 0)

                accuracy_rate = (
                    (correct_pred / total_pred * 100) if total_pred > 0 else 0.0
                )
                win_rate = (wins / total_pred * 100) if total_pred > 0 else 0.0
                place_rate = (places / total_pred * 100) if total_pred > 0 else 0.0
                roi_percentage = (
                    (total_profit / total_stakes * 100) if total_stakes > 0 else 0.0
                )

                # Format confidence breakdown
                confidence_data = {}
                for conf in confidence_breakdown:
                    level = conf["confidence_level"]
                    total_bets = conf["total_bets"] or 0
                    successful_bets = conf["successful_bets"] or 0
                    conf_accuracy = (
                        (successful_bets / total_bets * 100) if total_bets > 0 else 0.0
                    )

                    confidence_data[level] = {
                        "total_bets": total_bets,
                        "successful_bets": successful_bets,
                        "accuracy_rate": round(conf_accuracy, 1),
                        "profit_loss": float(conf["profit_loss"] or 0),
                        "avg_roi": float(conf["avg_roi"] or 0),
                        "total_stakes": float(conf["total_stakes"] or 0),
                    }

                # Format daily performance
                daily_data = []
                for day in daily_performance:
                    daily_data.append(
                        {
                            "date": day["selection_date"].isoformat(),
                            "bets": day["daily_bets"],
                            "wins": day["daily_wins"],
                            "profit": float(day["daily_profit"] or 0),
                            "roi": float(day["daily_roi"] or 0),
                            "accuracy": (
                                (day["daily_wins"] / day["daily_bets"] * 100)
                                if day["daily_bets"] > 0
                                else 0.0
                            ),
                        }
                    )

                # Format performer data
                def format_performer(performer):
                    return {
                        "horse_name": performer["horse_name"],
                        "race_result": performer["race_result"],
                        "profit_loss": float(performer["net_profit_loss"]),
                        "roi_percentage": float(performer["roi_percentage"]),
                        "starting_price": float(performer["starting_price_decimal"]),
                        "confidence_level": performer["confidence_level"],
                        "date": performer["selection_date"].isoformat(),
                    }

                best_performers_data = [format_performer(p) for p in best_performers]
                worst_performers_data = [format_performer(p) for p in worst_performers]

                response = {
                    "status": "success",
                    "data": {
                        "summary": {
                            "total_predictions": total_pred,
                            "correct_predictions": correct_pred,
                            "accuracy_rate": round(accuracy_rate, 1),
                            "win_rate": round(win_rate, 1),
                            "place_rate": round(place_rate, 1),
                            "total_stakes": round(total_stakes, 2),
                            "total_returns": round(total_returns, 2),
                            "total_profit_loss": round(total_profit, 2),
                            "roi_percentage": round(roi_percentage, 2),
                            "avg_starting_price": float(
                                overall_stats["avg_starting_price"] or 0
                            ),
                            "latest_running_roi": float(
                                overall_stats["latest_running_roi"] or 0
                            ),
                            "period_start": (
                                overall_stats["period_start"].isoformat()
                                if overall_stats["period_start"]
                                else None
                            ),
                            "period_end": (
                                overall_stats["period_end"].isoformat()
                                if overall_stats["period_end"]
                                else None
                            ),
                        },
                        "confidence_breakdown": confidence_data,
                        "daily_performance": daily_data,
                        "best_performers": best_performers_data,
                        "worst_performers": worst_performers_data,
                        "timestamp": datetime.now().isoformat(),
                    },
                }
            else:
                response = {
                    "status": "success",
                    "data": {
                        "summary": {
                            "total_predictions": 0,
                            "accuracy_rate": 0.0,
                            "roi_percentage": 0.0,
                            "total_profit_loss": 0.0,
                        },
                        "message": "No performance data available for the specified period",
                    },
                }

            conn.close()
            return response

        except Exception as e:
            logger.error(f"Error fetching performance summary: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch performance data: {str(e)}",
                "data": {
                    "summary": {
                        "total_predictions": 0,
                        "accuracy_rate": 0.0,
                        "roi_percentage": 0.0,
                        "total_profit_loss": 0.0,
                    }
                },
            }

    def get_recent_selections(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent AI selections with results"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                SELECT 
                    race_id,
                    horse_name,
                    selection_date,
                    ai_prediction_probability,
                    confidence_level,
                    recommended_stake,
                    value_rating,
                    starting_price_decimal,
                    market_rank,
                    finishing_position,
                    race_result,
                    net_profit_loss,
                    roi_percentage,
                    created_at
                FROM betting_performance_tracker
                ORDER BY selection_date DESC, created_at DESC
                LIMIT %s
            """,
                (limit,),
            )

            selections = cursor.fetchall()

            # Format the data
            formatted_selections = []
            for selection in selections:
                formatted_selections.append(
                    {
                        "race_id": selection["race_id"],
                        "horse_name": selection["horse_name"],
                        "selection_date": selection["selection_date"].isoformat(),
                        "ai_probability": round(
                            float(selection["ai_prediction_probability"] or 0) * 100, 1
                        ),
                        "confidence_level": selection["confidence_level"],
                        "recommended_stake": float(selection["recommended_stake"] or 0),
                        "value_rating": round(float(selection["value_rating"] or 0), 2),
                        "starting_price": float(
                            selection["starting_price_decimal"] or 0
                        ),
                        "market_rank": selection["market_rank"],
                        "finishing_position": selection["finishing_position"],
                        "race_result": selection["race_result"],
                        "profit_loss": float(selection["net_profit_loss"] or 0),
                        "roi_percentage": round(
                            float(selection["roi_percentage"] or 0), 1
                        ),
                        "created_at": (
                            selection["created_at"].isoformat()
                            if selection["created_at"]
                            else None
                        ),
                    }
                )

            conn.close()

            return {
                "status": "success",
                "data": {
                    "selections": formatted_selections,
                    "count": len(formatted_selections),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching recent selections: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch recent selections: {str(e)}",
                "data": {"selections": [], "count": 0},
            }


# Create API instance
performance_api = PerformanceAPI()


# API endpoint functions
def get_performance_summary_endpoint(days_back: int = 30):
    """API endpoint for performance summary"""
    return performance_api.get_performance_summary(days_back)


def get_recent_selections_endpoint(limit: int = 50):
    """API endpoint for recent selections"""
    return performance_api.get_recent_selections(limit)


# Test the API
if __name__ == "__main__":
    api = PerformanceAPI()

    print("Testing Performance API...")
    print("=" * 50)

    # Test performance summary
    summary = api.get_performance_summary(14)
    print(f"Performance Summary Status: {summary['status']}")

    if summary["status"] == "success" and "summary" in summary["data"]:
        s = summary["data"]["summary"]
        print(f"Total Predictions: {s['total_predictions']}")
        print(f"Accuracy Rate: {s['accuracy_rate']}%")
        print(f"ROI: {s['roi_percentage']}%")
        print(f"Total P&L: £{s['total_profit_loss']}")

    # Test recent selections
    recent = api.get_recent_selections(10)
    print(f"\nRecent Selections Status: {recent['status']}")
    print(f"Recent Selections Count: {recent['data']['count']}")

    if recent["data"]["selections"]:
        print("\nSample selection:")
        sel = recent["data"]["selections"][0]
        print(
            f"  {sel['horse_name']} - {sel['race_result']} - P&L: £{sel['profit_loss']}"
        )


# Create global instance for import
performance_api = PerformanceAPI()
