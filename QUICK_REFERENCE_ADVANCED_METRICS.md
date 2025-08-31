# Node-RED Advanced Metrics - Quick Reference

## 🚀 READY TO USE - Copy & Paste Commands

### Primary Exec Command:

```bash
cat /home/jc/Documents/Horse-race-ai-v2.05/docker_advanced_metrics_populator.py | docker exec -i horse_racing_data_pipeline_clean python
```

### Success Output Contains:

```
✅ Inserted 200 speed ratings
✅ Inserted 200 power ratings
✅ Inserted 200 Monte Carlo results
🎉 SUCCESS: Advanced metrics populated!
```

### Verification Commands:

```sql
-- Check data was inserted
SELECT COUNT(*) FROM horse_speed_ratings;    -- Should return 200
SELECT COUNT(*) FROM horse_power_ratings;    -- Should return 200
SELECT COUNT(*) FROM monte_carlo_simulations; -- Should return 200
```

### Node-RED Exec Node Settings:

- **Command**: Use the primary exec command above
- **Append**: Leave empty
- **Timeout**: 30 seconds (plenty of time)
- **Return**: when command completes

### Integration Status:

✅ **TESTED & WORKING** - August 31, 2025  
✅ **200 records processed successfully**  
✅ **All advanced metrics calculated and stored**  
✅ **Ready for Node-RED integration**

---

## 🎯 What You Get:

1. **Speed Ratings** - Performance-based speed figures
2. **Power Ratings** - Comprehensive ability ratings
3. **Monte Carlo Simulations** - Win/place probabilities
4. **Real Data Processing** - Uses actual race results
5. **Docker Integration** - Runs in data-pipeline container

**Total**: 600 advanced metric records created from 200 race results!
