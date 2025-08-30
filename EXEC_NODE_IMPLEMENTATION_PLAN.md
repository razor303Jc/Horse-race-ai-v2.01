# 🚀 EXEC NODE IMPLEMENTATION PLAN

## Node-RED Python Script Integration Strategy

### 📋 **IDENTIFIED KEY SCRIPTS FOR INTEGRATION**

Based on analysis of the Horse Racing AI codebase, here are the priority Python scripts to convert to Node-RED exec nodes:

#### **🎯 TIER 1: Core Pipeline Scripts (Immediate Priority)**

1. **Manual Pipeline Trigger**
   - **Script**: `tools/manual_pipeline_trigger.py`
   - **Purpose**: Orchestrate all pipeline stages after data upload
   - **Current Usage**: Manual execution via command line
   - **Node-RED Integration**: Primary automation trigger

2. **Data Relationships Pipeline**
   - **Script**: `tools/data_processing/automated_relationships_pipeline.py`
   - **Purpose**: Process jockey/trainer statistics and relationships
   - **Current Usage**: Called by manual pipeline trigger
   - **Node-RED Integration**: Automated data processing workflow

3. **Performance Tracker**
   - **Script**: `tools/automation/daily_performance_tracker.py`
   - **Purpose**: Track AI model performance metrics
   - **Current Usage**: Called by manual pipeline trigger
   - **Node-RED Integration**: Automated performance monitoring

#### **🎯 TIER 2: ML Training Scripts (Secondary Priority)**

4. **ML Training Pipeline**
   - **Script**: `docker/ml_training/unified_ml_trainer.py`
   - **Purpose**: Train machine learning models
   - **Current Usage**: Manual execution
   - **Node-RED Integration**: Scheduled ML training automation

5. **AI Selections Generator**
   - **Script**: `scripts/run_real_selections.py`
   - **Purpose**: Generate AI-powered race predictions
   - **Current Usage**: Manual execution
   - **Node-RED Integration**: Automated daily selections

#### **🎯 TIER 3: Utility Scripts (Future Enhancement)**

6. **Data Validator**
   - **Script**: `docker/automation/data_validator.py`
   - **Purpose**: Validate incoming data files
   - **Current Usage**: Manual validation
   - **Node-RED Integration**: Automated file validation

---

## 🏗️ **NODE-RED EXEC NODE ARCHITECTURE**

### **Standard Exec Node Configuration**

```javascript
{
  "type": "exec",
  "name": "Python Script Runner",
  "command": "docker",
  "addpay": false,
  "append": "",
  "useSpawn": false,
  "timer": "",
  "winHide": false,
  "oldrc": false,
  "env": {
    "PYTHONPATH": "/app",
    "PYTHONUNBUFFERED": "1"
  },
  "killSignal": "SIGTERM",
  "timeout": "600"  // 10 minutes default
}
```

### **Script-Specific Configurations**

#### **1. Manual Pipeline Trigger Exec Node**

```javascript
{
  "id": "manual-pipeline-exec",
  "type": "exec",
  "name": "Manual Pipeline Trigger",
  "command": "docker exec horse_racing_data_pipeline_clean python /app/tools/manual_pipeline_trigger.py --all",
  "timeout": "1800",  // 30 minutes
  "env": {
    "TARGET_DATE": "{{msg.date || new Date().toISOString().split('T')[0]}}",
    "PYTHONUNBUFFERED": "1"
  }
}
```

#### **2. Data Relationships Pipeline Exec Node**

```javascript
{
  "id": "data-relationships-exec",
  "type": "exec", 
  "name": "Data Relationships Pipeline",
  "command": "docker exec horse_racing_data_pipeline_clean python /app/tools/data_processing/automated_relationships_pipeline.py",
  "timeout": "600",  // 10 minutes
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

#### **3. Performance Tracker Exec Node**

```javascript
{
  "id": "performance-tracker-exec",
  "type": "exec",
  "name": "Daily Performance Tracker", 
  "command": "docker exec horse_racing_ml_trainer_clean python /app/tools/automation/daily_performance_tracker.py",
  "timeout": "300",  // 5 minutes
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

#### **4. ML Training Exec Node**

```javascript
{
  "id": "ml-training-exec",
  "type": "exec",
  "name": "ML Model Training",
  "command": "docker exec horse_racing_ml_trainer_clean python /app/docker/ml_training/unified_ml_trainer.py",
  "timeout": "3600",  // 60 minutes
  "env": {
    "PYTHONUNBUFFERED": "1",
    "ML_TRAINING_MODE": "automated"
  }
}
```

#### **5. AI Selections Generator Exec Node**

```javascript
{
  "id": "ai-selections-exec",
  "type": "exec",
  "name": "AI Selections Generator",
  "command": "docker exec horse_racing_ml_trainer_clean python /app/scripts/run_real_selections.py",
  "timeout": "180",  // 3 minutes
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

---

## 🔧 **INPUT/OUTPUT DATA FLOW DESIGN**

### **Input Message Structure**

```javascript
// Standard input message for all exec nodes
msg = {
  "payload": {
    "action": "trigger",
    "parameters": {
      "date": "2025-08-30",
      "mode": "automated",
      "priority": "normal"
    }
  },
  "timestamp": "2025-08-30T19:30:00Z",
  "source": "c2_dashboard"
}
```

### **Output Message Structure**

```javascript
// Standard output message from exec nodes
msg = {
  "payload": {
    "success": true,
    "returncode": 0,
    "stdout": "Script output...",
    "stderr": "",
    "execution_time": "45.2s",
    "script": "manual_pipeline_trigger.py"
  },
  "timestamp": "2025-08-30T19:35:00Z",
  "duration_ms": 45200
}
```

---

## 🚨 **ERROR HANDLING & MONITORING STRATEGY**

### **Error Classification**

```javascript
// Error handling in function nodes after exec nodes
const classifyError = (stderr, returncode) => {
  if (returncode === 0) return "success";
  
  if (stderr.includes("TimeoutExpired")) return "timeout";
  if (stderr.includes("connection") || stderr.includes("database")) return "connection_error";
  if (stderr.includes("FileNotFoundError")) return "missing_file";
  if (stderr.includes("PermissionError")) return "permission_error";
  
  return "general_error";
};
```

### **Retry Logic**

```javascript
// Retry mechanism for failed exec nodes
const handleRetry = (msg, errorType) => {
  const retryCount = msg.retryCount || 0;
  const maxRetries = 3;
  
  if (retryCount < maxRetries && errorType !== "timeout") {
    msg.retryCount = retryCount + 1;
    msg.delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
    return [null, msg]; // Send to retry path
  }
  
  return [msg, null]; // Send to error handler
};
```

### **Progress Monitoring**

```javascript
// Progress tracking function
const trackProgress = (stdout, script) => {
  const progressIndicators = {
    "manual_pipeline_trigger": ["Starting", "Data Relationships", "Performance", "Horse Mapping", "Summary"],
    "data_relationships": ["Loading", "Processing", "Updating", "Completed"],
    "performance_tracker": ["Analyzing", "Calculating", "Storing", "Finished"]
  };
  
  const indicators = progressIndicators[script] || [];
  const currentStep = indicators.find(step => stdout.includes(step));
  const stepIndex = indicators.indexOf(currentStep);
  
  return {
    currentStep: currentStep || "Unknown",
    progressPercent: stepIndex >= 0 ? ((stepIndex + 1) / indicators.length) * 100 : 0
  };
};
```

---

## 📊 **C2 DASHBOARD INTEGRATION PLAN**

### **New Dashboard Elements**

#### **Pipeline Control Panel**

```html
<!-- Add to C2 dashboard -->
<div class="pipeline-control-panel">
  <h3>🚀 Pipeline Automation</h3>
  
  <div class="pipeline-buttons">
    <button onclick="triggerPipeline('manual-all')" class="btn-primary">
      🔄 Run Full Pipeline
    </button>
    
    <button onclick="triggerPipeline('data-relationships')" class="btn-secondary">
      📊 Data Relationships
    </button>
    
    <button onclick="triggerPipeline('performance-tracker')" class="btn-secondary">
      📈 Performance Tracker
    </button>
    
    <button onclick="triggerPipeline('ml-training')" class="btn-warning">
      🤖 ML Training
    </button>
    
    <button onclick="triggerPipeline('ai-selections')" class="btn-success">
      🎯 Generate Selections
    </button>
  </div>
  
  <div class="pipeline-status">
    <div id="pipeline-progress"></div>
    <div id="pipeline-logs"></div>
  </div>
</div>
```

#### **JavaScript Functions**

```javascript
// Add to C2 dashboard JavaScript
const triggerPipeline = async (action) => {
  try {
    showProgress(`Starting ${action}...`);
    
    const response = await fetch(`/api/pipeline/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        timestamp: new Date().toISOString(),
        source: 'c2_dashboard'
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      showSuccess(`${action} completed successfully`);
    } else {
      showError(`${action} failed: ${result.error}`);
    }
    
  } catch (error) {
    showError(`Network error: ${error.message}`);
  }
};

const showProgress = (message) => {
  document.getElementById('pipeline-progress').innerHTML = 
    `<div class="progress-indicator">⏳ ${message}</div>`;
};

const showSuccess = (message) => {
  document.getElementById('pipeline-progress').innerHTML = 
    `<div class="success-indicator">✅ ${message}</div>`;
};

const showError = (message) => {
  document.getElementById('pipeline-progress').innerHTML = 
    `<div class="error-indicator">❌ ${message}</div>`;
};
```

---

## 🛣️ **IMPLEMENTATION ROADMAP**

### **Phase 1: Foundation (1-2 hours)**
- [ ] Create basic exec node templates in Node-RED
- [ ] Test simple Python script execution
- [ ] Implement basic error handling
- [ ] Add logging and monitoring

### **Phase 2: Core Pipeline Integration (2-3 hours)**
- [ ] Implement Manual Pipeline Trigger exec node
- [ ] Add Data Relationships Pipeline exec node  
- [ ] Create Performance Tracker exec node
- [ ] Test end-to-end pipeline automation

### **Phase 3: Dashboard Integration (1-2 hours)**
- [ ] Add pipeline control buttons to C2 dashboard
- [ ] Implement API endpoints for pipeline triggers
- [ ] Add real-time progress monitoring
- [ ] Create pipeline status indicators

### **Phase 4: ML Integration (2-3 hours)**
- [ ] Add ML Training exec node
- [ ] Implement AI Selections Generator exec node
- [ ] Create scheduled automation triggers
- [ ] Add ML-specific monitoring and alerting

### **Phase 5: Advanced Features (1-2 hours)**
- [ ] Implement file watcher integration
- [ ] Add automated retry mechanisms
- [ ] Create pipeline orchestration workflows
- [ ] Add comprehensive logging and reporting

---

## ✅ **SUCCESS CRITERIA**

### **Immediate Goals**
- [ ] All Python scripts executable via Node-RED exec nodes
- [ ] C2 dashboard buttons trigger Node-RED workflows
- [ ] Real-time execution status and progress monitoring
- [ ] Robust error handling and retry mechanisms

### **Long-term Goals**  
- [ ] Fully automated pipeline orchestration
- [ ] Zero-downtime script execution
- [ ] Comprehensive audit trail and logging
- [ ] Performance optimization and monitoring

---

## 🎯 **NEXT IMMEDIATE ACTIONS**

1. **Create first exec node** for `manual_pipeline_trigger.py`
2. **Test script execution** and verify output handling
3. **Add error handling** and timeout management
4. **Create C2 dashboard button** to trigger the exec node
5. **Validate end-to-end workflow** from button click to script completion

This plan provides a systematic approach to converting the existing Python pipeline scripts into automated Node-RED workflows while maintaining all functionality and adding comprehensive monitoring.
