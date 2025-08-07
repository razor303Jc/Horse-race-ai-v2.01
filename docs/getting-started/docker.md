# Docker Setup

This guide covers setting up the Horse Racing AI v2.0 system using Docker containers.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- Git
- 4GB+ RAM available
- 10GB+ disk space

## Services Overview

The system consists of multiple interconnected services:

### Core Services

- **PostgreSQL**: Primary database for race data and analysis
- **Redis**: Caching layer for performance optimization
- **NTFY**: Notification server for real-time alerts

### Application Services

- **Web App**: Flask-based web interface
- **ML Engine**: Machine learning processing
- **Data Collector**: Automated data scraping

### Development Services

- **Test Container**: Isolated testing environment
- **MkDocs**: Live documentation server

## Quick Start

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Horse-race-ai-v2.0
   ```

2. **Create environment file**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**:

   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

## Service Access

- **Web Application**: http://localhost:3000
- **Documentation**: http://localhost:8000
- **NTFY Notifications**: http://localhost:8080
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Development Workflow

### Container-Based Development

All development happens inside containers:

```bash
# Start development environment
docker-compose up -d

# Access application container
docker-compose exec web bash

# Run tests in test container
docker-compose -f docker-compose.test.yml up --build
```

### Git Hooks Integration

The system includes automated Git hooks:

- **Pre-commit**: Runs linting and tests before commits
- **Post-commit**: Manages container restarts and suggestions

### Live Reload

Development containers support live reload:

- **Source Code**: Mounted as volumes for instant changes
- **Documentation**: MkDocs auto-rebuilds on file changes
- **Tests**: Test container monitors for changes

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=horse_racing
POSTGRES_USER=racing_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# NTFY
NTFY_URL=http://ntfy:8080
NTFY_TOPIC=horse-racing-alerts

# Application
DEBUG=true
SECRET_KEY=your-secret-key
```

### Docker Compose Profiles

Use profiles to control which services run:

```bash
# Development profile (includes docs and testing)
docker-compose --profile dev up -d

# Production profile (core services only)
docker-compose --profile prod up -d

# Testing profile
docker-compose --profile test up -d
```

## Volume Management

### Persistent Data

- **PostgreSQL Data**: `postgres_data` volume
- **Redis Data**: `redis_data` volume
- **Application Logs**: `app_logs` volume

### Development Volumes

- **Source Code**: Bind mount for live editing
- **Test Results**: Persistent test artifacts
- **Documentation**: Live documentation updates

## Networking

Services communicate via Docker networks:

- **Default Network**: Core application services
- **Test Network**: Isolated testing environment
- **External Access**: Traefik reverse proxy (optional)

## Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# View service logs
docker-compose logs -f web

# Monitor resource usage
docker stats
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 3000, 5432, 6379, 8000, 8080 are available
2. **Memory Issues**: Increase Docker memory allocation
3. **Permission Issues**: Check file permissions for mounted volumes

### Debug Commands

```bash
# View all container logs
docker-compose logs

# Access container shell
docker-compose exec service_name bash

# Restart specific service
docker-compose restart service_name

# Rebuild and restart
docker-compose up --build -d
```

### Performance Optimization

- **Resource Limits**: Set appropriate CPU/memory limits
- **Volume Optimization**: Use named volumes for better performance
- **Network Optimization**: Use internal networks for service communication

## Next Steps

- [Development Setup](../development/setup.md)
- [Testing Guide](../testing/overview.md)
- [API Documentation](../api/core.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
