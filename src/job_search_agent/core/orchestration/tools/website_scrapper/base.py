from abc import ABC, abstractmethod
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class BaseScraper(ABC):
    """Base class for all website scrapers."""
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        pass

    @abstractmethod
    async def scrape(self, url: str) -> JobVacancy:
        """Scrape the given URL and return a JobVacancy object."""
        pass
