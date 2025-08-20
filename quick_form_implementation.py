#!/usr/bin/env python3
"""
⚡ QUICK START GUIDE - Form Analysis Implementation
=================================================

This is the first immediate opportunity task - 2 hours estimated.
Let's implement basic form analysis to improve horse differentiation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class QuickFormAnalyzer:
    """Quick implementation of basic form analysis."""

    def __init__(self):
        self.form_weights = {
            "last_run": 0.5,  # Most recent run (50%)
            "second_last": 0.3,  # Second last run (30%)
            "third_last": 0.2,  # Third last run (20%)
        }

    def calculate_basic_form_score(self, horse_data):
        """Calculate a basic form score from recent runs."""
        try:
            # This would normally query recent race results
            # For quick implementation, we'll use power ratings as proxy

            power_rating = horse_data.get("power_rating", 50.0)
            speed_figure = horse_data.get("speed_figure", 50.0)
            win_probability = horse_data.get("win_probability", 0.1)

            # Basic form calculation
            form_score = (
                power_rating * 0.4 + speed_figure * 0.4 + (win_probability * 100) * 0.2
            )

            # Normalize to 0-100 scale
            form_score = max(0, min(100, form_score))

            return form_score

        except Exception:
            return 50.0  # Default average form

    def add_form_trend_indicator(self, form_scores):
        """Add form trend (improving/declining)."""
        if len(form_scores) < 2:
            return "STABLE"

        recent_avg = np.mean(form_scores[:2])
        older_avg = (
            np.mean(form_scores[2:]) if len(form_scores) > 2 else form_scores[-1]
        )

        improvement = recent_avg - older_avg

        if improvement > 5:
            return "IMPROVING"
        elif improvement < -5:
            return "DECLINING"
        else:
            return "STABLE"

    def calculate_form_confidence(self, form_score, trend):
        """Calculate confidence in form assessment."""
        base_confidence = 0.6

        # Boost confidence for extreme form scores
        if form_score > 80 or form_score < 30:
            base_confidence += 0.2

        # Adjust for trend
        if trend == "IMPROVING":
            base_confidence += 0.1
        elif trend == "DECLINING":
            base_confidence -= 0.1

        return min(0.95, max(0.3, base_confidence))


def integrate_form_analysis_quick():
    """Quick integration steps for form analysis."""

    print("⚡ QUICK FORM ANALYSIS IMPLEMENTATION GUIDE")
    print("=" * 50)

    steps = [
        {
            "step": 1,
            "title": "Add Form Calculation to Generator",
            "code": """
def add_form_analysis(self, df):
    \"\"\"Add basic form analysis to dataframe.\"\"\"
    form_analyzer = QuickFormAnalyzer()
    
    form_scores = []
    form_trends = []
    form_confidences = []
    
    for _, horse in df.iterrows():
        # Calculate form score
        form_score = form_analyzer.calculate_basic_form_score(horse.to_dict())
        form_scores.append(form_score)
        
        # For quick implementation, trend is based on power vs speed
        power_speed_diff = horse['power_rating'] - horse['speed_figure']
        if power_speed_diff > 10:
            trend = "IMPROVING"
        elif power_speed_diff < -10:
            trend = "DECLINING"  
        else:
            trend = "STABLE"
        form_trends.append(trend)
        
        # Calculate confidence
        confidence = form_analyzer.calculate_form_confidence(form_score, trend)
        form_confidences.append(confidence)
    
    df['form_score'] = form_scores
    df['form_trend'] = form_trends
    df['form_confidence'] = form_confidences
    
    return df
            """,
            "time": "30 minutes",
        },
        {
            "step": 2,
            "title": "Update Feature Engineering",
            "code": """
# In engineer_enhanced_features method, add:

# Form analysis
df = self.add_form_analysis(df)

# Form-based adjustments
df["form_adjusted_power"] = df["power_rating"] * (df["form_score"] / 100.0)
df["form_weighted_prob"] = df["win_probability"] * (df["form_confidence"])

# Form rank within race
race_groups = df.groupby(["course", "race_number"])
df["form_rank"] = race_groups["form_score"].rank(ascending=False)
            """,
            "time": "20 minutes",
        },
        {
            "step": 3,
            "title": "Update Ensemble Predictions",
            "code": """
# In ensemble probability calculations:

df["enhanced_win_prob"] = (
    df["win_probability"] * 0.3 +
    (1.0 / df["win_odds"]) * 0.25 +
    (df["power_rating"] / 100.0) * 0.25 +
    (df["form_score"] / 100.0) * 0.2  # Add form component
)

# Form-adjusted confidence
df["prediction_confidence"] = df["prediction_confidence"] * df["form_confidence"]
            """,
            "time": "15 minutes",
        },
        {
            "step": 4,
            "title": "Update Report Format",
            "code": """
# In format_improved_report method, add form info:

report += f"     Power: {selection['power_rating']:.1f} | Speed: {selection['speed_figure']:.1f} | Form: {selection.get('form_score', 50):.1f} | Market: #{selection['market_rank']}\\n"
report += f"     Trend: {selection.get('form_trend', 'STABLE')} | Value Score: {selection['value_score']:.2f} | {selection['value_category']}\\n"
            """,
            "time": "15 minutes",
        },
    ]

    total_time = 0
    for step_info in steps:
        print(f"\n📋 STEP {step_info['step']}: {step_info['title']}")
        print(f"⏱️ Time: {step_info['time']}")
        print("💻 Code to add:")
        print(step_info["code"])

        # Extract time in minutes
        time_str = step_info["time"]
        minutes = int(time_str.split()[0])
        total_time += minutes

    print(f"\n⏱️ TOTAL ESTIMATED TIME: {total_time} minutes ({total_time/60:.1f} hours)")
    print("\n🎯 EXPECTED IMPROVEMENTS:")
    print("  • Better horse differentiation based on recent form")
    print("  • Form trend indicators (improving/declining/stable)")
    print("  • Enhanced confidence scoring with form weighting")
    print("  • Reduced reliance on default/similar values")

    print(f"\n🚀 NEXT STEPS:")
    print("1. Copy QuickFormAnalyzer class to improved_ai_selections_generator.py")
    print("2. Implement the 4 integration steps above")
    print("3. Test with real data")
    print("4. Mark task as completed in task manager")


if __name__ == "__main__":
    integrate_form_analysis_quick()
