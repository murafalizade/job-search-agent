import json
import time
from collections import deque

from job_search_agent.core.llm_gateways.cost_controller import CostController


class ModelRouter:
    def __init__(self, config_path='config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.controller = CostController(self.config)

        # In-memory request trackers: { "model_name": deque([timestamps]) }
        self.history = {model: deque() for model in self.config['models']}

    def _is_rate_limited(self, model_name: str) -> bool:
        """Checks if the model has hit RPM or RPD limits."""
        now = time.time()
        limits = self.config['models'][model_name]['limits']['free_tier']
        usage = self.history[model_name]

        while usage and usage[0] < now - 86400:
            usage.popleft()

        if len(usage) >= limits['rpd']:
            return True

        rpm_count = sum(1 for t in usage if t > now - 60)
        if rpm_count >= limits['rpm']:
            return True

        return False

    def get_model(self, complexity: str, prompt_tokens: int):
        target_model = "gemini-2.5-flash-lite"  # Default
        for name, details in self.config['models'].items():
            if details['task_complexity'] == complexity:
                target_model = name
                break

        cost_est = self.controller.estimate_cost(target_model, prompt_tokens)
        can_afford = self.controller.can_afford(cost_est)

        is_limited = self._is_rate_limited(target_model)

        if can_afford and not is_limited:
            self.history[target_model].append(time.time())
            return target_model

        return "gemini-2.5-flash-lite"

def get_model_router():
    return ModelRouter()