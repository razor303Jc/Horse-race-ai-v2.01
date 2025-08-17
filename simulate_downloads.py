#!/usr/bin/env python3
"""
🎬 Download Simulation - Event-Driven Pipeline Testing
Simulates file downloads to test event-driven pipeline triggers

This script creates mock download files to trigger the event-driven pipeline:
- Creates races.csv, horses.csv, racecard_details.csv
- Simulates realistic download timing
- Tests file trigger system

Author: AI Assistant
Date: August 17, 2025
"""

import json
import time
from datetime import datetime
from pathlib import Path


def create_mock_races_csv(file_path: Path):
    """Create mock races.csv file"""
    content = """race_id,meeting_id,race_time,race_name,distance,track_condition
1001,MTG001,14:30,Maiden Stakes,1200m,Good
1002,MTG001,15:05,Handicap,1600m,Good  
1003,MTG001,15:40,Stakes Race,2000m,Soft
1004,MTG002,16:15,Sprint,1000m,Good
1005,MTG002,16:50,Feature Race,1800m,Good"""

    file_path.write_text(content)
    print(f"📝 Created: {file_path.name} ({len(content)} bytes)")


def create_mock_horses_csv(file_path: Path):
    """Create mock horses.csv file"""
    content = """horse_id,horse_name,age,weight,jockey,trainer,form,odds
H001,Lightning Bolt,4,58.5,J.Smith,T.Brown,1-2-1,3.50
H002,Thunder Strike,5,57.0,M.Jones,R.Wilson,3-1-2,5.20
H003,Speed Demon,3,56.0,L.Davis,K.Miller,2-3-1,7.80
H004,Royal Runner,6,59.0,P.Taylor,D.Johnson,1-1-3,2.90
H005,Storm Chaser,4,57.5,A.Clark,S.Anderson,2-2-2,6.40
H006,Fire Bolt,5,58.0,C.White,B.Thompson,1-3-1,4.10"""

    file_path.write_text(content)
    print(f"📝 Created: {file_path.name} ({len(content)} bytes)")


def create_mock_racecard_details_csv(file_path: Path):
    """Create mock racecard_details.csv file"""
    content = """race_id,horse_id,barrier,weight,jockey_claim,emergency
1001,H001,5,58.5,0,N
1001,H002,2,57.0,2,N
1001,H003,8,56.0,0,N
1002,H004,1,59.0,0,N
1002,H005,4,57.5,1.5,N
1002,H006,7,58.0,0,N"""

    file_path.write_text(content)
    print(f"📝 Created: {file_path.name} ({len(content)} bytes)")


def create_upload_manifest(file_path: Path):
    """Create upload manifest to simulate completion"""
    manifest = {
        "upload_timestamp": datetime.now().isoformat(),
        "files_uploaded": ["races.csv", "horses.csv", "racecard_details.csv"],
        "total_records": 150,
        "status": "complete",
    }

    file_path.write_text(json.dumps(manifest, indent=2))
    print(f"📤 Created: {file_path.name} (upload manifest)")


def simulate_downloads(project_root: Path, delay_between_files: int = 5):
    """Simulate download process with realistic timing"""

    print("🎬 Starting download simulation")
    print("=" * 50)

    # Define file paths
    data_dir = project_root / "data" / "daily_downloads"
    cards_dir = data_dir / "cards_data"
    results_dir = data_dir / "results"
    results_dir.mkdir(exist_ok=True)

    files_to_create = [
        (cards_dir / "races" / "races.csv", create_mock_races_csv),
        (cards_dir / "horses" / "horses.csv", create_mock_horses_csv),
        (
            cards_dir / "racecard_details" / "racecard_details.csv",
            create_mock_racecard_details_csv,
        ),
        (results_dir / "upload_manifest.json", create_upload_manifest),
    ]

    # Create files with delays
    for i, (file_path, creator_func) in enumerate(files_to_create, 1):
        print(f"⏱️  Step {i}/{len(files_to_create)}: Creating {file_path.name}")

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file
        creator_func(file_path)

        # Wait before next file (except last one)
        if i < len(files_to_create):
            print(f"⏳ Waiting {delay_between_files} seconds...")
            time.sleep(delay_between_files)

    print("\n✅ Download simulation complete!")
    print(f"📁 Files created in: {data_dir}")


def clean_previous_downloads(project_root: Path):
    """Clean up previous download files"""

    data_dir = project_root / "data" / "daily_downloads"

    files_to_remove = [
        data_dir / "cards_data" / "races" / "races.csv",
        data_dir / "cards_data" / "horses" / "horses.csv",
        data_dir / "cards_data" / "racecard_details" / "racecard_details.csv",
        data_dir / "results" / "upload_manifest.json",
    ]

    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            file_path.unlink()
            removed_count += 1

    if removed_count > 0:
        print(f"🧹 Cleaned {removed_count} previous files")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download Simulation for Event-Driven Pipeline"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean previous files first"
    )
    parser.add_argument(
        "--delay", type=int, default=5, help="Delay between files (seconds)"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent

    if args.clean:
        clean_previous_downloads(project_root)

    simulate_downloads(project_root, args.delay)


if __name__ == "__main__":
    main()
