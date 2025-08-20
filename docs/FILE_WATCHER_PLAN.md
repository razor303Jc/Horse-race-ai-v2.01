# 📁 File Watcher & Auto-Processing System

## Horse Racing AI v2.03 - Automated Pipeline Trigger

### 🎯 **Objective**

Create a robust file watcher system that monitors `/data/daily_downloads/manual_download/` for new ZIP files, automatically extracts them, and triggers the data pipeline.

---

## 📋 **Current State Analysis**

### **Downloaded Files Detected**

```
📁 /data/daily_downloads/manual_download/
├── uk-racecards-gmj4yd.zip    (Race Cards)
└── uk-results-jutrjw.zip      (Results)
```

### **Target Directory Structure**

```
📁 /data/daily_downloads/
├── manual_download/           # 👈 User drops ZIP files here
│   ├── uk-racecards-*.zip
│   └── uk-results-*.zip
├── cards_data/               # 👈 Auto-extracted race cards
│   ├── races/
│   ├── records/
│   └── horses/
├── results_data/             # 👈 Auto-extracted results
│   ├── races/
│   └── racecard_details/
└── processed/                # 👈 Archive processed files
    ├── 2025-08-20/
    └── backup/
```

---

## 🔄 **File Watcher Architecture**

### **1. Directory Monitoring Service**

```python
# tools/automation/file_watcher.py
import asyncio
import zipfile
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RacingDataFileWatcher(FileSystemEventHandler):
    """Monitors manual_download directory for new ZIP files"""

    def __init__(self):
        self.watch_dir = Path("data/daily_downloads/manual_download")
        self.cards_dir = Path("data/daily_downloads/cards_data")
        self.results_dir = Path("data/daily_downloads/results_data")
        self.processed_dir = Path("data/daily_downloads/processed")

    async def on_created(self, event):
        """Triggered when new file is added"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.zip':
            await self.process_zip_file(file_path)

    async def process_zip_file(self, zip_path: Path):
        """Process and extract ZIP file"""
        try:
            # Determine file type from name
            if 'racecard' in zip_path.name.lower() or 'card' in zip_path.name.lower():
                await self.extract_race_cards(zip_path)
            elif 'result' in zip_path.name.lower():
                await self.extract_results(zip_path)
            else:
                logger.warning(f"Unknown ZIP type: {zip_path.name}")

        except Exception as e:
            logger.error(f"Error processing {zip_path}: {e}")
```

### **2. Smart ZIP Extraction**

```python
class ZipExtractor:
    """Intelligent ZIP file extractor with validation"""

    async def extract_race_cards(self, zip_path: Path):
        """Extract race cards ZIP to cards_data directory"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Clear previous cards_data
            self.clear_directory(self.cards_dir)

            # Extract all files
            zip_ref.extractall(self.cards_dir)

            # Validate extracted data
            if await self.validate_cards_data():
                logger.info(f"✅ Race cards extracted: {zip_path.name}")
                await self.trigger_pipeline("cards")
                await self.archive_processed_file(zip_path, "cards")
            else:
                logger.error(f"❌ Invalid race cards data: {zip_path.name}")

    async def extract_results(self, zip_path: Path):
        """Extract results ZIP to results_data directory"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Clear previous results_data
            self.clear_directory(self.results_dir)

            # Extract all files
            zip_ref.extractall(self.results_dir)

            # Validate extracted data
            if await self.validate_results_data():
                logger.info(f"✅ Results extracted: {zip_path.name}")
                await self.trigger_pipeline("results")
                await self.archive_processed_file(zip_path, "results")
            else:
                logger.error(f"❌ Invalid results data: {zip_path.name}")
```

### **3. Data Validation Engine**

```python
class DataValidator:
    """Validates extracted race data quality"""

    async def validate_cards_data(self) -> bool:
        """Validate race cards data structure"""
        required_files = [
            "races/races.csv",
            "records/records.csv",
            "horses/horses.csv"
        ]

        for file_path in required_files:
            full_path = self.cards_dir / file_path
            if not full_path.exists():
                logger.error(f"Missing required file: {file_path}")
                return False

        # Validate CSV structure
        races_df = pd.read_csv(self.cards_dir / "races/races.csv")
        if not self.validate_races_columns(races_df):
            return False

        logger.info(f"✅ Cards data validation passed: {len(races_df)} races")
        return True

    async def validate_results_data(self) -> bool:
        """Validate results data structure"""
        required_files = [
            "races/races.csv",
            "racecard_details/racecard_details.html"
        ]

        for file_path in required_files:
            full_path = self.results_dir / file_path
            if not full_path.exists():
                logger.error(f"Missing required file: {file_path}")
                return False

        logger.info("✅ Results data validation passed")
        return True
```

### **4. Pipeline Integration**

```python
class PipelineTrigger:
    """Triggers data pipeline after successful extraction"""

    async def trigger_pipeline(self, data_type: str):
        """Trigger appropriate pipeline based on data type"""
        try:
            if data_type == "cards":
                await self.process_race_cards()
            elif data_type == "results":
                await self.process_results()

            # Check if both data types are ready
            if await self.both_datasets_ready():
                await self.trigger_full_pipeline()

        except Exception as e:
            logger.error(f"Pipeline trigger failed: {e}")

    async def process_race_cards(self):
        """Process race cards into database"""
        # Import race cards data
        from tools.data_processing.database_uploader import DatabaseUploader

        uploader = DatabaseUploader()
        success = await uploader.upload_race_cards(self.cards_dir)

        if success:
            logger.info("✅ Race cards uploaded to database")
            # Update API status
            await self.update_api_status("cards", "uploaded")
        else:
            logger.error("❌ Race cards upload failed")

    async def trigger_full_pipeline(self):
        """Trigger complete ML pipeline when both datasets ready"""
        logger.info("🚀 Triggering full ML pipeline...")

        # Trigger ML model retraining
        # Refresh betting recommendations
        # Update dashboard status

        await self.notify_completion()
```

---

## 🛠️ **Implementation Plan**

### **Phase 1: File Watcher Service (TODAY)**

```bash
# 1. Create directory structure
mkdir -p data/daily_downloads/manual_download
mkdir -p data/daily_downloads/processed
mkdir -p tools/automation

# 2. Install watchdog dependency
pip install watchdog

# 3. Create file watcher service
# tools/automation/file_watcher.py

# 4. Test with existing ZIP files
python tools/automation/file_watcher.py --test
```

### **Phase 2: Extract Current Files (TODAY)**

```python
# Immediate action - process existing files
async def process_existing_files():
    """Process the already downloaded ZIP files"""
    manual_dir = Path("data/daily_downloads/manual_download")

    for zip_file in manual_dir.glob("*.zip"):
        if 'racecard' in zip_file.name.lower():
            await extract_race_cards(zip_file)
        elif 'result' in zip_file.name.lower():
            await extract_results(zip_file)
```

### **Phase 3: Pipeline Integration (THIS WEEK)**

```python
# Integration with existing pipeline
class ExistingPipelineConnector:
    """Connect to existing data pipeline"""

    def __init__(self):
        self.data_pipeline = "data-pipeline service"
        self.database_uploader = "database upload service"

    async def trigger_existing_pipeline(self):
        """Restart existing pipeline with new data"""
        # Fix data-pipeline service health
        # Trigger database upload
        # Update ML models
```

---

## 📊 **File Watcher Configuration**

### **Docker Service Addition**

```yaml
# Add to docker-compose.yml
file-watcher:
  build:
    context: .
    dockerfile: docker/file-watcher/Dockerfile
  volumes:
    - ./data:/app/data
  environment:
    - WATCH_DIR=/app/data/daily_downloads/manual_download
    - EXTRACT_DIR=/app/data/daily_downloads
  depends_on:
    - postgres
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "python", "-c", "import tools.automation.file_watcher"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### **Systemd Service (Alternative)**

```ini
# /etc/systemd/system/racing-file-watcher.service
[Unit]
Description=Horse Racing Data File Watcher
After=network.target

[Service]
Type=simple
User=jc
WorkingDirectory=/home/jc/Documents/Horse-race-ai-v2.03
ExecStart=/usr/bin/python3 tools/automation/file_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔔 **Notification System**

### **Status Updates**

```python
class NotificationManager:
    """Send status updates about file processing"""

    async def notify_file_detected(self, filename: str):
        """Notify when new file is detected"""
        message = f"🔍 New file detected: {filename}"
        await self.send_notification(message)

    async def notify_extraction_complete(self, file_type: str, race_count: int):
        """Notify when extraction completes"""
        message = f"✅ {file_type} extracted: {race_count} races processed"
        await self.send_notification(message)

    async def notify_pipeline_complete(self):
        """Notify when full pipeline completes"""
        message = "🎉 Data pipeline complete - new race data available!"
        await self.send_notification(message)
```

---

## 🚀 **Immediate Next Steps**

### **1. Process Current Files (NOW)**

```bash
# Create the file watcher
cd /home/jc/Documents/Horse-race-ai-v2.03

# Process existing ZIP files
python -c "
import zipfile
from pathlib import Path

# Extract race cards
with zipfile.ZipFile('data/daily_downloads/manual_download/uk-racecards-gmj4yd.zip', 'r') as zip_ref:
    zip_ref.extractall('data/daily_downloads/cards_data')

# Extract results
with zipfile.ZipFile('data/daily_downloads/manual_download/uk-results-jutrjw.zip', 'r') as zip_ref:
    zip_ref.extractall('data/daily_downloads/results_data')

print('✅ Files extracted successfully')
"
```

### **2. Set Up File Watcher (TODAY)**

```bash
# Install dependencies
pip install watchdog pandas

# Create file watcher service
# Start monitoring for future files
```

### **3. Fix Data Pipeline (THIS WEEK)**

```bash
# Restart data pipeline with new data
docker compose restart data-pipeline

# Verify data is being processed
curl http://localhost:3000/api/daily_races
```

---

## ✅ **Success Criteria**

1. **✅ File Detection** - New ZIP files automatically detected
2. **✅ Smart Extraction** - Correct extraction to appropriate directories
3. **✅ Data Validation** - Extracted data validates successfully
4. **✅ Pipeline Trigger** - Data pipeline processes new data
5. **✅ Database Update** - Fresh race data available in APIs
6. **✅ Archive Management** - Processed files archived properly

This system will transform your manual download process into a seamless automated pipeline that starts working as soon as you drop the ZIP files into the watch directory!
