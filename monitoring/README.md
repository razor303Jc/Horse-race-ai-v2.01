# Monitoring Infrastructure

This directory contains the monitoring infrastructure for the Horse Racing AI system, featuring Prometheus metrics collection and Grafana visualization dashboards.

## Components

### Prometheus

- **Purpose**: Metrics collection and monitoring
- **Access**: http://prometheus.horserace.local
- **Configuration**: `prometheus.yml`

### Grafana

- **Purpose**: Metrics visualization and dashboards
- **Access**: http://grafana.horserace.local
- **Credentials**: admin / horseracing2024
- **Configuration**: `grafana.ini`

### Exporters

#### PostgreSQL Exporter

- **Purpose**: Database metrics collection
- **Port**: 9187
- **Configuration**: `postgres-exporter-queries.yaml`

#### Redis Exporter

- **Purpose**: Cache metrics collection
- **Port**: 9121

#### cAdvisor

- **Purpose**: Container resource metrics
- **Port**: 8080

#### Node Exporter

- **Purpose**: System metrics collection
- **Port**: 9100

## Setup Instructions

1. **Start monitoring stack with Traefik**:

   ```bash
   docker-compose up prometheus grafana postgres-exporter redis-exporter cadvisor node-exporter
   ```

2. **Access dashboards**:

   - Prometheus: http://prometheus.horserace.local
   - Grafana: http://grafana.horserace.local

3. **Import additional dashboards** (optional):
   - Go to Grafana → Dashboards → Import
   - Use dashboard IDs from https://grafana.com/grafana/dashboards/

## Key Metrics

### Application Metrics

- HTTP request rates and response times
- API endpoint performance
- Service uptime status

### Database Metrics

- Connection counts
- Query performance
- Table statistics
- Race data volumes

### System Metrics

- CPU and memory usage
- Disk I/O performance
- Network traffic
- Container resource consumption

### Business Metrics

- Total races processed
- Horse/jockey/trainer counts
- Recent activity (24h windows)
- Pipeline execution status

## Dashboard Panels

The default dashboard (`grafana-dashboard.json`) includes:

1. **HTTP Request Rate**: Real-time API traffic
2. **Service Uptime**: Health status of all services
3. **Database Connections**: PostgreSQL connection monitoring
4. **Redis Performance**: Cache hit rates and memory usage
5. **System Resources**: CPU/Memory/Disk usage
6. **Race Data Metrics**: Business-specific KPIs

## Alerting (Future Enhancement)

Planned alert conditions:

- Service downtime
- High error rates (>5%)
- Database connection failures
- Memory usage >85%
- Disk space <10%

## Configuration Files

- `prometheus.yml`: Prometheus scraping configuration
- `grafana.ini`: Grafana server configuration
- `grafana-dashboard.json`: Default monitoring dashboard
- `postgres-exporter-queries.yaml`: Custom PostgreSQL metrics

## Troubleshooting

### Common Issues

1. **Grafana shows "No data"**:

   - Check Prometheus targets: http://prometheus.horserace.local/targets
   - Verify all exporters are running

2. **PostgreSQL exporter fails**:

   - Check database credentials in docker-compose.yml
   - Verify queries.yaml syntax

3. **cAdvisor permission errors**:
   - Ensure Docker daemon is accessible
   - Check privileged mode is enabled

### Logs

```bash
# View service logs
docker logs horse_racing_prometheus
docker logs horse_racing_grafana
docker logs horse_racing_postgres_exporter
```

## Performance Considerations

- Prometheus retention: 200 hours (configurable)
- Scrape interval: 15 seconds
- Data volume: ~50MB/day for typical workload
- Dashboard refresh: 30 seconds

## Security Notes

- Grafana has anonymous access enabled for development
- Production deployments should disable anonymous access
- Consider adding authentication to Prometheus
- Monitor access logs for unusual activity
