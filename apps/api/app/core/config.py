"""
app/core/config.py — Application configuration

All settings come from environment variables / .env file.
No scattered os.getenv() calls elsewhere in the codebase.
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
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ─── Gemini / AI ──────────────────────────────────────────────────────────
    # "gemini_api" → uses GEMINI_API_KEY (Google AI Studio)
    # "vertex"     → uses GCP_PROJECT + GOOGLE_APPLICATION_CREDENTIALS
    GEMINI_BACKEND: str = "gemini_api"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Vertex AI (only needed when GEMINI_BACKEND=vertex)
    GCP_PROJECT: str = ""
    GCP_LOCATION: str = "us-central1"

    # ─── Playwright ───────────────────────────────────────────────────────────
    PLAYWRIGHT_TIMEOUT_MS: int = 30_000
    PLAYWRIGHT_HEADLESS: bool = True

    # ─── Persistence (future) ─────────────────────────────────────────────────
    # DATABASE_URL: str = ""
    # REDIS_URL: str = ""

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def gemini_configured(self) -> bool:
        if self.GEMINI_BACKEND == "gemini_api":
            return bool(self.GEMINI_API_KEY)
        if self.GEMINI_BACKEND == "vertex":
            return bool(self.GCP_PROJECT)
        return False


settings = Settings()
