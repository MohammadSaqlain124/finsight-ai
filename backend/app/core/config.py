from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "dev-insecure-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 10

    # SQLite locally. In production, set DATABASE_URL to the Neon Postgres
    # connection string through an environment variable.
    DATABASE_URL: str = "sqlite:///./finsight.db"

    # Comma separated origins allowed to call the API from a browser.
    # Local default here; the deployed frontend URL gets added in production.
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()