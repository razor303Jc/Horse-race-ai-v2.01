# 🎯 Pipeline Trigger Analysis & Planning

## 📊 Current Pipeline Architecture

### 17-Stage Dynamic Pipeline System

- **6 Phases**: Data Acquisition → Feature Engineering → Advanced Analytics → Simulation → Strategy → Pre-Race
- **17 Stages**: From data download to pre-race updates
- **Dynamic Timing**: Adaptive scheduling based on first race time
- **Intelligent Compression**: Quality-preserving time management

---

## 🔄 Current Trigger Mechanisms

### 1. **Schedule-Based Triggers** (Current Implementation)

```python
# In daily_orchestrator.py - schedule_daily_pipeline()
schedule.every().day.at("06:26").do(self.run_daily_pipeline)
```

**Current Flow:**

1. Fixed time trigger at 06:26 (after auto-downloader at 06:25)
2. Generate dynamic schedule based on first race time
3. Execute stages sequentially based on calculated timings

### 2. **Stage Mapping System** (Current Implementation)

```python
stage_mapping = {
    "data_download": "verify_download_completion",
    "data_validation": "validate_downloaded_data",
    "data_preprocessing": "process_data_relationships",
    "feature_engineering": "generate_contextual_analysis",
    "ml_model_training": "train_ml_models",
    # ... etc
}
```

---

## 🚀 **Proposed Event-Driven Trigger System**

### **Phase 1: DATA ACQUISITION**

```
Trigger Chain: File Detection → Validation → Processing → Relationship Mapping
```

#### **Stage 1: data_download** (Fixed: 00:01)

- **Current Trigger**: Fixed schedule via auto-downloader
- **Proposed Enhancement**: File monitoring system

```python
# File watcher implementation
class DataDownloadTrigger:
    def __init__(self):
        self.watch_directories = [
            "/data/daily_downloads/cards_data/",
            "/data/daily_downloads/results_data/"
        ]

    def on_file_complete(self, file_path):
        # Trigger: data_validation stage
        self.pipeline.trigger_stage("data_validation")
```

#### **Stage 2: data_validation**

- **Current Trigger**: Sequential after data_download
- **Proposed Trigger**: File completion event + integrity check

```python
class DataValidationTrigger:
    def trigger_conditions(self):
        return {
            "files_present": self.check_required_files(),
            "file_sizes_valid": self.validate_file_sizes(),
            "csv_headers_valid": self.validate_csv_structure()
        }

    def on_validation_complete(self, validation_results):
        if validation_results["success_rate"] >= 0.95:
            self.pipeline.trigger_stage("data_preprocessing")
        else:
            self.pipeline.handle_validation_failure(validation_results)
```

#### **Stage 3: data_preprocessing**

- **Current Trigger**: Sequential after validation
- **Proposed Trigger**: Validation success + data quality metrics

```python
class DataPreprocessingTrigger:
    def trigger_conditions(self):
        return {
            "validation_passed": True,
            "record_count": self.count_valid_records(),
            "quality_score": self.calculate_data_quality()
        }
```

#### **Stage 4: data_relationships**

- **Current Trigger**: Sequential after preprocessing
- **Proposed Trigger**: Preprocessing completion + relationship readiness

```python
class RelationshipTrigger:
    def trigger_conditions(self):
        return {
            "horses_processed": self.count_processed_horses(),
            "jockeys_processed": self.count_processed_jockeys(),
            "trainers_processed": self.count_processed_trainers(),
            "linkage_readiness": self.assess_linkage_potential()
        }
```

---

### **Phase 2: FEATURE ENGINEERING**

#### **Stage 5: feature_engineering**

- **Current Trigger**: Sequential after data_relationships
- **Proposed Trigger**: Relationship completion + feature readiness signal

```python
class FeatureEngineeringTrigger:
    def trigger_conditions(self):
        return {
            "relationships_complete": True,
            "historical_data_available": self.check_historical_availability(),
            "feature_targets_identified": self.identify_feature_targets()
        }

    def on_features_ready(self, feature_stats):
        # Parallel trigger for multiple ML processes
        self.pipeline.trigger_parallel([
            "ml_model_training",
            "contextual_analysis"
        ])
```

#### **Stage 6: ml_model_training** (Early Morning: 00:30-04:00)

- **Current Trigger**: Sequential timing
- **Proposed Trigger**: Feature readiness + resource availability + time window

```python
class MLTrainingTrigger:
    def __init__(self):
        self.optimal_window = "00:30-04:00"  # Early morning training
        self.resource_threshold = 0.8  # 80% CPU/Memory available

    def trigger_conditions(self):
        return {
            "features_ready": True,
            "time_window_available": self.check_time_window(),
            "resources_available": self.check_system_resources(),
            "training_data_sufficient": self.validate_training_data_size()
        }

    def on_training_complete(self, model_metrics):
        # Trigger downstream analytics that depend on fresh models
        self.pipeline.trigger_stage("contextual_analysis")
```

---

### **Phase 3: ADVANCED ANALYTICS**

#### **Stage 7: contextual_analysis**

- **Current Trigger**: After ML training
- **Proposed Trigger**: ML models updated OR feature engineering complete

```python
class ContextualAnalysisTrigger:
    def trigger_conditions(self):
        return {
            "models_updated": self.check_model_freshness(),
            "features_available": True,
            "context_data_ready": self.validate_context_sources()
        }
```

#### **Stage 8: form_scoring**

- **Current Trigger**: Sequential after contextual analysis
- **Proposed Trigger**: Context analysis complete + form data availability

```python
class FormScoringTrigger:
    def trigger_conditions(self):
        return {
            "context_complete": True,
            "historical_form_available": self.check_form_data(),
            "rating_algorithms_ready": self.validate_scoring_models()
        }
```

#### **Stage 9: power_ratings**

- **Current Trigger**: Sequential after form scoring
- **Proposed Trigger**: Form scores computed + speed data ready

```python
class PowerRatingsTrigger:
    def trigger_conditions(self):
        return {
            "form_scores_ready": True,
            "speed_data_available": self.validate_speed_data(),
            "track_conditions_known": self.check_track_conditions()
        }
```

#### **Stage 10: speed_analysis**

- **Current Trigger**: Sequential after power ratings
- **Proposed Trigger**: Power ratings complete + pace data ready

```python
class SpeedAnalysisTrigger:
    def trigger_conditions(self):
        return {
            "power_ratings_complete": True,
            "pace_data_available": self.validate_pace_data(),
            "sectional_times_ready": self.check_sectional_data()
        }
```

---

### **Phase 4: SIMULATION**

#### **Stage 11: monte_carlo_simulations**

- **Current Trigger**: Sequential after speed analysis
- **Proposed Trigger**: All analytics complete + computational resources available

```python
class MonteCarloTrigger:
    def __init__(self):
        self.min_simulations = 5000  # Per race
        self.resource_requirement = 0.9  # High CPU requirement

    def trigger_conditions(self):
        return {
            "analytics_complete": self.check_all_analytics_ready(),
            "computational_resources": self.check_cpu_availability(),
            "race_data_finalized": self.validate_race_completeness(),
            "simulation_parameters_set": self.validate_simulation_config()
        }

    def on_simulations_complete(self, simulation_results):
        # Parallel trigger for trend analysis and composite scoring
        self.pipeline.trigger_parallel([
            "race_trends",
            "composite_scoring"
        ])
```

#### **Stage 12: race_trends**

- **Current Trigger**: Sequential after Monte Carlo
- **Proposed Trigger**: Simulation data available + trend analysis ready

```python
class TrendAnalysisTrigger:
    def trigger_conditions(self):
        return {
            "simulation_data_ready": True,
            "historical_trends_available": self.check_trend_data(),
            "pattern_recognition_ready": self.validate_trend_algorithms()
        }
```

#### **Stage 13: composite_scoring**

- **Current Trigger**: Sequential after race trends
- **Proposed Trigger**: All scoring components available

```python
class CompositeScoringTrigger:
    def trigger_conditions(self):
        return {
            "form_scores_ready": True,
            "power_ratings_ready": True,
            "speed_ratings_ready": True,
            "simulation_results_ready": True,
            "trend_analysis_ready": True,
            "confidence_models_ready": self.validate_confidence_algorithms()
        }
```

---

### **Phase 5: STRATEGY**

#### **Stage 14: betting_strategies**

- **Current Trigger**: Sequential after composite scoring
- **Proposed Trigger**: Composite scores ready + market data available

```python
class BettingStrategyTrigger:
    def trigger_conditions(self):
        return {
            "composite_scores_ready": True,
            "market_odds_available": self.check_odds_availability(),
            "value_opportunities_identified": self.scan_value_bets(),
            "risk_parameters_set": self.validate_risk_settings()
        }
```

#### **Stage 15: ai_selections**

- **Current Trigger**: Sequential after betting strategies
- **Proposed Trigger**: Strategies complete + selection criteria met

```python
class AISelectionTrigger:
    def trigger_conditions(self):
        return {
            "strategies_ready": True,
            "confidence_thresholds_met": self.check_confidence_levels(),
            "selection_criteria_satisfied": self.validate_selection_rules(),
            "final_validation_passed": self.run_final_validation()
        }
```

#### **Stage 16: report_generation**

- **Current Trigger**: Sequential after AI selections
- **Proposed Trigger**: All analysis complete + reporting requirements met

```python
class ReportGenerationTrigger:
    def trigger_conditions(self):
        return {
            "all_analysis_complete": self.check_pipeline_completion(),
            "data_quality_sufficient": self.validate_report_data_quality(),
            "template_requirements_met": self.check_report_templates()
        }
```

---

### **Phase 6: PRE-RACE OPERATIONS**

#### **Stage 17: pre_race_updates**

- **Current Trigger**: Sequential after reports
- **Proposed Trigger**: Time-based + live data updates

```python
class PreRaceUpdatesTrigger:
    def __init__(self):
        self.update_frequency = 300  # Every 5 minutes
        self.cutoff_time = 15  # Minutes before race

    def trigger_conditions(self):
        return {
            "time_until_race": self.calculate_time_to_race(),
            "live_odds_changed": self.detect_odds_movements(),
            "scratching_updates": self.check_runner_changes(),
            "track_condition_changes": self.monitor_track_updates()
        }

    def continuous_monitoring(self):
        # Continuous trigger until race start
        while self.time_until_race() > self.cutoff_time:
            if self.should_update():
                self.pipeline.trigger_stage("pre_race_updates")
            time.sleep(self.update_frequency)
```

---

## 🎯 **Enhanced Trigger Orchestration System**

### **Event-Driven Pipeline Manager**

```python
class EventDrivenPipelineOrchestrator:
    def __init__(self):
        self.event_bus = EventBus()
        self.stage_dependencies = self._build_dependency_graph()
        self.active_triggers = {}
        self.stage_states = {}

    def register_stage_triggers(self):
        """Register all stage-specific triggers"""
        triggers = {
            "data_download": DataDownloadTrigger(),
            "data_validation": DataValidationTrigger(),
            "data_preprocessing": DataPreprocessingTrigger(),
            # ... all stages
        }

        for stage, trigger in triggers.items():
            self.event_bus.register(stage, trigger)

    def trigger_stage(self, stage_name, trigger_data=None):
        """Event-driven stage triggering"""
        if self.can_trigger_stage(stage_name):
            self.execute_stage(stage_name, trigger_data)
            self.update_downstream_triggers(stage_name)

    def trigger_parallel(self, stage_names):
        """Trigger multiple stages in parallel"""
        for stage in stage_names:
            if self.can_trigger_stage(stage):
                threading.Thread(
                    target=self.execute_stage,
                    args=(stage,)
                ).start()
```

### **Conditional Trigger System**

```python
class ConditionalTriggerManager:
    def __init__(self):
        self.conditions = {}
        self.thresholds = {}

    def add_condition(self, stage, condition_name, check_function, threshold=None):
        """Add conditional trigger"""
        if stage not in self.conditions:
            self.conditions[stage] = {}

        self.conditions[stage][condition_name] = {
            "check": check_function,
            "threshold": threshold,
            "last_checked": None,
            "last_result": None
        }

    def evaluate_triggers(self, stage):
        """Evaluate all conditions for a stage"""
        if stage not in self.conditions:
            return True  # No conditions = always trigger

        results = {}
        for condition_name, condition in self.conditions[stage].items():
            result = condition["check"]()
            results[condition_name] = result

            if condition["threshold"] and result < condition["threshold"]:
                return False

        return all(results.values())
```

### **Resource-Aware Triggering**

```python
class ResourceAwareTrigger:
    def __init__(self):
        self.cpu_threshold = 0.8
        self.memory_threshold = 0.8
        self.io_threshold = 0.7

    def check_resource_availability(self, stage_requirements):
        """Check if system resources are available for stage"""
        current_usage = self.get_system_metrics()

        return {
            "cpu_available": current_usage["cpu"] < self.cpu_threshold,
            "memory_available": current_usage["memory"] < self.memory_threshold,
            "io_available": current_usage["io"] < self.io_threshold,
            "can_proceed": all([
                current_usage["cpu"] < self.cpu_threshold,
                current_usage["memory"] < self.memory_threshold,
                current_usage["io"] < self.io_threshold
            ])
        }
```

---

## 🔧 **Implementation Strategy**

### **Phase 1: Basic Event System** (Immediate)

1. **File Watcher Implementation**
   - Monitor download completion
   - Trigger validation on file arrival
   - Basic event bus setup

### **Phase 2: Stage Completion Events** (Short-term)

1. **Completion Signals**
   - Each stage emits completion event
   - Downstream stages listen for dependencies
   - Success/failure propagation

### **Phase 3: Advanced Triggers** (Medium-term)

1. **Conditional Triggering**
   - Quality thresholds
   - Resource availability
   - Time window constraints

### **Phase 4: Intelligent Orchestration** (Long-term)

1. **Adaptive Scheduling**
   - Dynamic priority adjustment
   - Parallel execution optimization
   - Predictive resource allocation

---

## 📊 **Monitoring & Observability**

### **Trigger Event Logging**

```python
class TriggerEventLogger:
    def log_trigger_event(self, stage, trigger_type, conditions, result):
        """Log all trigger events for analysis"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "trigger_type": trigger_type,
            "conditions": conditions,
            "result": result,
            "execution_time": None  # Set when stage completes
        }

        self.event_log.append(event)
        self.write_to_monitoring_system(event)
```

### **Performance Metrics**

- **Trigger Latency**: Time from condition met to stage start
- **Stage Execution Time**: Actual vs allocated time
- **Dependency Resolution**: Time to resolve all dependencies
- **Resource Utilization**: CPU/Memory during each stage
- **Success Rate**: Percentage of successful triggers

---

## 🎯 **Next Steps**

1. **Implement File Watchers** for data download detection
2. **Create Event Bus System** for inter-stage communication
3. **Add Completion Signals** to existing stage methods
4. **Build Conditional Triggers** for quality thresholds
5. **Add Resource Monitoring** for intelligent scheduling
6. **Create Monitoring Dashboard** for trigger observability

This event-driven system will transform the current time-based scheduling into a responsive, intelligent pipeline that reacts to actual conditions and optimizes performance dynamically.
