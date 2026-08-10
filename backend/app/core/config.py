from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    serper_api_key: str | None = None

    database_url: str

    supabase_url: str
    supabase_jwt_secret: str

    cors_origins: list[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ai-job-application-assist.netlify.app",
    ]


settings = Settings()
