import json
import os
from datetime import datetime
from typing import Dict
from pydantic import BaseModel

class ModelPrice(BaseModel):
    input_price_per_1m: float
    output_price_per_1m: float

class CostController:
    """
    Tracks and controls the cost of LLM calls with file-based persistence.
    """
    
    PRICES: Dict[str, ModelPrice] = {
        "gemini-1.5-flash": ModelPrice(input_price_per_1m=0.075, output_price_per_1m=0.30),
        "gemini-1.5-pro": ModelPrice(input_price_per_1m=3.50, output_price_per_1m=10.50),
        "gemini-2.0-flash-exp": ModelPrice(input_price_per_1m=0.0, output_price_per_1m=0.0),
        "gemini-2.0-flash-thinking-exp": ModelPrice(input_price_per_1m=0.0, output_price_per_1m=0.0),
    }

    def __init__(self, daily_budget: float = 0.50, storage_path: str = "usage_stats.json"):
        self.daily_budget = daily_budget
        self.storage_path = storage_path
        self.total_cost = 0.0
        self.total_tokens_input = 0
        self.total_tokens_output = 0
        self.last_reset_date = datetime.now().strftime("%Y-%m-%d")
        
        self._load_state()
        self._check_daily_reset()

    def _load_state(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.total_cost = data.get("total_cost", 0.0)
                    self.total_tokens_input = data.get("total_tokens_input", 0)
                    self.total_tokens_output = data.get("total_tokens_output", 0)
                    self.last_reset_date = data.get("last_reset_date", self.last_reset_date)
            except Exception as e:
                print(f"Error loading usage stats: {e}")

    def _save_state(self):
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({
                    "total_cost": self.total_cost,
                    "total_tokens_input": self.total_tokens_input,
                    "total_tokens_output": self.total_tokens_output,
                    "last_reset_date": self.last_reset_date
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving usage stats: {e}")

    def _check_daily_reset(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.last_reset_date:
            print(f"New day detected ({current_date}). Resetting daily budget.")
            self.total_cost = 0.0
            self.total_tokens_input = 0
            self.total_tokens_output = 0
            self.last_reset_date = current_date
            self._save_state()

    def update_usage(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        self._check_daily_reset()
        
        clean_name = model_name.split(":")[-1] if ":" in model_name else model_name
        price = self.PRICES.get(clean_name, self.PRICES["gemini-1.5-flash"])
        
        call_cost = (input_tokens / 1_000_000 * price.input_price_per_1m) + \
                    (output_tokens / 1_000_000 * price.output_price_per_1m)
        
        self.total_cost += call_cost
        self.total_tokens_input += input_tokens
        self.total_tokens_output += output_tokens
        
        self._save_state()
        return call_cost

    def is_within_budget(self) -> bool:
        self._check_daily_reset()
        return self.total_cost < self.daily_budget

    def get_report(self) -> str:
        return (f"Cost Report ({self.last_reset_date}):\n"
                f"- Total Cost: ${self.total_cost:.4f}\n"
                f"- Budget: ${self.daily_budget:.4f}\n"
                f"- Tokens: {self.total_tokens_input} in / {self.total_tokens_output} out")
