import asyncio
import math
from typing import List, Tuple
from langchain_huggingface import HuggingFaceEmbeddings
from job_search_agent.core.orchestration.models.resume_models import Resume

from job_search_agent.configs.setting import get_settings
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.orchestration.agents.resume_agent import ResumeAgent
from job_search_agent.core.orchestration.tools.search_tool.ddg_search_tool import DuckDuckGoSearchTool
from job_search_agent.core.orchestration.tools.website_scrapper.engine import ScrapingEngine
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class ResumeRankingAgent(BaseAgent): 
    def __init__(self):
        super().__init__()
        settings = get_settings()
        self.web_searcher = DuckDuckGoSearchTool()
        self.scraper = ScrapingEngine()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if not magnitude1 or not magnitude2:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def _build_cv_profile(self, cv: Resume) -> str:
        """Create a clean, structured profile from CV data."""
        return f"Professional Titles: {', '.join(cv.titles)}\n Skills: {', '.join(cv.skills)}"

    def _build_job_profile(self, job: JobVacancy) -> str:
        """Create a clean, structured profile from Job data, limiting noise."""
        # Use requirements primarily, fallback to title + snippet if empty
        if not job:
            return ""
        reqs = job.requirements if job.requirements else ""
        desc_snippet = job.description[:300] if not reqs else job.description[:150]
        return f"Job Title: {job.title}\nRequirements: {reqs}\nDescription: {desc_snippet}"

    def run(self, cv: Resume) -> List[Tuple[JobVacancy, float]]:
        cv_profile = self._build_cv_profile(cv)
        cv_embedding = self.embeddings.embed_query(cv_profile)
        
        # Ensure we have a clean list of titles (handle case where user might pass "Title1, Title2" as one string)
        actual_titles = []
        for t in cv.titles:
            if "," in t:
                actual_titles.extend([item.strip() for item in t.split(",")])
            else:
                actual_titles.append(t.strip())
        
        # Deduplicate titles
        actual_titles = list(dict.fromkeys(actual_titles))

        # Search for jobs using all titles concurrently
        async def search_all_titles(titles: List[str]) -> List[str]:
            tasks = [asyncio.to_thread(self.web_searcher.search, title.lower()) for title in titles]
            results = await asyncio.gather(*tasks)
            # Flatten and deduplicate
            unique_urls = set()
            for url_list in results:
                if isinstance(url_list, list):
                    unique_urls.update(url_list)
            print(f"Found {len(unique_urls)} URLs.")
            return list(unique_urls)

        print(f"Searching for jobs with titles: {', '.join(actual_titles)}...")
        urls = asyncio.run(search_all_titles(actual_titles))
        
        if not urls:
            print("No URLs found.")
            return []

        async def scrape_all(urls: List[str]) -> List[JobVacancy]:
            tasks = [self.scraper.scrape_url(url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
            
        print(f"Scraping {len(urls)} potential jobs...")
        # Since scrape_all is async and we are in a sync run() method, 
        # we can combine it into the same event loop if we wanted, 
        # but the current structure uses asyncio.run()
        results = asyncio.run(scrape_all(urls))
        jobs = [job for job in results if isinstance(job, JobVacancy) and job is not None]
        
        if not jobs:
            print("No valid jobs scraped.")
            return []
        
        print(f"Ranking {len(jobs)} jobs using multilingual embeddings...")
        job_profiles = [self._build_job_profile(job) for job in jobs]
        job_embeddings = self.embeddings.embed_documents(job_profiles)
        
        ranked_jobs = []
        for job, job_embedding in zip(jobs, job_embeddings):
            score = self._cosine_similarity(cv_embedding, job_embedding)
            ranked_jobs.append((job, score))
            
        ranked_jobs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Successfully ranked {len(ranked_jobs)} jobs.")
        return ranked_jobs

if __name__ == "__main__":
    from job_search_agent.core.orchestration.models.resume_models import Resume
    ranker = ResumeRankingAgent()
    resume_agent = ResumeAgent()
    dummy_cv = Resume(
        titles=['Frontend Developer', 'Frontend Proqramçı', 'frontend developer'], 
        skills=[], seniority='Mid', years_experience=5, preferred_locations=[], keywords=['software engineer', '5 years experience']
    )
    result = ranker.run(dummy_cv)
    for job, score in result:
        if job:
            print(f"Score: {score:.4f} | Title: {job.title} | Company: {job.company}")
       