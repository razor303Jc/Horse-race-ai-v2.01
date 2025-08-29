#!/bin/bash

# 🏇 Horse Racing AI - Comprehensive System Test
# Generated: August 28, 2025

echo "🚀 Starting comprehensive system test for Horse Racing AI platform..."
echo "============================================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

test_service() {
    local service_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -e "${BLUE}Testing: $service_name${NC}"
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✅ PASS: $service_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL: $service_name${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}📋 Infrastructure Services Tests${NC}"
echo "----------------------------------------"

# Test Docker containers
test_service "Docker containers running" "docker ps | grep -q horse_racing"

# Test Traefik
test_service "Traefik reverse proxy" "curl -f http://localhost:8080/api/overview"

# Test PostgreSQL
test_service "PostgreSQL main database" "docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c 'SELECT 1;'"

# Test specialized databases
test_service "Cards database" "docker exec horse_racing_postgres_clean psql -U horse_racing -d cards_horse_racing_db -c 'SELECT 1;'"
test_service "Results database" "docker exec horse_racing_postgres_clean psql -U horse_racing -d results_horse_racing_db -c 'SELECT 1;'"
test_service "Advanced metrics database" "docker exec horse_racing_postgres_clean psql -U horse_racing -d advanced_racing_metrics_db -c 'SELECT 1;'"

# Test Redis
test_service "Redis cache" "docker exec horse_racing_redis_clean redis-cli -a redis_password_123 ping"

echo ""
echo -e "${YELLOW}🌐 Application Services Tests${NC}"
echo "----------------------------------------"

# Test Web Application
test_service "Main web application" "curl -f http://localhost:3000"
test_service "Web app health check" "curl -f http://localhost:3000/health"

# Test PgAdmin
test_service "PgAdmin database manager" "curl -f http://localhost:8083"

echo ""
echo -e "${YELLOW}🤖 Node-RED Automation Tests${NC}"
echo "----------------------------------------"

# Test Node-RED
test_service "Node-RED web interface" "curl -f http://localhost:1881"
test_service "Node-RED dashboard" "curl -f http://localhost:1881/ui"

# Test Node-RED packages
test_service "Node-RED Dashboard package" "docker exec horse_racing_node_red_custom ls /data/node_modules/node-red-dashboard"
test_service "Node-RED Cron package" "docker exec horse_racing_node_red_custom ls /data/node_modules/node-red-contrib-cron-plus"
test_service "Node-RED Email package" "docker exec horse_racing_node_red_custom ls /data/node_modules/node-red-node-email"
test_service "Node-RED PostgreSQL package" "docker exec horse_racing_node_red_custom ls /data/node_modules/node-red-contrib-postgres-multi"

echo ""
echo -e "${YELLOW}🔗 Network Connectivity Tests${NC}"
echo "----------------------------------------"

# Test internal network connectivity
test_service "Database from web app" "docker exec horse_racing_web_app_clean nc -z postgres 5432"
test_service "Redis from web app" "docker exec horse_racing_web_app_clean nc -z redis 6379"
test_service "Database from Node-RED" "docker exec horse_racing_node_red_custom nc -z host.docker.internal 5432"

echo ""
echo -e "${YELLOW}🏥 Health Check Tests${NC}"
echo "----------------------------------------"

# Container health checks
CONTAINERS=("horse_racing_postgres_clean" "horse_racing_redis_clean" "horse_racing_web_app_clean" "horse_racing_ml_trainer_clean" "horse_racing_node_red_custom")

for container in "${CONTAINERS[@]}"; do
    if docker inspect "$container" --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy\|starting"; then
        test_service "$container health" "true"
    elif docker inspect "$container" --format='{{.State.Status}}' 2>/dev/null | grep -q "running"; then
        test_service "$container running" "true"
    else
        test_service "$container status" "false"
    fi
done

echo ""
echo "============================================================================"
echo -e "${BLUE}📊 TEST RESULTS SUMMARY${NC}"
echo "============================================================================"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo -e "${GREEN}✅ Passed: $TESTS_PASSED/$TOTAL_TESTS tests${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED/$TOTAL_TESTS tests${NC}"
echo -e "${BLUE}📈 Success Rate: $SUCCESS_RATE%${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    echo -e "${GREEN}🏇 Horse Racing AI platform is fully operational!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Quick Access Links:${NC}"
    echo "• Main Application:    http://localhost:3000"
    echo "• Node-RED Editor:     http://localhost:1881"
    echo "• Node-RED Dashboard:  http://localhost:1881/ui"
    echo "• Traefik Dashboard:   http://localhost:8080"
    echo "• PgAdmin:            http://localhost:8083"
    echo ""
    echo -e "${YELLOW}🔧 Next Steps:${NC}"
    echo "1. Configure Node-RED flows for automation"
    echo "2. Set up email notifications with Gmail"
    echo "3. Create custom dashboards"
    echo "4. Schedule data processing jobs"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Please check the services above.${NC}"
    echo -e "${YELLOW}💡 Troubleshooting tips:${NC}"
    echo "• Check container logs: docker logs <container_name>"
    echo "• Restart services: docker-compose restart <service>"
    echo "• Verify network connectivity"
    exit 1
fi
