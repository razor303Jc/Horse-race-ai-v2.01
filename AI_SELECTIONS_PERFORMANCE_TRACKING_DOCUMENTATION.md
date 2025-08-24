# AI Selections Performance Tracking System

## 🎯 System Overview

Created a comprehensive performance tracking system to analyze AI selections against actual race results, stored in the `results_horse_racing_db` database for consistency with results data.

## 🏗️ Database Schema Created

### Table: `ai_selections_performance` (results_horse_racing_db)

#### Core Identification Fields

- `performance_id` (SERIAL PRIMARY KEY) - Unique record identifier
- `race_date` (DATE NOT NULL) - Race date
- `race_id` (INTEGER NOT NULL) - Links to races table
- `course` (VARCHAR NOT NULL) - Race venue
- `race_number` (INTEGER NOT NULL) - Race number at venue
- `horse_name` (VARCHAR NOT NULL) - Horse identifier

#### AI Prediction Data

- `ai_win_probability` (DECIMAL(5,4) NOT NULL) - AI predicted win probability
- `ai_confidence_score` (DECIMAL(5,4) NOT NULL) - AI confidence level
- `ai_selection_type` (VARCHAR(20) NOT NULL) - Type of prediction (win/place/each-way)
- `model_name` (VARCHAR(50) NOT NULL) - ML model used (LogisticRegression)
- `model_version` (VARCHAR(20) NOT NULL) - Model version (v1.0)

#### Actual Race Results

- `actual_position` (INTEGER NULL) - Finishing position
- `actual_starting_price` (DECIMAL(8,2) NULL) - Starting price/odds
- `actual_jockey` (VARCHAR(200) NULL) - Actual jockey
- `actual_trainer` (VARCHAR(200) NULL) - Actual trainer

#### Performance Metrics

- `prediction_correct` (BOOLEAN NULL) - Whether prediction was correct
- `win_prediction_correct` (BOOLEAN NULL) - Whether win prediction was correct
- `place_prediction_correct` (BOOLEAN NULL) - Whether placed (top 3)
- `roi_if_backed` (DECIMAL(8,2) NULL) - Return on investment if £1 staked
- `probability_accuracy_score` (DECIMAL(8,4) NULL) - Brier score for probability accuracy

#### Ranking Analysis

- `ai_probability_rank` (INTEGER NULL) - AI probability rank within race
- `actual_finish_rank` (INTEGER NULL) - Actual finishing position
- `rank_difference` (INTEGER NULL) - Difference between predicted and actual rank

#### Metadata

- `analysis_date` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - When analysis was performed
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Record creation time

### Indexes Created

1. **Primary Key**: `performance_id`
2. **Unique Constraint**: `(race_date, race_id, horse_name, model_name)`
3. **Performance Indexes**:
   - `idx_ai_perf_race_date` - Fast date-based queries
   - `idx_ai_perf_course_date` - Course and date combinations
   - `idx_ai_perf_model` - Model-specific analysis

## 🔧 Performance Tracking Tool Created

### File: `tools/ml_training/ai_selections_performance_tracker.py`

#### Key Features

1. **Data Integration**: Combines AI selections from `cards_horse_racing_db` with results from `results_horse_racing_db`
2. **Performance Metrics**: Calculates comprehensive performance statistics
3. **ROI Analysis**: Tracks financial performance of AI selections
4. **Probability Accuracy**: Uses Brier Score to measure prediction quality
5. **Ranking Analysis**: Compares predicted vs actual finishing positions

#### Usage

```bash
# Analyze AI selections performance for specific date
docker exec horse_racing_data_pipeline_clean python /app/tools/ml_training/ai_selections_performance_tracker.py --date 2025-08-22
```

## 📊 Current Status (August 22, 2025)

### ✅ Completed

- **AI Selections**: 418 predictions generated and stored in `cards_horse_racing_db`
- **Performance Table**: Created in `results_horse_racing_db` with full schema
- **Analysis Tool**: Ready to process results when available
- **Database Integration**: Seamless connection between prediction and results databases

### ⏳ Pending

- **Race Results**: Results for August 22nd not yet uploaded to `results_horse_racing_db`
- **Performance Analysis**: Will be available once results are uploaded

### 🔍 Data Status

- **AI Selections Available**: ✅ 418 selections across 47 races, 7 courses
- **Race Metadata Available**: ✅ 47 races scheduled for August 22nd
- **Race Results Available**: ❌ Results not yet in `results_horse_racing_db.records`

## 📈 Expected Performance Metrics

Once results are uploaded, the system will calculate:

### Win Prediction Analysis

- **Win Rate**: Percentage of winners correctly predicted
- **Strike Rate**: Winners predicted vs total selections
- **ROI**: Return on investment for all selections
- **Average ROI per Bet**: Expected value per selection

### Probability Accuracy

- **Brier Score**: Measures probability calibration (lower = better)
- **Probability vs Outcome**: How well probabilities match actual results
- **Confidence Intervals**: Reliability of probability estimates

### Ranking Performance

- **Rank Correlation**: How well AI rankings match actual finishing order
- **Top Selection Accuracy**: Performance of highest-rated selections
- **Rank Difference Analysis**: Systematic biases in ranking predictions

## 🔄 Next Steps

### When Results Are Available

1. **Upload Results**: Ensure August 22nd results are in `results_horse_racing_db.records`
2. **Run Analysis**: Execute performance tracker for complete metrics
3. **Generate Report**: Create detailed performance summary
4. **Model Improvement**: Use performance data to enhance future predictions

### Command to Run Analysis

```bash
# Once results are uploaded
docker exec horse_racing_data_pipeline_clean python /app/tools/ml_training/ai_selections_performance_tracker.py --date 2025-08-22
```

## 🎯 Business Value

### Performance Tracking Benefits

1. **Model Validation**: Objective measurement of AI prediction quality
2. **ROI Analysis**: Financial performance assessment
3. **Continuous Improvement**: Data-driven model enhancement
4. **Confidence Calibration**: Understanding prediction reliability

### Operational Advantages

1. **Automated Analysis**: Daily performance tracking without manual intervention
2. **Historical Tracking**: Build performance database over time
3. **Model Comparison**: Compare different model versions and approaches
4. **Risk Management**: Identify low-confidence predictions

## 📋 Database Architecture Summary

```
results_horse_racing_db:
├── races (race metadata)
├── records (race results)
├── ai_selections_performance (NEW - performance tracking)
├── horses, jockeys_stats, trainers_stats (supporting data)

cards_horse_racing_db:
├── ai_selections (AI predictions)
├── races, racecard_details (race card data)
```

**Design Principle**: Clean separation of concerns

- **Cards DB**: Prediction and race card data
- **Results DB**: Actual results and performance analysis

This architecture maintains consistency and enables comprehensive analysis while keeping related data together.

---

**Status**: ✅ Performance tracking system ready
**Next Action**: Upload August 22nd results to enable complete analysis
**Expected Outcome**: Comprehensive AI selection performance metrics and ROI analysis
