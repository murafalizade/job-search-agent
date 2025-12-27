from typing import List, Optional
from job_search_agent.core.orchestration.tools.website_scrapper.base import BaseScraper
from job_search_agent.core.orchestration.tools.website_scrapper.scrapers.jobsearch_az import JobSearchAzScraper
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
import httpx
from bs4 import BeautifulSoup

class DefaultScraper(BaseScraper):
    """Generic fallback scraper for unknown domains."""
    
    def can_handle(self, url: str) -> bool:
        return True # Fallback

    async def scrape(self, url: str) -> JobVacancy:
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            html = response.text
        
        soup = BeautifulSoup(html, "html.parser")
        
        title = soup.title.string if soup.title else url
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
            
        return JobVacancy(
            title=title,
            company="Unknown",
            deadline="N/A",
            url=url,
            source="Generic",
            description=description or "No description found",
            requirements="N/A",
            how_to_apply="N/A",
            salary=None,
            email=None
        )

class ScrapingEngine:
    """Orchestrates different scrapers based on URL."""
    
    def __init__(self, scrapers: Optional[List[BaseScraper]] = None):
        self.scrapers = scrapers or [
            JobSearchAzScraper(),
            # Add more scrapers here as they are developed
        ]
        self.default_scraper = DefaultScraper()

    async def scrape_url(self, url: str) -> JobVacancy:
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                try:
                    return await scraper.scrape(url)
                except Exception as e:
                    # Log error and try next or fallback
                    print(f"Error scraping with {scraper.__class__.__name__}: {e}")
                    continue
        
        return await self.default_scraper.scrape(url)
