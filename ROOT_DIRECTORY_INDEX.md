# 📁 ROOT DIRECTORY INDEX

**Horse Racing AI v2.04 - Key Files Reference**

---

## 🎯 **ESSENTIAL FILES (Always Keep in Root)**

### 📋 **Daily Operations**

- **`morning_briefing.md`** - Daily startup checklist and system status
- **`evening_debrief.md`** - End-of-day analysis and performance review
- **`ADVANCED_TODO.md`** → `docs/ADVANCED_AI_RACING_TODO_LIST.md` (symlink)

### 📖 **Documentation**

- **`README.md`** → `docs/README.md` (symlink) - Main project documentation
- **`Critical_path_to_resolution.md`** - Critical issues and resolution paths

### 🐳 **Docker & Configuration**

- **`docker-compose.clean.yml`** - Main Docker configuration
- **`.env`** - Environment variables (keep secure)
- **`example.env`** - Environment template
- **`pyproject.toml`** - Python project configuration
- **`pytest.ini`** - Testing configuration

### 🔧 **Build & Development**

- **`Makefile`** - Build automation commands
- **`run_tests.sh`** - Test execution script
- **`.gitignore`** - Git ignore patterns
- **`.flake8`** - Code style configuration

### 🚀 **Startup Scripts**

- **`start_daily_watcher.sh`** - Daily automation startup
- **`start_pipeline_integration.sh`** - Pipeline integration startup

---

## 📂 **DIRECTORY STRUCTURE OVERVIEW**

```
Horse-race-ai-v2.04/
├── 📋 morning_briefing.md              # Daily operations checklist
├── 🌆 evening_debrief.md               # Daily analysis report
├── 📖 README.md → docs/README.md       # Main documentation
├── 🎯 ADVANCED_TODO.md → docs/...      # Advanced features roadmap
├── 🐳 docker-compose.clean.yml         # Docker configuration
├── ⚙️  pyproject.toml                  # Python configuration
├── 🧪 pytest.ini                      # Testing setup
├── 🔧 Makefile                        # Build commands
├── 🚀 start_*.sh                      # Startup scripts
├── 📝 .env                            # Environment variables
├──
├── 📁 src/                            # Source code
├── 📁 tools/                          # Utility scripts
├── 📁 database/                       # Database schemas
├── 📁 docs/                           # Documentation
├── 📁 tests/                          # Test suite
├── 📁 config/                         # Configuration files
├── 📁 data/                           # Data storage
├── 📁 docker/                         # Docker configurations
├── 📁 scripts/                        # Automation scripts
├── 📁 templates/                      # Templates
└── 📁 logs/                           # Log files
```

---

## 🔗 **SYMBOLIC LINKS CREATED**

### 📋 **Documentation Links**

```bash
# Main documentation
ln -sf docs/README.md README.md

# Advanced todo list
ln -sf docs/ADVANCED_AI_RACING_TODO_LIST.md ADVANCED_TODO.md
```

### 🛠️ **Quick Access Commands**

```bash
# View all symbolic links
ls -la *.md | grep " -> "

# Update links if files move
ln -sf docs/README.md README.md
ln -sf docs/ADVANCED_AI_RACING_TODO_LIST.md ADVANCED_TODO.md
```

---

## 🎯 **FILE PURPOSES**

### 📅 **Daily Workflow Files**

| File                  | Purpose                     | When to Use                   |
| --------------------- | --------------------------- | ----------------------------- |
| `morning_briefing.md` | System startup checklist    | Every morning before starting |
| `evening_debrief.md`  | Performance analysis        | Every evening after racing    |
| `ADVANCED_TODO.md`    | Feature development roadmap | Planning and development      |

### 🐳 **System Configuration**

| File                       | Purpose                 | Critical Info          |
| -------------------------- | ----------------------- | ---------------------- |
| `docker-compose.clean.yml` | Container orchestration | Database & ML services |
| `.env`                     | Environment variables   | Passwords, API keys    |
| `pyproject.toml`           | Python dependencies     | Package management     |

### 🚀 **Automation Scripts**

| File                            | Purpose          | Usage                             |
| ------------------------------- | ---------------- | --------------------------------- |
| `start_daily_watcher.sh`        | Daily automation | `./start_daily_watcher.sh`        |
| `start_pipeline_integration.sh` | Pipeline startup | `./start_pipeline_integration.sh` |
| `run_tests.sh`                  | Test execution   | `./run_tests.sh`                  |

---

## ⚠️ **ROOT DIRECTORY RULES**

### ✅ **KEEP IN ROOT**

- Essential daily operation files
- Main configuration files
- Docker orchestration files
- Startup scripts
- Main documentation (via symlinks)

### ❌ **MOVE TO SUBDIRECTORIES**

- Temporary files → `/temp/` or `/cache/`
- Test files → `/tests/`
- Source code → `/src/`
- Utilities → `/tools/`
- Data files → `/data/`
- Documentation → `/docs/`

### 🔄 **SYMLINK STRATEGY**

- Keep original files in proper subdirectories
- Create symlinks in root for quick access
- Update symlinks if files are reorganized
- Document all symlinks in this index

---

## 🧹 **CLEANUP CHECKLIST**

### 📋 **Weekly Cleanup**

- [ ] Remove temporary files from root
- [ ] Check symlinks are valid
- [ ] Move misplaced files to correct directories
- [ ] Update this index if structure changes

### 🔍 **Files to Watch For**

- `*.tmp`, `*.temp` → Delete or move to `/temp/`
- `test_*.py` in root → Move to `/tests/`
- `*.log` → Move to `/logs/`
- Data files → Move to `/data/`
- Scripts → Move to `/scripts/` or `/tools/`

---

## 📞 **QUICK REFERENCE**

### 🚀 **Start System**

```bash
# Morning routine
cat morning_briefing.md
docker-compose -f docker-compose.clean.yml up -d
./start_daily_watcher.sh
```

### 🧪 **Run Tests**

```bash
./run_tests.sh
# OR
pytest tests/ -v
```

### 📊 **Evening Routine**

```bash
# Fill out debrief
nano evening_debrief.md
# Commit day's work
git add -A && git commit -m "feat: daily work $(date +%Y-%m-%d)"
```

---

_Keep this file updated when adding new essential files to the root directory_
