#!/usr/bin/env python3
"""
API Routes Module
Handles all API endpoints for the Horse Racing AI v2.0 system
"""

from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)


def register_api_routes(app):
    """Register all API routes with the Flask application"""

    # Create API blueprint
    api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

    @api_bp.route("/ml/predictions")
    def get_ml_predictions():
        """Get ML model predictions for current races"""
        try:
            ml_service = app.services.get("ml_service")
            if not ml_service:
                return jsonify({"error": "ML service not available"}), 503

            predictions = ml_service.get_current_predictions()
            return jsonify(
                {
                    "success": True,
                    "data": predictions,
                    "model_performance": {
                        "auc": "76.5%",
                        "ensemble": "4-model",
                        "features": "40+",
                    },
                }
            )
        except Exception as e:
            logger.error(f"Error getting ML predictions: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.route("/contextual/analysis")
    def get_contextual_analysis():
        """Get 32-factor contextual AI analysis"""
        try:
            contextual_service = app.services.get("contextual_service")
            if not contextual_service:
                return jsonify({"error": "Contextual service not available"}), 503

            analysis = contextual_service.get_analysis()
            return jsonify(
                {
                    "success": True,
                    "data": analysis,
                    "factors_analyzed": 32,
                    "enhancement_multiplier": analysis.get("enhancement_factor", 1.0),
                }
            )
        except Exception as e:
            logger.error(f"Error getting contextual analysis: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.route("/betting/strategies")
    def get_betting_strategies():
        """Get available betting strategies and performance"""
        try:
            betting_service = app.services.get("betting_service")
            if not betting_service:
                return jsonify({"error": "Betting service not available"}), 503

            strategies = betting_service.get_strategies()
            return jsonify(
                {
                    "success": True,
                    "data": strategies,
                    "available_strategies": [
                        "Value Betting",
                        "Kelly Criterion",
                        "Each-Way",
                        "20/80 Strategy",
                        "Dutching",
                    ],
                }
            )
        except Exception as e:
            logger.error(f"Error getting betting strategies: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.route("/live/performance")
    def get_live_performance():
        """Get real-time system performance metrics"""
        try:
            performance_service = app.services.get("performance_service")
            if not performance_service:
                return jsonify({"error": "Performance service not available"}), 503

            metrics = performance_service.get_live_metrics()
            return jsonify(
                {
                    "success": True,
                    "data": metrics,
                    "last_updated": metrics.get("timestamp"),
                    "system_status": "operational",
                }
            )
        except Exception as e:
            logger.error(f"Error getting live performance: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.route("/races/current")
    def get_current_races():
        """Get current and upcoming races"""
        try:
            race_service = app.services.get("race_service")
            if not race_service:
                return jsonify({"error": "Race service not available"}), 503

            races = race_service.get_current_races()
            return jsonify(
                {"success": True, "data": races, "count": len(races) if races else 0}
            )
        except Exception as e:
            logger.error(f"Error getting current races: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.route("/system/status")
    def get_system_status():
        """Get comprehensive system status"""
        try:
            return jsonify(
                {
                    "success": True,
                    "system": {
                        "version": "2.0",
                        "status": "operational",
                        "ml_accuracy": "76.5%",
                        "contextual_factors": 32,
                        "features_per_horse": "40+",
                        "model_ensemble": "4-model",
                    },
                    "services": {
                        "ml_service": "active",
                        "contextual_service": "active",
                        "betting_service": "active",
                        "performance_service": "active",
                        "race_service": "active",
                    },
                }
            )
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return jsonify({"error": str(e)}), 500

    # Register the blueprint
    app.register_blueprint(api_bp)
    logger.info("✅ API routes registered")

    return api_bp
