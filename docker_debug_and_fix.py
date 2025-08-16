#!/usr/bin/env python3
"""
Docker Debug and Fix Script
Systematically diagnoses and fixes Docker issues
"""

import os
import subprocess
import time
from pathlib import Path


class DockerDebugger:
    def __init__(self):
        self.compose_file = "docker-compose.clean.yml"
        self.test_compose = "docker-compose.test.yml"
        self.issues = []
        self.fixes = []

    def run_cmd(self, cmd):
        """Run command and return success, output, error"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def log_issue(self, issue):
        self.issues.append(issue)
        print(f"❌ ISSUE: {issue}")

    def log_fix(self, fix):
        self.fixes.append(fix)
        print(f"🔧 FIX: {fix}")

    def check_web_app_logs(self):
        """Check web app logs for specific errors"""
        print("\n📋 ANALYZING WEB APP LOGS:")
        print("-" * 40)

        # Check test container logs
        success, logs, err = self.run_cmd(
            "docker logs horse_racing_web_app_test --tail=20"
        )

        if success and logs:
            print("Recent error logs:")
            lines = logs.split("\n")
            for line in lines[-10:]:
                if line.strip():
                    print(f"  {line}")

            # Analyze common errors
            if "ModuleNotFoundError" in logs:
                missing_modules = []
                for line in lines:
                    if "ModuleNotFoundError: No module named" in line:
                        module = line.split("'")[1] if "'" in line else "unknown"
                        missing_modules.append(module)

                if missing_modules:
                    self.log_issue(
                        f"Missing Python modules: {list(set(missing_modules))}"
                    )
                    return missing_modules

            if "cannot connect" in logs.lower() or "connection refused" in logs.lower():
                self.log_issue("Database/Redis connection issues")

            if "port already in use" in logs.lower():
                self.log_issue("Port conflicts")

        return []

    def fix_requirements(self, missing_modules):
        """Add missing modules to requirements"""
        req_file = "docker/requirements/requirements-web-app-optimized.txt"

        if missing_modules and Path(req_file).exists():
            print(f"\n🔧 FIXING REQUIREMENTS in {req_file}")

            # Read current requirements
            with open(req_file, "r") as f:
                content = f.read()

            # Add missing modules
            additions = []
            module_map = {
                "joblib": "joblib>=1.3.0",
                "sklearn": "scikit-learn>=1.3.0",
                "torch": "torch>=2.0.0",
                "numpy": "numpy>=1.24.0",
                "matplotlib": "matplotlib>=3.7.0",
                "seaborn": "seaborn>=0.12.0",
            }

            for module in missing_modules:
                if module in module_map and module_map[module] not in content:
                    additions.append(module_map[module])

            if additions:
                with open(req_file, "a") as f:
                    f.write("\n# Added by debugger\n")
                    for addition in additions:
                        f.write(f"{addition}\n")

                self.log_fix(f"Added {additions} to {req_file}")
                return True

        return False

    def check_database_connectivity(self):
        """Test database connectivity"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY:")
        print("-" * 40)

        # Check if postgres containers are running
        success, out, err = self.run_cmd(
            "docker ps --filter name=postgres --format '{{.Names}}'"
        )

        if success and out.strip():
            postgres_containers = out.strip().split("\n")
            print(f"Found PostgreSQL containers: {postgres_containers}")

            # Test connection to each
            for container in postgres_containers:
                success, out, err = self.run_cmd(f"docker exec {container} pg_isready")
                if success:
                    print(f"✅ {container} is ready")
                else:
                    print(f"❌ {container} is not ready: {err}")
        else:
            self.log_issue("No PostgreSQL containers running")

    def check_port_conflicts(self):
        """Check for port conflicts"""
        print("\n🔌 CHECKING PORT CONFLICTS:")
        print("-" * 40)

        # Check what's using ports 8000-8002
        for port in [8000, 8001, 8002]:
            success, out, err = self.run_cmd(f"lsof -i :{port}")
            if success and out.strip():
                print(f"⚠️ Port {port} is in use:")
                print(f"  {out.strip()}")
            else:
                print(f"✅ Port {port} is available")

    def rebuild_and_restart(self):
        """Rebuild and restart web app"""
        print("\n🏗️ REBUILDING AND RESTARTING WEB APP:")
        print("-" * 40)

        # Stop current container
        print("Stopping current web app...")
        self.run_cmd("docker-compose -f docker-compose.test.yml down")

        # Rebuild
        print("Rebuilding web app...")
        success, out, err = self.run_cmd(
            "docker-compose -f docker-compose.test.yml build web-app"
        )

        if success:
            print("✅ Rebuild successful")

            # Start again
            print("Starting web app...")
            success, out, err = self.run_cmd(
                "docker-compose -f docker-compose.test.yml up -d web-app"
            )

            if success:
                print("✅ Web app started")
                time.sleep(10)  # Wait for startup

                # Check status
                success, out, err = self.run_cmd(
                    "docker-compose -f docker-compose.test.yml ps"
                )
                print(f"Container status:\n{out}")

                return True
            else:
                print(f"❌ Failed to start: {err}")
        else:
            print(f"❌ Rebuild failed: {err}")

        return False

    def test_endpoint(self):
        """Test web app endpoint"""
        print("\n🌐 TESTING WEB APP ENDPOINT:")
        print("-" * 40)

        try:
            import requests

            # Test different ports
            for port in [8002, 8001, 8000]:
                try:
                    url = f"http://localhost:{port}/health"
                    print(f"Testing {url}...")

                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Web app responding on port {port}")
                        print(f"Response: {response.text}")
                        return True
                    else:
                        print(f"❌ Port {port} returned {response.status_code}")

                except requests.exceptions.ConnectionError:
                    print(f"❌ Port {port} - Connection refused")
                except Exception as e:
                    print(f"❌ Port {port} - Error: {e}")

            return False

        except ImportError:
            print("⚠️ requests not available, trying curl...")

            success, out, err = self.run_cmd("curl -s http://localhost:8002/health")
            if success:
                print(f"✅ Web app responding: {out}")
                return True
            else:
                print(f"❌ Curl failed: {err}")
                return False

    def run_diagnosis(self):
        """Run complete diagnosis"""
        print("🐳 DOCKER SYSTEM DIAGNOSIS")
        print("=" * 50)

        # Step 1: Check logs for specific errors
        missing_modules = self.check_web_app_logs()

        # Step 2: Fix requirements if needed
        if missing_modules:
            requirements_fixed = self.fix_requirements(missing_modules)
            if requirements_fixed:
                # Rebuild after fixing requirements
                self.rebuild_and_restart()

        # Step 3: Check database connectivity
        self.check_database_connectivity()

        # Step 4: Check port conflicts
        self.check_port_conflicts()

        # Step 5: Test endpoint
        endpoint_working = self.test_endpoint()

        # Step 6: Final status
        print("\n" + "=" * 50)
        print("🎯 DIAGNOSIS COMPLETE")
        print("=" * 50)

        print(f"\n📊 SUMMARY:")
        print(f"Issues found: {len(self.issues)}")
        print(f"Fixes applied: {len(self.fixes)}")
        print(f"Endpoint working: {'✅' if endpoint_working else '❌'}")

        if self.issues:
            print(f"\n❌ REMAINING ISSUES:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")

        if self.fixes:
            print(f"\n🔧 FIXES APPLIED:")
            for i, fix in enumerate(self.fixes, 1):
                print(f"  {i}. {fix}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not endpoint_working:
            print("1. Check container logs: docker logs horse_racing_web_app_test")
            print("2. Verify database connectivity")
            print("3. Check for port conflicts")
            print("4. Rebuild with --no-cache if issues persist")
        else:
            print("✅ Web application is working correctly!")
            print("1. Run integration tests")
            print("2. Start other services (data-pipeline, ml-trainer)")


if __name__ == "__main__":
    debugger = DockerDebugger()
    debugger.run_diagnosis()
