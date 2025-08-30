#!/bin/bash
# Node-RED Command & Control Setup Script
# Sets up comprehensive C2 flows with NTFY integration

set -e

NODERED_URL="http://localhost:1881"
FLOWS_FILE="/home/jc/Documents/Horse-race-ai-v2.04/NODE_RED_C2_MASTER_FLOWS.json"
BACKUP_DIR="/home/jc/Documents/Horse-race-ai-v2.04/backups"

echo "🎯 Setting up Node-RED Command & Control Center..."

# Create backup of existing flows
timestamp=$(date '+%Y%m%d_%H%M%S')
backup_file="$BACKUP_DIR/nodered_flows_backup_c2_setup_$timestamp.json"

echo "📦 Creating backup of existing Node-RED flows..."
if curl -s "$NODERED_URL/flows" > "$backup_file"; then
    echo "✅ Backup created: $backup_file"
else
    echo "⚠️ Could not create backup, continuing anyway..."
fi

# Install required Node-RED nodes
echo "📦 Installing required Node-RED nodes..."

# Check if Node-RED admin API is available
if ! curl -s "$NODERED_URL/flows" > /dev/null; then
    echo "❌ Node-RED is not accessible at $NODERED_URL"
    echo "Please ensure Node-RED is running on port 1881"
    exit 1
fi

# Install required nodes via Docker exec (since we're running in container)
echo "🔧 Installing Node-RED nodes in container..."
docker exec horse_racing_node_red_dashboard npm install \
    node-red-dashboard \
    node-red-contrib-postgres \
    node-red-node-email \
    node-red-contrib-ui-led \
    node-red-contrib-moment \
    node-red-contrib-fs-ops \
    node-red-contrib-cron-plus

echo "🔄 Restarting Node-RED to load new nodes..."
docker restart horse_racing_node_red_dashboard

# Wait for Node-RED to come back online
echo "⏳ Waiting for Node-RED to restart..."
sleep 10

max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s "$NODERED_URL/flows" > /dev/null; then
        echo "✅ Node-RED is back online"
        break
    fi
    echo "⏳ Attempt $attempt/$max_attempts - waiting for Node-RED..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Node-RED did not come back online within expected time"
    exit 1
fi

# Deploy C2 flows
echo "🚀 Deploying Command & Control flows..."
if [ -f "$FLOWS_FILE" ]; then
    if curl -X POST \
           -H "Content-Type: application/json" \
           -d @"$FLOWS_FILE" \
           "$NODERED_URL/flows"; then
        echo "✅ C2 flows deployed successfully"
    else
        echo "❌ Failed to deploy C2 flows"
        exit 1
    fi
else
    echo "❌ C2 flows file not found: $FLOWS_FILE"
    exit 1
fi

# Configure PostgreSQL connections
echo "🗃️ Setting up database connections..."

# Test database connectivity
echo "🧪 Testing database connections..."
for db in "cards_horse_racing_db" "results_horse_racing_db" "advanced_racing_metrics_db"; do
    if docker exec horse_racing_postgres_clean psql -U postgres -d "$db" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Database $db is accessible"
    else
        echo "⚠️ Database $db may not be accessible"
    fi
done

# Send deployment notification
echo "📱 Sending deployment notification..."
curl -X POST \
     -H 'Title: 🎯 C2 System Deployed' \
     -H 'Tags: deployment,c2,system,success' \
     -H 'Priority: default' \
     -d 'Node-RED Command & Control Center has been successfully deployed! Dashboard is available at http://localhost:1881 with real-time system monitoring, NTFY integration, and comprehensive automation workflows.' \
     http://localhost:8082/horserace-system

# Create C2 management shortcuts
echo "🔧 Creating management shortcuts..."

cat > /home/jc/Documents/Horse-race-ai-v2.04/c2_control.sh << 'EOF'
#!/bin/bash
# Quick C2 Control Commands

NODERED_URL="http://localhost:1881"
NTFY_URL="http://localhost:8082"

case "$1" in
    "dashboard")
        echo "🎯 Opening C2 Dashboard..."
        xdg-open "$NODERED_URL" 2>/dev/null || echo "Dashboard: $NODERED_URL"
        ;;
    "ntfy")
        echo "📱 Opening NTFY Interface..."
        xdg-open "$NTFY_URL" 2>/dev/null || echo "NTFY: $NTFY_URL"
        ;;
    "status")
        echo "📊 System Status:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(web_app|node_red|ntfy|postgres)"
        ;;
    "restart")
        echo "🔄 Restarting C2 services..."
        docker restart horse_racing_node_red_dashboard
        echo "✅ Node-RED restarted"
        ;;
    "backup")
        echo "💾 Creating flows backup..."
        timestamp=$(date '+%Y%m%d_%H%M%S')
        curl -s "$NODERED_URL/flows" > "/home/jc/Documents/Horse-race-ai-v2.04/backups/manual_backup_$timestamp.json"
        echo "✅ Backup created: manual_backup_$timestamp.json"
        ;;
    "notify")
        shift
        message="$*"
        if [ -n "$message" ]; then
            curl -X POST -H 'Title: 📢 Manual Notification' -H 'Tags: manual,admin' -d "$message" "$NTFY_URL/horserace-system"
            echo "✅ Notification sent"
        else
            echo "Usage: $0 notify <message>"
        fi
        ;;
    *)
        echo "🎯 Horse Racing AI - C2 Control Panel"
        echo "Usage: $0 {dashboard|ntfy|status|restart|backup|notify}"
        echo ""
        echo "Commands:"
        echo "  dashboard  - Open Node-RED C2 dashboard"
        echo "  ntfy      - Open NTFY notification interface"
        echo "  status    - Show service status"
        echo "  restart   - Restart Node-RED service"
        echo "  backup    - Create manual flows backup"
        echo "  notify    - Send manual notification"
        ;;
esac
EOF

chmod +x /home/jc/Documents/Horse-race-ai-v2.04/c2_control.sh

echo ""
echo "🎉 Node-RED Command & Control Center Setup Complete!"
echo ""
echo "📋 Quick Access:"
echo "   C2 Dashboard:  http://localhost:1881"
echo "   NTFY Monitor:  http://localhost:8082"
echo "   Web App:       http://localhost:3000"
echo ""
echo "🛠️ Management Commands:"
echo "   ./c2_control.sh dashboard  # Open C2 dashboard"
echo "   ./c2_control.sh status     # Check system status"
echo "   ./c2_control.sh notify     # Send notifications"
echo ""
echo "📱 NTFY Topics:"
echo "   horserace-system      # System notifications"
echo "   horserace-processing  # Data processing updates"
echo "   horserace-alerts     # Critical alerts"
echo "   horserace-monitoring # Performance monitoring"
echo ""
echo "✅ Your Command & Control Center is now operational!"
