# Docker Development Environment

Complete guide for developing within Docker containers.

## Overview

The Horse Racing AI v2.0 project uses a fully containerized development environment. All development, testing, and documentation happens inside Docker containers.

## Development Stack

### Core Containers

1. **PostgreSQL** (`postgres:15-alpine`)
   - Primary database
   - Persistent data storage
   - Health checks enabled

2. **Redis** (`redis:7-alpine`)
   - Caching layer
   - Session storage
   - Real-time data caching

3. **NTFY** (`binwiederhier/ntfy:latest`)
   - Notification system
   - Real-time alerts
   - Web UI for testing

4. **Web Application** (`horse-racing-web`)
   - Flask-based web interface
   - Live reload enabled
   - Source code mounted

5. **Test Container** (`horse-racing-test`)
   - Isolated test environment
   - Comprehensive test suite
   - CI/CD integration

6. **MkDocs** (`squidfunk/mkdocs-material`)
   - Live documentation
   - Material theme
   - Auto-rebuild on changes

## Getting Started

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd Horse-race-ai-v2.0

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 2. Start Development Environment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access Services

- **Web App**: http://localhost:3000
- **Documentation**: http://localhost:8000
- **NTFY**: http://localhost:8080
- **Database**: localhost:5432 (via client)

## Development Workflow

### Container Management

```bash
# Start development environment
docker-compose --profile dev up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart web

# View logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash
```

### Live Development

1. **Source Code Changes**:
   - Files are mounted as volumes
   - Changes reflect immediately
   - Flask auto-reloads on changes

2. **Database Changes**:
   - Schema changes persist
   - Use migrations for versioning
   - Backup important data

3. **Configuration Changes**:
   - Restart containers after config changes
   - Environment variables loaded on startup

### Git Integration

The project includes automated Git hooks:

#### Pre-commit Hook

- Runs automatically before commits
- Executes linting and quick tests
- Validates Docker environment
- Checks for sensitive data

#### Post-commit Hook

- Manages container restarts
- Provides development suggestions
- Monitors dependency changes

### Testing Integration

```bash
# Run full test suite
docker-compose -f docker-compose.test.yml up --build

# Run specific test category
docker-compose exec test pytest tests/unit/

# Run with coverage
docker-compose exec test pytest --cov=src tests/

# Watch mode for development
docker-compose exec test pytest-watch
```

## Development Best Practices

### Code Organization

```
src/
├── core/           # Core business logic
├── models/         # Database models
├── api/            # API endpoints
├── services/       # Business services
├── utils/          # Utility functions
└── config/         # Configuration

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py     # Test configuration
```

### Database Development

1. **Migrations**:

   ```bash
   # Create migration
   docker-compose exec web flask db migrate -m "Description"

   # Apply migration
   docker-compose exec web flask db upgrade
   ```

2. **Database Console**:

   ```bash
   # Access PostgreSQL
   docker-compose exec postgres psql -U racing_user -d horse_racing

   # Redis CLI
   docker-compose exec redis redis-cli
   ```

### Debugging

1. **Application Debugging**:

   ```bash
   # View application logs
   docker-compose logs -f web

   # Access Python debugger
   docker-compose exec web python -c "import pdb; pdb.set_trace()"
   ```

2. **Database Debugging**:

   ```bash
   # Check database connections
   docker-compose exec postgres pg_isready

   # View database logs
   docker-compose logs postgres
   ```

3. **Performance Monitoring**:

   ```bash
   # Monitor container resources
   docker stats

   # Check container health
   docker-compose ps
   ```

### Environment Configuration

#### Development Variables (.env)

```bash
# Application
DEBUG=true
FLASK_ENV=development
SECRET_KEY=dev-secret-key

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=horse_racing
POSTGRES_USER=racing_user
POSTGRES_PASSWORD=dev_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# NTFY
NTFY_URL=http://ntfy:8080
NTFY_TOPIC=horse-racing-dev

# Testing
TEST_DATABASE_URL=postgresql://racing_user:dev_password@postgres-test:5432/horse_racing_test
```

## Container Customization

### Building Custom Images

```bash
# Build development image
docker-compose build web

# Build test image
docker-compose -f docker-compose.test.yml build

# Build with no cache
docker-compose build --no-cache web
```

### Volume Management

```bash
# List volumes
docker volume ls

# Backup database
docker-compose exec postgres pg_dump -U racing_user horse_racing > backup.sql

# Restore database
docker-compose exec -T postgres psql -U racing_user horse_racing < backup.sql
```

### Networking

```bash
# List networks
docker network ls

# Inspect network
docker network inspect horse-race-ai-v20_default

# Connect to external services
# Use host.docker.internal for host machine services
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**:

   ```bash
   # Check port usage
   netstat -tulpn | grep :3000

   # Change ports in docker-compose.yml
   ```

2. **Volume Permissions**:

   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER .

   # Set proper permissions
   chmod 755 scripts/*.sh
   ```

3. **Database Connection Issues**:

   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres

   # Check connection
   docker-compose exec postgres pg_isready
   ```

### Performance Optimization

1. **Resource Allocation**:
   - Set appropriate memory limits
   - Configure CPU limits
   - Use multi-stage builds

2. **Volume Optimization**:
   - Use named volumes for data
   - Bind mounts for development
   - Cache dependencies

3. **Network Optimization**:
   - Use internal networks
   - Minimize external calls
   - Implement connection pooling

## Next Steps

- [Testing Guide](../testing/overview.md)
- [Git Workflow](git-workflow.md)
- [Code Style](code-style.md)
- [API Documentation](../api/core.md)
