#!/usr/bin/env python3
"""
Complete Monte Carlo Demo for Horse Racing AI v2.0

This script demonstrates the full functionality of the Monte Carlo simulation system
integrated with the web GUI, showing z-scores, probability distributions, and betting analysis.
"""

import json
import os
import sys
import time

import requests
from colorama import Back, Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)


def print_banner():
    """Print the demo banner"""
    print(f"{Back.BLUE}{Fore.WHITE}")
    print("=" * 70)
    print("   🏇 HORSE RACING AI v2.0 - MONTE CARLO SIMULATION DEMO   ")
    print("=" * 70)
    print(f"{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}Complete integration of z-scores, probability analysis, and web GUI{Style.RESET_ALL}"
    )
    print()


def check_web_server():
    """Check if the web server is running"""
    try:
        response = requests.get("http://localhost:5001/api/data-stats", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


def get_race_cards():
    """Get available race cards"""
    try:
        response = requests.get("http://localhost:5001/api/race-cards", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"{Fore.RED}Error getting race cards: {e}{Style.RESET_ALL}")
    return []


def run_monte_carlo_analysis(race_index):
    """Run Monte Carlo analysis for a specific race"""
    try:
        response = requests.get(
            f"http://localhost:5001/api/monte-carlo/{race_index}", timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"{Fore.RED}Error running Monte Carlo analysis: {e}{Style.RESET_ALL}")
    return None


def display_z_score_analysis(recommendations):
    """Display detailed z-score analysis"""
    print(f"{Fore.YELLOW}📊 Z-SCORE PERFORMANCE ANALYSIS:{Style.RESET_ALL}")
    print("-" * 70)

    z_score_groups = {
        "Exceptional (Z > +1.5)": [],
        "Strong (Z +1.0 to +1.5)": [],
        "Above Average (Z 0 to +1.0)": [],
        "Below Average (Z -1.0 to 0)": [],
        "Poor (Z < -1.0)": [],
    }

    for horse in recommendations:
        z = horse["z_score"]
        if z > 1.5:
            z_score_groups["Exceptional (Z > +1.5)"].append(horse)
        elif z > 1.0:
            z_score_groups["Strong (Z +1.0 to +1.5)"].append(horse)
        elif z > 0:
            z_score_groups["Above Average (Z 0 to +1.0)"].append(horse)
        elif z > -1.0:
            z_score_groups["Below Average (Z -1.0 to 0)"].append(horse)
        else:
            z_score_groups["Poor (Z < -1.0)"].append(horse)

    for category, horses in z_score_groups.items():
        if horses:
            if "Exceptional" in category:
                color = Fore.RED
                icon = "🔥"
            elif "Strong" in category:
                color = Fore.MAGENTA
                icon = "⚡"
            elif "Above Average" in category:
                color = Fore.GREEN
                icon = "✨"
            elif "Below Average" in category:
                color = Fore.YELLOW
                icon = "⚠️"
            else:
                color = Fore.CYAN
                icon = "💤"

            print(f"{color}{icon} {category}:{Style.RESET_ALL}")
            for horse in horses:
                print(
                    f"  {horse['horse_name']}: Z={horse['z_score']:+.3f}, Win%={horse['probability']*100:.1f}%, Odds={horse['fair_odds']:.2f}"
                )
            print()


def display_betting_strategy(recommendations):
    """Display betting strategy recommendations"""
    print(f"{Fore.GREEN}💰 BETTING STRATEGY RECOMMENDATIONS:{Style.RESET_ALL}")
    print("-" * 70)

    # Top picks based on z-scores and probabilities
    top_horses = sorted(recommendations, key=lambda x: x["z_score"], reverse=True)[:3]

    print(f"{Fore.CYAN}🎯 TOP 3 SELECTIONS (by Z-Score):{Style.RESET_ALL}")
    for i, horse in enumerate(top_horses, 1):
        confidence_text = f"{horse['confidence']*100:.0f}%"
        if horse["z_score"] > 1.0:
            strategy = "🔥 STRONG WIN BET"
            color = Fore.RED
        elif horse["z_score"] > 0:
            strategy = "⚡ VALUE BET"
            color = Fore.GREEN
        else:
            strategy = "💤 AVOID"
            color = Fore.YELLOW

        print(f"{color}#{i} {horse['horse_name']} - {strategy}{Style.RESET_ALL}")
        print(
            f"   Z-Score: {horse['z_score']:+.3f} | Win Probability: {horse['probability']*100:.1f}%"
        )
        print(
            f"   Fair Odds: {horse['fair_odds']:.2f} | Expected Position: {horse['average_position']:.1f}"
        )
        print(
            f"   Confidence: {confidence_text} | Performance Range: {horse['performance_range'][0]:.1f}-{horse['performance_range'][1]:.1f}"
        )
        print()


def run_complete_demo():
    """Run the complete Monte Carlo demonstration"""
    print_banner()

    # Check if web server is running
    print(f"{Fore.CYAN}🌐 Checking web server status...{Style.RESET_ALL}")
    if not check_web_server():
        print(
            f"{Fore.RED}❌ Web server is not running at http://localhost:5001{Style.RESET_ALL}"
        )
        print(
            f"{Fore.YELLOW}💡 Please start the web server with: python web_gui.py{Style.RESET_ALL}"
        )
        return

    print(f"{Fore.GREEN}✅ Web server is running!{Style.RESET_ALL}")
    print()

    # Get race cards
    print(f"{Fore.CYAN}📋 Loading race cards...{Style.RESET_ALL}")
    race_cards = get_race_cards()

    if not race_cards:
        print(f"{Fore.RED}❌ No race cards available{Style.RESET_ALL}")
        return

    print(f"{Fore.GREEN}✅ Found {len(race_cards)} races available{Style.RESET_ALL}")
    print()

    # Display available races
    print(f"{Fore.YELLOW}🏁 AVAILABLE RACES:{Style.RESET_ALL}")
    for i, race in enumerate(race_cards[:3]):  # Show first 3 races
        print(
            f"{i+1}. {race.get('race_id', 'Unknown')} - {race.get('track', 'Unknown Track')}"
        )
        print(
            f"   Distance: {race.get('distance', 'Unknown')}m | Horses: {race.get('num_horses', 'Unknown')}"
        )
    print()

    # Run Monte Carlo analysis on first race
    race_index = 0
    selected_race = race_cards[race_index]

    print(
        f"{Fore.MAGENTA}🎲 Running Monte Carlo Simulation for Race: {selected_race.get('race_id', 'Unknown')}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}⏳ This may take a few seconds for statistical analysis...{Style.RESET_ALL}"
    )

    start_time = time.time()
    monte_carlo_results = run_monte_carlo_analysis(race_index)
    end_time = time.time()

    if not monte_carlo_results:
        print(f"{Fore.RED}❌ Failed to run Monte Carlo analysis{Style.RESET_ALL}")
        return

    analysis_time = end_time - start_time
    print(
        f"{Fore.GREEN}✅ Monte Carlo analysis completed in {analysis_time:.2f} seconds{Style.RESET_ALL}"
    )
    print()

    # Display race information
    race_info = monte_carlo_results["race_info"]
    print(f"{Fore.BLUE}🏇 RACE INFORMATION:{Style.RESET_ALL}")
    print(f"Name: {race_info.get('race_name', 'Unknown')}")
    print(f"Track: {race_info.get('track', 'Unknown')}")
    print(f"Distance: {race_info.get('distance', 'Unknown')}m")
    print(f"Surface: {race_info.get('surface', 'Unknown')}")
    print(f"Prize Money: ${race_info.get('prize_money', 0):,}")
    print()

    # Display z-score analysis
    recommendations = monte_carlo_results["betting_recommendations"]
    display_z_score_analysis(recommendations)

    # Display betting strategy
    display_betting_strategy(recommendations)

    # Performance summary
    print(f"{Fore.BLUE}📈 SIMULATION SUMMARY:{Style.RESET_ALL}")
    print(f"Total Horses Analyzed: {len(recommendations)}")
    print(f"Simulation Method: Monte Carlo with Z-Score Analysis")
    print(f"Statistical Measures: Performance vs Field Average")
    print(f"Confidence Intervals: ±1 Standard Deviation")
    print()

    print(f"{Fore.GREEN}🎯 WEB GUI ACCESS:{Style.RESET_ALL}")
    print(
        f"View full interactive analysis at: {Fore.CYAN}http://localhost:5001{Style.RESET_ALL}"
    )
    print(f"• Select race from dropdown")
    print(f"• Click '🎲 Monte Carlo Simulation' button")
    print(f"• View detailed z-score analysis and betting recommendations")
    print()

    print(
        f"{Back.GREEN}{Fore.WHITE}🏆 MONTE CARLO SIMULATION DEMO COMPLETE! 🏆{Style.RESET_ALL}"
    )


if __name__ == "__main__":
    try:
        run_complete_demo()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Demo error: {e}{Style.RESET_ALL}")
