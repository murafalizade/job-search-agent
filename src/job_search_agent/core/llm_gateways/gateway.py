from typing import Any, Dict, Optional
from langchain.chat_models import init_chat_model
from job_search_agent.core.llm_gateways.cost_controller import CostController
from job_search_agent.core.llm_gateways.observability import telemetry
from job_search_agent.configs.setting import get_settings

class LLMGateway:
    """
    Production-ready Gateway with Cost Control, Routing, and Observability.
    """
    
    def __init__(self, daily_budget: float = 0.50):
        self.settings = get_settings()
        self.cost_controller = CostController(daily_budget=daily_budget)
        self.models = {
            "low": "google_genai:gemini-1.5-flash",
            "medium": "google_genai:gemini-1.5-pro",
            "high": "google_genai:gemini-2.0-flash-thinking-exp"
        }

    def _truncate_input(self, text: str, max_chars: int = 10000) -> str:
        """Simple token guard to prevent massive prompts."""
        if len(text) > max_chars:
            return text[:max_chars] + "... [TRUNCATED FOR COST CONTROL]"
        return text

    def get_llm(self, complexity: str = "low"):
        model_name = self.models.get(complexity, self.models["low"])
        
        # Observability: Log model selection
        telemetry.log_event("Gateway", "model_routing", {
            "requested_complexity": complexity,
            "selected_model": model_name,
            "current_total_cost": self.cost_controller.total_cost
        })

        return init_chat_model(
            model_name,
            api_key=self.settings.GOOGLE_API_KEY.get_secret_value()
        )

    def track_usage(self, model_name: str, response: Any, context: Optional[str] = None):
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            cost = self.cost_controller.update_usage(model_name, input_tokens, output_tokens)
            
            # Observability: Log usage and cost
            telemetry.log_event("Gateway", "llm_usage", {
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "context": context
            })
            
            print(f"Cost: ${cost:.6f} | Total: ${self.cost_controller.total_cost:.4f}")

_gateway = None
def get_gateway() -> LLMGateway:
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway
