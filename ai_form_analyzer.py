#!/usr/bin/env python3
"""
AI Horse Form Analyzer
=======================
Uses both Ollama models to analyze complex horse racing form patterns.
"""

import json
import re
import subprocess
import time
from datetime import datetime


class AIFormAnalyzer:
    """Advanced form analysis using AI models."""

    def __init__(self):
        self.coder_model = "qwen2.5-coder:7b"
        self.analysis_model = "jimscard/whiterabbit-neo:13b-q5_K_M"

    def query_model(self, model, prompt, timeout=3600):
        """Query specified Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

    def deep_form_analysis(self, horse_data):
        """Deep analysis of horse form using WhiteRabbit Neo."""
        prompt = f"""Analyze this horse's racing form in detail:

{horse_data}

Provide comprehensive analysis covering:

1. FORM PATTERNS
   - Recent form trend (improving/declining)
   - Distance preferences and optimal trips
   - Surface preferences (turf/dirt/all-weather)
   - Seasonal patterns and peak months

2. CLASS ANALYSIS
   - Current class level and trajectory
   - Performance at different class levels
   - Ability to step up/down in grade

3. PACE ANALYSIS
   - Running style and tactical preferences
   - Early speed vs closing kick
   - Performance in different pace scenarios

4. CONDITIONS ANALYSIS
   - Ground preference (firm/good/soft/heavy)
   - Track configuration preferences
   - Weather impact factors

5. JOCKEY/TRAINER FACTORS
   - Partnership statistics
   - Trainer patterns and timing
   - Jockey booking significance

6. MARKET BEHAVIOR
   - Betting market support patterns
   - Value opportunities based on form

7. RACE FITNESS
   - Current fitness level assessment
   - Layoff impacts and comeback ability
   - Training indicators

Provide a rating out of 10 for this horse's chances in upcoming races."""

        return self.query_model(self.analysis_model, prompt)

    def pattern_recognition(self, multiple_horses_data):
        """Use Qwen2.5-Coder to identify statistical patterns."""
        prompt = f"""Analyze these horse racing records and identify patterns:

{multiple_horses_data}

Using your coding and statistical analysis skills:

1. Create a pattern recognition algorithm in Python pseudocode
2. Identify statistical correlations in the data
3. Find performance predictors
4. Calculate win/place percentages by various factors
5. Identify value betting opportunities
6. Create a ranking algorithm

Focus on mathematical patterns and data-driven insights."""

        return self.query_model(self.coder_model, prompt)

    def comparative_analysis(self, field_data):
        """Compare all horses in a race field."""
        prompt = f"""Compare these horses for an upcoming race:

{field_data}

Provide detailed comparison including:

1. SPEED FIGURES COMPARISON
   - Recent speed ratings
   - Peak performance levels
   - Consistency ratings

2. FORM CYCLES
   - Which horses are peaking
   - Which are declining
   - Which need the run

3. TACTICAL MATCHUP
   - How the race will be run
   - Pace scenario predictions
   - Tactical advantages

4. CONDITIONS MATCHUP
   - Who suits today's conditions
   - Track/distance specialists
   - Class relief/step up

5. VALUE ASSESSMENT
   - Market accuracy analysis
   - Over/under bet recommendations
   - Each-way opportunities

6. CONFIDENCE RATINGS
Rate each horse 1-10 for:
   - Win chance
   - Place chance  
   - Value opportunity

Provide your top 3 selections with reasoning."""

        return self.query_model(self.analysis_model, prompt)

    def ai_form_study(self):
        """Demonstrate comprehensive AI form analysis."""
        print("🔬 AI HORSE FORM ANALYZER")
        print("=" * 40)

        # Sample horse data
        horse_data = """
        HORSE: Thunder Bay (5yo gelding)
        
        RECENT FORM (last 6 runs):
        1. 15Nov23 - Newmarket 1m2f - 3rd of 8 (beaten 2¼L) - Good ground
        2. 28Oct23 - Ascot 1m4f - 1st of 10 (won by 1½L) - Soft ground  
        3. 14Oct23 - York 1m2f - 2nd of 12 (beaten ¾L) - Good to firm
        4. 23Sep23 - Doncaster 1m3f - 4th of 14 (beaten 3L) - Good ground
        5. 08Sep23 - Goodwood 1m2f - 2nd of 9 (beaten neck) - Good ground
        6. 19Aug23 - Sandown 1m1f - 6th of 11 (beaten 6L) - Firm ground
        
        TRAINER: John Smith (23% strike rate, excellent with older horses)
        JOCKEY: P. Murphy (22% strike rate, 3 wins from 8 rides on this horse)
        
        CAREER STATS:
        - 24 runs: 5 wins, 8 places, 11 unplaced
        - Prize money: £145,000
        - Best on good/soft ground (4 wins from 12 runs)
        - Distance: 1m2f-1m4f optimal (5 wins from 14 runs)
        - Class: Performs best in Class 2-3 handicaps
        
        UPCOMING RACE:
        Tomorrow at Kempton - 1m3f Class 2 Handicap - Standard to slow ground
        Current odds: 7/2 (4.5 decimal)
        """

        print("📊 DEEP FORM ANALYSIS...")
        analysis = self.deep_form_analysis(horse_data)
        print(analysis)
        print("\n" + "=" * 60)

        # Multiple horses for pattern recognition
        multiple_horses = """
        STATISTICAL DATA SET:
        
        Horse A: 12 runs, 3 wins (25%), avg speed rating 85, prefers soft ground
        Horse B: 18 runs, 2 wins (11%), avg speed rating 78, distance specialist  
        Horse C: 8 runs, 4 wins (50%), avg speed rating 92, class dropper
        Horse D: 15 runs, 1 win (7%), avg speed rating 75, consistent placer
        Horse E: 20 runs, 5 wins (25%), avg speed rating 88, form cycling up
        
        PERFORMANCE FACTORS:
        - Ground: Firm (40% field win rate), Good (35%), Soft (45%)
        - Distance: 1m (30%), 1m2f (38%), 1m4f+ (42%)
        - Class: Class 1 (15%), Class 2 (25%), Class 3 (35%)
        - Age: 3yo (25%), 4yo (30%), 5yo+ (40%)
        """

        print("🧮 PATTERN RECOGNITION ANALYSIS...")
        patterns = self.pattern_recognition(multiple_horses)
        print(patterns)
        print("\n" + "=" * 60)

        # Full field comparison
        field_data = """
        RACE: 3:30 Kempton - Class 2 Handicap 1m3f (8 runners)
        
        1. THUNDER BAY (7/2) - Detailed form above
        2. LIGHTNING STRIKE (5/2 fav) - 4 wins from 8, consistent, likes track
        3. GOLDEN ARROW (3/1) - Class dropper, 2 wins from 4 at this level
        4. STORM CHASER (9/2) - Improving 4yo, won last twice
        5. DESERT WIND (6/1) - Course winner, needs soft ground (today standard)
        6. MIDNIGHT EXPRESS (8/1) - Inconsistent but capable on day
        7. FIRE MOUNTAIN (12/1) - Outsider, first time tongue-tie
        8. ROYAL FLUSH (16/1) - Long lay-off, needs the run
        
        CONDITIONS: Standard to slow ground, overcast, light wind
        PACE: Likely moderate early pace, strong finish expected
        """

        print("⚖️ COMPARATIVE FIELD ANALYSIS...")
        comparison = self.comparative_analysis(field_data)
        print(comparison)

        print("\n✅ AI FORM ANALYSIS COMPLETE")

    def quick_form_check(self, horse_name):
        """Quick form analysis for a single horse."""
        prompt = f"""Provide a quick form summary for {horse_name}:

Give a concise analysis covering:
- Recent form trend
- Key strengths and weaknesses  
- Optimal conditions
- Current rating out of 10
- One-line summary

Keep it brief but insightful."""

        return self.query_model(self.analysis_model, prompt, timeout=1800)


def main():
    """Main function for AI form analyzer."""
    print("🔬 AI HORSE FORM ANALYZER")
    print("Powered by Dual AI Models")
    print("=" * 40)

    analyzer = AIFormAnalyzer()

    print("\nSelect analysis type:")
    print("1. Full form study demonstration")
    print("2. Quick horse form check")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        analyzer.ai_form_study()
    elif choice == "2":
        horse_name = input("Enter horse name: ").strip()
        if horse_name:
            print(f"\n🔍 Quick analysis for {horse_name}...")
            result = analyzer.quick_form_check(horse_name)
            print(result)
    else:
        print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
