"""
Horse Base Structure Mapper

This tool makes minimal requests to Horse Base to understand their HTML structure
and page layouts, then saves examples for offline development.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from bs4 import BeautifulSoup
import httpx

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class HorseBaseStructureMapper:
    """
    Maps Horse Base website structure with minimal requests.
    
    This tool is designed to make just a few strategic requests to understand
    the site structure, then save examples for offline development.
    """
    
    def __init__(self):
        self.base_url = settings.horse_race_base_url
        self.username = settings.horse_race_base_username
        self.password = settings.horse_race_base_password
        self.session: Optional[httpx.AsyncClient] = None
        self.logged_in = False
        
        # Create output directory for structure samples
        self.output_dir = Path("./data/horse_base_structure")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    async def _login(self) -> None:
        """Login to Horse Base using form-based authentication."""
        if not self.username or not self.password:
            raise ValueError("Horse Base username and password not configured")
        
        try:
            print(f"🔄 Attempting login to {self.base_url}")
            
            # Get the main page to find login form
            response = await self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save the main page structure for analysis
            await self._save_page_structure("main_page", response.text, "Main login page")
            
            # Look for login form - Horse Base might use different patterns
            login_data = {
                'username': self.username,
                'password': self.password,
                'login': self.username,
                'user': self.username,
                'pass': self.password,
                'Login': 'Login',
                'submit': 'Login'
            }
            
            # Try different common login endpoints
            login_endpoints = [
                "/",
                "/login.php", 
                "/member.php",
                "/auth.php"
            ]
            
            for endpoint in login_endpoints:
                try:
                    login_url = f"{self.base_url.rstrip('/')}{endpoint}"
                    print(f"   Trying login at: {endpoint}")
                    
                    response = await self.session.post(login_url, data=login_data)
                    
                    if self._check_login_success(response.text):
                        self.logged_in = True
                        print(f"✅ Login successful via {endpoint}")
                        
                        # Save successful login page for analysis
                        await self._save_page_structure("post_login", response.text, f"Post-login page via {endpoint}")
                        return
                        
                except Exception as e:
                    print(f"   Login attempt failed at {endpoint}: {e}")
                    continue
            
            # If all login attempts failed, still mark as "logged in" for structure mapping
            # since we might be able to access some public areas
            print("⚠️  Login attempts completed - will map public structure")
            self.logged_in = True
                
        except Exception as e:
            logger.error(f"Horse Base login failed: {e}")
            # Continue anyway to map public structure
            self.logged_in = True
    
    def _check_login_success(self, html_content: str) -> bool:
        """Check if login was successful."""
        success_indicators = [
            "logout", "my account", "my hrb", "welcome", "dashboard",
            "my systems", "my horses", "my qualifiers", "member"
        ]
        
        failure_indicators = [
            "invalid", "incorrect", "login failed", "error", "try again"
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
        
        return False
    
    async def _save_page_structure(self, name: str, html_content: str, description: str):
        """Save HTML page structure and analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw HTML
        html_file = self.output_dir / f"{name}_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Parse and analyze structure
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            "timestamp": timestamp,
            "description": description,
            "url_patterns": self._extract_url_patterns(soup),
            "forms": self._analyze_forms(soup),
            "navigation": self._analyze_navigation(soup),
            "content_sections": self._analyze_content_sections(soup),
            "data_tables": self._analyze_data_tables(soup),
            "race_related_elements": self._find_race_elements(soup)
        }
        
        # Save analysis
        analysis_file = self.output_dir / f"{name}_{timestamp}_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"   📄 Saved: {html_file.name}")
        print(f"   📊 Analysis: {analysis_file.name}")
    
    def _extract_url_patterns(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract URL patterns from the page."""
        patterns = {
            "internal_links": [],
            "racing_related": [],
            "api_endpoints": [],
            "data_sources": []
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            patterns["internal_links"].append({
                "href": href,
                "text": text
            })
            
            # Look for racing-related URLs
            racing_keywords = ['race', 'racing', 'horse', 'jockey', 'trainer', 'result', 'card', 'form']
            if any(keyword in href.lower() or keyword in text for keyword in racing_keywords):
                patterns["racing_related"].append({
                    "href": href,
                    "text": text
                })
        
        return patterns
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze forms on the page."""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "inputs": []
            }
            
            for input_elem in form.find_all('input'):
                form_data["inputs"].append({
                    "name": input_elem.get('name', ''),
                    "type": input_elem.get('type', 'text'),
                    "value": input_elem.get('value', '')
                })
            
            forms.append(form_data)
        
        return forms
    
    def _analyze_navigation(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Analyze navigation structure."""
        nav_elements = {
            "main_nav": [],
            "breadcrumbs": [],
            "menus": []
        }
        
        # Look for navigation elements
        for nav in soup.find_all(['nav', 'ul', 'div'], class_=lambda x: x and ('nav' in x.lower() or 'menu' in x.lower())):
            nav_links = []
            for link in nav.find_all('a'):
                nav_links.append({
                    "text": link.get_text(strip=True),
                    "href": link.get('href', '')
                })
            
            if nav_links:
                nav_elements["main_nav"].extend(nav_links)
        
        return nav_elements
    
    def _analyze_content_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze main content sections."""
        sections = []
        
        # Look for main content areas
        content_selectors = [
            'main', 'article', '.content', '#content', '.main', '#main',
            '.race-card', '.results', '.form', '.data'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                sections.append({
                    "selector": selector,
                    "tag": elem.name,
                    "classes": elem.get('class', []),
                    "id": elem.get('id', ''),
                    "text_preview": elem.get_text()[:200] + "..." if len(elem.get_text()) > 200 else elem.get_text()
                })
        
        return sections
    
    def _analyze_data_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze data tables that might contain race information."""
        tables = []
        
        for table in soup.find_all('table'):
            table_data = {
                "classes": table.get('class', []),
                "id": table.get('id', ''),
                "headers": [],
                "row_count": 0
            }
            
            # Get headers
            for th in table.find_all('th'):
                table_data["headers"].append(th.get_text(strip=True))
            
            # Count rows
            table_data["row_count"] = len(table.find_all('tr'))
            
            # Look for racing-related content
            table_text = table.get_text().lower()
            racing_keywords = ['horse', 'jockey', 'trainer', 'odds', 'time', 'distance', 'race', 'position']
            table_data["likely_racing_data"] = any(keyword in table_text for keyword in racing_keywords)
            
            tables.append(table_data)
        
        return tables
    
    def _find_race_elements(self, soup: BeautifulSoup) -> Dict[str, List[Dict]]:
        """Find elements that likely contain race data."""
        race_elements = {
            "race_cards": [],
            "results": [],
            "horses": [],
            "odds": []
        }
        
        # Look for race-related classes and IDs
        race_selectors = [
            '[class*="race"]', '[id*="race"]',
            '[class*="horse"]', '[id*="horse"]',
            '[class*="result"]', '[id*="result"]',
            '[class*="odds"]', '[id*="odds"]',
            '[class*="card"]', '[id*="card"]'
        ]
        
        for selector in race_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    element_data = {
                        "tag": elem.name,
                        "classes": elem.get('class', []),
                        "id": elem.get('id', ''),
                        "selector": selector,
                        "text_preview": elem.get_text()[:100] + "..." if len(elem.get_text()) > 100 else elem.get_text()
                    }
                    
                    # Categorize based on content
                    text_lower = elem.get_text().lower()
                    if 'race' in text_lower and ('card' in text_lower or 'time' in text_lower):
                        race_elements["race_cards"].append(element_data)
                    elif 'result' in text_lower or 'winner' in text_lower:
                        race_elements["results"].append(element_data)
                    elif 'horse' in text_lower and ('name' in text_lower or 'form' in text_lower):
                        race_elements["horses"].append(element_data)
                    elif 'odds' in text_lower or '/' in elem.get_text():
                        race_elements["odds"].append(element_data)
                        
            except Exception as e:
                continue
        
        return race_elements
    
    async def map_key_pages(self) -> Dict[str, Any]:
        """Map key Horse Base pages with minimal requests."""
        print("🗺️  Mapping Horse Base structure...")
        
        key_pages = [
            ("/", "home_page", "Main homepage"),
            ("/horse-racing-today.php", "today_racing", "Today's racing page"),
            ("/horse-racing-research.php", "research", "Research tools page"),
            ("/horse-racing-information.php", "information", "Information page"),
            ("/shortcuts.php", "shortcuts", "Shortcuts page"),
        ]
        
        mapped_pages = {}
        
        for url_path, name, description in key_pages:
            try:
                print(f"🔄 Mapping: {description}")
                
                # Add delay to be respectful
                await asyncio.sleep(3)
                
                url = f"{self.base_url.rstrip('/')}{url_path}"
                response = await self.session.get(url)
                
                if response.status_code == 200:
                    await self._save_page_structure(name, response.text, description)
                    mapped_pages[name] = {
                        "url": url,
                        "status": "success",
                        "description": description
                    }
                    print(f"✅ Mapped: {description}")
                else:
                    print(f"⚠️  Could not access: {description} (status: {response.status_code})")
                    mapped_pages[name] = {
                        "url": url,
                        "status": f"error_{response.status_code}",
                        "description": description
                    }
                    
            except Exception as e:
                print(f"❌ Failed to map {description}: {e}")
                mapped_pages[name] = {
                    "url": url_path,
                    "status": "error",
                    "description": description,
                    "error": str(e)
                }
        
        # Save mapping summary
        summary_file = self.output_dir / f"mapping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(mapped_pages, f, indent=2, default=str)
        
        print(f"📋 Mapping summary saved: {summary_file.name}")
        return mapped_pages


async def map_horse_base_structure():
    """Main function to map Horse Base structure."""
    print("🏇 Horse Base Structure Mapping Tool")
    print("===================================")
    print("This tool makes minimal requests to understand Horse Base structure")
    print("for offline development with test data.\n")
    
    try:
        async with HorseBaseStructureMapper() as mapper:
            results = await mapper.map_key_pages()
            
            print("\n✅ Structure mapping completed!")
            print(f"📁 Output directory: {mapper.output_dir}")
            print("\n📋 Next Steps:")
            print("   1. Review the saved HTML files and analysis")
            print("   2. Create test data based on the structure")
            print("   3. Build parsers using the test data")
            print("   4. Minimize live requests during development")
            
            return results
            
    except Exception as e:
        print(f"❌ Structure mapping failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(map_horse_base_structure())
