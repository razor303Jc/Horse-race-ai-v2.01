#!/usr/bin/env python3
"""
AI-Powered Code Analyzer using Qwen2.5-Coder
===========================================
Uses Qwen2.5-Coder to analyze and improve the horse racing AI codebase.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class CodeAnalyzer:
    """AI-powered code analysis using Qwen2.5-Coder."""

    def __init__(self):
        self.coder_model = "qwen2.5-coder:7b"
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")

    def query_coder(self, prompt, timeout=300):
        """Query Qwen2.5-Coder with code analysis prompt."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.coder_model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

    def analyze_ml_models_performance(self):
        """Analyze ML models code for optimization opportunities."""
        print("🤖 ANALYZING ML MODELS WITH QWEN2.5-CODER")
        print("=" * 50)

        # Read a sample of ML code
        ml_file = self.project_root / "src" / "models" / "enhanced_ml_models.py"
        if ml_file.exists():
            with open(ml_file) as f:
                code_sample = f.read()[:2000]  # First 2000 characters
        else:
            code_sample = """
# Sample ML code from the project
class EnhancedMLRatingSystem:
    def __init__(self):
        self.models = {
            "random_forest": RandomForestRegressor(n_estimators=200, max_depth=15),
            "gradient_boost": GradientBoostingRegressor(n_estimators=150),
            "ridge": Ridge(alpha=1.0),
            "neural_net": MLPRegressor(hidden_layer_sizes=(100, 50))
        }
"""

        prompt = f"""Analyze this horse racing ML code for optimization:

{code_sample}

Provide specific recommendations for:
1. Performance improvements
2. Memory optimization
3. Better feature engineering
4. Model ensemble improvements
5. Code structure enhancements

Focus on practical, implementable suggestions."""

        response = self.query_coder(prompt, timeout=300)
        print(response)
        return response

    def suggest_new_features(self):
        """Suggest new features for the horse racing system."""
        print("\n🚀 SUGGESTING NEW FEATURES WITH AI")
        print("=" * 50)

        prompt = """As an expert Python developer working on a horse racing AI system, suggest 5 innovative features we could add:

Current system includes:
- ML models for race prediction
- Web dashboard 
- BETDAQ integration
- Social media analysis
- Real-time data feeds

Suggest features like:
1. Advanced data visualizations
2. New prediction algorithms
3. User experience improvements
4. Performance optimizations
5. Integration opportunities

Provide Python code snippets for implementation."""

        response = self.query_coder(prompt, timeout=300)
        print(response)
        return response

    def debug_common_issues(self):
        """Help debug common issues in the codebase."""
        print("\n🔧 AI-POWERED DEBUGGING ASSISTANCE")
        print("=" * 50)

        prompt = """Common issues in Python machine learning projects and how to fix them:

For a horse racing prediction system, what are the top 5 most likely bugs or issues and how would you debug them?

Include:
- Data pipeline issues
- Model performance problems  
- Web application errors
- Memory/performance bottlenecks
- Database connection issues

Provide specific debugging techniques and code examples."""

        response = self.query_coder(prompt, timeout=300)
        print(response)
        return response

    def generate_test_cases(self):
        """Generate test cases for the racing system."""
        print("\n🧪 GENERATING AI-POWERED TEST CASES")
        print("=" * 50)

        prompt = """Generate comprehensive test cases for a horse racing AI system:

Create unit tests for:
1. ML model prediction accuracy
2. Data validation and preprocessing
3. API endpoint functionality 
4. Database operations
5. Error handling scenarios

Provide Python pytest code with realistic test data and edge cases."""

        response = self.query_coder(prompt, timeout=300)
        print(response)
        return response

    def optimize_database_queries(self):
        """Suggest database optimizations."""
        print("\n🗄️ DATABASE OPTIMIZATION SUGGESTIONS")
        print("=" * 50)

        prompt = """Optimize database queries for a horse racing application:

Common queries include:
- Race results by date range
- Horse performance history
- Jockey/trainer statistics
- Market odds tracking
- Prediction accuracy metrics

Suggest:
1. SQL query optimizations
2. Index strategies
3. Caching approaches
4. Database schema improvements
5. Performance monitoring

Provide specific SQL and Python examples."""

        response = self.query_coder(prompt, timeout=300)
        print(response)
        return response

    def fix_lint_errors(self, file_path=None):
        """Use Qwen2.5-Coder to fix lint errors in Python files."""
        print("\n🔧 AI-POWERED LINT ERROR FIXING")
        print("=" * 50)

        if file_path:
            # Fix specific file
            files_to_check = [Path(file_path)]
        else:
            # Find Python files with potential lint issues
            files_to_check = []
            for pattern in ["*.py", "**/*.py"]:
                files_to_check.extend(self.project_root.glob(pattern))

        for file_path in files_to_check[:5]:  # Limit to 5 files per run
            if not file_path.exists() or file_path.name.startswith("."):
                continue

            print(f"\n📁 Analyzing: {file_path.name}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                # Check if file has common lint issues
                lint_issues = self._detect_lint_issues(file_content)

                if lint_issues:
                    print(f"🚨 Found {len(lint_issues)} potential issues")
                    fixed_content = self._fix_with_ai(
                        file_content, lint_issues, file_path.name
                    )

                    if fixed_content and fixed_content != file_content:
                        # Write fixed content to new file for review
                        fixed_file = file_path.parent / f"{file_path.stem}_fixed.py"
                        with open(fixed_file, "w", encoding="utf-8") as f:
                            f.write(fixed_content)
                        print(f"✅ Fixed version saved as: {fixed_file.name}")
                    else:
                        print("ℹ️ No changes needed or AI couldn't improve")
                else:
                    print("✅ No lint issues detected")

            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")

    def _detect_lint_issues(self, content):
        """Detect common lint issues in Python code."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Line too long (>88 characters)
            if len(line) > 88:
                issues.append(f"Line {i}: Line too long ({len(line)} > 88 characters)")

            # Trailing whitespace
            if line.endswith(" ") or line.endswith("\t"):
                issues.append(f"Line {i}: Trailing whitespace")

            # Multiple blank lines
            if i > 1 and not line.strip() and not lines[i - 2].strip():
                issues.append(f"Line {i}: Multiple consecutive blank lines")

            # Missing space after comma
            if "," in line and ",," not in line:
                import re

                if re.search(r",[^\s]", line):
                    issues.append(f"Line {i}: Missing space after comma")

            # Bare except
            if "except:" in line:
                issues.append(f"Line {i}: Bare except clause")

        return issues

    def _fix_with_ai(self, content, issues, filename):
        """Use AI to fix the detected lint issues."""
        prompt = f"""Fix these lint issues in the Python file '{filename}':

ISSUES FOUND:
{chr(10).join(issues[:10])}  # Show first 10 issues

ORIGINAL CODE:
```python
{content[:3000]}  # First 3000 characters
```

Please provide the corrected Python code that fixes these issues:

1. Shorten lines over 88 characters by breaking them appropriately
2. Remove trailing whitespace
3. Fix multiple consecutive blank lines (max 2)
4. Add spaces after commas where missing
5. Replace bare 'except:' with specific exceptions
6. Maintain code functionality and readability
7. Follow PEP 8 style guidelines

Return ONLY the corrected Python code, no explanations."""

        response = self.query_coder(prompt, timeout=300)

        # Extract code from response if wrapped in code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        return (
            response.strip() if response and not response.startswith("Error") else None
        )


def main():
    """Run the AI code analyzer."""
    print("🤖 AI-POWERED CODE ANALYZER")
    print("Using Qwen2.5-Coder for Horse Racing AI Optimization")
    print("=" * 60)

    analyzer = CodeAnalyzer()

    print("What would you like to analyze?")
    print("1. ML Models Performance")
    print("2. Suggest New Features")
    print("3. Debug Common Issues")
    print("4. Generate Test Cases")
    print("5. Database Optimizations")
    print("6. Fix Lint Errors")
    print("7. All analyses")

    choice = input("\nEnter choice (1-7): ").strip()

    if choice == "1":
        analyzer.analyze_ml_models_performance()
    elif choice == "2":
        analyzer.suggest_new_features()
    elif choice == "3":
        analyzer.debug_common_issues()
    elif choice == "4":
        analyzer.generate_test_cases()
    elif choice == "5":
        analyzer.optimize_database_queries()
    elif choice == "6":
        analyzer.fix_lint_errors()
    elif choice == "7":
        print("🔄 Running all analyses...\n")
        analyzer.analyze_ml_models_performance()
        analyzer.suggest_new_features()
        analyzer.debug_common_issues()
        analyzer.generate_test_cases()
        analyzer.optimize_database_queries()
        analyzer.fix_lint_errors()
    else:
        print("Invalid choice, running ML analysis...")
        analyzer.analyze_ml_models_performance()


if __name__ == "__main__":
    main()
