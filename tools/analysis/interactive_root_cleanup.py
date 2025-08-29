#!/usr/bin/env python3
"""
🏠 Interactive Root Directory Cleanup
=====================================

Step-by-step cleanup with detailed confirmation at each stage.
Shows exactly what will be protected and moved with user confirmation.

Author: AI Assistant
Date: August 29, 2025
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime


def load_analysis():
    """Load the analysis results"""
    project_root = Path(__file__).parent.parent.parent
    results_file = project_root / "ROOT_CLEANUP_ANALYSIS.json"
    
    if not results_file.exists():
        print("❌ Analysis results not found. Run root_directory_analyzer.py first")
        return None, None
    
    with open(results_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    return analysis, project_root


def show_protected_files(analysis):
    """Show what files will be protected"""
    protected_files = analysis.get('protected_files', [])
    
    print("🔒 PROTECTED FILES (WILL STAY IN ROOT)")
    print("=" * 50)
    
    by_category = {}
    for pfile in protected_files:
        category = pfile['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(pfile)
    
    for category, files in by_category.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for pfile in files:
            print(f"  ✅ {pfile['path']} ({pfile['size']:,} bytes)")
    
    print(f"\nTotal protected files: {len(protected_files)}")
    return protected_files


def show_move_plan(analysis, priority):
    """Show files to move for specific priority"""
    move_candidates = analysis.get('move_candidates', {})
    
    files_to_move = []
    total_size = 0
    
    for target_dir, files in move_candidates.items():
        priority_files = [f for f in files if f['priority'] == priority]
        if priority_files:
            files_to_move.extend([(target_dir, f) for f in priority_files])
            total_size += sum(f['size'] for f in priority_files)
    
    if not files_to_move:
        print(f"✅ No {priority} priority files to move")
        return []
    
    print(f"📦 {priority.upper()} PRIORITY FILES TO MOVE")
    print("=" * 50)
    print(f"Total files: {len(files_to_move)}")
    print(f"Total size: {total_size:,} bytes")
    print()
    
    # Group by destination
    by_dest = {}
    for target_dir, file_info in files_to_move:
        if target_dir not in by_dest:
            by_dest[target_dir] = []
        by_dest[target_dir].append(file_info)
    
    for target_dir, files in by_dest.items():
        print(f"📁 → {target_dir}/ ({len(files)} files)")
        for file_info in files[:5]:  # Show first 5
            print(f"  • {file_info['path']} ({file_info['size']:,} bytes)")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
        print()
    
    return files_to_move


def move_files(files_to_move, project_root, priority):
    """Move files with confirmation"""
    if not files_to_move:
        return []
    
    response = input(f"\nProceed with moving {priority} priority files? (y/N): ").strip().lower()
    if response != 'y':
        print(f"⏭️ Skipped {priority} priority files")
        return []
    
    moved_files = []
    
    # Create target directories first
    target_dirs = set()
    for target_dir, _ in files_to_move:
        target_dirs.add(target_dir)
    
    print("\n📁 Creating target directories...")
    for target_dir in target_dirs:
        target_path = project_root / target_dir
        target_path.mkdir(exist_ok=True)
        print(f"  ✅ {target_dir}/")
    
    print(f"\n📦 Moving {priority} priority files...")
    
    for target_dir, file_info in files_to_move:
        source_path = project_root / file_info['path']
        target_path = project_root / target_dir
        dest_path = target_path / source_path.name
        
        if not source_path.exists():
            print(f"  ⚠️ File not found: {file_info['path']}")
            continue
        
        try:
            shutil.move(str(source_path), str(dest_path))
            print(f"  ✅ {file_info['path']} → {target_dir}/{source_path.name}")
            moved_files.append({
                'source': file_info['path'],
                'destination': f"{target_dir}/{source_path.name}",
                'priority': priority
            })
        except Exception as e:
            print(f"  ❌ Error moving {file_info['path']}: {e}")
    
    print(f"\n✅ Moved {len(moved_files)} {priority} priority files")
    return moved_files


def cleanup_temp_directories(analysis, project_root):
    """Clean up temporary directories with individual confirmation"""
    cleanup_opportunities = analysis.get('cleanup_opportunities', [])
    temp_dirs = [op for op in cleanup_opportunities if op['type'] == 'temp_directory']
    
    if not temp_dirs:
        print("✅ No temporary directories found")
        return []
    
    print("🗑️ TEMPORARY DIRECTORIES")
    print("=" * 50)
    
    for temp_dir in temp_dirs:
        print(f"📁 {temp_dir['path']} - {temp_dir['reason']}")
    
    print(f"\nFound {len(temp_dirs)} temporary directories")
    
    removed_dirs = []
    
    for temp_dir in temp_dirs:
        dir_path = project_root / temp_dir['path']
        
        if not dir_path.exists():
            print(f"⚠️ Directory not found: {temp_dir['path']}")
            continue
        
        # Calculate directory size
        try:
            dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            print(f"\n🗑️ Remove {temp_dir['path']}?")
            print(f"   Reason: {temp_dir['reason']}")
            print(f"   Size: {dir_size:,} bytes")
        except:
            dir_size = 0
            print(f"\n🗑️ Remove {temp_dir['path']}?")
            print(f"   Reason: {temp_dir['reason']}")
        
        response = input("   Remove? (y/N): ").strip().lower()
        
        if response == 'y':
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Removed {temp_dir['path']}")
                removed_dirs.append(temp_dir['path'])
            except Exception as e:
                print(f"   ❌ Error removing {temp_dir['path']}: {e}")
        else:
            print(f"   ⏭️ Skipped {temp_dir['path']}")
    
    return removed_dirs


def create_final_summary(protected_files, all_moved_files, removed_dirs, project_root):
    """Create final summary of all changes"""
    print("\n📊 CLEANUP SUMMARY")
    print("=" * 50)
    
    print(f"✅ Protected files in root: {len(protected_files)}")
    print(f"📦 Files moved: {len(all_moved_files)}")
    print(f"🗑️ Directories removed: {len(removed_dirs)}")
    
    # Show current root directory contents
    print("\n📁 Root directory now contains:")
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    root_dirs = [d for d in project_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    print(f"   Files: {len(root_files)}")
    for file_path in sorted(root_files)[:10]:
        print(f"     • {file_path.name}")
    if len(root_files) > 10:
        print(f"     ... and {len(root_files) - 10} more files")
    
    print(f"   Directories: {len(root_dirs)}")
    for dir_path in sorted(root_dirs)[:10]:
        print(f"     📁 {dir_path.name}/")
    if len(root_dirs) > 10:
        print(f"     ... and {len(root_dirs) - 10} more directories")


def main():
    """Interactive cleanup main function"""
    print("🏠 INTERACTIVE ROOT DIRECTORY CLEANUP")
    print("=" * 50)
    print("This will show you exactly what will be protected and moved,")
    print("and ask for confirmation at each stage.\n")
    
    # Load analysis
    analysis, project_root = load_analysis()
    if not analysis:
        return
    
    # Step 1: Show protected files
    protected_files = show_protected_files(analysis)
    
    input("\nPress Enter to continue to file moving plan...")
    
    # Step 2: Move files by priority
    all_moved_files = []
    priorities = ['high', 'medium', 'low']
    
    for priority in priorities:
        print(f"\n{'='*60}")
        files_to_move = show_move_plan(analysis, priority)
        moved_files = move_files(files_to_move, project_root, priority)
        all_moved_files.extend(moved_files)
        
        if moved_files:
            input(f"\nPress Enter to continue to next priority level...")
    
    # Step 3: Clean up temporary directories
    print(f"\n{'='*60}")
    removed_dirs = cleanup_temp_directories(analysis, project_root)
    
    # Step 4: Final summary
    create_final_summary(protected_files, all_moved_files, removed_dirs, project_root)
    
    print(f"\n🎉 ROOT DIRECTORY CLEANUP COMPLETE!")
    print(f"Your root directory is now clean and organized!")


if __name__ == "__main__":
    main()
