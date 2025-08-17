#!/usr/bin/env python3
"""
🎯 Complete Data Management Integration
Comprehensive script that integrates archival system with download workflow

Workflow:
1. Archive existing downloaded files (zip and secure storage)
2. Clean download directory
3. Simulate new downloads
4. Record in database
5. Show data organized by date
6. Display archive history

Author: AI Assistant
Date: August 17, 2025
"""

import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "tools" / "data_management"))

from enhanced_download_system import EnhancedDownloadSystem


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )


def display_workflow_banner():
    """Display workflow banner"""
    print("🎯 COMPLETE DATA MANAGEMENT WORKFLOW")
    print("=" * 60)
    print("1. 📦 Archive existing files (zip + secure storage)")
    print("2. 🧹 Clean download directory")
    print("3. 📥 Download new data files")
    print("4. 📊 Record in database")
    print("5. 📅 Show data by date")
    print("6. 📚 Display archive history")
    print("=" * 60)


def run_complete_workflow(download_system: EnhancedDownloadSystem, 
                         download_date: str = None) -> Dict:
    """Run the complete data management workflow"""
    
    if download_date is None:
        download_date = datetime.now().strftime("%Y-%m-%d")
    
    logger = logging.getLogger(__name__)
    
    print(f"\n🚀 Starting workflow for {download_date}")
    print("-" * 40)
    
    # Execute complete workflow
    result = download_system.complete_download_workflow(download_date)
    
    # Display results
    if result["success"]:
        print(f"\n✅ Workflow completed successfully!")
        
        # Archive results
        if "archive_result" in result:
            archive = result["archive_result"]
            if archive.get("success"):
                print(f"   📦 Archive created: ID {archive['archive_id']}")
                print(f"   📁 Files archived: {archive['files_archived']}")
                print(f"   📈 Compression: {archive['compression_percentage']:.1f}%")
                print(f"   💾 Original size: {archive['original_size_mb']:.1f} MB")
                print(f"   📦 Compressed size: {archive['compressed_size_mb']:.1f} MB")
            elif not archive.get("archived", True):
                print(f"   📁 No files to archive ({archive.get('reason', 'unknown')})")
        
        # Download results  
        if "download_result" in result:
            download = result["download_result"]
            if download.get("success"):
                print(f"   📥 New files downloaded: {download['files_downloaded']}")
                
                # Show download details
                for detail in download.get("download_details", []):
                    filename = detail["filename"]
                    records = detail["records"]
                    size_kb = detail["size"] / 1024
                    print(f"      📄 {filename}: {records} records ({size_kb:.1f} KB)")
    else:
        print("❌ Workflow failed!")
        logger.error("Workflow execution failed")
    
    return result


def show_archive_history(download_system: EnhancedDownloadSystem, days: int = 7):
    """Show archive history"""
    
    print(f"\n📚 ARCHIVE HISTORY - Last {days} days")
    print("=" * 60)
    
    archives = download_system.archiver.get_archive_history(days)
    
    if not archives:
        print("⚠️ No archives found in the specified time period")
        return
    
    for archive in archives:
        date = archive["archive_date"]
        filename = archive["archive_filename"]
        files = archive["file_count"]
        size_mb = archive["total_size_bytes"] / 1024 / 1024
        compression = archive["compression_ratio"] * 100
        
        print(f"\n📦 {date} - {filename}")
        print(f"   📁 Files: {files}")
        print(f"   💾 Size: {size_mb:.1f} MB")
        print(f"   📈 Compression: {100-compression:.1f}%")
        print(f"   🔒 Status: {archive['status']}")


def show_database_data_by_date(download_system: EnhancedDownloadSystem, days: int = 7):
    """Show database data organized by date"""
    
    print(f"\n📊 DATABASE DATA BY DATE - Last {days} days")
    print("=" * 60)
    
    # Use the enhanced download system's method
    data_summary = download_system.show_data_by_date(days)
    
    return data_summary


def show_detailed_date_view(download_system: EnhancedDownloadSystem, target_date: str):
    """Show detailed view for a specific date"""
    
    print(f"\n🔍 DETAILED VIEW - {target_date}")
    print("=" * 60)
    
    # Get download details
    download_details = download_system.db_manager.get_download_details(target_date)
    
    if not download_details:
        print(f"⚠️ No downloads found for {target_date}")
        return
    
    # Group by source type
    cards_data = [d for d in download_details if d["source_type"] == "cards_data"]
    results_data = [d for d in download_details if d["source_type"] == "results_data"]
    
    if cards_data:
        print(f"\n📄 Cards Data ({len(cards_data)} files):")
        for download in cards_data:
            filename = download["filename"]
            category = download["file_category"]
            records = download["record_count"] or 0
            size_kb = download["file_size_bytes"] / 1024
            status = download["status"]
            
            status_icon = "📦" if status == "archived" else "📁"
            print(f"   {status_icon} {category}/{filename}: {records} records ({size_kb:.1f} KB)")
    
    if results_data:
        print(f"\n🏆 Results Data ({len(results_data)} files):")
        for download in results_data:
            filename = download["filename"]
            category = download["file_category"]
            records = download["record_count"] or 0
            size_kb = download["file_size_bytes"] / 1024
            status = download["status"]
            
            status_icon = "📦" if status == "archived" else "📁"
            print(f"   {status_icon} {category}/{filename}: {records} records ({size_kb:.1f} KB)")


def interactive_menu(download_system: EnhancedDownloadSystem):
    """Interactive menu for data management operations"""
    
    while True:
        print(f"\n🎯 DATA MANAGEMENT MENU")
        print("-" * 30)
        print("1. 🔄 Run complete workflow")
        print("2. 📅 Show data by date")
        print("3. 📚 Show archive history")
        print("4. 🔍 View specific date details")
        print("5. 📦 Archive current files only")
        print("6. 📥 Download simulation only")
        print("0. ❌ Exit")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            target_date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            run_complete_workflow(download_system, target_date)
        elif choice == "2":
            days_input = input("Enter number of days (default 7): ").strip()
            days = int(days_input) if days_input.isdigit() else 7
            show_database_data_by_date(download_system, days)
        elif choice == "3":
            days_input = input("Enter number of days (default 7): ").strip()
            days = int(days_input) if days_input.isdigit() else 7
            show_archive_history(download_system, days)
        elif choice == "4":
            date_input = input("Enter date (YYYY-MM-DD): ").strip()
            if date_input:
                show_detailed_date_view(download_system, date_input)
            else:
                print("⚠️ Please enter a valid date")
        elif choice == "5":
            date_input = input("Enter archive date (YYYY-MM-DD) or press Enter for today: ").strip()
            target_date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            archive_result = download_system.pre_download_archive(target_date)
            print(f"📦 Archive result: {archive_result}")
        elif choice == "6":
            date_input = input("Enter download date (YYYY-MM-DD) or press Enter for today: ").strip()
            target_date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            download_result = download_system.simulate_download(target_date)
            print(f"📥 Download result: {download_result}")
        else:
            print("⚠️ Invalid option. Please try again.")


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Complete Data Management System")
    parser.add_argument("--date", "-d", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to show")
    parser.add_argument("--workflow", "-w", action="store_true", help="Run complete workflow")
    parser.add_argument("--archive-only", "-a", action="store_true", help="Archive only")
    parser.add_argument("--download-only", "-dl", action="store_true", help="Download only")
    parser.add_argument("--show-data", "-s", action="store_true", help="Show data by date")
    parser.add_argument("--show-archives", "-sa", action="store_true", help="Show archive history")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Display banner
    display_workflow_banner()
    
    try:
        # Create enhanced download system
        download_system = EnhancedDownloadSystem(project_root)
        
        target_date = args.date or datetime.now().strftime("%Y-%m-%d")
        
        if args.interactive:
            interactive_menu(download_system)
        elif args.workflow:
            run_complete_workflow(download_system, target_date)
        elif args.archive_only:
            result = download_system.pre_download_archive(target_date)
            print(f"📦 Archive result: {result}")
        elif args.download_only:
            result = download_system.simulate_download(target_date)
            print(f"📥 Download result: {result}")
        elif args.show_data:
            show_database_data_by_date(download_system, args.days)
        elif args.show_archives:
            show_archive_history(download_system, args.days)
        else:
            # Default: run complete workflow
            run_complete_workflow(download_system, target_date)
            show_database_data_by_date(download_system, args.days)
            show_archive_history(download_system, args.days)
        
        logger.info("✅ Data management operations complete")
        
    except Exception as e:
        logger.error(f"💥 Error in data management: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
