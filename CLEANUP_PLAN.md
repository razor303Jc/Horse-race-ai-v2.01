# File Cleanup & Organization Plan

**Date:** August 30, 2025  
**Project:** Horse Racing AI v2.05  
**Purpose:** Remove redundant files and organize project structure

## 🎯 **Cleanup Summary**

### **Current File Count Analysis:**

- **Total key files:** 9,290 (JSON, MD, PY, SH)
- **CSV data files:** 62 files (~30MB)
- **Node-RED flows:** 24+ flow files (many duplicates)
- **Temporary data:** Multiple temp directories with duplicates

## 🗑️ **Files to Remove**

### **1. Duplicate Node-RED Flows (High Priority)**

These appear to be outdated or duplicate flow configurations:

**Root Level Duplicates:**

```
❌ backup_flows_20250830_200940.json (60KB) - Backup, keep in archive
❌ c2_enhanced_flows.json (87 lines) - Development version
❌ current_flows.json (1 line) - Empty/minimal
❌ current_flows_backup.json - Backup duplicate
❌ current_flows_before_redis.json - Development version
❌ flows_c2_with_ml_trainer.json - Development version
❌ flows_c2_with_pipeline.json - Development version
❌ flows_c2_with_redis.json - Development version
❌ flows_redis_health_fixed.json - Development version
❌ flows_with_redis_health.json - Development version
❌ flows_with_redis_tab.json - Development version
❌ merged_flows.json (empty) - Empty file
❌ new_health_flows.json - Development version
❌ pipeline_automation_flows.json - Development version
❌ updated_flows.json - Development version
❌ working-c2-flows.json (empty) - Empty file
```

**Action:** Move development flows to `/archive/node_red_development/`

### **2. Temporary Data Directories (High Priority)**

```
❌ temp_extract/ - Contains duplicate CSV data
❌ temp_card_processing/ - Contains duplicate CSV data
❌ Current processing temp files
```

**Action:** Archive any unique data, remove duplicates

### **3. Development Test Files (Medium Priority)**

```
❌ test_direct_exec.py - Development testing
❌ test_exec_node.json - Development config
❌ test_exec_node_readiness.py - Development testing
❌ Various C2 integration test files
```

**Action:** Move to `/archive/development_tests/`

### **4. Historical Data (Low Priority)**

```
📁 data/2025-08-20/ to 2025-08-24/ - Archive but keep
📁 Individual date directories in temp processing
```

**Action:** Archive as planned in reorganization script

## 📁 **Recommended Organization Structure**

### **Post-Cleanup Project Structure:**

```
Horse-race-ai-v2.05/
├── data/                           # Organized data (per reorganization plan)
│   ├── development/               # Active development data
│   ├── archive/                   # Historical data
│   ├── staging/                   # Pipeline processing
│   └── test_outputs/              # Generated results
├── archive/                       # Project-level archives
│   ├── node_red_development/      # Old flow files
│   ├── development_tests/         # Old test files
│   └── temp_data_backup/          # Archived temp data
├── tools/                         # Active development tools
├── tests/                         # Current test suite
├── docs/                          # Documentation
├── config/                        # Configuration files
└── [active development files]     # Current working files
```

## 🎯 **Cleanup Implementation Plan**

### **Phase 1: Critical Cleanup (Execute First)**

1. **Archive duplicate flows** to `archive/node_red_development/`
2. **Remove empty files** (merged_flows.json, working-c2-flows.json)
3. **Clean temp directories** (temp_extract, temp_card_processing)
4. **Remove development test files** to `archive/development_tests/`

### **Phase 2: Data Organization (Use Reorganization Script)**

1. Execute `./reorganize_data_structure.sh`
2. Reorganize data directories per plan
3. Create development/archive structure
4. Generate quick test samples

### **Phase 3: Final Organization**

1. Create project-level archive structure
2. Clean up root directory
3. Update documentation paths
4. Verify no broken references

## 📊 **Expected Results**

### **Space Savings:**

- **Node-RED flows:** ~500KB+ (consolidate 15+ duplicate files)
- **Temp data:** ~5-10MB (remove duplicate CSV data)
- **Development files:** ~2-5MB (archive old test files)
- **Total estimated savings:** ~15-20MB + better organization

### **Organization Benefits:**

- 🎯 Clear separation of active vs. archived files
- ⚡ Faster file system operations
- 📝 Better project navigation
- 🔍 Easier file location for developers

## ⚠️ **Safety Measures**

### **Before Cleanup:**

1. ✅ Complete git commit of current state
2. ✅ Create full project backup
3. ✅ Verify all important flows are in protected files
4. ✅ Document any custom configurations

### **During Cleanup:**

1. Move (don't delete) files to archive first
2. Verify no dependencies broken
3. Test critical functionality after each phase
4. Keep reorganization script backup available

## 🚀 **Execution Order**

### **Immediate Actions:**

```bash
# 1. Create archive structure
mkdir -p archive/{node_red_development,development_tests,temp_data_backup}

# 2. Archive duplicate flows
mv *flows*.json archive/node_red_development/ 2>/dev/null || true
mv pipeline_automation_flows.json archive/node_red_development/ 2>/dev/null || true

# 3. Execute data reorganization
./reorganize_data_structure.sh

# 4. Clean development test files
mv test_*exec* archive/development_tests/ 2>/dev/null || true
mv test_*c2* archive/development_tests/ 2>/dev/null || true
```

### **Verification Steps:**

```bash
# Verify critical systems still work
python -m pytest tests/automation/ -v
curl -X POST http://c2.horse-racing.local/api/pipeline/trigger
```

## ✅ **Success Criteria**

1. **File count reduced** by 50+ redundant files
2. **Clear project structure** with logical organization
3. **Development data optimized** for efficient testing
4. **All critical functionality** preserved and working
5. **Documentation updated** to reflect new structure

---

**This cleanup will create a lean, efficient development environment while preserving all valuable project assets.**
