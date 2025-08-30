# Horse Racing AI Network Configuration

## Network Details

- **Network Name**: horse_racing_network
- **Subnet**: 172.20.0.0/16
- **Gateway**: 172.20.0.1
- **Driver**: bridge

## Static IP Assignments

| Service              | Container Name                          | Static IP   | Ports       | Purpose                      |
| -------------------- | --------------------------------------- | ----------- | ----------- | ---------------------------- |
| postgres             | horse_racing_postgres_clean             | 172.20.0.10 | 5432:5432   | Main PostgreSQL Database     |
| redis                | horse_racing_redis_clean                | 172.20.0.11 | -           | Redis Cache & Message Broker |
| web-app              | horse_racing_web_app_clean              | 172.20.0.12 | 3000:8000   | Main Web Application         |
| data-pipeline        | horse_racing_data_pipeline_clean        | 172.20.0.13 | -           | Data Processing Pipeline     |
| ml-trainer           | horse_racing_ml_trainer_clean           | 172.20.0.14 | -           | ML Training Service          |
| node-red             | horse_racing_node_red                   | 172.20.0.15 | 1881:1880   | C2 Command Center Dashboard  |
| live-execution       | horse_racing_live_execution_clean       | 172.20.0.16 | -           | Live Trading Strategy        |
| production-dashboard | horse_racing_production_dashboard_clean | 172.20.0.17 | 5000:5000   | Production Dashboard         |
| alert-system         | horse_racing_alert_system_clean         | 172.20.0.18 | -           | Alert & Notification System  |
| docs                 | horse_racing_docs                       | 172.20.0.19 | 8000        | Documentation Service        |
| news-analyzer        | horse_racing_news_analyzer              | 172.20.0.20 | 11434:11434 | News Analysis with Ollama    |
| reports              | horse_racing_reports_clean              | 172.20.0.21 | -           | Reporting Service            |
| pgadmin              | horse_racing_pgadmin                    | 172.20.0.22 | 8083:80     | PostgreSQL Admin Interface   |
| ntfy                 | horse_racing_ntfy                       | 172.20.0.23 | 8082:80     | Notification Service         |

## Network Architecture Benefits

1. **Predictable IP Addresses**: Each service has a fixed IP that won't change between restarts
2. **Internal DNS Resolution**: Services can communicate using container names or static IPs
3. **Security**: Internal network isolation with controlled external access via ports
4. **Monitoring**: Easier to set up monitoring and logging with known IP addresses
5. **Load Balancing**: Traefik can route to specific IPs for better traffic management

## Connection Examples

### Database Connections

```bash
# Internal connection from any container
postgresql://horse_racing:password@172.20.0.10:5432/database_name
redis://172.20.0.11:6379/0

# External connection
postgresql://horse_racing:password@localhost:5432/database_name
```

### Node-RED C2 Dashboard

```bash
# Internal access
http://172.20.0.15:1880

# External access
http://localhost:1881
```

### Service Communication

```bash
# From any container to web-app
curl http://172.20.0.12:8000/health

# From any container to Node-RED
curl http://172.20.0.15:1880
```

## Network Management Commands

```bash
# Start the complete stack
docker-compose -f docker-compose.clean.yml up -d

# Check network details
docker network inspect horse_racing_network

# View container IPs
docker network inspect horse_racing_network | jq '.[0].Containers'

# Test connectivity between containers
docker exec horse_racing_web_app_clean ping 172.20.0.10
```

## Troubleshooting

If you encounter IP conflicts:

1. Stop all containers: `docker-compose -f docker-compose.clean.yml down`
2. Remove the network: `docker network rm horse_racing_network`
3. Restart the stack: `docker-compose -f docker-compose.clean.yml up -d`

The Docker daemon will automatically recreate the network with the specified configuration.
