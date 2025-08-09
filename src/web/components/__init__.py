#!/usr/bin/env python3
"""
Web Components Module
Handles all web page routes and components for the Horse Racing AI v2.0 system
"""

from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)


def register_component_routes(app):
    """Register all component routes with the Flask application"""

    # Create main blueprint
    main_bp = Blueprint("main", __name__)

    @main_bp.route("/")
    def dashboard():
        """Main dashboard with comprehensive system overview"""
        try:
            # Get services
            ml_service = app.services.get("ml_service")
            performance_service = app.services.get("performance_service")

            # Get dashboard data
            dashboard_data = {
                "system_status": "operational",
                "ml_accuracy": "76.5%",
                "model_ensemble": "4-Model",
                "contextual_factors": 32,
                "features_per_horse": "40+",
                "current_races": [],
                "recent_performance": {},
                "live_metrics": {},
            }

            # Try to get live data
            if ml_service:
                dashboard_data["current_predictions"] = (
                    ml_service.get_current_predictions()
                )

            if performance_service:
                dashboard_data["live_metrics"] = performance_service.get_live_metrics()

            return render_template("enhanced_dashboard.html", **dashboard_data)

        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            return render_template(
                "error.html", error="Dashboard loading error", message=str(e)
            )

    @main_bp.route("/ml-performance")
    def ml_performance():
        """ML Models performance and analysis page"""
        try:
            ml_service = app.services.get("ml_service")

            performance_data = {
                "model_accuracy": {
                    "Random Forest": "76.19%",
                    "Gradient Boosting": "76.50%",
                    "Logistic Regression": "75.47%",
                    "Neural Network": "65.76%",
                },
                "ensemble_auc": "76.5%",
                "features_engineered": "40+",
                "training_records": "308K+",
                "model_weights": {
                    "Random Forest": 25,
                    "Gradient Boosting": 35,
                    "Logistic Regression": 25,
                    "Neural Network": 15,
                },
            }

            if ml_service:
                performance_data["live_predictions"] = (
                    ml_service.get_current_predictions()
                )
                performance_data["model_health"] = ml_service.get_model_health()

            return render_template("ml_performance.html", **performance_data)

        except Exception as e:
            logger.error(f"Error loading ML performance: {e}")
            return render_template(
                "error.html", error="ML Performance loading error", message=str(e)
            )

    @main_bp.route("/live-analysis")
    def live_analysis():
        """Live race analysis and predictions page"""
        try:
            race_service = app.services.get("race_service")
            contextual_service = app.services.get("contextual_service")

            analysis_data = {
                "current_races": [],
                "contextual_analysis": {},
                "enhancement_factor": 1.0,
                "live_predictions": [],
                "betting_opportunities": [],
            }

            if race_service:
                analysis_data["current_races"] = race_service.get_current_races()

            if contextual_service:
                contextual = contextual_service.get_analysis()
                analysis_data["contextual_analysis"] = contextual
                analysis_data["enhancement_factor"] = contextual.get(
                    "enhancement_factor", 1.0
                )

            return render_template("live_analysis.html", **analysis_data)

        except Exception as e:
            logger.error(f"Error loading live analysis: {e}")
            return render_template(
                "error.html", error="Live Analysis loading error", message=str(e)
            )

    @main_bp.route("/betting-strategies")
    def betting_strategies():
        """Betting strategies and performance page"""
        try:
            betting_service = app.services.get("betting_service")

            betting_data = {
                "available_strategies": [
                    "Value Betting",
                    "Kelly Criterion",
                    "Each-Way",
                    "20/80 Strategy",
                    "Dutching",
                ],
                "strategy_performance": {},
                "current_opportunities": [],
                "risk_management": {
                    "max_bet_percentage": "5%",
                    "kelly_multiplier": "0.25",
                    "confidence_threshold": "70%",
                },
            }

            if betting_service:
                betting_data["strategy_performance"] = betting_service.get_performance()
                betting_data["current_opportunities"] = (
                    betting_service.get_opportunities()
                )

            return render_template("betting_strategies.html", **betting_data)

        except Exception as e:
            logger.error(f"Error loading betting strategies: {e}")
            return render_template(
                "error.html", error="Betting Strategies loading error", message=str(e)
            )

    @main_bp.route("/system-monitor")
    def system_monitor():
        """System monitoring and health page"""
        try:
            performance_service = app.services.get("performance_service")

            monitor_data = {
                "system_health": "excellent",
                "service_status": {
                    "ml_service": "active",
                    "contextual_service": "active",
                    "betting_service": "active",
                    "race_service": "active",
                    "performance_service": "active",
                },
                "performance_metrics": {},
                "alerts": [],
            }

            if performance_service:
                monitor_data["performance_metrics"] = (
                    performance_service.get_comprehensive_metrics()
                )
                monitor_data["alerts"] = performance_service.get_alerts()

            return render_template("system_monitor.html", **monitor_data)

        except Exception as e:
            logger.error(f"Error loading system monitor: {e}")
            return render_template(
                "error.html", error="System Monitor loading error", message=str(e)
            )

    # Register the blueprint
    app.register_blueprint(main_bp)
    logger.info("✅ Component routes registered")

    return main_bp
