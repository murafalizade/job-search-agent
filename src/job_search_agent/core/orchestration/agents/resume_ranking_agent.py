from langsmith.run_helpers import traceable
import asyncio
from typing import List, Tuple
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.matching_models import BatchJobMatchResult
from job_search_agent.core.llm_gateways.prompts.matching_prompts import JOB_MATCHING_PROMPT

from job_search_agent.configs.setting import get_settings
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.orchestration.tools.search_tool.tavily_search_tool import TavilySearchTool
from job_search_agent.core.orchestration.tools.search_tool.ddg_search_tool import DuckDuckGoSearchTool
from job_search_agent.core.orchestration.tools.website_scrapper.engine import ScrapingEngine
from job_search_agent.core.orchestration.tools.api_call.glorri_api_call import GlorriAPICall
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class ResumeRankingAgent(BaseAgent): 
    def __init__(self):
        super().__init__('advanced')
        settings = get_settings()
        if settings.TAVILY_API_KEY:
            self.web_searcher = TavilySearchTool(max_results=10)
        else:
            self.web_searcher = DuckDuckGoSearchTool(max_results=10)
        self.scraper = ScrapingEngine()
        self.api_searcher = GlorriAPICall()


    def _build_resume_summary(self, cv: Resume) -> str:
        """Create a concise summary of the resume for the matching agent."""
        return f"Titles: {', '.join(cv.titles)}\nSkills: {', '.join(cv.skills)}\nExperience: {cv.years_experience} years ({cv.seniority})"

    async def _batch_check_matches(self, jobs: List[JobVacancy], resume_summary: str) -> BatchJobMatchResult:
        """Use AI to check which jobs match the resume in a single batch call."""
        if not jobs:
            return BatchJobMatchResult(matching_indices=[], reasons={})
            
        jobs_formatted = ""
        for i, job in enumerate(jobs):
            jobs_formatted += f"--- JOB INDEX {i} ---\nTitle: {job.title}\nRequirements: {job.requirements}\n\n"

        prompt_text = JOB_MATCHING_PROMPT.format_messages(
            resume=resume_summary,
            jobs_list=jobs_formatted
        )
        prompt_string = JOB_MATCHING_PROMPT.format(
            resume=resume_summary,
            jobs_list=jobs_formatted
        )
        
        structured_llm = self.get_structured_llm(len(prompt_string), BatchJobMatchResult)
        try:
            response = await structured_llm.ainvoke(prompt_text)
            return response
        except Exception as e:
            print(f"Error in batch matching: {e}")
            return BatchJobMatchResult(matching_indices=[], reasons={})

    @traceable
    async def run(self, cv: Resume) -> List[Tuple[JobVacancy, float, str]]:
        search_queries = list(dict.fromkeys(cv.keywords))

        async def search_all_keywords(queries: List[str]) -> List[str]:
            tasks = [asyncio.to_thread(self.web_searcher.search, f"{query.lower()}") for query in queries]
            results = await asyncio.gather(*tasks)
            unique_urls = set()
            for url_list in results:
                if isinstance(url_list, list):
                    unique_urls.update(url_list)
            return list(unique_urls)

        search_urls = await search_all_keywords(search_queries)
        
        # API Search for URLs
        api_urls = []
        print(f"Searching via API for {len(search_queries)} queries...")
        api_tasks = [self.api_searcher.scrape(query) for query in search_queries]
        api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
        for res in api_results:
            if isinstance(res, list):
                api_urls.extend(res)
            elif isinstance(res, Exception):
                print(f"API search error: {res}")

        # Combine and unique URLs
        all_urls = list(set(search_urls + api_urls))
        
        jobs = []
        if all_urls:
            async def scrape_all(urls: List[str]) -> List[JobVacancy]:
                tasks = [self.scraper.scrape_url(url) for url in urls]
                return await asyncio.gather(*tasks, return_exceptions=True)
                
            print(f"Scraping {len(all_urls)} potential jobs from combined sources...")
            results = await scrape_all(all_urls)
            jobs = [job for job in results if isinstance(job, JobVacancy) and job is not None]
        
        # Deduplicate jobs by (title + company)
        unique_jobs = []
        seen_job_keys = set()
        for job in jobs:
            title_norm = job.title.strip().lower() if job.title else ""
            company_norm = job.company.strip().lower() if job.company else ""
            job_key = (title_norm, company_norm)
            
            if job_key not in seen_job_keys:
                seen_job_keys.add(job_key)
                unique_jobs.append(job)
        
        jobs = unique_jobs

        if not jobs:
            print("No valid jobs found.")
            return []
        
        jobs_to_process = jobs[:15]
        resume_summary = self._build_resume_summary(cv)

        match_result = await self._batch_check_matches(jobs_to_process, resume_summary)
        matching_indices = match_result.matching_indices
        reasons = match_result.reasons
        
        ranked_jobs = []
        for i, job in enumerate(jobs_to_process):
            reason = reasons.get(i) or reasons.get(str(i), "Səbəb tapılmadı")
            if i in matching_indices:
                ranked_jobs.append((job, 1.0, reason))
            else:
                print(f"Not a match: {job.title} at {job.company}")
                print(f"Reason: {reason}")
            
        return ranked_jobs