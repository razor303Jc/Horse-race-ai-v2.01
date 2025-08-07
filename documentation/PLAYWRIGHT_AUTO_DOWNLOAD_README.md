# Playwright Auto-Download System

## Overview

The Playwright Auto-Download System is a comprehensive solution for collecting real horse racing data and gradually integrating it with synthetic training data. This system serves as both a primary data collection tool and a backup when APIs are unavailable.

## System Components

### 1. Enhanced Playwright Auto-Download (`enhanced_playwright_auto_download.py`)

**Purpose**: Comprehensive real racing data collection from multiple sources

**Features**:

- Multi-source data scraping (Racing Post, Timeform, At The Races, Racing UK)
- Stealth browsing with realistic user simulation
- Real-time data conversion to training format
- Betting odds extraction and validation
- Performance history generation
- Rich console UI with progress tracking

**Key Capabilities**:

```python
# Collect data from multiple sources
scraper = EnhancedPlaywrightAutoDownload()
await scraper.collect_daily_racing_data()

# Get specific race data
race_data = await scraper.scrape_race_card("racing_post", race_url)

# Convert to training format
training_data = scraper.convert_to_training_format(race_data)
```

### 2. Real Data Integration Manager (`real_data_integration_manager.py`)

**Purpose**: Gradual integration of real data with synthetic training data

**Features**:

- Configurable integration percentages (0% → 100% real data)
- Data quality validation and thresholds
- Automatic backup creation before integration
- Integration logging and monitoring
- Rollback capabilities for failed integrations

**Key Capabilities**:

```python
# Initialize with configuration
manager = RealDataIntegrationManager(
    real_data_percentage=10.0,  # Start with 10% real data
    quality_threshold=0.8,      # Minimum 80% quality
    backup_enabled=True
)

# Perform integration
result = await manager.integrate_data()

# Monitor integration progress
status = manager.get_integration_status()
```

### 3. Demo System (`playwright_auto_download_demo.py`)

**Purpose**: Comprehensive demonstration of the complete system

**Features**:

- Simulated data collection with realistic scenarios
- Live dashboard with progress tracking
- Training system compatibility testing
- API fallback scenario simulation
- Performance metrics and reporting

## Installation

### Prerequisites

```bash
# Install Python dependencies
pip install playwright beautifulsoup4 lxml rich pandas numpy

# Install Playwright browsers
playwright install chromium
```

### System Requirements

- Python 3.11+
- 8GB+ RAM (for browser automation)
- 50GB+ disk space (for data storage)
- Stable internet connection

## Configuration

### Environment Variables

```bash
# Racing data sources
RACING_POST_USERNAME="your_username"
RACING_POST_PASSWORD="your_password"
TIMEFORM_API_KEY="your_api_key"

# Data directories
REAL_DATA_DIR="./data/real_racing_data"
INTEGRATION_DATA_DIR="./data/integrated_data"
BACKUP_DATA_DIR="./data/backups"

# Integration settings
INITIAL_REAL_DATA_PERCENTAGE=5.0
QUALITY_THRESHOLD=0.85
MAX_INTEGRATION_RETRIES=3

# Browser settings
BROWSER_TIMEOUT=30000
STEALTH_MODE=true
HEADLESS_MODE=true
```

### Configuration Files

Create `config/playwright_config.json`:

```json
{
  "data_sources": {
    "racing_post": {
      "enabled": true,
      "priority": 1,
      "rate_limit": 2.0,
      "retry_attempts": 3
    },
    "timeform": {
      "enabled": true,
      "priority": 2,
      "rate_limit": 1.5,
      "retry_attempts": 2
    }
  },
  "integration": {
    "initial_percentage": 5.0,
    "increment_step": 5.0,
    "max_percentage": 100.0,
    "quality_threshold": 0.8
  },
  "browser": {
    "headless": true,
    "timeout": 30000,
    "viewport": { "width": 1920, "height": 1080 },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
}
```

## Usage

### Quick Start Demo

```bash
# Run the complete demonstration
python run_playwright_demo.py
```

This will show:

- ✅ Data collection simulation
- ✅ Data validation process
- ✅ Integration with synthetic data
- ✅ Training system compatibility
- ✅ API fallback scenarios

### Production Data Collection

```python
from enhanced_playwright_auto_download import EnhancedPlaywrightAutoDownload

# Initialize scraper
scraper = EnhancedPlaywrightAutoDownload()

# Collect today's racing data
daily_data = await scraper.collect_daily_racing_data()

# Process specific tracks
track_data = await scraper.collect_track_data("Newmarket")

# Get race results
results = await scraper.collect_race_results()
```

### Data Integration

```python
from real_data_integration_manager import RealDataIntegrationManager

# Initialize integration manager
manager = RealDataIntegrationManager(
    real_data_percentage=10.0,
    quality_threshold=0.8
)

# Perform integration
integration_result = await manager.integrate_data()

if integration_result['success']:
    print(f"Integration complete: {integration_result['summary']}")
else:
    print(f"Integration failed: {integration_result['error']}")
```

### Gradual Data Replacement

```python
# Start with 5% real data
await manager.set_real_data_percentage(5.0)
await manager.integrate_data()

# Gradually increase
for percentage in [10, 15, 25, 40, 60, 80, 100]:
    await manager.set_real_data_percentage(percentage)
    result = await manager.integrate_data()

    if result['quality_score'] < 0.8:
        # Rollback if quality drops
        await manager.rollback_integration()
        break
```

## Data Sources

### Primary Sources

1. **Racing Post** (`racing_post`)
   - Comprehensive race cards
   - Historical form data
   - Betting odds
   - Jockey/trainer information

2. **Timeform** (`timeform`)
   - Speed figures and ratings
   - Detailed form analysis
   - Track conditions
   - Performance analytics

3. **At The Races** (`at_the_races`)
   - Live race data
   - Video content
   - Expert tips
   - Market information

4. **Racing UK** (`racing_uk`)
   - Course information
   - Race results
   - Industry news
   - Statistical data

### Data Quality Validation

```python
# Quality checks performed:
quality_checks = {
    "required_fields": ["race_id", "track", "horses", "betting_odds"],
    "minimum_horses": 3,
    "valid_odds_range": (1.01, 1000.0),
    "data_freshness": "24_hours",
    "completeness_threshold": 0.85
}
```

## Integration Process

### Phase 1: Data Collection (0-5% Real Data)

- Start with synthetic data only
- Collect and validate real data in background
- Build data quality baselines
- Test data conversion processes

### Phase 2: Initial Integration (5-25% Real Data)

- Begin replacing synthetic data gradually
- Monitor training system performance
- Validate data quality continuously
- Create automatic backups

### Phase 3: Scaling Integration (25-75% Real Data)

- Increase real data percentage systematically
- Monitor model performance metrics
- Optimize data processing pipelines
- Handle integration edge cases

### Phase 4: Full Integration (75-100% Real Data)

- Complete transition to real data
- Maintain backup systems
- Implement monitoring and alerting
- Prepare for API integration

## API Fallback Strategy

### Scenario: horseracedatabase.com API Unavailable

```python
# Automatic fallback chain
fallback_chain = [
    "horseracedatabase_api",    # Primary
    "backup_api_1",             # Secondary
    "backup_api_2",             # Tertiary
    "playwright_scraper"        # Fallback
]

# Fallback implementation
for source in fallback_chain:
    try:
        data = await collect_data_from_source(source)
        if validate_data_quality(data):
            break
    except Exception as e:
        logger.warning(f"Source {source} failed: {e}")
        continue
```

### Monitoring and Alerts

```python
# Set up monitoring
monitor = DataSourceMonitor()

# Configure alerts
monitor.add_alert("api_failure", threshold=3, action="switch_to_playwright")
monitor.add_alert("data_quality", threshold=0.7, action="stop_integration")
monitor.add_alert("scraper_blocked", threshold=1, action="rotate_proxies")
```

## Performance Optimization

### Browser Performance

```python
# Optimize browser settings
browser_config = {
    "headless": True,
    "disable_images": True,
    "disable_javascript": False,  # Keep for dynamic content
    "timeout": 30000,
    "concurrent_pages": 3,
    "memory_limit": "2GB"
}
```

### Data Processing

```python
# Batch processing for efficiency
batch_processor = BatchDataProcessor(
    batch_size=50,
    max_workers=4,
    processing_timeout=300
)

# Process data in chunks
results = await batch_processor.process_race_data(all_races)
```

### Caching Strategy

```python
# Implement caching for repeated requests
cache_config = {
    "race_cards": {"ttl": 3600},      # 1 hour
    "odds_data": {"ttl": 300},        # 5 minutes
    "form_data": {"ttl": 86400},      # 24 hours
    "static_data": {"ttl": 604800}    # 1 week
}
```

## Error Handling

### Common Issues and Solutions

1. **Website Structure Changes**

   ```python
   # Implement adaptive selectors
   selectors = {
       "race_title": ["h1.race-title", ".title-main", "[data-test='race-title']"],
       "horse_name": [".horse-name", ".runner-name", "[data-horse-name]"]
   }
   ```

2. **Rate Limiting**

   ```python
   # Implement intelligent delays
   rate_limiter = AdaptiveRateLimiter(
       min_delay=1.0,
       max_delay=10.0,
       backoff_factor=1.5
   )
   ```

3. **Bot Detection**
   ```python
   # Use stealth techniques
   stealth_config = {
       "randomize_viewport": True,
       "rotate_user_agents": True,
       "simulate_human_behavior": True,
       "use_residential_proxies": True
   }
   ```

## Monitoring and Logging

### Log Configuration

```python
import logging

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/playwright_scraper.log'),
        logging.StreamHandler()
    ]
)

# Specific loggers
data_logger = logging.getLogger('data_collection')
integration_logger = logging.getLogger('data_integration')
performance_logger = logging.getLogger('performance')
```

### Performance Metrics

```python
# Track key metrics
metrics = {
    "collection_rate": "races_per_hour",
    "success_rate": "percentage_successful",
    "data_quality": "average_quality_score",
    "processing_time": "seconds_per_race",
    "memory_usage": "mb_average",
    "error_rate": "errors_per_hour"
}
```

## Testing

### Unit Tests

```bash
# Run comprehensive tests
python -m pytest tests/test_playwright_scraper.py -v
python -m pytest tests/test_data_integration.py -v
python -m pytest tests/test_quality_validation.py -v
```

### Integration Tests

```bash
# Test with real data sources (use carefully)
python -m pytest tests/integration/ --slow
```

### Load Testing

```bash
# Test system under load
python tests/load_test_scraper.py --concurrent-users=5 --duration=300
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application
COPY . /app
WORKDIR /app

# Run application
CMD ["python", "enhanced_playwright_auto_download.py"]
```

### Production Deployment

```bash
# Deploy to production server
docker-compose -f docker-compose.prod.yml up -d

# Monitor deployment
docker-compose logs -f playwright-scraper
```

## Security Considerations

### Data Protection

```python
# Implement data encryption
from cryptography.fernet import Fernet

# Encrypt sensitive data
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

encrypted_credentials = cipher.encrypt(credentials.encode())
```

### Access Control

```python
# Implement authentication
auth_config = {
    "require_api_key": True,
    "rate_limit_per_key": 1000,
    "whitelist_ips": ["192.168.1.0/24"],
    "blacklist_detection": True
}
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Predictive data validation
   - Automatic quality improvement
   - Anomaly detection

2. **Advanced Scheduling**
   - Race calendar integration
   - Optimal collection timing
   - Resource allocation

3. **Multi-Region Support**
   - International racing data
   - Timezone handling
   - Currency conversion

4. **Real-Time Processing**
   - Live odds monitoring
   - Instant data validation
   - Stream processing

## Support and Maintenance

### Regular Maintenance Tasks

```bash
# Weekly maintenance script
#!/bin/bash

# Clean old data
find ./data/cache -type f -mtime +7 -delete

# Rotate logs
logrotate /etc/logrotate.d/playwright-scraper

# Update browser drivers
playwright install chromium

# Check system health
python scripts/health_check.py
```

### Troubleshooting

1. **Browser Issues**: Update Playwright browsers
2. **Memory Issues**: Reduce concurrent pages
3. **Network Issues**: Check proxy configuration
4. **Data Quality**: Review validation rules

### Getting Help

- **Documentation**: See `docs/` directory
- **Examples**: Check `examples/` directory
- **Issues**: Create GitHub issue with logs
- **Performance**: Run `scripts/performance_profile.py`

---

**Status**: ✅ Production Ready
**Last Updated**: January 2025
**Version**: 2.0.0
