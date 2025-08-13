#!/usr/bin/env python3
"""
Racing News Analyzer Dashboard
Monitor and manage the news analysis system
"""

import argparse
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import requests


class NewsAnalyzerDashboard:
    def __init__(self, db_path="news_analysis.db"):
        self.db_path = db_path

    def get_system_status(self):
        """Get overall system status"""
        status = {
            "ollama_running": self.check_ollama_status(),
            "database_accessible": self.check_database(),
            "last_analysis": self.get_last_analysis_time(),
            "total_articles": self.get_total_articles(),
            "reports_generated": self.get_reports_count(),
        }
        return status

    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_database(self):
        """Check database accessibility"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            conn.close()
            return True
        except:
            return False

    def get_last_analysis_time(self):
        """Get timestamp of last analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MAX(scraped_date) FROM news_articles
            """
            )
            result = cursor.fetchone()
            conn.close()
            return result[0] if result[0] else "Never"
        except:
            return "Error"

    def get_total_articles(self):
        """Get total number of articles analyzed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            result = cursor.fetchone()
            conn.close()
            return result[0]
        except:
            return 0

    def get_reports_count(self):
        """Get number of daily reports generated"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_reports")
            result = cursor.fetchone()
            conn.close()
            return result[0]
        except:
            return 0

    def get_recent_articles(self, days=7):
        """Get recent articles analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            since_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute(
                """
                SELECT title, source, scraped_date, sentiment_score, key_topics
                FROM news_articles 
                WHERE scraped_date > ?
                ORDER BY scraped_date DESC
                LIMIT 20
            """,
                (since_date,),
            )

            articles = []
            for row in cursor.fetchall():
                articles.append(
                    {
                        "title": row[0],
                        "source": row[1] if row[1] else "Unknown",
                        "date": row[2],
                        "sentiment": row[3] if row[3] else 0,
                        "topics": json.loads(row[4]) if row[4] else [],
                    }
                )

            conn.close()
            return articles
        except Exception as e:
            print(f"Error getting recent articles: {e}")
            return []

    def get_sentiment_trend(self, days=30):
        """Get sentiment trend over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            since_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute(
                """
                SELECT DATE(scraped_date) as date, AVG(sentiment_score) as avg_sentiment
                FROM news_articles 
                WHERE scraped_date > ?
                GROUP BY DATE(scraped_date)
                ORDER BY date DESC
            """,
                (since_date,),
            )

            trend = []
            for row in cursor.fetchall():
                trend.append(
                    {"date": row[0], "sentiment": round(row[1], 3) if row[1] else 0}
                )

            conn.close()
            return trend
        except Exception as e:
            print(f"Error getting sentiment trend: {e}")
            return []

    def display_dashboard(self):
        """Display the main dashboard"""
        print("🏇 Racing News Analyzer Dashboard")
        print("=" * 50)

        # System Status
        status = self.get_system_status()
        print("\n📊 System Status:")
        print(
            f"  Ollama Service: {'✅ Running' if status['ollama_running'] else '❌ Not Running'}"
        )
        print(
            f"  Database: {'✅ Accessible' if status['database_accessible'] else '❌ Error'}"
        )
        print(f"  Last Analysis: {status['last_analysis']}")
        print(f"  Total Articles: {status['total_articles']}")
        print(f"  Reports Generated: {status['reports_generated']}")

        # Recent Articles
        print("\n📰 Recent Articles (Last 7 days):")
        recent = self.get_recent_articles(7)
        if recent:
            for article in recent[:5]:
                sentiment_icon = (
                    "🔴"
                    if article["sentiment"] < -0.3
                    else "🟢" if article["sentiment"] > 0.3 else "🟡"
                )
                print(f"  {sentiment_icon} {article['title'][:50]}...")
                print(
                    f"     Source: {article['source']} | Date: {article['date'][:19]}"
                )
                print(f"     Sentiment: {article['sentiment']:.2f}")
        else:
            print("  No recent articles found")

        # Sentiment Trend
        print("\n📈 Sentiment Trend (Last 7 days):")
        trend = self.get_sentiment_trend(7)
        if trend:
            for day in trend[:7]:
                sentiment_bar = "█" * max(1, int((day["sentiment"] + 1) * 10))
                print(f"  {day['date']}: {sentiment_bar} ({day['sentiment']:.2f})")
        else:
            print("  No trend data available")

        # Reports
        reports_dir = Path("reports/daily_news")
        if reports_dir.exists():
            reports = list(reports_dir.glob("*.md"))
            print(f"\n📋 Recent Reports ({len(reports)} total):")
            for report in sorted(reports, reverse=True)[:3]:
                print(f"  📄 {report.name}")

        print("\n" + "=" * 50)

    def run_analysis_now(self):
        """Trigger analysis immediately"""
        print("🔄 Running analysis now...")
        try:
            result = subprocess.run(
                ["python3", "daily_news_analyzer.py"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ Analysis completed successfully")
            else:
                print(f"❌ Analysis failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Analysis timed out")
        except Exception as e:
            print(f"❌ Error running analysis: {e}")

    def clean_old_data(self, days=30):
        """Clean old data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute(
                "DELETE FROM news_articles WHERE scraped_date < ?", (cutoff_date,)
            )
            cursor.execute(
                "DELETE FROM daily_reports WHERE created_at < ?", (cutoff_date,)
            )

            deleted_articles = cursor.rowcount
            conn.commit()
            conn.close()

            print(f"🗑️ Cleaned {deleted_articles} old articles (older than {days} days)")
        except Exception as e:
            print(f"❌ Error cleaning data: {e}")


def main():
    parser = argparse.ArgumentParser(description="Racing News Analyzer Dashboard")
    parser.add_argument("--run", action="store_true", help="Run analysis now")
    parser.add_argument("--clean", type=int, help="Clean data older than N days")
    parser.add_argument("--status", action="store_true", help="Show status only")

    args = parser.parse_args()

    dashboard = NewsAnalyzerDashboard()

    if args.run:
        dashboard.run_analysis_now()
    elif args.clean:
        dashboard.clean_old_data(args.clean)
    elif args.status:
        status = dashboard.get_system_status()
        print(json.dumps(status, indent=2))
    else:
        dashboard.display_dashboard()


if __name__ == "__main__":
    main()
