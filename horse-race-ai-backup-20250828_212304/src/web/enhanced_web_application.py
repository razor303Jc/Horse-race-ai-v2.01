#!/usr/bin/env python3
"""
Enhanced Web Application - Flask + React Integration
==================================================

This module creates the enhanced Flask application that serves both the API
and the React frontend for the Horse Racing AI system.

Features:
- Flask backend with comprehensive API endpoints
- React frontend integration
- Real-time data updates
- Enhanced racing list with filtering and sorting
- Professional dashboard with analytics
- BETDAQ integration ready
"""

import os
import sys
from pathlib import Path

from flask import Flask, render_template_string, send_from_directory
from flask_cors import CORS

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def create_enhanced_app():
    """Create and configure the enhanced Flask application"""

    app = Flask(__name__, static_folder="dist", static_url_path="")
    CORS(app)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["DEBUG"] = os.environ.get("DEBUG", "false").lower() == "true"

    @app.route("/")
    def index():
        """Serve the React app"""
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        """Serve static files"""
        return send_from_directory(app.static_folder, path)

    # Import and register API routes
    try:
        from .api_server_enhanced import app as api_app

        # Mount the FastAPI app under /api
        # Note: This is a simplified approach. In production, consider using
        # a proper ASGI/WSGI adapter or run them separately

        @app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
        def api_proxy(path):
            """Proxy API requests to FastAPI server"""
            # In production, this should be handled by a reverse proxy
            import json

            import requests
            from flask import request

            # Forward the request to the FastAPI server
            api_url = f"http://localhost:8001/api/{path}"

            try:
                if request.method == "GET":
                    response = requests.get(api_url, params=request.args)
                elif request.method == "POST":
                    response = requests.post(api_url, json=request.get_json())
                elif request.method == "PUT":
                    response = requests.put(api_url, json=request.get_json())
                elif request.method == "DELETE":
                    response = requests.delete(api_url)

                return response.json(), response.status_code
            except Exception as e:
                return {"error": f"API unavailable: {str(e)}"}, 503

    except ImportError:
        # Fallback if FastAPI server is not available
        @app.route("/api/<path:path>")
        def api_fallback(path):
            return {"error": "API server not available"}, 503

    # Health check endpoint
    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "enhanced_web_application"}

    return app


if __name__ == "__main__":
    # For development - run Flask directly
    app = create_enhanced_app()
    app.run(host="127.0.0.1", port=5002, debug=True)
