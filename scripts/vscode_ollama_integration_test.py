#!/usr/bin/env python3
"""
VS Code + Ollama Integration Test
===============================

Test script to verify VS Code integration with Ollama AI models
for the Horse Racing AI v2.01 project.
"""

import subprocess
import json
import requests
import time


def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            print(f"📊 Available models: {len(models.get('models', []))}")
            for model in models.get("models", []):
                print(f"  - {model['name']} ({model['size']})")
            return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False


def test_continue_config():
    """Test Continue configuration."""
    import os

    config_path = os.path.expanduser("~/.continue/config.json")
    if os.path.exists(config_path):
        print("✅ Continue configuration found")
        with open(config_path) as f:
            config = json.load(f)
            print(f"📋 Configured models: {len(config.get('models', []))}")
            for model in config.get("models", []):
                print(f"  - {model['title']}")
        return True
    else:
        print("❌ Continue configuration not found")
        return False


def test_vscode_extensions():
    """Test VS Code extensions."""
    try:
        result = subprocess.run(
            ["code", "--list-extensions"], capture_output=True, text=True
        )
        extensions = result.stdout.strip().split("\n")

        required_extensions = [
            "continue.continue",
            "tabnine.tabnine-vscode",
            "ms-python.python",
        ]

        installed = []
        missing = []

        for ext in required_extensions:
            if ext in extensions:
                installed.append(ext)
            else:
                missing.append(ext)

        print(f"✅ Installed extensions: {len(installed)}")
        for ext in installed:
            print(f"  - {ext}")

        if missing:
            print(f"⚠️  Missing extensions: {len(missing)}")
            for ext in missing:
                print(f"  - {ext}")

        return len(missing) == 0

    except Exception as e:
        print(f"❌ Extension check failed: {e}")
        return False


def test_ai_query():
    """Test AI model with horse racing query."""
    try:
        # Test with Qwen2.5-Coder
        payload = {
            "model": "qwen2.5-coder:7b",
            "prompt": "What are the key components of the Horse Racing AI v2.01 ML pipeline?",
            "stream": False,
        }

        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ AI model responding successfully!")
            print(f"🤖 Response preview: {result['response'][:200]}...")
            return True
        else:
            print(f"❌ AI query failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ AI query error: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 VS Code + Ollama Integration Test")
    print("=" * 50)

    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Continue Configuration", test_continue_config),
        ("VS Code Extensions", test_vscode_extensions),
        ("AI Model Query", test_ai_query),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 VS Code + Ollama integration is ready!")
        print("\n📋 Next steps:")
        print("1. Open VS Code: code horse-racing-ai.code-workspace")
        print("2. Use Ctrl+Shift+P and search 'Continue'")
        print("3. Try custom commands: /horse-racing-expert")
        print("4. Use tab completion with Qwen2.5-Coder")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")


if __name__ == "__main__":
    main()
