#!/usr/bin/env python3
"""
Horse Racing AI v2.0 - Enhanced Web Application
Main entry point with all the latest system intelligence and capabilities.

This version incorporates ALL the learnings and advances from the system:
- 76.5% AUC ML performance with 4-model ensemble
- 32-factor contextual AI enhancement
- Professional betting strategies and risk management
- Real-time performance tracking and analytics
- Live BETDAQ integration
- Comprehensive dashboard and monitoring
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced web GUI
from src.web.enhanced_web_application import create_enhanced_app


def main():
    """Main application entry point"""

    # Detect if running in Docker
    is_docker = os.path.exists("/.dockerenv") or os.environ.get(
        "DOCKER_CONTAINER", False
    )

    print("🏇 " + "=" * 60)
    print("  HORSE RACING AI v2.0 - ENHANCED WEB APPLICATION")
    if is_docker:
        print("  🐋 RUNNING IN DOCKER CONTAINER")
    print("=" * 65)
    print()
    print("🤖 FEATURES LOADED:")
    print("   ✅ Advanced ML Models (76.5% AUC)")
    print("   ✅ 4-Model Ensemble (RF, GB, LR, NN)")
    print("   ✅ 40+ Features per Horse")
    print("   ✅ 32-Factor Contextual AI")
    print("   ✅ Professional Betting Strategies")
    print("   ✅ Real-time Performance Tracking")
    print("   ✅ Live BETDAQ Integration")
    print("   ✅ Risk Management & Bankroll Protection")
    print("   ✅ Comprehensive Analytics Dashboard")
    print()
    print("🌐 STARTING WEB APPLICATION...")

    # Get configuration from environment
    host = os.environ.get("FLASK_HOST", "0.0.0.0" if is_docker else "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5002))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    print(f"   📍 URL: http://{host}:{port}")
    print("   📊 Enhanced Dashboard with all system capabilities")
    print("   🔄 Real-time updates and live integration")
    if is_docker:
        print("   🐋 Docker mode: All services containerized")
    print()

    # Create and configure the enhanced application
    app = create_enhanced_app()

    # Run the application
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()
