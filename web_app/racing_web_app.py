"""
Horse Racing AI Web Application
Integrated with Node-RED pipeline and APIs
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import logging
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2 import sql
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
NODE_RED_URL = "http://localhost:1880"
PREDICTION_API_URL = "http://localhost:5000"
ML_API_URL = "http://localhost:5001"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "racing_data",
    "user": "racing_user",
    "password": "racing_password",
}


class WebAppAPI:
    def __init__(self):
        self.app = app

    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None

    def trigger_node_red_flow(self, flow_type, data=None):
        """Trigger Node-RED flows via HTTP"""
        try:
            endpoint = f"{NODE_RED_URL}/trigger/{flow_type}"
            response = requests.post(endpoint, json=data or {}, timeout=30)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Node-RED trigger error: {e}")
            return None

    def get_api_status(self):
        """Check status of both APIs"""
        status = {"prediction_api": False, "ml_api": False, "node_red": False}

        # Check Prediction API
        try:
            response = requests.get(f"{PREDICTION_API_URL}/health", timeout=5)
            status["prediction_api"] = response.status_code == 200
        except:
            pass

        # Check ML API
        try:
            response = requests.get(f"{ML_API_URL}/health", timeout=5)
            status["ml_api"] = response.status_code == 200
        except:
            pass

        # Check Node-RED
        try:
            response = requests.get(f"{NODE_RED_URL}/flows", timeout=5)
            status["node_red"] = response.status_code == 200
        except:
            pass

        return status

    def get_recent_predictions(self, limit=10):
        """Get recent predictions from database"""
        conn = self.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            query = """
                SELECT race_date, track, race_number, horse_name, 
                       prediction_confidence, actual_result, created_at
                FROM predictions 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()

            predictions = []
            for row in results:
                predictions.append(
                    {
                        "race_date": row[0],
                        "track": row[1],
                        "race_number": row[2],
                        "horse_name": row[3],
                        "confidence": row[4],
                        "result": row[5],
                        "created_at": row[6],
                    }
                )

            return predictions
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []
        finally:
            conn.close()

    def get_processing_stats(self):
        """Get data processing statistics"""
        conn = self.get_db_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()

            # Get counts for different data types
            stats = {}

            # Cards processed today
            cursor.execute(
                """
                SELECT COUNT(*) FROM cards 
                WHERE DATE(created_at) = CURRENT_DATE
            """
            )
            stats["cards_today"] = cursor.fetchone()[0]

            # Results processed today
            cursor.execute(
                """
                SELECT COUNT(*) FROM results 
                WHERE DATE(created_at) = CURRENT_DATE
            """
            )
            stats["results_today"] = cursor.fetchone()[0]

            # Total records
            cursor.execute("SELECT COUNT(*) FROM cards")
            stats["total_cards"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM results")
            stats["total_results"] = cursor.fetchone()[0]

            return stats
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {}
        finally:
            conn.close()


# Initialize web app API
web_api = WebAppAPI()


@app.route("/")
def dashboard():
    """Main dashboard"""
    api_status = web_api.get_api_status()
    recent_predictions = web_api.get_recent_predictions()
    processing_stats = web_api.get_processing_stats()

    return render_template(
        "dashboard.html",
        api_status=api_status,
        predictions=recent_predictions,
        stats=processing_stats,
    )


@app.route("/data-processing")
def data_processing():
    """Data processing control panel"""
    return render_template("data_processing.html")


@app.route("/api/trigger-processing", methods=["POST"])
def trigger_processing():
    """Trigger data processing via Node-RED"""
    data = request.get_json()

    processing_type = data.get("type", "both")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    # Prepare data for Node-RED
    trigger_data = {
        "type": processing_type,
        "start_date": start_date,
        "end_date": end_date,
        "source": "web_app",
    }

    # Trigger Node-RED flow
    result = web_api.trigger_node_red_flow("data_processing", trigger_data)

    if result:
        return jsonify(
            {"status": "success", "message": "Processing triggered successfully"}
        )
    else:
        return (
            jsonify({"status": "error", "message": "Failed to trigger processing"}),
            500,
        )


@app.route("/api/trigger-pipeline", methods=["POST"])
def trigger_full_pipeline():
    """Trigger full pipeline via Node-RED"""
    result = web_api.trigger_node_red_flow("full_pipeline")

    if result:
        return jsonify(
            {"status": "success", "message": "Full pipeline triggered successfully"}
        )
    else:
        return (
            jsonify({"status": "error", "message": "Failed to trigger pipeline"}),
            500,
        )


@app.route("/api/system-status")
def system_status():
    """Get system status"""
    status = web_api.get_api_status()
    stats = web_api.get_processing_stats()

    return jsonify(
        {
            "api_status": status,
            "processing_stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/predictions")
def get_predictions():
    """Get predictions API endpoint"""
    limit = request.args.get("limit", 20, type=int)
    predictions = web_api.get_recent_predictions(limit)

    return jsonify({"predictions": predictions})


@app.route("/predictions")
def predictions_page():
    """Predictions display page"""
    predictions = web_api.get_recent_predictions(50)
    return render_template("predictions.html", predictions=predictions)


@app.route("/api/start-apis", methods=["POST"])
def start_apis():
    """Start APIs via Node-RED"""
    result = web_api.trigger_node_red_flow("start_apis")

    if result:
        return jsonify({"status": "success", "message": "APIs start triggered"})
    else:
        return jsonify({"status": "error", "message": "Failed to start APIs"}), 500


@app.route("/api/test-database", methods=["POST"])
def test_database():
    """Test database connection"""
    conn = web_api.get_db_connection()

    if conn:
        conn.close()
        return jsonify(
            {"status": "success", "message": "Database connection successful"}
        )
    else:
        return (
            jsonify({"status": "error", "message": "Database connection failed"}),
            500,
        )


@app.route("/monitoring")
def monitoring():
    """System monitoring page"""
    api_status = web_api.get_api_status()
    stats = web_api.get_processing_stats()

    return render_template("monitoring.html", api_status=api_status, stats=stats)


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    logger.info("Starting Horse Racing AI Web Application")
    app.run(host="0.0.0.0", port=8080, debug=True)
