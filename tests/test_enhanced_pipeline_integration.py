#!/usr/bin/env python3
"""
Test Enhanced Pipeline Integration with Time-Aware ML Training
Horse Racing AI v2.04 - Comprehensive Integration Testing

Tests the complete enhanced pipeline workflow including:
- Data pipeline processing
- ML training optimization
- Time constraint management
- Notification systems
"""

import pytest
import sys
import os
import tempfile
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.automation.enhanced_pipeline_integration import EnhancedPipelineIntegration
from tools.ml_training.time_aware_ml_optimizer import TimeAwareMLOptimizer


class TestEnhancedPipelineIntegration:
    """Test suite for enhanced pipeline integration."""

    @pytest.fixture
    def temp_base_path(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Create necessary subdirectories
            (temp_path / "notifications").mkdir(exist_ok=True)
            (temp_path / "tools" / "automation").mkdir(parents=True, exist_ok=True)
            (temp_path / "tools" / "ml_training").mkdir(parents=True, exist_ok=True)
            yield temp_path

    @pytest.fixture
    def enhanced_pipeline(self, temp_base_path):
        """Create enhanced pipeline instance for testing."""
        return EnhancedPipelineIntegration(base_path=str(temp_base_path))

    def test_enhanced_pipeline_initialization(self, enhanced_pipeline):
        """Test enhanced pipeline initialization."""
        assert enhanced_pipeline.base_path is not None
        assert enhanced_pipeline.ml_optimizer is not None
        assert enhanced_pipeline.pipeline_config is not None

        # Check default configuration
        config = enhanced_pipeline.pipeline_config
        assert config["enable_ml_optimization"] is True
        assert config["ml_trigger_after_upload"] is True
        assert config["skip_ml_if_no_time"] is True
        assert config["notification_enabled"] is True

    @patch("subprocess.run")
    def test_check_data_freshness_success(self, mock_run, enhanced_pipeline):
        """Test successful data freshness check."""
        # Mock successful database query
        mock_run.return_value = MagicMock(
            returncode=0, stdout="2025-01-20 10:30:00\n(1 row)"
        )

        result = enhanced_pipeline.check_data_freshness()

        assert result["has_new_data"] is True
        assert "data_tables" in result

    @patch("subprocess.run")
    def test_check_data_freshness_no_data(self, mock_run, enhanced_pipeline):
        """Test data freshness check with no recent data."""
        # Mock query with no recent data
        mock_run.return_value = MagicMock(returncode=0, stdout="(0 rows)")

        result = enhanced_pipeline.check_data_freshness()

        assert result["has_new_data"] is False

    @patch("subprocess.run")
    def test_check_data_freshness_error(self, mock_run, enhanced_pipeline):
        """Test data freshness check with database error."""
        # Mock database connection error that raises exception
        mock_run.side_effect = Exception("Database connection failed")

        result = enhanced_pipeline.check_data_freshness()

        assert result["has_new_data"] is False
        assert "error" in result

    def test_should_trigger_ml_training_disabled(self, enhanced_pipeline):
        """Test ML training trigger when optimization is disabled."""
        enhanced_pipeline.pipeline_config["enable_ml_optimization"] = False

        data_status = {"has_new_data": True, "data_tables": {"result_races": 5000}}

        result = enhanced_pipeline.should_trigger_ml_training(data_status)

        assert result is False

    def test_should_trigger_ml_training_no_data(self, enhanced_pipeline):
        """Test ML training trigger with no new data."""
        data_status = {"has_new_data": False}

        result = enhanced_pipeline.should_trigger_ml_training(data_status)

        assert result is False

    def test_should_trigger_ml_training_insufficient_data(self, enhanced_pipeline):
        """Test ML training trigger with insufficient data."""
        data_status = {
            "has_new_data": True,
            "data_tables": {"result_races": 500},  # Below threshold
        }

        result = enhanced_pipeline.should_trigger_ml_training(data_status)

        assert result is False

    @patch.object(TimeAwareMLOptimizer, "calculate_available_training_time")
    def test_should_trigger_ml_training_insufficient_time(
        self, mock_time_calc, enhanced_pipeline
    ):
        """Test ML training trigger with insufficient time."""
        mock_time_calc.return_value = 30  # 30 minutes (below threshold)

        data_status = {"has_new_data": True, "data_tables": {"result_races": 5000}}

        result = enhanced_pipeline.should_trigger_ml_training(data_status)

        assert result is False

    @patch.object(TimeAwareMLOptimizer, "calculate_available_training_time")
    def test_should_trigger_ml_training_success(
        self, mock_time_calc, enhanced_pipeline
    ):
        """Test successful ML training trigger."""
        mock_time_calc.return_value = 180  # 3 hours (sufficient time)

        data_status = {"has_new_data": True, "data_tables": {"result_races": 5000}}

        result = enhanced_pipeline.should_trigger_ml_training(data_status)

        assert result is True

    @patch("subprocess.run")
    @patch.object(EnhancedPipelineIntegration, "check_data_freshness")
    @patch.object(EnhancedPipelineIntegration, "should_trigger_ml_training")
    @patch.object(TimeAwareMLOptimizer, "run_optimization_cycles")
    def test_run_enhanced_pipeline_success_with_ml(
        self,
        mock_ml_optimize,
        mock_should_trigger,
        mock_data_check,
        mock_subprocess,
        enhanced_pipeline,
    ):
        """Test successful enhanced pipeline run with ML training."""
        # Mock successful pipeline run
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")

        # Mock data check
        mock_data_check.return_value = {
            "has_new_data": True,
            "data_tables": {"result_races": 5000},
        }

        # Mock ML training trigger
        mock_should_trigger.return_value = True

        # Mock ML optimization
        mock_ml_optimize.return_value = {
            "training_completed": True,
            "cycles_completed": 3,
            "performance_improvement": 0.05,
        }

        result = enhanced_pipeline.run_enhanced_pipeline()

        assert result["success"] is True
        assert "data_pipeline" in result["steps_completed"]
        assert "data_check" in result["steps_completed"]
        assert "ml_training" in result["steps_completed"]
        assert "notifications" in result["steps_completed"]
        assert result["ml_training_results"]["training_completed"] is True

    @patch("subprocess.run")
    @patch.object(EnhancedPipelineIntegration, "check_data_freshness")
    @patch.object(EnhancedPipelineIntegration, "should_trigger_ml_training")
    def test_run_enhanced_pipeline_success_without_ml(
        self, mock_should_trigger, mock_data_check, mock_subprocess, enhanced_pipeline
    ):
        """Test successful enhanced pipeline run without ML training."""
        # Mock successful pipeline run
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")

        # Mock data check
        mock_data_check.return_value = {
            "has_new_data": True,
            "data_tables": {"result_races": 500},  # Insufficient data
        }

        # Mock ML training trigger (skip)
        mock_should_trigger.return_value = False

        result = enhanced_pipeline.run_enhanced_pipeline()

        assert result["success"] is True
        assert "data_pipeline" in result["steps_completed"]
        assert "data_check" in result["steps_completed"]
        assert "ml_training_skipped" in result["steps_completed"]
        assert result["ml_training_results"]["skipped"] is True

    @patch("subprocess.run")
    def test_run_enhanced_pipeline_data_pipeline_failure(
        self, mock_subprocess, enhanced_pipeline
    ):
        """Test enhanced pipeline with data pipeline failure."""
        # Mock failed pipeline run
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="Pipeline failed")

        result = enhanced_pipeline.run_enhanced_pipeline()

        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "Data pipeline failed"

    def test_send_pipeline_completion_notification(
        self, enhanced_pipeline, temp_base_path
    ):
        """Test pipeline completion notification."""
        results = {
            "success": True,
            "total_duration": 15.5,
            "ml_training_results": {"training_completed": True},
            "steps_completed": ["data_pipeline", "ml_training"],
        }

        enhanced_pipeline._send_pipeline_completion_notification(results)

        # Check notification file was created
        notification_dir = temp_base_path / "notifications"
        notification_files = list(notification_dir.glob("pipeline_complete_*.txt"))

        assert len(notification_files) > 0

        # Check notification content
        with open(notification_files[0], "r") as f:
            content = f.read()
            assert "✅ Success" in content
            assert "15.5 minutes" in content
            assert "✅ Completed" in content

    def test_send_pipeline_completion_notification_disabled(self, enhanced_pipeline):
        """Test notification when disabled."""
        enhanced_pipeline.pipeline_config["notification_enabled"] = False

        results = {"success": True}

        # Should not raise exception
        enhanced_pipeline._send_pipeline_completion_notification(results)

        # No notification files should be created
        notification_dir = enhanced_pipeline.base_path / "notifications"
        if notification_dir.exists():
            notification_files = list(notification_dir.glob("pipeline_complete_*.txt"))
            assert len(notification_files) == 0


class TestEnhancedPipelineIntegrationScenarios:
    """Test various real-world scenarios for enhanced pipeline."""

    def test_race_day_morning_scenario(self, tmp_path):
        """Test pipeline behavior on race day morning (limited time)."""
        pipeline = EnhancedPipelineIntegration(base_path=str(tmp_path))

        # Mock race starting soon (limited time)
        with patch.object(
            TimeAwareMLOptimizer, "calculate_available_training_time"
        ) as mock_time:
            mock_time.return_value = 30  # Only 30 minutes available

            data_status = {"has_new_data": True, "data_tables": {"result_races": 5000}}

            # Should skip ML training due to time constraints
            result = pipeline.should_trigger_ml_training(data_status)
            assert result is False

    def test_overnight_processing_scenario(self, tmp_path):
        """Test pipeline behavior during overnight processing (ample time)."""
        pipeline = EnhancedPipelineIntegration(base_path=str(tmp_path))

        # Mock overnight processing (ample time)
        with patch.object(
            TimeAwareMLOptimizer, "calculate_available_training_time"
        ) as mock_time:
            mock_time.return_value = 480  # 8 hours available

            data_status = {"has_new_data": True, "data_tables": {"result_races": 10000}}

            # Should trigger ML training with ample time
            result = pipeline.should_trigger_ml_training(data_status)
            assert result is True

    def test_mid_week_data_update_scenario(self, tmp_path):
        """Test pipeline behavior with mid-week data updates."""
        pipeline = EnhancedPipelineIntegration(base_path=str(tmp_path))

        # Mock mid-week scenario (moderate time)
        with patch.object(
            TimeAwareMLOptimizer, "calculate_available_training_time"
        ) as mock_time:
            mock_time.return_value = 150  # 2.5 hours available

            data_status = {"has_new_data": True, "data_tables": {"result_races": 3000}}

            # Should trigger ML training with sufficient time
            result = pipeline.should_trigger_ml_training(data_status)
            assert result is True


def test_enhanced_pipeline_cli():
    """Test enhanced pipeline command-line interface."""
    # Test help output
    result = subprocess.run(
        ["python3", "tools/automation/enhanced_pipeline_integration.py", "--help"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )

    assert result.returncode == 0
    assert "Enhanced Pipeline with ML Optimization" in result.stdout


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
