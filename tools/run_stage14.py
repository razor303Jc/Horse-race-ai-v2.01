#!/usr/bin/env python3
"""
Stage 14 Security and Compliance Integration Runner
Simple script to execute the complete security and compliance pipeline
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.pipeline.stage14_security_pipeline import Stage14SecurityPipeline


def run_stage14():
    """Run Stage 14 Security and Compliance pipeline"""
    print("🔒 Starting Stage 14: Security and Compliance")
    print("=" * 60)
    
    pipeline = Stage14SecurityPipeline()
    
    async def execute():
        try:
            print("🛡️ Running comprehensive security assessment...")
            assessment = await pipeline.run_complete_pipeline()
            
            print("\n✅ Stage 14 Security and Compliance Pipeline COMPLETED")
            print("=" * 60)
            print(f"🛡️ Overall Security Score: {assessment.overall_security_score:.1f}/100")
            print(f"🔐 Secret Management: {assessment.secret_management_score:.1f}/100")
            print(f"🔍 Input Validation: {assessment.input_validation_score:.1f}/100")
            print(f"📋 Audit Logging: {assessment.audit_logging_score:.1f}/100")
            print(f"🔑 Authentication: {assessment.authentication_score:.1f}/100")
            print(f"📊 Compliance: {assessment.compliance_score:.1f}/100")
            print(f"⚠️ Vulnerabilities: {len(assessment.vulnerabilities)}")
            print(f"💡 Recommendations: {len(assessment.recommendations)}")
            print(f"📄 Compliance Frameworks: {len(assessment.compliance_status)}")
            
            print(f"\n📁 Reports saved to: {pipeline.reports_dir}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Stage 14 pipeline failed: {e}")
            return False
    
    return asyncio.run(execute())


if __name__ == "__main__":
    success = run_stage14()
    sys.exit(0 if success else 1)
