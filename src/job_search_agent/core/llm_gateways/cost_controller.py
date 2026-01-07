from job_search_agent.utils.helper import get_config_file


class CostController:
    # Hardcoded global state for the session (Simulates a DB)
    _total_spent = 0.0

    def __init__(self):
        config = get_config_file()
        self.pricing = config['models']
        self.opt_features = config['optimization_features']
        self.budget_limit = 10.00

    @classmethod
    def get_spent(cls):
        return cls._total_spent

    def estimate_cost(self, model_id, prompt_tokens, expected_output=800):
        model_cfg = self.pricing.get(model_id)

        if "input_short_context" in model_cfg['pricing']:
            p = model_cfg['pricing']
            rate = p['input_short_context'] if prompt_tokens < p['context_threshold'] else p['input_long_context']
            input_cost = (prompt_tokens / 1_000_000) * rate
        else:
            input_cost = (prompt_tokens / 1_000_000) * model_cfg['pricing']['input_per_million']

        cache_cfg = self.opt_features['caching']
        if cache_cfg['enabled'] and prompt_tokens >= cache_cfg['min_context_tokens']:
            input_cost *= cache_cfg['cost_multiplier']  # 0.10 multiplier

        output_cost = (expected_output / 1_000_000) * model_cfg['pricing'].get('output_per_million', 10.0)
        return input_cost + output_cost

    def can_afford(self, estimated_cost):
        return (self._total_spent + estimated_cost) < self.budget_limit

    def commit_spend(self, actual_cost):
        CostController._total_spent += actual_cost
        print(f" Spend Updated: ${actual_cost:.4f} | Total: ${self._total_spent:.4f}")