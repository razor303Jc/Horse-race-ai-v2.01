#!/usr/bin/env python3
"""
🚀 Deploy Automated Data Relationships Pipeline
Production Deployment Script for 5-Year Historic Dataset Building

This script handles the deployment and configuration of the automated
data relationships pipeline for continuous operation.

Usage:
    python3 deploy_automated_pipeline.py [mode]

Modes:
    - daemon: Start as background daemon process
    - cron: Set up cron job for scheduled execution
    - test: Run test to verify deployment
    - status: Check current deployment status
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineDeployer:
    """Handles deployment of the automated pipeline system."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.tools_dir = self.base_dir / "tools" / "data_processing"
        self.config_file = self.tools_dir / "data_relationships_pipeline.json"
        self.status_file = self.tools_dir / "pipeline_status.json"

    def deploy_daemon_mode(self):
        """Deploy pipeline in daemon mode."""
        logger.info("🔧 Deploying automated pipeline in daemon mode...")

        try:
            # Start the scheduler in daemon mode
            daemon_script = self.tools_dir / "pipeline_scheduler.py"
            cmd = [sys.executable, str(daemon_script), "daemon"]

            # Start process in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir),
            )

            # Update status
            self.update_status(
                {
                    "mode": "daemon",
                    "pid": process.pid,
                    "started_at": datetime.now().isoformat(),
                    "status": "running",
                }
            )

            logger.info(f"✅ Daemon started with PID: {process.pid}")
            logger.info(
                "📋 Daemon will monitor for new data uploads and run pipeline automatically"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to deploy daemon mode: {e}")
            return False

    def deploy_cron_job(self):
        """Deploy pipeline as cron job."""
        logger.info("🔧 Setting up cron job for automated pipeline...")

        try:
            # Generate cron job
            scheduler_script = self.tools_dir / "pipeline_scheduler.py"
            cron_command = f"*/30 * * * * cd {self.base_dir} && {sys.executable} {scheduler_script} cron"

            # Display cron job setup instructions
            print("\n" + "=" * 70)
            print("📅 CRON JOB SETUP INSTRUCTIONS")
            print("=" * 70)
            print("\n1. Open crontab editor:")
            print("   crontab -e")
            print("\n2. Add this line to run pipeline every 30 minutes:")
            print(f"   {cron_command}")
            print("\n3. Save and exit the editor")
            print("\n4. Verify cron job is active:")
            print("   crontab -l")
            print("\n" + "=" * 70)

            # Update status
            self.update_status(
                {
                    "mode": "cron",
                    "cron_command": cron_command,
                    "configured_at": datetime.now().isoformat(),
                    "status": "configured",
                }
            )

            logger.info("✅ Cron job configuration ready")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to configure cron job: {e}")
            return False

    def run_test_deployment(self):
        """Test the deployment by running the pipeline."""
        logger.info("🧪 Testing automated pipeline deployment...")

        try:
            # Test upload integration hook
            hook_script = self.tools_dir / "upload_integration_hook.py"
            result = subprocess.run(
                [sys.executable, str(hook_script)],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir),
            )

            if result.returncode == 0:
                logger.info("✅ Upload integration hook test passed")

                # Test main pipeline
                pipeline_script = self.tools_dir / "automated_relationships_pipeline.py"
                result = subprocess.run(
                    [sys.executable, str(pipeline_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.base_dir),
                )

                if result.returncode == 0:
                    logger.info("✅ Main pipeline test passed")
                    logger.info("🎉 All deployment tests successful!")
                    return True
                else:
                    logger.error(f"❌ Main pipeline test failed: {result.stderr}")
                    return False
            else:
                logger.error(f"❌ Upload integration test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Test deployment failed: {e}")
            return False

    def check_status(self):
        """Check current deployment status."""
        logger.info("📊 Checking automated pipeline deployment status...")

        try:
            if self.status_file.exists():
                with open(self.status_file, "r") as f:
                    status = json.load(f)

                print("\n" + "=" * 60)
                print("📋 AUTOMATED PIPELINE STATUS")
                print("=" * 60)
                print(f"Mode: {status.get('mode', 'Unknown')}")
                print(f"Status: {status.get('status', 'Unknown')}")

                if status.get("mode") == "daemon":
                    print(f"PID: {status.get('pid', 'Unknown')}")
                    print(f"Started: {status.get('started_at', 'Unknown')}")
                elif status.get("mode") == "cron":
                    print(f"Configured: {status.get('configured_at', 'Unknown')}")
                    print(f"Command: {status.get('cron_command', 'Unknown')}")

                print("=" * 60)
                return True
            else:
                logger.info("📋 No deployment status found - pipeline not deployed")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to check status: {e}")
            return False

    def update_status(self, status_data):
        """Update deployment status file."""
        try:
            with open(self.status_file, "w") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update status: {e}")

    def show_usage(self):
        """Show usage instructions."""
        print(__doc__)


def main():
    """Main deployment function."""
    deployer = PipelineDeployer()

    if len(sys.argv) < 2:
        deployer.show_usage()
        return

    mode = sys.argv[1].lower()

    print("🚀 Automated Data Relationships Pipeline Deployment")
    print("Production-Ready System for 5-Year Historic Dataset Building")
    print("=" * 70)

    if mode == "daemon":
        success = deployer.deploy_daemon_mode()
    elif mode == "cron":
        success = deployer.deploy_cron_job()
    elif mode == "test":
        success = deployer.run_test_deployment()
    elif mode == "status":
        success = deployer.check_status()
    else:
        print(f"❌ Unknown mode: {mode}")
        deployer.show_usage()
        return

    if success:
        print("\n🎉 Deployment operation completed successfully!")
    else:
        print("\n❌ Deployment operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
