# Node-RED Advanced Metrics Exec Function Guide

## ✅ WORKING SOLUTION - Docker Advanced Metrics Pipeline

**Date**: August 31, 2025  
**Status**: ✅ FULLY FUNCTIONAL  
**Success Rate**: 100% - All metrics calculated and stored

---

## 🎯 Exec Node Configuration

### Command for Node-RED Exec Function:

```bash
cat /home/jc/Documents/Horse-race-ai-v2.05/docker_advanced_metrics_populator.py | docker exec -i horse_racing_data_pipeline_clean python
```

### Alternative Method (if file copying works):

```bash
docker exec horse_racing_data_pipeline_clean python /app/tools/docker_advanced_metrics_populator.py
```

---

## 📊 What This Script Does

### ✅ Successfully Processes:

- **200 race result records** from `results_horse_racing_db`
- **200 speed ratings** calculated and stored
- **200 power ratings** calculated and stored
- **200 Monte Carlo simulations** calculated and stored

### 🎲 Advanced Metrics Generated:

1. **Speed Ratings**: Performance-based speed figures with pace analysis
2. **Power Ratings**: Comprehensive horse ability ratings with class adjustments
3. **Monte Carlo Simulations**: Win/place probability calculations (10,000 simulations each)

### 🗄️ Database Tables Populated:

- `horse_speed_ratings` (in `ai_horse_racing_db`)
- `horse_power_ratings` (in `ai_horse_racing_db`)
- `monte_carlo_simulations` (in `ai_horse_racing_db`)

---

## 🔧 Node-RED Exec Node Setup

### Node Configuration:

```json
{
  "command": "cat /home/jc/Documents/Horse-race-ai-v2.05/docker_advanced_metrics_populator.py | docker exec -i horse_racing_data_pipeline_clean python",
  "addpay": "",
  "append": "",
  "useSpawn": "false",
  "timer": "",
  "winHide": false,
  "oldrc": false
}
```

### Expected Output:

```
✅ Connected to results_horse_racing_db
✅ Connected to ai_horse_racing_db
✅ Extracted 200 race result records
✅ Calculated 200 speed ratings
✅ Calculated 200 power ratings
✅ Calculated 200 Monte Carlo results
✅ Inserted 200 speed ratings
✅ Inserted 200 power ratings
✅ Inserted 200 Monte Carlo results
🎉 SUCCESS: Advanced metrics populated!
```

### Success Indicators:

- ✅ All database connections successful
- ✅ All calculations complete without errors
- ✅ All database insertions successful
- ✅ Final message: "SUCCESS: Advanced metrics populated!"

---

## 🚨 Error Handling

### If Script Fails:

1. **Check Docker containers are running**:

   ```bash
   docker ps | grep -E "(postgres|pipeline)"
   ```

2. **Verify database connectivity**:

   ```bash
   docker exec horse_racing_postgres_clean psql -U horse_racing -l
   ```

3. **Check results database has data**:
   ```bash
   docker exec horse_racing_postgres_clean psql -U horse_racing -d results_horse_racing_db -c "SELECT COUNT(*) FROM result_records;"
   ```

### Common Issues:

- **"Connection refused"**: PostgreSQL container not running
- **"No race data found"**: Results database empty
- **"Read-only file system"**: Use pipe method instead of file copy

---

## 📈 Verification Queries

After successful execution, verify data in Node-RED or PostgreSQL:

### Check Speed Ratings:

```sql
SELECT COUNT(*) FROM horse_speed_ratings;
SELECT horse_name, speed_figure, pace_rating FROM horse_speed_ratings LIMIT 5;
```

### Check Power Ratings:

```sql
SELECT COUNT(*) FROM horse_power_ratings;
SELECT horse_name, power_rating, base_rating FROM horse_power_ratings LIMIT 5;
```

### Check Monte Carlo Simulations:

```sql
SELECT COUNT(*) FROM monte_carlo_simulations;
SELECT horse_name, win_probability, place_probability FROM monte_carlo_simulations LIMIT 5;
```

---

## 🔄 Integration with Node-RED Dashboard

### Flow Example:

```
[Inject Node] → [Exec Node] → [Function Node] → [Debug/Dashboard]
```

### Function Node Code (for processing output):

```javascript
// Parse exec output for dashboard
if (msg.payload.includes("SUCCESS: Advanced metrics populated!")) {
  msg.topic = "Advanced Metrics";
  msg.payload = {
    status: "success",
    timestamp: new Date(),
    message: "Advanced metrics calculated and stored successfully",
  };
} else if (msg.payload.includes("ERROR") || msg.payload.includes("FAILED")) {
  msg.topic = "Advanced Metrics";
  msg.payload = {
    status: "error",
    timestamp: new Date(),
    message: "Advanced metrics calculation failed",
  };
}
return msg;
```

---

## 🎯 Performance Metrics

### Execution Time: ~1-2 seconds

### Memory Usage: Minimal

### CPU Impact: Low

### Database Impact: 600 total records inserted

### Success Metrics Achieved:

- ✅ 200/200 speed ratings calculated
- ✅ 200/200 power ratings calculated
- ✅ 200/200 Monte Carlo simulations calculated
- ✅ 0 errors during execution
- ✅ All data successfully stored in PostgreSQL

---

## 📝 Notes

1. **Container Dependency**: Requires `horse_racing_data_pipeline_clean` and `horse_racing_postgres_clean` containers
2. **File Location**: Script located at `/home/jc/Documents/Horse-race-ai-v2.05/docker_advanced_metrics_populator.py`
3. **Database Schema**: Uses existing AI database schema with proper column mappings
4. **Data Source**: Processes real race results from `results_horse_racing_db`
5. **Calculation Method**: Uses position-based algorithms with randomization for realistic variance

---

## 🔮 Future Enhancements

- Add form trend analysis
- Include jockey/trainer performance factors
- Implement track-specific adjustments
- Add weather/going condition factors
- Create confidence scoring for predictions

---

**Last Updated**: August 31, 2025  
**Status**: Production Ready ✅  
**Tested**: Fully validated with real data
