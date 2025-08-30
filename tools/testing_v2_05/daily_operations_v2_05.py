#!/usr/bin/env python3
"""
Daily Operations v2.05 - Horse Racing AI Testing & Simulation Strategy
Complete daily workflow automation with comprehensive testing and validation

Features:
- Complete daily data pipeline automation
- PostgreSQL entity table population and validation
- Performance monitoring and reporting
- Error recovery and data integrity checks
- Comprehensive testing framework integration
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import v2.05 modules
try:
    from .data_mapping_v2_05 import DataMappingV205
    from .data_validation_v2_05 import DataValidationV205, ValidationLevel
    from .data_processing_v2_05 import DataProcessorV205
    from .upload_system_v2_05 import UploadSystemV205, UploadConfig
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from data_mapping_v2_05 import DataMappingV205
    from data_validation_v2_05 import DataValidationV205, ValidationLevel
    from data_processing_v2_05 import DataProcessorV205
    from upload_system_v2_05 import UploadSystemV205, UploadConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyOperationsV205:
    """Complete daily operations automation for Testing & Simulation Strategy"""
    
    def __init__(self, connection_config: Optional[Dict[str, str]] = None):
        """Initialize daily operations system"""
        
        self.connection_config = connection_config or self._get_default_config()
        
        # Initialize v2.05 components
        self.mapper = DataMappingV205(self.connection_config)
        self.validator = DataValidationV205(ValidationLevel.STRICT)
        self.processor = DataProcessorV205(
            connection_config=self.connection_config,
            batch_size=1000
        )
        self.uploader = UploadSystemV205(
            connection_config=self.connection_config,
            upload_config=UploadConfig(
                batch_size=1000,
                max_workers=2,
                validate_before_upload=True,
                upsert_on_conflict=True
            )
        )
        
        # Operation tracking
        self.operation_log = []
        self.performance_metrics = {}
        
        logger.info("🚀 Daily Operations v2.05 initialized")
        logger.info("🎯 Testing & Simulation Strategy ready")
    
    def _get_default_config(self) -> Dict[str, str]:
        """Get default PostgreSQL connection configuration"""
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "results"),
            "user": os.environ.get("DB_USER", "horse_racing"),
            "password": os.environ.get("DB_PASSWORD", "secure_password_123")
        }
    
    def execute_daily_pipeline(self, data_date: str) -> Dict[str, Any]:
        """Execute complete daily data pipeline"""
        
        pipeline_start = time.time()
        
        logger.info(f"🗓️ Starting daily pipeline for {data_date}")
        
        pipeline_result = {
            "date": data_date,
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "overall_success": False,
            "total_records_processed": 0,
            "performance_metrics": {}
        }
        
        try:
            # Phase 1: Data Validation
            logger.info("📋 Phase 1: Data Validation")
            validation_result = self._execute_validation_phase(data_date)
            pipeline_result["phases"]["validation"] = validation_result
            
            if not validation_result["success"]:
                logger.error("❌ Validation phase failed - stopping pipeline")
                return pipeline_result
            
            # Phase 2: Data Processing
            logger.info("🔄 Phase 2: Data Processing")
            processing_result = self._execute_processing_phase(data_date)
            pipeline_result["phases"]["processing"] = processing_result
            
            if not processing_result["success"]:
                logger.error("❌ Processing phase failed - stopping pipeline")
                return pipeline_result
            
            # Phase 3: Data Upload
            logger.info("📤 Phase 3: Data Upload")
            upload_result = self._execute_upload_phase(data_date)
            pipeline_result["phases"]["upload"] = upload_result
            
            if not upload_result["success"]:
                logger.error("❌ Upload phase failed - stopping pipeline")
                return pipeline_result
            
            # Phase 4: Integrity Verification
            logger.info("🔍 Phase 4: Integrity Verification")
            verification_result = self._execute_verification_phase()
            pipeline_result["phases"]["verification"] = verification_result
            
            # Calculate final metrics
            pipeline_time = time.time() - pipeline_start
            pipeline_result["performance_metrics"] = {
                "total_pipeline_time_seconds": pipeline_time,
                "phases_completed": len(pipeline_result["phases"]),
                "average_phase_time": pipeline_time / len(pipeline_result["phases"])
            }
            
            # Aggregate record counts
            total_records = 0
            for phase_data in pipeline_result["phases"].values():
                if "records_processed" in phase_data:
                    total_records += phase_data["records_processed"]
            
            pipeline_result["total_records_processed"] = total_records
            pipeline_result["overall_success"] = all(
                phase["success"] for phase in pipeline_result["phases"].values()
            )
            
            if pipeline_result["overall_success"]:
                logger.info("✅ Daily pipeline completed successfully")
            else:
                logger.warning("⚠️ Daily pipeline completed with warnings")
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"❌ Daily pipeline failed: {str(e)}")
            pipeline_result["error"] = str(e)
            pipeline_result["end_time"] = datetime.now().isoformat()
            return pipeline_result
    
    def _execute_validation_phase(self, data_date: str) -> Dict[str, Any]:
        """Execute data validation phase"""
        
        phase_start = time.time()
        
        try:
            data_path = (
                f"/home/jc/Documents/Horse-race-ai-v2.05/data/"
                f"raw_csv_archives/{data_date}"
            )
            
            # Find data files
            test_files = []
            
            # Cards data
            cards_zip = f"{data_path}/raw_csv_cards_{data_date}_105906.zip"
            if Path(cards_zip).exists():
                extracted = self.processor.extract_csv_from_archive(
                    cards_zip, f"/tmp/validation_{data_date}"
                )
                test_files.extend(extracted)
            
            # Results data
            results_zip = f"{data_path}/raw_csv_results_{data_date}_105906.zip"
            if Path(results_zip).exists():
                extracted = self.processor.extract_csv_from_archive(
                    results_zip, f"/tmp/validation_{data_date}"
                )
                test_files.extend(extracted)
            
            # Validate files
            validation_report = self.validator.generate_data_quality_report(test_files)
            
            # Check validation success
            validation_success = all(
                result.is_valid for result in validation_report.validation_results
            )
            
            phase_time = time.time() - phase_start
            
            return {
                "success": validation_success,
                "files_validated": len(test_files),
                "records_processed": validation_report.total_rows,
                "validation_errors": sum(
                    len(result.errors) 
                    for result in validation_report.validation_results
                ),
                "validation_warnings": sum(
                    len(result.warnings) 
                    for result in validation_report.validation_results
                ),
                "phase_time_seconds": phase_time
            }
            
        except Exception as e:
            logger.error(f"Validation phase error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phase_time_seconds": time.time() - phase_start
            }
    
    def _execute_processing_phase(self, data_date: str) -> Dict[str, Any]:
        """Execute data processing phase"""
        
        phase_start = time.time()
        
        try:
            # Process complete dataset
            processing_results = self.processor.process_complete_dataset(data_date)
            
            # Calculate metrics
            total_processed = sum(
                stats.processed_records 
                for stats in processing_results.values()
            )
            
            processing_success = all(
                stats.error_records == 0 
                for stats in processing_results.values()
            )
            
            phase_time = time.time() - phase_start
            
            return {
                "success": processing_success,
                "entities_processed": len(processing_results),
                "records_processed": total_processed,
                "processing_errors": sum(
                    stats.error_records 
                    for stats in processing_results.values()
                ),
                "phase_time_seconds": phase_time,
                "entity_details": {
                    entity: {
                        "records": stats.processed_records,
                        "errors": stats.error_records,
                        "time": stats.processing_time_seconds
                    }
                    for entity, stats in processing_results.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Processing phase error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phase_time_seconds": time.time() - phase_start
            }
    
    def _execute_upload_phase(self, data_date: str) -> Dict[str, Any]:
        """Execute data upload phase"""
        
        phase_start = time.time()
        
        try:
            # Upload complete dataset
            upload_results = self.uploader.upload_complete_dataset(data_date)
            
            # Calculate metrics
            total_uploaded = sum(
                result.records_uploaded 
                for result in upload_results.values()
            )
            
            upload_success = all(
                result.success 
                for result in upload_results.values()
            )
            
            phase_time = time.time() - phase_start
            
            return {
                "success": upload_success,
                "entities_uploaded": len(upload_results),
                "records_processed": total_uploaded,
                "upload_failures": sum(
                    result.records_failed 
                    for result in upload_results.values()
                ),
                "phase_time_seconds": phase_time,
                "entity_details": {
                    entity: {
                        "uploaded": result.records_uploaded,
                        "failed": result.records_failed,
                        "time": result.upload_time_seconds
                    }
                    for entity, result in upload_results.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Upload phase error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phase_time_seconds": time.time() - phase_start
            }
    
    def _execute_verification_phase(self) -> Dict[str, Any]:
        """Execute integrity verification phase"""
        
        phase_start = time.time()
        
        try:
            verification_results = {}
            
            # Verify each entity type
            for entity_type in ["horses", "jockeys", "trainers"]:
                verification = self.uploader.verify_upload_integrity(entity_type)
                verification_results[entity_type] = verification
            
            # Check overall integrity
            verification_success = all(
                result.get("integrity_status") == "PASS" 
                for result in verification_results.values()
                if "integrity_status" in result
            )
            
            phase_time = time.time() - phase_start
            
            return {
                "success": verification_success,
                "entities_verified": len(verification_results),
                "phase_time_seconds": phase_time,
                "verification_details": verification_results
            }
            
        except Exception as e:
            logger.error(f"Verification phase error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phase_time_seconds": time.time() - phase_start
            }
    
    def simulate_daily_operations(self, start_date: str, days: int = 1) -> Dict[str, Any]:
        """Simulate multiple days of operations for testing"""
        
        simulation_start = time.time()
        
        logger.info(f"🎮 Starting {days}-day simulation from {start_date}")
        
        simulation_results = {
            "simulation_start": datetime.now().isoformat(),
            "start_date": start_date,
            "days_simulated": days,
            "daily_results": {},
            "summary_metrics": {}
        }
        
        base_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        for day_offset in range(days):
            current_date = base_date + timedelta(days=day_offset)
            date_str = current_date.strftime("%Y-%m-%d")
            
            logger.info(f"📅 Simulating day {day_offset + 1}: {date_str}")
            
            # Execute daily pipeline
            daily_result = self.execute_daily_pipeline(date_str)
            simulation_results["daily_results"][date_str] = daily_result
            
            # Add delay between days for realistic simulation
            if day_offset < days - 1:
                time.sleep(1)  # Small delay
        
        # Calculate simulation summary
        simulation_time = time.time() - simulation_start
        
        total_records = sum(
            day_result["total_records_processed"] 
            for day_result in simulation_results["daily_results"].values()
        )
        
        successful_days = sum(
            1 for day_result in simulation_results["daily_results"].values()
            if day_result["overall_success"]
        )
        
        simulation_results["summary_metrics"] = {
            "total_simulation_time_seconds": simulation_time,
            "total_records_processed": total_records,
            "successful_days": successful_days,
            "success_rate_percentage": (successful_days / days) * 100,
            "average_records_per_day": total_records / days,
            "average_processing_time_per_day": simulation_time / days
        }
        
        simulation_results["simulation_end"] = datetime.now().isoformat()
        
        logger.info(f"🎯 Simulation complete: {successful_days}/{days} days successful")
        
        return simulation_results
    
    def export_operation_report(self, results: Dict[str, Any], 
                               output_file: str) -> bool:
        """Export operation results to JSON report"""
        
        try:
            report_data = {
                "report_generated": datetime.now().isoformat(),
                "report_type": "daily_operations_v2_05",
                "results": results,
                "system_info": {
                    "mapper_version": "2.05",
                    "validator_version": "2.05", 
                    "processor_version": "2.05",
                    "uploader_version": "2.05"
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"📝 Operation report exported: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Report export failed: {str(e)}")
            return False


def main():
    """Main function for testing daily operations"""
    
    # Initialize daily operations
    daily_ops = DailyOperationsV205()
    
    print("🚀 Daily Operations v2.05 - Testing & Simulation Strategy")
    print("=" * 60)
    
    # Test with 2025-08-26 dataset
    test_date = "2025-08-26"
    
    try:
        print(f"📊 Executing daily pipeline for {test_date}...")
        
        # Execute single day pipeline
        pipeline_result = daily_ops.execute_daily_pipeline(test_date)
        
        # Display results
        print(f"\n✅ Pipeline Status: {'SUCCESS' if pipeline_result['overall_success'] else 'FAILED'}")
        print(f"📈 Total Records: {pipeline_result['total_records_processed']}")
        print(f"⏱️ Total Time: {pipeline_result['performance_metrics']['total_pipeline_time_seconds']:.2f}s")
        
        # Show phase details
        print(f"\n📋 Phase Results:")
        for phase_name, phase_data in pipeline_result["phases"].items():
            status = "✅" if phase_data["success"] else "❌"
            print(f"{status} {phase_name}: {phase_data.get('records_processed', 0)} records")
        
        # Export report
        report_file = f"/tmp/daily_operations_report_{test_date}.json"
        daily_ops.export_operation_report(pipeline_result, report_file)
        
        print(f"\n📝 Report exported: {report_file}")
        
        # Optional: Run simulation for multiple days
        simulate_multiple = input("\n🎮 Run 3-day simulation? (y/n): ").lower().strip()
        
        if simulate_multiple == 'y':
            print("\n🎮 Running 3-day simulation...")
            
            simulation_result = daily_ops.simulate_daily_operations(test_date, 3)
            
            print(f"🎯 Simulation Results:")
            print(f"📊 Success Rate: {simulation_result['summary_metrics']['success_rate_percentage']:.1f}%")
            print(f"📈 Total Records: {simulation_result['summary_metrics']['total_records_processed']}")
            
            # Export simulation report
            sim_report_file = f"/tmp/simulation_report_{test_date}.json"
            daily_ops.export_operation_report(simulation_result, sim_report_file)
            print(f"📝 Simulation report: {sim_report_file}")
        
    except Exception as e:
        print(f"❌ Daily operations failed: {str(e)}")
    
    print("\n🎯 Daily Operations v2.05 testing complete!")


if __name__ == "__main__":
    main()
