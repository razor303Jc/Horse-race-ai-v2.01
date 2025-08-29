#!/usr/bin/env python3
"""
System Health Monitoring and Alerting System for Horse Racing AI V2.03
Provides comprehensive monitoring, alerting, and health tracking
"""

import os
import sys
import json
import asyncio
import logging
import psutil
import sqlite3
import aiohttp
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import docker
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """System health metrics"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in: float
    network_out: float
    active_connections: int
    response_time: Optional[float]
    error_rate: float
    queue_size: int


@dataclass
class Alert:
    """Alert configuration and state"""

    alert_id: str
    name: str
    metric: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '=='
    severity: str  # 'critical', 'warning', 'info'
    enabled: bool
    cooldown_minutes: int
    last_triggered: Optional[datetime]
    notification_channels: List[str]


@dataclass
class HealthCheck:
    """Health check configuration"""

    check_id: str
    name: str
    check_type: str  # 'http', 'database', 'service', 'file'
    target: str
    interval_seconds: int
    timeout_seconds: int
    expected_response: Optional[str]
    enabled: bool
    last_check: Optional[datetime]
    last_status: Optional[bool]


class SystemHealthMonitor:
    """
    System Health Monitoring and Alerting System
    Monitors system resources, services, and application health
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the System Health Monitor"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.monitoring_enabled = True

        # Health checks and alerts
        self.health_checks = self._initialize_health_checks()
        self.alerts = self._initialize_alerts()

        # Monitoring state
        self.current_metrics = None
        self.metric_history = []

        # Docker client for container monitoring
        self.docker_client = None

        # Statistics
        self.stats = {
            "checks_performed": 0,
            "alerts_triggered": 0,
            "uptime_start": datetime.now(),
            "last_check_cycle": None,
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "monitoring_interval": 60,  # 1 minute
            "metric_retention_days": 30,
            "alert_cooldown_minutes": 15,
            "notification": {
                "email_enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "from_email": "monitoring@horse-racing-ai.com",
                "admin_emails": [],
                "webhook_url": None,
            },
            "thresholds": {
                "cpu_warning": 80.0,
                "cpu_critical": 95.0,
                "memory_warning": 85.0,
                "memory_critical": 95.0,
                "disk_warning": 85.0,
                "disk_critical": 95.0,
                "response_time_warning": 5000.0,  # milliseconds
                "response_time_critical": 10000.0,
                "error_rate_warning": 5.0,  # percentage
                "error_rate_critical": 10.0,
            },
        }

    def _initialize_health_checks(self) -> List[HealthCheck]:
        """Initialize health check configurations"""
        checks = []

        # Database health check
        checks.append(
            HealthCheck(
                check_id="database_check",
                name="Database Connection",
                check_type="database",
                target=self.db_path,
                interval_seconds=60,
                timeout_seconds=10,
                expected_response=None,
                enabled=True,
                last_check=None,
                last_status=None,
            )
        )

        # API health check
        checks.append(
            HealthCheck(
                check_id="api_health_check",
                name="API Health Endpoint",
                check_type="http",
                target="http://localhost:8000/health",
                interval_seconds=30,
                timeout_seconds=5,
                expected_response='{"status": "healthy"}',
                enabled=True,
                last_check=None,
                last_status=None,
            )
        )

        # Model files check
        checks.append(
            HealthCheck(
                check_id="models_check",
                name="Model Files Availability",
                check_type="file",
                target="models/",
                interval_seconds=300,  # 5 minutes
                timeout_seconds=5,
                expected_response=None,
                enabled=True,
                last_check=None,
                last_status=None,
            )
        )

        # Docker containers check
        checks.append(
            HealthCheck(
                check_id="containers_check",
                name="Docker Containers Status",
                check_type="service",
                target="docker",
                interval_seconds=120,  # 2 minutes
                timeout_seconds=10,
                expected_response=None,
                enabled=True,
                last_check=None,
                last_status=None,
            )
        )

        return checks

    def _initialize_alerts(self) -> List[Alert]:
        """Initialize alert configurations"""
        alerts = []
        thresholds = self.config.get("thresholds", {})

        # CPU alerts
        alerts.append(
            Alert(
                alert_id="cpu_warning",
                name="High CPU Usage Warning",
                metric="cpu_usage",
                threshold=thresholds.get("cpu_warning", 80.0),
                operator=">=",
                severity="warning",
                enabled=True,
                cooldown_minutes=self.config.get("alert_cooldown_minutes", 15),
                last_triggered=None,
                notification_channels=["email", "log"],
            )
        )

        alerts.append(
            Alert(
                alert_id="cpu_critical",
                name="Critical CPU Usage",
                metric="cpu_usage",
                threshold=thresholds.get("cpu_critical", 95.0),
                operator=">=",
                severity="critical",
                enabled=True,
                cooldown_minutes=5,
                last_triggered=None,
                notification_channels=["email", "webhook", "log"],
            )
        )

        # Memory alerts
        alerts.append(
            Alert(
                alert_id="memory_warning",
                name="High Memory Usage Warning",
                metric="memory_usage",
                threshold=thresholds.get("memory_warning", 85.0),
                operator=">=",
                severity="warning",
                enabled=True,
                cooldown_minutes=self.config.get("alert_cooldown_minutes", 15),
                last_triggered=None,
                notification_channels=["email", "log"],
            )
        )

        alerts.append(
            Alert(
                alert_id="memory_critical",
                name="Critical Memory Usage",
                metric="memory_usage",
                threshold=thresholds.get("memory_critical", 95.0),
                operator=">=",
                severity="critical",
                enabled=True,
                cooldown_minutes=5,
                last_triggered=None,
                notification_channels=["email", "webhook", "log"],
            )
        )

        # Disk alerts
        alerts.append(
            Alert(
                alert_id="disk_warning",
                name="High Disk Usage Warning",
                metric="disk_usage",
                threshold=thresholds.get("disk_warning", 85.0),
                operator=">=",
                severity="warning",
                enabled=True,
                cooldown_minutes=self.config.get("alert_cooldown_minutes", 15),
                last_triggered=None,
                notification_channels=["email", "log"],
            )
        )

        # Response time alerts
        alerts.append(
            Alert(
                alert_id="response_time_warning",
                name="Slow Response Time Warning",
                metric="response_time",
                threshold=thresholds.get("response_time_warning", 5000.0),
                operator=">=",
                severity="warning",
                enabled=True,
                cooldown_minutes=10,
                last_triggered=None,
                notification_channels=["email", "log"],
            )
        )

        # Error rate alerts
        alerts.append(
            Alert(
                alert_id="error_rate_critical",
                name="High Error Rate",
                metric="error_rate",
                threshold=thresholds.get("error_rate_critical", 10.0),
                operator=">=",
                severity="critical",
                enabled=True,
                cooldown_minutes=5,
                last_triggered=None,
                notification_channels=["email", "webhook", "log"],
            )
        )

        return alerts

    async def initialize_database(self):
        """Initialize database tables for health monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Health metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    disk_usage REAL NOT NULL,
                    network_in REAL NOT NULL,
                    network_out REAL NOT NULL,
                    active_connections INTEGER NOT NULL,
                    response_time REAL,
                    error_rate REAL NOT NULL,
                    queue_size INTEGER NOT NULL
                )
            """
            )

            # Health checks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS health_check_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_id TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    check_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    status BOOLEAN NOT NULL,
                    response_time REAL,
                    error_message TEXT,
                    details_json TEXT
                )
            """
            )

            # Alerts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT NOT NULL,
                    alert_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    triggered_at TIMESTAMP NOT NULL,
                    resolved_at TIMESTAMP,
                    notification_sent BOOLEAN DEFAULT FALSE,
                    message TEXT
                )
            """
            )

            # System events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    severity TEXT NOT NULL,
                    details_json TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_metrics_timestamp ON health_metrics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_check_results(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alert_history(triggered_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp)"
            )

            conn.commit()
            conn.close()

            logger.info("Health monitoring database tables initialized")

        except Exception as e:
            logger.error(f"Error initializing monitoring database: {e}")
            raise

    async def initialize_docker_client(self):
        """Initialize Docker client for container monitoring"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            logger.info("Docker client initialized for monitoring")
        except Exception as e:
            logger.warning(f"Docker client not available for monitoring: {e}")
            self.docker_client = None

    async def collect_system_metrics(self) -> HealthMetrics:
        """Collect current system health metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_usage = (disk.used / disk.total) * 100

            # Network statistics
            network = psutil.net_io_counters()
            network_in = network.bytes_recv / (1024 * 1024)  # MB
            network_out = network.bytes_sent / (1024 * 1024)  # MB

            # Active connections
            active_connections = len(psutil.net_connections())

            # Application-specific metrics
            response_time = await self._measure_response_time()
            error_rate = await self._calculate_error_rate()
            queue_size = await self._get_queue_size()

            metrics = HealthMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_in=network_in,
                network_out=network_out,
                active_connections=active_connections,
                response_time=response_time,
                error_rate=error_rate,
                queue_size=queue_size,
            )

            self.current_metrics = metrics
            self.metric_history.append(metrics)

            # Keep only recent history (last 1000 measurements)
            if len(self.metric_history) > 1000:
                self.metric_history = self.metric_history[-1000:]

            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise

    async def _measure_response_time(self) -> Optional[float]:
        """Measure API response time"""
        try:
            start_time = datetime.now()

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get("http://localhost:8000/health") as response:
                    await response.text()

            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            return response_time_ms

        except Exception as e:
            logger.debug(f"Error measuring response time: {e}")
            return None

    async def _calculate_error_rate(self) -> float:
        """Calculate recent error rate from logs"""
        try:
            # Check log files for recent errors
            log_files = ["logs/application.log", "logs/error.log"]
            error_count = 0
            total_requests = 0

            cutoff_time = datetime.now() - timedelta(minutes=5)

            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            lines = f.readlines()

                        for line in lines[-1000:]:  # Check last 1000 lines
                            if "ERROR" in line or "CRITICAL" in line:
                                error_count += 1
                            if "INFO" in line and (
                                "request" in line.lower()
                                or "prediction" in line.lower()
                            ):
                                total_requests += 1
                    except:
                        continue

            if total_requests > 0:
                return (error_count / total_requests) * 100
            else:
                return 0.0

        except Exception as e:
            logger.debug(f"Error calculating error rate: {e}")
            return 0.0

    async def _get_queue_size(self) -> int:
        """Get current processing queue size"""
        try:
            # Check database for pending jobs/tasks
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count pending retraining jobs
            cursor.execute(
                "SELECT COUNT(*) FROM retraining_jobs WHERE status = 'pending'"
            )
            retraining_pending = cursor.fetchone()[0] or 0

            # Count pending deployment jobs
            cursor.execute(
                "SELECT COUNT(*) FROM deployment_jobs WHERE status = 'pending'"
            )
            deployment_pending = cursor.fetchone()[0] or 0

            conn.close()

            return retraining_pending + deployment_pending

        except Exception as e:
            logger.debug(f"Error getting queue size: {e}")
            return 0

    async def perform_health_check(
        self, check: HealthCheck
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Perform a specific health check"""
        try:
            start_time = datetime.now()

            if check.check_type == "http":
                status, error, details = await self._check_http_endpoint(check)
            elif check.check_type == "database":
                status, error, details = await self._check_database_connection(check)
            elif check.check_type == "file":
                status, error, details = await self._check_file_availability(check)
            elif check.check_type == "service":
                status, error, details = await self._check_service_status(check)
            else:
                status, error, details = (
                    False,
                    f"Unknown check type: {check.check_type}",
                    {},
                )

            response_time = (datetime.now() - start_time).total_seconds() * 1000
            details["response_time_ms"] = response_time

            # Update check status
            check.last_check = datetime.now()
            check.last_status = status

            return status, error, details

        except Exception as e:
            logger.error(f"Error performing health check {check.check_id}: {e}")
            return False, str(e), {}

    async def _check_http_endpoint(
        self, check: HealthCheck
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check HTTP endpoint health"""
        try:
            timeout = aiohttp.ClientTimeout(total=check.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(check.target) as response:
                    response_text = await response.text()

                    details = {
                        "status_code": response.status,
                        "response_body": response_text[:500],  # Limit response size
                    }

                    if response.status == 200:
                        if check.expected_response:
                            if check.expected_response in response_text:
                                return True, None, details
                            else:
                                return False, f"Expected response not found", details
                        else:
                            return True, None, details
                    else:
                        return False, f"HTTP {response.status}", details

        except Exception as e:
            return False, str(e), {}

    async def _check_database_connection(
        self, check: HealthCheck
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check database connection health"""
        try:
            conn = sqlite3.connect(check.target, timeout=check.timeout_seconds)
            cursor = conn.cursor()

            # Simple query to test connection
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            # Get database info
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]

            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_mb = (page_count * page_size) / (1024 * 1024)

            conn.close()

            details = {
                "table_count": table_count,
                "database_size_mb": round(db_size_mb, 2),
            }

            return True, None, details

        except Exception as e:
            return False, str(e), {}

    async def _check_file_availability(
        self, check: HealthCheck
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check file/directory availability"""
        try:
            target_path = Path(check.target)

            if target_path.is_dir():
                # Count files in directory
                file_count = len(list(target_path.glob("*")))
                model_files = len(list(target_path.glob("*.joblib"))) + len(
                    list(target_path.glob("*.pkl"))
                )

                details = {
                    "type": "directory",
                    "file_count": file_count,
                    "model_files": model_files,
                    "exists": True,
                }

                return True, None, details

            elif target_path.is_file():
                file_size = target_path.stat().st_size
                modified_time = datetime.fromtimestamp(target_path.stat().st_mtime)

                details = {
                    "type": "file",
                    "size_bytes": file_size,
                    "modified_time": modified_time.isoformat(),
                    "exists": True,
                }

                return True, None, details
            else:
                return False, "File/directory not found", {"exists": False}

        except Exception as e:
            return False, str(e), {}

    async def _check_service_status(
        self, check: HealthCheck
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check service status (Docker containers, processes, etc.)"""
        try:
            if check.target == "docker" and self.docker_client:
                containers = self.docker_client.containers.list(all=True)

                running_containers = [c for c in containers if c.status == "running"]
                horse_racing_containers = [
                    c for c in containers if "horse_racing" in c.name.lower()
                ]

                details = {
                    "total_containers": len(containers),
                    "running_containers": len(running_containers),
                    "horse_racing_containers": len(horse_racing_containers),
                    "container_statuses": [
                        {
                            "name": c.name,
                            "status": c.status,
                            "image": c.image.tags[0] if c.image.tags else "unknown",
                        }
                        for c in horse_racing_containers
                    ],
                }

                # Check if any horse racing containers are not running
                unhealthy_containers = [
                    c for c in horse_racing_containers if c.status != "running"
                ]

                if unhealthy_containers:
                    return (
                        False,
                        f"{len(unhealthy_containers)} containers not running",
                        details,
                    )
                else:
                    return True, None, details
            else:
                return False, "Service check not supported", {}

        except Exception as e:
            return False, str(e), {}

    async def save_health_metrics(self, metrics: HealthMetrics):
        """Save health metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO health_metrics 
                (timestamp, cpu_usage, memory_usage, disk_usage, network_in, network_out,
                 active_connections, response_time, error_rate, queue_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.timestamp,
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.disk_usage,
                    metrics.network_in,
                    metrics.network_out,
                    metrics.active_connections,
                    metrics.response_time,
                    metrics.error_rate,
                    metrics.queue_size,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving health metrics: {e}")

    async def save_health_check_result(
        self,
        check: HealthCheck,
        status: bool,
        error_message: Optional[str],
        details: Dict[str, Any],
    ):
        """Save health check result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            response_time = details.get("response_time_ms")

            cursor.execute(
                """
                INSERT INTO health_check_results 
                (check_id, check_name, check_type, timestamp, status, response_time, error_message, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    check.check_id,
                    check.name,
                    check.check_type,
                    check.last_check,
                    status,
                    response_time,
                    error_message,
                    json.dumps(details, default=str),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving health check result: {e}")

    async def check_alerts(self, metrics: HealthMetrics) -> List[Alert]:
        """Check if any alerts should be triggered"""
        triggered_alerts = []

        for alert in self.alerts:
            if not alert.enabled:
                continue

            # Check cooldown period
            if alert.last_triggered:
                cooldown_delta = timedelta(minutes=alert.cooldown_minutes)
                if datetime.now() - alert.last_triggered < cooldown_delta:
                    continue

            # Get metric value
            metric_value = getattr(metrics, alert.metric, None)
            if metric_value is None:
                continue

            # Evaluate condition
            should_trigger = False
            if alert.operator == ">=":
                should_trigger = metric_value >= alert.threshold
            elif alert.operator == ">":
                should_trigger = metric_value > alert.threshold
            elif alert.operator == "<=":
                should_trigger = metric_value <= alert.threshold
            elif alert.operator == "<":
                should_trigger = metric_value < alert.threshold
            elif alert.operator == "==":
                should_trigger = metric_value == alert.threshold

            if should_trigger:
                alert.last_triggered = datetime.now()
                triggered_alerts.append(alert)

                # Save alert to database
                await self._save_alert(alert, metric_value, metrics.timestamp)

                logger.warning(
                    f"Alert triggered: {alert.name} - {alert.metric}={metric_value} {alert.operator} {alert.threshold}"
                )

        return triggered_alerts

    async def _save_alert(self, alert: Alert, metric_value: float, timestamp: datetime):
        """Save triggered alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            message = f"{alert.name}: {alert.metric} is {metric_value} (threshold: {alert.threshold})"

            cursor.execute(
                """
                INSERT INTO alert_history 
                (alert_id, alert_name, severity, metric, metric_value, threshold, triggered_at, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert.alert_id,
                    alert.name,
                    alert.severity,
                    alert.metric,
                    metric_value,
                    alert.threshold,
                    timestamp,
                    message,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving alert: {e}")

    async def send_notifications(self, alerts: List[Alert]):
        """Send notifications for triggered alerts"""
        for alert in alerts:
            for channel in alert.notification_channels:
                try:
                    if channel == "email":
                        await self._send_email_notification(alert)
                    elif channel == "webhook":
                        await self._send_webhook_notification(alert)
                    elif channel == "log":
                        await self._send_log_notification(alert)

                except Exception as e:
                    logger.error(
                        f"Error sending {channel} notification for alert {alert.alert_id}: {e}"
                    )

    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        if not self.config.get("notification", {}).get("email_enabled", False):
            return

        try:
            smtp_config = self.config.get("notification", {})

            msg = MimeMultipart()
            msg["From"] = smtp_config.get(
                "from_email", "monitoring@horse-racing-ai.com"
            )
            msg["To"] = ", ".join(smtp_config.get("admin_emails", []))
            msg["Subject"] = (
                f"[{alert.severity.upper()}] Horse Racing AI Alert: {alert.name}"
            )

            body = f"""
Alert: {alert.name}
Severity: {alert.severity}
Metric: {alert.metric}
Threshold: {alert.threshold}
Time: {alert.last_triggered}

This is an automated alert from the Horse Racing AI monitoring system.
            """

            msg.attach(MimeText(body, "plain"))

            server = smtplib.SMTP(
                smtp_config.get("smtp_server"), smtp_config.get("smtp_port", 587)
            )
            server.starttls()
            server.login(
                smtp_config.get("smtp_username"), smtp_config.get("smtp_password")
            )
            text = msg.as_string()
            server.sendmail(msg["From"], smtp_config.get("admin_emails", []), text)
            server.quit()

            logger.info(f"Email notification sent for alert: {alert.alert_id}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        webhook_url = self.config.get("notification", {}).get("webhook_url")
        if not webhook_url:
            return

        try:
            payload = {
                "alert_id": alert.alert_id,
                "alert_name": alert.name,
                "severity": alert.severity,
                "metric": alert.metric,
                "threshold": alert.threshold,
                "triggered_at": alert.last_triggered.isoformat(),
                "system": "horse_racing_ai_v2.03",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(
                            f"Webhook notification sent for alert: {alert.alert_id}"
                        )
                    else:
                        logger.warning(
                            f"Webhook notification failed: HTTP {response.status}"
                        )

        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")

    async def _send_log_notification(self, alert: Alert):
        """Send log notification"""
        message = f"ALERT [{alert.severity.upper()}] {alert.name}: {alert.metric} threshold exceeded"

        if alert.severity == "critical":
            logger.critical(message)
        elif alert.severity == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    async def perform_monitoring_cycle(self) -> Dict[str, Any]:
        """Perform one complete monitoring cycle"""
        cycle_start = datetime.now()
        results = {
            "metrics_collected": False,
            "health_checks_performed": 0,
            "health_checks_passed": 0,
            "alerts_triggered": 0,
            "cycle_duration": 0.0,
        }

        try:
            # Collect system metrics
            metrics = await self.collect_system_metrics()
            await self.save_health_metrics(metrics)
            results["metrics_collected"] = True

            # Perform health checks
            for check in self.health_checks:
                if not check.enabled:
                    continue

                # Check if it's time for this check
                if check.last_check:
                    next_check = check.last_check + timedelta(
                        seconds=check.interval_seconds
                    )
                    if datetime.now() < next_check:
                        continue

                status, error, details = await self.perform_health_check(check)
                await self.save_health_check_result(check, status, error, details)

                results["health_checks_performed"] += 1
                if status:
                    results["health_checks_passed"] += 1

                self.stats["checks_performed"] += 1

            # Check for alerts
            triggered_alerts = await self.check_alerts(metrics)
            if triggered_alerts:
                await self.send_notifications(triggered_alerts)
                results["alerts_triggered"] = len(triggered_alerts)
                self.stats["alerts_triggered"] += len(triggered_alerts)

            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            results["cycle_duration"] = cycle_duration

            self.stats["last_check_cycle"] = datetime.now()

            logger.debug(f"Monitoring cycle completed in {cycle_duration:.2f}s")

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            results["error"] = str(e)

        return results

    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Recent metrics summary
            cursor.execute(
                """
                SELECT 
                    AVG(cpu_usage) as avg_cpu,
                    AVG(memory_usage) as avg_memory,
                    AVG(disk_usage) as avg_disk,
                    AVG(response_time) as avg_response_time,
                    AVG(error_rate) as avg_error_rate
                FROM health_metrics 
                WHERE timestamp >= datetime('now', '-1 hour')
            """
            )
            metrics_summary = cursor.fetchone()

            # Health check success rates
            cursor.execute(
                """
                SELECT check_id, check_name,
                       COUNT(*) as total_checks,
                       SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as successful_checks
                FROM health_check_results 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY check_id, check_name
            """
            )
            health_check_stats = [
                {
                    "check_id": row[0],
                    "check_name": row[1],
                    "total_checks": row[2],
                    "successful_checks": row[3],
                    "success_rate": (row[3] / row[2] * 100) if row[2] > 0 else 0,
                }
                for row in cursor.fetchall()
            ]

            # Recent alerts
            cursor.execute(
                """
                SELECT alert_id, alert_name, severity, COUNT(*) as count
                FROM alert_history 
                WHERE triggered_at >= datetime('now', '-24 hours')
                GROUP BY alert_id, alert_name, severity
                ORDER BY count DESC
            """
            )
            recent_alerts = [
                {
                    "alert_id": row[0],
                    "alert_name": row[1],
                    "severity": row[2],
                    "count": row[3],
                }
                for row in cursor.fetchall()
            ]

            conn.close()

            # System uptime
            uptime = datetime.now() - self.stats["uptime_start"]

            return {
                "system_stats": {
                    **self.stats,
                    "uptime_hours": uptime.total_seconds() / 3600,
                    "monitoring_enabled": self.monitoring_enabled,
                },
                "metrics_summary": (
                    {
                        "avg_cpu_usage": round(metrics_summary[0] or 0, 2),
                        "avg_memory_usage": round(metrics_summary[1] or 0, 2),
                        "avg_disk_usage": round(metrics_summary[2] or 0, 2),
                        "avg_response_time": round(metrics_summary[3] or 0, 2),
                        "avg_error_rate": round(metrics_summary[4] or 0, 2),
                    }
                    if metrics_summary[0] is not None
                    else {}
                ),
                "health_checks": health_check_stats,
                "recent_alerts": recent_alerts,
                "current_metrics": (
                    asdict(self.current_metrics) if self.current_metrics else None
                ),
                "configured_checks": len(self.health_checks),
                "configured_alerts": len(self.alerts),
            }

        except Exception as e:
            logger.error(f"Error getting monitoring statistics: {e}")
            return {"error": str(e)}

    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old monitoring data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Clean up old metrics
            cursor.execute(
                "DELETE FROM health_metrics WHERE timestamp < ?", (cutoff_date,)
            )
            metrics_deleted = cursor.rowcount

            # Clean up old health check results
            cursor.execute(
                "DELETE FROM health_check_results WHERE timestamp < ?", (cutoff_date,)
            )
            checks_deleted = cursor.rowcount

            # Clean up resolved alerts older than retention period
            cursor.execute(
                "DELETE FROM alert_history WHERE resolved_at < ?", (cutoff_date,)
            )
            alerts_deleted = cursor.rowcount

            conn.commit()
            conn.close()

            cleanup_results = {
                "metrics_deleted": metrics_deleted,
                "checks_deleted": checks_deleted,
                "alerts_deleted": alerts_deleted,
            }

            logger.info(f"Monitoring data cleanup completed: {cleanup_results}")
            return cleanup_results

        except Exception as e:
            logger.error(f"Error cleaning up monitoring data: {e}")
            return {"error": str(e)}


async def main():
    """Main function for testing the System Health Monitor"""

    print("🏥 System Health Monitoring and Alerting System V2.03")
    print("=" * 60)

    try:
        # Initialize monitor
        monitor = SystemHealthMonitor()

        # Initialize database
        print("📊 Initializing database...")
        await monitor.initialize_database()

        # Initialize Docker client
        print("🐳 Initializing Docker client...")
        await monitor.initialize_docker_client()

        # Perform monitoring cycle
        print("🔍 Performing monitoring cycle...")
        cycle_results = await monitor.perform_monitoring_cycle()

        print(f"✅ Monitoring cycle completed:")
        print(f"   - Metrics collected: {cycle_results['metrics_collected']}")
        print(
            f"   - Health checks performed: {cycle_results['health_checks_performed']}"
        )
        print(f"   - Health checks passed: {cycle_results['health_checks_passed']}")
        print(f"   - Alerts triggered: {cycle_results['alerts_triggered']}")
        print(f"   - Cycle duration: {cycle_results['cycle_duration']:.2f}s")

        # Get statistics
        print("\n📈 Monitoring Statistics:")
        stats = await monitor.get_monitoring_statistics()

        print(f"   - Configured checks: {stats['configured_checks']}")
        print(f"   - Configured alerts: {stats['configured_alerts']}")
        print(f"   - System uptime: {stats['system_stats']['uptime_hours']:.1f} hours")
        print(
            f"   - Total checks performed: {stats['system_stats']['checks_performed']}"
        )
        print(
            f"   - Total alerts triggered: {stats['system_stats']['alerts_triggered']}"
        )

        if stats["current_metrics"]:
            metrics = stats["current_metrics"]
            print(f"   - Current CPU usage: {metrics['cpu_usage']:.1f}%")
            print(f"   - Current memory usage: {metrics['memory_usage']:.1f}%")
            print(f"   - Current disk usage: {metrics['disk_usage']:.1f}%")

            if metrics["response_time"]:
                print(f"   - Current response time: {metrics['response_time']:.0f}ms")

        if stats["health_checks"]:
            print("   - Health check success rates:")
            for check in stats["health_checks"]:
                print(f"     • {check['check_name']}: {check['success_rate']:.1f}%")

        # Test cleanup
        print("\n🧹 Testing cleanup...")
        cleanup_results = await monitor.cleanup_old_data(days_to_keep=90)
        print(
            f"   - Cleaned up {cleanup_results.get('metrics_deleted', 0)} old metrics"
        )
        print(
            f"   - Cleaned up {cleanup_results.get('checks_deleted', 0)} old check results"
        )
        print(f"   - Cleaned up {cleanup_results.get('alerts_deleted', 0)} old alerts")

        print("\n✅ System Health Monitoring testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
