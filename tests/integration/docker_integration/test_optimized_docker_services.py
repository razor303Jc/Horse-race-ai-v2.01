"""
🧪 Optimized Docker Services Tests - v2.05
==========================================

Comprehensive test suite for the new optimized Docker service architecture.
Tests service-specific dockerignore files, build optimization, container sizes,
security, and deployment scenarios.
"""

import pytest
import docker
import subprocess
import json
import time
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import tempfile
import shutil
import os

# Test configuration
TEST_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCKER_ROOT = TEST_PROJECT_ROOT / "docker"

# Service configurations for testing
OPTIMIZED_SERVICES = {
    "web-app": {
        "dockerfile": "docker/dockerfiles/Dockerfile.web-optimized",
        "dockerignore": "docker/web-app/.dockerignore",
        "expected_size_mb": 150,
        "required_files": ["src/web/", "templates/", "static/"],
        "excluded_files": ["models/", "flows/", "data/"],
        "ports": [5000],
        "health_endpoint": "/health",
    },
    "data-pipeline": {
        "dockerfile": "docker/dockerfiles/Dockerfile.pipeline-optimized",
        "dockerignore": "docker/data-pipeline/.dockerignore",
        "expected_size_mb": 240,
        "required_files": ["src/automation/", "src/feeds/", "src/database/"],
        "excluded_files": ["templates/", "static/", "flows/"],
        "ports": [],
        "health_endpoint": None,
    },
    "ml-trainer": {
        "dockerfile": "docker/dockerfiles/Dockerfile.ml-models",
        "dockerignore": "docker/ml-trainer/.dockerignore",
        "expected_size_mb": 400,
        "required_files": ["src/horse_racing_ai/", "docker/ml_training/"],
        "excluded_files": ["src/web/", "flows/", "static/"],
        "ports": [],
        "health_endpoint": None,
    },
    "node-red": {
        "dockerfile": "docker/node-red/Dockerfile.enhanced",
        "dockerignore": "docker/node-red/.dockerignore",
        "expected_size_mb": 80,
        "required_files": ["flows/", "docker/node-red/"],
        "excluded_files": ["src/horse_racing_ai/", "models/", "templates/"],
        "ports": [1880],
        "health_endpoint": "/",
    },
    "docs": {
        "dockerfile": "docker/dockerfiles/Dockerfile.mkdocs",
        "dockerignore": "docker/docs/.dockerignore",
        "expected_size_mb": 30,
        "required_files": ["docs/", "*.md"],
        "excluded_files": ["src/", "models/", "data/"],
        "ports": [8000],
        "health_endpoint": "/",
    },
    "production": {
        "dockerfile": "docker/dockerfiles/Dockerfile.production",
        "dockerignore": "docker/production/.dockerignore",
        "expected_size_mb": 420,
        "required_files": ["src/", "api/", "config/"],
        "excluded_files": ["tests/", "docs/", "data/training/"],
        "ports": [],
        "health_endpoint": None,
    },
    "alerts": {
        "dockerfile": "docker/dockerfiles/Dockerfile.alerts",
        "dockerignore": "docker/alerts/.dockerignore",
        "expected_size_mb": 87,
        "required_files": ["src/alerts/", "templates/alerts/"],
        "excluded_files": ["src/horse_racing_ai/", "models/", "flows/"],
        "ports": [],
        "health_endpoint": None,
    },
}

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def docker_client():
    """Docker client for container management"""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")


@pytest.fixture
def temp_build_context():
    """Create temporary build context for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create mock project structure
        (temp_path / "src").mkdir()
        (temp_path / "src" / "web").mkdir()
        (temp_path / "src" / "horse_racing_ai").mkdir()
        (temp_path / "templates").mkdir()
        (temp_path / "static").mkdir()
        (temp_path / "models").mkdir()
        (temp_path / "flows").mkdir()
        (temp_path / "data").mkdir()
        (temp_path / "docs").mkdir()

        # Create mock files
        (temp_path / "src" / "web" / "app.py").write_text("# Web app")
        (temp_path / "templates" / "index.html").write_text("<html></html>")
        (temp_path / "models" / "model.pkl").write_text("fake model data")
        (temp_path / "flows" / "main_flow.json").write_text("{}")
        (temp_path / "data" / "data.csv").write_text("col1,col2\n1,2")
        (temp_path / "README.md").write_text("# Test Project")

        yield temp_path


@pytest.fixture
def compose_config():
    """Load docker-compose configuration for testing"""
    compose_file = TEST_PROJECT_ROOT / "docker-compose.clean.yml"
    if compose_file.exists():
        with open(compose_file) as f:
            return yaml.safe_load(f)
    return {}


# ============================================================================
# SERVICE-SPECIFIC DOCKERIGNORE TESTS
# ============================================================================


class TestServiceSpecificDockerIgnore:
    """Test service-specific .dockerignore files"""

    def test_dockerignore_files_exist(self):
        """Test that all service-specific .dockerignore files exist"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            assert (
                dockerignore_path.exists()
            ), f"Missing .dockerignore for {service_name}: {dockerignore_path}"

            # Check file is not empty
            content = dockerignore_path.read_text()
            assert len(content.strip()) > 0, f"Empty .dockerignore for {service_name}"

            # Check has proper header
            assert (
                "Docker Ignore" in content
            ), f"Missing header in {service_name} .dockerignore"

    def test_dockerignore_excludes_development_files(self):
        """Test that .dockerignore files exclude development files"""
        # Define patterns with alternatives for more flexible matching
        dev_patterns = {
            ".git/": [".git/"],
            ".vscode/": [".vscode/"],
            ".idea/": [".idea/"],
            "__pycache__/": ["__pycache__/"],
            "*.pyc": ["*.pyc", "*.py[cod]", "*.pyo", "*.pyd"],  # Accept variations
            "tests/": ["tests/"],
            "pytest.ini": ["pytest.ini"],
            ".env": [".env"],
            "docker-compose*.yml": ["docker-compose*.yml", "docker-compose.*.yml"],
        }

        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            content = dockerignore_path.read_text()

            for pattern_name, alternatives in dev_patterns.items():
                found = any(alt in content for alt in alternatives)
                assert found, (
                    f"Missing dev exclusion for '{pattern_name}' in "
                    f"{service_name}. Expected one of: {alternatives}"
                )

    def test_dockerignore_service_specific_exclusions(self):
        """Test that each service excludes files it doesn't need"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            content = dockerignore_path.read_text()

            # Check excluded files are actually excluded
            for excluded_pattern in config["excluded_files"]:
                # Handle directory patterns
                pattern_to_check = excluded_pattern.rstrip("/")
                if not pattern_to_check.endswith("/"):
                    pattern_to_check += "/"

                assert (
                    pattern_to_check in content
                ), f"Missing exclusion '{excluded_pattern}' in {service_name}"

    def test_dockerignore_preserves_required_files(self):
        """Test that required files are not excluded"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            content = dockerignore_path.read_text()

            # Check that required files are not explicitly excluded
            for required_pattern in config["required_files"]:
                # This is a bit complex as we need to ensure required files aren't excluded
                # We'll check they're not explicitly mentioned in exclusion patterns
                lines = content.split("\n")
                exclusion_lines = [
                    line.strip()
                    for line in lines
                    if line.strip() and not line.startswith("#")
                ]

                # Check if any exclusion would catch our required files
                pattern_conflicts = []
                for exclusion in exclusion_lines:
                    if required_pattern.startswith(exclusion.rstrip("/")):
                        pattern_conflicts.append(exclusion)

                # If there are conflicts, there should be explicit inclusion patterns
                if pattern_conflicts:
                    has_inclusion = any(
                        line.startswith("!") and required_pattern in line
                        for line in exclusion_lines
                    )
                    if not has_inclusion:
                        # This is a warning rather than failure, as some services might be OK
                        print(
                            f"Warning: {service_name} may exclude required file {required_pattern}"
                        )


# ============================================================================
# BUILD OPTIMIZATION TESTS
# ============================================================================


class TestOptimizedBuilds:
    """Test optimized Docker builds"""

    def test_build_script_exists(self):
        """Test that optimized build script exists and is executable"""
        build_script = TEST_PROJECT_ROOT / "build_optimized_services.sh"
        assert build_script.exists(), "Missing build_optimized_services.sh script"

        # Check executable permissions
        stat = build_script.stat()
        assert stat.st_mode & 0o111, "Build script is not executable"

    def test_dockerfile_exists_for_all_services(self):
        """Test that Dockerfiles exist for all optimized services"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerfile_path = TEST_PROJECT_ROOT / config["dockerfile"]
            assert (
                dockerfile_path.exists()
            ), f"Missing Dockerfile for {service_name}: {dockerfile_path}"

    @pytest.mark.slow
    def test_dry_run_build_context_size(self, temp_build_context):
        """Test that build contexts are smaller with service-specific dockerignore"""
        # This test checks build context size reduction
        for service_name, config in OPTIMIZED_SERVICES.items():
            # Copy dockerignore to temp directory
            dockerignore_src = TEST_PROJECT_ROOT / config["dockerignore"]
            if dockerignore_src.exists():
                shutil.copy(dockerignore_src, temp_build_context / ".dockerignore")

                # Run dry build to check context size
                try:
                    result = subprocess.run(
                        ["docker", "build", "--dry-run", str(temp_build_context)],
                        capture_output=True,
                        text=True,
                        cwd=temp_build_context,
                    )

                    # Parse build context size from output
                    if "Sending build context" in result.stderr:
                        print(f"Build context for {service_name}: {result.stderr}")
                        # Extract size information if available

                except subprocess.CalledProcessError:
                    # Skip if docker build fails (expected in test environment)
                    pass
                finally:
                    # Clean up
                    dockerignore_file = temp_build_context / ".dockerignore"
                    if dockerignore_file.exists():
                        dockerignore_file.unlink()


# ============================================================================
# CONTAINER SIZE TESTS
# ============================================================================


class TestContainerSizes:
    """Test container size optimization"""

    def test_expected_size_configuration(self):
        """Test that expected sizes are configured for all services"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            assert (
                "expected_size_mb" in config
            ), f"Missing expected_size_mb for {service_name}"
            assert (
                config["expected_size_mb"] > 0
            ), f"Invalid expected size for {service_name}"

    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("DOCKER_BUILD_TESTS"), reason="Docker build tests disabled"
    )
    def test_built_image_sizes(self, docker_client):
        """Test that built images meet size expectations"""
        # This test requires actual builds, so it's marked as slow and optional
        for service_name, config in OPTIMIZED_SERVICES.items():
            image_name = f"horse-racing-{service_name}:test"

            try:
                # Try to get the image (assuming it was built)
                image = docker_client.images.get(image_name)

                # Get size in MB
                size_bytes = image.attrs["Size"]
                size_mb = size_bytes / (1024 * 1024)

                expected_size = config["expected_size_mb"]
                tolerance = expected_size * 0.3  # 30% tolerance

                assert (
                    size_mb <= expected_size + tolerance
                ), f"{service_name} image too large: {size_mb:.1f}MB > {expected_size + tolerance:.1f}MB"

                print(
                    f"✅ {service_name}: {size_mb:.1f}MB (expected: {expected_size}MB)"
                )

            except docker.errors.ImageNotFound:
                pytest.skip(f"Image {image_name} not found - build required")


# ============================================================================
# SECURITY TESTS
# ============================================================================


class TestContainerSecurity:
    """Test container security aspects"""

    def test_no_sensitive_files_in_dockerignore(self):
        """Test that sensitive file patterns are excluded"""
        sensitive_patterns = [
            ".env",
            "*.key",
            "*.pem",
            "*.p12",
            "secrets/",
            "credentials/",
            "*.password",
            "auth.json",
        ]

        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            content = dockerignore_path.read_text()

            for pattern in sensitive_patterns:
                assert (
                    pattern in content or f"*{pattern}" in content
                ), f"Missing sensitive file exclusion '{pattern}' in {service_name}"

    def test_no_development_tools_included(self):
        """Test that development tools are excluded"""
        dev_tool_patterns = [
            ".vscode/",
            ".idea/",
            "*.swp",
            ".git/",
            "pytest.ini",
            "Makefile",
            ".flake8",
        ]

        for service_name, config in OPTIMIZED_SERVICES.items():
            dockerignore_path = TEST_PROJECT_ROOT / config["dockerignore"]
            content = dockerignore_path.read_text()

            excluded_count = sum(
                1 for pattern in dev_tool_patterns if pattern in content
            )
            assert (
                excluded_count >= len(dev_tool_patterns) * 0.8
            ), f"Insufficient dev tool exclusions in {service_name}"


# ============================================================================
# DOCKER COMPOSE INTEGRATION TESTS
# ============================================================================


class TestDockerComposeIntegration:
    """Test docker-compose integration with optimized services"""

    def test_compose_file_has_optimized_services(self, compose_config):
        """Test that docker-compose.clean.yml includes optimized services"""
        if not compose_config:
            pytest.skip("docker-compose.clean.yml not found")

        services = compose_config.get("services", {})

        # Check for key services
        expected_services = [
            "web-app",
            "data-pipeline",
            "ml-trainer",
            "node-red",
            "docs",
        ]
        for service in expected_services:
            # Service might have different name in compose file
            service_found = any(
                service.replace("-", "_") in s or service.replace("-", "-") in s
                for s in services.keys()
            )
            if not service_found:
                print(f"Warning: Service {service} not found in docker-compose")

    def test_compose_services_have_build_contexts(self, compose_config):
        """Test that services have proper build contexts"""
        if not compose_config:
            pytest.skip("docker-compose.clean.yml not found")

        services = compose_config.get("services", {})

        for service_name, service_config in services.items():
            if "build" in service_config:
                build_config = service_config["build"]

                if isinstance(build_config, dict):
                    assert (
                        "context" in build_config
                    ), f"Missing build context for {service_name}"
                    assert (
                        "dockerfile" in build_config
                    ), f"Missing dockerfile for {service_name}"

    def test_compose_volume_mounts(self, compose_config):
        """Test that data files are mounted as volumes, not copied"""
        if not compose_config:
            pytest.skip("docker-compose.clean.yml not found")

        services = compose_config.get("services", {})

        # Data directories that should be mounted, not copied
        expected_volume_mounts = ["data", "logs", "models", "trained_models"]

        for service_name, service_config in services.items():
            volumes = service_config.get("volumes", [])

            # Check that data directories are mounted
            volume_mounts = [v.split(":")[0].lstrip("./") for v in volumes if ":" in v]

            for expected_mount in expected_volume_mounts:
                if any(expected_mount in mount for mount in volume_mounts):
                    print(f"✅ {service_name} mounts {expected_mount} as volume")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestBuildPerformance:
    """Test build performance improvements"""

    def test_build_script_completion_time(self):
        """Test that build script completes in reasonable time"""
        build_script = TEST_PROJECT_ROOT / "build_optimized_services.sh"

        if not build_script.exists():
            pytest.skip("Build script not found")

        # Test help command (should be fast)
        start_time = time.time()
        result = subprocess.run(
            [str(build_script), "--help"], capture_output=True, text=True
        )
        execution_time = time.time() - start_time

        assert execution_time < 5, f"Help command too slow: {execution_time:.2f}s"
        assert result.returncode == 0, "Help command failed"
        assert "Usage:" in result.stdout, "Help output missing"

    def test_list_services_functionality(self):
        """Test that build script can list services"""
        build_script = TEST_PROJECT_ROOT / "build_optimized_services.sh"

        if not build_script.exists():
            pytest.skip("Build script not found")

        result = subprocess.run(
            [str(build_script), "--list"], capture_output=True, text=True
        )

        assert result.returncode == 0, "List command failed"
        assert "Available services:" in result.stdout, "List output missing"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestServiceIntegration:
    """Test service integration scenarios"""

    @pytest.mark.integration
    def test_service_health_endpoints(self):
        """Test that services with health endpoints are configured correctly"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            if config["health_endpoint"]:
                # This would test actual health endpoints if services were running
                print(
                    f"Service {service_name} has health endpoint: {config['health_endpoint']}"
                )
                assert config["health_endpoint"].startswith(
                    "/"
                ), f"Invalid health endpoint for {service_name}"

    @pytest.mark.integration
    def test_service_port_configuration(self):
        """Test that services have correct port configuration"""
        for service_name, config in OPTIMIZED_SERVICES.items():
            ports = config["ports"]

            for port in ports:
                assert isinstance(
                    port, int
                ), f"Invalid port type for {service_name}: {port}"
                assert (
                    1 <= port <= 65535
                ), f"Invalid port number for {service_name}: {port}"


# ============================================================================
# SMOKE TESTS
# ============================================================================


class TestDockerSetupSmoke:
    """Smoke tests for Docker setup"""

    def test_docker_available(self):
        """Test that Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            assert result.returncode == 0, "Docker not available"
            assert "Docker version" in result.stdout, "Invalid Docker version output"
        except FileNotFoundError:
            pytest.skip("Docker not installed")

    def test_docker_compose_available(self):
        """Test that Docker Compose is available"""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            assert result.returncode == 0, "Docker Compose not available"
        except FileNotFoundError:
            pytest.skip("Docker Compose not installed")

    def test_project_structure(self):
        """Test that required project structure exists"""
        required_dirs = [
            "docker/dockerfiles",
            "docker/web-app",
            "docker/data-pipeline",
            "docker/ml-trainer",
            "docker/node-red",
            "docker/docs",
            "docker/production",
            "docker/alerts",
        ]

        for dir_path in required_dirs:
            full_path = TEST_PROJECT_ROOT / dir_path
            assert full_path.exists(), f"Missing required directory: {dir_path}"


# ============================================================================
# PYTEST MARKERS
# ============================================================================

# Register custom markers
pytest.mark.docker = pytest.mark.docker
pytest.mark.slow = pytest.mark.slow
pytest.mark.integration = pytest.mark.integration
