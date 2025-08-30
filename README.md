# Horse Race AI v2.05 - Clean Architecture

## Project Structure

This is a clean rebuild of the Horse Race AI system with improved architecture and organization.

### Directory Structure

```
Horse-race-ai-v2.05/
├── api/                    # API endpoints and services
├── backups/               # System backups
├── c2_protected_files/    # C2 Command Center protected files
├── config/                # Configuration files
├── data/                  # Data storage
├── docker/                # Docker configurations
├── docs/                  # Documentation
├── logs/                  # System logs
├── models/                # ML models
├── monitoring/            # System monitoring
├── results/               # Analysis results
├── scripts/               # Utility scripts
├── src/                   # Source code
├── tests/                 # Test suites
└── tools/                 # Development tools
```

### Key Components

#### Docker Infrastructure
- **docker-compose.clean.yml**: Main clean docker compose configuration
- **docker-compose.node-red.yml**: Node-RED specific configuration
- **docker-compose.monitoring.yml**: Monitoring stack
- **docker-compose.traefik.yml**: Traefik reverse proxy
- **docker/requirements/**: All Docker requirement files organized by service

#### C2 Command Center (Protected)
- Complete C2 system with 987 protected files
- Node-RED flows and configurations
- API endpoints and test framework
- Real-time dashboard and monitoring

#### Core APIs
- **api/prediction_api.py**: Main prediction API
- **api/ml_management_api.py**: ML model management API
- **api/requirements.txt**: API-specific requirements

### Getting Started

1. **Start Services**
   ```bash
   # Start the clean architecture
   docker-compose -f docker-compose.clean.yml up -d
   ```

2. **C2 Command Center**
   ```bash
   # Access via: http://localhost:1880 (Node-RED)
   # API access via: http://localhost:8000
   ```

### Essential Files Status

✅ **Docker Infrastructure**: Complete
✅ **API Layer**: Complete  
✅ **Configuration**: Complete
✅ **Core Scripts**: Complete
✅ **C2 Protected Files**: Complete (987 files)

### Next Steps

1. Copy additional source code from v2.04
2. Copy tools and test suites
3. Data and model migration

---
*Generated: August 30, 2025*
*Infrastructure Complete - Ready for Source Code Migration*
