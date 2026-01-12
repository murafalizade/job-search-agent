import asyncio
from typing import List, Any
import httpx

from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.tools.api_call.model_mapper import map_glorri_response


class GlorriAPICall:
    def __init__(self):
        pass

    async def scrape(self, query: str) -> List[str]:
        url = f"https://api-dev.glorri.az/job-service-v2/jobs/public?keyword={query.lower()}&offset=0&limit=10"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        jobs = [map_glorri_response(item) for item in data.get("entities", [])]
        return jobs


async def main():
    scraper = GlorriAPICall()
    jobs = await scraper.scrape("developer")  # your search query
    for job in jobs:
        print(job)


if __name__ == "__main__":
    asyncio.run(main())