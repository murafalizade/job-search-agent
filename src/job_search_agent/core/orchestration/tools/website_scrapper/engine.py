from typing import List, Optional
from job_search_agent.core.orchestration.tools.website_scrapper.base import BaseScraper
from job_search_agent.core.orchestration.tools.website_scrapper.scrapers.jobsearch_az import JobSearchAzScraper
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
import httpx
from bs4 import BeautifulSoup

class ScrapingEngine:
    """Orchestrates different scrapers based on URL."""
    
    def __init__(self, scrapers: Optional[List[BaseScraper]] = None):
        self.scrapers = scrapers or [
            JobSearchAzScraper(),
        ]


    async def scrape_url(self, url: str) -> JobVacancy:
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                try:
                    return await scraper.scrape(url)
                except Exception as e:
                    print(f"Error scraping with {scraper.__class__.__name__}: {e}")
                    continue
        
