# Live Test Incident Report - August 12, 2025

## Executive Summary

The 11:01 live test was partially successful - the auto-downloader worked perfectly, but 3 Docker containers unexpectedly stopped during execution.

## Timeline of Events

### 09:51:25 UTC (Approximately)

- **Event**: React App, PgAdmin, and Docs containers received SIGTERM signals and shut down
- **Status**: Graceful shutdown (Exit codes: 0, 0, 143)
- **Root Cause**: Unknown - not resource exhaustion

### 11:01:00 UTC (Scheduled)

- **Event**: Auto-downloader successfully triggered
- **Status**: ✅ SUCCESSFUL
- **Data**: Downloaded 26 race results (248 records) and 19 race cards
- **Issue**: NTFY notification failed (hostname resolution)

### 11:02:00 UTC (Recovery)

- **Event**: Containers manually restarted
- **Status**: ✅ All systems operational

## Detailed Analysis

### ✅ What Worked

1. **Auto-Downloader Execution**: Perfect execution at 11:01
2. **Login Process**: Successful human-like login flow
3. **Data Download**: All files downloaded and extracted correctly
4. **Data Validation**: 0 validation errors, data integrity confirmed
5. **Core Infrastructure**: PostgreSQL, Redis, NTFY containers remained running

### ❌ What Failed

1. **Container Stability**: 3 containers stopped unexpectedly
2. **NTFY Notifications**: Hostname resolution error
3. **Pipeline Continuity**: Main application services were down during test

### 🔍 Root Cause Investigation

#### Container Stop Analysis

- **When**: ~09:51:25 UTC (1 hour 10 minutes before scheduled test)
- **How**: Graceful SIGTERM shutdown (not crash)
- **Why**: Unknown - potential causes:
  - Docker daemon restart/maintenance
  - System-level signal sent to containers
  - Memory pressure (unlikely - 5.4GB free)
  - Background process interference

#### NTFY Resolution Issue

```
HTTPConnectionPool(host='ntfy', port=8081): Max retries exceeded
Failed to resolve 'ntfy' - Temporary failure in name resolution
```

## Data Validation Results

### Downloaded Data (Aug 11, 2025)

- **Results**: 26 races, 248 records
- **Cards**: 19 races
- **Files**: All 25 files extracted successfully
- **Location**: `data/daily_downloads/results_data_extracted/`
- **Validation**: ✅ PASSED (0 warnings)

## System Status Post-Recovery

### Container Health

```
✅ horse_racing_react_app    - Up 10 seconds (healthy)
✅ horse_racing_pgadmin      - Up 10 seconds
✅ horse_racing_docs         - Up 9 seconds
✅ horserace-auto-downloader - Up About an hour (healthy)
✅ horse_racing_ntfy         - Up 2 hours (healthy)
✅ horse_racing_redis        - Up 2 hours (healthy)
✅ horse_racing_postgres     - Up 12 hours (healthy)
```

### Resource Utilization

- **Memory**: 5.4GB available (out of 15GB)
- **Disk**: 116GB available (out of 468GB)
- **Swap**: 784MB free

## Recommendations

### Immediate Actions

1. **✅ COMPLETED**: Restart stopped containers
2. **🔄 PENDING**: Fix NTFY hostname resolution
3. **🔄 PENDING**: Investigate container stop cause
4. **🔄 PENDING**: Test full pipeline execution with downloaded data

### Preventive Measures

1. **Container Monitoring**: Add restart policies
2. **Health Checks**: Implement container health monitoring
3. **Resource Monitoring**: Add memory/CPU alerts
4. **Network Stability**: Fix NTFY service discovery
5. **Logging Enhancement**: Add container lifecycle logging

### Next Steps

1. Execute daily pipeline with downloaded data
2. Monitor container stability during processing
3. Implement robust container restart policies
4. Add comprehensive health monitoring

## Live Test Outcome

| Component           | Status             | Details                                |
| ------------------- | ------------------ | -------------------------------------- |
| Auto-Downloader     | ✅ SUCCESS         | Perfect execution, data downloaded     |
| Data Validation     | ✅ SUCCESS         | 0 errors, 248 records validated        |
| Container Stability | ❌ PARTIAL         | 3 containers stopped unexpectedly      |
| Notifications       | ❌ FAILED          | NTFY hostname resolution               |
| Overall Test        | 🟡 PARTIAL SUCCESS | Core function worked, stability issues |

## Files Generated

- Downloaded data: `data/daily_downloads/results_data_extracted/`
- Race data: 26 races from Aug 11, 2025
- Records: 248 individual records
- Cards: 19 race cards for Aug 12, 2025

---

_Report generated: August 12, 2025 11:05 UTC_
_Status: Containers restored, system operational_
