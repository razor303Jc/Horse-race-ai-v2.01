#!/usr/bin/env python3
"""
Quick Racing Media Test for WhiteRabbit Neo
===========================================
Simple test script for racing social media analysis.
"""

import subprocess
import time


def quick_racing_analysis():
    """Quick test of WhiteRabbit Neo for racing analysis."""

    prompt = """Analyze this racing Twitter post for betting insights:
    
"@RacingTips: Lightning Bolt looking sharp in morning work at Ascot. 
Trainer confident for 2:15 race. Each-way value at current 6/1 odds."

What are the key takeaways for punters?"""

    try:
        print("🤖 Testing WhiteRabbit Neo with racing content...")
        print("🔄 Processing...")

        start_time = time.time()
        result = subprocess.run(
            ["ollama", "run", "jimscard/whiterabbit-neo:13b-q5_K_M"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60,
        )
        end_time = time.time()

        if result.returncode == 0:
            response = result.stdout.strip()
            response_time = end_time - start_time
            print(f"✅ Response received in {response_time:.2f}s")
            print("=" * 60)
            print(response)
            print("=" * 60)
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Request timed out after 1 minute")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Main function."""
    print("🏇 Quick Racing Media Analysis Test")
    print("Testing WhiteRabbit Neo capabilities")
    print("=" * 45)

    if quick_racing_analysis():
        print("\n✅ WhiteRabbit Neo is working for racing analysis!")
        print("💡 You can now run the full racing_media_analyzer.py")
    else:
        print("\n❌ WhiteRabbit Neo test failed")
        print("💡 Try checking Ollama status: ollama list")


if __name__ == "__main__":
    main()
