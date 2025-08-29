#!/usr/bin/env python3
"""
📚 Documentation Consolidation Analyzer
======================================

Analyzes the docs directory to identify files that can be:
1. Summarized and consolidated
2. Archived as historical references
3. Converted to index/reference documents
4. Merged with similar content

Author: AI Assistant
Date: August 29, 2025
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json


class DocsConsolidationAnalyzer:
    def __init__(self, docs_path):
        self.docs_path = Path(docs_path)
        self.analysis_results = {
            "total_files": 0,
            "total_size": 0,
            "categories": defaultdict(list),
            "consolidation_opportunities": [],
            "duplicate_content": [],
            "archive_candidates": [],
            "empty_files": [],
        }

    def analyze_documentation(self):
        """Comprehensive analysis of documentation structure"""
        print("📚 Starting Documentation Consolidation Analysis...")

        # Scan all markdown files
        for file_path in self.docs_path.rglob("*.md"):
            if file_path.is_file():
                self._analyze_file(file_path)

        # Identify consolidation opportunities
        self._identify_consolidation_opportunities()
        self._identify_duplicate_content()
        self._identify_archive_candidates()

        return self.analysis_results

    def _analyze_file(self, file_path):
        """Analyze individual documentation file"""
        relative_path = file_path.relative_to(self.docs_path)
        file_size = file_path.stat().st_size
        modified_time = file_path.stat().st_mtime

        self.analysis_results["total_files"] += 1
        self.analysis_results["total_size"] += file_size

        # Check for empty files
        if file_size == 0:
            self.analysis_results["empty_files"].append(
                {"path": str(relative_path), "size": file_size}
            )
            return

        # Read content for analysis
        try:
            content = file_path.read_text(encoding="utf-8")

            # Categorize by content type
            category = self._categorize_file(relative_path, content)

            file_info = {
                "path": str(relative_path),
                "size": file_size,
                "modified": modified_time,
                "category": category,
                "content_summary": self._summarize_content(content),
                "word_count": len(content.split()),
            }

            self.analysis_results["categories"][category].append(file_info)

        except Exception as e:
            print(f"Error reading {relative_path}: {e}")

    def _categorize_file(self, file_path, content):
        """Categorize file based on name and content patterns"""
        filename = file_path.name.upper()
        content_upper = content.upper()

        # Priority categorization
        if "TODO" in filename or "TODO" in content_upper:
            return "todo_lists"
        elif any(word in filename for word in ["COMPLETE", "SUCCESS", "FINISHED"]):
            return "completion_reports"
        elif any(word in filename for word in ["SUMMARY", "REPORT"]):
            return "summary_reports"
        elif any(word in filename for word in ["IMPLEMENTATION", "INTEGRATION"]):
            return "implementation_docs"
        elif any(word in filename for word in ["GUIDE", "README"]):
            return "guides_and_references"
        elif any(word in filename for word in ["PLAN", "STRATEGY"]):
            return "planning_docs"
        elif "TEST" in filename:
            return "testing_docs"
        elif any(word in filename for word in ["STATUS", "TRACKING"]):
            return "status_tracking"
        elif "ML_" in filename or "AI_" in filename:
            return "ml_ai_docs"
        elif file_path.parent.name == "implementation":
            return "implementation_docs"
        elif file_path.parent.name == "guides":
            return "guides_and_references"
        elif file_path.parent.name == "status":
            return "status_tracking"
        else:
            return "general_docs"

    def _summarize_content(self, content):
        """Create brief content summary"""
        lines = content.split("\n")

        # Extract title and first few meaningful lines
        title = ""
        description = ""

        for line in lines:
            line = line.strip()
            if line.startswith("#") and not title:
                title = line.lstrip("#").strip()
            elif line and not line.startswith("#") and not description:
                description = line[:100] + "..." if len(line) > 100 else line
                break

        return {"title": title, "description": description, "line_count": len(lines)}

    def _identify_consolidation_opportunities(self):
        """Identify files that can be consolidated"""
        opportunities = []

        # Group similar TODO files
        todo_files = self.analysis_results["categories"]["todo_lists"]
        if len(todo_files) > 3:
            opportunities.append(
                {
                    "type": "todo_consolidation",
                    "description": f"Consolidate {len(todo_files)} TODO lists into master TODO",
                    "files": [f["path"] for f in todo_files],
                    "estimated_reduction": sum(f["size"] for f in todo_files) * 0.7,
                }
            )

        # Group completion reports
        completion_files = self.analysis_results["categories"]["completion_reports"]
        if len(completion_files) > 5:
            opportunities.append(
                {
                    "type": "completion_archive",
                    "description": f"Archive {len(completion_files)} completion reports",
                    "files": [f["path"] for f in completion_files],
                    "estimated_reduction": sum(f["size"] for f in completion_files)
                    * 0.8,
                }
            )

        # Group implementation docs
        impl_files = self.analysis_results["categories"]["implementation_docs"]
        if len(impl_files) > 10:
            opportunities.append(
                {
                    "type": "implementation_index",
                    "description": f"Create index for {len(impl_files)} implementation docs",
                    "files": [f["path"] for f in impl_files],
                    "estimated_reduction": sum(f["size"] for f in impl_files) * 0.5,
                }
            )

        self.analysis_results["consolidation_opportunities"] = opportunities

    def _identify_duplicate_content(self):
        """Identify files with similar content"""
        # Look for files with very similar titles
        all_files = []
        for category_files in self.analysis_results["categories"].values():
            all_files.extend(category_files)

        duplicates = []
        seen_titles = defaultdict(list)

        for file_info in all_files:
            title = file_info["content_summary"]["title"].lower()
            # Normalize title for comparison
            normalized = re.sub(r"[^a-z0-9]", "", title)
            if len(normalized) > 10:  # Only consider substantial titles
                seen_titles[normalized].append(file_info)

        for title, files in seen_titles.items():
            if len(files) > 1:
                duplicates.append(
                    {
                        "similar_title": title,
                        "files": [f["path"] for f in files],
                        "potential_duplicates": len(files),
                    }
                )

        self.analysis_results["duplicate_content"] = duplicates

    def _identify_archive_candidates(self):
        """Identify files that should be archived"""
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)  # 30 days ago

        candidates = []

        # Old completion reports
        for file_info in self.analysis_results["categories"]["completion_reports"]:
            if file_info["modified"] < cutoff_time:
                candidates.append(
                    {
                        "path": file_info["path"],
                        "reason": "Old completion report",
                        "age_days": (datetime.now().timestamp() - file_info["modified"])
                        / (24 * 3600),
                    }
                )

        # Large files that might be outdated
        for category_files in self.analysis_results["categories"].values():
            for file_info in category_files:
                if file_info["size"] > 20000 and file_info["modified"] < cutoff_time:
                    candidates.append(
                        {
                            "path": file_info["path"],
                            "reason": "Large outdated file",
                            "size": file_info["size"],
                            "age_days": (
                                datetime.now().timestamp() - file_info["modified"]
                            )
                            / (24 * 3600),
                        }
                    )

        self.analysis_results["archive_candidates"] = candidates

    def generate_report(self):
        """Generate comprehensive consolidation report"""
        report = []
        report.append("📚 DOCUMENTATION CONSOLIDATION ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Files: {self.analysis_results['total_files']}")
        report.append(f"Total Size: {self.analysis_results['total_size']:,} bytes")
        report.append("")

        # Category breakdown
        report.append("📂 DOCUMENTATION CATEGORIES")
        report.append("-" * 30)
        for category, files in self.analysis_results["categories"].items():
            if files:
                total_size = sum(f["size"] for f in files)
                report.append(
                    f"{category.replace('_', ' ').title()}: {len(files)} files ({total_size:,} bytes)"
                )
        report.append("")

        # Empty files
        if self.analysis_results["empty_files"]:
            report.append("🗑️  EMPTY FILES (IMMEDIATE CLEANUP)")
            report.append("-" * 30)
            for empty_file in self.analysis_results["empty_files"]:
                report.append(f"  • {empty_file['path']}")
            report.append("")

        # Consolidation opportunities
        report.append("🔧 CONSOLIDATION OPPORTUNITIES")
        report.append("-" * 30)
        for opportunity in self.analysis_results["consolidation_opportunities"]:
            report.append(f"• {opportunity['description']}")
            report.append(
                f"  Estimated size reduction: {opportunity['estimated_reduction']:,.0f} bytes"
            )
            report.append(f"  Files affected: {len(opportunity['files'])}")
            report.append("")

        # Archive candidates
        if self.analysis_results["archive_candidates"]:
            report.append("📦 ARCHIVE CANDIDATES")
            report.append("-" * 30)
            for candidate in self.analysis_results["archive_candidates"]:
                age = candidate.get("age_days", 0)
                report.append(
                    f"• {candidate['path']} ({candidate['reason']}, {age:.0f} days old)"
                )
            report.append("")

        # Recommendations
        report.append("💡 CONSOLIDATION RECOMMENDATIONS")
        report.append("-" * 30)
        report.append("1. **Immediate**: Remove empty files")
        report.append(
            "2. **High Priority**: Consolidate TODO lists into master document"
        )
        report.append("3. **Medium Priority**: Archive old completion reports")
        report.append("4. **Low Priority**: Create implementation documentation index")
        report.append("")

        # Summary statistics
        total_consolidation_savings = sum(
            op["estimated_reduction"]
            for op in self.analysis_results["consolidation_opportunities"]
        )
        report.append("📊 POTENTIAL IMPACT")
        report.append("-" * 30)
        report.append(
            f"Estimated size reduction: {total_consolidation_savings:,.0f} bytes"
        )
        report.append(
            f"File count reduction: ~{len(self.analysis_results['empty_files']) + len(self.analysis_results['archive_candidates'])}"
        )

        return "\n".join(report)


def main():
    """Main execution function"""
    docs_path = Path(__file__).parent.parent.parent / "docs"

    analyzer = DocsConsolidationAnalyzer(docs_path)
    results = analyzer.analyze_documentation()

    # Generate and save report
    report = analyzer.generate_report()
    print(report)

    # Save detailed results
    results_file = docs_path / "CONSOLIDATION_ANALYSIS_RESULTS.json"
    with open(results_file, "w") as f:
        # Convert defaultdict to regular dict for JSON serialization
        json_results = dict(results)
        json_results["categories"] = dict(json_results["categories"])
        json.dump(json_results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    main()
