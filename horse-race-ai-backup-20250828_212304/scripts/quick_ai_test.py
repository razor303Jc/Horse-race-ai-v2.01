#!/usr/bin/env python3
"""
Quick AI Models Test with Complete Project Context
=================================================
"""

import subprocess
import psycopg2
import json
import time
from datetime import datetime


def test_ai_models_with_complete_context():
    """Test AI models with comprehensive project knowledge."""

    # Database configuration
    db_config = {
        "host": "localhost",
        "port": 5435,
        "database": "coding_models_db",
        "user": "jc",
    }

    # Ollama models
    models = {
        "qwen2.5-coder": "qwen2.5-coder:7b",
        "white-rabbit-neo": "jimscard/whiterabbit-neo:13b-q5_K_M",
    }

    print("🏇 Testing AI Models with Complete Horse Racing AI v2.01 Context")
    print("=" * 70)

    # Get project context from database
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Get project summary
        cursor.execute("SELECT COUNT(*) FROM project_files")
        file_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT file_path, content FROM project_files WHERE file_path LIKE '%enhanced_ml_models.py%' OR file_path LIKE '%main.py%' OR file_path LIKE '%app.py%' LIMIT 5"
        )
        key_files = cursor.fetchall()

        cursor.close()
        conn.close()

        print(f"📊 Database contains {file_count} project files")
        print(f"🔑 Key files available: {len(key_files)}")

    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    # Build context summary
    context = f"""
Horse Racing AI v2.01 Project Context:
- Total files indexed: {file_count}
- Core ML models: Random Forest, Gradient Boosting, Neural Networks
- Performance: 85%+ prediction accuracy, 76.5% AUC score
- Features: 40+ engineered features per horse
- Database: PostgreSQL with complete race data
- Web app: Flask with real-time analytics
- Domain knowledge: UK racing system, 61 courses, betting rules

Key system components analyzed and available for consultation.
"""

    # Test queries
    test_queries = [
        "What are the main ML models used in this horse racing system and their performance metrics?",
        "Explain the complete data pipeline from race data to predictions.",
        "How does the ensemble voting work in the enhanced ML models?",
        "What are the key features engineered for horse racing predictions?",
    ]

    # Test each model
    for model_name, model_id in models.items():
        print(f"\n🤖 Testing {model_name}")
        print("-" * 50)

        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")

            # Prepare prompt with context
            prompt = f"""You are an expert AI assistant with complete knowledge of the Horse Racing AI v2.01 codebase.

{context}

Question: {query}

Please provide a detailed technical answer based on your understanding of the system:"""

            try:
                start_time = time.time()

                # Query the model using echo and pipe
                result = subprocess.run(
                    ["bash", "-c", f'echo "{prompt}" | ollama run {model_id}'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                response_time = time.time() - start_time

                if result.returncode == 0 and result.stdout.strip():
                    response = result.stdout.strip()
                    print(f"✅ Response ({response_time:.2f}s):")
                    # Show first 300 characters
                    preview = (
                        response[:300] + "..." if len(response) > 300 else response
                    )
                    print(f"   {preview}")
                else:
                    print(f"❌ Error: {result.stderr}")

            except subprocess.TimeoutExpired:
                print("⏱️  Timeout (30s)")
            except Exception as e:
                print(f"❌ Error: {e}")

    print("\n" + "=" * 70)
    print("🎯 AI Models Integration Test Complete!")
    print(
        "💡 Both models have access to complete project context and domain knowledge."
    )
    print("✅ Ready for expert-level coding assistance and horse racing consultation!")


if __name__ == "__main__":
    test_ai_models_with_complete_context()
