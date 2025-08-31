# 🔄 Advanced ML Analytics Node-RED Integration Plan

**Date:** August 31, 2025  
**Purpose:** Node-RED flows and subflows for ML Analytics Framework  
**Integration:** cards_horse_racing_db → results_horse_racing_db → advanced_horse_racing_db

---

## 🏗️ **Node-RED Architecture Overview**

### **Main Flow Structure**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Ingestion │ -> │  ML Processing  │ -> │  Analytics DB   │
│     (Cards)     │    │   (Compute)     │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
    ┌────v────┐           ┌──────v──────┐         ┌──────v──────┐
    │Scheduler│           │  Subflows   │         │   API       │
    │Triggers │           │ (6 Types)   │         │ Endpoints   │
    └─────────┘           └─────────────┘         └─────────────┘
```

---

## 🎯 **Core Flows Design**

### **Flow 1: ML Analytics Master Controller**

- **Tab:** `ml-analytics-main`
- **Purpose:** Orchestrate all ML analytics processes
- **Trigger:** Schedule-based (daily 6 AM, post-race results)
- **Components:**
  - Data readiness checker
  - Sequential subflow coordinator
  - Error handling and monitoring
  - Progress tracking dashboard

### **Flow 2: Data Pipeline Integration**

- **Tab:** `ml-data-pipeline`
- **Purpose:** Connect three databases for ML processing
- **Data Flow:**
  ```
  cards_horse_racing_db -> Extract race cards
  results_horse_racing_db -> Extract historical results
  advanced_horse_racing_db -> Store computed analytics
  ```

---

## 🧩 **Subflow Definitions (6 Analytics Components)**

### **Subflow 1: Form Score Calculator** 🏃‍♂️

```json
{
  "name": "form-score-calculator",
  "category": "ML Analytics",
  "inputs": ["horse_id", "race_history", "performance_data"],
  "outputs": ["form_score", "confidence_level", "computation_metadata"],
  "database_operations": [
    "SELECT horse performance history",
    "INSERT INTO form_scores table",
    "UPDATE analytics metrics"
  ],
  "processing_time": "30-60 seconds per horse"
}
```

**Implementation:**

- **Input:** Horse ID + race history from results_db
- **Computation:** Weighted performance analysis algorithm
- **Output:** Form score (0-100) with confidence rating
- **Storage:** `advanced_horse_racing_db.form_scores`

### **Subflow 2: Power Ratings Engine** ⚡

```json
{
  "name": "power-ratings-engine",
  "category": "ML Analytics",
  "inputs": ["horse_data", "race_conditions", "track_info"],
  "outputs": ["power_rating", "rating_breakdown", "adjustment_factors"],
  "database_operations": [
    "SELECT track and condition data",
    "INSERT INTO power_ratings table",
    "UPDATE rating history"
  ],
  "processing_time": "45-90 seconds per horse"
}
```

**Implementation:**

- **Input:** Multi-factor data (track, conditions, jockey, trainer)
- **Computation:** 8-component comprehensive assessment
- **Output:** Power rating with breakdown by factor
- **Storage:** `advanced_horse_racing_db.power_ratings`

### **Subflow 3: Speed Ratings Analyzer** 🏎️

```json
{
  "name": "speed-ratings-analyzer",
  "category": "ML Analytics",
  "inputs": ["race_times", "track_data", "pace_data"],
  "outputs": ["speed_rating", "pace_adjustment", "track_variant"],
  "database_operations": [
    "SELECT timing and track data",
    "INSERT INTO speed_ratings table",
    "UPDATE track variants"
  ],
  "processing_time": "20-40 seconds per race"
}
```

**Implementation:**

- **Input:** Race timing data and track conditions
- **Computation:** Track-specific and pace-adjusted speed analysis
- **Output:** Normalized speed rating with adjustments
- **Storage:** `advanced_horse_racing_db.speed_ratings`

### **Subflow 4: Pace Analysis Framework** ⏱️

```json
{
  "name": "pace-analysis-framework",
  "category": "ML Analytics",
  "inputs": ["sectional_times", "race_shape", "running_style"],
  "outputs": ["pace_profile", "early_late_pace", "tactical_analysis"],
  "database_operations": [
    "SELECT sectional timing data",
    "INSERT INTO pace_analysis table",
    "UPDATE pace patterns"
  ],
  "processing_time": "15-30 seconds per race"
}
```

**Implementation:**

- **Input:** Sectional timing and race shape data
- **Computation:** Early/late pace calculations and tactical analysis
- **Output:** Pace profile with handicapping insights
- **Storage:** `advanced_horse_racing_db.pace_analysis`

### **Subflow 5: Z-Scores Statistical Engine** 📊

```json
{
  "name": "z-scores-statistical-engine",
  "category": "ML Analytics",
  "inputs": ["performance_metrics", "population_data", "normalization_params"],
  "outputs": ["z_scores", "statistical_significance", "deviation_analysis"],
  "database_operations": [
    "SELECT population statistics",
    "INSERT INTO z_scores table",
    "UPDATE statistical baselines"
  ],
  "processing_time": "10-25 seconds per metric"
}
```

**Implementation:**

- **Input:** Multi-metric performance data for normalization
- **Computation:** Statistical z-score calculations across metrics
- **Output:** Normalized scores with significance testing
- **Storage:** `advanced_horse_racing_db.z_scores`

### **Subflow 6: Monte Carlo Simulator** 🎲

```json
{
  "name": "monte-carlo-simulator",
  "category": "ML Analytics",
  "inputs": ["race_field", "probability_data", "simulation_params"],
  "outputs": [
    "outcome_probabilities",
    "confidence_intervals",
    "simulation_results"
  ],
  "database_operations": [
    "SELECT race and probability data",
    "INSERT INTO monte_carlo_simulations table",
    "UPDATE probability models"
  ],
  "processing_time": "2-5 minutes per race (1000+ simulations)"
}
```

**Implementation:**

- **Input:** Complete race field with computed analytics
- **Computation:** Probabilistic race outcome modeling (1000+ iterations)
- **Output:** Win/place probabilities with confidence intervals
- **Storage:** `advanced_horse_racing_db.monte_carlo_simulations`

---

## 🔄 **Flow Integration Architecture**

### **Master Flow Sequence:**

```javascript
// Pseudo-code for master controller
1. Check data readiness (cards + results available)
2. Initialize progress tracking
3. FOR each race in today's card:
   a. Trigger Form Score Calculator subflow
   b. Trigger Power Ratings Engine subflow
   c. Trigger Speed Ratings Analyzer subflow
   d. Trigger Pace Analysis Framework subflow
   e. Trigger Z-Scores Statistical Engine subflow
   f. Trigger Monte Carlo Simulator subflow
4. Aggregate results and update analytics dashboard
5. Generate API endpoints for computed data
6. Send completion notifications
```

### **Error Handling Flow:**

```javascript
// Error management and recovery
- Subflow timeout detection (5 minutes max)
- Database connection failure recovery
- Partial computation resumption
- Notification system for failures
- Automatic retry logic (max 3 attempts)
```

---

## 📡 **API Integration Endpoints**

### **Generated Endpoints** (Auto-created by flows):

```
GET /ml-analytics/form-scores/:horse_id
GET /ml-analytics/power-ratings/:horse_id
GET /ml-analytics/speed-ratings/:race_id
GET /ml-analytics/pace-analysis/:race_id
GET /ml-analytics/z-scores/:metric/:horse_id
GET /ml-analytics/monte-carlo/:race_id
GET /ml-analytics/complete-analysis/:race_id
```

### **Control Endpoints:**

```
POST /ml-analytics/trigger/:component  # Manual trigger
GET /ml-analytics/status                # Processing status
POST /ml-analytics/stop                 # Emergency stop
GET /ml-analytics/dashboard             # Progress dashboard
```

---

## ⏰ **Scheduling & Triggers**

### **Automated Triggers:**

1. **Daily Processing:** 6:00 AM (after overnight data ingestion)
2. **Post-Race Processing:** 15 minutes after each race result
3. **Weekly Batch:** Sunday 2:00 AM (historical recomputation)
4. **Manual Triggers:** Via API endpoints or dashboard

### **Processing Dependencies:**

```
Cards Data Available -> Form Scores + Power Ratings
Results Data Available -> Speed Ratings + Pace Analysis
All Components Complete -> Z-Scores + Monte Carlo
Final Analytics -> API Endpoint Updates
```

---

## 🎛️ **Dashboard Integration**

### **Real-time Monitoring Panel:**

- **Progress Bars:** Each subflow completion status
- **Performance Metrics:** Processing times, success rates
- **Error Tracking:** Failed computations, retry status
- **Data Volume:** Records processed, analytics generated
- **API Status:** Endpoint availability, response times

### **Control Interface:**

- **Manual Triggers:** Start individual or all analytics
- **Emergency Stop:** Halt all processing immediately
- **Configuration:** Adjust parameters and thresholds
- **History:** View past processing runs and performance

---

## 🔧 **Implementation Files Required**

### **Main Flows:**

```
flows/ml_analytics_master_flow.json
flows/ml_data_pipeline_integration.json
flows/ml_dashboard_interface.json
```

### **Subflows:**

```
subflows/form_score_calculator.json
subflows/power_ratings_engine.json
subflows/speed_ratings_analyzer.json
subflows/pace_analysis_framework.json
subflows/z_scores_statistical_engine.json
subflows/monte_carlo_simulator.json
```

### **Configuration:**

```
config/ml_analytics_config.json
config/database_connections.json
config/processing_parameters.json
```

---

## 🎯 **Success Criteria**

### **Performance Targets:**

- **Processing Time:** Complete analytics for 8-race card in under 15 minutes
- **Reliability:** 99.5% successful completion rate
- **API Response:** Sub-200ms for computed analytics retrieval
- **Resource Usage:** <2GB RAM, <50% CPU during processing

### **Data Quality:**

- **Coverage:** 100% of race cards processed within 30 minutes
- **Accuracy:** All analytics cross-validated with historical data
- **Consistency:** Identical results for identical inputs
- **Traceability:** Full audit trail for all computations

This comprehensive Node-RED integration will transform the Horse Racing AI system into a fully automated, production-grade ML analytics platform with real-time processing capabilities and robust monitoring infrastructure.

---

**Next Step:** Create the actual Node-RED flow JSON files and subflow definitions for implementation.
