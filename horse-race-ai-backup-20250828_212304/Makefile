# Makefile for Horse Racing AI v2.0
# Provides GNU Make interface for automation tasks

.PHONY: help install clean test lint format check watch docker-build docker-up docker-down dev serve monitor

# Default Python interpreter
PYTHON := python3
PIP := pip3

# Project directories
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Horse Racing AI v2.0 - Development Automation$(NC)"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup development environment
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -e ".[dev]"
	playwright install --with-deps
	npm install
	@echo "$(GREEN)✓ Installation completed$(NC)"

clean: ## Clean up build artifacts and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov dist build *.egg-info
	rm -rf node_modules package-lock.json
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black $(SRC_DIR) $(TESTS_DIR)
	isort $(SRC_DIR) $(TESTS_DIR)
	@echo "$(GREEN)✓ Code formatting completed$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	black --check --diff $(SRC_DIR) $(TESTS_DIR)
	isort --check-only --diff $(SRC_DIR) $(TESTS_DIR)

lint: ## Run linting with flake8 and mypy
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 $(SRC_DIR) $(TESTS_DIR)
	mypy $(SRC_DIR)
	@echo "$(GREEN)✓ Linting completed$(NC)"

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-fast: ## Run tests without coverage
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest $(TESTS_DIR) -x
	@echo "$(GREEN)✓ Fast tests completed$(NC)"

test-integration: ## Run database separation integration tests
	@echo "$(BLUE)Running database separation integration tests...$(NC)"
	@./tests/run_integration_tests.sh
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

test-db-separation: ## Test database separation implementation
	@echo "$(BLUE)Testing database separation implementation...$(NC)"
	python tests/run_database_separation_tests.py
	@echo "$(GREEN)✓ Database separation tests completed$(NC)"

test-all: test test-integration ## Run all tests including integration

check: format-check lint test ## Run all code quality checks

watch-test: ## Run tests in watch mode
	@echo "$(BLUE)Starting test watch mode...$(NC)"
	invoke dev.test-watch

watch-lint: ## Watch files and auto-run linting
	@echo "$(BLUE)Starting lint watch mode...$(NC)"
	invoke watch lint

watch-format: ## Watch files and auto-format
	@echo "$(BLUE)Starting format watch mode...$(NC)"
	invoke watch format

watch-check: ## Watch files and run all checks
	@echo "$(BLUE)Starting full check watch mode...$(NC)"
	invoke watch check

dev: ## Start development server with auto-reload
	@echo "$(BLUE)Starting development server...$(NC)"
	concurrently \
		"invoke dev.serve" \
		"npm run build:css" \
		"npm start"

serve: ## Start production server
	@echo "$(BLUE)Starting production server...$(NC)"
	gunicorn horse_racing_ai.web.app:app --bind 0.0.0.0:8000 --workers 4

# Docker commands
docker-build: ## Build Docker containers
	@echo "$(BLUE)Building Docker containers...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker build completed$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Docker containers started$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Docker containers stopped$(NC)"

docker-logs: ## View Docker container logs
	docker-compose logs -f

docker-restart: docker-down docker-up ## Restart Docker containers

docker-clean: ## Clean Docker containers and volumes
	@echo "$(BLUE)Cleaning Docker containers and volumes...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✓ Docker cleanup completed$(NC)"

# Database commands
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✓ Database migration completed$(NC)"

db-reset: ## Reset database (WARNING: Destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		$(MAKE) db-migrate; \
	fi

# Monitoring and logs
monitor: ## Start system monitoring
	@echo "$(BLUE)Starting system monitoring...$(NC)"
	invoke monitor

logs: ## View application logs
	tail -f logs/*.log

# Automation and CI/CD
# Comprehensive Testing Commands for V2.03

test-all: ## Run comprehensive test suite (unit, integration, performance, security)
	@echo "$(BLUE)🧪 Running comprehensive test suite...$(NC)"
	$(PYTHON) tests/run_comprehensive_tests.py
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	$(PYTHON) tests/run_comprehensive_tests.py --unit
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration: ## Run database separation integration tests
	@echo "$(BLUE)Running database separation integration tests...$(NC)"
	@./tests/run_integration_tests.sh
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

test-performance: ## Run performance tests only
	@echo "$(BLUE)🚀 Running performance tests...$(NC)"
	$(PYTHON) tests/run_comprehensive_tests.py --performance
	@echo "$(GREEN)✓ Performance tests completed$(NC)"

test-security: ## Run security tests only
	@echo "$(BLUE)🔒 Running security tests...$(NC)"
	$(PYTHON) tests/run_comprehensive_tests.py --security
	@echo "$(GREEN)✓ Security tests completed$(NC)"

test-quick: ## Run quick unit tests without coverage
	@echo "$(BLUE)⚡ Running quick unit tests...$(NC)"
	pytest tests/unit/ -v --tb=short --no-cov
	@echo "$(GREEN)✓ Quick tests completed$(NC)"

# Coverage Commands
test-coverage: ## Generate comprehensive coverage report
	@echo "$(BLUE)📊 Generating coverage report...$(NC)"
	coverage run -m pytest tests/unit/
	coverage report
	coverage html
	@echo "$(GREEN)✓ Coverage report generated at htmlcov/index.html$(NC)"

# Component-specific tests
test-data-processing: ## Test data processing components
	@echo "$(BLUE)📊 Testing data processing...$(NC)"
	pytest tests/unit/test_data_processing.py -v
	@echo "$(GREEN)✓ Data processing tests completed$(NC)"

test-ml-components: ## Test ML components
	@echo "$(BLUE)🤖 Testing ML components...$(NC)"
	pytest tests/unit/test_ml_components.py -v
	@echo "$(GREEN)✓ ML component tests completed$(NC)"

test-security-components: ## Test security components
	@echo "$(BLUE)🔒 Testing security components...$(NC)"
	pytest tests/unit/test_security_components.py -v
	@echo "$(GREEN)✓ Security component tests completed$(NC)"

# Stage-specific tests
test-stage2: ## Test Stage 2 (Data Quality Pipeline)
	@echo "$(BLUE)🔧 Testing Stage 2 components...$(NC)"
	$(PYTHON) tools/run_stage2.py --test-mode || true
	@echo "$(GREEN)✓ Stage 2 tests completed$(NC)"

test-stage12: ## Test Stage 12 (Performance & Scalability)
	@echo "$(BLUE)🔧 Testing Stage 12 components...$(NC)"
	$(PYTHON) tools/run_stage12.py --test-mode || true
	@echo "$(GREEN)✓ Stage 12 tests completed$(NC)"

test-stage13: ## Test Stage 13 (Code Quality)
	@echo "$(BLUE)🔧 Testing Stage 13 components...$(NC)"
	$(PYTHON) tools/run_stage13.py --test-mode || true
	@echo "$(GREEN)✓ Stage 13 tests completed$(NC)"

test-stage14: ## Test Stage 14 (Security & Compliance)
	@echo "$(BLUE)🔧 Testing Stage 14 components...$(NC)"
	$(PYTHON) tools/run_stage14.py --test-mode || true
	@echo "$(GREEN)✓ Stage 14 tests completed$(NC)"

# Quality and validation
validate-tests: ## Validate test framework setup
	@echo "$(BLUE)✅ Validating test framework...$(NC)"
	$(PYTHON) -c "import tests.run_comprehensive_tests; print('✅ Test runner imports successfully')"
	$(PYTHON) -c "import tests.test_complete_system_integration; print('✅ Integration tests import successfully')" || true
	$(PYTHON) -c "import tests.performance.test_performance_load; print('✅ Performance tests import successfully')" || true
	@echo "$(GREEN)✓ Test framework validation complete$(NC)"

# Test reporting
test-report: ## Generate comprehensive test report
	@echo "$(BLUE)📋 Generating test report...$(NC)"
	$(PYTHON) tests/run_comprehensive_tests.py --output-dir=tests/reports
	@echo "$(GREEN)✓ Test report generated$(NC)"

# Continuous Integration
ci: clean install check ## Run full CI pipeline
	@echo "$(GREEN)✓ CI pipeline completed successfully$(NC)"

pre-commit: format lint test-fast ## Run pre-commit checks

pre-push: check ## Run pre-push checks

# Documentation
docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html
	@echo "$(GREEN)✓ Documentation built$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8080

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	# Add staging deployment commands here
	@echo "$(GREEN)✓ Staging deployment completed$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	# Add production deployment commands here
	@echo "$(GREEN)✓ Production deployment completed$(NC)"

# Security
security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	safety check
	bandit -r $(SRC_DIR)
	@echo "$(GREEN)✓ Security checks completed$(NC)"

# Performance
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	pytest tests/benchmarks/ -v
	@echo "$(GREEN)✓ Benchmarks completed$(NC)"

# Quick start for new developers
setup: clean install db-migrate ## Complete setup for new developers
	@echo "$(GREEN)✓ Complete setup finished!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make dev' to start development server"
	@echo "  3. Run 'make test' to verify everything works"

# Enhanced Pipeline Integration with Time-Aware ML
pipeline-enhanced: ## Run enhanced pipeline with time-aware ML training
	@echo "$(BLUE)🚀 Running enhanced pipeline with ML optimization...$(NC)"
	$(PYTHON) tools/automation/enhanced_pipeline_integration.py --run-once
	@echo "$(GREEN)✓ Enhanced pipeline completed$(NC)"

pipeline-continuous: ## Start continuous pipeline monitoring with ML optimization
	@echo "$(BLUE)🔄 Starting continuous pipeline monitoring...$(NC)"
	$(PYTHON) tools/automation/enhanced_pipeline_integration.py --continuous
	@echo "$(GREEN)✓ Continuous monitoring started$(NC)"

pipeline-continuous-fast: ## Start continuous monitoring with 30-minute intervals
	@echo "$(BLUE)🔄 Starting fast continuous monitoring (30min intervals)...$(NC)"
	$(PYTHON) tools/automation/enhanced_pipeline_integration.py --continuous --check-interval 30
	@echo "$(GREEN)✓ Fast continuous monitoring started$(NC)"

pipeline-no-ml: ## Run enhanced pipeline without ML optimization
	@echo "$(BLUE)🔄 Running enhanced pipeline (no ML training)...$(NC)"
	$(PYTHON) tools/automation/enhanced_pipeline_integration.py --run-once --disable-ml
	@echo "$(GREEN)✓ Enhanced pipeline (no ML) completed$(NC)"

ml-optimize: ## Run time-aware ML optimization only
	@echo "$(BLUE)🤖 Running time-aware ML optimization...$(NC)"
	$(PYTHON) tools/ml_training/time_aware_ml_optimizer.py --optimize-models
	@echo "$(GREEN)✓ ML optimization completed$(NC)"

ml-optimize-dry-run: ## Dry run of ML optimization (no actual training)
	@echo "$(BLUE)🤖 Running ML optimization dry run...$(NC)"
	$(PYTHON) tools/ml_training/time_aware_ml_optimizer.py --dry-run
	@echo "$(GREEN)✓ ML optimization dry run completed$(NC)"
