#!/bin/bash
# Qwen2.5 Auto-Updater Setup Script
# Quick setup for the Qwen auto-updater system

set -e

echo "🚀 Setting up Qwen2.5 Auto-Updater System..."

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

# Check if running from correct directory
if [ ! -f "qwen_auto_updater.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama not found in PATH. The auto-updater will install it in the container."
fi

print_success "Prerequisites check passed"

# Create necessary directories
print_status "Creating directories..."
mkdir -p {config,logs,backups/{models,database},temp/downloads}
print_success "Directories created"

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install pyyaml schedule psycopg2-binary requests
fi

# Install additional dependencies for auto-updater
pip install schedule pyyaml psycopg2-binary requests chardet numpy pandas

print_success "Python dependencies installed"

# Setup Docker environment
print_status "Setting up Docker environment..."
python qwen_docker_updater.py setup

if [ $? -eq 0 ]; then
    print_success "Docker environment setup completed"
else
    print_error "Docker environment setup failed"
    exit 1
fi

# Create systemd service (optional)
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /tmp/qwen-auto-updater.service << EOF
[Unit]
Description=Qwen2.5 Auto-Updater Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/qwen_auto_updater.py daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    if [ "$EUID" -eq 0 ]; then
        cp /tmp/qwen-auto-updater.service /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable qwen-auto-updater.service
        print_success "Systemd service created and enabled"
        print_status "Start with: sudo systemctl start qwen-auto-updater"
    else
        print_warning "Not running as root. Systemd service file created at /tmp/qwen-auto-updater.service"
        print_status "To install: sudo cp /tmp/qwen-auto-updater.service /etc/systemd/system/"
        print_status "Then: sudo systemctl daemon-reload && sudo systemctl enable qwen-auto-updater"
    fi
}

# Ask if user wants systemd service
read -p "Do you want to create a systemd service? (y/N): " create_service
if [[ $create_service =~ ^[Yy]$ ]]; then
    create_systemd_service
fi

# Test the installation
print_status "Testing installation..."

# Test Qwen model check
print_status "Testing Qwen model check..."
python qwen_auto_updater.py check-model

if [ $? -eq 0 ]; then
    print_success "Qwen model check working"
else
    print_warning "Qwen model check had issues (this may be normal if Qwen is not yet installed)"
fi

# Test database check
print_status "Testing database check..."
python qwen_auto_updater.py check-db

if [ $? -eq 0 ]; then
    print_success "Database check working"
else
    print_warning "Database check had issues (check your database configuration)"
fi

print_success "🎉 Qwen2.5 Auto-Updater setup completed!"

echo ""
echo "📋 Next Steps:"
echo "1. Review configuration: config/qwen_updater_config.yaml"
echo "2. Check status: python qwen_auto_updater.py status"
echo "3. Start daemon: python qwen_auto_updater.py daemon"
echo "4. Or use Docker: python qwen_docker_updater.py start"
echo ""
echo "📖 Usage Examples:"
echo "   python qwen_auto_updater.py check-model    # Check for model updates"
echo "   python qwen_auto_updater.py update-model   # Update model"
echo "   python qwen_auto_updater.py check-db       # Check database"
echo "   python qwen_auto_updater.py update-db      # Update database"
echo "   python qwen_auto_updater.py daemon         # Run as daemon"
echo ""
echo "🐳 Docker Commands:"
echo "   python qwen_docker_updater.py status       # Check Docker service"
echo "   python qwen_docker_updater.py logs         # View logs"
echo "   python qwen_docker_updater.py restart      # Restart service"
echo ""
echo "✅ Setup complete! Your Qwen2.5 auto-updater is ready to use."
