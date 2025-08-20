#!/usr/bin/env python3
"""
🏇 Horse Racing AI Pipeline Analysis Report
===========================================

Comprehensive step-by-step analysis of the automated pipeline system
with timing, functionality, and data requirements assessment.
"""

import psycopg2
from datetime import datetime, date, timedelta
import json
import os
from pathlib import Path


def generate_pipeline_report():
    """Generate comprehensive pipeline analysis report"""

    print("🏇 HORSE RACING AI V2.03 - PIPELINE ANALYSIS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')}")
    print()

    # Check system status first
    system_status = check_system_status()

    print("📋 EXECUTIVE SUMMARY")
    print("-" * 40)
    print(
        f"• System Status: {'🟢 OPERATIONAL' if system_status['database_connected'] else '🔴 ISSUES DETECTED'}"
    )
    print(
        f"• Data Availability: {system_status['total_races']:,} races, {system_status['total_records']:,} records"
    )
    print(f"• Today's Races: {system_status['todays_races']} races available")
    print(
        f"• Data Range: {system_status['date_range'][0]} to {system_status['date_range'][1]}"
    )

    if system_status["todays_races"] == 0:
        print("\n⚠️  CRITICAL NOTICE:")
        print("   No races available for today - AI selections cannot be generated")
        print("   This could indicate:")
        print("   • No racing scheduled for today (normal on some days)")
        print("   • Auto-downloader hasn't completed today's run")
        print("   • Data processing pipeline needs to be triggered")

    print("\n\n🔄 PIPELINE STAGE ANALYSIS")
    print("=" * 70)

    stages = get_pipeline_stages()

    for i, stage in enumerate(stages, 1):
        print(f"\n{i}. {stage['name']}")
        print(f"   {'─' * (len(stage['name']) + 3)}")
        print(f"   ⏰ Timing: {stage['timing']}")
        print(f"   🎯 Purpose: {stage['purpose']}")
        print(f"   🔧 What it does: {stage['description']}")
        print(f"   📊 Why it's needed: {stage['why_needed']}")
        print(f"   ⚡ Criticality: {stage['criticality']}")
        print(f"   📁 Input: {stage['input']}")
        print(f"   📤 Output: {stage['output']}")
        print(f"   🔗 Dependencies: {stage['dependencies']}")

        # Check if stage has run today
        stage_status = check_stage_status(stage["name"])
        if stage_status:
            print(f"   ✅ Status: {stage_status}")
        else:
            print(f"   ❓ Status: Not executed today")

    print("\n\n📊 DATA SUFFICIENCY ANALYSIS")
    print("=" * 70)

    data_analysis = analyze_data_sufficiency()

    print(f"Current Data Status:")
    print(f"• Historical Races: {data_analysis['historical_races']:,}")
    print(f"• Training Records: {data_analysis['training_records']:,}")
    print(f"• Unique Horses: {data_analysis['unique_horses']:,}")
    print(f"• Unique Jockeys: {data_analysis['unique_jockeys']:,}")
    print(f"• Unique Trainers: {data_analysis['unique_trainers']:,}")

    print(f"\nML Model Requirements:")
    print(f"• Minimum for basic predictions: {data_analysis['min_basic']} records")
    print(f"• Recommended for accuracy: {data_analysis['min_recommended']} records")
    print(f"• Current status: {data_analysis['ml_readiness']}")

    print(f"\nToday's Selection Capability:")
    if data_analysis["can_make_selections"]:
        print("✅ System CAN generate AI selections")
        print(f"   • {data_analysis['todays_races']} races available")
        print(f"   • {data_analysis['training_records']:,} training records")
        print(f"   • Models trained and ready")
    else:
        print("❌ System CANNOT generate AI selections")
        print(f"   Reasons: {', '.join(data_analysis['blocking_reasons'])}")
        print(f"   Recommendations: {', '.join(data_analysis['recommendations'])}")

    print("\n\n🕐 TYPICAL DAILY TIMELINE")
    print("=" * 70)

    timeline = get_daily_timeline()

    for time_slot in timeline:
        print(f"{time_slot['time']:>8} | {time_slot['activity']}")
        if time_slot.get("note"):
            print(f"{'':>8} | 💡 {time_slot['note']}")

    print("\n\n🚨 ISSUE DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 70)

    issues = diagnose_issues(system_status, data_analysis)

    if issues:
        for issue in issues:
            print(f"\n⚠️  {issue['severity']}: {issue['title']}")
            print(f"   Problem: {issue['description']}")
            print(f"   Impact: {issue['impact']}")
            print(f"   Solution: {issue['solution']}")
    else:
        print("✅ No critical issues detected - system operating normally")

    print(f"\n\n📋 SUMMARY & NEXT STEPS")
    print("=" * 70)

    if system_status["todays_races"] > 0:
        print("🎯 SYSTEM IS READY FOR AI SELECTIONS")
        print("   Next steps:")
        print("   1. Access web dashboard: http://localhost:3000")
        print("   2. View today's races and predictions")
        print("   3. Monitor performance and results")
    else:
        print("⏳ SYSTEM WAITING FOR TODAY'S DATA")
        print("   Next steps:")
        print("   1. Wait for auto-downloader (runs at 00:01 daily)")
        print("   2. Monitor pipeline logs for completion")
        print("   3. Check back in 30-60 minutes after data download")
        print("   4. If urgent, manually trigger data download")

    print(f"\n📞 Support Information:")
    print(f"   • Pipeline logs: /app/logs/")
    print(f"   • Database status: PostgreSQL on port 5434")
    print(f"   • Web interface: http://localhost:3000")
    print(f"   • Docker status: docker-compose ps")


def check_system_status():
    """Check overall system status"""
    status = {
        "database_connected": False,
        "total_races": 0,
        "total_records": 0,
        "todays_races": 0,
        "date_range": (None, None),
    }

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()

        status["database_connected"] = True

        # Get basic counts
        cursor.execute("SELECT COUNT(*) FROM races")
        status["total_races"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        status["total_records"] = cursor.fetchone()[0]

        # Get date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM races")
        status["date_range"] = cursor.fetchone()

        # Check today's races
        today = date.today()
        cursor.execute("SELECT COUNT(*) FROM races WHERE date = %s", (today,))
        status["todays_races"] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database connection error: {e}")

    return status


def get_pipeline_stages():
    """Define all pipeline stages with detailed information"""
    return [
        {
            "name": "AUTO-DOWNLOADER TRIGGER",
            "timing": "00:01 Daily (Scheduled)",
            "purpose": "Data Acquisition",
            "description": "Downloads fresh racing data from external sources including race cards, results, and form data",
            "why_needed": "System needs current data to make accurate predictions - without fresh data, AI cannot provide today's selections",
            "criticality": "🔴 CRITICAL - System fails without this",
            "input": "External racing data sources (APIs, feeds)",
            "output": "Raw CSV files in daily_downloads directory",
            "dependencies": "Internet connection, external data sources available",
        },
        {
            "name": "DATA VALIDATION",
            "timing": "05:00-05:05 (5 minutes)",
            "purpose": "Quality Assurance",
            "description": "Validates downloaded data integrity, completeness, and format correctness",
            "why_needed": "Ensures corrupted or incomplete data doesn't break the pipeline or produce invalid predictions",
            "criticality": "🟡 HIGH - Prevents downstream errors",
            "input": "Raw downloaded CSV files",
            "output": "Validation reports and clean data confirmation",
            "dependencies": "Successful data download completion",
        },
        {
            "name": "CSV IMPORT & DATABASE LOADING",
            "timing": "06:01-06:04 (3 minutes)",
            "purpose": "Data Integration",
            "description": "Imports validated CSV data into PostgreSQL database with proper schema mapping and type conversion",
            "why_needed": "Transforms raw files into structured database format required for ML processing and analysis",
            "criticality": "🔴 CRITICAL - No database data = No predictions",
            "input": "Validated CSV files (races, records, horses)",
            "output": "Structured data in PostgreSQL database",
            "dependencies": "Database connectivity, valid CSV format",
        },
        {
            "name": "DATA PREPROCESSING & RELATIONSHIPS",
            "timing": "06:04-06:16 (12 minutes)",
            "purpose": "Data Enhancement",
            "description": "Fixes data relationships, assigns jockey/trainer names, populates course information, cleans inconsistencies",
            "why_needed": "Raw data often has broken relationships and missing information - this stage makes it ML-ready",
            "criticality": "🟡 HIGH - Improves prediction accuracy",
            "input": "Raw database records with potential inconsistencies",
            "output": "Clean, relationship-linked database with enhanced information",
            "dependencies": "Successful database import",
        },
        {
            "name": "FEATURE ENGINEERING",
            "timing": "06:16-06:42 (26 minutes)",
            "purpose": "ML Preparation",
            "description": "Extracts and engineers features for ML models including form metrics, speed figures, and contextual factors",
            "why_needed": "ML models require numerical features - this transforms racing data into prediction-ready format",
            "criticality": "🔴 CRITICAL - No features = No ML predictions",
            "input": "Clean, processed database records",
            "output": "Feature matrices ready for ML training",
            "dependencies": "Completed data preprocessing",
        },
        {
            "name": "ML MODEL TRAINING",
            "timing": "07:44-09:09 (85 minutes)",
            "purpose": "Prediction Engine",
            "description": "Trains Random Forest, XGBoost, and Neural Network models using historical data and current features",
            "why_needed": 'Creates the AI "brain" that makes predictions - without trained models, no selections possible',
            "criticality": "🔴 CRITICAL - Core AI functionality",
            "input": "Engineered features and historical race outcomes",
            "output": "Trained ML models with performance metrics",
            "dependencies": "Sufficient training data, feature engineering complete",
        },
        {
            "name": "MONTE CARLO SIMULATIONS",
            "timing": "09:09-09:39 (30 minutes)",
            "purpose": "Risk Assessment",
            "description": "Runs thousands of race simulations to assess prediction confidence and outcome probabilities",
            "why_needed": "Provides confidence intervals and risk assessment for betting recommendations",
            "criticality": "🟢 MEDIUM - Enhances decision quality",
            "input": "Trained ML models and race data",
            "output": "Probability distributions and confidence metrics",
            "dependencies": "Completed ML training",
        },
        {
            "name": "SELECTION GENERATION",
            "timing": "09:59-10:14 (15 minutes)",
            "purpose": "Final Output",
            "description": "Generates final AI selections with win/place probabilities, confidence scores, and betting recommendations",
            "why_needed": "Combines all analysis into actionable recommendations for users",
            "criticality": "🔴 CRITICAL - Final user-facing output",
            "input": "ML predictions, Monte Carlo results, form analysis",
            "output": "Today's AI horse selections with probabilities",
            "dependencies": "All previous stages completed successfully",
        },
    ]


def analyze_data_sufficiency():
    """Analyze if we have sufficient data for ML predictions"""
    analysis = {
        "historical_races": 0,
        "training_records": 0,
        "unique_horses": 0,
        "unique_jockeys": 0,
        "unique_trainers": 0,
        "todays_races": 0,
        "min_basic": 100,
        "min_recommended": 1000,
        "ml_readiness": "Unknown",
        "can_make_selections": False,
        "blocking_reasons": [],
        "recommendations": [],
    }

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()

        # Get data counts
        cursor.execute("SELECT COUNT(*) FROM races")
        analysis["historical_races"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        analysis["training_records"] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT horse) FROM records WHERE horse IS NOT NULL"
        )
        analysis["unique_horses"] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT jockey) FROM records WHERE jockey IS NOT NULL"
        )
        analysis["unique_jockeys"] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT trainer) FROM records WHERE trainer IS NOT NULL"
        )
        analysis["unique_trainers"] = cursor.fetchone()[0]

        # Check today's races
        today = date.today()
        cursor.execute("SELECT COUNT(*) FROM races WHERE date = %s", (today,))
        analysis["todays_races"] = cursor.fetchone()[0]

        # Assess ML readiness
        if analysis["training_records"] >= analysis["min_recommended"]:
            analysis["ml_readiness"] = "🟢 EXCELLENT - High accuracy expected"
        elif analysis["training_records"] >= analysis["min_basic"]:
            analysis["ml_readiness"] = "🟡 ADEQUATE - Basic predictions possible"
        else:
            analysis["ml_readiness"] = "🔴 INSUFFICIENT - More data needed"

        # Assess selection capability
        if analysis["todays_races"] == 0:
            analysis["blocking_reasons"].append("No races scheduled for today")
            analysis["recommendations"].append(
                "Wait for auto-downloader or check racing calendar"
            )

        if analysis["training_records"] < analysis["min_basic"]:
            analysis["blocking_reasons"].append("Insufficient training data")
            analysis["recommendations"].append(
                "Allow system to collect more historical data"
            )

        # Check if models exist
        models_dir = Path("/home/jc/Documents/Horse-race-ai-v2.03/models")
        if not any(models_dir.glob("*.joblib")):
            analysis["blocking_reasons"].append("No trained models found")
            analysis["recommendations"].append("Run ML training pipeline")

        analysis["can_make_selections"] = (
            analysis["todays_races"] > 0
            and analysis["training_records"] >= analysis["min_basic"]
            and len(analysis["blocking_reasons"]) == 0
        )

        cursor.close()
        conn.close()

    except Exception as e:
        analysis["blocking_reasons"].append(f"Database connection error: {e}")
        analysis["recommendations"].append("Check PostgreSQL container status")

    return analysis


def get_daily_timeline():
    """Get typical daily processing timeline"""
    return [
        {
            "time": "00:01",
            "activity": "🤖 Auto-downloader starts - fetching racing data",
        },
        {
            "time": "00:05",
            "activity": "📥 Data download complete - files saved locally",
        },
        {
            "time": "05:00",
            "activity": "🔍 Data validation begins - checking file integrity",
        },
        {"time": "05:05", "activity": "✅ Validation complete - data ready for import"},
        {"time": "06:01", "activity": "📊 CSV import starts - loading into database"},
        {
            "time": "06:04",
            "activity": "🔄 Data preprocessing begins - cleaning relationships",
        },
        {
            "time": "06:16",
            "activity": "⚙️  Feature engineering starts - preparing ML features",
        },
        {
            "time": "06:42",
            "activity": "🧠 ML model training begins - updating AI models",
        },
        {
            "time": "09:09",
            "activity": "🎲 Monte Carlo simulations start - risk assessment",
        },
        {"time": "09:39", "activity": "📈 Final analysis and selection generation"},
        {
            "time": "10:14",
            "activity": "🏆 AI selections ready - available via web interface",
        },
        {
            "time": "10:15",
            "activity": "🌐 Web interface updated with today's predictions",
            "note": "Users can now access AI selections",
        },
        {
            "time": "14:00",
            "activity": "🏁 First races typically start",
            "note": "Racing day begins",
        },
        {
            "time": "20:00",
            "activity": "🏁 Last races typically finish",
            "note": "Results available for tomorrow's training",
        },
    ]


def check_stage_status(stage_name):
    """Check if a pipeline stage has run today"""
    try:
        status_file = Path("/app/logs/pipeline_status.json")
        if status_file.exists():
            with open(status_file) as f:
                status = json.load(f)

            if stage_name.lower().replace(" ", "_") in status:
                return status[stage_name.lower().replace(" ", "_")]["message"]
    except:
        pass

    return None


def diagnose_issues(system_status, data_analysis):
    """Diagnose potential issues and provide recommendations"""
    issues = []

    if not system_status["database_connected"]:
        issues.append(
            {
                "severity": "CRITICAL",
                "title": "Database Connection Failed",
                "description": "Cannot connect to PostgreSQL database",
                "impact": "Complete system failure - no data access possible",
                "solution": "Check Docker containers: docker-compose ps",
            }
        )

    if system_status["todays_races"] == 0:
        issues.append(
            {
                "severity": "HIGH",
                "title": "No Today's Racing Data",
                "description": "No races found for current date in database",
                "impact": "Cannot generate AI selections for today",
                "solution": "Check auto-downloader logs or manually trigger data download",
            }
        )

    if system_status["total_records"] < 100:
        issues.append(
            {
                "severity": "HIGH",
                "title": "Insufficient Training Data",
                "description": f'Only {system_status["total_records"]} records available',
                "impact": "ML models cannot achieve good accuracy",
                "solution": "Allow system to collect more data over several days",
            }
        )

    # Check if it's early morning (before pipeline should complete)
    current_hour = datetime.now().hour
    if current_hour < 10 and system_status["todays_races"] == 0:
        issues.append(
            {
                "severity": "INFO",
                "title": "Pipeline Still Processing",
                "description": "Early morning - pipeline may still be running",
                "impact": "Temporary - selections will be available later",
                "solution": "Wait until 10:15 AM for pipeline completion",
            }
        )

    return issues


if __name__ == "__main__":
    generate_pipeline_report()
