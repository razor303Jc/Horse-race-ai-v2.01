#!/usr/bin/env python3
"""
Quick Ollama Model Interactive Tester
====================================
Simple script to quickly test Ollama models with custom prompts.
"""

import subprocess
import sys
import time


def query_ollama(model_name, prompt):
    """Query an Ollama model with a prompt."""
    try:
        print(f"🤖 Querying {model_name}...")
        print("🔄 Processing... (this may take a moment)")

        start_time = time.time()
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120,
        )
        end_time = time.time()

        if result.returncode == 0:
            response = result.stdout.strip()
            response_time = end_time - start_time
            print(f"\n✅ Response received in {response_time:.2f}s")
            print("=" * 60)
            print(response)
            print("=" * 60)
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


def main():
    """Main interactive loop."""
    models = {"1": "qwen2.5-coder:7b", "2": "jimscard/whiterabbit-neo:13b-q5_K_M"}

    print("🚀 Quick Ollama Model Tester")
    print("=" * 40)

    # Check if Ollama is running
    try:
        subprocess.run(["ollama", "list"], capture_output=True, check=True)
        print("✅ Ollama is running and accessible")
    except Exception:
        print("❌ Ollama not running. Please start it first.")
        return

    while True:
        print("\n🤖 Available Models:")
        print("1. Qwen2.5-Coder 7B (Coding specialist)")
        print("2. WhiteRabbit Neo 13B (General AI)")
        print("3. Exit")

        choice = input("\nSelect model (1-3): ").strip()

        if choice == "3":
            print("👋 Goodbye!")
            break
        elif choice in models:
            model_name = models[choice]
            print(f"\n🎯 Selected: {model_name}")

            # Get user prompt
            print("\n📝 Enter your prompt (press Enter twice to submit):")
            lines = []
            while True:
                try:
                    line = input()
                    if line == "" and lines:
                        break
                    lines.append(line)
                except KeyboardInterrupt:
                    print("\n⏹️  Cancelled")
                    break

            if lines:
                prompt = "\n".join(lines)
                print(f"\n📤 Sending prompt to {model_name}...")
                query_ollama(model_name, prompt)
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
