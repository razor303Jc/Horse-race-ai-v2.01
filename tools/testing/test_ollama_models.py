#!/usr/bin/env python3
"""
Ollama Models Testing Script for Horse Racing AI
================================================
Test both Qwen2.5-Coder and WhiteRabbit Neo models with various
coding and AI tasks related to the horse racing project.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional


class OllamaModelTester:
    """Test suite for Ollama AI models."""

    def __init__(self):
        self.models = {
            "coder": "qwen2.5-coder:7b",
            "general": "jimscard/whiterabbit-neo:13b-q5_K_M",
        }
        self.results = {}

    def query_model(
        self, model_name: str, prompt: str, timeout: int = 60
    ) -> Optional[str]:
        """Query an Ollama model with a prompt."""
        try:
            print(f"🤖 Querying {model_name}...")
            start_time = time.time()

            result = subprocess.run(
                ["ollama", "run", model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )

            end_time = time.time()
            response_time = end_time - start_time

            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"✅ Response received in {response_time:.2f}s")
                return response
            else:
                print(f"❌ Error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout after {timeout}s")
            return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def test_coding_capabilities(self):
        """Test coding-specific capabilities with Qwen2.5-Coder."""
        print("\n" + "=" * 60)
        print("🔧 TESTING CODING CAPABILITIES - Qwen2.5-Coder")
        print("=" * 60)

        coding_prompts = [
            {
                "name": "Code Review",
                "prompt": """Review this Python function for horse racing prediction:

```python
def calculate_horse_rating(horse_data):
    rating = 0
    if horse_data['recent_form']:
        rating += len(horse_data['recent_form']) * 2
    if horse_data['jockey_wins'] > 5:
        rating += 10
    return rating
```

What improvements would you suggest?""",
            },
            {
                "name": "ML Model Optimization",
                "prompt": """I have a horse racing ML pipeline with these models:
- Random Forest
- Gradient Boosting  
- XGBoost
- Neural Network

How can I optimize this ensemble for better predictions? Provide specific Python code.""",
            },
            {
                "name": "Database Query Optimization",
                "prompt": """Optimize this SQL query for horse racing data:

```sql
SELECT * FROM races r 
JOIN horses h ON r.horse_id = h.id 
JOIN jockeys j ON r.jockey_id = j.id 
WHERE r.race_date > '2024-01-01' 
ORDER BY r.race_date;
```

Make it more efficient for large datasets.""",
            },
        ]

        for test in coding_prompts:
            print(f"\n📝 {test['name']}")
            print("-" * 40)
            response = self.query_model(self.models["coder"], test["prompt"])
            if response:
                print(f"Response: {response[:500]}...")
                self.results[f"coding_{test['name'].replace(' ', '_').lower()}"] = {
                    "prompt": test["prompt"],
                    "response": response,
                    "model": self.models["coder"],
                }

    def test_general_ai_capabilities(self):
        """Test general AI capabilities with WhiteRabbit Neo."""
        print("\n" + "=" * 60)
        print("🧠 TESTING GENERAL AI CAPABILITIES - WhiteRabbit Neo")
        print("=" * 60)

        general_prompts = [
            {
                "name": "Horse Racing Strategy",
                "prompt": """As an expert in horse racing, what are the top 5 factors that most influence race outcomes? 
                Explain how each factor impacts betting strategies.""",
            },
            {
                "name": "AI Ethics Discussion",
                "prompt": """What are the ethical considerations when using AI for horse racing predictions and betting? 
                How should responsible AI be implemented in this domain?""",
            },
            {
                "name": "Market Analysis",
                "prompt": """Analyze the current trends in sports betting AI. What opportunities exist for 
                innovation in horse racing prediction systems?""",
            },
        ]

        for test in general_prompts:
            print(f"\n🎯 {test['name']}")
            print("-" * 40)
            response = self.query_model(self.models["general"], test["prompt"])
            if response:
                print(f"Response: {response[:500]}...")
                self.results[f"general_{test['name'].replace(' ', '_').lower()}"] = {
                    "prompt": test["prompt"],
                    "response": response,
                    "model": self.models["general"],
                }

    def test_comparative_analysis(self):
        """Test both models on the same prompt for comparison."""
        print("\n" + "=" * 60)
        print("⚖️  COMPARATIVE ANALYSIS - Both Models")
        print("=" * 60)

        comparison_prompt = """Create a Python function that predicts the win probability 
        of a horse based on these features:
        - Recent form (list of finishing positions)
        - Jockey win rate (percentage)
        - Track conditions (good/soft/heavy)
        - Distance preference (sprinter/miler/stayer)
        
        Make it production-ready with error handling."""

        print("\n🔍 Comparing responses to the same coding prompt...")

        # Test with coding model
        print("\n1️⃣ Qwen2.5-Coder Response:")
        coder_response = self.query_model(self.models["coder"], comparison_prompt)

        # Test with general model
        print("\n2️⃣ WhiteRabbit Neo Response:")
        general_response = self.query_model(self.models["general"], comparison_prompt)

        if coder_response and general_response:
            self.results["comparison"] = {
                "prompt": comparison_prompt,
                "coder_response": coder_response,
                "general_response": general_response,
            }

    def test_project_context_awareness(self):
        """Test models' understanding of the horse racing AI project."""
        print("\n" + "=" * 60)
        print("🏇 PROJECT CONTEXT AWARENESS TEST")
        print("=" * 60)

        context_prompt = """Based on a horse racing AI project that includes:
        - ML models (Random Forest, XGBoost, Neural Networks)
        - Real-time data processing
        - Betting strategy optimization
        - Database with PostgreSQL
        - Web interface with Flask
        
        What would be the next 3 most important features to implement?
        Provide technical implementation details."""

        print("\n📊 Testing project understanding...")
        response = self.query_model(self.models["coder"], context_prompt)
        if response:
            print(f"Response: {response[:500]}...")
            self.results["project_context"] = {
                "prompt": context_prompt,
                "response": response,
                "model": self.models["coder"],
            }

    def benchmark_performance(self):
        """Benchmark response times for different query types."""
        print("\n" + "=" * 60)
        print("⚡ PERFORMANCE BENCHMARK")
        print("=" * 60)

        benchmarks = [
            ("Simple Question", "What is machine learning?"),
            ("Code Generation", "Write a Python function to calculate factorial"),
            (
                "Complex Analysis",
                "Explain the mathematical principles behind gradient boosting algorithms",
            ),
        ]

        for name, prompt in benchmarks:
            print(f"\n🎯 {name}")
            print("-" * 30)

            for model_type, model_name in self.models.items():
                start_time = time.time()
                response = self.query_model(model_name, prompt, timeout=30)
                end_time = time.time()

                if response:
                    response_time = end_time - start_time
                    word_count = len(response.split())
                    print(
                        f"  {model_type.upper()}: {response_time:.2f}s ({word_count} words)"
                    )

    def save_results(self):
        """Save test results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ollama_test_results_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Ollama Models Test Suite")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            self.test_coding_capabilities()
            self.test_general_ai_capabilities()
            self.test_comparative_analysis()
            self.test_project_context_awareness()
            self.benchmark_performance()

            print("\n" + "=" * 60)
            print("🎉 ALL TESTS COMPLETED!")
            print("=" * 60)

            self.save_results()

        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")


def main():
    """Main function."""
    print("🤖 Ollama Models Testing for Horse Racing AI v2.01")
    print("=" * 60)

    tester = OllamaModelTester()

    # Check if models are available
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is running")
            print("📋 Available models:")
            for line in result.stdout.split("\n")[1:]:  # Skip header
                if line.strip():
                    print(f"  {line}")
        else:
            print("❌ Ollama not running or not accessible")
            return
    except Exception as e:
        print(f"❌ Failed to check Ollama status: {e}")
        return

    # Ask user what they want to test
    print("\nWhat would you like to test?")
    print("1. All tests (comprehensive)")
    print("2. Coding capabilities only")
    print("3. General AI capabilities only")
    print("4. Comparative analysis")
    print("5. Performance benchmark")

    choice = input("\nEnter your choice (1-5): ").strip()

    if choice == "1":
        tester.run_all_tests()
    elif choice == "2":
        tester.test_coding_capabilities()
    elif choice == "3":
        tester.test_general_ai_capabilities()
    elif choice == "4":
        tester.test_comparative_analysis()
    elif choice == "5":
        tester.benchmark_performance()
    else:
        print("Invalid choice. Running all tests...")
        tester.run_all_tests()


if __name__ == "__main__":
    main()
