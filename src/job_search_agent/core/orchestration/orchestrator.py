from typing import List, Tuple, Optional
from job_search_agent.core.orchestration.agents.resume_agent import ResumeAgent
from job_search_agent.core.orchestration.agents.resume_ranking_agent import ResumeRankingAgent
from job_search_agent.core.orchestration.agents.job_optimizer_agent import JobOptimizerAgent
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult
from job_search_agent.core.llm_gateways.gateway import get_gateway

class JobSearchOrchestrator:
    def __init__(self):
        self.resume_agent = ResumeAgent()
        self.ranking_agent = ResumeRankingAgent()
        self.optimizer_agent = JobOptimizerAgent()
        self.gateway = get_gateway()
        
        # In-memory state (for a real app, this would be in Redis/DB)
        self.current_resume: Optional[Resume] = None
        self.last_ranked_jobs: List[Tuple[JobVacancy, float]] = []

    def process_cv(self, cv_text: str) -> Tuple[Resume, List[Tuple[JobVacancy, float]]]:
        """Parses CV and finds/ranks matching jobs."""
        self.current_resume = self.resume_agent.parse_cv(cv_text)
        self.last_ranked_jobs = self.ranking_agent.run(cv_text)
        return self.current_resume, self.last_ranked_jobs

    def optimize_job(self, job_index: int) -> OptimizationResult:
        """Optimizes a specific job from the last ranked list."""
        if not self.current_resume:
            raise ValueError("No CV processed yet. Please upload a CV first.")
        
        if job_index < 0 or job_index >= len(self.last_ranked_jobs):
            raise IndexError("Invalid job selection index.")
            
        selected_job = self.last_ranked_jobs[job_index][0]
        return self.optimizer_agent.run(job=selected_job, resume=self.current_resume)

    def get_usage_report(self) -> str:
        return self.gateway.cost_controller.get_report()
