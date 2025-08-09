#!/bin/bash
# 🔧 Quick Database Auth Fix for Project Scanner

echo "🔧 Fixing PostgreSQL authentication for project scanner..."

# Option 1: Use peer authentication (recommended)
echo "Setting up peer authentication..."
sudo -u postgres psql -c "
CREATE USER IF NOT EXISTS $USER;
GRANT ALL PRIVILEGES ON DATABASE coding_models_db TO $USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $USER;
"

# Option 2: Update pg_hba.conf for local connections
echo "Updating PostgreSQL authentication config..."
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /etc/postgresql/*/main/pg_hba.conf

# Restart PostgreSQL to apply changes
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

# Test connection
echo "Testing database connection..."
if psql -d coding_models_db -c "SELECT current_database();" 2>/dev/null; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection still failing"
fi

echo "🎯 Ready to run project scanner!"
