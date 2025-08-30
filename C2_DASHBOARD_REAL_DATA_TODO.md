# 🎯 C2 Dashboard Real Data Integration - TODO List

## 🚨 **PRIORITY: Remove ALL Mock Data and Hardcoded Values**

Based on analysis of the current C2 dashboard at `http://c2.horse-racing.local/c2`, the following areas contain mock/hardcoded data that must be replaced with real database queries and live system monitoring.

---

## 📊 **1. SYSTEM STATUS PANEL**

**Location**: `/html/body/div[2]/div[1]` - "📊 System Status"

### ❌ **Current Issues**:

- All status indicators hardcoded as 'healthy'
- Static IP addresses displayed (no dynamic discovery)
- No real container health checks

### ✅ **Required Changes**:

#### **1.1 Database Status (172.20.0.10)** ✅ **COMPLETED**

- [x] **Write Test**: Create integration test for real database health integration in C2 status
- [x] **Replace**: `database: 'healthy'` hardcoded value
- [x] **Add**: Real PostgreSQL health check via existing `/database/health` endpoint
- [x] **Implement**: HTTP request from C2 status function to database health API
- [x] **Query**: Use existing health endpoint that returns connection status + performance
- [x] **Status Logic**:
  - 🟢 Green: Connection successful + query response < 100ms
  - 🟡 Yellow: Connection slow (100-500ms)
  - 🔴 Red: Connection failed or timeout
- [ ] **Test Coverage**: Verify C2 dashboard shows real database status instead of hardcoded values

#### **1.2 Redis Cache Status (172.20.0.11)**

- [ ] **Write Test**: Create Redis health endpoint integration test
- [ ] **Create Endpoint**: `/redis/health` following database health pattern
- [ ] **Replace**: `redis: 'healthy'` hardcoded value
- [ ] **Add**: Real Redis health check via `PING` command
- [ ] **Implement**: Redis connection test with timeout
- [ ] **Monitor**: Redis memory usage and connected clients
- [ ] **Status Logic**:
  - 🟢 Green: PING returns PONG + memory < 80%
  - 🟡 Yellow: High memory usage (80-95%)
  - 🔴 Red: Connection failed or memory > 95%
- [ ] **Test Coverage**: Verify Redis health endpoint returns proper status structure

#### **1.3 Data Pipeline Status (172.20.0.13)**

- [ ] **Write Test**: Create container health monitoring test suite
- [ ] **Create Endpoint**: `/containers/health` for Docker container monitoring

- [ ] **Replace**: `pipeline: 'healthy'` hardcoded value
- [ ] **Add**: Docker container health check for `horse_racing_data_pipeline_clean`
- [ ] **Implement**: Pipeline API endpoint health check
- [ ] **Monitor**: Active pipeline processes and queue status
- [ ] **Status Logic**:
  - 🟢 Green: Container running + API responsive + no stuck processes
  - 🟡 Yellow: Container running but high load or warnings
  - 🔴 Red: Container stopped or API unreachable

#### **1.4 ML Trainer Status (172.20.0.14)**

- [ ] **Replace**: `ml_trainer: 'healthy'` hardcoded value
- [ ] **Add**: Docker container health check for `horse_racing_ml_trainer_clean`
- [ ] **Implement**: ML service API health check
- [ ] **Monitor**: Training job status and model availability
- [ ] **Status Logic**:
  - 🟢 Green: Container running + models loaded + no training errors
  - 🟡 Yellow: Training in progress or model loading
  - 🔴 Red: Container stopped or training failed

#### **1.5 Web App Status (172.20.0.12)**

- [ ] **Replace**: `web_app: 'healthy'` hardcoded value
- [ ] **Add**: HTTP health check to web application
- [ ] **Implement**: API endpoint availability test
- [ ] **Monitor**: Response time and error rates
- [ ] **Status Logic**:
  - 🟢 Green: HTTP 200 response + response time < 200ms
  - 🟡 Yellow: Slow response (200-1000ms) or occasional errors
  - 🔴 Red: HTTP errors or timeout

---

## 📈 **2. PERFORMANCE METRICS PANEL**

**Location**: `/html/body/div[2]/div[3]` - "📈 Performance Metrics"

### ❌ **Current Issues**:

- All metrics use `Math.random()` for fake data
- No connection to actual AI selections database
- Hardcoded ROI and profit/loss calculations

### ✅ **Required Changes**:

#### **2.1 Today's Selections**

- [ ] **Replace**: `Math.floor(Math.random() * 20)` with real query
- [ ] **Database Query**:
  ```sql
  SELECT COUNT(*) FROM ai_selections
  WHERE DATE(created_at) = CURRENT_DATE
  AND status = 'active'
  ```
- [ ] **Fallback**: Show 0 if no database connection

#### **2.2 Success Rate**

- [ ] **Replace**: `Math.floor(Math.random() * 100)` with real calculation
- [ ] **Database Query**:
  ```sql
  SELECT
    ROUND(
      (COUNT(CASE WHEN result = 'win' THEN 1 END) * 100.0 / COUNT(*)), 2
    ) as success_rate
  FROM ai_selections
  WHERE DATE(created_at) >= CURRENT_DATE - INTERVAL '30 days'
  AND result IS NOT NULL
  ```
- [ ] **Display**: Show as percentage with 1 decimal place

#### **2.3 ROI (Return on Investment)**

- [ ] **Replace**: `(Math.random() * 50 - 10).toFixed(1)` with real calculation
- [ ] **Database Query**:
  ```sql
  SELECT
    ROUND(
      ((SUM(CASE WHEN result = 'win' THEN payout ELSE 0 END) - SUM(stake)) / SUM(stake) * 100), 1
    ) as roi
  FROM betting_records
  WHERE DATE(placed_at) >= CURRENT_DATE - INTERVAL '30 days'
  ```
- [ ] **Color Logic**: Green if positive, Red if negative

#### **2.4 Profit/Loss**

- [ ] **Replace**: `(Math.random() * 1000 - 200).toFixed(2)` with real calculation
- [ ] **Database Query**:
  ```sql
  SELECT
    ROUND(
      SUM(CASE WHEN result = 'win' THEN payout ELSE 0 END) - SUM(stake), 2
    ) as profit_loss
  FROM betting_records
  WHERE DATE(placed_at) >= CURRENT_DATE - INTERVAL '30 days'
  ```
- [ ] **Currency**: Format as £XXX.XX with proper currency symbols

#### **2.5 Models Trained**

- [ ] **Replace**: `Math.floor(Math.random() * 10)` with real count
- [ ] **Database Query**:
  ```sql
  SELECT COUNT(*) FROM ml_models
  WHERE DATE(created_at) = CURRENT_DATE
  AND status = 'completed'
  ```
- [ ] **Include**: Model training timestamp and accuracy

---

## ⚡ **3. REAL-TIME PROCESSING PANEL**

**Location**: `/html/body/nav/div/ul/li[2]/a` - "⚡ Real-time Processing"

### ❌ **Current Issues**:

- Queue size uses `Math.floor(Math.random() * 10)`
- Processing rate hardcoded as `Math.floor(Math.random() * 20) + ' files/min'`
- No real file processing monitoring

### ✅ **Required Changes**:

#### **3.1 Queue Size**

- [ ] **Replace**: Random generation with real queue monitoring
- [ ] **Redis Query**: `LLEN processing_queue` for current queue length
- [ ] **Alternative**: Check file system queue directory
- [ ] **Monitor**: Different queue types (cards, results, analysis)

#### **3.2 Processing Rate**

- [ ] **Replace**: Random `files/min` with real throughput calculation
- [ ] **Implementation**: Track processed files in last 60 seconds
- [ ] **Redis Counter**: Increment on each file processed, decay over time
- [ ] **Calculate**: `(files_processed_last_minute) files/min`

#### **3.3 Error Count**

- [ ] **Add**: Real error monitoring from processing logs
- [ ] **Log Analysis**: Parse recent log files for ERROR level entries
- [ ] **Database Query**: Error tracking table with timestamps
- [ ] **Alert Logic**: Red status if errors > 5 in last hour

#### **3.4 Processing Status**

- [ ] **Replace**: 'Idle' hardcoded with real pipeline status
- [ ] **Monitor**: Current pipeline stage from Redis or database
- [ ] **Status Options**: 'Processing Cards', 'Uploading Data', 'Training Models', 'Idle'

---

## 🔧 **4. PIPELINE CONTROL PANEL**

**Location**: `/html/body/div[2]/div[2]` - "🔧 Pipeline Control"

### ❌ **Current Issues**:

- Pipeline progress uses `Math.floor(Math.random() * 100)`
- Pipeline stage hardcoded as 'Processing Data'
- Buttons trigger fake actions

### ✅ **Required Changes**:

#### **4.1 Pipeline Progress**

- [ ] **Replace**: Random percentage with real progress tracking
- [ ] **Implementation**: Track completion of pipeline stages
- [ ] **Calculation**: `(completed_stages / total_stages) * 100`
- [ ] **Update**: Real-time progress from pipeline API

#### **4.2 Pipeline Stage**

- [ ] **Replace**: 'Processing Data' hardcoded value
- [ ] **Monitor**: Current active pipeline stage from Redis
- [ ] **Stages**: 'Data Validation', 'Data Processing', 'Data Upload', 'Ratings Generation', 'ML Training'
- [ ] **Timestamp**: Show when current stage started

#### **4.3 Button Actions**

- [ ] **Replace**: Fake logging with real pipeline API calls
- [ ] **Implement**: POST requests to actual pipeline endpoints
- [ ] **Response Handling**: Show real success/error messages
- [ ] **Status Updates**: Refresh dashboard after action completion

---

## 🤖 **5. AI SELECTION MONITOR PANEL**

**Location**: `/html/body/div[2]/div[5]` - "🤖 AI Selection Monitor"

### ❌ **Current Issues**:

- Active models hardcoded as `3`
- Last prediction hardcoded as 'Horse #7 - Win'
- Confidence and accuracy use random generation

### ✅ **Required Changes**:

#### **5.1 Active Models**

- [ ] **Replace**: Hardcoded `3` with real model count
- [ ] **Database Query**:
  ```sql
  SELECT COUNT(*) FROM ml_models
  WHERE status = 'active'
  AND last_used > CURRENT_TIMESTAMP - INTERVAL '24 hours'
  ```

#### **5.2 Last Prediction**

- [ ] **Replace**: 'Horse #7 - Win' with real latest prediction
- [ ] **Database Query**:
  ```sql
  SELECT horse_name, prediction_type, race_time
  FROM ai_predictions
  ORDER BY created_at DESC
  LIMIT 1
  ```
- [ ] **Format**: "Horse Name - Prediction (Time)"

#### **5.3 Confidence Score**

- [ ] **Replace**: Random generation with real confidence from ML model
- [ ] **Database Query**: Latest prediction confidence score
- [ ] **Color Logic**: Green >80%, Yellow 60-80%, Red <60%

#### **5.4 Model Accuracy**

- [ ] **Replace**: Random generation with real accuracy metrics
- [ ] **Database Query**: Calculate accuracy from recent predictions vs results
- [ ] **Time Period**: Last 30 days performance

---

## ✅ **6. DATA VALIDATION PANEL**

**Location**: `/html/body/div[2]/div[4]` - "✅ Data Validation"

### ❌ **Current Issues**:

- All validation metrics hardcoded as 0 or 'Never'
- No real validation status tracking

### ✅ **Required Changes**:

#### **6.1 Last Validation**

- [ ] **Replace**: 'Never' with real timestamp from validation logs
- [ ] **Database Query**: Last validation run timestamp
- [ ] **Format**: "X minutes ago" or "Today at HH:MM"

#### **6.2 Records Processed**

- [ ] **Replace**: `0` with real count from last validation
- [ ] **Database Query**: Sum of records validated in last run
- [ ] **Include**: Breakdown by data type (cards, results, odds)

#### **6.3 Validation Errors**

- [ ] **Replace**: `0` with real error count
- [ ] **Database Query**: Count of validation errors found
- [ ] **Alert Logic**: Red background if errors > 0

---

## 📝 **7. REAL-TIME LOGS PANEL**

**Location**: `/html/body/div[2]/div[6]` - "📝 Real-time Logs"

### ❌ **Current Issues**:

- Static log entries: 'C2 Command Center initialized', 'Monitoring all systems...'
- No real log streaming

### ✅ **Required Changes**:

#### **7.1 Live Log Streaming**

- [ ] **Replace**: Static messages with real log entries
- [ ] **Implementation**: WebSocket connection to log aggregator
- [ ] **Sources**: Node-RED, Pipeline, ML Trainer, Web App logs
- [ ] **Filtering**: Show only INFO, WARN, ERROR levels

#### **7.2 Log Entry Format**

- [ ] **Timestamp**: Real timestamps from log entries
- [ ] **Level**: Color-coded log levels (INFO=white, WARN=yellow, ERROR=red)
- [ ] **Source**: Show which service generated the log
- [ ] **Auto-scroll**: Keep newest entries visible

---

## 🗄️ **8. DATABASE INTEGRATION REQUIREMENTS**

### **8.1 Required Database Tables**

- [ ] **ai_selections**: Store AI predictions and results
- [ ] **betting_records**: Track betting history and outcomes
- [ ] **ml_models**: Model metadata and performance metrics
- [ ] **validation_logs**: Data validation history
- [ ] **pipeline_status**: Current pipeline state and progress
- [ ] **system_health**: Health check results and timestamps

### **8.2 Required PostgreSQL Node Configurations**

- [ ] **Main Database**: `horse_racing_postgres_clean:5432`
- [ ] **Cards Database**: Separate connection for card data
- [ ] **Results Database**: Separate connection for results data
- [ ] **Connection Pooling**: Configure max connections and timeouts

### **8.3 Required Redis Integrations**

- [ ] **Queue Monitoring**: Real-time queue length tracking
- [ ] **Processing Counters**: File processing rate calculations
- [ ] **Pipeline State**: Current pipeline stage and progress
- [ ] **Cache Health**: Memory usage and connection monitoring

---

## 🔄 **9. REAL-TIME UPDATE MECHANISMS**

### **9.1 Auto-refresh Intervals**

- [ ] **System Status**: Every 10 seconds
- [ ] **Performance Metrics**: Every 30 seconds
- [ ] **Processing Stats**: Every 5 seconds
- [ ] **Logs**: Real-time streaming (WebSocket)

### **9.2 Error Handling**

- [ ] **Database Timeout**: Show 'Connection Lost' status
- [ ] **API Failures**: Graceful degradation with last known values
- [ ] **Network Issues**: Retry logic with exponential backoff

### **9.3 Performance Optimization**

- [ ] **Caching**: Cache expensive queries for 30-60 seconds
- [ ] **Batch Updates**: Group multiple status updates
- [ ] **Efficient Queries**: Use indexed columns and LIMIT clauses

---

## 🎯 **10. IMPLEMENTATION PRIORITY**

### **Phase 1: Critical Data (Week 1)**

1. ✅ Database health status (already working)
2. 🔄 System container health checks
3. 🔄 Real queue monitoring
4. 🔄 Basic performance metrics

### **Phase 2: AI Metrics (Week 2)**

1. 🔄 AI selection counts and results
2. 🔄 Model performance tracking
3. 🔄 Real prediction data
4. 🔄 ROI calculations

### **Phase 3: Advanced Features (Week 3)**

1. 🔄 Real-time log streaming
2. 🔄 Pipeline progress tracking
3. 🔄 Advanced error monitoring
4. 🔄 Performance optimization

---

## 🚀 **SUCCESS CRITERIA**

### **Definition of Done:**

- [ ] **Zero hardcoded values** in all dashboard panels
- [ ] **Real database queries** for all metrics
- [ ] **Live container monitoring** for all services
- [ ] **Functional pipeline controls** with real API integration
- [ ] **Error handling** for all failure scenarios
- [ ] **Performance targets**: Dashboard loads < 2 seconds
- [ ] **Accuracy**: All displayed data matches database reality
- [ ] **Responsiveness**: Updates reflect real system changes within 30 seconds

### **Testing Checklist:**

- [ ] All metrics update when underlying data changes
- [ ] Dashboard handles database connection failures gracefully
- [ ] Container restarts are reflected in status indicators
- [ ] Pipeline actions trigger real system responses
- [ ] Log entries appear in real-time
- [ ] Performance metrics match manual database queries
- [ ] Mobile responsiveness maintained with real data

---

## 📚 **REFERENCE DOCUMENTATION**

- **Database Schema**: Document all table structures and relationships
- **API Endpoints**: Document all pipeline and ML service APIs
- **Error Codes**: Standardize error handling across all components
- **Performance Benchmarks**: Establish baseline metrics for monitoring

---

**🎯 GOAL**: Transform the C2 dashboard from a static mock interface into a fully functional real-time monitoring and control system for the Horse Racing AI pipeline.\*\*
