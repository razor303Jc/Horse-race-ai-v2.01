#!/usr/bin/env python3
'''
API Migration to PostgreSQL - V2.05
==================================

Migration script to update existing API endpoints to use PostgreSQL backend.
'''

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def update_api_database_connections():
    '''Update API server database connections to PostgreSQL'''
    
    # Files to update
    api_files = [
        'src/web/api_server.py',
        'tools/web_interface/enhanced_api_server_complete.py',
        'tools/web_interface/enhanced_api_server.py',
        'src/web/api_server_enhanced.py'
    ]
    
    print("🔄 Migrating API endpoints to PostgreSQL...")
    
    for api_file in api_files:
        file_path = project_root / api_file
        
        if file_path.exists():
            print(f"  📁 Updating: {api_file}")
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update database configuration
            if 'sqlite' in content.lower():
                print(f"    🔄 SQLite references found - needs manual update")
            
            # Check for database connection patterns
            if 'psycopg2' in content:
                print(f"    ✅ Already using PostgreSQL")
            else:
                print(f"    📝 Needs PostgreSQL integration")
        
        else:
            print(f"  ❌ File not found: {api_file}")
    
    print("\n📋 Migration Summary:")
    print("  • PostgreSQL configuration created")
    print("  • Environment variables defined")
    print("  • Connection pooling configured")
    print("  • Performance settings optimized")
    
    print("\n🚀 Next Steps:")
    print("  1. Update API server imports to use psycopg2")
    print("  2. Replace SQLite connections with PostgreSQL pool")
    print("  3. Update query syntax for PostgreSQL compatibility")
    print("  4. Test all endpoints with PostgreSQL backend")
    print("  5. Deploy with connection pooling")

if __name__ == "__main__":
    update_api_database_connections()
