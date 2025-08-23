# Important Data Processing Scripts - V2.03

## 🔧 Core Data Processing Tools

### CSV Processing & Mapping

- **`tools/data_processing/complete_csv_processor.py`** ⭐⭐⭐
  - **Purpose**: Complete CSV processor with Docker database support (port 5434)
  - **Status**: Working - processes and maps ALL CSV columns with proper NULL handling
  - **Key Features**:
    - Maps CSV columns to database schema using `config/complete_csv_column_mapping.json`
    - Handles NULL values properly
    - Processes multiple tables: races, records, horses, jockeys_stats, trainers_stats
    - Saves mapped files to `data/daily_downloads/complete_mapped_*.csv`
  - **Usage**: `python tools/data_processing/complete_csv_processor.py`

### Database Upload

- **`upload_mapped_data.py`** ⭐⭐⭐

  - **Purpose**: Direct uploader for processed CSV files to Docker database
  - **Status**: Ready - handles conflicts and bulk inserts
  - **Key Features**:
    - Docker database connection (postgres:5432)
    - ON CONFLICT handling for duplicates
    - Bulk insert with execute_values
    - Proper NULL value handling
  - **Usage**: `python upload_mapped_data.py`

- **`tools/data_processing/csv_uploader.py`** ⭐⭐
  - **Purpose**: Daily CSV uploader (updated for Docker port 5434)
  - **Status**: Working - general CSV upload functionality
  - **Usage**: For daily automated uploads

### Integration & Hooks

- **`tools/data_processing/upload_integration_hook.py`** ⭐⭐
  - **Purpose**: Post-upload integration hook with ML preprocessing
  - **Status**: Working - runs data relationships and ML feature prep after uploads
  - **Key Features**:
    - Two-stage workflow: data relationships + ML preprocessing
    - Logging to `logs/upload_integration.log`
    - Database connectivity checks

## 📊 Configuration Files

### Column Mapping

- **`config/complete_csv_column_mapping.json`** ⭐⭐⭐
  - **Purpose**: Complete column mapping configuration for all tables
  - **Status**: Working - maps CSV columns to database schema
  - **Tables Covered**: races, records, horses, jockeys_stats, trainers_stats

## 📁 Data Recovery & Processing

### Recovery Summary

- **`data/recovered_from_trash/RECOVERY_SUMMARY.md`** ⭐⭐
  - **Purpose**: Documentation of recovered racing data from trash
  - **Contents**: 4MB of valuable racing data (Race_IDs 182648-182690)
  - **Status**: Processed and ready for import

### Processed Data Location

- **`data/daily_downloads/complete_mapped_*.csv`** ⭐⭐⭐
  - **Files**:
    - `complete_mapped_races.csv` (70 races total)
    - `complete_mapped_records.csv` (404+ records)
    - `complete_mapped_horses.csv` (695+ horses)
    - `complete_mapped_jockeys_stats.csv` (6602 jockeys)
    - `complete_mapped_trainers_stats.csv` (4259 trainers)
  - **Status**: Ready for database upload

## 🎯 Workflow Summary

### Standard Data Processing Workflow:

1. **Extract** - Data from zip files to `data/recovered_from_trash/extracted_*`
2. **Map** - Run `complete_csv_processor.py` to map columns and handle NULLs
3. **Upload** - Run `upload_mapped_data.py` to insert into database
4. **Integrate** - Post-upload hooks run automatically for relationships and ML prep

### Database Status:

- **Current Records**: 404 race records, 54 races, 414 horses
- **Recovered Data**: Additional 43 races (182648-182690) ready for import
- **Connection**: Docker PostgreSQL on postgres:5432

## 🚀 Next Actions:

1. Run `upload_mapped_data.py` to import recovered data
2. Verify database integrity after import
3. Continue with TODO list item #2 (Database Connection Configuration)

## 📝 Notes:

- All scripts updated for Docker database configuration (port 5434)
- NULL handling implemented across all processors
- Conflict resolution (ON CONFLICT DO NOTHING) prevents duplicates
- Integration hooks ready for automated workflows
