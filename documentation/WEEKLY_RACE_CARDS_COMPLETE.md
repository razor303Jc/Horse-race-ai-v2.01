# Weekly Race Cards System - Complete Implementation

## Overview

This document describes the complete Weekly Race Cards system that generates realistic 7-day racing schedules with progressive daily release functionality. This enables comprehensive testing of the Horse Racing AI system with realistic data flow patterns.

## System Architecture

### Core Components

1. **WeeklyRaceCardsGenerator** (`tests/weekly_race_cards_generator.py`)

   - Generates complete weekly racing schedules
   - Creates realistic UK/Irish racing patterns
   - Manages database schema and data insertion

2. **DailyRaceSimulator** (`tests/daily_race_simulator.py`)

   - Simulates progressive daily race card releases
   - Provides status monitoring and reporting
   - Enables testing of daily processing workflows

3. **Shell Scripts**
   - `scripts/generate_weekly_race_cards.sh` - Quick weekly generation
   - `scripts/demo_weekly_race_cards.sh` - Complete demonstration

## Realistic Racing Patterns

### Daily Course Scheduling

The system follows authentic UK/Irish racing patterns:

**Monday**: Smaller venues, development races

- Brighton, Catterick, Leicester, Plumpton, Sedgefield
- Wolverhampton, Dundalk, Kempton Park, Lingfield Park

**Tuesday**: Mid-week competitive racing

- Chepstow, Doncaster, Fakenham, Newcastle, Warwick
- Chelmsford City, Southwell, Bangor-on-Dee

**Wednesday**: Quality mid-week meetings

- Ascot, Bath, Exeter, Huntingdon, Market Rasen
- Redcar, Yarmouth, Navan, Cork

**Thursday**: Premium mid-week racing

- Goodwood, Hamilton, Ludlow, Newbury, Sandown Park
- Taunton, Windsor, Punchestown, Leopardstown

**Friday**: High-quality weekend preparation

- Haydock Park, Newmarket, Pontefract, Ripon, Salisbury
- Uttoxeter, York, The Curragh, Galway

**Saturday**: Premium weekend racing (Group races)

- Aintree, Cheltenham, Epsom Downs, Kempton Park
- Newmarket, Sandown Park, York, Leopardstown, Fairyhouse

**Sunday**: Weekend conclusion, specialist meetings

- Fontwell Park, Hexham, Worcester, Wetherby
- Carlisle, Naas, Clonmel, Downpatrick

### Race Type Distribution

- **Monday-Tuesday**: Handicaps, Maidens, Claiming, Selling
- **Wednesday-Thursday**: Handicaps, Listed, Maidens, Novice
- **Friday**: Handicaps, Listed, Group 2, Group 3
- **Saturday**: Group 1, Group 2, Listed, Handicaps (premium day)
- **Sunday**: Handicaps, Maidens, Novice, Hunter Chase

### Prize Money Ranges

- **Monday**: £2,000 - £15,000
- **Tuesday**: £2,500 - £18,000
- **Wednesday**: £3,000 - £25,000
- **Thursday**: £4,000 - £35,000
- **Friday**: £5,000 - £50,000
- **Saturday**: £10,000 - £100,000 (premium races)
- **Sunday**: £3,000 - £20,000

## Database Schema

### Weekly Management Tables

```sql
-- Weekly race cards tracking
CREATE TABLE weekly_race_schedule (
    schedule_id SERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL,
    day_number INTEGER NOT NULL CHECK (day_number BETWEEN 1 AND 7),
    day_name VARCHAR(20) NOT NULL,
    race_date DATE NOT NULL,
    total_races INTEGER DEFAULT 0,
    races_released BOOLEAN DEFAULT FALSE,
    release_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily race release tracking
CREATE TABLE daily_race_releases (
    release_id SERIAL PRIMARY KEY,
    race_date DATE NOT NULL,
    course VARCHAR(100) NOT NULL,
    total_races INTEGER NOT NULL,
    release_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    release_status VARCHAR(20) DEFAULT 'pending'
);

-- Week management
CREATE TABLE week_management (
    week_id SERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL UNIQUE,
    week_end_date DATE NOT NULL,
    total_race_cards INTEGER DEFAULT 0,
    cards_generated INTEGER DEFAULT 0,
    cards_released INTEGER DEFAULT 0,
    week_status VARCHAR(20) DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Examples

### 1. Generate Complete Week Instantly

```bash
# Generate full week starting today
./scripts/generate_weekly_race_cards.sh

# Generate specific week with 7 days
./scripts/generate_weekly_race_cards.sh 2025-08-05 7
```

### 2. Progressive Daily Release Simulation

```bash
# Simulate 7-day progressive release
python3 tests/daily_race_simulator.py \
    --week-start 2025-08-05 \
    --simulate-days 7 \
    --delay 3

# Release just today's races
python3 tests/daily_race_simulator.py --release-today

# Check current status
python3 tests/daily_race_simulator.py --status
```

### 3. Status Monitoring

```python
from tests.daily_race_simulator import DailyRaceSimulator
from datetime import date

simulator = DailyRaceSimulator()

# Get week status
status = simulator.get_current_status(date(2025, 8, 5))
print(f"Week progress: {status['progress']['percentage_complete']:.1f}%")

# Get released races summary
summary = simulator.get_released_races_summary()
print(f"Total races this week: {summary['week_totals']['total_races']}")
```

## Integration with Testing Framework

### Test Environment Setup

The system integrates with the existing test Docker environment:

```bash
# Database: postgresql://postgres:password@localhost:5434/horse_racing_test_db
# Uses docker-compose.test.yml configuration
# Completely separate from development environment
```

### Testing Scenarios

1. **Progressive Data Testing**

   - Test AI systems with gradually increasing data
   - Validate daily processing workflows
   - Monitor performance with growing datasets

2. **Realistic Workflow Testing**

   - Test race card processing as they become available
   - Validate time-based operations
   - Test notification systems with realistic timing

3. **Volume Testing**
   - 300+ races per week (realistic UK/Irish volume)
   - 3,000+ individual race participants
   - Full range of race types and conditions

## Performance Characteristics

### Generation Speed

- **Complete Week**: ~15-30 seconds for 300+ races
- **Daily Release**: ~3-5 seconds per day
- **Database Insertion**: Batched for optimal performance

### Data Volume per Week

- **Races**: 250-350 races
- **Participants**: 2,500-4,000 individual entries
- **Courses**: 15-25 different venues
- **Race Types**: All major UK/Irish categories

## Real-World Testing Applications

### 1. Monte Carlo + Fast Results Testing

```bash
# Generate week of race cards
./scripts/generate_weekly_race_cards.sh

# Test daily processing with Monte Carlo
python3 tests/daily_race_simulator.py --release-today
python3 demos/complete_monte_carlo_demo.py  # Process today's releases
```

### 2. NTFY Notification Testing

```bash
# Progressive release with notifications
python3 tests/daily_race_simulator.py --simulate-days 7 --delay 10
# Each day's release can trigger NTFY notifications
```

### 3. Performance Benchmarking

```bash
# Generate large dataset
python3 tests/weekly_race_cards_generator.py --days 7

# Benchmark database queries
python3 -c "
from src.database.database_manager import DatabaseManager
import time
db = DatabaseManager()
start = time.time()
races = db.get_races(limit=1000)
print(f'Query time: {time.time() - start:.3f}s for {len(races)} races')
"
```

## Configuration Options

### Environment Variables

```bash
export DATABASE_URL="postgresql://postgres:password@localhost:5434/horse_racing_test_db"
export RACE_WEEK_START="2025-08-05"  # Optional: default week start
export SIMULATION_DELAY="3"          # Delay between days in simulation
```

### Customization Parameters

1. **Course Selection**: Modify `courses_by_day` in WeeklyRaceCardsGenerator
2. **Race Types**: Adjust `race_types_by_day` for different race distributions
3. **Prize Ranges**: Customize `prize_ranges` for different economic periods
4. **Participant Names**: Update name lists for different regions/eras

## Integration Points

### 1. Database Manager Integration

```python
from src.database.database_manager import DatabaseManager

# After generating weekly data
db = DatabaseManager(database_url="postgresql://postgres:password@localhost:5434/horse_racing_test_db")
summary = db.get_database_summary()
print(f"Total races: {summary['tables']['races_cards']}")
```

### 2. Monte Carlo Integration

```python
# Daily release triggers Monte Carlo analysis
from tests.daily_race_simulator import DailyRaceSimulator
from demos.complete_monte_carlo_demo import main as run_monte_carlo

simulator = DailyRaceSimulator()
release_result = simulator.release_today_races()

if release_result['status'] == 'success':
    run_monte_carlo()  # Process newly released races
```

### 3. NTFY Integration

```python
# Notification on each daily release
def notify_daily_release(release_result):
    if release_result['status'] == 'success':
        message = f"📅 {release_result['races_released']} races released for {release_result['date']}"
        # Send NTFY notification
        # Integration with existing NTFY system
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   ```bash
   # Check if test database is running
   docker-compose -f docker-compose.test.yml ps
   # Start if needed
   docker-compose -f docker-compose.test.yml up -d postgres
   ```

2. **No Races Found for Date**

   ```bash
   # Check if week was set up
   python3 tests/daily_race_simulator.py --status
   # Generate week if needed
   python3 tests/weekly_race_cards_generator.py --days 7
   ```

3. **Performance Issues**
   ```bash
   # Check database statistics
   python3 -c "
   from src.database.database_manager import DatabaseManager
   db = DatabaseManager()
   summary = db.get_database_summary()
   print(summary)
   "
   ```

## Future Enhancements

### Planned Features

1. **Historical Data Generation**: Multi-year historical racing data
2. **Weather Integration**: Weather-dependent race modifications
3. **International Expansion**: French, US, Australian racing patterns
4. **Real-Time Sync**: Integration with live racing data feeds
5. **Advanced Analytics**: Performance trending and prediction validation

### Extension Points

1. **Custom Race Types**: Add new race categories and formats
2. **Regional Variations**: Different countries' racing patterns
3. **Seasonal Adjustments**: Jump season vs. Flat season variations
4. **Economic Modeling**: Prize money inflation and economic factors

## Summary

The Weekly Race Cards system provides:

✅ **Realistic Testing Environment**: Authentic UK/Irish racing patterns
✅ **Progressive Data Flow**: Day-by-day race card releases
✅ **Comprehensive Volume**: 300+ races per week with full participant data
✅ **Integration Ready**: Seamless integration with existing AI systems
✅ **Performance Optimized**: Fast generation and efficient database operations
✅ **Monitoring Capable**: Full status tracking and progress reporting

This system enables comprehensive testing of all Horse Racing AI components with realistic data volumes and timing patterns, ensuring the system performs optimally in production environments.
