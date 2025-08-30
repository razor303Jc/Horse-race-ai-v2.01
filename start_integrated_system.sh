#!/bin/bash

# Horse Racing AI - Complete System Startup Script
# This script starts all components of the integrated pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🐎 Horse Racing AI - System Startup"
echo "====================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start a service in background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    
    echo "Starting $name..."
    
    if check_port $port; then
        echo "⚠️  Port $port already in use - $name may already be running"
    else
        cd "$PROJECT_ROOT"
        nohup $command > "logs/${name}.log" 2>&1 &
        echo $! > "logs/${name}.pid"
        
        # Wait a moment and check if it started
        sleep 2
        if check_port $port; then
            echo "✅ $name started successfully on port $port"
        else
            echo "❌ Failed to start $name on port $port"
        fi
    fi
}

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

echo ""
echo "1️⃣ Starting Node-RED (Dashboard & Automation)"
if check_port 1880; then
    echo "⚠️  Node-RED already running on port 1880"
else
    cd "$PROJECT_ROOT"
    nohup node-red --userDir node-red > logs/node-red.log 2>&1 &
    echo $! > logs/node-red.pid
    sleep 3
    if check_port 1880; then
        echo "✅ Node-RED started successfully"
        echo "   Dashboard: http://localhost:1880"
    else
        echo "❌ Failed to start Node-RED"
    fi
fi

echo ""
echo "2️⃣ Starting Prediction API"
start_service "prediction-api" "python api/prediction_api.py" 5000

echo ""
echo "3️⃣ Starting ML Management API"
start_service "ml-management-api" "python api/ml_management_api.py" 5001

echo ""
echo "4️⃣ Starting Web Application"
cd "$PROJECT_ROOT/web_app"
start_service "web-app" "python racing_web_app.py" 8080

echo ""
echo "🎉 System Startup Complete!"
echo "=========================="
echo ""
echo "📊 Access Points:"
echo "  • Node-RED Dashboard:    http://localhost:1880"
echo "  • Web Application:       http://localhost:8080"  
echo "  • Prediction API:        http://localhost:5000"
echo "  • ML Management API:     http://localhost:5001"
echo ""
echo "📝 Logs are available in: $PROJECT_ROOT/logs/"
echo ""
echo "🔧 Management Commands:"
echo "  • Stop all services:     ./stop_system.sh"
echo "  • View logs:             tail -f logs/[service-name].log"
echo "  • Check status:          ./check_system_status.sh"
echo ""

# Create a simple status check
cat > "$PROJECT_ROOT/check_system_status.sh" << 'EOF'
#!/bin/bash

echo "🐎 Horse Racing AI - System Status"
echo "=================================="

services=(
    "Node-RED:1880"
    "Prediction API:5000"
    "ML Management API:5001"
    "Web Application:8080"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "✅ $name (port $port) - Running"
    else
        echo "❌ $name (port $port) - Stopped"
    fi
done

echo ""
echo "📊 Quick Health Check:"
echo "  Database connection:"
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(host='localhost', database='racing_data', user='racing_user', password='racing_password')
    conn.close()
    print('  ✅ PostgreSQL - Connected')
except:
    print('  ❌ PostgreSQL - Connection failed')
" 2>/dev/null || echo "  ❌ PostgreSQL - psycopg2 not available"
EOF

chmod +x "$PROJECT_ROOT/check_system_status.sh"

# Create stop script
cat > "$PROJECT_ROOT/stop_system.sh" << 'EOF'
#!/bin/bash

echo "🛑 Stopping Horse Racing AI System"
echo "================================="

# Kill processes by PID files
for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        service_name=$(basename "$pidfile" .pid)
        pid=$(cat "$pidfile")
        
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            rm "$pidfile"
        else
            echo "$service_name was not running"
            rm "$pidfile"
        fi
    fi
done

# Also kill any remaining processes on our ports
ports=(1880 5000 5001 8080)
for port in "${ports[@]}"; do
    pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill $pid 2>/dev/null || true
    fi
done

echo "✅ System stopped"
EOF

chmod +x "$PROJECT_ROOT/stop_system.sh"

echo "💡 Pro tip: Run './check_system_status.sh' to verify all services are running"
