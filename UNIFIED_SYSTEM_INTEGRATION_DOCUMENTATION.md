# Horse Racing AI - Unified System Integration

## Overview

This document describes the complete integration of the Horse Racing AI system, combining Node-RED automation, API services, and a web application into a unified pipeline.

## System Architecture

### 🏗️ Components

#### 1. Node-RED Dashboard & Automation (`localhost:1880`)

- **Main Automation Tab**: Daily scheduled data processing pipeline
- **Data Processing & APIs Tab**: Manual controls and API integration
- **Monitoring & Alerts Tab**: System health monitoring and alerts

#### 2. Web Application (`localhost:8080`)

- **Dashboard**: System overview with status indicators and recent predictions
- **Data Processing**: Interactive controls for data processing with date ranges
- **Monitoring**: Real-time system health and performance metrics
- **Predictions**: Display of recent AI predictions and results

#### 3. API Services

- **Prediction API** (`localhost:5000`): ML prediction services
- **ML Management API** (`localhost:5001`): Model training and management

### 🔄 Integration Flow

```
Web App ↔ Node-RED ↔ APIs ↔ Database
    ↓         ↓        ↓        ↓
   HTTP    Automation  ML     PostgreSQL
  Interface  Pipeline Services  Storage
```

## Key Features

### ✅ Consolidated Data Processing

- **Single Interface**: All data processing controls unified in one location
- **Date Range Selection**: Custom date range processing with type selection
- **Real-time Feedback**: Live processing status and error handling
- **API Integration**: Automatic API updates after data processing

### 🌐 Web Application Integration

- **HTTP Endpoints**: Node-RED exposes HTTP endpoints for web app integration
- **RESTful API**: Clean API interface for triggering operations
- **Real-time Status**: Live system status monitoring
- **User-Friendly Interface**: Bootstrap-based responsive design

### 🤖 Automated Pipeline

- **Daily Scheduling**: Automatic daily data processing at 7 AM
- **Error Handling**: Comprehensive error tracking and alerts
- **API Startup**: Automatic API service initialization
- **Health Monitoring**: Continuous system health checks

## File Structure

```
/home/jc/Documents/Horse-race-ai-v2.04/
├── node-red/
│   ├── flows-unified-with-apis.json    # Main Node-RED flow
│   └── http-endpoints-addon.json       # HTTP endpoint configurations
├── web_app/
│   ├── racing_web_app.py              # Flask web application
│   ├── requirements.txt               # Python dependencies
│   └── templates/
│       ├── dashboard.html             # Main dashboard
│       ├── data_processing.html       # Data processing interface
│       └── monitoring.html            # System monitoring
├── api/
│   ├── prediction_api.py              # Prediction service
│   ├── ml_management_api.py           # ML management service
│   └── requirements.txt               # API dependencies
└── tools/
    └── node_red_data_processor.py     # Backend processing script
```

## System Startup

### 🚀 Quick Start

```bash
# Start all services
./start_integrated_system.sh

# Check system status
./check_system_status.sh

# Stop all services
./stop_system.sh
```

### 📊 Access Points

- **Node-RED Dashboard**: http://localhost:1880
- **Web Application**: http://localhost:8080
- **Prediction API**: http://localhost:5000
- **ML Management API**: http://localhost:5001

## Usage Guide

### 1. Web Application

- Navigate to http://localhost:8080
- Use the dashboard to monitor system status
- Access data processing controls for manual operations
- View predictions and system health

### 2. Node-RED Interface

- Access http://localhost:1880 for flow management
- Use inject nodes for manual triggers
- Monitor debug output for real-time feedback
- Configure automation schedules

### 3. API Integration

- APIs automatically start with the pipeline
- Web app communicates with Node-RED via HTTP endpoints
- Data processing triggers API reload operations
- Health checks ensure service availability

## Configuration

### Database Settings

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'racing_data',
    'user': 'racing_user',
    'password': 'racing_password'
}
```

### API Endpoints

- Node-RED: http://localhost:1880
- Prediction API: http://localhost:5000
- ML Management API: http://localhost:5001
- Web Application: http://localhost:8080

### Data Processing Options

- **Types**: `cards`, `results`, `both`
- **Date Ranges**: Single day, week, custom range
- **Sources**: Manual, scheduled, web app triggered

## Monitoring & Health Checks

### System Status Indicators

- ✅ **Green**: Service online and responding
- ❌ **Red**: Service offline or error
- 🔄 **Yellow**: Service starting or processing

### Automatic Monitoring

- Health checks every 5 minutes
- API status monitoring
- Database connection verification
- Processing status tracking

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Check if ports 1880, 5000, 5001, 8080 are available
2. **Database Connection**: Verify PostgreSQL is running and accessible
3. **Node Dependencies**: Ensure all Python packages are installed
4. **Permission Issues**: Check script execution permissions

### Log Files

- Node-RED: `logs/node-red.log`
- Prediction API: `logs/prediction-api.log`
- ML Management API: `logs/ml-management-api.log`
- Web Application: `logs/web-app.log`

## Development Notes

### HTTP Integration

Node-RED exposes HTTP endpoints for web app integration:

- `/trigger/data_processing` - Trigger data processing
- `/trigger/full_pipeline` - Trigger complete pipeline
- `/trigger/start_apis` - Start API services

### Data Flow

1. Web app sends HTTP requests to Node-RED
2. Node-RED processes requests and triggers appropriate flows
3. Flows execute Python scripts for data processing
4. Results are logged and APIs are notified
5. Web app displays status and results

### Extensibility

- Add new processing types in Node-RED flows
- Extend web app with additional pages
- Integrate new APIs via Node-RED HTTP nodes
- Add custom monitoring metrics

## Security Considerations

### Current Implementation

- Local network access only
- No authentication implemented
- Database credentials in configuration files

### Production Recommendations

- Implement user authentication
- Use environment variables for credentials
- Add HTTPS/SSL certificates
- Implement rate limiting
- Add input validation and sanitization

## Performance Optimization

### Current Optimizations

- Async processing in Node-RED
- Connection pooling for database
- Background API services
- Efficient data processing scripts

### Future Enhancements

- Caching layer for frequent queries
- Load balancing for multiple instances
- Database indexing optimization
- API response compression

## Conclusion

The integrated system provides a comprehensive solution for horse racing data processing and AI predictions, combining the visual flow-based automation of Node-RED with a modern web interface and robust API services. The unified architecture ensures seamless data flow and real-time monitoring across all components.
