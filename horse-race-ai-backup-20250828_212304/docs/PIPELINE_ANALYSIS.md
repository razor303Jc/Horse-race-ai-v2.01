# Horse Racing AI Pipeline Architecture Analysis

## Power Ratings, Speed Ratings, Form Scoring & Monte Carlo Integration

### Current Pipeline Phases Overview

Based on analysis of the codebase, here's the complete pipeline architecture and what advanced racing metrics need to be integrated:

## 📊 **Current Pipeline Flow**

### **Phase 1: Data Acquisition**

- **Manual Downloads**: ZIP file processing from daily downloads
- **Automated Downloads**: File watcher for racing data
- **CSV Import**: Racing data, race cards, results import
- **Data Validation**: Quality checks and preprocessing

### **Phase 2: Data Processing**

- **Relationships Pipeline**: Horse-trainer-jockey connections
- **Data Quality Enhancement**: Missing value handling, format standardization
- **Feature Engineering**: Basic racing features (17 current features)

### **Phase 3: ML Pipeline**

- **Model Training**: 4 ensemble models (RF, GBC, LR, NN)
- **Prediction Generation**: AI selections with confidence scores
- **Performance Monitoring**: Model accuracy tracking

### **Phase 4: Advanced Analytics** (GAPS IDENTIFIED)

- ❌ **Power Ratings**: Not implemented
- ❌ **Speed Ratings**: Limited implementation
- ❌ **Form Scoring**: Basic form consistency only
- ❌ **Monte Carlo Simulations**: Standalone, not integrated

---

## 🗄️ **Current Database Schema Analysis**

### **Existing Tables with Racing Metrics**

#### **race_entries** (Main table - 360 current rows)

```sql
- entry_id, race_id, horse_id
- horse_name, age, weight_kg
- jockey, trainer
- odds, odds_decimal
- horse_rate (basic rating)
- timeform_comments
```

#### **horse_form_trends** (Form analysis)

```sql
- horse_id, horse_name
- form_trend, trend_confidence
- last_5_ratings (JSONB)
- best_rating, current_rating
```

#### **performance_metrics_cache** (Performance data)

```sql
- metric_key, metric_value
- start_date, end_date
- metadata (text)
```

### **Missing Tables for Advanced Metrics**

#### **🔥 NEEDED: horse_power_ratings**

```sql
- horse_id
- race_date
- power_rating (0-140 scale)
- class_adjusted_rating
- distance_adjusted_rating
- surface_adjusted_rating
- weight_adjusted_rating
- going_adjusted_rating
- calculated_at
- rating_confidence
```

#### **⚡ NEEDED: horse_speed_ratings**

```sql
- horse_id
- race_date
- speed_figure (0-120 scale)
- pace_rating
- sectional_times (JSONB)
- speed_map_position
- pace_classification (front/mid/closer)
- track_variant
- time_comparison
- calculated_at
```

#### **📈 NEEDED: horse_form_scores**

```sql
- horse_id
- race_date
- form_score (0-100)
- recent_form_trend
- class_progression
- distance_form
- surface_form
- trainer_form
- jockey_form
- consistency_rating
- improvement_indicator
- calculated_at
```

#### **🎲 NEEDED: monte_carlo_simulations**

```sql
- simulation_id
- race_id
- horse_id
- simulation_runs (default 10000)
- win_probability
- place_probability
- show_probability
- expected_position
- confidence_interval
- value_rating
- fair_odds
- z_score
- calculated_at
```

---

## 🔧 **Current Data Flow Analysis**

### **Existing Speed Analysis** (Limited)

```json
// From: data/speed_analysis/speed_analysis_*.json
{
  "speed_figure": 96.0,
  "pace_rating": 77.5,
  "sectional_times": [26.25, 19.5, 11.7...],
  "pace_classification": "closer",
  "speed_map_position": 1
}
```

**Status**: ✅ Data generated but ❌ NOT stored in database

### **Existing Monte Carlo Data** (Standalone)

```json
// From: data/monte_carlo_results/stage10_monte_carlo_*.json
{
  "win_probabilities": { "Horse_1": 0.3174 },
  "place_probabilities": { "Horse_1": 0.6042 },
  "betting_recommendations": [
    {
      "probability": 0.3174,
      "fair_odds": 3.15,
      "confidence": 0.5736,
      "z_score": 1.511
    }
  ]
}
```

**Status**: ✅ Data generated but ❌ NOT stored in database

### **Form Analysis** (Basic)

```sql
-- Current horse_form_trends table
form_trend: "improving/declining/stable"
last_5_ratings: [82, 85, 88, 91, 94]
current_rating: 94.0
```

**Status**: ⚠️ Basic implementation, needs enhancement

---

## 🎯 **Integration Roadmap**

### **Phase 5A: Enhanced Speed Ratings Integration**

1. **Database Schema**: Create `horse_speed_ratings` table
2. **Pipeline Integration**: Connect speed analysis JSON to database
3. **Historical Analysis**: Calculate speed ratings for past performances
4. **Real-time Updates**: Update speed ratings after each race

### **Phase 5B: Power Ratings System**

1. **Rating Algorithm**: Implement class-par based power ratings
2. **Adjustments Engine**: Surface, distance, weight, going adjustments
3. **Database Storage**: Power ratings with confidence metrics
4. **Historical Tracking**: Power rating progression over time

### **Phase 5C: Advanced Form Scoring**

1. **Multi-factor Scoring**: Class, distance, surface, trainer form
2. **Trend Analysis**: Improvement/decline indicators
3. **Consistency Metrics**: Performance reliability scoring
4. **Database Enhancement**: Expand form scoring capabilities

### **Phase 5D: Monte Carlo Database Integration**

1. **Results Storage**: Store simulation results in database
2. **Historical Tracking**: Track prediction accuracy over time
3. **Real-time Access**: API endpoints for simulation data
4. **Performance Analysis**: Compare simulated vs actual results

---

## 📋 **Implementation Priority**

### **HIGH PRIORITY** 🔥

1. **Speed Ratings Database Integration** - Data exists, needs storage
2. **Monte Carlo Database Integration** - Data exists, needs storage
3. **Power Ratings Algorithm** - Core rating system implementation

### **MEDIUM PRIORITY** ⚡

4. **Enhanced Form Scoring** - Expand current basic system
5. **Rating Adjustments Engine** - Surface/distance/weight factors
6. **Historical Analysis Pipeline** - Backfill historical ratings

### **LOW PRIORITY** 📊

7. **Advanced Sectional Analysis** - Detailed pace analysis
8. **Trainer/Jockey Form Integration** - Connections performance
9. **Weather/Going Impact Analysis** - Condition-based adjustments

---

## 🚀 **Next Steps**

### **Immediate Actions**

1. ✅ **Create database schemas** for missing tables
2. ✅ **Modify pipeline coordinator** to include advanced metrics phases
3. ✅ **Connect existing JSON data** to database storage
4. ✅ **Implement power ratings algorithm**

### **Pipeline Enhancement**

```python
# New pipeline phases to add:
# Phase 5: Speed Ratings Integration
# Phase 6: Power Ratings Calculation
# Phase 7: Enhanced Form Scoring
# Phase 8: Monte Carlo Database Storage
# Phase 9: Advanced Metrics API
```

This analysis shows we have excellent foundational data and significant advanced analytics already running. The key gap is **database integration** - we're generating sophisticated racing metrics but not storing them for historical analysis and real-time access.

**Estimated Implementation Time**: 2-3 days for database integration, 1 week for complete advanced metrics system.
