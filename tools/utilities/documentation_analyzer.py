#!/usr/bin/env python3
"""
Documentation Directory Analysis and Cleanup Tool
Analyzes all documentation files to categorize and organize for production pipeline
"""

import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class DocumentationAnalyzer:
    def __init__(self, base_path="/home/jc/Documents/Horse-race-ai-v2.01"):
        self.base_path = base_path
        self.documentation_path = os.path.join(base_path, "documentation")
        self.docs_path = os.path.join(base_path, "docs")

        # Status indicators for current relevance
        self.production_indicators = [
            "PRODUCTION READY",
            "READY FOR DEPLOYMENT",
            "COMPLETE",
            "FINAL STATUS",
            "SUCCESS",
            "OPERATIONAL",
            "HEALTHY",
        ]

        self.outdated_indicators = [
            "TODO",
            "ANALYSIS",
            "PLAN",
            "DRAFT",
            "TEMP",
            "OLD",
            "DEPRECATED",
            "ARCHIVED",
            "LEGACY",
        ]

        self.analysis_results = {
            "production_ready": [],
            "implementation_summaries": [],
            "status_reports": [],
            "outdated_plans": [],
            "guides_current": [],
            "guides_outdated": [],
            "duplicates": [],
            "consolidation_candidates": [],
            "removal_candidates": [],
        }

    def analyze_file_status(self, filepath):
        """Analyze a documentation file to determine its current status and relevance"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Get file stats
            stat = os.stat(filepath)
            file_size = stat.st_size
            mod_time = datetime.fromtimestamp(stat.st_mtime)

            # Analyze content
            status_score = 0
            content_upper = content.upper()

            # Check for production readiness indicators
            for indicator in self.production_indicators:
                if indicator in content_upper:
                    status_score += 5

            # Check for outdated indicators
            for indicator in self.outdated_indicators:
                if indicator in content_upper:
                    status_score -= 3

            # Check for implementation details vs planning
            implementation_patterns = [
                r"```python",
                r"def\s+\w+",
                r"class\s+\w+",
                r"✅",
                r"COMPLETE",
                r"IMPLEMENTATION",
                r"SYSTEM.*READY",
            ]

            planning_patterns = [
                r"TODO",
                r"PLAN",
                r"ANALYSIS",
                r"PROPOSAL",
                r"DESIGN",
                r"SPECIFICATION",
                r"REQUIREMENTS",
            ]

            for pattern in implementation_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    status_score += 2

            for pattern in planning_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    status_score -= 1

            # Check recency (files older than 30 days get penalty)
            days_old = (datetime.now() - mod_time).days
            if days_old > 30:
                status_score -= 2
            elif days_old > 60:
                status_score -= 4

            return {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "size": file_size,
                "modified": mod_time.isoformat(),
                "days_old": days_old,
                "status_score": status_score,
                "content_length": len(content),
                "line_count": len(content.split("\n")),
            }

        except Exception as e:
            return {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "error": str(e),
                "status_score": -10,
            }

    def find_duplicates_and_overlaps(self, files_analysis):
        """Find files with similar content or overlapping purposes"""
        duplicates = []

        # Group by similar names
        name_groups = defaultdict(list)
        for file_data in files_analysis:
            if "error" in file_data:
                continue

            base_name = file_data["filename"].upper()
            # Extract key terms
            key_terms = []
            for term in [
                "IMPLEMENTATION",
                "COMPLETE",
                "STATUS",
                "GUIDE",
                "ANALYSIS",
                "REPORT",
                "SUMMARY",
                "TODO",
                "PLAN",
            ]:
                if term in base_name:
                    key_terms.append(term)

            if key_terms:
                key = "_".join(sorted(key_terms))
                name_groups[key].append(file_data)

        # Find groups with multiple files
        for key, files in name_groups.items():
            if len(files) > 1:
                duplicates.append(
                    {
                        "category": key,
                        "files": files,
                        "action": (
                            "consolidate" if len(files) <= 3 else "review_manually"
                        ),
                    }
                )

        return duplicates

    def categorize_documentation(self):
        """Analyze all documentation files and categorize them"""
        print("🔍 Analyzing documentation directory structure...")

        all_files = []

        # Analyze documentation/ directory
        if os.path.exists(self.documentation_path):
            for file in os.listdir(self.documentation_path):
                if file.endswith(".md"):
                    filepath = os.path.join(self.documentation_path, file)
                    all_files.append(filepath)

        # Analyze docs/ directory
        if os.path.exists(self.docs_path):
            for root, dirs, files in os.walk(self.docs_path):
                for file in files:
                    if file.endswith(".md"):
                        filepath = os.path.join(root, file)
                        all_files.append(filepath)

        print(f"📊 Found {len(all_files)} documentation files to analyze")

        # Analyze each file
        files_analysis = []
        for filepath in all_files:
            analysis = self.analyze_file_status(filepath)
            files_analysis.append(analysis)

        # Categorize based on analysis
        for file_data in files_analysis:
            if "error" in file_data:
                self.analysis_results["removal_candidates"].append(file_data)
                continue

            score = file_data["status_score"]
            filename = file_data["filename"].upper()

            # Categorize by status score and content
            if score >= 8:
                self.analysis_results["production_ready"].append(file_data)
            elif "IMPLEMENTATION" in filename and "COMPLETE" in filename:
                self.analysis_results["implementation_summaries"].append(file_data)
            elif "STATUS" in filename or "REPORT" in filename:
                self.analysis_results["status_reports"].append(file_data)
            elif score < 0 or "TODO" in filename or "PLAN" in filename:
                self.analysis_results["outdated_plans"].append(file_data)
            elif "GUIDE" in filename and score > 0:
                self.analysis_results["guides_current"].append(file_data)
            elif "GUIDE" in filename:
                self.analysis_results["guides_outdated"].append(file_data)
            else:
                # Default categorization
                if score > 3:
                    self.analysis_results["implementation_summaries"].append(file_data)
                else:
                    self.analysis_results["removal_candidates"].append(file_data)

        # Find duplicates
        self.analysis_results["duplicates"] = self.find_duplicates_and_overlaps(
            files_analysis
        )

        return self.analysis_results

    def generate_cleanup_recommendations(self):
        """Generate specific cleanup recommendations"""
        recommendations = {
            "immediate_removal": [],
            "archive_candidates": [],
            "consolidation_tasks": [],
            "keep_production": [],
            "reorganization_plan": {},
        }

        # Files to remove immediately (outdated, errors, low value)
        for file_data in self.analysis_results["removal_candidates"]:
            if file_data["status_score"] < -5 or "error" in file_data:
                recommendations["immediate_removal"].append(file_data["filepath"])

        # Files to archive (outdated but potentially historical value)
        for file_data in self.analysis_results["outdated_plans"]:
            if file_data["days_old"] > 30:
                recommendations["archive_candidates"].append(file_data["filepath"])

        # Files to keep for production
        for category in [
            "production_ready",
            "implementation_summaries",
            "guides_current",
        ]:
            for file_data in self.analysis_results[category]:
                recommendations["keep_production"].append(file_data["filepath"])

        # Consolidation tasks
        for duplicate_group in self.analysis_results["duplicates"]:
            if len(duplicate_group["files"]) > 1:
                recommendations["consolidation_tasks"].append(
                    {
                        "category": duplicate_group["category"],
                        "files": [f["filepath"] for f in duplicate_group["files"]],
                        "recommended_action": duplicate_group["action"],
                    }
                )

        # Reorganization plan
        recommendations["reorganization_plan"] = {
            "production_docs/": [
                f["filepath"] for f in self.analysis_results["production_ready"]
            ],
            "implementation_summaries/": [
                f["filepath"] for f in self.analysis_results["implementation_summaries"]
            ],
            "current_guides/": [
                f["filepath"] for f in self.analysis_results["guides_current"]
            ],
            "archive/": recommendations["archive_candidates"],
            "remove/": recommendations["immediate_removal"],
        }

        return recommendations

    def create_cleanup_report(self):
        """Create comprehensive cleanup report"""
        analysis = self.categorize_documentation()
        recommendations = self.generate_cleanup_recommendations()

        # Calculate statistics
        total_files = sum(
            len(category)
            for category in analysis.values()
            if isinstance(category, list)
        )
        production_files = len(recommendations["keep_production"])
        removal_files = len(recommendations["immediate_removal"])
        archive_files = len(recommendations["archive_candidates"])

        efficiency_gain = (
            ((removal_files + archive_files) / total_files * 100)
            if total_files > 0
            else 0
        )

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_files_analyzed": total_files,
                "production_ready": production_files,
                "immediate_removal": removal_files,
                "archive_candidates": archive_files,
                "efficiency_gain_percent": round(efficiency_gain, 1),
            },
            "categorization": analysis,
            "recommendations": recommendations,
            "summary": {
                "action_required": removal_files + archive_files > 0,
                "consolidation_needed": len(recommendations["consolidation_tasks"]) > 0,
                "reorganization_recommended": True,
            },
        }

        return report


def main():
    """Run documentation analysis and generate cleanup report"""
    print("🔍 DOCUMENTATION DIRECTORY ANALYSIS")
    print("=" * 50)

    analyzer = DocumentationAnalyzer()
    report = analyzer.create_cleanup_report()

    # Save detailed report
    report_file = (
        "/home/jc/Documents/Horse-race-ai-v2.01/DOCUMENTATION_CLEANUP_ANALYSIS.json"
    )
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    stats = report["statistics"]
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"├── Total Files Analyzed: {stats['total_files_analyzed']}")
    print(f"├── Production Ready: {stats['production_ready']}")
    print(f"├── Immediate Removal: {stats['immediate_removal']}")
    print(f"├── Archive Candidates: {stats['archive_candidates']}")
    print(f"└── Efficiency Gain: {stats['efficiency_gain_percent']}%")

    print(f"\n🎯 RECOMMENDATIONS:")
    recs = report["recommendations"]
    print(f"├── Remove {len(recs['immediate_removal'])} outdated files")
    print(f"├── Archive {len(recs['archive_candidates'])} historical files")
    print(f"├── Consolidate {len(recs['consolidation_tasks'])} duplicate groups")
    print(f"└── Keep {len(recs['keep_production'])} production files")

    print(f"\n📁 DETAILED REPORT SAVED: {report_file}")

    return report


if __name__ == "__main__":
    main()
