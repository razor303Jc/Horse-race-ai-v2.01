#!/usr/bin/env python3
"""
📊 Comprehensive Pipeline Monitoring & Reporting System
Real-time monitoring, metrics collection, and automated reporting

Features:
- Real-time pipeline monitoring
- Performance metrics collection
- Automated report generation
- Dashboard creation
- Alert integration
- Historical trend analysis
"""

import json
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from jinja2 import Template
import threading
import schedule


@dataclass
class PipelineMetrics:
    """Pipeline execution metrics"""
    timestamp: datetime
    phase: str
    stage: str
    process: str
    duration_seconds: float
    success: bool
    records_processed: int = 0
    files_processed: int = 0
    data_quality_score: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    error_count: int = 0
    warning_count: int = 0


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    active_connections: int
    load_average: float


@dataclass
class MLMetrics:
    """Machine learning model metrics"""
    timestamp: datetime
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    training_time_seconds: float
    prediction_count: int
    confidence_avg: float


class MetricsCollector:
    """Collect and store pipeline metrics"""
    
    def __init__(self, db_path: str = "monitoring/pipeline_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self.is_monitoring = False
        self.monitor_thread = None
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    phase TEXT,
                    stage TEXT,
                    process TEXT,
                    duration_seconds REAL,
                    success BOOLEAN,
                    records_processed INTEGER,
                    files_processed INTEGER,
                    data_quality_score REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    error_count INTEGER,
                    warning_count INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_io TEXT,
                    active_connections INTEGER,
                    load_average REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_name TEXT,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    auc_roc REAL,
                    training_time_seconds REAL,
                    prediction_count INTEGER,
                    confidence_avg REAL
                )
            """)
    
    def record_pipeline_metrics(self, metrics: PipelineMetrics):
        """Record pipeline execution metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO pipeline_metrics (
                    timestamp, phase, stage, process, duration_seconds, success,
                    records_processed, files_processed, data_quality_score,
                    memory_usage_mb, cpu_usage_percent, error_count, warning_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.phase, metrics.stage, metrics.process,
                metrics.duration_seconds, metrics.success,
                metrics.records_processed, metrics.files_processed,
                metrics.data_quality_score, metrics.memory_usage_mb,
                metrics.cpu_usage_percent, metrics.error_count,
                metrics.warning_count
            ))
    
    def record_system_metrics(self, metrics: SystemMetrics):
        """Record system performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics (
                    timestamp, cpu_percent, memory_percent, disk_percent,
                    network_io, active_connections, load_average
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.cpu_percent, metrics.memory_percent, metrics.disk_percent,
                json.dumps(metrics.network_io), metrics.active_connections,
                metrics.load_average
            ))
    
    def record_ml_metrics(self, metrics: MLMetrics):
        """Record ML model metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO ml_metrics (
                    timestamp, model_name, accuracy, precision, recall,
                    f1_score, auc_roc, training_time_seconds, prediction_count,
                    confidence_avg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.model_name, metrics.accuracy, metrics.precision,
                metrics.recall, metrics.f1_score, metrics.auc_roc,
                metrics.training_time_seconds, metrics.prediction_count,
                metrics.confidence_avg
            ))
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_system,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_system(self, interval_seconds: int):
        """Continuous system monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Try to get load average (Unix/Linux only)
                try:
                    load_avg = psutil.getloadavg()[0]
                except (AttributeError, OSError):
                    load_avg = 0.0
                
                # Count active connections
                try:
                    connections = len(psutil.net_connections())
                except (psutil.AccessDenied, OSError):
                    connections = 0
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=(disk.used / disk.total) * 100,
                    network_io={
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    },
                    active_connections=connections,
                    load_average=load_avg
                )
                
                self.record_system_metrics(metrics)
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(interval_seconds)
    
    def get_pipeline_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get pipeline metrics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM pipeline_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_time.isoformat(),))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system metrics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM system_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_time.isoformat(),))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_ml_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get ML metrics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM ml_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_time.isoformat(),))
            
            return [dict(row) for row in cursor.fetchall()]


class ReportGenerator:
    """Generate comprehensive pipeline reports"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.report_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load Jinja2 templates for report generation"""
        templates = {}
        
        # Dashboard template
        dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>🏇 Horse Racing AI Pipeline Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .metric-card { background: white; padding: 20px; margin: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .error { color: #e74c3c; }
        .chart-container { width: 100%; height: 400px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏇 Horse Racing AI Pipeline Dashboard</h1>
            <p>Generated: {{ current_time }}</p>
            <p>Coverage: Last {{ hours }} hours</p>
        </div>
        
        <div class="metric-grid">
            <div class="metric-card">
                <h3>📊 Pipeline Overview</h3>
                <p><strong>Total Executions:</strong> {{ pipeline_summary.total_executions }}</p>
                <p><strong>Success Rate:</strong> <span class="success">{{ "%.1f"|format(pipeline_summary.success_rate) }}%</span></p>
                <p><strong>Avg Duration:</strong> {{ "%.2f"|format(pipeline_summary.avg_duration) }}s</p>
                <p><strong>Records Processed:</strong> {{ pipeline_summary.total_records }}</p>
            </div>
            
            <div class="metric-card">
                <h3>🖥️ System Health</h3>
                <p><strong>CPU Usage:</strong> {{ "%.1f"|format(system_summary.avg_cpu) }}%</p>
                <p><strong>Memory Usage:</strong> {{ "%.1f"|format(system_summary.avg_memory) }}%</p>
                <p><strong>Disk Usage:</strong> {{ "%.1f"|format(system_summary.avg_disk) }}%</p>
                <p><strong>Load Average:</strong> {{ "%.2f"|format(system_summary.avg_load) }}</p>
            </div>
            
            <div class="metric-card">
                <h3>🤖 ML Performance</h3>
                <p><strong>Model Accuracy:</strong> <span class="success">{{ "%.3f"|format(ml_summary.avg_accuracy) }}</span></p>
                <p><strong>Predictions Made:</strong> {{ ml_summary.total_predictions }}</p>
                <p><strong>Avg Confidence:</strong> {{ "%.3f"|format(ml_summary.avg_confidence) }}</p>
                <p><strong>Training Time:</strong> {{ "%.1f"|format(ml_summary.total_training_time) }}s</p>
            </div>
            
            <div class="metric-card">
                <h3>📈 Data Quality</h3>
                <p><strong>Avg Quality Score:</strong> <span class="success">{{ "%.1f"|format(data_quality.avg_score) }}%</span></p>
                <p><strong>Files Processed:</strong> {{ data_quality.total_files }}</p>
                <p><strong>Errors:</strong> <span class="error">{{ data_quality.total_errors }}</span></p>
                <p><strong>Warnings:</strong> <span class="warning">{{ data_quality.total_warnings }}</span></p>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>📋 Recent Pipeline Executions</h3>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Phase</th>
                        <th>Stage</th>
                        <th>Duration</th>
                        <th>Status</th>
                        <th>Records</th>
                        <th>Quality</th>
                    </tr>
                </thead>
                <tbody>
                    {% for execution in recent_executions %}
                    <tr>
                        <td>{{ execution.timestamp[:19] }}</td>
                        <td>{{ execution.phase }}</td>
                        <td>{{ execution.stage }}</td>
                        <td>{{ "%.2f"|format(execution.duration_seconds) }}s</td>
                        <td class="{{ 'success' if execution.success else 'error' }}">
                            {{ '✅' if execution.success else '❌' }}
                        </td>
                        <td>{{ execution.records_processed }}</td>
                        <td>{{ "%.1f"|format(execution.data_quality_score) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """
        
        templates['dashboard'] = Template(dashboard_template)
        return templates
    
    def generate_dashboard(self, hours: int = 24) -> str:
        """Generate HTML dashboard"""
        # Get metrics data
        pipeline_metrics = self.metrics_collector.get_pipeline_metrics(hours)
        system_metrics = self.metrics_collector.get_system_metrics(hours)
        ml_metrics = self.metrics_collector.get_ml_metrics(hours)
        
        # Calculate summaries
        pipeline_summary = self._calculate_pipeline_summary(pipeline_metrics)
        system_summary = self._calculate_system_summary(system_metrics)
        ml_summary = self._calculate_ml_summary(ml_metrics)
        data_quality = self._calculate_data_quality_summary(pipeline_metrics)
        
        # Render template
        return self.report_templates['dashboard'].render(
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            hours=hours,
            pipeline_summary=pipeline_summary,
            system_summary=system_summary,
            ml_summary=ml_summary,
            data_quality=data_quality,
            recent_executions=pipeline_metrics[:20]  # Last 20 executions
        )
    
    def _calculate_pipeline_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate pipeline execution summary"""
        if not metrics:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "total_records": 0
            }
        
        total_executions = len(metrics)
        successful = sum(1 for m in metrics if m['success'])
        success_rate = (successful / total_executions) * 100
        avg_duration = sum(m['duration_seconds'] for m in metrics) / total_executions
        total_records = sum(m['records_processed'] for m in metrics)
        
        return {
            "total_executions": total_executions,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "total_records": total_records
        }
    
    def _calculate_system_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate system performance summary"""
        if not metrics:
            return {
                "avg_cpu": 0,
                "avg_memory": 0,
                "avg_disk": 0,
                "avg_load": 0
            }
        
        avg_cpu = sum(m['cpu_percent'] for m in metrics) / len(metrics)
        avg_memory = sum(m['memory_percent'] for m in metrics) / len(metrics)
        avg_disk = sum(m['disk_percent'] for m in metrics) / len(metrics)
        avg_load = sum(m['load_average'] for m in metrics) / len(metrics)
        
        return {
            "avg_cpu": avg_cpu,
            "avg_memory": avg_memory,
            "avg_disk": avg_disk,
            "avg_load": avg_load
        }
    
    def _calculate_ml_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ML performance summary"""
        if not metrics:
            return {
                "avg_accuracy": 0,
                "total_predictions": 0,
                "avg_confidence": 0,
                "total_training_time": 0
            }
        
        avg_accuracy = sum(m['accuracy'] for m in metrics) / len(metrics)
        total_predictions = sum(m['prediction_count'] for m in metrics)
        avg_confidence = sum(m['confidence_avg'] for m in metrics) / len(metrics)
        total_training_time = sum(m['training_time_seconds'] for m in metrics)
        
        return {
            "avg_accuracy": avg_accuracy,
            "total_predictions": total_predictions,
            "avg_confidence": avg_confidence,
            "total_training_time": total_training_time
        }
    
    def _calculate_data_quality_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate data quality summary"""
        if not metrics:
            return {
                "avg_score": 0,
                "total_files": 0,
                "total_errors": 0,
                "total_warnings": 0
            }
        
        avg_score = sum(m['data_quality_score'] for m in metrics) / len(metrics)
        total_files = sum(m['files_processed'] for m in metrics)
        total_errors = sum(m['error_count'] for m in metrics)
        total_warnings = sum(m['warning_count'] for m in metrics)
        
        return {
            "avg_score": avg_score,
            "total_files": total_files,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        }
    
    def generate_performance_charts(self, hours: int = 24) -> Dict[str, str]:
        """Generate performance charts"""
        # Get metrics data
        pipeline_metrics = self.metrics_collector.get_pipeline_metrics(hours)
        system_metrics = self.metrics_collector.get_system_metrics(hours)
        
        charts = {}
        
        # Pipeline execution times chart
        if pipeline_metrics:
            df_pipeline = pd.DataFrame(pipeline_metrics)
            df_pipeline['timestamp'] = pd.to_datetime(df_pipeline['timestamp'])
            
            plt.figure(figsize=(12, 6))
            plt.plot(df_pipeline['timestamp'], df_pipeline['duration_seconds'], 'b-', linewidth=2)
            plt.title('Pipeline Execution Times')
            plt.xlabel('Time')
            plt.ylabel('Duration (seconds)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = f"monitoring/charts/pipeline_times_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            Path(chart_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            charts['pipeline_times'] = chart_path
        
        # System metrics chart
        if system_metrics:
            df_system = pd.DataFrame(system_metrics)
            df_system['timestamp'] = pd.to_datetime(df_system['timestamp'])
            
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            plt.plot(df_system['timestamp'], df_system['cpu_percent'], 'r-', linewidth=2)
            plt.title('CPU Usage')
            plt.ylabel('Percentage')
            plt.xticks(rotation=45)
            
            plt.subplot(2, 2, 2)
            plt.plot(df_system['timestamp'], df_system['memory_percent'], 'g-', linewidth=2)
            plt.title('Memory Usage')
            plt.ylabel('Percentage')
            plt.xticks(rotation=45)
            
            plt.subplot(2, 2, 3)
            plt.plot(df_system['timestamp'], df_system['disk_percent'], 'b-', linewidth=2)
            plt.title('Disk Usage')
            plt.ylabel('Percentage')
            plt.xticks(rotation=45)
            
            plt.subplot(2, 2, 4)
            plt.plot(df_system['timestamp'], df_system['load_average'], 'm-', linewidth=2)
            plt.title('Load Average')
            plt.ylabel('Load')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            chart_path = f"monitoring/charts/system_metrics_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            Path(chart_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            charts['system_metrics'] = chart_path
        
        return charts
    
    def save_dashboard(self, output_path: str = None, hours: int = 24):
        """Save dashboard to HTML file"""
        if output_path is None:
            output_path = f"monitoring/reports/dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        dashboard_html = self.generate_dashboard(hours)
        
        with open(output_path, 'w') as f:
            f.write(dashboard_html)
        
        return output_path


class PipelineMonitor:
    """Comprehensive pipeline monitoring system"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.report_generator = ReportGenerator(self.metrics_collector)
        self.is_running = False
        
        # Start system monitoring
        self.metrics_collector.start_monitoring(interval_seconds=60)
        
        # Schedule automated reports
        self._setup_scheduled_reports()
    
    def _setup_scheduled_reports(self):
        """Setup automated report generation"""
        # Daily dashboard at 6 AM
        schedule.every().day.at("06:00").do(self._generate_daily_report)
        
        # Weekly report on Mondays at 6 AM
        schedule.every().monday.at("06:00").do(self._generate_weekly_report)
        
        # Monthly report on 1st of month at 6 AM
        schedule.every().month.at("06:00").do(self._generate_monthly_report)
    
    def _generate_daily_report(self):
        """Generate daily report"""
        output_path = f"monitoring/reports/daily_{datetime.now().strftime('%Y%m%d')}.html"
        self.report_generator.save_dashboard(output_path, hours=24)
        print(f"📊 Daily report generated: {output_path}")
    
    def _generate_weekly_report(self):
        """Generate weekly report"""
        output_path = f"monitoring/reports/weekly_{datetime.now().strftime('%Y_W%U')}.html"
        self.report_generator.save_dashboard(output_path, hours=168)  # 7 days
        print(f"📊 Weekly report generated: {output_path}")
    
    def _generate_monthly_report(self):
        """Generate monthly report"""
        output_path = f"monitoring/reports/monthly_{datetime.now().strftime('%Y_%m')}.html"
        self.report_generator.save_dashboard(output_path, hours=720)  # 30 days
        print(f"📊 Monthly report generated: {output_path}")
    
    def record_phase_start(self, phase: str, phase_id: str) -> datetime:
        """Record the start of a pipeline phase"""
        return datetime.now()
    
    def record_phase_end(self, phase: str, phase_id: str, start_time: datetime,
                        success: bool = True, **kwargs):
        """Record the end of a pipeline phase"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Get current system metrics
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        metrics = PipelineMetrics(
            timestamp=end_time,
            phase=phase,
            stage=kwargs.get('stage', ''),
            process=kwargs.get('process', ''),
            duration_seconds=duration,
            success=success,
            records_processed=kwargs.get('records_processed', 0),
            files_processed=kwargs.get('files_processed', 0),
            data_quality_score=kwargs.get('data_quality_score', 0.0),
            memory_usage_mb=memory_info.used / 1024 / 1024,
            cpu_usage_percent=cpu_percent,
            error_count=kwargs.get('error_count', 0),
            warning_count=kwargs.get('warning_count', 0)
        )
        
        self.metrics_collector.record_pipeline_metrics(metrics)
    
    def record_ml_metrics(self, model_name: str, **metrics):
        """Record ML model performance metrics"""
        ml_metrics = MLMetrics(
            timestamp=datetime.now(),
            model_name=model_name,
            accuracy=metrics.get('accuracy', 0.0),
            precision=metrics.get('precision', 0.0),
            recall=metrics.get('recall', 0.0),
            f1_score=metrics.get('f1_score', 0.0),
            auc_roc=metrics.get('auc_roc', 0.0),
            training_time_seconds=metrics.get('training_time', 0.0),
            prediction_count=metrics.get('prediction_count', 0),
            confidence_avg=metrics.get('confidence_avg', 0.0)
        )
        
        self.metrics_collector.record_ml_metrics(ml_metrics)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        # Get recent metrics
        recent_pipeline = self.metrics_collector.get_pipeline_metrics(hours=1)
        recent_system = self.metrics_collector.get_system_metrics(hours=1)
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_health": "healthy" if recent_pipeline and recent_pipeline[0]['success'] else "degraded",
            "recent_executions": len(recent_pipeline),
            "system_health": self._assess_system_health(recent_system),
            "last_execution": recent_pipeline[0] if recent_pipeline else None
        }
        
        return status
    
    def _assess_system_health(self, system_metrics: List[Dict[str, Any]]) -> str:
        """Assess overall system health"""
        if not system_metrics:
            return "unknown"
        
        latest = system_metrics[0]
        
        if (latest['cpu_percent'] > 90 or 
            latest['memory_percent'] > 90 or 
            latest['disk_percent'] > 95):
            return "critical"
        elif (latest['cpu_percent'] > 70 or 
              latest['memory_percent'] > 80 or 
              latest['disk_percent'] > 85):
            return "warning"
        else:
            return "healthy"
    
    def run_scheduled_tasks(self):
        """Run scheduled reporting tasks"""
        schedule.run_pending()
    
    def shutdown(self):
        """Shutdown monitoring system"""
        self.metrics_collector.stop_monitoring()
        print("📊 Pipeline monitoring system shutdown")


# Example usage and testing
if __name__ == "__main__":
    # Initialize monitoring system
    monitor = PipelineMonitor()
    
    print("📊 Testing Pipeline Monitoring System")
    
    # Simulate pipeline execution
    start_time = monitor.record_phase_start("data_acquisition", "phase_1")
    time.sleep(2)  # Simulate processing time
    
    monitor.record_phase_end(
        "data_acquisition", "phase_1", start_time,
        success=True,
        stage="download",
        process="auto_downloader",
        records_processed=1500,
        files_processed=15,
        data_quality_score=97.5
    )
    
    # Record ML metrics
    monitor.record_ml_metrics(
        "xgboost_classifier",
        accuracy=0.765,
        precision=0.741,
        recall=0.789,
        f1_score=0.764,
        auc_roc=0.823,
        training_time=45.2,
        prediction_count=1200,
        confidence_avg=0.78
    )
    
    # Generate dashboard
    dashboard_path = monitor.report_generator.save_dashboard(
        "monitoring/test_dashboard.html", hours=1
    )
    
    print(f"📊 Test dashboard generated: {dashboard_path}")
    
    # Get current status
    status = monitor.get_current_status()
    print(f"📊 Current status: {status}")
    
    print("✅ Monitoring system testing completed!")
