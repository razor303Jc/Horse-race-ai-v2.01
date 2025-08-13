#!/usr/bin/env python3
"""
Test Suite for Auto-Downloader Schedule Manager CLI
Tests the schedule management functionality and CLI interface
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
try:
    from tools.cli.schedule_manager import ScheduleManager
except ImportError:
    # Handle import error gracefully for testing
    ScheduleManager = None


class TestScheduleManagerCLI:
    """Test the Auto-Downloader Schedule Manager CLI tool"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test config directory structure
        self.config_dir = self.temp_path / "config" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Create test tools directory
        self.tools_dir = self.temp_path / "tools" / "utilities"
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        # Create test docker directory
        self.docker_dir = self.temp_path / "docker" / "automation"
        self.docker_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Cleanup after test"""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def create_test_config_file(self, filename: str, schedule_time: str = "04:00"):
        """Create a test configuration file"""
        config = {
            "pipeline": {"name": "Test Pipeline", "version": "2.0"},
            "schedule": {"download_time": schedule_time, "analysis_time": "01:00"},
        }

        config_file = self.config_dir / filename
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        return config_file

    def create_test_python_file(self, filename: str, schedule_time: str = "04:00"):
        """Create a test Python file with schedule"""
        content = f'''#!/usr/bin/env python3
"""Test auto downloader script"""

import schedule

def run_once():
    return True

def run_scheduled():
    # Schedule for {schedule_time} daily (test schedule)
    schedule.every().day.at("{schedule_time}").do(run_once)
    
    print("📅 Scheduled auto downloader for {schedule_time} daily")
    print("🔄 Waiting for scheduled time...")
'''

        if "utilities" in str(filename):
            python_file = self.tools_dir / filename
        else:
            python_file = self.docker_dir / filename

        with open(python_file, "w") as f:
            f.write(content)

        return python_file

    @patch("tools.cli.schedule_manager.ScheduleManager.__init__")
    def test_schedule_manager_initialization(self, mock_init):
        """Test ScheduleManager initialization"""
        mock_init.return_value = None
        manager = ScheduleManager()
        mock_init.assert_called_once()
        print("✅ ScheduleManager initialization test passed")

    def test_time_validation(self):
        """Test time format validation"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Valid time formats
        assert manager.validate_time("04:00") == "04:00"
        assert manager.validate_time("12:30") == "12:30"
        assert manager.validate_time("23:59") == "23:59"
        assert manager.validate_time("0:00") == "00:00"  # Should normalize

        # Invalid time formats
        with pytest.raises(ValueError):
            manager.validate_time("25:00")  # Invalid hour

        with pytest.raises(ValueError):
            manager.validate_time("12:60")  # Invalid minute

        with pytest.raises(ValueError):
            manager.validate_time("invalid")  # Invalid format

        print("✅ Time validation test passed")

    def test_config_file_discovery(self):
        """Test discovery of configuration files"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create test config files
        self.create_test_config_file("daily_pipeline_config.json")
        self.create_test_config_file("daily_pipeline_config_staging.json")

        config_files = manager.get_config_files()

        assert len(config_files) == 2
        assert any("daily_pipeline_config.json" in str(f) for f in config_files)
        assert any("daily_pipeline_config_staging.json" in str(f) for f in config_files)

        print("✅ Config file discovery test passed")

    def test_schedule_file_discovery(self):
        """Test discovery of Python schedule files"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create test Python files
        self.create_test_python_file("run_docker_auto_downloader.py")

        # Create daily pipeline orchestrator
        orchestrator_file = self.temp_path / "daily_pipeline_orchestrator.py"
        with open(orchestrator_file, "w") as f:
            f.write('# Test orchestrator file\n"download_time": "04:00"\n')

        schedule_files = manager.get_schedule_files()

        # Should find at least the orchestrator file
        assert len(schedule_files) >= 1

        print("✅ Schedule file discovery test passed")

    def test_get_current_schedules(self):
        """Test reading current schedules from files"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create test files with different schedules
        self.create_test_config_file("config1.json", "04:00")
        self.create_test_config_file("config2.json", "06:00")
        self.create_test_python_file("script1.py", "04:00")

        schedules = manager.get_current_schedules()

        assert len(schedules) >= 2  # At least the config files

        # Check if we got the expected schedule times
        schedule_times = list(schedules.values())
        assert "04:00" in schedule_times
        assert "06:00" in schedule_times

        print("✅ Get current schedules test passed")

    def test_update_json_config(self):
        """Test updating JSON configuration files"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create test config file
        config_file = self.create_test_config_file("test_config.json", "04:00")

        # Update the schedule
        success = manager.update_json_config(config_file, "06:30")
        assert success

        # Verify the update
        with open(config_file, "r") as f:
            updated_config = json.load(f)

        assert updated_config["schedule"]["download_time"] == "06:30"

        print("✅ JSON config update test passed")

    def test_update_python_file(self):
        """Test updating Python files with schedule"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create test Python file
        python_file = self.create_test_python_file("test_script.py", "04:00")

        # Update the schedule
        success = manager.update_python_file(python_file, "08:15")
        assert success

        # Verify the update
        with open(python_file, "r") as f:
            content = f.read()

        assert "08:15" in content
        assert 'schedule.every().day.at("08:15")' in content

        print("✅ Python file update test passed")

    @patch("subprocess.run")
    def test_container_operations(self, mock_subprocess):
        """Test Docker container operations"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Mock successful subprocess calls
        mock_subprocess.return_value.returncode = 0

        # Test container restart
        success = manager.restart_container()

        # Should have called docker commands
        assert mock_subprocess.call_count >= 3  # stop, rm, up

        print("✅ Container operations test passed")

    def test_cli_integration(self):
        """Test CLI integration with actual script"""
        # Test the CLI script exists and is executable
        script_path = (
            Path(__file__).parent.parent / "tools" / "cli" / "schedule_manager.py"
        )
        assert script_path.exists(), "CLI script not found"

        # Test help command
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                check=True,
            )
            assert "Auto-Downloader Schedule Manager" in result.stdout
            print("✅ CLI help command test passed")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"CLI help command failed: {e}")

    def test_schedule_consistency_check(self):
        """Test schedule consistency detection"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Create files with consistent schedules
        self.create_test_config_file("config1.json", "04:00")
        self.create_test_config_file("config2.json", "04:00")
        self.create_test_python_file("script1.py", "04:00")

        schedules = manager.get_current_schedules()

        # All schedules should be the same
        unique_times = set(schedules.values())
        assert len(unique_times) == 1
        assert "04:00" in unique_times

        print("✅ Schedule consistency check test passed")

    @patch("tools.cli.schedule_manager.ScheduleManager.restart_container")
    def test_full_schedule_update(self, mock_restart):
        """Test complete schedule update workflow"""
        manager = ScheduleManager()
        manager.project_root = self.temp_path

        # Mock container restart
        mock_restart.return_value = True

        # Create test files
        self.create_test_config_file("config.json", "04:00")
        self.create_test_python_file("script.py", "04:00")

        # Update schedule
        success = manager.update_schedule("07:45", restart=True)
        assert success

        # Verify updates
        schedules = manager.get_current_schedules()
        for schedule_time in schedules.values():
            assert schedule_time == "07:45"

        # Verify restart was called
        mock_restart.assert_called_once()

        print("✅ Full schedule update test passed")


def test_staging_pipeline_timing():
    """Test pipeline staging for race preparation timing"""
    print("\n🏁 Testing Pipeline Staging for Race Preparation")

    # Simulate race times and calculate staging
    race_times = [
        "13:30",  # First race at 1:30 PM
        "14:00",  # Second race at 2:00 PM
        "14:30",  # Third race at 2:30 PM
    ]

    def calculate_staging_time(first_race_time: str, prep_minutes: int = 15) -> str:
        """Calculate when pipeline should be ready"""
        from datetime import datetime, timedelta

        # Parse the race time
        hour, minute = map(int, first_race_time.split(":"))
        race_datetime = datetime.now().replace(hour=hour, minute=minute, second=0)

        # Subtract preparation time
        staging_datetime = race_datetime - timedelta(minutes=prep_minutes)

        return staging_datetime.strftime("%H:%M")

    first_race = race_times[0]
    staging_time = calculate_staging_time(first_race, 15)

    print(f"📅 First race: {first_race}")
    print(f"⏰ Pipeline staging time: {staging_time}")
    print(f"🎯 AI/ML models ready: 15 minutes before first race")

    # Verify staging time is 15 minutes before
    expected_staging = "13:15"  # 15 minutes before 13:30
    assert staging_time == expected_staging

    print("✅ Pipeline staging timing test passed")


def test_race_staging_manager_integration():
    """Test integration with the Race Staging Manager"""
    print("\n🚀 Testing Race Staging Manager Integration")

    try:
        # Import the staging manager
        import sys
        from pathlib import Path

        sys.path.append(str(Path.cwd()))
        from tools.pipeline.race_staging_manager import RaceStagingManager

        manager = RaceStagingManager()

        # Test race detection
        race_times = manager.detect_race_times()
        print(f"📊 Detected {len(race_times)} races for today")

        if race_times:
            # Test staging calculation
            first_race = race_times[0]
            staging_time = manager.calculate_staging_time(first_race, 15)

            print(f"🏁 First race: {first_race}")
            print(f"⏰ Staging time: {staging_time}")

            # Test status
            status = manager.get_status()
            assert "staging_status" in status
            assert "config" in status

            print("✅ Race Staging Manager integration test passed")
        else:
            print("⚠️ No races detected - staging manager available but no data")

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        assert False, "Failed to import Race Staging Manager"
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        assert False, f"Race Staging Manager integration failed: {e}"


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
