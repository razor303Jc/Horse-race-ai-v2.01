# Entity Tables Implementation TODO

**Created:** August 30, 2025  
**Database:** PostgreSQL (3 databases: results, cards, advanced_metrics)  
**Purpose:** Create indexed entity tables for horses, jockeys, and trainers

## 🎯 **Objective**

Create efficient entity tables with unique indexes for:

- **Horses** - Unique horse entities with CSV IDs and auto-increment keys
- **Jockeys** - Unique jockey entities with CSV IDs and auto-increment keys
- **Trainers** - Unique trainer entities with CSV IDs and auto-increment keys

## 📊 **CSV Data Analysis Results**

### **Horse IDs:**

- **Format:** Numeric (e.g., 1234567, 2345678)
- **Sample IDs:** 1234567, 2345678, 3456789, 4567890, 5678901
- **Usage:** Present in horse_details.csv and race results

### **Jockey IDs:**

- **Format:** Numeric (e.g., 12345, 23456)
- **Sample IDs:** 12345, 23456, 34567, 45678, 56789
- **Usage:** Present in horse_details.csv and race results

### **Trainer IDs:**

- **Format:** Numeric (e.g., 1234, 2345)
- **Sample IDs:** 1234, 2345, 3456, 4567, 5678
- **Usage:** Present in horse_details.csv

## 📋 **Implementation Tasks**

### **Phase 1: Database Schema Design** ⏳

#### **Task 1.1: Create Entity Schemas** 🔄

- [ ] Design `horses` entity table for all 3 databases
- [ ] Design `jockeys` entity table for all 3 databases
- [ ] Design `trainers` entity table for all 3 databases
- [ ] Add proper indexes and constraints
- [ ] Include audit fields (created_at, updated_at)

#### **Task 1.2: Create Migration Scripts** 📝

- [ ] Create PostgreSQL migration for `results` database
- [ ] Create PostgreSQL migration for `cards` database
- [ ] Create PostgreSQL migration for `advanced_metrics` database
- [ ] Add rollback scripts for each migration
- [ ] Test migrations on development environment

### **Phase 2: Schema Implementation** ⏳

#### **Task 2.1: Horses Entity Table** 🐎

```sql
-- Target schema for horses table
CREATE TABLE horses (
    id SERIAL PRIMARY KEY,                    -- Auto-increment key
    horse_id INTEGER UNIQUE NOT NULL,        -- CSV horse_id
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    weight_carried VARCHAR(20),
    jockey_id INTEGER,                       -- Foreign key to jockeys
    trainer_id INTEGER,                      -- Foreign key to trainers
    odds VARCHAR(50),
    draw_position INTEGER,
    last_ran DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Implementation Steps:**

- [ ] Create horses table in `results` database
- [ ] Create horses table in `cards` database
- [ ] Create horses table in `advanced_metrics` database
- [ ] Add indexes on horse_id, name, jockey_id, trainer_id
- [ ] Test table creation and constraints

#### **Task 2.2: Jockeys Entity Table** 🏇

```sql
-- Target schema for jockeys table
CREATE TABLE jockeys (
    id SERIAL PRIMARY KEY,                    -- Auto-increment key
    jockey_id INTEGER UNIQUE NOT NULL,       -- CSV jockey_id
    name VARCHAR(255) NOT NULL,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2),
    prize_money DECIMAL(15,2),
    claim_allowance VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Implementation Steps:**

- [ ] Create jockeys table in `results` database
- [ ] Create jockeys table in `cards` database
- [ ] Create jockeys table in `advanced_metrics` database
- [ ] Add indexes on jockey_id, name, win_percentage
- [ ] Test table creation and constraints

#### **Task 2.3: Trainers Entity Table** 👨‍🏫

```sql
-- Target schema for trainers table
CREATE TABLE trainers (
    id SERIAL PRIMARY KEY,                    -- Auto-increment key
    trainer_id INTEGER UNIQUE NOT NULL,      -- CSV trainer_id
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    total_horses INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2),
    prize_money DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Implementation Steps:**

- [ ] Create trainers table in `results` database
- [ ] Create trainers table in `cards` database
- [ ] Create trainers table in `advanced_metrics` database
- [ ] Add indexes on trainer_id, name, win_percentage
- [ ] Test table creation and constraints

### **Phase 3: Data Population** ⏳

#### **Task 3.1: Extract Unique Entities** 📊

- [ ] Create script to extract unique horses from CSV files
- [ ] Create script to extract unique jockeys from CSV files
- [ ] Create script to extract unique trainers from CSV files
- [ ] Handle data deduplication and normalization
- [ ] Generate entity population statistics

#### **Task 3.2: Populate Entity Tables** 🔄

- [ ] Populate horses table from 2025-08-26 dataset
- [ ] Populate jockeys table from 2025-08-26 dataset
- [ ] Populate trainers table from 2025-08-26 dataset
- [ ] Verify data integrity and constraints
- [ ] Generate population reports

#### **Task 3.3: Create Lookup Functions** 🔍

- [ ] Create function to get horse by CSV horse_id
- [ ] Create function to get jockey by CSV jockey_id
- [ ] Create function to get trainer by CSV trainer_id
- [ ] Add bulk lookup functions for performance
- [ ] Test all lookup functions

### **Phase 4: Integration & Testing** ⏳

#### **Task 4.1: Update Existing Tables** 🔗

- [ ] Add foreign key relationships to existing race tables
- [ ] Update horse_details imports to use entity tables
- [ ] Update race results imports to use entity tables
- [ ] Ensure referential integrity across all tables
- [ ] Test data consistency

#### **Task 4.2: Performance Testing** ⚡

- [ ] Benchmark entity table query performance
- [ ] Test lookup performance with large datasets
- [ ] Optimize indexes based on query patterns
- [ ] Compare performance before/after entity tables
- [ ] Document performance improvements

#### **Task 4.3: Data Validation** ✅

- [ ] Validate entity data against CSV sources
- [ ] Check for orphaned records in related tables
- [ ] Verify constraint enforcement
- [ ] Test entity table updates and deletions
- [ ] Create data validation reports

### **Phase 5: Documentation & Maintenance** ⏳

#### **Task 5.1: Documentation** 📚

- [ ] Document entity table schemas
- [ ] Create entity relationship diagrams
- [ ] Document lookup procedures and best practices
- [ ] Create maintenance procedures
- [ ] Update system architecture documentation

#### **Task 5.2: Automation Scripts** 🤖

- [ ] Create automated entity sync scripts
- [ ] Add entity table monitoring
- [ ] Create backup and restore procedures
- [ ] Add entity data cleanup routines
- [ ] Schedule automated maintenance tasks

## 🗂️ **File Structure**

```
database/
├── entities/
│   ├── horses_entity_schema.sql          # 🔄 To Create
│   ├── jockeys_entity_schema.sql         # 🔄 To Create
│   ├── trainers_entity_schema.sql        # 🔄 To Create
│   └── entity_relationships.sql          # 🔄 To Create
├── migrations/
│   ├── 001_create_horses_entity.sql      # 🔄 To Create
│   ├── 002_create_jockeys_entity.sql     # 🔄 To Create
│   ├── 003_create_trainers_entity.sql    # 🔄 To Create
│   └── 004_add_entity_relationships.sql  # 🔄 To Create
└── scripts/
    ├── populate_entities.py              # 🔄 To Create
    ├── entity_lookup_functions.sql       # 🔄 To Create
    └── entity_maintenance.py             # 🔄 To Create
```

## 🎯 **Success Criteria**

### **Performance Goals:**

- **Entity Lookups:** < 5ms for single entity lookup
- **Bulk Operations:** Handle 10,000+ entity operations efficiently
- **Storage Efficiency:** Reduce redundant data storage by 60%+
- **Query Performance:** 50%+ improvement in relational queries

### **Data Quality Goals:**

- **Uniqueness:** 100% unique entities across all tables
- **Referential Integrity:** 0 orphaned records
- **Data Consistency:** 100% match with CSV source data
- **Completeness:** All entities from test dataset captured

### **Integration Goals:**

- **Seamless Integration:** No disruption to existing workflows
- **Backward Compatibility:** Existing queries continue to work
- **Performance:** No degradation in current system performance
- **Maintainability:** Clear procedures for ongoing maintenance

## 🚀 **Getting Started**

### **Immediate Next Steps:**

1. **Review CSV data structure** - Confirm ID formats and patterns
2. **Create entity schemas** - Design optimal table structures
3. **Test on development** - Validate approach before production
4. **Create migration scripts** - Prepare for database updates

### **Quick Start Commands:**

```bash
# 1. Check PostgreSQL connection
docker exec -it horse_racing_postgres_clean psql -U horse_racing -d postgres

# 2. Review existing schemas
ls -la database/schemas/

# 3. Start with horses entity
# Create: database/entities/horses_entity_schema.sql

# 4. Test schema creation
# psql -U horse_racing -d results_horse_racing_db -f database/entities/horses_entity_schema.sql
```

---

**Ready to begin implementation!** Start with Phase 1 (Schema Design) and work systematically through each phase.
