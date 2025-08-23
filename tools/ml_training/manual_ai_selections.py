#!/usr/bin/env python3
"""
Manual AI Selections - No pandas, direct cursor approach
"""

import psycopg2
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def manual_ai_selections():
    """Generate AI selections manually without pandas"""
    print("🚀 MANUAL AI SELECTIONS")
    print("=" * 50)

    # Step 1: Train model on results data
    print("🤖 Training AI model...")

    conn_r = psycopg2.connect(
        host="postgres",
        database="results_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )
    cursor_r = conn_r.cursor()

    cursor_r.execute(
        """
        SELECT CAST(starting_price AS FLOAT), age, position
        FROM records 
        WHERE position IS NOT NULL 
          AND starting_price IS NOT NULL
          AND CAST(starting_price AS FLOAT) > 0
          AND age IS NOT NULL
        LIMIT 300
    """
    )

    training_data = cursor_r.fetchall()
    conn_r.close()

    print(f"📊 Training on {len(training_data)} records")

    # Prepare training features
    X_train = []
    y_train = []

    for odds, age, position in training_data:
        features = [
            float(odds),
            np.log(float(odds)),
            1.0 / float(odds),  # implied probability
            float(age),
        ]
        X_train.append(features)
        y_train.append(1 if position == 1 else 0)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Train model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(random_state=42)
    model.fit(X_scaled, y_train)

    accuracy = model.score(X_scaled, y_train)
    print(f"✅ Model trained - Accuracy: {accuracy:.3f}")

    # Step 2: Get race card data
    print("📋 Loading race cards...")

    conn_c = psycopg2.connect(
        host="postgres",
        database="cards_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )
    cursor_c = conn_c.cursor()

    # Get a sample race with good data
    cursor_c.execute(
        """
        SELECT r.race_id, r.course, r.race_time, 
               rd.horse_name, rd.jockey, rd.trainer,
               COALESCE(rd.odds, 5.0) as odds,
               COALESCE(rd.age, 4) as age
        FROM races r
        JOIN racecard_details rd ON r.race_id = rd.race_id
        WHERE r.race_id IN (
            SELECT race_id FROM racecard_details 
            GROUP BY race_id 
            HAVING COUNT(*) > 5
            LIMIT 3
        )
        ORDER BY r.race_id, rd.number
    """
    )

    race_data = cursor_c.fetchall()
    conn_c.close()

    print(f"📋 Found {len(race_data)} horses")

    # Step 3: Make predictions
    print("🎯 Making AI predictions...")

    race_predictions = {}

    for race_id, course, race_time, horse_name, jockey, trainer, odds, age in race_data:
        # Prepare features
        features = [float(odds), np.log(float(odds)), 1.0 / float(odds), float(age)]

        # Scale and predict
        X_pred = scaler.transform([features])
        win_prob = model.predict_proba(X_pred)[0][1]

        if race_id not in race_predictions:
            race_predictions[race_id] = {
                "course": course,
                "race_time": race_time,
                "horses": [],
            }

        race_predictions[race_id]["horses"].append(
            {
                "name": horse_name,
                "jockey": jockey,
                "trainer": trainer,
                "odds": odds,
                "age": age,
                "ai_prob": win_prob,
            }
        )

    # Step 4: Display selections
    print("\\n" + "=" * 70)
    print("🏇 AI HORSE RACING SELECTIONS")
    print("=" * 70)

    for race_id, race_info in race_predictions.items():
        print(f"\\n📍 Race {race_id}: {race_info['course']}")
        print(f"🕐 Time: {race_info['race_time']}")
        print("-" * 50)

        # Sort horses by AI probability
        horses = sorted(race_info["horses"], key=lambda x: x["ai_prob"], reverse=True)

        # Top 3 selections
        for i, horse in enumerate(horses[:3]):
            confidence = horse["ai_prob"] * 100
            print(f"{i+1}. {horse['name']}")
            print(f"   🏃 Jockey: {horse['jockey']}")
            print(f"   💰 Odds: {horse['odds']:.1f}/1")
            print(f"   🤖 AI Confidence: {confidence:.1f}%")
            print()

    print("✅ AI Selections Complete!")


if __name__ == "__main__":
    manual_ai_selections()
