# Root Directory Cleanup & Organization Plan

## Status: In Progress

### 📂 Current Root Directory Issues

- Multiple standalone scripts that should be in proper directories
- Test files scattered in root instead of tests/ directory
- Configuration files mixed with implementation files
- Documentation files not organized
- Temporary/debug files cluttering root
- AI selections files not properly organized

### 🎯 Organization Strategy

#### 1. **Documentation Files** → `docs/`

- `*.md` files (implementation summaries, guides, reports)
- Keep only `README.md` in root

#### 2. **Test Files** → `tests/`

- `test_*.py` files
- `quick_*_test.py` files
- Test results and logs

#### 3. **Scripts & Tools** → `scripts/` or `tools/`

- Standalone analysis scripts
- Utility scripts
- Demo scripts

#### 4. **Configuration** → `config/`

- Analysis configurations
- Pipeline configurations

#### 5. **Temporary/Debug Files** → Remove or Archive

- Debug scripts
- Temporary output files
- Log files older than current session

#### 6. **AI Selections Integration** → Proper Module Structure

- Move AI selections files to appropriate src/ directories
- Integrate with existing pipeline
- Add to Docker configuration

### 🔄 Integration Plan

#### A. **Pipeline Integration**

1. Add AI selections tracking to existing pipeline stages
2. Update configuration management
3. Add monitoring and reporting

#### B. **Docker Integration**

1. Update Dockerfile dependencies
2. Add AI selections services
3. Update docker-compose configuration
4. Add environment variables

#### C. **Web App Integration**

1. Add AI selections dashboard routes
2. Update templates for new features
3. Add API endpoints
4. Update monitoring dashboards

### 📋 Execution Steps

1. ✅ Analyze current structure
2. 🔄 Move files to correct directories
3. ⏳ Update import paths
4. ⏳ Update configuration files
5. ⏳ Integrate with pipeline
6. ⏳ Update Docker configuration
7. ⏳ Test integrated system
8. ⏳ Update documentation

Let's begin the cleanup process...
