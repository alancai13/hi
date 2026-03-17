"""
app/core/config.py — Application configuration

Reads settings from environment variables (and a .env file in development).
All configuration lives here — no scattered os.getenv() calls elsewhere.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ─── Application ──────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "info"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://app.example.com"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ─── LLM (future) ─────────────────────────────────────────────────────────
    # ANTHROPIC_API_KEY: str = ""
    # OPENAI_API_KEY: str = ""
    # LLM_PROVIDER: str = "anthropic"

    # ─── Playwright (future) ──────────────────────────────────────────────────
    # PLAYWRIGHT_TIMEOUT_MS: int = 30_000
    # PLAYWRIGHT_HEADLESS: bool = True

    # ─── Persistence (future) ─────────────────────────────────────────────────
    # DATABASE_URL: str = ""
    # REDIS_URL: str = ""

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


# Single settings instance — import this everywhere.
settings = Settings()
