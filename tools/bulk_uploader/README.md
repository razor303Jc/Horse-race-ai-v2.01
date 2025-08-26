# Bulk Uploader Documentation

## Overview

The Bulk Uploader is a comprehensive data processing and upload system designed specifically for the Horse Racing AI project. It provides automated discovery, validation, processing, and bulk uploading of race data files to PostgreSQL databases.

## Features

### 🔍 **Intelligent File Discovery**

- Recursive directory scanning
- Automatic file type detection (.csv, .json, .xlsx)
- Smart table classification based on filename patterns
- Metadata extraction and analysis

### ✅ **Comprehensive Validation**

- Schema compatibility checking
- Data integrity validation
- Foreign key constraint validation
- Duplicate detection and handling
- Date consistency checks

### ⚡ **High-Performance Processing**

- Bulk insert operations with `execute_values`
- Parallel processing with configurable workers
- Memory-efficient streaming for large files
- Automatic batch partitioning
- Connection pooling for optimal performance

### 🛡️ **Robust Error Handling**

- Transaction management with rollback
- Retry logic with exponential backoff
- Conflict resolution strategies
- Comprehensive error reporting
- Progress tracking and monitoring

### 🐳 **Docker Integration**

- Container-optimized execution
- Environment-based configuration
- Direct database access within containers
- Automated daily processing workflows

## Architecture

```
BulkUploader
├── DataDiscoveryEngine     # File discovery and classification
├── ValidationEngine        # Schema and data validation
├── BulkProcessingEngine    # Data transformation and processing
├── BulkUploadEngine        # Database upload operations
└── DatabaseConnectionManager # Connection management
```

## Installation

### Requirements

- Python 3.8+
- PostgreSQL database
- Required packages: `pandas`, `psycopg2`, `pyyaml`, `pytest`

### Setup

```bash
# Install dependencies
pip install pandas psycopg2-binary pyyaml pytest

# Clone the bulk uploader
cd tools/bulk_uploader

# Make scripts executable
chmod +x cli.py container_runner.py
```

## Usage

### Command Line Interface

#### Basic Upload

```bash
# Upload all files in a directory
python cli.py upload /path/to/data

# Upload with recursive directory search
python cli.py upload /path/to/data --recursive

# Upload with custom configuration
python cli.py upload /path/to/data --config config.yaml --workers 8
```

#### Validation Only

```bash
# Validate files without uploading
python cli.py validate /path/to/data --verbose

# Recursive validation
python cli.py validate /path/to/data --recursive
```

#### Database Testing

```bash
# Test database connection
python cli.py test-connection

# Test with custom config
python cli.py test-connection --config config.yaml
```

#### Status Monitoring

```bash
# Show recent upload status
python cli.py status

# Detailed status information
python cli.py status --verbose
```

#### Configuration Management

```bash
# Show current configuration
python cli.py config

# Create default configuration file
python cli.py config --create config.yaml

# Overwrite existing configuration
python cli.py config --create config.yaml --force
```

### Docker Container Usage

#### Daily Downloads Processing

```bash
# Set environment and run
export BULK_UPLOAD_MODE="daily_downloads"
python container_runner.py
```

#### Specific Files Processing

```bash
# Process specific files
export BULK_UPLOAD_MODE="specific_files"
export BULK_UPLOAD_FILES="/app/data/file1.csv,/app/data/file2.csv"
python container_runner.py
```

### Python API Usage

```python
from bulk_uploader import BulkUploader, BulkUploadConfig
from pathlib import Path

# Initialize with custom config
config = BulkUploadConfig(
    batch_size=2000,
    max_workers=8,
    validation_level="strict"
)
uploader = BulkUploader()

# Discover and queue files
job_ids = uploader.discover_and_queue_files(Path("/data"), recursive=True)

# Process all jobs
results = uploader.process_all_jobs()

# Check individual job status
for job_id in job_ids:
    status = uploader.get_job_status(job_id)
    print(f"Job {job_id}: {status['status']}")
```

## Configuration

### YAML Configuration File

```yaml
processing:
  batch_size: 1000 # Records per batch
  max_workers: 4 # Parallel workers
  validation_level: "strict" # strict, moderate, lenient
  conflict_resolution: "ignore" # ignore, update, error
  foreign_key_handling: "ordered" # ordered, disabled
  max_memory_usage: "1GB" # Memory limit
  retry_attempts: 3 # Retry attempts
  retry_delay: 1.0 # Retry delay (seconds)
  connection_pool_size: 10 # Connection pool size

# Database configuration
database:
  development:
    host: "localhost"
    port: 5432
    database: "results_horse_racing_db"
    user: "horse_racing"
    password: "secure_password_123"

  container:
    host: "postgres"
    port: 5432
    database: "results_horse_racing_db"
    user: "horse_racing"
    password: "secure_password_123"
```

### Environment Variables

```bash
# Container configuration
BULK_BATCH_SIZE=1000
BULK_MAX_WORKERS=4
BULK_VALIDATION_LEVEL=strict
BULK_CONFLICT_RESOLUTION=ignore
BULK_RETRY_ATTEMPTS=3
BULK_CONNECTION_POOL=10

# Processing modes
BULK_UPLOAD_MODE=daily_downloads
BULK_UPLOAD_FILES=/app/data/file1.csv,/app/data/file2.csv
```

## File Processing

### Supported File Formats

- **CSV**: Primary format with automatic delimiter detection
- **JSON**: Structured data format
- **Excel**: .xlsx and .xls files with automatic sheet detection

### File Classification Rules

The system automatically classifies files based on filename patterns:

| Table            | Patterns                                     |
| ---------------- | -------------------------------------------- |
| `horses`         | horse, mapped_horses, horse_data             |
| `jockeys_stats`  | jockey, mapped_jockeys_stats, jockey_data    |
| `trainers_stats` | trainer, mapped_trainers_stats, trainer_data |
| `races`          | race, mapped_races, race_data                |
| `records`        | record, result, mapped_records, results_data |

### Column Mapping

Automatic column mapping handles common variations:

```python
column_mappings = {
    "horses": {
        "id": "horse_id",
        "name": "horse_name",
        "UptoDate": "uptodate"
    },
    "jockeys_stats": {
        "UptoDate": "uptodate",
        "Jockey_ID": "jockey_id",
        "Name": "jockey_name"
    }
    # ... additional mappings
}
```

## Database Integration

### Foreign Key Constraint Handling

The system respects foreign key constraints through ordered processing:

1. **races** (parent table) - uploaded first
2. **horses**, **jockeys_stats**, **trainers_stats** (independent) - uploaded in parallel
3. **records** (child table) - uploaded last

### Conflict Resolution

Multiple strategies for handling duplicate data:

- **ignore**: Use `ON CONFLICT DO NOTHING` (default)
- **update**: Use `ON CONFLICT DO UPDATE`
- **error**: Fail on conflicts

### Transaction Management

- Per-table transaction boundaries
- Automatic rollback on errors
- Connection pooling for performance

## Validation Framework

### Schema Validation

- Database schema compatibility checking
- Column mapping validation
- Required field verification
- Data type compatibility

### Data Integrity Validation

- Empty row detection and removal
- Duplicate record identification
- Date format validation
- Numeric value range checking
- Custom validation rules

### Validation Levels

- **strict**: All validations must pass
- **moderate**: Warnings allowed, errors fail
- **lenient**: Continue processing with warnings

## Performance Optimization

### Bulk Operations

- `psycopg2.extras.execute_values` for maximum throughput
- Configurable batch sizes (default: 1000 records)
- Memory-efficient streaming for large files

### Parallel Processing

- Multi-threaded file processing
- Respect for foreign key constraints
- Configurable worker pools

### Memory Management

- Chunked file reading for large datasets
- Automatic garbage collection
- Configurable memory limits

## Monitoring and Logging

### Progress Tracking

- Real-time progress updates
- Record count tracking
- Performance metrics
- Success/failure statistics

### Logging

- Structured logging with timestamps
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output
- Container-optimized logging

### Status Reporting

- JSON status files for monitoring
- Detailed job tracking
- Error aggregation
- Performance metrics

## Error Handling

### Recovery Mechanisms

- Automatic retry with exponential backoff
- Transaction rollback on failures
- Partial success handling
- Detailed error reporting

### Error Types

- **Validation Errors**: Schema mismatches, data integrity issues
- **Database Errors**: Connection failures, constraint violations
- **File Errors**: Missing files, format issues
- **System Errors**: Memory limits, timeout issues

## Testing

### Test Suite

```bash
# Run all tests
python test_bulk_uploader.py

# Run with pytest for detailed output
pytest test_bulk_uploader.py -v

# Run specific test class
pytest test_bulk_uploader.py::TestBulkUploader -v
```

### Test Coverage

- Configuration management
- File discovery and classification
- Validation framework
- Data processing pipeline
- Upload operations
- Error handling

## Integration Examples

### Daily Processing Workflow

```bash
#!/bin/bash
# Daily bulk upload script

# Download latest data
python download_daily_data.py

# Run bulk upload
python cli.py upload /data/daily_downloads --force --output /logs/upload_results.json

# Check results
if [ $? -eq 0 ]; then
    echo "✅ Daily upload successful"
else
    echo "❌ Daily upload failed"
    python cli.py status --verbose
fi
```

### Docker Compose Integration

```yaml
services:
  bulk-uploader:
    build: ./tools/bulk_uploader
    environment:
      - BULK_UPLOAD_MODE=daily_downloads
      - BULK_BATCH_SIZE=2000
      - BULK_MAX_WORKERS=6
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
```

### API Integration

```python
from flask import Flask, request, jsonify
from bulk_uploader import BulkUploader

app = Flask(__name__)
uploader = BulkUploader()

@app.route('/upload', methods=['POST'])
def upload_files():
    data_path = request.json.get('path')
    job_ids = uploader.discover_and_queue_files(Path(data_path))
    results = uploader.process_all_jobs()
    return jsonify(results)

@app.route('/status/<job_id>')
def get_status(job_id):
    status = uploader.get_job_status(job_id)
    return jsonify(status)
```

## Troubleshooting

### Common Issues

#### Database Connection Failures

```bash
# Test connection
python cli.py test-connection

# Check environment detection
python -c "from bulk_uploader import DatabaseConnectionManager; print(DatabaseConnectionManager().config)"
```

#### File Classification Issues

```bash
# Validate specific files
python cli.py validate /path/to/data --verbose

# Check classification rules
python -c "from bulk_uploader import DataDiscoveryEngine; engine = DataDiscoveryEngine(None); print(engine.classify_file(Path('your_file.csv')))"
```

#### Performance Issues

```bash
# Reduce batch size for memory-constrained environments
python cli.py upload /data --config config.yaml  # Set batch_size: 500 in config

# Reduce worker count
export BULK_MAX_WORKERS=2
python container_runner.py
```

#### Validation Failures

```bash
# Use lenient validation
# Set validation_level: "lenient" in config.yaml

# Check schema compatibility
python -c "from bulk_uploader import ValidationEngine; # Manual schema check"
```

### Debug Mode

```bash
# Enable debug logging
export BULK_LOG_LEVEL=DEBUG
python cli.py upload /data --verbose
```

## Best Practices

### File Organization

- Use consistent naming conventions
- Organize files by date and type
- Maintain clean directory structures
- Remove processed files regularly

### Configuration Management

- Use environment-specific configurations
- Store sensitive credentials in environment variables
- Version control configuration files
- Document configuration changes

### Monitoring

- Set up automated status checking
- Monitor log files for errors
- Track performance metrics
- Set up alerting for failures

### Performance Tuning

- Adjust batch sizes based on available memory
- Use appropriate worker counts for CPU cores
- Monitor database connection usage
- Optimize file sizes for processing

---

For more information and updates, see the project documentation and changelog.
