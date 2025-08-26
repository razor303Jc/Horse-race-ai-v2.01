#!/bin/bash
# Web App Entrypoint Script
# =========================
# 
# This script:
# 1. Builds the React frontend if needed
# 2. Starts the FastAPI server
# 3. Handles graceful shutdown

set -e

echo "🏇 Horse Racing AI Web App - Starting..."
echo "=========================================="

# Check if we're in the correct directory
if [ ! -f "src/web/api_server_enhanced.py" ]; then
    echo "❌ Error: api_server_enhanced.py not found"
    echo "Current directory: $(pwd)"
    echo "Contents: $(ls -la)"
    exit 1
fi

# Function for graceful shutdown
cleanup() {
    echo "🛑 Shutting down web app gracefully..."
    kill -TERM "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
    echo "✅ Web app stopped"
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGTERM SIGINT

# Check if React build exists and is recent
REACT_BUILD_DIR="/app/src/web/dist"
REACT_SRC_DIR="/app/src/web/src"
PACKAGE_JSON="/app/src/web/package.json"

echo "📋 Checking React build status..."

NEED_BUILD=false

# Check if build directory exists
if [ ! -d "$REACT_BUILD_DIR" ]; then
    echo "🔄 No React build found - building from scratch"
    NEED_BUILD=true
elif [ ! -f "$REACT_BUILD_DIR/index.html" ]; then
    echo "🔄 Incomplete React build - rebuilding"
    NEED_BUILD=true
elif [ -d "$REACT_SRC_DIR" ] && [ "$(find $REACT_SRC_DIR -newer $REACT_BUILD_DIR/index.html | wc -l)" -gt 0 ]; then
    echo "🔄 React source files newer than build - rebuilding"
    NEED_BUILD=true
else
    echo "✅ React build is up to date"
fi

# Build React app if needed
if [ "$NEED_BUILD" = true ]; then
    echo "🔨 Building React application..."
    cd /app/src/web
    
    # Check if package.json exists
    if [ ! -f "$PACKAGE_JSON" ]; then
        echo "❌ Error: package.json not found in /app/src/web"
        exit 1
    fi
    
    # Install dependencies with legacy peer deps to resolve conflicts
    echo "📦 Installing npm dependencies..."
    if NODE_ENV=development npm install --legacy-peer-deps --include=dev; then
        echo "✅ npm install completed"
    else
        echo "❌ npm install failed - continuing with API only"
        BUILD_SUCCESS=false
        cd /app
        # Skip build process and go to API startup
    fi
    
    # Only proceed with build if npm install succeeded
    if [ "$BUILD_SUCCESS" != false ]; then
        # Verify critical packages are available
        echo "🔍 Verifying build tools..."
        if npx vite --version >/dev/null 2>&1; then
            echo "✅ Vite available"
        else
            echo "⚠️ Vite not found, installing..."
            npm install vite@^5.0.0 --save-dev --legacy-peer-deps
        fi
        
        # Build the app
        echo "⚙️  Building React app..."
        if npm run build; then
            echo "✅ React build completed successfully"
            BUILD_SUCCESS=true
        else
            echo "❌ React build failed - continuing with API only"
            BUILD_SUCCESS=false
        fi
    fi
    
    # Verify build was created
    if [ "$BUILD_SUCCESS" = true ] && [ -f "$REACT_BUILD_DIR/index.html" ]; then
        echo "✅ React build verified - index.html exists"
        echo "📊 Build size: $(du -sh $REACT_BUILD_DIR | cut -f1)"
    elif [ "$BUILD_SUCCESS" = false ]; then
        echo "⚠️ Continuing without React build - API only mode"
    else
        echo "❌ React build verification failed - no index.html"
        echo "⚠️ Continuing in API-only mode"
    fi
    
    cd /app
else
    echo "⏭️  Skipping React build - already up to date"
fi

# Wait for database to be ready
echo "🗄️  Waiting for database connection..."
DB_HOST=${DATABASE_HOST:-postgres}
DB_PORT=${DATABASE_PORT:-5432}
DB_USER=${DATABASE_USER:-horse_racing}
DB_NAME=${DATABASE_NAME:-cards_horse_racing_db}

# Wait up to 60 seconds for database
for i in $(seq 1 60); do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
        echo "✅ Database connection established"
        break
    fi
    
    if [ $i -eq 60 ]; then
        echo "❌ Database connection timeout after 60 seconds"
        echo "🔍 Database details:"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT" 
        echo "  User: $DB_USER"
        echo "  Database: $DB_NAME"
        exit 1
    fi
    
    echo "⏳ Waiting for database... ($i/60)"
    sleep 1
done

# Wait for Redis to be ready
echo "🔴 Waiting for Redis connection..."
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

for i in $(seq 1 30); do
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        echo "✅ Redis connection established"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Redis connection timeout after 30 seconds"
        echo "🔍 Redis details:"
        echo "  Host: $REDIS_HOST"
        echo "  Port: $REDIS_PORT"
        exit 1
    fi
    
    echo "⏳ Waiting for Redis... ($i/30)"
    sleep 1
done

# Set environment variables for the API server
export PYTHONPATH=/app
export DATABASE_URL="postgresql://${DB_USER}:${POSTGRES_PASSWORD:-secure_password_123}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
export REDIS_URL="redis://:${REDIS_PASSWORD:-redis_password_123}@${REDIS_HOST}:${REDIS_PORT}/0"

echo "🌐 Starting API server..."
echo "📍 API will be available on port 8000"
echo "📍 Web UI will be available on port 3000 (via proxy)"
echo "🔧 Environment:"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  DATABASE_URL: postgresql://${DB_USER}:***@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "  REDIS_URL: redis://***@${REDIS_HOST}:${REDIS_PORT}/0"

# Start the API server in the background
python src/web/api_server_enhanced.py &
API_PID=$!

echo "🚀 Web app started successfully!"
echo "📊 Process ID: $API_PID"
echo "💡 Use docker logs to monitor the application"

# Wait for the API server process
wait "$API_PID"
