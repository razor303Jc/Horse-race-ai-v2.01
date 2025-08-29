
# CRITICAL CSV DATA QUALITY ANALYSIS REPORT
## Analysis Date: 2025-08-28 07:12:44

## 🚨 EXECUTIVE SUMMARY
- **Total Files Analyzed**: 15
- **Files with Critical Issues**: 14
- **Files with Warnings**: 15
- **Clean Files**: 1

## 🔴 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION


### 1. racecard_details.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/racecards_2025-08-27/racecard_details/racecard_details.csv`
**Size**: 73,525 bytes | **Rows**: 265 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'odds': Contains special characters

### 2. races.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/racecards_2025-08-27/races/races.csv`
**Size**: 4,312 bytes | **Rows**: 28 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'Race_name': Contains special characters

### 3. horses.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/racecards_2025-08-27/horses/horses.csv`
**Size**: 64,580 bytes | **Rows**: 265 | **Columns**: 39

**CRITICAL ISSUES:**
- ❌ Column 'owner': Contains special characters
- ❌ Column 'sire': Contains special characters
- ❌ Column 'dam': Contains special characters
- ❌ Column 'dam_sire': Contains special characters

### 4. racecard_details.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_card_processing/2025-08-23/racecard_details/racecard_details.csv`
**Size**: 113,393 bytes | **Rows**: 418 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'trainer': Contains special characters
- ❌ Column 'odds': Contains special characters
- ❌ Column 'Timeform_comments': Contains special characters

### 5. races.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_card_processing/2025-08-23/races/races.csv`
**Size**: 7,309 bytes | **Rows**: 47 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'Race_name': Contains special characters

### 6. horses.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_card_processing/2025-08-23/horses/horses.csv`
**Size**: 101,216 bytes | **Rows**: 418 | **Columns**: 39

**CRITICAL ISSUES:**
- ❌ Column 'owner': Contains special characters
- ❌ Column 'sire': Contains special characters
- ❌ Column 'dam': Contains special characters
- ❌ Column 'dam_sire': Contains special characters

### 7. racecard_details.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/cards_data/2025-08-27/racecard_details/racecard_details.csv`
**Size**: 73,525 bytes | **Rows**: 265 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'odds': Contains special characters

### 8. races.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/cards_data/2025-08-27/races/races.csv`
**Size**: 4,312 bytes | **Rows**: 28 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'Race_name': Contains special characters

### 9. horses.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/cards_data/2025-08-27/horses/horses.csv`
**Size**: 64,580 bytes | **Rows**: 265 | **Columns**: 39

**CRITICAL ISSUES:**
- ❌ Column 'owner': Contains special characters
- ❌ Column 'sire': Contains special characters
- ❌ Column 'dam': Contains special characters
- ❌ Column 'dam_sire': Contains special characters

### 10. racecard_details.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/racecard_details/racecard_details.csv`
**Size**: 73,525 bytes | **Rows**: 265 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'odds': Contains special characters

### 11. races.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/races/races.csv`
**Size**: 4,312 bytes | **Rows**: 28 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'Race_name': Contains special characters

### 12. horses.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_extract/horses/horses.csv`
**Size**: 64,580 bytes | **Rows**: 265 | **Columns**: 39

**CRITICAL ISSUES:**
- ❌ Column 'owner': Contains special characters
- ❌ Column 'sire': Contains special characters
- ❌ Column 'dam': Contains special characters
- ❌ Column 'dam_sire': Contains special characters

### 13. racecard_details.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_card_processing/racecard_details/racecard_details.csv`
**Size**: 113,393 bytes | **Rows**: 418 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'trainer': Contains special characters
- ❌ Column 'odds': Contains special characters
- ❌ Column 'Timeform_comments': Contains special characters

### 14. races.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/temp_card_processing/races/races.csv`
**Size**: 7,309 bytes | **Rows**: 47 | **Columns**: 20

**CRITICAL ISSUES:**
- ❌ Column 'Race_name': Contains special characters


## ⚠️ WARNING ISSUES NEEDING ATTENTION


### 1. jockeys_stats.csv
**Path**: `/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/results_data/2025-08-27/jockeys_stats/jockeys_stats.csv`
**Rows**: 6,606 | **Columns**: 28

**WARNING ISSUES:**
- ⚠️ Column 'UptoDate': Contains dash characters


## 📊 DETAILED COLUMN ANALYSIS


### racecard_details.csv - Column Details
**Columns**: id, race_id, horse_number, Draw, Horse_ID, Country, Name, Age, weight_uk, weight, gears, Horse_rate, jockey_ID, jockey, trainer_ID, trainer, fav, odds, odds_decimal, Timeform_comments


**weight_uk**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 36
- Issues: Contains dash characters
- Sample Values: ['11-2', '11-2', '11-0', '10-9', '10-6']

**jockey**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 137
- Issues: Contains dash characters
- Sample Values: ['Mr E Cagney', 'Miss Remie Morgan', 'Mr Henry Callan', 'Miss Amber Jackson-Fennell', 'Miss Alice Tregoning']

**trainer**:
- Data Type: object
- Null Count: 1/265 (0.4%)
- Unique Values: 166
- Issues: Contains dash characters
- Sample Values: ['B R Johnson', "F O'Brien", 'R Eddery', 'N A Twiston-Davies', 'M P Tregoning']

**odds**:
- Data Type: object
- Null Count: 203/265 (76.6%)
- Unique Values: 29
- Issues: Contains special characters
- Sample Values: ['22/1', '11/1', '11/1', '11/1', '5/1']

**Timeform_comments**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 265
- Issues: Contains dash characters
- Sample Values: ['Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.', 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.', 'Won readily, improving on his turf debut when landing a handicap by 9l off 60 over 1m6f at Yarmouth last time. Effective over 14f on the all-weather. Progressive and could improve further for 2m.', 'Ran to form when fourth, beaten 6 1/4l, in a handicap at Kempton last time. Returning from a long layoff. Effective from 11f to 16f on the all-weather; has had issues.', 'Needed the run when beaten 7l in a handicap over 1m6f at Ffos Las last time. Generally consistent over 12-14f and acts on the all-weather.']

### races.csv - Column Details
**Columns**: Race_ID, race_number, race_time, course_id, Course, Race_type, Date, Race_name, Class, Years, Distance, Surface, Prize, Runners_racecard, Runners, Draw, EW_racecard, EW, Places_EW_racecard, Places_EW


**race_time**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 28
- Issues: Numeric-looking but not parseable: 16:25
- Sample Values: ['16:25', '16:55', '17:25', '17:55', '18:25']

**Date**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**Race_name**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 25
- Issues: Contains special characters
- Sample Values: ['Irish Stallion Farms EBF Median Auction Maiden', 'Gibneys Malahide Handicap', 'Gibneys Malahide Handicap', "Peadar Kearney's Pub Handicap", 'Irish EBF Auction Series Maiden']

**Surface**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 4
- Issues: Contains dash characters
- Sample Values: ['Yielding', 'Yielding', 'Yielding', 'Yielding', 'Yielding']

### horses.csv - Column Details
**Columns**: id, uptodate, state, race_id_last_race, date_last_race, name, country, age, color, owner, sire, dam, dam_sire, sex, Total_races, Wins, Percentage_wins, placed, Percentage_placed, Flat_AW_races, Flat_AW_wins, Flat_AW_rate, Flat_AW_placed, Flat_AW_placed_rate, Flat_Turf_races, Flat_Turf_wins, Flat_Turf_rate, Flat_Turf_placed, Flat_Turf_placed_rate, Chase_races, Chase_wins, Chase_rate, Chase_placed, Chase_placed_rate, Hurdle_races, Hurdle_wins, Hurdle_rate, Hurdle_placed, Hurdle_placed_rate


**uptodate**:
- Data Type: object
- Null Count: 17/265 (6.4%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25']

**date_last_race**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**owner**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 255
- Issues: Contains special characters
- Sample Values: ["Mr Timothy O'Gram & Partner", 'S Mullins Racing Club', 'Cragg Wood Racing', 'Ambrose Turnbull & John Cruces', 'Miss L A Perratt']

**sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 134
- Issues: Contains special characters
- Sample Values: ["Poet's Voice (UK)", 'Cityscape (UK)', 'Bungle Inthejungle (UK)', 'Dandy Man (IRE)', 'Dansili (UK)']

**dam**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 262
- Issues: Contains special characters
- Sample Values: ['Dudley Queen (IRE)', 'Moonlight Applause (UK)', 'Ramamara (IRE)', 'Deira (USA)', 'Trois Lunes (FR)']

**dam_sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 155
- Issues: Contains special characters
- Sample Values: ['Excellent Art (UK)', 'Royal Applause (UK)', 'Trans Island (UK)', 'Green Desert (USA)', 'Manduro (GER)']

### racecard_details.csv - Column Details
**Columns**: id, race_id, horse_number, Draw, Horse_ID, Country, Name, Age, weight_uk, weight, gears, Horse_rate, jockey_ID, jockey, trainer_ID, trainer, fav, odds, odds_decimal, Timeform_comments


**weight_uk**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 49
- Issues: Contains dash characters
- Sample Values: ['10-1', '10-0', '9-12', '9-9', '9-6']

**jockey**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 208
- Issues: Contains dash characters
- Sample Values: ['L Morris', 'Saffie Osborne', 'Elizabeth Gale', 'Callum Hutchinson', 'Finley Marsh']

**trainer**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 203
- Issues: Contains special characters
- Sample Values: ['Ollie Sangster', 'Ian Williams', 'B J Llewellyn', 'N P Mulholland', 'Harry Charlton']

**odds**:
- Data Type: object
- Null Count: 291/418 (69.6%)
- Unique Values: 41
- Issues: Contains special characters
- Sample Values: ['9/1', '16/1', '5/1', '6/5', '85/40']

**Timeform_comments**:
- Data Type: object
- Null Count: 6/418 (1.4%)
- Unique Values: 412
- Issues: Contains special characters
- Sample Values: ['Improved for quicker ground with an easy victory when landing a handicap by 7l off a mark of 74 over 2m1f at Pontefract last time. Significant jockey booking. Steadily progressive as the trip increases and has more to come as a stayer.', 'Scored by a head off 69 at Haydock in May. Ran to form when fourth, beaten 8 1/2l off the same mark last time. Significant jockey booking. A consistent stayer who goes well on a sound surface.', 'Below form in first-time cheekpieces when comfortably held in a handicap over 1m6f here last time. Generally out of form and struggling of late, though now back below her last winning mark.', 'Travelled well and improved down in grade with a positive ride when scoring by 9l off 97 over 2m7f at Worcester on his penultimate start. A veteran who needs a sound surface. Back to form over hurdles latest and could transfer that back to the flat.', 'Improved up in trip under a positive ride when landing a handicap by 2l off 63 over 1m6f at Salisbury last time. Trainer in form. Progressing as the trip increases, quick ground suits, and he has more to come as a stayer.']

### races.csv - Column Details
**Columns**: Race_ID, race_number, race_time, course_id, Course, Race_type, Date, Race_name, Class, Years, Distance, Surface, Prize, Runners_racecard, Runners, Draw, EW_racecard, EW, Places_EW_racecard, Places_EW


**race_time**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 47
- Issues: Numeric-looking but not parseable: 14:10
- Sample Values: ['14:10', '14:45', '15:20', '15:55', '16:30']

**Date**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22']

**Race_name**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 47
- Issues: Contains special characters
- Sample Values: ['Ascona Ladies Fuelled By Fashion Handicap', 'Ascona Ladies In Lace EBF Restricted Novice Stakes', 'Ascona Ladies Chic Fashion Handicap', 'Ascona Ladies Fashion And Style Handicap', 'Ascona Fabulous Ladies Classified Stakes']

**Surface**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 3
- Issues: Contains dash characters
- Sample Values: ['Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places']

### horses.csv - Column Details
**Columns**: id, uptodate, state, race_id_last_race, date_last_race, name, country, age, color, owner, sire, dam, dam_sire, sex, Total_races, Wins, Percentage_wins, placed, Percentage_placed, Flat_AW_races, Flat_AW_wins, Flat_AW_rate, Flat_AW_placed, Flat_AW_placed_rate, Flat_Turf_races, Flat_Turf_wins, Flat_Turf_rate, Flat_Turf_placed, Flat_Turf_placed_rate, Chase_races, Chase_wins, Chase_rate, Chase_placed, Chase_placed_rate, Hurdle_races, Hurdle_wins, Hurdle_rate, Hurdle_placed, Hurdle_placed_rate


**uptodate**:
- Data Type: object
- Null Count: 27/418 (6.5%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-21', '2025-08-21', '2025-08-21', '2025-08-21', '2025-08-21']

**date_last_race**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22']

**owner**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 377
- Issues: Contains special characters
- Sample Values: ['John Patrick Ryan & Miss Gillian Ryan', 'T T Racing', 'Shirley Symonds & Fred Camis', 'Amphitheatre Racing Limited', 'F Harty']

**sire**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 192
- Issues: Contains special characters
- Sample Values: ['Kutub (IRE)', 'Equiano (FR)', 'Requinto (IRE)', 'Harbour Watch (IRE)', 'Famous Name (UK)']

**dam**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 416
- Issues: Contains special characters
- Sample Values: ['Astrid (IRE)', 'Spring Clean (FR)', 'Rancho Star (IRE)', 'Holy Nola (USA)', 'Ginger Genie (IRE)']

**dam_sire**:
- Data Type: object
- Null Count: 2/418 (0.5%)
- Unique Values: 225
- Issues: Contains special characters
- Sample Values: ['Rhoman Rule (USA)', 'Danehill (USA)', 'Soviet Star (USA)', 'Silver Deputy (CAN)', 'Wizard King (UK)']

### racecard_details.csv - Column Details
**Columns**: id, race_id, horse_number, Draw, Horse_ID, Country, Name, Age, weight_uk, weight, gears, Horse_rate, jockey_ID, jockey, trainer_ID, trainer, fav, odds, odds_decimal, Timeform_comments


**weight_uk**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 36
- Issues: Contains dash characters
- Sample Values: ['11-2', '11-2', '11-0', '10-9', '10-6']

**jockey**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 137
- Issues: Contains dash characters
- Sample Values: ['Mr E Cagney', 'Miss Remie Morgan', 'Mr Henry Callan', 'Miss Amber Jackson-Fennell', 'Miss Alice Tregoning']

**trainer**:
- Data Type: object
- Null Count: 1/265 (0.4%)
- Unique Values: 166
- Issues: Contains dash characters
- Sample Values: ['B R Johnson', "F O'Brien", 'R Eddery', 'N A Twiston-Davies', 'M P Tregoning']

**odds**:
- Data Type: object
- Null Count: 203/265 (76.6%)
- Unique Values: 29
- Issues: Contains special characters
- Sample Values: ['22/1', '11/1', '11/1', '11/1', '5/1']

**Timeform_comments**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 265
- Issues: Contains dash characters
- Sample Values: ['Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.', 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.', 'Won readily, improving on his turf debut when landing a handicap by 9l off 60 over 1m6f at Yarmouth last time. Effective over 14f on the all-weather. Progressive and could improve further for 2m.', 'Ran to form when fourth, beaten 6 1/4l, in a handicap at Kempton last time. Returning from a long layoff. Effective from 11f to 16f on the all-weather; has had issues.', 'Needed the run when beaten 7l in a handicap over 1m6f at Ffos Las last time. Generally consistent over 12-14f and acts on the all-weather.']

### races.csv - Column Details
**Columns**: Race_ID, race_number, race_time, course_id, Course, Race_type, Date, Race_name, Class, Years, Distance, Surface, Prize, Runners_racecard, Runners, Draw, EW_racecard, EW, Places_EW_racecard, Places_EW


**race_time**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 28
- Issues: Numeric-looking but not parseable: 16:25
- Sample Values: ['16:25', '16:55', '17:25', '17:55', '18:25']

**Date**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**Race_name**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 25
- Issues: Contains special characters
- Sample Values: ['Irish Stallion Farms EBF Median Auction Maiden', 'Gibneys Malahide Handicap', 'Gibneys Malahide Handicap', "Peadar Kearney's Pub Handicap", 'Irish EBF Auction Series Maiden']

**Surface**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 4
- Issues: Contains dash characters
- Sample Values: ['Yielding', 'Yielding', 'Yielding', 'Yielding', 'Yielding']

### horses.csv - Column Details
**Columns**: id, uptodate, state, race_id_last_race, date_last_race, name, country, age, color, owner, sire, dam, dam_sire, sex, Total_races, Wins, Percentage_wins, placed, Percentage_placed, Flat_AW_races, Flat_AW_wins, Flat_AW_rate, Flat_AW_placed, Flat_AW_placed_rate, Flat_Turf_races, Flat_Turf_wins, Flat_Turf_rate, Flat_Turf_placed, Flat_Turf_placed_rate, Chase_races, Chase_wins, Chase_rate, Chase_placed, Chase_placed_rate, Hurdle_races, Hurdle_wins, Hurdle_rate, Hurdle_placed, Hurdle_placed_rate


**uptodate**:
- Data Type: object
- Null Count: 17/265 (6.4%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25']

**date_last_race**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**owner**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 255
- Issues: Contains special characters
- Sample Values: ["Mr Timothy O'Gram & Partner", 'S Mullins Racing Club', 'Cragg Wood Racing', 'Ambrose Turnbull & John Cruces', 'Miss L A Perratt']

**sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 134
- Issues: Contains special characters
- Sample Values: ["Poet's Voice (UK)", 'Cityscape (UK)', 'Bungle Inthejungle (UK)', 'Dandy Man (IRE)', 'Dansili (UK)']

**dam**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 262
- Issues: Contains special characters
- Sample Values: ['Dudley Queen (IRE)', 'Moonlight Applause (UK)', 'Ramamara (IRE)', 'Deira (USA)', 'Trois Lunes (FR)']

**dam_sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 155
- Issues: Contains special characters
- Sample Values: ['Excellent Art (UK)', 'Royal Applause (UK)', 'Trans Island (UK)', 'Green Desert (USA)', 'Manduro (GER)']

### racecard_details.csv - Column Details
**Columns**: id, race_id, horse_number, Draw, Horse_ID, Country, Name, Age, weight_uk, weight, gears, Horse_rate, jockey_ID, jockey, trainer_ID, trainer, fav, odds, odds_decimal, Timeform_comments


**weight_uk**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 36
- Issues: Contains dash characters
- Sample Values: ['11-2', '11-2', '11-0', '10-9', '10-6']

**jockey**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 137
- Issues: Contains dash characters
- Sample Values: ['Mr E Cagney', 'Miss Remie Morgan', 'Mr Henry Callan', 'Miss Amber Jackson-Fennell', 'Miss Alice Tregoning']

**trainer**:
- Data Type: object
- Null Count: 1/265 (0.4%)
- Unique Values: 166
- Issues: Contains dash characters
- Sample Values: ['B R Johnson', "F O'Brien", 'R Eddery', 'N A Twiston-Davies', 'M P Tregoning']

**odds**:
- Data Type: object
- Null Count: 203/265 (76.6%)
- Unique Values: 29
- Issues: Contains special characters
- Sample Values: ['22/1', '11/1', '11/1', '11/1', '5/1']

**Timeform_comments**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 265
- Issues: Contains dash characters
- Sample Values: ['Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.', 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.', 'Won readily, improving on his turf debut when landing a handicap by 9l off 60 over 1m6f at Yarmouth last time. Effective over 14f on the all-weather. Progressive and could improve further for 2m.', 'Ran to form when fourth, beaten 6 1/4l, in a handicap at Kempton last time. Returning from a long layoff. Effective from 11f to 16f on the all-weather; has had issues.', 'Needed the run when beaten 7l in a handicap over 1m6f at Ffos Las last time. Generally consistent over 12-14f and acts on the all-weather.']

### races.csv - Column Details
**Columns**: Race_ID, race_number, race_time, course_id, Course, Race_type, Date, Race_name, Class, Years, Distance, Surface, Prize, Runners_racecard, Runners, Draw, EW_racecard, EW, Places_EW_racecard, Places_EW


**race_time**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 28
- Issues: Numeric-looking but not parseable: 16:25
- Sample Values: ['16:25', '16:55', '17:25', '17:55', '18:25']

**Date**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**Race_name**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 25
- Issues: Contains special characters
- Sample Values: ['Irish Stallion Farms EBF Median Auction Maiden', 'Gibneys Malahide Handicap', 'Gibneys Malahide Handicap', "Peadar Kearney's Pub Handicap", 'Irish EBF Auction Series Maiden']

**Surface**:
- Data Type: object
- Null Count: 0/28 (0.0%)
- Unique Values: 4
- Issues: Contains dash characters
- Sample Values: ['Yielding', 'Yielding', 'Yielding', 'Yielding', 'Yielding']

### horses.csv - Column Details
**Columns**: id, uptodate, state, race_id_last_race, date_last_race, name, country, age, color, owner, sire, dam, dam_sire, sex, Total_races, Wins, Percentage_wins, placed, Percentage_placed, Flat_AW_races, Flat_AW_wins, Flat_AW_rate, Flat_AW_placed, Flat_AW_placed_rate, Flat_Turf_races, Flat_Turf_wins, Flat_Turf_rate, Flat_Turf_placed, Flat_Turf_placed_rate, Chase_races, Chase_wins, Chase_rate, Chase_placed, Chase_placed_rate, Hurdle_races, Hurdle_wins, Hurdle_rate, Hurdle_placed, Hurdle_placed_rate


**uptodate**:
- Data Type: object
- Null Count: 17/265 (6.4%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25']

**date_last_race**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26', '2025-08-26']

**owner**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 255
- Issues: Contains special characters
- Sample Values: ["Mr Timothy O'Gram & Partner", 'S Mullins Racing Club', 'Cragg Wood Racing', 'Ambrose Turnbull & John Cruces', 'Miss L A Perratt']

**sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 134
- Issues: Contains special characters
- Sample Values: ["Poet's Voice (UK)", 'Cityscape (UK)', 'Bungle Inthejungle (UK)', 'Dandy Man (IRE)', 'Dansili (UK)']

**dam**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 262
- Issues: Contains special characters
- Sample Values: ['Dudley Queen (IRE)', 'Moonlight Applause (UK)', 'Ramamara (IRE)', 'Deira (USA)', 'Trois Lunes (FR)']

**dam_sire**:
- Data Type: object
- Null Count: 0/265 (0.0%)
- Unique Values: 155
- Issues: Contains special characters
- Sample Values: ['Excellent Art (UK)', 'Royal Applause (UK)', 'Trans Island (UK)', 'Green Desert (USA)', 'Manduro (GER)']

### racecard_details.csv - Column Details
**Columns**: id, race_id, horse_number, Draw, Horse_ID, Country, Name, Age, weight_uk, weight, gears, Horse_rate, jockey_ID, jockey, trainer_ID, trainer, fav, odds, odds_decimal, Timeform_comments


**weight_uk**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 49
- Issues: Contains dash characters
- Sample Values: ['10-1', '10-0', '9-12', '9-9', '9-6']

**jockey**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 208
- Issues: Contains dash characters
- Sample Values: ['L Morris', 'Saffie Osborne', 'Elizabeth Gale', 'Callum Hutchinson', 'Finley Marsh']

**trainer**:
- Data Type: object
- Null Count: 0/418 (0.0%)
- Unique Values: 203
- Issues: Contains special characters
- Sample Values: ['Ollie Sangster', 'Ian Williams', 'B J Llewellyn', 'N P Mulholland', 'Harry Charlton']

**odds**:
- Data Type: object
- Null Count: 291/418 (69.6%)
- Unique Values: 41
- Issues: Contains special characters
- Sample Values: ['9/1', '16/1', '5/1', '6/5', '85/40']

**Timeform_comments**:
- Data Type: object
- Null Count: 6/418 (1.4%)
- Unique Values: 412
- Issues: Contains special characters
- Sample Values: ['Improved for quicker ground with an easy victory when landing a handicap by 7l off a mark of 74 over 2m1f at Pontefract last time. Significant jockey booking. Steadily progressive as the trip increases and has more to come as a stayer.', 'Scored by a head off 69 at Haydock in May. Ran to form when fourth, beaten 8 1/2l off the same mark last time. Significant jockey booking. A consistent stayer who goes well on a sound surface.', 'Below form in first-time cheekpieces when comfortably held in a handicap over 1m6f here last time. Generally out of form and struggling of late, though now back below her last winning mark.', 'Travelled well and improved down in grade with a positive ride when scoring by 9l off 97 over 2m7f at Worcester on his penultimate start. A veteran who needs a sound surface. Back to form over hurdles latest and could transfer that back to the flat.', 'Improved up in trip under a positive ride when landing a handicap by 2l off 63 over 1m6f at Salisbury last time. Trainer in form. Progressing as the trip increases, quick ground suits, and he has more to come as a stayer.']

### races.csv - Column Details
**Columns**: Race_ID, race_number, race_time, course_id, Course, Race_type, Date, Race_name, Class, Years, Distance, Surface, Prize, Runners_racecard, Runners, Draw, EW_racecard, EW, Places_EW_racecard, Places_EW


**race_time**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 47
- Issues: Numeric-looking but not parseable: 14:10
- Sample Values: ['14:10', '14:45', '15:20', '15:55', '16:30']

**Date**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 1
- Issues: Contains dash characters
- Sample Values: ['2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22']

**Race_name**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 47
- Issues: Contains special characters
- Sample Values: ['Ascona Ladies Fuelled By Fashion Handicap', 'Ascona Ladies In Lace EBF Restricted Novice Stakes', 'Ascona Ladies Chic Fashion Handicap', 'Ascona Ladies Fashion And Style Handicap', 'Ascona Fabulous Ladies Classified Stakes']

**Surface**:
- Data Type: object
- Null Count: 0/47 (0.0%)
- Unique Values: 3
- Issues: Contains dash characters
- Sample Values: ['Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places', 'Good-good to firm in places']


## 🔍 SAMPLE DATA FROM PROBLEMATIC FILES


### racecard_details.csv - Sample Rows

**Row 1**: {'id': 300034, 'race_id': 183488, 'horse_number': 1, 'Draw': 8, 'Horse_ID': 113372, 'Country': 'USA', 'Name': 'Moel Arthur', 'Age': 7, 'weight_uk': '11-2', 'weight': 70.75, 'gears': 't', 'Horse_rate': 70.0, 'jockey_ID': 6284.0, 'jockey': 'Mr E Cagney', 'trainer_ID': 235.0, 'trainer': 'B R Johnson', 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.'}

**Row 2**: {'id': 300035, 'race_id': 183488, 'horse_number': 2, 'Draw': 7, 'Horse_ID': 132833, 'Country': 'FR', 'Name': 'Sun Dancer Girl', 'Age': 4, 'weight_uk': '11-2', 'weight': 70.75, 'gears': nan, 'Horse_rate': 70.0, 'jockey_ID': 6553.0, 'jockey': 'Miss Remie Morgan', 'trainer_ID': 1184.0, 'trainer': "F O'Brien", 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.'}

### races.csv - Sample Rows

**Row 1**: {'Race_ID': 183508, 'race_number': 1, 'race_time': '16:25', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Irish Stallion Farms EBF Median Auction Maiden', 'Class': 'No Class', 'Years': '3YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 9000, 'Runners_racecard': 17, 'Runners': 17, 'Draw': 'Low', 'EW_racecard': 5, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

**Row 2**: {'Race_ID': 183509, 'race_number': 2, 'race_time': '16:55', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Gibneys Malahide Handicap', 'Class': 'No Class', 'Years': '4YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 6000, 'Runners_racecard': 15, 'Runners': 15, 'Draw': 'Low', 'EW_racecard': 4, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

### horses.csv - Sample Rows

**Row 1**: {'id': 72797, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183496, 'date_last_race': '2025-08-26', 'name': 'Poets Dawn', 'country': 'GB', 'age': 10, 'color': 'chestnut', 'owner': "Mr Timothy O'Gram & Partner", 'sire': "Poet's Voice (UK)", 'dam': 'Dudley Queen (IRE)', 'dam_sire': 'Excellent Art (UK)', 'sex': 'gelding', 'Total_races': 113.0, 'Wins': 11.0, 'Percentage_wins': 9.73, 'placed': 45.0, 'Percentage_placed': 39.82, 'Flat_AW_races': 4.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 1.0, 'Flat_AW_placed_rate': 25.0, 'Flat_Turf_races': 109.0, 'Flat_Turf_wins': 11.0, 'Flat_Turf_rate': 10.09, 'Flat_Turf_placed': 44.0, 'Flat_Turf_placed_rate': 40.37, 'Chase_races': 0.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 0.0, 'Chase_placed_rate': 0.0, 'Hurdle_races': 0.0, 'Hurdle_wins': 0.0, 'Hurdle_rate': 0.0, 'Hurdle_placed': 0.0, 'Hurdle_placed_rate': 0.0}

**Row 2**: {'id': 81052, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183488, 'date_last_race': '2025-08-26', 'name': 'Wilderness', 'country': 'GB', 'age': 10, 'color': 'bay', 'owner': 'S Mullins Racing Club', 'sire': 'Cityscape (UK)', 'dam': 'Moonlight Applause (UK)', 'dam_sire': 'Royal Applause (UK)', 'sex': 'mare', 'Total_races': 60.0, 'Wins': 6.0, 'Percentage_wins': 10.0, 'placed': 17.0, 'Percentage_placed': 28.33, 'Flat_AW_races': 8.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 4.0, 'Flat_AW_placed_rate': 50.0, 'Flat_Turf_races': 33.0, 'Flat_Turf_wins': 5.0, 'Flat_Turf_rate': 15.15, 'Flat_Turf_placed': 9.0, 'Flat_Turf_placed_rate': 27.27, 'Chase_races': 4.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 1.0, 'Chase_placed_rate': 25.0, 'Hurdle_races': 15.0, 'Hurdle_wins': 1.0, 'Hurdle_rate': 6.67, 'Hurdle_placed': 3.0, 'Hurdle_placed_rate': 20.0}

### racecard_details.csv - Sample Rows

**Row 1**: {'id': 298390, 'race_id': 183316, 'horse_number': 1, 'Draw': 6.0, 'Horse_ID': 145096, 'Country': 'IRE', 'Name': 'Kentucky River', 'Age': 3, 'weight_uk': '10-1', 'weight': 63.95, 'gears': 'p', 'Horse_rate': 80.0, 'jockey_ID': 22, 'jockey': 'L Morris', 'trainer_ID': 3867, 'trainer': 'Ollie Sangster', 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Improved for quicker ground with an easy victory when landing a handicap by 7l off a mark of 74 over 2m1f at Pontefract last time. Significant jockey booking. Steadily progressive as the trip increases and has more to come as a stayer.'}

**Row 2**: {'id': 298391, 'race_id': 183316, 'horse_number': 2, 'Draw': 3.0, 'Horse_ID': 133838, 'Country': 'IRE', 'Name': 'Simiyann', 'Age': 5, 'weight_uk': '10-0', 'weight': 63.5, 'gears': 'p', 'Horse_rate': 68.0, 'jockey_ID': 5191, 'jockey': 'Saffie Osborne', 'trainer_ID': 45, 'trainer': 'Ian Williams', 'fav': nan, 'odds': '9/1', 'odds_decimal': 10.0, 'Timeform_comments': 'Scored by a head off 69 at Haydock in May. Ran to form when fourth, beaten 8 1/2l off the same mark last time. Significant jockey booking. A consistent stayer who goes well on a sound surface.'}

### races.csv - Sample Rows

**Row 1**: {'Race_ID': 183316, 'race_number': 1, 'race_time': '14:10', 'course_id': 26, 'Course': 'Ffos-Las', 'Race_type': 'Flat Turf', 'Date': '2025-08-22', 'Race_name': 'Ascona Ladies Fuelled By Fashion Handicap', 'Class': 'Class 5', 'Years': '3YO plus', 'Distance': '2m', 'Surface': 'Good-good to firm in places', 'Prize': 4187, 'Runners_racecard': 5, 'Runners': 5, 'Draw': nan, 'EW_racecard': 4, 'EW': 0, 'Places_EW_racecard': 2, 'Places_EW': 0}

**Row 2**: {'Race_ID': 183317, 'race_number': 2, 'race_time': '14:45', 'course_id': 26, 'Course': 'Ffos-Las', 'Race_type': 'Flat Turf', 'Date': '2025-08-22', 'Race_name': 'Ascona Ladies In Lace EBF Restricted Novice Stakes', 'Class': 'Class 5', 'Years': '2YO only', 'Distance': '7f 80y', 'Surface': 'Good-good to firm in places', 'Prize': 3672, 'Runners_racecard': 4, 'Runners': 4, 'Draw': 'High', 'EW_racecard': 1, 'EW': 0, 'Places_EW_racecard': 1, 'Places_EW': 0}

### horses.csv - Sample Rows

**Row 1**: {'id': 57825, 'uptodate': '2025-08-21', 'state': 'Active', 'race_id_last_race': 183353, 'date_last_race': '2025-08-22', 'name': 'Father Jed', 'country': 'IRE', 'age': 14, 'color': 'bay', 'owner': 'John Patrick Ryan & Miss Gillian Ryan', 'sire': 'Kutub (IRE)', 'dam': 'Astrid (IRE)', 'dam_sire': 'Rhoman Rule (USA)', 'sex': 'gelding', 'Total_races': 93.0, 'Wins': 9.0, 'Percentage_wins': 9.68, 'placed': 21.0, 'Percentage_placed': 22.58, 'Flat_AW_races': 0.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 0.0, 'Flat_AW_placed_rate': 0.0, 'Flat_Turf_races': 0.0, 'Flat_Turf_wins': 0.0, 'Flat_Turf_rate': 0.0, 'Flat_Turf_placed': 0.0, 'Flat_Turf_placed_rate': 0.0, 'Chase_races': 47.0, 'Chase_wins': 2.0, 'Chase_rate': 4.26, 'Chase_placed': 14.0, 'Chase_placed_rate': 29.79, 'Hurdle_races': 46.0, 'Hurdle_wins': 7.0, 'Hurdle_rate': 15.22, 'Hurdle_placed': 7.0, 'Hurdle_placed_rate': 15.22}

**Row 2**: {'id': 68056, 'uptodate': '2025-08-21', 'state': 'Active', 'race_id_last_race': 183335, 'date_last_race': '2025-08-22', 'name': 'Equiano Springs', 'country': 'GB', 'age': 11, 'color': 'bay', 'owner': 'T T Racing', 'sire': 'Equiano (FR)', 'dam': 'Spring Clean (FR)', 'dam_sire': 'Danehill (USA)', 'sex': 'gelding', 'Total_races': 71.0, 'Wins': 13.0, 'Percentage_wins': 18.31, 'placed': 21.0, 'Percentage_placed': 29.58, 'Flat_AW_races': 14.0, 'Flat_AW_wins': 5.0, 'Flat_AW_rate': 35.71, 'Flat_AW_placed': 3.0, 'Flat_AW_placed_rate': 21.43, 'Flat_Turf_races': 57.0, 'Flat_Turf_wins': 8.0, 'Flat_Turf_rate': 14.04, 'Flat_Turf_placed': 18.0, 'Flat_Turf_placed_rate': 31.58, 'Chase_races': 0.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 0.0, 'Chase_placed_rate': 0.0, 'Hurdle_races': 0.0, 'Hurdle_wins': 0.0, 'Hurdle_rate': 0.0, 'Hurdle_placed': 0.0, 'Hurdle_placed_rate': 0.0}

### racecard_details.csv - Sample Rows

**Row 1**: {'id': 300034, 'race_id': 183488, 'horse_number': 1, 'Draw': 8, 'Horse_ID': 113372, 'Country': 'USA', 'Name': 'Moel Arthur', 'Age': 7, 'weight_uk': '11-2', 'weight': 70.75, 'gears': 't', 'Horse_rate': 70.0, 'jockey_ID': 6284.0, 'jockey': 'Mr E Cagney', 'trainer_ID': 235.0, 'trainer': 'B R Johnson', 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.'}

**Row 2**: {'id': 300035, 'race_id': 183488, 'horse_number': 2, 'Draw': 7, 'Horse_ID': 132833, 'Country': 'FR', 'Name': 'Sun Dancer Girl', 'Age': 4, 'weight_uk': '11-2', 'weight': 70.75, 'gears': nan, 'Horse_rate': 70.0, 'jockey_ID': 6553.0, 'jockey': 'Miss Remie Morgan', 'trainer_ID': 1184.0, 'trainer': "F O'Brien", 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.'}

### races.csv - Sample Rows

**Row 1**: {'Race_ID': 183508, 'race_number': 1, 'race_time': '16:25', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Irish Stallion Farms EBF Median Auction Maiden', 'Class': 'No Class', 'Years': '3YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 9000, 'Runners_racecard': 17, 'Runners': 17, 'Draw': 'Low', 'EW_racecard': 5, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

**Row 2**: {'Race_ID': 183509, 'race_number': 2, 'race_time': '16:55', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Gibneys Malahide Handicap', 'Class': 'No Class', 'Years': '4YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 6000, 'Runners_racecard': 15, 'Runners': 15, 'Draw': 'Low', 'EW_racecard': 4, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

### horses.csv - Sample Rows

**Row 1**: {'id': 72797, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183496, 'date_last_race': '2025-08-26', 'name': 'Poets Dawn', 'country': 'GB', 'age': 10, 'color': 'chestnut', 'owner': "Mr Timothy O'Gram & Partner", 'sire': "Poet's Voice (UK)", 'dam': 'Dudley Queen (IRE)', 'dam_sire': 'Excellent Art (UK)', 'sex': 'gelding', 'Total_races': 113.0, 'Wins': 11.0, 'Percentage_wins': 9.73, 'placed': 45.0, 'Percentage_placed': 39.82, 'Flat_AW_races': 4.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 1.0, 'Flat_AW_placed_rate': 25.0, 'Flat_Turf_races': 109.0, 'Flat_Turf_wins': 11.0, 'Flat_Turf_rate': 10.09, 'Flat_Turf_placed': 44.0, 'Flat_Turf_placed_rate': 40.37, 'Chase_races': 0.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 0.0, 'Chase_placed_rate': 0.0, 'Hurdle_races': 0.0, 'Hurdle_wins': 0.0, 'Hurdle_rate': 0.0, 'Hurdle_placed': 0.0, 'Hurdle_placed_rate': 0.0}

**Row 2**: {'id': 81052, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183488, 'date_last_race': '2025-08-26', 'name': 'Wilderness', 'country': 'GB', 'age': 10, 'color': 'bay', 'owner': 'S Mullins Racing Club', 'sire': 'Cityscape (UK)', 'dam': 'Moonlight Applause (UK)', 'dam_sire': 'Royal Applause (UK)', 'sex': 'mare', 'Total_races': 60.0, 'Wins': 6.0, 'Percentage_wins': 10.0, 'placed': 17.0, 'Percentage_placed': 28.33, 'Flat_AW_races': 8.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 4.0, 'Flat_AW_placed_rate': 50.0, 'Flat_Turf_races': 33.0, 'Flat_Turf_wins': 5.0, 'Flat_Turf_rate': 15.15, 'Flat_Turf_placed': 9.0, 'Flat_Turf_placed_rate': 27.27, 'Chase_races': 4.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 1.0, 'Chase_placed_rate': 25.0, 'Hurdle_races': 15.0, 'Hurdle_wins': 1.0, 'Hurdle_rate': 6.67, 'Hurdle_placed': 3.0, 'Hurdle_placed_rate': 20.0}

### racecard_details.csv - Sample Rows

**Row 1**: {'id': 300034, 'race_id': 183488, 'horse_number': 1, 'Draw': 8, 'Horse_ID': 113372, 'Country': 'USA', 'Name': 'Moel Arthur', 'Age': 7, 'weight_uk': '11-2', 'weight': 70.75, 'gears': 't', 'Horse_rate': 70.0, 'jockey_ID': 6284.0, 'jockey': 'Mr E Cagney', 'trainer_ID': 235.0, 'trainer': 'B R Johnson', 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Ran to form when beaten 2l off a mark of 70 over 1m6f at Sandown last time. This is a significant jockey booking. Suited by 2m, with the pace to be effective at 14f, and can win off this mark.'}

**Row 2**: {'id': 300035, 'race_id': 183488, 'horse_number': 2, 'Draw': 7, 'Horse_ID': 132833, 'Country': 'FR', 'Name': 'Sun Dancer Girl', 'Age': 4, 'weight_uk': '11-2', 'weight': 70.75, 'gears': nan, 'Horse_rate': 70.0, 'jockey_ID': 6553.0, 'jockey': 'Miss Remie Morgan', 'trainer_ID': 1184.0, 'trainer': "F O'Brien", 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Disappointing flat return when well beaten in a handicap at Kempton last time. Generally consistent at 2m on the all-weather for her old yard and could bounce back.'}

### races.csv - Sample Rows

**Row 1**: {'Race_ID': 183508, 'race_number': 1, 'race_time': '16:25', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Irish Stallion Farms EBF Median Auction Maiden', 'Class': 'No Class', 'Years': '3YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 9000, 'Runners_racecard': 17, 'Runners': 17, 'Draw': 'Low', 'EW_racecard': 5, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

**Row 2**: {'Race_ID': 183509, 'race_number': 2, 'race_time': '16:55', 'course_id': nan, 'Course': 'Bellewstown', 'Race_type': 'Flat Turf', 'Date': '2025-08-26', 'Race_name': 'Gibneys Malahide Handicap', 'Class': 'No Class', 'Years': '4YO plus', 'Distance': '7f 195y', 'Surface': 'Yielding', 'Prize': 6000, 'Runners_racecard': 15, 'Runners': 15, 'Draw': 'Low', 'EW_racecard': 4, 'EW': 0, 'Places_EW_racecard': 3, 'Places_EW': 0}

### horses.csv - Sample Rows

**Row 1**: {'id': 72797, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183496, 'date_last_race': '2025-08-26', 'name': 'Poets Dawn', 'country': 'GB', 'age': 10, 'color': 'chestnut', 'owner': "Mr Timothy O'Gram & Partner", 'sire': "Poet's Voice (UK)", 'dam': 'Dudley Queen (IRE)', 'dam_sire': 'Excellent Art (UK)', 'sex': 'gelding', 'Total_races': 113.0, 'Wins': 11.0, 'Percentage_wins': 9.73, 'placed': 45.0, 'Percentage_placed': 39.82, 'Flat_AW_races': 4.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 1.0, 'Flat_AW_placed_rate': 25.0, 'Flat_Turf_races': 109.0, 'Flat_Turf_wins': 11.0, 'Flat_Turf_rate': 10.09, 'Flat_Turf_placed': 44.0, 'Flat_Turf_placed_rate': 40.37, 'Chase_races': 0.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 0.0, 'Chase_placed_rate': 0.0, 'Hurdle_races': 0.0, 'Hurdle_wins': 0.0, 'Hurdle_rate': 0.0, 'Hurdle_placed': 0.0, 'Hurdle_placed_rate': 0.0}

**Row 2**: {'id': 81052, 'uptodate': '2025-08-25', 'state': 'Active', 'race_id_last_race': 183488, 'date_last_race': '2025-08-26', 'name': 'Wilderness', 'country': 'GB', 'age': 10, 'color': 'bay', 'owner': 'S Mullins Racing Club', 'sire': 'Cityscape (UK)', 'dam': 'Moonlight Applause (UK)', 'dam_sire': 'Royal Applause (UK)', 'sex': 'mare', 'Total_races': 60.0, 'Wins': 6.0, 'Percentage_wins': 10.0, 'placed': 17.0, 'Percentage_placed': 28.33, 'Flat_AW_races': 8.0, 'Flat_AW_wins': 0.0, 'Flat_AW_rate': 0.0, 'Flat_AW_placed': 4.0, 'Flat_AW_placed_rate': 50.0, 'Flat_Turf_races': 33.0, 'Flat_Turf_wins': 5.0, 'Flat_Turf_rate': 15.15, 'Flat_Turf_placed': 9.0, 'Flat_Turf_placed_rate': 27.27, 'Chase_races': 4.0, 'Chase_wins': 0.0, 'Chase_rate': 0.0, 'Chase_placed': 1.0, 'Chase_placed_rate': 25.0, 'Hurdle_races': 15.0, 'Hurdle_wins': 1.0, 'Hurdle_rate': 6.67, 'Hurdle_placed': 3.0, 'Hurdle_placed_rate': 20.0}

### racecard_details.csv - Sample Rows

**Row 1**: {'id': 298390, 'race_id': 183316, 'horse_number': 1, 'Draw': 6.0, 'Horse_ID': 145096, 'Country': 'IRE', 'Name': 'Kentucky River', 'Age': 3, 'weight_uk': '10-1', 'weight': 63.95, 'gears': 'p', 'Horse_rate': 80.0, 'jockey_ID': 22, 'jockey': 'L Morris', 'trainer_ID': 3867, 'trainer': 'Ollie Sangster', 'fav': nan, 'odds': nan, 'odds_decimal': nan, 'Timeform_comments': 'Improved for quicker ground with an easy victory when landing a handicap by 7l off a mark of 74 over 2m1f at Pontefract last time. Significant jockey booking. Steadily progressive as the trip increases and has more to come as a stayer.'}

**Row 2**: {'id': 298391, 'race_id': 183316, 'horse_number': 2, 'Draw': 3.0, 'Horse_ID': 133838, 'Country': 'IRE', 'Name': 'Simiyann', 'Age': 5, 'weight_uk': '10-0', 'weight': 63.5, 'gears': 'p', 'Horse_rate': 68.0, 'jockey_ID': 5191, 'jockey': 'Saffie Osborne', 'trainer_ID': 45, 'trainer': 'Ian Williams', 'fav': nan, 'odds': '9/1', 'odds_decimal': 10.0, 'Timeform_comments': 'Scored by a head off 69 at Haydock in May. Ran to form when fourth, beaten 8 1/2l off the same mark last time. Significant jockey booking. A consistent stayer who goes well on a sound surface.'}

### races.csv - Sample Rows

**Row 1**: {'Race_ID': 183316, 'race_number': 1, 'race_time': '14:10', 'course_id': 26, 'Course': 'Ffos-Las', 'Race_type': 'Flat Turf', 'Date': '2025-08-22', 'Race_name': 'Ascona Ladies Fuelled By Fashion Handicap', 'Class': 'Class 5', 'Years': '3YO plus', 'Distance': '2m', 'Surface': 'Good-good to firm in places', 'Prize': 4187, 'Runners_racecard': 5, 'Runners': 5, 'Draw': nan, 'EW_racecard': 4, 'EW': 0, 'Places_EW_racecard': 2, 'Places_EW': 0}

**Row 2**: {'Race_ID': 183317, 'race_number': 2, 'race_time': '14:45', 'course_id': 26, 'Course': 'Ffos-Las', 'Race_type': 'Flat Turf', 'Date': '2025-08-22', 'Race_name': 'Ascona Ladies In Lace EBF Restricted Novice Stakes', 'Class': 'Class 5', 'Years': '2YO only', 'Distance': '7f 80y', 'Surface': 'Good-good to firm in places', 'Prize': 3672, 'Runners_racecard': 4, 'Runners': 4, 'Draw': 'High', 'EW_racecard': 1, 'EW': 0, 'Places_EW_racecard': 1, 'Places_EW': 0}


## 💡 RECOMMENDATIONS FOR IMMEDIATE ACTION

### Critical Actions Required:
1. **Data Cleaning**: Remove or fix % symbols, special characters, and invalid formats
2. **Null Value Handling**: Address columns with excessive null values
3. **Header Standardization**: Fix unnamed columns and problematic column names
4. **Encoding Verification**: Ensure consistent UTF-8 encoding across all files
5. **Data Type Consistency**: Standardize data types within columns

### Specific Fixes Needed:
- Remove percentage symbols (%) from numeric data
- Standardize dash (-) usage in text fields
- Clean special characters from data fields
- Validate date formats and fix inconsistencies
- Handle null/blank values appropriately

### Prevention Measures:
- Implement data validation at source
- Add automated data quality checks to pipeline
- Standardize CSV export formats
- Regular data quality monitoring

## ⚡ IMPACT ASSESSMENT
**HIGH RISK**: Files with critical issues will cause pipeline failures
**MEDIUM RISK**: Warning issues may cause data inconsistencies
**ACTION REQUIRED**: Address critical issues before running any data processing

---
*This analysis is critical for system reliability. Address all critical issues immediately.*
