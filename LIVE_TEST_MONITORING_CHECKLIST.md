# 🔍 LIVE TEST MONITORING CHECKLIST - 12:31 AUTO-DOWNLOADER

## **PRE-TEST BASELINE (11:56)**

### **Container Status:**

```bash
docker ps --filter name=horserace-auto-downloader
# Expected: Running (healthy)
```

### **Database Baseline:**

```bash
PGPASSWORD=secure_password_123 psql -h localhost -p 5433 -U horse_racing -d horse_racing_db -c "
SELECT COUNT(*) as total_records, COUNT(race_date) as with_dates
FROM race_results;"
# Current: 7,332 total, 432 with dates
```

### **Downloads Directory:**

```bash
ls -la data/daily_downloads/
# Should be clean (removed previous test data)
```

---

## **MONITORING COMMANDS (12:30-12:35)**

### **1. Auto-Downloader Logs (Real-time)**

```bash
docker logs -f horserace-auto-downloader
# Watch for: "📅 Scheduled auto downloader for 12:31 daily"
# Then: Login process, downloads, validation
```

### **2. File System Monitoring**

```bash
watch -n 10 "find data/daily_downloads -name '*.csv' -mtime -1 2>/dev/null | head -10"
# Watch for new CSV files appearing
```

### **3. Database Record Tracking**

```bash
# Run every minute from 12:30-12:35
PGPASSWORD=secure_password_123 psql -h localhost -p 5433 -U horse_racing -d horse_racing_db -c "
SELECT
  (SELECT COUNT(*) FROM race_results) as race_results_total,
  (SELECT COUNT(race_date) FROM race_results WHERE race_date IS NOT NULL) as race_results_with_dates,
  (SELECT COUNT(*) FROM races_cards) as races_cards_total,
  (SELECT COUNT(date) FROM races_cards WHERE date IS NOT NULL) as races_cards_with_dates;
"
```

---

## **CRITICAL CHECKPOINTS**

### **12:31:00 - Trigger Time**

- [ ] Auto-downloader starts execution
- [ ] Login process begins
- [ ] Browser automation starts

### **12:31:30 - Login Phase**

- [ ] Successful authentication
- [ ] Navigation to downloads page
- [ ] Cookie extraction

### **12:32:00 - Download Phase**

- [ ] Results data download starts
- [ ] Cards data download starts
- [ ] ZIP files created

### **12:32:30 - Processing Phase**

- [ ] ZIP file extraction
- [ ] CSV files created
- [ ] Data validation runs

### **12:33:00 - Completion**

- [ ] Validation passes
- [ ] NTFY notification sent
- [ ] Process completes

### **12:33:30 - Database Impact**

- [ ] Check if CSV data imported to database
- [ ] Check if race_date fields populated
- [ ] Check if new dates appear

---

## **DATA FLOW TRACKING**

### **Step 1: CSV Creation**

```bash
# After 12:32, check for new CSV files
find data/daily_downloads -name "*.csv" -newer /tmp/test_marker 2>/dev/null
```

### **Step 2: Date Content Analysis**

```bash
# Check what dates are in the new CSV files
for file in $(find data/daily_downloads -name "*.csv" -mtime -1); do
  echo "File: $file"
  head -2 "$file" | tail -1 | grep -oE "2025-[0-9]{2}-[0-9]{2}" | head -1
done
```

### **Step 3: Database Import Detection**

```bash
# Check if database changes after CSV creation
PGPASSWORD=secure_password_123 psql -h localhost -p 5433 -U horse_racing -d horse_racing_db -c "
SELECT MAX(id), COUNT(*) FROM race_results;
SELECT DISTINCT race_date FROM race_results WHERE race_date > '2025-08-01';
"
```

---

## **PROBLEM IDENTIFICATION MATRIX**

| Issue                       | Symptom                         | Root Cause                  |
| --------------------------- | ------------------------------- | --------------------------- |
| No auto-downloader trigger  | No logs at 12:31                | Scheduling problem          |
| Login fails                 | Authentication errors           | Credentials/website changes |
| Download fails              | No ZIP files                    | Network/server issues       |
| No CSV files                | ZIP extracted but no CSVs       | Extraction process broken   |
| CSV files but no DB import  | Files exist, DB unchanged       | Import pipeline missing     |
| Wrong dates in CSV          | Dates don't match today         | Source data timing issue    |
| CSV imported but NULL dates | DB records increase, dates NULL | Date parsing/mapping issue  |

---

## **REAL-TIME MONITORING PROTOCOL**

### **12:30-12:31: Pre-execution**

- Start `docker logs -f horserace-auto-downloader` in terminal
- Create timestamp marker: `touch /tmp/test_marker`

### **12:31-12:32: Execution**

- Watch logs for trigger and login
- Monitor container health
- Check for error messages

### **12:32-12:33: Download & Processing**

- Watch for ZIP download messages
- Monitor file system for new files
- Check data validation logs

### **12:33-12:35: Post-processing**

- Check database for changes
- Analyze CSV content vs DB content
- Document any discrepancies

---

## **SUCCESS CRITERIA**

### **Minimum Success:**

- ✅ Auto-downloader triggers at 12:31
- ✅ Downloads complete successfully
- ✅ CSV files created with valid data

### **Full Success:**

- ✅ All minimum criteria +
- ✅ Database records increase
- ✅ New dates appear in database
- ✅ Date fields properly populated

---

_Use this checklist to systematically track the live test and identify exactly where the data pipeline breaks down._
