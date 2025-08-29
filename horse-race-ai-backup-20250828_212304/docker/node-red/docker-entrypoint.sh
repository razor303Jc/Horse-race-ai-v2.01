#!/bin/bash
set -e

echo "🏇 Starting Horse Racing AI Node-RED Container..."

# Set Node-RED data directory
export NODE_RED_DATA_DIR=/data

# Ensure data directory exists and has correct permissions
mkdir -p $NODE_RED_DATA_DIR
chown -R node-red:node-red $NODE_RED_DATA_DIR

# Install additional npm packages if package.json exists
if [ -f "$NODE_RED_DATA_DIR/package.json" ]; then
    echo "📦 Installing additional npm packages from package.json..."
    cd $NODE_RED_DATA_DIR
    npm install --production
fi

#!/bin/bash
set -e

echo "🏇 Starting Horse Racing AI Node-RED Container..."

# Start Node-RED with the default entrypoint
echo "🚀 Starting Node-RED..."
exec /usr/src/node-red/entrypoint.sh
