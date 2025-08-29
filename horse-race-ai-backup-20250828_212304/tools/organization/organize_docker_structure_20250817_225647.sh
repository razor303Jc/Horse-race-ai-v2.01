#!/bin/bash
# Docker Structure Organization Script
# Generated: 2025-08-17 22:56:47

echo "🐳 Starting Docker Structure Organization..."
echo "=" * 50

# Create backup
backup_dir="backup_before_organization_20250817_225647"
echo "📦 Creating backup: $backup_dir"
mkdir -p "$backup_dir"

# Function to safely move files
safe_move() {
    local source="$1"
    local destination="$2"
    local reason="$3"
    
    if [ -f "$source" ]; then
        echo "📂 Moving $source -> $destination ($reason)"
        mkdir -p "$(dirname "$destination")"
        cp "$source" "$backup_dir/"
        mv "$source" "$destination"
    else
        echo "⚠️  Warning: $source not found"
    fi
}

# Function to create directory structure
create_dirs() {
    echo "📁 Creating directory structure..."
    mkdir -p "scripts/"
    mkdir -p "scripts/automation/"
    mkdir -p "scripts/deployment/"
    mkdir -p "scripts/maintenance/"
    mkdir -p "scripts/testing/"
    mkdir -p "scripts/pipeline/"
    mkdir -p "docker/scripts/"
    mkdir -p "docs/"
    mkdir -p "config/"
    mkdir -p "tests/"
}

# Create directories
create_dirs

echo
echo "📂 Moving files..."

# Moving files to scripts/
safe_move "enhanced_preprocessing_pipeline.py" "scripts/pipeline/enhanced_preprocessing_pipeline.py" "Pipeline management script"
safe_move "upload_all_fresh_data.py" "scripts/automation/upload_all_fresh_data.py" "Automation script"
safe_move "integrated_auto_pipeline.py" "scripts/pipeline/integrated_auto_pipeline.py" "Pipeline management script"
safe_move "fixed_upload_test.py" "scripts/automation/fixed_upload_test.py" "Automation script"
safe_move "production_integration_summary.py" "scripts/automation/production_integration_summary.py" "General automation script"
safe_move "fix_schema_sizes.py" "scripts/maintenance/fix_schema_sizes.py" "Maintenance script"
safe_move "check_root_protection.py" "scripts/testing/check_root_protection.py" "Testing script"
safe_move "pipeline_performance_monitor.py" "scripts/pipeline/pipeline_performance_monitor.py" "Pipeline management script"
safe_move "simple_csv_uploader.py" "scripts/automation/simple_csv_uploader.py" "Automation script"
safe_move "working_csv_uploader.py" "scripts/automation/working_csv_uploader.py" "Automation script"
safe_move "upload_to_recovered_db.py" "scripts/automation/upload_to_recovered_db.py" "Automation script"
safe_move "process_monitor.py" "scripts/automation/process_monitor.py" "Automation script"
safe_move "test_ml_cycles.py" "scripts/testing/test_ml_cycles.py" "Testing script"
safe_move "quick_status_check.py" "scripts/testing/quick_status_check.py" "Testing script"
safe_move "test_pipeline_timeline.py" "scripts/pipeline/test_pipeline_timeline.py" "Pipeline management script"
safe_move "debug_upload_test.py" "scripts/automation/debug_upload_test.py" "Automation script"
safe_move "implementation_complete_summary.py" "scripts/automation/implementation_complete_summary.py" "General automation script"
safe_move "test_early_morning_schedule.py" "scripts/testing/test_early_morning_schedule.py" "Testing script"
safe_move "integrated_ai_launcher.py" "scripts/automation/integrated_ai_launcher.py" "Automation script"
safe_move "docker_debug_and_fix.py" "scripts/deployment/docker_debug_and_fix.py" "Deployment script"
safe_move "simulate_downloads.py" "scripts/automation/simulate_downloads.py" "General automation script"
safe_move "pipeline_process_tracker.py" "scripts/pipeline/pipeline_process_tracker.py" "Pipeline management script"
safe_move "validate_complete_docker_setup.py" "scripts/deployment/validate_complete_docker_setup.py" "Deployment script"
safe_move "manual_pipeline_trigger.py" "scripts/pipeline/manual_pipeline_trigger.py" "Pipeline management script"
safe_move "container_training_launcher.py" "scripts/automation/container_training_launcher.py" "Automation script"
safe_move "simple_form_analyzer.py" "scripts/automation/simple_form_analyzer.py" "General automation script"
safe_move "test_unified_trainer_basic.py" "scripts/testing/test_unified_trainer_basic.py" "Testing script"
safe_move "test_cached_features.py" "scripts/testing/test_cached_features.py" "Testing script"
safe_move "integrate_event_driven_pipeline.py" "scripts/pipeline/integrate_event_driven_pipeline.py" "Pipeline management script"
safe_move "working_auto_downloader.py" "scripts/automation/working_auto_downloader.py" "Automation script"
safe_move "test_pipeline_integration.py" "scripts/pipeline/test_pipeline_integration.py" "Pipeline management script"
safe_move "create_proper_schema.py" "scripts/automation/create_proper_schema.py" "Data management script"
safe_move "direct_csv_upload.py" "scripts/automation/direct_csv_upload.py" "Automation script"
safe_move "comprehensive_pipeline_monitor.py" "scripts/pipeline/comprehensive_pipeline_monitor.py" "Pipeline management script"
safe_move "git_pattern_upload.py" "scripts/automation/git_pattern_upload.py" "Automation script"
safe_move "incremental_test_upload.py" "scripts/automation/incremental_test_upload.py" "Automation script"
safe_move "complete_event_demo.py" "scripts/automation/complete_event_demo.py" "General automation script"
safe_move "test_updated_pipeline_timing.py" "scripts/pipeline/test_updated_pipeline_timing.py" "Pipeline management script"
safe_move "complete_data_fix_upload.py" "scripts/automation/complete_data_fix_upload.py" "Automation script"
safe_move "data_validator.py" "scripts/automation/data_validator.py" "Data management script"
safe_move "test_cache_simple.py" "scripts/testing/test_cache_simple.py" "Testing script"
safe_move "complete_data_management.py" "scripts/maintenance/complete_data_management.py" "Maintenance script"
safe_move "safe_upload_all.py" "scripts/automation/safe_upload_all.py" "Automation script"
safe_move "run_docker_auto_downloader.py" "scripts/automation/run_docker_auto_downloader.py" "Automation script"
safe_move "manual_upload.py" "scripts/automation/manual_upload.py" "Automation script"
safe_move "upload_fresh_data.py" "scripts/automation/upload_fresh_data.py" "Automation script"
safe_move "check_schema.py" "scripts/testing/check_schema.py" "Testing script"
safe_move "pipeline_comprehensive_fixes.py" "scripts/pipeline/pipeline_comprehensive_fixes.py" "Pipeline management script"
safe_move "simple_pipeline_monitor.py" "scripts/pipeline/simple_pipeline_monitor.py" "Pipeline management script"
safe_move "database_viewer.py" "scripts/automation/database_viewer.py" "Data management script"
safe_move "complete_codebase_cleanup.sh" "scripts/automation/complete_codebase_cleanup.sh" "General shell script"
safe_move "test_system_health.sh" "scripts/automation/test_system_health.sh" "General shell script"

# Moving files to docker/scripts/
safe_move "start_dev.sh" "docker/scripts/start_dev.sh" "Docker deployment script"
safe_move "start_ml_training_1000.sh" "docker/scripts/start_ml_training_1000.sh" "Docker deployment script"
safe_move "start_ml_training_2000.sh" "docker/scripts/start_ml_training_2000.sh" "Docker deployment script"
safe_move "enable_optional_services.sh" "docker/scripts/enable_optional_services.sh" "Docker deployment script"
safe_move "run_reports_docker.sh" "docker/scripts/run_reports_docker.sh" "Docker deployment script"
safe_move "startup-optimized.sh" "docker/scripts/startup-optimized.sh" "Docker deployment script"
safe_move "verify_startup.sh" "docker/scripts/verify_startup.sh" "Docker deployment script"
safe_move "enable_ml_service.sh" "docker/scripts/enable_ml_service.sh" "Docker deployment script"
safe_move "start_ml_training.sh" "docker/scripts/start_ml_training.sh" "Docker deployment script"
safe_move "fix_core_services.sh" "docker/scripts/fix_core_services.sh" "Docker deployment script"
safe_move "fresh_start_status.sh" "docker/scripts/fresh_start_status.sh" "Docker deployment script"
safe_move "deploy_early_morning_ml.sh" "docker/scripts/deploy_early_morning_ml.sh" "Docker deployment script"

# Moving files to docs/
safe_move "DOCKER_SERVICES_STATUS_REPORT.md" "docs/DOCKER_SERVICES_STATUS_REPORT.md" "Documentation file"
safe_move "STEP_1_VALIDATION_REPORT.md" "docs/STEP_1_VALIDATION_REPORT.md" "Documentation file"
safe_move "DOCKER_STRUCTURE_ORGANIZATION_COMPLETE.md" "docs/DOCKER_STRUCTURE_ORGANIZATION_COMPLETE.md" "Documentation file"
safe_move "BUY_ME_A_COFFEE_BLOG_POST.md" "docs/BUY_ME_A_COFFEE_BLOG_POST.md" "Documentation file"
safe_move "COMPREHENSIVE_PIPELINE_ARCHITECTURE.md" "docs/COMPREHENSIVE_PIPELINE_ARCHITECTURE.md" "Documentation file"
safe_move "PIPELINE_SUCCESS_REPORT.md" "docs/PIPELINE_SUCCESS_REPORT.md" "Documentation file"
safe_move "AUTO_DOWNLOADER_DEPLOYMENT_GUIDE.md" "docs/AUTO_DOWNLOADER_DEPLOYMENT_GUIDE.md" "Documentation file"
safe_move "ML_TRAINING_50_CYCLE_CONFIG.md" "docs/ML_TRAINING_50_CYCLE_CONFIG.md" "Documentation file"
safe_move "ML_TRAINING_COMPONENTS_ANALYSIS.md" "docs/ML_TRAINING_COMPONENTS_ANALYSIS.md" "Documentation file"
safe_move "EARLY_MORNING_ML_IMPLEMENTATION.md" "docs/EARLY_MORNING_ML_IMPLEMENTATION.md" "Documentation file"
safe_move "service_startup_plan.md" "docs/service_startup_plan.md" "Documentation file"
safe_move "MICROSERVICES_CLEANUP_COMPLETE.md" "docs/MICROSERVICES_CLEANUP_COMPLETE.md" "Documentation file"
safe_move "docker-microservices-analysis.md" "docs/docker-microservices-analysis.md" "Documentation file"
safe_move "ROOT_PROTECTION_IMPLEMENTATION.md" "docs/ROOT_PROTECTION_IMPLEMENTATION.md" "Documentation file"
safe_move "SYSTEM_STATUS_REPORT.md" "docs/SYSTEM_STATUS_REPORT.md" "Documentation file"
safe_move "ML_TRAINING_AUTOMATION_SUMMARY.md" "docs/ML_TRAINING_AUTOMATION_SUMMARY.md" "Documentation file"
safe_move "POST.md" "docs/POST.md" "Documentation file"
safe_move "DATABASE_ANALYSIS_REPORT.md" "docs/DATABASE_ANALYSIS_REPORT.md" "Documentation file"
safe_move "PROJECT_COMPLETION_REPORT.md" "docs/PROJECT_COMPLETION_REPORT.md" "Documentation file"

# Moving files to config/
safe_move "pipeline_monitoring_20250817_192543.json" "config/pipeline_monitoring_20250817_192543.json" "Documentation file"
safe_move "mkdocs-improved.yml" "config/mkdocs-improved.yml" "Documentation file"
safe_move "mkdocs-clean.yml" "config/mkdocs-clean.yml" "Documentation file"
safe_move "mkdocs.yml" "config/mkdocs.yml" "Documentation file"

echo
echo "🗑️  Cleaning up temporary files..."

echo
echo "✅ Organization completed!"
echo "📊 Summary:"
echo "   - Backup created: $backup_dir"
echo "   - Files organized into proper Docker structure"
echo "   - Ready for comprehensive testing"
echo
echo "🧪 Next steps:"
echo "   1. Review organized structure"
echo "   2. Update import paths if needed" 
echo "   3. Run comprehensive test suite"
echo "   4. Update Docker configurations"
