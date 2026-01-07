import logging
import json
from datetime import datetime
from typing import Any, Dict

import os

from job_search_agent.configs.setting import get_settings

def init_langsmith():
    """Initializes LangSmith tracing by exporting settings to environment variables."""
    settings = get_settings()
    
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY.get_secret_value()
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
        
        print(f"LangSmith Tracing Configured for Project: {settings.LANGCHAIN_PROJECT}")
    else:
        print("LangSmith Tracing is disabled (API Key not found).")

init_langsmith()
