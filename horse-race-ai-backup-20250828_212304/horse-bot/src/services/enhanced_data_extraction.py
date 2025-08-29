"""
Enhanced Free Data Extraction Service

Maximizes the value extracted from free Horse Race Base access
by implementing intelligent parsing and data aggregation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup, Tag
from ..core.config import get_settings
from .external_apis import HorseBaseWebScraper, HorseBaseRaceData

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class EnhancedHorseData:
    """Enhanced horse data extracted from free sources."""
    name: str
    number: Optional[int] = None
    jockey: Optional[str] = None
    trainer: Optional[str] = None
    weight: Optional[str] = None
    age: Optional[int] = None
    form: Optional[str] = None  # Last 5 runs: "12345"
    last_run_days: Optional[int] = None
    career_wins: Optional[int] = None
    career_runs: Optional[int] = None
    recent_form_rating: Optional[float] = None  # 0-10 scale
    distance_suitability: Optional[float] = None  # 0-10 scale
    track_suitability: Optional[float] = None  # 0-10 scale


@dataclass
class EnhancedRaceData:
    """Enhanced race data with improved analysis."""
    race_id: str
    track_name: str
    race_date: datetime
    race_number: int
    race_time: Optional[str]
    distance: Optional[str]
    distance_meters: Optional[int]
    surface: Optional[str]  # Turf, All-Weather, etc.
    conditions: Optional[str]  # Good, Soft, Heavy, etc.
    race_class: Optional[str]  # Class 1-6, Listed, Group 1-3
    prize_money: Optional[str]
    field_size: int
    horses: List[EnhancedHorseData]
    
    # Enhanced analytics
    competitive_rating: Optional[float] = None  # 0-10 how competitive
    pace_prediction: Optional[str] = None  # Fast, Steady, Slow
    key_contenders: List[str] = None  # Top 3-4 horses


class EnhancedDataExtractor:
    """
    Enhanced data extraction engine that maximizes value from free Horse Race Base access.
    """
    
    def __init__(self):
        self.scraper = HorseBaseWebScraper()
        
        # Pattern libraries for parsing
        self.weight_patterns = [
            r'(\d+)-(\d+)',  # 10-7 format
            r'(\d+)st\s*(\d+)lb',  # 10st 7lb format
            r'(\d+)lb'  # Just pounds
        ]
        
        self.form_patterns = [
            r'([0-9PUF\-]{1,8})',  # Numbers, P (pulled up), U (unseated), F (fell)
            r'(\d{1,5})',  # Just position numbers
        ]
        
        self.distance_conversions = {
            '5f': 1000, '6f': 1200, '7f': 1400, '1m': 1600,
            '1m1f': 1800, '1m2f': 2000, '1m3f': 2200, '1m4f': 2400,
            '1m5f': 2600, '1m6f': 2800, '2m': 3200, '2m4f': 4000
        }
        
    async def extract_enhanced_race_data(self, race_date: datetime) -> List[EnhancedRaceData]:
        """Extract enhanced race data for a specific date."""
        
        try:
            # Get basic race data from scraper
            basic_races = await self.scraper.get_races_by_date(race_date)
            enhanced_races = []
            
            for basic_race in basic_races:
                try:
                    enhanced_race = await self._enhance_race_data(basic_race)
                    if enhanced_race:
                        enhanced_races.append(enhanced_race)
                except Exception as e:
                    logger.error(f"Failed to enhance race {basic_race.race_id}: {e}")
                    continue
            
            logger.info(f"Enhanced {len(enhanced_races)} races for {race_date.date()}")
            return enhanced_races
            
        except Exception as e:
            logger.error(f"Failed to extract enhanced race data: {e}")
            return []
    
    async def _enhance_race_data(self, basic_race: HorseBaseRaceData) -> Optional[EnhancedRaceData]:
        """Enhance basic race data with additional parsing and analysis."""
        
        try:
            # Get detailed race page
            race_url = f"/race-card/{basic_race.race_id}"
            response = await self.scraper._make_request("GET", race_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Enhanced race information
            enhanced_race = EnhancedRaceData(
                race_id=basic_race.race_id,
                track_name=basic_race.track_name,
                race_date=basic_race.race_date,
                race_number=basic_race.race_number,
                race_time=basic_race.race_time,
                distance=basic_race.distance,
                distance_meters=self._parse_distance_meters(basic_race.distance),
                surface=basic_race.surface,
                conditions=basic_race.conditions,
                race_class=self._extract_race_class(soup),
                prize_money=self._extract_prize_money(soup),
                field_size=len(basic_race.horses),
                horses=[]
            )
            
            # Extract enhanced horse data
            horse_rows = self._find_horse_rows(soup)
            for i, row in enumerate(horse_rows):
                try:
                    horse_data = self._extract_enhanced_horse_data(row, i)
                    if horse_data:
                        enhanced_race.horses.append(horse_data)
                except Exception as e:
                    logger.debug(f"Failed to extract horse data from row {i}: {e}")
                    continue
            
            # Calculate race analytics
            enhanced_race.competitive_rating = self._calculate_competitive_rating(enhanced_race)
            enhanced_race.pace_prediction = self._predict_pace(enhanced_race)
            enhanced_race.key_contenders = self._identify_key_contenders(enhanced_race)
            
            return enhanced_race
            
        except Exception as e:
            logger.error(f"Failed to enhance race data: {e}")
            return None
    
    def _find_horse_rows(self, soup: BeautifulSoup) -> List[Tag]:
        """Find horse data rows in various HTML structures."""
        
        # Try multiple selectors for different page layouts
        selectors = [
            'tr.runner',
            'tr.horse-row',
            'div.runner',
            'div.horse-card',
            'table tbody tr',
            '.race-card tr',
            '.runners tr'
        ]
        
        for selector in selectors:
            rows = soup.select(selector)
            if rows and len(rows) > 1:  # Need more than just header
                return rows
        
        # Fallback: find by text patterns
        all_rows = soup.find_all('tr')
        horse_rows = []
        
        for row in all_rows:
            text = row.get_text().lower()
            if any(pattern in text for pattern in ['jockey', 'trainer', 'weight', 'form']):
                horse_rows.append(row)
        
        return horse_rows[:20]  # Limit to reasonable number
    
    def _extract_enhanced_horse_data(self, row: Tag, index: int) -> Optional[EnhancedHorseData]:
        """Extract detailed horse data from a table row or card."""
        
        try:
            text = row.get_text()
            cells = row.find_all(['td', 'div', 'span'])
            
            # Extract horse name (usually first or most prominent)
            horse_name = self._extract_horse_name(row, cells, text)
            if not horse_name:
                return None
            
            # Extract other data
            horse_data = EnhancedHorseData(
                name=horse_name,
                number=self._extract_horse_number(text, index),
                jockey=self._extract_jockey(text, cells),
                trainer=self._extract_trainer(text, cells),
                weight=self._extract_weight(text),
                age=self._extract_age(text),
                form=self._extract_form(text),
                last_run_days=self._calculate_last_run_days(text),
                career_wins=self._extract_career_wins(text),
                career_runs=self._extract_career_runs(text)
            )
            
            # Calculate derived metrics
            horse_data.recent_form_rating = self._calculate_form_rating(horse_data.form)
            horse_data.distance_suitability = self._assess_distance_suitability(horse_data)
            horse_data.track_suitability = self._assess_track_suitability(horse_data)
            
            return horse_data
            
        except Exception as e:
            logger.debug(f"Failed to extract horse data: {e}")
            return None
    
    def _extract_horse_name(self, row: Tag, cells: List[Tag], text: str) -> Optional[str]:
        """Extract horse name using multiple strategies."""
        
        # Strategy 1: Look for links (horse names often linked)
        links = row.find_all('a')
        for link in links:
            href = link.get('href', '')
            if 'horse' in href.lower() or 'runner' in href.lower():
                name = link.get_text().strip()
                if name and len(name) > 2:
                    return name
        
        # Strategy 2: Look for bold text
        bold_elements = row.find_all(['b', 'strong'])
        for bold in bold_elements:
            name = bold.get_text().strip()
            if name and len(name) > 2 and not name.isdigit():
                return name
        
        # Strategy 3: Look for specific classes
        name_elements = row.find_all(class_=re.compile(r'horse|runner|name', re.I))
        for element in name_elements:
            name = element.get_text().strip()
            if name and len(name) > 2:
                return name
        
        # Strategy 4: Extract from text using patterns
        lines = text.strip().split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if line and len(line) > 2 and not line.isdigit():
                # Skip common non-name patterns
                if not any(skip in line.lower() for skip in ['jockey', 'trainer', 'weight', 'form', 'age']):
                    return line
        
        return None
    
    def _extract_horse_number(self, text: str, index: int) -> Optional[int]:
        """Extract horse number from text."""
        
        # Look for standalone numbers at the beginning
        number_match = re.search(r'^(\d{1,2})\b', text.strip())
        if number_match:
            return int(number_match.group(1))
        
        # Look for numbers in parentheses
        paren_match = re.search(r'\((\d{1,2})\)', text)
        if paren_match:
            return int(paren_match.group(1))
        
        # Fallback: use index + 1
        return index + 1
    
    def _extract_jockey(self, text: str, cells: List[Tag]) -> Optional[str]:
        """Extract jockey name."""
        
        # Look for "J:" or "Jockey:" prefix
        jockey_match = re.search(r'(?:J:|Jockey:)\s*([A-Za-z\s\.]+)', text, re.I)
        if jockey_match:
            return jockey_match.group(1).strip()
        
        # Look for cells with jockey-related classes
        for cell in cells:
            class_str = ' '.join(cell.get('class', []))
            if 'jockey' in class_str.lower():
                name = cell.get_text().strip()
                if name and len(name) > 2:
                    return name
        
        # Pattern matching for common jockey name formats
        name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        names = re.findall(name_pattern, text)
        
        # Return first reasonable name (not a common racing term)
        for name in names:
            if not any(term in name.lower() for term in ['handicap', 'maiden', 'stakes', 'hurdle']):
                return name
        
        return None
    
    def _extract_trainer(self, text: str, cells: List[Tag]) -> Optional[str]:
        """Extract trainer name."""
        
        # Look for "T:" or "Trainer:" prefix
        trainer_match = re.search(r'(?:T:|Trainer:)\s*([A-Za-z\s\.]+)', text, re.I)
        if trainer_match:
            return trainer_match.group(1).strip()
        
        # Look for cells with trainer-related classes
        for cell in cells:
            class_str = ' '.join(cell.get('class', []))
            if 'trainer' in class_str.lower():
                name = cell.get_text().strip()
                if name and len(name) > 2:
                    return name
        
        return None
    
    def _extract_weight(self, text: str) -> Optional[str]:
        """Extract weight carried."""
        
        for pattern in self.weight_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_age(self, text: str) -> Optional[int]:
        """Extract horse age."""
        
        age_match = re.search(r'\b([2-9]|1[0-5])yo\b', text)
        if age_match:
            return int(age_match.group(1))
        
        # Look for standalone age numbers
        age_match = re.search(r'\bage[:\s]*([2-9])\b', text, re.I)
        if age_match:
            return int(age_match.group(1))
        
        return None
    
    def _extract_form(self, text: str) -> Optional[str]:
        """Extract recent form string."""
        
        for pattern in self.form_patterns:
            match = re.search(pattern, text)
            if match:
                form = match.group(1)
                # Validate form string
                if len(form) >= 3 and len(form) <= 8:
                    return form
        
        return None
    
    def _calculate_last_run_days(self, text: str) -> Optional[int]:
        """Calculate days since last run."""
        
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # DD/MM/YY
            r'(\d{1,2})-(\d{1,2})-(\d{2,4})',  # DD-MM-YY
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',  # DD MMM
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    # Simple calculation (would need proper date parsing)
                    return 7  # Placeholder
                except:
                    continue
        
        # Look for "days ago" pattern
        days_match = re.search(r'(\d+)\s*days?\s*ago', text, re.I)
        if days_match:
            return int(days_match.group(1))
        
        return None
    
    def _extract_career_wins(self, text: str) -> Optional[int]:
        """Extract career wins."""
        
        wins_match = re.search(r'(\d+)\s*wins?', text, re.I)
        if wins_match:
            return int(wins_match.group(1))
        
        # Look for win-run ratio like "3-15"
        ratio_match = re.search(r'(\d+)-(\d+)', text)
        if ratio_match:
            return int(ratio_match.group(1))
        
        return None
    
    def _extract_career_runs(self, text: str) -> Optional[int]:
        """Extract total career runs."""
        
        runs_match = re.search(r'(\d+)\s*runs?', text, re.I)
        if runs_match:
            return int(runs_match.group(1))
        
        # Look for win-run ratio like "3-15"
        ratio_match = re.search(r'(\d+)-(\d+)', text)
        if ratio_match:
            return int(ratio_match.group(2))
        
        return None
    
    def _parse_distance_meters(self, distance: Optional[str]) -> Optional[int]:
        """Convert distance string to meters."""
        
        if not distance:
            return None
        
        distance = distance.lower().strip()
        
        # Direct lookup
        if distance in self.distance_conversions:
            return self.distance_conversions[distance]
        
        # Parse complex distances
        if 'm' in distance:
            # Extract miles and furlongs
            match = re.search(r'(\d+)m(?:\s*(\d+)f)?', distance)
            if match:
                miles = int(match.group(1))
                furlongs = int(match.group(2)) if match.group(2) else 0
                return (miles * 1600) + (furlongs * 200)
        
        elif 'f' in distance:
            # Extract furlongs only
            match = re.search(r'(\d+)f', distance)
            if match:
                furlongs = int(match.group(1))
                return furlongs * 200
        
        return None
    
    def _extract_race_class(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract race class/grade."""
        
        class_patterns = [
            r'(Class\s+[1-6])',
            r'(Group\s+[1-3])',
            r'(Grade\s+[1-3])',
            r'(Listed)',
            r'(Handicap)',
            r'(Maiden)',
            r'(Novice)',
            r'(Stakes)',
        ]
        
        text = soup.get_text()
        
        for pattern in class_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_prize_money(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract prize money."""
        
        text = soup.get_text()
        
        money_patterns = [
            r'£([\d,]+)',
            r'\$([\d,]+)',
            r'([\d,]+)\s*pounds?',
        ]
        
        for pattern in money_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0)
        
        return None
    
    def _calculate_form_rating(self, form: Optional[str]) -> Optional[float]:
        """Calculate a form rating from 0-10 based on recent results."""
        
        if not form:
            return None
        
        # Simple rating based on recent positions
        total_score = 0
        count = 0
        
        for char in form[-5:]:  # Last 5 runs
            if char.isdigit():
                position = int(char)
                if position == 1:
                    total_score += 10
                elif position == 2:
                    total_score += 8
                elif position == 3:
                    total_score += 6
                elif position <= 5:
                    total_score += 4
                else:
                    total_score += 1
                count += 1
            elif char in 'PUF':  # Poor performance
                total_score += 0
                count += 1
        
        if count == 0:
            return None
        
        return round(total_score / count, 1)
    
    def _assess_distance_suitability(self, horse: EnhancedHorseData) -> Optional[float]:
        """Assess how suitable the distance is for this horse (0-10)."""
        
        # This would require historical distance performance data
        # For now, return a default rating
        return 5.0
    
    def _assess_track_suitability(self, horse: EnhancedHorseData) -> Optional[float]:
        """Assess how suitable the track is for this horse (0-10)."""
        
        # This would require historical track performance data
        # For now, return a default rating
        return 5.0
    
    def _calculate_competitive_rating(self, race: EnhancedRaceData) -> Optional[float]:
        """Calculate how competitive the race is (0-10)."""
        
        if not race.horses:
            return None
        
        # Factor in field size, form ratings, and class
        base_rating = min(race.field_size / 2, 5)  # More horses = more competitive
        
        form_ratings = [h.recent_form_rating for h in race.horses if h.recent_form_rating]
        if form_ratings:
            avg_form = sum(form_ratings) / len(form_ratings)
            base_rating += avg_form * 0.5
        
        return min(round(base_rating, 1), 10.0)
    
    def _predict_pace(self, race: EnhancedRaceData) -> Optional[str]:
        """Predict race pace based on distance and field."""
        
        if not race.distance_meters:
            return None
        
        # Simple heuristics
        if race.distance_meters < 1400:  # Sprint
            return "Fast"
        elif race.distance_meters > 2400:  # Stay
            return "Steady"
        else:
            return "Moderate"
    
    def _identify_key_contenders(self, race: EnhancedRaceData) -> List[str]:
        """Identify the top 3-4 contenders based on available data."""
        
        if not race.horses:
            return []
        
        # Score horses based on available data
        scored_horses = []
        
        for horse in race.horses:
            score = 0
            
            # Form rating contribution
            if horse.recent_form_rating:
                score += horse.recent_form_rating
            
            # Recent activity bonus
            if horse.last_run_days and horse.last_run_days < 30:
                score += 2
            
            # Experience bonus
            if horse.career_runs and horse.career_runs > 5:
                score += 1
            
            scored_horses.append((horse.name, score))
        
        # Sort by score and return top contenders
        scored_horses.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in scored_horses[:4]]


# Global enhanced extractor instance
_enhanced_extractor: Optional[EnhancedDataExtractor] = None


async def get_enhanced_extractor() -> EnhancedDataExtractor:
    """Get or create the global enhanced data extractor."""
    global _enhanced_extractor
    
    if _enhanced_extractor is None:
        _enhanced_extractor = EnhancedDataExtractor()
        await _enhanced_extractor.scraper.connect()
    
    return _enhanced_extractor


async def get_enhanced_today_data() -> List[EnhancedRaceData]:
    """Get enhanced race data for today."""
    extractor = await get_enhanced_extractor()
    return await extractor.extract_enhanced_race_data(datetime.now())


async def get_enhanced_date_data(date: datetime) -> List[EnhancedRaceData]:
    """Get enhanced race data for a specific date."""
    extractor = await get_enhanced_extractor()
    return await extractor.extract_enhanced_race_data(date)
