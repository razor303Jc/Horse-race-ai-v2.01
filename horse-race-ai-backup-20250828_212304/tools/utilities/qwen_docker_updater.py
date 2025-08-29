#!/usr/bin/env python3
"""
Qwen2.5 Auto-Updater Docker Service
Docker container orchestration for the Qwen auto-updater
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QwenDockerUpdater:
    """
    Docker-based auto-updater for Qwen2.5 model and services
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.updater_service_name = "qwen-auto-updater"
    
    def create_updater_service(self):
        """Add auto-updater service to docker-compose.yml"""
        logger.info("🐳 Creating Qwen auto-updater Docker service...")
        
        try:
            # Read existing docker-compose.yml
            if self.docker_compose_file.exists():
                with open(self.docker_compose_file, 'r') as f:
                    compose_data = yaml.safe_load(f)
            else:
                compose_data = {"version": "3.8", "services": {}}
            
            # Add auto-updater service
            compose_data["services"][self.updater_service_name] = {
                "build": {
                    "context": ".",
                    "dockerfile": "docker/qwen-auto-updater/Dockerfile"
                },
                "container_name": "qwen_auto_updater",
                "restart": "unless-stopped",
                "environment": [
                    "PYTHONPATH=/app",
                    "LOG_LEVEL=INFO"
                ],
                "volumes": [
                    "./config:/app/config",
                    "./logs:/app/logs",
                    "./backups:/app/backups",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "./qwen_auto_updater.py:/app/qwen_auto_updater.py"
                ],
                "depends_on": [
                    "horse_racing_postgres",
                    "horse_racing_redis"
                ],
                "networks": ["horse_racing_network"],
                "command": "python qwen_auto_updater.py daemon"
            }
            
            # Ensure networks section exists
            if "networks" not in compose_data:
                compose_data["networks"] = {}
            
            if "horse_racing_network" not in compose_data["networks"]:
                compose_data["networks"]["horse_racing_network"] = {
                    "driver": "bridge"
                }
            
            # Write updated docker-compose.yml
            with open(self.docker_compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
            
            logger.info("✅ Auto-updater service added to docker-compose.yml")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create auto-updater service: {e}")
            return False
    
    def create_dockerfile(self):
        """Create Dockerfile for the auto-updater"""
        logger.info("🐳 Creating Dockerfile for Qwen auto-updater...")
        
        dockerfile_dir = self.project_root / "docker" / "qwen-auto-updater"
        dockerfile_dir.mkdir(parents=True, exist_ok=True)
        
        dockerfile_content = '''FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    curl \\
    docker.io \\
    cron \\
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for auto-updater
RUN pip install --no-cache-dir \\
    schedule \\
    pyyaml \\
    psycopg2-binary \\
    requests

# Copy application code
COPY qwen_auto_updater.py .
COPY project_root / 'config' /  ./project_root / 'config' / 

# Create directories for logs and backups
RUN mkdir -p logs backups/models backups/database temp/downloads

# Set permissions
RUN chmod +x qwen_auto_updater.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import subprocess; subprocess.run(['python', 'qwen_auto_updater.py', 'status'], check=True)"

# Default command
CMD ["python", "qwen_auto_updater.py", "daemon"]
'''
        
        dockerfile_path = dockerfile_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        logger.info(f"✅ Dockerfile created: {dockerfile_path}")
        return True
    
    def build_and_start_service(self):
        """Build and start the auto-updater service"""
        logger.info("🚀 Building and starting Qwen auto-updater service...")
        
        try:
            # Build the service
            build_cmd = ["docker-compose", "build", self.updater_service_name]
            logger.info(f"Building: {' '.join(build_cmd)}")
            
            result = subprocess.run(build_cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Build failed: {result.stderr}")
                return False
            
            logger.info("✅ Auto-updater service built successfully")
            
            # Start the service
            start_cmd = ["docker-compose", "up", "-d", self.updater_service_name]
            logger.info(f"Starting: {' '.join(start_cmd)}")
            
            result = subprocess.run(start_cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Start failed: {result.stderr}")
                return False
            
            logger.info("✅ Auto-updater service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to build and start service: {e}")
            return False
    
    def check_service_status(self):
        """Check the status of the auto-updater service"""
        try:
            result = subprocess.run(
                ["docker-compose", "ps", self.updater_service_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("📊 Auto-updater service status:")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ Failed to check service status: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking service status: {e}")
            return False
    
    def view_service_logs(self, follow=False):
        """View logs from the auto-updater service"""
        try:
            cmd = ["docker-compose", "logs"]
            if follow:
                cmd.append("-f")
            cmd.append(self.updater_service_name)
            
            if follow:
                # Stream logs in real-time
                subprocess.run(cmd, cwd=self.project_root)
            else:
                # Get recent logs
                result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    logger.error(f"❌ Failed to get logs: {result.stderr}")
                    
        except KeyboardInterrupt:
            logger.info("⏹️ Log streaming stopped")
        except Exception as e:
            logger.error(f"❌ Error viewing logs: {e}")
    
    def restart_service(self):
        """Restart the auto-updater service"""
        logger.info("🔄 Restarting Qwen auto-updater service...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "restart", self.updater_service_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Auto-updater service restarted successfully")
                return True
            else:
                logger.error(f"❌ Failed to restart service: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restarting service: {e}")
            return False
    
    def setup_complete_environment(self):
        """Setup complete auto-updater environment"""
        logger.info("🏗️ Setting up complete Qwen auto-updater environment...")
        
        try:
            # Step 1: Create Dockerfile
            if not self.create_dockerfile():
                return False
            
            # Step 2: Create Docker Compose service
            if not self.create_updater_service():
                return False
            
            # Step 3: Create default configuration
            self._create_default_config()
            
            # Step 4: Build and start service
            if not self.build_and_start_service():
                return False
            
            logger.info("🎉 Qwen auto-updater environment setup completed!")
            logger.info("📋 Next steps:")
            logger.info("   1. Check service status: python qwen_docker_updater.py status")
            logger.info("   2. View logs: python qwen_docker_updater.py logs")
            logger.info("   3. Configure updates in project_root / 'config' / qwen_updater_config.yaml")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            return False
    
    def _create_default_config(self):
        """Create default configuration files"""
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # This will be created by the main auto-updater when it runs
        logger.info("✅ Configuration directory ready")


def main():
    """Main CLI interface for Docker updater"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qwen2.5 Docker Auto-Updater")
    parser.add_argument("command", choices=[
        "setup", "build", "start", "stop", "restart", 
        "status", "logs", "logs-follow"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    updater = QwenDockerUpdater()
    
    if args.command == "setup":
        success = updater.setup_complete_environment()
        sys.exit(0 if success else 1)
        
    elif args.command == "build":
        success = updater.build_and_start_service()
        sys.exit(0 if success else 1)
        
    elif args.command == "start":
        success = updater.build_and_start_service()
        sys.exit(0 if success else 1)
        
    elif args.command == "stop":
        try:
            subprocess.run(["docker-compose", "stop", updater.updater_service_name], check=True)
            logger.info("✅ Auto-updater service stopped")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to stop service: {e}")
            sys.exit(1)
        
    elif args.command == "restart":
        success = updater.restart_service()
        sys.exit(0 if success else 1)
        
    elif args.command == "status":
        success = updater.check_service_status()
        sys.exit(0 if success else 1)
        
    elif args.command == "logs":
        updater.view_service_logs(follow=False)
        
    elif args.command == "logs-follow":
        updater.view_service_logs(follow=True)


if __name__ == "__main__":
    main()
