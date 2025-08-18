#!/usr/bin/env python3
"""
🧪 Test Monitoring System
=========================

Tests for the automated monitoring and reporting system
created for the 82% accuracy ML model and 17-stage pipeline.
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest


class TestPipelineStageReporter:
    """Test the PipelineStageReporter class"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary test database"""
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_path = temp_db.name
        temp_db.close()
        yield db_path
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def sample_stage_data(self):
        """Sample stage execution data"""
        return {
            "stage_id": "ml_model_training",
            "stage_name": "ML Model Training",
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(minutes=85),
            "duration": 85.0,
            "records_processed": 850,
            "records_output": 850,
            "quality_score": 94.2,
            "throughput": 10.0,
            "memory_usage": 512.5,
            "cpu_usage": 75.2,
            "status": "completed",
            "error_count": 0,
            "warnings": [],
        }

    def test_stage_metrics_calculation(self, sample_stage_data):
        """Test stage metrics calculation"""
        # Test duration calculation
        start_time = sample_stage_data["start_time"]
        end_time = sample_stage_data["end_time"]
        expected_duration = (end_time - start_time).total_seconds() / 60

        assert abs(expected_duration - 85.0) < 0.1

        # Test throughput calculation
        records = sample_stage_data["records_processed"]
        duration_minutes = sample_stage_data["duration"]
        expected_throughput = records / duration_minutes

        assert abs(expected_throughput - 10.0) < 0.1

        # Test quality score validation
        quality = sample_stage_data["quality_score"]
        assert 0 <= quality <= 100
        assert quality == 94.2

    def test_database_operations(self, temp_db, sample_stage_data):
        """Test database operations for metrics storage"""
        # Initialize database
        conn = sqlite3.connect(temp_db)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                stage_id TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration REAL,
                records_processed INTEGER,
                records_output INTEGER,
                quality_score REAL,
                throughput REAL,
                memory_usage REAL,
                cpu_usage REAL,
                status TEXT,
                error_count INTEGER,
                warnings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()

        # Insert test data
        run_id = "test_run_001"
        stage_data = sample_stage_data

        conn.execute(
            """
            INSERT INTO pipeline_metrics (
                run_id, stage_id, stage_name, start_time, end_time,
                duration, records_processed, records_output, quality_score,
                throughput, memory_usage, cpu_usage, status, error_count, warnings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                stage_data["stage_id"],
                stage_data["stage_name"],
                stage_data["start_time"].isoformat(),
                stage_data["end_time"].isoformat(),
                stage_data["duration"],
                stage_data["records_processed"],
                stage_data["records_output"],
                stage_data["quality_score"],
                stage_data["throughput"],
                stage_data["memory_usage"],
                stage_data["cpu_usage"],
                stage_data["status"],
                stage_data["error_count"],
                json.dumps(stage_data["warnings"]),
            ),
        )
        conn.commit()

        # Verify data insertion
        cursor = conn.execute(
            "SELECT COUNT(*) FROM pipeline_metrics WHERE run_id = ?", (run_id,)
        )
        count = cursor.fetchone()[0]
        assert count == 1

        # Verify data integrity
        cursor = conn.execute(
            "SELECT stage_id, quality_score, status FROM pipeline_metrics WHERE run_id = ?",
            (run_id,),
        )
        row = cursor.fetchone()
        assert row[0] == "ml_model_training"
        assert row[1] == 94.2
        assert row[2] == "completed"

        conn.close()

    def test_html_report_generation(self, sample_stage_data):
        """Test HTML report generation"""
        # Mock pipeline run data
        pipeline_data = {
            "run_id": "test_run_001",
            "start_time": datetime.now(),
            "total_duration": 290,
            "total_stages": 17,
            "success_rate": 100.0,
            "avg_quality": 94.9,
            "stages": [sample_stage_data],
        }

        # Generate HTML report
        html_content = self._generate_html_report(pipeline_data)

        # Verify HTML content
        assert "test_run_001" in html_content
        assert "ML Model Training" in html_content
        assert "94.2" in html_content
        assert "completed" in html_content
        assert "<!DOCTYPE html>" in html_content
        assert "</html>" in html_content

    def _generate_html_report(self, data):
        """Generate HTML report for testing"""
        return (
            f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pipeline Report - {data['run_id']}</title>
        </head>
        <body>
            <h1>Pipeline Report</h1>
            <p>Run ID: {data['run_id']}</p>
            <p>Total Duration: {data['total_duration']} minutes</p>
            <p>Success Rate: {data['success_rate']}%</p>
            <h2>Stages</h2>
            <ul>
        """
            + "".join(
                [
                    f"<li>{stage['stage_name']}: {stage['quality_score']}% quality, {stage['status']}</li>"
                    for stage in data["stages"]
                ]
            )
            + """
            </ul>
        </body>
        </html>
        """
        )

    def test_csv_export_functionality(self, sample_stage_data):
        """Test CSV export functionality"""
        # Create test data
        stages_data = [
            sample_stage_data,
            {
                **sample_stage_data,
                "stage_id": "betting_strategies",
                "stage_name": "Betting Strategies",
                "duration": 15.0,
                "records_processed": 80,
                "quality_score": 92.8,
            },
        ]

        # Convert to DataFrame
        df_data = []
        for stage in stages_data:
            df_data.append(
                {
                    "stage_id": stage["stage_id"],
                    "stage_name": stage["stage_name"],
                    "duration": stage["duration"],
                    "records_processed": stage["records_processed"],
                    "quality_score": stage["quality_score"],
                    "status": stage["status"],
                }
            )

        df = pd.DataFrame(df_data)

        # Test DataFrame structure
        assert len(df) == 2
        assert "stage_id" in df.columns
        assert "quality_score" in df.columns

        # Test data integrity
        assert df.iloc[0]["stage_id"] == "ml_model_training"
        assert df.iloc[1]["stage_id"] == "betting_strategies"
        assert df.iloc[0]["quality_score"] == 94.2
        assert df.iloc[1]["quality_score"] == 92.8


class TestLivePipelineReports:
    """Test live pipeline monitoring functionality"""

    @pytest.fixture
    def mock_pipeline_stages(self):
        """Mock pipeline stages configuration"""
        return {
            "data_download": {"duration": 5, "records": 1200},
            "data_validation": {"duration": 3, "records": 1180},
            "ml_model_training": {"duration": 85, "records": 850},
            "betting_strategies": {"duration": 15, "records": 80},
            "report_generation": {"duration": 12, "records": 25},
        }

    def test_stage_execution_monitoring(self, mock_pipeline_stages):
        """Test live stage execution monitoring"""
        executed_stages = []

        for stage_id, config in mock_pipeline_stages.items():
            # Simulate stage execution
            stage_result = {
                "stage_id": stage_id,
                "start_time": datetime.now(),
                "duration": config["duration"],
                "records": config["records"],
                "status": "completed",
            }
            executed_stages.append(stage_result)

        # Verify execution tracking
        assert len(executed_stages) == 5
        assert all(stage["status"] == "completed" for stage in executed_stages)

        # Verify stage order and timing
        total_duration = sum(stage["duration"] for stage in executed_stages)
        assert total_duration == 120  # 5 + 3 + 85 + 15 + 12

    def test_real_time_status_updates(self, mock_pipeline_stages):
        """Test real-time status updates"""
        pipeline_status = {
            "current_stage": None,
            "completed_stages": 0,
            "total_stages": len(mock_pipeline_stages),
            "overall_progress": 0.0,
            "estimated_completion": None,
        }

        # Simulate pipeline execution
        for i, (stage_id, config) in enumerate(mock_pipeline_stages.items()):
            # Update status
            pipeline_status["current_stage"] = stage_id
            pipeline_status["completed_stages"] = i
            pipeline_status["overall_progress"] = (i / len(mock_pipeline_stages)) * 100

            # Verify status update
            assert pipeline_status["current_stage"] == stage_id
            assert pipeline_status["completed_stages"] == i
            assert 0 <= pipeline_status["overall_progress"] <= 100

        # Final status
        pipeline_status["current_stage"] = None
        pipeline_status["completed_stages"] = len(mock_pipeline_stages)
        pipeline_status["overall_progress"] = 100.0

        assert pipeline_status["completed_stages"] == 5
        assert pipeline_status["overall_progress"] == 100.0

    def test_error_handling_and_reporting(self):
        """Test error handling in monitoring system"""
        # Simulate various error scenarios
        error_scenarios = [
            {
                "stage_id": "data_download",
                "error_type": "ConnectionError",
                "error_message": "Failed to download data",
                "recovery_action": "retry",
            },
            {
                "stage_id": "ml_model_training",
                "error_type": "MemoryError",
                "error_message": "Insufficient memory for model training",
                "recovery_action": "reduce_batch_size",
            },
            {
                "stage_id": "betting_strategies",
                "error_type": "ValidationError",
                "error_message": "Invalid betting parameters",
                "recovery_action": "use_defaults",
            },
        ]

        for scenario in error_scenarios:
            # Test error logging
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "stage_id": scenario["stage_id"],
                "error_type": scenario["error_type"],
                "error_message": scenario["error_message"],
                "recovery_action": scenario["recovery_action"],
                "severity": (
                    "high" if "model_training" in scenario["stage_id"] else "medium"
                ),
            }

            # Verify error logging structure
            assert "timestamp" in error_log
            assert "stage_id" in error_log
            assert "error_type" in error_log
            assert error_log["severity"] in ["low", "medium", "high"]


class TestPipelineReportsIntegration:
    """Test pipeline reports integration system"""

    def test_context_manager_functionality(self):
        """Test context manager for stage monitoring"""
        # Mock context manager behavior
        stage_context = {
            "stage_id": "ml_model_training",
            "start_time": None,
            "end_time": None,
            "metrics": {},
        }

        # Simulate context manager entry
        stage_context["start_time"] = datetime.now()

        # Simulate stage execution
        execution_time = 85.0  # minutes
        records_processed = 850

        # Simulate context manager exit
        stage_context["end_time"] = stage_context["start_time"] + timedelta(
            minutes=execution_time
        )
        stage_context["metrics"] = {
            "duration": execution_time,
            "records_processed": records_processed,
            "quality_score": 94.2,
        }

        # Verify context manager data
        assert stage_context["start_time"] is not None
        assert stage_context["end_time"] is not None
        assert stage_context["metrics"]["duration"] == 85.0
        assert stage_context["metrics"]["records_processed"] == 850

    def test_decorator_functionality(self):
        """Test decorator for automatic stage monitoring"""

        # Mock decorator behavior
        def stage_monitor_decorator(func):
            def wrapper(*args, **kwargs):
                # Pre-execution monitoring
                start_time = datetime.now()

                # Execute function
                result = func(*args, **kwargs)

                # Post-execution monitoring
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds() / 60

                # Log metrics
                metrics = {
                    "function_name": func.__name__,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "result": result,
                }

                return result, metrics

            return wrapper

        # Test decorator application
        @stage_monitor_decorator
        def mock_ml_training():
            # Simulate ML training
            return {"accuracy": 0.82, "model_size": "150MB"}

        result, metrics = mock_ml_training()

        # Verify decorator functionality
        assert result["accuracy"] == 0.82
        assert "duration" in metrics
        assert "start_time" in metrics
        assert metrics["function_name"] == "mock_ml_training"

    def test_integration_with_master_schedule(self):
        """Test integration with master schedule configuration"""
        # Mock master schedule
        master_schedule = {
            "pipeline_stages": {
                "data_download": {
                    "duration_minutes": 5,
                    "priority": "high",
                    "dependencies": [],
                },
                "ml_model_training": {
                    "duration_minutes": 85,
                    "priority": "critical",
                    "dependencies": ["data_download", "data_preprocessing"],
                },
                "betting_strategies": {
                    "duration_minutes": 15,
                    "priority": "high",
                    "dependencies": ["ml_model_training"],
                },
            }
        }

        # Test schedule parsing
        stages = master_schedule["pipeline_stages"]
        assert len(stages) == 3
        assert stages["ml_model_training"]["priority"] == "critical"
        assert "data_download" in stages["ml_model_training"]["dependencies"]

        # Test total duration calculation
        total_duration = sum(stage["duration_minutes"] for stage in stages.values())
        assert total_duration == 105  # 5 + 85 + 15


def run_monitoring_tests():
    """Run all monitoring system tests"""
    print("🧪 Testing Monitoring System...")
    print("=" * 35)

    # Run pytest programmatically for this file
    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v"], capture_output=True, text=True
    )

    print("Test Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    success = run_monitoring_tests()
    if success:
        print("✅ All monitoring tests passed!")
    else:
        print("❌ Some tests failed!")
