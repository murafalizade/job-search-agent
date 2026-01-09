from abc import ABC, abstractmethod
from typing import Any

from job_search_agent.core.llm_gateways.gateway import get_gateway

class BaseAgent(ABC):
    def __init__(self, complexity: str = "free"):
        model_gateway = get_gateway()
        self.llm = model_gateway.get_llm(complexity)

    def get_structured_llm(self, schema: Any):
        return self.llm.with_structured_output(schema)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Main execution method for the agent."""
        pass
