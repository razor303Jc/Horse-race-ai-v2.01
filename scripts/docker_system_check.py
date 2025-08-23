#!/usr/bin/env python3
"""
Docker System Check - Comprehensive Health Monitor
=================================================

Checks all Docker containers, services, networks, and dependencies
for the Horse Racing AI system.
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import os


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class DockerSystemCheck:
    def __init__(self):
        self.services = [
            "horse_racing_postgres_clean",
            "horse_racing_redis_clean",
            "horse_racing_web_app_clean",
            "horse_racing_ml_trainer_clean",
            "horse_racing_data_pipeline_clean",
        ]
        self.networks = ["horse_racing_network"]
        self.volumes = ["postgres_data", "redis_data"]

    def run_command(self, cmd: str) -> Tuple[bool, str]:
        """Run shell command and return (success, output)"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{title:^60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")

    def print_status(self, item: str, status: str, details: str = ""):
        """Print formatted status line"""
        if status == "HEALTHY" or status == "RUNNING":
            color = Colors.GREEN
            symbol = "✅"
        elif status == "UNHEALTHY" or status == "EXITED":
            color = Colors.RED
            symbol = "❌"
        elif status == "STARTING":
            color = Colors.YELLOW
            symbol = "⚠️"
        else:
            color = Colors.YELLOW
            symbol = "🔍"

        print(f"{symbol} {color}{item:<30}{Colors.END} {status}")
        if details:
            print(f"   {Colors.WHITE}{details}{Colors.END}")

    def check_docker_daemon(self) -> bool:
        """Check if Docker daemon is running"""
        self.print_header("DOCKER DAEMON STATUS")
        success, output = self.run_command("docker info")
        if success:
            self.print_status("Docker Daemon", "RUNNING", "Docker is accessible")
            return True
        else:
            self.print_status(
                "Docker Daemon", "STOPPED", "Docker is not running or accessible"
            )
            return False

    def check_containers(self) -> Dict[str, Dict]:
        """Check status of all containers"""
        self.print_header("CONTAINER STATUS")

        container_status = {}
        success, output = self.run_command(
            "docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'"
        )

        if not success:
            print(f"{Colors.RED}❌ Failed to get container status{Colors.END}")
            return container_status

        for service in self.services:
            found = False
            for line in output.split("\n"):
                if line and service in line:
                    parts = line.split("\t")
                    name = parts[0]
                    status = parts[1] if len(parts) > 1 else "UNKNOWN"
                    ports = parts[2] if len(parts) > 2 else "No ports"

                    container_status[service] = {
                        "status": status,
                        "ports": ports,
                        "found": True,
                    }

                    if "Up" in status and "healthy" in status:
                        self.print_status(name, "HEALTHY", f"Ports: {ports}")
                    elif "Up" in status and "unhealthy" in status:
                        self.print_status(name, "UNHEALTHY", f"Ports: {ports}")
                    elif "Up" in status:
                        self.print_status(name, "RUNNING", f"Ports: {ports}")
                    else:
                        self.print_status(name, "STOPPED", status)
                    found = True
                    break

            if not found:
                container_status[service] = {"status": "NOT_FOUND", "found": False}
                self.print_status(service, "NOT_FOUND", "Container not created")

        return container_status

    def check_networks(self) -> Dict[str, bool]:
        """Check Docker networks"""
        self.print_header("NETWORK STATUS")

        network_status = {}
        success, output = self.run_command("docker network ls --format '{{.Name}}'")

        if not success:
            print(f"{Colors.RED}❌ Failed to get network status{Colors.END}")
            return network_status

        existing_networks = output.split("\n")

        for network in self.networks:
            if network in existing_networks:
                network_status[network] = True
                self.print_status(network, "EXISTS")

                # Check network details
                success, details = self.run_command(f"docker network inspect {network}")
                if success:
                    try:
                        network_info = json.loads(details)[0]
                        containers = network_info.get("Containers", {})
                        print(
                            f"   {Colors.WHITE}Connected containers: {len(containers)}{Colors.END}"
                        )
                        for container_id, info in containers.items():
                            container_name = info.get("Name", "Unknown")
                            print(f"   {Colors.WHITE}  - {container_name}{Colors.END}")
                    except:
                        pass
            else:
                network_status[network] = False
                self.print_status(network, "MISSING")

        return network_status

    def check_volumes(self) -> Dict[str, bool]:
        """Check Docker volumes"""
        self.print_header("VOLUME STATUS")

        volume_status = {}
        success, output = self.run_command("docker volume ls --format '{{.Name}}'")

        if not success:
            print(f"{Colors.RED}❌ Failed to get volume status{Colors.END}")
            return volume_status

        existing_volumes = output.split("\n")

        for volume in self.volumes:
            volume_name = f"horse-race-ai-v204_{volume}"  # Docker Compose prefix
            if volume_name in existing_volumes or volume in existing_volumes:
                volume_status[volume] = True
                self.print_status(volume, "EXISTS")

                # Check volume size
                success, size_info = self.run_command(
                    f"docker system df -v | grep {volume}"
                )
                if success and size_info:
                    print(f"   {Colors.WHITE}{size_info}{Colors.END}")
            else:
                volume_status[volume] = False
                self.print_status(volume, "MISSING")

        return volume_status

    def check_services_health(self, container_status: Dict) -> Dict[str, Dict]:
        """Detailed health check for each service"""
        self.print_header("SERVICE HEALTH CHECKS")

        health_status = {}

        # PostgreSQL Health Check
        if container_status.get("horse_racing_postgres_clean", {}).get("found"):
            success, output = self.run_command(
                "docker exec horse_racing_postgres_clean pg_isready -U horse_racing -d horse_racing_db"
            )
            if success:
                self.print_status(
                    "PostgreSQL Database", "HEALTHY", "Database accepting connections"
                )

                # Check database size
                success, db_size = self.run_command(
                    "docker exec horse_racing_postgres_clean psql -U horse_racing -d horse_racing_db -c \"SELECT pg_size_pretty(pg_database_size('horse_racing_db'));\""
                )
                if success:
                    size_line = [
                        line
                        for line in db_size.split("\n")
                        if "MB" in line or "GB" in line or "kB" in line
                    ]
                    if size_line:
                        print(
                            f"   {Colors.WHITE}Database size: {size_line[0].strip()}{Colors.END}"
                        )

                health_status["postgres"] = {"status": "healthy", "details": db_size}
            else:
                self.print_status("PostgreSQL Database", "UNHEALTHY", output)
                health_status["postgres"] = {"status": "unhealthy", "details": output}
        else:
            self.print_status("PostgreSQL Database", "NOT_RUNNING")
            health_status["postgres"] = {"status": "not_running"}

        # Redis Health Check
        if container_status.get("horse_racing_redis_clean", {}).get("found"):
            # Try with authentication first
            success, output = self.run_command(
                "docker exec horse_racing_redis_clean redis-cli -a redis_password_123 ping"
            )
            if not success or "PONG" not in output:
                # Try without authentication as fallback
                success, output = self.run_command(
                    "docker exec horse_racing_redis_clean redis-cli ping"
                )

            if success and "PONG" in output:
                self.print_status("Redis Cache", "HEALTHY", "Cache responding to ping")
                health_status["redis"] = {"status": "healthy"}
            else:
                self.print_status("Redis Cache", "UNHEALTHY", output)
                health_status["redis"] = {"status": "unhealthy", "details": output}
        else:
            self.print_status("Redis Cache", "NOT_RUNNING")
            health_status["redis"] = {"status": "not_running"}

        # Web App Health Check
        if container_status.get("horse_racing_web_app_clean", {}).get("found"):
            success, output = self.run_command(
                "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health"
            )
            if success and output == "200":
                self.print_status(
                    "Web Application", "HEALTHY", "API responding on port 3000"
                )
                health_status["web_app"] = {"status": "healthy"}
            else:
                self.print_status(
                    "Web Application", "UNHEALTHY", f"HTTP status: {output}"
                )
                health_status["web_app"] = {
                    "status": "unhealthy",
                    "details": f"HTTP {output}",
                }
        else:
            self.print_status("Web Application", "NOT_RUNNING")
            health_status["web_app"] = {"status": "not_running"}

        # ML Trainer Health Check
        if container_status.get("horse_racing_ml_trainer_clean", {}).get("found"):
            success, output = self.run_command(
                "docker exec horse_racing_ml_trainer_clean python -c 'import sys; print(sys.version)'"
            )
            if success:
                self.print_status("ML Trainer", "HEALTHY", "Python environment ready")
                health_status["ml_trainer"] = {"status": "healthy"}
            else:
                self.print_status("ML Trainer", "UNHEALTHY", output)
                health_status["ml_trainer"] = {"status": "unhealthy", "details": output}
        else:
            self.print_status("ML Trainer", "NOT_RUNNING")
            health_status["ml_trainer"] = {"status": "not_running"}

        # Data Pipeline Health Check
        if container_status.get("horse_racing_data_pipeline_clean", {}).get("found"):
            success, output = self.run_command(
                "docker logs horse_racing_data_pipeline_clean --tail 5"
            )
            if success and "error" not in output.lower():
                self.print_status(
                    "Data Pipeline", "HEALTHY", "Pipeline running without errors"
                )
                health_status["data_pipeline"] = {"status": "healthy"}
            else:
                self.print_status("Data Pipeline", "UNHEALTHY", "Check logs for errors")
                health_status["data_pipeline"] = {
                    "status": "unhealthy",
                    "details": "See logs",
                }
        else:
            self.print_status("Data Pipeline", "NOT_RUNNING")
            health_status["data_pipeline"] = {"status": "not_running"}

        return health_status

    def check_resource_usage(self):
        """Check Docker resource usage"""
        self.print_header("RESOURCE USAGE")

        success, output = self.run_command(
            "docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'"
        )
        if success:
            lines = output.split("\n")
            for line in lines:
                if line and not line.startswith("CONTAINER"):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        container = parts[0]
                        cpu = parts[1]
                        memory = parts[2]
                        print(
                            f"📊 {Colors.WHITE}{container:<30}{Colors.END} CPU: {Colors.YELLOW}{cpu}{Colors.END} Memory: {Colors.BLUE}{memory}{Colors.END}"
                        )

    def generate_recommendations(
        self, container_status: Dict, health_status: Dict
    ) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []

        for service, status in container_status.items():
            if not status.get("found"):
                recommendations.append(
                    f"🔧 Start {service} container: docker-compose up -d"
                )
            elif "UNHEALTHY" in status.get("status", ""):
                recommendations.append(
                    f"🔧 Restart {service}: docker-compose restart {service.replace('horse_racing_', '').replace('_clean', '')}"
                )

        for service, health in health_status.items():
            if health.get("status") == "unhealthy":
                recommendations.append(
                    f"🔍 Debug {service}: docker logs horse_racing_{service}_clean"
                )

        if not recommendations:
            recommendations.append("✅ All systems operational - no actions needed!")

        return recommendations

    def run_full_check(self):
        """Run comprehensive system check"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}")
        print("🏇 Horse Racing AI - Docker System Check")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.END}")

        # Check Docker daemon
        if not self.check_docker_daemon():
            print(
                f"\n{Colors.RED}❌ Cannot proceed - Docker daemon not running{Colors.END}"
            )
            return False

        # Run all checks
        container_status = self.check_containers()
        network_status = self.check_networks()
        volume_status = self.check_volumes()
        health_status = self.check_services_health(container_status)

        # Resource usage
        self.check_resource_usage()

        # Generate recommendations
        self.print_header("RECOMMENDATIONS")
        recommendations = self.generate_recommendations(container_status, health_status)
        for rec in recommendations:
            print(f"{rec}")

        # Summary
        self.print_header("SUMMARY")
        healthy_services = sum(
            1 for h in health_status.values() if h.get("status") == "healthy"
        )
        total_services = len(self.services)

        if healthy_services == total_services:
            print(f"🎉 {Colors.GREEN}ALL SYSTEMS OPERATIONAL{Colors.END}")
            print(f"   {healthy_services}/{total_services} services healthy")
        else:
            print(f"⚠️  {Colors.YELLOW}SYSTEM ISSUES DETECTED{Colors.END}")
            print(f"   {healthy_services}/{total_services} services healthy")

        return healthy_services == total_services


if __name__ == "__main__":
    checker = DockerSystemCheck()
    success = checker.run_full_check()
    sys.exit(0 if success else 1)
