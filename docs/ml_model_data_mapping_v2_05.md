# ML Model Data Mapping Documentation v2.05

# Version Tag: latest:v2.05

# Horse Racing AI System - Data Processing Mappings

## NULL Value Mapping Strategy

### Standardized -0 Replacement

All NULL, missing, and empty values in the dataset are replaced with `-0` (negative zero).

**Rationale:**

- Creates consistent, traceable mapping across all data types
- Easily identifiable by ML models during training
- Distinguishes from legitimate zero values (0)
- Maintains numerical data type consistency
- Prevents data type conflicts during model training

### NULL Value Sources

The following representations are detected and converted to `-0`:

- `NULL`
- `null`
- `None`
- `nan`
- `NaN`
- `-` (dash)
- `` (empty string)
- `N/A`
- `n/a`

## Data Type Mappings

### Numeric Fields

**Original NULL → -0**

- Race times: `-0` = timing not recorded
- Distances: `-0` = distance not specified
- Weights: `-0` = weight not recorded
- Ages: `-0` = age unknown
- Ratings: `-0` = no rating available
- Percentages: `-0` = no data for calculation

### String Fields

**Original NULL → -0**

- Horse names: `-0` = name not recorded
- Jockey names: `-0` = jockey unknown
- Trainer names: `-0` = trainer unknown
- Course names: `-0` = course not specified

### ID Fields

**Original NULL → -0**

- Horse IDs: `-0` = horse not identified
- Jockey IDs: `-0` = jockey not identified
- Trainer IDs: `-0` = trainer not identified
- Race IDs: `-0` = race not identified

## ML Model Training Guidelines

### Feature Engineering

When using this data for ML model training:

1. **NULL Detection**: Use `value == -0` to identify missing values
2. **Feature Flags**: Consider creating boolean features like `has_weight = (weight != -0)`
3. **Imputation**: Replace `-0` with domain-appropriate values if needed
4. **Normalization**: Handle `-0` appropriately during scaling operations

### Example Code for Model Training

```python
# Detect missing values
missing_mask = (df == -0)

# Create feature flags
df['has_weight'] = (df['weight'] != -0).astype(int)
df['has_jockey_rating'] = (df['jockey_rating'] != -0).astype(int)

# Replace -0 with mean for specific features
df.loc[df['weight'] == -0, 'weight'] = df[df['weight'] != -0]['weight'].mean()
```

## Quality Metrics Tracking

### Processing Statistics

Each processing run tracks:

- Total NULL values found
- Total replacements made with `-0`
- Percentage of NULL values per table
- Column-wise NULL distribution

### Quality Scores

Quality assessment considers:

- NULL percentage thresholds (default: 25% max)
- Data completeness scores
- Consistency validation
- Type conversion success rates

## Data Tables and NULL Patterns

### Races Table

**Common NULL Fields:**

- `going_description`: Often missing for older races
- `prize_money`: Not always recorded
- `race_class`: May be unspecified

### Records Table

**High NULL Percentage Fields (Expected):**

- Sectional timings (`sec_1` through `sec_6`): 60-70% NULL (timing technology not always available)
- `video_detail`: Often missing
- `comment`: Frequently empty

### Horses Table

**Occasional NULL Fields:**

- `sire_name`: Breeding info may be missing
- `dam_name`: Breeding info may be missing
- `age`: Sometimes not recorded

### Statistics Tables (Jockeys/Trainers)

**Calculated Fields:**

- Percentages may be NULL when no races recorded
- Rates calculated from available data only

## Processing Validation

### Date Validation

- Filename dates vs content dates are cross-validated
- Discrepancies logged and corrected
- Date format standardized to YYYY-MM-DD

### Type Validation

- Numeric fields validated for proper conversion
- String fields checked for encoding issues
- Percentage fields normalized to decimal format

## Error Handling

### Data Quality Issues

1. **Date Mismatches**: Auto-corrected using content data over filename
2. **Type Conversion Errors**: Logged and quarantined
3. **Excessive NULL Values**: Flagged if over quality threshold
4. **Duplicate Records**: Identified and deduplicated

### Recovery Procedures

- Failed files moved to quarantine directory
- Processing reports generated for all runs
- Error logs maintained with detailed traceability
- Redis status tracking for monitoring

## Integration Points

### File Watcher Integration

The Enhanced File Watcher v2.05 automatically triggers processing with:

- Standardized `-0` NULL mapping
- Quality validation reporting
- Status updates to Redis cache
- C2 Command Center notifications

### Database Upload

Processed data uploaded to PostgreSQL with:

- NULL values as `-0` maintained
- Type consistency enforced
- Referential integrity validated
- Transaction rollback on errors

## Version History

### v2.05 (latest:v2.05) - 2025-08-30

- Implemented standardized `-0` NULL mapping
- Enhanced ML model compatibility
- Improved documentation and traceability
- Added comprehensive quality metrics

---

**Important Notes:**

1. Always use `-0` to identify missing values in ML models
2. Consider the high NULL percentage in sectional timing data as normal
3. Date discrepancies between filenames and content are automatically resolved
4. This mapping strategy ensures consistent model training across all data sources

**Contact:** Horse Racing AI Development Team  
**Last Updated:** 2025-08-30  
**Status:** Production Ready - latest:v2.05
