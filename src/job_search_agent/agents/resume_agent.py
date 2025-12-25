from job_search_agent.agents.base import BaseAgent
from job_search_agent.prompts.resume_prompts import RESUME_PARSER_PROMPT
from job_search_agent.models.resume_models import ResumeData

class ResumeAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt = RESUME_PARSER_PROMPT
        self.structured_llm = self.get_structured_llm(ResumeData)

    def parse_cv(self, cv_text: str) -> ResumeData:
        return self.run(cv=cv_text)

    def run(self, cv: str) -> ResumeData:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({"cv": cv})
        print(f"Extracted Data: {response}")
        return response


if __name__ == "__main__":
    agent = ResumeAgent()
    cv_text = """I am a software engineer with 5 years of experience in the field."""
    agent.parse_cv(cv_text)