#!/usr/bin/env python3
"""
Simple WhiteRabbit Racing Test
=============================
Test WhiteRabbit with very short prompts for racing analysis.
"""

import subprocess
import time


def test_simple_racing_query():
    """Test WhiteRabbit with a very short racing query."""

    short_prompt = "What makes a good racehorse?"

    try:
        print("🤖 Testing WhiteRabbit Neo with simple query...")
        print(f"📝 Prompt: {short_prompt}")

        start_time = time.time()
        result = subprocess.run(
            ["ollama", "run", "jimscard/whiterabbit-neo:13b-q5_K_M"],
            input=short_prompt,
            text=True,
            capture_output=True,
            timeout=30,
        )
        end_time = time.time()

        if result.returncode == 0:
            response = result.stdout.strip()
            response_time = end_time - start_time
            print(f"✅ Success in {response_time:.2f}s")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Timeout after 30s")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Main function."""
    print("🏇 Simple WhiteRabbit Racing Test")
    print("=" * 40)

    if test_simple_racing_query():
        print("\n✅ WhiteRabbit Neo is working!")
        print("💡 Try increasing timeout for longer analyses")
    else:
        print("\n❌ WhiteRabbit Neo test failed")
        print("💡 Check Ollama status or try restarting")


if __name__ == "__main__":
    main()