#!/usr/bin/env python3
"""
🚀 Advanced Performance Monitor for Horse Racing Pipeline
========================================================

Enhanced monitoring system with:
- Real-time performance metrics collection
- Resource usage tracking (CPU, Memory, Disk)
- Performance degradation detection
- Intelligent alerting system
- Historical trend analysis
"""

import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""

    timestamp: datetime
    stage: str
    cpu_percent: float
    memory_percent: float
    processing_time: float
    throughput: float
    error_count: int


@dataclass
class ResourceSnapshot:
    """System resource snapshot."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_free_gb: float
    process_count: int


@dataclass
class PerformanceAlert:
    """Performance alert structure."""

    timestamp: datetime
    alert_type: str
    severity: str
    message: str
    metrics: Dict[str, Any]
    recommended_action: str


class AlertManager:
    """Intelligent alerting system."""

    def __init__(self, thresholds: Optional[Dict] = None):
        """Initialize alert manager."""
        self.thresholds = thresholds or {
            "cpu_critical": 90.0,
            "memory_critical": 95.0,
            "performance_degradation": 0.20,
        }
        self.alert_history: deque = deque(maxlen=100)
        self.alert_cooldown: Dict[str, datetime] = {}
        self.cooldown_minutes = 5

    def should_alert(self, alert_type: str) -> bool:
        """Check if enough time passed since last alert."""
        if alert_type not in self.alert_cooldown:
            return True
        time_since = datetime.now() - self.alert_cooldown[alert_type]
        return time_since.total_seconds() > (self.cooldown_minutes * 60)

    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metrics: Dict[str, Any],
        action: str,
    ) -> PerformanceAlert:
        """Create and log performance alert."""
        alert = PerformanceAlert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            metrics=metrics,
            recommended_action=action,
        )
        self.alert_history.append(alert)
        self.alert_cooldown[alert_type] = alert.timestamp
        logging.warning(f"ALERT [{severity}] {alert_type}: {message}")
        return alert

    def check_resource_alerts(
        self, snapshot: ResourceSnapshot
    ) -> List[PerformanceAlert]:
        """Check resource usage and generate alerts."""
        alerts = []

        # CPU alerts
        if snapshot.cpu_percent >= self.thresholds["cpu_critical"]:
            if self.should_alert("cpu_critical"):
                alerts.append(
                    self.create_alert(
                        "cpu_critical",
                        "CRITICAL",
                        f"CPU usage critically high: {snapshot.cpu_percent:.1f}%",
                        {"cpu_percent": snapshot.cpu_percent},
                        "Scale pipeline or reduce concurrent operations",
                    )
                )

        # Memory alerts
        if snapshot.memory_percent >= self.thresholds["memory_critical"]:
            if self.should_alert("memory_critical"):
                alerts.append(
                    self.create_alert(
                        "memory_critical",
                        "CRITICAL",
                        f"Memory usage high: {snapshot.memory_percent:.1f}%",
                        {"memory_percent": snapshot.memory_percent},
                        "Restart services or increase memory",
                    )
                )

        return alerts


class AdvancedPerformanceMonitor:
    """Advanced performance monitoring system."""

    def __init__(self, monitoring_interval: int = 30):
        """Initialize the performance monitor."""
        self.monitoring_interval = monitoring_interval
        self.project_root = Path(__file__).parent.parent.parent
        self.metrics_history: deque = deque(maxlen=1000)
        self.resource_history: deque = deque(maxlen=500)
        self.stage_baselines: Dict[str, PerformanceMetric] = {}
        self.stage_timings: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.alert_manager = AlertManager()
        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup performance monitoring logging."""
        log_dir = self.project_root / "logs" / "monitoring"
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "performance_monitor.log"),
                logging.StreamHandler(),
            ],
        )

    def collect_system_metrics(self) -> ResourceSnapshot:
        """Collect system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            process_count = len(psutil.pids())

            return ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_mb=memory.used / (1024 * 1024),
                disk_free_gb=disk.free / (1024**3),
                process_count=process_count,
            )
        except Exception as e:
            logging.error(f"Failed to collect system metrics: {e}")
            return ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=0,
                memory_percent=0,
                memory_mb=0,
                disk_free_gb=0,
                process_count=0,
            )

    def collect_pipeline_metrics(
        self,
        stage: str,
        processing_time: float,
        records_processed: int,
        errors: int = 0,
    ) -> PerformanceMetric:
        """Collect performance metrics for pipeline stage."""
        resource_snapshot = self.collect_system_metrics()
        throughput = records_processed / processing_time if processing_time > 0 else 0

        metric = PerformanceMetric(
            timestamp=datetime.now(),
            stage=stage,
            cpu_percent=resource_snapshot.cpu_percent,
            memory_percent=resource_snapshot.memory_percent,
            processing_time=processing_time,
            throughput=throughput,
            error_count=errors,
        )

        # Store metrics
        self.metrics_history.append(metric)
        self.stage_timings[stage].append(processing_time)

        # Check for performance alerts
        baseline = self.stage_baselines.get(stage)
        if baseline:
            time_increase = (
                metric.processing_time - baseline.processing_time
            ) / baseline.processing_time
            if time_increase >= 0.20:  # 20% degradation
                self.alert_manager.create_alert(
                    f"performance_{stage}",
                    "WARNING",
                    f"Stage {stage} degraded by {time_increase*100:.1f}%",
                    {
                        "current": metric.processing_time,
                        "baseline": baseline.processing_time,
                    },
                    "Investigate stage bottlenecks",
                )

        # Update baseline if better performance
        if not baseline or (
            processing_time < baseline.processing_time * 0.9
            and throughput > baseline.throughput * 1.1
        ):
            self.stage_baselines[stage] = metric

        return metric

    def analyze_performance_trends(
        self, stage: str, lookback_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze performance trends for specific stage."""
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

        stage_metrics = [
            m
            for m in self.metrics_history
            if m.stage == stage and m.timestamp >= cutoff_time
        ]

        if not stage_metrics:
            return {"error": f"No metrics for stage {stage}"}

        processing_times = [m.processing_time for m in stage_metrics]
        throughputs = [m.throughput for m in stage_metrics if m.throughput > 0]

        return {
            "stage": stage,
            "period_hours": lookback_hours,
            "metric_count": len(stage_metrics),
            "processing_time": {
                "mean": statistics.mean(processing_times),
                "median": statistics.median(processing_times),
                "min": min(processing_times),
                "max": max(processing_times),
            },
            "throughput": {
                "mean": statistics.mean(throughputs) if throughputs else 0,
                "median": statistics.median(throughputs) if throughputs else 0,
                "min": min(throughputs) if throughputs else 0,
                "max": max(throughputs) if throughputs else 0,
            },
        }

    def generate_performance_report(self) -> str:
        """Generate performance summary report."""
        report_lines = [
            "🚀 Pipeline Performance Report",
            "=" * 40,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Monitoring Period: {self.monitoring_interval}s intervals",
            "",
            "📊 Overall Statistics:",
            f"  • Total Metrics Collected: {len(self.metrics_history)}",
            f"  • Resource Snapshots: {len(self.resource_history)}",
            f"  • Stages Monitored: {len(self.stage_timings)}",
            f"  • Active Alerts: {len(self.alert_manager.alert_history)}",
            "",
        ]

        # Stage performance summary
        if self.stage_timings:
            report_lines.extend(["⏱️ Stage Performance Summary:", "-" * 30])

            for stage, timings in self.stage_timings.items():
                if timings:
                    avg_time = statistics.mean(timings)
                    min_time = min(timings)
                    max_time = max(timings)

                    report_lines.append(
                        f"  {stage:20} | Avg: {avg_time:6.2f}s | "
                        f"Min: {min_time:6.2f}s | Max: {max_time:6.2f}s"
                    )
            report_lines.append("")

        # Recent alerts summary
        if self.alert_manager.alert_history:
            report_lines.extend(["🚨 Recent Alerts:", "-" * 20])

            for alert in list(self.alert_manager.alert_history)[-10:]:
                report_lines.append(
                    f"  [{alert.timestamp.strftime('%H:%M:%S')}] "
                    f"{alert.severity}: {alert.message}"
                )
        else:
            report_lines.append("✅ No recent alerts")

        return "\n".join(report_lines)

    def create_monitoring_display(self) -> Layout:
        """Create enhanced monitoring display."""
        layout = Layout()

        # Get latest data
        latest_snapshot = self.resource_history[-1] if self.resource_history else None
        recent_alerts = list(self.alert_manager.alert_history)[-5:]

        # System metrics panel
        if latest_snapshot:
            system_table = Table(title="🖥️ System Performance")
            system_table.add_column("Metric", style="cyan")
            system_table.add_column("Value", style="green")
            system_table.add_column("Status", style="yellow")

            cpu_status = (
                "🟢 Normal"
                if latest_snapshot.cpu_percent < 70
                else "🟡 High" if latest_snapshot.cpu_percent < 90 else "🔴 Critical"
            )
            system_table.add_row(
                "CPU Usage", f"{latest_snapshot.cpu_percent:.1f}%", cpu_status
            )

            mem_status = (
                "🟢 Normal"
                if latest_snapshot.memory_percent < 70
                else "🟡 High" if latest_snapshot.memory_percent < 85 else "🔴 Critical"
            )
            system_table.add_row(
                "Memory",
                f"{latest_snapshot.memory_percent:.1f}% "
                f"({latest_snapshot.memory_mb:.0f} MB)",
                mem_status,
            )

            system_table.add_row(
                "Disk Free", f"{latest_snapshot.disk_free_gb:.1f} GB", "🟢 Normal"
            )
            system_table.add_row(
                "Processes", str(latest_snapshot.process_count), "🟢 Normal"
            )
        else:
            system_table = Table(title="🖥️ System Performance")
            system_table.add_column("Status", style="red")
            system_table.add_row("No system metrics available")

        # Performance trends panel
        perf_table = Table(title="📊 Performance Trends")
        perf_table.add_column("Stage", style="cyan")
        perf_table.add_column("Avg Time", style="green")
        perf_table.add_column("Samples", style="yellow")
        perf_table.add_column("Trend", style="magenta")

        for stage, timings in list(self.stage_timings.items())[-5:]:
            if timings:
                avg_time = statistics.mean(timings)
                sample_count = len(timings)

                # Simple trend calculation
                if len(timings) >= 5:
                    recent_avg = statistics.mean(list(timings)[-3:])
                    older_avg = (
                        statistics.mean(list(timings)[-6:-3])
                        if len(timings) >= 6
                        else avg_time
                    )
                    trend = (
                        "📈 Slower"
                        if recent_avg > older_avg * 1.1
                        else "📉 Faster" if recent_avg < older_avg * 0.9 else "➡️ Stable"
                    )
                else:
                    trend = "📊 Tracking"

                perf_table.add_row(stage, f"{avg_time:.2f}s", str(sample_count), trend)

        # Recent alerts panel
        alerts_text = Text()
        if recent_alerts:
            for alert in recent_alerts:
                severity_color = "red" if alert.severity == "CRITICAL" else "yellow"
                alerts_text.append(
                    f"[{alert.timestamp.strftime('%H:%M')}] ", style="dim"
                )
                alerts_text.append(f"{alert.alert_type}: ", style=severity_color)
                alerts_text.append(f"{alert.message}\n", style="white")
        else:
            alerts_text.append("No recent alerts", style="green")

        alerts_panel = Panel(
            alerts_text,
            title="🚨 Recent Alerts",
            border_style="red" if recent_alerts else "green",
        )

        # Monitor status panel
        monitoring_info = f"""
Running: {datetime.now().strftime('%H:%M:%S')}
Metrics: {len(self.metrics_history)}
Snapshots: {len(self.resource_history)}
Stages: {len(self.stage_timings)}
Alerts: {len(recent_alerts)}
"""
        monitoring_panel = Panel(
            monitoring_info, title="📈 Monitor Status", border_style="blue"
        )

        # Create layout
        layout.split_column(
            Layout(system_table, name="system"),
            Layout(name="main", ratio=2),
            Layout(alerts_panel, name="alerts", size=8),
        )

        layout["main"].split_row(
            Layout(perf_table, name="performance"),
            Layout(monitoring_panel, name="status"),
        )

        return layout

    def run_continuous_monitoring(self):
        """Run continuous performance monitoring."""
        console.print(
            "🚀 [bold green]Starting Advanced Performance Monitor[/bold green]"
        )
        console.print(f"📊 Monitoring interval: {self.monitoring_interval} seconds")
        console.print("🔄 Press Ctrl+C to stop\n")

        try:
            with Live(self.create_monitoring_display(), refresh_per_second=0.5) as live:
                while True:
                    # Collect resource snapshot
                    snapshot = self.collect_system_metrics()
                    self.resource_history.append(snapshot)

                    # Check for resource alerts
                    alerts = self.alert_manager.check_resource_alerts(snapshot)
                    for alert in alerts:
                        console.print(f"[red]ALERT: {alert.message}[/red]")

                    # Update display
                    live.update(self.create_monitoring_display())

                    # Wait for next cycle
                    time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            console.print("\n🛑 [bold red]Performance Monitor stopped[/bold red]")
            # Generate final report
            report = self.generate_performance_report()
            console.print("\n" + report)

            # Save report to file
            report_path = (
                self.project_root / "logs" / "monitoring" / "performance_report.txt"
            )
            with open(report_path, "w") as f:
                f.write(report)
            console.print(f"\n📄 Performance report saved: {report_path}")

        except Exception as e:
            console.print(f"\n❌ [bold red]Monitor error: {e}[/bold red]")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Performance Monitor")
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Monitoring interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate report only (no live monitoring)",
    )

    args = parser.parse_args()
    monitor = AdvancedPerformanceMonitor(monitoring_interval=args.interval)

    if args.report:
        report = monitor.generate_performance_report()
        print(report)
    else:
        monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main()
