from job_search_agent.configs.setting import get_settings
from abc import ABC, abstractmethod
from typing import Any
from langchain.chat_models import init_chat_model


class BaseAgent(ABC):
    def __init__(self, model_name: str = "google_genai:gemini-2.5-flash"):
        settings = get_settings()
        self.llm = init_chat_model(
            model_name,
            api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )


    def get_structured_llm(self, schema: Any):
        return self.llm.with_structured_output(schema)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Main execution method for the agent."""
        pass
