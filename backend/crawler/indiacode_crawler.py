"""IndiaCode crawler for fetching acts and sections from indiacode.nic.in."""
import re
import logging
from typing import Optional
from backend.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class IndiaCodeCrawler(BaseCrawler):
    """Crawler for IndiaCode (indiacode.nic.in) - Central Acts database."""
    
    BASE_URL = "https://www.indiacode.nic.in"
    
    def search_acts(self, query: str, max_results: int = 10) -> list[dict]:
        """Search for acts on IndiaCode."""
        search_url = f"{self.BASE_URL}/handle/123456789/1362/search"
        params = {
            "query": query,
            "submit": "Search",
        }
        
        soup = self.fetch_page(f"{search_url}?query={query}")
        if not soup:
            logger.warning(f"Could not fetch IndiaCode search for: {query}")
            return []
        
        results = []
        # Parse search results
        for item in soup.select(".artifact-title a, .ds-artifact-item a"):
            title = item.get_text(strip=True)
            link = item.get("href", "")
            if title and link:
                results.append({
                    "title": title,
                    "url": f"{self.BASE_URL}{link}" if link.startswith("/") else link,
                    "source": "indiacode",
                })
                if len(results) >= max_results:
                    break
        
        return results
    
    def fetch_act_content(self, url: str) -> Optional[dict]:
        """Fetch the full content of an act from IndiaCode."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Try to extract act title and content
        title = ""
        title_elem = soup.select_one("h1, .page-header, title")
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # Extract main content
        content_selectors = [
            ".item-page-field-wrapper",
            "#aspect_artifactbrowser_ItemViewer",
            "main",
            ".container",
        ]
        
        content = ""
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                content = self.clean_text(elem.get_text())
                if len(content) > 100:
                    break
        
        if not content:
            content = self.extract_text(soup)
        
        return {
            "title": title,
            "content": content,
            "url": url,
            "source": "indiacode",
            "content_type": "statute",
        }


indiacode_crawler = IndiaCodeCrawler()
