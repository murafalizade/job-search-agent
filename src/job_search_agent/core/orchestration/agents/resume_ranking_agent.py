import asyncio
import math
from typing import List, Tuple
from langchain_google_genai import GoogleGenerativeAIEmbeddings
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
        self.resume_agent = ResumeAgent()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if not magnitude1 or not magnitude2:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def run(self, cv: str) -> List[Tuple[JobVacancy, float]]:
        print("Parsing CV...")
        parsed_resume = self.resume_agent.parse_cv(cv)
        
        cv_profile = f"{' '.join(parsed_resume.titles)} {' '.join(parsed_resume.skills)} {' '.join(parsed_resume.keywords)}"
        cv_embedding = self.embeddings.embed_query(cv_profile)
        
        print(f"Searching for jobs matching: {parsed_resume.titles[0] if parsed_resume.titles else 'CV'}...")
        urls = self.web_searcher.search(cv_profile)
        
        if not urls:
            print("No URLs found.")
            return []

        async def scrape_all(urls: List[str]) -> List[JobVacancy]:
            tasks = [self.scraper.scrape_url(url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
            
        print(f"Scraping {len(urls)} potential jobs...")
        results = asyncio.run(scrape_all(urls))
        jobs = [job for job in results if isinstance(job, JobVacancy)]
        
        if not jobs:
            print("No valid jobs scraped.")
            return []
        
        print(f"Ranking {len(jobs)} jobs using embeddings...")
        job_profiles = [f"{job.title} {job.requirements} {job.description[:500]}" for job in jobs]
        job_embeddings = self.embeddings.embed_documents(job_profiles)
        
        ranked_jobs = []
        for job, job_embedding in zip(jobs, job_embeddings):
            score = self._cosine_similarity(cv_embedding, job_embedding)
            ranked_jobs.append((job, score))
            
        ranked_jobs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Successfully ranked {len(ranked_jobs)} jobs.")
        return ranked_jobs