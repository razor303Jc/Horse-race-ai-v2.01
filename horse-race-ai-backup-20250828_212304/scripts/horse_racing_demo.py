#!/usr/bin/env python3
"""
Horse Racing AI Expert Demo - Quick Test
Shows the enhanced system with domain knowledge
"""

import sys
import os

sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01/scripts")

from horse_racing_ai_expert import HorseRacingAIExpert


def main():
    """Demo the enhanced AI expert system"""
    print("🐎 HORSE RACING AI EXPERT SYSTEM - DEMO")
    print("=" * 60)

    expert = HorseRacingAIExpert()

    # Test question about horse racing domain knowledge
    test_question = "Explain how apprentice jockey weight allowances work and their strategic importance in handicap races"

    print(f"\n📝 Demo Question:")
    print(f"   {test_question}")

    # Get analysis from Qwen model (faster for demo)
    print(f"\n🔄 Querying Qwen2.5-Coder with enhanced domain knowledge...")

    results = expert.get_expert_analysis(test_question, model="qwen")

    print(f"\n✅ Demo Complete!")
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✓ Comprehensive horse racing domain knowledge loaded")
    print(f"   ✓ Project context integration from database")
    print(f"   ✓ Expert-level analysis combining domain + technical knowledge")
    print(f"   ✓ AI models now understand racing terminology, rules, and systems")


if __name__ == "__main__":
    main()
