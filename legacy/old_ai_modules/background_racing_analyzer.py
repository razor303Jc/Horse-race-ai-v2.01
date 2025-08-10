#!/usr/bin/env python3
"""
Background Racing Media Analyzer with Web App Reports
====================================================
Uses WhiteRabbit Neo to analyze racing data in background with extended timeouts
and generates HTML reports for web app integration.
"""

import json
import logging
import os
import subprocess
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

# Setup logging for background processing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("racing_analyzer.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class BackgroundRacingAnalyzer:
    """Background racing analyzer with web app report generation."""

    def __init__(self, target_date: str = None, output_dir: str = "reports"):
        self.model_name = "jimscard/whiterabbit-neo:13b-q5_K_M"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Extended timeout for background processing
        self.timeout = 300  # 5 minutes per query

        # Set target date
        if target_date:
            self.target_date = self._parse_date(target_date)
        else:
            self.target_date = date.today()

        self.target_date_str = self.target_date.strftime("%B %d, %Y")
        self.target_date_short = self.target_date.strftime("%Y-%m-%d")
        self.day_of_week = self.target_date.strftime("%A")
        self.results = {}

        logger.info(
            f"Initializing analyzer for {self.target_date_str} ({self.day_of_week})"
        )

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
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y"]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue

                logger.warning(f"Invalid date format: {date_str}, using today")
                return date.today()
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return date.today()

    def query_whiterabbit_background(self, prompt: str, section: str) -> Optional[str]:
        """Query WhiteRabbit with extended timeout for background processing."""
        try:
            logger.info(f"Starting {section} analysis...")

            start_time = time.time()
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout,
            )
            end_time = time.time()

            if result.returncode == 0:
                response = result.stdout.strip()
                response_time = end_time - start_time
                logger.info(f"{section} completed in {response_time:.2f}s")
                return response
            else:
                logger.error(f"{section} failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"{section} timed out after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"{section} exception: {e}")
            return None

    def analyze_social_trends(self):
        """Analyze social media trends with background processing."""
        logger.info("Starting social media trends analysis")

        prompt = f"""Analyze horse racing social media for {self.target_date_str}:

Social media indicates:
- Strong trainer confidence for key runners
- Positive gallops reports from major stables  
- Market movements suggesting informed backing
- Weather conditions favorable for racing
- Jockey bookings showing stable confidence

Provide concise analysis covering:
1. Top horses generating buzz
2. Trainer/jockey confidence signals  
3. Track conditions and weather impact
4. Market intelligence insights
5. Value betting opportunities

Keep response focused and actionable for {self.day_of_week} racing."""

        response = self.query_whiterabbit_background(prompt, "Social Trends")
        if response:
            self.results["social_trends"] = {
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "section": "Social Media Trends",
            }
        return response

    def analyze_expert_tips(self):
        """Analyze expert racing tips and opinions."""
        logger.info("Starting expert tips analysis")

        prompt = f"""Provide expert racing tips for {self.target_date_str}:

Expert analysis focus:
- Key races and competitive fields
- Trainer form and stable news
- Jockey bookings and riding plans
- Track conditions and ground preferences
- Market confidence indicators

Deliver professional tips including:
1. Best bets for major races
2. Each-way value selections
3. Potential upset candidates
4. Accumulator suggestions
5. Horses to follow

Format as expert tipster recommendations for {self.day_of_week}."""

        response = self.query_whiterabbit_background(prompt, "Expert Tips")
        if response:
            self.results["expert_tips"] = {
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "section": "Expert Tips & Analysis",
            }
        return response

    def research_race_cards(self):
        """Research detailed race card analysis."""
        logger.info("Starting race card research")

        prompt = f"""Research race cards for {self.target_date_str}:

Race card analysis should cover:
- Meeting previews and key races
- Field analysis and competitive levels
- Distance and surface suitability
- Recent form and performance trends
- Trainer/jockey combinations

Provide comprehensive research including:
1. Race-by-race previews
2. Form analysis and ratings
3. Speed figures and sectionals
4. Breeding and pedigree insights
5. Strategic betting approaches

Present as detailed race card analysis for {self.day_of_week}."""

        response = self.query_whiterabbit_background(prompt, "Race Cards")
        if response:
            self.results["race_cards"] = {
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "section": "Race Card Research",
            }
        return response

    def generate_betting_guide(self):
        """Generate comprehensive betting guide."""
        logger.info("Starting betting guide generation")

        prompt = f"""Create betting guide for {self.target_date_str}:

Betting strategy elements:
- Risk assessment and bankroll management
- Single bets vs combination wagers
- Value identification techniques
- Market timing considerations
- Profit maximization approaches

Provide detailed guide with:
1. Recommended bet types and stakes
2. Best value opportunities
3. Accumulator and multiple strategies
4. Risk management principles
5. Profit-taking and loss-cutting rules

Format as professional betting advisory for {self.day_of_week}."""

        response = self.query_whiterabbit_background(prompt, "Betting Guide")
        if response:
            self.results["betting_guide"] = {
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "section": "Betting Guide",
            }
        return response

    def generate_web_app_html_report(self):
        """Generate HTML report for web app integration."""
        logger.info("Generating HTML report for web app")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = (
            self.output_dir / f"racing_report_{self.target_date_short}_{timestamp}.html"
        )

        # Generate comprehensive HTML report
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Racing Analysis - {self.target_date_str}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2c3e50;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .date {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 25px;
            background: #fafafa;
            border-radius: 8px;
            border-left: 5px solid #3498db;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.8em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .section-content {{
            white-space: pre-wrap;
            line-height: 1.8;
            color: #34495e;
        }}
        .timestamp {{
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        .bet-tip {{
            background-color: #d4edda;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
                margin: 10px;
            }}
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏇 Horse Racing Analysis Report</h1>
            <div class="date">{self.target_date_str} ({self.day_of_week})</div>
        </div>
"""

        # Add each analysis section
        for section_key, section_data in self.results.items():
            section_title = section_data.get(
                "section", section_key.replace("_", " ").title()
            )
            content = section_data.get("content", "Analysis not available")

            html_content += f"""
        <div class="section">
            <h2>{section_title}</h2>
            <div class="section-content">{content}</div>
        </div>
"""

        # Add footer
        html_content += f"""
        <div class="timestamp">
            Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
            <br>
            Powered by WhiteRabbit Neo AI Racing Analysis
        </div>
    </div>
</body>
</html>"""

        # Save HTML report
        try:
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML report saved: {html_filename}")

            # Also save JSON for API access
            json_filename = (
                self.output_dir
                / f"racing_data_{self.target_date_short}_{timestamp}.json"
            )
            with open(json_filename, "w") as f:
                json.dump(
                    {
                        "date": self.target_date_str,
                        "day": self.day_of_week,
                        "generated": datetime.now().isoformat(),
                        "sections": self.results,
                    },
                    f,
                    indent=2,
                )
            logger.info(f"JSON data saved: {json_filename}")

            return str(html_filename), str(json_filename)

        except Exception as e:
            logger.error(f"Failed to save reports: {e}")
            return None, None

    def run_background_analysis(self):
        """Run complete analysis in background mode."""
        logger.info("Starting background racing analysis")
        start_time = time.time()

        try:
            # Check model availability
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if self.model_name not in result.stdout:
                logger.error(f"Model {self.model_name} not available")
                return False

            logger.info("WhiteRabbit Neo model ready")

            # Run analysis modules with delays
            self.analyze_social_trends()
            time.sleep(5)  # Brief pause between analyses

            self.analyze_expert_tips()
            time.sleep(5)

            self.research_race_cards()
            time.sleep(5)

            self.generate_betting_guide()

            # Generate web reports
            html_file, json_file = self.generate_web_app_html_report()

            total_time = time.time() - start_time
            logger.info(f"Background analysis completed in {total_time:.2f}s")

            if html_file and json_file:
                logger.info(f"Reports generated: {html_file}, {json_file}")
                return True

            return False

        except Exception as e:
            logger.error(f"Background analysis failed: {e}")
            return False


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Background Racing Media Analyzer")
    parser.add_argument(
        "--date", "-d", help="Target date (YYYY-MM-DD, today, tomorrow, etc.)"
    )
    parser.add_argument(
        "--output", "-o", default="reports", help="Output directory for reports"
    )
    parser.add_argument(
        "--background", "-b", action="store_true", help="Run in background mode"
    )

    args = parser.parse_args()

    print("🏇 Background Racing Media Analyzer")
    print("=" * 50)

    analyzer = BackgroundRacingAnalyzer(args.date, args.output)

    if args.background:
        logger.info("Running in background mode...")
        success = analyzer.run_background_analysis()
        if success:
            print("✅ Background analysis completed successfully")
            print(f"📊 Reports saved to: {analyzer.output_dir}")
        else:
            print("❌ Background analysis failed")
    else:
        # Interactive mode
        print(f"Target date: {analyzer.target_date_str}")
        print("Starting background analysis...")
        success = analyzer.run_background_analysis()

        if success:
            print("\n🎉 Analysis completed!")
            print(f"📁 Reports directory: {analyzer.output_dir}")
        else:
            print("\n❌ Analysis failed")


if __name__ == "__main__":
    main()
