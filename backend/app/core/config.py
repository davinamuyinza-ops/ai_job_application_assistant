from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    openai_api_key: str
    adzuna_app_id: str
    adzuna_app_key: str

    database_url: str

    supabase_url: str
    supabase_jwt_secret: str

    cors_origins: list[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ai-job-application-assist.netlify.app",
    ]


settings = Settings()
