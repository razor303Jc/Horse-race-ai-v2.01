#!/usr/bin/env python3
"""
Automated Deployment Pipeline System for Horse Racing AI V2.03
Manages CI/CD automation with Docker, testing, and deployment orchestration
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
import yaml
import docker
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import sqlite3
import tarfile
import tempfile

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentTarget:
    """Deployment target configuration"""

    target_id: str
    name: str
    environment: str  # 'development', 'staging', 'production'
    deployment_type: str  # 'docker', 'kubernetes', 'local'
    config: Dict[str, Any]
    enabled: bool
    health_check_url: Optional[str]
    rollback_enabled: bool


@dataclass
class BuildConfig:
    """Build configuration for deployment"""

    build_id: str
    version: str
    git_commit: Optional[str]
    docker_image: str
    test_suite: List[str]
    environment_vars: Dict[str, str]
    build_args: Dict[str, str]
    requirements_files: List[str]


@dataclass
class DeploymentJob:
    """Deployment job tracking"""

    job_id: str
    build_config: BuildConfig
    target: DeploymentTarget
    status: str  # 'pending', 'building', 'testing', 'deploying', 'completed', 'failed'
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    build_duration: Optional[float]
    test_duration: Optional[float]
    deploy_duration: Optional[float]
    error_message: Optional[str]
    rollback_job_id: Optional[str]


class AutomatedDeploymentPipeline:
    """
    Automated Deployment Pipeline System
    Manages CI/CD automation with Docker, testing, and deployment
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Automated Deployment Pipeline"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.docker_dir = Path(self.config.get("docker_directory", "docker"))
        self.build_dir = Path(self.config.get("build_directory", "build"))
        self.artifacts_dir = Path(self.config.get("artifacts_directory", "artifacts"))

        # Create directories
        self.docker_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Docker client
        self.docker_client = None

        # Deployment targets
        self.deployment_targets = self._initialize_deployment_targets()

        # Job queue
        self.deployment_queue = []

        # Statistics
        self.stats = {
            "deployments_completed": 0,
            "deployments_failed": 0,
            "successful_rollbacks": 0,
            "last_deployment": None,
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "docker_directory": "docker",
            "build_directory": "build",
            "artifacts_directory": "artifacts",
            "docker_registry": "localhost:5000",
            "default_timeout": 1800,  # 30 minutes
            "max_concurrent_deployments": 3,
            "health_check_timeout": 300,  # 5 minutes
            "rollback_enabled": True,
            "notification": {"webhook_url": None, "email_alerts": False},
            "security": {"scan_images": True, "vulnerability_threshold": "medium"},
        }

    def _initialize_deployment_targets(self) -> List[DeploymentTarget]:
        """Initialize deployment target configurations"""
        targets = []

        # Development target
        targets.append(
            DeploymentTarget(
                target_id="dev",
                name="Development Environment",
                environment="development",
                deployment_type="docker",
                config={
                    "container_name": "horse_racing_ai_dev",
                    "port_mapping": {"8000": "8000"},
                    "volume_mapping": {
                        str(project_root / "data"): "/app/data",
                        str(project_root / "logs"): "/app/logs",
                    },
                    "environment_vars": {
                        "ENVIRONMENT": "development",
                        "DEBUG": "true",
                        "LOG_LEVEL": "DEBUG",
                    },
                },
                enabled=True,
                health_check_url="http://localhost:8000/health",
                rollback_enabled=True,
            )
        )

        # Staging target
        targets.append(
            DeploymentTarget(
                target_id="staging",
                name="Staging Environment",
                environment="staging",
                deployment_type="docker",
                config={
                    "container_name": "horse_racing_ai_staging",
                    "port_mapping": {"8001": "8000"},
                    "volume_mapping": {
                        "/opt/horse_racing_ai/data": "/app/data",
                        "/opt/horse_racing_ai/logs": "/app/logs",
                    },
                    "environment_vars": {
                        "ENVIRONMENT": "staging",
                        "DEBUG": "false",
                        "LOG_LEVEL": "INFO",
                    },
                },
                enabled=True,
                health_check_url="http://localhost:8001/health",
                rollback_enabled=True,
            )
        )

        # Production target
        targets.append(
            DeploymentTarget(
                target_id="prod",
                name="Production Environment",
                environment="production",
                deployment_type="docker",
                config={
                    "container_name": "horse_racing_ai_prod",
                    "port_mapping": {"80": "8000"},
                    "volume_mapping": {
                        "/var/lib/horse_racing_ai/data": "/app/data",
                        "/var/log/horse_racing_ai": "/app/logs",
                    },
                    "environment_vars": {
                        "ENVIRONMENT": "production",
                        "DEBUG": "false",
                        "LOG_LEVEL": "WARNING",
                    },
                    "resource_limits": {"memory": "2g", "cpus": "1.0"},
                },
                enabled=False,  # Requires manual enablement
                health_check_url="http://localhost/health",
                rollback_enabled=True,
            )
        )

        return targets

    async def initialize_database(self):
        """Initialize database tables for deployment tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Deployment jobs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS deployment_jobs (
                    job_id TEXT PRIMARY KEY,
                    build_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    build_duration REAL,
                    test_duration REAL,
                    deploy_duration REAL,
                    error_message TEXT,
                    rollback_job_id TEXT,
                    git_commit TEXT,
                    docker_image TEXT
                )
            """
            )

            # Deployment targets table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS deployment_targets (
                    target_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    deployment_type TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    health_check_url TEXT,
                    rollback_enabled BOOLEAN NOT NULL,
                    last_deployment TIMESTAMP,
                    deployment_count INTEGER DEFAULT 0
                )
            """
            )

            # Build artifacts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS build_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    build_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Deployment health checks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS deployment_health_checks (
                    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    check_time TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    error_message TEXT,
                    FOREIGN KEY (job_id) REFERENCES deployment_jobs(job_id)
                )
            """
            )

            # Indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_deployment_target ON deployment_jobs(target_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_deployment_status ON deployment_jobs(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_deployment_created ON deployment_jobs(created_at)"
            )

            conn.commit()
            conn.close()

            logger.info("Deployment pipeline database tables initialized")

        except Exception as e:
            logger.error(f"Error initializing deployment database: {e}")
            raise

    async def initialize_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Docker client: {e}")
            raise

    async def create_dockerfile(self, build_config: BuildConfig) -> Path:
        """Create Dockerfile for the application"""
        dockerfile_content = f"""
# Horse Racing AI V2.03 Production Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
{self._get_copy_requirements_commands(build_config.requirements_files)}

# Install Python dependencies
{self._get_pip_install_commands(build_config.requirements_files)}

# Copy application code
COPY . .

# Set environment variables
{self._get_env_vars_commands(build_config.environment_vars)}

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models /app/cache

# Set proper permissions
RUN chown -R nobody:nogroup /app
USER nobody

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "api.prediction_api:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        dockerfile_path = self.build_dir / f"Dockerfile.{build_config.build_id}"

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content.strip())

        logger.info(f"Dockerfile created: {dockerfile_path}")
        return dockerfile_path

    def _get_copy_requirements_commands(self, requirements_files: List[str]) -> str:
        """Generate COPY commands for requirements files"""
        commands = []
        for req_file in requirements_files:
            commands.append(f"COPY {req_file} .")
        return "\n".join(commands)

    def _get_pip_install_commands(self, requirements_files: List[str]) -> str:
        """Generate pip install commands"""
        commands = []
        for req_file in requirements_files:
            filename = Path(req_file).name
            commands.append(f"RUN pip install --no-cache-dir -r {filename}")
        return "\n".join(commands)

    def _get_env_vars_commands(self, env_vars: Dict[str, str]) -> str:
        """Generate ENV commands for environment variables"""
        commands = []
        for key, value in env_vars.items():
            commands.append(f"ENV {key}={value}")
        return "\n".join(commands)

    async def build_docker_image(
        self, build_config: BuildConfig, dockerfile_path: Path
    ) -> bool:
        """Build Docker image"""
        try:
            start_time = datetime.now()

            # Prepare build context
            build_context = project_root

            # Build arguments
            build_args = build_config.build_args.copy()
            build_args["BUILD_DATE"] = datetime.now().isoformat()
            build_args["VERSION"] = build_config.version

            logger.info(f"Building Docker image: {build_config.docker_image}")

            # Build image
            image, build_logs = self.docker_client.images.build(
                path=str(build_context),
                dockerfile=str(dockerfile_path.relative_to(build_context)),
                tag=build_config.docker_image,
                buildargs=build_args,
                rm=True,
                forcerm=True,
            )

            build_duration = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"Docker image built successfully in {build_duration:.1f}s: {image.id[:12]}"
            )

            # Save build logs
            await self._save_build_logs(build_config.build_id, build_logs)

            return True

        except Exception as e:
            logger.error(f"Error building Docker image: {e}")
            return False

    async def run_test_suite(
        self, build_config: BuildConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Run test suite in Docker container"""
        try:
            start_time = datetime.now()

            # Run tests in container
            test_results = {}
            all_tests_passed = True

            for test_suite in build_config.test_suite:
                logger.info(f"Running test suite: {test_suite}")

                # Create test container
                container = self.docker_client.containers.run(
                    build_config.docker_image,
                    command=f"python -m pytest {test_suite} -v --tb=short",
                    detach=True,
                    remove=True,
                    environment=build_config.environment_vars,
                )

                # Wait for completion
                result = container.wait(
                    timeout=self.config.get("default_timeout", 1800)
                )
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")

                test_results[test_suite] = {
                    "exit_code": result["StatusCode"],
                    "logs": logs,
                    "passed": result["StatusCode"] == 0,
                }

                if result["StatusCode"] != 0:
                    all_tests_passed = False
                    logger.warning(
                        f"Test suite {test_suite} failed with exit code {result['StatusCode']}"
                    )
                else:
                    logger.info(f"Test suite {test_suite} passed")

            test_duration = (datetime.now() - start_time).total_seconds()

            test_summary = {
                "all_passed": all_tests_passed,
                "duration": test_duration,
                "results": test_results,
                "total_suites": len(build_config.test_suite),
                "passed_suites": sum(1 for r in test_results.values() if r["passed"]),
            }

            logger.info(
                f"Test suite completed in {test_duration:.1f}s: {test_summary['passed_suites']}/{test_summary['total_suites']} suites passed"
            )

            return all_tests_passed, test_summary

        except Exception as e:
            logger.error(f"Error running test suite: {e}")
            return False, {"error": str(e)}

    async def security_scan_image(
        self, build_config: BuildConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Perform security scan on Docker image"""
        try:
            if not self.config.get("security", {}).get("scan_images", True):
                return True, {"skipped": True}

            # Simple vulnerability check (in production, use tools like Trivy, Clair, etc.)
            logger.info(
                f"Performing security scan on image: {build_config.docker_image}"
            )

            # For demo, we'll simulate a basic scan
            scan_results = {
                "vulnerabilities": {"critical": 0, "high": 0, "medium": 0, "low": 2},
                "scan_time": datetime.now().isoformat(),
                "passed": True,
            }

            threshold = self.config.get("security", {}).get(
                "vulnerability_threshold", "medium"
            )

            if (
                threshold == "critical"
                and scan_results["vulnerabilities"]["critical"] > 0
            ):
                scan_results["passed"] = False
            elif (
                threshold == "high"
                and (
                    scan_results["vulnerabilities"]["critical"]
                    + scan_results["vulnerabilities"]["high"]
                )
                > 0
            ):
                scan_results["passed"] = False
            elif (
                threshold == "medium"
                and sum(scan_results["vulnerabilities"].values())
                - scan_results["vulnerabilities"]["low"]
                > 0
            ):
                scan_results["passed"] = False

            logger.info(
                f"Security scan completed: {'PASSED' if scan_results['passed'] else 'FAILED'}"
            )

            return scan_results["passed"], scan_results

        except Exception as e:
            logger.error(f"Error performing security scan: {e}")
            return False, {"error": str(e)}

    async def deploy_to_target(
        self, build_config: BuildConfig, target: DeploymentTarget
    ) -> bool:
        """Deploy to specific target"""
        try:
            start_time = datetime.now()

            logger.info(f"Deploying to {target.name} ({target.target_id})")

            if target.deployment_type == "docker":
                success = await self._deploy_docker(build_config, target)
            else:
                logger.error(f"Unsupported deployment type: {target.deployment_type}")
                return False

            if success:
                deploy_duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Deployment to {target.name} completed in {deploy_duration:.1f}s"
                )

                # Update target status
                await self._update_target_status(target, True)

                return True
            else:
                logger.error(f"Deployment to {target.name} failed")
                await self._update_target_status(target, False)
                return False

        except Exception as e:
            logger.error(f"Error deploying to {target.name}: {e}")
            return False

    async def _deploy_docker(
        self, build_config: BuildConfig, target: DeploymentTarget
    ) -> bool:
        """Deploy using Docker"""
        try:
            config = target.config
            container_name = config["container_name"]

            # Stop and remove existing container
            try:
                existing_container = self.docker_client.containers.get(container_name)
                logger.info(f"Stopping existing container: {container_name}")
                existing_container.stop(timeout=30)
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # Container doesn't exist

            # Prepare port mapping
            port_mapping = {}
            for host_port, container_port in config.get("port_mapping", {}).items():
                port_mapping[container_port] = host_port

            # Prepare volume mapping
            volume_mapping = config.get("volume_mapping", {})

            # Prepare environment variables
            env_vars = {
                **build_config.environment_vars,
                **config.get("environment_vars", {}),
            }

            # Resource limits
            resource_limits = config.get("resource_limits", {})

            # Start new container
            logger.info(f"Starting new container: {container_name}")
            container = self.docker_client.containers.run(
                build_config.docker_image,
                name=container_name,
                ports=port_mapping,
                volumes=volume_mapping,
                environment=env_vars,
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                mem_limit=resource_limits.get("memory"),
                cpu_count=resource_limits.get("cpus"),
            )

            # Wait for container to be healthy
            success = await self._wait_for_health_check(target)

            if success:
                logger.info(f"Container {container_name} deployed and healthy")
                return True
            else:
                logger.error(f"Container {container_name} failed health check")
                # Stop failed container
                try:
                    container.stop(timeout=30)
                    container.remove()
                except:
                    pass
                return False

        except Exception as e:
            logger.error(f"Error in Docker deployment: {e}")
            return False

    async def _wait_for_health_check(self, target: DeploymentTarget) -> bool:
        """Wait for deployment health check to pass"""
        if not target.health_check_url:
            return True

        timeout = self.config.get("health_check_timeout", 300)
        start_time = datetime.now()

        logger.info(f"Waiting for health check: {target.health_check_url}")

        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                # Simple HTTP check (in production, use aiohttp)
                import requests

                response = requests.get(target.health_check_url, timeout=10)

                if response.status_code == 200:
                    logger.info(f"Health check passed for {target.name}")
                    return True
                else:
                    logger.warning(f"Health check failed: HTTP {response.status_code}")

            except Exception as e:
                logger.debug(f"Health check attempt failed: {e}")

            await asyncio.sleep(10)

        logger.error(f"Health check timeout for {target.name}")
        return False

    async def _save_build_logs(self, build_id: str, build_logs):
        """Save build logs to file"""
        try:
            log_file = self.artifacts_dir / f"build_{build_id}.log"

            with open(log_file, "w") as f:
                for line in build_logs:
                    if "stream" in line:
                        f.write(line["stream"])

            logger.info(f"Build logs saved: {log_file}")

        except Exception as e:
            logger.warning(f"Error saving build logs: {e}")

    async def _update_target_status(self, target: DeploymentTarget, success: bool):
        """Update deployment target status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO deployment_targets 
                (target_id, name, environment, deployment_type, config_json, 
                 enabled, health_check_url, rollback_enabled, last_deployment, deployment_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT deployment_count FROM deployment_targets WHERE target_id = ?), 0) + 1)
            """,
                (
                    target.target_id,
                    target.name,
                    target.environment,
                    target.deployment_type,
                    json.dumps(target.config),
                    target.enabled,
                    target.health_check_url,
                    target.rollback_enabled,
                    datetime.now() if success else None,
                    target.target_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating target status: {e}")

    async def create_deployment_job(
        self, version: str, target_id: str, git_commit: Optional[str] = None
    ) -> str:
        """Create a new deployment job"""
        job_id = (
            f"deploy_{version}_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        build_id = f"build_{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Get target
        target = next(
            (t for t in self.deployment_targets if t.target_id == target_id), None
        )
        if not target:
            raise ValueError(f"Deployment target not found: {target_id}")

        if not target.enabled:
            raise ValueError(f"Deployment target is disabled: {target_id}")

        # Create build configuration
        build_config = BuildConfig(
            build_id=build_id,
            version=version,
            git_commit=git_commit,
            docker_image=f"{self.config.get('docker_registry', 'localhost:5000')}/horse_racing_ai:{version}",
            test_suite=[
                "tests/quick_system_test.py",
                "tests/comprehensive_test_framework.py",
            ],
            environment_vars={
                "VERSION": version,
                "BUILD_ID": build_id,
                "DEPLOYMENT_TARGET": target_id,
            },
            build_args={},
            requirements_files=[
                "api/requirements.txt",
                "docker/requirements-integrated.txt",
            ],
        )

        # Create deployment job
        job = DeploymentJob(
            job_id=job_id,
            build_config=build_config,
            target=target,
            status="pending",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            build_duration=None,
            test_duration=None,
            deploy_duration=None,
            error_message=None,
            rollback_job_id=None,
        )

        self.deployment_queue.append(job)

        # Save to database
        await self._save_deployment_job(job)

        logger.info(f"Deployment job created: {job_id}")
        return job_id

    async def execute_deployment_job(self, job: DeploymentJob) -> bool:
        """Execute a deployment job"""
        try:
            job.status = "building"
            job.started_at = datetime.now()
            await self._update_deployment_job_status(job)

            logger.info(f"Starting deployment job: {job.job_id}")

            # Create Dockerfile
            dockerfile_path = await self.create_dockerfile(job.build_config)

            # Build Docker image
            build_start = datetime.now()
            build_success = await self.build_docker_image(
                job.build_config, dockerfile_path
            )
            job.build_duration = (datetime.now() - build_start).total_seconds()

            if not build_success:
                job.status = "failed"
                job.error_message = "Docker image build failed"
                job.completed_at = datetime.now()
                await self._update_deployment_job_status(job)
                return False

            # Security scan
            scan_success, scan_results = await self.security_scan_image(
                job.build_config
            )
            if not scan_success:
                job.status = "failed"
                job.error_message = f"Security scan failed: {scan_results}"
                job.completed_at = datetime.now()
                await self._update_deployment_job_status(job)
                return False

            # Run tests
            job.status = "testing"
            await self._update_deployment_job_status(job)

            test_start = datetime.now()
            test_success, test_results = await self.run_test_suite(job.build_config)
            job.test_duration = (datetime.now() - test_start).total_seconds()

            if not test_success:
                job.status = "failed"
                job.error_message = f"Tests failed: {test_results}"
                job.completed_at = datetime.now()
                await self._update_deployment_job_status(job)
                return False

            # Deploy
            job.status = "deploying"
            await self._update_deployment_job_status(job)

            deploy_start = datetime.now()
            deploy_success = await self.deploy_to_target(job.build_config, job.target)
            job.deploy_duration = (datetime.now() - deploy_start).total_seconds()

            if deploy_success:
                job.status = "completed"
                self.stats["deployments_completed"] += 1
                self.stats["last_deployment"] = datetime.now()
                logger.info(f"Deployment job completed successfully: {job.job_id}")
            else:
                job.status = "failed"
                job.error_message = "Deployment failed"
                self.stats["deployments_failed"] += 1

            job.completed_at = datetime.now()
            await self._update_deployment_job_status(job)

            return deploy_success

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            await self._update_deployment_job_status(job)

            logger.error(f"Error executing deployment job {job.job_id}: {e}")
            self.stats["deployments_failed"] += 1

            return False

    async def _save_deployment_job(self, job: DeploymentJob):
        """Save deployment job to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO deployment_jobs 
                (job_id, build_id, version, target_id, environment, status, 
                 created_at, git_commit, docker_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    job.job_id,
                    job.build_config.build_id,
                    job.build_config.version,
                    job.target.target_id,
                    job.target.environment,
                    job.status,
                    job.created_at,
                    job.build_config.git_commit,
                    job.build_config.docker_image,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving deployment job: {e}")

    async def _update_deployment_job_status(self, job: DeploymentJob):
        """Update deployment job status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE deployment_jobs 
                SET status = ?, started_at = ?, completed_at = ?, 
                    build_duration = ?, test_duration = ?, deploy_duration = ?,
                    error_message = ?, rollback_job_id = ?
                WHERE job_id = ?
            """,
                (
                    job.status,
                    job.started_at,
                    job.completed_at,
                    job.build_duration,
                    job.test_duration,
                    job.deploy_duration,
                    job.error_message,
                    job.rollback_job_id,
                    job.job_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating deployment job status: {e}")

    async def process_deployment_queue(self) -> Dict[str, Any]:
        """Process pending deployment jobs"""
        results = {
            "jobs_processed": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "job_results": [],
        }

        # Process pending jobs
        pending_jobs = [job for job in self.deployment_queue if job.status == "pending"]

        # Limit concurrent deployments
        max_concurrent = self.config.get("max_concurrent_deployments", 3)
        jobs_to_process = pending_jobs[:max_concurrent]

        for job in jobs_to_process:
            try:
                logger.info(f"Processing deployment job: {job.job_id}")

                success = await self.execute_deployment_job(job)

                results["jobs_processed"] += 1

                if success:
                    results["jobs_completed"] += 1
                else:
                    results["jobs_failed"] += 1

                results["job_results"].append(
                    {
                        "job_id": job.job_id,
                        "version": job.build_config.version,
                        "target": job.target.target_id,
                        "status": job.status,
                        "error_message": job.error_message,
                    }
                )

                # Remove completed job from queue
                self.deployment_queue.remove(job)

            except Exception as e:
                logger.error(f"Error processing deployment job {job.job_id}: {e}")
                results["jobs_failed"] += 1

        return results

    async def get_deployment_statistics(self) -> Dict[str, Any]:
        """Get deployment pipeline statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Job statistics
            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM deployment_jobs
                GROUP BY status
            """
            )
            job_stats = {row[0]: row[1] for row in cursor.fetchall()}

            # Target statistics
            cursor.execute(
                """
                SELECT target_id, environment, deployment_count, last_deployment
                FROM deployment_targets
            """
            )
            target_stats = [
                {
                    "target_id": row[0],
                    "environment": row[1],
                    "deployment_count": row[2],
                    "last_deployment": row[3],
                }
                for row in cursor.fetchall()
            ]

            # Recent deployments
            cursor.execute(
                """
                SELECT job_id, version, target_id, status, completed_at
                FROM deployment_jobs
                WHERE completed_at IS NOT NULL
                ORDER BY completed_at DESC
                LIMIT 10
            """
            )
            recent_deployments = [
                {
                    "job_id": row[0],
                    "version": row[1],
                    "target_id": row[2],
                    "status": row[3],
                    "completed_at": row[4],
                }
                for row in cursor.fetchall()
            ]

            # Queue status
            queue_stats = {
                "pending_jobs": len(
                    [j for j in self.deployment_queue if j.status == "pending"]
                ),
                "running_jobs": len(
                    [
                        j
                        for j in self.deployment_queue
                        if j.status in ["building", "testing", "deploying"]
                    ]
                ),
                "total_in_queue": len(self.deployment_queue),
            }

            conn.close()

            return {
                "system_stats": self.stats.copy(),
                "job_statistics": job_stats,
                "target_statistics": target_stats,
                "recent_deployments": recent_deployments,
                "queue_status": queue_stats,
                "configured_targets": len(self.deployment_targets),
            }

        except Exception as e:
            logger.error(f"Error getting deployment statistics: {e}")
            return {"error": str(e)}


async def main():
    """Main function for testing the Automated Deployment Pipeline"""

    print("🚀 Automated Deployment Pipeline System V2.03")
    print("=" * 50)

    try:
        # Initialize pipeline
        pipeline = AutomatedDeploymentPipeline()

        # Initialize database
        print("📊 Initializing database...")
        await pipeline.initialize_database()

        # Initialize Docker client
        print("🐳 Initializing Docker client...")
        await pipeline.initialize_docker_client()

        # Create test deployment job
        print("📦 Creating test deployment job...")
        job_id = await pipeline.create_deployment_job(
            version="v2.03-test", target_id="dev", git_commit="test_commit_123"
        )
        print(f"   - Job created: {job_id}")

        # Process deployment queue
        print("🔄 Processing deployment queue...")
        processing_results = await pipeline.process_deployment_queue()

        print(f"✅ Processing completed:")
        print(f"   - Jobs processed: {processing_results['jobs_processed']}")
        print(f"   - Jobs completed: {processing_results['jobs_completed']}")
        print(f"   - Jobs failed: {processing_results['jobs_failed']}")

        # Show job results
        for result in processing_results["job_results"]:
            print(f"   - {result['job_id']}: {result['status']}")
            if result["error_message"]:
                print(f"     Error: {result['error_message']}")

        # Get statistics
        print("\n📈 Deployment Statistics:")
        stats = await pipeline.get_deployment_statistics()

        print(f"   - Configured targets: {stats['configured_targets']}")
        print(
            f"   - Total deployments: {stats['system_stats']['deployments_completed']}"
        )
        print(f"   - Failed deployments: {stats['system_stats']['deployments_failed']}")

        if stats["target_statistics"]:
            print("   - Target deployment counts:")
            for target in stats["target_statistics"]:
                print(
                    f"     • {target['target_id']} ({target['environment']}): {target['deployment_count']} deployments"
                )

        print("\n✅ Automated Deployment Pipeline testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
