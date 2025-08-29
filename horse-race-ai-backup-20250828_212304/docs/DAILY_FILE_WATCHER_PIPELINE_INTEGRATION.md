# Daily File Watcher Pipeline Integration

## Horse Racing AI v2.04 - Complete Integration Summary

### Overview

The daily file watcher has been fully integrated into the existing pipeline infrastructure, providing seamless event-driven data processing that automatically advances day-by-day until files are received and processed.

### Integration Architecture

#### 1. Daily File Watcher (`tools/automation/daily_file_watcher.py`)

- **Primary Function**: Monitors for daily racing files (cards + results)
- **Daily Progression**: Automatically advances to next day after completion
- **Persistence**: Remembers completed days and current target date
- **Validation**: Validates file structure and content before processing

#### 2. Pipeline Integration (`tools/pipeline/daily_file_watcher_integration.py`)

- **Event Bridge**: Connects file watcher events to pipeline orchestrator
- **Stage Triggering**: Automatically triggers pipeline stages on file completion
- **Error Handling**: Manages failures and retries across pipeline stages
- **Status Monitoring**: Provides real-time status updates and logging

#### 3. Startup Management

- **Main Control**: `start_pipeline_integration.sh` - Manages the complete system
- **Fallback**: `start_daily_watcher.sh` - Standalone file watcher only

### File Flow Process

```
1. Files Placed → data/daily_downloads/manual_download/
   ├── racecards_YYYY-MM-DD.zip
   └── results_YYYY-MM-DD.zip

2. File Detection → Daily File Watcher
   ├── Validates file date matches target
   ├── Extracts to date-specific directories
   └── Validates content structure

3. Pipeline Trigger → Both files ready
   ├── data_validation (immediate)
   ├── database_upload (30s delay)
   ├── relationship_analysis (60s delay)
   ├── ml_model_update (120s delay)
   └── contextual_analysis (180s delay)

4. Day Completion → Advance to next day
   ├── Mark current day complete
   ├── Reset file tracking
   └── Update target date
```

### Daily Monitoring Cycle

The system operates on a **persistent daily cycle**:

1. **Morning**: Start monitoring for today's race cards
2. **Throughout Day**: Wait for cards file arrival and validation
3. **Evening**: Wait for results file arrival and validation
4. **Night**: When both received → trigger full pipeline
5. **Completion**: Mark day complete, advance to tomorrow
6. **Repeat**: Continue monitoring next day automatically

### Pipeline Stages Integration

#### Stage 1: Data Validation

- **Trigger**: Immediate on file completion
- **Purpose**: Validate file structure and data integrity
- **Required**: Yes (pipeline stops if fails)

#### Stage 2: Database Upload

- **Trigger**: 30 seconds after validation
- **Purpose**: Upload validated data to PostgreSQL database
- **Required**: Yes (critical for downstream processes)

#### Stage 3: Relationship Analysis

- **Trigger**: 60 seconds after database upload
- **Purpose**: Analyze data relationships and patterns
- **Required**: No (continues even if fails)

#### Stage 4: ML Model Update

- **Trigger**: 120 seconds after relationship analysis
- **Purpose**: Retrain models with new data
- **Required**: No (can run independently)

#### Stage 5: Contextual Analysis

- **Trigger**: 180 seconds after ML update
- **Purpose**: Generate insights and analysis reports
- **Required**: No (final optional stage)

### Configuration Files

#### 1. Daily Watcher Config (`config/daily_watcher_config.json`)

- File pattern recognition settings
- Validation requirements
- Directory structure
- Monitoring intervals

#### 2. Pipeline Integration Config (`config/pipeline_integration_config.json`)

- Stage trigger mappings
- Dependency definitions
- Timeout and retry settings
- Error handling policies

### Usage Commands

#### Start Complete Integration

```bash
./start_pipeline_integration.sh start
```

#### Check Status

```bash
./start_pipeline_integration.sh status
```

#### Stop Integration

```bash
./start_pipeline_integration.sh stop
```

#### Restart System

```bash
./start_pipeline_integration.sh restart
```

### Status Monitoring

#### Real-time Status Files

- **Pipeline Status**: `data/pipeline_integration_status.json`
- **Watcher Status**: `data/daily_watcher_status.json`
- **Watcher State**: `data/daily_watcher_state.json`

#### Log Files

- **Integration Logs**: `logs/pipeline_integration.log`
- **Watcher Logs**: `logs/daily_file_watcher.log`
- **Startup Logs**: `logs/daily_watcher_startup.log`

### File Naming Conventions

#### Required Patterns

Files must include date and type identifiers:

**Race Cards Examples:**

- `racecards_2025-08-23.zip`
- `uk-racecards-20250823.zip`
- `cards_2025_08_23.zip`

**Results Examples:**

- `results_2025-08-23.zip`
- `uk-results-20250823.zip`
- `outcomes_2025_08_23.zip`

#### Date Formats Supported

- `YYYY-MM-DD` (preferred)
- `YYYYMMDD`
- `YYYY_MM_DD`
- `YYYY/MM/DD`

### Key Features

#### 1. Persistent Daily Progression

- System remembers which days are completed
- Automatically advances to next day after success
- Continues monitoring indefinitely until files arrive

#### 2. Event-Driven Pipeline

- No time-based scheduling required
- Pipeline triggers only when files are ready
- Intelligent dependency management between stages

#### 3. Robust Error Handling

- Validates files before processing
- Retries failed stages with exponential backoff
- Continues processing non-critical stage failures

#### 4. Status Transparency

- Real-time status via JSON files
- Comprehensive logging at all levels
- Web app integration for live monitoring

### Docker Integration

The daily file watcher integrates seamlessly with the existing Docker infrastructure:

- **File Watching**: Monitors Docker volume-mounted directory
- **Database Access**: Uses internal Docker network (postgres:5432)
- **Pipeline Execution**: Runs within existing container network
- **Logging**: Outputs to Docker volume-mounted logs directory

### Web App Integration

Status information is automatically made available to the web app:

- **Current Target Date**: Which day is being monitored
- **File Status**: Which files have been received/validated
- **Pipeline Progress**: Current stage and completion status
- **Historical Data**: Days completed and processing history

### Next Steps

1. **Start the System**: Use `./start_pipeline_integration.sh start`
2. **Monitor Status**: Check `./start_pipeline_integration.sh status`
3. **Place Files**: Add daily ZIP files to `data/daily_downloads/manual_download/`
4. **Watch Processing**: Monitor logs and status files for progress
5. **Review Results**: Check database and analysis outputs

The system is now ready for continuous daily operation, automatically processing each day's racing data as it becomes available and advancing to the next day upon completion.
