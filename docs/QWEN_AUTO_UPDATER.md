# 🤖 Qwen2.5 Auto-Updater System

## Overview

The Qwen2.5 Auto-Updater is a comprehensive system designed to automatically maintain and update your Qwen2.5 model and its associated database. This ensures your AI model stays current with the latest improvements and your database remains optimized for peak performance.

## 🚀 Quick Start

### 1. Automated Setup
```bash
# Run the automated setup script
./setup_qwen_updater.sh
```

### 2. Manual Setup
```bash
# Install dependencies
pip install pyyaml schedule psycopg2-binary requests

# Create directories
mkdir -p {config,logs,backups/{models,database},temp/downloads}

# Setup Docker environment
python qwen_docker_updater.py setup
```

## 📊 Features

### Model Management
- ✅ **Automatic Model Updates**: Detects and installs Qwen2.5 model updates
- ✅ **Performance Monitoring**: Tracks model response times and health
- ✅ **Backup & Rollback**: Automatic backups with rollback on failure
- ✅ **Version Comparison**: Intelligent version detection and comparison
- ✅ **Health Checks**: Regular model responsiveness testing

### Database Management
- ✅ **Data Freshness Monitoring**: Tracks when data was last updated
- ✅ **Schema Optimization**: Automatic database performance tuning
- ✅ **Index Management**: Creates and maintains optimal indexes
- ✅ **Data Quality Checks**: Identifies and fixes data integrity issues
- ✅ **Automated Backups**: Regular database backups with retention policy

### Monitoring & Alerting
- ✅ **Real-time Monitoring**: Continuous health and performance tracking
- ✅ **Scheduled Updates**: Configurable update schedules (daily/weekly)
- ✅ **Notification System**: Alerts for critical issues and updates
- ✅ **Performance Metrics**: Detailed performance and usage analytics
- ✅ **Docker Integration**: Full container orchestration support

## 🔧 Configuration

The system uses a YAML configuration file located at `config/qwen_updater_config.yaml`:

```yaml
qwen:
  model_name: "qwen2.5-coder:latest"
  backup_model: "qwen2.5-coder:7b"
  update_schedule: "daily"  # daily, weekly, manual
  auto_pull: true
  check_interval_hours: 24

database:
  host: "localhost"
  port: 5433
  database: "horse_racing_db"
  user: "horse_racing"
  password: "secure_password_123"
  auto_backup: true
  retention_days: 30

monitoring:
  enable_alerts: true
  performance_tracking: true

update_policies:
  require_confirmation: false
  rollback_on_failure: true
  test_new_model: true
```

## 📋 Usage Commands

### Model Operations
```bash
# Check for model updates
python qwen_auto_updater.py check-model

# Update model (with safety checks)
python qwen_auto_updater.py update-model

# Force update (bypass checks)
python qwen_auto_updater.py update-model --force

# View current status
python qwen_auto_updater.py status
```

### Database Operations
```bash
# Check database status
python qwen_auto_updater.py check-db

# Update database
python qwen_auto_updater.py update-db

# View configuration
python qwen_auto_updater.py config
```

### Daemon Mode
```bash
# Run as background daemon
python qwen_auto_updater.py daemon

# Or use systemd (after setup)
sudo systemctl start qwen-auto-updater
sudo systemctl status qwen-auto-updater
```

### Docker Operations
```bash
# Setup Docker environment
python qwen_docker_updater.py setup

# Start Docker service
python qwen_docker_updater.py start

# Check service status
python qwen_docker_updater.py status

# View logs
python qwen_docker_updater.py logs

# Follow logs in real-time
python qwen_docker_updater.py logs-follow

# Restart service
python qwen_docker_updater.py restart
```

## 🏗️ Architecture

### Components

1. **QwenAutoUpdater**: Core updater logic
   - Model update management
   - Database optimization
   - Health monitoring
   - Backup/restore operations

2. **QwenDockerUpdater**: Docker orchestration
   - Container management
   - Service deployment
   - Docker Compose integration

3. **Configuration Manager**: Settings management
   - YAML configuration
   - Environment variables
   - Runtime settings

4. **Monitoring System**: Health and performance tracking
   - Model performance metrics
   - Database health checks
   - Alert notifications

### Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│  Update Check   │───▶│   Execution     │
│   (Daemon)      │    │   (Model/DB)    │    │   (Backup/     │
└─────────────────┘    └─────────────────┘    │    Update)     │
                                              └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   Monitoring    │
                                              │   & Alerts      │
                                              └─────────────────┘
```

## 🔍 Monitoring Dashboard

### Model Status
- **Current Version**: qwen2.5-coder:latest
- **Last Updated**: Auto-detected
- **Response Time**: < 5 seconds
- **Health Status**: ✅ Healthy
- **Next Check**: Scheduled daily at 02:00

### Database Status
- **Data Freshness**: Current (last race: today)
- **Schema Version**: Optimized
- **Index Health**: All indexes present
- **Backup Status**: ✅ Daily backups enabled
- **Storage Usage**: Monitored

### System Metrics
- **Uptime**: Continuous monitoring
- **CPU Usage**: Model execution monitoring
- **Memory Usage**: Resource optimization
- **Disk Space**: Backup storage tracking

## 🚨 Alerting & Notifications

### Alert Types

1. **Critical Alerts** 🚨
   - Model not responding
   - Database connection failure
   - Backup failures

2. **Warning Alerts** ⚠️
   - Slow model response
   - Data becoming stale
   - Storage space low

3. **Info Alerts** ℹ️
   - Updates available
   - Successful updates
   - Scheduled maintenance

### Notification Channels
- **Logs**: Detailed logging to files
- **Console**: Real-time console output
- **Systemd**: Integration with system logging
- **Future**: Slack/Email notifications (configurable)

## 🔧 Troubleshooting

### Common Issues

#### Model Not Updating
```bash
# Check Ollama service
ollama list

# Check model status
python qwen_auto_updater.py check-model

# Force update
python qwen_auto_updater.py update-model --force
```

#### Database Connection Issues
```bash
# Check database connectivity
python qwen_auto_updater.py check-db

# Verify Docker containers
docker-compose ps

# Check database logs
docker-compose logs horse_racing_postgres
```

#### Docker Service Issues
```bash
# Check service status
python qwen_docker_updater.py status

# View service logs
python qwen_docker_updater.py logs

# Restart service
python qwen_docker_updater.py restart

# Rebuild if needed
python qwen_docker_updater.py setup
```

### Log Files
- **Main Logs**: `logs/qwen_auto_updater.log`
- **Docker Logs**: `docker-compose logs qwen-auto-updater`
- **System Logs**: `/var/log/qwen-auto-updater.log` (if using systemd)

## 🔐 Security Considerations

### Database Security
- Use strong passwords
- Limit database access
- Regular backup encryption
- Connection timeout settings

### Model Security
- Verify model sources
- Backup before updates
- Test new models before deployment
- Rollback capabilities

### System Security
- Run with minimal privileges
- Secure configuration files
- Monitor access logs
- Regular security updates

## 📈 Performance Optimization

### Model Performance
- Response time monitoring
- Memory usage optimization
- Concurrent request handling
- Model size considerations

### Database Performance
- Index optimization
- Query performance monitoring
- Connection pooling
- Regular maintenance

### System Performance
- Resource monitoring
- Disk space management
- Network optimization
- Container resource limits

## 🔄 Backup & Recovery

### Automatic Backups
- **Model Backups**: Before each update
- **Database Backups**: Daily scheduled backups
- **Configuration Backups**: Version controlled
- **Retention Policy**: Configurable retention period

### Recovery Procedures
```bash
# Model rollback
python qwen_auto_updater.py rollback-model

# Database restore (manual)
pg_restore -h localhost -p 5433 -U horse_racing -d horse_racing_db backup_file.sql

# Full system restore
docker-compose down
docker-compose up -d
```

## 📝 Maintenance Tasks

### Daily
- ✅ Automated health checks
- ✅ Performance monitoring
- ✅ Log rotation
- ✅ Backup verification

### Weekly
- ✅ Model update checks
- ✅ Database optimization
- ✅ Storage cleanup
- ✅ Security updates

### Monthly
- ✅ Full system review
- ✅ Performance analysis
- ✅ Backup testing
- ✅ Configuration review

## 🚀 Future Enhancements

### Planned Features
- [ ] Web-based monitoring dashboard
- [ ] Advanced ML model comparison
- [ ] Multi-model support
- [ ] Cloud deployment options
- [ ] Advanced analytics integration

### Integration Possibilities
- [ ] Slack/Discord notifications
- [ ] Email alerting system
- [ ] Prometheus metrics export
- [ ] Grafana dashboard integration
- [ ] API endpoint for external monitoring

## 📞 Support

### Getting Help
1. Check the logs: `logs/qwen_auto_updater.log`
2. Verify configuration: `config/qwen_updater_config.yaml`
3. Test components individually
4. Check Docker service status
5. Review system resources

### Useful Commands
```bash
# System status overview
python qwen_auto_updater.py status

# Detailed health check
python qwen_auto_updater.py check-model
python qwen_auto_updater.py check-db

# Docker environment check
python qwen_docker_updater.py status
docker-compose ps
docker-compose logs
```

---

🎉 **Your Qwen2.5 model and database will now stay automatically updated and optimized!**
