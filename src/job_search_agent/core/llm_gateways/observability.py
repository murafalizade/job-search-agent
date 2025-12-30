import logging
import json
from datetime import datetime
from typing import Any, Dict

import os
from job_search_agent.configs.setting import get_settings

class AgentLogger:
    """
    Handles structured logging for observability.
    Logs are saved in JSON format for easy parsing by tools like ELK or Datadog.
    """
    def __init__(self, log_file: str = "agent_trace.log"):
        self.logger = logging.getLogger("JobSearchAgent")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file)
        self.logger.addHandler(fh)

    def log_event(self, agent_name: str, event_type: str, data: Dict[str, Any]):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "event": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))

def init_langsmith():
    """Initializes LangSmith tracing using settings."""
    settings = get_settings()
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY.get_secret_value()
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
        print(f"🚀 LangSmith Tracing enabled for project: {settings.LANGCHAIN_PROJECT}")
    else:
        print("ℹ️ LangSmith Tracing is disabled.")

# Global instance
telemetry = AgentLogger()
init_langsmith()
