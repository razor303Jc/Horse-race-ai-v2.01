# 📤 Manual Data Upload System Plan

## Horse Racing AI v2.03 - Data Pipeline Enhancement

### 🎯 **Objective**

Design a robust manual data upload system to replace unreliable auto-downloader, ensuring consistent daily data flow for the racing analysis system.

---

## 📋 **Phase 1: Web-Based Upload Interface**

### **1.1 Upload Dashboard (Priority: 🔴 CRITICAL)**

```typescript
// New API endpoint: /api/admin/upload
POST / api / admin / upload / race - cards; // Upload today's race cards
POST / api / admin / upload / results; // Upload yesterday's results
GET / api / admin / upload / status; // Check upload status
GET / api / admin / upload / history; // Upload history
DELETE / api / admin / upload / { date }; // Remove incorrect upload
```

### **1.2 File Upload Features**

- **Drag & Drop Interface** - Modern file upload with progress bars
- **File Validation** - Check file format (CSV, JSON, ZIP)
- **Date Detection** - Auto-detect race date from uploaded files
- **Duplicate Prevention** - Warn if data already exists for date
- **Preview Mode** - Show sample data before confirming upload

### **1.3 Upload Status Dashboard**

```
📊 Data Upload Status - August 20, 2025

┌─────────────────────────────────────────┐
│ 📅 Today's Status                       │
├─────────────────────────────────────────┤
│ ✅ Race Cards: Uploaded (31 races)      │
│ ❌ Results: Missing for Aug 19          │
│ 🔄 Data Pipeline: Processing...         │
│ ⚠️  ML Models: Waiting for data         │
└─────────────────────────────────────────┘

🎯 Required Actions:
• Upload yesterday's results (Aug 19)
• Verify data pipeline completion
```

---

## 📋 **Phase 2: Enhanced Data Pipeline**

### **2.1 Pipeline Restructure**

```python
# New pipeline architecture
class ManualDataPipeline:
    def process_uploaded_files(self, file_type: str, date: str):
        """Process manually uploaded files"""

    def validate_data_integrity(self):
        """Validate uploaded data quality"""

    def update_database(self):
        """Smart database updates with conflict resolution"""

    def trigger_ml_retraining(self):
        """Trigger ML model updates when new data available"""
```

### **2.2 Data Validation Engine**

- **Schema Validation** - Ensure correct CSV column structure
- **Date Consistency** - Verify race dates match expected patterns
- **Data Completeness** - Check for missing horses, jockeys, odds
- **Cross-Reference Checks** - Validate race IDs between cards and results

### **2.3 Smart Upload Processing**

- **Incremental Updates** - Only process new/changed records
- **Rollback Capability** - Undo incorrect uploads
- **Data Merge Logic** - Handle partial uploads (e.g., only some races)
- **Error Recovery** - Continue processing despite individual record errors

---

## 📋 **Phase 3: User Experience Enhancements**

### **3.1 Upload Workflow**

```
1. 📥 User Downloads Files from HorseRaceDatabase.com
   ├── Race Cards (today's races)
   └── Results (yesterday's completed races)

2. 🖱️  User Drags Files to Upload Dashboard
   ├── Auto-detect file type (cards vs results)
   ├── Show preview of detected races
   └── Confirm date and race count

3. 🔄 System Processes Upload
   ├── Validate file structure
   ├── Check for duplicates
   ├── Import to database
   └── Update ML models

4. ✅ Confirmation & Status Update
   ├── Show successful import summary
   ├── Update dashboard status
   └── Trigger betting recommendations refresh
```

### **3.2 Error Handling & User Guidance**

- **Clear Error Messages** - "File format incorrect - expected CSV with columns: Race_ID, Course, etc."
- **Upload Guidelines** - Step-by-step instructions with screenshots
- **File Templates** - Download sample files showing correct format
- **Support Links** - Direct links to HorseRaceDatabase.com download pages

---

## 📋 **Phase 4: Automation & Monitoring**

### **4.1 Upload Monitoring**

```python
# Daily data completeness check
class DataCompletenessMonitor:
    def check_daily_requirements(self, date: str):
        """Check if all required data is available for date"""
        required = {
            'race_cards': f"cards_data for {date}",
            'results': f"results_data for {date-1}",
            'horses': "horse entries with odds",
            'jockeys': "jockey assignments"
        }
        return self.validate_requirements(required)
```

### **4.2 Smart Notifications**

- **Missing Data Alerts** - Email/dashboard notifications for missing uploads
- **Data Quality Warnings** - Alert when uploaded data has issues
- **Success Confirmations** - Confirm when day's data is complete
- **ML Model Status** - Notify when models need retraining

### **4.3 Backup & Recovery**

- **Automatic Backups** - Save uploaded files to secure archive
- **Upload History** - Track what was uploaded when and by whom
- **Data Rollback** - Ability to restore previous day's data if needed

---

## 📋 **Implementation Priority**

### **Week 1: Core Upload System** 🔴

- [ ] Create upload API endpoints
- [ ] Build file upload interface
- [ ] Implement basic validation
- [ ] Test with sample data files

### **Week 2: Pipeline Integration** 🟡

- [ ] Connect uploads to database pipeline
- [ ] Fix data-pipeline service health issues
- [ ] Add data validation engine
- [ ] Test end-to-end workflow

### **Week 3: User Experience** 🟢

- [ ] Polish upload interface
- [ ] Add status dashboard
- [ ] Create user documentation
- [ ] Implement error handling

### **Week 4: Monitoring & Automation** 🔵

- [ ] Add upload monitoring
- [ ] Implement notifications
- [ ] Create backup system
- [ ] Performance optimization

---

## 🔧 **Technical Implementation**

### **API Endpoints to Add**

```python
# src/web/api_server_enhanced.py

@app.post("/api/admin/upload/race-cards")
async def upload_race_cards(file: UploadFile):
    """Upload today's race cards CSV/ZIP file"""

@app.post("/api/admin/upload/results")
async def upload_results(file: UploadFile):
    """Upload yesterday's results CSV/ZIP file"""

@app.get("/api/admin/upload/status")
async def get_upload_status():
    """Get current data upload status and completeness"""

@app.get("/api/admin/data-requirements")
async def get_data_requirements():
    """Get list of required uploads for today"""
```

### **Frontend Components to Add**

```typescript
// React components needed
-UploadDashboard.tsx - // Main upload interface
  FileDropZone.tsx - // Drag & drop file upload
  UploadStatus.tsx - // Status indicators
  DataPreview.tsx - // Preview uploaded data
  UploadHistory.tsx; // Historical upload tracking
```

---

## 🎯 **Success Metrics**

### **Reliability**

- ✅ **99% Daily Data Availability** - No missing race days
- ✅ **< 2 Hour Processing Time** - From upload to ML models updated
- ✅ **Zero Data Loss** - All uploads properly backed up

### **User Experience**

- ✅ **< 5 Minutes Upload Time** - From file download to system update
- ✅ **Clear Status Visibility** - Always know what data is missing
- ✅ **Error Recovery** - Easy to fix incorrect uploads

### **Data Quality**

- ✅ **100% Schema Validation** - All uploads match expected format
- ✅ **Duplicate Prevention** - No accidental double-imports
- ✅ **Cross-Reference Integrity** - Race IDs consistent across files

---

## 🚀 **Next Steps**

1. **Immediate** - Disable auto-downloader to prevent confusion
2. **Today** - Start building core upload API endpoints
3. **This Week** - Create basic upload interface for testing
4. **Next Week** - Full system integration and testing

This plan transforms the unreliable auto-download system into a robust, user-controlled data pipeline that ensures consistent daily data flow while giving you full control over data quality and timing.
