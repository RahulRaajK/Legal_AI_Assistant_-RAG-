"""Indian Kanoon crawler for case judgments."""
import re
import logging
from typing import Optional
from backend.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class IndianKanoonCrawler(BaseCrawler):
    """Crawler for Indian Kanoon (indiankanoon.org) - Case law database."""
    
    BASE_URL = "https://indiankanoon.org"
    
    def search_cases(self, query: str, max_results: int = 10) -> list[dict]:
        """Search for cases on Indian Kanoon."""
        search_url = f"{self.BASE_URL}/search/?formInput={query}"
        
        soup = self.fetch_page(search_url)
        if not soup:
            logger.warning(f"Could not fetch Indian Kanoon search for: {query}")
            return []
        
        results = []
        for item in soup.select(".result_title a, .result a"):
            title = item.get_text(strip=True)
            link = item.get("href", "")
            if title and link and "/doc/" in link:
                full_url = f"{self.BASE_URL}{link}" if link.startswith("/") else link
                
                # Try to extract year from title
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                year = int(year_match.group()) if year_match else None
                
                results.append({
                    "title": title,
                    "url": full_url,
                    "year": year,
                    "source": "indiankanoon",
                    "content_type": "judgment",
                })
                if len(results) >= max_results:
                    break
        
        return results
    
    def fetch_judgment(self, url: str) -> Optional[dict]:
        """Fetch the full text of a judgment."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract judgment title
        title = ""
        title_elem = soup.select_one(".doc_title, h2, .docsource_main")
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # Extract judgment text
        judgment_elem = soup.select_one(".judgments, .expanded, #maincontent")
        content = ""
        if judgment_elem:
            content = self.clean_text(judgment_elem.get_text())
        else:
            content = self.extract_text(soup)
        
        # Extract metadata
        court = ""
        judge = ""
        date = ""
        
        bench_elem = soup.select_one(".doc_bench, .docsource_main")
        if bench_elem:
            judge = bench_elem.get_text(strip=True)
        
        author_elem = soup.select_one(".doc_author")
        if author_elem:
            court = author_elem.get_text(strip=True)
        
        # Extract year from title or content
        year_match = re.search(r'\b(19|20)\d{2}\b', title or content[:200])
        year = int(year_match.group()) if year_match else None
        
        return {
            "title": title,
            "content": content,
            "url": url,
            "source": "indiankanoon",
            "content_type": "judgment",
            "court": court,
            "judge": judge,
            "year": year,
        }


indiankanoon_crawler = IndianKanoonCrawler()
