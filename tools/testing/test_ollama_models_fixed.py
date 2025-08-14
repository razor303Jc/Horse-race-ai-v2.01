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
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
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