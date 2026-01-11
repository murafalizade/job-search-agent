from typing import List, Tuple

from job_search_agent.core.orchestration.agents import ResumeAgent
from job_search_agent.core.orchestration.agents.job_optimizer_agent import JobOptimizerAgent
from job_search_agent.core.orchestration.agents.resume_ranking_agent import ResumeRankingAgent
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult
from job_search_agent.core.llm_gateways.gateway import get_gateway
from job_search_agent.utils.resume_parser import resume_parser


class JobSearchOrchestrator:
    def __init__(self):
        self.gateway = get_gateway()

    @staticmethod
    async def process_cv(cv_file: bytes) -> Resume:
        """Parses CV into a structured Resume object."""
        cv_text = resume_parser(cv_file)
        agent = ResumeAgent()
        result = await agent.parse_cv(cv_text)
        return result

    @staticmethod
    async def find_jobs(cv: Resume) -> List[Tuple[JobVacancy, float, str]]:
        """Finds and ranks jobs based on currently parsed the CV."""
        agent = ResumeRankingAgent()
        ranked_jobs = await agent.run(cv)
        return ranked_jobs

    @staticmethod
    async def optimize_job(job: JobVacancy, cv: Resume) -> OptimizationResult:
        """Optimizes a specific job using the LangGraph optimize_job node."""
        agent = JobOptimizerAgent()
        result = await agent.run(job, cv)
        return result

    def get_usage_report(self) -> str:
        return self.gateway.cost_controller.get_spent()