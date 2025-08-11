#!/usr/bin/env python3
"""
🔍 Horse Racing AI v2.0 - System Health Monitor
=============================================

Comprehensive system monitoring and health checking tool.
Provides real-time monitoring of all system components.

Features:
- Database connectivity monitoring
- Container health checks  
- Log analysis and error detection
- Performance metrics collection
- Automated alerting via NTFY
- HTML dashboard generation

Author: AI Assistant
Date: August 11, 2025
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    """Health status for a system component."""
    name: str
    status: str  # healthy, warning, critical, unknown
    last_check: datetime
    response_time_ms: float
    error_count: int
    details: Dict
    

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_connections: int
    uptime_hours: float
    

class SystemHealthMonitor:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "reports" / "monitoring"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # NTFY configuration
        self.ntfy_enabled = os.getenv("NTFY_ENABLED", "true").lower() == "true"
        self.ntfy_url = os.getenv("NTFY_URL", "http://localhost:8081")
        self.ntfy_topic = os.getenv("NTFY_TOPIC", "horse-racing-alerts")
        
        # Component definitions
        self.components = {
            "database": {
                "host": "localhost",
                "port": 5433,
                "database": "horse_racing_db",
                "user": "horse_racing",
                "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123")
            },
            "redis": {
                "host": "localhost", 
                "port": 6380,
                "password": os.getenv("REDIS_PASSWORD", "redis_password_123")
            },
            "web_app": {
                "url": "http://localhost:8000/api/system_status"
            },
            "ntfy": {
                "url": "http://localhost:8081"
            }
        }
        
        self.health_thresholds = {
            "response_time_warning": 5000,  # 5 seconds
            "response_time_critical": 15000,  # 15 seconds
            "error_rate_warning": 5,  # 5%
            "error_rate_critical": 10,  # 10%
            "cpu_warning": 80,  # 80%
            "cpu_critical": 95,  # 95%
            "memory_warning": 85,  # 85%
            "memory_critical": 95,  # 95%
            "disk_warning": 80,  # 80%
            "disk_critical": 90   # 90%
        }

    def check_database_health(self) -> ComponentHealth:
        """Check PostgreSQL database health."""
        start_time = time.time()
        
        try:
            import psycopg2
            
            config = self.components["database"]
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                database=config["database"],
                user=config["user"],
                password=config["password"],
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM races;")
            race_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM horses;")
            horse_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            status = "healthy"
            if response_time > self.health_thresholds["response_time_warning"]:
                status = "warning"
            if response_time > self.health_thresholds["response_time_critical"]:
                status = "critical"
                
            return ComponentHealth(
                name="database",
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_count=0,
                details={
                    "race_count": race_count,
                    "horse_count": horse_count,
                    "connection_time_ms": response_time
                }
            )
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ComponentHealth(
                name="database",
                status="critical",
                last_check=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_count=1,
                details={"error": str(e)}
            )

    def check_redis_health(self) -> ComponentHealth:
        """Check Redis cache health."""
        start_time = time.time()
        
        try:
            import redis
            
            config = self.components["redis"]
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"],
                socket_timeout=10
            )
            
            # Test basic operations
            r.ping()
            r.set("health_check", "ok", ex=60)
            test_value = r.get("health_check")
            
            response_time = (time.time() - start_time) * 1000
            
            status = "healthy"
            if response_time > self.health_thresholds["response_time_warning"]:
                status = "warning"
                
            return ComponentHealth(
                name="redis",
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_count=0,
                details={
                    "ping_successful": True,
                    "test_operation": "success",
                    "response_time_ms": response_time
                }
            )
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="redis", 
                status="critical",
                last_check=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_count=1,
                details={"error": str(e)}
            )

    def check_web_app_health(self) -> ComponentHealth:
        """Check web application health."""
        start_time = time.time()
        
        try:
            config = self.components["web_app"]
            response = requests.get(config["url"], timeout=10)
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = "healthy"
                if response_time > self.health_thresholds["response_time_warning"]:
                    status = "warning"
                    
                return ComponentHealth(
                    name="web_app",
                    status=status,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_count=0,
                    details={
                        "status_code": response.status_code,
                        "response_data": data,
                        "response_time_ms": response_time
                    }
                )
            else:
                return ComponentHealth(
                    name="web_app",
                    status="warning",
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_count=1,
                    details={
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}"
                    }
                )
                
        except Exception as e:
            logger.error(f"Web app health check failed: {e}")
            return ComponentHealth(
                name="web_app",
                status="critical",
                last_check=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_count=1,
                details={"error": str(e)}
            )

    def check_container_health(self) -> List[ComponentHealth]:
        """Check Docker container health."""
        containers = []
        
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        name = parts[0]
                        status = parts[1]
                        image = parts[2]
                        
                        health_status = "healthy" if "healthy" in status.lower() else "warning"
                        if "exited" in status.lower() or "dead" in status.lower():
                            health_status = "critical"
                            
                        containers.append(ComponentHealth(
                            name=f"container_{name}",
                            status=health_status,
                            last_check=datetime.now(),
                            response_time_ms=0,
                            error_count=0 if health_status == "healthy" else 1,
                            details={
                                "container_name": name,
                                "status": status,
                                "image": image
                            }
                        ))
                        
        except Exception as e:
            logger.error(f"Container health check failed: {e}")
            containers.append(ComponentHealth(
                name="docker_system",
                status="critical",
                last_check=datetime.now(),
                response_time_ms=0,
                error_count=1,
                details={"error": str(e)}
            ))
            
        return containers

    def get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_hours = (time.time() - boot_time) / 3600
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_percent,
                network_connections=connections,
                uptime_hours=uptime_hours
            )
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(0, 0, 0, 0, 0)

    def analyze_logs(self) -> Dict:
        """Analyze recent log files for errors and warnings."""
        log_analysis = {
            "error_count": 0,
            "warning_count": 0,
            "recent_errors": [],
            "log_files_checked": 0
        }
        
        try:
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                # Check recent log files (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for log_file in logs_dir.rglob("*.log"):
                    try:
                        if log_file.stat().st_mtime > cutoff_time.timestamp():
                            log_analysis["log_files_checked"] += 1
                            
                            with open(log_file, 'r') as f:
                                lines = f.readlines()
                                for line in lines[-100:]:  # Check last 100 lines
                                    if " ERROR " in line:
                                        log_analysis["error_count"] += 1
                                        if len(log_analysis["recent_errors"]) < 10:
                                            log_analysis["recent_errors"].append({
                                                "file": str(log_file),
                                                "line": line.strip()
                                            })
                                    elif " WARNING " in line:
                                        log_analysis["warning_count"] += 1
                                        
                    except Exception as e:
                        logger.warning(f"Failed to analyze log file {log_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Log analysis failed: {e}")
            
        return log_analysis

    def send_alert(self, component: ComponentHealth, severity: str = "default"):
        """Send NTFY alert for component issues."""
        if not self.ntfy_enabled:
            return
            
        try:
            title = f"🚨 {component.name.upper()} {component.status.upper()}"
            message = f"Component: {component.name}\nStatus: {component.status}\nResponse Time: {component.response_time_ms:.0f}ms"
            
            if component.details.get("error"):
                message += f"\nError: {component.details['error']}"
                
            headers = {
                "Title": title,
                "Priority": severity,
                "Tags": "monitoring,health,system"
            }
            
            url = f"{self.ntfy_url}/{self.ntfy_topic}"
            response = requests.post(url, data=message, headers=headers, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Alert sent for {component.name}")
            else:
                logger.warning(f"Failed to send alert: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        logger.info("🔍 Starting system health check...")
        
        # Check all components
        health_checks = []
        
        # Core services
        health_checks.append(self.check_database_health())
        health_checks.append(self.check_redis_health()) 
        health_checks.append(self.check_web_app_health())
        
        # Container health
        health_checks.extend(self.check_container_health())
        
        # System metrics
        system_metrics = self.get_system_metrics()
        
        # Log analysis
        log_analysis = self.analyze_logs()
        
        # Overall status determination
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
                "healthy_components": sum(1 for check in health_checks if check.status == "healthy"),
                "warning_components": warning_count,
                "critical_components": critical_count
            },
            "components": [
                {
                    "name": check.name,
                    "status": check.status,
                    "response_time_ms": check.response_time_ms,
                    "error_count": check.error_count,
                    "details": check.details,
                    "last_check": check.last_check.isoformat()
                }
                for check in health_checks
            ],
            "system_metrics": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "network_connections": system_metrics.network_connections,
                "uptime_hours": system_metrics.uptime_hours
            },
            "log_analysis": log_analysis
        }
        
        # Send alerts for critical issues
        for check in health_checks:
            if check.status == "critical":
                self.send_alert(check, "high")
            elif check.status == "warning":
                self.send_alert(check, "default")
        
        # Save report
        report_file = self.reports_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
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
            component_html += f'''
            <div class="component">
                <div>
                    <strong>{component['name']}</strong>
                    <div class="response-time">Response: {component['response_time_ms']:.1f}ms</div>
                </div>
                <span class="status-badge {status_class}">{component['status'].upper()}</span>
            </div>
            '''
        
        # Build recent errors HTML
        errors_html = ""
        if report["log_analysis"]["recent_errors"]:
            errors_html = "<h4>Recent Errors:</h4>"
            for error in report["log_analysis"]["recent_errors"][:10]:  # Show last 10
                errors_html += f'<div class="error-item">{error}</div>'
        else:
            errors_html = "<p>No recent errors detected.</p>"
        
        # Determine status color
        status_colors = {
            "healthy": "#27ae60",
            "warning": "#f39c12", 
            "critical": "#e74c3c"
        }
        status_color = status_colors.get(report["overall_status"], "#7f8c8d")
        
        # Create HTML content using simple concatenation to avoid format issues
        html_content = f'''<!DOCTYPE html>
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
            <h1>🔍 System Health Dashboard</h1>
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
            <h3>💻 System Metrics</h3>
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
            <h3>🔧 Component Status</h3>
            {component_html}
        </div>
        
        <div class="log-section">
            <h3>📋 Log Analysis</h3>
            <p><strong>Files Checked:</strong> {report["log_analysis"]["log_files_checked"]}</p>
            <p><strong>Errors:</strong> {report["log_analysis"]["error_count"]} | <strong>Warnings:</strong> {report["log_analysis"]["warning_count"]}</p>
            {errors_html}
        </div>
    </div>
</body>
</html>'''
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #27ae60;">{healthy_components}</div>
                <div class="metric-label">Healthy</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #f39c12;">{warning_components}</div>
                <div class="metric-label">Warnings</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #e74c3c;">{critical_components}</div>
                <div class="metric-label">Critical</div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>💻 System Metrics</h3>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{cpu_percent:.1f}%</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{memory_percent:.1f}%</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{disk_percent:.1f}%</div>
                    <div class="metric-label">Disk Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{uptime_hours:.1f}h</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
        </div>
        
        <div class="component-list">
            <h3>🔧 Component Status</h3>
            {component_list}
        </div>
        
        <div class="log-section">
            <h3>📋 Log Analysis</h3>
            <p><strong>Files Checked:</strong> {log_files_checked}</p>
            <p><strong>Errors:</strong> {error_count} | <strong>Warnings:</strong> {warning_count}</p>
            {recent_errors}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
        '''
        
        # Status color mapping
        status_colors = {
            "healthy": "#27ae60",
            "warning": "#f39c12", 
            "critical": "#e74c3c"
        }
        
        # Build component list HTML
        component_html = ""
        for component in report["components"]:
            badge_class = f"badge-{component['status']}"
            component_html += f'''
            <div class="component">
                <div>
                    <strong>{component['name']}</strong>
                    <div class="response-time">Response: {component['response_time_ms']:.0f}ms</div>
                </div>
                <span class="status-badge {badge_class}">{component['status'].upper()}</span>
            </div>
            '''
        
        # Build recent errors HTML
        errors_html = ""
        if report["log_analysis"]["recent_errors"]:
            errors_html = "<h4>Recent Errors:</h4>"
            for error in report["log_analysis"]["recent_errors"][:5]:  # Show top 5
                errors_html += f'''
                <div class="error-item">
                    <strong>File:</strong> {error['file']}<br>
                    <strong>Error:</strong> {error['line']}
                </div>
                '''
        else:
            errors_html = "<p>✅ No recent errors found</p>"
        
        # Fill template
        html_content = html_template.format(
            timestamp=report["timestamp"],
            overall_status=report["overall_status"].upper(),
            status_color=status_colors.get(report["overall_status"], "#7f8c8d"),
            total_components=report["summary"]["total_components"],
            healthy_components=report["summary"]["healthy_components"], 
            warning_components=report["summary"]["warning_components"],
            critical_components=report["summary"]["critical_components"],
            cpu_percent=report["system_metrics"]["cpu_percent"],
            memory_percent=report["system_metrics"]["memory_percent"],
            disk_percent=report["system_metrics"]["disk_usage_percent"],
            uptime_hours=report["system_metrics"]["uptime_hours"],
            component_list=component_html,
            log_files_checked=report["log_analysis"]["log_files_checked"],
            error_count=report["log_analysis"]["error_count"],
            warning_count=report["log_analysis"]["warning_count"],
            recent_errors=errors_html
        )
        
        # Save HTML dashboard
        dashboard_file = self.reports_dir / f"health_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(dashboard_file, 'w') as f:
            f.write(html_content)
            
        # Also save as latest
        latest_file = self.reports_dir / "latest_health_dashboard.html"
        with open(latest_file, 'w') as f:
            f.write(html_content)
            
        logger.info(f"HTML dashboard saved: {dashboard_file}")
        return dashboard_file

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """Run continuous monitoring with specified interval."""
        logger.info(f"🔄 Starting continuous monitoring (interval: {interval_minutes} minutes)")
        
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
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in minutes")
    parser.add_argument("--dashboard", action="store_true", help="Generate HTML dashboard only")
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor()
    
    if args.continuous:
        monitor.run_continuous_monitoring(args.interval)
    else:
        report = monitor.generate_health_report()
        dashboard_file = monitor.generate_html_dashboard(report)
        
        if args.dashboard:
            print(f"📊 Dashboard generated: {dashboard_file}")
            print(f"🌐 View at: file://{dashboard_file.absolute()}")


if __name__ == "__main__":
    main()
