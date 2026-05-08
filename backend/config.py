from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_academic"
    model_provider: str = "openai"
    model_name: str = "gpt-4.1"
    embedding_model: str = "text-embedding-3-large"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    chroma_persist_dir: str = "./data/chroma"
    auth_provider: str = "clerk"
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    clerk_jwks_url: str | None = None


settings = Settings()  # type: ignore[call-arg]
