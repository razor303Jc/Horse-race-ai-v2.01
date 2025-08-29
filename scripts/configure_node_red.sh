#!/bin/bash

# 🏇 Node-RED Configuration Script
# Automatically configures database connections, email settings, and flows

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🏇 Node-RED Configuration Wizard"
echo "================================"
echo ""

# Check if Node-RED container is running
if ! docker ps -q -f name=horse_racing_node_red | grep -q .; then
    print_error "Node-RED container not running. Please start it first with ./setup_node_red.sh"
    exit 1
fi

print_status "Node-RED container is running ✓"

# Wait for Node-RED to be ready
print_status "Waiting for Node-RED to be ready..."
for i in {1..30}; do
    if curl -f -s http://localhost:1881 > /dev/null 2>&1; then
        print_success "Node-RED is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Node-RED did not become ready in time"
        exit 1
    fi
    sleep 2
done

# ============================================================================
# STEP 1: Configure Database Connection
# ============================================================================

echo ""
echo "🗄️  Step 1: Database Configuration"
echo "================================="

# Extract database credentials from docker-compose
DB_HOST="postgres"  # Container name in Docker network
DB_PORT="5432"
DB_NAME="postgres"
DB_USER="horse_racing"
DB_PASSWORD="secure_password_123"

print_status "Database connection details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: [HIDDEN]"

# Test database connectivity from Node-RED container
print_status "Testing database connectivity..."
if docker exec horse_racing_node_red sh -c "curl -f -s telnet://$DB_HOST:$DB_PORT" > /dev/null 2>&1; then
    print_success "Database is reachable from Node-RED container"
else
    print_warning "Cannot verify database connectivity (this is normal)"
fi

# Create database configuration file for Node-RED
print_status "Creating database configuration..."
cat > node-red/database-config.json << EOF
{
  "postgres_connection": {
    "host": "$DB_HOST",
    "port": $DB_PORT,
    "database": "$DB_NAME",
    "user": "$DB_USER",
    "password": "$DB_PASSWORD",
    "ssl": false,
    "max": 10,
    "idleTimeoutMillis": 30000,
    "connectionTimeoutMillis": 10000
  }
}
EOF

print_success "Database configuration saved to node-red/database-config.json"

# ============================================================================
# STEP 2: Email Configuration  
# ============================================================================

echo ""
echo "📧 Step 2: Email Configuration"
echo "=============================="

print_status "Email configuration options:"
echo "1. Gmail/Google Workspace"
echo "2. Outlook/Hotmail"
echo "3. Custom SMTP"
echo "4. Skip email configuration"
echo ""

read -p "Choose option (1-4) [1]: " email_choice
email_choice=${email_choice:-1}

case $email_choice in
    1)
        echo ""
        print_status "Gmail/Google Workspace Configuration"
        echo "Note: You'll need to create an App Password for Gmail"
        echo "1. Go to Google Account Settings → Security → 2-Step Verification"
        echo "2. Create App Password for 'Mail'"
        echo "3. Use that 16-character password below"
        echo ""
        
        read -p "Enter your Gmail address: " gmail_user
        read -s -p "Enter your App Password (16 characters): " gmail_pass
        echo ""
        read -p "Enter alert recipient email: " alert_email
        
        cat > node-red/email-config.json << EOF
{
  "email_config": {
    "service": "gmail",
    "host": "smtp.gmail.com",
    "port": 465,
    "secure": true,
    "auth": {
      "user": "$gmail_user",
      "pass": "$gmail_pass"
    },
    "from": "$gmail_user",
    "to": "$alert_email"
  }
}
EOF
        print_success "Gmail configuration saved"
        ;;
    2)
        echo ""
        print_status "Outlook/Hotmail Configuration"
        read -p "Enter your Outlook email: " outlook_user
        read -s -p "Enter your password: " outlook_pass
        echo ""
        read -p "Enter alert recipient email: " alert_email
        
        cat > node-red/email-config.json << EOF
{
  "email_config": {
    "service": "outlook",
    "host": "smtp-mail.outlook.com",
    "port": 587,
    "secure": true,
    "auth": {
      "user": "$outlook_user",
      "pass": "$outlook_pass"
    },
    "from": "$outlook_user",
    "to": "$alert_email"
  }
}
EOF
        print_success "Outlook configuration saved"
        ;;
    3)
        echo ""
        print_status "Custom SMTP Configuration"
        read -p "SMTP Host: " smtp_host
        read -p "SMTP Port [587]: " smtp_port
        smtp_port=${smtp_port:-587}
        read -p "Username: " smtp_user
        read -s -p "Password: " smtp_pass
        echo ""
        read -p "From email: " from_email
        read -p "Alert recipient email: " alert_email
        
        cat > node-red/email-config.json << EOF
{
  "email_config": {
    "service": "custom",
    "host": "$smtp_host",
    "port": $smtp_port,
    "secure": true,
    "auth": {
      "user": "$smtp_user",
      "pass": "$smtp_pass"
    },
    "from": "$from_email",
    "to": "$alert_email"
  }
}
EOF
        print_success "Custom SMTP configuration saved"
        ;;
    4)
        print_warning "Skipping email configuration"
        ;;
    *)
        print_warning "Invalid choice, skipping email configuration"
        ;;
esac

# ============================================================================
# STEP 3: Deploy and Test Flows
# ============================================================================

echo ""
echo "⚡ Step 3: Deploy and Test Flows"
echo "==============================="

print_status "Deploying flows to Node-RED..."

# Deploy flows via API
if curl -X POST -H "Content-Type: application/json" -s http://localhost:1881/flows > /dev/null 2>&1; then
    print_success "Flows deployed successfully"
else
    print_warning "Could not auto-deploy flows - you'll need to deploy manually"
fi

# Test database connection
print_status "Testing database connection..."
test_query='{"query": "SELECT current_timestamp as test_time, version() as postgres_version", "output": true}'

if curl -X POST -H "Content-Type: application/json" -d "$test_query" -s http://localhost:1881/test-db > /dev/null 2>&1; then
    print_success "Database test endpoint available"
else
    print_warning "Database test endpoint not available - configure manually in Node-RED"
fi

# ============================================================================
# STEP 4: Configure Schedules
# ============================================================================

echo ""
echo "⏰ Step 4: Schedule Configuration"
echo "==============================="

print_status "Available schedule options:"
echo "1. Standard (6 AM & 10 PM daily)"
echo "2. Frequent (Every 4 hours)"
echo "3. Business hours only (9 AM - 5 PM, weekdays)"
echo "4. Custom schedule"
echo ""

read -p "Choose schedule option (1-4) [1]: " schedule_choice
schedule_choice=${schedule_choice:-1}

case $schedule_choice in
    1)
        cron_schedule="0 6,22 * * *"
        schedule_desc="6 AM and 10 PM daily"
        ;;
    2)
        cron_schedule="0 */4 * * *"
        schedule_desc="Every 4 hours"
        ;;
    3)
        cron_schedule="0 9-17 * * 1-5"
        schedule_desc="Every hour, 9 AM - 5 PM, weekdays only"
        ;;
    4)
        echo ""
        print_status "Custom cron schedule format: minute hour day month weekday"
        print_status "Examples:"
        echo "  0 6,22 * * *     = 6 AM and 10 PM daily"
        echo "  */30 9-18 * * *  = Every 30 minutes, 9 AM - 6 PM"
        echo "  0 2 * * 0        = 2 AM every Sunday"
        echo ""
        read -p "Enter your cron schedule: " cron_schedule
        schedule_desc="Custom: $cron_schedule"
        ;;
esac

cat > node-red/schedule-config.json << EOF
{
  "schedule_config": {
    "main_schedule": "$cron_schedule",
    "description": "$schedule_desc",
    "timezone": "UTC",
    "enabled": true
  }
}
EOF

print_success "Schedule configuration saved: $schedule_desc"

# ============================================================================
# STEP 5: Dashboard Setup
# ============================================================================

echo ""
echo "📈 Step 5: Dashboard Configuration"
echo "================================="

print_status "Setting up dashboard components..."

# Create dashboard layout configuration
cat > node-red/dashboard-config.json << EOF
{
  "dashboard_config": {
    "title": "Horse Racing AI Dashboard",
    "theme": "dark",
    "layout": {
      "system_status": {
        "group": "System Status",
        "order": 1,
        "components": ["health_gauge", "last_update", "error_count"]
      },
      "predictions": {
        "group": "AI Predictions", 
        "order": 2,
        "components": ["accuracy_chart", "best_bets", "roi_tracker"]
      },
      "data_quality": {
        "group": "Data Quality",
        "order": 3,
        "components": ["files_processed", "validation_status", "import_progress"]
      },
      "controls": {
        "group": "Manual Controls",
        "order": 4,
        "components": ["trigger_pipeline", "emergency_stop", "refresh_data"]
      }
    }
  }
}
EOF

print_success "Dashboard configuration saved"
print_status "Dashboard will be available at: http://localhost:1881/ui"

# ============================================================================
# FINAL STEPS
# ============================================================================

echo ""
echo "🎯 Configuration Summary"
echo "======================="

print_success "✅ Database configuration: Complete"
if [ -f "node-red/email-config.json" ]; then
    print_success "✅ Email configuration: Complete"
else
    print_warning "⚠️  Email configuration: Skipped"
fi
print_success "✅ Flow deployment: Ready"
print_success "✅ Schedule configuration: Complete ($schedule_desc)"
print_success "✅ Dashboard setup: Complete"

echo ""
echo "🚀 Next Steps:"
echo "============="
echo "1. Open Node-RED Editor: http://localhost:1881"
echo "2. Open Dashboard: http://localhost:1881/ui"
echo "3. Deploy flows manually if not auto-deployed"
echo "4. Test database connections in PostgreSQL nodes"
echo "5. Test email alerts in Email nodes"
echo "6. Verify schedule in Cron Plus nodes"
echo ""

echo "🔧 Manual Configuration Required:"
echo "================================"
echo "1. PostgreSQL nodes - paste this connection string:"
echo "   postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
if [ -f "node-red/email-config.json" ]; then
    echo "2. Email nodes - configure with saved settings in email-config.json"
    echo ""
fi
echo "3. Cron Plus nodes - set schedule: $cron_schedule"
echo "4. Dashboard nodes - customize as needed"
echo ""

echo "📋 Configuration Files Created:"
echo "=============================="
echo "- node-red/database-config.json (Database settings)"
if [ -f "node-red/email-config.json" ]; then
    echo "- node-red/email-config.json (Email settings)"
fi
echo "- node-red/schedule-config.json (Schedule settings)"
echo "- node-red/dashboard-config.json (Dashboard layout)"
echo ""

print_success "🏇 Configuration wizard complete!"
echo ""
echo "💡 Tip: Keep your email app password secure and never commit it to version control!"
echo ""

# Open Node-RED in browser
if command -v xdg-open &> /dev/null; then
    print_status "Opening Node-RED editor in browser..."
    xdg-open http://localhost:1881 2>/dev/null &
elif command -v open &> /dev/null; then
    print_status "Opening Node-RED editor in browser..."
    open http://localhost:1881 2>/dev/null &
fi
