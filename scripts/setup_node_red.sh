#!/bin/bash

# Node-RED Setup Script for Horse Racing AI Automation
# This script sets up Node-RED with all required dependencies

echo "🏇 Setting up Node-RED for Horse Racing AI Automation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running ✓"

# Create Node-RED directory structure
print_status "Creating Node-RED directory structure..."
mkdir -p node-red/data
mkdir -p node-red/flows
mkdir -p logs/node-red

# Set permissions
chmod 755 node-red
chmod 755 node-red/data
chmod 755 node-red/flows

print_success "Directory structure created"

# Copy starter flows if they don't exist
if [ ! -f "node-red/data/flows.json" ]; then
    print_status "Copying starter flows..."
    cp node-red/flows-starter.json node-red/data/flows.json
    print_success "Starter flows copied"
fi

# Stop existing Node-RED container if running
if docker ps -q -f name=horse_racing_node_red | grep -q .; then
    print_warning "Stopping existing Node-RED container..."
    docker stop horse_racing_node_red
    docker rm horse_racing_node_red
fi

# Start Node-RED with the new configuration
print_status "Starting Node-RED container..."

docker run -d \
    --name horse_racing_node_red \
    --restart unless-stopped \
    -p 1881:1880 \
    -v "$(pwd)/node-red/data:/data" \
    -v "$(pwd):/workspace:ro" \
    -v "$(pwd)/data:/workspace/data" \
    -v "$(pwd)/logs:/workspace/logs" \
    -v "$(pwd)/temp_extract:/workspace/temp_extract" \
    -v "$(pwd)/temp_card_processing:/workspace/temp_card_processing" \
    -v "$(pwd)/tools:/workspace/tools:ro" \
    -v "$(pwd)/scripts:/workspace/scripts:ro" \
    -e TZ=UTC \
    -e NODE_RED_ENABLE_PROJECTS=true \
    --network horse_racing_network \
    nodered/node-red:latest

# Wait for Node-RED to start
print_status "Waiting for Node-RED to start..."
sleep 10

# Check if Node-RED is running
if docker ps -q -f name=horse_racing_node_red | grep -q .; then
    print_success "Node-RED is running!"
    
    # Install required nodes
    print_status "Installing required Node-RED nodes..."
    
    # List of essential nodes to install
    nodes=(
        "node-red-dashboard"
        "node-red-node-cron-plus"
        "node-red-node-email"
        "node-red-contrib-postgres"
        "node-red-contrib-fs-ops"
        "node-red-contrib-moment"
        "node-red-contrib-csv"
    )
    
    for node in "${nodes[@]}"; do
        print_status "Installing $node..."
        docker exec horse_racing_node_red npm install $node
    done
    
    print_success "Node installation complete!"
    
    # Restart Node-RED to load new nodes
    print_status "Restarting Node-RED to load new nodes..."
    docker restart horse_racing_node_red
    sleep 5
    
    print_success "Setup complete!"
    echo ""
    echo "🎯 Node-RED is now running!"
    echo "📊 Access the editor at: http://localhost:1881"
    echo "📈 Access the dashboard at: http://localhost:1881/ui"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Open http://localhost:1881 in your browser"
    echo "2. Import the starter flows from the flows-starter.json"
    echo "3. Configure email settings for alerts"
    echo "4. Set up database connections"
    echo "5. Test the automation flows"
    echo ""
    echo "📋 Available Features:"
    echo "- ⏰ Scheduled data downloads (6 AM & 10 PM)"
    echo "- 🧹 Automatic CSV cleaning"
    echo "- 💾 Database import automation"
    echo "- 🤖 AI prediction generation"
    echo "- 📧 Email alerts for failures"
    echo "- 📊 Real-time dashboard"
    echo ""
    
else
    print_error "Failed to start Node-RED container"
    docker logs horse_racing_node_red
    exit 1
fi

# Show container status
echo "📋 Container Status:"
docker ps -f name=horse_racing_node_red --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
print_success "Node-RED Horse Racing AI Automation setup complete! 🏇"
