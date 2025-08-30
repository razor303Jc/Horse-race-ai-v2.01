# Node-RED Dashboard Enhancement Documentation

## Overview

Enhanced the Node-RED dashboard with a dedicated **Data Processing** tab that allows users to selectively process horse racing data by date range and data type.

## New Features Added

### 1. Data Processing Tab

- **Purpose**: Interactive data processing with user-controlled parameters
- **Location**: New tab in Node-RED dashboard interface
- **Components**: Date range picker, data type selector, process button, status display

### 2. User Interface Components

#### Date Range Picker

- **Start Date Picker**: Select the beginning date for data processing
- **End Date Picker**: Select the ending date for data processing
- **Validation**: Automatically validates date range (max 30 days)

#### Data Type Selector

- **Cards Data**: Process only cards (race card information)
- **Results Data**: Process only results (race outcome data)
- **Both Cards & Results**: Process both data types together

#### Process Button

- **Trigger**: Starts the data processing workflow
- **Validation**: Checks all parameters before execution
- **Status Updates**: Real-time processing status display

### 3. Backend Processing Script

#### Script Location

```
/tools/node_red_data_processor.py
```

#### Command Line Interface

```bash
python tools/node_red_data_processor.py \
  --start-date 2025-01-14 \
  --end-date 2025-01-14 \
  --type cards \
  --output-format json
```

#### Parameters

- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format
- `--type`: Data type (cards, results, both)
- `--output-format`: Output format (json, text)

### 4. Node-RED Flow Structure

#### Flow Configuration File

```
/node-red/flows-with-data-processing.json
```

#### Key Nodes

1. **Date Range Picker Nodes**: Capture start/end dates
2. **Data Type Selector**: Dropdown for data type selection
3. **Validation Node**: Validates parameters before processing
4. **Execution Node**: Calls the Python processing script
5. **Status Nodes**: Display processing status and results
6. **Notification Nodes**: Success/error notifications

### 5. Validation Features

#### Date Range Validation

- Start date must be before or equal to end date
- Maximum range of 30 days to prevent excessive processing
- Date format validation (YYYY-MM-DD)

#### Data Type Validation

- Required selection from dropdown
- Options: cards, results, both

#### Error Handling

- Parameter validation errors display in UI
- Processing errors show notifications
- Detailed logging to `/logs/data_processing.log`

### 6. Dashboard Integration

#### System Status Section

- System health gauge
- Last update timestamp
- Error count display
- Processing summary

#### Processing Statistics Section

- Recent processing activity
- Data volume charts
- Historical processing data

### 7. Usage Workflow

1. **Select Date Range**: Choose start and end dates
2. **Choose Data Type**: Select cards, results, or both
3. **Validate Parameters**: System checks inputs automatically
4. **Start Processing**: Click the process button
5. **Monitor Progress**: View real-time status updates
6. **Review Results**: Check completion notifications and logs

### 8. Technical Architecture

#### Frontend (Node-RED UI)

- Date picker components
- Dropdown selectors
- Button triggers
- Status displays
- Notification system

#### Backend (Python Script)

- Parameter validation
- Data processing logic
- Error handling
- Logging system
- Result reporting

#### Integration Layer

- Node-RED exec nodes
- Command parameter passing
- Output parsing
- Status updates

### 9. Error Handling

#### Validation Errors

- Missing parameters
- Invalid date ranges
- Date format errors
- Range limit exceeded

#### Processing Errors

- Script execution failures
- Database connection issues
- File processing errors
- Timeout handling

### 10. Logging and Monitoring

#### Log Files

- `/logs/data_processing.log`: Detailed processing logs
- Node-RED debug output: Real-time flow monitoring

#### Status Tracking

- Processing start/end times
- Success/failure status
- Record counts processed
- Error details and codes

## Configuration

### Prerequisites

- Node-RED dashboard nodes installed
- PostgreSQL database configured
- Python environment with required packages
- Proper file permissions for script execution

### Deployment

1. Import flows-with-data-processing.json into Node-RED
2. Configure database connections
3. Set up email notifications (optional)
4. Deploy flows to activate dashboard

### Customization

- Modify date range limits in validation code
- Add additional data types to dropdown
- Customize UI styling with CSS classes
- Extend processing script for new data sources

## Benefits

### User Experience

- No command-line interaction required
- Visual feedback and status updates
- Error prevention through validation
- Intuitive date and type selection

### Operational

- Selective data processing saves time
- Reduced system load with date range limits
- Comprehensive error handling and logging
- Integration with existing Node-RED workflows

### Maintenance

- Centralized processing logic
- Consistent error handling
- Automated logging
- Easy to extend and modify

## Future Enhancements

### Possible Additions

- Progress bars for long-running processes
- Data preview before processing
- Scheduling capabilities
- Advanced filtering options
- Export processed data functionality
- Integration with ML model training

### Integration Opportunities

- Connect to existing automation flows
- Link with prediction generation
- Integration with backup systems
- Connection to monitoring dashboards
