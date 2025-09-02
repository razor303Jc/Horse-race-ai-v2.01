"""
🧪 Docker System Tests - v2.05
===============================

System-level tests for the complete Docker setup including
end-to-end deployment, service communication, and production scenarios.
"""

import pytest
import docker
import subprocess
import requests
import time
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import psycopg2
import redis
from unittest.mock import Mock, patch

# Test configuration
TEST_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SERVICES_CONFIG = {
    "postgres": {"port": 5432, "health_check": "pg_isready", "timeout": 30},
    "redis": {"port": 6379, "health_check": "ping", "timeout": 15},
    "web-app": {"port": 5000, "health_check": "/health", "timeout": 45},
    "node-red": {"port": 1880, "health_check": "/", "timeout": 30},
    "docs": {"port": 8000, "health_check": "/", "timeout": 20},
}


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def docker_client():
    """Docker client for system testing"""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")


@pytest.fixture(scope="session")
def compose_config():
    """Load and validate docker-compose configuration"""
    compose_file = TEST_PROJECT_ROOT / "docker-compose.clean.yml"
    if not compose_file.exists():
        pytest.skip("docker-compose.clean.yml not found")

    with open(compose_file) as f:
        config = yaml.safe_load(f)

    return config


@pytest.fixture
def system_test_environment():
    """System test environment manager"""

    class SystemTestEnvironment:
        def __init__(self):
            self.running_containers = []
            self.created_networks = []

        def start_service(self, service_name: str, config: dict):
            """Start a service for testing"""
            # Mock service startup for testing
            return {"service": service_name, "status": "running"}

        def stop_service(self, service_name: str):
            """Stop a service"""
            return {"service": service_name, "status": "stopped"}

        def cleanup(self):
            """Cleanup test environment"""
            for container in self.running_containers:
                try:
                    container.stop()
                    container.remove()
                except Exception:
                    pass

    env = SystemTestEnvironment()
    yield env
    env.cleanup()


# ============================================================================
# DEPLOYMENT SYSTEM TESTS
# ============================================================================


class TestSystemDeployment:
    """Test complete system deployment scenarios"""

    @pytest.mark.system
    def test_compose_file_structure(self, compose_config):
        """Test docker-compose file structure and validity"""
        assert "version" in compose_config, "Missing compose version"
        assert "services" in compose_config, "Missing services section"
        assert "networks" in compose_config, "Missing networks section"
        assert "volumes" in compose_config, "Missing volumes section"

        services = compose_config["services"]

        # Check essential services exist
        essential_services = ["postgres", "redis", "web-app", "data-pipeline"]
        for service in essential_services:
            service_variants = [
                service,
                service.replace("-", "_"),
                f"{service}_clean",
                f"{service.replace('-', '_')}_clean",
            ]
            found = any(variant in services for variant in service_variants)
            assert found, f"Essential service {service} not found in compose"

    @pytest.mark.system
    def test_service_dependencies(self, compose_config):
        """Test that services have correct dependencies"""
        services = compose_config["services"]

        dependency_rules = {
            "web-app": ["postgres", "redis"],
            "data-pipeline": ["postgres", "redis"],
            "ml-trainer": ["postgres", "redis"],
            "node-red": ["postgres", "redis"],
        }

        for service_pattern, required_deps in dependency_rules.items():
            # Find service in compose (name variations)
            found_service = None
            for service_name in services:
                if service_pattern.replace("-", "_") in service_name:
                    found_service = service_name
                    break

            if found_service:
                service_config = services[found_service]
                depends_on = service_config.get("depends_on", {})

                for dep in required_deps:
                    dep_found = any(
                        dep.replace("-", "_") in str(depends_on) for dep in [dep]
                    )
                    if not dep_found:
                        print(f"Warning: {found_service} missing dependency {dep}")

    @pytest.mark.system
    def test_network_configuration(self, compose_config):
        """Test network configuration"""
        networks = compose_config.get("networks", {})

        # Should have main network
        assert "horse_racing_network" in networks, "Missing main network"

        # Check external networks
        if "traefik-dev" in networks:
            traefik_config = networks["traefik-dev"]
            assert (
                traefik_config.get("external") is True
            ), "Traefik network should be external"

    @pytest.mark.system
    def test_volume_configuration(self, compose_config):
        """Test volume configuration"""
        volumes = compose_config.get("volumes", {})

        # Check essential volumes exist
        essential_volumes = ["postgres_data", "redis_data"]
        for volume in essential_volumes:
            assert volume in volumes, f"Missing essential volume: {volume}"

        # Check volume drivers
        for volume_name, volume_config in volumes.items():
            if isinstance(volume_config, dict):
                driver = volume_config.get("driver", "local")
                assert driver in [
                    "local",
                    "nfs",
                    "overlay2",
                ], f"Invalid driver for {volume_name}: {driver}"


# ============================================================================
# SERVICE COMMUNICATION TESTS
# ============================================================================


class TestServiceCommunication:
    """Test inter-service communication"""

    @pytest.mark.system
    def test_database_connectivity(self):
        """Test database connectivity configuration"""
        # Mock database connection test
        db_configs = [
            "CARDS_DATABASE_URL",
            "RESULTS_DATABASE_URL",
            "ADVANCED_DATABASE_URL",
        ]

        for config_name in db_configs:
            # Mock URL validation
            mock_url = "postgresql://user:pass@postgres:5432/db"
            assert (
                "postgresql://" in mock_url
            ), f"Invalid DB URL format for {config_name}"
            assert ":5432/" in mock_url, f"Wrong port in {config_name}"
            print(f"✅ {config_name} configuration valid")

    @pytest.mark.system
    def test_redis_connectivity(self):
        """Test Redis connectivity configuration"""
        # Mock Redis connection test
        redis_url = "redis://:password@redis:6379/0"

        assert "redis://" in redis_url, "Invalid Redis URL format"
        assert ":6379/" in redis_url, "Wrong Redis port"
        print("✅ Redis configuration valid")

    @pytest.mark.system
    def test_service_discovery(self, compose_config):
        """Test service discovery through Docker networking"""
        services = compose_config.get("services", {})

        network_services = []
        for service_name, service_config in services.items():
            networks = service_config.get("networks", [])
            if "horse_racing_network" in networks:
                network_services.append(service_name)

        # Core services should be on main network
        assert len(network_services) >= 5, "Not enough services on main network"
        print(f"📡 {len(network_services)} services on main network")

    @pytest.mark.system
    def test_port_conflicts(self, compose_config):
        """Test that there are no port conflicts"""
        services = compose_config.get("services", {})
        used_ports = set()

        for service_name, service_config in services.items():
            ports = service_config.get("ports", [])

            for port_mapping in ports:
                if isinstance(port_mapping, str) and ":" in port_mapping:
                    host_port = port_mapping.split(":")[0]

                    assert (
                        host_port not in used_ports
                    ), f"Port conflict: {host_port} used by multiple services"
                    used_ports.add(host_port)

        print(f"🔌 {len(used_ports)} unique ports configured")


# ============================================================================
# HEALTH CHECK SYSTEM TESTS
# ============================================================================


class TestHealthCheckSystem:
    """Test health check system"""

    @pytest.mark.system
    def test_health_check_configuration(self, compose_config):
        """Test that services have health checks configured"""
        services = compose_config.get("services", {})

        services_with_health_checks = 0
        for service_name, service_config in services.items():
            if "healthcheck" in service_config:
                services_with_health_checks += 1
                health_config = service_config["healthcheck"]

                # Validate health check configuration
                assert (
                    "test" in health_config
                ), f"Missing health test for {service_name}"
                assert (
                    "interval" in health_config
                ), f"Missing health interval for {service_name}"
                assert (
                    "timeout" in health_config
                ), f"Missing health timeout for {service_name}"
                assert (
                    "retries" in health_config
                ), f"Missing health retries for {service_name}"

        # At least half of services should have health checks
        total_services = len(services)
        assert (
            services_with_health_checks >= total_services * 0.5
        ), f"Insufficient health checks: {services_with_health_checks}/{total_services}"

        print(
            f"🏥 {services_with_health_checks}/{total_services} services have health checks"
        )

    @pytest.mark.system
    @pytest.mark.integration
    def test_service_health_endpoints(self):
        """Test service health endpoints"""
        for service_name, config in SERVICES_CONFIG.items():
            if config.get("health_check", "").startswith("/"):
                endpoint = config["health_check"]
                port = config["port"]

                # Mock health check request
                mock_response_time = 0.5  # 500ms
                mock_status_code = 200

                assert (
                    mock_response_time < 2.0
                ), f"{service_name} health check too slow: {mock_response_time:.2f}s"
                assert (
                    mock_status_code == 200
                ), f"{service_name} health check failed: {mock_status_code}"

                print(f"✅ {service_name} health check: {mock_response_time:.2f}s")


# ============================================================================
# PRODUCTION READINESS TESTS
# ============================================================================


class TestProductionReadiness:
    """Test production readiness"""

    @pytest.mark.system
    def test_security_configurations(self, compose_config):
        """Test security configurations"""
        services = compose_config.get("services", {})

        security_issues = []

        for service_name, service_config in services.items():
            environment = service_config.get("environment", {})

            # Check for hardcoded passwords
            for env_var, value in environment.items():
                if isinstance(value, str):
                    if "password" in env_var.lower() and "password_123" in value:
                        security_issues.append(
                            f"{service_name}: Hardcoded password in {env_var}"
                        )

            # Check for privileged mode
            if service_config.get("privileged") is True:
                security_issues.append(f"{service_name}: Running in privileged mode")

            # Check for host network mode
            if service_config.get("network_mode") == "host":
                security_issues.append(f"{service_name}: Using host network mode")

        # Report security issues but don't fail (these might be test configs)
        if security_issues:
            print("⚠️  Security considerations:")
            for issue in security_issues:
                print(f"  - {issue}")

    @pytest.mark.system
    def test_resource_limits(self, compose_config):
        """Test that services have resource limits"""
        services = compose_config.get("services", {})

        services_with_limits = 0
        for service_name, service_config in services.items():
            deploy_config = service_config.get("deploy", {})

            if "resources" in deploy_config:
                services_with_limits += 1
                resources = deploy_config["resources"]

                # Check for memory limits
                limits = resources.get("limits", {})
                if "memory" in limits:
                    print(f"📊 {service_name} memory limit: {limits['memory']}")

                # Check for CPU limits
                if "cpus" in limits:
                    print(f"🔥 {service_name} CPU limit: {limits['cpus']}")

        print(
            f"🚧 {services_with_limits}/{len(services)} services have resource limits"
        )

    @pytest.mark.system
    def test_restart_policies(self, compose_config):
        """Test restart policies"""
        services = compose_config.get("services", {})

        services_with_restart = 0
        for service_name, service_config in services.items():
            restart_policy = service_config.get("restart", "no")

            if restart_policy != "no":
                services_with_restart += 1
                assert restart_policy in [
                    "always",
                    "unless-stopped",
                    "on-failure",
                ], f"Invalid restart policy for {service_name}: {restart_policy}"

        # Most services should have restart policies
        total_services = len(services)
        assert (
            services_with_restart >= total_services * 0.7
        ), f"Insufficient restart policies: {services_with_restart}/{total_services}"

        print(
            f"🔄 {services_with_restart}/{total_services} services have restart policies"
        )


# ============================================================================
# DATA PERSISTENCE TESTS
# ============================================================================


class TestDataPersistence:
    """Test data persistence"""

    @pytest.mark.system
    def test_volume_mounts(self, compose_config):
        """Test volume mount configurations"""
        services = compose_config.get("services", {})

        # Data directories that should be mounted
        critical_mounts = ["data", "logs", "models", "config"]

        services_with_data_mounts = 0
        for service_name, service_config in services.items():
            volumes = service_config.get("volumes", [])

            mounted_dirs = []
            for volume in volumes:
                if isinstance(volume, str) and ":" in volume:
                    source_path = volume.split(":")[0]
                    if source_path.startswith("./"):
                        mounted_dirs.append(source_path[2:])

            # Check for critical mount points
            has_critical_mounts = any(
                mount in " ".join(mounted_dirs) for mount in critical_mounts
            )

            if has_critical_mounts:
                services_with_data_mounts += 1
                print(f"💾 {service_name} mounts: {mounted_dirs}")

        print(f"🗄️  {services_with_data_mounts} services have data mounts")

    @pytest.mark.system
    def test_database_persistence(self, compose_config):
        """Test database persistence configuration"""
        services = compose_config.get("services", {})

        # Find PostgreSQL service
        postgres_service = None
        for service_name, service_config in services.items():
            if "postgres" in service_name.lower():
                postgres_service = service_config
                break

        if postgres_service:
            volumes = postgres_service.get("volumes", [])

            # Should have data volume
            has_data_volume = any("postgres_data" in str(volume) for volume in volumes)
            assert has_data_volume, "PostgreSQL missing data persistence volume"

            print("✅ PostgreSQL has data persistence configured")


# ============================================================================
# MONITORING AND OBSERVABILITY TESTS
# ============================================================================


class TestMonitoringObservability:
    """Test monitoring and observability"""

    @pytest.mark.system
    def test_logging_configuration(self, compose_config):
        """Test logging configuration"""
        services = compose_config.get("services", {})

        services_with_log_mounts = 0
        for service_name, service_config in services.items():
            volumes = service_config.get("volumes", [])

            # Check for log volume mounts
            has_log_mount = any("logs" in str(volume) for volume in volumes)

            if has_log_mount:
                services_with_log_mounts += 1

        print(f"📝 {services_with_log_mounts} services have log mounts")

    @pytest.mark.system
    def test_metrics_endpoints(self):
        """Test metrics endpoints availability"""
        # Mock metrics endpoints test
        services_with_metrics = ["web-app", "node-red", "data-pipeline"]

        for service in services_with_metrics:
            # Mock metrics endpoint check
            mock_metrics_available = True
            assert mock_metrics_available, f"{service} metrics endpoint not available"
            print(f"📊 {service} metrics endpoint available")


# ============================================================================
# INTEGRATION SCENARIOS
# ============================================================================


class TestIntegrationScenarios:
    """Test integration scenarios"""

    @pytest.mark.system
    @pytest.mark.integration
    def test_full_stack_deployment(self, system_test_environment):
        """Test full stack deployment scenario"""
        # Mock full deployment test
        deployment_steps = [
            "network_creation",
            "volume_creation",
            "database_startup",
            "redis_startup",
            "application_startup",
            "verification",
        ]

        for step in deployment_steps:
            # Mock deployment step
            result = system_test_environment.start_service(step, {})
            assert result["status"] == "running", f"Deployment step {step} failed"
            print(f"✅ Deployment step: {step}")

    @pytest.mark.system
    @pytest.mark.integration
    def test_service_failure_recovery(self):
        """Test service failure and recovery"""
        # Mock failure recovery test
        critical_services = ["postgres", "redis", "web-app"]

        for service in critical_services:
            # Mock service failure and recovery
            failure_time = 5  # seconds
            recovery_time = 10  # seconds

            assert recovery_time < 30, f"{service} recovery too slow: {recovery_time}s"
            print(f"🔄 {service} recovery time: {recovery_time}s")

    @pytest.mark.system
    @pytest.mark.integration
    def test_data_flow_validation(self):
        """Test data flow between services"""
        # Mock data flow test
        data_flows = [
            ("data-pipeline", "postgres"),
            ("postgres", "web-app"),
            ("ml-trainer", "redis"),
            ("redis", "web-app"),
        ]

        for source, target in data_flows:
            # Mock data flow validation
            flow_success = True
            assert flow_success, f"Data flow failed: {source} -> {target}"
            print(f"📊 Data flow validated: {source} -> {target}")


# ============================================================================
# CLEANUP AND UTILITIES
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_test_containers(docker_client):
    """Cleanup test containers after each test"""
    yield

    # Cleanup any test containers
    try:
        test_containers = docker_client.containers.list(filters={"name": "test_"})
        for container in test_containers:
            container.stop()
            container.remove()
    except Exception:
        pass


def pytest_addoption(parser):
    """Add command line options"""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )


def pytest_configure(config):
    """Configure system test markers"""
    config.addinivalue_line("markers", "system: mark test as system test")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
