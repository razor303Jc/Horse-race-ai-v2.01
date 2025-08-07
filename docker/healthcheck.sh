#!/bin/bash
# Health check script for Horse Racing AI containers

set -e

# Check if the application is running
if [ "$1" = "web" ]; then
    # Check web application
    curl -f http://localhost:5002/health || exit 1
elif [ "$1" = "api" ]; then
    # Check API endpoints
    curl -f http://localhost:8000/api/health || exit 1
elif [ "$1" = "tests" ]; then
    # Check if test environment is ready
    python -c "import src.horse_racing_ai; print('✅ Module imports OK')" || exit 1
    python -c "import pytest; print('✅ Pytest available')" || exit 1
else
    # Default health check
    python -c "import src.horse_racing_ai; print('✅ Application healthy')" || exit 1
fi

echo "✅ Health check passed"
