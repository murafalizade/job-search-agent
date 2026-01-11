from functools import lru_cache
from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_PROJECT_ID: SecretStr
    GOOGLE_API_KEY: SecretStr
    
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_PROJECT: str = "default"
    LANGCHAIN_API_KEY: Optional[SecretStr] = None
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    TAVILY_API_KEY: SecretStr

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()