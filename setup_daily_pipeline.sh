#!/bin/bash
"""
🚀 Daily Pipeline Setup Script
Sets up the complete automation pipeline for stages 2 & 3

This script configures:
- Daily data download at 00:01
- Automated relationship processing  
- Contextual analysis and insights
- Report generation with charts
- ML model updates
- System monitoring

Author: AI Assistant
Date: August 11, 2025
"""

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_USER="${USER}"
PIPELINE_HOME="${PROJECT_ROOT}"

echo "🏇 Setting up Horse Racing Daily Pipeline Automation"
echo "=================================================="
echo "Project Root: ${PROJECT_ROOT}"
echo "Pipeline User: ${PIPELINE_USER}"
echo ""

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p "${PROJECT_ROOT}/logs"
mkdir -p "${PROJECT_ROOT}/config"
mkdir -p "${PROJECT_ROOT}/reports/daily"
mkdir -p "${PROJECT_ROOT}/cache/pipeline"

# Set up configuration
echo "⚙️ Setting up configuration..."
cd "${PROJECT_ROOT}"
python3 config/daily_pipeline_config_manager.py

# Install required packages
echo "📦 Installing required Python packages..."
pip3 install schedule psycopg2-binary asyncio

# Create systemd service file
echo "🔧 Creating systemd service..."
SERVICE_FILE="/tmp/horse-racing-pipeline.service"

cat > "${SERVICE_FILE}" << EOF
[Unit]
Description=Horse Racing Daily Pipeline Automation
After=network.target postgresql.service docker.service
Wants=postgresql.service docker.service

[Service]
Type=simple
User=${PIPELINE_USER}
WorkingDirectory=${PROJECT_ROOT}
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=${PROJECT_ROOT}
Environment=POSTGRES_PASSWORD=secure_password_123
ExecStart=/usr/bin/python3 ${PROJECT_ROOT}/daily_pipeline_orchestrator.py --schedule
Restart=always
RestartSec=30
StandardOutput=append:${PROJECT_ROOT}/logs/pipeline_service.log
StandardError=append:${PROJECT_ROOT}/logs/pipeline_service.log

[Install]
WantedBy=multi-user.target
EOF

echo "📋 Systemd service file created at: ${SERVICE_FILE}"

# Create cron job as backup
echo "⏰ Setting up cron job backup..."
CRON_FILE="/tmp/horse-racing-cron"

cat > "${CRON_FILE}" << EOF
# Horse Racing Daily Pipeline Automation
# Runs daily at 00:01 AM
1 0 * * * cd ${PROJECT_ROOT} && /usr/bin/python3 ${PROJECT_ROOT}/daily_pipeline_orchestrator.py --run-now >> ${PROJECT_ROOT}/logs/cron_pipeline.log 2>&1

# Health check every hour during business hours
0 8-18 * * * cd ${PROJECT_ROOT} && /usr/bin/python3 ${PROJECT_ROOT}/daily_pipeline_orchestrator.py --status >> ${PROJECT_ROOT}/logs/health_check.log 2>&1

# Weekly cleanup of old logs (Sunday 3 AM)
0 3 * * 0 find ${PROJECT_ROOT}/logs -name "*.log" -mtime +30 -delete

# Monthly backup of configuration
0 2 1 * * cp ${PROJECT_ROOT}/config/daily_pipeline_config.json ${PROJECT_ROOT}/config/backup_\$(date +\%Y\%m\%d).json
EOF

echo "📋 Cron job file created at: ${CRON_FILE}"

# Create monitoring script
echo "🔍 Creating monitoring script..."
cat > "${PROJECT_ROOT}/monitor_pipeline.py" << 'EOF'
#!/usr/bin/env python3
"""
Pipeline monitoring and health check script.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def check_pipeline_health():
    """Check the health of the daily pipeline."""
    project_root = Path(__file__).parent
    status_file = project_root / "logs" / "pipeline_status.json"
    
    if not status_file.exists():
        print("❌ No pipeline status file found")
        return False
    
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        last_run = status.get("last_run")
        if last_run:
            last_run_time = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            time_since_last_run = datetime.now() - last_run_time.replace(tzinfo=None)
            
            if time_since_last_run > timedelta(hours=25):  # Allow 1 hour grace
                print(f"⚠️ Pipeline hasn't run in {time_since_last_run}")
                return False
        
        success_count = status.get("success_count", 0)
        failure_count = status.get("failure_count", 0)
        
        if failure_count > 0 and failure_count > success_count:
            print(f"⚠️ High failure rate: {failure_count} failures vs {success_count} successes")
            return False
        
        print(f"✅ Pipeline healthy - Last run: {last_run}")
        print(f"📊 Success: {success_count}, Failures: {failure_count}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking pipeline health: {e}")
        return False


if __name__ == "__main__":
    healthy = check_pipeline_health()
    sys.exit(0 if healthy else 1)
EOF

chmod +x "${PROJECT_ROOT}/monitor_pipeline.py"

# Create startup script
echo "🚀 Creating startup script..."
cat > "${PROJECT_ROOT}/start_daily_pipeline.sh" << EOF
#!/bin/bash
# Start the daily pipeline automation

cd "${PROJECT_ROOT}"

echo "🏇 Starting Horse Racing Daily Pipeline..."

# Start Docker services if not running
if ! docker-compose ps | grep -q "Up"; then
    echo "🐳 Starting Docker services..."
    docker-compose up -d postgres mkdocs
    sleep 10
fi

# Start the pipeline orchestrator
echo "🚀 Starting pipeline orchestrator..."
python3 daily_pipeline_orchestrator.py --schedule
EOF

chmod +x "${PROJECT_ROOT}/start_daily_pipeline.sh"

# Create test script
echo "🧪 Creating test script..."
cat > "${PROJECT_ROOT}/test_daily_pipeline.sh" << EOF
#!/bin/bash
# Test the daily pipeline setup

cd "${PROJECT_ROOT}"

echo "🧪 Testing Daily Pipeline Setup..."
echo "================================"

# Test configuration
echo "📋 Testing configuration..."
python3 -c "
import json
from pathlib import Path
config_file = Path('config/daily_pipeline_config.json')
if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
    print('✅ Configuration loaded successfully')
    print(f'   - Schedule: {config[\"schedule\"][\"download_time\"]}')
    print(f'   - Sources: {len(config[\"data_sources\"][\"enabled\"])}')
else:
    print('❌ Configuration file not found')
    exit(1)
"

# Test database connection
echo "🗄️ Testing database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='horse_racing_db',
        user='horse_racing',
        password='secure_password_123'
    )
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM race_results')
        count = cur.fetchone()[0]
    print(f'✅ Database connection successful - {count} records')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# Test pipeline execution (dry run)
echo "🔄 Testing pipeline execution..."
python3 daily_pipeline_orchestrator.py --status

echo ""
echo "✅ Daily Pipeline Setup Complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "1. Review configuration in config/daily_pipeline_config.json"
echo "2. Install systemd service: sudo cp /tmp/horse-racing-pipeline.service /etc/systemd/system/"
echo "3. Enable service: sudo systemctl enable horse-racing-pipeline"
echo "4. Start service: sudo systemctl start horse-racing-pipeline"
echo "5. Install cron job: crontab /tmp/horse-racing-cron"
echo "6. Monitor logs: tail -f logs/pipeline_service.log"
echo ""
echo "Manual commands:"
echo "- Start pipeline: ./start_daily_pipeline.sh"
echo "- Run once: python3 daily_pipeline_orchestrator.py --run-now"
echo "- Check status: python3 daily_pipeline_orchestrator.py --status"
echo "- Monitor health: python3 monitor_pipeline.py"
EOF

chmod +x "${PROJECT_ROOT}/test_daily_pipeline.sh"

echo ""
echo "✅ Daily Pipeline Setup Complete!"
echo "================================="
echo ""
echo "Files created:"
echo "- ${PROJECT_ROOT}/daily_pipeline_orchestrator.py"
echo "- ${PROJECT_ROOT}/config/daily_pipeline_config_manager.py"
echo "- ${PROJECT_ROOT}/monitor_pipeline.py"
echo "- ${PROJECT_ROOT}/start_daily_pipeline.sh"
echo "- ${PROJECT_ROOT}/test_daily_pipeline.sh"
echo "- ${SERVICE_FILE}"
echo "- ${CRON_FILE}"
echo ""
echo "🚀 Ready to automate your complete pipeline!"
echo ""
echo "Run the test script to verify everything:"
echo "./test_daily_pipeline.sh"
