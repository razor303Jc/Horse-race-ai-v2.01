"""
Horse Base Web Scraping Service

This module handles web scraping interactions with Horse Base,
including authentication, session management, and data extraction.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import re

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class HorseBaseCredentials(BaseModel):
    """Horse Base login credentials."""
    username: str
    password: str
    base_url: str = "https://www.horseracebase.com"


class HorseBaseRaceData(BaseModel):
    """Race data scraped from Horse Base."""
    race_id: str
    track_name: str
    race_date: datetime
    race_number: int
    race_time: Optional[str]
    distance: Optional[str]
    surface: Optional[str]
    conditions: Optional[str]
    horses: List[Dict[str, Any]] = Field(default_factory=list)


class HorseBaseWebScraper:
    """
    Web scraper for Horse Base racing data.
    
    Handles login, session management, and data extraction
    from Horse Base web pages.
    """
    
    def __init__(self):
        self.base_url = settings.horse_race_base_url
        self.username = settings.horse_race_base_username
        self.password = settings.horse_race_base_password
        self.session: Optional[httpx.AsyncClient] = None
        self.logged_in = False
        
        # Rate limiting
        self.last_request_time = datetime.now()
        self.min_request_interval = timedelta(seconds=2)  # Be respectful - 2 seconds between requests
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Initialize HTTP session and login."""
        if self.session is None:
            timeout = httpx.Timeout(30.0, connect=10.0)
            self.session = httpx.AsyncClient(
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
                follow_redirects=True
            )
            
        await self._login()
    
    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None
            self.logged_in = False
    
    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        now = datetime.now()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = (self.min_request_interval - time_since_last).total_seconds()
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.now()
    
    async def _login(self) -> None:
        """
        Login to Horse Base using form-based authentication.
        """
        if not self.username or not self.password:
            raise ValueError("Horse Base username and password not configured")
        
        try:
            # Get the login page to extract any hidden form fields
            await self._rate_limit()
            login_url = urljoin(self.base_url, "/")
            response = await self.session.get(login_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the login form - looking for username/password fields
            login_form = None
            for form in soup.find_all('form'):
                if (form.find('input', {'name': re.compile(r'(user|login|email)', re.I)}) and 
                    form.find('input', {'type': 'password'})):
                    login_form = form
                    break
            
            if not login_form:
                # Try direct login if no form found on main page
                login_url = urljoin(self.base_url, "/login.php")  # Common login endpoint
                await self._rate_limit()
                response = await self.session.get(login_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                login_form = soup.find('form')
            
            if not login_form:
                raise ValueError("Could not find login form on Horse Base")
            
            # Extract form action and method
            form_action = login_form.get('action', login_url)
            if not form_action.startswith('http'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = login_form.get('method', 'POST').upper()
            
            # Build form data
            form_data = {}
            
            # Add all hidden input fields
            for hidden_input in login_form.find_all('input', {'type': 'hidden'}):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Find username and password field names
            username_field = login_form.find('input', {'name': re.compile(r'(user|login|email)', re.I)})
            password_field = login_form.find('input', {'type': 'password'})
            
            if not username_field or not password_field:
                # Try common field names
                form_data.update({
                    'username': self.username,
                    'password': self.password,
                    'login': self.username,
                    'user': self.username,
                    'pass': self.password,
                })
            else:
                form_data[username_field.get('name')] = self.username
                form_data[password_field.get('name')] = self.password
            
            # Submit login form
            await self._rate_limit()
            if form_method == 'GET':
                response = await self.session.get(form_action, params=form_data)
            else:
                response = await self.session.post(form_action, data=form_data)
            
            response.raise_for_status()
            
            # Check if login was successful
            if self._check_login_success(response.text):
                self.logged_in = True
                logger.info("Successfully logged into Horse Base")
            else:
                raise ValueError("Login failed - check credentials")
                
        except Exception as e:
            logger.error(f"Horse Base login failed: {e}")
            raise
    
    def _check_login_success(self, html_content: str) -> bool:
        """
        Check if login was successful by looking for indicators in the response.
        """
        # Common indicators of successful login
        success_indicators = [
            "logout", "my account", "my hrb", "welcome", "dashboard",
            "my systems", "my horses", "my qualifiers"
        ]
        
        # Common indicators of failed login
        failure_indicators = [
            "invalid", "incorrect", "login failed", "error", "try again",
            "username or password", "authentication failed"
        ]
        
        html_lower = html_content.lower()
        
        # Check for failure indicators first
        for indicator in failure_indicators:
            if indicator in html_lower:
                return False
        
        # Check for success indicators
        for indicator in success_indicators:
            if indicator in html_lower:
                return True
        
        # If no clear indicators, check if we're redirected to a member area
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for member-only content
        member_content = soup.find_all(text=re.compile(r'(member|subscription|account|logout)', re.I))
        if member_content:
            return True
        
        # Default to false if uncertain
        return False
    
    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make authenticated HTTP request.
        """
        if not self.session:
            await self.connect()
        
        if not self.logged_in:
            await self._login()
        
        await self._rate_limit()
        
        try:
            response = await self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Check if session expired (redirected to login)
            if "login" in response.url.path.lower() and not self._check_login_success(response.text):
                logger.warning("Session expired, re-authenticating...")
                await self._login()
                # Retry the request
                await self._rate_limit()
                response = await self.session.request(method, url, **kwargs)
                response.raise_for_status()
            
            logger.debug(f"Horse Base request: {method} {url} -> {response.status_code}")
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Horse Base HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Horse Base request error: {e}")
            raise
    
    async def get_today_races(self) -> List[HorseBaseRaceData]:
        """
        Scrape today's race cards from Horse Base.
        """
        try:
            # Horse Base today's racing URL (common pattern)
            today_url = urljoin(self.base_url, "/horse-racing-today.php")
            response = await self._make_request("GET", today_url)
            
            return self._parse_race_cards(response.text)
            
        except Exception as e:
            logger.error(f"Failed to get today's races: {e}")
            return []
    
    async def get_races_by_date(self, race_date: datetime) -> List[HorseBaseRaceData]:
        """
        Scrape race cards for a specific date.
        """
        try:
            # Format date for Horse Base (they likely use a specific format)
            date_str = race_date.strftime("%Y-%m-%d")
            
            # Try different URL patterns
            date_urls = [
                f"/horse-racing-{date_str}.php",
                f"/racing-{date_str}.php",
                f"/results.php?date={date_str}",
                f"/cards.php?date={date_str}",
            ]
            
            for url_path in date_urls:
                try:
                    url = urljoin(self.base_url, url_path)
                    response = await self._make_request("GET", url)
                    races = self._parse_race_cards(response.text)
                    if races:
                        return races
                except Exception as e:
                    logger.debug(f"Failed to get races from {url}: {e}")
                    continue
            
            logger.warning(f"No races found for {date_str}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get races for {race_date}: {e}")
            return []
    
    def _parse_race_cards(self, html_content: str) -> List[HorseBaseRaceData]:
        """
        Parse race card data from HTML content.
        """
        races = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # This is a placeholder - we'll need to analyze the actual HTML structure
        # from Horse Base to implement proper parsing
        
        # Look for common race card patterns
        race_elements = soup.find_all(['div', 'table', 'tr'], class_=re.compile(r'race|card', re.I))
        
        for i, element in enumerate(race_elements[:10]):  # Limit to first 10 for testing
            try:
                # Extract basic race information
                race_text = element.get_text()
                
                race = HorseBaseRaceData(
                    race_id=f"hrb_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                    track_name="Unknown Track",
                    race_date=datetime.now(),
                    race_number=i+1,
                    race_time=None,
                    distance=None,
                    surface=None,
                    conditions=None,
                    horses=[]
                )
                
                races.append(race)
                
            except Exception as e:
                logger.debug(f"Failed to parse race element: {e}")
                continue
        
        logger.info(f"Parsed {len(races)} races from Horse Base")
        return races
    
    async def health_check(self) -> bool:
        """
        Check if Horse Base is accessible and credentials work.
        """
        try:
            if not self.session:
                await self.connect()
            
            # Try to access a simple page
            response = await self._make_request("GET", self.base_url)
            return self.logged_in and response.status_code == 200
            
        except Exception as e:
            logger.error(f"Horse Base health check failed: {e}")
            return False


# Global client instance
_horse_base_client: Optional[HorseBaseWebScraper] = None


async def get_horse_base_client() -> HorseBaseWebScraper:
    """
    Get or create the global Horse Base web scraper.
    """
    global _horse_base_client
    
    if _horse_base_client is None:
        _horse_base_client = HorseBaseWebScraper()
        await _horse_base_client.connect()
    
    return _horse_base_client


async def close_horse_base_client() -> None:
    """Close the global Horse Base client."""
    global _horse_base_client
    
    if _horse_base_client:
        await _horse_base_client.disconnect()
        _horse_base_client = None
