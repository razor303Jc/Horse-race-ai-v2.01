#!/usr/bin/env python3
"""
Production Web Dashboard Deployment
===================================

Production-ready deployment configuration for the strategy monitoring dashboard.
Includes WSGI setup, reverse proxy configuration, and production optimizations.

Features:
- WSGI production server setup
- Nginx reverse proxy configuration
- SSL/HTTPS configuration
- Environment-based configuration
- Logging and monitoring
- Auto-restart and health checks

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask
import gunicorn.app.base

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.monitoring.dashboard_app import app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Standalone Gunicorn application for production deployment"""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_production_config():
    """Create production configuration files"""

    # 1. Gunicorn configuration
    gunicorn_config = """
# Gunicorn configuration for Horse Racing AI Dashboard
# /etc/horse-racing-ai/gunicorn.conf.py

import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "/var/log/horse-racing-ai/access.log"
errorlog = "/var/log/horse-racing-ai/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "horse_racing_ai_dashboard"

# Daemon
daemon = False
pidfile = "/var/run/horse-racing-ai/dashboard.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if using Gunicorn SSL instead of Nginx)
# keyfile = "/etc/ssl/private/horse-racing-ai.key"
# certfile = "/etc/ssl/certs/horse-racing-ai.crt"
"""

    # 2. Nginx configuration
    nginx_config = """
# Nginx configuration for Horse Racing AI Dashboard
# /etc/nginx/sites-available/horse-racing-ai

upstream horse_racing_ai {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/horse-racing-ai.crt;
    ssl_certificate_key /etc/ssl/private/horse-racing-ai.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/x-javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=dashboard:10m rate=10r/s;
    limit_req zone=dashboard burst=20 nodelay;
    
    # Main location
    location / {
        proxy_pass http://horse_racing_ai;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # WebSocket support for real-time updates
    location /ws/ {
        proxy_pass http://horse_racing_ai;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/horse-racing-ai/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://horse_racing_ai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://horse_racing_ai/health;
    }
}
"""

    # 3. Systemd service file
    systemd_service = """
# Systemd service for Horse Racing AI Dashboard
# /etc/systemd/system/horse-racing-ai-dashboard.service

[Unit]
Description=Horse Racing AI Strategy Dashboard
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/horse-racing-ai
Environment=FLASK_ENV=production
Environment=PYTHONPATH=/var/www/horse-racing-ai
ExecStart=/usr/local/bin/gunicorn --config /etc/horse-racing-ai/gunicorn.conf.py production_dashboard:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    # 4. Environment configuration
    env_config = """
# Environment configuration for production
# /etc/horse-racing-ai/environment

# Flask settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here

# Database settings
DATABASE_URL=sqlite:///var/lib/horse-racing-ai/live_strategy_monitoring.db
BACKUP_DATABASE_URL=sqlite:///var/backup/horse-racing-ai/live_strategy_monitoring_backup.db

# API Keys
RACE_DATA_API_KEY=your-race-data-api-key
BETFAIR_APP_KEY=your-betfair-app-key
BETFAIR_USERNAME=your-betfair-username
BETFAIR_PASSWORD=your-betfair-password

# Email settings for alerts
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# SMS settings for alerts
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Monitoring settings
ENABLE_REAL_TIME_MONITORING=True
MONITORING_INTERVAL=30
MAX_DAILY_STAKE=200
MAX_SINGLE_STAKE=50

# Security settings
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
"""

    # 5. Deployment script
    deployment_script = """#!/bin/bash
# Production deployment script for Horse Racing AI Dashboard
# deploy.sh

set -e

echo "Starting Horse Racing AI Dashboard deployment..."

# Configuration
APP_DIR="/var/www/horse-racing-ai"
BACKUP_DIR="/var/backup/horse-racing-ai"
LOG_DIR="/var/log/horse-racing-ai"
CONFIG_DIR="/etc/horse-racing-ai"

# Create directories
sudo mkdir -p $APP_DIR
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p $CONFIG_DIR

# Copy application files
echo "Copying application files..."
sudo cp -r /home/jc/Documents/Horse-race-ai-v2.03/* $APP_DIR/
sudo chown -R www-data:www-data $APP_DIR

# Install Python dependencies
echo "Installing Python dependencies..."
cd $APP_DIR
sudo -u www-data python3 -m pip install --user -r requirements.txt

# Copy configuration files
echo "Setting up configuration..."
sudo cp configs/gunicorn.conf.py $CONFIG_DIR/
sudo cp configs/environment $CONFIG_DIR/
sudo chmod 600 $CONFIG_DIR/environment

# Set up Nginx
echo "Configuring Nginx..."
sudo cp configs/nginx-horse-racing-ai /etc/nginx/sites-available/horse-racing-ai
sudo ln -sf /etc/nginx/sites-available/horse-racing-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up systemd service
echo "Setting up systemd service..."
sudo cp configs/horse-racing-ai-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable horse-racing-ai-dashboard

# Set up log rotation
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/horse-racing-ai > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload horse-racing-ai-dashboard
    endscript
}
EOF

# Set up database backup
echo "Setting up database backup..."
sudo tee /etc/cron.d/horse-racing-ai-backup > /dev/null <<EOF
# Backup database every 6 hours
0 */6 * * * www-data cp /var/lib/horse-racing-ai/live_strategy_monitoring.db $BACKUP_DIR/live_strategy_monitoring_\$(date +\\%Y\\%m\\%d_\\%H\\%M).db

# Clean old backups (keep 7 days)
0 2 * * * www-data find $BACKUP_DIR -name "*.db" -mtime +7 -delete
EOF

# Start the service
echo "Starting Horse Racing AI Dashboard service..."
sudo systemctl start horse-racing-ai-dashboard
sudo systemctl status horse-racing-ai-dashboard

# Set up SSL certificate (Let's Encrypt)
echo "Setting up SSL certificate..."
if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d your-domain.com -d www.your-domain.com
else
    echo "Certbot not found. Please install certbot and run:"
    echo "sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
fi

# Set up monitoring
echo "Setting up monitoring..."
sudo tee /etc/systemd/system/horse-racing-ai-monitor.service > /dev/null <<EOF
[Unit]
Description=Horse Racing AI System Monitor
After=horse-racing-ai-dashboard.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR
Environment=PYTHONPATH=$APP_DIR
ExecStart=/usr/bin/python3 scripts/complete_live_integration.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable horse-racing-ai-monitor
sudo systemctl start horse-racing-ai-monitor

echo "Deployment completed successfully!"
echo "Dashboard available at: https://your-domain.com"
echo "Check service status: sudo systemctl status horse-racing-ai-dashboard"
echo "Check logs: sudo journalctl -u horse-racing-ai-dashboard -f"
"""

    # Write all configuration files
    configs = {
        "configs/gunicorn.conf.py": gunicorn_config,
        "configs/nginx-horse-racing-ai": nginx_config,
        "configs/horse-racing-ai-dashboard.service": systemd_service,
        "configs/environment": env_config,
        "deploy.sh": deployment_script,
    }

    for filepath, content in configs.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content.strip())

    # Make deployment script executable
    os.chmod("deploy.sh", 0o755)

    print("Production deployment configuration created:")
    for filepath in configs.keys():
        print(f"  - {filepath}")


def run_production_server():
    """Run the dashboard in production mode using Gunicorn"""

    # Production configuration
    options = {
        "bind": "127.0.0.1:5000",
        "workers": 4,
        "worker_class": "sync",
        "timeout": 30,
        "keepalive": 2,
        "max_requests": 1000,
        "preload_app": True,
        "accesslog": "logs/access.log",
        "errorlog": "logs/error.log",
        "loglevel": "info",
        "capture_output": True,
    }

    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)

    # Configure Flask for production
    app.config.update(
        {
            "ENV": "production",
            "DEBUG": False,
            "TESTING": False,
            "SECRET_KEY": os.environ.get(
                "SECRET_KEY", "production-secret-key-change-me"
            ),
        }
    )

    # Start Gunicorn server
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create-config":
        create_production_config()
        print("\nNext steps for deployment:")
        print("1. Edit configs/environment with your actual API keys and settings")
        print("2. Update configs/nginx-horse-racing-ai with your domain name")
        print("3. Run: chmod +x deploy.sh && sudo ./deploy.sh")
        print("4. Configure your domain DNS to point to your server")
        print("5. The dashboard will be available at https://your-domain.com")
    else:
        # Run production server
        run_production_server()
