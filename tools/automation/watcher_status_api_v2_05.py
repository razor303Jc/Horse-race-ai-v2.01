#!/usr/bin/env python3
"""
Enhanced File Watcher v2.05 - Status Dashboard Integration
Node-RED C2 Command Center Integration Script

This script provides API endpoints and status interfaces for the
Node-RED C2 Command Center to monitor and control the Enhanced File Watcher v2.05.

Features:
- Real-time status reporting
- Pipeline control integration
- Health monitoring
- Performance metrics
- Error tracking and reporting
- Configuration management

Author: Horse Racing AI System
Version: v2.05 - Latest
"""

import json
import os
import sys
import time
import redis
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatcherStatusAPI:
    """API interface for Enhanced File Watcher v2.05 status reporting"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.05"):
        self.base_path = Path(base_path)
        self.version = "v2.05"

        # Initialize connections
        self.redis_client = self._init_redis()
        self.db_config = self._get_db_config()

        # Status files
        self.state_file = self.base_path / "data/watcher_state_v2_05.json"
        self.status_file = self.base_path / "data/watcher_status_v2_05.json"
        self.config_file = self.base_path / "config/enhanced_watcher_config_v2_05.json"
        self.pid_file = self.base_path / "logs/watcher_v2_05.pid"
        self.log_file = self.base_path / "logs/enhanced_file_watcher_v2_05.log"

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection"""
        try:
            client = redis.Redis(
                host="redis",
                port=6379,
                password="redis_password_123",
                decode_responses=True,
            )
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return {
            "host": "postgres",
            "port": "5432",
            "dbname": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def get_service_status(self) -> Dict[str, Any]:
        """Get overall service status"""
        try:
            # Check if service is running
            is_running = False
            pid = None
            uptime = 0

            if self.pid_file.exists():
                try:
                    with open(self.pid_file, "r") as f:
                        pid = int(f.read().strip())

                    # Check if process is actually running
                    import subprocess

                    result = subprocess.run(
                        ["ps", "-p", str(pid)], capture_output=True, text=True
                    )
                    is_running = result.returncode == 0

                    if is_running and self.state_file.exists():
                        with open(self.state_file, "r") as f:
                            state = json.load(f)
                            startup_time = datetime.fromisoformat(
                                state.get("last_startup", datetime.now().isoformat())
                            )
                            uptime = (
                                datetime.now() - startup_time
                            ).total_seconds() / 3600

                except Exception as e:
                    logger.warning(f"Error checking service status: {e}")

            return {
                "version": self.version,
                "status": "running" if is_running else "stopped",
                "pid": pid,
                "uptime_hours": round(uptime, 2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "version": self.version,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status from Redis"""
        try:
            if not self.redis_client:
                return {"error": "Redis not available"}

            # Get status from Redis
            summary = self.redis_client.get("watcher:summary")
            if summary:
                return json.loads(summary)

            # Fallback to file-based status
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    state = json.load(f)

                return {
                    "version": self.version,
                    "cards_ready": False,
                    "results_ready": False,
                    "form_ready": False,
                    "pipeline_active": False,
                    "completed_days": len(state.get("completed_days", [])),
                    "processing_queue": [],
                    "last_update": state.get("last_update", "unknown"),
                    "source": "file_fallback",
                }

            return {"error": "No status available"}

        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        health = {
            "overall": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        try:
            # Check Redis connectivity
            try:
                if self.redis_client:
                    self.redis_client.ping()
                    health["checks"]["redis"] = {
                        "status": "healthy",
                        "response_time_ms": 1,
                    }
                else:
                    health["checks"]["redis"] = {
                        "status": "unavailable",
                        "error": "No connection",
                    }
                    health["overall"] = "degraded"
            except Exception as e:
                health["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
                health["overall"] = "degraded"

            # Check database connectivity
            try:
                import psycopg2

                conn = psycopg2.connect(**self.db_config)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()
                health["checks"]["database"] = {"status": "healthy"}
            except Exception as e:
                health["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
                health["overall"] = "unhealthy"

            # Check Docker containers
            try:
                import subprocess

                containers = ["redis", "postgres", "horse_racing_data_pipeline_clean"]
                container_status = {}

                for container in containers:
                    result = subprocess.run(
                        ["docker", "inspect", "--format={{.State.Status}}", container],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        status = result.stdout.strip()
                        container_status[container] = status
                        if status != "running":
                            health["overall"] = "degraded"
                    else:
                        container_status[container] = "not_found"
                        health["overall"] = "unhealthy"

                health["checks"]["containers"] = container_status

            except Exception as e:
                health["checks"]["containers"] = {"error": str(e)}
                health["overall"] = "degraded"

            # Check file system
            try:
                # Check critical directories
                directories = [
                    self.base_path / "data/daily_downloads/manual_download",
                    self.base_path / "data/daily_downloads/auto_download",
                    self.base_path / "logs",
                ]

                fs_status = {}
                for directory in directories:
                    fs_status[str(directory)] = {
                        "exists": directory.exists(),
                        "writable": (
                            os.access(directory, os.W_OK)
                            if directory.exists()
                            else False
                        ),
                    }

                health["checks"]["filesystem"] = fs_status

            except Exception as e:
                health["checks"]["filesystem"] = {"error": str(e)}

            # Check log file size
            try:
                if self.log_file.exists():
                    log_size_mb = self.log_file.stat().st_size / (1024 * 1024)
                    health["checks"]["logs"] = {
                        "size_mb": round(log_size_mb, 2),
                        "status": "normal" if log_size_mb < 50 else "large",
                    }
                else:
                    health["checks"]["logs"] = {"status": "not_created"}

            except Exception as e:
                health["checks"]["logs"] = {"error": str(e)}

        except Exception as e:
            health["overall"] = "error"
            health["error"] = str(e)

        return health

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            metrics = {"timestamp": datetime.now().isoformat(), "version": self.version}

            # Get from Redis if available
            if self.redis_client:
                try:
                    # Get processing metrics
                    summary = self.redis_client.get("watcher:summary")
                    if summary:
                        summary_data = json.loads(summary)
                        metrics.update(
                            {
                                "success_count": summary_data.get("success_count", 0),
                                "error_count": summary_data.get("error_count", 0),
                                "uptime_hours": summary_data.get("uptime", 0),
                                "last_processed": summary_data.get("last_processed"),
                                "completed_days": summary_data.get("completed_days", 0),
                            }
                        )

                    # Get error history
                    last_error = self.redis_client.get("watcher:last_error")
                    if last_error:
                        metrics["last_error"] = json.loads(last_error)

                except Exception as e:
                    metrics["redis_error"] = str(e)

            # Get file-based metrics
            if self.state_file.exists():
                try:
                    with open(self.state_file, "r") as f:
                        state = json.load(f)

                    stats = state.get("statistics", {})
                    metrics.update(
                        {
                            "total_files_processed": stats.get(
                                "total_files_processed", 0
                            ),
                            "total_races_processed": stats.get(
                                "total_races_processed", 0
                            ),
                            "total_errors": stats.get("total_errors", 0),
                            "processing_history_count": len(
                                state.get("processing_history", [])
                            ),
                        }
                    )

                except Exception as e:
                    metrics["file_error"] = str(e)

            return metrics

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_configuration_info(self) -> Dict[str, Any]:
        """Get current configuration information"""
        try:
            config_info = {
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
            }

            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                config_info.update(
                    {
                        "config_version": config.get("version", "unknown"),
                        "auto_process": config.get("watcher_settings", {}).get(
                            "auto_process", False
                        ),
                        "pipeline_integration": config.get("watcher_settings", {}).get(
                            "pipeline_integration", False
                        ),
                        "validation_required": config.get("watcher_settings", {}).get(
                            "validation_required", False
                        ),
                        "retry_attempts": config.get("watcher_settings", {}).get(
                            "retry_attempts", 0
                        ),
                        "monitored_directories": len(
                            config.get("directory_structure", {}).get(
                                "watch_directories", []
                            )
                        ),
                        "data_types": list(config.get("file_patterns", {}).keys()),
                    }
                )
            else:
                config_info["error"] = "Configuration file not found"

            return config_info

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_recent_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get recent log entries"""
        try:
            if not self.log_file.exists():
                return {
                    "error": "Log file not found",
                    "timestamp": datetime.now().isoformat(),
                }

            # Read last N lines
            with open(self.log_file, "r") as f:
                log_lines = f.readlines()

            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines

            return {
                "lines": [line.strip() for line in recent_lines],
                "total_lines": len(log_lines),
                "requested_lines": lines,
                "returned_lines": len(recent_lines),
                "log_file_size_mb": round(
                    self.log_file.stat().st_size / (1024 * 1024), 2
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status for C2 dashboard"""
        try:
            return {
                "service": self.get_service_status(),
                "processing": self.get_processing_status(),
                "health": self.get_health_status(),
                "performance": self.get_performance_metrics(),
                "configuration": self.get_configuration_info(),
                "timestamp": datetime.now().isoformat(),
                "version": self.version,
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "version": self.version,
            }


def main():
    """Command line interface for status API"""
    if len(sys.argv) < 2:
        print("Usage: python3 watcher_status_api_v2_05.py [command]")
        print(
            "Commands: service, processing, health, performance, config, logs, comprehensive"
        )
        sys.exit(1)

    api = WatcherStatusAPI()
    command = sys.argv[1].lower()

    if command == "service":
        result = api.get_service_status()
    elif command == "processing":
        result = api.get_processing_status()
    elif command == "health":
        result = api.get_health_status()
    elif command == "performance":
        result = api.get_performance_metrics()
    elif command == "config":
        result = api.get_configuration_info()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        result = api.get_recent_logs(lines)
    elif command == "comprehensive":
        result = api.get_comprehensive_status()
    else:
        result = {"error": f"Unknown command: {command}"}

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
