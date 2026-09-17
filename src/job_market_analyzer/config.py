from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    arvan_api_key: str = ""
    arvan_base_url: str = ""
    arvan_model: str = ""
    requesty_api_key: str = Field(min_length=1)
    requesty_policy: str = Field(min_length=1)
    requesty_extraction_policy: str = "policy/Job-Market-Analyzer"
    openrouter_api_key: str = Field(min_length=1)
    openrouter_preset: str = Field(min_length=1)
    openrouter_extraction_preset: str = "@preset/job-market-analyzer-job-extraction"
    database_url: str = Field(min_length=1)
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    visitor_cookie_secure: bool = False
    visitor_cookie_samesite: str = "lax"
    analysis_request_limit: int = 0
    analysis_request_cooldown_seconds: int = 0
    ai_extraction_max_tokens: int = 1200
    ai_recommendation_max_tokens: int = 700

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
