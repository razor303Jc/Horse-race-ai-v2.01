#!/usr/bin/env python3
"""
Horse Racing Media Analyzer with WhiteRabbit Neo
===============================================
Uses WhiteRabbit Neo AI model to analyze horse racing social media content,
news, and research today's racing insights from various sources.
"""

import json
import re
import subprocess
import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import requests


class RacingMediaAnalyzer:
    """Analyze horse racing media content using WhiteRabbit Neo."""

    def __init__(self, target_date: str = None):
        self.model_name = "jimscard/whiterabbit-neo:13b-q5_K_M"
        
        # Set target date - can be today or any specified date
        if target_date:
            try:
                # Parse the input date
                if target_date.lower() in ['today', 'now']:
                    self.target_date = date.today()
                elif target_date.lower() == 'tomorrow':
                    self.target_date = date.today() + timedelta(days=1)
                elif target_date.lower() == 'yesterday':
                    self.target_date = date.today() - timedelta(days=1)
                else:
                    # Try to parse various date formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%B %d, %Y']:
                        try:
                            self.target_date = datetime.strptime(target_date, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        print(f"❌ Invalid date format: {target_date}")
                        print("💡 Use formats like: 2025-08-09, 09/08/2025, or 'today'")
                        self.target_date = date.today()
            except Exception as e:
                print(f"❌ Date parsing error: {e}")
                self.target_date = date.today()
        else:
            self.target_date = date.today()
        
        self.target_date_str = self.target_date.strftime("%B %d, %Y")
        self.target_date_short = self.target_date.strftime("%Y-%m-%d")
        self.day_of_week = self.target_date.strftime("%A")
        self.results = {}
        
        print(f"📅 Analyzing racing for: {self.target_date_str} ({self.day_of_week})")

    def query_whiterabbit(self, prompt: str, timeout: int = 120) -> Optional[str]:
        """Query WhiteRabbit Neo model with a prompt."""
        try:
            print(f"🤖 Querying WhiteRabbit Neo...")
            print("🔄 Analyzing racing media... (this may take a moment)")

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
            print("⏰ Request timed out after 2 minutes")
            return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def analyze_twitter_trends(self):
        """Analyze simulated Twitter/X racing trends for today."""
        print("\n" + "=" * 60)
        print("🐦 ANALYZING TWITTER/X RACING TRENDS")
        print("=" * 60)

        # Simulate current racing Twitter content
        twitter_content = f"""
    def analyze_twitter_trends(self):
        """Analyze simulated Twitter/X racing trends for target date."""
        print("
" + "="*60)
        print("🐦 ANALYZING TWITTER/X RACING TRENDS")
        print(f"📅 Date: {self.target_date_str}")
        print("="*60)

        # Simulate current racing Twitter content for target date
        twitter_content = f"""
        Analyze these Twitter/X posts about horse racing for {self.target_date_str} ({self.day_of_week}):

        @RacingPost: "BREAKING: Golden Thunder showing excellent form in morning gallops. 
        Jockey confidence high for 3:30 race at Newmarket #{self.target_date_short}"

        @TipsterKing: "🔥 HOT TIP: Lightning Bolt each-way value in the 2:15. 
        Recent form suggests big run coming. Trainer bullish! #Racing #{self.day_of_week}"

        @WeatherRacing: "Track conditions update for {self.target_date_str}: 
        Newmarket GOOD, Ascot GOOD TO SOFT, York SOFT. Weather looks stable."

        @JockeyInsider: "Word from the weighing room: Frankie Dettori confident 
        about his rides on {self.day_of_week}. Mentions stable is 'very happy' with Storm Chaser"

        @BloodstockAgent: "Market movers for {self.target_date_str}: 
        Midnight Express drifting out to 8/1 from 5/1. Something brewing?"

        @RacingTelegraph: "Trainer quotes: 'Desert Wind has never been better' 
        - John Gosden ahead of {self.day_of_week}'s Group 2. Expecting big performance"

        Based on this social media activity for {self.target_date_str}, provide:
        1. Key horses to watch on {self.day_of_week}
        2. Market intelligence insights
        3. Track condition impacts
        4. Potential value bets
        5. Red flags or concerns
        """"""

        response = self.query_whiterabbit(twitter_content)
        if response:
            print(response)
            self.results["twitter_analysis"] = response
            return response
        return None

    def analyze_racing_news(self):
        """Analyze racing news and expert opinions."""
        print("\n" + "=" * 60)
        print("📰 ANALYZING RACING NEWS & EXPERT OPINIONS")
        print("=" * 60)

        news_content = f"""
        Analyze these racing news headlines and expert opinions for {self.today}:
        
        RACING POST HEADLINES:
        - "Gosden duo head strong Newmarket field in Group 2 showdown"
        - "Dettori seeking Group 1 redemption after Goodwood disappointment"
        - "Ascot conditions favor early pace - front runners to prosper"
        - "York's testing ground could spring surprises in handicap"
        
        EXPERT TIPS & ANALYSIS:
        "The ground at York has dried significantly overnight but remains on the softer side. 
        This will suit the more genuine stayers in the longer races. Watch for horses that 
        have shown form on similar conditions." - Matt Chapman
        
        "Market confidence is high around the Gosden-trained runners today. The stable is 
        in excellent form and their two-year-olds in particular have been showing 
        significant improvement." - Ruby Walsh
        
        "Weather forecast shows possible rain later, but tracks should hold up well. 
        The key races are the 2:15 at Ascot and 3:30 at Newmarket - both look competitive." - Timeform
        
        Provide analysis on:
        1. Expert consensus picks
        2. Weather and ground impact
        3. Trainer form patterns
        4. Key races to focus on
        5. Contrarian opportunities
        """

        response = self.query_whiterabbit(news_content)
        if response:
            print(response)
            self.results["news_analysis"] = response
            return response
        return None

    def analyze_betting_patterns(self):
        """Analyze betting market movements and patterns."""
        print("\n" + "=" * 60)
        print("💰 ANALYZING BETTING MARKET PATTERNS")
        print("=" * 60)

        betting_content = f"""
        Analyze these betting market movements for {self.today}:
        
        MARKET MOVERS:
        - Lightning Bolt: 6/1 → 4/1 (shortened) - Ascot 2:15
        - Midnight Express: 5/1 → 8/1 (drifted) - Newmarket 3:30
        - Golden Thunder: 3/1 → 5/2 (shortened) - Newmarket 3:30
        - Storm Chaser: 7/2 → 3/1 (drifted) - York 4:00
        - Desert Wind: 2/1 fav → 6/4 fav (still favorite but eased)
        
        EXCHANGE DATA:
        - Heavy backing for Lightning Bolt on Betfair
        - Significant laying of Midnight Express
        - Professional money on Desert Wind despite drift
        - Each-way interest in outsiders at York
        
        BOOKMAKER INTEL:
        "We've seen consistent support for the Gosden horses today, but interestingly 
        some of the market leaders are being opposed by what looks like informed money."
        
        "The York handicap is seeing plenty of each-way interest in the bigger prices. 
        Suggests punters think it's a wide-open contest."
        
        Analyze:
        1. Smart money movements
        2. Value opportunities
        3. Market confidence levels
        4. Professional vs public betting
        5. Each-way value spots
        """

        response = self.query_whiterabbit(betting_content)
        if response:
            print(response)
            self.results["betting_analysis"] = response
            return response
        return None

    def research_todays_racing(self):
        """Comprehensive research on today's key races."""
        print("\n" + "=" * 60)
        print("🏇 RESEARCHING TODAY'S KEY RACES")
        print("=" * 60)

        racing_research = f"""
        Provide comprehensive research for today's ({self.today}) key horse racing:
        
        TODAY'S MAJOR RACES:
        
        🏆 2:15 Ascot - Class 2 Handicap (1m 2f)
        Field: 12 runners, competitive handicap
        Key contenders: Lightning Bolt, Silver Streak, Dancing Queen
        Track: Good to Soft, suits versatile types
        
        🏆 3:30 Newmarket - Group 2 Stakes (1m)
        Field: 8 runners, quality field
        Key contenders: Golden Thunder, Midnight Express, Desert Wind
        Track: Good, will suit speed horses
        
        🏆 4:00 York - Class 3 Handicap (1m 6f)
        Field: 14 runners, wide open contest
        Key contenders: Storm Chaser, Northern Light, Royal Command
        Track: Soft, stamina test
        
        Based on your racing expertise, provide:
        
        1. **Race-by-race predictions** with reasoning
        2. **Best bets** for each race (win/each-way)
        3. **Potential upsets** to watch for
        4. **Jockey/trainer combinations** in form
        5. **Track bias** and tactical insights
        6. **Value bets** across all meetings
        7. **Accumulator suggestions** for today
        8. **Safety nets** and risk management
        
        Consider all factors: form, ground, distance, jockey booking, trainer record, 
        market confidence, and any insider intelligence from the social media analysis.
        """

        response = self.query_whiterabbit(racing_research)
        if response:
            print(response)
            self.results["racing_research"] = response
            return response
        return None

    def generate_final_recommendations(self):
        """Generate final betting recommendations based on all analysis."""
        print("\n" + "=" * 60)
        print("🎯 FINAL RECOMMENDATIONS SYNTHESIS")
        print("=" * 60)

        synthesis_prompt = f"""
        Based on all the racing analysis for {self.today}, synthesize the information 
        from social media trends, expert opinions, betting patterns, and race research 
        to provide final recommendations:
        
        SYNTHESIS REQUEST:
        Taking into account:
        - Twitter/X sentiment and insider tips
        - Expert opinions and track conditions
        - Betting market intelligence
        - Detailed race analysis
        
        Provide:
        1. **TOP 3 BEST BETS** for today (with confidence ratings)
        2. **VALUE PLAYS** - overlooked horses with potential
        3. **ACCUMULATOR** - realistic multi-race bet
        4. **EACH-WAY SPECIALS** - bigger price chances
        5. **AVOID LIST** - horses to steer clear of
        6. **BANKROLL STRATEGY** - how to distribute stakes
        7. **CONTINGENCY PLANS** - if main selections don't run
        
        Present as a professional tipster would, with clear reasoning and 
        risk assessment for each recommendation.
        """

        response = self.query_whiterabbit(synthesis_prompt)
        if response:
            print(response)
            self.results["final_recommendations"] = response
            return response
        return None

    def save_analysis_report(self):
        """Save all analysis to a comprehensive report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"racing_media_analysis_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(
                    {
                        "date": self.today,
                        "timestamp": timestamp,
                        "analysis": self.results,
                    },
                    f,
                    indent=2,
                )
            print(f"\n💾 Complete analysis saved to {filename}")

            # Also create a readable text report
            text_filename = f"racing_analysis_report_{timestamp}.txt"
            with open(text_filename, "w") as f:
                f.write(f"HORSE RACING MEDIA ANALYSIS REPORT\n")
                f.write(f"Date: {self.today}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                for section, content in self.results.items():
                    f.write(f"{section.upper().replace('_', ' ')}\n")
                    f.write("-" * 40 + "\n")
                    f.write(content + "\n\n")

            print(f"📄 Readable report saved to {text_filename}")

        except Exception as e:
            print(f"❌ Failed to save analysis: {e}")

    def run_complete_analysis(self):
        """Run the complete racing media analysis."""
        print("🏇 RACING MEDIA ANALYZER WITH WHITERABBIT NEO")
        print(f"📅 Analyzing racing for {self.today}")
        print("=" * 60)

        try:
            # Check if WhiteRabbit is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if self.model_name not in result.stdout:
                print(f"❌ {self.model_name} not available")
                return

            print("✅ WhiteRabbit Neo is ready for analysis")

            # Run all analysis modules
            self.analyze_twitter_trends()
            time.sleep(2)  # Brief pause between analyses

            self.analyze_racing_news()
            time.sleep(2)

            self.analyze_betting_patterns()
            time.sleep(2)

            self.research_todays_racing()
            time.sleep(2)

            self.generate_final_recommendations()

            # Save comprehensive report
            self.save_analysis_report()

            print("\n" + "=" * 60)
            print("🎉 COMPLETE RACING ANALYSIS FINISHED!")
            print("=" * 60)
            print("📊 All modules completed successfully")
            print("💡 Check the generated reports for detailed insights")

        except KeyboardInterrupt:
            print("\n⏹️  Analysis interrupted by user")
        except Exception as e:
            print(f"\n❌ Analysis error: {e}")


def main():
    """Main function."""
    print("🐦 Horse Racing Media Analyzer")
    print("Using WhiteRabbit Neo for racing intelligence")
    print("=" * 50)

    analyzer = RacingMediaAnalyzer()

    print("\nWhat would you like to analyze?")
    print("1. Complete analysis (all modules)")
    print("2. Twitter/X trends only")
    print("3. Racing news only")
    print("4. Betting patterns only")
    print("5. Today's racing research")
    print("6. Final recommendations")

    choice = input("\nEnter your choice (1-6): ").strip()

    if choice == "1":
        analyzer.run_complete_analysis()
    elif choice == "2":
        analyzer.analyze_twitter_trends()
    elif choice == "3":
        analyzer.analyze_racing_news()
    elif choice == "4":
        analyzer.analyze_betting_patterns()
    elif choice == "5":
        analyzer.research_todays_racing()
    elif choice == "6":
        analyzer.generate_final_recommendations()
    else:
        print("Invalid choice. Running complete analysis...")
        analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
