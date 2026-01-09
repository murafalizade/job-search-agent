from langsmith import traceable

from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.llm_gateways.prompts.optimizer_prompts import JOB_OPTIMIZER_PROMPT

class JobOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__('mid')
        self.prompt = JOB_OPTIMIZER_PROMPT

    @traceable
    async def run(self, job: JobVacancy, resume: Resume) -> OptimizationResult:
        prompt_text = self.prompt.format(job=job, resume=resume)
        structured_llm = self.get_structured_llm(len(prompt_text), OptimizationResult)

        response = await structured_llm.ainvoke(prompt_text)
        return response