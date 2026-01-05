from functools import lru_cache
from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_PROJECT_ID: str
    GOOGLE_API_KEY: SecretStr
    
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[SecretStr] = None
    LANGCHAIN_PROJECT: str = "job-search-agent"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()