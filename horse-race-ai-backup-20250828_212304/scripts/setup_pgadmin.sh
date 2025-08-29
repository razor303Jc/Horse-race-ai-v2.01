#!/bin/bash

# pgAdmin Docker Container Setup Script
# Sets up proper permissions for pgAdmin configuration files

echo "Setting up pgAdmin configuration permissions..."

# Create pgAdmin data directory if it doesn't exist
sudo mkdir -p ./data/pgadmin

# Set proper ownership for pgAdmin data directory
sudo chown -R 5050:5050 ./data/pgadmin

# Set proper permissions for configuration files
chmod 600 ./config/pgadmin/pgpass
chmod 644 ./config/pgadmin/servers.json
chmod 644 ./config/pgadmin/config_local.py

# Create storage directories
mkdir -p ./data/pgadmin/storage
mkdir -p ./data/pgadmin/sessions
mkdir -p ./data/pgadmin/upload

echo "pgAdmin permissions setup complete!"
echo ""
echo "You can now access pgAdmin at:"
echo "- Direct: http://localhost:8083"
echo "- Via Traefik: http://pgadmin.localhost"
echo ""
echo "Login credentials:"
echo "- Email: admin@horseracing.com"
echo "- Password: admin_password_123 (or your PGADMIN_PASSWORD env var)"
echo ""
echo "Pre-configured database connections:"
echo "- Horse Racing PostgreSQL (main server)"
echo "- Cards Database (cards_horse_racing_db)"
echo "- Results Database (results_horse_racing_db)"
echo "- Advanced Metrics Database (advanced_racing_metrics_db)"
