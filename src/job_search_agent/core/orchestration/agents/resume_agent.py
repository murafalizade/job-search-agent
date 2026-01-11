from langsmith import traceable

from job_search_agent.core.llm_gateways.prompts.resume_prompts import RESUME_PARSER_PROMPT
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.orchestration.models.resume_models import Resume


class ResumeAgent(BaseAgent):
    def __init__(self):
        super().__init__('basic')
        self.prompt = RESUME_PARSER_PROMPT

    @traceable
    async def parse_cv(self, cv_text: str) -> Resume:
        return await self.run(cv=cv_text)

    async def run(self, cv: str) -> Resume:
        prompt_text = self.prompt.format_messages(cv=cv)
        prompt_string = self.prompt.format(cv=cv)
        structured_llm = self.get_structured_llm(len(prompt_string), Resume)
        response = await structured_llm.ainvoke(prompt_text)
        return response