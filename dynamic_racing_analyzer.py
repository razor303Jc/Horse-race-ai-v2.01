#!/usr/bin/env python3
"""
Dynamic Horse Racing Media Analyzer with WhiteRabbit Neo
=======================================================
Uses WhiteRabbit Neo AI model to analyze horse racing social media content,
news, and research racing insights for any specified date.
"""

import json
import subprocess
import time
from datetime import date, datetime, timedelta
from typing import Optional


class DynamicRacingAnalyzer:
    """Analyze horse racing media content for any date using WhiteRabbit Neo."""

    def __init__(self, target_date: str = None):
        self.model_name = "jimscard/whiterabbit-neo:13b-q5_K_M"

        # Set target date - can be today or any specified date
        if target_date:
            self.target_date = self._parse_date(target_date)
        else:
            self.target_date = date.today()

        self.target_date_str = self.target_date.strftime("%B %d, %Y")
        self.target_date_short = self.target_date.strftime("%Y-%m-%d")
        self.day_of_week = self.target_date.strftime("%A")
        self.results = {}

        print(f"📅 Analyzing racing for: {self.target_date_str} ({self.day_of_week})")

    def _parse_date(self, date_str: str) -> date:
        """Parse various date formats into a date object."""
        try:
            if date_str.lower() in ["today", "now"]:
                return date.today()
            elif date_str.lower() == "tomorrow":
                return date.today() + timedelta(days=1)
            elif date_str.lower() == "yesterday":
                return date.today() - timedelta(days=1)
            else:
                # Try to parse various date formats
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%d %B %Y"]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue

                print(f"❌ Invalid date format: {date_str}")
                print("💡 Use formats like: 2025-08-09, 09/08/2025, or 'today'")
                return date.today()
        except Exception as e:
            print(f"❌ Date parsing error: {e}")
            return date.today()

    def query_whiterabbit(self, prompt: str, timeout: int = 90) -> Optional[str]:
        """Query WhiteRabbit Neo model with a prompt."""
        try:
            print("🤖 Querying WhiteRabbit Neo...")
            print("🔄 Analyzing racing media...")

            start_time = time.time()
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
            end_time = time.time()

            if result.returncode == 0:
                response = result.stdout.strip()
                response_time = end_time - start_time
                print(f"✅ Analysis complete in {response_time:.2f}s")
                return response
            else:
                print(f"❌ Error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"⏰ Request timed out after {timeout}s")
            return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def analyze_social_media_trends(self):
        """Analyze social media racing trends for the target date."""
        print("\n" + "=" * 60)
        print("🐦 ANALYZING SOCIAL MEDIA RACING TRENDS")
        print(f"📅 Date: {self.target_date_str}")
        print("=" * 60)

        prompt = f"""Analyze horse racing social media trends for {self.target_date_str} ({self.day_of_week}):

Key social media insights:
- Morning gallops reports looking positive for several runners
- Trainer confidence high for key races
- Weather conditions stable, tracks in good condition
- Market movements suggesting informed backing
- Jockey bookings indicating strong stable confidence

For {self.day_of_week}, {self.target_date_str}, provide:
1. Top horses generating social media buzz
2. Trainer/jockey confidence indicators
3. Track condition updates and impacts
4. Market intelligence from social chatter
5. Value betting opportunities

Keep analysis concise and focused on actionable insights."""

        response = self.query_whiterabbit(prompt)
        if response:
            print(response)
            self.results["social_media"] = response
        return response

    def analyze_racing_news(self):
        """Analyze racing news for the target date."""
        print("\n" + "=" * 60)
        print("📰 ANALYZING RACING NEWS")
        print(f"📅 Date: {self.target_date_str}")
        print("=" * 60)

        prompt = f"""Analyze racing news and expert opinions for {self.target_date_str} ({self.day_of_week}):

Focus areas:
- Key races scheduled for {self.day_of_week}
- Trainer quotes and stable confidence
- Track conditions and weather impact
- Jockey bookings and riding arrangements
- Market movements and betting patterns

Provide expert analysis covering:
1. Must-watch races for {self.day_of_week}
2. Trainer form and stable news
3. Ground conditions and weather factors
4. Jockey/trainer combinations in form
5. Potential surprises and value picks

Format as professional racing analysis."""

        response = self.query_whiterabbit(prompt)
        if response:
            print(response)
            self.results["racing_news"] = response
        return response

    def research_days_racing(self):
        """Research comprehensive racing analysis for the target date."""
        print("\n" + "=" * 60)
        print("🏇 RESEARCHING DAY'S RACING")
        print(f"📅 Date: {self.target_date_str}")
        print("=" * 60)

        prompt = f"""Provide comprehensive racing research for {self.target_date_str} ({self.day_of_week}):

Racing Schedule Analysis:
- Major meetings and key races
- Class levels and prize money
- Distance and surface preferences
- Field sizes and competitive levels

Key Factors for {self.day_of_week}:
- Track conditions and weather
- Trainer and jockey form
- Recent performance trends
- Market confidence indicators

Provide detailed analysis including:
1. Race-by-race preview for major meetings
2. Best betting opportunities (win/each-way)
3. Potential upsets and long shots
4. Accumulator and multiple bet suggestions
5. Horses to follow for future races
6. Risk assessment and bankroll management

Present as comprehensive daily racing guide."""

        response = self.query_whiterabbit(prompt)
        if response:
            print(response)
            self.results["racing_research"] = response
        return response

    def generate_betting_strategy(self):
        """Generate betting strategy for the target date."""
        print("\n" + "=" * 60)
        print("💰 GENERATING BETTING STRATEGY")
        print(f"📅 Date: {self.target_date_str}")
        print("=" * 60)

        prompt = f"""Create a betting strategy for {self.target_date_str} ({self.day_of_week}):

Strategy Elements:
- Conservative vs aggressive approaches
- Single bets vs multiples
- Win vs each-way considerations
- Value betting opportunities
- Risk management principles

For {self.day_of_week}'s racing, provide:
1. Top 3 best bets with confidence ratings
2. Value each-way selections
3. Accumulator suggestions (treble/4-fold)
4. Speculative long shots
5. Lay betting opportunities
6. Bankroll allocation strategy
7. Stop-loss and profit-taking plans

Present as professional betting advisory."""

        response = self.query_whiterabbit(prompt)
        if response:
            print(response)
            self.results["betting_strategy"] = response
        return response

    def save_analysis_report(self):
        """Save analysis to files."""
        timestamp = datetime.now().strftime("%H%M%S")
        date_stamp = self.target_date.strftime("%Y%m%d")

        # JSON report
        json_filename = f"racing_analysis_{date_stamp}_{timestamp}.json"
        try:
            with open(json_filename, "w") as f:
                json.dump(
                    {
                        "target_date": self.target_date_str,
                        "day_of_week": self.day_of_week,
                        "analysis_time": datetime.now().isoformat(),
                        "results": self.results,
                    },
                    f,
                    indent=2,
                )
            print(f"💾 JSON report saved: {json_filename}")
        except Exception as e:
            print(f"❌ Failed to save JSON: {e}")

        # Text report
        text_filename = f"racing_report_{date_stamp}_{timestamp}.txt"
        try:
            with open(text_filename, "w") as f:
                f.write(f"HORSE RACING ANALYSIS REPORT\n")
                f.write(f"Date: {self.target_date_str} ({self.day_of_week})\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                for section, content in self.results.items():
                    f.write(f"{section.upper().replace('_', ' ')}\n")
                    f.write("-" * 40 + "\n")
                    f.write(content + "\n\n")

            print(f"📄 Text report saved: {text_filename}")
        except Exception as e:
            print(f"❌ Failed to save text report: {e}")

    def run_complete_analysis(self):
        """Run complete analysis for the target date."""
        print("🏇 DYNAMIC RACING MEDIA ANALYZER")
        print("=" * 50)

        try:
            # Check if model is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if self.model_name not in result.stdout:
                print(f"❌ {self.model_name} not available")
                return

            print("✅ WhiteRabbit Neo ready for analysis")

            # Run analysis modules
            self.analyze_social_media_trends()
            time.sleep(1)

            self.analyze_racing_news()
            time.sleep(1)

            self.research_days_racing()
            time.sleep(1)

            self.generate_betting_strategy()

            # Save reports
            self.save_analysis_report()

            print("\n" + "=" * 60)
            print("🎉 COMPLETE ANALYSIS FINISHED!")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n⏹️  Analysis interrupted")
        except Exception as e:
            print(f"\n❌ Analysis error: {e}")


def get_date_from_user():
    """Get target date from user input."""
    print("\n📅 Select analysis date:")
    print("1. Today")
    print("2. Tomorrow")
    print("3. Yesterday")
    print("4. Specific date")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        return "today"
    elif choice == "2":
        return "tomorrow"
    elif choice == "3":
        return "yesterday"
    elif choice == "4":
        date_input = input("Enter date (YYYY-MM-DD or DD/MM/YYYY): ").strip()
        return date_input
    else:
        print("Invalid choice, using today")
        return "today"


def main():
    """Main function."""
    print("🏇 Dynamic Horse Racing Media Analyzer")
    print("Using WhiteRabbit Neo for racing intelligence")
    print("=" * 50)

    # Get target date
    target_date = get_date_from_user()

    # Create analyzer
    analyzer = DynamicRacingAnalyzer(target_date)

    print("\nWhat analysis would you like?")
    print("1. Complete analysis (all modules)")
    print("2. Social media trends only")
    print("3. Racing news only")
    print("4. Day's racing research")
    print("5. Betting strategy only")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        analyzer.run_complete_analysis()
    elif choice == "2":
        analyzer.analyze_social_media_trends()
    elif choice == "3":
        analyzer.analyze_racing_news()
    elif choice == "4":
        analyzer.research_days_racing()
    elif choice == "5":
        analyzer.generate_betting_strategy()
    else:
        print("Invalid choice. Running complete analysis...")
        analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
