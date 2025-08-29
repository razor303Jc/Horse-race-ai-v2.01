#!/usr/bin/env python3
"""
Advanced Code Quality Analysis and Improvement Tool for Horse Racing AI V2.03
Provides comprehensive code quality analysis, metrics, and automated improvements
"""

import os
import sys
import ast
import json
import time
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
import logging
from collections import defaultdict

# Code analysis imports
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
import bandit
from flake8.api import legacy as flake8


@dataclass
class CodeQualityMetrics:
    """Comprehensive code quality metrics"""

    file_path: str
    lines_of_code: int
    complexity: int
    maintainability_index: float
    duplication_percentage: float
    test_coverage: float
    security_issues: int
    style_violations: int
    documentation_score: float
    overall_score: float


@dataclass
class SecurityIssue:
    """Security vulnerability information"""

    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    recommendation: str


@dataclass
class StyleViolation:
    """Code style violation information"""

    file_path: str
    line_number: int
    column: int
    violation_type: str
    message: str
    suggestion: str


@dataclass
class CodeSmell:
    """Code smell detection"""

    file_path: str
    line_number: int
    smell_type: str
    description: str
    refactoring_suggestion: str
    impact: str


class ComplexityAnalyzer:
    """Advanced complexity analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze complexity metrics for a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Cyclomatic complexity
            cc_results = radon_cc.cc_visit(content)

            # Halstead metrics
            halstead = radon_metrics.h_visit(content)

            # Raw metrics
            raw = radon_metrics.mi_visit(content, multi=True)

            # Calculate aggregated metrics
            total_complexity = sum(item.complexity for item in cc_results)
            avg_complexity = total_complexity / len(cc_results) if cc_results else 0

            max_complexity = max((item.complexity for item in cc_results), default=0)

            # Maintainability index
            mi_score = sum(mi.mi for mi in raw) / len(raw) if raw else 0

            return {
                "cyclomatic_complexity": {
                    "total": total_complexity,
                    "average": avg_complexity,
                    "maximum": max_complexity,
                    "functions": [
                        {
                            "name": item.name,
                            "complexity": item.complexity,
                            "line": item.lineno,
                            "rank": self._get_complexity_rank(item.complexity),
                        }
                        for item in cc_results
                    ],
                },
                "halstead_metrics": {
                    "volume": sum(h.volume for h in halstead) if halstead else 0,
                    "difficulty": (
                        sum(h.difficulty for h in halstead) if halstead else 0
                    ),
                    "effort": sum(h.effort for h in halstead) if halstead else 0,
                },
                "maintainability_index": mi_score,
                "lines_of_code": len(content.splitlines()),
                "file_path": file_path,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing complexity for {file_path}: {e}")
            return {}

    def _get_complexity_rank(self, complexity: int) -> str:
        """Get complexity rank based on cyclomatic complexity"""
        if complexity <= 5:
            return "A"  # Low risk
        elif complexity <= 10:
            return "B"  # Medium risk
        elif complexity <= 20:
            return "C"  # High risk
        elif complexity <= 50:
            return "D"  # Very high risk
        else:
            return "F"  # Unmaintainable


class SecurityAnalyzer:
    """Advanced security vulnerability analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: str) -> List[SecurityIssue]:
        """Analyze security vulnerabilities in a Python file"""
        try:
            # Use Bandit for security analysis
            from bandit.core.manager import BanditManager
            from bandit.core.config import BanditConfig

            # Configure Bandit
            conf = BanditConfig()
            manager = BanditManager(conf, "file")

            # Run analysis
            manager.discover_files([file_path])
            manager.run_tests()

            # Process results
            issues = []
            for result in manager.get_issue_list():
                issue = SecurityIssue(
                    file_path=result.fname,
                    line_number=result.lineno,
                    issue_type=result.test_id,
                    severity=result.severity,
                    description=result.text,
                    recommendation=self._get_security_recommendation(result.test_id),
                )
                issues.append(issue)

            return issues

        except Exception as e:
            self.logger.error(f"Error analyzing security for {file_path}: {e}")
            return []

    def _get_security_recommendation(self, test_id: str) -> str:
        """Get security recommendation for test ID"""
        recommendations = {
            "B101": "Use assert statements only for debugging, not for data validation",
            "B102": "Avoid exec() function - use safer alternatives",
            "B103": "Set file permissions explicitly - avoid default umask",
            "B104": "Bind to localhost only unless external access is required",
            "B105": "Validate and sanitize shell input to prevent injection",
            "B106": "Use secure random number generators for cryptographic purposes",
            "B107": "Use try/except blocks instead of bare except clauses",
            "B108": "Specify temp file deletion explicitly",
            "B110": "Add exception handling for try/except/pass blocks",
            "B112": "Use secure SSL/TLS configurations",
            "B201": "Use subprocess with shell=False for better security",
            "B301": "Use pickle alternatives for untrusted data",
            "B302": "Use safe YAML loading methods",
            "B303": "Use cryptographically secure hash functions",
            "B304": "Use secure encryption algorithms",
            "B305": "Use HTTPS for sensitive data transmission",
            "B306": "Validate file paths to prevent directory traversal",
            "B307": "Use SQL parameterized queries to prevent injection",
            "B308": "Use XML parsers that disable external entity processing",
            "B309": "Validate and sanitize HTTP request data",
            "B310": "Use secure authentication mechanisms",
            "B311": "Use cryptographically secure random generators",
            "B312": "Use secure session management",
            "B313": "Implement proper input validation",
            "B314": "Use secure communication protocols",
            "B315": "Implement proper error handling without information disclosure",
        }
        return recommendations.get(
            test_id, "Review security implications and follow best practices"
        )


class StyleAnalyzer:
    """Advanced code style analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: str) -> List[StyleViolation]:
        """Analyze code style violations using flake8"""
        try:
            from flake8.api import legacy as flake8

            style_guide = flake8.get_style_guide(
                max_line_length=88,
                extend_ignore=["E203", "W503"],  # Black compatibility
            )

            # Capture violations
            violations = []

            # Run flake8 check
            report = style_guide.check_files([file_path])

            # Process results
            for error in report.get_statistics("E"):
                parts = error.split(":")
                if len(parts) >= 4:
                    violation = StyleViolation(
                        file_path=file_path,
                        line_number=int(parts[1]),
                        column=int(parts[2]),
                        violation_type=parts[3].strip().split()[0],
                        message=":".join(parts[3:]).strip(),
                        suggestion=self._get_style_suggestion(
                            parts[3].strip().split()[0]
                        ),
                    )
                    violations.append(violation)

            return violations

        except Exception as e:
            self.logger.error(f"Error analyzing style for {file_path}: {e}")
            return []

    def _get_style_suggestion(self, violation_code: str) -> str:
        """Get style improvement suggestion for violation code"""
        suggestions = {
            "E101": "Use 4 spaces for indentation",
            "E111": "Use 4 spaces per indentation level",
            "E112": "Expected an indented block",
            "E113": "Unexpected indentation",
            "E114": "Indentation is not a multiple of four (comment)",
            "E115": "Expected an indented block (comment)",
            "E116": "Unexpected indentation (comment)",
            "E121": "Continuation line under-indented for hanging indent",
            "E122": "Continuation line missing indentation or outdented",
            "E123": "Closing bracket does not match indentation of opening bracket's line",
            "E124": "Closing bracket does not match visual indentation",
            "E125": "Continuation line with same indent as next logical line",
            "E126": "Continuation line over-indented for hanging indent",
            "E127": "Continuation line over-indented for visual indent",
            "E128": "Continuation line under-indented for visual indent",
            "E129": "Visually indented line with same indent as next logical line",
            "E131": "Continuation line unaligned for hanging indent",
            "E133": "Closing bracket is missing indentation",
            "E201": "Remove whitespace after '('",
            "E202": "Remove whitespace before ')'",
            "E203": "Remove whitespace before ':'",
            "E211": "Remove whitespace before '('",
            "E221": "Use single space around operator",
            "E222": "Use single space after operator",
            "E223": "Use single space before operator",
            "E224": "Use single space after operator",
            "E225": "Add space around operator",
            "E226": "Add space around arithmetic operator",
            "E227": "Add space around bitwise/shift operator",
            "E228": "Add space around modulo operator",
            "E231": "Add space after ','",
            "E241": "Use single space after ','",
            "E242": "Use single space around operator",
            "E251": "Remove space around = in function default argument",
            "E261": "Add at least two spaces before inline comment",
            "E262": "Add space after comment hash",
            "E265": "Add space after comment hash",
            "E266": "Use only a single # for block comments",
            "E271": "Use single space after keyword",
            "E272": "Use single space before keyword",
            "E273": "Use single space after keyword",
            "E274": "Use single space before keyword",
            "E275": "Add space after keyword",
            "E301": "Add 1 blank line",
            "E302": "Add 2 blank lines before class/function definition",
            "E303": "Remove extra blank lines",
            "E304": "Remove blank line after function decorator",
            "E305": "Add 2 blank lines after class/function definition",
            "E306": "Add 1 blank line before nested definition",
            "E401": "Import modules on separate lines",
            "E402": "Place imports at the top of the file",
            "E501": "Split long lines (max 88 characters)",
            "E502": "Remove backslash between brackets",
            "E701": "Put multiple statements on separate lines",
            "E702": "Put multiple statements on separate lines",
            "E703": "Remove semicolon",
            "E704": "Put multiple statements on separate lines",
            "E711": "Use 'is' or 'is not' for None comparison",
            "E712": "Use 'is' or 'is not' for boolean comparison",
            "E713": "Use 'not in' for membership testing",
            "E714": "Use 'is not' for object comparison",
            "E721": "Use isinstance() instead of type() comparison",
            "E722": "Use specific exception types instead of bare except",
            "E731": "Use def instead of lambda assignment",
            "E741": "Use more descriptive variable names",
            "E742": "Use more descriptive class names",
            "E743": "Use more descriptive function names",
            "W191": "Use spaces instead of tabs",
            "W291": "Remove trailing whitespace",
            "W292": "Add newline at end of file",
            "W293": "Remove blank line with whitespace",
            "W391": "Remove blank line at end of file",
            "W503": "Line break before binary operator (acceptable with Black)",
            "W504": "Line break after binary operator",
        }
        return suggestions.get(violation_code, "Follow PEP 8 style guidelines")


class DuplicationDetector:
    """Advanced code duplication detection"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Detect code duplication across project"""
        try:
            python_files = []
            for root, dirs, files in os.walk(project_path):
                # Skip common directories
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in ["__pycache__", ".git", "node_modules", "venv", ".venv"]
                ]
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        python_files.append(os.path.join(root, file))

            # Analyze duplication
            duplications = []
            file_hashes = {}

            for file_path in python_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Extract functions and classes
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            code_block = ast.get_source_segment(content, node)
                            if code_block:
                                block_hash = hash(code_block.strip())

                                if block_hash in file_hashes:
                                    duplications.append(
                                        {
                                            "original_file": file_hashes[block_hash][
                                                "file"
                                            ],
                                            "original_line": file_hashes[block_hash][
                                                "line"
                                            ],
                                            "duplicate_file": file_path,
                                            "duplicate_line": node.lineno,
                                            "type": type(node).__name__,
                                            "name": node.name,
                                            "similarity": 100.0,
                                        }
                                    )
                                else:
                                    file_hashes[block_hash] = {
                                        "file": file_path,
                                        "line": node.lineno,
                                        "name": node.name,
                                    }

                except Exception as e:
                    self.logger.warning(f"Error processing {file_path}: {e}")
                    continue

            # Calculate duplication percentage
            total_blocks = len(file_hashes)
            duplicate_blocks = len(duplications)
            duplication_percentage = (
                (duplicate_blocks / total_blocks * 100) if total_blocks > 0 else 0
            )

            return {
                "total_files": len(python_files),
                "total_code_blocks": total_blocks,
                "duplicate_blocks": duplicate_blocks,
                "duplication_percentage": duplication_percentage,
                "duplications": duplications,
            }

        except Exception as e:
            self.logger.error(f"Error detecting duplication: {e}")
            return {}


class DocumentationAnalyzer:
    """Advanced documentation analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze documentation quality for a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Count elements
            total_functions = 0
            documented_functions = 0
            total_classes = 0
            documented_classes = 0

            # Analyze module docstring
            module_docstring = ast.get_docstring(tree)
            has_module_doc = bool(module_docstring)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    if ast.get_docstring(node):
                        documented_functions += 1

                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if ast.get_docstring(node):
                        documented_classes += 1

            # Calculate documentation scores
            function_doc_score = (
                (documented_functions / total_functions * 100)
                if total_functions > 0
                else 100
            )
            class_doc_score = (
                (documented_classes / total_classes * 100) if total_classes > 0 else 100
            )

            # Overall documentation score
            overall_score = (
                (function_doc_score * 0.5)
                + (class_doc_score * 0.3)
                + (100 if has_module_doc else 0) * 0.2
            )

            return {
                "file_path": file_path,
                "module_documented": has_module_doc,
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "function_documentation_percentage": function_doc_score,
                "total_classes": total_classes,
                "documented_classes": documented_classes,
                "class_documentation_percentage": class_doc_score,
                "overall_documentation_score": overall_score,
                "documentation_issues": self._identify_documentation_issues(
                    tree, content
                ),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing documentation for {file_path}: {e}")
            return {}

    def _identify_documentation_issues(
        self, tree: ast.AST, content: str
    ) -> List[Dict[str, Any]]:
        """Identify specific documentation issues"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)

                if not docstring:
                    issues.append(
                        {
                            "type": "missing_docstring",
                            "element": "function",
                            "name": node.name,
                            "line": node.lineno,
                            "severity": "medium",
                        }
                    )
                else:
                    # Check docstring quality
                    if len(docstring.strip()) < 10:
                        issues.append(
                            {
                                "type": "short_docstring",
                                "element": "function",
                                "name": node.name,
                                "line": node.lineno,
                                "severity": "low",
                            }
                        )

                    # Check for parameter documentation
                    if (
                        node.args.args
                        and "Args:" not in docstring
                        and "Parameters:" not in docstring
                    ):
                        issues.append(
                            {
                                "type": "missing_parameter_docs",
                                "element": "function",
                                "name": node.name,
                                "line": node.lineno,
                                "severity": "medium",
                            }
                        )

                    # Check for return documentation
                    if any(
                        isinstance(n, ast.Return) and n.value for n in ast.walk(node)
                    ):
                        if "Returns:" not in docstring and "Return:" not in docstring:
                            issues.append(
                                {
                                    "type": "missing_return_docs",
                                    "element": "function",
                                    "name": node.name,
                                    "line": node.lineno,
                                    "severity": "low",
                                }
                            )

            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)

                if not docstring:
                    issues.append(
                        {
                            "type": "missing_docstring",
                            "element": "class",
                            "name": node.name,
                            "line": node.lineno,
                            "severity": "high",
                        }
                    )

        return issues


class CodeSmellDetector:
    """Advanced code smell detection"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: str) -> List[CodeSmell]:
        """Detect code smells in a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            smells = []

            for node in ast.walk(tree):
                # Long method smell
                if isinstance(node, ast.FunctionDef):
                    lines = (
                        node.end_lineno - node.lineno + 1
                        if hasattr(node, "end_lineno")
                        else 0
                    )
                    if lines > 50:
                        smells.append(
                            CodeSmell(
                                file_path=file_path,
                                line_number=node.lineno,
                                smell_type="long_method",
                                description=f"Method '{node.name}' is {lines} lines long",
                                refactoring_suggestion="Break down into smaller, focused methods",
                                impact="high",
                            )
                        )

                # Large class smell
                elif isinstance(node, ast.ClassDef):
                    lines = (
                        node.end_lineno - node.lineno + 1
                        if hasattr(node, "end_lineno")
                        else 0
                    )
                    methods = len(
                        [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    )

                    if lines > 200:
                        smells.append(
                            CodeSmell(
                                file_path=file_path,
                                line_number=node.lineno,
                                smell_type="large_class",
                                description=f"Class '{node.name}' is {lines} lines with {methods} methods",
                                refactoring_suggestion="Split into multiple smaller, cohesive classes",
                                impact="high",
                            )
                        )

                # Too many parameters smell
                elif isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 5:
                        smells.append(
                            CodeSmell(
                                file_path=file_path,
                                line_number=node.lineno,
                                smell_type="too_many_parameters",
                                description=f"Method '{node.name}' has {param_count} parameters",
                                refactoring_suggestion="Use parameter objects or reduce parameter count",
                                impact="medium",
                            )
                        )

                # Nested conditionals smell
                elif isinstance(node, ast.If):
                    depth = self._calculate_nesting_depth(node)
                    if depth > 3:
                        smells.append(
                            CodeSmell(
                                file_path=file_path,
                                line_number=node.lineno,
                                smell_type="nested_conditionals",
                                description=f"Nested conditionals with depth {depth}",
                                refactoring_suggestion="Use early returns or extract methods",
                                impact="medium",
                            )
                        )

            # Detect duplicate code within file
            smells.extend(self._detect_duplicate_code_in_file(file_path, content))

            return smells

        except Exception as e:
            self.logger.error(f"Error detecting code smells for {file_path}: {e}")
            return []

    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth of conditionals"""
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _detect_duplicate_code_in_file(
        self, file_path: str, content: str
    ) -> List[CodeSmell]:
        """Detect duplicate code within a single file"""
        smells = []
        lines = content.splitlines()

        # Look for duplicate line sequences
        for i in range(len(lines) - 5):  # Check sequences of 5+ lines
            sequence = lines[i : i + 5]
            sequence_str = "\n".join(sequence).strip()

            if not sequence_str or sequence_str.startswith("#"):
                continue

            # Look for duplicates
            for j in range(i + 10, len(lines) - 5):
                other_sequence = lines[j : j + 5]
                other_str = "\n".join(other_sequence).strip()

                if sequence_str == other_str:
                    smells.append(
                        CodeSmell(
                            file_path=file_path,
                            line_number=i + 1,
                            smell_type="duplicate_code",
                            description=f"Duplicate code block found at lines {i+1} and {j+1}",
                            refactoring_suggestion="Extract common code into a shared method",
                            impact="medium",
                        )
                    )
                    break

        return smells


class ComprehensiveCodeQualityAnalyzer:
    """Main comprehensive code quality analysis system"""

    def __init__(self, project_root: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "code_quality"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize analyzers
        self.complexity_analyzer = ComplexityAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.style_analyzer = StyleAnalyzer()
        self.duplication_detector = DuplicationDetector()
        self.documentation_analyzer = DocumentationAnalyzer()
        self.code_smell_detector = CodeSmellDetector()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.project_root / "logs" / "code_quality.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def discover_python_files(self) -> List[str]:
        """Discover all Python files in the project"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    "__pycache__",
                    ".git",
                    "node_modules",
                    "venv",
                    ".venv",
                    "build",
                    "dist",
                ]
            ]

            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)

        self.logger.info(f"Discovered {len(python_files)} Python files for analysis")
        return python_files

    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive code quality analysis"""
        self.logger.info("Starting comprehensive code quality analysis...")

        python_files = self.discover_python_files()

        # Initialize results
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": len(python_files),
            "file_metrics": [],
            "project_metrics": {},
            "security_issues": [],
            "style_violations": [],
            "code_smells": [],
            "duplication_analysis": {},
            "recommendations": [],
        }

        # Analyze each file
        total_lines = 0
        total_complexity = 0
        total_security_issues = 0
        total_style_violations = 0
        total_code_smells = 0

        for file_path in python_files:
            try:
                self.logger.info(f"Analyzing {file_path}")

                # Complexity analysis
                complexity = self.complexity_analyzer.analyze_file(file_path)

                # Security analysis
                security_issues = self.security_analyzer.analyze_file(file_path)

                # Style analysis
                style_violations = self.style_analyzer.analyze_file(file_path)

                # Documentation analysis
                documentation = self.documentation_analyzer.analyze_file(file_path)

                # Code smell detection
                code_smells = self.code_smell_detector.analyze_file(file_path)

                # Calculate file metrics
                file_metrics = CodeQualityMetrics(
                    file_path=file_path,
                    lines_of_code=complexity.get("lines_of_code", 0),
                    complexity=complexity.get("cyclomatic_complexity", {}).get(
                        "total", 0
                    ),
                    maintainability_index=complexity.get("maintainability_index", 0),
                    duplication_percentage=0,  # Will be calculated later
                    test_coverage=0,  # Will be calculated later
                    security_issues=len(security_issues),
                    style_violations=len(style_violations),
                    documentation_score=documentation.get(
                        "overall_documentation_score", 0
                    ),
                    overall_score=0,  # Will be calculated
                )

                # Calculate overall score
                file_metrics.overall_score = self._calculate_overall_score(file_metrics)

                # Add to results
                results["file_metrics"].append(file_metrics.__dict__)
                results["security_issues"].extend(
                    [issue.__dict__ for issue in security_issues]
                )
                results["style_violations"].extend(
                    [violation.__dict__ for violation in style_violations]
                )
                results["code_smells"].extend([smell.__dict__ for smell in code_smells])

                # Update totals
                total_lines += file_metrics.lines_of_code
                total_complexity += file_metrics.complexity
                total_security_issues += file_metrics.security_issues
                total_style_violations += file_metrics.style_violations
                total_code_smells += len(code_smells)

            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")
                continue

        # Project-wide duplication analysis
        duplication_analysis = self.duplication_detector.analyze_project(
            str(self.project_root)
        )
        results["duplication_analysis"] = duplication_analysis

        # Calculate project metrics
        avg_complexity = total_complexity / len(python_files) if python_files else 0
        avg_doc_score = (
            sum(fm["documentation_score"] for fm in results["file_metrics"])
            / len(python_files)
            if python_files
            else 0
        )
        avg_overall_score = (
            sum(fm["overall_score"] for fm in results["file_metrics"])
            / len(python_files)
            if python_files
            else 0
        )

        results["project_metrics"] = {
            "total_lines_of_code": total_lines,
            "average_complexity": avg_complexity,
            "total_security_issues": total_security_issues,
            "total_style_violations": total_style_violations,
            "total_code_smells": total_code_smells,
            "duplication_percentage": duplication_analysis.get(
                "duplication_percentage", 0
            ),
            "average_documentation_score": avg_doc_score,
            "average_overall_score": avg_overall_score,
            "quality_grade": self._get_quality_grade(avg_overall_score),
        }

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        # Save results
        self._save_analysis_results(results)

        self.logger.info("Code quality analysis completed")
        return results

    def _calculate_overall_score(self, metrics: CodeQualityMetrics) -> float:
        """Calculate overall quality score for a file"""
        # Scoring weights
        weights = {
            "complexity": 0.2,
            "maintainability": 0.15,
            "security": 0.25,
            "style": 0.15,
            "documentation": 0.15,
            "duplication": 0.1,
        }

        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (metrics.complexity * 2))

        # Maintainability index (0-100, higher is better)
        maintainability_score = min(100, max(0, metrics.maintainability_index))

        # Security score (fewer issues is better)
        security_score = max(0, 100 - (metrics.security_issues * 10))

        # Style score (fewer violations is better)
        style_score = max(0, 100 - (metrics.style_violations * 2))

        # Documentation score (0-100, higher is better)
        documentation_score = metrics.documentation_score

        # Duplication score (lower is better)
        duplication_score = max(0, 100 - (metrics.duplication_percentage * 2))

        # Calculate weighted score
        overall_score = (
            complexity_score * weights["complexity"]
            + maintainability_score * weights["maintainability"]
            + security_score * weights["security"]
            + style_score * weights["style"]
            + documentation_score * weights["documentation"]
            + duplication_score * weights["duplication"]
        )

        return round(overall_score, 2)

    def _get_quality_grade(self, score: float) -> str:
        """Get quality grade based on score"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        elif score >= 60:
            return "D+"
        elif score >= 55:
            return "D"
        else:
            return "F"

    def _generate_recommendations(
        self, results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate improvement recommendations"""
        recommendations = []

        project_metrics = results["project_metrics"]

        # Complexity recommendations
        if project_metrics["average_complexity"] > 10:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "complexity",
                    "title": "Reduce Code Complexity",
                    "description": f"Average complexity is {project_metrics['average_complexity']:.1f}, which is above recommended threshold of 10",
                    "action": "Refactor complex functions into smaller, focused methods",
                    "impact": "Improves maintainability and reduces bugs",
                }
            )

        # Security recommendations
        if project_metrics["total_security_issues"] > 0:
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "security",
                    "title": "Address Security Vulnerabilities",
                    "description": f"Found {project_metrics['total_security_issues']} security issues",
                    "action": "Review and fix security vulnerabilities using secure coding practices",
                    "impact": "Prevents potential security breaches and data loss",
                }
            )

        # Style recommendations
        if project_metrics["total_style_violations"] > 50:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "style",
                    "title": "Improve Code Style Consistency",
                    "description": f"Found {project_metrics['total_style_violations']} style violations",
                    "action": "Run automated code formatters (Black, isort) and fix style issues",
                    "impact": "Improves code readability and team collaboration",
                }
            )

        # Documentation recommendations
        if project_metrics["average_documentation_score"] < 70:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "documentation",
                    "title": "Improve Code Documentation",
                    "description": f"Documentation score is {project_metrics['average_documentation_score']:.1f}%, below recommended 70%",
                    "action": "Add docstrings to functions, classes, and modules",
                    "impact": "Improves code understanding and maintenance",
                }
            )

        # Duplication recommendations
        if project_metrics["duplication_percentage"] > 5:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "duplication",
                    "title": "Reduce Code Duplication",
                    "description": f"Code duplication is {project_metrics['duplication_percentage']:.1f}%, above recommended 5%",
                    "action": "Extract common code into shared functions or classes",
                    "impact": "Reduces maintenance burden and improves consistency",
                }
            )

        # Code smells recommendations
        if project_metrics["total_code_smells"] > 10:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "code_smells",
                    "title": "Address Code Smells",
                    "description": f"Found {project_metrics['total_code_smells']} code smells",
                    "action": "Refactor code to eliminate smells and improve design",
                    "impact": "Improves code quality and maintainability",
                }
            )

        return recommendations

    def _save_analysis_results(self, results: Dict[str, Any]):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_file = self.reports_dir / f"code_quality_analysis_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        # Save HTML report
        html_file = self.reports_dir / f"code_quality_report_{timestamp}.html"
        html_content = self._generate_html_report(results)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save summary report
        summary_file = self.reports_dir / "code_quality_summary.md"
        summary_content = self._generate_summary_report(results)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)

        self.logger.info(f"Analysis results saved to {self.reports_dir}")

    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; }}
        .high-priority {{ border-left-color: #d32f2f; }}
        .medium-priority {{ border-left-color: #f57c00; }}
        .low-priority {{ border-left-color: #388e3c; }}
        .grade-A {{ color: #4caf50; font-weight: bold; }}
        .grade-B {{ color: #ff9800; font-weight: bold; }}
        .grade-C {{ color: #f44336; font-weight: bold; }}
        .recommendations {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Quality Analysis Report</h1>
        <p>Generated: {results['timestamp']}</p>
        <p>Project: {results['project_root']}</p>
        <p>Files analyzed: {results['total_files']}</p>
    </div>
    
    <h2>Project Metrics</h2>
    <div class="metric">
        <strong>Overall Quality Grade:</strong> 
        <span class="grade-{results['project_metrics']['quality_grade'][0]}">{results['project_metrics']['quality_grade']}</span>
    </div>
    <div class="metric">
        <strong>Average Score:</strong> {results['project_metrics']['average_overall_score']:.1f}/100
    </div>
    <div class="metric">
        <strong>Total Lines of Code:</strong> {results['project_metrics']['total_lines_of_code']:,}
    </div>
    <div class="metric">
        <strong>Average Complexity:</strong> {results['project_metrics']['average_complexity']:.1f}
    </div>
    <div class="metric">
        <strong>Security Issues:</strong> {results['project_metrics']['total_security_issues']}
    </div>
    <div class="metric">
        <strong>Style Violations:</strong> {results['project_metrics']['total_style_violations']}
    </div>
    <div class="metric">
        <strong>Code Duplication:</strong> {results['project_metrics']['duplication_percentage']:.1f}%
    </div>
    <div class="metric">
        <strong>Documentation Score:</strong> {results['project_metrics']['average_documentation_score']:.1f}%
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        """

        for rec in results["recommendations"]:
            priority_class = f"{rec['priority']}-priority"
            html += f"""
        <div class="metric {priority_class}">
            <h3>{rec['title']} ({rec['priority'].upper()} Priority)</h3>
            <p><strong>Issue:</strong> {rec['description']}</p>
            <p><strong>Action:</strong> {rec['action']}</p>
            <p><strong>Impact:</strong> {rec['impact']}</p>
        </div>
            """

        html += """
    </div>
</body>
</html>
        """

        return html

    def _generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown summary report"""
        summary = f"""# Code Quality Analysis Summary

**Generated:** {results['timestamp']}  
**Project:** {results['project_root']}  
**Files Analyzed:** {results['total_files']}

## Overall Assessment

**Quality Grade:** {results['project_metrics']['quality_grade']}  
**Average Score:** {results['project_metrics']['average_overall_score']:.1f}/100

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Lines of Code | {results['project_metrics']['total_lines_of_code']:,} |
| Average Complexity | {results['project_metrics']['average_complexity']:.1f} |
| Security Issues | {results['project_metrics']['total_security_issues']} |
| Style Violations | {results['project_metrics']['total_style_violations']} |
| Code Smells | {results['project_metrics']['total_code_smells']} |
| Code Duplication | {results['project_metrics']['duplication_percentage']:.1f}% |
| Documentation Score | {results['project_metrics']['average_documentation_score']:.1f}% |

## Priority Recommendations

"""

        for rec in results["recommendations"]:
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(rec["priority"], "⚪")
            summary += f"""### {priority_emoji} {rec['title']} ({rec['priority'].upper()})

**Issue:** {rec['description']}  
**Action:** {rec['action']}  
**Impact:** {rec['impact']}

"""

        return summary


def main():
    """Main code quality analysis execution"""
    analyzer = ComprehensiveCodeQualityAnalyzer()

    print("🔍 Comprehensive Code Quality Analysis for Horse Racing AI V2.03")
    print("=" * 70)

    # Run analysis
    results = analyzer.analyze_project()

    # Display summary
    print("\n📊 Analysis Results:")
    print(f"  Files Analyzed: {results['total_files']}")
    print(f"  Overall Grade: {results['project_metrics']['quality_grade']}")
    print(
        f"  Average Score: {results['project_metrics']['average_overall_score']:.1f}/100"
    )
    print(f"  Security Issues: {results['project_metrics']['total_security_issues']}")
    print(f"  Style Violations: {results['project_metrics']['total_style_violations']}")
    print(f"  Code Smells: {results['project_metrics']['total_code_smells']}")

    print(f"\n📝 Reports saved to: {analyzer.reports_dir}")

    # Display top recommendations
    if results["recommendations"]:
        print("\n🔧 Top Recommendations:")
        for i, rec in enumerate(results["recommendations"][:3], 1):
            print(f"  {i}. {rec['title']} ({rec['priority'].upper()} priority)")
            print(f"     {rec['description']}")

    print("\n✅ Code quality analysis completed")


if __name__ == "__main__":
    main()
