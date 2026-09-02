from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Financial Research System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    SECRET_KEY: str = (
        "infosys_financial_research_secret_key_2026_super_secure_token"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    MONGODB_URL: Optional[str] = None
    DATABASE_NAME: str = "financial_research_db"

    # Configuration used by agents that require an OpenAI-compatible API key
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()