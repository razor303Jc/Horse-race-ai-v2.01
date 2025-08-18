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
