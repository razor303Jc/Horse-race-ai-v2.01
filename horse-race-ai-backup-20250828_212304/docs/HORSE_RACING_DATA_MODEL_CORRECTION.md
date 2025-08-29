# Horse Racing Data Model - Field Definitions

## Correct Understanding of Horse Racing Terminology

**Date:** August 24, 2025  
**Context:** Schema Compatibility Checker Implementation  
**TODO ID:** 27 - Documentation Update

---

## 🐎 Critical Field Distinctions

### **Two Different Horse Identification Fields:**

#### 1. **`number` (Cloth Number)**

- **Purpose:** The number displayed on the horse's cloth/silks during the race
- **Always Present:** Yes - every horse has a race number
- **Data Type:** Integer (1-30 typically)
- **Example:** Horse wearing number 7 cloth
- **Database Field:** `number`, `horse_number`, `cloth_number`
- **Required:** YES - Critical for identification

#### 2. **`draw` (Starting Stall/Position)**

- **Purpose:** The stall/gate position where the horse starts the race
- **Always Present:** No - only for certain race types (flat races with stalls)
- **Data Type:** Integer (can be NULL)
- **Example:** Horse starts from stall 12, or NULL for jump races
- **Database Field:** `draw`, `stall`, `starting_stall`
- **Required:** NO - Can be NULL for jump races, some flat races

---

## ❌ Previous Incorrect Assumption

**WRONG:** `draw` and `number` are the same field with different names  
**CORRECT:** `draw` and `number` are completely different fields serving different purposes

---

## ✅ Corrected Schema Validation Rules

### **Required Fields (Must Always Exist):**

```json
{
  "racecard_details": [
    "race_id", // Race identifier
    "number", // Cloth number (ALWAYS required)
    "horse" // Horse name
  ]
}
```

### **Optional Fields (Can Be NULL):**

```json
{
  "allow_null_fields": [
    "draw", // Starting stall (NULL for jump races)
    "timeform_comments",
    "distance_btn",
    "odds",
    "sp"
  ]
}
```

### **Field Name Standardization:**

```json
{
  "field_name_standards": {
    "horse_number": "number", // Standardize to 'number'
    "cloth_number": "number", // Standardize to 'number'
    // "draw" stays as "draw" - different field!
    "horse_name": "horse",
    "jockey_name": "jockey"
  }
}
```

---

## 🔍 Schema Validation Logic

### **For AI Selections Model Training:**

1. **MUST have `number`** - Required for horse identification in race
2. **MAY have `draw`** - Optional starting position (can be NULL)
3. **Both fields can exist together** - they serve different purposes

### **Data Quality Checks:**

- `number`: Must be integer 1-30, never NULL
- `draw`: Can be integer 1-20 or NULL (depending on race type)
- No correlation required between `number` and `draw` values

---

## 🚨 Impact on Previous AI Selections Issue

### **What Actually Happened:**

- CSV had `draw` field but AI model expected `number` field
- These are **different data points** - not a naming issue
- Missing `number` (cloth number) caused model training to fail

### **Correct Solution:**

1. ✅ **Keep `draw` field** for stall positions (when available)
2. ✅ **Ensure `number` field** exists for cloth numbers
3. ✅ **Map variations** like `horse_number` → `number`
4. ✅ **Allow NULL `draw`** for races without starting stalls

---

## 📋 Updated Database Schema

### **Races Table:**

```sql
CREATE TABLE races (
  race_id VARCHAR PRIMARY KEY,
  date DATE NOT NULL,
  course VARCHAR NOT NULL,
  race_time TIME NOT NULL,
  race_type VARCHAR,  -- 'flat', 'jump', 'harness'
  -- ... other fields
);
```

### **Race Entries Table:**

```sql
CREATE TABLE racecard_details (
  detail_id SERIAL PRIMARY KEY,
  race_id VARCHAR NOT NULL,
  number INTEGER NOT NULL,      -- Cloth number (always required)
  draw INTEGER,                 -- Starting stall (can be NULL)
  horse VARCHAR NOT NULL,
  jockey VARCHAR,
  trainer VARCHAR,
  odds DECIMAL,
  -- ... other fields

  CONSTRAINT fk_race FOREIGN KEY (race_id) REFERENCES races(race_id)
);
```

---

## 🎯 Schema Checker Updates Applied

1. **Removed incorrect `draw → number` mapping**
2. **Added `draw` to nullable fields list**
3. **Kept `number` as required field**
4. **Added proper field pattern recognition**
5. **Updated validation logic to handle both fields**

---

## 💡 Key Takeaways

- **Horse racing has specific terminology** - cloth numbers vs stall positions
- **Schema validation must understand domain context**
- **NULL handling is critical** for optional race data
- **Field mapping requires racing knowledge** to be accurate

This correction ensures the Schema Compatibility Checker properly validates horse racing CSV data according to actual racing terminology and data requirements.
