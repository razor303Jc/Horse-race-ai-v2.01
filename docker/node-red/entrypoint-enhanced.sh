#!/bin/bash

# 🏇 Horse Racing AI v2.05 - Node-RED Enhanced Entrypoint
# ========================================================
# Builds and deploys flows automatically on container startup

set -e

# Configuration
NODE_RED_USER_DIR="${NODE_RED_USER_DIR:-/data}"
FLOWS_BUILD_DIR="${NODE_RED_USER_DIR}/flows-build"
FLOWS_SOURCE_DIR="${NODE_RED_USER_DIR}/flows-source"
VERSION="v2.05"
BUILD_DATE=$(date +%Y%m%d_%H%M%S)
BUILD_TAG="${VERSION}_${BUILD_DATE}"

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[NODE-RED-ENTRYPOINT]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_build() {
    echo -e "${PURPLE}[FLOW-BUILD]${NC} $1"
}

# Wait for Node-RED to be ready
wait_for_node_red() {
    log_info "Waiting for Node-RED to start..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:1880 > /dev/null 2>&1; then
            log_success "Node-RED is ready!"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Node-RED failed to start within timeout"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for Node-RED..."
        sleep 2
        ((attempt++))
    done
}

# Check if flows source exists
check_flows_source() {
    log_info "Checking for flows source directory..."
    
    if [ -d "$FLOWS_SOURCE_DIR" ] && [ "$(ls -A "$FLOWS_SOURCE_DIR" 2>/dev/null)" ]; then
        log_success "Flows source directory found with $(find "$FLOWS_SOURCE_DIR" -name "*.json" | wc -l) JSON files"
        return 0
    else
        log_warning "No flows source directory found at $FLOWS_SOURCE_DIR"
        log_info "Skipping automatic flow build - using default flows"
        return 1
    fi
}

# Build flows using integrated build script
build_flows() {
    log_build "Starting Horse Racing AI $VERSION flow build process..."
    
    # Create build directory
    mkdir -p "$FLOWS_BUILD_DIR"
    mkdir -p "$FLOWS_BUILD_DIR/main"
    mkdir -p "$FLOWS_BUILD_DIR/subflows"
    mkdir -p "$FLOWS_BUILD_DIR/documentation"
    
    # Function to update flow version in JSON using Node.js
    local update_script="$FLOWS_BUILD_DIR/update_flow_version.js"
    cat > "$update_script" << 'EOF'
const fs = require('fs');

function updateFlowVersion(inputFile, outputFile, flowName, flowType, version, buildTag) {
    try {
        const data = fs.readFileSync(inputFile, 'utf8');
        const flows = JSON.parse(data);
        
        // Update each flow object
        flows.forEach(flow => {
            if (flow.type === 'tab') {
                // Update tab label with version
                const originalLabel = flow.label || '';
                if (!originalLabel.includes(version)) {
                    flow.label = `${originalLabel} ${version}`;
                }
                
                // Add/update info field with build information
                const buildInfo = `Horse Racing AI ${version} - ${flowType}\n` +
                                `Build: ${buildTag}\n` +
                                `Generated: ${new Date().toISOString()}\n` +
                                `Component: ${flowName}`;
                
                if (flow.info) {
                    flow.info = buildInfo + '\n\n' + flow.info;
                } else {
                    flow.info = buildInfo;
                }
            } else if (['subflow', 'function', 'template', 'http in'].includes(flow.type)) {
                // Update names to include version
                if (flow.name && !flow.name.includes(version)) {
                    flow.name = `${flow.name} ${version}`;
                }
                
                // Add version comment to function nodes
                if (flow.type === 'function' && flow.func) {
                    const versionComment = `// Horse Racing AI ${version} - ${flowName}\n// Build: ${buildTag}\n\n`;
                    if (!flow.func.startsWith('//')) {
                        flow.func = versionComment + flow.func;
                    }
                }
                
                // Add version info to template nodes
                if (flow.type === 'template' && flow.template) {
                    if (flow.template.startsWith('<!DOCTYPE html>')) {
                        // HTML template - add version to title
                        flow.template = flow.template.replace(
                            '<title>',
                            `<title>Horse Racing AI ${version} - `
                        );
                        // Add version meta tag
                        const versionMeta = `    <meta name="version" content="${version}">\n    <meta name="build" content="${buildTag}">\n`;
                        flow.template = flow.template.replace(
                            '<meta charset="UTF-8">',
                            `<meta charset="UTF-8">\n${versionMeta}`
                        );
                    }
                }
            }
        });
        
        // Save updated flows
        fs.writeFileSync(outputFile, JSON.stringify(flows, null, 2));
        console.log(`SUCCESS: Updated ${flows.length} flow objects`);
        return true;
        
    } catch (error) {
        console.error(`ERROR: ${error.message}`);
        return false;
    }
}

// Main execution
const [, , inputFile, outputFile, flowName, flowType, version, buildTag] = process.argv;
const success = updateFlowVersion(inputFile, outputFile, flowName, flowType, version, buildTag);
process.exit(success ? 0 : 1);
EOF

    # Build main flow
    log_build "Building main production flow..."
    local main_flow_candidates=(
        "$FLOWS_SOURCE_DIR/flows_c2_enhanced_with_advanced_metrics.json"
        "$FLOWS_SOURCE_DIR/active/production_flows_*.json"
        "$FLOWS_SOURCE_DIR/dashboards/flows_c2_enhanced_with_advanced_metrics.json"
    )
    
    local main_flow_source=""
    for candidate in "${main_flow_candidates[@]}"; do
        # Handle wildcard expansion
        for file in $candidate; do
            if [ -f "$file" ]; then
                main_flow_source="$file"
                break 2
            fi
        done
    done
    
    if [ -n "$main_flow_source" ]; then
        local main_output="$FLOWS_BUILD_DIR/main/horse_racing_ai_main_flow_${BUILD_TAG}.json"
        
        if node "$update_script" "$main_flow_source" "$main_output" "Main Production Flow" "Primary Dashboard" "$VERSION" "$BUILD_TAG"; then
            log_success "Main flow built: $(basename "$main_output")"
            
            # Set as current flows.json for Node-RED
            cp "$main_output" "$NODE_RED_USER_DIR/flows.json"
            log_success "Main flow deployed as current flows.json"
        else
            log_error "Failed to build main flow"
            return 1
        fi
    else
        log_warning "No suitable main flow source found"
    fi
    
    # Build subflows
    log_build "Building specialized subflows..."
    
    local subflow_mappings=(
        "pipeline/database_config_flows.json:database_config_subflow:Database Configuration:Subflow"
        "pipeline/pipeline_automation_flows.json:pipeline_automation_subflow:Pipeline Automation:Subflow" 
        "pipeline/flows_redis_health_fixed.json:health_monitoring_subflow:Health Monitoring:Subflow"
        "dashboards/flows_advanced_metrics_dashboard.json:advanced_metrics_subflow:Advanced Metrics:Subflow"
        "c2-variants/c2_enhanced_flows.json:c2_command_variants_subflow:C2 Command Variants:Subflow"
        "testing/test_flows.json:testing_development_subflow:Testing & Development:Subflow"
    )
    
    for mapping in "${subflow_mappings[@]}"; do
        IFS=':' read -r source_path output_name flow_name flow_type <<< "$mapping"
        local source_file="$FLOWS_SOURCE_DIR/$source_path"
        local output_file="$FLOWS_BUILD_DIR/subflows/${output_name}_${BUILD_TAG}.json"
        
        if [ -f "$source_file" ]; then
            if node "$update_script" "$source_file" "$output_file" "$flow_name" "$flow_type" "$VERSION" "$BUILD_TAG"; then
                log_success "Built subflow: $(basename "$output_file")"
            else
                log_warning "Failed to build subflow: $output_name"
            fi
        else
            log_warning "Source not found for subflow: $source_path"
        fi
    done
    
    # Create build documentation
    cat > "$FLOWS_BUILD_DIR/BUILD_INFO_${BUILD_TAG}.md" << EOF
# 🏇 Horse Racing AI $VERSION - Container Build

**Build Tag:** $BUILD_TAG  
**Build Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Container:** Node-RED Enhanced  
**Environment:** Docker Container

## 📦 Build Results

- **Main Flow:** \`main/horse_racing_ai_main_flow_${BUILD_TAG}.json\`
- **Subflows:** $(ls "$FLOWS_BUILD_DIR/subflows"/*.json 2>/dev/null | wc -l) specialized subflows
- **Deployment:** Main flow deployed as current flows.json

## 🚀 Automatic Deployment

The main production flow has been automatically deployed to Node-RED.
Access the dashboard at: http://localhost:1880/c2

## 📊 Flow Statistics

- **Source Files Processed:** $(find "$FLOWS_SOURCE_DIR" -name "*.json" 2>/dev/null | wc -l)
- **Build Files Created:** $(find "$FLOWS_BUILD_DIR" -name "*.json" 2>/dev/null | wc -l)
- **Version Applied:** $VERSION with build tag $BUILD_TAG

Built automatically by Node-RED Enhanced Container.
EOF

    # Clean up temporary files
    rm -f "$update_script"
    
    log_success "Flow build process completed"
}

# Install required Node-RED packages if not present
install_node_red_packages() {
    log_info "Checking Node-RED package dependencies..."
    
    local required_packages=(
        "node-red-dashboard"
        "node-red-contrib-postgres"
        "node-red-contrib-moment"
        "node-red-contrib-cron-plus"
        "node-red-node-email"
        "node-red-contrib-fs-ops"
    )
    
    for package in "${required_packages[@]}"; do
        if [ ! -d "$NODE_RED_USER_DIR/node_modules/$package" ]; then
            log_info "Installing missing package: $package"
            cd "$NODE_RED_USER_DIR"
            npm install "$package" --silent
        fi
    done
    
    log_success "All required packages are available"
}

# Deploy flows to running Node-RED instance
deploy_flows() {
    log_info "Deploying flows to Node-RED..."
    
    # Wait a moment for Node-RED to fully initialize
    sleep 5
    
    # Trigger a deployment
    if curl -X POST "http://localhost:1880/flows" \
        -H "Content-Type: application/json" \
        -d '{"deploy":"full"}' \
        --silent --show-error; then
        log_success "Flows deployed successfully"
    else
        log_warning "Flow deployment may have issues - check Node-RED logs"
    fi
}

# Validate deployment
validate_deployment() {
    log_info "Validating deployment..."
    
    # Wait for flows to be ready
    sleep 10
    
    # Test main dashboard endpoint
    if curl -s "http://localhost:1880/c2" > /dev/null; then
        log_success "Main dashboard is accessible at /c2"
    else
        log_warning "Main dashboard validation failed"
    fi
    
    # Test status endpoint
    if curl -s "http://localhost:1880/c2/status" > /dev/null; then
        log_success "Status API is accessible at /c2/status"
    else
        log_warning "Status API validation failed"
    fi
}

# Main entrypoint execution
main() {
    log_info "🏇 Horse Racing AI $VERSION - Node-RED Enhanced Container Starting..."
    log_info "User Directory: $NODE_RED_USER_DIR"
    log_info "Build Tag: $BUILD_TAG"
    
    # Start Node-RED in background
    log_info "Starting Node-RED..."
    cd /usr/src/node-red
    npm start --cache /data/.npm -- --userDir /data &
    NODE_RED_PID=$!
    
    # Wait for Node-RED to be ready
    if wait_for_node_red; then
        # Install required packages
        install_node_red_packages
        
        # Check if we should build flows
        if check_flows_source; then
            # Build and deploy flows
            build_flows
            deploy_flows
            validate_deployment
        else
            log_info "Using default Node-RED flows"
        fi
        
        log_success "🎉 Horse Racing AI $VERSION container ready!"
        log_info "🌐 Access dashboard: http://localhost:1880/c2"
        log_info "⚙️ Node-RED editor: http://localhost:1880"
    else
        log_error "Failed to initialize Node-RED"
        exit 1
    fi
    
    # Wait for Node-RED process
    wait $NODE_RED_PID
}

# Execute main function
main "$@"
