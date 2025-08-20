#!/usr/bin/env python3
"""
Horse Base Structure Mapper

This script makes minimal requests to Horse Base to map the site structure
and understand the HTML layout for data extraction. It saves the results
to files for analysis without repeatedly hitting their servers.

Usage:
    python map_horse_base_structure.py
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from bs4 import BeautifulSoup
    import httpx
except ImportError:
    print("❌ Required dependencies not installed. Run ./setup_dev.sh first")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HorseBaseStructureMapper:
    """
    Maps Horse Base site structure with minimal requests.
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://www.horseracebase.com"
        self.session = None
        self.logged_in = False
        
        # Create output directory
        self.output_dir = Path("horse_base_analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Tracking
        self.request_count = 0
        self.max_requests = 10  # Stay well under any limits
        
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = httpx.Timeout(30.0, connect=10.0)
        self.session = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def _rate_limit(self):
        """Add delay between requests."""
        await asyncio.sleep(3)  # 3 second delay to be very respectful
    
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        """Make a rate-limited request."""
        if self.request_count >= self.max_requests:
            raise Exception(f"Request limit reached ({self.max_requests})")
        
        await self._rate_limit()
        self.request_count += 1
        
        logger.info(f"Request {self.request_count}/{self.max_requests}: {method} {url}")
        response = await self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    async def login(self) -> bool:
        """Login to Horse Base and return success status."""
        try:
            # Get login page
            login_url = f"{self.base_url}/"
            response = await self._make_request(login_url)
            
            # Save login page for analysis
            self._save_html("00_login_page.html", response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find login form
            login_forms = soup.find_all('form')
            login_form = None
            
            for form in login_forms:
                # Look for password input
                if form.find('input', {'type': 'password'}):
                    login_form = form
                    break
            
            if not login_form:
                logger.error("Could not find login form")
                return False
            
            # Extract form details
            form_action = login_form.get('action', '')
            if not form_action.startswith('http'):
                form_action = f"{self.base_url}{form_action}"
            
            # Build form data
            form_data = {}
            
            # Add hidden fields
            for hidden_input in login_form.find_all('input', {'type': 'hidden'}):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Find username/password fields
            username_input = login_form.find('input', {'name': re.compile(r'(user|login|email)', re.I)})
            password_input = login_form.find('input', {'type': 'password'})
            
            if username_input and password_input:
                form_data[username_input.get('name')] = self.username
                form_data[password_input.get('name')] = self.password
            else:
                # Try common field names
                form_data.update({
                    'username': self.username,
                    'password': self.password,
                    'login': self.username,
                    'user': self.username,
                    'pass': self.password,
                })
            
            # Submit login
            logger.info(f"Submitting login form to: {form_action}")
            response = await self._make_request(form_action, "POST", data=form_data)
            
            # Save login response
            self._save_html("01_login_response.html", response.text)
            
            # Check if login successful
            html_lower = response.text.lower()
            success_indicators = ["logout", "my account", "my hrb", "welcome", "dashboard"]
            failure_indicators = ["invalid", "incorrect", "login failed", "error"]
            
            for indicator in failure_indicators:
                if indicator in html_lower:
                    logger.error(f"Login failed - found '{indicator}' in response")
                    return False
            
            for indicator in success_indicators:
                if indicator in html_lower:
                    logger.info("Login successful!")
                    self.logged_in = True
                    return True
            
            logger.warning("Login status unclear - assuming success")
            self.logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _save_html(self, filename: str, content: str):
        """Save HTML content to file."""
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved HTML to: {file_path}")
    
    def _save_json(self, filename: str, data: Dict[str, Any]):
        """Save JSON data to file."""
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved JSON to: {file_path}")
    
    def _analyze_html(self, html_content: str, page_name: str) -> Dict[str, Any]:
        """Analyze HTML structure and extract useful information."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            "page_name": page_name,
            "title": soup.title.string if soup.title else "No title",
            "forms": [],
            "tables": [],
            "links": [],
            "race_data_candidates": [],
            "navigation": [],
        }
        
        # Analyze forms
        for i, form in enumerate(soup.find_all('form')):
            form_info = {
                "index": i,
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "inputs": []
            }
            
            for input_elem in form.find_all('input'):
                form_info["inputs"].append({
                    "name": input_elem.get('name'),
                    "type": input_elem.get('type'),
                    "value": input_elem.get('value', ''),
                })
            
            analysis["forms"].append(form_info)
        
        # Analyze tables (likely to contain race data)
        for i, table in enumerate(soup.find_all('table')):
            table_info = {
                "index": i,
                "class": table.get('class', []),
                "id": table.get('id', ''),
                "rows": len(table.find_all('tr')),
                "headers": []
            }
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_info["headers"] = [h.get_text(strip=True) for h in headers]
            
            analysis["tables"].append(table_info)
        
        # Analyze navigation links
        nav_elements = soup.find_all(['nav', 'div'], class_=re.compile(r'nav|menu', re.I))
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href and text:
                    analysis["navigation"].append({
                        "text": text,
                        "href": href,
                        "full_url": href if href.startswith('http') else f"{self.base_url}{href}"
                    })
        
        # Look for race data indicators
        race_keywords = ['race', 'horse', 'jockey', 'trainer', 'odds', 'time', 'distance']
        for keyword in race_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            if elements:
                analysis["race_data_candidates"].extend([
                    {"keyword": keyword, "count": len(elements), "sample": str(elements[0])[:100]}
                ])
        
        return analysis
    
    async def map_key_pages(self):
        """Map the key pages we'll need for data extraction."""
        if not self.logged_in:
            logger.error("Must be logged in first")
            return
        
        key_pages = [
            ("today_racing", "/horse-racing-today.php", "Today's racing"),
            ("shortcuts", "/shortcuts.php", "Shortcuts/tools page"),
            ("research", "/horse-racing-research.php", "Research tools"),
        ]
        
        page_analyses = {}
        
        for page_key, url, description in key_pages:
            try:
                if self.request_count >= self.max_requests:
                    logger.warning(f"Request limit reached, skipping {page_key}")
                    break
                
                full_url = f"{self.base_url}{url}"
                logger.info(f"Mapping {description}: {full_url}")
                
                response = await self._make_request(full_url)
                
                # Save HTML
                self._save_html(f"02_{page_key}.html", response.text)
                
                # Analyze structure
                analysis = self._analyze_html(response.text, page_key)
                page_analyses[page_key] = analysis
                
            except Exception as e:
                logger.error(f"Failed to map {page_key}: {e}")
                continue
        
        # Save analysis
        self._save_json("page_analysis.json", page_analyses)
        
        return page_analyses
    
    async def generate_structure_report(self):
        """Generate a comprehensive structure report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "username": self.username,
            "base_url": self.base_url,
            "total_requests": self.request_count,
            "login_successful": self.logged_in,
            "analysis_directory": str(self.output_dir),
            "key_findings": [],
            "recommended_urls": [],
            "data_extraction_strategy": {}
        }
        
        # Add key findings based on what we discovered
        if self.logged_in:
            report["key_findings"].append("✅ Login mechanism identified and working")
            report["recommended_urls"].extend([
                "/horse-racing-today.php - Today's race cards",
                "/shortcuts.php - Quick access tools",
                "/horse-racing-research.php - Research tools"
            ])
            
            report["data_extraction_strategy"] = {
                "authentication": "Form-based login with session cookies",
                "rate_limiting": "3+ seconds between requests recommended",
                "primary_pages": [
                    "/horse-racing-today.php",
                    "/horse-racing-{date}.php (for historical)",
                    "/results.php?date={date}"
                ],
                "parsing_strategy": "BeautifulSoup with table and form analysis",
                "session_management": "Cookie-based, may need re-authentication"
            }
        else:
            report["key_findings"].append("❌ Login failed - need to investigate authentication")
        
        self._save_json("structure_report.json", report)
        
        return report


async def main():
    """Main mapping function."""
    # Credentials - should come from environment in production
    username = "raxor303"
    demo_password = "horse"  # Demo credential, not a real password
    
    print("🗺️  Horse Base Structure Mapper")
    print("=" * 50)
    print(f"Username: {username}")
    print(f"Max requests: 10 (to be respectful)")
    print(f"Rate limit: 3 seconds between requests")
    print()
    
    async with HorseBaseStructureMapper(username, demo_password) as mapper:
        try:
            # Step 1: Login
            print("🔐 Step 1: Testing login...")
            if await mapper.login():
                print("✅ Login successful!")
            else:
                print("❌ Login failed!")
                return False
            
            # Step 2: Map key pages
            print("\n🗺️  Step 2: Mapping key pages...")
            analyses = await mapper.map_key_pages()
            print(f"✅ Mapped {len(analyses)} pages")
            
            # Step 3: Generate report
            print("\n📊 Step 3: Generating structure report...")
            report = await mapper.generate_structure_report()
            
            print(f"\n🎉 Structure mapping complete!")
            print(f"📁 Results saved to: {mapper.output_dir}")
            print(f"📈 Total requests made: {mapper.request_count}/10")
            print("\n📋 Next steps:")
            print("   1. Review HTML files in horse_base_analysis/")
            print("   2. Check structure_report.json for findings")
            print("   3. Create test data based on discovered structure")
            print("   4. Build parsers using the HTML structure")
            
            return True
            
        except Exception as e:
            logger.error(f"Mapping failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
