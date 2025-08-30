#!/usr/bin/env python3
"""
Pipeline API Handler for Node-RED C2 Integration
=============================================

This module provides a REST API interface for Node-RED to interact with
the horse racing data pipeline. It wraps existing pipeline commands and
provides standardized responses for the C2 Command Center.

Created: August 30, 2025
Author: Horse Racing AI System
"""

import os
import sys
import json
import subprocess
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineAPIHandler:
    """
    Main API handler for pipeline operations accessible from Node-RED
    """

    def __init__(self):
        self.redis_client = self._init_redis()
        self.db_config = self._get_db_config()

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection"""
        try:
            client = redis.Redis(
                host="redis",
                port=6379,
                password="redis_password_123",
                decode_responses=True,
            )
            client.ping()
            logger.info("Redis connection established")
            return client
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return {
            "host": "postgres",
            "port": "5432",
            "dbname": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def _execute_command(
        self, command: List[str], cwd: str = "/app/tools"
    ) -> Dict[str, Any]:
        """
        Execute a command and return standardized response
        """
        try:
            logger.info(f"Executing command: {' '.join(command)}")

            # Update pipeline status
            self.redis_client.set("pipeline:status", "running")
            self.redis_client.set("pipeline:last_command", " ".join(command))
            self.redis_client.set("pipeline:start_time", datetime.now().isoformat())

            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            response = {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command),
                "timestamp": datetime.now().isoformat(),
            }

            # Update Redis with results
            status = "completed" if result.returncode == 0 else "failed"
            self.redis_client.set("pipeline:status", status)
            self.redis_client.set("pipeline:last_result", json.dumps(response))

            logger.info(f"Command completed with return code: {result.returncode}")
            return response

        except subprocess.TimeoutExpired:
            response = {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "timestamp": datetime.now().isoformat(),
            }
            self.redis_client.set("pipeline:status", "timeout")
            return response

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            response = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
            }
            self.redis_client.set("pipeline:status", "error")
            return response

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for C2 dashboard
        """
        try:
            status = {
                "pipeline": {
                    "status": self.redis_client.get("pipeline:status") or "ready",
                    "last_command": self.redis_client.get("pipeline:last_command")
                    or "none",
                    "start_time": self.redis_client.get("pipeline:start_time")
                    or "none",
                    "uptime": self._get_uptime(),
                },
                "database": self._check_database_status(),
                "redis": self._check_redis_status(),
                "services": self._check_service_status(),
                "timestamp": datetime.now().isoformat(),
            }
            return status

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def start_data_validation(self) -> Dict[str, Any]:
        """
        Start data validation process
        """
        # Use today's date for validation
        from datetime import date

        today = date.today().strftime("%Y-%m-%d")
        command = [
            "python",
            "node_red_data_processor.py",
            "--start-date",
            today,
            "--end-date",
            today,
            "--type",
            "both",
            "--output-format",
            "json",
        ]
        return self._execute_command(command)

    def process_data(self) -> Dict[str, Any]:
        """
        Start data processing
        """
        command = ["python", "manual_pipeline_trigger.py"]
        return self._execute_command(command)

    def start_ml_training(self) -> Dict[str, Any]:
        """
        Start ML training process
        """
        command = ["python", "v2_01_ensemble_trainer.py"]
        return self._execute_command(command)

    def upload_data(self) -> Dict[str, Any]:
        """
        Start data upload process
        """
        command = ["python", "quick_upload_today.py"]
        return self._execute_command(command)

    def generate_ratings(self) -> Dict[str, Any]:
        """
        Generate AI ratings and selections
        """
        command = ["python", "enhanced_ai_selections_generator.py"]
        return self._execute_command(command)

    def emergency_stop(self) -> Dict[str, Any]:
        """
        Emergency stop all pipeline processes
        """
        try:
            logger.warning("Emergency stop initiated")

            # Set emergency stop status
            self.redis_client.set("pipeline:status", "emergency_stop")
            self.redis_client.set(
                "pipeline:emergency_stop_time", datetime.now().isoformat()
            )

            # Kill any running Python processes (be careful with this)
            kill_command = ["pkill", "-f", "python.*pipeline"]
            result = subprocess.run(kill_command, capture_output=True, text=True)

            return {
                "success": True,
                "message": "Emergency stop executed",
                "killed_processes": result.stdout,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_logs(self, lines: int = 100) -> Dict[str, Any]:
        """
        Get recent pipeline logs
        """
        try:
            # Get logs from multiple sources
            logs = {
                "pipeline_logs": self._get_file_logs("/app/logs/pipeline.log", lines),
                "system_logs": self._get_redis_logs(lines),
                "timestamp": datetime.now().isoformat(),
            }
            return logs

        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            result = subprocess.run(["uptime"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

    def _check_database_status(self) -> Dict[str, Any]:
        """Check database connectivity and status"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Check basic connectivity
            cursor.execute("SELECT 1")

            # Get database stats - simplified query
            cursor.execute(
                """
                SELECT 
                    schemaname,
                    relname as tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables 
                ORDER BY schemaname, relname
                LIMIT 10
            """
            )

            stats = cursor.fetchall()
            conn.close()

            return {
                "status": "connected",
                "recent_activity": [dict(row) for row in stats],
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_redis_status(self) -> Dict[str, Any]:
        """Check Redis status"""
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "memory_used": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_service_status(self) -> List[Dict[str, Any]]:
        """Check status of various services"""
        services = []

        # Check Python processes
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            python_processes = [
                line for line in result.stdout.split("\n") if "python" in line
            ]

            services.append(
                {
                    "name": "python_processes",
                    "status": "running",
                    "count": len(python_processes),
                    "details": python_processes[:5],  # First 5 processes
                }
            )
        except:
            services.append(
                {
                    "name": "python_processes",
                    "status": "error",
                    "error": "Could not check processes",
                }
            )

        return services

    def _get_file_logs(self, filepath: str, lines: int) -> List[str]:
        """Get logs from a file"""
        try:
            result = subprocess.run(
                ["tail", f"-{lines}", filepath], capture_output=True, text=True
            )
            return result.stdout.split("\n")
        except:
            return ["Log file not accessible"]

    def _get_redis_logs(self, lines: int) -> List[str]:
        """Get logs from Redis"""
        try:
            logs = []
            # Get recent pipeline events from Redis
            for i in range(min(lines, 50)):  # Limit to 50 entries
                log_entry = self.redis_client.get(f"pipeline:log:{i}")
                if log_entry:
                    logs.append(log_entry)
            return logs or ["No Redis logs available"]
        except:
            return ["Redis logs not accessible"]


def main():
    """
    Main function for command-line usage
    """
    if len(sys.argv) < 2:
        print("Usage: python pipeline_api_handler.py <command> [args]")
        print("Commands: status, validate, process, train, upload, ratings, stop, logs")
        sys.exit(1)

    handler = PipelineAPIHandler()
    command = sys.argv[1].lower()

    try:
        if command == "status":
            result = handler.get_system_status()
        elif command == "validate":
            result = handler.start_data_validation()
        elif command == "process":
            result = handler.process_data()
        elif command == "train":
            result = handler.start_ml_training()
        elif command == "upload":
            result = handler.upload_data()
        elif command == "ratings":
            result = handler.generate_ratings()
        elif command == "stop":
            result = handler.emergency_stop()
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            result = handler.get_logs(lines)
        else:
            result = {"error": f"Unknown command: {command}"}

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
