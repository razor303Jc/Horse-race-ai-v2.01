# 🐳 Docker Container Deployment Guide

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

### **docker/config/**
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
docker-compose -f docker/config/docker-compose.auto-downloader.yml up -d

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
docker-compose exec horse-racing-ai tail -f logs/daily_upload.log
```

---
*Container organization completed: Auto-organized Docker deployment structure*
