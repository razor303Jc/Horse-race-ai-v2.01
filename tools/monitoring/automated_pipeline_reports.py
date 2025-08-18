#!/usr/bin/env python3
"""
🎯 Automated Pipeline Reports System for 17-Stage Dynamic Pipeline
===============================================================

Comprehensive automated reporting for all pipeline stages:
- Real-time stage monitoring and reporting
- Performance metrics per stage
- Quality assessment for each phase
- Automated HTML dashboard generation
- CSV export for detailed analysis
- Integration with existing monitoring system
"""

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StageMetrics:
    """Metrics for individual pipeline stage"""

    stage_id: str
    stage_name: str
    phase: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    records_processed: int = 0
    records_output: int = 0
    success: bool = True
    error_count: int = 0
    warning_count: int = 0
    data_quality_score: float = 100.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    throughput_records_per_sec: float = 0.0
    status: str = "RUNNING"
    notes: str = ""


@dataclass
class PipelineRunSummary:
    """Summary of complete pipeline run"""

    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    stages_completed: int = 0
    stages_failed: int = 0
    total_records_processed: int = 0
    overall_success_rate: float = 100.0
    overall_data_quality: float = 100.0
    pipeline_efficiency: float = 100.0


class PipelineStageReporter:
    """Automated reporting system for pipeline stages"""

    def __init__(self, db_path: str = "monitoring/pipeline_reports.db"):
        """Initialize the reporting system"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Pipeline stage definitions from master schedule
        self.stage_definitions = {
            "data_download": {
                "name": "Data Download",
                "phase": "Data Acquisition",
                "description": "Download daily racing data",
                "critical": True,
                "expected_duration": 5,
                "expected_records": 1000,
            },
            "data_validation": {
                "name": "Data Validation",
                "phase": "Data Acquisition",
                "description": "Validate downloaded data integrity",
                "critical": True,
                "expected_duration": 3,
                "expected_records": 1000,
            },
            "enhanced_preprocessing": {
                "name": "Enhanced Preprocessing",
                "phase": "Data Processing",
                "description": "Enhanced CSV cleaning and standardization",
                "critical": True,
                "expected_duration": 12,
                "expected_records": 950,
            },
            "data_preprocessing": {
                "name": "Data Preprocessing",
                "phase": "Data Processing",
                "description": "Clean and preprocess race data",
                "critical": True,
                "expected_duration": 12,
                "expected_records": 900,
            },
            "data_relationships": {
                "name": "Data Relationships",
                "phase": "Data Processing",
                "description": "Process data relationships and linkages",
                "critical": True,
                "expected_duration": 8,
                "expected_records": 900,
            },
            "feature_engineering": {
                "name": "Feature Engineering",
                "phase": "Analysis",
                "description": "Create ML features from processed data",
                "critical": True,
                "expected_duration": 18,
                "expected_records": 850,
            },
            "contextual_analysis": {
                "name": "Contextual Analysis",
                "phase": "Analysis",
                "description": "Analyze racing context and conditions",
                "critical": True,
                "expected_duration": 15,
                "expected_records": 850,
            },
            "form_scoring": {
                "name": "Form Scoring",
                "phase": "Scoring",
                "description": "Calculate horse form scores",
                "critical": True,
                "expected_duration": 12,
                "expected_records": 800,
            },
            "power_ratings": {
                "name": "Power Ratings",
                "phase": "Scoring",
                "description": "Generate power ratings for horses",
                "critical": True,
                "expected_duration": 20,
                "expected_records": 800,
            },
            "speed_analysis": {
                "name": "Speed Analysis",
                "phase": "Scoring",
                "description": "Analyze speed ratings and performance",
                "critical": True,
                "expected_duration": 15,
                "expected_records": 800,
            },
            "ml_model_training": {
                "name": "ML Model Training",
                "phase": "Machine Learning",
                "description": "Train and update ML models",
                "critical": True,
                "expected_duration": 85,
                "expected_records": 750,
            },
            "monte_carlo_simulations": {
                "name": "Monte Carlo Simulations",
                "phase": "Prediction",
                "description": "Run Monte Carlo race simulations",
                "critical": True,
                "expected_duration": 30,
                "expected_records": 200,
            },
            "race_trends": {
                "name": "Race Trends",
                "phase": "Analysis",
                "description": "Analyze trends and patterns",
                "critical": False,
                "expected_duration": 10,
                "expected_records": 100,
            },
            "composite_scoring": {
                "name": "Composite Scoring",
                "phase": "Scoring",
                "description": "Generate composite prediction scores",
                "critical": True,
                "expected_duration": 10,
                "expected_records": 200,
            },
            "betting_strategies": {
                "name": "Betting Strategies",
                "phase": "Betting",
                "description": "Generate betting recommendations",
                "critical": True,
                "expected_duration": 15,
                "expected_records": 50,
            },
            "ai_selections": {
                "name": "AI Selections",
                "phase": "Output",
                "description": "Generate final AI selections",
                "critical": True,
                "expected_duration": 8,
                "expected_records": 20,
            },
            "report_generation": {
                "name": "Report Generation",
                "phase": "Output",
                "description": "Generate comprehensive reports",
                "critical": True,
                "expected_duration": 12,
                "expected_records": 10,
            },
            "pre_race_updates": {
                "name": "Pre-race Updates",
                "phase": "Live Updates",
                "description": "Final pre-race data updates",
                "critical": False,
                "expected_duration": 15,
                "expected_records": 20,
            },
        }

        self._init_database()
        self.current_run_id = None

        logger.info(
            f"Pipeline Stage Reporter initialized with {len(self.stage_definitions)} stages"
        )

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            # Stage metrics table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stage_id TEXT NOT NULL,
                    stage_name TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    records_processed INTEGER,
                    records_output INTEGER,
                    success BOOLEAN,
                    error_count INTEGER,
                    warning_count INTEGER,
                    data_quality_score REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    throughput_records_per_sec REAL,
                    status TEXT,
                    notes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Pipeline run summary table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT UNIQUE NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    total_duration_seconds REAL,
                    stages_completed INTEGER,
                    stages_failed INTEGER,
                    total_records_processed INTEGER,
                    overall_success_rate REAL,
                    overall_data_quality REAL,
                    pipeline_efficiency REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

    def start_pipeline_run(self) -> str:
        """Start a new pipeline run"""
        self.current_run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        run_summary = PipelineRunSummary(
            run_id=self.current_run_id, start_time=datetime.now()
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO pipeline_runs 
                (run_id, start_time, stages_completed, stages_failed, 
                 total_records_processed, overall_success_rate, 
                 overall_data_quality, pipeline_efficiency)
                VALUES (?, ?, 0, 0, 0, 100.0, 100.0, 100.0)
            """,
                (run_summary.run_id, run_summary.start_time.isoformat()),
            )

        logger.info(f"🚀 Started pipeline run: {self.current_run_id}")
        return self.current_run_id

    def start_stage(self, stage_id: str, **kwargs) -> StageMetrics:
        """Start monitoring a pipeline stage"""
        if not self.current_run_id:
            self.start_pipeline_run()

        stage_def = self.stage_definitions.get(stage_id, {})

        stage_metrics = StageMetrics(
            stage_id=stage_id,
            stage_name=stage_def.get("name", stage_id.replace("_", " ").title()),
            phase=stage_def.get("phase", "Unknown"),
            start_time=datetime.now(),
            status="RUNNING",
        )

        # Update with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(stage_metrics, key):
                setattr(stage_metrics, key, value)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO stage_metrics 
                (run_id, stage_id, stage_name, phase, start_time, 
                 records_processed, records_output, success, error_count, 
                 warning_count, data_quality_score, memory_usage_mb, 
                 cpu_usage_percent, throughput_records_per_sec, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.current_run_id,
                    stage_metrics.stage_id,
                    stage_metrics.stage_name,
                    stage_metrics.phase,
                    stage_metrics.start_time.isoformat(),
                    stage_metrics.records_processed,
                    stage_metrics.records_output,
                    stage_metrics.success,
                    stage_metrics.error_count,
                    stage_metrics.warning_count,
                    stage_metrics.data_quality_score,
                    stage_metrics.memory_usage_mb,
                    stage_metrics.cpu_usage_percent,
                    stage_metrics.throughput_records_per_sec,
                    stage_metrics.status,
                    stage_metrics.notes,
                ),
            )

        logger.info(f"▶️  Started stage: {stage_metrics.stage_name} ({stage_id})")
        return stage_metrics

    def complete_stage(self, stage_id: str, **kwargs) -> StageMetrics:
        """Complete monitoring a pipeline stage"""
        end_time = datetime.now()

        # Get the most recent stage entry
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM stage_metrics 
                WHERE run_id = ? AND stage_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """,
                (self.current_run_id, stage_id),
            )

            row = cursor.fetchone()
            if not row:
                logger.error(f"No active stage found for {stage_id}")
                return None

        # Calculate metrics
        start_time = datetime.fromisoformat(row[5])  # start_time column
        duration = (end_time - start_time).total_seconds()

        # Calculate throughput
        records_processed = kwargs.get("records_processed", row[7])
        throughput = records_processed / duration if duration > 0 else 0

        # Update stage completion
        update_data = {
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "records_processed": kwargs.get("records_processed", row[7]),
            "records_output": kwargs.get("records_output", row[8]),
            "success": kwargs.get("success", True),
            "error_count": kwargs.get("error_count", 0),
            "warning_count": kwargs.get("warning_count", 0),
            "data_quality_score": kwargs.get("data_quality_score", 100.0),
            "memory_usage_mb": kwargs.get("memory_usage_mb", 0.0),
            "cpu_usage_percent": kwargs.get("cpu_usage_percent", 0.0),
            "throughput_records_per_sec": throughput,
            "status": "COMPLETED" if kwargs.get("success", True) else "FAILED",
            "notes": kwargs.get("notes", ""),
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE stage_metrics SET
                    end_time = ?, duration_seconds = ?, records_processed = ?,
                    records_output = ?, success = ?, error_count = ?,
                    warning_count = ?, data_quality_score = ?, memory_usage_mb = ?,
                    cpu_usage_percent = ?, throughput_records_per_sec = ?,
                    status = ?, notes = ?
                WHERE run_id = ? AND stage_id = ? AND id = ?
            """,
                (
                    update_data["end_time"],
                    update_data["duration_seconds"],
                    update_data["records_processed"],
                    update_data["records_output"],
                    update_data["success"],
                    update_data["error_count"],
                    update_data["warning_count"],
                    update_data["data_quality_score"],
                    update_data["memory_usage_mb"],
                    update_data["cpu_usage_percent"],
                    update_data["throughput_records_per_sec"],
                    update_data["status"],
                    update_data["notes"],
                    self.current_run_id,
                    stage_id,
                    row[0],
                ),
            )

        # Update pipeline run summary
        self._update_pipeline_summary()

        status_icon = "✅" if update_data["success"] else "❌"
        logger.info(
            f"{status_icon} Completed stage: {row[3]} in {duration:.2f}s "
            f"({records_processed} records, {throughput:.1f} rec/s)"
        )

        return update_data

    def _update_pipeline_summary(self):
        """Update the pipeline run summary"""
        with sqlite3.connect(self.db_path) as conn:
            # Get stage statistics
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_stages,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_stages,
                    SUM(records_processed) as total_records,
                    AVG(data_quality_score) as avg_quality,
                    SUM(duration_seconds) as total_duration
                FROM stage_metrics 
                WHERE run_id = ?
            """,
                (self.current_run_id,),
            )

            stats = cursor.fetchone()

            if stats and stats[0] > 0:
                total_stages = stats[0]
                successful_stages = stats[1] or 0
                failed_stages = total_stages - successful_stages
                success_rate = (successful_stages / total_stages) * 100

                # Calculate efficiency (actual vs expected duration)
                expected_total = sum(
                    stage["expected_duration"]
                    for stage in self.stage_definitions.values()
                )
                actual_total = stats[4] / 60  # Convert to minutes
                efficiency = (
                    (expected_total / actual_total) * 100 if actual_total > 0 else 100
                )

                conn.execute(
                    """
                    UPDATE pipeline_runs SET
                        stages_completed = ?, stages_failed = ?,
                        total_records_processed = ?, overall_success_rate = ?,
                        overall_data_quality = ?, pipeline_efficiency = ?,
                        total_duration_seconds = ?
                    WHERE run_id = ?
                """,
                    (
                        successful_stages,
                        failed_stages,
                        stats[2] or 0,
                        success_rate,
                        stats[3] or 100.0,
                        min(efficiency, 100.0),
                        stats[4] or 0,
                        self.current_run_id,
                    ),
                )

    def complete_pipeline_run(self):
        """Complete the current pipeline run"""
        if not self.current_run_id:
            return

        end_time = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE pipeline_runs SET end_time = ? WHERE run_id = ?
            """,
                (end_time.isoformat(), self.current_run_id),
            )

        logger.info(f"🏁 Completed pipeline run: {self.current_run_id}")

        # Generate completion report
        self.generate_pipeline_report(self.current_run_id)

        self.current_run_id = None

    def generate_pipeline_report(self, run_id: str = None) -> str:
        """Generate comprehensive pipeline report"""
        if run_id is None:
            run_id = self.current_run_id

        if not run_id:
            logger.error("No run ID provided for report generation")
            return None

        # Get run summary
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM pipeline_runs WHERE run_id = ?
            """,
                (run_id,),
            )
            run_data = cursor.fetchone()

            if not run_data:
                logger.error(f"No run data found for {run_id}")
                return None

            # Get stage details
            cursor = conn.execute(
                """
                SELECT * FROM stage_metrics WHERE run_id = ? ORDER BY start_time
            """,
                (run_id,),
            )
            stages_data = cursor.fetchall()

        # Generate HTML report
        report_html = self._generate_html_report(run_data, stages_data)

        # Save report
        report_path = f"monitoring/reports/pipeline_report_{run_id}.html"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            f.write(report_html)

        logger.info(f"📊 Pipeline report generated: {report_path}")
        return report_path

    def _generate_html_report(self, run_data: tuple, stages_data: List[tuple]) -> str:
        """Generate HTML report from run data"""
        template = Template(
            """
<!DOCTYPE html>
<html>
<head>
    <title>🏇 Pipeline Report - {{ run_id }}</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .error { color: #e74c3c; }
        .stage-table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
        .stage-table th, .stage-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .stage-table th { background: #34495e; color: white; }
        .status-success { background: #d5f4e6; color: #27ae60; }
        .status-failed { background: #ffeaea; color: #e74c3c; }
        .status-running { background: #fff3cd; color: #856404; }
        .chart-container { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .phase-group { margin: 20px 0; }
        .phase-header { background: #3498db; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏇 Horse Racing AI Pipeline Report</h1>
            <h2>Run ID: {{ run_id }}</h2>
            <p><strong>Generated:</strong> {{ current_time }}</p>
            <p><strong>Duration:</strong> {{ run_duration_formatted }}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>📊 Execution Summary</h3>
                <p><strong>Total Stages:</strong> {{ total_stages }}</p>
                <p><strong>Completed:</strong> <span class="success">{{ stages_completed }}</span></p>
                <p><strong>Failed:</strong> <span class="error">{{ stages_failed }}</span></p>
                <p><strong>Success Rate:</strong> <span class="success">{{ "%.1f"|format(success_rate) }}%</span></p>
            </div>
            
            <div class="summary-card">
                <h3>📈 Performance Metrics</h3>
                <p><strong>Total Records:</strong> {{ total_records }}</p>
                <p><strong>Avg Quality:</strong> <span class="success">{{ "%.1f"|format(avg_quality) }}%</span></p>
                <p><strong>Pipeline Efficiency:</strong> <span class="success">{{ "%.1f"|format(efficiency) }}%</span></p>
                <p><strong>Total Duration:</strong> {{ "%.1f"|format(total_duration_minutes) }} min</p>
            </div>
            
            <div class="summary-card">
                <h3>🔧 System Health</h3>
                <p><strong>Avg CPU:</strong> {{ "%.1f"|format(avg_cpu) }}%</p>
                <p><strong>Avg Memory:</strong> {{ "%.1f"|format(avg_memory) }} MB</p>
                <p><strong>Total Errors:</strong> <span class="error">{{ total_errors }}</span></p>
                <p><strong>Total Warnings:</strong> <span class="warning">{{ total_warnings }}</span></p>
            </div>
            
            <div class="summary-card">
                <h3>⚡ Throughput</h3>
                <p><strong>Avg Throughput:</strong> {{ "%.1f"|format(avg_throughput) }} rec/s</p>
                <p><strong>Peak Throughput:</strong> {{ "%.1f"|format(peak_throughput) }} rec/s</p>
                <p><strong>Total Processing Time:</strong> {{ "%.1f"|format(total_processing_time) }} min</p>
                <p><strong>Data Processing Rate:</strong> {{ "%.1f"|format(data_rate) }} rec/min</p>
            </div>
        </div>
        
        <!-- Stages by Phase -->
        {% for phase, phase_stages in stages_by_phase.items() %}
        <div class="phase-group">
            <div class="phase-header">
                <h3>{{ phase }} Phase ({{ phase_stages|length }} stages)</h3>
            </div>
            
            <table class="stage-table">
                <thead>
                    <tr>
                        <th>Stage</th>
                        <th>Duration</th>
                        <th>Records In</th>
                        <th>Records Out</th>
                        <th>Quality</th>
                        <th>Throughput</th>
                        <th>Status</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stage in phase_stages %}
                    <tr>
                        <td><strong>{{ stage.stage_name }}</strong></td>
                        <td>{{ "%.2f"|format(stage.duration_seconds) }}s</td>
                        <td>{{ stage.records_processed }}</td>
                        <td>{{ stage.records_output }}</td>
                        <td>{{ "%.1f"|format(stage.data_quality_score) }}%</td>
                        <td>{{ "%.1f"|format(stage.throughput_records_per_sec) }} rec/s</td>
                        <td class="status-{{ 'success' if stage.success else 'failed' }}">
                            {{ '✅ COMPLETED' if stage.success else '❌ FAILED' }}
                        </td>
                        <td>{{ stage.notes or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endfor %}
        
        <!-- Detailed Stage Timeline -->
        <div class="chart-container">
            <h3>📋 Complete Stage Timeline</h3>
            <table class="stage-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Stage</th>
                        <th>Phase</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Duration</th>
                        <th>Records</th>
                        <th>Quality</th>
                        <th>Errors</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stage in all_stages %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ stage.stage_name }}</strong></td>
                        <td>{{ stage.phase }}</td>
                        <td>{{ stage.start_time_formatted }}</td>
                        <td>{{ stage.end_time_formatted }}</td>
                        <td>{{ "%.2f"|format(stage.duration_seconds) }}s</td>
                        <td>{{ stage.records_processed }}</td>
                        <td>{{ "%.1f"|format(stage.data_quality_score) }}%</td>
                        <td>{{ stage.error_count }}</td>
                        <td class="status-{{ 'success' if stage.success else 'failed' }}">
                            {{ stage.status }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="chart-container">
            <h3>📊 Performance Analysis</h3>
            <h4>Key Insights:</h4>
            <ul>
                <li><strong>Most Efficient Stage:</strong> {{ most_efficient_stage }} ({{ "%.1f"|format(highest_throughput) }} rec/s)</li>
                <li><strong>Longest Running Stage:</strong> {{ longest_stage }} ({{ "%.2f"|format(longest_duration) }}s)</li>
                <li><strong>Highest Quality Stage:</strong> {{ highest_quality_stage }} ({{ "%.1f"|format(highest_quality) }}%)</li>
                <li><strong>Total Pipeline Efficiency:</strong> {{ "%.1f"|format(efficiency) }}% of expected time</li>
                {% if bottleneck_stage %}
                <li><strong>Potential Bottleneck:</strong> {{ bottleneck_stage }} ({{ "%.1f"|format(bottleneck_ratio) }}x expected time)</li>
                {% endif %}
            </ul>
        </div>
        
        <div class="chart-container">
            <h3>🔍 Quality Assessment</h3>
            <h4>Data Quality Summary:</h4>
            <ul>
                <li><strong>Overall Data Quality:</strong> {{ "%.1f"|format(avg_quality) }}%</li>
                <li><strong>Stages with Perfect Quality:</strong> {{ perfect_quality_count }}/{{ total_stages }}</li>
                <li><strong>Stages with Warnings:</strong> {{ stages_with_warnings }}</li>
                <li><strong>Stages with Errors:</strong> {{ stages_with_errors }}</li>
            </ul>
        </div>
        
        <div class="chart-container">
            <h3>⏱️ Timing Analysis</h3>
            <h4>Schedule Performance:</h4>
            <ul>
                <li><strong>Planned Total Duration:</strong> {{ planned_duration }} minutes</li>
                <li><strong>Actual Total Duration:</strong> {{ "%.1f"|format(total_duration_minutes) }} minutes</li>
                <li><strong>Time Variance:</strong> {{ "%.1f"|format(time_variance) }}% {{ 'ahead' if time_variance < 0 else 'behind' }} schedule</li>
                <li><strong>Buffer Time Remaining:</strong> {{ "%.1f"|format(buffer_remaining) }} minutes</li>
            </ul>
        </div>
    </div>
</body>
</html>
        """
        )

        # Parse stage data
        stages = []
        for stage_row in stages_data:
            stage = {
                "stage_id": stage_row[2],
                "stage_name": stage_row[3],
                "phase": stage_row[4],
                "start_time": stage_row[5],
                "end_time": stage_row[6],
                "duration_seconds": stage_row[7] or 0,
                "records_processed": stage_row[8] or 0,
                "records_output": stage_row[9] or 0,
                "success": bool(stage_row[10]),
                "error_count": stage_row[11] or 0,
                "warning_count": stage_row[12] or 0,
                "data_quality_score": stage_row[13] or 100,
                "memory_usage_mb": stage_row[14] or 0,
                "cpu_usage_percent": stage_row[15] or 0,
                "throughput_records_per_sec": stage_row[16] or 0,
                "status": stage_row[17],
                "notes": stage_row[18] or "",
                "start_time_formatted": stage_row[5][:19] if stage_row[5] else "",
                "end_time_formatted": stage_row[6][:19] if stage_row[6] else "",
            }
            stages.append(stage)

        # Group stages by phase
        stages_by_phase = {}
        for stage in stages:
            phase = stage["phase"]
            if phase not in stages_by_phase:
                stages_by_phase[phase] = []
            stages_by_phase[phase].append(stage)

        # Calculate summary statistics
        total_stages = len(stages)
        stages_completed = sum(1 for s in stages if s["success"])
        stages_failed = total_stages - stages_completed
        success_rate = (
            (stages_completed / total_stages * 100) if total_stages > 0 else 0
        )

        total_records = sum(s["records_processed"] for s in stages)
        avg_quality = (
            sum(s["data_quality_score"] for s in stages) / total_stages
            if total_stages > 0
            else 0
        )
        total_duration_seconds = sum(s["duration_seconds"] for s in stages)
        total_duration_minutes = total_duration_seconds / 60

        avg_cpu = (
            sum(s["cpu_usage_percent"] for s in stages) / total_stages
            if total_stages > 0
            else 0
        )
        avg_memory = (
            sum(s["memory_usage_mb"] for s in stages) / total_stages
            if total_stages > 0
            else 0
        )
        total_errors = sum(s["error_count"] for s in stages)
        total_warnings = sum(s["warning_count"] for s in stages)

        throughputs = [
            s["throughput_records_per_sec"]
            for s in stages
            if s["throughput_records_per_sec"] > 0
        ]
        avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0
        peak_throughput = max(throughputs) if throughputs else 0

        # Performance analysis
        most_efficient_stage = (
            max(stages, key=lambda x: x["throughput_records_per_sec"])["stage_name"]
            if stages
            else "N/A"
        )
        highest_throughput = max(throughputs) if throughputs else 0
        longest_stage = (
            max(stages, key=lambda x: x["duration_seconds"])["stage_name"]
            if stages
            else "N/A"
        )
        longest_duration = max(s["duration_seconds"] for s in stages) if stages else 0
        highest_quality_stage = (
            max(stages, key=lambda x: x["data_quality_score"])["stage_name"]
            if stages
            else "N/A"
        )
        highest_quality = max(s["data_quality_score"] for s in stages) if stages else 0

        # Calculate efficiency based on expected durations
        planned_duration = sum(
            self.stage_definitions[s["stage_id"]]["expected_duration"]
            for s in stages
            if s["stage_id"] in self.stage_definitions
        )
        efficiency = (
            (planned_duration / total_duration_minutes * 100)
            if total_duration_minutes > 0
            else 100
        )

        # Quality metrics
        perfect_quality_count = sum(1 for s in stages if s["data_quality_score"] >= 100)
        stages_with_warnings = sum(1 for s in stages if s["warning_count"] > 0)
        stages_with_errors = sum(1 for s in stages if s["error_count"] > 0)

        # Timing analysis
        time_variance = (
            ((total_duration_minutes - planned_duration) / planned_duration * 100)
            if planned_duration > 0
            else 0
        )
        buffer_remaining = (
            176 - total_duration_minutes
        )  # 176 minutes buffer before first race

        # Additional metrics
        total_processing_time = total_duration_minutes
        data_rate = (
            total_records / total_duration_minutes if total_duration_minutes > 0 else 0
        )

        # Run duration
        start_time = datetime.fromisoformat(run_data[2])
        end_time = (
            datetime.fromisoformat(run_data[3]) if run_data[3] else datetime.now()
        )
        run_duration = end_time - start_time
        run_duration_formatted = str(run_duration).split(".")[0]  # Remove microseconds

        return template.render(
            run_id=run_data[1],
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            run_duration_formatted=run_duration_formatted,
            total_stages=total_stages,
            stages_completed=stages_completed,
            stages_failed=stages_failed,
            success_rate=success_rate,
            total_records=total_records,
            avg_quality=avg_quality,
            efficiency=efficiency,
            total_duration_minutes=total_duration_minutes,
            avg_cpu=avg_cpu,
            avg_memory=avg_memory,
            total_errors=total_errors,
            total_warnings=total_warnings,
            avg_throughput=avg_throughput,
            peak_throughput=peak_throughput,
            total_processing_time=total_processing_time,
            data_rate=data_rate,
            stages_by_phase=stages_by_phase,
            all_stages=stages,
            most_efficient_stage=most_efficient_stage,
            highest_throughput=highest_throughput,
            longest_stage=longest_stage,
            longest_duration=longest_duration,
            highest_quality_stage=highest_quality_stage,
            highest_quality=highest_quality,
            perfect_quality_count=perfect_quality_count,
            stages_with_warnings=stages_with_warnings,
            stages_with_errors=stages_with_errors,
            planned_duration=planned_duration,
            time_variance=time_variance,
            buffer_remaining=buffer_remaining,
        )

    def export_to_csv(self, run_id: str = None, output_path: str = None) -> str:
        """Export pipeline report to CSV for detailed analysis"""
        if run_id is None:
            run_id = self.current_run_id

        if not run_id:
            logger.error("No run ID provided for CSV export")
            return None

        if output_path is None:
            output_path = f"monitoring/exports/pipeline_data_{run_id}.csv"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Get stage data
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    run_id, stage_id, stage_name, phase, start_time, end_time,
                    duration_seconds, records_processed, records_output, success,
                    error_count, warning_count, data_quality_score, memory_usage_mb,
                    cpu_usage_percent, throughput_records_per_sec, status, notes
                FROM stage_metrics 
                WHERE run_id = ? 
                ORDER BY start_time
            """

            df = pd.read_sql_query(query, conn, params=(run_id,))

        # Save to CSV
        df.to_csv(output_path, index=False)

        logger.info(f"📊 CSV export saved: {output_path}")
        return output_path

    def get_stage_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get stage performance statistics over time"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    stage_id,
                    stage_name,
                    COUNT(*) as execution_count,
                    AVG(duration_seconds) as avg_duration,
                    AVG(throughput_records_per_sec) as avg_throughput,
                    AVG(data_quality_score) as avg_quality,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(error_count) as total_errors,
                    SUM(warning_count) as total_warnings
                FROM stage_metrics 
                WHERE timestamp > datetime('now', '-{} days')
                GROUP BY stage_id, stage_name
                ORDER BY stage_id
            """.format(
                days
            )

            cursor = conn.execute(query)
            results = cursor.fetchall()

        statistics = {}
        for row in results:
            stage_id = row[0]
            statistics[stage_id] = {
                "stage_name": row[1],
                "execution_count": row[2],
                "avg_duration": row[3],
                "avg_throughput": row[4],
                "avg_quality": row[5],
                "success_rate": (row[6] / row[2] * 100) if row[2] > 0 else 0,
                "total_errors": row[7],
                "total_warnings": row[8],
            }

        return statistics

    def generate_summary_dashboard(self, days: int = 7) -> str:
        """Generate summary dashboard for multiple pipeline runs"""
        # Get pipeline run summaries
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM pipeline_runs 
                WHERE timestamp > datetime('now', '-{} days')
                ORDER BY start_time DESC
            """.format(
                days
            )

            df_runs = pd.read_sql_query(query, conn)

        if df_runs.empty:
            logger.warning("No pipeline runs found in the specified period")
            return None

        # Generate charts
        charts_dir = Path("monitoring/charts")
        charts_dir.mkdir(parents=True, exist_ok=True)

        # Success rate trend
        plt.figure(figsize=(12, 6))
        plt.plot(
            pd.to_datetime(df_runs["start_time"]),
            df_runs["overall_success_rate"],
            "b-o",
        )
        plt.title("Pipeline Success Rate Trend")
        plt.ylabel("Success Rate (%)")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        success_chart = charts_dir / f"success_trend_{days}d.png"
        plt.savefig(success_chart, dpi=150, bbox_inches="tight")
        plt.close()

        # Duration trend
        plt.figure(figsize=(12, 6))
        plt.plot(
            pd.to_datetime(df_runs["start_time"]),
            df_runs["total_duration_seconds"] / 60,
            "g-o",
        )
        plt.title("Pipeline Duration Trend")
        plt.ylabel("Duration (minutes)")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        duration_chart = charts_dir / f"duration_trend_{days}d.png"
        plt.savefig(duration_chart, dpi=150, bbox_inches="tight")
        plt.close()

        # Generate summary HTML
        summary_html = f"""
        <html>
        <head><title>Pipeline Summary Dashboard - Last {days} Days</title></head>
        <body>
            <h1>Pipeline Summary Dashboard</h1>
            <h2>Last {days} Days</h2>
            
            <h3>Summary Statistics</h3>
            <ul>
                <li><strong>Total Runs:</strong> {len(df_runs)}</li>
                <li><strong>Average Success Rate:</strong> {df_runs['overall_success_rate'].mean():.1f}%</li>
                <li><strong>Average Duration:</strong> {df_runs['total_duration_seconds'].mean()/60:.1f} minutes</li>
                <li><strong>Average Records Processed:</strong> {df_runs['total_records_processed'].mean():.0f}</li>
            </ul>
            
            <h3>Trends</h3>
            <img src="charts/{success_chart.name}" style="max-width: 100%; margin: 10px;">
            <img src="charts/{duration_chart.name}" style="max-width: 100%; margin: 10px;">
            
            <h3>Recent Runs</h3>
            {df_runs.to_html(index=False, classes='table table-striped')}
        </body>
        </html>
        """

        summary_path = f"monitoring/reports/summary_dashboard_{days}d.html"
        Path(summary_path).parent.mkdir(parents=True, exist_ok=True)

        with open(summary_path, "w") as f:
            f.write(summary_html)

        logger.info(f"📊 Summary dashboard generated: {summary_path}")
        return summary_path


def demonstrate_reporting_system():
    """Demonstrate the automated reporting system"""
    print("🎯 AUTOMATED PIPELINE REPORTING SYSTEM DEMO")
    print("=" * 60)

    # Initialize reporter
    reporter = PipelineStageReporter()

    # Start a demo pipeline run
    run_id = reporter.start_pipeline_run()
    print(f"🚀 Started demo pipeline run: {run_id}")

    # Simulate some pipeline stages
    demo_stages = [
        (
            "data_download",
            {
                "records_processed": 1200,
                "records_output": 1200,
                "data_quality_score": 98.5,
            },
        ),
        (
            "data_validation",
            {
                "records_processed": 1200,
                "records_output": 1180,
                "data_quality_score": 97.2,
            },
        ),
        (
            "enhanced_preprocessing",
            {
                "records_processed": 1180,
                "records_output": 1150,
                "data_quality_score": 96.8,
            },
        ),
        (
            "feature_engineering",
            {
                "records_processed": 1150,
                "records_output": 1100,
                "data_quality_score": 95.5,
            },
        ),
        (
            "ml_model_training",
            {
                "records_processed": 1100,
                "records_output": 800,
                "data_quality_score": 94.2,
            },
        ),
    ]

    for stage_id, completion_data in demo_stages:
        print(f"\n▶️  Processing stage: {stage_id}")

        # Start stage
        stage_metrics = reporter.start_stage(stage_id)

        # Simulate processing time
        import time

        time.sleep(0.5)

        # Complete stage
        completion_data.update(
            {"success": True, "memory_usage_mb": 150.0, "cpu_usage_percent": 65.0}
        )

        reporter.complete_stage(stage_id, **completion_data)
        print(f"✅ Completed stage: {stage_id}")

    # Complete pipeline run
    reporter.complete_pipeline_run()

    # Generate additional reports
    print(f"\n📊 Generating additional reports...")

    # CSV export
    csv_path = reporter.export_to_csv(run_id)
    print(f"📋 CSV export: {csv_path}")

    # Stage statistics
    stats = reporter.get_stage_statistics(days=1)
    print(f"📈 Stage statistics generated for {len(stats)} stages")

    # Summary dashboard
    summary_path = reporter.generate_summary_dashboard(days=1)
    if summary_path:
        print(f"📊 Summary dashboard: {summary_path}")

    print(
        f"\n✅ Demo completed! Check the monitoring/reports/ directory for generated reports."
    )
    return reporter


if __name__ == "__main__":
    # Run demonstration
    demonstrate_reporting_system()
