#!/bin/bash

# 🚀 EXEC NODE DEPLOYMENT SCRIPT
# Deploys pipeline automation flows to Node-RED

echo "🏇 Horse Racing AI - Exec Node Deployment"
echo "=========================================="

# Configuration
NODE_RED_HOST="localhost:1880"
NODE_RED_ADMIN_AUTH=""  # Add authentication if enabled
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Color codes for output
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

# Check if Node-RED is running
check_node_red() {
    print_status "Checking Node-RED connectivity..."
    
    if curl -s "http://${NODE_RED_HOST}" > /dev/null; then
        print_success "Node-RED is accessible at http://${NODE_RED_HOST}"
        return 0
    else
        print_error "Cannot connect to Node-RED at http://${NODE_RED_HOST}"
        print_warning "Please ensure Node-RED is running with: docker-compose up node-red"
        return 1
    fi
}

# Backup existing flows
backup_flows() {
    print_status "Creating backup of existing flows..."
    
    if curl -s "http://${NODE_RED_HOST}/flows" -o "backup_flows_${TIMESTAMP}.json"; then
        print_success "Existing flows backed up to: backup_flows_${TIMESTAMP}.json"
        return 0
    else
        print_warning "Could not create backup (Node-RED may be empty)"
        return 0
    fi
}

# Deploy pipeline automation flows
deploy_pipeline_flows() {
    print_status "Deploying pipeline automation flows..."
    
    if [ ! -f "pipeline_automation_flows.json" ]; then
        print_error "pipeline_automation_flows.json not found!"
        return 1
    fi
    
    # Import flows using Node-RED Admin API
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d @pipeline_automation_flows.json \
        "http://${NODE_RED_HOST}/flow")
    
    if echo "$response" | grep -q "id"; then
        print_success "Pipeline automation flows deployed successfully"
        return 0
    else
        print_error "Failed to deploy pipeline flows: $response"
        return 1
    fi
}

# Deploy enhanced C2 dashboard
deploy_c2_flows() {
    print_status "Deploying enhanced C2 dashboard..."
    
    if [ ! -f "c2_enhanced_flows.json" ]; then
        print_error "c2_enhanced_flows.json not found!"
        return 1
    fi
    
    # Import enhanced C2 flows
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d @c2_enhanced_flows.json \
        "http://${NODE_RED_HOST}/flow")
    
    if echo "$response" | grep -q "id"; then
        print_success "Enhanced C2 dashboard deployed successfully"
        return 0
    else
        print_error "Failed to deploy C2 dashboard: $response"
        return 1
    fi
}

# Restart Node-RED flows
restart_flows() {
    print_status "Restarting Node-RED flows..."
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"type":"full"}' \
        "http://${NODE_RED_HOST}/flows")
    
    if [ $? -eq 0 ]; then
        print_success "Node-RED flows restarted successfully"
        return 0
    else
        print_error "Failed to restart flows"
        return 1
    fi
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Check C2 dashboard
    if curl -s "http://${NODE_RED_HOST}/c2" | grep -q "Pipeline Automation"; then
        print_success "✅ C2 Dashboard accessible with pipeline controls"
    else
        print_warning "⚠️ C2 Dashboard may not be fully loaded"
    fi
    
    # Check pipeline API endpoints
    if curl -s "http://${NODE_RED_HOST}/api/pipeline/status" | grep -q "success"; then
        print_success "✅ Pipeline API endpoints responding"
    else
        print_warning "⚠️ Pipeline API endpoints may not be active"
    fi
    
    print_success "🎉 Deployment verification complete!"
}

# Main deployment process
main() {
    echo
    print_status "Starting exec node deployment process..."
    echo
    
    # Step 1: Check Node-RED connectivity
    if ! check_node_red; then
        exit 1
    fi
    
    echo
    
    # Step 2: Backup existing flows
    backup_flows
    
    echo
    
    # Step 3: Deploy pipeline automation flows
    if ! deploy_pipeline_flows; then
        print_error "Pipeline deployment failed!"
        exit 1
    fi
    
    echo
    
    # Step 4: Deploy enhanced C2 dashboard
    if ! deploy_c2_flows; then
        print_error "C2 dashboard deployment failed!"
        exit 1
    fi
    
    echo
    
    # Step 5: Restart flows
    sleep 2  # Allow time for flows to be processed
    restart_flows
    
    echo
    
    # Step 6: Verify deployment
    sleep 3  # Allow time for restart
    verify_deployment
    
    echo
    print_success "🏇 EXEC NODE DEPLOYMENT COMPLETE!"
    echo
    print_status "Access your enhanced C2 dashboard at: http://${NODE_RED_HOST}/c2"
    print_status "Access Node-RED editor at: http://${NODE_RED_HOST}/admin"
    echo
    print_status "Available API endpoints:"
    print_status "  - POST http://${NODE_RED_HOST}/api/pipeline/manual-trigger"
    print_status "  - GET  http://${NODE_RED_HOST}/api/pipeline/status"
    echo
    print_status "Ready to automate Python pipeline scripts! 🚀"
}

# Handle script arguments
case "${1:-}" in
    "backup")
        check_node_red && backup_flows
        ;;
    "pipeline")
        check_node_red && deploy_pipeline_flows
        ;;
    "c2")
        check_node_red && deploy_c2_flows
        ;;
    "verify")
        verify_deployment
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [backup|pipeline|c2|verify|help]"
        echo ""
        echo "Commands:"
        echo "  backup   - Backup existing flows only"
        echo "  pipeline - Deploy pipeline automation flows only"
        echo "  c2       - Deploy C2 dashboard only"
        echo "  verify   - Verify deployment only"
        echo "  help     - Show this help message"
        echo ""
        echo "Run without arguments to perform full deployment"
        ;;
    *)
        main
        ;;
esac
