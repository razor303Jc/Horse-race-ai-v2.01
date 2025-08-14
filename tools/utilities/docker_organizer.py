#!/usr/bin/env python3
"""
Docker Container Script Organization
====================================

Moves scripts that need to be inside Docker containers to appropriate locations
and updates Dockerfile references accordingly.
"""

import shutil
from pathlib import Path


def organize_docker_scripts():
    """Organize scripts for Docker container deployment"""

    print("🐳 ORGANIZING DOCKER CONTAINER SCRIPTS")
    print("=" * 50)

    # Create Docker-specific directories
    docker_dirs = {
        "docker/scripts": "Scripts that run inside containers",
        "docker/data_pipeline": "Data pipeline scripts for container",
        "docker/automation": "Automation scripts for container",
        "docker/config": "Container configuration files",
    }

    for dir_path, description in docker_dirs.items():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {dir_path} - {description}")

    # Scripts that need to be in Docker containers
    container_scripts = {
        # Main data pipeline (runs in container)
        "docker/data_pipeline": [
            "daily_data_uploader.py",
            "production_pipeline.py",
            "csv_column_mapper.py",
            "data_validator.py",
            "qwen_bigint_solution.py",
        ],
        # Auto downloader (runs in container)
        "docker/automation": [
            "working_auto_downloader.py",
            "run_docker_auto_downloader.py",
            "qwen_auto_downloader.py",
        ],
        # Utility scripts for containers
        "docker/scripts": ["start_web_app.sh", "manage_docker_auto_downloader.sh"],
    }

    # Move scripts to Docker directories
    moved_count = 0
    for target_dir, scripts in container_scripts.items():
        for script in scripts:
            source_path = Path(script)
            if source_path.exists():
                target_path = Path(target_dir) / script

                # Move the file
                shutil.move(str(source_path), str(target_path))
                print(f"  ✅ Moved: {script} → {target_dir}/")
                moved_count += 1
            else:
                print(f"  ⚠️  Not found: {script}")

    # Move Docker compose files to proper location
    compose_files = [
        "configs/docker/docker-compose.auto-downloader.yml",
        "configs/docker/docker-compose.auto-downloader-fixed.yml",
    ]

    for compose_file in compose_files:
        source_path = Path(compose_file)
        if source_path.exists():
            target_path = Path("docker/config") / source_path.name
            shutil.copy2(str(source_path), str(target_path))
            print(f"  📋 Copied: {compose_file} → docker/project_root / 'config' / ")

    print(f"\n📊 Total files moved: {moved_count}")

    # Create updated Dockerfile
    create_updated_dockerfile()

    # Create container deployment guide
    create_deployment_guide()


def create_updated_dockerfile():
    """Create updated Dockerfile with correct paths"""

    dockerfile_content = """# Official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \\
    wget \\
    curl \\
    gnupg \\
    ca-certificates \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional ML dependencies
RUN pip install --no-cache-dir scikit-learn==1.7.1 httpx

# Install Playwright browsers as root first
RUN playwright install --with-deps chromium

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY main.py .
COPY app.py .

# Copy Docker-specific scripts
COPY docker/automation/ ./automation/
COPY docker/data_pipeline/ ./data_pipeline/
COPY docker/scripts/ ./scripts/

# Copy configuration
COPY docker/project_root / 'config' /  ./project_root / 'config' / 

# Copy templates and static files
COPY templates/ ./templates/
COPY static/ ./static/

# Copy essential AI modules (keep in root for compatibility)
COPY ai_modules/ ./ai_modules/

# Copy startup scripts and make executable
COPY docker/scripts/start_web_app.sh ./
RUN chmod +x start_web_app.sh ./scripts/*.sh

# Install the package in development mode
RUN pip install -e .

# Create directories
RUN mkdir -p /app/data /app/logs /app/models /app/cache /app/reports /app/downloads

# Create non-root user and set up permissions
RUN groupadd -r horseai && useradd -r -g horseai -m horseai
RUN chown -R horseai:horseai /app
RUN chmod -R 755 /app/logs /app/data /app/models /app/cache /app/reports /app/downloads

# Install Playwright browsers for the horseai user
USER horseai
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
RUN playwright install chromium

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose ports for web services
EXPOSE 5003 8000

# Default command - can be overridden in docker-compose
CMD ["python", "app.py"]
"""

    with open("Dockerfile.updated", "w") as f:
        f.write(dockerfile_content)

    print("📄 Created: Dockerfile.updated (review and replace Dockerfile)")


def create_deployment_guide():
    """Create deployment guide for Docker containers"""

    guide_content = """# 🐳 Docker Container Deployment Guide

## 📁 Container Script Organization

### **docker/data_pipeline/**
- `daily_data_uploader.py` - Production data uploader
- `production_pipeline.py` - Enterprise pipeline with monitoring  
- `csv_column_mapper.py` - Column mapping and validation
- `data_validator.py` - Data validation utilities
- `qwen_bigint_solution.py` - BIGINT handling solution

### **docker/automation/**
- `working_auto_downloader.py` - Main auto downloader
- `run_docker_auto_downloader.py` - Container entry point
- `qwen_auto_downloader.py` - AI-enhanced downloader

### **docker/scripts/**
- `start_web_app.sh` - Web application startup
- `manage_docker_auto_downloader.sh` - Container management

### **docker/project_root / 'config' / **
- Docker compose configurations
- Container-specific settings

## 🚀 Deployment Commands

### **Data Pipeline Container**
```bash
# Build and start data pipeline
docker-compose up -d postgres
docker-compose run --rm horse-racing-ai python data_pipeline/daily_data_uploader.py

# Monitor pipeline
docker-compose run --rm horse-racing-ai python data_pipeline/production_pipeline.py status
```

### **Auto Downloader Container**
```bash
# Start auto downloader
docker-compose -f docker/project_root / 'config' / docker-compose.auto-downloader.yml up -d

# Check logs
docker logs horserace-auto-downloader -f
```

### **Web Application Container**
```bash
# Start full application stack
docker-compose up -d

# Access web interface
# http://localhost:5003
```

## 🔧 Configuration

### **Environment Variables**
- `HORSERACE_DB_USERNAME` - Database username
- `HORSERACE_DB_PASSWORD` - Database password  
- `POSTGRES_PASSWORD` - PostgreSQL password
- `HEADLESS=true` - Headless browser mode

### **Volume Mounts**
- `./data:/app/data` - Persistent data storage
- `./logs:/app/logs` - Log files
- `./cache:/app/cache` - Cache storage

## 📊 Monitoring

### **Health Checks**
- Database: `pg_isready` checks
- Auto Downloader: Custom validation script
- Web App: HTTP endpoint monitoring

### **Log Access**
```bash
# Container logs
docker-compose logs -f horse-racing-ai
docker logs horserace-auto-downloader -f

# Application logs
docker-compose exec horse-racing-ai tail -f project_root / 'logs' / daily_upload.log
```

---
*Container organization completed: Auto-organized Docker deployment structure*
"""

    with open("docker/DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide_content)

    print("📚 Created: docker/DEPLOYMENT_GUIDE.md")


def main():
    """Main execution"""
    try:
        organize_docker_scripts()

        print("\\n" + "=" * 50)
        print("✅ DOCKER SCRIPT ORGANIZATION COMPLETE!")
        print("🐳 Container-ready structure created")
        print("📋 Next steps:")
        print("   1. Review Dockerfile.updated")
        print("   2. Test container builds")
        print("   3. Update docker-compose references")
        print("   4. Deploy with new structure")

    except Exception as e:
        print(f"❌ Error during organization: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
