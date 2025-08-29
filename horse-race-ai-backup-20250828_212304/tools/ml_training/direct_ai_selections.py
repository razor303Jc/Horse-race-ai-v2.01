#!/usr/bin/env python3
"""
Direct AI Selections using newly uploaded card data
"""

import psycopg2
import pandas as pd
import numpy as np
import os
from datetime import date
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def connect_results():
    return psycopg2.connect(
        host="postgres",
        database="results_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )


def connect_cards():
    return psycopg2.connect(
        host="postgres",
        database="cards_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )


def train_simple_model():
    """Train a simple model on historical results"""
    print("🤖 Training AI model...")

    with connect_results() as conn:
        query = """
            SELECT 
                CAST(starting_price AS FLOAT) as odds,
                age,
                position
            FROM records 
            WHERE position IS NOT NULL 
              AND starting_price IS NOT NULL
              AND CAST(starting_price AS FLOAT) > 0
              AND age IS NOT NULL
            LIMIT 300
        """
        df = pd.read_sql_query(query, conn)

    print(f"📊 Training on {len(df)} records")

    # Simple features
    X = np.column_stack(
        [
            df["odds"].values,
            np.log(df["odds"].values),
            1.0 / df["odds"].values,  # implied probability
            df["age"].values,
        ]
    )

    y = (df["position"] == 1).astype(int)

    # Train model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(random_state=42)
    model.fit(X_scaled, y)

    accuracy = model.score(X_scaled, y)
    print(f"✅ Model trained - Accuracy: {accuracy:.3f}")

    return model, scaler


def get_latest_race_cards():
    """Get the most recent race cards"""
    print("📋 Loading race cards...")

    with connect_cards() as conn:
        # Get the most recent date with data
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.date, COUNT(rd.detail_id) as horses
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            GROUP BY r.date
            ORDER BY r.date DESC
            LIMIT 3
        """
        )

        available_dates = cursor.fetchall()
        print("📅 Available dates with horses:")
        for d, h in available_dates:
            print(f"  {d}: {h} horses")

        if not available_dates:
            print("❌ No race card data found")
            return pd.DataFrame()

        target_date = available_dates[0][0]
        print(f"🎯 Using races from: {target_date}")

        query = """
            SELECT 
                r.race_id,
                r.course,
                r.race_time,
                rd.horse_name,
                rd.jockey,
                rd.trainer,
                rd.number,
                COALESCE(rd.odds, 5.0) as odds,
                COALESCE(rd.age, 4) as age
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            WHERE r.date = %s
            ORDER BY r.race_time, rd.number
        """

        df = pd.read_sql_query(query, conn, params=(target_date,))

    print(f"📋 Found {len(df)} horses in {df['race_id'].nunique()} races")
    return df


def make_ai_selections(model, scaler, cards_df):
    """Generate AI selections"""
    print("🎯 Making AI selections...")

    # Prepare features
    X = np.column_stack(
        [
            cards_df["odds"].values,
            np.log(cards_df["odds"].values),
            1.0 / cards_df["odds"].values,  # implied probability
            cards_df["age"].values,
        ]
    )

    # Scale and predict
    X_scaled = scaler.transform(X)
    win_probs = model.predict_proba(X_scaled)[:, 1]

    cards_df = cards_df.copy()
    cards_df["ai_win_prob"] = win_probs

    return cards_df


def display_selections(selections_df):
    """Display AI selections"""
    print("\\n" + "=" * 70)
    print("🏇 AI HORSE RACING SELECTIONS")
    print("=" * 70)

    for race_id in selections_df["race_id"].unique():
        race_data = selections_df[selections_df["race_id"] == race_id].copy()
        race_data = race_data.sort_values("ai_win_prob", ascending=False)

        race_info = race_data.iloc[0]
        print(f"\\n📍 Race {race_id}: {race_info['course']}")
        print(f"🕐 Time: {race_info['race_time']}")
        print("-" * 50)

        # Top 3 selections
        for i, (_, horse) in enumerate(race_data.head(3).iterrows()):
            confidence = horse["ai_win_prob"] * 100
            print(f"{i+1}. {horse['horse_name']}")
            print(f"   🏃 Jockey: {horse['jockey']}")
            print(f"   💰 Odds: {horse['odds']:.1f}/1")
            print(f"   🤖 AI Confidence: {confidence:.1f}%")
            print()


def main():
    print("🚀 DIRECT AI SELECTIONS")
    print("=" * 50)

    # Train model
    model, scaler = train_simple_model()

    # Get race cards
    cards_df = get_latest_race_cards()

    if len(cards_df) == 0:
        print("❌ No race card data available")
        return

    # Make selections
    selections_df = make_ai_selections(model, scaler, cards_df)

    # Display results
    display_selections(selections_df)

    print("✅ AI Selections Complete!")


if __name__ == "__main__":
    main()
