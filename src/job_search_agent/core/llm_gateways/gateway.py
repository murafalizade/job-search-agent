from langchain.chat_models import init_chat_model
from job_search_agent.core.llm_gateways.cost_controller import CostController
from job_search_agent.core.llm_gateways.model_router import get_model_router
from job_search_agent.core.llm_gateways.observability import telemetry
from job_search_agent.configs.setting import get_settings

class LLMGateway:
    """
    Production-ready Gateway with Cost Control, Routing, and Observability.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.cost_controller = CostController('')
        self.model_router = get_model_router()

    def get_llm(self, complexity: str = "basic"):
        model_name = self.model_router.get_model(complexity)
        
        telemetry.log_event("Gateway", "model_routing", {
            "requested_complexity": complexity,
            "selected_model": model_name,
            "current_total_cost": self.cost_controller.get_spent()
        })

        if model_name.startswith("gemini"):
            return init_chat_model(
                model_name,
                api_key=self.settings.GOOGLE_API_KEY.get_secret_value()
            )
        else:
            return init_chat_model(model_name)

_gateway = None
def get_gateway() -> LLMGateway:
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway
