# Horse Racing AI - Docker Quick Reference

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Copy and edit environment configuration
cp .env.template .env
nano .env  # Edit with your settings

# Deploy the complete stack
./deploy-docker.sh deploy
```

### 2. Management Commands

```bash
# View all services status
./deploy-docker.sh status

# View live logs
./deploy-docker.sh logs

# Restart all services
./deploy-docker.sh restart

# Stop all services
./deploy-docker.sh stop

# Clean everything (removes data!)
./deploy-docker.sh clean
```

## 🌐 Service URLs

After deployment, access services via:

| Service             | URL                                     | Purpose                  |
| ------------------- | --------------------------------------- | ------------------------ |
| **Main App**        | `https://horse-racing.{DOMAIN}`         | Web interface & API      |
| **Database Admin**  | `https://pgadmin.horse-racing.{DOMAIN}` | PostgreSQL management    |
| **Notifications**   | `https://ntfy.horse-racing.{DOMAIN}`    | NTFY web interface       |
| **Scraper Monitor** | `https://scraper.horse-racing.{DOMAIN}` | Scraper health dashboard |

## 🔧 Individual Service Management

### Start specific service

```bash
docker-compose up -d postgres
docker-compose up -d redis
docker-compose up -d ntfy
docker-compose up -d horse-racing-ai
docker-compose up -d scraper
```

### View service logs

```bash
docker-compose logs -f horse-racing-ai
docker-compose logs -f scraper
docker-compose logs -f ntfy
```

### Restart specific service

```bash
docker-compose restart horse-racing-ai
docker-compose restart scraper
```

### Execute commands in containers

```bash
# Access main app shell
docker-compose exec horse-racing-ai bash

# Access database
docker-compose exec postgres psql -U horse_racing horse_racing_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

## 📊 Monitoring & Health Checks

### Check all container health

```bash
docker-compose ps
```

### View resource usage

```bash
docker stats
```

### Container health details

```bash
docker inspect horse_racing_app --format='{{.State.Health.Status}}'
```

## 🗄️ Database Operations

### Backup database

```bash
docker-compose exec postgres pg_dump -U horse_racing horse_racing_db > backup.sql
```

### Restore database

```bash
docker-compose exec -T postgres psql -U horse_racing horse_racing_db < backup.sql
```

### Access database directly

```bash
docker-compose exec postgres psql -U horse_racing horse_racing_db
```

## 🔔 NTFY Management

### Test notification

```bash
# Replace {DOMAIN} with your actual domain
curl -d "Test message" https://ntfy.horse-racing.{DOMAIN}/horse-racing-alerts
```

### High priority notification

```bash
curl -H "Priority: high" \
     -H "Title: 🚨 Alert" \
     -d "Important message" \
     https://ntfy.horse-racing.{DOMAIN}/horse_racing_alerts_betting
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs for errors
docker-compose logs service-name

# Rebuild image
docker-compose build --no-cache service-name
docker-compose up -d service-name
```

### Permission issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/ cache/ logs/
chmod -R 755 data/ cache/ logs/
```

### Network issues

```bash
# Recreate networks
docker network rm traefik horse_racing_network
docker network create traefik
docker-compose up -d
```

### Database connection issues

```bash
# Check database is running
docker-compose exec postgres pg_isready -U horse_racing

# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait for startup, then start other services
```

### Clear all data and restart

```bash
# WARNING: This removes all data!
docker-compose down -v --remove-orphans
docker system prune -a -f
./deploy-docker.sh deploy
```

## 📝 Configuration Files

### Key files to customize

- `.env` - Environment variables
- `docker-compose.yml` - Service configuration
- `docker/pgadmin/servers.json` - Database admin config

### Environment variables reference

```bash
# Domain configuration
DOMAIN=yourdomain.com

# Database settings
POSTGRES_PASSWORD=secure_password_123
REDIS_PASSWORD=redis_password_123

# Application settings
DEBUG=false
LOG_LEVEL=INFO

# NTFY topics
NTFY_TOPIC=horse-racing-alerts
```

## 🔐 Security Considerations

### Update default passwords

```bash
# Generate secure passwords
openssl rand -base64 32  # For database passwords
openssl rand -hex 32     # For API keys
```

### SSL/TLS Configuration

- Ensure Traefik is configured with Let's Encrypt
- Use strong authentication middleware
- Regularly update container images

### Backup Strategy

```bash
# Create automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U horse_racing horse_racing_db > "backup_${DATE}.sql"
```

## 📈 Performance Optimization

### Monitor resource usage

```bash
# Container resource usage
docker stats --no-stream

# System resource usage
htop
df -h
```

### Optimize for production

```bash
# Limit container resources in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## 🚨 Emergency Procedures

### Quick service recovery

```bash
# If services are unresponsive
docker-compose restart

# If containers are corrupted
docker-compose down
docker-compose up -d --force-recreate
```

### Data recovery

```bash
# If only database data is intact
docker-compose down
docker volume ls  # Check volume exists
docker-compose up -d postgres
# Wait for database, then start other services
```
