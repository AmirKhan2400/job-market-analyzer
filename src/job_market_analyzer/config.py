from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    requesty_api_key: str = Field(min_length=1)
    requesty_policy: str = Field(min_length=1)
    openrouter_api_key: str = Field(min_length=1)
    openrouter_preset: str = Field(min_length=1)
    database_url: str = Field(min_length=1)
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    visitor_cookie_secure: bool = False
    visitor_cookie_samesite: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
