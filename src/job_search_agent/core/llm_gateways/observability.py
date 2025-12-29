import logging
import json
from datetime import datetime
from typing import Any, Dict

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

# Global instance
telemetry = AgentLogger()
