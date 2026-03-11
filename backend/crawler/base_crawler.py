"""Base crawler with rate limiting and HTML cleaning."""
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional
from fake_useragent import UserAgent
from backend.config import get_settings
import re
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseCrawler:
    """Base crawler with rate limiting, error handling, and content extraction."""
    
    def __init__(self):
        self.session = requests.Session()
        try:
            ua = UserAgent()
            self.session.headers.update({"User-Agent": ua.random})
        except Exception:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
        self.delay = settings.CRAWL_DELAY_SECONDS
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page."""
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text - remove extra whitespace, normalize."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def extract_text(self, soup: BeautifulSoup, selector: str = None) -> str:
        """Extract text from a BeautifulSoup element."""
        if selector:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return self.clean_text(soup.get_text())
