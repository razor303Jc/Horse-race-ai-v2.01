#!/usr/bin/env python3
"""
Enhanced API and Web Interface Pipeline Integration - V2.03
===========================================================

Pipeline integration for Point #9: API and Web Interface Enhancements
Integrates the enhanced API server with modern features into the V2.03 pipeline.
"""

import asyncio
import json
import logging
import multiprocessing
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced API server
from tools.web_interface.enhanced_api_server import EnhancedAPIServer

logger = logging.getLogger(__name__)


class EnhancedWebInterfacePipeline:
    """Pipeline wrapper for the Enhanced API and Web Interface System."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the enhanced web interface pipeline."""
        self.config_path = config_path or self._get_default_config_path()
        self.server_process = None
        self.is_running = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        logger.info("Enhanced Web Interface Pipeline initialized")

    def _get_default_config_path(self) -> str:
        """Get default configuration path."""
        config_path = project_root / "config" / "enhanced_api_config.json"
        if config_path.exists():
            return str(config_path)
        return None

    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate that all required dependencies are available."""
        validation_results = {
            "status": "success",
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        try:
            # Check PostgreSQL connection
            try:
                import psycopg2

                # Try to create a test server instance to validate config
                test_server = EnhancedAPIServer(config_path=self.config_path)
                conn = test_server.get_db_connection()
                conn.close()
                validation_results["checks"][
                    "database"
                ] = "✅ PostgreSQL connection successful"
            except Exception as e:
                validation_results["errors"].append(f"Database connection failed: {e}")
                validation_results["checks"][
                    "database"
                ] = "❌ PostgreSQL connection failed"

            # Check Redis connection (optional)
            try:
                import redis

                if self.config_path:
                    with open(self.config_path, "r") as f:
                        config = json.load(f)
                    redis_config = config.get("redis", {})
                    r = redis.Redis(
                        host=redis_config.get("host", "localhost"),
                        port=redis_config.get("port", 6379),
                        db=redis_config.get("db", 0),
                        password=redis_config.get("password"),
                    )
                    r.ping()
                    validation_results["checks"][
                        "redis"
                    ] = "✅ Redis connection successful"
                else:
                    validation_results["warnings"].append(
                        "No config file - Redis will use defaults"
                    )
                    validation_results["checks"][
                        "redis"
                    ] = "⚠️ Redis using default settings"
            except Exception as e:
                validation_results["warnings"].append(f"Redis connection failed: {e}")
                validation_results["checks"][
                    "redis"
                ] = "⚠️ Redis unavailable (will use fallback)"

            # Check required Python packages
            required_packages = [
                "fastapi",
                "uvicorn",
                "psycopg2",
                "jwt",
                "bcrypt",
                "slowapi",
                "jinja2",
                "websockets",
            ]

            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                    validation_results["checks"][
                        f"package_{package}"
                    ] = f"✅ {package} available"
                except ImportError:
                    missing_packages.append(package)
                    validation_results["checks"][
                        f"package_{package}"
                    ] = f"❌ {package} missing"

            if missing_packages:
                validation_results["errors"].append(
                    f"Missing required packages: {', '.join(missing_packages)}"
                )

            # Check template directory
            template_dir = project_root / "templates"
            if template_dir.exists():
                validation_results["checks"][
                    "templates"
                ] = "✅ Template directory found"
            else:
                validation_results["warnings"].append("Template directory not found")
                validation_results["checks"][
                    "templates"
                ] = "⚠️ Template directory missing"

            # Overall status
            if validation_results["errors"]:
                validation_results["status"] = "error"
            elif validation_results["warnings"]:
                validation_results["status"] = "warning"

        except Exception as e:
            validation_results["status"] = "error"
            validation_results["errors"].append(f"Validation failed: {e}")

        return validation_results

    def start_server(self) -> Dict[str, Any]:
        """Start the enhanced API server."""
        try:
            if self.is_running:
                return {
                    "status": "already_running",
                    "message": "Enhanced API server is already running",
                    "process_id": (
                        self.server_process.pid if self.server_process else None
                    ),
                }

            logger.info("Starting Enhanced API Server...")

            # Validate dependencies before starting
            validation = self.validate_dependencies()
            if validation["status"] == "error":
                return {
                    "status": "error",
                    "message": "Dependency validation failed",
                    "validation": validation,
                }

            # Start server in separate process
            def run_server():
                server = EnhancedAPIServer(config_path=self.config_path)
                server.run()

            self.server_process = multiprocessing.Process(target=run_server)
            self.server_process.start()
            self.is_running = True

            # Wait a moment to check if server started successfully
            time.sleep(2)

            if self.server_process.is_alive():
                logger.info(
                    f"Enhanced API Server started successfully (PID: {self.server_process.pid})"
                )
                return {
                    "status": "success",
                    "message": "Enhanced API server started successfully",
                    "process_id": self.server_process.pid,
                    "server_url": self._get_server_url(),
                    "features": [
                        "Real-time WebSocket updates",
                        "User authentication system",
                        "Advanced search and filtering",
                        "Mobile-responsive design",
                        "API rate limiting",
                        "Redis session management",
                    ],
                    "validation": validation,
                }
            else:
                self.is_running = False
                return {
                    "status": "error",
                    "message": "Enhanced API server failed to start",
                    "process_id": None,
                }

        except Exception as e:
            logger.error(f"Failed to start Enhanced API server: {e}")
            self.is_running = False
            return {
                "status": "error",
                "message": f"Failed to start server: {e}",
                "process_id": None,
            }

    def stop_server(self) -> Dict[str, Any]:
        """Stop the enhanced API server."""
        try:
            if not self.is_running or not self.server_process:
                return {
                    "status": "not_running",
                    "message": "Enhanced API server is not running",
                }

            logger.info("Stopping Enhanced API Server...")

            # Terminate the server process
            self.server_process.terminate()
            self.server_process.join(timeout=5)

            if self.server_process.is_alive():
                # Force kill if it doesn't terminate gracefully
                self.server_process.kill()
                self.server_process.join()

            self.is_running = False
            self.server_process = None

            logger.info("Enhanced API Server stopped successfully")
            return {
                "status": "success",
                "message": "Enhanced API server stopped successfully",
            }

        except Exception as e:
            logger.error(f"Failed to stop Enhanced API server: {e}")
            return {"status": "error", "message": f"Failed to stop server: {e}"}

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the enhanced API server."""
        try:
            if not self.is_running or not self.server_process:
                return {
                    "status": "stopped",
                    "message": "Enhanced API server is not running",
                    "process_id": None,
                    "uptime": 0,
                }

            if self.server_process.is_alive():
                return {
                    "status": "running",
                    "message": "Enhanced API server is running",
                    "process_id": self.server_process.pid,
                    "server_url": self._get_server_url(),
                    "features_enabled": {
                        "websocket": True,
                        "authentication": True,
                        "rate_limiting": True,
                        "advanced_search": True,
                        "mobile_responsive": True,
                    },
                }
            else:
                self.is_running = False
                self.server_process = None
                return {
                    "status": "crashed",
                    "message": "Enhanced API server process has crashed",
                    "process_id": None,
                }

        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            return {
                "status": "error",
                "message": f"Failed to get status: {e}",
                "process_id": None,
            }

    def restart_server(self) -> Dict[str, Any]:
        """Restart the enhanced API server."""
        logger.info("Restarting Enhanced API Server...")

        # Stop the server
        stop_result = self.stop_server()
        if stop_result["status"] not in ["success", "not_running"]:
            return {
                "status": "error",
                "message": f"Failed to stop server for restart: {stop_result['message']}",
            }

        # Wait a moment
        time.sleep(1)

        # Start the server
        start_result = self.start_server()
        if start_result["status"] == "success":
            return {
                "status": "success",
                "message": "Enhanced API server restarted successfully",
                "process_id": start_result["process_id"],
                "server_url": start_result["server_url"],
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to start server after restart: {start_result['message']}",
            }

    def _get_server_url(self) -> str:
        """Get the server URL from configuration."""
        try:
            if self.config_path and os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                server_config = config.get("server", {})
                host = server_config.get("host", "0.0.0.0")
                port = server_config.get("port", 8000)

                # Convert 0.0.0.0 to localhost for display
                display_host = "localhost" if host == "0.0.0.0" else host
                return f"http://{display_host}:{port}"
            else:
                return "http://localhost:8000"
        except Exception:
            return "http://localhost:8000"

    def run_stage(self, action: str = "start") -> Dict[str, Any]:
        """Run the enhanced web interface stage."""
        logger.info(f"Running Enhanced Web Interface Pipeline - Action: {action}")

        if action == "start":
            return self.start_server()
        elif action == "stop":
            return self.stop_server()
        elif action == "restart":
            return self.restart_server()
        elif action == "status":
            return self.get_status()
        elif action == "validate":
            return self.validate_dependencies()
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Supported actions: start, stop, restart, status, validate",
            }

    def cleanup(self):
        """Cleanup resources."""
        if self.is_running:
            self.stop_server()


def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced API and Web Interface Pipeline - V2.03"
    )
    parser.add_argument("--config", help="Path to configuration file", default=None)
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "validate"],
        default="start",
        help="Action to perform",
    )

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = EnhancedWebInterfacePipeline(config_path=args.config)

    try:
        # Run the requested action
        result = pipeline.run_stage(action=args.action)

        # Print results
        print(f"\n{'='*60}")
        print(f"Enhanced API and Web Interface Pipeline - V2.03")
        print(f"{'='*60}")
        print(f"Action: {args.action}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")

        if result.get("process_id"):
            print(f"Process ID: {result['process_id']}")

        if result.get("server_url"):
            print(f"Server URL: {result['server_url']}")

        if result.get("features"):
            print(f"\nEnabled Features:")
            for feature in result["features"]:
                print(f"  ✅ {feature}")

        if result.get("validation"):
            validation = result["validation"]
            print(f"\nDependency Validation:")
            for check, status in validation["checks"].items():
                print(f"  {status}")

            if validation.get("warnings"):
                print(f"\nWarnings:")
                for warning in validation["warnings"]:
                    print(f"  ⚠️ {warning}")

            if validation.get("errors"):
                print(f"\nErrors:")
                for error in validation["errors"]:
                    print(f"  ❌ {error}")

        print(f"{'='*60}\n")

        # If starting the server, keep running
        if args.action == "start" and result["status"] == "success":
            print("Enhanced API Server is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down Enhanced API Server...")
                pipeline.stop_server()
                print("Server stopped.")

        # Exit with appropriate code
        sys.exit(0 if result["status"] in ["success", "already_running"] else 1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        pipeline.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        pipeline.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
