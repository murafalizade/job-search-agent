from job_search_agent.core.orchestration.tools.website_scrapper.engine import ScrapingEngine
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

async def scrape_job(url: str) -> JobVacancy:
    """
    Scrapes a job vacancy from a given URL.
    Returns a JobVacancy model.
    """
    engine = ScrapingEngine()
    return await engine.scrape_url(url)

__all__ = ["ScrapingEngine", "scrape_job", "JobVacancy"]
