from abc import ABC, abstractmethod
from typing import Any

from job_search_agent.core.llm_gateways.gateway import get_gateway

class BaseAgent(ABC):
    def __init__(self, complexity: str = "free"):
        self.complexity = complexity

    def get_llm(self, prompt_tokens: int):
        return get_gateway().get_llm(prompt_tokens, self.complexity)

    def get_structured_llm(self, prompt_tokens: int, schema: Any):
        llm = get_gateway().get_llm(prompt_tokens, self.complexity)
        return llm.with_structured_output(schema)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Main execution method for the agent."""
        pass
