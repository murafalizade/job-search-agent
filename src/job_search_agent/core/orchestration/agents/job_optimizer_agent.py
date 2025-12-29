from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.llm_gateways.prompts.optimizer_prompts import JOB_OPTIMIZER_PROMPT

class JobOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt = JOB_OPTIMIZER_PROMPT
        self.structured_llm = self.get_structured_llm(OptimizationResult)
    
    def run(self, job: JobVacancy, resume: Resume) -> OptimizationResult:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({
            "job": job.model_dump(),
            "resume": resume.model_dump()
        })
        return response