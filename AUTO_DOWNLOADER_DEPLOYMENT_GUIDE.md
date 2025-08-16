# 🤖 Auto-Downloader Deployment Guide

## Current Status: ✅ FULLY INTEGRATED

The auto-downloader has been properly integrated into the Docker microservices architecture with correct file paths, USER_NAME permissions, and multiple deployment options.

## 📁 File Structure Status

### ✅ Dockerfile Paths Fixed

- **Main**: `docker/dockerfiles/Dockerfile` (✅ 1420 bytes)
- **Auto-downloader config**: Uses proper paths with USER_NAME integration
- **All requirements**: Organized in `docker/requirements/`

### ✅ Configuration Files

- **Standalone**: `configs/docker/docker-compose.auto-downloader.yml`
- **Integrated**: Added to `docker-compose.clean.yml` (main microservices)
- **Legacy**: Available in `docker-compose.yml` (reference)

## 🚀 Deployment Options

### Option 1: Clean Microservices (RECOMMENDED)

```bash
# Start with auto-downloader included
docker-compose -f docker-compose.clean.yml --profile auto-downloader up -d

# Check status
docker-compose -f docker-compose.clean.yml --profile auto-downloader ps

# View logs
docker-compose -f docker-compose.clean.yml --profile auto-downloader logs -f auto-downloader
```

### Option 2: Standalone Auto-Downloader

```bash
# Navigate to configs directory
cd configs/docker

# Start standalone auto-downloader
docker-compose -f docker-compose.auto-downloader.yml up -d

# Test mode (run once)
docker-compose -f docker-compose.auto-downloader.yml --profile test up auto-downloader-test
```

### Option 3: Legacy Full System

```bash
# Start the complete legacy system (11+ services including auto-downloader)
docker-compose up -d auto-downloader
```

## 🔧 Configuration Details

### Environment Variables (from .env)

```bash
USER_NAME=jc
USER_ID=1000
GROUP_ID=1000
HORSERACE_DB_USERNAME=your_username
HORSERACE_DB_PASSWORD=your_password
HORSERACE_DB_RESULTS_URL=your_results_url
HORSERACE_DB_CARDS_URL=your_cards_url
```

### Auto-Downloader Features

- **Scheduled Mode**: Runs continuously with automatic scheduling
- **Browser Optimization**: 2GB shared memory, Chrome/Chromium support
- **Resource Limits**: 3GB RAM, 1.5 CPU cores max
- **Health Checks**: 5-minute intervals with Docker config validation
- **Error Handling**: Comprehensive logging and retry mechanisms
- **Database Integration**: PostgreSQL and Redis connectivity

## 🏗️ Architecture Integration

### In Clean Microservices (`docker-compose.clean.yml`)

```yaml
services:
  auto-downloader:
    build:
      dockerfile: docker/dockerfiles/Dockerfile
      args:
        USER_NAME: ${USER_NAME:-jc}
    profiles:
      - auto-downloader # Optional service
    depends_on:
      - postgres
      - redis
```

### Service Dependencies

1. **PostgreSQL**: Database storage for downloaded data
2. **Redis**: Caching and coordination
3. **Data Pipeline**: Coordinates with main data processing
4. **ML Trainer**: Provides data for training cycles

## 🎯 Best Practices

### 1. Use Profile-Based Deployment

```bash
# Only start auto-downloader when needed
docker-compose -f docker-compose.clean.yml --profile auto-downloader up -d
```

### 2. Monitor Resource Usage

```bash
# Check memory and CPU usage
docker stats horse_racing_auto_downloader
```

### 3. Log Management

```bash
# Tail logs with timestamps
docker-compose -f docker-compose.clean.yml logs -f -t auto-downloader
```

### 4. Browser Debugging

```bash
# For development, disable headless mode
docker-compose -f docker-compose.clean.yml exec auto-downloader \
  bash -c "HEADLESS=false python run_docker_auto_downloader.py --mode once"
```

## 🔍 Troubleshooting

### Permission Issues

- Ensure USER_NAME, USER_ID, GROUP_ID are set in .env
- All containers now use the same user permissions (jc:1000:1000)

### Browser Issues

- Containers include `seccomp:unconfined` for Chrome compatibility
- 2GB shared memory allocated for browser stability

### Memory Issues

- Auto-downloader limited to 3GB RAM
- Use `docker system prune` to clean up unused resources

## ✅ Validation Commands

```bash
# Check all Docker files exist
ls -la docker/dockerfiles/Dockerfile*

# Verify auto-downloader configuration
docker-compose -f docker-compose.clean.yml config | grep -A 20 auto-downloader

# Test auto-downloader build
docker-compose -f docker-compose.clean.yml build auto-downloader
```

The auto-downloader is now fully integrated with proper microservices architecture, correct file paths, USER_NAME permissions, and multiple deployment options! 🎉
