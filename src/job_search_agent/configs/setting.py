from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_PROJECT_ID: str
    GOOGLE_API_KEY: SecretStr
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()