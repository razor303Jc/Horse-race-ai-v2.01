#!/usr/bin/env python3
"""
Stage 13 Code Quality Integration Runner
Simple script to execute the complete code quality pipeline
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.pipeline.stage13_code_quality_pipeline import Stage13CodeQualityPipeline


def run_stage13():
    """Run Stage 13 Code Quality and Structure pipeline"""
    print("🚀 Starting Stage 13: Code Quality and Structure")
    print("=" * 60)

    pipeline = Stage13CodeQualityPipeline()

    async def execute():
        try:
            print("📊 Running comprehensive code quality analysis...")
            report = await pipeline.run_complete_pipeline()

            print("\n✅ Stage 13 Code Quality Pipeline COMPLETED")
            print("=" * 60)
            print(f"📈 Overall Quality Score: {report.overall_score}/100")
            print(f"🧪 Test Coverage: {report.test_coverage:.1f}%")
            print(f"🔒 Security Score: {report.security_score:.1f}/100")
            print(f"🔧 Maintainability: {report.maintainability_score:.1f}/100")
            print(f"📦 Modularity: {report.modularity_score:.1f}/100")
            print(f"📚 Documentation: {report.documentation_score:.1f}%")
            print(f"⚠️ Critical Issues: {len(report.critical_issues)}")
            print(f"💡 Recommendations: {len(report.recommendations)}")
            print(f"🛣️ Improvement Roadmap: {len(report.improvement_roadmap)} phases")

            print(f"\n📁 Reports saved to: {pipeline.reports_dir}")

            return True

        except Exception as e:
            print(f"\n❌ Stage 13 pipeline failed: {e}")
            return False

    return asyncio.run(execute())


if __name__ == "__main__":
    success = run_stage13()
    sys.exit(0 if success else 1)
