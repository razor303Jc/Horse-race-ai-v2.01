# Production Docker Build Configuration

## Overview

The `.dockerignore` file has been optimized for production builds, excluding development files while maintaining security and performance.

## Key Exclusions for Production

### 🚫 **Development Files**

- `.git/`, `.vscode/`, `.idea/` - Version control and IDE files
- `__pycache__/`, `*.pyc` - Python cache files
- `node_modules/` - Node.js dependencies (installed in container)
- `.env*` files - Use environment variables instead

### 🚫 **Data & Logs**

- `data/`, `backups/`, `logs/` - Mounted as volumes, not copied
- `models/`, `trained_models/` - Large files mounted as volumes
- `*.log`, `cache/` - Runtime generated files

### 🚫 **Documentation & Scripts**

- `*.md` files (except README.md)
- `*.sh` scripts (except Docker entrypoints)
- `docs/`, `analysis/` - Not needed in production containers

### 🚫 **Testing & Configuration**

- `tests/`, `pytest.ini` - Test files
- `docker-compose*.yml` - Orchestration files
- `Makefile`, `.flake8` - Development tools

## Service-Specific Inclusions

### **Python Services (Web App, Data Pipeline, ML Trainer)**

```dockerfile
# In Dockerfile, explicitly copy needed files:
COPY src/ /app/src/
COPY config/ /app/config/
COPY docker/requirements/ /app/requirements/
```

### **Node-RED Service**

```dockerfile
# Override exclusions for flows:
COPY flows/ /app/flows/
COPY docker/node-red/ /app/docker/node-red/
```

### **Documentation Service**

```dockerfile
# Override exclusions for docs:
COPY docs/ /docs/docs/
COPY *.md /docs/
```

### **Web Services**

```dockerfile
# Include web assets:
COPY templates/ /app/templates/
COPY static/ /app/static/
```

## Build Size Impact

### **Before .dockerignore**

- All development files included
- Large data directories copied
- Cache and log files included
- Estimated: ~500MB+ per image

### **After .dockerignore**

- Only essential system files
- No unnecessary development files
- Clean production images
- Estimated: ~50-100MB per image

## Security Benefits

1. **No Sensitive Files**: `.env` files and secrets excluded
2. **No Source History**: `.git` directory excluded
3. **No Development Tools**: IDEs and dev configs excluded
4. **Minimal Attack Surface**: Only production code included

## Volume Mount Strategy

Instead of copying large files, use volume mounts:

```yaml
volumes:
  - ./data:/app/data:ro # Data files
  - ./logs:/app/logs:rw # Log files
  - ./models:/app/models:ro # ML models
  - ./config:/app/config:ro # Configuration
```

## Dockerfile Best Practices

```dockerfile
# Multi-stage build example
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for layer caching)
COPY docker/requirements/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code (respects .dockerignore)
COPY src/ /app/src/
COPY config/ /app/config/

# Production stage
FROM base as production
WORKDIR /app
USER 1000:1000
CMD ["python", "src/main.py"]
```

## Build Verification

Test your build context size:

```bash
# Check build context size
docker build --dry-run . 2>&1 | grep "build context"

# Build specific service
docker-compose build web-app

# Check image size
docker images | grep horse_racing
```

## Maintenance

Regularly review and update:

1. Check for new file types to exclude
2. Verify service-specific needs
3. Update for new dependencies
4. Monitor build times and sizes

The `.dockerignore` file ensures lean, secure, production-ready Docker images while maintaining all necessary functionality.
