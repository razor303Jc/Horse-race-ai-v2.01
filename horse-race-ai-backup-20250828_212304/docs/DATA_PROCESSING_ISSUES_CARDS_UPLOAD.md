# Data Processing Issues - Historical Cards Upload

## Overview

This document details the data processing issues encountered during the historical cards database upload process (Aug 22-24, 2025) and the solutions implemented. These fixes need to be integrated into the automated pipeline to handle similar issues in future data processing.

## Critical Issues Encountered

### 1. PostgreSQL Integer Overflow (Critical)

**Problem**: Large integer values in CSV files exceeded PostgreSQL's 32-bit integer limit (2,147,483,647)

- **Affected Fields**: `race_id`, `course_id`, `runners_racecard`, `runners`, `draw`, etc.
- **Error**: `psycopg2.errors.NumericValueOutOfRange: integer out of range`
- **Impact**: Complete upload failure for affected records

**Solution Implemented**:

```python
def clean_integer_field(value):
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        val = int(float(value))
        # PostgreSQL 32-bit integer limits
        if val > 2147483647 or val < -2147483648:
            return None  # Convert overflow to NULL
        return val
    except (ValueError, TypeError):
        return None
```

**Pipeline Integration Required**:

- Apply to ALL integer fields before database insertion
- Log overflow incidents for monitoring
- Consider upgrading affected fields to BIGINT if values consistently exceed limits

### 2. Auto-Increment Field Issues (Critical)

**Problem**: `racecard_details.detail_id` field was NOT auto-increment despite being non-nullable

- **Database Schema**: `detail_id` integer NOT NULL with no default value
- **Error**: `null value in column 'detail_id' violates not-null constraint`
- **Impact**: Complete failure of racecard_details uploads

**Solution Implemented**:

```python
# Generate sequential detail_id values
detail_id_counter = 1
df_valid['detail_id'] = range(detail_id_counter, detail_id_counter + len(df_valid))

# For subsequent uploads, get current max:
cur.execute('SELECT COALESCE(MAX(detail_id), 0) FROM racecard_details')
max_detail_id = cur.fetchone()[0]
df_valid['detail_id'] = range(max_detail_id + 1, max_detail_id + 1 + len(df_valid))
```

**Pipeline Integration Required**:

- Auto-detect non-auto-increment ID fields
- Generate sequential IDs for each batch upload
- Maintain ID continuity across multiple upload sessions

### 3. Foreign Key Constraint Violations (Critical)

**Problem**: Racecard details referenced race_ids that didn't exist in the races table

- **Scenario**: Aug 24th racecard_details had race_ids 183418-183443, but races table only had 183316-183362
- **Cause**: Incomplete race uploads before attempting details upload
- **Impact**: 252 out of 670 racecard details failed to upload

**Solution Implemented**:

```python
# Get valid race_ids from database
cur.execute('SELECT DISTINCT race_id FROM races ORDER BY race_id')
valid_race_ids = set(row[0] for row in cur.fetchall())

# Filter details to only valid race_ids
df_valid = df[df['race_id'].isin(valid_race_ids)].copy()
```

**Pipeline Integration Required**:

- Always upload parent tables (races, horses) before child tables (racecard_details)
- Validate foreign key relationships before upload
- Log and report orphaned records

### 4. Column Name Mapping Issues (Medium)

**Problem**: CSV column names didn't match database schema

- **Example**: CSV had `race_date` but database expected `date`
- **Impact**: Column mismatch causing upload failures

**Solution Implemented**:

```python
# Dynamic column renaming
if 'race_date' in df.columns and 'date' not in df.columns:
    df = df.rename(columns={'race_date': 'date'})
```

**Pipeline Integration Required**:

- Create comprehensive column mapping configuration
- Apply mappings automatically based on file type
- Log mapping applications for audit trail

### 5. Duplicate Column Issues (Medium)

**Problem**: CSV files contained duplicate columns (e.g., `odds` and `odds.1`)

- **Cause**: Pandas read_csv creating duplicate column names when headers repeat
- **Impact**: Schema mismatch and data confusion

**Solution Implemented**:

```python
# Remove duplicate columns
if 'odds.1' in df.columns:
    df = df.drop(columns=['odds.1'])
```

**Pipeline Integration Required**:

- Detect and remove duplicate columns automatically
- Prefer the first occurrence of duplicated columns
- Log duplicate removals

### 6. Data Type Cleaning Requirements (Medium)

**Problem**: Inconsistent data types and formats in CSV files

- **Numeric fields**: Empty strings, NaN, invalid formats
- **Percentage fields**: Mixed % symbols and decimal formats
- **Impact**: Type conversion errors during upload

**Solution Implemented**:

```python
def clean_numeric_field(value):
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def clean_percentage(value):
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, str) and "%" in value:
        return float(value.replace("%", ""))
    return float(value)
```

**Pipeline Integration Required**:

- Apply appropriate cleaning functions based on field types
- Configure cleaning rules per table/column
- Standardize percentage handling across all tables

## Upload Statistics Summary

### Final Results:

- **Races**: 73 total (47 from Aug 22nd, 26 from Aug 24th)
- **Horses**: 418 total (all from Aug 22nd data)
- **Racecard Details**: 670 total (418 from Aug 22nd, 252 from Aug 24th after fixes)

### Coverage by Date:

- **Aug 22nd**: Complete coverage (47 races, 418 details)
- **Aug 23rd**: Duplicate of Aug 22nd (skipped in final upload)
- **Aug 24th**: Complete coverage after fixes (26 races, 252 details)

## Critical Pipeline Enhancements Needed

### 1. Pre-Upload Validation

```python
def validate_upload_readiness(df, table_name, db_cursor):
    """Validate data before upload attempt"""
    issues = []

    # Check integer overflows
    integer_fields = get_integer_fields(table_name)
    for field in integer_fields:
        if field in df.columns:
            overflow_count = check_integer_overflow(df[field])
            if overflow_count > 0:
                issues.append(f"{field}: {overflow_count} integer overflows")

    # Check foreign key constraints
    fk_fields = get_foreign_key_fields(table_name)
    for field, parent_table in fk_fields.items():
        if field in df.columns:
            orphan_count = check_foreign_key_violations(df[field], parent_table, db_cursor)
            if orphan_count > 0:
                issues.append(f"{field}: {orphan_count} foreign key violations")

    return issues
```

### 2. Automated Data Cleaning Pipeline

```python
def auto_clean_dataframe(df, table_name):
    """Apply all necessary cleaning transformations"""

    # Apply column mappings
    df = apply_column_mappings(df, table_name)

    # Remove duplicate columns
    df = remove_duplicate_columns(df)

    # Clean data types
    df = clean_integer_fields(df, table_name)
    df = clean_numeric_fields(df, table_name)
    df = clean_percentage_fields(df, table_name)

    # Generate required ID fields
    df = generate_id_fields(df, table_name)

    return df
```

### 3. Upload Order Management

```python
def get_upload_order():
    """Define correct table upload order to respect foreign keys"""
    return [
        'races',      # Parent table
        'horses',     # Independent table
        'racecard_details',  # Child table (depends on races)
        'jockeys_stats',     # Independent
        'trainers_stats'     # Independent
    ]
```

### 4. Error Recovery and Reporting

```python
def upload_with_recovery(tables_data, db_connection):
    """Upload with automatic error recovery and detailed reporting"""

    results = {
        'successful': [],
        'failed': [],
        'warnings': [],
        'statistics': {}
    }

    for table_name in get_upload_order():
        if table_name in tables_data:
            try:
                # Pre-validate
                issues = validate_upload_readiness(tables_data[table_name], table_name, db_connection.cursor())
                if issues:
                    results['warnings'].extend(issues)

                # Clean data
                clean_df = auto_clean_dataframe(tables_data[table_name], table_name)

                # Upload
                count = upload_table_data(db_connection.cursor(), table_name, clean_df)
                results['successful'].append((table_name, count))

            except Exception as e:
                results['failed'].append((table_name, str(e)))

    return results
```

## Configuration Requirements

### 1. Column Mapping Configuration

Create `config/cards_column_mappings.json`:

```json
{
  "races": {
    "race_date": "date",
    "race_time": "time"
  },
  "racecard_details": {
    "horse_name": "name",
    "odds_decimal": "odds"
  }
}
```

### 2. Field Type Configuration

Create `config/cards_field_types.json`:

```json
{
  "races": {
    "integer_fields": [
      "race_id",
      "race_number",
      "course_id",
      "runners",
      "draw"
    ],
    "numeric_fields": ["prize", "distance"],
    "percentage_fields": [],
    "id_fields": []
  },
  "racecard_details": {
    "integer_fields": ["race_id", "number", "age"],
    "numeric_fields": ["odds", "weight"],
    "percentage_fields": [],
    "id_fields": ["detail_id"]
  }
}
```

## Next Steps for Pipeline Integration

1. **Implement validation functions** in the data processing pipeline
2. **Create configuration files** for column mappings and field types
3. **Add automatic data cleaning** to the ETL process
4. **Implement upload order management** for foreign key compliance
5. **Add comprehensive error logging** and recovery mechanisms
6. **Create monitoring dashboards** for tracking data quality issues

## Testing Requirements

Before deploying these fixes to production:

1. **Test with known problematic datasets** to verify all issues are resolved
2. **Validate foreign key handling** with incomplete parent data
3. **Test integer overflow protection** with edge case values
4. **Verify ID generation** doesn't create conflicts
5. **Test error recovery** scenarios

This documentation should be referenced when implementing automated data processing in the daily pipeline to prevent the same issues from recurring.
