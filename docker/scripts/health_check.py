#!/usr/bin/env python3
"""
Health check script for the web app container.
Uses Python urllib instead of curl to avoid external dependencies.
"""
import urllib.request
import sys

try:
    with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as response:
        if response.status == 200:
            sys.exit(0)
        else:
            sys.exit(1)
except Exception:
    sys.exit(1)
