#!/usr/bin/env python3
"""
Main entry point for Horse Racing AI v2.0 Web Application
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from src.web.web_gui import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
