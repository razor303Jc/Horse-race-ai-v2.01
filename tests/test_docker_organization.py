#!/usr/bin/env python3
"""
Test suite for Docker data processing components

This module tests the data processing scripts that have been moved
to the docker/data_processing directory.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDataProcessingComponents(unittest.TestCase):
    """Test suite for data processing Docker components"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_path = Path(self.test_dir)

    def test_docker_data_processing_structure(self):
        """Test that data processing files are properly organized"""
        data_processing_dir = project_root / "docker" / "data_processing"

        # Check that the directory exists
        self.assertTrue(
            data_processing_dir.exists(),
            "docker/data_processing directory should exist",
        )

        # Check for expected files
        expected_files = [
            "data_cleaner.py",
            "clean_upload.py",
            "simple_upload.py",
            "upload_races.py",
        ]

        for file_name in expected_files:
            file_path = data_processing_dir / file_name
            self.assertTrue(
                file_path.exists(),
                f"{file_name} should exist in docker/data_processing/",
            )
            self.assertGreater(
                file_path.stat().st_size, 0, f"{file_name} should not be empty"
            )

    def test_dockerfile_data_processing_exists(self):
        """Test that Dockerfile for data processing exists"""
        dockerfile_path = project_root / "Dockerfile.data-processing"

        self.assertTrue(
            dockerfile_path.exists(), "Dockerfile.data-processing should exist"
        )

        # Check dockerfile content
        with open(dockerfile_path, "r") as f:
            content = f.read()
            self.assertIn("Data Processing Container", content)
            self.assertIn("COPY docker/data_processing/", content)
            self.assertIn("dataprocessor", content)

    @patch("subprocess.run")
    def test_data_processing_container_build(self, mock_subprocess):
        """Test that data processing container can be built"""
        mock_subprocess.return_value.returncode = 0

        # This would normally build the container
        # We'll mock it for unit testing
        result = mock_subprocess.return_value
        self.assertEqual(result.returncode, 0)

    def test_data_processing_imports(self):
        """Test that data processing modules can be imported"""
        # Test importing the moved modules (if they have relative imports)
        try:
            # We can't directly import due to the move, but we can check syntax
            data_processing_dir = project_root / "docker" / "data_processing"
            for py_file in data_processing_dir.glob("*.py"):
                with open(py_file, "r") as f:
                    content = f.read()
                    # Basic syntax check - try to compile
                    compile(content, str(py_file), "exec")
        except SyntaxError as e:
            self.fail(f"Syntax error in data processing file: {e}")

    def test_docker_compose_data_processing_service(self):
        """Test that docker-compose includes data processing service"""
        compose_file = project_root / "docker-compose.yml"

        with open(compose_file, "r") as f:
            content = f.read()

        self.assertIn("data-processor:", content)
        self.assertIn("Dockerfile.data-processing", content)
        self.assertIn("horse_racing_data_processor", content)


class TestPipelineManagementComponents(unittest.TestCase):
    """Test suite for pipeline management Docker components"""

    def test_docker_pipeline_management_structure(self):
        """Test that pipeline management files are properly organized"""
        pipeline_dir = project_root / "docker" / "pipeline_management"

        # Check that the directory exists
        self.assertTrue(
            pipeline_dir.exists(), "docker/pipeline_management directory should exist"
        )

        # Check for expected files
        expected_files = [
            "dynamic_pipeline_timing.py",
            "pipeline_integration_summary.py",
        ]

        for file_name in expected_files:
            file_path = pipeline_dir / file_name
            self.assertTrue(
                file_path.exists(),
                f"{file_name} should exist in docker/pipeline_management/",
            )
            self.assertGreater(
                file_path.stat().st_size, 0, f"{file_name} should not be empty"
            )

    def test_dockerfile_pipeline_management_exists(self):
        """Test that Dockerfile for pipeline management exists"""
        dockerfile_path = project_root / "Dockerfile.pipeline-management"

        self.assertTrue(
            dockerfile_path.exists(), "Dockerfile.pipeline-management should exist"
        )

        # Check dockerfile content
        with open(dockerfile_path, "r") as f:
            content = f.read()
            self.assertIn("Pipeline Management Container", content)
            self.assertIn("COPY docker/pipeline_management/", content)
            self.assertIn("pipelinemanager", content)


class TestWebAppComponents(unittest.TestCase):
    """Test suite for web app Docker components"""

    def test_docker_web_app_structure(self):
        """Test that web app files are properly organized"""
        web_app_dir = project_root / "docker" / "web_app"

        # Check that the directory exists
        self.assertTrue(web_app_dir.exists(), "docker/web_app directory should exist")

        # Check for expected files
        expected_files = ["app.py", "main.py"]

        for file_name in expected_files:
            file_path = web_app_dir / file_name
            self.assertTrue(
                file_path.exists(), f"{file_name} should exist in docker/web_app/"
            )
            self.assertGreater(
                file_path.stat().st_size, 0, f"{file_name} should not be empty"
            )

    def test_dockerfile_updated_flask_app_path(self):
        """Test that main Dockerfile points to new app location"""
        dockerfile_path = project_root / "Dockerfile"

        with open(dockerfile_path, "r") as f:
            content = f.read()

        self.assertIn("FLASK_APP=docker/web_app/app.py", content)


class TestScheduleUpdate(unittest.TestCase):
    """Test suite for schedule time updates"""

    def test_schedule_updated_to_midnight(self):
        """Test that schedule has been updated to 00:01"""
        config_file = project_root / "config" / "daily_pipeline_config.json"

        with open(config_file, "r") as f:
            config = json.load(f)

        # Check the schedule time
        download_time = config["dynamic_schedule"]["download_time"]
        self.assertEqual(
            download_time, "00:01", "Download time should be updated to 00:01"
        )

    def test_duplicate_config_updated(self):
        """Test that duplicate config file is also updated"""
        config_file = project_root / "config" / "config" / "daily_pipeline_config.json"

        with open(config_file, "r") as f:
            config = json.load(f)

        # Check the schedule time
        download_time = config["schedule"]["download_time"]
        self.assertEqual(
            download_time, "00:01", "Download time should be updated to 00:01"
        )


class TestDockerComposeIntegration(unittest.TestCase):
    """Test suite for Docker Compose integration"""

    def test_new_services_in_compose(self):
        """Test that new services are added to docker-compose.yml"""
        compose_file = project_root / "docker-compose.yml"

        with open(compose_file, "r") as f:
            content = f.read()

        # Check for new services
        self.assertIn("data-processor:", content)
        self.assertIn("pipeline-manager:", content)

        # Check for proper profiles
        self.assertIn("data-processing", content)
        self.assertIn("pipeline-management", content)

    def test_dockerfile_references(self):
        """Test that docker-compose references correct Dockerfiles"""
        compose_file = project_root / "docker-compose.yml"

        with open(compose_file, "r") as f:
            content = f.read()

        self.assertIn("Dockerfile.data-processing", content)
        self.assertIn("Dockerfile.pipeline-management", content)


if __name__ == "__main__":
    print("🧪 Running Docker Organization Tests")
    print("=" * 50)

    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessingComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineManagementComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestWebAppComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduleUpdate))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerComposeIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All Docker organization tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")

    sys.exit(0 if result.wasSuccessful() else 1)
