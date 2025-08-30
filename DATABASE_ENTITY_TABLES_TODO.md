# Database Entity Tables Implementation TODO

**Created:** August 30, 2025  
**Branch:** `testing-simulation-implementation`  
**Purpose:** Create indexed entity tables for horses, jockeys, and trainers with auto-increment keys  
**Database:** PostgreSQL (results, cards, advanced_metrics)

## ✅ **COMPLETED: PostgreSQL Configuration**

### **Environment Setup** ✅

- [x] **Removed MSSQL linting** - Updated VS Code settings for PostgreSQL
- [x] **Added PostgreSQL linting** - Configured proper PostgreSQL language support
- [x] **VS Code Extensions** - Recommended SQLTools with PostgreSQL driver
- [x] **Database Connections** - Configured for results, cards, advanced_metrics databases

### **Schema Creation** ✅

- [x] **Created database/schemas/ directory** - PostgreSQL schema files
- [x] **horses_entity.sql** - Complete PostgreSQL schema with constraints and triggers
- [x] **jockeys_entity.sql** - Complete PostgreSQL schema with performance metrics
- [x] **trainers_entity.sql** - Complete PostgreSQL schema with race type stats
- [x] **Added proper indexing** - Performance indexes for all entity tables
- [x] **Added constraints** - Data validation and referential integrity
- [x] **Added triggers** - Auto-update timestamps

### **Migration Tools** ✅

- [x] **setup_entity_tables.py** - Complete PostgreSQL migration script
- [x] **Connection testing** - PostgreSQL connection validation
- [x] **Table verification** - Schema validation and row counting
- [x] **Error handling** - Comprehensive error reporting

## 🎯 **Objective**

Create normalized database tables to store unique entities (horses, jockeys, trainers) with:

- Auto-increment primary keys for performance
- Original CSV IDs preserved for data integrity
- Optimized indexes for fast lookups
- Proper relational structure for race results

## 📊 **Data Analysis Results**

### **Horse Records (horses.csv)**

```
Primary ID Field: `id` (e.g., 37056, 57825, 66378)
Key Fields: id, name, country, age, color, owner, sire, dam, sex
Performance Fields: Total_races, Wins, Percentage_wins, placed, etc.
```

### **Jockey Records (jockeys_stats.csv)**

```
Primary ID Field: `Jockey_ID` (e.g., 1, 2, 3, 4)
Key Fields: Jockey_ID, Name
Performance Fields: Total_races, Wins, Percentage_wins, placed, etc.
```

### **Trainer Records (trainers_stats.csv)**

```
Primary ID Field: `Trainer_ID` (e.g., 1, 2)
Key Fields: Trainer_ID, Name
Performance Fields: Total_races, Wins, Percentage_wins, placed, etc.
```

## 📋 **Implementation Tasks**

### **Phase 1: Database Schema Design** 🔄

#### **Task 1.1: Create Horses Entity Table**

```sql
CREATE TABLE horses_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(10),
    age INTEGER,
    color VARCHAR(50),
    owner VARCHAR(255),
    sire VARCHAR(255),
    dam VARCHAR(255),
    dam_sire VARCHAR(255),
    sex VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_horses_original_id ON horses_entity(original_id);
CREATE INDEX idx_horses_name ON horses_entity(name);
CREATE INDEX idx_horses_owner ON horses_entity(owner);
```

#### **Task 1.2: Create Jockeys Entity Table**

```sql
CREATE TABLE jockeys_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jockeys_original_id ON jockeys_entity(original_id);
CREATE INDEX idx_jockeys_name ON jockeys_entity(name);
```

#### **Task 1.3: Create Trainers Entity Table**

```sql
CREATE TABLE trainers_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trainers_original_id ON trainers_entity(original_id);
CREATE INDEX idx_trainers_name ON trainers_entity(name);
```

### **Phase 2: Performance Statistics Tables** 🔄

#### **Task 2.1: Create Horse Performance Table**

```sql
CREATE TABLE horse_performance_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    horse_entity_id INTEGER,
    uptodate DATE,
    state VARCHAR(20),
    race_id_last_race INTEGER,
    date_last_race DATE,
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL(5,2) DEFAULT 0.00,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL(5,2) DEFAULT 0.00,
    -- Flat AW Statistics
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    -- Flat Turf Statistics
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    -- Chase Statistics
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL(5,2) DEFAULT 0.00,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    -- Hurdle Statistics
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL(5,2) DEFAULT 0.00,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (horse_entity_id) REFERENCES horses_entity(entity_id)
);

CREATE INDEX idx_horse_perf_entity_id ON horse_performance_stats(horse_entity_id);
CREATE INDEX idx_horse_perf_uptodate ON horse_performance_stats(uptodate);
```

#### **Task 2.2: Create Jockey Performance Table**

```sql
CREATE TABLE jockey_performance_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    jockey_entity_id INTEGER,
    uptodate DATE,
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL(5,2) DEFAULT 0.00,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL(5,2) DEFAULT 0.00,
    -- Performance by race type (same structure as horses)
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL(5,2) DEFAULT 0.00,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL(5,2) DEFAULT 0.00,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jockey_entity_id) REFERENCES jockeys_entity(entity_id)
);

CREATE INDEX idx_jockey_perf_entity_id ON jockey_performance_stats(jockey_entity_id);
CREATE INDEX idx_jockey_perf_uptodate ON jockey_performance_stats(uptodate);
```

#### **Task 2.3: Create Trainer Performance Table**

```sql
CREATE TABLE trainer_performance_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_entity_id INTEGER,
    uptodate DATE,
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL(5,2) DEFAULT 0.00,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL(5,2) DEFAULT 0.00,
    -- Performance by race type (same structure as horses and jockeys)
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL(5,2) DEFAULT 0.00,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL(5,2) DEFAULT 0.00,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL(5,2) DEFAULT 0.00,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_entity_id) REFERENCES trainers_entity(entity_id)
);

CREATE INDEX idx_trainer_perf_entity_id ON trainer_performance_stats(trainer_entity_id);
CREATE INDEX idx_trainer_perf_uptodate ON trainer_performance_stats(uptodate);
```

### **Phase 3: Data Import Scripts** 🔄

#### **Task 3.1: Create Horse Data Import Script**

- [ ] **File:** `import_horses_entities.py`
- [ ] Read horses CSV files from all available dates
- [ ] Extract unique horses by original_id
- [ ] Insert into horses_entity table with duplicate checking
- [ ] Import performance statistics into horse_performance_stats
- [ ] Handle data validation and error logging

#### **Task 3.2: Create Jockey Data Import Script**

- [ ] **File:** `import_jockeys_entities.py`
- [ ] Read jockeys_stats CSV files from all available dates
- [ ] Extract unique jockeys by Jockey_ID
- [ ] Insert into jockeys_entity table with duplicate checking
- [ ] Import performance statistics into jockey_performance_stats
- [ ] Handle data validation and error logging

#### **Task 3.3: Create Trainer Data Import Script**

- [ ] **File:** `import_trainers_entities.py`
- [ ] Read trainers_stats CSV files from all available dates
- [ ] Extract unique trainers by Trainer_ID
- [ ] Insert into trainers_entity table with duplicate checking
- [ ] Import performance statistics into trainer_performance_stats
- [ ] Handle data validation and error logging

### **Phase 4: Database Utilities** 🔄

#### **Task 4.1: Create Entity Lookup Functions**

```python
def get_horse_entity_id(original_id):
    """Get entity_id for horse by original CSV ID"""

def get_jockey_entity_id(original_id):
    """Get entity_id for jockey by original CSV ID"""

def get_trainer_entity_id(original_id):
    """Get entity_id for trainer by original CSV ID"""
```

#### **Task 4.2: Create Entity Statistics Functions**

```python
def get_horse_latest_stats(entity_id):
    """Get most recent performance stats for horse"""

def get_jockey_latest_stats(entity_id):
    """Get most recent performance stats for jockey"""

def get_trainer_latest_stats(entity_id):
    """Get most recent performance stats for trainer"""
```

#### **Task 4.3: Create Data Validation Functions**

```python
def validate_entity_data_integrity():
    """Validate all entity tables for data consistency"""

def check_duplicate_entities():
    """Check for potential duplicate entities across tables"""

def generate_entity_statistics_report():
    """Generate comprehensive report on entity table usage"""
```

### **Phase 5: Integration & Testing** 🔄

#### **Task 5.1: Update Race Results Schema**

- [ ] Modify race results tables to reference entity_id instead of original IDs
- [ ] Create foreign key relationships to entity tables
- [ ] Update existing queries to use entity lookups

#### **Task 5.2: Create Entity Management API Endpoints**

- [ ] `/api/entities/horses` - List all horses with pagination
- [ ] `/api/entities/horses/{entity_id}` - Get horse details and stats
- [ ] `/api/entities/jockeys` - List all jockeys with pagination
- [ ] `/api/entities/jockeys/{entity_id}` - Get jockey details and stats
- [ ] `/api/entities/trainers` - List all trainers with pagination
- [ ] `/api/entities/trainers/{entity_id}` - Get trainer details and stats

#### **Task 5.3: Performance Testing**

- [ ] Test entity lookup performance vs. original CSV ID lookups
- [ ] Benchmark database queries with indexes
- [ ] Test concurrent access to entity tables
- [ ] Validate memory usage with large datasets

## 🚀 **Implementation Priority**

### **High Priority (Week 1)**

1. **Database Schema Creation** (Tasks 1.1, 1.2, 1.3)
2. **Basic Entity Tables** (Without performance stats initially)
3. **Horse Data Import** (Task 3.1 - simplified version)

### **Medium Priority (Week 2)**

4. **Performance Statistics Tables** (Tasks 2.1, 2.2, 2.3)
5. **Complete Data Import Scripts** (Tasks 3.2, 3.3)
6. **Basic Utility Functions** (Task 4.1)

### **Lower Priority (Week 3)**

7. **Advanced Utilities** (Tasks 4.2, 4.3)
8. **API Integration** (Task 5.2)
9. **Performance Testing** (Task 5.3)

## 📁 **File Structure**

```
database/
├── entities/
│   ├── create_entity_tables.sql
│   ├── import_horses_entities.py
│   ├── import_jockeys_entities.py
│   ├── import_trainers_entities.py
│   └── entity_utilities.py
├── migrations/
│   ├── 001_create_horses_entity.sql
│   ├── 002_create_jockeys_entity.sql
│   ├── 003_create_trainers_entity.sql
│   ├── 004_create_performance_tables.sql
│   └── 005_create_indexes.sql
└── tests/
    ├── test_entity_import.py
    ├── test_entity_lookups.py
    └── test_performance_queries.py
```

## 🎯 **Success Metrics**

### **Performance Targets:**

- **Entity Lookup Time:** < 1ms for indexed lookups
- **Import Speed:** Process 10,000+ entities per minute
- **Memory Usage:** < 100MB for entity cache
- **Query Performance:** < 10ms for complex entity joins

### **Data Quality Targets:**

- **Uniqueness:** 100% unique entities by original_id
- **Completeness:** 99%+ data import success rate
- **Consistency:** 100% referential integrity maintenance
- **Accuracy:** 100% ID mapping validation

## 🔧 **Getting Started**

### **Step 1: Create Database Schema**

```bash
# Create the SQL scripts
mkdir -p database/entities database/migrations database/tests

# Start with horses entity table
sqlite3 results.db < database/migrations/001_create_horses_entity.sql
```

### **Step 2: Import Sample Data**

```bash
# Test with 2025-08-26 dataset first
python database/entities/import_horses_entities.py --date 2025-08-26 --test-mode
```

### **Step 3: Validate Results**

```bash
# Check entity creation
python database/tests/test_entity_import.py
```

---

**Ready to begin entity table implementation!** Start with horses entity table creation and basic import functionality.
