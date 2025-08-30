# 🔧 IMMEDIATE ACTION PLAN: Node-RED Integration

## Next Steps for Database, API & Pipeline Integration

### 🎯 IMMEDIATE PRIORITIES (Next 2-4 Hours)

#### ✅ STEP 1: Database Connection Setup (30 minutes)

**Files to modify**: `docker/node-red/package.json`, Node-RED flows

```bash
# 1. Add PostgreSQL node package to Node-RED
echo '"node-red-contrib-postgres": "^1.0.0",' >> docker/node-red/package.json

# 2. Create database config nodes in Node-RED editor
# - Main DB: horse_racing_postgres_clean:5432
# - Cards DB: CARDS_DATABASE_URL
# - Results DB: RESULTS_DATABASE_URL
# - Advanced DB: ADVANCED_DATABASE_URL
```

**Tasks:**

- [ ] Install `node-red-contrib-postgres` package
- [ ] Create PostgreSQL config node for main database
- [ ] Test database connectivity from Node-RED
- [ ] Create simple query execution node
- [ ] Add database health check endpoint: `/api/database/health`

#### ✅ STEP 2: API Integration Points (45 minutes)

**Target APIs to integrate**:

```javascript
// Current API endpoints to convert to Node-RED nodes:
/api/system-status        → Database status checks
/api/trigger-processing   → Data pipeline triggers
/api/web-app/health      → Web app health monitoring
/api/containers/status   → Docker container monitoring
/api/database/stats      → Database performance metrics
```

**Tasks:**

- [ ] Create HTTP request nodes for each API endpoint
- [ ] Add error handling and retry logic
- [ ] Implement response formatting
- [ ] Add API response caching
- [ ] Create API status dashboard panel

#### ✅ STEP 3: Critical Pipeline Integration (60 minutes)

**Python scripts to convert to Node-RED nodes**:

1. **Data Validation Pipeline**

   ```python
   # File: tools/data_validator.py
   # Convert to: Node-RED "Data Validation" node
   # Function: Validate incoming data files
   # Triggers: File upload detection, manual trigger
   ```

2. **Data Processing Pipeline**

   ```python
   # File: tools/data_processor.py
   # Convert to: Node-RED "Data Processing" node
   # Function: Process and transform data
   # Triggers: Post-validation, scheduled runs
   ```

3. **Upload Coordinator**
   ```python
   # File: tools/upload_coordinator.py
   # Convert to: Node-RED "Upload Orchestration" node
   # Function: Coordinate multi-database uploads
   # Triggers: Post-processing, manual upload
   ```

**Tasks:**

- [ ] Create exec nodes to call Python scripts
- [ ] Add progress monitoring and logging
- [ ] Implement error handling and notifications
- [ ] Create pipeline status tracking
- [ ] Add manual trigger buttons in C2 dashboard

---

### 🗃️ DATABASE INTEGRATION CHECKLIST

#### PostgreSQL Connection Nodes Needed:

```json
{
  "main_db": {
    "host": "horse_racing_postgres_clean",
    "port": 5432,
    "database": "horse_racing",
    "user": "horse_racing",
    "password": "secure_password_123"
  },
  "cards_db": {
    "connection_string": "${CARDS_DATABASE_URL}"
  },
  "results_db": {
    "connection_string": "${RESULTS_DATABASE_URL}"
  },
  "advanced_db": {
    "connection_string": "${ADVANCED_DATABASE_URL}"
  }
}
```

#### Database Monitoring Queries:

```sql
-- Database health check
SELECT 1 as healthy;

-- Connection count
SELECT count(*) as active_connections FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('horse_racing')) as db_size;

-- Table row counts
SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del
FROM pg_stat_user_tables;
```

**Tasks:**

- [ ] Create database config nodes for all 4 databases
- [ ] Add connection health monitoring
- [ ] Create database metrics dashboard
- [ ] Implement automatic reconnection logic
- [ ] Add query execution logging

---

### 🔌 API INTEGRATION MAPPING

#### Current C2 Dashboard Buttons → Node-RED Nodes:

```javascript
// C2 Dashboard Functions to implement as Node-RED nodes:

triggerAction('data-validation')  → /api/pipeline/validate
triggerAction('data-processing')  → /api/pipeline/process
triggerAction('upload-data')      → /api/pipeline/upload
triggerAction('generate-ratings') → /api/ml/generate-ratings
triggerAction('ml-training')      → /api/ml/train-models
emergencyStop()                   → /api/pipeline/emergency-stop
refreshStatus()                   → /api/system/refresh-status
```

#### API Endpoints to Create:

```bash
# Pipeline Control APIs
POST /api/pipeline/validate      # Trigger data validation
POST /api/pipeline/process       # Start data processing
POST /api/pipeline/upload        # Begin upload sequence
POST /api/pipeline/emergency-stop # Stop all operations

# ML & Analytics APIs
POST /api/ml/train-models        # Start ML training
POST /api/ml/generate-ratings    # Generate AI selections
GET  /api/ml/model-status        # Get training status
GET  /api/analytics/performance  # Get performance metrics

# System Monitoring APIs
GET  /api/system/health          # Overall system health
GET  /api/database/status        # Database connection status
GET  /api/containers/status      # Docker container status
GET  /api/pipeline/status        # Pipeline execution status
```

**Tasks:**

- [ ] Create HTTP In nodes for each API endpoint
- [ ] Implement business logic in function nodes
- [ ] Add response formatting and error handling
- [ ] Connect to database query nodes
- [ ] Add logging and monitoring

---

### 🔄 PIPELINE WORKFLOW NODES

#### Data Processing Workflow:

```
File Upload → Validation → Processing → Upload → Notification
     ↓            ↓           ↓         ↓         ↓
[File Watch] → [Validate] → [Process] → [Upload] → [Alert]
```

#### Node-RED Flow Structure:

```javascript
// 1. File Watcher Node (monitors data directory)
{
  "type": "watch",
  "property": "/workspace/data/incoming/*",
  "recursive": true
}

// 2. Data Validation Node (calls validation script)
{
  "type": "exec",
  "command": "python /workspace/tools/data_validator.py",
  "addpay": false
}

// 3. Data Processing Node (processes validated data)
{
  "type": "exec",
  "command": "python /workspace/tools/data_processor.py",
  "addpay": false
}

// 4. Upload Coordinator Node (uploads to databases)
{
  "type": "function",
  "func": "// Call upload_coordinator.py with proper parameters"
}

// 5. Notification Node (sends completion alerts)
{
  "type": "http request",
  "method": "POST",
  "url": "http://horse_racing_ntfy:80/pipeline-alerts"
}
```

**Tasks:**

- [ ] Create file watcher nodes for data directories
- [ ] Implement validation workflow with error handling
- [ ] Add processing pipeline with progress tracking
- [ ] Create upload orchestration with rollback capability
- [ ] Implement notification system for all outcomes

---

### 🚀 IMPLEMENTATION ORDER

#### Hour 1: Database Foundation

1. Install PostgreSQL node package
2. Create database config nodes
3. Test basic connectivity
4. Add health check endpoints

#### Hour 2: API Framework

1. Create API endpoint structure
2. Implement basic request/response handling
3. Add error handling and logging
4. Test with C2 dashboard buttons

#### Hour 3: Pipeline Integration

1. Create file monitoring nodes
2. Implement validation workflow
3. Add processing pipeline nodes
4. Test end-to-end data flow

#### Hour 4: Testing & Refinement

1. Test all integrated components
2. Add missing error handling
3. Optimize performance
4. Document new functionality

---

### 🎯 SUCCESS CRITERIA

**End of Integration:**

- ✅ All C2 dashboard buttons trigger Node-RED flows
- ✅ Database queries execute through Node-RED nodes
- ✅ Pipeline scripts integrated as automated workflows
- ✅ Real-time monitoring of all components
- ✅ Error handling and notification system working
- ✅ Complete observability of system state

**Ready for Production:**

- 🚀 Zero-downtime deployments
- 🚀 Automated failover and recovery
- 🚀 Performance monitoring and alerting
- 🚀 Complete audit trail of all operations
