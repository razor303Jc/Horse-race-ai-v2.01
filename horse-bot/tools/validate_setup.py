#!/usr/bin/env python3
"""
Validation script to check code structure and imports.
Run this after environment setup to validate the codebase.
"""

import sys
import importlib
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def validate_imports():
    """Test that all our modules can be imported."""
    modules_to_test = [
        "src.core.config",
        "src.models.database", 
        "src.models.horse_base",
        "src.services.external_apis",
        "src.simulation.monte_carlo",
        "src.api.routes.health"
    ]
    
    print("🔍 Validating Module Imports")
    print("=" * 40)
    
    all_good = True
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
    
    return all_good

def check_config():
    """Check that configuration loads properly."""
    try:
        from src.core.config import get_settings
        settings = get_settings()
        print(f"\n✅ Configuration loaded successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   Horse Base URL: {settings.horse_race_base_url}")
        return True
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🏇 Horse Race Handicapping AI - Code Validation")
    print("=" * 60)
    
    imports_ok = validate_imports()
    config_ok = check_config()
    
    if imports_ok and config_ok:
        print(f"\n🎉 All validations passed! Ready to start coding.")
        sys.exit(0)
    else:
        print(f"\n❌ Some validations failed. Check the errors above.")
        sys.exit(1)
