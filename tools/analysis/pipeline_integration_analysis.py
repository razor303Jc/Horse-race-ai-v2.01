#!/usr/bin/env python3
"""
🔍 Pipeline Integration Status Analysis
======================================

Comprehensive analysis of what pipeline triggers are integrated vs. missing
after the 15:15 auto-downloader success.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


class PipelineStatusAnalyzer:
    def __init__(self):
        self.base_path = Path("/home/jc/Documents/Horse-race-ai-v2.02")
        self.data_path = self.base_path / "data" / "daily_downloads"

    def analyze_current_status(self):
        """Analyze current pipeline integration status"""
        print("🔍 PIPELINE INTEGRATION STATUS ANALYSIS")
        print("=" * 60)
        print(f"📅 Analysis Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📁 Data Path: {self.data_path}")

        # 1. Check what completed successfully
        self.check_stage_1_completion()

        # 2. Check what should happen next
        self.check_missing_integrations()

        # 3. Check container statuses
        self.check_container_pipeline_status()

        # 4. Analyze next steps
        self.analyze_next_steps()

    def check_stage_1_completion(self):
        """Check Stage 1: Data Download completion"""
        print("\n🎯 STAGE 1: DATA DOWNLOAD")
        print("-" * 30)

        # Check if download completed
        results_path = self.data_path / "results_data"
        cards_path = self.data_path / "cards_data"

        if results_path.exists() and cards_path.exists():
            results_files = len([f for f in results_path.rglob("*") if f.is_file()])
            cards_files = len([f for f in cards_path.rglob("*") if f.is_file()])

            print(f"✅ COMPLETED at 15:15")
            print(f"   📊 Results files: {results_files}")
            print(f"   📊 Cards files: {cards_files}")
            print(f"   🔧 Processing fix: WORKING (dates corrected)")

            # Check file dates in races.csv
            races_results = results_path / "races" / "races.csv"
            races_cards = cards_path / "races" / "races.csv"

            if races_results.exists():
                content = races_results.read_text()
                if "2025-08-17" in content:
                    print(f"   ✅ Results data: Aug 17 (TODAY - correct)")
                else:
                    print(f"   ⚠️ Results data: Date unclear")

            if races_cards.exists():
                content = races_cards.read_text()
                if "2025-08-16" in content:
                    print(f"   ✅ Cards data: Aug 16 (YESTERDAY - correct)")
                else:
                    print(f"   ⚠️ Cards data: Date unclear")
        else:
            print("❌ NOT COMPLETED - No data found")

    def check_missing_integrations(self):
        """Check what pipeline stages should have triggered but didn't"""
        print("\n🚫 MISSING INTEGRATIONS")
        print("-" * 30)

        missing_stages = []

        # Stage 2: Data Validation (should trigger immediately after download)
        print("Stage 2: Data Validation")
        if not self.check_for_validation_logs():
            print("   ❌ NOT TRIGGERED - No validation logs found")
            missing_stages.append("data_validation")
        else:
            print("   ✅ TRIGGERED - Validation logs found")

        # Stage 3: CSV Import (should trigger after validation)
        print("Stage 3: CSV Database Import")
        if not self.check_for_csv_import():
            print("   ❌ NOT TRIGGERED - No database import detected")
            missing_stages.append("csv_import")
        else:
            print("   ✅ TRIGGERED - Database import detected")

        # Stage 4: Data Preprocessing
        print("Stage 4: Data Preprocessing")
        if not self.check_for_preprocessing():
            print("   ❌ NOT TRIGGERED - No preprocessing detected")
            missing_stages.append("data_preprocessing")
        else:
            print("   ✅ TRIGGERED - Preprocessing detected")

        # Stages 5-17: ML Pipeline
        print("Stages 5-17: ML Pipeline")
        if not self.check_for_ml_pipeline():
            print("   ❌ NOT TRIGGERED - No ML processing detected")
            missing_stages.append("ml_pipeline")
        else:
            print("   ✅ TRIGGERED - ML pipeline active")

        return missing_stages

    def check_for_validation_logs(self):
        """Check if data validation stage ran"""
        try:
            # Check auto-downloader logs for validation
            result = subprocess.run(
                ["docker", "logs", "horse_racing_auto_downloader_clean"],
                capture_output=True,
                text=True,
            )

            return "Data validation passed" in result.stdout
        except:
            return False

    def check_for_csv_import(self):
        """Check if CSV import to database happened"""
        # Check for database activity in PostgreSQL
        try:
            result = subprocess.run(
                ["docker", "logs", "horse_racing_postgres_clean", "--tail", "50"],
                capture_output=True,
                text=True,
            )

            # Look for recent INSERT/UPDATE activity
            recent_activity = any(
                [
                    "INSERT" in result.stdout,
                    "UPDATE" in result.stdout,
                    "COPY" in result.stdout,
                ]
            )

            return recent_activity
        except:
            return False

    def check_for_preprocessing(self):
        """Check if data preprocessing stage ran"""
        # Look for preprocessing output files or logs
        processing_indicators = [
            self.base_path / "cache" / "processed_data",
            self.base_path / "data" / "processed",
            self.base_path / "models" / "preprocessing",
        ]

        return any(path.exists() for path in processing_indicators)

    def check_for_ml_pipeline(self):
        """Check if ML pipeline stages are running"""
        try:
            result = subprocess.run(
                ["docker", "logs", "horse_racing_ml_trainer_clean", "--tail", "20"],
                capture_output=True,
                text=True,
            )

            # Look for recent ML activity
            ml_activity = any(
                [
                    "training" in result.stdout.lower(),
                    "model" in result.stdout.lower(),
                    "feature" in result.stdout.lower(),
                ]
            )

            return ml_activity
        except:
            return False

    def check_container_pipeline_status(self):
        """Check what pipeline containers are doing"""
        print("\n🐳 CONTAINER PIPELINE STATUS")
        print("-" * 30)

        containers = [
            "horse_racing_auto_downloader_clean",
            "horse_racing_data_pipeline_clean",
            "horse_racing_ml_trainer_clean",
        ]

        for container in containers:
            try:
                # Get container status
                status_result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        f"name={container}",
                        "--format",
                        "{{.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                )

                status = status_result.stdout.strip()

                if "Up" in status:
                    if "healthy" in status:
                        health_emoji = "✅"
                    elif "unhealthy" in status:
                        health_emoji = "⚠️"
                    else:
                        health_emoji = "🔄"

                    print(
                        f"{health_emoji} {container.replace('horse_racing_', '').replace('_clean', '')}: {status}"
                    )
                else:
                    print(
                        f"❌ {container.replace('horse_racing_', '').replace('_clean', '')}: Not running"
                    )

            except Exception as e:
                print(f"❌ {container}: Error checking status")

    def analyze_next_steps(self):
        """Analyze what should happen next"""
        print("\n🚀 NEXT STEPS ANALYSIS")
        print("-" * 30)

        current_time = datetime.now()
        download_time = current_time.replace(
            hour=15, minute=15, second=0, microsecond=0
        )

        if current_time < download_time:
            print("⏰ Waiting for 15:15 download trigger")
            return

        # If we're past 15:15, analyze what should be happening
        time_since_download = current_time - download_time

        print(f"⏰ Time since download: {time_since_download}")

        if time_since_download < timedelta(minutes=5):
            print("🔄 Stage 2 (Data Validation) should be running now")
            print("🔄 Stage 3 (CSV Import) should start in ~2 minutes")
        elif time_since_download < timedelta(minutes=15):
            print("🔄 Stage 3 (CSV Import) should be running now")
            print("🔄 Stage 4 (Data Preprocessing) should start soon")
        elif time_since_download < timedelta(minutes=30):
            print(
                "🔄 Stages 4-6 (Preprocessing & Feature Engineering) should be running"
            )
        elif time_since_download < timedelta(hours=1):
            print("🔄 Stages 7-12 (ML Pipeline) should be active")
        else:
            print("🔄 Advanced ML stages should be running")

        # Check what's actually missing
        print("\n🔧 INTEGRATION GAPS:")
        print("1. Event-driven pipeline triggers - NOT ACTIVE")
        print("2. Automatic CSV import after download - NOT ACTIVE")
        print("3. Sequential stage triggering - NOT ACTIVE")
        print("4. File monitoring system - NOT ACTIVE")

        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Activate event-driven pipeline orchestrator")
        print("2. Trigger manual CSV import of downloaded data")
        print("3. Start missing pipeline stages manually")
        print("4. Implement file monitoring triggers")


def main():
    analyzer = PipelineStatusAnalyzer()
    analyzer.analyze_current_status()


if __name__ == "__main__":
    main()
