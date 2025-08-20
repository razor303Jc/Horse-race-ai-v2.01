#!/usr/bin/env python3
"""
File Watcher Status API
Provides real-time status information from the file watcher system
"""

from pathlib import Path
import json
from datetime import datetime


class FileWatcherStatus:
    """Reads and provides file watcher status information"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.base_path = Path(base_path)
        self.status_file = (
            self.base_path / "data/daily_downloads/processing_status.json"
        )

    def get_status(self) -> dict:
        """Get current file watcher processing status"""
        try:
            if not self.status_file.exists():
                return self._default_status()

            with open(self.status_file, "r") as f:
                status = json.load(f)

            # Add additional status checks
            status["manual_download_empty"] = self._check_manual_download_empty()
            status["cards_data_available"] = self._check_cards_data_available()
            status["results_data_available"] = self._check_results_data_available()
            status["status_timestamp"] = datetime.now().isoformat()

            return status

        except Exception as e:
            return {
                "error": f"Failed to read status: {e}",
                "status_timestamp": datetime.now().isoformat(),
            }

    def _default_status(self) -> dict:
        """Return default status when no status file exists"""
        return {
            "cards_ready": False,
            "results_ready": False,
            "last_processed": None,
            "race_day_info": {},
            "user_message": "📥 **Ready for Data Upload**\n\nWaiting for race data files...",
            "download_instructions": """
📥 **Daily Data Download Instructions:**

1. **Visit Racing Data Source** (check your data provider)
2. **Download Today's Files:**
   - UK Race Cards (ZIP file)
   - UK Results (ZIP file)  
3. **Save to Manual Download Folder:**
   - Location: `/data/daily_downloads/manual_download/`
   - File names should contain 'racecard' or 'result'
4. **Automatic Processing:**
   - Files detected automatically
   - Data extracted and validated
   - Manual download folder cleaned
   - Race analysis generated

🚨 **Important:** Download fresh files daily for accurate predictions
            """.strip(),
            "manual_download_empty": self._check_manual_download_empty(),
            "cards_data_available": self._check_cards_data_available(),
            "results_data_available": self._check_results_data_available(),
            "status_timestamp": datetime.now().isoformat(),
        }

    def _check_manual_download_empty(self) -> bool:
        """Check if manual download directory is empty"""
        try:
            manual_dir = self.base_path / "data/daily_downloads/manual_download"
            if not manual_dir.exists():
                return True

            zip_files = list(manual_dir.glob("*.zip"))
            return len(zip_files) == 0

        except Exception:
            return False

    def _check_cards_data_available(self) -> bool:
        """Check if race cards data is available"""
        try:
            cards_dir = self.base_path / "data/daily_downloads/cards_data"
            if not cards_dir.exists():
                return False

            # Check for races directory and CSV file
            races_dir = cards_dir / "races"
            if not races_dir.exists():
                return False

            races_csv = list(races_dir.glob("*.csv"))
            return len(races_csv) > 0

        except Exception:
            return False

    def _check_results_data_available(self) -> bool:
        """Check if results data is available"""
        try:
            results_dir = self.base_path / "data/daily_downloads/results_data"
            if not results_dir.exists():
                return False

            # Check for any CSV files
            csv_files = list(results_dir.rglob("*.csv"))
            return len(csv_files) > 0

        except Exception:
            return False

    def get_race_day_summary(self) -> dict:
        """Get summarized race day information"""
        status = self.get_status()
        race_info = status.get("race_day_info", {})

        if not race_info:
            return {"has_data": False, "message": "No race data available"}

        return {
            "has_data": True,
            "date": race_info.get("date"),
            "total_races": race_info.get("total_races", 0),
            "courses": race_info.get("courses", []),
            "first_race": race_info.get("first_race"),
            "last_race": race_info.get("last_race"),
            "course_count": len(race_info.get("courses", [])),
            "racing_duration": self._calculate_racing_duration(
                race_info.get("first_race"), race_info.get("last_race")
            ),
        }

    def _calculate_racing_duration(self, first_race: str, last_race: str) -> str:
        """Calculate total racing duration"""
        try:
            if not first_race or not last_race:
                return "Unknown"

            from datetime import datetime

            first = datetime.strptime(first_race, "%H:%M:%S").time()
            last = datetime.strptime(last_race, "%H:%M:%S").time()

            # Convert to datetime for calculation
            first_dt = datetime.combine(datetime.today(), first)
            last_dt = datetime.combine(datetime.today(), last)

            duration = last_dt - first_dt
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            return f"{hours}h {minutes}m"

        except Exception:
            return "Unknown"


# For API integration
def get_file_watcher_status():
    """Simple function to get status for API endpoints"""
    status_reader = FileWatcherStatus()
    return status_reader.get_status()


def get_race_day_summary():
    """Simple function to get race day summary for API endpoints"""
    status_reader = FileWatcherStatus()
    return status_reader.get_race_day_summary()


if __name__ == "__main__":
    # Test the status reader
    status_reader = FileWatcherStatus()
    status = status_reader.get_status()
    summary = status_reader.get_race_day_summary()

    print("📊 File Watcher Status:")
    print(json.dumps(status, indent=2))
    print("\n📋 Race Day Summary:")
    print(json.dumps(summary, indent=2))
