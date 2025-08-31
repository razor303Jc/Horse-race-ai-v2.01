#!/bin/bash
# 🧹 Root Directory Cleanup Script
# Reorganizes files into proper directory structure

echo "🧹 Starting Root Directory Cleanup..."

# Create organized directory structure
mkdir -p {docs/{reports,plans,guides,analysis},tests/results,scripts/{automation,database,api,pipeline},flows/backups,configs,logs/archive}

# 1. Move Documentation Files
echo "📚 Moving documentation files..."

# Reports
mv *_REPORT.md docs/reports/ 2>/dev/null || true
mv *_SUCCESS_REPORT.md docs/reports/ 2>/dev/null || true  
mv *_COMPLETION_REPORT.md docs/reports/ 2>/dev/null || true
mv *_ANALYSIS_REPORT.md docs/reports/ 2>/dev/null || true
mv *_SUMMARY.md docs/reports/ 2>/dev/null || true

# Plans and TODOs
mv *_TODO.md docs/plans/ 2>/dev/null || true
mv *_PLAN.md docs/plans/ 2>/dev/null || true
mv NEXT_PRIORITY_TASKS_AUG30.md docs/plans/ 2>/dev/null || true
mv POST_AUTOMATION_TODO_AUG30.md docs/plans/ 2>/dev/null || true
mv CURRENT_PRIORITY_TODO_AUG25.md docs/plans/ 2>/dev/null || true

# Guides and Documentation  
mv *_GUIDE.md docs/guides/ 2>/dev/null || true
mv *_DOCUMENTATION.md docs/guides/ 2>/dev/null || true
mv SETUP_COMPLETION_REPORT.md docs/guides/ 2>/dev/null || true
mv TECHNICAL_IMPLEMENTATION_GUIDE.md docs/guides/ 2>/dev/null || true
mv TESTING_*.md docs/guides/ 2>/dev/null || true

# Analysis and Notes
mv *_ANALYSIS.md docs/analysis/ 2>/dev/null || true
mv *_NOTES.md docs/analysis/ 2>/dev/null || true
mv evening_debrief.md docs/analysis/ 2>/dev/null || true
mv morning_briefing.md docs/analysis/ 2>/dev/null || true

# 2. Move Test Files and Results
echo "🧪 Moving test files..."
mv test_*.py tests/ 2>/dev/null || true
mv *_test.py tests/ 2>/dev/null || true  
mv test_results_*/ tests/results/ 2>/dev/null || true
mv test_results_summary.md tests/results/ 2>/dev/null || true

# 3. Move Scripts
echo "🔧 Moving scripts..."
mv *pipeline*.py scripts/pipeline/ 2>/dev/null || true
mv *automation*.py scripts/automation/ 2>/dev/null || true
mv *database*.py scripts/database/ 2>/dev/null || true
mv setup_entity_*.py scripts/database/ 2>/dev/null || true
mv deploy_*.py scripts/automation/ 2>/dev/null || true
mv simulate_*.py scripts/automation/ 2>/dev/null || true
mv upload_*.py scripts/database/ 2>/dev/null || true
mv process_*.py scripts/database/ 2>/dev/null || true
mv debug_*.py scripts/database/ 2>/dev/null || true
mv quick_*.py scripts/api/ 2>/dev/null || true
mv api_load_testing.py scripts/api/ 2>/dev/null || true

# 4. Move Flow Files
echo "🌊 Moving Node-RED flow files..."
mv *.json flows/ 2>/dev/null || true
mv flows_*.json flows/backups/ 2>/dev/null || true
mv backup_flows_*.json flows/backups/ 2>/dev/null || true

# 5. Move Configuration Files  
echo "⚙️ Moving configuration files..."
mv *.env* configs/ 2>/dev/null || true
mv ML_CONFIG.yaml configs/ 2>/dev/null || true

# 6. Move Shell Scripts
echo "🐚 Moving shell scripts..."
mv *.sh scripts/ 2>/dev/null || true

# 7. Move JavaScript Files  
echo "🟨 Moving JavaScript files..."
mv *.js flows/ 2>/dev/null || true

# 8. Archive old log and temporary files
echo "🗂️ Archiving temporary files..."
mv api_load_test_results_*.json logs/archive/ 2>/dev/null || true

# 9. Keep important files in root
echo "📌 Keeping essential files in root..."
# Keep: README.md, Makefile, pyproject.toml, pytest.ini, .gitignore, AI_SCHEMA.sql, ADVANCED_TODO.md

echo "✅ Root directory cleanup completed!"
echo "📁 Files organized into:"
echo "   📚 docs/ - Documentation, reports, guides, plans"  
echo "   🧪 tests/ - Test files and results"
echo "   🔧 scripts/ - Python scripts organized by category"
echo "   🌊 flows/ - Node-RED flows and JavaScript files"
echo "   ⚙️ configs/ - Configuration files"
echo "   📊 logs/ - Log files and archives"
echo ""
echo "🔍 Please review the organization and test the system!"
