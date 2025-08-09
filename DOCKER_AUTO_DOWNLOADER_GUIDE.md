# Docker Auto Downloader Setup - Complete Guide

## 🐳 Overview

The horse racing auto downloader has been optimized for Docker containers with the following key features:

### ✅ Docker Optimizations

1. **Headless Browser Configuration**

   - Always runs headless in containers (`headless: true`)
   - Docker-optimized Chromium arguments for stability
   - Memory and resource management for containers

2. **Container-Specific Arguments**

   ```
   --no-sandbox
   --disable-dev-shm-usage
   --disable-gpu
   --single-process
   --memory-pressure-off
   --disable-images (for performance)
   ```

3. **Environment Detection**
   - Automatically detects Docker environment
   - Uses different configurations for local vs container
   - Optimized resource usage in containers

## 🚀 Quick Start

### Option 1: Using Management Script

```bash
# Build and start the auto downloader
./manage_docker_auto_downloader.sh build
./manage_docker_auto_downloader.sh start

# Test one-time download
./manage_docker_auto_downloader.sh test

# View logs
./manage_docker_auto_downloader.sh logs
```

### Option 2: Using Docker Compose Directly

```bash
# Start scheduled downloader (runs daily at 00:01)
docker compose -f docker-compose.auto-downloader.yml up -d auto-downloader

# Run one-time test
docker compose -f docker-compose.auto-downloader.yml --profile test run auto-downloader-test
```

### Option 3: Direct Python Script

```bash
# Inside container
python run_docker_auto_downloader.py --mode once
python run_docker_auto_downloader.py --mode scheduled
```

## 🔧 Configuration Files

### 1. `docker-compose.auto-downloader.yml`

- Production auto downloader service
- Health checks and resource limits
- Environment variable management
- Persistent data volumes

### 2. `run_docker_auto_downloader.py`

- Docker-specific runner script
- Environment validation
- Logging configuration
- Scheduled vs one-time execution

### 3. `src/automation/docker_config.py`

- Docker-optimized configuration
- Browser arguments for containers
- Directory setup and validation
- Environment detection

### 4. `manage_docker_auto_downloader.sh`

- Management script for easy operations
- Start/stop/restart/test commands
- Log viewing and status checking
- Build and cleanup utilities

## 📁 Directory Structure

```
/app/
├── data/
│   └── daily_downloads/     # Downloaded race data
│       └── backups/         # Backup files
├── logs/                    # Application logs
├── cache/                   # Browser cache
├── .playwright/             # Playwright browsers
└── src/automation/          # Auto downloader code
```

## 🌐 Environment Variables

Required in `.env` file or Docker environment:

```bash
# WooCommerce Integration
HORSERACE_DB_USERNAME=your_username
HORSERACE_DB_PASSWORD=your_password
HORSERACE_DB_RESULTS_URL=https://horseracedatabase.com/...
HORSERACE_DB_CARDS_URL=https://horseracedatabase.com/...

# Docker Configuration
DOCKER_CONTAINER=true
HEADLESS=true
PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
LOG_LEVEL=INFO
```

## 🚦 Service Management

### Start Auto Downloader

```bash
./manage_docker_auto_downloader.sh start
```

- Starts scheduled service (runs daily at 00:01 UTC)
- Creates necessary Docker networks
- Mounts persistent volumes for data/logs

### Test Download

```bash
./manage_docker_auto_downloader.sh test
```

- Runs one-time download for testing
- Uses DEBUG logging level
- Validates configuration and connection

### Monitor Logs

```bash
./manage_docker_auto_downloader.sh logs
```

- Shows real-time logs from auto downloader
- Use Ctrl+C to exit log viewing

### Check Status

```bash
./manage_docker_auto_downloader.sh status
```

- Shows container status and health
- Displays recent log entries
- Indicates if service is running properly

## 🔄 Auto Downloader Workflow

1. **Human-Like Login**

   - Character-by-character typing with delays
   - Modal handling (newsletter popups)
   - Session cookie extraction

2. **WooCommerce Downloads**

   - Authenticated direct URL downloads
   - Results.zip and cards.zip files
   - Timestamped file naming

3. **Fallback to Scraping**

   - If WooCommerce fails, falls back to web scraping
   - Respectful rate limiting (12 req/min in containers)
   - Proper delays between requests

4. **Data Management**
   - Files saved to `/app/data/daily_downloads/`
   - Automatic backup creation
   - Log rotation and management

## 🎛️ Configuration Options

### Production (Scheduled)

- Runs daily at 00:01 UTC
- Memory limit: 2GB
- CPU limit: 1.0 cores
- Restart policy: unless-stopped

### Development/Testing

- Run once and exit
- DEBUG logging level
- No resource limits
- Manual execution

## 🏥 Health Monitoring

The container includes health checks:

- Validates Docker environment setup
- Checks Playwright installation
- Monitors container resource usage
- 30-minute check intervals

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**

   - Ensure proper volume permissions
   - Check user `horseai` has access to mounted directories

2. **Playwright Installation**

   - Browsers are installed during image build
   - Use `PLAYWRIGHT_BROWSERS_PATH=/app/.playwright`

3. **Memory Issues**

   - Container limited to 2GB RAM
   - Increase if needed in docker-compose.yml

4. **Network Connectivity**
   - Ensure horserace-network exists
   - Check external network access

### Debug Commands

```bash
# Check container logs
docker logs horserace-auto-downloader

# Enter container for debugging
docker exec -it horserace-auto-downloader bash

# Test configuration
docker exec horserace-auto-downloader python src/automation/docker_config.py

# Manual run inside container
docker exec horserace-auto-downloader python run_docker_auto_downloader.py --mode once --log-level DEBUG
```

## 📊 Performance Considerations

### Container Optimizations

- Single process mode for stability
- Disabled images and unnecessary features
- Memory pressure management
- GPU acceleration disabled

### Network Efficiency

- Reduced request rate (12/min vs 15/min)
- Compressed data transfer
- Connection reuse

### Storage Management

- Automatic cleanup of old downloads
- Log rotation policies
- Backup retention schedules

## 🔐 Security

### Container Security

- Non-root user execution (`horseai`)
- Read-only filesystem where possible
- Minimal attack surface
- No unnecessary network exposure

### Data Protection

- Secure credential handling
- Encrypted data transfer
- Session management
- Audit logging

The Docker setup provides a robust, scalable, and secure environment for automated horse racing data collection! 🏇
