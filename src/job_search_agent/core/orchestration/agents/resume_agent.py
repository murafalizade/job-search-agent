from job_search_agent.core.llm_gateways.prompts.resume_prompts import RESUME_PARSER_PROMPT
from job_search_agent.core.orchestration.agents.base import BaseAgent
from job_search_agent.core.orchestration.models.resume_models import Resume


class ResumeAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt = RESUME_PARSER_PROMPT
        self.structured_llm = self.get_structured_llm(Resume)

    async def parse_cv(self, cv_text: str) -> Resume:
        return await self.run(cv=cv_text)

    async def run(self, cv: str) -> Resume:
        chain = self.prompt | self.structured_llm
        response = await chain.ainvoke({"cv": cv})
        print(f"Extracted Data: {response}")
        return response