#!/usr/bin/env python3
"""
📊 Database Data Viewer
Simple script to view database data organized by date
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def show_database_summary(project_root: Path):
    """Show comprehensive database summary"""

    db_path = project_root / "data" / "racing_data_tracking.db"

    if not db_path.exists():
        print("⚠️ Database not found")
        return

    print("📊 DATABASE SUMMARY")
    print("=" * 50)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Get daily summaries
        cursor.execute(
            """
            SELECT 
                data_date,
                total_downloads,
                total_files,
                total_size_bytes,
                races_count,
                horses_count,
                jockeys_count,
                trainers_count,
                records_count,
                status
            FROM daily_data_summary
            ORDER BY data_date DESC
            LIMIT 10
        """
        )

        daily_data = cursor.fetchall()

        if daily_data:
            print("\n📅 DAILY SUMMARIES:")
            for row in daily_data:
                (
                    date,
                    downloads,
                    files,
                    size_bytes,
                    races,
                    horses,
                    jockeys,
                    trainers,
                    records,
                    status,
                ) = row
                size_mb = (size_bytes or 0) / 1024 / 1024

                print(f"\n🗓️  {date}:")
                print(f"   📥 Downloads: {downloads}")
                print(f"   📁 Files: {files}")
                print(f"   💾 Size: {size_mb:.1f} MB")
                print(f"   🏇 Races: {races}")
                print(f"   🐎 Horses: {horses}")
                print(f"   👤 Jockeys: {jockeys}")
                print(f"   🎯 Trainers: {trainers}")
                print(f"   📊 Records: {records}")
                print(f"   🔒 Status: {status}")

        # Get download details for today
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT 
                download_timestamp,
                source_type,
                file_category,
                filename,
                file_size_bytes,
                record_count,
                status,
                archive_id
            FROM downloads
            WHERE download_date = ?
            ORDER BY download_timestamp DESC
        """,
            (today,),
        )

        today_downloads = cursor.fetchall()

        if today_downloads:
            print(f"\n🔍 TODAY'S DOWNLOADS ({today}):")
            print("-" * 40)

            cards_data = [d for d in today_downloads if d[1] == "cards_data"]
            results_data = [d for d in today_downloads if d[1] == "results_data"]

            if cards_data:
                print(f"\n📄 Cards Data ({len(cards_data)} files):")
                for download in cards_data:
                    (
                        timestamp,
                        source_type,
                        category,
                        filename,
                        size_bytes,
                        records,
                        status,
                        archive_id,
                    ) = download
                    size_kb = size_bytes / 1024

                    status_icon = "📦" if status == "archived" else "📁"
                    archive_text = f" (Archive: {archive_id})" if archive_id else ""

                    print(
                        f"   {status_icon} {category}/{filename}: {records or 0} records ({size_kb:.1f} KB){archive_text}"
                    )

            if results_data:
                print(f"\n🏆 Results Data ({len(results_data)} files):")
                for download in results_data:
                    (
                        timestamp,
                        source_type,
                        category,
                        filename,
                        size_bytes,
                        records,
                        status,
                        archive_id,
                    ) = download
                    size_kb = size_bytes / 1024

                    status_icon = "📦" if status == "archived" else "📁"
                    archive_text = f" (Archive: {archive_id})" if archive_id else ""

                    print(
                        f"   {status_icon} {category}/{filename}: {records or 0} records ({size_kb:.1f} KB){archive_text}"
                    )


def show_archive_summary(project_root: Path):
    """Show archive summary"""

    archive_db_path = project_root / "data" / "archives" / "archive_tracking.db"

    if not archive_db_path.exists():
        print("⚠️ Archive database not found")
        return

    print("\n📚 ARCHIVE SUMMARY")
    print("=" * 50)

    with sqlite3.connect(archive_db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                id,
                archive_date,
                archive_filename,
                file_count,
                total_size_bytes,
                compression_ratio,
                created_timestamp,
                status
            FROM archives
            ORDER BY created_timestamp DESC
            LIMIT 5
        """
        )

        archives = cursor.fetchall()

        if archives:
            for archive in archives:
                (
                    id,
                    date,
                    filename,
                    files,
                    size_bytes,
                    compression_ratio,
                    timestamp,
                    status,
                ) = archive
                size_mb = size_bytes / 1024 / 1024
                compression_pct = (1 - compression_ratio) * 100

                print(f"\n📦 Archive {id} - {date}")
                print(f"   📄 {filename}")
                print(f"   📁 Files: {files}")
                print(f"   💾 Size: {size_mb:.1f} MB")
                print(f"   📈 Compression: {compression_pct:.1f}%")
                print(f"   ⏰ Created: {timestamp}")
                print(f"   🔒 Status: {status}")


def main():
    """Main function"""

    project_root = Path(__file__).parent

    show_database_summary(project_root)
    show_archive_summary(project_root)


if __name__ == "__main__":
    main()
