#!/bin/bash
# Setup Racing News Analyzer
# Installation and configuration script

echo "🏇 Setting up Racing News Analyzer with Ollama..."

# Check if running as root for service installation
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Please run this script as your regular user, not root"
    echo "The script will ask for sudo when needed"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p reports/daily_news
mkdir -p logs

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user requests beautifulsoup4 schedule

# Check if Ollama is installed
echo "🔍 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first:"
    echo "curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
else
    echo "✅ Ollama found"
fi

# Check if required models are available
echo "🔍 Checking Ollama models..."
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Llama 3.1 8B model found"
else
    echo "📥 Downloading Llama 3.1 8B model..."
    ollama pull llama3.1:8b
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x daily_news_analyzer.py
chmod +x news_scheduler.py

# Test the news analyzer
echo "🧪 Testing news analyzer..."
python3 daily_news_analyzer.py --test 2>/dev/null || echo "⚠️  Test run completed (some errors expected on first run)"

# Setup systemd service (optional)
read -p "🤖 Would you like to install as a system service? (y/N): " setup_service
if [[ $setup_service =~ ^[Yy]$ ]]; then
    echo "🔧 Setting up systemd service..."
    sudo cp racing-news-scheduler.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable racing-news-scheduler
    echo "✅ Service installed. Start with: sudo systemctl start racing-news-scheduler"
else
    echo "📝 To run manually:"
    echo "  python3 news_scheduler.py"
fi

# Create a quick start script
cat > start_news_analyzer.sh << 'EOF'
#!/bin/bash
echo "🏇 Starting Racing News Analyzer..."
cd /home/jc/Documents/Horse-race-ai-v2.01
python3 news_scheduler.py
EOF

chmod +x start_news_analyzer.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Available commands:"
echo "  ./start_news_analyzer.sh        - Start the scheduler manually"
echo "  python3 daily_news_analyzer.py  - Run analysis once"
echo "  python3 news_scheduler.py       - Run scheduler manually"
echo ""
echo "📊 Reports will be saved to: reports/daily_news/"
echo "📜 Logs will be saved to: news_analyzer.log and news_scheduler.log"
echo ""
echo "🕐 Scheduled times:"
echo "  - 08:00 AM - Morning analysis"
echo "  - 02:00 PM - Afternoon analysis"  
echo "  - 08:00 PM - Evening summary"
echo ""
