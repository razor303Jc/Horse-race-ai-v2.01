#!/bin/bash
# Quick Access Script for Horse Racing AI System
# Usage: ./quick_access.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏇 Horse Racing AI v2.04 - Quick Access${NC}"
echo "=============================================="

case "${1:-help}" in
    "status"|"s")
        echo -e "${YELLOW}📊 System Status${NC}"
        echo "Docker containers:"
        docker ps --filter "name=horse_racing" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "Database connectivity:"
        docker exec horse_racing_postgres_clean pg_isready -h localhost -p 5432 || echo "❌ Database not ready"
        ;;
    
    "morning"|"m")
        echo -e "${GREEN}🌅 Morning Briefing${NC}"
        cat morning_briefing.md
        ;;
    
    "evening"|"e")
        echo -e "${BLUE}🌆 Evening Debrief${NC}"
        cat evening_debrief.md
        ;;
    
    "ai"|"predict")
        echo -e "${GREEN}🤖 Generating AI Selections${NC}"
        docker exec horse_racing_ml_trainer_clean python /app/tools/ml_training/enhanced_selections.py
        ;;
    
    "save")
        if [ -z "$2" ]; then
            DATE=$(date +%Y-%m-%d)
        else
            DATE="$2"
        fi
        echo -e "${GREEN}💾 Saving AI Selections for ${DATE}${NC}"
        docker exec horse_racing_ml_trainer_clean python /app/tools/ml_training/simple_ai_selections_saver.py --date "$DATE"
        ;;
    
    "db"|"database")
        echo -e "${BLUE}🗄️ Database Access${NC}"
        docker exec -it horse_racing_postgres_clean psql -h localhost -U horse_racing -d cards_horse_racing_db
        ;;
    
    "test"|"t")
        echo -e "${YELLOW}🧪 Running Tests${NC}"
        ./run_tests.sh
        ;;
    
    "commit"|"c")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide commit message${NC}"
            echo "Usage: ./quick_access.sh commit \"your message\""
            exit 1
        fi
        echo -e "${GREEN}📝 Git Commit${NC}"
        git add -A
        git commit -m "$2"
        git push origin dev
        ;;
    
    "clean")
        echo -e "${YELLOW}🧹 Cleaning Root Directory${NC}"
        # Remove common temporary files
        find . -maxdepth 1 -name "*.tmp" -delete 2>/dev/null || true
        find . -maxdepth 1 -name "*.temp" -delete 2>/dev/null || true
        find . -maxdepth 1 -name "*.log" -exec mv {} logs/ \; 2>/dev/null || true
        echo "✅ Cleanup complete"
        ;;
    
    "links"|"l")
        echo -e "${BLUE}🔗 Symbolic Links Status${NC}"
        ls -la *.md *.sql *.yaml 2>/dev/null | grep " -> " || echo "No symbolic links found"
        ;;
    
    "todo")
        echo -e "${YELLOW}📋 Advanced TODO List${NC}"
        cat ADVANCED_TODO.md
        ;;
    
    "help"|"h"|*)
        echo -e "${GREEN}Available commands:${NC}"
        echo "  status, s     - Show system status"
        echo "  morning, m    - Show morning briefing"
        echo "  evening, e    - Show evening debrief"
        echo "  ai, predict   - Generate AI selections"
        echo "  save [date]   - Save AI selections (default: today)"
        echo "  db, database  - Access database shell"
        echo "  test, t       - Run test suite"
        echo "  commit, c     - Git commit with message"
        echo "  clean         - Clean up root directory"
        echo "  links, l      - Show symbolic links"
        echo "  todo          - Show advanced TODO list"
        echo "  help, h       - Show this help"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  ./quick_access.sh status"
        echo "  ./quick_access.sh save 2025-08-23"
        echo "  ./quick_access.sh commit \"feat: add new feature\""
        ;;
esac
