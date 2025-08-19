#!/usr/bin/env python3
import os
import glob
from pathlib import Path
from collections import defaultdict

def analyze_project_files():
    print("🔍 HORSE RACING AI v2.03 - FILE ANALYSIS")
    print("=" * 60)
    
    total_files = 0
    file_categories = defaultdict(list)
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.startswith('.'):
                continue
                
            total_files += 1
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            
            if file.endswith('.py'):
                if file_size == 0:
                    file_categories['empty_python'].append((file_path, file_size))
                elif 'test_' in file:
                    file_categories['test_files'].append((file_path, file_size))
                elif file.endswith('.backup') or 'backup' in file:
                    file_categories['backup_files'].append((file_path, file_size))
                else:
                    file_categories['python_files'].append((file_path, file_size))
            elif file.endswith('.pyc'):
                file_categories['compiled_python'].append((file_path, file_size))
            elif file.endswith(('.yml', '.yaml')):
                file_categories['config_files'].append((file_path, file_size))
            elif file.endswith('.sql'):
                file_categories['database_files'].append((file_path, file_size))
            elif file.endswith('.html'):
                file_categories['template_files'].append((file_path, file_size))
            elif file.endswith('.txt'):
                file_categories['text_files'].append((file_path, file_size))
            elif file.endswith('.md'):
                file_categories['documentation'].append((file_path, file_size))
            elif file.endswith('.json'):
                file_categories['json_files'].append((file_path, file_size))
            else:
                file_categories['other_files'].append((file_path, file_size))
    
    print(f"📊 TOTAL FILES: {total_files}")
    print("\n📂 FILE CATEGORIES:")
    print("-" * 40)
    
    for category, files in file_categories.items():
        total_size = sum(size for _, size in files)
        print(f"  {category.replace('_', ' ').title()}: {len(files)} files ({total_size:,} bytes)")
    
    print("\n🗑️ FILES THAT CAN BE REMOVED:")
    print("-" * 30)
    
    removable_files = []
    
    if file_categories['empty_python']:
        print("  📭 Empty Python Files:")
        for file_path, size in file_categories['empty_python']:
            print(f"    ❌ {file_path}")
            removable_files.append(file_path)
    
    if file_categories['backup_files']:
        print("  💾 Backup Files:")
        for file_path, size in file_categories['backup_files']:
            print(f"    ❌ {file_path}")
            removable_files.append(file_path)
    
    if file_categories['compiled_python']:
        print("  🔄 Compiled Python Files:")
        for file_path, size in file_categories['compiled_python']:
            print(f"    ❌ {file_path}")
            removable_files.append(file_path)
    
    cache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dirs.append(os.path.join(root, '__pycache__'))
    
    if cache_dirs:
        print("  🗂️ Cache Directories:")
        for cache_dir in cache_dirs:
            print(f"    ❌ {cache_dir}/")
            removable_files.append(cache_dir)
    
    print(f"\n📝 TOTAL REMOVABLE: {len(removable_files)}")
    
    return len(removable_files), total_files

if __name__ == "__main__":
    removable_count, total_count = analyze_project_files()
    print(f"\n🎯 SUMMARY: {removable_count}/{total_count} files can be removed ({removable_count/total_count*100:.1f}%)")
