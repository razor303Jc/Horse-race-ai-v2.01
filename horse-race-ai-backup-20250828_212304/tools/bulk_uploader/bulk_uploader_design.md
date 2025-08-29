# Bulk Uploader Design Document

_Created: $(date)_

## Overview

Comprehensive bulk uploader system based on analysis of existing upload infrastructure, designed to handle large-scale data processing, validation, and upload operations.

## Analysis of Existing Upload Infrastructure

### Key Scripts Analyzed

1. **upload_race_data.py** - Main upload script with validation patterns
2. **upload_results_data_container.py** - Container-optimized bulk operations
3. **data_validator.py** - Comprehensive validation framework
4. **schema_guardian_container.py** - Schema compatibility and mapping

### Identified Patterns

- **Validation → Processing → Upload** workflow
- Foreign key constraint handling (races before records)
- Bulk insert with conflict resolution (ON CONFLICT DO NOTHING)
- Comprehensive error handling and logging
- Environment-based configuration
- Progress monitoring and reporting

### Technical Stack

- **Database**: PostgreSQL with psycopg2/psycopg2.extras
- **Data Processing**: pandas for manipulation
- **Validation**: Custom validators with pathlib
- **Container**: Docker-optimized execution
- **Monitoring**: Comprehensive logging and progress tracking

## Bulk Uploader Architecture

### Core Components

#### 1. Data Discovery & Intake

```
BulkDataDiscovery
├── Directory scanning (recursive)
├── File type detection (.csv, .json, .xlsx)
├── Data source classification
├── Metadata extraction
└── Processing queue generation
```

#### 2. Validation Engine

```
BulkValidationEngine
├── Schema compatibility checking
├── Data integrity validation
├── Foreign key constraint validation
├── Duplicate detection
├── Date consistency checks
└── Custom validation rules
```

#### 3. Processing Pipeline

```
BulkProcessingPipeline
├── Data transformation (mappings)
├── Column normalization
├── Data type conversion
├── NULL value handling
├── Batch partitioning
└── Progress tracking
```

#### 4. Upload Manager

```
BulkUploadManager
├── Connection pool management
├── Transaction handling
├── Conflict resolution strategies
├── Retry logic with exponential backoff
├── Foreign key constraint ordering
└── Performance optimization
```

#### 5. Monitoring & Reporting

```
BulkMonitoringSystem
├── Real-time progress tracking
├── Error aggregation and reporting
├── Performance metrics
├── Success/failure statistics
├── Detailed logging
└── Post-upload validation
```

## Implementation Plan

### Phase 1: Core Infrastructure

- [ ] Base BulkUploader class with configuration management
- [ ] Database connection pool with environment detection
- [ ] Logging framework with structured output
- [ ] Configuration schema and validation

### Phase 2: Data Discovery

- [ ] Recursive directory scanning
- [ ] File type detection and classification
- [ ] Metadata extraction and analysis
- [ ] Processing queue prioritization

### Phase 3: Validation Framework

- [ ] Integrate existing validation patterns from data_validator.py
- [ ] Schema compatibility checking from schema_guardian
- [ ] Foreign key constraint validation
- [ ] Custom validation rule engine

### Phase 4: Processing Engine

- [ ] Data transformation pipeline
- [ ] Column mapping and normalization
- [ ] Batch partitioning for large datasets
- [ ] Memory-efficient processing

### Phase 5: Upload Management

- [ ] Bulk insert optimization with execute_values
- [ ] Conflict resolution strategies
- [ ] Transaction management and rollback
- [ ] Foreign key ordering from existing patterns

### Phase 6: Monitoring & CLI

- [ ] Progress tracking and reporting
- [ ] Command-line interface
- [ ] Integration with existing Docker infrastructure
- [ ] Performance optimization and tuning

## Technical Specifications

### Database Integration

- **Connection**: Environment-based configuration (host detection)
- **Operations**: Bulk insert with psycopg2.extras.execute_values
- **Conflicts**: ON CONFLICT DO NOTHING for duplicates
- **Transactions**: Per-table transaction boundaries
- **Constraints**: Foreign key ordering (races → horses/jockeys/trainers → records)

### File Processing

- **Formats**: CSV (primary), JSON, Excel support
- **Encoding**: UTF-8 with fallback detection
- **Size Limits**: Chunked processing for large files
- **Validation**: Schema compatibility before processing

### Performance Targets

- **Throughput**: 10,000+ records per minute
- **Memory**: Streaming processing for large datasets
- **Concurrency**: Connection pooling with configurable pool size
- **Recovery**: Automatic retry with exponential backoff

### Error Handling

- **Validation Errors**: Detailed reporting with line numbers
- **Database Errors**: Transaction rollback with retry logic
- **File Errors**: Graceful handling with alternative processing
- **Network Errors**: Automatic reconnection with backoff

## Configuration Schema

### Environment Detection

```yaml
databases:
  development:
    host: localhost
    port: 5432
  container:
    host: postgres
    port: 5432
  production:
    host: ${DB_HOST}
    port: ${DB_PORT}
```

### Processing Rules

```yaml
processing:
  batch_size: 1000
  max_memory_usage: "1GB"
  validation_level: "strict"
  conflict_resolution: "ignore"
  foreign_key_handling: "ordered"
```

### Table Mappings

```yaml
mappings:
  horses:
    file_patterns: ["*horses*.csv", "*horse_data*.csv"]
    column_mappings:
      id: horse_id
      name: horse_name
      UptoDate: uptodate
```

## Integration Points

### Existing Systems

- **Schema Guardian**: Column mapping and compatibility
- **Data Validator**: Validation rule integration
- **Docker Infrastructure**: Container-optimized execution
- **Database Schemas**: Results, cards, advanced_metrics databases

### API Endpoints

- **Status**: GET /bulk-upload/status
- **Queue**: POST /bulk-upload/queue
- **Progress**: GET /bulk-upload/progress/{job_id}
- **Results**: GET /bulk-upload/results/{job_id}

## Success Metrics

### Performance

- Upload speed: Records per minute
- Memory efficiency: Peak memory usage
- Success rate: Percentage of successful uploads
- Error recovery: Time to recovery from failures

### Quality

- Data integrity: Validation pass rate
- Schema compliance: Compatibility success rate
- Duplicate handling: Effective deduplication
- Constraint satisfaction: Foreign key integrity

### Usability

- Setup time: Time from installation to first upload
- Error clarity: Understandable error messages
- Progress visibility: Clear status reporting
- Documentation completeness: Usage examples and guides

## Risk Mitigation

### Data Safety

- **Backup Creation**: Automatic backup before bulk operations
- **Transaction Rollback**: Safe failure recovery
- **Validation Gates**: Multi-level validation before upload
- **Audit Trail**: Complete operation logging

### Performance

- **Memory Management**: Streaming and chunked processing
- **Connection Limits**: Pool management and timeout handling
- **Resource Monitoring**: Automatic scaling and throttling
- **Optimization**: Query plan analysis and indexing

### Reliability

- **Error Recovery**: Comprehensive retry mechanisms
- **Health Checks**: Database and service availability
- **Monitoring**: Real-time status and alerting
- **Testing**: Comprehensive test suite with edge cases

## Next Steps

1. **Review and Approve** this design document
2. **Create base infrastructure** with configuration management
3. **Implement data discovery** and file classification
4. **Build validation engine** based on existing patterns
5. **Develop processing pipeline** with optimization
6. **Create upload manager** with bulk operations
7. **Add monitoring system** with reporting
8. **Integration testing** with existing Docker infrastructure
9. **Performance optimization** and tuning
10. **Documentation** and deployment guides

---

_This design leverages the strengths of existing upload infrastructure while providing a comprehensive, scalable solution for bulk data operations._
