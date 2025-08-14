#!/usr/bin/env python3
"""
Quick Lint Fixer for Specific Files
====================================
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path


def fix_file_with_ai(file_path):
    """Fix lint errors in a specific file using Qwen2.5-Coder."""
    print(f"🔧 FIXING LINT ERRORS IN: {file_path}")
    print("=" * 50)

    with open(file_path, "r") as f:
        content = f.read()

    prompt = f"""Fix these specific lint errors in this Python code:

ISSUES TO FIX:
1. Line too long errors (keep lines under 88 characters)
2. Trailing whitespace
3. Unused variables (remove or use them)
4. Bare except clauses (make them specific)
5. Missing spaces after commas

ORIGINAL CODE:
```python
{content}
```

Return the corrected Python code with all lint issues fixed.
Maintain all functionality while following PEP 8 style guidelines.
Only return the corrected code, no explanations."""

    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2.5-coder:7b"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=3600,
        )

        if result.returncode == 0:
            response = result.stdout.strip()

            # Extract code if wrapped in code blocks
            if "```python" in response:
                start = response.find("```python") + 9
                end = response.find("```", start)
                if end != -1:
                    fixed_code = response[start:end].strip()
                else:
                    fixed_code = response
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    fixed_code = response[start:end].strip()
                else:
                    fixed_code = response
            else:
                fixed_code = response

            # Save fixed version
            fixed_file = file_path.replace(".py", "_lint_fixed.py")
            with open(fixed_file, "w") as f:
                f.write(fixed_code)

            print(f"✅ Fixed version saved as: {Path(fixed_file).name}")
            return fixed_code

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "ai_betting_bot.py"

    fix_file_with_ai(file_path)
