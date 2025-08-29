#!/usr/bin/env python3
"""
Strategy Performance Dashboard
=============================

Web-based dashboard for monitoring 80/20 and Dutching strategy performance.
Provides real-time metrics, alerts, and opportunity tracking.

Features:
- Real-time performance metrics
- ROI tracking and visualization
- Strategy opportunity monitoring
- Alert management
- Historical performance analysis
- Live race integration status

Author: Horse Racing AI System V2.03
Date: August 2025
"""

from flask import Flask, render_template, jsonify, request
import json
import sqlite3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.monitoring.live_strategy_monitor import LiveStrategyMonitor

# Flask app setup
app = Flask(__name__)
app.secret_key = "strategy_dashboard_secret_key"

# Initialize monitoring system
monitor = LiveStrategyMonitor()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template("strategy_dashboard.html")


@app.route("/api/dashboard-data")
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        dashboard_data = monitor.get_dashboard_data()
        return jsonify(
            {
                "success": True,
                "data": dashboard_data,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/strategy-performance/<strategy_name>")
def get_strategy_performance(strategy_name):
    """Get detailed performance for a specific strategy"""
    try:
        days = request.args.get("days", 30, type=int)
        performance = monitor.db.get_strategy_performance(strategy_name, days=days)

        return jsonify(
            {
                "success": True,
                "data": performance.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting {strategy_name} performance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/live-opportunities")
def get_live_opportunities():
    """Get current live opportunities"""
    try:
        # Get opportunities from today
        today_80_20 = monitor.daily_opportunities.get("80/20", [])
        today_dutching = monitor.daily_opportunities.get("dutching", [])

        opportunities = []
        for opp in today_80_20:
            opportunities.append(opp.to_dict())
        for opp in today_dutching:
            opportunities.append(opp.to_dict())

        return jsonify(
            {
                "success": True,
                "data": opportunities,
                "count": len(opportunities),
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting live opportunities: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/historical-performance")
def get_historical_performance():
    """Get historical performance data for charts"""
    try:
        days = request.args.get("days", 30, type=int)
        strategy_name = request.args.get("strategy", "all")

        with sqlite3.connect(monitor.db.db_path) as conn:
            if strategy_name == "all":
                query = (
                    """
                SELECT date, strategy_name, net_profit, roi_percentage, total_bets
                FROM daily_performance 
                WHERE date >= date('now', '-%d days')
                ORDER BY date, strategy_name
                """
                    % days
                )
                cursor = conn.execute(query)
            else:
                query = (
                    """
                SELECT date, strategy_name, net_profit, roi_percentage, total_bets
                FROM daily_performance 
                WHERE strategy_name = ? AND date >= date('now', '-%d days')
                ORDER BY date
                """
                    % days
                )
                cursor = conn.execute(query, (strategy_name,))

            historical_data = []
            for row in cursor.fetchall():
                historical_data.append(
                    {
                        "date": row[0],
                        "strategy_name": row[1],
                        "net_profit": row[2],
                        "roi_percentage": row[3],
                        "total_bets": row[4],
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": historical_data,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting historical performance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts")
def get_alerts():
    """Get recent alerts"""
    try:
        limit = request.args.get("limit", 50, type=int)

        with sqlite3.connect(monitor.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT alert_type, strategy_name, message, severity, 
                       created_at, acknowledged
                FROM performance_alerts 
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            alerts = []
            for row in cursor.fetchall():
                alerts.append(
                    {
                        "alert_type": row[0],
                        "strategy_name": row[1],
                        "message": row[2],
                        "severity": row[3],
                        "created_at": row[4],
                        "acknowledged": bool(row[5]),
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": alerts,
                "count": len(alerts),
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/monitoring/start", methods=["POST"])
def start_monitoring():
    """Start live monitoring"""
    try:
        if not monitor.monitoring_active:
            monitor.start_monitoring()
            return jsonify(
                {
                    "success": True,
                    "message": "Live monitoring started",
                    "status": "active",
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": "Monitoring already active",
                    "status": "active",
                }
            )
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/monitoring/stop", methods=["POST"])
def stop_monitoring():
    """Stop live monitoring"""
    try:
        if monitor.monitoring_active:
            monitor.stop_monitoring()
            return jsonify(
                {
                    "success": True,
                    "message": "Live monitoring stopped",
                    "status": "inactive",
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": "Monitoring already inactive",
                    "status": "inactive",
                }
            )
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/monitoring/status")
def get_monitoring_status():
    """Get current monitoring status"""
    try:
        return jsonify(
            {
                "success": True,
                "data": {
                    "active": monitor.monitoring_active,
                    "last_scan": datetime.now().isoformat(),
                    "opportunities_today": {
                        "80/20": len(monitor.daily_opportunities.get("80/20", [])),
                        "dutching": len(
                            monitor.daily_opportunities.get("dutching", [])
                        ),
                    },
                },
            }
        )
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/execute-opportunity", methods=["POST"])
def execute_opportunity():
    """Execute a strategy opportunity"""
    try:
        data = request.get_json()

        # This would integrate with actual betting system
        # For now, simulate execution
        execution_result = {
            "result": "simulated",
            "total_return": data.get("total_stake", 0) * 1.1,  # Simulate 10% return
            "odds": data.get("odds", []),
        }

        # Record execution (would be done by actual betting system)
        logger.info(f"Simulated execution of {data.get('strategy_type')} opportunity")

        return jsonify(
            {
                "success": True,
                "message": "Opportunity executed (simulated)",
                "result": execution_result,
            }
        )
    except Exception as e:
        logger.error(f"Error executing opportunity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
