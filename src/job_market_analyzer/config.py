from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    openrouter_api_key: str
    database_url: str
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    visitor_cookie_secure: bool = False
    visitor_cookie_samesite: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
