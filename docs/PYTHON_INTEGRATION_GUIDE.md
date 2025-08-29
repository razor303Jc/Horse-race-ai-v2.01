# 🐍 Python Integration Node-RED Setup Guide

## 🎯 **Complete Python Script Integration**

This guide shows how to integrate your Node-RED flows with all your existing Python scripts for full automation of your Horse Racing AI platform.

## 📋 **Available Python Scripts Integration**

### 🔄 **Data Processing & Pipeline**

- **Automated Data Pipeline**: `tools/automation/automated_data_pipeline.py`
- **Race Card Fetcher**: `tools/data_processing/race_card_fetcher.py`
- **Race Data Analysis**: `tools/analysis/race_data_analysis.py`
- **Manual Data Processor**: `process_manual_data.py`

### 🤖 **Machine Learning & Training**

- **Unified ML Trainer**: `tools/ml_training/unified_ml_trainer.py`
- **Cyclic Training**: `scripts/run_cyclic_training.py`
- **Automated Model Retrainer**: `tools/integration/automated_model_retrainer.py`
- **ML Cycle Manager**: `tools/ml_training/automated_ml_cycle_manager.py`

### 🎯 **AI Analysis & Selections**

- **Race Data Quality Analyzer**: `src/contextual_ai/race_data_quality_analyzer.py`
- **Race Trends Analyzer**: `src/horse_racing_ai/analysis/race_trends_analyzer.py`
- **AI Selections Generator**: `scripts/run_real_selections.py`
- **Performance Tracking**: `tools/performance/race_results_tracker.py`

### 📊 **Database & Monitoring**

- **Database Health Check**: `scripts/check_db_metrics.py`
- **Database Connection Test**: `scripts/test_db_connection.py`
- **Schema Setup**: `scripts/setup_schema.py`

## 🚀 **Import and Setup**

### Step 1: Import the Integration Flows

1. Open Node-RED editor: http://localhost:1881
2. Click the hamburger menu (☰) → Import
3. **Import file**: `horse_racing_python_integration_flows.json`
4. Click "Import" and "Deploy"

### Step 2: Configure Database Credentials

Set up database credentials for each config node:

- **Username**: `horse_racing`
- **Password**: `secure_password_123`
- **Host**: `host.docker.internal`
- **Port**: `5432`

### Step 3: Update Email Settings

In all email formatting nodes, update:

```javascript
msg.to = "your-actual-email@example.com";
```

## 📊 **Available Automation Workflows**

### 🔄 **Python Integration Tab**

**Manual Execution Controls:**

- **Data Pipeline**: Run complete data processing pipeline
- **Race Analysis**: Execute race data quality analysis
- **AI Selections**: Generate AI-powered race selections
- **Performance Tracking**: Track and analyze betting performance

**Features:**

- Real-time execution monitoring
- Success/error handling with email notifications
- Debug output for troubleshooting

### 🤖 **ML Training Tab**

**Training Operations:**

- **Unified ML Training**: Run comprehensive model training
- **Cyclic Training**: Execute training in cycles for optimization
- **Model Retraining**: Automated model lifecycle management

**Features:**

- Training progress monitoring
- Performance metrics tracking
- Automated model deployment

### ⏰ **Scheduled Automation**

**Automated Schedule:**

- **00:30**: Early morning ML training (when enabled in config)
- **06:00**: Daily data pipeline processing
- **20:00**: Evening analysis and reports
- **08:00 Sat/Sun**: Weekend AI selections generation

### 📊 **Monitoring Dashboard**

**Real-time Controls:**

- **Run Pipeline**: Manual data pipeline execution
- **Train Models**: Start ML training on demand
- **AI Selections**: Generate selections manually
- **Check DB**: Database health verification

**System Status:**

- Database connectivity status
- Python script execution status
- ML training progress
- Email notification status

## 🔧 **Script Execution Environment**

All Python scripts run in the Docker container environment with:

- **Working Directory**: `/app` (project root)
- **Python Path**: Pre-configured with project modules
- **Database Access**: Direct connection to PostgreSQL containers
- **Environment Variables**: Loaded from `.env` file

## 🔄 **Integration Workflow Examples**

### Morning Automation (06:00)

1. **Data Pipeline** → Fetch and process race cards
2. **Quality Analysis** → Analyze data reliability
3. **Email Report** → Send morning status update

### Evening Analysis (20:00)

1. **Results Tracking** → Update race results
2. **Performance Analysis** → Calculate ROI and accuracy
3. **Trend Analysis** → Identify betting patterns
4. **Email Summary** → Send evening performance report

### Weekend Selections (Saturday/Sunday 08:00)

1. **Data Refresh** → Update race cards
2. **ML Prediction** → Generate AI selections
3. **Quality Check** → Validate selection confidence
4. **Email Selections** → Send AI picks to user

## 🚨 **Error Handling & Notifications**

### Success Notifications

- ✅ Data pipeline completion
- ✅ ML training success
- ✅ AI selections generated
- ✅ Performance tracking updates

### Error Alerts

- ❌ Script execution failures
- ❌ Database connection issues
- ❌ ML training errors
- ❌ Data processing problems

### Debug Information

- Real-time script output in Node-RED debug panel
- Execution timestamps and duration
- Error details and stack traces
- Performance metrics and statistics

## 🎯 **Advanced Features**

### Conditional Execution

- Scripts only run when data is available
- ML training skips when models are up-to-date
- Email notifications include relevant context

### Performance Optimization

- Background execution for long-running tasks
- Parallel processing where appropriate
- Resource usage monitoring

### Integration Benefits

- **Unified Control**: All scripts manageable from Node-RED
- **Visual Workflow**: See automation flow graphically
- **Real-time Monitoring**: Live execution status
- **Email Integration**: Automated notifications
- **Scheduling**: Precise timing control
- **Error Recovery**: Automated retry logic

## 🔗 **Access Points**

- **Node-RED Editor**: http://localhost:1881
- **Dashboard**: http://localhost:1881/ui
- **Main Web App**: http://localhost:3000
- **Database Admin**: http://localhost:8083

## ✅ **Ready for Production**

Once configured, your Node-RED automation will:

1. Execute Python scripts on schedule
2. Monitor execution status
3. Send email notifications
4. Provide dashboard controls
5. Handle errors gracefully
6. Log all activities

**Your complete Horse Racing AI platform is now fully integrated with automated Python script execution!** 🏇🤖
