#!/usr/bin/env python3
"""
🔍 System Health Monitor - Production Monitoring System
Comprehensive health monitoring for the horse racing AI system

Features:
- Real-time component health checks
- Database connectivity monitoring
- Container status verification
- Log analysis and error detection
- Performance metrics tracking
- HTML dashboard generation
- Alert notifications via NTFY

Author: AI Assistant
Date: August 11, 2025
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class HealthCheck:
    """Represents a component health check result."""

    name: str
    status: str  # healthy, warning, critical
    response_time_ms: float
    error_count: int
    details: str
    last_check: datetime


@dataclass
class SystemMetrics:
    """System performance metrics."""

    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_connections: int
    uptime_hours: float


class SystemHealthMonitor:
    """Main system health monitoring class."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "reports" / "monitoring"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Database connection details
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # NTFY notification settings - try localhost first, fallback to container name
        try:
            # Test if we can reach localhost (when running outside Docker)
            test_response = requests.get("http://localhost:8081", timeout=2)
            self.ntfy_url = "http://localhost:8081"
        except:
            # Fallback to container name (when running inside Docker)
            self.ntfy_url = "http://ntfy:8081"

        self.ntfy_topic = "horse-racing-alerts"

    def check_database_health(self) -> HealthCheck:
        """Check PostgreSQL database connectivity and performance."""
        start_time = time.time()

        try:
            import psycopg2

            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Test basic connectivity
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Check table existence and record counts
            tables_check = []
            test_tables = [
                "race_results",
                "races_cards",
                "horses",
                "jockey_stats",
                "trainer_stats",
                "racecard_details",
            ]

            for table in test_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    tables_check.append(f"{table}: {count} records")
                except Exception as e:
                    tables_check.append(f"{table}: ERROR - {str(e)}")

            cursor.close()
            conn.close()

            response_time = (time.time() - start_time) * 1000
            details = f"Connected successfully. Tables: {', '.join(tables_check)}"

            return HealthCheck(
                name="PostgreSQL Database",
                status="healthy",
                response_time_ms=response_time,
                error_count=0,
                details=details,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="PostgreSQL Database",
                status="critical",
                response_time_ms=response_time,
                error_count=1,
                details=f"Database connection failed: {str(e)}",
                last_check=datetime.now(),
            )

    def check_redis_health(self) -> HealthCheck:
        """Check Redis connectivity and performance."""
        start_time = time.time()

        try:
            import redis

            r = redis.Redis(
                host="localhost",
                port=6380,
                password="redis_password_123",
                decode_responses=True,
            )

            # Test basic connectivity
            r.ping()

            # Get Redis info
            info = r.info()
            connected_clients = info.get("connected_clients", 0)
            used_memory = info.get("used_memory_human", "unknown")

            response_time = (time.time() - start_time) * 1000
            details = f"Connected. Clients: {connected_clients}, Memory: {used_memory}"

            return HealthCheck(
                name="Redis Cache",
                status="healthy",
                response_time_ms=response_time,
                error_count=0,
                details=details,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="Redis Cache",
                status="critical",
                response_time_ms=response_time,
                error_count=1,
                details=f"Redis connection failed: {str(e)}",
                last_check=datetime.now(),
            )

    def check_container_health(self) -> List[HealthCheck]:
        """Check Docker container status."""
        checks = []

        # Expected containers
        expected_containers = [
            "horse_racing_postgres",
            "horse_racing_redis",
            "horse_racing_react_app",
            "horse_racing_pgadmin",
            "horse_racing_ntfy",
            "horserace-auto-downloader",
        ]

        try:
            # Get container status via docker ps
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--format",
                    "table {{.Names}}\t{{.Status}}\t{{.Ports}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                running_containers = {}
                for line in result.stdout.split("\n")[1:]:  # Skip header
                    if line.strip():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            name = parts[0]
                            status = parts[1]
                            running_containers[name] = status

                for container in expected_containers:
                    if container in running_containers:
                        status_text = running_containers[container]
                        is_healthy = "Up" in status_text and "(healthy)" in status_text

                        checks.append(
                            HealthCheck(
                                name=f"Container: {container}",
                                status="healthy" if is_healthy else "warning",
                                response_time_ms=0,
                                error_count=0 if is_healthy else 1,
                                details=status_text,
                                last_check=datetime.now(),
                            )
                        )
                    else:
                        checks.append(
                            HealthCheck(
                                name=f"Container: {container}",
                                status="critical",
                                response_time_ms=0,
                                error_count=1,
                                details="Container not running",
                                last_check=datetime.now(),
                            )
                        )
            else:
                checks.append(
                    HealthCheck(
                        name="Docker System",
                        status="critical",
                        response_time_ms=0,
                        error_count=1,
                        details="Docker command failed",
                        last_check=datetime.now(),
                    )
                )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name="Docker System",
                    status="critical",
                    response_time_ms=0,
                    error_count=1,
                    details=f"Container check failed: {str(e)}",
                    last_check=datetime.now(),
                )
            )

        return checks

    def check_web_service_health(self) -> HealthCheck:
        """Check web application health."""
        start_time = time.time()

        try:
            response = requests.get(
                "http://localhost:8000/api/system_status", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return HealthCheck(
                    name="Web Application",
                    status="healthy",
                    response_time_ms=response_time,
                    error_count=0,
                    details=f"HTTP {response.status_code} - Service responding",
                    last_check=datetime.now(),
                )
            else:
                return HealthCheck(
                    name="Web Application",
                    status="warning",
                    response_time_ms=response_time,
                    error_count=1,
                    details=f"HTTP {response.status_code} - Unexpected response",
                    last_check=datetime.now(),
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="Web Application",
                status="critical",
                response_time_ms=response_time,
                error_count=1,
                details=f"Web service failed: {str(e)}",
                last_check=datetime.now(),
            )

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Network connections
            connections = len(psutil.net_connections())

            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_percent,
                network_connections=connections,
                uptime_hours=uptime_hours,
            )
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(0, 0, 0, 0, 0)

    def analyze_logs(self) -> Dict:
        """Analyze recent log files for errors and warnings."""
        log_analysis = {
            "log_files_checked": 0,
            "error_count": 0,
            "warning_count": 0,
            "recent_errors": [],
        }

        try:
            # Check main log files
            log_files = []
            if self.logs_dir.exists():
                log_files = list(self.logs_dir.glob("*.log"))

            # Also check application logs
            for pattern in [
                "racing_analyzer.log",
                "upload_integration.log",
                "ml_preprocessing.log",
            ]:
                log_file = self.project_root / pattern
                if log_file.exists():
                    log_files.append(log_file)

            log_analysis["log_files_checked"] = len(log_files)

            # Analyze each log file (last 1000 lines)
            cutoff_time = datetime.now() - timedelta(hours=24)

            for log_file in log_files:
                try:
                    with open(log_file, "r") as f:
                        lines = f.readlines()[-1000:]  # Last 1000 lines

                    for line in lines:
                        line = line.strip()
                        if "ERROR" in line:
                            log_analysis["error_count"] += 1
                            if len(log_analysis["recent_errors"]) < 20:
                                log_analysis["recent_errors"].append(line)
                        elif "WARNING" in line:
                            log_analysis["warning_count"] += 1

                except Exception as e:
                    logger.warning(f"Failed to analyze log file {log_file}: {e}")

        except Exception as e:
            logger.error(f"Log analysis failed: {e}")

        return log_analysis

    def send_alert(self, check: HealthCheck, priority: str = "default"):
        """Send alert notification via NTFY."""
        try:
            # Simple text message without emojis to avoid encoding issues
            message = f"ALERT: {check.name} is {check.status.upper()}"
            if check.details:
                message += f" - {check.details}"

            # Send notification
            response = requests.post(
                f"{self.ntfy_url}/{self.ntfy_topic}",
                data=message,
                headers={
                    "Priority": priority,
                    "Title": "Horse Racing AI - System Alert",
                },
            )

            if response.status_code == 200:
                logger.info(f"Alert sent for {check.name}")
            else:
                logger.warning(f"Failed to send alert: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        logger.info("Starting system health check...")

        # Perform all health checks
        health_checks = []

        # Database checks
        health_checks.append(self.check_database_health())
        health_checks.append(self.check_redis_health())

        # Container checks
        health_checks.extend(self.check_container_health())

        # Web service check
        health_checks.append(self.check_web_service_health())

        # Get system metrics
        system_metrics = self.get_system_metrics()

        # Analyze logs
        log_analysis = self.analyze_logs()

        # Calculate overall status
        critical_count = sum(1 for check in health_checks if check.status == "critical")
        warning_count = sum(1 for check in health_checks if check.status == "warning")

        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "total_components": len(health_checks),
                "healthy_components": sum(
                    1 for check in health_checks if check.status == "healthy"
                ),
                "warning_components": warning_count,
                "critical_components": critical_count,
            },
            "components": [
                {
                    "name": check.name,
                    "status": check.status,
                    "response_time_ms": check.response_time_ms,
                    "error_count": check.error_count,
                    "details": check.details,
                    "last_check": check.last_check.isoformat(),
                }
                for check in health_checks
            ],
            "system_metrics": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "network_connections": system_metrics.network_connections,
                "uptime_hours": system_metrics.uptime_hours,
            },
            "log_analysis": log_analysis,
        }

        # Send alerts for critical issues
        for check in health_checks:
            if check.status == "critical":
                self.send_alert(check, "high")
            elif check.status == "warning":
                self.send_alert(check, "default")

        # Save report
        report_file = (
            self.reports_dir
            / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Health report saved: {report_file}")
        logger.info(f"Overall status: {overall_status.upper()}")

        return report

    def generate_html_dashboard(self, report: Dict) -> Path:
        """Generate HTML dashboard from health report."""
        # Build component list HTML
        component_html = ""
        for component in report["components"]:
            status_class = f"badge-{component['status']}"
            component_html += f"""
            <div class="component">
                <div>
                    <strong>{component['name']}</strong>
                    <div class="response-time">Response: {component['response_time_ms']:.1f}ms</div>
                </div>
                <span class="status-badge {status_class}">{component['status'].upper()}</span>
            </div>
            """

        # Build recent errors HTML
        errors_html = ""
        if report["log_analysis"]["recent_errors"]:
            errors_html = "<h4>Recent Errors:</h4>"
            for error in report["log_analysis"]["recent_errors"][:10]:  # Show last 10
                # Escape HTML and remove emojis to prevent encoding issues
                safe_error = (
                    error.replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .encode("ascii", "ignore")
                    .decode("ascii")
                )
                errors_html += f'<div class="error-item">{safe_error}</div>'
        else:
            errors_html = "<p>No recent errors detected.</p>"

        # Determine status color
        status_colors = {
            "healthy": "#27ae60",
            "warning": "#f39c12",
            "critical": "#e74c3c",
        }
        status_color = status_colors.get(report["overall_status"], "#7f8c8d")

        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Health Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .status-card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .metric {{ background: white; padding: 15px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .component-list {{ background: white; padding: 20px; border-radius: 8px; }}
        .component {{ padding: 10px; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center; }}
        .component:last-child {{ border-bottom: none; }}
        .status-badge {{ padding: 4px 12px; border-radius: 20px; color: white; font-size: 0.8em; font-weight: bold; }}
        .badge-healthy {{ background: #27ae60; }}
        .badge-warning {{ background: #f39c12; }}
        .badge-critical {{ background: #e74c3c; }}
        .response-time {{ color: #7f8c8d; font-size: 0.9em; }}
        .log-section {{ background: white; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .error-item {{ background: #fdf2f2; border: 1px solid #f5c6cb; padding: 10px; margin: 5px 0; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>System Health Dashboard</h1>
            <p class="timestamp">Generated: {report["timestamp"]}</p>
            <h2>Overall Status: <span style="color: {status_color};">{report["overall_status"].upper()}</span></h2>
        </div>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-value">{report["summary"]["total_components"]}</div>
                <div class="metric-label">Total Components</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #27ae60;">{report["summary"]["healthy_components"]}</div>
                <div class="metric-label">Healthy</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #f39c12;">{report["summary"]["warning_components"]}</div>
                <div class="metric-label">Warnings</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #e74c3c;">{report["summary"]["critical_components"]}</div>
                <div class="metric-label">Critical</div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>System Metrics</h3>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{report["system_metrics"]["cpu_percent"]:.1f}%</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{report["system_metrics"]["memory_percent"]:.1f}%</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{report["system_metrics"]["disk_usage_percent"]:.1f}%</div>
                    <div class="metric-label">Disk Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{report["system_metrics"]["uptime_hours"]:.1f}h</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
        </div>
        
        <div class="component-list">
            <h3>Component Status</h3>
            {component_html}
        </div>
        
        <div class="log-section">
            <h3>Log Analysis</h3>
            <p><strong>Files Checked:</strong> {report["log_analysis"]["log_files_checked"]}</p>
            <p><strong>Errors:</strong> {report["log_analysis"]["error_count"]} | <strong>Warnings:</strong> {report["log_analysis"]["warning_count"]}</p>
            {errors_html}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>"""

        # Save HTML dashboard
        dashboard_file = (
            self.reports_dir
            / f"health_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Also save as latest
        latest_file = self.reports_dir / "latest_health_dashboard.html"
        with open(latest_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML dashboard saved: {dashboard_file}")
        return dashboard_file

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """Run continuous monitoring with specified interval."""
        logger.info(
            f"Starting continuous monitoring (interval: {interval_minutes} minutes)"
        )

        while True:
            try:
                report = self.generate_health_report()
                self.generate_html_dashboard(report)

                logger.info(f"Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Monitoring interval in minutes"
    )
    parser.add_argument(
        "--dashboard-only", action="store_true", help="Generate dashboard only"
    )

    args = parser.parse_args()

    monitor = SystemHealthMonitor()

    if args.continuous:
        monitor.run_continuous_monitoring(args.interval)
    else:
        # Single health check
        report = monitor.generate_health_report()
        dashboard_file = monitor.generate_html_dashboard(report)

        print(f"Health check complete!")
        print(f"Overall status: {report['overall_status'].upper()}")
        print(f"Dashboard: {dashboard_file}")
        print(f"Report: {monitor.reports_dir}")


if __name__ == "__main__":
    main()
