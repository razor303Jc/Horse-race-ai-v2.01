# SQLite3 Backup Tracking System Documentation

## Overview

The CSV Backup Manager now uses SQLite3 for comprehensive backup tracking and metadata management. This system provides enhanced querying, monitoring, and management capabilities while maintaining complete separation from the PostgreSQL horse racing data.

## Important Separation

**⚠️ CRITICAL: SQLite3 is ONLY for backup tracking - NOT for horse racing data**

- **SQLite3**: Used exclusively for backup metadata, tracking, and management
- **PostgreSQL Docker**: Used exclusively for horse racing data (races, horses, results, etc.)

These databases serve completely different purposes and must never be mixed.

## SQLite Database Schema

### Tables

#### 1. `backup_archives`

Primary table for tracking backup archives:

```sql
CREATE TABLE backup_archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_name TEXT NOT NULL,          -- Filename of backup ZIP
    archive_path TEXT NOT NULL,          -- Full path to backup file
    data_type TEXT NOT NULL,             -- 'cards' or 'results'
    file_date TEXT NOT NULL,             -- Date of racing data (YYYY-MM-DD)
    original_zip_name TEXT NOT NULL,     -- Original downloaded ZIP name
    created_timestamp TEXT NOT NULL,     -- ISO timestamp of backup creation
    size_bytes INTEGER NOT NULL,         -- Archive file size in bytes
    csv_files_count INTEGER NOT NULL,    -- Number of CSV files in archive
    detected_date TEXT,                  -- Date detected from CSV analysis
    first_race_time TEXT,                -- Earliest race time found
    last_race_time TEXT,                 -- Latest race time found
    total_races INTEGER,                 -- Total number of races
    courses TEXT,                        -- JSON array of course names
    status TEXT DEFAULT 'active',       -- 'active', 'missing', 'deleted'
    notes TEXT                           -- Additional notes
);
```

#### 2. `backup_csv_files`

Detailed tracking of individual CSV files within each backup:

```sql
CREATE TABLE backup_csv_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_id INTEGER NOT NULL,         -- Foreign key to backup_archives
    filename TEXT NOT NULL,             -- CSV filename
    relative_path TEXT NOT NULL,        -- Path within backup archive
    size_bytes INTEGER NOT NULL,        -- Individual file size
    records_count INTEGER,              -- Number of records in CSV
    columns_list TEXT,                  -- JSON array of column names
    date_values TEXT,                   -- JSON array of unique dates found
    FOREIGN KEY (backup_id) REFERENCES backup_archives (id)
);
```

#### 3. `backup_operations`

Audit log of all backup operations:

```sql
CREATE TABLE backup_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,       -- 'create_backup', 'cleanup', 'mark_missing'
    backup_id INTEGER,                  -- Related backup (if applicable)
    timestamp TEXT NOT NULL,            -- ISO timestamp of operation
    status TEXT NOT NULL,               -- 'success', 'warning', 'error'
    details TEXT,                       -- Operation details
    error_message TEXT,                 -- Error information (if any)
    FOREIGN KEY (backup_id) REFERENCES backup_archives (id)
);
```

## Database Location

```
data/daily_downloads/backups/backup_tracking.db
```

This SQLite database file is created automatically when the CSVBackupManager is first initialized.

## Enhanced Features

### 1. Automatic Tracking

Every backup operation is automatically recorded with:

- Complete file metadata
- CSV content analysis
- Validation results
- Operation timestamps

### 2. Fast Querying

SQLite enables rapid queries for:

- Backups by date range
- Backups by data type
- Missing or corrupted files
- Statistical analysis

### 3. Status Management

Backups are tracked with status indicators:

- **active**: Archive exists and is valid
- **missing**: Archive file no longer exists on filesystem
- **deleted**: Archive was intentionally removed during cleanup

### 4. Comprehensive Statistics

Get detailed statistics including:

- Total backups by type and date
- Storage usage analysis
- Date range coverage
- Missing file detection

## Usage Examples

### Basic Backup with SQLite Tracking

```python
from tools.data_processing.csv_backup_manager import CSVBackupManager

manager = CSVBackupManager()

# This automatically records in SQLite
result = manager.extract_and_backup_zip(
    zip_path=Path("cards_2025-08-24.zip"),
    data_type="cards",
    target_date="2025-08-24"
)
```

### Query Backups from SQLite

```python
# List all active backups
backups = manager.list_csv_backups()

# List only results backups
results_backups = manager.list_csv_backups(data_type="results")

# List backups for specific date
today_backups = manager.list_csv_backups(date="2025-08-24")
```

### Get Statistics

```python
stats = manager.get_backup_statistics()
print(f"Active backups: {stats['active_backups']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"By type: {stats['by_data_type']}")
```

### Display Enhanced Status

```python
# Shows SQLite-powered statistics
manager.display_backup_status()
```

## Data Integrity Features

### 1. Filesystem Validation

- Automatically checks if archive files still exist
- Marks missing files in database
- Provides fallback to filesystem scanning if database issues occur

### 2. Duplicate Prevention

- Tracks all backup operations
- Prevents accidental overwrites
- Maintains complete audit trail

### 3. Error Logging

- All database errors are logged
- Graceful fallback to filesystem operations
- Detailed error reporting

## Separation from Horse Racing Data

### What SQLite DOES store:

- Backup file metadata and paths
- CSV file lists and analysis
- Backup operation history
- File validation results
- Storage statistics

### What SQLite does NOT store:

- Race results or race card data
- Horse information
- Betting odds or prices
- Performance statistics
- Any actual horse racing content

### PostgreSQL Docker Containers Store:

- All actual horse racing data
- Race results and cards
- Horse and jockey information
- Performance metrics
- ML training data and predictions

## Backup and Recovery

### Database Backup

The SQLite tracking database should be backed up regularly:

```bash
# Copy the SQLite database
cp data/daily_downloads/backups/backup_tracking.db /backup/location/
```

### Database Recovery

If the SQLite database is corrupted or lost:

1. The system will automatically recreate the schema
2. Existing backups can be re-indexed from filesystem
3. No actual backup data is lost (only tracking metadata)

## CLI Commands

### Enhanced Status Display

```bash
python tools/data_processing/csv_backup_manager.py status
```

### Cleanup with SQLite Tracking

```bash
python tools/data_processing/csv_backup_manager.py cleanup 30
```

### List Backups

```bash
python tools/data_processing/csv_backup_manager.py list [data_type]
```

## Integration Points

### 1. Pipeline Integration

The SQLite tracking integrates seamlessly with:

- Enhanced date validation
- Pipeline orchestration
- File monitoring systems
- Automated backup creation

### 2. Monitoring Systems

Statistics can be used for:

- Storage usage monitoring
- Backup health checks
- Data availability reports
- System performance metrics

### 3. API Integration

The backup tracking can be exposed via API for:

- Backup status queries
- Historical data analysis
- Automated monitoring
- External system integration

## Performance Benefits

1. **Fast Queries**: SQLite provides much faster searching than filesystem scanning
2. **Rich Filtering**: Complex queries on dates, types, sizes, etc.
3. **Statistics**: Instant statistics without file system traversal
4. **Scalability**: Handles thousands of backups efficiently
5. **Reliability**: Database consistency and ACID compliance

## Future Enhancements

1. **Web Dashboard**: SQLite data can power a web interface for backup management
2. **Automated Alerts**: Monitor for missing backups or storage issues
3. **Backup Verification**: Periodic integrity checking of archives
4. **Retention Policies**: Sophisticated cleanup rules based on various criteria
5. **Export/Import**: Easy data migration and backup sharing

This SQLite integration provides a robust foundation for professional backup management while maintaining strict separation from the horse racing data systems.
